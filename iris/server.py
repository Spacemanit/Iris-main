import argparse
import asyncio
import contextlib
import logging
import json
import math
import time

from .audio import Endpoint
from .protocol import Control, MIC, VIDEO, SPEAKER, pack, rms, unpack
from .vision import Gaze, Vision
from .preview import Preview, PreviewServer
from .microphone import LaptopMicrophone
from .speaker import LaptopSpeaker
from .levels import MicrophoneMeter

log = logging.getLogger("iris")
VOICE_RESPONSE_TIMEOUT = 90
SOCKET_SEND_TIMEOUT = 5


class Session:
    def __init__(self, websocket, vision, brain=None, mirror=False, preview=None,
                 microphone=None, brain_ready=None, speaker_output="esp32", speaker_device=None,
                 mic_test=False, mic_threshold=.015):
        self.ws, self.vision, self.brain = websocket, vision, brain
        self.preview = preview
        self.microphone, self.brain_ready = microphone, brain_ready
        self.speaker_output, self.speaker_device = speaker_output, speaker_device
        self.mic_test = mic_test
        self.voice_enabled = mic_test or brain is not None or brain_ready is not None or microphone is not None
        self.microphone_meter = MicrophoneMeter()
        self.next_meter_update = 0.0
        self.resume_audio_at = 0.0
        self.frames = asyncio.Queue(maxsize=1)
        self.utterances = asyncio.Queue(maxsize=1)
        self.control = Control()
        self.gaze = Gaze(mirror)
        self.endpoint = Endpoint(threshold=mic_threshold)
        self.busy = False
        self.last_frame = time.monotonic()
        self.last_audio = time.monotonic()
        self.frames_processed = self.frames_dropped = self.invalid = 0
        self.mic_gaps = 0
        self.control_changed = asyncio.Event()
        self.frame_ack = 0
        self.tracking_ms = 0.0
        self.device_status = None

    def feed_audio(self, pcm, captured_at=None):
        # Measure arrivals even when inference is not accepting utterances.
        self.microphone_meter.feed(pcm)
        if time.monotonic() >= self.next_meter_update:
            self.publish_microphone()
            self.next_meter_update = time.monotonic() + .1
        if not self.brain or self.busy:
            return
        if captured_at is None:
            captured_at = time.monotonic()
        if captured_at < self.resume_audio_at:
            return
        self.last_audio = time.monotonic()
        previous = self.control.state
        utterance = self.endpoint.feed(pcm)
        self.control.state = "listening" if self.endpoint.buffer else "idle"
        if utterance and not self.utterances.full():
            self.busy = True
            self.control.state = "thinking"
            self.utterances.put_nowait(utterance)
            log.info("Speech captured: %.2f seconds", len(utterance) / 32000)
        if self.control.state != previous:
            self.control_changed.set()

    def microphone_status(self):
        if not self.voice_enabled:
            return "disabled"
        if self.mic_test:
            return "test"
        if self.busy:
            return "playback" if self.control.state == "talking" else "processing"
        if self.brain is None:
            return "unavailable" if self.brain_ready is not None and self.brain_ready.done() else "loading"
        if time.monotonic() < self.resume_audio_at:
            return "cooldown"
        return "active"

    def publish_microphone(self):
        if self.preview is not None:
            data = self.microphone_meter.snapshot()
            data.update(source="laptop" if self.microphone is not None else "esp32",
                        status=self.microphone_status(), threshold=self.endpoint.threshold,
                        gaps=self.mic_gaps)
            self.preview.publish_microphone(data)

    async def monitor_microphone(self):
        while True:
            self.publish_microphone()
            await asyncio.sleep(2)
            level, peak, packets = self.microphone_meter.take_window()
            ac, dc = self.microphone_meter.take_bias_window()
            status = self.microphone_status()
            db = f"{20 * math.log10(level):.1f}" if level else "-inf"
            log.info("Mic [%s]: RMS %.3f%% | peak %.3f%% | AC RMS %.3f%% | DC %.3f%% | %s dBFS | threshold %.2f%% | %d packets/2s | gaps=%d",
                     status, level * 100, peak * 100, ac * 100, dc * 100, db,
                     self.endpoint.threshold * 100, packets, self.mic_gaps)

    async def listen(self):
        try:
            if self.brain_ready is not None:
                self.brain = await asyncio.shield(self.brain_ready)
            if self.brain is not None and self.microphone is None:
                log.info("ESP32 microphone ready; speak into the INMP441")
            if (self.brain is not None or self.mic_test) and self.microphone is not None:
                async for pcm, captured_at, gap in self.microphone.chunks():
                    if gap:
                        self.endpoint.reset()
                        log.warning("Microphone overflow: discarded stale audio")
                    self.feed_audio(pcm, captured_at)
        except Exception:
            log.exception("Laptop microphone unavailable; camera tracking continues")
        # A failed/stopped microphone must not end the camera's session.
        await asyncio.Future()

    async def receive(self):
        async for message in self.ws:
            try:
                if isinstance(message, str):
                    if len(message) > 512:
                        raise ValueError("Device notice too large")
                    notice = json.loads(message)
                    if isinstance(notice, dict) and set(notice) == {"device_status"}:
                        status = notice["device_status"]
                        fields = {"uptime_ms", "wifi_drops", "wifi_reason", "ws_drops", "rssi", "heap", "reset"}
                        if not isinstance(status, dict) or set(status) != fields or any(type(value) is not int for value in status.values()):
                            raise ValueError("Invalid device status")
                        previous = self.device_status
                        if previous is None or any(status[key] != previous[key] for key in ("wifi_drops", "ws_drops")):
                            resets = {1: "power-on", 3: "software restart", 4: "crash", 5: "interrupt watchdog", 6: "task watchdog", 7: "watchdog", 9: "brownout"}
                            log.info("ESP32 health: uptime=%.1fs | Wi-Fi drops=%d reason=%d | host drops=%d | RSSI=%d dBm | heap=%d | boot=%s",
                                     status["uptime_ms"] / 1000, status["wifi_drops"], status["wifi_reason"],
                                     status["ws_drops"], status["rssi"], status["heap"], resets.get(status["reset"], str(status["reset"])))
                        self.device_status = status
                        continue
                    if notice == {"mic_gap": True} and self.microphone is None:
                        self.mic_gaps += 1
                        interrupted = bool(self.endpoint.buffer) and not self.busy
                        self.endpoint.reset()
                        if interrupted:
                            self.control.state = "idle"
                            self.control_changed.set()
                            log.warning("ESP32 microphone overflow: speech interrupted; please repeat")
                        else:
                            log.debug("ESP32 microphone gap during silence or a response")
                        continue
                    raise ValueError("Unexpected device notice")
                tag, payload = unpack(message)
                if tag == VIDEO:
                    if self.frames.full():
                        self.frames.get_nowait()
                        self.frames_dropped += 1
                    self.frames.put_nowait(payload)
                elif tag == MIC and self.microphone is None:
                    self.feed_audio(payload)
                elif tag != MIC:
                    raise ValueError("Unexpected inbound tag")
            except (ValueError, TypeError):
                self.invalid += 1
                if self.invalid >= 20:
                    await self.ws.close(code=1008, reason="Too many invalid packets")
                    return

    async def track(self):
        while True:
            jpeg = await self.frames.get()
            started = time.monotonic()
            try:
                faces, width, height = await asyncio.to_thread(self.vision.detect, jpeg)
                self.control.gaze_x, self.control.gaze_y = self.gaze.update(faces, width, height)
                self.last_frame = time.monotonic()
                self.frames_processed += 1
                self.tracking_ms = (time.monotonic() - started) * 1000
                if self.preview is not None:
                    self.preview.publish(jpeg, faces, width, height,
                                         self.control.gaze_x, self.control.gaze_y, self.gaze.mirror)
            except ValueError:
                log.warning("Rejected undecodable camera frame")
            finally:
                # Acknowledge even rejected images so the device cannot stall.
                self.frame_ack += 1
                self.control_changed.set()

    async def controls(self):
        while True:
            self.control_changed.clear()
            if not self.busy and time.monotonic() - self.last_audio > 2:
                self.endpoint.reset()
            if not self.busy and not self.endpoint.buffer:
                self.control.state = "sleeping" if time.monotonic() - self.last_frame > 3 else "idle"
            control = json.loads(self.control.encode())
            control["frame_ack"] = self.frame_ack
            control["device_health"] = True
            control["mic_enabled"] = (self.microphone is None and self.brain is not None
                                      and not self.busy and time.monotonic() >= self.resume_audio_at)
            if self.mic_test and self.microphone is None:
                control["mic_enabled"] = True
            if self.speaker_output == "laptop":
                control["speaker_local"] = True
            async with asyncio.timeout(SOCKET_SEND_TIMEOUT):
                await self.ws.send(json.dumps(control, separators=(",", ":")))
            self.publish_microphone()
            # Wake immediately after tracking/state changes; otherwise send
            # only a keepalive, rather than filling the ESP32 with stale gaze.
            with contextlib.suppress(asyncio.TimeoutError):
                # timeout() preserves cancellation when a control event and
                # disconnect arrive together (wait_for() can swallow it).
                async with asyncio.timeout(.5):
                    await self.control_changed.wait()

    async def speak(self):
        while True:
            utterance = await self.utterances.get()
            try:
                # A cancelled thread still finishes under LocalBrain's lock;
                # the display and microphone must not wait indefinitely for it.
                async with asyncio.timeout(VOICE_RESPONSE_TIMEOUT):
                    pcm = await asyncio.to_thread(self.brain.respond, utterance)
                if not pcm:
                    log.info("No response audio to play; returning to listening")
                    continue
                self.control.state = "talking"
                self.control_changed.set()
                if self.speaker_output == "laptop":
                    speaker = LaptopSpeaker(self.speaker_device)
                    async with contextlib.aclosing(speaker.play(pcm)) as playback:
                        async for chunk in playback:
                            self.control.mouth_wave = min(1, rms(chunk) * 5)
                            self.control_changed.set()
                else:
                    # External MAX98357A: send PCM16 paced at 16 kHz.
                    for offset in range(0, len(pcm), 1024):
                        chunk = pcm[offset:offset + 1024]
                        self.control.mouth_wave = min(1, rms(chunk) * 5)
                        self.control_changed.set()
                        async with asyncio.timeout(SOCKET_SEND_TIMEOUT):
                            await self.ws.send(pack(SPEAKER, chunk))
                        # Do not burst overdue packets into the board after a slow send.
                        await asyncio.sleep(len(chunk) / 32000)
                await asyncio.sleep(0.15)
            except asyncio.TimeoutError:
                log.error("Voice response timed out; returning to idle. Check the last recognition/reply/speech log to locate the stalled stage")
            except Exception:
                log.exception("Voice response failed")
            finally:
                self.control.state = "idle"
                self.control.mouth_wave = 0
                self.endpoint.reset()
                self.busy = False
                self.resume_audio_at = time.monotonic() + .35
                self.control_changed.set()

    async def run(self):
        workers = [asyncio.create_task(fn()) for fn in (self.receive, self.track, self.controls, self.speak)]
        if self.microphone is not None or self.brain_ready is not None:
            workers.append(asyncio.create_task(self.listen()))
        if self.voice_enabled:
            workers.append(asyncio.create_task(self.monitor_microphone()))
        try:
            done, _ = await asyncio.wait(workers, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                task.result()
        finally:
            for task in workers:
                task.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
            log.info("Session ended: processed=%d dropped=%d invalid=%d mic_gaps=%d last_tracking=%.1fms", self.frames_processed, self.frames_dropped, self.invalid, self.mic_gaps, self.tracking_ms)


async def serve(args):
    from websockets.asyncio.server import serve as websocket_serve
    from websockets.exceptions import ConnectionClosed
    voice_task = None

    async def load_voice():
        from .brain import LocalBrain
        try:
            log.info("Loading voice models in the background; first use may download weights")
            brain = await asyncio.to_thread(LocalBrain, args.whisper_model, args.ollama_url, args.ollama_model, args.tts_model)
            log.info("Voice models ready; microphone input=%s", getattr(args, "mic_source", "esp32"))
            return brain
        except Exception:
            log.exception("Voice models unavailable; camera tracking continues")
            return None
    # One wall device per host bounds camera and model resource use.
    vision = await asyncio.to_thread(Vision)
    active_task = active_ws = None
    preview = Preview()

    async def handler(ws):
        nonlocal active_task, active_ws
        if active_task is not None:
            if active_ws.remote_address[0] != ws.remote_address[0]:
                await ws.close(code=1013, reason="One wall device per host")
                return
            # A reconnect from the same device may arrive before the old TCP
            # connection times out. Retire it instead of rejecting reconnects.
            previous_task, previous_ws = active_task, active_ws
            log.info("Replacing stale device connection from %s", ws.remote_address[0])
            previous_task.cancel()
            await asyncio.gather(previous_task, return_exceptions=True)
            await previous_ws.close(code=1012, reason="Device reconnected")
            # Another reconnect can arrive while the previous close awaits.
            if active_task is not None:
                await ws.close(code=1013, reason="Reconnect already in progress")
                return
        active_task, active_ws = asyncio.current_task(), ws
        preview.connect()
        try:
            use_laptop = getattr(args, "mic_source", "esp32") == "laptop"
            mic_test = getattr(args, "mic_test", False)
            microphone = LaptopMicrophone(getattr(args, "mic_device", None)) if (args.voice or mic_test) and use_laptop else None
            session = Session(ws, vision, mirror=args.mirror, preview=preview,
                              microphone=microphone, brain_ready=voice_task,
                              speaker_output=getattr(args, "speaker_output", "esp32"),
                              speaker_device=getattr(args, "speaker_device", None), mic_test=mic_test,
                              mic_threshold=getattr(args, "mic_threshold", .015))
            try:
                await session.run()
            except ConnectionClosed as error:
                log.info("Device disconnected: %s", error)
        finally:
            if active_task is asyncio.current_task():
                preview.disconnect()
                active_task = active_ws = None

    async with websocket_serve(handler, args.bind, args.port, max_size=262145,
                               max_queue=8, compression=None, ping_interval=20,
                               ping_timeout=30, close_timeout=1):
        with PreviewServer(preview, args.bind, args.preview_port):
            log.info("Iris listening on %s:%d; voice=%s", args.bind, args.port, args.voice)
            log.info("Camera preview: http://localhost:%d", args.preview_port)
            if args.voice:
                log.info("Voice input: %s; output: %s", getattr(args, "mic_source", "esp32"),
                         getattr(args, "speaker_output", "esp32"))
            if getattr(args, "mic_test", False):
                log.info("Microphone test mode: level meter only; AI models and replies are disabled")
            if args.voice and not getattr(args, "mic_test", False):
                voice_task = asyncio.create_task(load_voice())
            try:
                await asyncio.Future()
            finally:
                if voice_task is not None:
                    voice_task.cancel()
                    await asyncio.gather(voice_task, return_exceptions=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Path to host JSON configuration")
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--preview-port", type=int, default=8080, help="HTTP camera preview port")
    parser.add_argument("--mirror", action="store_true")
    parser.add_argument("--voice", action="store_true")
    parser.add_argument("--no-voice", action="store_false", dest="voice", help="Camera/display only")
    parser.set_defaults(voice=False)
    parser.add_argument("--mic-test", action="store_true", help="Show microphone levels without loading AI models or replying")
    parser.add_argument("--mic-source", choices=("esp32", "laptop"), default="esp32",
                        help="Speech input: external INMP441 or laptop microphone")
    parser.add_argument("--mic-device", help="Laptop input device index or name; default is Windows' microphone")
    parser.add_argument("--mic-threshold", type=float, default=.015,
                        help="Speech trigger RMS as a fraction of full scale: 0.45 means 45 percent")
    parser.add_argument("--speaker-output", choices=("laptop", "esp32"), default="esp32",
                        help="Speech destination: external MAX98357A or laptop speakers")
    parser.add_argument("--speaker-device", help="Laptop output device index or name; default is Windows' output")
    parser.add_argument("--whisper-model", default="base")
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument("--ollama-model", default="llama3.2")
    parser.add_argument("--tts-model", default="tts_models/en/ljspeech/tacotron2-DDC")
    preliminary, _ = parser.parse_known_args()
    if preliminary.config:
        try:
            with open(preliminary.config, encoding="utf-8") as file:
                settings = json.load(file)
            allowed = {"bind", "port", "preview_port", "mirror", "voice", "mic_source", "mic_device", "mic_threshold", "speaker_output", "speaker_device", "whisper_model", "ollama_url", "ollama_model", "tts_model"}
            if not isinstance(settings, dict) or settings.keys() - allowed:
                raise ValueError("Unknown configuration fields")
            parser.set_defaults(**settings)
        except (OSError, ValueError) as error:
            parser.error(str(error))
    logging.basicConfig(level=logging.INFO)
    try:
        args = parser.parse_args()
        try:
            Endpoint(threshold=args.mic_threshold)
        except ValueError as error:
            parser.error(str(error))
        if args.mic_source not in ("laptop", "esp32"):
            parser.error("mic_source must be laptop or esp32")
        if args.speaker_output not in ("laptop", "esp32"):
            parser.error("speaker_output must be laptop or esp32")
        if isinstance(args.mic_device, str) and args.mic_device.isdecimal():
            args.mic_device = int(args.mic_device)
        if isinstance(args.speaker_device, str) and args.speaker_device.isdecimal():
            args.speaker_device = int(args.speaker_device)
        asyncio.run(serve(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
