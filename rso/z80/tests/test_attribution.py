"""C-017-T030 behavioural tests (unittest; harry1 has no pytest). Run from the repo root:
    python -m unittest rso.z80.tests.test_attribution -v
Development seeds only (17_030_xxx, PREREGISTRATION.md s6). No confirmatory seed (17_050_xxx) is used here."""
import copy
import unittest
from fractions import Fraction

from archaeon.z80atlas import engine as E, vm
from rso.z80 import analysis, assay, observe, subjects as S

DEV = [17_030_901 + i for i in range(6)]          # dev partition, arm slot 0 offset 900+: never used by the dev check


def short(name, epochs):
    return S.spec(S.ARM[name], epochs=epochs)


class Replay(unittest.TestCase):
    """observe.replay re-implements engine.run's population loop for the declared subset; it must equal the engine."""
    def check(self, name, epochs, seed):
        spec = short(name, epochs)
        out = E.run(spec, seed)
        obs = observe.replay(spec, seed)
        self.assertEqual([(o["cell"], o["tape"], o["generation"]) for o in out["final_population"]],
                         [(o["cell"], o["tape"].hex(), o["gen"]) for o in obs["final"]], name)
        self.assertEqual((out["signals"]["births"], out["signals"]["births_endo"]), (obs["births"], obs["births_endo"]), name)

    def test_endogenous_transplant(self):
        self.check("H_ENDO_GATED", 25, DEV[0])

    def test_external_tournament(self):
        self.check("H_EXT_GATED", 25, DEV[1])

    def test_seeded_path_and_random_fill(self):
        self.check("SEEDED_ENDO_GATED", 25, DEV[2])

    def test_implicit_survival_and_reconstructor(self):
        self.check("H_ENDO_IMPL", 20, DEV[3])
        self.check("RECON_ENDO_GATED", 20, DEV[3])

    def test_unsupported_spec_is_refused_not_replayed(self):
        spec = short("H_ENDO_GATED", 5)
        spec["world"] = dict(spec["world"], topology="grid_vn")
        self.assertTrue(observe.unsupported(spec))
        self.assertRaises(observe.Unsupported, observe.replay, spec, DEV[0])


class Tags(unittest.TestCase):
    """Per-byte writer tags: I inserted, P written by the parent's own execution, K kept from the target cell,
    R written by the runner, M changed by mutation or copy noise."""
    def test_founders_are_inserted(self):
        obs = observe.replay(short("NH_ENDO_SHORT", 1), DEV[0])
        self.assertTrue(obs["final"])
        self.assertTrue(all(o["tags"] == "I" * S.G for o in obs["final"] if o["gen"] == 0))

    def test_endogenous_child_of_H_is_parent_written(self):
        obs = observe.replay(short("H_ENDO_GATED", 6), DEV[1])
        born = [o for o in obs["final"] if o["gen"] > 0]
        self.assertTrue(born)
        self.assertTrue(all(set(o["tags"]) <= {"P", "M"} for o in born))
        self.assertTrue(any(o["tags"] == "P" * S.G for o in born))

    def test_reconstructor_child_keeps_function_bytes_from_the_target(self):
        obs = observe.replay(short("RECON_ENDO_GATED", 6), DEV[2])
        born = [o for o in obs["final"] if o["gen"] > 0]
        self.assertTrue(born)
        self.assertTrue(all(o["tags"][:3] == "KKK" for o in born if "M" not in o["tags"][:3]))

    def test_external_child_is_runner_written(self):
        obs = observe.replay(short("H_EXT_GATED", 6), DEV[3])
        born = [o for o in obs["final"] if o["gen"] > 0]
        self.assertTrue(born)
        self.assertTrue(all(o["tags"] == "R" * S.G for o in born))

    def test_environment_read_makes_written_bytes_kept(self):
        res = {"nbr_window": bytes(S.G), "nbr_mask": bytes([1] * S.G), "reads_nbr": 1, "exec_foreign": 0, "sealed": False}
        self.assertEqual(observe.endo_tags(res, bytes(S.G)), "K" * S.G)
        res.update(reads_nbr=0)
        self.assertEqual(observe.endo_tags(res, bytes(S.G)), "P" * S.G)
        child = bytes([1]) + bytes(S.G - 1)
        self.assertEqual(observe.endo_tags(res, child), "M" + "P" * (S.G - 1))
        res.update(nbr_mask=bytes([0] * 3 + [1] * (S.G - 3)))
        self.assertEqual(observe.endo_tags(res, bytes(S.G)), "KKK" + "P" * (S.G - 3))
        res.update(exec_foreign=1)
        self.assertEqual(observe.endo_tags(res, bytes(S.G)), "K" * S.G)
        res.update(exec_foreign=0, sealed=True)
        self.assertEqual(observe.endo_tags(res, bytes(S.G)), "K" * S.G)


