"""C-017-T030 behavioural tests (unittest; harry1 has no pytest). Run from the repo root:
    python -m unittest rso.z80.tests.test_attribution -v
Development seeds only (17_030_xxx, PREREGISTRATION.md s6). No confirmatory seed (17_050_xxx) is used here."""
import copy
import unittest
from fractions import Fraction

from archaeon.z80atlas import engine as E, tasks as T, vm
from rso.z80 import analysis, assay, observe, subjects as S

DEV = [17_030_901 + i for i in range(6)]          # dev partition, arm slot 0 offset 900+: never used by the dev check


def short(name, epochs):
    return S.spec(S.ARM[name], epochs=epochs)


def planted(tapes, phys, press, epochs):
    s = S.spec(dict(S.ARM["NH_EXT_GATED"], phys=phys, press=press), epochs=epochs)
    s["transplant"]["tapes"] = [t.hex() for t in tapes]
    return s


# v1.1.0 unit parents (C-017-T041). I = vm.I
I = vm.I
# executes ONE target byte (window 0) and returns through a JP it wrote at window 1..2, then writes A to window 3. Target 7 (XOR A,A)
# and its complement 0xF8 (XCHG A,D; D = 0) both leave A = 0; 7 + 0x55 = 0x5C (LD A,G) leaves 32. No read: only the counterfactual
# can see it, and only through the +0x55 sample.
XEXEC = T.pad([I(1, 0), 13, I(19, 0, 1), 129, I(1, 0), 12, I(19, 0, 1), 130, I(1, 0), 5, I(13), 128, I(19, 0, 1), 131, I(23)], S.G)
# copies its whole tape, then jumps into its own fresh copy's HALT: exec_foreign > 0, reads 0 (the ONBOARDING s3.2 4/21 shape)
OWN = T.pad([I(1, 1), 0, I(1, 2), 128, I(1, 3), 32, I(20), I(6, 3), I(16), 0xFC, I(13), 128 + 12, I(23)], S.G)
# writes the INPUT byte of its case to window 0, then copies own 1..31 (challenge/subjects_c.py INPW)
INPW = T.pad([I(21, 0), I(22, 0), I(19, 0, 1), 128, I(1, 1), 1, I(1, 2), 129, I(1, 3), 31, I(20), I(6, 3), I(16), 0xFC, I(23)], S.G)
# IN A; JR +<byte 2>; OUT A; HALT (challenge/subjects_c.py JROP): byte 2 is an operand; zero makes the jump a no-op
JROP = T.pad([I(21, 0), I(14), 0, I(22, 0), I(23)], S.G)


def tags_of(parent, nbr, inp=(7,)):
    res = vm.execute(parent, nbr, inp, 256, True)
    return observe.endo_tags(res, res["nbr_window"], observe.counterfactual(parent, nbr, inp, 256, True))


