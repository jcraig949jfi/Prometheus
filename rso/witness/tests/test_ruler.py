"""Tests for the stochastic retention ruler P-RET and the calibration gate P-CAL (C-009-T014).

SYNTHETIC DATA ONLY (SELECTION.md gate): every episode below is generated here from a stated model (random.Random
with a fixed seed); no Ares organism, world or output is read. Expected values come from RULER.md (computed before
any data), never from the ruler's own output. Python >= 3.8, standard library only.
"""
import os
import random
import unittest
from fractions import Fraction

from rso.witness import ruler as RU

N = RU.N_EPISODES
HALF = N // 2


def balanced(decide, seed=0):
    """N synthetic episodes, exactly half with r = 1, decision = decide(r, rng)."""
    rng = random.Random(seed)
    rs = [0] * HALF + [1] * HALF
    rng.shuffle(rs)
    return [(r, decide(r, rng)) for r in rs]


def with_accuracy(p):
    """A subject that answers correctly with probability p, otherwise the other action (never abstains)."""
    return lambda r, rng: r + 1 if rng.random() < p else 2 - r


def coin(r, rng):                          # no carry: decision independent of r
    return rng.choice((1, 2))


def coin_or_abstain(r, rng):               # no carry, abstains half the time
    return RU.NO_ANSWER if rng.random() < 0.5 else rng.choice((1, 2))


def exact_count(correct_n, wrong_n):
    """A deterministic balanced episode list with the given numbers of correct and wrong answers."""
    eps, c, w = [], correct_n, wrong_n
    for i in range(N):
        r = i % 2
        if c:
            eps.append((r, r + 1)); c -= 1
        elif w:
            eps.append((r, 2 - r)); w -= 1
        else:
            eps.append((r, RU.NO_ANSWER))
    return eps


class TestRegistration(unittest.TestCase):
    def test_registered_values(self):
        self.assertEqual((N, RU.ALPHA, RU.DELTA, RU.BOUND), (2048, Fraction(1, 100), Fraction(1, 20), Fraction(1, 2)))
        self.assertEqual(RU.thresholds(), {"n": 2048, "k_pos": 1078, "k_neg": 1073})

    def test_thresholds_are_the_exact_boundaries(self):
        th = RU.thresholds()
        self.assertLessEqual(RU.tail_ge(N, th["k_pos"], RU.BOUND), RU.ALPHA)
        self.assertGreater(RU.tail_ge(N, th["k_pos"] - 1, RU.BOUND), RU.ALPHA)
        self.assertLessEqual(RU.tail_le(N, th["k_neg"], RU.BOUND + RU.DELTA), RU.ALPHA)
        self.assertGreater(RU.tail_le(N, th["k_neg"] + 1, RU.BOUND + RU.DELTA), RU.ALPHA)

    def test_size_and_power_exact(self):
        # RULER.md s4, before any data.
        null = RU.outcome_probabilities(Fraction(1, 2))
        self.assertLessEqual(null["POSITIVE"], RU.ALPHA)              # size of POSITIVE under no carry
        self.assertLessEqual(null["NOT_SHOWN"], RU.ALPHA)
        self.assertGreaterEqual(null["NEGATIVE"], Fraction(95, 100))   # power to call NEGATIVE at the bound
        edge = RU.outcome_probabilities(RU.BOUND + RU.DELTA)
        self.assertLessEqual(edge["NEGATIVE"], RU.ALPHA)               # equivalence size at bound + delta
        self.assertGreaterEqual(edge["POSITIVE"], Fraction(95, 100))   # power at the smallest effect of interest
        self.assertEqual(sum(null.values()), 1)

    def test_small_n_is_refused_odd(self):
        with self.assertRaises(RU.RulerError):
            RU.thresholds(7)


class TestEpisodeDecision(unittest.TestCase):
    def test_majority_after_the_last_interrupt(self):
        acts = [2, 2, 2, 2, 2, 1, 1, 0, 1]
        self.assertEqual(RU.episode_decision(acts, last_interrupt=4), 1)   # steps 5..8: 1, 1, 0, 1
        self.assertEqual(RU.episode_decision(acts, last_interrupt=-1), 2)  # whole episode: 5 x 2, 3 x 1

    def test_tie_and_abstain_are_no_answer(self):
        self.assertEqual(RU.episode_decision([1, 2, 0, 0], last_interrupt=-1), RU.NO_ANSWER)
        self.assertEqual(RU.episode_decision([1, 1, 0, 0], last_interrupt=1), RU.NO_ANSWER)

    def test_scoring(self):
        self.assertEqual([RU.correct(d, 0) for d in (0, 1, 2)], [0, 1, 0])
        self.assertEqual([RU.wrong(d, 0) for d in (0, 1, 2)], [0, 0, 1])
        with self.assertRaises(RU.RulerError):
            RU.episode_decision([3], -1)


