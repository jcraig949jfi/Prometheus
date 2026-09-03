"""V0.5 gate tests, frozen BEFORE any V0.5 measurement."""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from proteus.foundry import grammar  # noqa: E402
from proteus.foundry.affordances import AFFORDANCE_HASH, STORAGE_BOUNDS  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH  # noqa: E402
from proteus.foundry.prng import SplitMix64  # noqa: E402
from proteus.v0_5 import kernel as K  # noqa: E402
from proteus.v0_5 import multiplicity as M  # noqa: E402

V0_4_GRAMMAR = "5043f5e11a726b63a9553cc4855995c3ac324e55f8154ffe4adf28dad553a832"


class FrozenGrammar(unittest.TestCase):
    def test_grammar_is_exactly_v0_4(self):
        self.assertEqual(grammar.GRAMMAR_VERSION, "proteus.grammar.v0.4")
        self.assertEqual(grammar.GRAMMAR_HASH, V0_4_GRAMMAR)

    def test_no_operator_or_weight_moved(self):
        survivors = [o for o in grammar.OPERATORS_V0_2 if o[0] != "zeroing"]
        self.assertEqual(len(grammar.OPERATORS), 12)
        for (n, w, d), (n2, w2, d2) in zip(survivors, grammar.OPERATORS):
            self.assertEqual((n, d), (n2, d2))
            self.assertAlmostEqual(w2, w / 0.96, places=12)
        self.assertEqual(STORAGE_BOUNDS["tape_words"], {"min": 16, "max": 4096})
        self.assertEqual(STORAGE_BOUNDS["genome_words"], {"min": 4, "max": 4096})

    def test_runtime_and_affordance_unchanged(self):
        self.assertEqual(RUNTIME_HASH[:16], "73f110e21b9df879")
        self.assertEqual(AFFORDANCE_HASH[:16], "f1607ee8be680acc")

    def test_prior_verdicts_still_pinned(self):
        for path, key, val in (
            (("proteus", "v0_4", "PREREG_V0_4.json"), "grammar_hash", V0_4_GRAMMAR),
            (("proteus", "v0_4", "ADJUDICATION_V0_4.json"), "grammar_hash", V0_4_GRAMMAR),
            (("proteus", "v0_3", "PREREG_V0_3.json"), "grammar_hash", grammar.GRAMMAR_HASH_V0_3),
        ):
            with open(os.path.join(ROOT, *path), encoding="utf-8") as f:
                self.assertEqual(json.load(f)[key], val, path)


class GlobalMultiplicity(unittest.TestCase):
    def test_fixtures(self):
        for name, fx in M.FIXTURES.items():
            got = sorted(k for k, v in M.global_holm_agree(fx["cells"]).items() if v)
            self.assertEqual(got, fx["expected"], name)

    def test_within_cohort_can_pass_what_global_rejects(self):
        fx = M.FIXTURES["within_cohort_passes_but_global_does_not"]
        w = sorted(k for k, v in M.within_cohort_holm(fx["cells"]).items() if v)
        g = sorted(k for k, v in M.global_holm_agree(fx["cells"]).items() if v)
        self.assertEqual(w, fx["expected_within_cohort"])
        self.assertEqual(g, [])
        self.assertGreater(len(w), len(g))

    def test_implementations_agree_on_random_families(self):
        r = SplitMix64(20260905)
        for _ in range(200):
            n = 1 + r.randbelow(60)
            cells = [((f"c{i}", 1 + r.randbelow(5)), (r.unit() * 12) - 6) for i in range(n)]
            M.global_holm_agree(cells)

    def test_confirmatory_test_shape(self):
        c = M.confirmatory_test(3.0, -1, -1, 0.05)
        self.assertTrue(c["confirmed"])
        self.assertTrue(c["same_sign"])
        w = M.confirmatory_test(3.0, -1, +1, 0.05)
        self.assertFalse(w["confirmed"])
        weak = M.confirmatory_test(1.0, -1, -1, 0.05)
        self.assertFalse(weak["confirmed"])
        self.assertAlmostEqual(c["critical_z_one_sided"], 1.6449, places=3)


class KernelMachinery(unittest.TestCase):
    def test_state_space_enumeration(self):
        st = K.state_space((16, 32, 64, 128, 256), 64)
        self.assertEqual(len(st), 124)
        for L, T in st:
            self.assertLessEqual(L * 4, T)

    def test_rows_are_probability_distributions(self):
        st = K.state_space((16, 32), 8)
        P, _oc, tr = K.measure_kernel(st, 300, 1, "t")
        for s in st:
            self.assertAlmostEqual(sum(P[s].values()), 1.0, places=12)
            self.assertGreaterEqual(tr[s], 0.0)

    def test_reversible_reference_satisfies_detailed_balance(self):
        st = K.state_space((16, 32), 8)
        P, _oc, _tr = K.measure_kernel(st, 500, 2, "t2")
        pi, _it, _d = K.stationary(P, st)
        Q = K.reversible_reference(P, pi, st)
        for i in st:
            self.assertAlmostEqual(sum(Q[i].values()), 1.0, places=10)
            for j in st:
                if i == j:
                    continue
                self.assertAlmostEqual(pi[i] * Q[i].get(j, 0.0),
                                       pi[j] * Q[j].get(i, 0.0), places=15)

    def test_reversible_reference_preserves_pi(self):
        st = K.state_space((16, 32), 8)
        P, _oc, _tr = K.measure_kernel(st, 500, 3, "t3")
        pi, _it, _d = K.stationary(P, st)
        Q = K.reversible_reference(P, pi, st)
        for j in st:
            got = sum(pi[i] * Q[i].get(j, 0.0) for i in st)
            self.assertAlmostEqual(got, pi[j], places=12)

    def test_reversible_reference_has_zero_current(self):
        st = K.state_space((16, 32), 8)
        P, _oc, _tr = K.measure_kernel(st, 500, 4, "t4")
        pi, _it, _d = K.stationary(P, st)
        Q = K.reversible_reference(P, pi, st)
        for row in K.currents(Q, pi, st):
            self.assertLess(abs(row["J"]), 1e-15)

    def test_stationary_is_invariant(self):
        st = K.state_space((16, 32), 8)
        P, _oc, _tr = K.measure_kernel(st, 500, 5, "t5")
        pi, _it, _d = K.stationary(P, st)
        self.assertAlmostEqual(sum(pi.values()), 1.0, places=12)
        for j in st:
            got = sum(pi[i] * P[i].get(j, 0.0) for i in st)
            self.assertAlmostEqual(got, pi[j], places=9)


if __name__ == "__main__":
    unittest.main()