# echoes only inputs < 128: a competent-looking organism on some cases, never neighbour-dependent
HALF = T.pad([vm.I(21, 0), vm.I(1, 1), 0x80, vm.I(12, 1), vm.I(17), 0x01, vm.I(23), vm.I(22, 0), vm.I(23)], S.G)


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
        self.check("RECON_ENDO_IMPL", 20, DEV[3])

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
        obs = observe.replay(short("RECON_ENDO_IMPL", 6), DEV[2])
        born = [o for o in obs["final"] if o["gen"] > 0]
        self.assertTrue(born)
        self.assertTrue(all(o["tags"][:3] == "KKK" for o in born if "M" not in o["tags"][:3]))

    def test_background_mutation_is_tagged_where_it_changed_bytes(self):
        seen = 0
        for sd in DEV:
            for o in observe.replay(short("NH_ENDO_SHORT", 30), sd)["final"]:
                if o["gen"] == 0 and o["tape"] != S.NH():
                    seen += 1
                    self.assertEqual(o["tags"], "".join("M" if a != b else "I" for a, b in zip(o["tape"], S.NH())))
        self.assertGreater(seen, 0)

    def test_external_child_is_runner_written(self):
        obs = observe.replay(short("H_EXT_GATED", 6), DEV[3])
        born = [o for o in obs["final"] if o["gen"] > 0]
        self.assertTrue(born)
        self.assertTrue(all(o["tags"] == "R" * S.G for o in born))

    def test_counterfactual_tags_per_byte(self):
        z = bytes(S.G); same = {"nbr_window": z, "nbr_mask": bytes([1] * S.G), "reads_nbr": 0}
        self.assertEqual(observe.endo_tags(same, z, [same, same]), "P" * S.G)
        self.assertEqual(observe.endo_tags(same, bytes([1]) + z[1:], [same, same]), "M" + "P" * (S.G - 1))
        part = {"nbr_window": z, "nbr_mask": bytes([0] * 3 + [1] * (S.G - 3)), "reads_nbr": 0}
        self.assertEqual(observe.endo_tags(part, z, [part, part]), "KKK" + "P" * (S.G - 3))
        moved = {"nbr_window": bytes([9]) + z[1:], "nbr_mask": bytes([1] * S.G)}       # byte 0's value follows the pre-window
        self.assertEqual(observe.endo_tags(same, z, [same, moved]), "K" + "P" * (S.G - 1))
        unmasked = {"nbr_window": z, "nbr_mask": bytes([0]) + bytes([1] * (S.G - 1))}   # byte 0 written only for this pre-window
        self.assertEqual(observe.endo_tags(same, z, [unmasked, same]), "K" + "P" * (S.G - 1))
        # byte 0..2 NOT written in the actual execution, written (same value) under both altered pre-windows: still kept
        self.assertEqual(observe.endo_tags(part, z, [same, same]), "KKK" + "P" * (S.G - 3))

    def test_a_copy_made_by_the_neighbours_code_is_environmental(self):
        # a parent that COPIES THE WINDOW ONTO ITSELF (B = C = 128): all 32 bytes written by the parent's execution, every value
        # the target cell's. Environmental reconstruction through a read. A parent copying its own tape is P.
        env = T.pad([vm.I(1, 1), 128, vm.I(1, 2), 128, vm.I(1, 3), 32, vm.I(20), vm.I(6, 3), vm.I(16), 0xFC, vm.I(23)], S.G)
        nbr = S.H()
        res = vm.execute(env, nbr, (7,), 256, True)
        self.assertEqual(res["nbr_window"], nbr)
        self.assertEqual(sum(res["nbr_mask"]), S.G)
        self.assertEqual(observe.endo_tags(res, res["nbr_window"], observe.counterfactual(env, nbr, (7,), 256, True)), "K" * S.G)
        res = vm.execute(S.H(), S.NH(), (7,), 256, True)
        self.assertEqual(observe.endo_tags(res, res["nbr_window"], observe.counterfactual(S.H(), S.NH(), (7,), 256, True)), "P" * S.G)


    def test_a_parent_that_reads_the_window_writes_no_parent_byte(self):
        # v1.1.0 (REPORT s4.1): CDIST writes its head as circdist(t0, t2) of the target -- invariant under both alterations
        cd = S.CDIST()
        res = vm.execute(cd, cd, (7,), 256, True)
        self.assertEqual((res["nbr_window"][:2], res["reads_nbr"] > 0), (cd[:2], True))
        self.assertEqual(tags_of(cd, cd), "K" * S.G)
        cs = assay.probe_cases(DEV[0])
        self.assertEqual(assay.label(res["nbr_window"], tags_of(cd, cd), None, cs), "ENV")
        self.assertFalse(assay.f0(vm.execute(cd, bytes(S.G), (7,), 256, True)["nbr_window"], cs))   # over an empty target: dead

    def test_running_into_its_own_fresh_copy_stays_parent_written(self):
        res = vm.execute(OWN, S.H(), (7,), 256, True)
        self.assertEqual((res["reads_nbr"], res["exec_foreign"] > 0, res["halted"]), (0, True, True))
        self.assertEqual(tags_of(OWN, S.H()), "P" * S.G)
        self.assertEqual(tags_of(S.H(), S.H()), "P" * S.G)

    def test_both_counterfactual_samples_are_load_bearing(self):
        nbr = bytes([7]) + bytes(S.G - 1)
        self.assertEqual(vm.execute(XEXEC, nbr, (7,), 256, True)["reads_nbr"], 0)
        self.assertEqual(tags_of(XEXEC, nbr)[:4], "KPPK")      # window 3 follows the target under +0x55 only

    def test_the_counterfactual_keeps_the_parents_input(self):
        # ENV means the target cell, not the world's input: an input-dependent write is the parent's (REPORT s4.3)
        self.assertEqual(tags_of(INPW, bytes(S.G), (21,)), "P" * S.G)


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
        self.assertFalse(assay.f0(HALF, self.cases))                 # solves some probe cases, not all

    def test_situ_is_neighbour_dependence_not_luck(self):
        # half-solvers solve some cases (by luck all 3 of an opportunity): never functional, alone or run by a parasite from a
        # half-competent host. A parasite that ran a full host is functional only with it: ENV.
        half_host = bytes([vm.I(23)]) + HALF[:S.G - 1]
        for sd in DEV[:3]:
            # one epoch: every neighbour observed is an original tape (a runner child is placed after the opportunities; by
            # epoch 2 a host can mutate into a full echo, and the parasite running it is then truly neighbour-dependent)
            for tapes in ([HALF] * 64, [S.PARASITE(), half_host] * 64):
                spec = planted(tapes, "EXTERNAL", "implicit_survival", 1)
                self.assertFalse(any(o["situ"] for o in observe.replay(spec, sd)["final"]), sd)
                c = assay.classify({"seed": sd, "spec": spec, "out": E.run(spec, sd)})
                self.assertEqual((c["cls"], c["n_ENV"]), ("NONE", 0))
        spec = planted([S.PARASITE(), S.HOST()] * 64, "EXTERNAL", "implicit_survival", 1)
        obs = observe.replay(spec, DEV[0])
        para = [o for o in obs["final"] if o["tape"] == S.PARASITE() and o["situ"]]
        self.assertTrue(para)
        cs = assay.probe_cases(DEV[0])
        self.assertTrue(all(assay.label(o["tape"], o["tags"], o["situ"], cs) == "ENV" for o in para))
        self.assertEqual(assay.classify({"seed": DEV[0], "spec": spec, "out": E.run(spec, DEV[0])})["cls"], "ENV")

    def test_the_sufficiency_filler_is_zero(self):
        # v1.1.0 (REPORT s4.4 E2): zero, not another NOP opcode; a kept jump operand zeroed is a no-op -> ENDO (filler-dependent)
        self.assertEqual(assay.label(JROP, "PPKPP" + "P" * (S.G - 5), None, self.cases), "ENDO")
        self.assertEqual(assay.restrict(JROP, "PPKPP" + "P" * (S.G - 5), "P")[2], 0)

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
        cs = assay.probe_cases(1)
        self.assertEqual(assay.origin([(bytes(S.G), "R"), (S.NH(), "S")], cs), "INSERTED")
        self.assertEqual(assay.origin([(S.NH(), "R")], cs), "ARISEN")           # a lucky random founder is not insertion
        self.assertEqual(assay.origin([(bytes(S.G), "S")], cs), "ARISEN")
        obs = observe.replay(short("SEEDED_ENDO_GATED", 1), DEV[0])
        self.assertEqual({src for _, src in obs["founders"]}, {"S", "R"})
        self.assertTrue(all(t == S.H() for t, src in obs["founders"] if src == "S"))
        rnd = assay.record(S.ARM["RANDOM_ENDO_GATED"], DEV[5], epochs=3)
        self.assertEqual(assay.classify(rnd)["cls"], "NONE")


