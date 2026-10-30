import json
import math
import struct
from dataclasses import asdict, dataclass

VIDEO, MIC, SPEAKER = 1, 2, 3
MAX_VIDEO = 256 * 1024
MAX_AUDIO = 2048
STATES = {"sleeping", "idle", "listening", "thinking", "talking", "excited"}


def unpack(message: bytes) -> tuple[int, bytes]:
    if not isinstance(message, bytes) or len(message) < 2:
        raise ValueError("Expected tag and payload")
    tag, payload = message[0], message[1:]
    if tag == VIDEO:
        if len(payload) > MAX_VIDEO or not payload.startswith(b"\xff\xd8") or not payload.endswith(b"\xff\xd9"):
            raise ValueError("Invalid JPEG packet")
    elif tag in (MIC, SPEAKER):
        if len(payload) > MAX_AUDIO or len(payload) % 2:
            raise ValueError("Invalid PCM16 packet")
    else:
        raise ValueError("Unknown packet tag")
    return tag, payload


def pack(tag: int, payload: bytes) -> bytes:
    message = bytes([tag]) + payload
    unpack(message)
    return message


def rms(pcm: bytes) -> float:
    if not pcm:
        return 0.0
    values = struct.unpack(f"<{len(pcm) // 2}h", pcm)
    return math.sqrt(sum(v * v for v in values) / len(values)) / 32768


@dataclass
class Control:
    gaze_x: float = 0.0
    gaze_y: float = 0.0
    state: str = "idle"
    mouth_wave: float = 0.0
    version: int = 1

    def encode(self) -> str:
        if self.version != 1 or self.state not in STATES:
            raise ValueError("Unsupported control")
        for value, low, high in ((self.gaze_x, -1, 1), (self.gaze_y, -1, 1), (self.mouth_wave, 0, 1)):
            if isinstance(value, bool) or not math.isfinite(value) or not low <= value <= high:
                raise ValueError("Control outside bounds")
        return json.dumps(asdict(self), separators=(",", ":"), allow_nan=False)
