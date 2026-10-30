import math
import struct
import unittest

from iris.levels import MicrophoneMeter


class MicrophoneLevelTests(unittest.TestCase):
    def test_constant_bias_is_distinct_from_changing_sound(self):
        meter = MicrophoneMeter()
        meter.feed(struct.pack("<512h", *([9830] * 512)), now=1)
        data = meter.snapshot(now=1)
        self.assertAlmostEqual(data["rms"], .3, places=4)
        self.assertEqual(data["ac_rms"], 0)
        self.assertAlmostEqual(data["dc_offset"], .3, places=4)
        ac, dc = meter.take_bias_window()
        self.assertEqual(ac, 0)
        self.assertAlmostEqual(dc, .3, places=4)
        self.assertEqual(meter.take_bias_window(), (0, 0))
        meter.feed(struct.pack("<4h", 16384, -16384, 16384, -16384), now=2)
        data = meter.snapshot(now=2)
        self.assertEqual(data["ac_rms"], .5)
        self.assertEqual(data["dc_offset"], 0)
        self.assertEqual(meter.take_bias_window(), (.5, 0))
        self.assertEqual(meter.snapshot(now=3)["ac_rms"], 0)

    def test_silent_packets_are_distinct_from_no_input_and_levels_expire(self):
        meter = MicrophoneMeter()
        self.assertIsNone(meter.snapshot(now=0)["age"])
        meter.feed(bytes(1024), now=1)
        data = meter.snapshot(now=1.1)
        self.assertEqual(data["packets"], 1)
        self.assertEqual(data["rms"], 0)
        self.assertIsNone(data["dbfs"])
        self.assertAlmostEqual(data["age"], .1)
        meter.feed(struct.pack("<4h", 16384, -16384, 16384, -16384), now=1.2)
        data = meter.snapshot(now=1.3)
        self.assertEqual(data["rms"], .5)
        self.assertEqual(data["peak"], .5)
        self.assertAlmostEqual(data["dbfs"], 20 * math.log10(.5))
        data = meter.snapshot(now=2)
        self.assertEqual(data["rms"], 0)
        self.assertEqual(data["peak"], 0)
        self.assertAlmostEqual(data["age"], .8)
        self.assertEqual(data["packets"], 2)

    def test_clipping_and_terminal_window_hold_short_sounds(self):
        meter = MicrophoneMeter()
        meter.feed(struct.pack("<2h", -32768, 32767), now=0)
        data = meter.snapshot(now=.1)
        self.assertTrue(data["clipping"])
        self.assertEqual(data["peak"], 1)
        meter.feed(bytes(1024), now=.5)
        level, peak, packets = meter.take_window()
        self.assertGreater(level, .99)
        self.assertEqual(peak, 1)
        self.assertEqual(packets, 2)
        self.assertEqual(meter.take_window(), (0, 0, 0))
        self.assertFalse(meter.snapshot(now=.6)["clipping"])
        for i in range(100):
            meter.feed(bytes(1024), now=i)
        self.assertLessEqual(len(meter.recent), 32)
