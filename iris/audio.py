import math

from .protocol import rms


class Endpoint:
    """Bound utterances to ten seconds, ending after 600 ms of silence."""
    def __init__(self, threshold=0.015, silence_samples=9600, max_samples=160000):
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not math.isfinite(threshold) or not 0 < threshold < 1:
            raise ValueError("mic_threshold must be a number greater than 0 and less than 1")
        self.threshold = threshold
        self.silence_samples = silence_samples
        self.max_samples = max_samples
        self.reset()

    def reset(self):
        self.buffer = bytearray()
        self.silent = 0

    def feed(self, pcm):
        active = rms(pcm) >= self.threshold
        if not self.buffer and not active:
            return None
        remaining = self.max_samples * 2 - len(self.buffer)
        self.buffer.extend(pcm[:remaining])
        self.silent = 0 if active else self.silent + len(pcm) // 2
        if self.silent >= self.silence_samples or len(self.buffer) >= self.max_samples * 2:
            result = bytes(self.buffer)
            self.reset()
            return result
        return None
