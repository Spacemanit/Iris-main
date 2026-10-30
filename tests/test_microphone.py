import asyncio
import json
import threading
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import cv2
import numpy as np
from websockets.asyncio.client import connect
from websockets.asyncio.server import serve

from iris.microphone import LaptopMicrophone
from iris.protocol import SPEAKER, VIDEO, pack, unpack
from iris.server import Session


class MicrophoneTests(unittest.IsolatedAsyncioTestCase):
    async def test_native_sample_rate_fallback_and_stream_cleanup(self):
        opened = threading.Event()
        streams = []

        class FakeStream:
            def __init__(self, **kwargs):
                self.callback = kwargs["callback"]
                self.active = False
                self.closed = False
                streams.append(self)

            def start(self):
                self.active = True
                opened.set()

            def stop(self):
                self.active = False

            def close(self):
                self.closed = True

        def settings(**kwargs):
            if kwargs["samplerate"] == 16000:
                raise RuntimeError("Native input rate required")

        fake = SimpleNamespace(query_devices=lambda *a: {"name": "Test mic", "default_samplerate": 48000},
                               PortAudioError=RuntimeError, check_input_settings=settings,
                               RawInputStream=FakeStream)
        with patch.dict("sys.modules", sounddevice=fake):
            mic = LaptopMicrophone()
            chunks = mic.chunks()
            waiting = asyncio.create_task(anext(chunks))
            try:
                self.assertTrue(await asyncio.to_thread(opened.wait, 8))
                pcm = np.full(1536, 1000, dtype="<i2").tobytes()
                await asyncio.to_thread(streams[0].callback, pcm, 1536, None, False)
                converted, stamp, gap = await asyncio.wait_for(waiting, 5)
                self.assertEqual(len(converted), 1024)
                self.assertAlmostEqual(float(np.median(np.frombuffer(converted, dtype="<i2"))), 1000, delta=2)
                self.assertFalse(gap)
                self.assertLessEqual(stamp, time.monotonic())
                # An overloaded consumer keeps a bounded, recent audio queue.
                for _ in range(20):
                    streams[0].callback(pcm, 1536, None, False)
                self.assertLessEqual(mic.pending.qsize(), 8)
                _, _, gap = await asyncio.wait_for(anext(chunks), 2)
                self.assertTrue(gap)
            finally:
                waiting.cancel()
                await asyncio.gather(waiting, return_exceptions=True)
                await chunks.aclose()
            self.assertTrue(streams[0].closed)
            self.assertIsNone(mic.stream)

    async def test_laptop_speech_playback_keeps_camera_responsive_and_ignores_echo(self):
        started, closed = asyncio.Event(), asyncio.Event()
        incoming = asyncio.Queue()
        responding, release = threading.Event(), threading.Event()
        calls = []
        sessions = []
        reply = np.full(1024, 3000, dtype="<i2").tobytes()

        class Source:
            async def chunks(self):
                started.set()
                try:
                    while True:
                        yield await incoming.get()
                finally:
                    closed.set()

        class Brain:
            def respond(self, pcm):
                calls.append(pcm)
                responding.set()
                if not release.wait(3):
                    raise RuntimeError("Test voice worker not released")
                return reply

        class Detector:
            def detect(self, jpeg):
                return [(200, 80, 50, 50)], 320, 240

        async def handler(ws):
            session = Session(ws, Detector(), brain=Brain(), microphone=Source())
            sessions.append(session)
            await session.run()

        async def control_until(device, predicate):
            for _ in range(20):
                message = await asyncio.wait_for(device.recv(), 2)
                if isinstance(message, str):
                    control = json.loads(message)
                    if predicate(control):
                        return control
            self.fail("Expected control was not received")

        speech = np.full(512, 5000, dtype="<i2").tobytes()
        silence = bytes(1024)
        try:
            async with serve(handler, "127.0.0.1", 0) as server:
                port = server.sockets[0].getsockname()[1]
                async with connect(f"ws://127.0.0.1:{port}") as device:
                    await asyncio.wait_for(started.wait(), 2)
                    await incoming.put((speech, time.monotonic(), False))
                    await control_until(device, lambda c: c["state"] == "listening")
                    await incoming.put((speech, time.monotonic(), False))
                    for _ in range(19):
                        await incoming.put((silence, time.monotonic(), False))
                    await control_until(device, lambda c: c["state"] == "thinking")
                    self.assertTrue(await asyncio.to_thread(responding.wait, 2))
                    echo_time = time.monotonic()
                    await incoming.put((speech, echo_time, False))
                    jpeg = cv2.imencode(".jpg", np.zeros((240, 320, 3), dtype=np.uint8))[1].tobytes()
                    await device.send(pack(VIDEO, jpeg))
                    control = await control_until(device, lambda c: c["frame_ack"] == 1)
                    self.assertEqual(control["state"], "thinking")
                    pong = await device.ping()
                    await asyncio.wait_for(pong, 1)
                    release.set()
                    playback = bytearray()
                    for _ in range(20):
                        message = await asyncio.wait_for(device.recv(), 2)
                        if isinstance(message, bytes):
                            tag, pcm = unpack(message)
                            self.assertEqual(tag, SPEAKER)
                            playback.extend(pcm)
                        elif playback and json.loads(message)["state"] == "idle":
                            break
                    self.assertEqual(playback, reply)
                    self.assertEqual(len(calls), 1)
                    # Audio captured during a response is ignored even if its
                    # delivery occurs after playback completes.
                    await incoming.put((speech, echo_time, False))
                    await asyncio.sleep(.05)
                    self.assertFalse(sessions[0].endpoint.buffer)
                await asyncio.wait_for(closed.wait(), 2)
        finally:
            release.set()

    async def test_microphone_failure_does_not_disconnect_camera(self):
        class BrokenSource:
            async def chunks(self):
                raise RuntimeError("Input device unavailable")
                yield  # Make this an async generator.

        class Detector:
            def detect(self, jpeg):
                return [], 320, 240

        async def handler(ws):
            await Session(ws, Detector(), brain=object(), microphone=BrokenSource()).run()

        with self.assertLogs("iris", level="ERROR") as logs:
            async with serve(handler, "127.0.0.1", 0) as server:
                port = server.sockets[0].getsockname()[1]
                async with connect(f"ws://127.0.0.1:{port}") as device:
                    jpeg = cv2.imencode(".jpg", np.zeros((240, 320, 3), dtype=np.uint8))[1].tobytes()
                    await device.send(pack(VIDEO, jpeg))
                    for _ in range(10):
                        control = json.loads(await asyncio.wait_for(device.recv(), 2))
                        if control["frame_ack"] == 1:
                            break
                    self.assertEqual(control["frame_ack"], 1)
            self.assertIn("camera tracking continues", logs.output[0])

    async def test_model_loading_and_reconnect_preserve_camera_and_shared_loader(self):
        brain_ready = asyncio.get_running_loop().create_future()
        mic_started = asyncio.Event()

        class Source:
            async def chunks(self):
                mic_started.set()
                await asyncio.Future()
                yield

        class Detector:
            def detect(self, jpeg):
                return [], 320, 240

        async def handler(ws):
            await Session(ws, Detector(), microphone=Source(), brain_ready=brain_ready).run()

        async with serve(handler, "127.0.0.1", 0) as server:
            port = server.sockets[0].getsockname()[1]
            async with connect(f"ws://127.0.0.1:{port}") as device:
                jpeg = cv2.imencode(".jpg", np.zeros((240, 320, 3), dtype=np.uint8))[1].tobytes()
                await device.send(pack(VIDEO, jpeg))
                for _ in range(10):
                    control = json.loads(await asyncio.wait_for(device.recv(), 2))
                    if control["frame_ack"] == 1:
                        break
                self.assertEqual(control["frame_ack"], 1)
                self.assertFalse(mic_started.is_set())
            await asyncio.sleep(.05)
            self.assertFalse(brain_ready.done())
            async with connect(f"ws://127.0.0.1:{port}") as replacement:
                await asyncio.wait_for(replacement.recv(), 2)
                brain_ready.set_result(object())
                await asyncio.wait_for(mic_started.wait(), 2)
                pong = await replacement.ping()
                await asyncio.wait_for(pong, 1)


if __name__ == "__main__":
    unittest.main()
