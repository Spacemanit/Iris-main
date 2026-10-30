import json
import math
import threading
import urllib.request
import urllib.error
import logging
import re
import unicodedata

log = logging.getLogger("iris")


def speech_text(reply):
    """Keep spoken words while removing emoji and their joining characters."""
    reply = re.sub(r"[0-9#*]\ufe0f?\u20e3", "", reply)
    text = "".join(" " if unicodedata.category(char) == "So" else char
                   for char in reply if unicodedata.category(char) != "Cf"
                   and not 0xFE00 <= ord(char) <= 0xFE0F
                   and not 0x1F3FB <= ord(char) <= 0x1F3FF)
    text = " ".join(text.split())
    return text if any(char.isalnum() for char in text) else "I'm here."


class LocalBrain:
    """Load optional models only when voice is explicitly enabled."""
    def __init__(self, whisper_model, ollama_url, ollama_model, tts_model):
        from faster_whisper import WhisperModel
        from TTS.api import TTS
        import torch
        torch.set_num_threads(2)
        log.info("Loading Whisper model: %s", whisper_model)
        self.stt = WhisperModel(whisper_model, device="cpu", compute_type="int8", cpu_threads=2, num_workers=1)
        log.info("Loading speech playback model: %s", tts_model)
        self.tts = TTS(model_name=tts_model, progress_bar=False)
        self.url = ollama_url.rstrip("/") + "/api/chat"
        self.model = ollama_model
        self.lock = threading.Lock()

    def respond(self, pcm):
        # Cancelling an asyncio caller cannot stop an inference thread.
        # Serialize across reconnects as well as within a session.
        if not self.lock.acquire(blocking=False):
            raise RuntimeError("Previous voice inference is still finishing")
        try:
            return self._respond(pcm)
        finally:
            self.lock.release()

    def _respond(self, pcm):
        import numpy as np
        from scipy.signal import resample_poly
        audio = np.frombuffer(pcm, dtype="<i2").astype(np.float32) / 32768
        segments, _ = self.stt.transcribe(audio, beam_size=1, language="en", task="transcribe")
        transcript = " ".join(segment.text.strip() for segment in segments).strip()
        if not transcript:
            log.warning("Whisper recognized no intelligible speech; no AI request was sent")
            return b""
        log.info("Heard: %s", transcript)
        body = json.dumps({"model": self.model, "stream": False, "think": False, "keep_alive": "10m", "messages": [
            {"role": "system", "content": "You are Iris, a friendly wall companion. Reply in English, briefly in one or two spoken sentences. Use plain text without emoji or markdown."},
            {"role": "user", "content": transcript}], "options": {"num_predict": 160, "num_ctx": 2048}}).encode()
        request = urllib.request.Request(self.url, body, {"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read(65537)
        except urllib.error.URLError as error:
            raise RuntimeError("Cannot get an Ollama reply. Start Ollama and check ollama_url/ollama_model in iris.config.json") from error
        if len(data) > 65536:
            raise ValueError("LLM response too large")
        reply = json.loads(data)["message"]["content"][:1000]
        if not reply.strip():
            log.warning("Ollama returned an empty reply; no speech was generated")
            return b""
        log.info("Iris reply: %s", reply)
        spoken = speech_text(reply)
        log.info("Generating speech: %s", spoken)
        waveform = np.asarray(self.tts.tts(text=spoken), dtype=np.float32)
        if waveform.ndim != 1 or not np.isfinite(waveform).all():
            raise ValueError("Voice model returned invalid audio")
        rate = self.tts.synthesizer.output_sample_rate
        divisor = math.gcd(rate, 16000)
        waveform = resample_poly(waveform, 16000 // divisor, rate // divisor)
        pcm = (np.clip(waveform[:16000 * 30], -1, 1) * 32767).astype("<i2").tobytes()
        log.info("Speech generated: %.2f seconds", len(pcm) / 32000)
        return pcm
