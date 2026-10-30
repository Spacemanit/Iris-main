import asyncio
import json
import threading
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import cv2
from websockets.asyncio.client import connect
from websockets.asyncio.server import serve

from iris.protocol import VIDEO, pack
from iris.server import Session
from iris.speaker import LaptopSpeaker


class SpeakerTests(unittest.IsolatedAsyncioTestCase):
    async def test_laptop_output_sends_controls_without_speaker_packets(self):
        streams = []
        entered, release = threading.Event(), threading.Event()
        sessions = []
        reply = np.full(2048, 3000, dtype="<i2").tobytes()

        class Stream:
            def __init__(self, **kwargs):
                self.settings = kwargs
                self.data = bytearray()
                self.stopped = self.closed = False
                streams.append(self)

            def start(self):
                pass

            def write(self, data):
                entered.set()
                if not release.wait(3):
                    raise RuntimeError("Test write not released")
                self.data.extend(data)
                time.sleep(.032)

            def stop(self):
                self.stopped = True

            def abort(self):
                pass

            def close(self):
                self.closed = True

        fake = SimpleNamespace(
            query_devices=lambda *a: {"name": "Test speakers", "default_samplerate": 16000,
                                      "max_output_channels": 2},
            check_output_settings=lambda **k: None, RawOutputStream=Stream)

        class Brain:
            def respond(self, pcm):
                return reply

        class Detector:
            def detect(self, jpeg):
                return [(200, 80, 50, 50)], 320, 240

        async def handler(ws):
            session = Session(ws, Detector(), brain=Brain(), speaker_output="laptop")
            sessions.append(session)
            await session.run()

        async def until(device, predicate):
            for _ in range(30):
                message = await asyncio.wait_for(device.recv(), 2)
                self.assertIsInstance(message, str, "Laptop output must send no speaker PCM")
                control = json.loads(message)
                self.assertTrue(control["speaker_local"])
                if predicate(control):
                    return control
            self.fail("Expected speech control was not received")

        try:
            with patch.dict("sys.modules", sounddevice=fake):
                async with serve(handler, "127.0.0.1", 0) as server:
                    port = server.sockets[0].getsockname()[1]
                    async with connect(f"ws://127.0.0.1:{port}") as device:
                        await until(device, lambda c: c["frame_ack"] == 0)
                        sessions[0].busy = True
                        sessions[0].utterances.put_nowait(b"speech")
                        self.assertTrue(await asyncio.to_thread(entered.wait, 2))
                        # A blocking audio driver must not delay camera processing/pings.
                        jpeg = cv2.imencode(".jpg", np.zeros((240, 320, 3), dtype=np.uint8))[1].tobytes()
                        await device.send(pack(VIDEO, jpeg))
                        await until(device, lambda c: c["frame_ack"] == 1)
                        pong = await device.ping()
                        await asyncio.wait_for(pong, 1)
                        release.set()
                        await until(device, lambda c: c["state"] == "talking" and c["mouth_wave"] > 0)
                        await until(device, lambda c: c["state"] == "idle")
                        self.assertEqual(streams[0].data,
                                         np.repeat(np.frombuffer(reply, dtype="<i2"), 2).tobytes())
                        self.assertTrue(streams[0].stopped)
                        self.assertTrue(streams[0].closed)
                        self.assertFalse(sessions[0].busy)
        finally:
            release.set()

    async def test_disconnect_waits_for_inflight_write_then_aborts_output(self):
        entered, release = threading.Event(), threading.Event()
        streams = []

        class Stream:
            def __init__(self, **kwargs):
                self.aborted = self.closed = False
                streams.append(self)

            def start(self):
                pass

            def write(self, data):
                entered.set()
                release.wait(3)

            def stop(self):
                raise AssertionError("Interrupted playback must not drain the entire response")

            def abort(self):
                self.aborted = True

            def close(self):
                self.closed = True

        fake = SimpleNamespace(
            query_devices=lambda *a: {"name": "Test output", "default_samplerate": 16000,
                                      "max_output_channels": 1},
            check_output_settings=lambda **k: None, RawOutputStream=Stream)

        async def play():
            async for _ in LaptopSpeaker().play(bytes(32000)):
                pass

        with patch.dict("sys.modules", sounddevice=fake):
            task = asyncio.create_task(play())
            try:
                self.assertTrue(await asyncio.to_thread(entered.wait, 2))
                task.cancel()
                await asyncio.sleep(.03)
                self.assertFalse(streams[0].closed)
                release.set()
                with self.assertRaises(asyncio.CancelledError):
                    await asyncio.wait_for(task, 2)
                self.assertTrue(streams[0].aborted)
                self.assertTrue(streams[0].closed)
            finally:
                release.set()
                await asyncio.gather(task, return_exceptions=True)

    async def test_native_rate_resampling_preserves_duration_and_level(self):
        streams = []

        class Stream:
            def __init__(self, **kwargs):
                self.settings = kwargs
                self.data = bytearray()
                self.closed = False
                streams.append(self)

            def start(self):
                pass

            def write(self, data):
                self.data.extend(data)

            def stop(self):
                pass

            def close(self):
                self.closed = True

        fake = SimpleNamespace(
            query_devices=lambda *a: {"name": "Native rate output", "default_samplerate": 48000,
                                      "max_output_channels": 2},
            check_output_settings=lambda **k: None, RawOutputStream=Stream)
        with patch.dict("sys.modules", sounddevice=fake):
            pcm = np.full(1600, 1000, dtype="<i2").tobytes()
            async for _ in LaptopSpeaker().play(pcm):
                pass
        samples = np.frombuffer(streams[0].data, dtype="<i2").reshape(-1, 2)
        self.assertEqual(len(samples), 4800)
        np.testing.assert_array_equal(samples[:, 0], samples[:, 1])
        self.assertAlmostEqual(float(np.median(samples)), 1000, delta=2)
        self.assertTrue(streams[0].closed)


if __name__ == "__main__":
    unittest.main()
