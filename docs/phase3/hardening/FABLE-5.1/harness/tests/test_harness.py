"""Tests of the reference harness v0. Run from the harness folder:

    python -B -m unittest discover -v

The first group checks the gates against their registered sound cases and mutants. The second
checks that the meta-gate itself can fail and that every known escape is still an escape. The rest
put a scripted input on each side of every registered threshold, so that a change to a gate's logic
does not pass unnoticed.

What this suite is worth. Readers wrote one-line changes to the gates' logic without seeing how the
tests would answer. The suite of the day let 22 of 25 through, then 34 of 44, 20 of 32 and 26 of
36, and on the third version 12 of 26 and 20 of 54. Tests for those changes were added after each
round, so a score on them now says only that those holes are closed. mutation_probe.py records
both figures.
"""
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from rso_harness import (audits, claims, ladder, meta, registration, retain1, rulers, search, stats,  # noqa: E402
                         torture)
from rso_harness.verdict import (ALL, BLOCKED, FAIL, INDETERMINATE, PASS, UNQUALIFIED, Result,  # noqa: E402
                                 combine)

ROWS = meta.qualify()
ESCAPES = meta.known_escapes()
R = retain1
SEEDS, PAIRS, DEMAND, TRAIN = meta.SEEDS, meta.PAIRS, meta.DEMAND, meta.TRAIN


class GatesAreQualified(unittest.TestCase):
    def test_every_gate_passes_its_sound_cases_and_rejects_its_mutants(self):
        for gid, row in ROWS.items():
            self.assertEqual(row["status"], PASS, (gid, row["false_alarms"], row["escapes"], row["wrong_kind"]))

    def test_the_registry_holds_21_gates_50_sound_cases_and_258_mutants(self):
        self.assertEqual(len(ROWS), 21)
        self.assertEqual(sum(r["clean"] for r in ROWS.values()), 50)
        self.assertEqual(sum(r["mutants"] for r in ROWS.values()), 258)
        for gid, row in ROWS.items():
            self.assertGreaterEqual(row["clean"], 1, gid)
            self.assertGreaterEqual(row["mutants"], 3, gid)

    def test_mutants_use_all_four_ways_of_not_passing(self):
        seen = {m["verdict"] for r in ROWS.values() for m in r["mutant_verdicts"]}
        self.assertEqual(seen, {FAIL, BLOCKED, UNQUALIFIED, INDETERMINATE})

    def test_indeterminate_is_computed_by_six_gates_and_carried_by_one(self):
        gates = {gid for gid, r in ROWS.items() for m in r["mutant_verdicts"] if m["verdict"] == INDETERMINATE}
        self.assertEqual(gates - {"G12.promote"}, {"G1.receipt", "G3.exclusion", "G4.entry", "G5.neutrality", "G8.demand",
                                                  "G9.clauses"})
        self.assertIn("G12.promote", gates)       # it passes on a facet's verdict; it computes none

    def test_the_lists_the_mutants_use_are_the_lists_the_gates_use(self):
        self.assertEqual(len(meta.CELL_FIELDS), 16)
        self.assertEqual(sorted(meta.CELL_FIELDS), sorted(registration.REQUIRED + ("design_seeds",)))
        self.assertEqual(len(meta.CUSTODY_FIELDS), 10)
        self.assertEqual(meta.CUSTODY_FIELDS, claims.CUSTODY_FIELDS)
        self.assertEqual(meta.BASELINES_REQUIRED, torture.REQUIRED_BASELINES)
        self.assertEqual((meta.FACETS[1], meta.FACETS[2], meta.FACETS[3], meta.FACETS[4]),
                         (claims.L1, claims.L2, claims.L3, claims.L4))
        self.assertEqual(meta.KIND_FACETS, claims.KIND)
        self.assertEqual(len(claims.KIND), 7)


class TheMetaGateCanFail(unittest.TestCase):
    def test_a_gate_with_no_mutant_is_unqualified(self):
        rows = meta.qualify({"X": ("guards nothing", [lambda: Result("X", PASS)], [])})
        self.assertEqual(rows["X"]["status"], UNQUALIFIED)

    def test_a_gate_with_no_sound_case_is_unqualified(self):
        rows = meta.qualify({"X": ("accuses everything", [], [("m", lambda: Result("X", FAIL), FAIL)])})
        self.assertEqual(rows["X"]["status"], UNQUALIFIED)

    def test_a_mutant_that_passes_is_an_escape(self):
        rows = meta.qualify({"X": ("blind", [lambda: Result("X", PASS)], [("m", lambda: Result("X", PASS), FAIL)])})
        self.assertEqual(rows["X"]["status"], FAIL)
        self.assertEqual(rows["X"]["escapes"], ["m"])

    def test_a_sound_case_that_fails_is_a_false_accusation(self):
        rows = meta.qualify({"X": ("paranoid", [lambda: Result("X", FAIL, "no")],
                                   [("m", lambda: Result("X", FAIL), FAIL)])})
        self.assertEqual(rows["X"]["status"], FAIL)
        self.assertEqual(rows["X"]["false_alarms"], ["no"])

    def test_a_mutant_rejected_for_the_wrong_reason_is_reported(self):
        rows = meta.qualify({"X": ("confused", [lambda: Result("X", PASS)],
                                   [("m", lambda: Result("X", BLOCKED), FAIL)])})
        self.assertEqual(rows["X"]["status"], FAIL)
        self.assertEqual(len(rows["X"]["wrong_kind"]), 1)

    def test_a_sound_case_refused_in_any_way_is_a_false_accusation(self):
        for verdict in (BLOCKED, UNQUALIFIED, INDETERMINATE):
            rows = meta.qualify({"X": ("refuses", [lambda: Result("X", verdict, "refused")],
                                       [("m", lambda: Result("X", FAIL), FAIL)])})
            self.assertEqual((rows["X"]["status"], rows["X"]["false_alarms"]), (FAIL, ["refused"]), verdict)

    def test_the_helpers_that_stand_for_many_mutants_try_every_one(self):
        fields = tuple("f%d" % i for i in range(10))

        def forgets_the_last(record):
            return Result("x", BLOCKED if any(record[f] is None for f in fields[:9]) else PASS)

        def make(**change):
            return dict({f: 1 for f in fields}, **change)

        self.assertEqual(meta.every_missing_field_blocks(forgets_the_last, make, fields).verdict, PASS)
        self.assertEqual(meta.every_missing_field_blocks(forgets_the_last, make, fields[:9]).verdict, BLOCKED)
        kept = claims.KIND["TRANSFER"]
        try:
            claims.KIND["TRANSFER"] = ()                    # a gate that forgot what a TRANSFER claim needs
            self.assertEqual(meta.every_kind_facet_blocks().verdict, PASS)
        finally:
            claims.KIND["TRANSFER"] = kept
        self.assertEqual(meta.every_kind_facet_blocks().verdict, BLOCKED)
        kept = meta.EMPTY.pop("known_answers")
        try:
            meta.EMPTY["design_seeds"] = []
            self.assertEqual(meta.every_empty_container_blocks().verdict, BLOCKED)
        finally:
            meta.EMPTY.pop("design_seeds")
            meta.EMPTY["known_answers"] = kept


