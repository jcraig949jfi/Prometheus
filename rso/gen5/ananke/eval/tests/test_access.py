"""Accessibility statistics on synthetic data with known answers (C-019-T040 item 4). Written before access.py."""
import json
import math
import unittest

import numpy as np

from rso.gen5.ananke.eval import access as A


class ExactCI(unittest.TestCase):
    def test_owner_recorded_bounds(self):
        # RESULT_PTE_C4.md s2/s5 (@ f58362c5e): 0/32 -> .109, 0/24 -> .142, 0/96 -> .038, 0/72 -> .050, 2/32 -> .008-.208
        self.assertAlmostEqual(A.cp_interval(0, 32)[1], 0.109, places=3)
        self.assertAlmostEqual(A.cp_interval(0, 24)[1], 0.142, places=3)
        self.assertAlmostEqual(A.cp_interval(0, 96)[1], 0.038, places=3)
        self.assertAlmostEqual(A.cp_interval(0, 72)[1], 0.050, places=3)
        lo, hi = A.cp_interval(2, 32)
        self.assertAlmostEqual(lo, 0.008, places=3); self.assertAlmostEqual(hi, 0.208, places=3)

    def test_edges(self):
        self.assertEqual(A.cp_interval(0, 10)[0], 0.0)
        self.assertEqual(A.cp_interval(10, 10)[1], 1.0)
        with self.assertRaises(ValueError):
            A.cp_interval(3, 2)
        with self.assertRaises(ValueError):
            A.cp_interval(0, 0)


class Fisher(unittest.TestCase):
    def test_coordination_numbers(self):
        # rso/gen5/ananke/COORDINATION.md s3: 5/32 vs 0/32 one-sided p ~ .03
        self.assertAlmostEqual(A.fisher_one_sided(5, 32, 0, 32), math.comb(32, 5) / math.comb(64, 5), places=12)
        self.assertLess(A.fisher_one_sided(5, 32, 0, 32), 0.03)
        self.assertGreater(A.fisher_one_sided(4, 32, 0, 32), 0.05)
        self.assertEqual(A.fisher_one_sided(0, 32, 0, 32), 1.0)
        self.assertAlmostEqual(A.fisher_one_sided(0, 32, 5, 32), 1.0, places=12)


class KaplanMeier(unittest.TestCase):
    def test_all_observed(self):
        km = A.km([1, 2, 3], [True, True, True])
        self.assertEqual([round(s, 12) for s in km["S"]], [round(2 / 3, 12), round(1 / 3, 12), 0.0])
        self.assertEqual(km["median"], 2)

    def test_textbook_censoring(self):
        # times 1,2+,3,4+ : S(1) = 3/4, S(3) = 3/4 * 1/2 = 3/8
        km = A.km([1, 2, 3, 4], [True, False, True, False])
        self.assertEqual(km["t"], [1, 3])
        self.assertAlmostEqual(km["S"][0], 0.75); self.assertAlmostEqual(km["S"][1], 0.375)
        self.assertEqual(km["median"], 3)

    def test_all_censored_arm_is_finite(self):
        km = A.km([36] * 32, [False] * 32)
        self.assertEqual(km["t"], []); self.assertEqual(km["S"], [])
        self.assertEqual(km["median"], "NOT_REACHED")
        self.assertEqual(km["p_by_budget"], 0.0)
        self.assertEqual(km["rmst"], 36.0)            # restricted mean = the budget, never infinity
        json.dumps(km, allow_nan=False)               # no inf / nan anywhere

    def test_zero_time_censoring_not_run(self):
        with self.assertRaises(ValueError):
            A.km([0, 5], [False, True])                # a search that never ran is excluded upstream, not censored at 0

    def test_synthetic_geometric_rate(self):
        rng = np.random.default_rng(7)
        p, budget, n = 0.05, 36, 4000
        t = rng.geometric(p, n)
        obs = t <= budget
        km = A.km(np.minimum(t, budget).tolist(), obs.tolist())
        truth = 1 - (1 - p) ** budget
        self.assertAlmostEqual(km["p_by_budget"], truth, delta=0.03)
        self.assertAlmostEqual(1 - A.S_at(km, 10), 1 - (1 - p) ** 10, delta=0.03)

    def test_logrank_known(self):
        same = A.logrank([1, 2, 3, 4], [True] * 4, [1, 2, 3, 4], [True] * 4)
        self.assertAlmostEqual(same["chi2"], 0.0, places=12)
        far = A.logrank([1] * 20, [True] * 20, [36] * 20, [False] * 20)
        self.assertLess(far["p"], 1e-6)


class Paired(unittest.TestCase):
    def test_mcnemar_exact(self):
        # 6 (cell, idx) pairs where REUSE hit and CONTROL missed, 0 the other way: one-sided p = .5**6
        rows = [(True, False)] * 6 + [(False, False)] * 26
        r = A.paired_binary(rows)
        self.assertEqual((r["b"], r["c"]), (6, 0))
        self.assertAlmostEqual(r["p_one_sided"], 0.5 ** 6)
        self.assertEqual(A.paired_binary([(False, False)] * 32)["p_one_sided"], 1.0)

    def test_paired_times_censoring(self):
        # (t_reuse, hit_reuse, t_ctrl, hit_ctrl): decidable when the earlier time is an observed hit
        rows = [(5, True, 36, False), (10, True, 8, True), (36, False, 36, False), (36, False, 12, True)]
        r = A.paired_times(rows)
        self.assertEqual((r["reuse_first"], r["control_first"], r["undecidable"]), (1, 2, 1))


