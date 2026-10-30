import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import numpy as np

from iris.brain import LocalBrain, speech_text


class BrainDiagnosticsTests(unittest.TestCase):
    def test_emoji_sequences_are_removed_without_losing_spoken_words(self):
        self.assertEqual(speech_text("Hello🙂world! 👨‍👩‍👧‍👦 👍🏽 🇮🇳 ❤️ 1️⃣"), "Hello world!")
        self.assertEqual(speech_text("Café costs ₹5. I'm well!"), "Café costs ₹5. I'm well!")
        self.assertEqual(speech_text("😊❤️"), "I'm here.")

    def make_brain(self, words):
        brain = LocalBrain.__new__(LocalBrain)
        brain.stt = Mock()
        brain.stt.transcribe.return_value = (iter(SimpleNamespace(text=word) for word in words), None)
        brain.tts = Mock()
        brain.tts.tts.return_value = np.zeros(160, dtype=np.float32)
        brain.tts.synthesizer.output_sample_rate = 16000
        brain.url, brain.model = "http://localhost:11434/api/chat", "test"
        return brain

    def test_empty_recognition_reports_reason_without_ai_or_synthesis(self):
        brain = self.make_brain([])
        with patch("iris.brain.urllib.request.urlopen") as request, self.assertLogs("iris", level="WARNING") as logs:
            self.assertEqual(brain._respond(bytes(20480)), b"")
        self.assertIn("no intelligible speech", logs.output[0])
        request.assert_not_called()
        brain.tts.tts.assert_not_called()

    def test_recognized_sentence_reaches_ai_and_reply_is_synthesized(self):
        brain = self.make_brain(["Hello", "how are you?"])
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = json.dumps({"message": {"content": "I'm well. 😊"}}).encode()
        with patch("iris.brain.urllib.request.urlopen", return_value=response) as request, self.assertLogs("iris", level="INFO") as logs:
            self.assertEqual(len(brain._respond(bytes(20480))), 320)
        body = json.loads(request.call_args.args[0].data)
        self.assertEqual(body["messages"][-1]["content"], "Hello how are you?")
        brain.tts.tts.assert_called_once_with(text="I'm well.")
        self.assertTrue(any("Heard: Hello how are you?" in line for line in logs.output))
        self.assertTrue(any("Iris reply:" in line for line in logs.output))