class KnownEscapes(unittest.TestCase):
    def test_known_escapes_are_still_escapes(self):
        self.assertEqual([e["gate"] for e in ESCAPES], [
            "G1.cell", "G1.receipt", "G2.preflight", "G3.exclusion", "G4.entry", "G4.entry", "G4.entry",
            "G5.neutrality", "G6.observer", "G6.observer", "G6.reset", "G6.reset", "G6.restart", "G7.calibration",
            "G7.calibration", "G7.report", "G8.demand", "G8.demand", "G9.arms", "G9.arms", "G9.clauses", "G9.sham",
            "G10.setting", "G10.contrast", "G10.ruler", "G10.ruler", "G11.custody", "G12.promote", "G12.render"])
        for e in ESCAPES:
            self.assertEqual(e["verdict"], PASS, e["fault"])

    def test_every_gate_has_a_known_escape(self):
        self.assertEqual({e["gate"] for e in ESCAPES}, set(ROWS))

    def test_the_bound_is_pinned_by_the_thresholds_and_only_bracketed_by_the_organisms(self):
        shown = [e for e in ESCAPES if e["gate"] == "G3.exclusion"][0]["shown"]
        self.assertEqual(shown["by_organisms"], [0.342, 0.686])
        self.assertEqual(shown["at_registered_thresholds"], [0.49921, 0.50079])
        self.assertEqual((shown["impostor_scores"], shown["impostor_series"]), ([25, 41], 4))
        self.assertEqual((shown["positive_scores"], shown["weak_positive_score"]), ([64, 64, 64, 64], 61))
        self.assertEqual(meta.WRONG_BOUND, 0.48)

    def test_the_escapes_are_real_faults(self):
        by = {}
        for e in ESCAPES:
            by.setdefault(e["gate"], []).append(e)
        self.assertEqual(by["G8.demand"][0]["shown"], {"a_policy_that_reads_that_bit_scores": 64, "of": 64})
        shown = by["G7.calibration"][0]["shown"]
        self.assertLess(shown["exact_at_95_percent"], shown["exact_at_budget"] - 0.015)
        self.assertEqual(by["G7.calibration"][1]["shown"], {"it_reports": 0, "of": 256, "where_exact_reach_is": 1.0})
        # the weak carrier: called a negative on 64 episodes, shown to carry on 2,048
        self.assertEqual(by["G4.entry"][2]["shown"], {"it_scores": 40, "of": 64})
        # the short-lived positive: right in its first 64 episodes, wrong in the next 64
        short = R.scripted(64)
        self.assertEqual((R.score(short, SEEDS), R.score(short, meta.BLOCKS[0])), (64, 0))
        many = R.score(R.weak_carrier(), DEMAND)
        self.assertEqual((many, stats.equivalence(many, len(DEMAND), 0.5, 0.1, 1e-6)), (1249, "OUTSIDE"))

        def answers(make, *episodes):
            w, org = R.World(), make()
            return [w.episode(org, s, **kw)["answer"] for s, kw in enumerate(episodes, 1)]

        one, blank = {"force_bit": 1}, {"cue": False}
        self.assertEqual(answers(R.Register, one, one, blank), [1, 1, 0])
        self.assertEqual(answers(R.EveryThirdReset, one, one, blank), [1, 1, 1])     # the third reset leaks
        self.assertEqual(answers(R.SleeperRegister, one, one, one), [1, 1, 0])       # the carry bites two later
        self.assertEqual(answers(R.HiddenCounter, one, one, one), [1, 0, 0])         # wrong from the second on
        self.assertEqual(torture.observer_equivalence(R.Register, [9999], torture.rare_observer(PAIRS)).verdict, FAIL)
        org = R.Register()
        R.World().episode(org, 2000, observer=torture.hidden_observer([]))
        self.assertEqual(org.touched, 8)
        # run 2's ruler did say yes to the fixed builder; the registry's NEGATIVE is what makes that a fault
        self.assertEqual(audits.returned(meta.COUNTERFEIT, ("RECEIPT_gauntlet2.json", "cell", "BUILDER")), "POSITIVE")
        self.assertEqual(len(audits.audit_arms(meta.nudged(meta.run3()["STRATEGIST"]["replicates"], 3),
                                               meta.ARMS3).detail), 8)


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


class Arithmetic(unittest.TestCase):
    def test_registered_constants(self):
        self.assertEqual((stats.POWER_FLOOR, stats.DESIGN_CONFIDENCE), (0.99, 0.99))
        self.assertEqual((rulers.BOUND, rulers.ALPHA, rulers.P_WEAKEST, rulers.MIN_PHYSICS), (0.5, 1e-6, 15 / 16, 3))
        self.assertEqual((torture.MARGIN, torture.DEMAND_ALPHA), (0.1, 1e-6))
        self.assertEqual((search.CAL_ALPHA, search.CONTROL), (0.002, "ASCENT"))
        self.assertEqual((audits.N, audits.HOLDS_AT, audits.FAILS_AT), (24, 22, 12))
        self.assertEqual((audits.GOOD_MAX, audits.BAD_MIN), (3.5, 6.0))

    def test_binomial(self):
        self.assertAlmostEqual(stats.tail_ge(4, 0, 0.3), 1.0)
        self.assertAlmostEqual(stats.tail_ge(4, 4, 0.5), 0.0625)
        self.assertAlmostEqual(stats.tail_le(4, 0, 0.5), 0.0625)
        self.assertAlmostEqual(sum(stats.pmf(2048, 0.4)), 1.0)
        self.assertEqual("%.3e" % stats.tail_ge(64, 51, 0.5), "9.405e-07")
        self.assertEqual((stats.critical_k(64, 0.5, 1e-6), stats.critical_k(128, 0.5, 1e-6)), (51, 92))
        self.assertEqual(stats.critical_k(20, 0.5, 1e-6), 20)
        self.assertIsNone(stats.critical_k(16, 0.5, 1e-6))
        self.assertEqual((stats.lower_critical(64, 0.5, 1e-6), stats.lower_critical(128, 0.5, 1e-6)), (13, 36))
        self.assertEqual((stats.lower_critical(64, 15 / 16, 1e-6), stats.lower_critical(128, 15 / 16, 1e-6)), (47, 103))
        self.assertIsNone(stats.lower_critical(4, 0.5, 1e-6))

    def test_bounds_on_a_rate_seen_in_design_runs(self):
        self.assertAlmostEqual(stats.lower_bound(20, 20), 0.01 ** (1 / 20), places=9)
        self.assertAlmostEqual(stats.lower_bound(480, 480), 0.01 ** (1 / 480), places=9)
        self.assertAlmostEqual(stats.upper_bound(0, 480), 1 - 0.01 ** (1 / 480), places=9)
        self.assertEqual((stats.lower_bound(0, 480), stats.upper_bound(480, 480)), (0.0, 1.0))
        self.assertEqual("%.4f %.4f" % (stats.lower_bound(96, 480), stats.upper_bound(96, 480)), "0.1591 0.2459")
        self.assertEqual("%.4f" % stats.zero_hit_upper(24), "0.1173")
        self.assertEqual("%.4f" % stats.zero_hit_upper(128), "0.0231")
        self.assertEqual("%.4f" % stats.zero_hit_upper(128, 0.99), "0.0353")

    def test_a_count_is_a_non_negative_integer_and_not_a_boolean(self):
        self.assertEqual([stats.is_count(v) for v in (0, 7, -1, True, False, 1.0, "1", None)],
                         [True, True, False, False, False, False, False, False])

    def test_a_score_has_five_places_to_stand(self):
        def at(k, **kw):
            return stats.classify(k, 64, 0.5, 1e-6, rulers.P_WEAKEST, **kw)
        self.assertEqual([at(k) for k in (64, 51, 50, 48, 47, 14, 13, 0)], [
            "EXCLUDES", "EXCLUDES", "UNDECIDED", "UNDECIDED", "AT_BOUND", "AT_BOUND", "INVERTED", "INVERTED"])
        self.assertEqual(at(13, exact_rate=False), "AT_BOUND")
        self.assertEqual(stats.classify(16, 16, 0.5, 1e-6, 1.0), "UNDERPOWERED")
        # with 128 trials the two answers meet: no score is undecided
        self.assertEqual([stats.classify(k, 128, 0.5, 1e-6, 15 / 16) for k in (92, 91, 37, 36)],
                         ["EXCLUDES", "AT_BOUND", "AT_BOUND", "INVERTED"])
        self.assertNotIn("UNDECIDED", {stats.classify(k, 128, 0.5, 1e-6, 15 / 16) for k in range(129)})

    def test_the_registered_thresholds_are_the_ones_the_arithmetic_gives(self):
        self.assertEqual(rulers.EDGES, {51: "POSITIVE", 50: "UNDECIDED", 48: "UNDECIDED", 47: "NEGATIVE",
                                        14: "NEGATIVE", 13: "INVERTED"})
        self.assertEqual(meta.edges_for(0.5), rulers.EDGES)
        self.assertEqual(meta.edges_for(0.48), {50: "POSITIVE", 49: "UNDECIDED", 48: "UNDECIDED", 47: "NEGATIVE",
                                                12: "NEGATIVE", 11: "INVERTED"})

    def test_preflight_floors(self):
        weak = stats.preflight(64, 0.5, 1e-6, 0.85)
        self.assertEqual((weak.verdict, "%.5f" % weak.detail["power"]), (BLOCKED, "0.90959"))
        self.assertEqual(stats.preflight(64, 0.5, 1e-6, 0.88).verdict, BLOCKED)          # power 0.982
        strong = stats.preflight(64, 0.5, 1e-6, 0.89)
        self.assertEqual((strong.verdict, "%.5f" % strong.detail["power"], strong.detail["critical_k"]),
                         (PASS, "0.99118", 51))
        self.assertEqual("%.5f" % stats.preflight(64, 0.5, 1e-6, 15 / 16).detail["power"], "0.99997")
        self.assertEqual(stats.preflight(64, 0.5, 0.0099, 1.0).verdict, PASS)
        self.assertEqual(stats.preflight(64, 0.5, 0.011, 1.0).verdict, BLOCKED)          # 1 - alpha under the floor
        low = stats.preflight(18, 0.02, 1e-6, 0.6)
        self.assertEqual((low.verdict, "%.3f" % low.detail["negative"], "%.4f" % low.detail["power"]),
                         (BLOCKED, "0.695", "0.9942"))
        self.assertEqual(stats.preflight(64, 0.5, 1e-6, 99).verdict, BLOCKED)
        self.assertEqual(stats.preflight(0, 0.5, 1e-6, 1.0).verdict, BLOCKED)

    def test_a_design_rate_is_used_at_its_lower_bound(self):
        self.assertEqual(stats.preflight_from_design(64, 0.5, 1e-6, 256, 256).verdict, PASS)
        self.assertEqual(stats.preflight_from_design(64, 0.5, 1e-6, 20, 20).verdict, BLOCKED)   # bound 0.794
        self.assertEqual(stats.preflight_from_design(64, 0.5, 1e-6, 38, 38).verdict, BLOCKED)   # bound 0.886
        self.assertEqual(stats.preflight_from_design(64, 0.5, 1e-6, 39, 39).verdict, PASS)      # bound 0.889
        for bad in ((0, 0), (5, 4), (-1, 4), (True, True), (4.0, 4)):
            self.assertEqual(stats.preflight_from_design(64, 0.5, 1e-6, *bad).verdict, BLOCKED, bad)

    def test_equivalence_is_not_absence_of_a_difference(self):
        def eq(k, n=2048):
            return stats.equivalence(k, n, 0.5, torture.MARGIN, 1e-6)
        self.assertEqual([eq(k) for k in (912, 913, 928, 929, 1024, 1119, 1120, 1135, 1136)], [
            "OUTSIDE", "UNDECIDED", "UNDECIDED", "WITHIN", "WITHIN", "WITHIN", "UNDECIDED", "UNDECIDED", "OUTSIDE"])
        self.assertNotIn("WITHIN", {eq(k, 64) for k in range(65)})

    def test_attainability_is_computed_from_the_table_at_the_worse_end_of_the_interval(self):
        t = meta.table()
        p = stats.outcome_probability(t, 0.97)
        self.assertEqual("%.4f %.4f" % (p["HOLDS"], p["INDETERMINATE"]), "0.9659 0.0341")

        def att(holds, fails):
            return registration.attainability(t, {"HOLDS": meta.runs(*holds), "FAILS": meta.runs(*fails)}).verdict

        self.assertEqual(att((480, 480), (96, 480)), PASS)
        self.assertEqual(att((478, 480), (96, 480)), PASS)          # the lower end gives 0.9919
        self.assertEqual(att((476, 480), (96, 480)), BLOCKED)       # the lower end gives 0.9808
        self.assertEqual(att((240, 240), (96, 480)), BLOCKED)       # 0.9897: too few design units
        self.assertEqual(att((480, 480), (110, 480)), PASS)         # the upper end gives 0.9944
        self.assertEqual(att((480, 480), (120, 480)), BLOCKED)      # the upper end gives 0.9888; the lower 0.9997
        self.assertEqual(registration.attainability(t, {"HOLDS": meta.runs(480, 480)}).verdict, BLOCKED)
        self.assertEqual(registration.attainability(t, {"HOLDS": meta.runs(480, 480), "NOPE": meta.runs(0, 480)}).verdict,
                         BLOCKED)
        self.assertEqual(registration.attainability(t, {"HOLDS": 0.999, "FAILS": 0.2}).verdict, BLOCKED)
        self.assertEqual(att((481, 480), (96, 480)), BLOCKED)


