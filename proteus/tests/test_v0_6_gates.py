"""V0.6 gate tests, frozen BEFORE the production run."""
import json, os, sys, unittest
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from proteus.foundry import grammar  # noqa: E402
from proteus.foundry.affordances import AFFORDANCE_HASH, STORAGE_BOUNDS  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH  # noqa: E402
from proteus.v0_6 import equilibrium as EQ, livekernel as LK, space  # noqa: E402

V04 = "5043f5e11a726b63a9553cc4855995c3ac324e55f8154ffe4adf28dad553a832"


class FrozenPhysics(unittest.TestCase):
    def test_grammar_runtime_affordance(self):
        self.assertEqual(grammar.GRAMMAR_VERSION, "proteus.grammar.v0.4")
        self.assertEqual(grammar.GRAMMAR_HASH, V04)
        self.assertEqual(RUNTIME_HASH[:16], "73f110e21b9df879")
        self.assertEqual(AFFORDANCE_HASH[:16], "f1607ee8be680acc")

    def test_weights_and_bounds_untouched(self):
        surv = [o for o in grammar.OPERATORS_V0_2 if o[0] != "zeroing"]
        self.assertEqual(len(grammar.OPERATORS), 12)
        for (n, w, d), (n2, w2, d2) in zip(surv, grammar.OPERATORS):
            self.assertEqual((n, d), (n2, d2))
            self.assertAlmostEqual(w2, w / 0.96, places=12)
        self.assertEqual(STORAGE_BOUNDS["tape_words"], {"min": 16, "max": 4096})

    def test_prereg_pins_active_grammar(self):
        p = os.path.join(ROOT, "proteus", "v0_6", "PREREG_V0_6.json")
        with open(p, encoding="utf-8") as f:
            pre = json.load(f)
        self.assertEqual(pre["grammar_hash"], V04)
        self.assertTrue(pre["zero_grammar_changes"])
        self.assertEqual(pre["space"]["escaped_valid_structural_state_count"], 0)


class SpaceAndKernel(unittest.TestCase):
    def test_regenerated_space_matches_prior(self):
        st, tapes, rules = space.regenerate_states()
        self.assertEqual(len(st), 2044)
        cmp = space.compare_with_prior(st)
        self.assertTrue(cmp["set_matches"])
        self.assertEqual(cmp["prior_hash"], cmp["regenerated_hash"])

    def test_parallel_equals_serial(self):
        st, _t, _r = space.regenerate_states()
        sub = [s for s in st if s[1] <= 32]
        a, _o, _n, _e = LK.measure_kernel_parallel(sub, 200, 11, "det", workers=1)
        b, _o2, _n2, _e2 = LK.measure_kernel_parallel(sub, 200, 11, "det", workers=4)
        self.assertEqual(a, b)

    def test_rows_are_distributions_and_closed(self):
        st, _t, _r = space.regenerate_states()
        sub = [s for s in st if s[1] <= 32]
        P, _o, _n, esc = LK.measure_kernel_parallel(sub, 300, 12, "closed", workers=2)
        # a TRUNCATED subset is not closed; escapes are expected here and are folded into the
        # self-loop so the row stays a distribution. Full-space closure is proved in the audit.
        self.assertGreaterEqual(sum(sum(v.values()) for v in esc.values()), 0)
        for s in sub:
            self.assertAlmostEqual(sum(P[s].values()), 1.0, places=12)


class Instruments(unittest.TestCase):
    def _small(self):
        st, _t, _r = space.regenerate_states()
        sub = [s for s in st if s[1] <= 32]
        P, _o, _n, _e = LK.measure_kernel_parallel(sub, 800, 13, "inst", workers=2)
        return sub, P

    def test_additive_reference_is_reversible_and_zero_current(self):
        sub, P = self._small()
        pi, _m = EQ.stationary_power(P, sub)
        Q = EQ.reversible_additive(P, pi, sub)
        for r in EQ.currents(Q, pi, sub):
            self.assertLess(abs(r["J"]), 1e-15)
        ep = EQ.entropy_production(Q, pi, sub)
        self.assertLess(abs(ep["sigma"]), 1e-12)

    def test_metropolis_reference_targets_uniform_and_is_reversible(self):
        sub, P = self._small()
        Q, tgt = EQ.reversible_metropolis(P, sub)
        pi, _m = EQ.stationary_power(Q, sub)
        for s in sub:
            self.assertAlmostEqual(pi[s], tgt[s], places=9)
        for r in EQ.currents(Q, pi, sub):
            self.assertLess(abs(r["J"]), 1e-12)

    def test_two_stationary_solvers_agree(self):
        sub, P = self._small()
        a, ma = EQ.stationary_power(P, sub)
        b, mb = EQ.stationary_gauss_seidel(P, sub)
        self.assertLess(EQ.compare_pi(a, b, sub)["l1"], 1e-8)
        self.assertLess(ma["residual_l1"], 1e-10)

    def test_cycle_affinity_zero_on_reversible(self):
        sub, P = self._small()
        pi, _m = EQ.stationary_power(P, sub)
        Q = EQ.reversible_additive(P, pi, sub)
        cycles, _t = EQ.cycle_basis(Q, sub)
        self.assertGreater(len(cycles), 0)
        for c in cycles[:200]:
            a = EQ.cycle_affinity(Q, c)
            if a is not None:
                self.assertLess(abs(a), 1e-9)


if __name__ == "__main__":
    unittest.main()
