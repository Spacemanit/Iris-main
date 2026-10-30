import threading


class Gaze:
    def __init__(self, mirror=False, smoothing=0.65):
        self.mirror = mirror
        self.smoothing = smoothing
        self.x = self.y = 0.0

    def update(self, faces, width, height):
        if faces:
            x, y, w, h = max(faces, key=lambda box: box[2] * box[3])
            target_x = 2 * (x + w / 2) / width - 1
            target_y = 2 * (y + h / 2) / height - 1
            if self.mirror:
                target_x = -target_x
        else:
            target_x = target_y = 0.0
        self.x += self.smoothing * (max(-1, min(1, target_x)) - self.x)
        self.y += self.smoothing * (max(-1, min(1, target_y)) - self.y)
        return self.x, self.y


class Vision:
    def __init__(self):
        import cv2
        self.cv2 = cv2
        self.lock = threading.Lock()
        # Keep CPU work bounded while networking and preview are active.
        cv2.setNumThreads(2)
        self.detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        if self.detector.empty():
            raise RuntimeError("OpenCV face detector is unavailable")

    def detect(self, jpeg):
        import numpy as np
        frame = self.cv2.imdecode(np.frombuffer(jpeg, dtype=np.uint8), self.cv2.IMREAD_GRAYSCALE)
        if frame is None:
            raise ValueError("Cannot decode JPEG")
        height, width = frame.shape
        if width > 1920 or height > 1080:
            raise ValueError("Frame dimensions exceed limit")
        # QVGA passes through unchanged; larger images don't expand the scan.
        scale = min(1.0, 320 / width)
        if scale < 1:
            frame = self.cv2.resize(frame, (320, max(1, round(height * scale))),
                                    interpolation=self.cv2.INTER_AREA)
        # A cancelled inference thread can finish during a device reconnect.
        with self.lock:
            faces = self.detector.detectMultiScale(frame, scaleFactor=1.15, minNeighbors=5, minSize=(25, 25))
        return [tuple(int(round(value / scale)) for value in box) for box in faces], width, height
