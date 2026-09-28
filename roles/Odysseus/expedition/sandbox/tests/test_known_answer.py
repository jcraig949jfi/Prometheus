"""Known-answer tests.

1. Fast per-world direction checks on single planted worlds (seconds).
2. The recorded gate (known_answer.json, n = 20 worlds/arm, produced by
   run_battery.py known) re-checked against PREREG s5 from the per-world data.
Run from sandbox/: python3 -m unittest tests.test_known_answer
"""
import json
import os
import sys
import unittest

HERE = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import run_battery as RB  # noqa: E402


class TestSingleWorldDirections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.P, _ = B.battery_world('P', 7)
        cls.C, _ = B.battery_world('C', 7)
        cls.Na, _ = B.battery_world('N_a', 7)

    def test_planted_content_matters(self):
        self.assertGreater(self.P['D1'], B.DELTA)
        self.assertGreater(self.P['Dp'], 0)
        self.assertGreater(self.P['Dr'], 0)
        self.assertAlmostEqual(self.P['Di'] or 0.0, 0.0, places=9)

    def test_cheat_presence_only(self):
        self.assertGreater(self.C['D1'], B.DELTA)          # deletion hurts
        self.assertAlmostEqual(self.C['Dp'], 0.0, places=9)  # permuted content: no loss
        self.assertAlmostEqual(self.C['Dr'], 0.0, places=9)  # random content: no loss

    def test_unused_record_no_reuse(self):
        self.assertGreater(self.Na['D0'], 0.2)              # record is informative
        self.assertAlmostEqual(self.Na['D1'], 0.0, places=9)  # but nobody uses it


class TestRecordedGate(unittest.TestCase):
    def setUp(self):
        path = os.path.join(HERE, 'known_answer.json')
        if not os.path.exists(path):
            self.skipTest('known_answer.json not produced yet')
        with open(path) as f:
            self.ka = json.load(f)

    def test_gate_recomputed_from_per_world_data(self):
        by = self.ka['per_world']
        dec = {a: B.decide(by[a]) for a in RB.KNOWN}
        dec['convention_P'] = B.convention(dec['P'], dec['P_sigma'])
        g = RB.gate(dec)
        self.assertTrue(g['PASS'], g)
        self.assertEqual(dec['P']['highest'], 'R3')
        self.assertIn(dec['N_a']['highest'], (None, 'R0'))
        self.assertIn(dec['N_b']['highest'], (None, 'R0'))
        self.assertEqual(dec['C']['highest'], 'R2')


if __name__ == '__main__':
    unittest.main()
