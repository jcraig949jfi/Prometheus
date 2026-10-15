"""C-019-T011 RED-first tests: every registered target, every attack, with the verdict the earlier generation's record predicts.
    python -m unittest rso.adversary.tests.test_targets -v        (~3 min: the Aether analyser is run for real on scratch copies)
Known-answer targets: C-017 Z80 six-shard fixture (rso.completeness), C-018 Aether confirmatory runs (rso.aether.confirm),
C-016/C-017 falsifiability miniatures (rso.qualify), C-013 D1 ledger (rso.reach.analyze). All READ-ONLY: the Aether runs are
copied to a temp dir; the Z80 shards are loaded into memory."""
import unittest

from rso.adversary import attacks as X, core as K, targets as T


def by(rows, attack, variant=None):
    out = [r for r in rows if r["attack"] == attack and (variant is None or r["variant"] == variant)]
    assert out, (attack, variant, [(r["attack"], r["variant"]) for r in rows])
    return out


class Common:
    NAME = None
    rows = None

    @classmethod
    def setUpClass(cls):
        cls.rows = K.run_target(cls.NAME)

    def test_every_attack_is_accounted_for(self):
        self.assertEqual({r["attack"] for r in self.rows}, set(X.ATTACKS))

    def test_every_executed_attack_fired(self):
        for r in self.rows:
            if r["verdict"] != K.NOT_APPLICABLE:
                self.assertTrue(r["fired"], r)
                self.assertNotEqual(r["verdict"], K.VACUOUS, r)

    def test_no_counterfeit_survived(self):
        self.assertEqual([r for r in self.rows if r["verdict"] == K.SURVIVED], [])


class Z80Completeness(Common, unittest.TestCase):
    NAME = "z80_completeness"

    def test_drop_is_incomplete(self):
        r = by(self.rows, "DROP")[0]
        self.assertEqual(r["verdict"], K.REJECTED)
        self.assertIn("INCOMPLETE", r["detail"])

    def test_every_shard_dropped_is_incomplete(self):
        self.assertEqual(len(by(self.rows, "DROP")), 6)

    def test_duplicate_shard_is_refused(self):
        r = by(self.rows, "DUPLICATE", "shard")[0]
        self.assertEqual(r["verdict"], K.REJECTED)
        self.assertIn("REFUSED", r["detail"])
        self.assertIn("DUPLICATE", r["detail"])

    def test_duplicate_row_preserving_count_is_refused(self):
        r = by(self.rows, "DUPLICATE", "row")[0]
        self.assertEqual(r["verdict"], K.REJECTED)
        self.assertIn("REFUSED", r["detail"])

    def test_rewritten_derived_field_with_rebound_hashes_is_refused(self):
        r = by(self.rows, "REWRITE_DERIVED")[0]
        self.assertEqual(r["verdict"], K.REJECTED)
        self.assertIn("REFUSED", r["detail"])

    def test_scrubbed_answer_field_is_refused(self):
        self.assertEqual(by(self.rows, "SCRUB_ANSWER")[0]["verdict"], K.REJECTED)

    def test_constant_is_not_applicable_with_a_reason(self):
        r = by(self.rows, "CONSTANT")[0]
        self.assertEqual(r["verdict"], K.NOT_APPLICABLE)
        self.assertTrue(r["detail"])


class AetherConfirm(Common, unittest.TestCase):
    NAME = "aether_confirm"

    def test_drop_shard_and_drop_law_are_incomplete(self):
        for v in ("shard", "law-V1"):
            r = by(self.rows, "DROP", v)[0]
            self.assertEqual(r["verdict"], K.REJECTED, r)
            self.assertIn("INCOMPLETE", r["detail"])

    def test_duplicate_unit_preserving_count_is_refused(self):
        r = by(self.rows, "DUPLICATE")[0]
        self.assertEqual(r["verdict"], K.REJECTED)

    def test_rewrite_of_a_non_sampled_clamp_array_is_the_recorded_limitation_R1c(self):
        r = by(self.rows, "REWRITE_DERIVED", "clamp-non-sampled-8201")[0]
        self.assertEqual((r["verdict"], r["limitation"]), (K.LIMITATION, "C018-R1c"))
        self.assertIn("CONFIRMED -> NONSPECIFIC", r["detail"])             # the counterfeit changed the class, no check failed

    def test_rewrite_of_a_sampled_clamp_array_is_rejected_by_the_replay(self):
        r = by(self.rows, "REWRITE_DERIVED", "clamp-sampled-8228")[0]
        self.assertEqual(r["verdict"], K.REJECTED)
        self.assertIn("native replay differs", r["detail"])

    def test_scrubbed_tree_and_corrupted_B_are_rejected(self):
        for v in ("tree-removed", "B-corrupted"):
            self.assertEqual(by(self.rows, "SCRUB_ANSWER", v)[0]["verdict"], K.REJECTED, v)


class QualifyFalsifiable(Common, unittest.TestCase):
    NAME = "qualify_falsifiable"

    def test_constant_classifier_is_flagged(self):
        for r in by(self.rows, "CONSTANT"):
            self.assertEqual(r["verdict"], K.REJECTED, r)
        self.assertIn("constant_passes", " ".join(r["detail"] for r in by(self.rows, "CONSTANT")))

    def test_answer_reading_detector_is_flagged_by_the_scrub(self):
        r = by(self.rows, "SCRUB_ANSWER")[0]
        self.assertEqual(r["verdict"], K.REJECTED)
        self.assertIn("reads_answer", r["detail"])

    def test_dropping_the_registered_near_misses_leaves_the_audit_not_ok(self):
        self.assertEqual(by(self.rows, "DROP")[0]["verdict"], K.REJECTED)


class ReachD1(Common, unittest.TestCase):
    NAME = "reach_d1_analyze"

    def test_derived_field_tamper_is_the_recorded_limitation(self):
        r = by(self.rows, "REWRITE_DERIVED")[0]
        self.assertEqual((r["verdict"], r["limitation"]), (K.LIMITATION, "C013-D1-trusts-derived"))

    def test_dropping_a_cell_row_leaves_an_incomplete_round_and_no_contrast_is_read(self):
        r = by(self.rows, "DROP")[0]
        self.assertEqual(r["verdict"], K.REJECTED)


class Registry(unittest.TestCase):
    def test_targets_cover_at_least_three_previous_generations(self):
        self.assertGreaterEqual(len({t["campaign"] for t in T.TARGETS.values()}), 3)

    def test_every_attack_has_an_executed_variant_somewhere(self):
        for a in X.ATTACKS:
            self.assertTrue(any(any(v[0] == a for v in t["variants"]) for t in T.TARGETS.values()), a)

    def test_unknown_target_is_refused(self):
        with self.assertRaises(KeyError):
            K.run_target("nope")


if __name__ == "__main__":
    unittest.main()