class TestRuler(unittest.TestCase):
    def test_outcomes_at_the_thresholds(self):
        th = RU.thresholds()
        self.assertEqual(RU.p_ret(exact_count(th["k_pos"], 0))["value"], "POSITIVE")
        self.assertEqual(RU.p_ret(exact_count(th["k_pos"] - 1, 0))["value"], "INDETERMINATE")
        self.assertEqual(RU.p_ret(exact_count(th["k_neg"], 0))["value"], "NEGATIVE")
        self.assertEqual(RU.p_ret(exact_count(th["k_neg"] + 1, 0))["value"], "INDETERMINATE")
        self.assertEqual(RU.p_ret(exact_count(0, th["k_pos"]))["value"], "NOT_SHOWN")

    def test_constant_answer_is_negative(self):
        # A no-carry subject that always picks action 1: exactly N/2 correct by the balanced design.
        o = RU.p_ret(balanced(lambda r, rng: 1))
        self.assertEqual((o["value"], o["successes"], o["statistic"]), ("NEGATIVE", HALF, "1/2"))

    def test_abstaining_subject_is_never_not_shown(self):
        # FD-T014-2: abstention lowers accuracy without any dependence on r; it must not read as inverted retention.
        self.assertEqual(RU.p_ret(balanced(lambda r, rng: RU.NO_ANSWER))["value"], "NEGATIVE")
        self.assertEqual(RU.p_ret(balanced(coin_or_abstain, 3))["value"], "NEGATIVE")

    def test_retaining_and_inverted_subjects(self):
        self.assertEqual(RU.p_ret(balanced(with_accuracy(0.6), 1))["value"], "POSITIVE")
        self.assertEqual(RU.p_ret(balanced(with_accuracy(0.4), 2))["value"], "NOT_SHOWN")

    def test_outcome_shape_is_a_ruler_never_pass_fail(self):
        o = RU.p_ret(balanced(coin, 4))
        self.assertEqual(o["kind"], "RULER")
        self.assertIn(o["value"], RU.RULER_VALUES)
        self.assertNotIn(o["value"], ("PASS", "FAIL"))
        self.assertEqual(o["thresholds"], RU.thresholds())

    def test_design_is_enforced(self):
        with self.assertRaises(RU.RulerError):
            RU.p_ret(balanced(coin)[:-2])
        unbalanced = [(1, 2)] * N
        with self.assertRaises(RU.RulerError):
            RU.p_ret(unbalanced)


class TestSizeUnderTheNull(unittest.TestCase):
    """Monte Carlo on synthetic no-carry subjects: the rate of a false POSITIVE (and of a false NOT_SHOWN) stays
    within alpha plus three Monte Carlo standard errors."""

    REPS = 600

    def _rate(self, decide, value, seed):
        hits = sum(RU.p_ret(balanced(decide, seed * 100000 + i))["value"] == value for i in range(self.REPS))
        return hits / self.REPS

    def _limit(self):
        a = float(RU.ALPHA)
        return a + 3 * (a * (1 - a) / self.REPS) ** 0.5

    def test_fair_coin(self):
        self.assertLessEqual(self._rate(coin, "POSITIVE", 1), self._limit())
        self.assertLessEqual(self._rate(coin, "NOT_SHOWN", 2), self._limit())

    def test_abstaining_coin(self):
        self.assertLessEqual(self._rate(coin_or_abstain, "POSITIVE", 3), self._limit())
        self.assertLessEqual(self._rate(coin_or_abstain, "NOT_SHOWN", 4), self._limit())


class TestCalibrationGate(unittest.TestCase):
    def test_pass(self):
        g = RU.p_cal(balanced(coin, 5), balanced(lambda r, rng: 1), balanced(with_accuracy(0.9), 6))
        self.assertEqual((g["kind"], g["predicate"], g["value"], g["witness"]), ("GATE", "P-CAL", "PASS", None))

    def test_abstaining_null_still_calibrates(self):
        g = RU.p_cal(balanced(coin_or_abstain, 7), balanced(coin, 8), balanced(with_accuracy(0.9), 9))
        self.assertEqual(g["value"], "PASS")

    def test_leaking_null_fails(self):
        g = RU.p_cal(balanced(with_accuracy(0.6), 10), balanced(coin, 11), balanced(with_accuracy(0.9), 12))
        self.assertEqual((g["value"], g["witness"]["arm"]), ("FAIL", "NULL"))

    def test_leaking_shuffled_world_fails(self):
        g = RU.p_cal(balanced(coin, 13), balanced(with_accuracy(0.6), 14), balanced(with_accuracy(0.9), 15))
        self.assertEqual((g["value"], g["witness"]["arm"]), ("FAIL", "SHUF"))

    def test_undetected_positive_control_fails(self):
        g = RU.p_cal(balanced(coin, 16), balanced(coin, 17), balanced(coin, 18))
        self.assertEqual((g["value"], g["witness"]["arm"]), ("FAIL", "POS"))
        self.assertIn("positive control not detected", g["reason"])


class TestNoWitnessData(unittest.TestCase):
    def test_ruler_reads_no_ares(self):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ruler.py")
        with open(path, encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("import ares", src)
        self.assertNotIn("from ares", src)


if __name__ == "__main__":
    unittest.main()