class Label(unittest.TestCase):
    """The organism label: which writer's bytes ALONE carry the function (sufficiency, others zeroed)."""
    cases = assay.probe_cases(DEV[0])

    def test_sufficiency_order(self):
        H, NH, R = S.H(), S.NH(), S.RECON()
        self.assertEqual(assay.label(H, "P" * S.G, None, self.cases), "ENDO")
        self.assertEqual(assay.label(H, "R" * S.G, None, self.cases), "EXT")
        self.assertEqual(assay.label(NH, "I" * S.G, None, self.cases), "INS")
        self.assertEqual(assay.label(R, "KKK" + "P" * (S.G - 3), None, self.cases), "ENV")
        self.assertEqual(assay.label(H, "MM" + "P" * (S.G - 2), None, self.cases), "OTHER")

    def test_parent_written_copy_outranks_kept_copy(self):
        # a converted reconstructor: kept IN/OUT at 0..1 AND a parent-written IN/OUT at 3..4 behind a NOP prefix
        t = bytes([vm.I(21, 0), vm.I(22, 0), 0, vm.I(21, 0), vm.I(22, 0)]) + bytes(S.G - 5)
        self.assertEqual(assay.label(t, "KKK" + "P" * (S.G - 3), None, self.cases), "ENDO")

    def test_function_only_with_the_neighbour_is_environmental(self):
        self.assertFalse(assay.f0(S.PARASITE(), self.cases))
        self.assertEqual(assay.label(S.PARASITE(), "R" * S.G, True, self.cases), "ENV")
        self.assertIsNone(assay.label(S.PARASITE(), "R" * S.G, False, self.cases))
        self.assertIsNone(assay.label(S.PARASITE(), "R" * S.G, None, self.cases))

    def test_nonfunctional_is_unlabelled(self):
        self.assertIsNone(assay.label(bytes(S.G), "P" * S.G, None, self.cases))

    def test_run_class_is_a_strict_majority(self):
        self.assertEqual(assay.run_class([]), "NONE")
        self.assertEqual(assay.run_class(["ENDO", "ENDO", "ENV"]), "ENDO")
        self.assertEqual(assay.run_class(["ENDO", "ENV"]), "MIXED")
        self.assertEqual(assay.run_class(["ENV", "ENV", "OTHER", "OTHER"]), "MIXED")


