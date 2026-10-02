"""Tests of the reference harness v0. Run from the harness folder:

    python -B -m unittest discover -v

The first group checks the gates against their registered clean cases and mutants. The second
checks that the meta-gate itself can fail and that every known escape is still an escape. The rest
pin thresholds and numbers, so that a change to a gate's logic does not pass unnoticed: the first
version of this suite let 22 of 25 such changes through.
"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from rso_harness import (audits, claims, ladder, meta, registration, retain1, rulers, search, stats,  # noqa: E402
                         torture)
from rso_harness.verdict import (ALL, BLOCKED, FAIL, INDETERMINATE, PASS, UNQUALIFIED, Result,  # noqa: E402
                                 combine)

ROWS = meta.qualify()
ESCAPES = meta.known_escapes()
R = retain1


class GatesAreQualified(unittest.TestCase):
    def test_every_gate_passes_its_clean_cases_and_rejects_its_mutants(self):
        for gid, row in ROWS.items():
            self.assertEqual(row["status"], PASS, (gid, row["false_alarms"], row["escapes"], row["wrong_kind"]))

    def test_every_gate_has_a_clean_case_and_a_mutant(self):
        self.assertEqual(len(ROWS), 21)
        for gid, row in ROWS.items():
            self.assertGreaterEqual(row["clean"], 1, gid)
            self.assertGreaterEqual(row["mutants"], 1, gid)

    def test_mutants_use_all_four_ways_of_not_passing(self):
        seen = {m["verdict"] for r in ROWS.values() for m in r["mutant_verdicts"]}
        self.assertEqual(seen, {FAIL, BLOCKED, UNQUALIFIED, INDETERMINATE})

    def test_indeterminate_is_returned_by_gates_and_not_only_carried_by_claims(self):
        gates = {gid for gid, r in ROWS.items() for m in r["mutant_verdicts"] if m["verdict"] == INDETERMINATE}
        self.assertEqual(gates, {"G1.receipt", "G3.exclusion", "G4.entry", "G8.demand", "G9.clauses", "G12.promote"})


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
        self.assertEqual([e["gate"] for e in ESCAPES], [
            "G3.exclusion", "G4.entry", "G5.neutrality", "G6.observer", "G6.reset", "G7.calibration", "G8.demand",
            "G9.sham", "G10.setting", "G11.custody", "G12.promote"])
        for e in ESCAPES:
            self.assertEqual(e["verdict"], PASS, e["fault"])

    def test_the_escapes_are_real_faults(self):
        by = {e["gate"]: e for e in ESCAPES}
        self.assertEqual(by["G8.demand"]["shown"], {"a_policy_that_reads_that_bit_scores": 64, "of": 64})
        shown = by["G7.calibration"]["shown"]
        self.assertLess(shown["exact_at_95_percent"], shown["exact_at_budget"] - 0.015)
        self.assertEqual(R.score(R.SleeperRegister, range(3)), 3)        # right while fresh
        w, org = R.World(), R.SleeperRegister()
        answers = [w.episode(org, s, force_bit=1)["answer"] for s in (1, 2, 3)]
        self.assertEqual(answers, [1, 1, 0])                              # the carry bites two episodes later


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


class Thresholds(unittest.TestCase):
    def test_binomial(self):
        self.assertAlmostEqual(stats.tail_ge(4, 0, 0.3), 1.0)
        self.assertAlmostEqual(stats.tail_ge(4, 4, 0.5), 0.0625)
        self.assertAlmostEqual(stats.tail_le(4, 0, 0.5), 0.0625)
        self.assertAlmostEqual(sum(stats.pmf(2048, 0.4)), 1.0)
        self.assertEqual(stats.critical_k(64, 0.5, 1e-6), 51)
        self.assertEqual(stats.critical_k(20, 0.5, 1e-6), 20)
        self.assertIsNone(stats.critical_k(16, 0.5, 1e-6))
        self.assertEqual(stats.lower_critical(64, 0.5, 1e-6), 13)
        self.assertEqual(stats.lower_critical(64, rulers.P_WEAKEST, 1e-6), 47)
        self.assertEqual("%.4f" % stats.zero_hit_upper(24), "0.1173")
        self.assertEqual("%.4f" % stats.zero_hit_upper(128), "0.0231")
        self.assertAlmostEqual(stats.lower_bound(20, 20), 0.01 ** (1 / 20), places=6)

    def test_a_score_has_five_places_to_stand(self):
        def at(k, **kw):
            return stats.classify(k, 64, 0.5, 1e-6, rulers.P_WEAKEST, **kw)
        self.assertEqual([at(k) for k in (64, 51, 50, 48, 47, 14, 13, 0)], [
            "EXCLUDES", "EXCLUDES", "UNDECIDED", "UNDECIDED", "AT_BOUND", "AT_BOUND", "INVERTED", "INVERTED"])
        self.assertEqual(at(13, exact_rate=False), "AT_BOUND")
        self.assertEqual(stats.classify(16, 16, 0.5, 1e-6, 1.0), "UNDERPOWERED")

    def test_preflight_floors(self):
        weak = stats.preflight(64, 0.5, 1e-6, 0.85)
        self.assertEqual(weak.verdict, BLOCKED)
        self.assertTrue(0.90 < weak.detail["power"] < 0.92)
        self.assertEqual(stats.preflight(64, 0.5, 0.05, 1.0).verdict, BLOCKED)
        self.assertEqual(stats.preflight(64, 0.5, 0.009, 1.0).verdict, PASS)
        self.assertEqual(stats.preflight(64, 0.5, 1e-6, rulers.P_WEAKEST).verdict, PASS)
        self.assertEqual(stats.preflight_from_design(64, 0.5, 1e-6, 256, 256).verdict, PASS)
        self.assertEqual(stats.preflight_from_design(64, 0.5, 1e-6, 20, 20).verdict, BLOCKED)

    def test_attainability_is_computed_from_the_table(self):
        p = stats.outcome_probability(meta.table(), 0.97)["HOLDS"]
        self.assertTrue(0.96 < p < 0.97)
        self.assertEqual(registration.attainability(meta.table(), {"HOLDS": 0.97, "FAILS": 0.2}).verdict, BLOCKED)
        self.assertEqual(registration.attainability(meta.table(), {"HOLDS": 0.999, "FAILS": 0.2}).verdict, PASS)

    def test_equivalence_is_not_absence_of_a_difference(self):
        def eq(k, n=2048):
            return stats.equivalence(k, n, 0.5, torture.MARGIN, 1e-6)
        self.assertEqual([eq(k) for k in (912, 913, 928, 929, 1024, 1119, 1120, 1135, 1136)], [
            "OUTSIDE", "UNDECIDED", "UNDECIDED", "WITHIN", "WITHIN", "WITHIN", "UNDECIDED", "UNDECIDED", "OUTSIDE"])
        self.assertNotIn("WITHIN", {eq(k, 64) for k in range(65)})

    def test_calibration_has_a_stated_resolution(self):
        exact = search.exact_reach("NEEDLE", "NEUTRAL", meta.BUDGET, "COLD")
        ok = [k for k in range(257) if stats.consistent(k, 256, exact, search.CAL_ALPHA)]
        self.assertEqual((ok[0], ok[-1]), (164, 208))

    def test_panel_scores_and_the_bracket_of_the_bound(self):
        got = {p: (R.score(pos, meta.SEEDS), R.score(imp, meta.SEEDS)) for p, (pos, imp) in R.PANEL.items()}
        self.assertEqual(got, {"REGISTER": (64, 26), "ATTRACTOR": (64, 31), "PACKET": (64, 26), "LATTICE": (64, 26)})
        self.assertEqual(R.score(R.FadingRegister, meta.SEEDS), 61)
        self.assertEqual(R.score(R.Inverter, meta.SEEDS), 0)
        b = meta.bracket()
        self.assertEqual((b["lowest"], b["highest"], b["impostor_scores"]), (0.35, 0.68, [25, 41]))

    def test_register_swap_is_valid_in_one_physics_only(self):
        t = rulers.known_answers(rulers.register_swap_ruler, R.PANEL, meta.PAIRS)
        self.assertEqual(sorted(p for p, row in t.items() if row["agrees"]), ["REGISTER"])

    def test_interchange_tells_an_inverter_from_an_impostor(self):
        self.assertEqual(rulers.interchange_ruler(R.Inverter, meta.PAIRS), "INVERTED")
        self.assertEqual(rulers.interchange_ruler(R.RegisterImpostor, meta.PAIRS), "NEGATIVE")
        self.assertEqual(rulers.interchange_ruler(R.Register, meta.PAIRS), "POSITIVE")
        self.assertEqual(rulers.register_swap_ruler(R.PacketRing, meta.PAIRS), "NEGATIVE")

    def test_exact_reach(self):
        b = meta.BUDGET
        self.assertEqual(search.exact_reach("NEEDLE", "STRICT", b, "COLD"), 0.0)
        self.assertEqual(search.exact_reach("VALLEY", "STRICT", b, "COLD"), 0.0)
        self.assertEqual(search.exact_reach("VALLEY", "NEUTRAL", b, "COLD"), 0.0)
        self.assertGreater(search.exact_reach("VALLEY", "STRICT", b, "REPAIR", 1), 0.99)
        self.assertGreater(search.exact_reach("ASCENT", "NEUTRAL", b, "COLD"), 0.99)
        self.assertLess(search.exact_reach("ASCENT", "NEUTRAL", 5, "COLD"), 0.99)
        self.assertEqual("%.4f" % search.exact_reach("NEEDLE", "NEUTRAL", b, "COLD"), "0.7298")
        self.assertEqual("%.4f" % search.exact_reach("NEEDLE", "NEUTRAL", b, "REPAIR", 1), "0.7757")
        self.assertEqual("%.4f" % search.exact_reach("VALLEY", "NEUTRAL", b, "REPAIR", 1), "0.1797")


class Torture(unittest.TestCase):
    def test_a_score_only_check_passes_a_broken_observer(self):
        for physics, (positive, _) in R.PANEL.items():
            r = torture.observer_equivalence(positive, meta.PAIRS, torture.greedy_observer, compare="score")
            self.assertEqual(r.verdict, PASS, physics)
            r = torture.observer_equivalence(positive, meta.PAIRS, torture.greedy_observer)
            self.assertEqual(r.verdict, FAIL, physics)

    def test_the_trajectory_includes_what_the_world_delivered(self):
        # A stored word never changes its own state when distractors change. The first version of the
        # observer gate compared organism state only and passed a broken observer on this physics.
        quiet = R.World().episode(R.Register(), 2000)
        noisy = R.World().episode(R.Register(), 2000, observer=torture.greedy_observer([]))
        self.assertEqual([step[4] for step in quiet["trace"]], [step[4] for step in noisy["trace"]])
        self.assertNotEqual(quiet["trace"], noisy["trace"])

    def test_a_disturbance_after_the_last_step_shows_only_in_the_final_state(self):
        quiet = R.World().episode(R.Register(), 2000)
        late = R.World().episode(R.Register(), 2000, observer=torture.late_observer([]))
        self.assertEqual(quiet["trace"], late["trace"])
        self.assertNotEqual(quiet["final"], late["final"])

    def test_restart_is_judged_on_the_trajectory_and_not_on_the_answer(self):
        make = R.LatticeLateBadCapture
        for seed in meta.PAIRS:
            whole = R.World().episode(make(), seed)

            def restart(org):
                used = make()
                R.World().episode(used, seed, force_bit=1 - whole["bit"])
                used.restore(org.capture())
                return used

            for at in range(7):
                self.assertEqual(R.World().episode(make(), seed, interrupt={at: restart})["answer"], whole["answer"])
        self.assertEqual(torture.restart_equivalence(make, meta.PAIRS).verdict, FAIL)

    def test_reset_is_judged_on_the_trajectory_and_not_on_the_answer(self):
        make = R.LatticeKeepsClock
        for seed in meta.PAIRS:
            fresh = R.World().episode(make(), seed + 1)["answer"]
            w, org = R.World(), make()
            w.episode(org, seed, force_bit=1)
            self.assertEqual(w.episode(org, seed + 1)["answer"], fresh)
        self.assertEqual(torture.reset_closure(make, meta.PAIRS).verdict, FAIL)

    def test_the_world_clears_its_mark_between_episodes(self):
        self.assertEqual(torture.reset_closure(R.WorldParker, meta.PAIRS, writable_mark=True).verdict, PASS)
        self.assertEqual(torture.reset_closure(R.WorldParker, meta.PAIRS, writable_mark=True, keep_mark=True).verdict,
                         FAIL)

    def test_demand_closure_needs_enough_episodes_to_say_yes(self):
        clean = torture.demand_closure(meta.DEMAND, meta.TRAIN)
        self.assertEqual(clean.verdict, PASS)
        self.assertEqual(sorted(clean.detail), ["CLOCK", "CONSTANT", "KEY_READER", "LAST_DISTRACTOR", "TABLE",
                                                "WORLD_PARKER"])
        self.assertEqual(torture.demand_closure(meta.SEEDS, meta.TRAIN).verdict, INDETERMINATE)
        half = torture.demand_closure(meta.DEMAND, meta.TRAIN, leak_key="inverted")
        self.assertEqual((half.verdict, half.detail["KEY_READER"]), (FAIL, 0))


class Reports(unittest.TestCase):
    def test_a_report_is_replayed_and_not_believed(self):
        honest = meta.report()
        self.assertEqual(search.check_report(honest).verdict, PASS)
        lying = meta.recount(honest, NEUTRAL={"seeds": list(meta.REPORTED), "hits": honest["policies"]["NEUTRAL"]["hits"] + 1})
        self.assertEqual(search.check_report(lying).verdict, FAIL)

    def test_a_bound_may_be_rounded_or_more_cautious_and_never_smaller(self):
        exact = stats.zero_hit_upper(len(meta.REPORTED))
        for bound, want in ((round(exact, 4), PASS), (stats.zero_hit_upper(len(meta.REPORTED), 0.99), PASS),
                            (exact - 0.001, FAIL), (1.5, FAIL)):
            self.assertEqual(search.check_report(meta.null(upper_bound=bound)).verdict, want, bound)

    def test_a_null_needs_a_policy_that_can_cross_a_neutral_step(self):
        self.assertEqual(search.check_report(meta.null("NEEDLE", ("STRICT", "ELITIST"))).verdict, BLOCKED)
        self.assertEqual(search.check_report(meta.null("VALLEY", ("STRICT", "NEUTRAL"))).verdict, PASS)


class AuditsOfTheReviewersOwnRuns(unittest.TestCase):
    """The harness, pointed at runs 1 to 3 of the review, returns faults its reviewers found by hand."""

    def setUp(self):
        self.r2, self.r3 = meta.run2(), meta.run3()

    def test_run2_clauses(self):
        r = audits.audit_clauses(self.r2, audits.clauses_run2)
        self.assertEqual(r.verdict, UNQUALIFIED)
        self.assertEqual(r.detail["cannot_fail"], [
            "NESTING.rescue_restores", "PROVENANCE.random_store_no_help", "U_TRANSFER.frozen_U_good_on_C",
            "U_TRANSFER.frozen_U_good_on_narrower_C"])
        self.assertEqual(r.detail["cannot_hold"], [])
        self.assertEqual((len(r.detail["table"]), len(r.detail["not_isolated"])), (13, 7))

    def test_run3_clauses(self):
        r = audits.audit_clauses(self.r3, audits.clauses_run3)
        self.assertEqual(r.detail["cannot_fail"], [
            "NESTING.lesion_hurts", "NESTING.rescue_restores", "NESTING.sham_harmless",
            "PROVENANCE.random_store_no_help", "U_TRANSFER.frozen_U_good_on_C",
            "U_TRANSFER.frozen_U_good_on_narrower_C"])
        self.assertEqual(len(r.detail["not_isolated"]), 6)

    def test_run3_eight_arms_give_three_series(self):
        r = audits.audit_arms(self.r3["STRATEGIST"]["replicates"], meta.ARMS3)
        self.assertEqual(r.verdict, FAIL)
        self.assertEqual(r.detail, [["naive_B", "lesion_B", "irrelevant_history_B"],
                                    ["dev_B", "sham_B", "rescue_B", "v_donor_B"], ["random_V_B"]])
        self.assertEqual(audits.audit_arms(meta.nudged(self.r3["STRATEGIST"]["replicates"]), meta.ARMS3).detail, r.detail)

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

    def test_the_sham_margin_is_a_quarter(self):
        row = {"GOOD": 24, "BAD": 0}
        for sham, want in ((12, PASS), (13, FAIL), (8, PASS), (7, FAIL)):
            reps = [{"dev_B": 10, "sham_B": sham} for _ in range(24)]
            self.assertEqual(audits.audit_sham(reps, row).verdict, want, sham)

    def test_two_of_nine_choices_were_never_registered_in_runs_2_and_3(self):
        for setting in (audits.RUN2, audits.RUN3):
            r = audits.audit_setting(setting)
            self.assertEqual(r.verdict, BLOCKED)
            self.assertEqual(r.reason, "power not registered; amortization_horizon not registered")

    def test_run3_differs_from_run2_in_six_of_the_ten_fields_written_down(self):
        r = audits.audit_contrast("parts_shared", audits.RUN2, audits.RUN3)
        self.assertEqual(r.verdict, FAIL)
        self.assertEqual(r.detail, ["content_reset", "effect_threshold", "family_A", "parts_shared", "sham",
                                    "wrong_history"])
        self.assertEqual(len(set(audits.RUN2) | set(audits.RUN3)), 10)

    def test_what_each_ruler_returned_on_the_kit(self):
        got = {(m, s): audits.returned(meta.COUNTERFEIT, src) for m, s, src, _ in audits.RUNS}
        self.assertEqual(got[("PROCEDURE_SELECTOR", "V01@RUN1")], "POSITIVE")
        self.assertEqual(got[("LIBRARY_FIXED_BUILDER", "S19@RUN2")], "POSITIVE")
        self.assertEqual(got[("LIBRARY_FIXED_BUILDER", "S19@RUN3")], "NEGATIVE")
        self.assertEqual(got[("SEARCH_ORDER_SELECTOR", "S19@RUN3")], "POSITIVE")
        self.assertEqual(got[("KEY_ACQUIRER", "BITS@KEYS")], "POSITIVE")
        self.assertEqual(sum(1 for v in got.values() if v == "NEGATIVE"), 8)

    def test_no_ruler_tried_for_the_strong_claim_answered_the_kit(self):
        want = {("STRONG", "V01@RUN1"): FAIL, ("STRONG", "S19@RUN2"): FAIL, ("STRONG", "S19@RUN3"): FAIL,
                ("REUSE", "V01@RUN1"): FAIL, ("REUSE", "S19@RUN2"): UNQUALIFIED, ("REUSE", "S19@RUN3"): FAIL,
                ("BITS", "BITS@KEYS"): PASS, ("BITS_TWO_LEVELS", "BITS@TWO"): UNQUALIFIED,
                ("COMPOSITION", "BITS@PAIRS"): UNQUALIFIED}
        for (claim, setting), verdict in want.items():
            self.assertEqual(audits.ruler_status(claim, setting, meta.COUNTERFEIT).verdict, verdict, (claim, setting))


class Claims(unittest.TestCase):
    def test_a_claim_goes_down_when_a_facet_is_withdrawn(self):
        c = meta.claim()
        self.assertEqual(claims.level(c), 2)
        c["facets"]["custody"]["verdict"] = FAIL
        self.assertEqual(claims.level(c), 1)
        c["facets"]["detection"]["verdict"] = UNQUALIFIED
        self.assertEqual(claims.level(c), 0)

    def test_a_structure_claim_without_an_exact_bound_stops_at_l1(self):
        self.assertEqual(claims.level(meta.claim("TRANSFER", exact_null=UNQUALIFIED)), 1)

    def test_a_quoted_claim_carries_its_setting_and_says_why_it_stands_no_higher(self):
        text = claims.render(meta.claim()).reason
        for part in ("EFFECT", "L2", "L3 withheld: reproduced: BLOCKED (absent)", "gap = 6", "alpha = 1e-6",
                     "episodes = 64"):
            self.assertIn(part, text)
        low = claims.render(meta.claim(demand=FAIL)).reason
        self.assertIn("L0 (L1 withheld: demand: FAIL)", low)

    def test_a_nested_claim_needs_more_than_a_retention_certificate(self):
        self.assertEqual(claims.KIND["NESTED"], ("retention_at_boundary", "mediation", "cargo_control", "flattened_twin"))
        for facet in claims.KIND["NESTED"]:
            self.assertEqual(claims.promote(meta.claim("NESTED", drop=facet), 1).verdict, BLOCKED, facet)

    def test_every_level_needs_its_own_facets(self):
        for facet in claims.L1:
            self.assertEqual(claims.promote(meta.claim(drop=facet), 1).verdict, BLOCKED, facet)
        for facet in claims.L2:
            self.assertEqual(claims.promote(meta.claim(drop=facet), 2).verdict, BLOCKED, facet)
            self.assertEqual(claims.promote(meta.claim(drop=facet), 1).verdict, PASS, facet)

    def test_custody_checks_every_field(self):
        self.assertEqual(claims.check_custody(meta.custody()).verdict, PASS)
        self.assertEqual(claims.check_custody(meta.custody(rule_fixed_at=20)).verdict, FAIL)
        self.assertEqual(claims.check_custody(meta.custody(rule_fixed_at=19)).verdict, PASS)
        self.assertEqual(claims.check_custody(meta.custody(tuning_evaluations=50)).verdict, PASS)
        self.assertEqual(claims.check_custody(meta.custody(tuning_evaluations=51)).verdict, FAIL)


class Registration(unittest.TestCase):
    def test_every_required_field_is_required(self):
        self.assertEqual(len(meta.CELL_FIELDS), 16)
        self.assertEqual(sorted(meta.CELL_FIELDS), sorted(registration.REQUIRED + ("design_seeds",)))
        for field in meta.CELL_FIELDS:
            self.assertEqual(registration.check_cell(meta.cell(**{field: None})).verdict, BLOCKED, field)
        self.assertEqual(sorted(meta.CUSTODY_FIELDS), sorted(claims.CUSTODY_FIELDS))
        self.assertEqual(sorted(meta.BASELINES_REQUIRED), sorted(torture.REQUIRED_BASELINES))

    def test_a_receipt_is_ordered_against_its_registration(self):
        def at(t):
            return registration.check_receipt(meta.cell(), meta.run_receipt(ran_at=t), meta.SOURCE).verdict
        self.assertEqual([at(99), at(100), at(101)], [FAIL, INDETERMINATE, PASS])


class Ladder(unittest.TestCase):
    """Exploratory. What a certificate at a boundary of the two-level key world certifies."""

    @classmethod
    def setUpClass(cls):
        cls.s = ladder.survey(60)
        cls.pairs = ladder.survey_pairs(60)

    def test_the_exact_bound(self):
        self.assertEqual("%.4f" % ladder.H16, "3.3807")

    def test_an_organism_that_carries_nothing_is_not_certified(self):
        for variant in ("ROTATION", "OFFSET"):
            row = self.s["%s/ELIM" % variant]
            self.assertEqual((row["across_families"]["answer"], row["across_epochs"]["answer"]),
                             ("NOT_SHOWN", "NOT_SHOWN"))

    def test_a_cache_with_a_fixed_re_indexer_is_certified_at_both_boundaries(self):
        row = self.s["ROTATION/CACHE"]
        self.assertEqual((row["across_families"]["answer"], row["across_epochs"]["answer"]), ("CARRIED", "CARRIED"))
        self.assertGreater(row["across_epochs"]["mean"], 13.0)

    def test_the_second_boundary_adds_nothing_when_its_object_composes_with_the_first(self):
        self.assertEqual(self.s["OFFSET/KEEPER"]["across_epochs"]["answer"], "CARRIED")
        self.assertEqual(self.s["ROTATION/KEEPER"]["across_epochs"]["answer"], "NOT_SHOWN")

    def test_an_organism_told_to_forget_is_not_certified_across_epochs(self):
        row = self.s["ROTATION/FORGETFUL"]
        self.assertEqual((row["across_families"]["answer"], row["across_epochs"]["answer"]), ("CARRIED", "NOT_SHOWN"))

    def test_on_an_unseen_pair_only_the_composer_beats_the_bound(self):
        got = {k: (v["after_eight_pairs"]["answer"], v["after_the_control_history"]["answer"])
               for k, v in self.pairs.items()}
        self.assertEqual(got, {"COMPOSER": ("CARRIED", "NOT_SHOWN"), "ELIM": ("NOT_SHOWN", "NOT_SHOWN"),
                               "TABLE_CACHE": ("NOT_SHOWN", "NOT_SHOWN")})
        self.assertEqual(self.pairs["COMPOSER"]["after_eight_pairs"]["mean"], 16.0)

    def test_the_composition_is_of_three_seen_tables(self):
        self.assertEqual((len(ladder.SHOWN), len(ladder.CONTROL)), (8, 6))
        self.assertNotIn(ladder.UNSEEN, ladder.SHOWN)
        self.assertTrue(all(k != 2 for _, k in ladder.CONTROL))


if __name__ == "__main__":
    unittest.main()
