import pathlib
import shutil
import subprocess
import tempfile
import unittest


class AudioCodecTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("g++"), "A host C++ compiler is needed for the firmware codec check")
    def test_firmware_pcm_conversion_channel_selection_and_clipping(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix="iris-codec-") as directory:
            executable = pathlib.Path(directory) / "codec-test.exe"
            result = subprocess.run([shutil.which("g++"), "-std=c++11", "-Wall", "-Wextra",
                                     "-I", str(root / "firmware/include"),
                                     str(root / "tests/test_audio_codec.cpp"), "-o", str(executable)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run([str(executable)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
