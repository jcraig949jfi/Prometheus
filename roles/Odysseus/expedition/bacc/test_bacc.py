"""Known-answer tests for bacc (stdlib unittest).   python3 test_bacc.py"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bacc  # noqa: E402

NBITS, KC = 12, 3            # 12-bit genotypes; phenotype = first 3 bits (8 phenotypes x 512 genotypes)


def s_mut(g, rng, j):
    return g ^ (1 << rng.randrange(NBITS))


def s_eval(g):
    b = g & 0b111
    return b, bin(b).count("1") / 3


def s_eval_flat(g):
    return g & 0b111, 0.0


def s_sample(rng):
    return rng.randrange(1 << NBITS)


def ident(g):
    return g


def eq(s, s0):
    return abs(s - s0) < 1e-12


def gt(s, s0):
    return s > s0 + 1e-12


def hamming(a, b):
    return bin(a ^ b).count("1")


SPEC = bacc.Spec("synthetic", s_mut, s_eval, ident, eq, gt, s_sample, hamming)
FLAT = bacc.Spec("synthetic_flat", s_mut, s_eval_flat, ident, eq, gt, s_sample, hamming)


def nbrs(g):
    return [g ^ (1 << i) for i in range(NBITS)]


class Exact(unittest.TestCase):
    def test_exact_map(self):
        ex = bacc.exact_map(range(1 << NBITS), nbrs, lambda g: g & 0b111)
        self.assertEqual(ex["n_phenotypes"], 8)
        self.assertTrue(all(v == 512 for v in ex["size"].values()))
        self.assertTrue(all(abs(v - 9 / 12) < 1e-12 for v in ex["phen_robustness"].values()))
        self.assertTrue(all(v == 3 for v in ex["phen_evolvability"].values()))
        self.assertAlmostEqual(ex["geno_robustness_mean"], 9 / 12)
        self.assertAlmostEqual(ex["geno_evolvability_mean"], 3)
        self.assertEqual(len(ex["edges"]), 12)                       # the 3-cube
        self.assertEqual(len(bacc.components(set(range(8)), ex["edges"])), 1)
        one_third = {p for p in range(8) if bin(p).count("1") == 1}
        sub = [e for e in ex["edges"] if e[0] in one_third and e[1] in one_third]
        self.assertEqual(len(bacc.components(one_third, sub)), 3)    # neutral classes are islands


class Walks(unittest.TestCase):
    def test_islanded_neutral_region(self):
        parents = [("p%d" % i, (i << 3) | 0b001) for i in range(4)]
        walkers, null = bacc.run_all(SPEC, parents, W=2, D=15, m=48, null_n=400)
        per, summ = bacc.analyse(SPEC, walkers, null, 15)
        for pid, p in per.items():
            self.assertEqual(p["B"], 1)                 # a neutral walk cannot leave phenotype 001
            self.assertEqual(p["DOM"], 1.0)
            self.assertGreater(p["G"], 100)
            self.assertEqual(p["first_improving_L"], [1, 1])
            self.assertEqual(p["behav_dist_to_nearest_improving"], 1)
            self.assertEqual(p["phenotype_evolvability_parent_class"], 3)
            self.assertAlmostEqual(p["parent_class_robustness"], 0.75, delta=0.05)
            self.assertAlmostEqual(p["genotype_evolvability_mean"], 3, delta=0.2)
            self.assertEqual(p["neutral_components"], 1)
            self.assertAlmostEqual(p["null_share_parent_behaviour"], 1 / 8, delta=0.04)
            self.assertLess(p["relative_poverty"], 0.5)
            self.assertAlmostEqual(sum(x for x in p["imp_rate_by_d"]) / 16, 2 / 12, delta=0.03)
        self.assertTrue(summ["BEHAVIOURAL_POVERTY"])

    def test_flat_connected(self):
        parents = [("q%d" % i, i << 3) for i in range(3)]
        walkers, null = bacc.run_all(FLAT, parents, W=2, D=80, m=24, null_n=200)
        per, summ = bacc.analyse(FLAT, walkers, null, 80)
        for p in per.values():
            self.assertEqual(p["B"], 8)
            self.assertEqual(p["neutral_classes"], 8)
            self.assertEqual(p["neutral_components"], 1)
            self.assertAlmostEqual(p["DOM"], 1 / 8, delta=0.1)
            self.assertAlmostEqual(p["H_bits"], 3.0, delta=0.4)   # finite autocorrelated walk: 2 walkers x 81 nodes
            self.assertIsNone(p["behav_dist_to_nearest_improving"])
        self.assertFalse(summ["BEHAVIOURAL_POVERTY"])

    def test_determinism_and_helpers(self):
        a = bacc.walk(SPEC, 1, "x", 0, 5, 8)
        b = bacc.walk(SPEC, 1, "x", 0, 5, 8)
        self.assertEqual(a, b)
        from collections import Counter
        self.assertAlmostEqual(bacc.entropy_bits(Counter({1: 1, 2: 1, 3: 1, 4: 1})), 2.0)
        self.assertEqual(bacc.rarefied_distinct([1, 1, 2, 2], 4), 2.0)
        self.assertAlmostEqual(bacc.slope([0, 1, 2], [1, 3, 5]), 2.0)

    def test_novelty_known(self):
        # flat map from phenotype 0: depth-0 probes see <= 3 new classes; later depths mostly revisits
        wk = bacc.walk(FLAT, 0, "n", 0, 80, 24)
        nov, nov_n, rev, E, G = bacc.walker_novelty(wk, 80)
        self.assertEqual(E[80], 8)
        self.assertLessEqual(E[0], 4)
        self.assertLess(sum(nov[d] for d in range(60, 81)) / 21, nov[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
