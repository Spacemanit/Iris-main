"""Desktop camera and face preview for the same device protocol."""
import argparse
import asyncio
import json


async def run(url, camera):
    import cv2
    import numpy as np
    from websockets.asyncio.client import connect
    from .protocol import VIDEO, pack
    capture = cv2.VideoCapture(camera) if camera >= 0 else None
    control = {"gaze_x": 0, "gaze_y": 0, "state": "sleeping", "mouth_wave": 0}
    try:
        async with connect(url, compression=None) as ws:
            async def receive():
                async for message in ws:
                    if isinstance(message, str):
                        control.update(json.loads(message))
            worker = asyncio.create_task(receive())
            try:
                while not worker.done():
                    preview = np.zeros((320, 256, 3), dtype=np.uint8)
                    for x in (80, 176):
                        cv2.circle(preview, (x, 120), 44, (255, 255, 255), -1)
                        cv2.circle(preview, (x + int(control['gaze_x'] * 22), 120 + int(control['gaze_y'] * 22)), 18, (0, 0, 0), -1)
                    cv2.ellipse(preview, (128, 240), (35, max(2, int(control['mouth_wave'] * 20))), 0, 0, 360, (255, 255, 255), -1)
                    cv2.putText(preview, control['state'], (10, 300), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255))
                    cv2.imshow("Iris simulator - Q to exit", preview)
                    if cv2.waitKey(1) & 255 == ord('q'):
                        break
                    if capture:
                        ok, frame = capture.read()
                        if not ok:
                            raise RuntimeError("Camera read failed")
                        ok, jpeg = cv2.imencode('.jpg', cv2.resize(frame, (320, 240)))
                        if ok:
                            await ws.send(pack(VIDEO, jpeg.tobytes()))
                    await asyncio.sleep(.1)
            finally:
                worker.cancel()
                await asyncio.gather(worker, return_exceptions=True)
    finally:
        if capture:
            capture.release()
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='ws://127.0.0.1:8765')
    parser.add_argument('--camera', type=int, default=-1, help='Use 0 for webcam; -1 for preview only')
    args = parser.parse_args()
    asyncio.run(run(args.url, args.camera))


if __name__ == '__main__':
    main()