class Registration(unittest.TestCase):
    def test_every_required_field_is_required(self):
        for field in meta.CELL_FIELDS:
            self.assertEqual(registration.check_cell(meta.cell(**{field: None})).verdict, BLOCKED, field)
        self.assertEqual(registration.check_cell({}).verdict, BLOCKED)
        self.assertEqual(registration.check_cell(meta.cell(registered_at="100")).verdict, BLOCKED)
        self.assertEqual(registration.check_cell(meta.cell(registered_at=True)).verdict, BLOCKED)
        self.assertEqual(registration.check_cell(meta.cell(exposure={"tuning_evaluations": True})).verdict, BLOCKED)

    def test_a_verdict_table_is_total_single_valued_and_reaches_every_outcome(self):
        check = registration.check_verdict_table
        self.assertEqual(check(meta.table()).verdict, PASS)
        self.assertEqual(check(dict(meta.table(), n=0)).verdict, BLOCKED)
        self.assertEqual(check(dict(meta.table(), n=True)).verdict, BLOCKED)
        self.assertEqual(check(dict(meta.table(), rule=[])).verdict, BLOCKED)
        self.assertEqual(check(dict(meta.table(), outcomes=[])).verdict, BLOCKED)
        self.assertEqual(check(meta.table([(22, 24, "HOLDS"), (0, 13, "FAILS"), (13, 21, "INDETERMINATE")])).verdict, FAIL)
        self.assertEqual(check(meta.table([(22, 24, "HOLDS"), (0, 12, "FAILS")])).verdict, FAIL)
        self.assertEqual(check(meta.table([(13, 24, "HOLDS"), (0, 12, "FAILS")])).verdict, FAIL)

    def test_one_seed_per_independent_unit(self):
        def cell(n):
            return registration.check_cell(meta.cell(registered_seeds=list(range(5000, 5000 + n)))).verdict
        self.assertEqual([cell(23), cell(24), cell(25)], [FAIL, PASS, FAIL])

    def test_a_receipt_is_ordered_against_its_registration(self):
        def at(t):
            return registration.check_receipt(meta.cell(), meta.run_receipt(ran_at=t), meta.SOURCE).verdict
        self.assertEqual([at(99), at(100), at(101)], [FAIL, INDETERMINATE, PASS])
        self.assertEqual(at(True), BLOCKED)

    def test_a_receipt_needs_each_of_its_three_fields(self):
        for field in ("source_sha256", "seeds", "ran_at"):
            r = registration.check_receipt(meta.cell(), meta.run_receipt(**{field: None}), meta.SOURCE)
            self.assertEqual(r.verdict, BLOCKED, field)
            self.assertIn(field, r.reason)

    def test_line_endings_do_not_change_a_source_hash(self):
        self.assertEqual(registration.sha(b"a\r\nb\r\n"), registration.sha(b"a\nb\n"))
        self.assertNotEqual(registration.sha(b"a\nb\n"), registration.sha(b"a\nc\n"))


