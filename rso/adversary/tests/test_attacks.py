"""C-019-T011 RED-first tests: the five attacks as plain functions, and the runner's verdict logic (rso/adversary/README.md).
    python -m unittest rso.adversary.tests.test_attacks -v
Every attack must FIRE (change its input), and a runner that cannot tell a refusal from a counterfeit verdict is worthless:
the classification tests use synthetic targets so SURVIVED / VACUOUS / unregistered-LIMITATION are exercised, not assumed."""
import copy
import unittest

import numpy as np

from rso.adversary import attacks as X, core as K, limitations as L


class AttackFunctions(unittest.TestCase):
    def test_five_attacks_named(self):
        self.assertEqual(X.ATTACKS, ("DROP", "DUPLICATE", "REWRITE_DERIVED", "CONSTANT", "SCRUB_ANSWER"))

    def test_drop_removes_one_and_leaves_input_alone(self):
        items = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
        before = copy.deepcopy(items)
        out = X.drop(items, 1)
        self.assertEqual([i["id"] for i in out], ["a", "c"])
        self.assertEqual(items, before)

    def test_drop_of_nothing_is_refused_not_silent(self):
        with self.assertRaises(ValueError):
            X.drop([], 0)

    def test_duplicate_preserves_the_count(self):
        rows = [{"seed": 1}, {"seed": 2}, {"seed": 3}]
        out = X.duplicate(rows, src=0, dst=2)
        self.assertEqual(len(out), len(rows))
        self.assertEqual(out[2], out[0])
        self.assertNotEqual(out, rows)

    def test_duplicate_onto_itself_is_refused(self):
        with self.assertRaises(ValueError):
            X.duplicate([{"seed": 1}, {"seed": 2}], src=1, dst=1)

    def test_duplicate_of_identical_rows_is_refused_as_vacuous(self):
        with self.assertRaises(ValueError):
            X.duplicate([{"seed": 1}, {"seed": 1}], src=0, dst=1)

    def test_rewrite_derived_rewrites_then_restores_the_invariant(self):
        obj = {"parts": [1, 2, 3], "total": 6}
        out = X.rewrite_derived(obj, rewrite=lambda o: o["parts"].__setitem__(0, 4),
                                rebind=lambda o: o.__setitem__("total", sum(o["parts"])))
        self.assertEqual(out, {"parts": [4, 2, 3], "total": 9})                 # invariant "total == sum(parts)" still holds
        self.assertEqual(obj, {"parts": [1, 2, 3], "total": 6})

    def test_rewrite_derived_without_rebind_leaves_a_visible_inconsistency(self):
        out = X.rewrite_derived({"parts": [1, 2], "total": 3}, rewrite=lambda o: o["parts"].append(5))
        self.assertNotEqual(sum(out["parts"]), out["total"])

    def test_constant_detector_ignores_its_input(self):
        d = X.constant_detector("X")
        self.assertEqual({d(1), d({"a": 2}), d(None)}, {"X"})

    def test_scrub_remove_and_corrupt(self):
        x = {"arm": "H_ENDO", "bytes": 3}
        self.assertEqual(X.scrub_answer(x, ["arm"]), {"bytes": 3})
        c = X.scrub_answer(x, ["arm"], mode="corrupt")
        self.assertIn("arm", c)
        self.assertNotEqual(c["arm"], "H_ENDO")
        self.assertEqual(x, {"arm": "H_ENDO", "bytes": 3})

    def test_scrub_of_an_absent_field_is_refused_as_vacuous(self):
        with self.assertRaises(ValueError):
            X.scrub_answer({"bytes": 3}, ["arm"])

    def test_fingerprint_sees_arrays_dicts_and_order(self):
        a = {"k": np.arange(4, dtype=np.int16), "z": [1, 2]}
        self.assertEqual(X.fingerprint(a), X.fingerprint(copy.deepcopy(a)))
        b = copy.deepcopy(a)
        b["k"][0] = 9
        self.assertNotEqual(X.fingerprint(a), X.fingerprint(b))
        self.assertNotEqual(X.fingerprint({"z": [1, 2]}), X.fingerprint({"z": [2, 1]}))


