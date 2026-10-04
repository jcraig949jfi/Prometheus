"""Tests for the retention ruler P2 and the calibration gate P1 (C-004-T012).

Cases are draft A A6 rows T01 and T02 (contract.json cases T01.REG, T01.PKTD, T01.QCARRY, T02.AMNESIAC,
T02.CLOCKED, T02.FLIP), realised on world.Runtime from their A6 descriptions. Expected values are the contract's
(A4 world-side facts, A5 P1/P2, A6 outcomes), stated here, never taken from rulers.py or checker.py. The last
class checks field by field that the ruler and gate agree with the consumer's recomputation (G-RECOMP).
Python >= 3.8, standard library only.
"""
import unittest
from fractions import Fraction

from rso.slice001 import checker as C
from rso.slice001 import receipt as R
from rso.slice001 import rulers as P
from rso.slice001 import world as W


class Reg(W.Runtime):
    """REG (A6): a := u and d := f at CUE; reset d := 0 and empties the channel, keeps a."""

    def on_cue(self, u, f):
        self.a, self.d = u, f

    def on_deliver(self, bits):
        pass

    def reset(self):
        self.d, self.chan, self.log_n = 0, [], self.log_n + 1


class Pktd(Reg):
    """PKTD (A6): display through the channel: sends (f, 0); d := first delivered bit."""

    def on_cue(self, u, f):
        self.a = u
        self.send(f, 0)

    def on_deliver(self, bits):
        if bits:
            self.d = bits[0]


class Qcarry(Reg):
    """QCARRY (A6, T01 false): sends (u, 1), sets a := delivered bit; reset does not flush."""

    def on_cue(self, u, f):
        self.d = f
        self.send(u, 1)

    def on_deliver(self, bits):
        if bits:
            self.a = bits[0]

    def reset(self):
        self.d, self.log_n = 0, self.log_n + 1


class Amnesiac(Reg):
    """AMNESIAC (A6, T02 true): a is never written; the answer is 0."""

    def on_cue(self, u, f):
        self.d = f


class Flip(Reg):
    """FLIP (A6, T02 ruler false): answers 1 - a."""

    def answer(self):
        return 1 - self.a


class Leaky(Reg):
    """Not an A6 fixture: answers u_j AND f_j -- depends on u_j, s = 3/4 (NOT_SHOWN, not NEGATIVE)."""

    def on_cue(self, u, f):
        self.a, self.d = u & f, f


class Xor(Reg):
    """Not an A6 fixture: answers u_j XOR f_j -- s = 1/2 exactly yet depends on u_j (A5 P2: NOT_SHOWN)."""

    def on_cue(self, u, f):
        self.a, self.d = u ^ f, f


_ANS = {}


def retention(cls, variant="STANDARD"):
    key = (cls.__name__, variant)
    if key not in _ANS:
        _ANS[key] = P.retention_of_runtime(cls, variant)
    return _ANS[key]


def probe_a_runs(cls):
    """The RESET run of trace:probe_a in checker.TRACE_LAYOUT, written here from world lives (12 chars per
    history: y_A then the PROBE_A display, episodes 1..6)."""
    lives = [W.run_life(cls, h) for h in W.histories()]
    run = "".join("%d%d" % life.probe_a(e) for life in lives for e in range(1, W.EPISODES + 1))
    return {"trace:probe_a": {"RESET": run}}


def collapse_stub(outcome):
    """The RED stub the packet names: a ruler that renders every non-POSITIVE result as a gate FAIL."""
    if outcome["value"] == "POSITIVE":
        return outcome
    return {"kind": "GATE", "predicate": "P2", "value": "FAIL", "reason": "retention failed", "witness": {"j": 1},
            "eligible_count": outcome["trials"], "applicable_count": None, "vacuous": False}


def assert_t02_negative(test, outcome):
    """T02 (closure C1): a correct negative observation is a RULER NEGATIVE at exactly 1/2, never a FAIL."""
    test.assertEqual(outcome["kind"], "RULER")
    test.assertEqual(outcome["value"], "NEGATIVE")
    test.assertNotEqual(outcome["value"], "FAIL")
    R._ruler_outcome(outcome, "outcome", "P2")
    test.assertEqual(P.success(outcome), Fraction(1, 2))
    test.assertEqual((outcome["successes"], outcome["trials"]), (6144, 12288))
    v = R.make_verdict("rcpt:AMNESIAC:RETENTION:STANDARD", {"status": "RAN", "missing": [], "run_id": "t"},
                       {"status": "QUALIFIED", "stage": "AUTHOR_TESTED"}, outcome, "POSITIVE")
    test.assertEqual(v["standing"], "UNMET")                  # a scientific negative, not a software failure


class TestT02NeverFail(unittest.TestCase):
    def test_amnesiac_is_negative_at_exactly_one_half(self):
        assert_t02_negative(self, retention(Amnesiac))

    def test_collapse_stub_is_caught(self):
        # Fire test of the check itself: the stub that turns NEGATIVE into FAIL must not pass it.
        with self.assertRaises((AssertionError, R.ReceiptError)):
            assert_t02_negative(self, collapse_stub(retention(Amnesiac)))