class Rulers(unittest.TestCase):
    def test_panel_scores(self):
        got = {p: (R.score(pos, SEEDS), R.score(imp, SEEDS)) for p, (pos, imp) in R.PANEL.items()}
        self.assertEqual(got, {"REGISTER": (64, 26), "ATTRACTOR": (64, 31), "PACKET": (64, 32), "LATTICE": (64, 33)})
        self.assertEqual(R.score(R.FadingRegister, SEEDS), 61)
        self.assertEqual(R.score(R.Inverter, SEEDS), 0)
        self.assertEqual(R.score(R.scripted(49), SEEDS), 49)

    def test_the_four_impostors_are_four_series(self):
        _, _, imp = meta.organism_scores()
        self.assertEqual(imp["ATTRACTOR"], [31, 34, 32, 31, 29, 40, 25, 32, 41])
        self.assertEqual(imp["REGISTER"], [26, 32, 30, 33, 34, 38, 27, 34, 36])
        self.assertEqual(len({tuple(v) for v in imp.values()}), 4)

    def test_the_exclusion_ruler_at_its_registered_thresholds(self):
        got = {k: rulers.exclusion_ruler(R.scripted(k), SEEDS) for k in (64, 51, 50, 48, 47, 14, 13, 0)}
        self.assertEqual(got, {64: "POSITIVE", 51: "POSITIVE", 50: "UNDECIDED", 48: "UNDECIDED", 47: "NEGATIVE",
                               14: "NEGATIVE", 13: "INVERTED", 0: "INVERTED"})
        self.assertEqual(rulers.exclusion_ruler(R.Register, SEEDS[:16]), "UNDERPOWERED")

    def test_interchange_gives_a_statistical_answer_of_each_kind(self):
        want = {R.Register: "POSITIVE", R.Attractor: "POSITIVE", R.PacketRing: "POSITIVE", R.Lattice: "POSITIVE",
                R.FadingRegister: "POSITIVE", R.LateBinder: "POSITIVE", R.Inverter: "INVERTED",
                R.RegisterImpostor: "NEGATIVE", R.AttractorImpostor: "NEGATIVE", R.PacketImpostor: "NEGATIVE",
                R.LatticeImpostor: "NEGATIVE", R.Constant: "NEGATIVE"}
        for make, answer in want.items():
            self.assertEqual(rulers.interchange_ruler(make, SEEDS), answer, make.__name__)
        self.assertEqual(rulers.interchange_ruler(R.Register, PAIRS[:8]), "UNDERPOWERED")

    def test_register_swap_is_valid_in_one_physics_only(self):
        t = rulers.known_answers(rulers.register_swap_ruler, R.PANEL, SEEDS)
        self.assertEqual(sorted(p for p, row in t.items() if row["agrees"]), ["REGISTER"])
        for make in (R.Attractor, R.PacketRing, R.Lattice):
            self.assertEqual(rulers.register_swap_ruler(make, SEEDS), "NOT_MOVED", make.__name__)

    def test_the_swap_is_made_after_the_fourth_step(self):
        # LateBinder writes the cue into its word at its fifth step. Swapped before, nothing moves.
        self.assertEqual(rulers.register_swap_ruler(R.LateBinder, SEEDS), "NOT_MOVED")
        word = (lambda org: org.w), (lambda org, v: setattr(org, "w", v))
        self.assertEqual(rulers._interchange(R.LateBinder, SEEDS, *word, at=5), "POSITIVE")

    def test_a_shared_ruler_needs_three_physics(self):
        three = {k: R.PANEL[k] for k in ("REGISTER", "ATTRACTOR", "PACKET")}
        self.assertEqual(meta.neutral("CLASS_EXCLUSION", "SHARED", three).verdict, PASS)
        two = {k: R.PANEL[k] for k in ("REGISTER", "ATTRACTOR")}
        self.assertEqual(meta.neutral("CLASS_EXCLUSION", "SHARED", two).verdict, UNQUALIFIED)

    def test_a_ruler_must_say_where_it_is_valid(self):
        for nowhere in ([], None, ""):
            self.assertEqual(meta.neutral("REGISTER_SWAP", nowhere).verdict, BLOCKED)

    def test_with_64_pairs_interchange_can_be_undecided(self):
        # 34 groups of stored words, then constants: 49 of 64 follow the donor, between the two answers
        self.assertEqual(rulers.interchange_ruler(R.faulty_from(103, R.Register, R.Constant), SEEDS[:32]), "UNDECIDED")
        self.assertEqual(rulers.interchange_ruler(R.Register, SEEDS[:32]), "POSITIVE")
        self.assertEqual(rulers.interchange_ruler(R.Constant, SEEDS[:32]), "NEGATIVE")


class Torture(unittest.TestCase):
    def test_a_score_only_check_passes_a_broken_observer(self):
        for physics, (positive, _) in R.PANEL.items():
            r = torture.observer_equivalence(positive, PAIRS, torture.greedy_observer, compare="score")
            self.assertEqual(r.verdict, PASS, physics)
            r = torture.observer_equivalence(positive, PAIRS, torture.greedy_observer)
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

    def test_a_disturbance_the_organism_repairs_shows_only_straight_after_the_observer(self):
        quiet = R.World().episode(R.Lattice(), 2000)
        healed = R.World().episode(R.Lattice(), 2000, observer=torture.healing_observer([]))
        self.assertEqual((quiet["answer"], quiet["final"]), (healed["answer"], healed["final"]))
        self.assertEqual([s[4] for s in quiet["trace"]], [s[4] for s in healed["trace"]])
        self.assertNotEqual([s[5] for s in quiet["trace"]], [s[5] for s in healed["trace"]])

    def test_restart_is_judged_on_the_trajectory_and_not_on_the_answer(self):
        make = R.LatticeLateBadCapture
        for seed in PAIRS:
            whole = R.World().episode(make(), seed)

            def restart(org):
                used = make()
                R.World().episode(used, seed, force_bit=1 - whole["bit"])
                used.restore(org.capture())
                return used

            for at in range(8):
                self.assertEqual(R.World().episode(make(), seed, interrupt={at: restart})["answer"], whole["answer"])
        self.assertEqual(torture.restart_equivalence(make, PAIRS).verdict, FAIL)

    def test_restart_cuts_after_every_one_of_the_eight_steps(self):
        self.assertEqual(len(R.World().episode(R.Register(), 2000)["trace"]), 8)
        r = torture.restart_equivalence(R.LatticeEndBadCapture, PAIRS)
        self.assertEqual((r.verdict, r.reason), (FAIL, "capture and restore do not carry the state (seed 2000, step 7)"))

    def test_reset_is_judged_on_the_trajectory_and_not_on_the_answer(self):
        make = R.LatticeKeepsClock
        for seed in PAIRS:
            fresh = R.World().episode(make(), seed + 1)["answer"]
            w, org = R.World(), make()
            w.episode(org, seed, force_bit=1)
            self.assertEqual(w.episode(org, seed + 1)["answer"], fresh)
        self.assertEqual(torture.reset_closure(make, PAIRS).verdict, FAIL)

    def test_reset_is_tried_after_each_kind_of_earlier_episode(self):
        self.assertEqual(torture.reset_closure(R.SneakyRegister, PAIRS).reason,
                         "state survives the reset (seed 2000, earlier cue 1)")
        self.assertEqual(torture.reset_closure(R.BlankCarry, PAIRS).reason,
                         "state survives the reset (seed 2000, earlier cue None)")
        self.assertEqual(torture.reset_closure(R.LeakyResetRegister, PAIRS).reason,
                         "state survives the reset (seed 2000, earlier cue 0)")
        # the earlier episode is drawn from another seed: two episodes of one seed share their distractors
        self.assertEqual(torture.reset_closure(R.RunEcho, PAIRS).verdict, FAIL)
        w, org = R.World(), R.RunEcho()
        for cue in (0, None, 1, None):
            w.episode(org, 2000, cue=cue is not None, force_bit=cue)
            self.assertEqual(org.native()[1], False)

    def test_a_fault_from_the_second_seed_on_is_found_at_the_second_seed(self):
        r = torture.reset_closure(R.faulty_from(13, R.Register, R.LeakyResetRegister), PAIRS)
        self.assertEqual((r.verdict, r.reason), (FAIL, "state survives the reset (seed 2001, earlier cue 0)"))
        r = torture.restart_equivalence(R.faulty_from(18, R.PacketRing, R.PacketRingBadCapture), PAIRS)
        self.assertEqual(r.verdict, FAIL)
        self.assertIn("seed 2001", r.reason)
        r = torture.observer_equivalence(R.Register, PAIRS, meta.all_but_first_observer)
        self.assertEqual((r.verdict, r.reason), (FAIL, "the observer changes the run (seed 2001)"))

    def test_the_world_clears_its_mark_between_episodes(self):
        self.assertEqual(torture.reset_closure(R.WorldParker, PAIRS, writable_mark=True).verdict, PASS)
        self.assertEqual(torture.reset_closure(R.WorldParker, PAIRS, writable_mark=True, keep_mark=True).verdict, FAIL)


