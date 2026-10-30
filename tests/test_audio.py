import math
import json
import pathlib
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

from iris.audio import Endpoint
from iris.server import main


class AudioSettingsTests(unittest.TestCase):
    def test_invalid_threshold_cannot_disable_or_permanently_trigger_input(self):
        for threshold in (0, 1, -.1, 2, math.nan, math.inf, True, "loud", None):
            with self.subTest(threshold=threshold), self.assertRaises(ValueError):
                Endpoint(threshold=threshold)

    def test_config_loads_threshold_and_cli_can_override_it(self):
        with tempfile.TemporaryDirectory(prefix="iris-settings-") as directory:
            config = pathlib.Path(directory) / "config.json"
            config.write_text(json.dumps({"mic_threshold": .45}), encoding="utf-8")
            for override, expected in (([], .45), (["--mic-threshold", ".5"], .5)):
                with patch("sys.argv", ["iris", "--config", str(config)] + override), \
                     patch("iris.server.serve", new_callable=AsyncMock) as host:
                    main()
                    self.assertEqual(host.call_args.args[0].mic_threshold, expected)
