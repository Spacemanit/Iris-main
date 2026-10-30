import asyncio
import json
import threading
import time
import unittest
from argparse import Namespace
from contextlib import asynccontextmanager
from unittest.mock import Mock, AsyncMock, patch

import cv2
import numpy as np
from websockets.asyncio.client import connect
from websockets.asyncio.server import serve

from iris.protocol import MIC, VIDEO, SPEAKER, pack, unpack
from iris.server import Session, serve as run_host
from iris.preview import Preview


class DeviceAudioTests(unittest.IsolatedAsyncioTestCase):
    async def test_stalled_inference_returns_to_idle_while_camera_controls_continue(self):
        started, release = threading.Event(), threading.Event()

        class SlowBrain:
            def respond(self, pcm):
                started.set()
                release.wait(3)
                return b""

        socket = Mock(send=AsyncMock())
        session = Session(socket, object(), brain=SlowBrain())
        session.busy = True
        session.control.state = "thinking"
        session.utterances.put_nowait(bytes(20480))
        with patch("iris.server.VOICE_RESPONSE_TIMEOUT", .1):
            worker = asyncio.create_task(session.speak())
            controls = asyncio.create_task(session.controls())
            try:
                with self.assertLogs("iris", level="ERROR") as logs:
                    for _ in range(100):
                        if started.is_set() and not session.busy:
                            break
                        await asyncio.sleep(.01)
                self.assertFalse(session.busy)
                self.assertEqual(session.control.state, "idle")
                self.assertTrue(session.utterances.empty())
                self.assertEqual(session.control.mouth_wave, 0)
                self.assertIn("timed out", logs.output[0])
                for _ in range(20):
                    if any(json.loads(call.args[0])["state"] == "idle" for call in socket.send.call_args_list):
                        break
                    await asyncio.sleep(.01)
                states = [json.loads(call.args[0])["state"] for call in socket.send.call_args_list]
                self.assertIn("thinking", states)
                self.assertIn("idle", states)
            finally:
                release.set()
                worker.cancel()
                controls.cancel()
                await asyncio.gather(worker, controls, return_exceptions=True)

    async def test_health_notices_do_not_break_audio_session_and_report_drop_changes(self):
        health = dict(uptime_ms=240000, wifi_drops=1, wifi_reason=200,
                      ws_drops=2, rssi=-68, heap=110000, reset=9)

        class HealthSocket:
            async def __aiter__(self):
                yield json.dumps({"device_status": health})
                yield json.dumps({"device_status": health})
                yield json.dumps({"device_status": dict(health, ws_drops=3)})
                yield json.dumps({"device_status": dict(health, rssi="bad")})

        session = Session(HealthSocket(), object())
        with self.assertLogs("iris", level="INFO") as logs:
            await session.receive()
        self.assertEqual(session.invalid, 1)
        self.assertEqual(session.device_status["ws_drops"], 3)
        self.assertEqual(len(logs.output), 2)
        self.assertIn("boot=brownout", logs.output[0])
        self.assertIn("host drops=3", logs.output[1])

    async def test_empty_response_does_not_enter_playback_or_send_speaker_data(self):
        class EmptyBrain:
            def respond(self, pcm):
                return b""

        socket = Mock()
        session = Session(socket, object(), brain=EmptyBrain())
        session.busy = True
        session.control.state = "thinking"
        session.utterances.put_nowait(bytes(20480))
        worker = asyncio.create_task(session.speak())
        try:
            for _ in range(100):
                if not session.busy:
                    break
                await asyncio.sleep(.01)
            self.assertFalse(session.busy)
            self.assertEqual(session.control.state, "idle")
            socket.send.assert_not_called()
        finally:
            worker.cancel()
            await asyncio.gather(worker, return_exceptions=True)

    async def test_configured_threshold_rejects_quiet_noise_and_ends_speech_after_noise(self):
        class NoticeSocket:
            async def __aiter__(self):
                yield '{"mic_gap":true}'

        session = Session(NoticeSocket(), object(), brain=object(), mic_threshold=.45)
        quiet = np.full(512, round(.35 * 32768), dtype="<i2").tobytes()
        speech = np.full(512, round(.6 * 32768), dtype="<i2").tobytes()
        for _ in range(65):
            session.feed_audio(quiet)
        self.assertFalse(session.endpoint.buffer)
        self.assertTrue(session.utterances.empty())
        with self.assertNoLogs("iris", level="WARNING"):
            await session.receive()
        self.assertEqual(session.mic_gaps, 1)
        session.feed_audio(speech)
        self.assertEqual(session.control.state, "listening")
        for _ in range(19):
            session.feed_audio(quiet)
        self.assertEqual(session.control.state, "thinking")
        self.assertEqual(session.utterances.get_nowait(), speech + quiet * 19)

    async def test_microphone_test_mode_receives_levels_without_ai_models_or_replies(self):
        ready = asyncio.get_running_loop().create_future()
        preview = Preview()

        @asynccontextmanager
        async def start_server(*args, **kwargs):
            async with serve(*args, **kwargs) as server:
                ready.set_result(server.sockets[0].getsockname()[1])
                yield server

        class Detector:
            def detect(self, jpeg):
                return [], 320, 240

        args = Namespace(bind="127.0.0.1", port=0, preview_port=0, voice=True,
                         mic_test=True, mirror=False, mic_source="esp32", speaker_output="esp32",
                         mic_threshold=.45)
        with patch("websockets.asyncio.server.serve", start_server), \
             patch("iris.server.Vision", Detector), patch("iris.server.Preview", return_value=preview), \
             patch("iris.brain.LocalBrain") as brain, patch("iris.server.LaptopMicrophone") as laptop_mic:
            host = asyncio.create_task(run_host(args))
            try:
                port = await asyncio.wait_for(ready, 3)
                async with connect(f"ws://127.0.0.1:{port}") as device:
                    control = json.loads(await asyncio.wait_for(device.recv(), 2))
                    self.assertTrue(control["mic_enabled"])
                    await device.send(pack(MIC, np.full(512, 8192, dtype="<i2").tobytes()))
                    for _ in range(50):
                        if preview.snapshot()["microphone"]["packets"]:
                            break
                        await asyncio.sleep(.01)
                    levels = preview.snapshot()["microphone"]
                    self.assertEqual(levels["packets"], 1)
                    self.assertEqual(levels["rms"], .25)
                    self.assertEqual(levels["status"], "test")
                    self.assertEqual(levels["source"], "esp32")
                    self.assertEqual(levels["threshold"], .45)
                    # Test mode never starts an AI reply, even above threshold.
                    control = json.loads(await asyncio.wait_for(device.recv(), 2))
                    self.assertTrue(control["mic_enabled"])
                    self.assertNotEqual(control["state"], "thinking")
                    brain.assert_not_called()
                    laptop_mic.assert_not_called()
            finally:
                host.cancel()
                await asyncio.gather(host, return_exceptions=True)

    async def test_gap_warns_only_when_speech_is_interrupted_and_resets_display_state(self):
        class NoticeSocket:
            async def __aiter__(self):
                yield '{"mic_gap":true}'

        session = Session(NoticeSocket(), object(), brain=object())
        # Gaps during silence are counted, but are not user-facing failures.
        with self.assertNoLogs("iris", level="WARNING"):
            await session.receive()
        self.assertEqual(session.mic_gaps, 1)
        self.assertEqual(session.invalid, 0)
        speech = np.full(512, 5000, dtype="<i2").tobytes()
        session.feed_audio(speech)
        self.assertEqual(session.control.state, "listening")
        session.control_changed.clear()
        with self.assertLogs("iris", level="WARNING") as logs:
            await session.receive()
        self.assertIn("speech interrupted", logs.output[0])
        self.assertFalse(session.endpoint.buffer)
        self.assertEqual(session.control.state, "idle")
        self.assertTrue(session.control_changed.is_set())
        # Delayed notices during a response must not change its state.
        session.busy = True
        session.control.state = "talking"
        with self.assertNoLogs("iris", level="WARNING"):
            await session.receive()
        self.assertEqual(session.control.state, "talking")
        self.assertEqual(session.mic_gaps, 3)

    async def test_external_microphone_model_loading_playback_and_echo_suppression(self):
        ready = asyncio.get_running_loop().create_future()
        load_started, load_release = threading.Event(), threading.Event()
        response_started, response_release = threading.Event(), threading.Event()
        utterances = []
        reply = np.full(1024, 3000, dtype="<i2").tobytes()

        @asynccontextmanager
        async def start_server(*args, **kwargs):
            async with serve(*args, **kwargs) as server:
                ready.set_result(server.sockets[0].getsockname()[1])
                yield server

        class Brain:
            def __init__(self, *args):
                load_started.set()
                if not load_release.wait(5):
                    raise RuntimeError("Model loader not released")

            def respond(self, pcm):
                utterances.append(pcm)
                response_started.set()
                if not response_release.wait(5):
                    raise RuntimeError("Voice response not released")
                return reply

        class Detector:
            def detect(self, jpeg):
                return [], 320, 240

        async def until(device, predicate):
            for _ in range(30):
                control = json.loads(await asyncio.wait_for(device.recv(), 2))
                if predicate(control):
                    return control
            self.fail("Expected control not received")

        args = Namespace(bind="127.0.0.1", port=0, preview_port=0, voice=True,
                         mirror=False, mic_source="esp32", speaker_output="esp32",
                         whisper_model="base", ollama_url="http://localhost:11434",
                         ollama_model="test", tts_model="test")
        speech = np.full(512, 5000, dtype="<i2").tobytes()
        silence = bytes(1024)
        jpeg = cv2.imencode(".jpg", np.zeros((240, 320, 3), dtype=np.uint8))[1].tobytes()
        with patch("websockets.asyncio.server.serve", start_server), \
             patch("iris.server.Vision", Detector), patch("iris.brain.LocalBrain", Brain), \
             patch("iris.server.LaptopMicrophone") as laptop_mic, \
             patch("iris.server.LaptopSpeaker") as laptop_speaker:
            host = asyncio.create_task(run_host(args))
            try:
                port = await asyncio.wait_for(ready, 3)
                async with connect(f"ws://127.0.0.1:{port}") as device:
                    self.assertTrue(await asyncio.to_thread(load_started.wait, 2))
                    control = await until(device, lambda c: not c["mic_enabled"])
                    await device.send(pack(VIDEO, jpeg))
                    await until(device, lambda c: c["frame_ack"] == 1)
                    load_release.set()
                    await until(device, lambda c: c["mic_enabled"])
                    await device.send(pack(MIC, speech))
                    await until(device, lambda c: c["state"] == "listening")
                    # A gap resets an incomplete utterance before fresh speech.
                    await device.send('{"mic_gap":true}')
                    await device.send(pack(MIC, speech))
                    for _ in range(19):
                        await device.send(pack(MIC, silence))
                    control = await until(device, lambda c: c["state"] == "thinking")
                    self.assertFalse(control["mic_enabled"])
                    self.assertTrue(await asyncio.to_thread(response_started.wait, 2))
                    self.assertEqual(utterances, [speech + silence * 19])
                    await device.send(pack(MIC, speech))  # Ignored during inference.
                    await device.send(pack(VIDEO, jpeg))
                    await until(device, lambda c: c["frame_ack"] == 2)
                    pong = await device.ping()
                    await asyncio.wait_for(pong, 1)
                    response_release.set()
                    playback = bytearray()
                    for _ in range(30):
                        message = await asyncio.wait_for(device.recv(), 2)
                        if isinstance(message, bytes):
                            tag, pcm = unpack(message)
                            self.assertEqual(tag, SPEAKER)
                            playback.extend(pcm)
                        else:
                            control = json.loads(message)
                            if control["state"] == "talking":
                                self.assertFalse(control["mic_enabled"])
                            if playback and control["state"] == "idle":
                                self.assertFalse(control["mic_enabled"])
                                break
                    self.assertEqual(playback, reply)
                    await device.send(pack(MIC, speech))  # Ignored during cooldown.
                    await until(device, lambda c: c["mic_enabled"])
                    self.assertEqual(len(utterances), 1)
                    self.assertEqual(control["state"], "idle")
                    laptop_mic.assert_not_called()
                    laptop_speaker.assert_not_called()
            finally:
                load_release.set()
                response_release.set()
                host.cancel()
                await asyncio.gather(host, return_exceptions=True)