class DemandClosure(unittest.TestCase):
    def test_what_is_scored(self):
        clean = torture.demand_closure(DEMAND, TRAIN)
        self.assertEqual(clean.verdict, PASS)
        self.assertEqual(sorted(clean.detail), [
            "CLOCK", "CONSTANT", "KEY_READER", "LAST_DISTRACTOR", "TABLE_ALL", "TABLE_CLOCK", "TABLE_FIRST1",
            "TABLE_FIRST2", "TABLE_FIRST3", "TABLE_LAST1", "TABLE_LAST2", "TABLE_LAST3", "TABLE_PROBE", "WORLD_PARKER"])
        self.assertTrue(all(929 <= k <= 1119 for k in clean.detail.values()))

    def test_a_baseline_at_each_edge_of_the_margin(self):
        def gate(k):
            return torture.demand_closure(DEMAND, TRAIN, baselines=dict(R.BASELINES, TABLE=None,
                                                                        EDGE=R.scripted(k))).verdict
        self.assertEqual([gate(k) for k in (912, 913, 928, 929, 1119, 1120, 1135, 1136)],
                         [FAIL, INDETERMINATE, INDETERMINATE, PASS, PASS, INDETERMINATE, INDETERMINATE, FAIL])

    def test_too_few_episodes_or_too_long_a_gap_give_no_yes(self):
        self.assertEqual(torture.demand_closure(SEEDS, TRAIN).verdict, INDETERMINATE)
        long_gap = torture.demand_closure(DEMAND, TRAIN, gap=20)
        self.assertEqual((long_gap.verdict, long_gap.reason), (INDETERMINATE, "too little data to fit: TABLE_ALL"))
        self.assertIsNone(long_gap.detail["TABLE_ALL"])

    def test_a_policy_that_is_reliably_wrong_has_the_information_too(self):
        half = torture.demand_closure(DEMAND, TRAIN, leak_key="inverted")
        self.assertEqual((half.verdict, half.detail["KEY_READER"]), (FAIL, 0))

    def test_no_seeds_or_shared_seeds_block(self):
        self.assertEqual(torture.demand_closure([], TRAIN).verdict, BLOCKED)
        self.assertEqual(torture.demand_closure(DEMAND, DEMAND[:1] + TRAIN).verdict, BLOCKED)


class Search(unittest.TestCase):
    def test_exact_reach(self):
        b = meta.BUDGET
        self.assertEqual(search.exact_reach("NEEDLE", "STRICT", b, "COLD"), 0.0)
        self.assertEqual(search.exact_reach("VALLEY", "STRICT", b, "COLD"), 0.0)
        self.assertEqual(search.exact_reach("VALLEY", "NEUTRAL", b, "COLD"), 0.0)
        self.assertGreater(search.exact_reach("VALLEY", "STRICT", b, "REPAIR", 1), 0.99)
        self.assertGreater(search.exact_reach("ASCENT", "NEUTRAL", b, "COLD"), 0.99)
        self.assertEqual("%.4f" % search.exact_reach("NEEDLE", "NEUTRAL", b, "COLD"), "0.7298")
        self.assertEqual("%.4f" % search.exact_reach("NEEDLE", "NEUTRAL", b, "REPAIR", 1), "0.7757")
        self.assertEqual("%.4f" % search.exact_reach("VALLEY", "NEUTRAL", b, "REPAIR", 1), "0.1797")
        self.assertEqual(["%.4f" % search.exact_reach("ASCENT", "STRICT", n, "COLD") for n in (5, 24, 46, 47)],
                         ["0.0107", "0.8126", "0.9896", "0.9909"])
        self.assertEqual("%.4f" % search.exact_reach("NEEDLE", "NEUTRAL", 24, "COLD"), "0.0624")

    def test_the_calibration_panel(self):
        self.assertEqual(search.CELLS, (("NEEDLE", "NEUTRAL", "COLD", 0), ("NEEDLE", "NEUTRAL", "REPAIR", 1),
                                        ("VALLEY", "NEUTRAL", "REPAIR", 1), ("ASCENT", "STRICT", "COLD", 0),
                                        ("VALLEY", "STRICT", "COLD", 0)))

    def test_calibration_has_a_stated_resolution(self):
        def cal(k):
            return search.calibration("NEEDLE", "NEUTRAL", meta.BUDGET, "COLD", meta.FOUNDERS, 0, lambda *a: k).verdict
        self.assertEqual([cal(163), cal(164), cal(208), cal(209)], [FAIL, PASS, PASS, FAIL])

    def test_a_report_is_replayed_and_not_believed(self):
        honest = meta.report()
        self.assertEqual(honest["policies"]["NEUTRAL"]["hits"], 101)
        self.assertEqual(meta.checked(honest).verdict, PASS)
        lying = meta.recount(honest, NEUTRAL={"seeds": list(meta.REPORTED), "hits": 102})
        self.assertEqual(meta.checked(lying).verdict, FAIL)

    def test_a_small_true_discovery_passes_and_one_hit_refutes_a_null(self):
        small = meta.report(budget=24)
        self.assertEqual((small["policies"]["NEUTRAL"]["hits"], meta.checked(small).verdict), (5, PASS))
        one = meta.null("NEEDLE", budget=8)
        self.assertEqual(sum(p["hits"] for p in one["policies"].values()), 1)
        self.assertEqual(meta.checked(one).verdict, FAIL)

    def test_a_bound_may_be_rounded_or_more_cautious_and_never_smaller(self):
        exact = stats.zero_hit_upper(len(meta.REPORTED))
        for bound, want in ((round(exact, 4), PASS), (stats.zero_hit_upper(len(meta.REPORTED), 0.99), PASS),
                            (exact - 0.001, FAIL), (1.5, FAIL)):
            self.assertEqual(meta.checked(meta.null(upper_bound=bound)).verdict, want, bound)

    def test_a_null_needs_a_policy_that_can_cross_a_neutral_step(self):
        self.assertEqual(meta.checked(meta.null("NEEDLE", ("STRICT", "ELITIST"))).verdict, BLOCKED)
        self.assertEqual(meta.checked(meta.null("VALLEY", ("STRICT", "NEUTRAL"))).verdict, PASS)

    def test_a_null_needs_a_positive_control_reached_99_times_in_100(self):
        self.assertEqual(meta.checked(meta.null(budget=46)).verdict, UNQUALIFIED)    # control 0.9896
        self.assertEqual(meta.checked(meta.null(budget=47)).verdict, PASS)           # control 0.9909

    def test_founders_registered_to_miss_or_to_hit_are_caught_only_by_the_exact_count(self):
        missed = meta.missers()
        r = meta.checked(meta.null("NEEDLE", seeds=missed), seeds=missed)
        self.assertEqual(r.verdict, FAIL)
        self.assertIn("the exact reach is above the stated bound: NEUTRAL 0.7298", r.reason)
        hit = meta.picked(True)
        r = meta.checked(meta.report(seeds=hit), seeds=hit)
        self.assertEqual(r.verdict, FAIL)
        self.assertIn("128 hits in 128 founders is not compatible with the exact reach 0.7298", r.reason)

    def test_a_report_is_held_to_what_was_registered(self):
        honest = meta.report()
        self.assertEqual(search.REGISTERED, ("landscape", "budget", "start_law", "distance", "policies", "seeds"))
        for field, other in (("landscape", "ASCENT"), ("budget", 399), ("start_law", "REPAIR"), ("distance", 1),
                             ("policies", ["STRICT"])):
            r = meta.checked(honest, **{field: other})
            self.assertEqual(r.verdict, FAIL, field)
            self.assertIn("the search reported is not the search registered: %s" % field, r.reason)
        for field in search.REGISTERED:
            partial = {k: v for k, v in meta.registered_for(honest).items() if k != field}
            self.assertEqual(search.check_report(honest, partial).verdict, BLOCKED, field)


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
        self.assertEqual((len(r.detail["table"]), len(self.r2), len(r.detail["not_isolated"])), (13, 9, 7))

    def test_run3_clauses(self):
        r = audits.audit_clauses(self.r3, audits.clauses_run3)
        self.assertEqual(r.detail["cannot_fail"], [
            "NESTING.lesion_hurts", "NESTING.rescue_restores", "NESTING.sham_harmless",
            "PROVENANCE.random_store_no_help", "U_TRANSFER.frozen_U_good_on_C",
            "U_TRANSFER.frozen_U_good_on_narrower_C"])
        self.assertEqual((len(self.r3), len(r.detail["not_isolated"])), (4, 6))

    def test_run3_eight_arms_give_three_series(self):
        r = audits.audit_arms(self.r3["STRATEGIST"]["replicates"], meta.ARMS3)
        self.assertEqual(r.verdict, FAIL)
        self.assertEqual(r.detail, [["naive_B", "lesion_B", "irrelevant_history_B"],
                                    ["dev_B", "sham_B", "rescue_B", "v_donor_B"], ["random_V_B"]])
        for replicates in (1, 2):
            self.assertEqual(audits.audit_arms(meta.nudged(self.r3["STRATEGIST"]["replicates"], replicates),
                                               meta.ARMS3).detail, r.detail)

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


