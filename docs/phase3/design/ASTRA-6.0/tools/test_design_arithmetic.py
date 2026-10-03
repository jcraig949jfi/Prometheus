"""Exact finite-law/planning checks, not an A0 implementation or field qualification."""

from collections import defaultdict
from fractions import Fraction as F
from itertools import product
import math
from pathlib import Path
from statistics import NormalDist
import unittest


def world(correlated=False):
    """Rows: hidden truth, observed cues, public price, exact probability."""
    rows = []
    for h, q in product((0, 1), (F(1, 32), F(1, 8))):
        for bits in product((0, 1), repeat=2 if correlated else 3):
            weight = F(1, 4)
            for bit in bits:
                weight *= F(3 if bit == h else 1, 4)
            cues = (bits[0], bits[1], bits[1]) if correlated else bits
            rows.append((h, cues, q, weight))
    return rows


def optimal_accuracy(rows, visible):
    posterior = defaultdict(lambda: [F(0), F(0)])
    for h, cues, q, weight in rows:
        posterior[(q,) + tuple(cues[i] for i in visible)][h] += weight
    return sum(max(masses) for masses in posterior.values())


def binomial_tail(n, p, lo, hi):
    return sum(math.comb(n, k) * p**k * (1-p)**(n-k) for k in range(lo, hi+1))


class DesignArithmeticTests(unittest.TestCase):
    def test_weighted_support_and_normalization(self):
        for correlated, count in ((False, 32), (True, 16)):
            rows = world(correlated)
            self.assertEqual(len(rows), count)
            self.assertEqual(sum(row[3] for row in rows), 1)
            self.assertTrue(all(row[3] > 0 for row in rows))

    def test_independent_majority_and_retained_cue_demand(self):
        rows = world()
        majority = sum(w for h, c, _, w in rows if int(sum(c) >= 2) == h)
        disagreement = sum(w for _, c, _, w in rows if c[1] != c[2])
        self.assertEqual(majority, F(27, 32))
        self.assertEqual(majority, optimal_accuracy(rows, (0, 1, 2)))
        self.assertEqual(disagreement, F(3, 8))
        self.assertEqual(optimal_accuracy(rows, (1, 2)), F(3, 4))
        self.assertEqual(optimal_accuracy(rows, (0,)), F(3, 4))

    def test_correlation_changes_optimal_query_policy(self):
        for correlated, expected in ((False, (F(26, 32), F(23, 32))),
                                     (True, (F(23, 32), F(20, 32)))):
            rows = world(correlated)
            # Optimize for each information state available BEFORE buying cues.
            for c1, (q, utility) in product((0, 1), zip((F(1, 32), F(1, 8)), expected)):
                subset = [row for row in rows if row[1][0] == c1 and row[2] == q]
                mass = sum(row[3] for row in subset)
                buy = optimal_accuracy(subset, (0, 1, 2)) / mass - q
                stop = optimal_accuracy(subset, (0,)) / mass
                self.assertEqual(buy, utility)
                self.assertEqual(stop, F(3, 4))
                self.assertEqual(buy > stop, not correlated and q == F(1, 32))

    def test_headroom_and_primary_stratum(self):
        gain = F(26, 32) - F(3, 4)
        self.assertEqual(gain, F(1, 16))
        self.assertEqual(gain / F(5, 4), F(1, 20))
        self.assertEqual(gain / F(5, 4) / 2 / 2, F(1, 80))
        self.assertLess(F(2, 100), gain / F(5, 4))

    def test_binomial_acceptance_boundaries(self):
        self.assertLess(binomial_tail(128, .8, 111, 128), .05)
        self.assertGreater(binomial_tail(128, .8, 110, 128), .05)
        self.assertLess(binomial_tail(128, .05, 0, 2), .05)
        self.assertGreater(binomial_tail(128, .05, 0, 3), .05)
        self.assertAlmostEqual(binomial_tail(128, .9, 111, 128), .91250, places=5)
        self.assertAlmostEqual(binomial_tail(128, .005, 0, 2), .97312, places=5)

    def test_normal_power_is_detection_not_threshold_certification(self):
        normal = NormalDist()
        z = normal.inv_cdf(1 - .0125 / 2)
        signal = .2 / (.5 / math.sqrt(96))
        power = 1 - normal.cdf(z - signal) + normal.cdf(-z - signal)
        self.assertAlmostEqual(power, .92241, places=5)
        self.assertEqual(math.ceil(((z + normal.inv_cdf(.8)) * .5 / .2)**2), 70)
        self.assertEqual(math.ceil((3.34 * .4 / .02)**2), 4463)
        self.assertAlmostEqual(.02 * math.sqrt(96) / 3.34, .05867, places=5)

    def test_units_and_conditional_zero_hit_bound(self):
        self.assertEqual((128 + 128) * 96, 24576)
        self.assertEqual(8 + 4 + 2 + 2 + 2 + 2, 20)
        self.assertEqual((12 * 20, 96 * 20), (240, 1920))
        self.assertAlmostEqual(1 - .05**(1/96), .030724, places=6)
        self.assertGreater(.05**(1/14), .8)
        self.assertLess(1 - .05**(1/59), .05)

    def test_tariff_hand_arithmetic_not_native_execution(self):
        self.assertEqual(16 * 8 + 2 + 1 + 1, 132)
        self.assertEqual(12 + 62 * 16 + 2 + 3 + 14, 1023)
        self.assertGreater(1023 + 2, 1024)
        self.assertEqual(12 + 63 * 16, 1020)
        self.assertEqual(12 + 5 * 14 + 4 * 2 + 26 + 2 + 4 + 1, 123)

    def test_live_document_budget_tables(self):
        package = Path(__file__).absolute().parents[1]
        mvp = (package / "MVP_90_DAYS.md").read_text(encoding="utf-8")
        portfolio = (package / "ENGINE_PORTFOLIO.md").read_text(encoding="utf-8")
        activity, energy, tokens, phase = [], [], [], []
        for line in mvp.splitlines():
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) == 8 and cells[0].startswith("Q"):
                numbers = [int(c) for c in cells[1:5]]
                self.assertEqual(sum(numbers[:3]), numbers[3])
                activity.append(numbers)
                energy.append(F(cells[6]))
                tokens.append(int(cells[7].replace(",", "")))
        for line in portfolio.splitlines():
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) == 7 and (cells[0].startswith("Q") or cells[0] == "Protected fault/correction audit"):
                numbers = [int(c) for c in cells[1:]]
                self.assertEqual(sum(numbers[:-1]), numbers[-1])
                phase.append(numbers)
        self.assertEqual(len(activity), 6)
        self.assertEqual([sum(row[i] for row in activity[:5]) for i in range(4)], [108, 186, 78, 372])
        self.assertEqual(sum(row[3] for row in activity) + 36, 480)
        self.assertEqual(sum(energy) + F(9, 2), 30)
        self.assertEqual(sum(tokens) + 2000, 20000)
        self.assertEqual(len(phase), 7)
        self.assertEqual([sum(row[i] for row in phase) for i in range(6)], [72, 120, 180, 72, 36, 480])


if __name__ == "__main__":
    unittest.main()