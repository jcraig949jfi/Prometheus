"""Each test replays, in miniature, a control that could not fail in a past campaign, and shows the check catches it.
The fixtures are synthetic: they reproduce the LOGIC of the historical defect, not the engines."""
import unittest

from rso.qualify import falsifiable as F

CLASSES = ("ENDO", "EXT", "ENV", "INS")


def exact_rule(max_wrong):
    return lambda preds, truths: sum(p != t for p, t in zip(preds, truths)) <= max_wrong


def per_class_rule(max_wrong):
    """Q1-style: every class present in the truths must be classed within max_wrong."""
    def rule(preds, truths):
        return all(sum(p != t for p, t in zip(preds, truths) if t == c) <= max_wrong for c in set(truths))
    return rule


class Z80Baselines(unittest.TestCase):
    """C-017-T040: b1 / b2 had no ENV output, so 'each baseline must fail Q1' was satisfied by construction."""
    cases = [({"phys": "ENDO", "copier": True}, "ENDO"), ({"phys": "EXT", "copier": False}, "EXT"),
             ({"phys": "ENDO", "copier": True, "kept": True}, "ENV"), ({"phys": "ENDO", "copier": False}, "INS")]

    def b1(self, x):            # the label reader: physics label, never ENV
        if x["phys"] == "EXT":
            return "EXT"
        return "ENDO" if x["copier"] else "INS"

    def test_label_reader_cannot_emit_env(self):
        self.assertEqual(F.cannot_emit(self.b1, [x for x, _ in self.cases], CLASSES), ["ENV"])

    def test_audit_blocks_a_baseline_that_cannot_discriminate_its_registered_class(self):
        rec = F.audit("b1", self.b1, per_class_rule(0), self.cases, CLASSES, must_discriminate=("ENV",),
                      near_misses=[({"phys": "ENDO", "copier": True, "kept": True}, "ENV", "a kept-byte copier")])
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["cannot_discriminate"], ["ENV"])


class Z80Origin(unittest.TestCase):
    """C-017-T040 S2: 'always INSERTED' passed Q2 for every outcome (w_max >= the number of ARISEN rows)."""

    def test_constant_inserted_passes_a_loose_origin_rule(self):
        cases = [({}, "INSERTED")] * 240 + [({}, "ARISEN")] * 24
        self.assertEqual(F.constant_passes(exact_rule(33), cases, ("INSERTED", "ARISEN")), ["INSERTED"])

    def test_a_rule_tight_enough_for_the_minority_class_is_not_passed_by_a_constant(self):
        cases = [({}, "INSERTED")] * 240 + [({}, "ARISEN")] * 24
        self.assertEqual(F.constant_passes(per_class_rule(3), cases, ("INSERTED", "ARISEN")), [])


class RecipeLookupTable(unittest.TestCase):
    """C-017-T041 A2: a recipe table keyed on the registered arm IS the ground-truth table."""
    TABLE = {"H_ENDO": "ENDO", "H_EXT": "EXT", "RECON": "ENV", "CDIST": "ENV"}
    cases = [({"arm": a, "bytes": i}, t) for i, (a, t) in enumerate(TABLE.items())]

    def lookup(self, x):
        return self.TABLE.get(x["arm"], "OTHER")

    def mechanism(self, x):     # reads only the bytes field; here a stand-in that knows the answer by bytes
        return ["ENDO", "EXT", "ENV", "ENV"][x["bytes"]]

    def scrub(self, x):         # remove the answer-bearing field, keep the evidence
        return {"arm": "BLINDED", "bytes": x["bytes"]}

    def test_lookup_table_reads_the_answer(self):
        self.assertEqual(F.reads_answer(self.lookup, self.cases, self.scrub), [0, 1, 2, 3])

    def test_a_detector_that_reads_only_evidence_is_not_flagged(self):
        self.assertEqual(F.reads_answer(self.mechanism, self.cases, self.scrub), [])


class D1DerivedField(unittest.TestCase):
    """C-013 D1 integration: analyze.py counted row['discovery'] and ignored certificate / seeded."""
    rows = [{"hit": True, "seeded": False, "certified": True, "discovery": True},
            {"hit": True, "seeded": False, "certified": True, "discovery": True},
            {"hit": False, "seeded": False, "certified": False, "discovery": False}]

    @staticmethod
    def tamper(rows):
        out = [dict(r) for r in rows]
        out[0]["certified"] = False     # components now say "not a discovery"; the derived field still says it is
        return out

    def test_an_analyzer_that_counts_the_derived_field_is_flagged(self):
        self.assertTrue(F.trusts_derived(lambda rs: sum(r["discovery"] for r in rs), self.rows, self.tamper))

    def test_an_analyzer_that_rederives_is_not_flagged(self):
        rederive = lambda rs: sum(r["hit"] and not r["seeded"] and r["certified"] for r in rs)
        self.assertFalse(F.trusts_derived(rederive, self.rows, self.tamper))


class EnsorainSelfRelative(unittest.TestCase):
    """C-016-T040: K1 vs the subject's own frozen arm was passed by perturbation noise (jitter)."""

    @staticmethod
    def k1_vs_frozen(x):        # 'revises' iff full beats frozen on the late window
        return "REVISES" if x["full_late"] > x["frozen_late"] else "NOT"

    @staticmethod
    def k1_vs_noise_too(x):     # the repaired comparator: must also beat the noise-matched arm
        return "REVISES" if x["full_late"] > max(x["frozen_late"], x["noise_late"]) else "NOT"

    jitter = ({"full_late": 0.42, "frozen_late": 0.0, "noise_late": 0.42}, "NOT", "perturbation noise, no learning")

    def test_the_near_miss_catches_the_self_relative_rule(self):
        self.assertEqual(F.near_miss_rejected(self.k1_vs_frozen, [self.jitter]), [("NOT", "perturbation noise, no learning")])

    def test_the_repaired_rule_rejects_the_near_miss(self):
        self.assertEqual(F.near_miss_rejected(self.k1_vs_noise_too, [self.jitter]), [])

    def test_no_near_miss_is_not_a_pass(self):
        with self.assertRaises(ValueError):
            F.near_miss_rejected(self.k1_vs_noise_too, [])


class OracleAndAudit(unittest.TestCase):
    def test_a_rule_even_the_truth_fails_is_flagged(self):
        impossible = lambda preds, truths: False
        self.assertTrue(F.oracle_fails(impossible, [({}, "A")]))

    def test_a_sound_control_audits_ok(self):
        cases = [({"v": 0}, "A"), ({"v": 1}, "B")]
        det = lambda x: "AB"[x["v"]]
        rec = F.audit("sound", det, per_class_rule(0), cases, ("A", "B"), must_discriminate=("A", "B"),
                      scrub=lambda x: dict(x), near_misses=[({"v": 1}, "B", "looks like A")])
        self.assertTrue(rec["ok"], rec)

    def test_audit_without_a_registered_near_miss_is_not_ok(self):
        cases = [({"v": 0}, "A"), ({"v": 1}, "B")]
        rec = F.audit("no-nm", lambda x: "AB"[x["v"]], per_class_rule(0), cases, ("A", "B"))
        self.assertFalse(rec["ok"])


if __name__ == "__main__":
    unittest.main()