def replicate(**change):
    """A run-2 replicate with every one of the thirteen clauses true, each at its boundary."""
    o = {"naive_B": 100, "dev_B": 25, "lifecycle_developed": 9, "lifecycle_naive": 10, "q_C_same_kind": 3.5,
         "q_C_narrower": 3.5, "q_C_lesioned_line": 6.0, "lesion_B": 50, "sham_B": 54, "rescue_B": 54, "v_donor_B": 25,
         "wrong_history_B": 50, "random_library_B": 50, "dev_D": 25, "naive_D": 100, "dev_E": 25, "naive_E": 100}
    o.update(change)
    return o


def toy(**false_in):
    """A toy cell of 24 replicates in which each named clause is false in the given number of them."""
    how = {"SAVINGS": {"dev_B": 60, "sham_B": 61}, "LESION": {"lesion_B": 10}, "SHAM": {"sham_B": 400}}
    reps = [dict(meta.TOY) for _ in range(24)]
    for clause, k in false_in.items():
        for o in reps[:k]:
            o.update(how[clause])
    return {"replicates": reps}


class AuditThresholds(unittest.TestCase):
    def test_each_clause_of_run_2_at_its_boundary(self):
        self.assertEqual(set(audits.clauses_run2(replicate()).values()), {True})
        one_step = {"SAVINGS": {"dev_B": 26, "sham_B": 54, "rescue_B": 54}, "LIFECYCLE": {"lifecycle_developed": 10},
                    "U_TRANSFER.frozen_U_good_on_C": {"q_C_same_kind": 3.6},
                    "U_TRANSFER.frozen_U_good_on_narrower_C": {"q_C_narrower": 3.6},
                    "U_TRANSFER.lesioned_line_bad_on_C": {"q_C_lesioned_line": 5.9},
                    "NESTING.lesion_hurts": {"lesion_B": 49}, "NESTING.sham_harmless": {"sham_B": 55},
                    "NESTING.rescue_restores": {"rescue_B": 55}, "NESTING.donor_V_helps": {"v_donor_B": 26},
                    "PROVENANCE.wrong_history_no_help": {"wrong_history_B": 49},
                    "PROVENANCE.random_store_no_help": {"random_library_B": 49}, "REPEAT.D": {"dev_D": 26},
                    "REPEAT.E": {"dev_E": 26}}
        self.assertEqual(len(one_step), 13)
        for clause, change in one_step.items():
            got = audits.clauses_run2(replicate(**change))
            self.assertEqual([c for c, v in got.items() if not v], [clause])

    def test_run_3_uses_a_factor_of_two_and_its_own_arm_names(self):
        o = replicate(dev_B=50, sham_B=104, rescue_B=104, v_donor_B=50, dev_D=50, dev_E=50)
        o["irrelevant_history_B"], o["random_V_B"] = o.pop("wrong_history_B"), o.pop("random_library_B")
        self.assertEqual(set(audits.clauses_run3(o).values()), {True})
        self.assertEqual([c for c, v in audits.clauses_run3(dict(o, dev_B=51)).items() if not v], ["SAVINGS"])
        self.assertEqual([c for c, v in audits.clauses_run3(dict(o, irrelevant_history_B=49)).items() if not v],
                         ["PROVENANCE.wrong_history_no_help"])

    def test_a_clause_can_fail_only_if_it_is_false_in_half_the_replicates_of_some_cell(self):
        def audit(false_in):
            cells = {"GOOD": toy(), "NO_SAVINGS": toy(SAVINGS=24), "NO_LESION": toy(LESION=24),
                     "HARMFUL_SHAM": toy(SHAM=false_in)}
            return audits.audit_clauses(cells, meta.toy_clauses)
        self.assertEqual(audit(12).verdict, PASS)                       # true in 12 of 24: it fails there
        r = audit(11)                                                   # true in 13 of 24: it fails nowhere
        self.assertEqual((r.verdict, r.detail["cannot_fail"]), (UNQUALIFIED, ["NESTING.sham_harmless"]))

    def test_a_clause_can_hold_only_if_it_is_true_in_22_replicates_of_some_cell(self):
        def audit(k):
            cells = {"GOOD": toy(SAVINGS=k), "NO_SAVINGS": toy(SAVINGS=24), "NO_LESION": toy(LESION=24, SAVINGS=k),
                     "HARMFUL_SHAM": toy(SHAM=24, SAVINGS=k)}
            return audits.audit_clauses(cells, meta.toy_clauses)
        self.assertEqual(audit(2).verdict, PASS)                        # true in 22 of 24
        r = audit(3)                                                    # true in 21 of 24 at best
        self.assertEqual((r.verdict, r.detail["cannot_hold"]), (UNQUALIFIED, ["SAVINGS"]))

    def test_a_clause_is_isolated_only_where_every_other_clause_holds(self):
        def audit(k):
            cells = {"GOOD": toy(), "NO_SAVINGS": toy(SAVINGS=24), "NO_LESION": toy(LESION=24, SAVINGS=k),
                     "HARMFUL_SHAM": toy(SHAM=24)}
            return audits.audit_clauses(cells, meta.toy_clauses)
        self.assertEqual(audit(2).verdict, PASS)
        r = audit(3)
        self.assertEqual((r.verdict, r.detail["not_isolated"]), (INDETERMINATE, ["NESTING.lesion_hurts"]))

    def test_arms_are_one_series_at_22_of_24(self):
        base = [{"a": i, "b": i} for i in range(24)]

        def groups(differ):
            reps = [dict(o, b=o["b"] + (1 if i < differ else 0)) for i, o in enumerate(base)]
            return len(audits.audit_arms(reps, ("a", "b")).detail)
        self.assertEqual([groups(0), groups(2), groups(3)], [1, 1, 2])

    def test_the_sham_margin_is_a_quarter_and_the_slack_one_task(self):
        row = {"GOOD": 24, "BAD": 0}
        for dev, sham, want in ((10, 12, PASS), (10, 13, FAIL), (10, 8, PASS), (10, 7, FAIL), (3, 4, PASS),
                                (3, 5, FAIL), (3, 2, PASS), (3, 1, FAIL)):
            reps = [{"dev_B": dev, "sham_B": sham} for _ in range(24)]
            self.assertEqual(audits.audit_sham(reps, row).verdict, want, (dev, sham))

    def test_a_sham_is_neutral_in_22_replicates_and_able_to_fail_in_12(self):
        def reps(far):
            return [{"dev_B": 10, "sham_B": 40 if i < far else 10} for i in range(24)]
        row = {"GOOD": 24, "BAD": 0}
        self.assertEqual([audits.audit_sham(reps(2), row).verdict, audits.audit_sham(reps(3), row).verdict], [PASS, FAIL])
        self.assertEqual(audits.audit_sham(reps(0), {"GOOD": 24, "BAD": 12}).verdict, PASS)
        self.assertEqual(audits.audit_sham(reps(0), {"GOOD": 24, "BAD": 13}).verdict, UNQUALIFIED)

    def test_what_counts_as_a_registered_choice(self):
        ok = meta.SETTING_OK
        self.assertEqual(audits.SETTING, ("cost", "later_families", "content_reset", "sham", "family_A",
                                          "wrong_history", "effect_threshold", "power", "amortization_horizon"))
        for word in ("", "tbd", "todo", "n/a", "na", "none", "unknown", "not computed", "?", " TBD ", "N/A"):
            self.assertEqual(audits.audit_setting(dict(ok, cost=word)).verdict, BLOCKED, word)
        for power, want in ((0.989, BLOCKED), (0.99, PASS), (1, PASS), (1.0, PASS), (1.01, BLOCKED), (True, BLOCKED),
                            ("0.99", BLOCKED)):
            self.assertEqual(audits.audit_setting(dict(ok, power=power)).verdict, want, power)
        for horizon, want in ((0, BLOCKED), (1, PASS), (3.0, PASS), (2.5, BLOCKED), ("3", BLOCKED), (True, BLOCKED)):
            self.assertEqual(audits.audit_setting(dict(ok, amortization_horizon=horizon)).verdict, want, horizon)
        for threshold, want in ((0, BLOCKED), (0.5, PASS), (-1, BLOCKED), ("large", BLOCKED), (True, BLOCKED)):
            self.assertEqual(audits.audit_setting(dict(ok, effect_threshold=threshold)).verdict, want, threshold)

    def test_a_contrast_changes_its_named_variable_and_nothing_else(self):
        a = {"x": 1, "y": 1, "z": 1}
        self.assertEqual(audits.audit_contrast("x", a, dict(a, x=2)).verdict, PASS)
        self.assertEqual(audits.audit_contrast("x", a, dict(a, x=2, y=2)).verdict, FAIL)
        self.assertEqual(audits.audit_contrast("x", a, dict(a, y=2)).verdict, FAIL)
        self.assertEqual(audits.audit_contrast("x", a, dict(a, x=2, w=0)).verdict, FAIL)


