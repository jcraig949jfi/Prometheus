"""C-016-T030 tests (unittest; harry1 has no pytest). Run from the repo root:
    python -m unittest rso.ensorain.tests.test_assay -v
Development seeds only (16_300_xxx, PREREGISTRATION.md s6). No confirmatory seed is used here."""
import copy
import unittest
from fractions import Fraction
from unittest import mock

import numpy as np

from ensorain.wtp5 import tape
from rso.ensorain import analysis, assay, subjects

DEV = [16_300_001 + i for i in range(12)]


class Endpoint(unittest.TestCase):
    def test_counts_are_integers_and_recompute_native_accuracy(self):
        row = assay.life(subjects.reference(), "full", DEV[0])
        for k in ("sw", "c_pre", "n_pre", "c_late", "n_late", "c5", "n5", "n_carried"):
            self.assertIsInstance(row[k], int, k)
        self.assertTrue(row["recompute_ok"])           # integer counts reproduce tape.lifetime's own floats
        self.assertGreater(row["n_late"], 0)

    def test_frozen_reference_scores_zero_late_and_full_pre(self):
        row = assay.life(subjects.reference(), "frozen", DEV[1])
        self.assertEqual(row["c_late"], 0)
        self.assertEqual(row["c_pre"], row["n_pre"])

    def test_rows_are_canonical(self):
        rows = assay.run({"reference": subjects.reference()}, ("full",), DEV[:2])
        self.assertEqual(len(assay.rows_sha256(rows)), 64)  # receipt-canonical refuses floats


class DeclaredMemory(unittest.TestCase):
    def test_real_lives_pass(self):
        for arm in ("full", "frozen", "shuffle", "newlife"):
            self.assertTrue(assay.life(subjects.reference(), arm, DEV[2])["memory_ok"], arm)

    def test_leak_at_non_plastic_key_is_flagged(self):
        real = tape.lifetime

        def leaky(g, *a, **kw):
            out = real(g, *a, **kw)
            out["learned"]["nodes"][1]["i"] = 3          # a non-plastic field changed across the life
            return out
        with mock.patch.object(tape, "lifetime", leaky):
            self.assertFalse(assay.life(subjects.reference(), "full", DEV[3])["memory_ok"])

    def test_working_state_carried_into_a_block_is_flagged(self):
        real = tape._run

        def carry(g, obs, K, T, S, z, *a):
            return real(g, obs, K, T, S, z + 1.0, *a)
        with mock.patch.object(tape, "_run", carry):
            self.assertFalse(assay.life(subjects.reference(), "full", DEV[3])["memory_ok"])

    def test_frozen_life_may_not_change_any_parameter(self):
        real = tape.lifetime

        def drift(g, *a, **kw):
            out = real(g, *a, **kw)
            out["learned"]["nodes"][4]["v"] = out["learned"]["nodes"][4]["v"] * 0 - 0.2
            return out
        with mock.patch.object(tape, "lifetime", drift):
            self.assertFalse(assay.life(subjects.reference(), "frozen", DEV[3])["memory_ok"])


class Subjects(unittest.TestCase):
    def test_smugglers_read_the_post_switch_sign_from_a_constant(self):
        for g in (subjects.smuggler(), subjects.smuggler_decorative()):
            row = assay.life(g, "full", DEV[4])
            self.assertEqual(row["c_late"], row["n_late"])  # perfect on the endpoint window ...
            self.assertEqual(row["c_pre"], 0)               # ... because it never knew the pre-switch law

    def test_genome_json_round_trip(self):
        g = subjects.reference()
        self.assertEqual(tape.ghash(subjects.from_json(subjects.to_json(g))), tape.ghash(g))

    def test_seed_partition_disjoint_from_registered(self):
        self.assertEqual(subjects.seed_conflicts(), [])


class Analysis(unittest.TestCase):
    def test_sign_test_exact(self):
        self.assertEqual(analysis.sign_p(10, 0), Fraction(1, 1024))
        self.assertEqual(analysis.sign_p(0, 0), Fraction(1))

    def test_late_comparison_is_exact_rational(self):
        a = dict(c_late=1, n_late=3)
        b = dict(c_late=2, n_late=6)
        self.assertEqual(analysis.cmp_late(a, b), 0)

    def test_smuggler_refused_reference_detected_on_dev(self):
        subs = {"reference": subjects.reference(), "smuggler": subjects.smuggler(),
                "smuggler_decorative": subjects.smuggler_decorative()}
        rows = assay.run(subs, assay.ARMS, DEV)
        v = analysis.verdicts(rows, n_required=len(DEV), alpha=Fraction(1, 20))
        self.assertEqual(v["smuggler"]["verdict"], "REFUSED_FIXED_PRIOR")
        self.assertEqual(v["smuggler_decorative"]["verdict"], "REFUSED_FIXED_PRIOR")
        self.assertTrue(v["reference"]["G_PRE"])

    def test_frozen_reference_is_not_a_revision(self):
        rows = assay.run({"memoryless_plus": subjects.memoryless(+1)}, assay.ARMS, DEV[:8])
        v = analysis.verdicts(rows, n_required=8, alpha=Fraction(1, 20))
        self.assertNotIn(v["memoryless_plus"]["verdict"], ("REVISION_HISTORY_DEPENDENT", "REVISION_NOT_HISTORY_DEPENDENT"))

    def test_wrong_n_refused(self):
        rows = assay.run({"reference": subjects.reference()}, assay.ARMS, DEV[:4])
        with self.assertRaises(analysis.AnalysisError):
            analysis.verdicts(rows, n_required=6, alpha=Fraction(1, 20))


class Freeze(unittest.TestCase):
    def test_confirm_refuses_on_changed_bytes(self):
        from rso.ensorain import freeze
        with mock.patch.object(freeze, "file_sha", lambda p, root=None: "0" * 64):
            self.assertTrue(freeze.mismatches())


if __name__ == "__main__":
    unittest.main()