class Classify(unittest.TestCase):
    """Run-level attribution from a RECORD (an engine run's own output), verified by replay; labels never read."""
    @classmethod
    def setUpClass(cls):
        cls.ext = assay.record(S.ARM["H_EXT_SHORT"], DEV[4])
        cls.ins = assay.record(S.ARM["NH_ENDO_SHORT"], DEV[4])

    def test_known_classes_and_origin(self):
        c = assay.classify(self.ext)
        self.assertEqual((c["cls"], c["origin"], c["refused"]), ("EXT", "INSERTED", ""))
        c = assay.classify(self.ins)
        self.assertEqual((c["cls"], c["origin"], c["refused"]), ("INS", "INSERTED", ""))

    def test_label_forgeries_change_nothing(self):
        for rec, kind in ((self.ext, "LABELS"), (self.ins, "PLANT")):
            a, b = assay.classify(rec), assay.classify(assay.forge(rec, kind))
            self.assertEqual({k: a[k] for k in assay.KEYS}, {k: b[k] for k in assay.KEYS}, kind)

    def test_byte_and_physics_forgeries_are_refused(self):
        for rec, kind in ((self.ext, "PHYS"), (self.ext, "TAPE"), (self.ins, "GEN"), (self.ins, "PHYS")):
            c = assay.classify(assay.forge(rec, kind))
            self.assertEqual((c["cls"], c["refused"]), ("REFUSED", "REPLAY_MISMATCH"), kind)

    def test_forgeries_actually_edit_the_record(self):
        for rec, kind in ((self.ext, "LABELS"), (self.ext, "PHYS"), (self.ext, "TAPE"), (self.ins, "GEN"), (self.ins, "PLANT"), (self.ins, "PHYS")):
            self.assertNotEqual(assay.canon(rec), assay.canon(assay.forge(rec, kind)), kind)

    def test_classify_reads_no_label_field(self):
        rec = copy.deepcopy(self.ext)
        for k in ("signals", "events", "snapshots", "founders", "telemetry", "dependents", "exploits", "env_changes"):
            rec["out"].pop(k, None)
        for o in rec["out"]["final_population"]:
            for k in list(o):
                if k not in ("cell", "tape", "generation"):
                    o.pop(k)
        rec["spec"]["scheduler_reason"] = "blinded"
        rec["arm"] = "blinded"
        self.assertEqual({k: assay.classify(rec)[k] for k in assay.KEYS}, {k: assay.classify(self.ext)[k] for k in assay.KEYS})

    def test_origin_reads_founder_bytes(self):
        self.assertEqual(assay.origin([bytes(S.G), S.NH()], assay.probe_cases(1)), "INSERTED")
        self.assertEqual(assay.origin([bytes(S.G)], assay.probe_cases(1)), "ARISEN")
        rnd = assay.record(S.ARM["RANDOM_ENDO_GATED"], DEV[5], epochs=3)
        self.assertEqual(assay.classify(rnd)["cls"], "NONE")


class Baselines(unittest.TestCase):
    """The two negative-control detectors must be fooled where the instrument is not."""
    def test_label_reader_never_says_env_and_follows_an_edited_spec(self):
        rec = assay.record(S.ARM["RECON_ENDO_GATED"], DEV[0], epochs=8)
        self.assertEqual(assay.classify(rec)["cls"], "ENV")
        self.assertNotEqual(assay.b1(rec)["cls"], "ENV")
        ext = assay.record(S.ARM["H_EXT_SHORT"], DEV[1], epochs=8)
        self.assertEqual(assay.b1(assay.forge(ext, "PHYS"))["cls"], "ENDO")

    def test_bytes_only_detector_credits_a_runner_written_copier(self):
        ext = assay.record(S.ARM["H_EXT_SHORT"], DEV[2], epochs=8)
        self.assertEqual(assay.b2(ext)["cls"], "ENDO")
        self.assertEqual(assay.classify(ext)["cls"], "EXT")


