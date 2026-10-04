"""Tests for rso/slice001/encoding.py (C-004-T018): E06 twins of REG, run and reported, not an exit criterion.

Expected facts (CONTRACT.md draft A A5 P8, A6 rows E06; AMENDMENT_v1.0.1 V4): a reversible re-encoding
(REG_ONEHOT) and a flattened transition table (REG_FLAT) give REG's outcome VALUES on P0-P7; a lossy "encoding"
(LOSSY) does not (RETENTION NEGATIVE vs POSITIVE); every report row says ONE physics (closure D08).
Outcome vectors are computed once per module (each costs about 4 CPU-s, RESTART dominating).
Python >= 3.8, standard library only.
"""
import unittest

from rso.slice001 import encoding as EN
from rso.slice001 import world as W
from rso.slice001.fixtures import world_cases as WC

_vec = {}


def vector(make):
    if make not in _vec:
        _vec[make] = EN.outcome_vector(make)
    return _vec[make]


class TestTwins(unittest.TestCase):
    def test_reg_vector_is_the_registered_one(self):
        self.assertEqual(vector(WC.REG), {"P0": "PASS", "P1": "PASS", "P2": "POSITIVE", "P3": "PASS",
                                          "P4": "PASS", "P5": "PASS", "P6": "PASS", "P7": "PASS"})

    def test_onehot_twin_equals_reg(self):
        out = EN.twin_eq(WC.REG, EN.REG_ONEHOT, vectors=(vector(WC.REG), vector(EN.REG_ONEHOT)))
        self.assertEqual(out["value"], "PASS", out["reason"])
        self.assertEqual(out["predicate"], "P8")

    def test_flat_twin_equals_reg(self):
        out = EN.twin_eq(WC.REG, EN.REG_FLAT, vectors=(vector(WC.REG), vector(EN.REG_FLAT)))
        self.assertEqual(out["value"], "PASS", out["reason"])

    def test_lossy_is_not_a_twin(self):
        out = EN.twin_eq(WC.REG, EN.LOSSY, vectors=(vector(WC.REG), vector(EN.LOSSY)))
        self.assertEqual(out["value"], "FAIL")
        self.assertEqual(out["reason"], "twin LOSSY differs from REG on RETENTION: POSITIVE vs NEGATIVE")
        self.assertEqual(out["witness"], {"predicate": "P2", "m": "POSITIVE", "twin": "NEGATIVE"})

    def test_twins_differ_in_representation_but_not_in_behaviour(self):
        reg, one, flat = WC.REG(), EN.REG_ONEHOT(), EN.REG_FLAT()
        self.assertFalse(hasattr(one, "a"))               # no bit register: a and d live only as one-hot pairs
        self.assertFalse(hasattr(one, "d"))
        self.assertEqual(one.aa, (1, 0))
        self.assertFalse(hasattr(flat, "a"))              # one state tuple, advanced only by table lookup
        self.assertGreater(len(EN.FLAT_TABLE), 0)
        for h in (0, 1365, 2730, 4095):
            o = W.run_life(WC.REG, h).outputs
            self.assertEqual(W.run_life(EN.REG_ONEHOT, h).outputs, o)
            self.assertEqual(W.run_life(EN.REG_FLAT, h).outputs, o)
        self.assertEqual(one.capture(), reg.capture())
        self.assertEqual(flat.capture(), reg.capture())

    def test_report_says_one_physics_and_never_unlike(self):
        rows = EN.e06_report(vectors={m: vector(m) for m in (WC.REG, EN.REG_ONEHOT, EN.REG_FLAT, EN.LOSSY)})
        self.assertEqual([r["twin"] for r in rows], ["REG_ONEHOT", "REG_FLAT", "LOSSY"])
        self.assertEqual([r["twin_eq"] for r in rows], ["PASS", "PASS", "FAIL"])
        for r in rows:
            self.assertEqual(r["physics"], "ONE")
            self.assertEqual(r["exit_criterion"], False)
            text = " ".join(str(v) for v in r.values()).lower()
            self.assertNotIn("unlike", text)
            self.assertNotIn("cross-physics", text.replace("no cross-physics", ""))


if __name__ == "__main__":
    unittest.main()