class Power(unittest.TestCase):
    def test_power_monotone_and_known(self):
        p_hi = A.power_fisher(0.0, 0.25, 32, alpha=0.05)
        p_lo = A.power_fisher(0.0, 0.05, 32, alpha=0.05)
        self.assertGreater(p_hi, 0.9); self.assertLess(p_lo, 0.35)   # p_hi = P(Bin(32,.25) >= 5) = .930
        self.assertEqual(A.power_fisher(0.1, 0.1, 32, alpha=0.05) <= 0.05 + 1e-12, True)   # size <= alpha at the null

    def test_exact_power_by_enumeration(self):
        # p0 = 0 means control is always 0/n; the test rejects iff k1 >= kmin, so power = P(Bin(n, p1) >= kmin)
        n, p1 = 32, 0.2
        kmin = min(k for k in range(n + 1) if A.fisher_one_sided(k, n, 0, n) <= 0.05)
        exact = sum(math.comb(n, k) * p1 ** k * (1 - p1) ** (n - k) for k in range(kmin, n + 1))
        self.assertAlmostEqual(A.power_fisher(0.0, p1, n, alpha=0.05), exact, places=12)

    def test_detectable(self):
        d = A.min_detectable(0.0625, 32, alpha=0.05, power=0.8)
        self.assertGreater(d, 0.25); self.assertLess(d, 0.5)
        self.assertGreaterEqual(A.power_fisher(0.0625, d, 32, 0.05), 0.8)
        self.assertGreater(A.n_per_arm(0.0625, 0.25, alpha=0.05, power=0.8), 32)


def _row(arm, cell, idx, cks, budget=36, ran=True):
    hit_gen = next((c["gen"] for c in cks if c["status"] == "TRUE"), None)
    return {"arm": arm, "cell": cell, "idx": idx, "ran": ran, "budget": budget, "checkpoints": cks,
            "hit": hit_gen is not None, "time": hit_gen if hit_gen is not None else (max([c["gen"] for c in cks]) if cks else 0)}


def _cks(hit_at=None, last=36, every=6):
    return [{"gen": g, "status": "TRUE" if hit_at is not None and g >= hit_at else "FALSE"} for g in range(every, last + 1, every)]


class SearchTable(unittest.TestCase):
    def table(self):
        rows = []
        for idx in range(8):
            rows.append(_row("CONTROL", "c0", idx, _cks(None)))
            rows.append(_row("REUSE", "c0", idx, _cks(12 if idx < 4 else None)))
        return rows

    def test_valid_table_and_comparison(self):
        rows = self.table()
        self.assertEqual(A.validate_searches(rows, ("CONTROL", "REUSE")), [])
        r = A.compare_arms(rows, "REUSE", "CONTROL")
        self.assertEqual((r["arm1"]["hits"], r["arm0"]["hits"], r["paired"]["b"], r["paired"]["c"]), (4, 0, 4, 0))
        self.assertEqual(r["arm0"]["km"]["median"], "NOT_REACHED")
        json.dumps(r, allow_nan=False)

    def test_refusals(self):
        rows = self.table()
        self.assertTrue(A.validate_searches(rows[1:], ("CONTROL", "REUSE")))                       # unpaired
        dup = [dict(r) for r in rows]; dup[2] = dict(dup[0])
        self.assertTrue(A.validate_searches(dup, ("CONTROL", "REUSE")))                            # duplicate key
        forged = [dict(r) for r in rows]; forged[0] = dict(forged[0], hit=True, time=6)
        self.assertTrue(A.validate_searches(forged, ("CONTROL", "REUSE")))                         # hit without a TRUE checkpoint
        scrub = [dict(r) for r in rows]; del scrub[1]["checkpoints"]
        self.assertTrue(A.validate_searches(scrub, ("CONTROL", "REUSE")))
        over = [dict(r) for r in rows]; over[1] = dict(over[1], time=40)
        self.assertTrue(A.validate_searches(over, ("CONTROL", "REUSE")))                           # past the budget

    def test_not_run_excluded_and_counted(self):
        rows = self.table()
        rows[0] = dict(rows[0], ran=False, checkpoints=[], hit=False, time=0)
        rows[1] = dict(rows[1], ran=False, checkpoints=[], hit=False, time=0)
        self.assertEqual(A.validate_searches(rows, ("CONTROL", "REUSE")), [])
        r = A.compare_arms(rows, "REUSE", "CONTROL")
        self.assertEqual((r["arm1"]["not_run"], r["arm1"]["n"], r["paired"]["pairs"]), (1, 7, 7))


if __name__ == "__main__":
    unittest.main()