class Analysis(unittest.TestCase):
    def test_w_max_is_the_exact_binomial_threshold(self):
        from rso.witness.ruler import tail_le
        for n in (21, 24, 48, 64, 100):
            w = analysis.w_max(n)
            self.assertLessEqual(tail_le(n, w, Fraction(1, 5)), Fraction(1, 100), n)
            self.assertGreater(tail_le(n, w + 1, Fraction(1, 5)), Fraction(1, 100), n)
        self.assertIsNone(analysis.w_max(20))            # 0.8**20 > 1/100: no count of errors can pass

    def rows(self, flip=None, n=24):
        out = []
        for gt in ("ENDO", "EXT", "ENV", "INS"):
            for k in range(n):
                out.append(dict(arm=gt + "_ARM", gt=gt, origin_gt="INSERTED", forgery="", cls=gt, origin="INSERTED", refused="",
                                b1="ENDO", b2="EXT", b1_origin="INSERTED", b2_origin="INSERTED"))
        for kind in ("LABELS", "PLANT"):
            out.append(dict(arm="F", gt="EXT", origin_gt="INSERTED", forgery=kind, cls="EXT", origin="INSERTED", refused="", source_cls="EXT",
                            source_origin="INSERTED", b1="ENDO", b2="EXT", b1_origin="INSERTED", b2_origin="INSERTED"))
        for kind in ("PHYS", "TAPE", "GEN"):
            out.append(dict(arm="F", gt="REFUSED", origin_gt="", forgery=kind, cls="REFUSED", origin="", refused="REPLAY_MISMATCH",
                            source_cls="EXT", source_origin="INSERTED", b1="ENDO", b2="EXT", b1_origin="INSERTED", b2_origin="INSERTED"))
        if flip:
            flip(out)
        return out

    def test_clean_rows_qualify(self):
        self.assertEqual(analysis.verdict(self.rows())["verdict"], "ATTRIBUTION_QUALIFIED")

    def test_too_many_class_errors_fail(self):
        def f(rows):
            for r in [r for r in rows if r["gt"] == "ENV" and not r["forgery"]][:analysis.w_max(24) + 1]:
                r["cls"] = "ENDO"
        v = analysis.verdict(self.rows(f))
        self.assertEqual(v["verdict"], "NOT_QUALIFIED")
        self.assertIn("Q1:ENV", v["failed"])

    def test_errors_up_to_w_max_pass(self):
        def f(rows):
            for r in [r for r in rows if r["gt"] == "ENV" and not r["forgery"]][:analysis.w_max(24)]:
                r["cls"] = "ENDO"
        self.assertEqual(analysis.verdict(self.rows(f))["verdict"], "ATTRIBUTION_QUALIFIED")

    def test_nonfunctional_runs_leave_the_denominator(self):
        def f(rows):
            for r in [r for r in rows if r["gt"] == "ENDO" and not r["forgery"]][:3]:
                r["cls"] = "NONE"
        v = analysis.verdict(self.rows(f, n=24))
        self.assertEqual(v["q1"]["ENDO"]["n"], 21)
        self.assertEqual(v["verdict"], "ATTRIBUTION_QUALIFIED")

    def test_underpowered_class(self):
        self.assertEqual(analysis.verdict(self.rows(n=20))["verdict"], "UNDERPOWERED")

    def test_one_unrefused_forgery_fails(self):
        def f(rows):
            r = [r for r in rows if r["forgery"] == "TAPE"][0]; r["cls"] = "EXT"; r["refused"] = ""
        self.assertIn("Q3:TAPE", analysis.verdict(self.rows(f))["failed"])

    def test_one_label_forgery_that_moves_the_class_fails(self):
        def f(rows):
            r = [r for r in rows if r["forgery"] == "LABELS"][0]; r["cls"] = "ENDO"
        self.assertIn("Q3:LABELS", analysis.verdict(self.rows(f))["failed"])

    def test_one_label_forgery_that_moves_the_origin_fails(self):
        def f(rows):
            r = [r for r in rows if r["forgery"] == "PLANT"][0]; r["origin"] = "ARISEN"
        self.assertIn("Q3:PLANT", analysis.verdict(self.rows(f))["failed"])

    def test_origin_errors_fail(self):
        def f(rows):
            for r in [r for r in rows if not r["forgery"]][:analysis.w_max(96) + 1]:
                r["origin"] = "ARISEN"
        self.assertIn("Q2", analysis.verdict(self.rows(f))["failed"])

    def test_a_baseline_that_passes_q1_makes_the_set_uninformative(self):
        def f(rows):
            for r in rows:
                r["b1"] = r["gt"] if not r["forgery"] else r["b1"]
        self.assertEqual(analysis.verdict(self.rows(f))["verdict"], "UNINFORMATIVE")

    def test_mixed_counts_as_wrong(self):
        def f(rows):
            for r in [r for r in rows if r["gt"] == "INS" and not r["forgery"]][:analysis.w_max(24) + 1]:
                r["cls"] = "MIXED"
        self.assertIn("Q1:INS", analysis.verdict(self.rows(f))["failed"])


class Seeds(unittest.TestCase):
    def test_partitions_are_disjoint_from_every_registered_namespace(self):
        self.assertEqual(S.partition_conflicts(), [])

    def test_partitions_do_not_overlap(self):
        d = set(S.seeds("H_ENDO_GATED", "dev", 50)); c = set(S.seeds("H_ENDO_GATED", "confirm", 50))
        self.assertFalse(d & c)
        self.assertEqual(S.seeds("RECON_ENDO_GATED", "confirm", 2), [17_050_000 + 1000 * S.NAMES.index("RECON_ENDO_GATED") + k for k in (1, 2)])


if __name__ == "__main__":
    unittest.main()
