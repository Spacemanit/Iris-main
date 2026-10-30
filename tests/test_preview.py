import asyncio
import base64
import json
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

import cv2
import numpy as np
from websockets.asyncio.client import connect
from websockets.asyncio.server import serve

from iris.preview import Preview, PreviewServer
from iris.protocol import VIDEO, pack
from iris.server import Session
from iris.vision import Vision


def fetch(url):
    with urlopen(url, timeout=3) as response:
        return response.read(), response.headers


class PreviewIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_audio_levels_update_without_new_camera_frames_and_reset_on_reconnect(self):
        from iris.levels import MicrophoneMeter

        preview = Preview()
        preview.connect()
        jpeg = cv2.imencode(".jpg", np.zeros((240, 320, 3), dtype=np.uint8))[1].tobytes()
        preview.publish(jpeg, [], 320, 240, 0, 0, False)
        meter = MicrophoneMeter()
        meter.feed(np.full(512, 8192, dtype="<i2").tobytes())
        levels = meter.snapshot()
        levels.update(source="esp32", status="test", threshold=.015, gaps=2)
        preview.publish_microphone(levels)
        with PreviewServer(preview, "127.0.0.1", 0) as http:
            url = f"http://127.0.0.1:{http.server.server_port}"
            page, _ = await asyncio.to_thread(fetch, url + "/")
            self.assertIn(b"Microphone level", page)
            self.assertIn(b"mic-pointer", page)
            data = json.loads((await asyncio.to_thread(fetch, url + "/frame?after=1"))[0])
            self.assertNotIn("jpeg", data)
            self.assertEqual(data["sequence"], 1)
            self.assertEqual(data["microphone"]["rms"], .25)
            self.assertEqual(data["microphone"]["packets"], 1)
            self.assertEqual(data["microphone"]["gaps"], 2)
            first_age = data["microphone"]["age"]
            await asyncio.sleep(.02)
            data = json.loads((await asyncio.to_thread(fetch, url + "/frame?after=1"))[0])
            self.assertGreater(data["microphone"]["age"], first_age)
            preview.disconnect()
            self.assertFalse(preview.snapshot()["connected"])
            preview.connect()
            data = preview.snapshot()
            self.assertEqual(data["microphone"]["packets"], 0)
            self.assertIsNone(data["microphone"]["age"])

    async def test_camera_controls_and_browser_share_tracking_and_reconnect(self):
        preview = Preview()

        class TestVision:
            faces = [(10, 20, 30, 30), (200, 60, 80, 100)]

            def detect(self, jpeg):
                # Decode a real JPEG, with predictable detections for gaze checks.
                _, width, height = Vision().detect(jpeg)
                return self.faces, width, height

        vision = TestVision()

        async def handler(ws):
            preview.connect()
            try:
                await Session(ws, vision, mirror=True, preview=preview).run()
            finally:
                preview.disconnect()

        encoded, data = cv2.imencode(".jpg", np.zeros((240, 320, 3), dtype=np.uint8))
        self.assertTrue(encoded)
        jpeg = data.tobytes()
        with PreviewServer(preview, "127.0.0.1", 0) as http:
            url = f"http://127.0.0.1:{http.server.server_port}"
            page, headers = await asyncio.to_thread(fetch, url + "/")
            self.assertIn(b"Camera feed", page)
            self.assertIn(b"Eye movement target", page)
            self.assertEqual(headers["Cache-Control"], "no-store")
            frame = json.loads((await asyncio.to_thread(fetch, url + "/frame"))[0])
            self.assertFalse(frame["connected"])
            self.assertIsNone(frame["age"])
            with self.assertRaises(HTTPError) as error:
                await asyncio.to_thread(fetch, url + "/missing")
            self.assertEqual(error.exception.code, 404)

            async with serve(handler, "127.0.0.1", 0) as device_server:
                port = device_server.sockets[0].getsockname()[1]
                async with connect(f"ws://127.0.0.1:{port}") as device:
                    await device.send(pack(VIDEO, jpeg))
                    for _ in range(30):
                        control = json.loads(await asyncio.wait_for(device.recv(), 3))
                        if control["gaze_x"] < -.1:
                            break
                    self.assertAlmostEqual(control["gaze_x"], -.325)
                    self.assertEqual(control["frame_ack"], 1)
                    frame = json.loads((await asyncio.to_thread(fetch, url + "/frame"))[0])
                    self.assertTrue(frame["connected"])
                    self.assertEqual(base64.b64decode(frame["jpeg"]), jpeg)
                    self.assertEqual(frame["face"], [200, 60, 80, 100])
                    self.assertEqual((frame["width"], frame["height"]), (320, 240))
                    self.assertEqual(frame["gaze_x"], control["gaze_x"])
                    self.assertEqual(frame["gaze_y"], control["gaze_y"])
                    self.assertTrue(frame["mirror"])
                    unchanged, _ = await asyncio.to_thread(fetch, url + "/frame?after=1")
                    self.assertNotIn("jpeg", json.loads(unchanged))
                    self.assertLess(len(unchanged), len(jpeg))

                    vision.faces = []
                    await device.send(pack(VIDEO, jpeg))
                    for _ in range(30):
                        control = json.loads(await asyncio.wait_for(device.recv(), 3))
                        if control["frame_ack"] == 2:
                            break
                    frame = json.loads((await asyncio.to_thread(fetch, url + "/frame"))[0])
                    self.assertIsNone(frame["face"])
                    self.assertAlmostEqual(frame["gaze_x"], -.325 * .35)
                    self.assertEqual(frame["sequence"], 2)

                for _ in range(30):
                    if not preview.snapshot()["connected"]:
                        break
                    await asyncio.sleep(.01)
                self.assertFalse(preview.snapshot()["connected"])
                async with connect(f"ws://127.0.0.1:{port}") as device:
                    await asyncio.wait_for(device.recv(), 3)
                    frame = json.loads((await asyncio.to_thread(fetch, url + "/frame"))[0])
                    self.assertTrue(frame["connected"])
                    self.assertIsNone(frame["age"])
                    self.assertNotIn("jpeg", frame)

    async def test_slow_tracking_keeps_network_alive_and_discards_old_frames(self):
        import threading

        started, release = threading.Event(), threading.Event()
        processed = []
        sessions = []

        class SlowVision:
            def detect(self, jpeg):
                processed.append(jpeg)
                if len(processed) == 1:
                    started.set()
                    if not release.wait(3):
                        raise RuntimeError("Test worker was not released")
                return [], 320, 240

        preview = Preview()

        async def handler(ws):
            session = Session(ws, SlowVision(), preview=preview)
            sessions.append(session)
            await session.run()

        images = [cv2.imencode(".jpg", np.full((240, 320, 3), shade, dtype=np.uint8))[1].tobytes()
                  for shade in range(0, 100, 10)]
        try:
            async with serve(handler, "127.0.0.1", 0) as server:
                port = server.sockets[0].getsockname()[1]
                async with connect(f"ws://127.0.0.1:{port}") as device:
                    initial = json.loads(await asyncio.wait_for(device.recv(), 1))
                    self.assertEqual(initial["frame_ack"], 0)
                    await device.send(pack(VIDEO, images[0]))
                    self.assertTrue(await asyncio.to_thread(started.wait, 1))
                    for jpeg in images[1:]:
                        await device.send(pack(VIDEO, jpeg))
                    for _ in range(100):
                        if sessions[0].frames_dropped == 8:
                            break
                        await asyncio.sleep(.01)
                    self.assertEqual(sessions[0].frames.qsize(), 1)
                    self.assertEqual(sessions[0].frames_dropped, 8)
                    # Inference must not block ping/pong or create a queue of
                    # thirty identical controls per second on the ESP32.
                    pong = await device.ping()
                    await asyncio.wait_for(pong, 1)
                    idle_controls = 0
                    deadline = asyncio.get_running_loop().time() + .6
                    while asyncio.get_running_loop().time() < deadline:
                        try:
                            await asyncio.wait_for(device.recv(), .1)
                            idle_controls += 1
                        except asyncio.TimeoutError:
                            pass
                    self.assertLessEqual(idle_controls, 3)
                    release.set()
                    for _ in range(10):
                        control = json.loads(await asyncio.wait_for(device.recv(), 1))
                        if control["frame_ack"] == 2:
                            break
                    self.assertEqual(control["frame_ack"], 2)
                    self.assertEqual(processed, [images[0], images[-1]])
                    self.assertEqual(base64.b64decode(preview.snapshot()["jpeg"]), images[-1])
        finally:
            release.set()

    async def test_host_accepts_reconnect_before_old_connection_times_out(self):
        from argparse import Namespace
        from contextlib import asynccontextmanager
        from unittest.mock import patch
        from websockets.exceptions import ConnectionClosed
        from iris.server import serve as run_host

        ready = asyncio.get_running_loop().create_future()

        @asynccontextmanager
        async def start_server(*args, **kwargs):
            async with serve(*args, **kwargs) as server:
                ready.set_result(server.sockets[0].getsockname()[1])
                yield server

        args = Namespace(bind="127.0.0.1", port=0, preview_port=0, voice=False, mirror=True)
        with patch("websockets.asyncio.server.serve", start_server):
            host = asyncio.create_task(run_host(args))
            try:
                port = await asyncio.wait_for(ready, 3)
                async with connect(f"ws://127.0.0.1:{port}") as first:
                    self.assertEqual(json.loads(await asyncio.wait_for(first.recv(), 2))["frame_ack"], 0)
                    # Keep the first transport open, as happens when the ESP32
                    # reconnects before the host notices a dead Wi-Fi session.
                    async with connect(f"ws://127.0.0.1:{port}") as replacement:
                        self.assertEqual(json.loads(await asyncio.wait_for(replacement.recv(), 2))["frame_ack"], 0)
                        with self.assertRaises(ConnectionClosed):
                            await asyncio.wait_for(first.recv(), 2)
                        jpeg = cv2.imencode(".jpg", np.zeros((240, 320, 3), dtype=np.uint8))[1].tobytes()
                        await replacement.send(pack(VIDEO, jpeg))
                        for _ in range(10):
                            control = json.loads(await asyncio.wait_for(replacement.recv(), 2))
                            if control["frame_ack"] == 1:
                                break
                        self.assertEqual(control["frame_ack"], 1)
            finally:
                host.cancel()
                await asyncio.gather(host, return_exceptions=True)


if __name__ == "__main__":
    unittest.main()