class Baselines(unittest.TestCase):
    """The two negative-control detectors must be fooled where the instrument is not."""
    def test_label_reader_never_says_env_and_follows_an_edited_spec(self):
        rec = assay.record(S.ARM["RECON_ENDO_IMPL"], DEV[0], epochs=8)
        self.assertEqual(assay.classify(rec)["cls"], "ENV")
        self.assertNotEqual(assay.b1(rec)["cls"], "ENV")
        ext = assay.record(S.ARM["H_EXT_SHORT"], DEV[1], epochs=8)
        self.assertEqual(assay.b1(assay.forge(ext, "PHYS"))["cls"], "ENDO")

    def test_bytes_only_detector_credits_a_runner_written_copier(self):
        ext = assay.record(S.ARM["H_EXT_SHORT"], DEV[2], epochs=8)
        self.assertEqual(assay.b2(ext)["cls"], "ENDO")
        self.assertEqual(assay.classify(ext)["cls"], "EXT")


    def test_recipe_reader_reads_the_construction(self):
        # v1.1.0: right on every v1.0.0 recipe, an ENV output (RECON), and CDIST's recipe read as ENDO
        got = {a["name"]: assay.b4({"seed": DEV[0], "spec": S.spec(a), "out": {}}) for a in S.ARMS}
        for a in S.ARMS:
            want = "ENDO" if a["name"] == "CDIST_ENDO_IMPL" else a["gt"]
            self.assertEqual((got[a["name"]]["cls"], got[a["name"]]["origin"]), (want, a["origin"]), a["name"])

    def test_cdist_arm_is_environmental_where_its_recipe_says_endogenous(self):
        rec = assay.record(S.ARM["CDIST_ENDO_IMPL"], DEV[0], epochs=3)
        c = assay.classify(assay.blinded(rec))
        self.assertEqual((c["cls"], c["origin"], c["n_ENDO"]), ("ENV", "INSERTED", 0))
        self.assertGreater(c["n_ENV"], 50)
        self.assertEqual((assay.b4(rec)["cls"], assay.b1(rec)["cls"]), ("ENDO", "ENDO"))


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
                                b1="ENDO", b2="EXT", b1_origin="INSERTED", b2_origin="INSERTED", b4="ENDO", b4_origin="INSERTED"))
        for kind in ("LABELS", "PLANT"):
            out.append(dict(arm="F", gt="EXT", origin_gt="INSERTED", forgery=kind, cls="EXT", origin="INSERTED", refused="", source_cls="EXT",
                            source_origin="INSERTED", b1="ENDO", b2="EXT", b1_origin="INSERTED", b2_origin="INSERTED", b4="ENDO",
                            b4_origin="INSERTED"))
        for kind in ("PHYS", "TAPE", "GEN"):
            out.append(dict(arm="F", gt="REFUSED", origin_gt="", forgery=kind, cls="REFUSED", origin="", refused="REPLAY_MISMATCH",
                            source_cls="EXT", source_origin="INSERTED", b1="ENDO", b2="EXT", b1_origin="INSERTED", b2_origin="INSERTED",
                            b4="ENDO", b4_origin="INSERTED"))
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

    def test_failure_outranks_underpowered(self):
        def f(rows):
            r = [r for r in rows if r["forgery"] == "GEN"][0]; r["cls"] = "INS"; r["refused"] = ""
        self.assertEqual(analysis.verdict(self.rows(f, n=20))["verdict"], "NOT_QUALIFIED")

    def test_a_missing_forgery_kind_fails(self):
        def f(rows):
            rows[:] = [r for r in rows if r["forgery"] != "PHYS"]
        self.assertIn("Q3:PHYS", analysis.verdict(self.rows(f))["failed"])

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

    def test_an_unforged_refusal_counts_as_wrong(self):
        # v1.1.0 (REPORT s4.4 E3): PREREG s5 'REFUSED included' pinned
        def f(rows):
            rows += [dict(r, cls="REFUSED", origin="", refused="REPLAY_MISMATCH") for r in rows if r["gt"] == "ENV" and not r["forgery"]][:5]
        v = analysis.verdict(self.rows(f))
        self.assertEqual((v["verdict"], v["q1"]["ENV"]["n"], v["q1"]["ENV"]["wrong"]), ("NOT_QUALIFIED", 29, 5))
        self.assertIn("Q1:ENV", v["failed"])

    def test_the_recipe_reader_is_a_registered_baseline(self):
        def f(rows):
            for r in rows:
                r["b4"] = r["gt"] if not r["forgery"] else r["b4"]
        v = analysis.verdict(self.rows(f))
        self.assertEqual((v["verdict"], v["baselines_passing_q1"]), ("UNINFORMATIVE", ["b4"]))

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
        self.assertEqual(S.seeds("RECON_ENDO_IMPL", "confirm", 2), [17_050_000 + 1000 * S.NAMES.index("RECON_ENDO_IMPL") + k for k in (1, 2)])


if __name__ == "__main__":
    unittest.main()