class Classification(unittest.TestCase):
    """The runner's three verdicts (and the two refusals to pass silently)."""

    def test_refusal_is_rejected(self):
        r = K.judge(accepted=False, refusal="INCOMPLETE missing [S.0]", fired=True)
        self.assertEqual((r.verdict, r.detail), (K.REJECTED, "INCOMPLETE missing [S.0]"))

    def test_accepted_counterfeit_is_survived(self):
        self.assertEqual(K.judge(accepted=True, refusal="", fired=True).verdict, K.SURVIVED)

    def test_accepted_with_a_registered_limitation_is_limitation_with_its_id(self):
        r = K.judge(accepted=True, refusal="", fired=True, limitation="C018-R1c")
        self.assertEqual((r.verdict, r.limitation), (K.LIMITATION, "C018-R1c"))

    def test_an_unregistered_limitation_id_is_not_accepted(self):
        r = K.judge(accepted=True, refusal="", fired=True, limitation="C999-made-up")
        self.assertEqual(r.verdict, K.SURVIVED)
        self.assertIn("unregistered", r.detail)

    def test_an_attack_that_changed_nothing_is_vacuous_whatever_the_component_said(self):
        for accepted in (True, False):
            self.assertEqual(K.judge(accepted=accepted, refusal="x", fired=False).verdict, K.VACUOUS)

    def test_exit_codes(self):
        mk = lambda v: {"verdict": v}
        self.assertEqual(K.exit_code([mk(K.REJECTED), mk(K.LIMITATION), mk(K.NOT_APPLICABLE)]), 0)
        self.assertEqual(K.exit_code([mk(K.REJECTED), mk(K.SURVIVED)]), 1)
        self.assertEqual(K.exit_code([mk(K.VACUOUS), mk(K.SURVIVED)]), 2)

    def test_run_variants_catches_a_raising_variant_as_rejected_by_exception(self):
        def boom():
            K.call(lambda: {}["tree"])
        rows = K.run_variants("syn", [("SCRUB_ANSWER", "v", boom)],
                              not_applicable={a: "n/a" for a in X.ATTACKS if a != "SCRUB_ANSWER"})
        row = [r for r in rows if r["attack"] == "SCRUB_ANSWER"][0]
        self.assertEqual(row["verdict"], K.REJECTED)
        self.assertIn("raised KeyError", row["detail"])

    def test_a_kit_bug_is_an_error_never_a_rejection(self):
        def kit_bug():
            raise PermissionError("harness could not open its own scratch file")
        rows = K.run_variants("syn", [("SCRUB_ANSWER", "v", kit_bug)],
                              not_applicable={a: "n/a" for a in X.ATTACKS if a != "SCRUB_ANSWER"})
        row = [r for r in rows if r["attack"] == "SCRUB_ANSWER"][0]
        self.assertEqual(row["verdict"], K.ERROR)
        self.assertEqual(K.exit_code(rows), 2)

    def test_run_variants_records_every_attack_even_when_not_applicable(self):
        rows = K.run_variants("syn", [("DROP", "v", lambda: K.judge(False, "r", True))],
                              not_applicable={a: "no such thing" for a in X.ATTACKS if a != "DROP"})
        self.assertEqual({r["attack"] for r in rows}, set(X.ATTACKS))
        self.assertEqual(sum(r["verdict"] == K.NOT_APPLICABLE for r in rows), 4)

    def test_a_target_that_covers_neither_an_attack_nor_a_reason_is_refused(self):
        with self.assertRaises(ValueError):
            K.run_variants("syn", [("DROP", "v", lambda: K.judge(False, "r", True))])


class LimitationRegistry(unittest.TestCase):
    def test_ids_resolve_to_recorded_text(self):
        self.assertIn("C018-R1c", L.LIMITATIONS)
        self.assertIn("C013-D1-trusts-derived", L.LIMITATIONS)
        for lid in L.LIMITATIONS:
            self.assertEqual(L.problems(lid), [], lid)

    def test_a_marker_that_is_not_in_the_source_is_a_problem(self):
        L.LIMITATIONS["__t"] = {"source": "rso/aether/RESULT.md", "marker": "no such marker xyzzy", "summary": "t"}
        try:
            self.assertTrue(L.problems("__t"))
        finally:
            del L.LIMITATIONS["__t"]


if __name__ == "__main__":
    unittest.main()