class TestRetention(unittest.TestCase):
    def test_t01_reg_and_pktd_positive(self):
        for cls in (Reg, Pktd):
            o = retention(cls)
            self.assertEqual((o["value"], o["statistic"], o["successes"], o["trials"]),
                             ("POSITIVE", "1/1", 12288, 12288), cls.__name__)
            self.assertEqual(o["per_boundary"], [{"j": j, "statistic": "1/1"} for j in (1, 2, 3)])

    def test_t01_qcarry_positive_too(self):
        # The ruler sees only the answer; QCARRY's forbidden route is CHANNEL's to catch (A6 T01 false).
        self.assertEqual(retention(Qcarry)["value"], "POSITIVE")

    def test_t02_flip_not_shown_never_negative(self):
        o = retention(Flip)
        self.assertEqual((o["value"], o["statistic"], o["successes"]), ("NOT_SHOWN", "0/1", 0))

    def test_dependence_at_other_rates_is_not_shown(self):
        o = retention(Leaky)
        self.assertEqual((o["value"], o["statistic"]), ("NOT_SHOWN", "3/4"))

    def test_one_half_with_dependence_is_not_shown(self):
        # s = 1/2 alone is not NEGATIVE: NEGATIVE needs the answer never to depend on u_j (FD-A2).
        o = retention(Xor)
        self.assertEqual((o["value"], o["statistic"]), ("NOT_SHOWN", "1/2"))

    def test_outcome_is_a_valid_ruler_outcome(self):
        for cls in (Reg, Amnesiac, Flip):
            R._ruler_outcome(retention(cls), "outcome", "P2")

    def test_retention_from_trace_runs_equals_runtime(self):
        self.assertEqual(P.retention_from_runs(probe_a_runs(Reg)), retention(Reg))


class TestCalibration(unittest.TestCase):
    def test_standard_passes_at_exactly_one_half(self):
        o = P.calibration("STANDARD")
        self.assertEqual((o["kind"], o["predicate"], o["value"], o["witness"], o["eligible_count"]),
                         ("GATE", "P1", "PASS", None, 8 * 12288))
        self.assertEqual(P.no_carry_maximum("STANDARD"), Fraction(1, 2))
        R._gate_outcome(o, "outcome", "P1")

    def test_t02_clocked_fails_with_the_clock_policy(self):
        o = P.calibration("CLOCKED")
        self.assertEqual(o["value"], "FAIL")
        self.assertEqual(P.no_carry_maximum("CLOCKED"), Fraction(1))
        self.assertEqual(o["witness"], {"j": 1, "policy": [1, 0, 1]})          # u_j = j mod 2
        self.assertEqual(o["reason"], "no-carry class reaches 1/1 > 1/2 at boundary 1")
        R._gate_outcome(o, "outcome", "P1")

    def test_calibration_reads_no_runtime(self):
        # P1 is a world-side fact (A4): the same result whatever runtime exists.
        self.assertEqual(P.calibration("STANDARD"), P.calibration("STANDARD"))
        self.assertNotIn("runs", P.calibration.__code__.co_varnames)


class TestAgreesWithConsumer(unittest.TestCase):
    """The consumer's G-RECOMP compares exactly these fields (checker.first_mismatch); they must agree."""

    def test_retention_fields_equal_the_consumer_recomputation(self):
        for cls in (Reg, Amnesiac, Flip, Leaky, Xor):
            runs = probe_a_runs(cls)
            mine = P.retention_from_runs(runs)
            self.assertIsNone(C.first_mismatch("RETENTION", mine, C.recompute("RETENTION", "STANDARD", runs)),
                              cls.__name__)

    def test_calibration_fields_equal_the_consumer_recomputation(self):
        for variant in ("STANDARD", "CLOCKED"):
            self.assertIsNone(C.first_mismatch("CALIBRATION", P.calibration(variant),
                                               C.recompute("CALIBRATION", variant, {})), variant)


class TestExpectedTable(unittest.TestCase):
    """T005's independent expected-answer table (rso/slice001/expected/EXPECTED_ANSWERS.json) agrees."""

    def test_t01_t02_rows(self):
        import json
        import os
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "expected",
                            "EXPECTED_ANSWERS.json")
        with open(path, encoding="utf-8") as f:
            rows = {r["id"]: r for r in json.load(f)["rows"]}
        got = {"T01.REG": retention(Reg), "T01.PKTD": retention(Pktd), "T02.AMNESIAC": retention(Amnesiac),
               "T02.FLIP": retention(Flip)}
        for case, o in sorted(got.items()):
            p = rows[case]["primary"]
            self.assertEqual((p["predicate"], p["outcome"]), ("RETENTION", o["value"]), case)
            for k in ("statistic", "successes", "trials"):
                if p.get(k) is not None:
                    self.assertEqual(p[k], o[k], (case, k))
        self.assertEqual(rows["T02.CLOCKED"]["primary"]["outcome"], P.calibration("CLOCKED")["value"])
        cal = [v for v in rows["T01.REG"]["other_verdicts"] if v["predicate"] == "CALIBRATION"][0]
        self.assertEqual((cal["outcome"], cal["eligible_count"]),
                         (P.calibration("STANDARD")["value"], P.calibration("STANDARD")["eligible_count"]))


if __name__ == "__main__":
    unittest.main()
