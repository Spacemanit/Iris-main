"""Session-scoped laptop playback; blocking audio calls stay off the event loop."""

import asyncio
import logging
import math

log = logging.getLogger("iris")


class LaptopSpeaker:
    def __init__(self, device=None):
        self.device = device
        self.stream = None

    def _open(self, pcm):
        import numpy as np
        import sounddevice as sd

        info = sd.query_devices(self.device, "output")
        rate = int(info["default_samplerate"])
        channels = min(2, int(info["max_output_channels"]))
        sd.check_output_settings(device=self.device, channels=channels,
                                 dtype="int16", samplerate=rate)
        if rate != 16000:
            from scipy.signal import resample_poly
            divisor = math.gcd(rate, 16000)
            samples = resample_poly(np.frombuffer(pcm, dtype="<i2").astype(np.float32),
                                    rate // divisor, 16000 // divisor)
            pcm = np.clip(samples, -32768, 32767).astype("<i2").tobytes()
        self.stream = sd.RawOutputStream(device=self.device, channels=channels,
                                         dtype="int16", samplerate=rate, latency="low")
        self.stream.start()
        log.info("Laptop speaker ready: %s (%d Hz)", info["name"], rate)
        return pcm, rate, channels

    def _close(self, complete):
        if self.stream is not None:
            try:
                # Drain the last samples normally; stop promptly on disconnect.
                if complete:
                    self.stream.stop()
                else:
                    self.stream.abort()
            finally:
                self.stream.close()
                self.stream = None

    async def play(self, pcm):
        """Yield mono chunks for mouth animation as the output stream accepts them."""
        import numpy as np

        operation = asyncio.create_task(asyncio.to_thread(self._open, pcm))
        complete = False
        try:
            pcm, rate, channels = await asyncio.shield(operation)
            block_bytes = round(rate * .032) * 2
            for offset in range(0, len(pcm), block_bytes):
                chunk = pcm[offset:offset + block_bytes]
                output = chunk
                if channels == 2:
                    output = np.repeat(np.frombuffer(chunk, dtype="<i2"), 2).tobytes()
                operation = asyncio.create_task(asyncio.to_thread(self.stream.write, output))
                await asyncio.shield(operation)
                yield chunk
            complete = True
        finally:
            # A cancelled to_thread call still runs: finish it before closing
            # or allowing a reconnect to create a replacement output stream.
            await asyncio.gather(operation, return_exceptions=True)
            closing = asyncio.create_task(asyncio.to_thread(self._close, complete))
            try:
                await asyncio.shield(closing)
            finally:
                await asyncio.gather(closing, return_exceptions=True)
