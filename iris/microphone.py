"""Bounded, non-blocking laptop microphone capture. Audio is never saved."""

import asyncio
import contextlib
import logging
import math
import queue
import threading
import time

log = logging.getLogger("iris")


class LaptopMicrophone:
    def __init__(self, device=None):
        self.device = device
        self.sample_rate = 16000
        self.name = ""
        self.stream = None
        self.pending = queue.Queue(maxsize=8)
        self.ready = asyncio.Event()
        self.loop = None
        self.wake_lock = threading.Lock()
        self.wake_pending = False
        self.closing = False
        self.resample = None

    def _wake(self):
        with self.wake_lock:
            self.wake_pending = False
        self.ready.set()

    def _callback(self, data, frames, timing, status):
        if self.closing:
            return
        gap = bool(status)
        if self.pending.full():
            # Stale audio must not turn into a delayed conversation.
            while True:
                try:
                    self.pending.get_nowait()
                except queue.Empty:
                    break
            gap = True
        self.pending.put_nowait((bytes(data), time.monotonic(), gap))
        with self.wake_lock:
            if not self.wake_pending and self.loop is not None:
                self.wake_pending = True
                with contextlib.suppress(RuntimeError):
                    self.loop.call_soon_threadsafe(self._wake)

    def open(self):
        import sounddevice as sd

        info = sd.query_devices(self.device, "input")
        self.name = info["name"]
        try:
            sd.check_input_settings(device=self.device, channels=1, dtype="int16", samplerate=16000)
        except sd.PortAudioError:
            self.sample_rate = int(info["default_samplerate"])
            sd.check_input_settings(device=self.device, channels=1, dtype="int16", samplerate=self.sample_rate)
        if self.sample_rate != 16000:
            # Import DSP before starting capture so its first import cannot
            # overflow the input queue while audio is already arriving.
            from scipy.signal import resample_poly
            self.resample = resample_poly
        self.stream = sd.RawInputStream(device=self.device, channels=1, dtype="int16",
                                       samplerate=self.sample_rate,
                                       blocksize=round(self.sample_rate * .032),
                                       latency="low", callback=self._callback)
        self.stream.start()
        log.info("Laptop microphone ready: %s (%d Hz → 16000 Hz)", self.name, self.sample_rate)

    def close(self):
        self.closing = True
        if self.stream is not None:
            try:
                self.stream.stop()
            finally:
                self.stream.close()
                self.stream = None

    def _convert(self, pcm):
        if self.sample_rate == 16000:
            return pcm
        import numpy as np

        divisor = math.gcd(self.sample_rate, 16000)
        samples = np.frombuffer(pcm, dtype="int16").astype(np.float32)
        samples = self.resample(samples, 16000 // divisor, self.sample_rate // divisor)
        return np.clip(samples, -32768, 32767).astype("<i2").tobytes()

    async def chunks(self):
        self.loop = asyncio.get_running_loop()
        starting = asyncio.create_task(asyncio.to_thread(self.open))
        try:
            await asyncio.shield(starting)
            while True:
                self.ready.clear()
                try:
                    pcm, captured_at, gap = self.pending.get_nowait()
                except queue.Empty:
                    try:
                        await asyncio.wait_for(self.ready.wait(), timeout=1)
                    except asyncio.TimeoutError:
                        if not self.stream.active:
                            raise RuntimeError("Laptop microphone stopped; check Windows input device")
                    continue
                if self.sample_rate != 16000:
                    pcm = await asyncio.to_thread(self._convert, pcm)
                yield pcm, captured_at, gap
        finally:
            # Opening an input device runs in a thread; let it finish before
            # closing, even if its session was cancelled during startup.
            await asyncio.gather(starting, return_exceptions=True)
            await asyncio.to_thread(self.close)
            self.loop = None