class Kit(unittest.TestCase):
    def test_every_cell_of_the_four_receipts_is_registered(self):
        self.assertEqual(len(audits.RUNS), 26)
        per = {}
        for _, setting, _, answers in audits.RUNS:
            per[setting] = per.get(setting, 0) + 1
            self.assertEqual(len(answers), 1)
        self.assertEqual(per, {"V01@RUN1": 4, "S19@RUN2": 9, "S19@RUN3": 4, "BITS@KEYS": 9})
        self.assertEqual({c for r in audits.RUNS for c in r[3]}, {"STRONG", "BITS"})      # no verdict on reuse
        self.assertEqual({a["STRONG"] for r in audits.RUNS for a in [r[3]] if "STRONG" in a}, {"NEGATIVE"})
        self.assertEqual(len(audits.UNBUILT), 15)
        self.assertEqual(sorted(m for m, a in audits.UNBUILT.items() if "COMBINATION" in a), [
            "PAIR_COMPOSER", "PAIR_ELIMINATOR", "PAIR_HIDER", "PAIR_REPEAT_WATCHER", "PAIR_SANDBAGGER",
            "PAIR_SCHEMA_CACHE", "PAIR_TABLE_CACHE", "PAIR_TWO_TABLES"])

    def test_what_each_ruler_returned_on_the_kit(self):
        got = {(m, s): audits.returned(meta.COUNTERFEIT, src) for m, s, src, _ in audits.RUNS}
        yes = sorted(k for k, v in got.items() if v == "POSITIVE")
        self.assertEqual(yes, [("KEY_ACQUIRER_12", "BITS@KEYS"), ("KEY_ACQUIRER_16", "BITS@KEYS"),
                               ("KEY_ACQUIRER_4", "BITS@KEYS"), ("KEY_ACQUIRER_8", "BITS@KEYS"),
                               ("LIBRARY_FIXED_BUILDER", "S19@RUN2"), ("LIBRARY_FIXED_BUILDER", "V01@RUN1"),
                               ("PROCEDURE_SELECTOR", "V01@RUN1"), ("SEARCH_ORDER_SELECTOR", "S19@RUN3")])
        self.assertEqual(sorted(set(got.values())), ["NEGATIVE", "POSITIVE"])

    def test_no_ruler_tried_for_the_strong_claim_answered_the_kit(self):
        want = {("STRONG", "V01@RUN1"): FAIL, ("STRONG", "S19@RUN2"): FAIL, ("STRONG", "S19@RUN3"): FAIL,
                ("BITS", "BITS@KEYS"): PASS, ("BITS_TWO_BOUNDARIES", "BITS@TWO"): UNQUALIFIED,
                ("COMBINATION", "BITS@PAIRS"): UNQUALIFIED, ("REUSE", "S19@RUN2"): UNQUALIFIED}
        for (claim, setting), verdict in want.items():
            self.assertEqual(audits.ruler_status(claim, setting, meta.COUNTERFEIT).verdict, verdict, (claim, setting))
        bits = audits.ruler_status("BITS", "BITS@KEYS", meta.COUNTERFEIT)
        self.assertEqual(bits.detail, {"answered": {"POSITIVE": 4, "NEGATIVE": 5}})

    def test_a_receipt_is_read_for_its_numbers_and_not_for_a_label(self):
        with tempfile.TemporaryDirectory() as d:
            folder = pathlib.Path(d)
            files = {"v.json": {"result": {"v01_verdict": {"A": {"x": "PASS", "y": "PASS"}, "B": {"x": "FAIL"},
                                                           "C": {"x": "PASS", "y": "FAIL"}}}},
                     "c.json": {"cells": {"A": {"verdict": "PASS"}, "B": {"verdict": "FAIL"},
                                          "C": {"verdict": "SOMETHING"}}},
                     "k.json": {"cells": {k: {"certified_bits_carried": b} for k, b in
                                          (("A", 2.0), ("B", 0), ("C", 5.0), ("D", 5.0))},
                                "verdicts": {"A": "ANY_LABEL", "B": "CONSTRUCTED", "C": "INHERITED_OR_LEAK",
                                             "D": "RULER_NOT_APPLICABLE"}}}
            for name, data in files.items():
                (folder / name).write_text(json.dumps(data), encoding="ascii")
            (folder / "broken.json").write_text("not json", encoding="ascii")

            def got(name, kind, keys):
                return [audits.returned(folder, (name, kind, k)) for k in keys]

            self.assertEqual(got("v.json", "v01", "ABC"), ["POSITIVE", "NEGATIVE", "MIXED"])
            self.assertEqual(got("c.json", "cell", "ABCZ"), ["POSITIVE", "NEGATIVE", None, None])
            self.assertEqual(got("k.json", "keys", "ABCD"), ["POSITIVE", "NEGATIVE", "NEGATIVE", "NEGATIVE"])
            self.assertEqual(got("broken.json", "cell", "A") + got("absent.json", "cell", "A"), [None, None])
            runs = [("M1", "S", ("v.json", "v01", "A"), {"X": "POSITIVE"}),
                    ("M2", "S", ("v.json", "v01", "B"), {"X": "NEGATIVE"})]
            self.assertEqual(audits.ruler_status("X", "S", folder, runs, {}).verdict, PASS)
            mixed = runs + [("M3", "S", ("v.json", "v01", "C"), {"X": "NEGATIVE"})]
            r = audits.ruler_status("X", "S", folder, mixed, {})
            self.assertEqual(r.verdict, FAIL)
            self.assertIn("M3: FAIL (registered NEGATIVE, the ruler returned MIXED)", r.reason)
            # a member run here and at another setting too is not counted as missing here
            twice = runs + [("M1", "T", ("v.json", "v01", "A"), {"X": "POSITIVE"})]
            self.assertEqual(audits.ruler_status("X", "S", folder, twice, {}).verdict, PASS)
            there = audits.ruler_status("X", "T", folder, twice, {})
            self.assertEqual(there.verdict, UNQUALIFIED)
            self.assertIn("built, and not run at this setting: M2", there.reason)


