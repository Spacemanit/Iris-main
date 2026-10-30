"""Digital microphone levels only; raw samples are never retained here."""

import math
import struct
import time
from collections import deque


class MicrophoneMeter:
    def __init__(self):
        self.recent = deque(maxlen=32)
        self.received_at = None
        self.packets = self.window_packets = 0
        self.window_rms = self.window_peak = 0.0
        self.window_ac = self.window_dc = 0.0

    def feed(self, pcm, now=None):
        if not pcm:
            return
        now = time.monotonic() if now is None else now
        values = struct.unpack(f"<{len(pcm) // 2}h", pcm)
        rms = math.sqrt(sum(value * value for value in values) / len(values)) / 32768
        peak = max(abs(value) for value in values) / 32768
        mean = sum(values) / len(values)
        dc = abs(mean) / 32768
        ac = math.sqrt(sum((value - mean) ** 2 for value in values) / len(values)) / 32768
        self.recent.append((now, rms, peak, ac, dc))
        self.received_at = now
        self.packets += 1
        self.window_packets += 1
        self.window_rms = max(self.window_rms, rms)
        self.window_peak = max(self.window_peak, peak)
        self.window_ac = max(self.window_ac, ac)
        self.window_dc = max(self.window_dc, dc)

    def snapshot(self, now=None):
        now = time.monotonic() if now is None else now
        while self.recent and self.recent[0][0] < now - .25:
            self.recent.popleft()
        rms = max((item[1] for item in self.recent), default=0.0)
        peak = max((item[2] for item in self.recent), default=0.0)
        ac = max((item[3] for item in self.recent), default=0.0)
        dc = max((item[4] for item in self.recent), default=0.0)
        return {"rms": rms, "peak": peak, "dbfs": 20 * math.log10(rms) if rms else None,
                "ac_rms": ac, "dc_offset": dc,
                "clipping": peak >= 32767 / 32768, "packets": self.packets,
                "age": None if self.received_at is None else max(0, now - self.received_at)}

    def take_window(self):
        result = self.window_rms, self.window_peak, self.window_packets
        self.window_rms = self.window_peak = 0.0
        self.window_packets = 0
        return result

    def take_bias_window(self):
        result = self.window_ac, self.window_dc
        self.window_ac = self.window_dc = 0.0
        return result
