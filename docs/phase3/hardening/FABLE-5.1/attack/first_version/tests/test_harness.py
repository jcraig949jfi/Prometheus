"""Tests of the reference harness v0. Run from the harness folder:

    python -B -m unittest discover -v

Each test can fail. The first group checks the gates against their registered clean cases and
mutants. The second checks that the meta-gate itself can fail. The third pins numbers.
"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from rso_harness import audits, claims, meta, retain1, rulers, search, stats, torture  # noqa: E402
from rso_harness.verdict import (ALL, BLOCKED, FAIL, INDETERMINATE, PASS, UNQUALIFIED, Result,  # noqa: E402
                                 combine)

ROWS = meta.qualify()


class GatesAreQualified(unittest.TestCase):
    def test_every_gate_passes_its_clean_cases_and_rejects_its_mutants(self):
        for gid, row in ROWS.items():
            self.assertEqual(row["status"], PASS, (gid, row["false_alarms"], row["escapes"], row["wrong_kind"]))

    def test_every_gate_has_a_clean_case_and_a_mutant(self):
        for gid, row in ROWS.items():
            self.assertGreaterEqual(row["clean"], 1, gid)
            self.assertGreaterEqual(row["mutants"], 1, gid)

    def test_counts(self):
        self.assertEqual(len(ROWS), 21)
        self.assertEqual(sum(r["mutants"] for r in ROWS.values()), 62)
        self.assertEqual(sum(r["clean"] for r in ROWS.values()), 34)

    def test_mutants_use_all_four_ways_of_not_passing(self):
        seen = {m["verdict"] for r in ROWS.values() for m in r["mutant_verdicts"]}
        self.assertEqual(seen, {FAIL, BLOCKED, UNQUALIFIED, INDETERMINATE})


class TheMetaGateCanFail(unittest.TestCase):
    def test_a_gate_with_no_mutant_is_unqualified(self):
        rows = meta.qualify({"X": ("guards nothing", [lambda: Result("X", PASS)], [])})
        self.assertEqual(rows["X"]["status"], UNQUALIFIED)

    def test_a_gate_with_no_clean_case_is_unqualified(self):
        rows = meta.qualify({"X": ("accuses everything", [], [("m", lambda: Result("X", FAIL), FAIL)])})
        self.assertEqual(rows["X"]["status"], UNQUALIFIED)

    def test_a_mutant_that_passes_is_an_escape(self):
        rows = meta.qualify({"X": ("blind", [lambda: Result("X", PASS)], [("m", lambda: Result("X", PASS), FAIL)])})
        self.assertEqual(rows["X"]["status"], FAIL)
        self.assertEqual(rows["X"]["escapes"], ["m"])

    def test_a_clean_case_that_fails_is_a_false_accusation(self):
        rows = meta.qualify({"X": ("paranoid", [lambda: Result("X", FAIL, "no")],
                                   [("m", lambda: Result("X", FAIL), FAIL)])})
        self.assertEqual(rows["X"]["status"], FAIL)
        self.assertEqual(rows["X"]["false_alarms"], ["no"])

    def test_a_mutant_rejected_for_the_wrong_reason_is_reported(self):
        rows = meta.qualify({"X": ("confused", [lambda: Result("X", PASS)],
                                   [("m", lambda: Result("X", BLOCKED), FAIL)])})
        self.assertEqual(rows["X"]["status"], FAIL)
        self.assertEqual(len(rows["X"]["wrong_kind"]), 1)

    def test_known_escapes_are_still_escapes(self):
        escapes = meta.known_escapes()
        self.assertEqual([e["gate"] for e in escapes], ["G3.exclusion", "G6.observer"])
        self.assertTrue(all(e["verdict"] == PASS for e in escapes))


class Verdicts(unittest.TestCase):
    def test_five_verdicts_and_no_sixth(self):
        self.assertEqual(len(set(ALL)), 5)
        with self.assertRaises(ValueError):
            Result("g", "MAYBE")

    def test_combine_reports_the_most_informative_reason(self):
        def c(*vs):
            return combine("g", [Result("s%d" % i, v) for i, v in enumerate(vs)]).verdict
        self.assertEqual(c(PASS, PASS), PASS)
        self.assertEqual(c(PASS, INDETERMINATE), INDETERMINATE)
        self.assertEqual(c(INDETERMINATE, UNQUALIFIED), UNQUALIFIED)
        self.assertEqual(c(UNQUALIFIED, BLOCKED), BLOCKED)
        self.assertEqual(c(BLOCKED, FAIL, UNQUALIFIED), FAIL)
        self.assertEqual(combine("g", []).verdict, BLOCKED)

    def test_unqualified_and_blocked_are_not_fail(self):
        self.assertEqual(audits.ruler_status("STRONG_RECURSION").verdict, UNQUALIFIED)
        self.assertEqual(stats.preflight(16, 0.5, 1e-6, 1.0).verdict, BLOCKED)
        self.assertNotIn(FAIL, {audits.ruler_status("STRONG_RECURSION").verdict,
                                stats.preflight(16, 0.5, 1e-6, 1.0).verdict})


class Numbers(unittest.TestCase):
    def test_binomial(self):
        self.assertAlmostEqual(stats.tail_ge(4, 0, 0.3), 1.0)
        self.assertAlmostEqual(stats.tail_ge(4, 4, 0.5), 0.0625)
        self.assertEqual(stats.critical_k(64, 0.5, 1e-6), 51)
        self.assertIsNone(stats.critical_k(16, 0.5, 1e-6))
        self.assertAlmostEqual(stats.zero_hit_upper(24), 1 - 0.05 ** (1 / 24))
        self.assertEqual("%.4f" % stats.zero_hit_upper(24), "0.1173")
        lo, hi = stats.clopper_pearson(12, 24)
        self.assertTrue(lo < 0.5 < hi)
        self.assertEqual([stats.three_way(c, 24, 22, 12) for c in (24, 22, 21, 13, 12, 0)],
                         [PASS, PASS, INDETERMINATE, INDETERMINATE, FAIL, FAIL])

    def test_panel_scores(self):
        for physics, (positive, impostor) in retain1.PANEL.items():
            self.assertEqual(retain1.score(positive, meta.SEEDS), 64, physics)
            self.assertLess(retain1.score(impostor, meta.SEEDS), 51, physics)

    def test_register_swap_is_valid_in_one_physics_only(self):
        t = rulers.measured_scope(rulers.register_swap_ruler, retain1.PANEL, meta.PAIRS)
        self.assertEqual(sorted(p for p, row in t.items() if row["agrees"]), ["REGISTER"])

    def test_exact_reach(self):
        b = meta.BUDGET
        self.assertEqual(search.exact_reach("NEEDLE", "STRICT", b, "COLD"), 0.0)
        self.assertEqual(search.exact_reach("VALLEY", "STRICT", b, "COLD"), 0.0)
        self.assertEqual(search.exact_reach("VALLEY", "NEUTRAL", b, "COLD"), 0.0)
        self.assertGreater(search.exact_reach("VALLEY", "STRICT", b, "REPAIR", 1), 0.99)
        self.assertGreater(search.exact_reach("ASCENT", "NEUTRAL", b, "COLD"), 0.99)
        self.assertEqual("%.4f" % search.exact_reach("NEEDLE", "NEUTRAL", b, "COLD"), "0.7298")
        self.assertEqual("%.4f" % search.exact_reach("VALLEY", "NEUTRAL", b, "REPAIR", 1), "0.1797")

    def test_a_score_only_check_passes_a_broken_observer(self):
        for physics, (positive, _) in retain1.PANEL.items():
            r = torture.observer_equivalence(positive, meta.PAIRS, torture.greedy_observer, compare="score")
            self.assertEqual(r.verdict, PASS, physics)
            r = torture.observer_equivalence(positive, meta.PAIRS, torture.greedy_observer)
            self.assertEqual(r.verdict, FAIL, physics)

    def test_the_trajectory_includes_what_the_world_delivered(self):
        # A stored word never changes its own state when distractors change. The first version of the
        # observer gate compared organism state only and passed a broken observer on this physics.
        quiet = retain1.World().episode(retain1.Register(), 2000)
        noisy = retain1.World().episode(retain1.Register(), 2000, observer=torture.greedy_observer([]))
        self.assertEqual([step[4] for step in quiet["trace"]], [step[4] for step in noisy["trace"]])
        self.assertNotEqual(quiet["trace"], noisy["trace"])


class AuditsOfTheReviewersOwnRuns(unittest.TestCase):
    """The harness, pointed at runs 2 and 3 of the review, returns what three reviewers found by hand."""

    def setUp(self):
        self.r2, self.r3 = meta.run2(), meta.run3()

    def test_run2_four_clauses_cannot_fail(self):
        r = audits.audit_clauses(self.r2, audits.clauses_run2)
        self.assertEqual(r.verdict, UNQUALIFIED)
        self.assertEqual(r.detail["cannot_fail"], [
            "NESTING.rescue_restores", "PROVENANCE.random_store_no_help", "U_TRANSFER.frozen_U_good_on_C",
            "U_TRANSFER.frozen_U_good_on_narrower_C"])
        self.assertEqual(r.detail["cannot_hold"], [])

    def test_run3_six_clauses_cannot_fail(self):
        r = audits.audit_clauses(self.r3, audits.clauses_run3)
        self.assertEqual(r.detail["cannot_fail"], [
            "NESTING.lesion_hurts", "NESTING.rescue_restores", "NESTING.sham_harmless",
            "PROVENANCE.random_store_no_help", "U_TRANSFER.frozen_U_good_on_C",
            "U_TRANSFER.frozen_U_good_on_narrower_C"])

    def test_run3_eight_arms_are_three_computations(self):
        r = audits.audit_arms(self.r3["STRATEGIST"]["replicates"], meta.ARMS3)
        self.assertEqual(r.verdict, FAIL)
        self.assertEqual(r.detail, [["naive_B", "lesion_B", "irrelevant_history_B"],
                                    ["dev_B", "sham_B", "rescue_B", "v_donor_B"], ["random_V_B"]])

    def test_run2_arms_are_separate(self):
        r = audits.audit_arms(self.r2["BUILDER"]["replicates"], meta.ARMS2)
        self.assertEqual(r.verdict, PASS)
        self.assertEqual(len(r.detail), 8)

    def test_run2_sham_is_not_neutral(self):
        t2 = audits.clause_table(self.r2, audits.clauses_run2)
        r = audits.audit_sham(self.r2["BUILDER"]["replicates"], t2["NESTING.sham_harmless"])
        self.assertEqual(r.verdict, FAIL)
        self.assertEqual((r.detail["within_margin"], r.detail["sham_faster"]), (8, 24))

    def test_run3_sham_cannot_fail(self):
        t3 = audits.clause_table(self.r3, audits.clauses_run3)
        r = audits.audit_sham(self.r3["STRATEGIST"]["replicates"], t3["NESTING.sham_harmless"])
        self.assertEqual(r.verdict, UNQUALIFIED)

    def test_runs_2_and_3_could_not_have_started(self):
        for setting in (audits.RUN2, audits.RUN3):
            r = audits.audit_setting(setting)
            self.assertEqual(r.verdict, BLOCKED)
            self.assertIn("power", r.reason)

    def test_run3_changed_five_things_besides_the_one_it_was_named_for(self):
        r = audits.audit_contrast("parts_shared", audits.RUN2, audits.RUN3)
        self.assertEqual(r.verdict, FAIL)
        self.assertEqual(r.detail, ["content_reset", "effect_threshold", "family_A", "parts_shared", "sham",
                                    "wrong_history"])


class Claims(unittest.TestCase):
    def test_a_claim_goes_down_when_a_facet_is_withdrawn(self):
        c = meta.claim()
        self.assertEqual(claims.level(c), 2)
        c["facets"]["custody"] = FAIL
        self.assertEqual(claims.level(c), 1)
        c["facets"]["detection"] = UNQUALIFIED
        self.assertEqual(claims.level(c), 0)

    def test_a_structure_claim_without_an_exact_bound_stops_at_l1(self):
        c = meta.claim(kind="TRANSFER", exact_null=UNQUALIFIED)
        self.assertEqual(claims.level(c), 1)

    def test_a_quoted_claim_carries_its_conditions(self):
        text = claims.render(meta.claim()).reason
        for part in ("EFFECT", "L2", "gap = 6", "alpha = 1e-6", "episodes = 64"):
            self.assertIn(part, text)

    def test_strong_recursion_has_no_ruler(self):
        r = audits.ruler_status("STRONG_RECURSION", receipts=meta.COUNTERFEIT)
        self.assertEqual(r.verdict, UNQUALIFIED)
        self.assertEqual(audits.ruler_status("ORDER3_BITS", receipts=meta.COUNTERFEIT).verdict, PASS)


if __name__ == "__main__":
    unittest.main()
