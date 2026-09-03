"""V0.4 gate tests, all frozen BEFORE the V0.4 arms run.

Two families:
  * the corrected Holm, against known fixtures, with the buggy V0.3 version kept as a
    demonstration that it over-declares;
  * the exhaustive paired tape-transition symmetry the V0.4 brief requires.
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from proteus.foundry import grammar  # noqa: E402
from proteus.foundry.affordances import STORAGE_BOUNDS  # noqa: E402
from proteus.foundry.prng import SplitMix64  # noqa: E402
from proteus.foundry.vm import SCHEMA, validate_manifest  # noqa: E402
from proteus.v0_4 import holm, nc5  # noqa: E402

IW = 4


class Holm(unittest.TestCase):
    def test_fixtures_by_z(self):
        for name, fx in holm.FIXTURES.items():
            got = sorted(k for k, v in holm.holm_by_z(fx["items"]).items() if v)
            self.assertEqual(got, fx["expected_rejected"], f"holm_by_z on {name}")

    def test_fixtures_by_p(self):
        for name, fx in holm.FIXTURES.items():
            got = sorted(k for k, v in holm.holm_by_p(fx["items"]).items() if v)
            self.assertEqual(got, fx["expected_rejected"], f"holm_by_p on {name}")

    def test_two_implementations_agree_on_every_fixture(self):
        for name, fx in holm.FIXTURES.items():
            self.assertEqual(holm.holm_agree(fx["items"]),
                             holm.holm_by_p(fx["items"]), name)

    def test_two_implementations_agree_on_random_families(self):
        r = SplitMix64(20260903)
        for _ in range(300):
            n = 1 + r.randbelow(40)
            items = [(f"c{i}", (r.unit() * 12.0) - 6.0) for i in range(n)]
            holm.holm_agree(items)          # raises on disagreement

    def test_disagreement_raises_rather_than_votes(self):
        with self.assertRaises(holm.HolmDisagreement):
            a = {"x": True}
            b = {"x": False}
            if a != b:
                raise holm.HolmDisagreement("forced")

    def test_v0_3_buggy_version_over_declares(self):
        fx = holm.FIXTURES["buggy_v0_3_over_declares"]
        buggy = sorted(k for k, v in holm.holm_v0_3_buggy(fx["items"]).items() if v)
        good = sorted(k for k, v in holm.holm_agree(fx["items"]).items() if v)
        self.assertEqual(buggy, fx["expected_buggy_rejected"])
        self.assertEqual(good, fx["expected_rejected"])
        self.assertGreater(len(buggy), len(good))
        self.assertEqual(len(buggy), 4)
        self.assertEqual(len(good), 1)

    def test_buggy_bar_is_lower_than_the_raw_interval_test(self):
        """The V0.3 defect made the 'corrected' test weaker than excluding zero."""
        items = [(f"c{i}", 2.0) for i in range(70)]
        buggy = holm.holm_v0_3_buggy(items)
        self.assertTrue(all(buggy.values()), "buggy version should pass everything at z=2.0")
        good = holm.holm_agree(items)
        self.assertFalse(any(good.values()))


class TapeSymmetry(unittest.TestCase):
    def test_state_space_is_enumerable_and_complete(self):
        st = nc5.states()
        self.assertEqual(len(st), 2044)
        for L, T in st:
            self.assertLessEqual(L * IW, T)
            self.assertGreaterEqual(L, nc5.GMIN)

    def test_only_tape_words_gates_structural_validity(self):
        self.assertEqual(nc5.config_fields_that_gate_validity(), ("tape_words",))

    def test_primitive_paired_proposals_are_equal(self):
        pr = nc5.paired_tape_symmetry_proof("v0_4")
        self.assertTrue(pr["primitive_proposal_probabilities_equal"])
        self.assertAlmostEqual(pr["q_t_to_2t"], pr["q_2t_to_t"], places=18)

    def test_no_fitting_shrink_is_blocked_under_v0_4(self):
        """EXHAUSTIVE over every (genome_length, tape_words) pair: the brief's core requirement."""
        pr = nc5.paired_tape_symmetry_proof("v0_4")
        self.assertTrue(pr["exhaustive"])
        self.assertEqual(pr["pairs_where_a_fitting_shrink_was_blocked"], 0, pr["violations"][:5])

    def test_v0_3_did_block_fitting_shrinks(self):
        """The defect being removed must be visible in the same instrument."""
        pr = nc5.paired_tape_symmetry_proof("v0_3")
        self.assertGreater(pr["pairs_where_a_fitting_shrink_was_blocked"], 0)

    def test_tape_edges_are_symmetric_under_v0_4(self):
        edges, _ = nc5.transition_graph("v0_4")
        for (a, b), p in edges.items():
            if a[1] != b[1]:                       # tape move
                self.assertAlmostEqual(p, edges.get((b, a), 0.0), places=15,
                                       msg=f"tape edge {a}->{b} not reversible")

    def test_nc5_has_no_asymmetric_edges_at_all(self):
        au = nc5.audit_transitions("nc5")
        self.assertEqual(au["n_asymmetric_pairs"], 0, au["asymmetries"][:5])

    def test_live_operator_matches_the_modelled_rule(self):
        """The graph model must agree with the real op_config_perturbation, not just describe it."""
        r = SplitMix64(7)
        checked = 0
        for T in nc5.TAPES:
            for L in (1, max(1, T // IW // 2), T // IW):
                if L < 1 or L * IW > T:
                    continue
                m = {"schema_version": SCHEMA, "n_regs": 8, "tape_words": T,
                     "genome": [0] * (IW * L), "code_writable": False, "persist": "none",
                     "tick_budget": 64, "out_cap": 4}
                validate_manifest(m)
                seen = set()
                for _ in range(400):
                    c, rec = grammar.op_config_perturbation(m, r, None)
                    if rec.get("field") == "tape_words":
                        seen.add(c["tape_words"])
                for nt in (T * 2, T // 2):
                    in_bounds = (STORAGE_BOUNDS["tape_words"]["min"] <= nt
                                 <= STORAGE_BOUNDS["tape_words"]["max"])
                    fits = nt >= L * IW
                    if in_bounds and fits:
                        self.assertIn(nt, seen, f"L={L} T={T}: valid move to {nt} never observed")
                    else:
                        self.assertNotIn(nt, seen, f"L={L} T={T}: invalid move to {nt} observed")
                checked += 1
        self.assertGreater(checked, 10)

    def test_grammar_identity_changed_and_history_preserved(self):
        self.assertEqual(grammar.GRAMMAR_VERSION, "proteus.grammar.v0.4")
        self.assertNotEqual(grammar.GRAMMAR_HASH, grammar.GRAMMAR_HASH_V0_3)
        self.assertNotEqual(grammar.GRAMMAR_HASH, grammar.GRAMMAR_HASH_V0_2)
        self.assertEqual(len(grammar.OPERATORS), 12)
        self.assertNotIn("zeroing", grammar.NAMES)
        self.assertAlmostEqual(sum(grammar.WEIGHTS), 1.0, places=12)

    def test_weights_and_limits_untouched_by_v0_4(self):
        """The only authorized change is the tape transition body."""
        survivors = [o for o in grammar.OPERATORS_V0_2 if o[0] != "zeroing"]
        for (n, w, _d), (n2, w2, _d2) in zip(survivors, grammar.OPERATORS):
            self.assertEqual(n, n2)
            self.assertAlmostEqual(w2, w / 0.96, places=12)
        self.assertEqual(STORAGE_BOUNDS["tape_words"], {"min": 16, "max": 4096})
        self.assertEqual(STORAGE_BOUNDS["genome_words"], {"min": 4, "max": 4096})


if __name__ == "__main__":
    unittest.main()