class Claims(unittest.TestCase):
    def test_a_claim_goes_down_when_a_facet_is_withdrawn(self):
        c = meta.claim()
        self.assertEqual(claims.level(c), 2)
        c["facets"]["custody"]["verdict"] = FAIL
        self.assertEqual(claims.level(c), 1)
        c["facets"]["detection"]["verdict"] = UNQUALIFIED
        self.assertEqual(claims.level(c), 0)

    def test_levels_three_and_four_need_their_own_facets(self):
        self.assertEqual([claims.level(meta.claim(level=n)) for n in (1, 2, 3, 4)], [1, 2, 3, 4])
        top = meta.claim(level=4)
        top["facets"]["custody"]["verdict"] = FAIL
        self.assertEqual(claims.level(top), 1)              # a higher level never stands on a lower one that fell

    def test_a_structure_claim_without_an_exact_bound_stops_at_l1(self):
        self.assertEqual(claims.level(meta.claim("TRANSFER", exact_null=UNQUALIFIED)), 1)

    def test_a_quoted_claim_carries_its_class_and_setting_and_says_why_it_stands_no_higher(self):
        self.assertEqual(claims.render(meta.claim()).reason,
                         "EFFECT, L2 (L3 withheld: reproduced: BLOCKED (absent)), cell REGISTER/RETAIN-1/designed; "
                         "excludes: policies that carry nothing across the gap; setting: alpha = 1e-6; episodes = 64; "
                         "gap = 6")
        low = claims.render(meta.claim(demand=FAIL)).reason
        self.assertIn("L0 (L1 withheld: demand: FAIL)", low)

    def test_every_kind_needs_its_own_facets(self):
        for kind, facets in meta.KIND_FACETS.items():
            self.assertEqual(claims.promote(meta.claim(kind), 1).verdict, PASS, kind)
            for facet in facets:
                self.assertEqual(claims.promote(meta.claim(kind, drop=facet), 1).verdict, BLOCKED, (kind, facet))
        self.assertIsNone(claims.required({"kind": "STRUCTURE"}, 1))

    def test_every_level_needs_its_own_facets(self):
        for facet in meta.FACETS[1]:
            self.assertEqual(claims.promote(meta.claim(drop=facet), 1).verdict, BLOCKED, facet)
        for facet in meta.FACETS[2]:
            self.assertEqual(claims.promote(meta.claim(drop=facet), 2).verdict, BLOCKED, facet)
            self.assertEqual(claims.promote(meta.claim(drop=facet), 1).verdict, PASS, facet)

    def test_the_hash_of_a_setting_does_not_depend_on_the_order_it_was_typed_in(self):
        self.assertEqual(claims.setting_hash({"gap": 6, "alpha": "1e-6"}), claims.setting_hash({"alpha": "1e-6", "gap": 6}))
        c = meta.claim()
        turned = dict(c, setting=dict(reversed(list(c["setting"].items()))))
        self.assertEqual(claims.render(turned).verdict, PASS)

    def test_a_facet_is_blocked_three_ways(self):
        c = meta.claim()
        self.assertEqual(claims.facet(c, "nothing").reason, "absent")
        self.assertEqual(claims.facet(dict(c, facets={"x": {"verdict": "passed", "source": "s"}}), "x").reason,
                         "no verdict")
        for source in (None, "", "  ", 7):
            self.assertEqual(claims.facet(dict(c, facets={"x": {"verdict": PASS, "source": source}}), "x").reason,
                             "no source")

    def test_custody_thresholds(self):
        check = claims.check_custody
        self.assertEqual(check(meta.custody()).verdict, PASS)
        self.assertEqual(check(meta.custody(rule_fixed_at=20)).verdict, FAIL)
        self.assertEqual(check(meta.custody(rule_fixed_at=19)).verdict, PASS)
        self.assertEqual(check(meta.custody(tuning_evaluations=50)).verdict, PASS)
        self.assertEqual(check(meta.custody(tuning_evaluations=51)).verdict, FAIL)
        self.assertEqual((claims.CUSTODY_CLAIMS, claims.SELECTED_ON), (("NEW_FAMILY", "NEW_SEEDS"),
                                                                       ("discovery", "confirmation")))
        for part in ("seeds", "panel_sha256", "generator_sha256"):
            for which in ("discovery", "confirmation"):
                self.assertEqual(check(meta.custody(**{which: meta.side(**{part: None})})).verdict, BLOCKED,
                                 (which, part))


class Ladder(unittest.TestCase):
    """Exploratory. What a certificate at a boundary of the two key worlds certifies."""

    @classmethod
    def setUpClass(cls):
        cls.s = ladder.survey(60)
        cls.pairs = ladder.survey_pairs(60)

    def test_the_exact_bound_and_the_certificate(self):
        self.assertEqual("%.4f" % ladder.H16, "3.3807")
        self.assertEqual("%.4f" % ladder.certificate([4.0] * 300)["threshold"], "5.8086")
        self.assertEqual(ladder.certificate([5.80] * 300)["answer"], "NOT_SHOWN")
        self.assertEqual(ladder.certificate([5.81] * 300)["answer"], "CARRIED")

    def test_an_organism_that_carries_nothing_is_not_certified(self):
        for variant in ("ROTATION", "OFFSET"):
            row = self.s["%s/ELIM" % variant]
            self.assertEqual((row["across_families"]["answer"], row["across_epochs"]["answer"]),
                             ("NOT_SHOWN", "NOT_SHOWN"))

    def test_a_cache_with_a_fixed_re_indexer_is_certified_at_both_boundaries(self):
        row = self.s["ROTATION/CACHE"]
        self.assertEqual((row["across_families"]["answer"], row["across_epochs"]["answer"]), ("CARRIED", "CARRIED"))
        self.assertGreater(row["across_epochs"]["mean"], 13.0)

    def test_a_smaller_re_indexer_is_certified_where_the_epoch_object_adds_to_the_family_object(self):
        self.assertEqual(self.s["OFFSET/KEEPER"]["across_epochs"]["answer"], "CARRIED")
        row = self.s["ROTATION/KEEPER"]["across_epochs"]       # above the bound, and not shown at 60 lives
        self.assertEqual(row["answer"], "NOT_SHOWN")
        self.assertTrue(ladder.H16 < row["mean"] < row["threshold"])

    def test_an_organism_told_to_forget_is_not_certified_across_epochs(self):
        row = self.s["ROTATION/FORGETFUL"]
        self.assertEqual((row["across_families"]["answer"], row["across_epochs"]["answer"]), ("CARRIED", "NOT_SHOWN"))

    def test_the_ninth_map_is_three_shown_tables_combined(self):
        self.assertEqual((len(ladder.SHOWN), ladder.UNSEEN), (8, (2, 2)))
        self.assertNotIn(ladder.UNSEEN, ladder.SHOWN)
        first = [sorted(range(16), key=lambda i, j=j: stats.khash(1, j, i)) for j in range(3)]
        second = [sorted(range(16), key=lambda i, k=k: stats.khash(2, k, i)) for k in range(3)]

        def family(j, k):
            return [second[k][first[j][x]] for x in range(16)]

        self.assertEqual(ladder.compose(family(1, 2), family(1, 1), family(2, 1)), family(2, 2))
        self.assertNotEqual(ladder.compose(family(1, 2), family(1, 1), family(2, 0)), family(2, 2))

    def test_on_the_unseen_pair_a_label_blind_cache_of_recombinations_beats_the_bound_too(self):
        got = {k: v["answer"] for k, v in self.pairs.items()}
        self.assertEqual(got, {
            "COMPOSER": "COMBINED", "SCHEMA_CACHE": "COMBINED", "ELIM": "NOT_SHOWN", "TABLE_CACHE": "NOT_SHOWN",
            "TWO_TABLES": "NOT_SHOWN", "REPEAT_WATCHER": "NOT_SHOWN",
            "HIDER, one key reused in both arms": "KEY_REUSED", "SANDBAGGER, one key reused in both arms": "KEY_REUSED",
            "REPEAT_WATCHER, the life's key reused and the control's drawn afresh": "KEY_REUSED"})
        self.assertEqual(self.pairs["COMPOSER"]["ninth_pair"]["mean"], 16.0)
        self.assertGreater(self.pairs["SCHEMA_CACHE"]["ninth_pair"]["mean"], 13.0)

    def test_in_the_control_every_organism_in_a_sound_harness_is_at_the_bound(self):
        for name in sorted(ladder.PAIR_ORGANISMS):
            self.assertEqual(self.pairs[name]["control"]["answer"], "NOT_SHOWN", name)
            self.assertLess(self.pairs[name]["control"]["mean"], 4.0, name)
            self.assertTrue(self.pairs[name]["keys_fresh"], name)

    def test_the_control_catches_a_leak_that_reaches_both_arms_and_misses_one_that_reaches_one(self):
        arms = {k: v["arms_alone"] for k, v in self.pairs.items() if not v["keys_fresh"]}
        self.assertEqual(arms, {
            "HIDER, one key reused in both arms": "NOT_FROM_THIS_LIFE",
            "SANDBAGGER, one key reused in both arms": "NOT_FROM_THIS_LIFE",
            "REPEAT_WATCHER, the life's key reused and the control's drawn afresh": "COMBINED"})

    def test_custody_of_the_keys(self):
        fresh, reused = [], []
        ladder.run_pairs(ladder.PairElim, 5, custody=fresh)
        ladder.run_pairs(ladder.PairElim, 5, reuse="own", custody=reused)
        self.assertEqual((len(set(fresh)), len(set(reused))), (5, 1))
        self.assertEqual([ladder.keys_fresh(fresh), ladder.keys_fresh(reused), ladder.keys_fresh([])], [True, False, False])

    def test_what_the_custody_check_and_the_two_arms_say_together(self):
        yes, no = {"answer": "CARRIED"}, {"answer": "NOT_SHOWN"}
        self.assertEqual([ladder.pair_answer(yes, no), ladder.pair_answer(no, no), ladder.pair_answer(yes, yes),
                          ladder.pair_answer(no, yes), ladder.pair_answer(yes, no, fresh=False)],
                         ["COMBINED", "NOT_SHOWN", "NOT_FROM_THIS_LIFE", "NOT_FROM_THIS_LIFE", "KEY_REUSED"])


if __name__ == "__main__":
    unittest.main()
