"""Plumbing tests for rso/witness/run_witness.py (C-009-T016).

HARD GATE (C-009-T016, SELECTION.md): plumbing only. Tiny configurations (P=4, G=1) on RANDOM populations in a temp
directory; the registered subject configurations (P=128, G=120) are never run here, and no accuracy, retention or
reward statistic is computed or printed for any arm or control. What is checked: one TOP_LEVEL launch per bundle,
every receipt binds (binding_reasons == []), a second run never reuses a launch, the seed record is complete and
independently replayable, pairing and exclusion refusals happen before any ledger row, cap exhaustion and node
failure leave an honest ledger and no MANIFEST. Python >= 3.8; numpy.
"""
import contextlib
import io
import json
import os
import tempfile
import unittest

import numpy as np

from ares import search as AR
from ares import substrate as S
from rso.binding import binding as B
from rso.slice001 import ledger as L
from rso.witness import ares_client as AC
from rso.witness import run_witness as RW

COMMIT = "0" * 40


def _write_contract(d, launches=5):
    p = os.path.join(d, "contract.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"caps": {"top_level_validation_launches": launches, "cpu_minutes": 600,
                            "new_artifact_mb": 600}}, f)
    return p


def _write_subject(d, name="subj", seed=7):
    """A RANDOM population organism as the canonical genome file the driver reads (no evolution)."""
    pop = S.random_population(S.Config(), 4, np.random.default_rng(seed))
    data = RW.genome_bytes(pop.genome(0))
    p = os.path.join(d, name + ".json")
    with open(p, "wb") as f:
        f.write(data)
    return p


def _write_config(d, subject, entries, name="config.json", **extra):
    cfg = dict({"schema": RW.CONFIG_SCHEMA, "label": "plumbing", "world": "W15", "entries": [
        {"subject": os.path.basename(subject), "arm": a, "predicate": "P-PLUMB", "seeds": s} for a, s in entries]},
        **extra)
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(cfg, f)
    return p


def _read(path):
    with open(path, "rb") as f:
        return f.read()


def _bundle(out):
    man = json.loads(_read(os.path.join(out, "MANIFEST.json")))
    rows = json.loads(_read(os.path.join(out, "inventory.json")))["rows"]
    run = json.loads(_read(os.path.join(out, "run.json")))
    return man, rows, run


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.d = self._tmp.name
        self.contract = _write_contract(self.d)
        self.ledger_path = os.path.join(self.d, "ledger.jsonl")
        self.subject = _write_subject(self.d)

    def tearDown(self):
        self._tmp.cleanup()

    def ledger(self):
        return L.Ledger.from_contract(self.ledger_path, self.contract)

    def launch(self, config, out_name="b1", **kw):
        out = os.path.join(self.d, out_name)
        kw.setdefault("code_commit", COMMIT)
        res = RW.launch(config, self.ledger(), out, **kw)
        return out, res

    def tops(self):
        return [r for r in self.ledger().inventory() if r.get("launch_kind") == B.TOP_LEVEL]


class TestLaunch(Base):
    def test_one_top_level_launch_and_every_receipt_binds(self):
        cfg = _write_config(self.d, self.subject, [("S", [101, 102, 103]), ("S-NOPL", [101, 102, 103]),
                                                   ("NULL", [101, 102]), ("POS", [104, 105])])
        out, res = self.launch(cfg)
        man, rows, run = _bundle(out)
        self.assertEqual(len(self.tops()), 1)
        self.assertEqual(self.tops()[0]["status"], "COMPLETED")
        self.assertEqual(man["launch_run_id"], run["run_id"])
        self.assertEqual(man["launch_run_id"], res["launch_run_id"])
        self.assertEqual(B.launch_reasons(rows, man["launch_run_id"]), [])
        self.assertEqual(len(man["nodes"]), 4)
        for n in man["nodes"]:
            data = _read(os.path.join(out, n["receipt_file"]))
            self.assertEqual(B.binding_reasons(n["node_id"], n["run_id"], data, rows, man["launch_run_id"]), [])
            self.assertEqual(n["artifact"]["sha256"], B.receipt_sha256(data))
        self.assertEqual(len(B.own_launch_rows(rows, man["launch_run_id"])), 4)

    def test_second_run_does_not_reuse_the_first_launch(self):
        cfg = _write_config(self.d, self.subject, [("S", [101, 102]), ("NULL", [101, 102])])
        out1, r1 = self.launch(cfg, "b1")
        out2, r2 = self.launch(cfg, "b2")
        self.assertNotEqual(r1["launch_run_id"], r2["launch_run_id"])
        self.assertEqual(len(self.tops()), 2)
        man2, rows2, _ = _bundle(out2)
        self.assertEqual(len(B.own_launch_rows(rows2, man2["launch_run_id"])), 2)
        # an explicit repeat of the first launch id is refused by the ledger, not silently reused
        with self.assertRaises(L.LedgerError):
            self.launch(cfg, "b3", launch_run_id=r1["launch_run_id"])
        self.assertEqual(len(self.tops()), 2)

    def test_cheat_controls_binding_catches_borrowing(self):
        cfg = _write_config(self.d, self.subject, [("S", [101, 102])])
        out1, _ = self.launch(cfg, "b1")
        out2, _ = self.launch(cfg, "b2")
        m1, rows, _ = _bundle(out1)
        m2, _, _ = _bundle(out2)
        n = m1["nodes"][0]
        data = _read(os.path.join(out1, n["receipt_file"]))
        # a receipt edited after its run
        self.assertIn(B.DIGEST_MISMATCH, B.binding_reasons(n["node_id"], n["run_id"], data + b" ", rows,
                                                           m1["launch_run_id"]))
        # a receipt presented under the other launch
        self.assertIn(B.FOREIGN_LAUNCH, B.binding_reasons(n["node_id"], n["run_id"], data, rows,
                                                          m2["launch_run_id"]))

    def test_seed_record_is_complete(self):
        cfg = _write_config(self.d, self.subject, [("S", [101, 102, 103]), ("S-NOPL", [101, 102, 103]),
                                                   ("NULL", [201, 202])])
        out, _ = self.launch(cfg)
        man, _, _ = _bundle(out)
        seeds = json.loads(_read(os.path.join(out, "seeds.json")))
        sha = man["subjects"][0]["sha256"]
        self.assertEqual(seeds["subjects"][sha]["arms"], {"S": [101, 102, 103], "S-NOPL": [101, 102, 103],
                                                          "NULL": [201, 202]})
        self.assertEqual(seeds["subjects"][sha]["union"], [101, 102, 103, 201, 202])
        for n in man["nodes"]:
            rec = json.loads(_read(os.path.join(out, n["receipt_file"])))
            self.assertEqual(rec["seeds"], seeds["subjects"][sha]["arms"][rec["arm"]])
        self.assertEqual(_read(os.path.join(out, man["subjects"][0]["file"])), _read(self.subject))

    def test_failed_node_leaves_honest_ledger_and_no_manifest(self):
        cfg = _write_config(self.d, self.subject, [("S", [101, 102]), ("NULL", [101, 102])])
        calls = []
        orig = AC.receipt_dict

        def boom(launch, arm_name, predicate, subject, seeds):
            calls.append(arm_name)
            if len(calls) == 2:
                raise RuntimeError("injected")
            return orig(launch, arm_name, predicate, subject, seeds)
        AC.receipt_dict = boom
        try:
            with self.assertRaises(RW.WitnessError):
                self.launch(cfg)
        finally:
            AC.receipt_dict = orig
        out = os.path.join(self.d, "b1")
        self.assertFalse(os.path.exists(os.path.join(out, "MANIFEST.json")))
        rows = self.ledger().inventory()
        self.assertEqual(self.tops()[0]["status"], "FAILED")
        self.assertEqual(sorted(r["status"] for r in rows if r.get("launch_kind") == B.RECEIPT),
                         ["COMPLETED", "FAILED"])

    def test_cap_exhaustion_is_refused_and_recorded(self):
        self.contract = _write_contract(self.d, launches=1)
        cfg = _write_config(self.d, self.subject, [("S", [101, 102])])
        self.launch(cfg, "b1")
        with self.assertRaises(L.CapExhausted):
            self.launch(cfg, "b2")
        self.assertFalse(os.path.exists(os.path.join(self.d, "b2", "MANIFEST.json")))
        self.assertIn("REFUSED", [r.get("status") for r in self.ledger().inventory()])

    def test_existing_bundle_directory_is_not_overwritten(self):
        cfg = _write_config(self.d, self.subject, [("S", [101, 102])])
        os.makedirs(os.path.join(self.d, "b1"))
        with open(os.path.join(self.d, "b1", "keep.txt"), "w") as f:
            f.write("x")
        with self.assertRaises(RW.WitnessError):
            self.launch(cfg, "b1")
        self.assertFalse(os.path.exists(self.ledger_path))


class TestRefusals(Base):
    """Every refusal happens before any ledger row is written."""

    def refused(self, entries, **extra):
        cfg = _write_config(self.d, self.subject, entries, **extra)
        with self.assertRaises(RW.WitnessError) as cm:
            self.launch(cfg)
        self.assertFalse(os.path.exists(self.ledger_path))
        return str(cm.exception)

    def test_nopl_must_share_the_subjects_seeds_in_order(self):
        self.assertIn("S-NOPL", self.refused([("S", [101, 102, 103]), ("S-NOPL", [101, 103, 102])]))
        self.assertIn("S-NOPL", self.refused([("S", [101, 102, 103]), ("S-NOPL", [101, 102, 104])]))

    def test_duplicate_seed_and_duplicate_node_refused(self):
        self.assertIn("duplicate", self.refused([("S", [101, 101])]))
        self.assertIn("duplicate", self.refused([("NULL", [101]), ("NULL", [102])]))

    def test_unknown_arm_and_empty_seeds_refused(self):
        self.assertIn("arm", self.refused([("BOGUS", [101])]))
        self.assertIn("seeds", self.refused([("S", [])]))

    def test_non_integer_seed_refused(self):
        self.assertIn("seed", self.refused([("S", [101, 1.5])]))
        self.assertIn("seed", self.refused([("S", [101, True])]))

    def test_seed_floor_and_ares_eval_seeds_refused(self):
        self.assertIn("floor", self.refused([("S", [101, 900001])], seed_floor=900000))
        self.assertIn("EVAL", self.refused([("S", [AR.EVAL_SEEDS[0]])]))

    def test_subject_ga_seeds_are_excluded(self):
        rec = os.path.join(self.d, "subject_record.json")
        with open(rec, "w") as f:
            json.dump({"episode_seeds": [555, 556]}, f)
        self.assertIn("excluded", self.refused([("S", [101, 556])], exclude_seed_records=["subject_record.json"]))

    def test_non_canonical_subject_file_refused(self):
        loose = json.dumps(json.loads(_read(self.subject)), indent=2).encode("utf-8")
        with open(self.subject, "wb") as f:
            f.write(loose)
        self.assertIn("canonical", self.refused([("S", [101])]))


class TestSubject(Base):
    def run_subject(self, name="s1", seed=1):
        out = os.path.join(self.d, name)
        return out, RW.run_subject("W4", "present", {}, P=4, G=1, eps=2, seed=seed, out_dir=out)

    def test_record_files_and_digests(self):
        out, rec = self.run_subject()
        gdata = _read(os.path.join(out, "genome.json"))
        saved = json.loads(_read(os.path.join(out, "subject_record.json")))
        self.assertEqual(saved["genome_sha256"], RW.sha256_hex(gdata))
        pop = S.Population.from_genomes([json.loads(gdata.decode("utf-8"))])
        self.assertEqual(AC.genome_digest(pop), saved["genome_sha256"])   # the node-id digest is this file's digest
        self.assertEqual(saved["run_receipt"]["spec"]["seed"], 1)
        self.assertEqual(saved["run_receipt"]["spec"]["P"], 4)

    def test_every_episode_seed_is_recorded_and_replayable(self):
        out, rec = self.run_subject(seed=3)
        # independent replay of generation 0's draw: the population initialiser consumes the rng first
        rng = np.random.default_rng(3)
        S.random_population(S.Config(), 4, rng)
        gen0 = [int(x) for x in rng.integers(0, 2**31 - 1, size=2)]
        self.assertEqual(rec["training_seeds_by_generation"][0], gen0)
        self.assertEqual(len(rec["training_seeds_by_generation"]), 1)
        self.assertEqual(rec["heldout_seed_sets"], [list(AR.EVAL_SEEDS)])
        self.assertEqual(rec["episode_seeds"], sorted(set(gen0) | set(AR.EVAL_SEEDS)))

    def test_recorder_does_not_change_the_run_and_restores_rollout(self):
        orig = AR.rollout
        out, rec = self.run_subject(seed=5)
        self.assertIs(AR.rollout, orig)
        plain = AR.run("W4", "present", S.Config(), P=4, G=1, eps=2, seed=5)
        self.assertEqual(rec["genome_sha256"], RW.sha256_hex(RW.genome_bytes(plain["final"]["genome"])))
        with self.assertRaises(Exception):
            RW.run_subject("NOSUCHWORLD", "present", {}, P=4, G=1, eps=2, seed=5,
                           out_dir=os.path.join(self.d, "s2"))
        self.assertIs(AR.rollout, orig)

    def test_no_fitness_is_stored(self):
        out, rec = self.run_subject()
        text = _read(os.path.join(out, "subject_record.json")).decode("utf-8").lower()
        for banned in ("fitness", "heldout\":", "reward", "best_train", "mean_train", "champ_heldout", "\"log\""):
            self.assertNotIn(banned, text)
        self.assertEqual(sorted(os.listdir(out)), ["genome.json", "subject_record.json"])

    def test_existing_output_directory_refused(self):
        out, _ = self.run_subject()
        with self.assertRaises(RW.WitnessError):
            RW.run_subject("W4", "present", {}, P=4, G=1, eps=2, seed=1, out_dir=out)

    def test_subject_record_feeds_the_exclusion_of_a_launch(self):
        out, rec = self.run_subject(seed=3)
        subj = os.path.join(self.d, "from_run.json")
        with open(subj, "wb") as f:
            f.write(_read(os.path.join(out, "genome.json")))
        drawn = rec["training_seeds_by_generation"][0][0]
        cfg = _write_config(self.d, subj, [("S", [101, drawn])],
                            exclude_seed_records=["s1/subject_record.json"])
        with self.assertRaises(RW.WitnessError):
            RW.launch(cfg, self.ledger(), os.path.join(self.d, "bx"), code_commit=COMMIT)


class TestCli(Base):
    def run_main(self, argv):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = RW.main(argv)
        return code, buf.getvalue()

    def test_launch_cli_prints_no_statistic(self):
        cfg = _write_config(self.d, self.subject, [("S", [101, 102]), ("NULL", [101, 102])])
        out = os.path.join(self.d, "cli")
        code, text = self.run_main(["launch", cfg, "--ledger", self.ledger_path, "--contract", self.contract,
                                    "--out", out, "--code-commit", COMMIT])
        self.assertEqual(code, 0)
        summary = json.loads(text)
        self.assertEqual(sorted(summary), ["bundle", "launch_run_id", "nodes", "status"])
        self.assertEqual(summary["nodes"], 2)

    def test_cli_cap_exhaustion_exit_code(self):
        self.contract = _write_contract(self.d, launches=1)
        cfg = _write_config(self.d, self.subject, [("S", [101])])
        args = ["launch", cfg, "--ledger", self.ledger_path, "--contract", self.contract, "--code-commit", COMMIT]
        self.assertEqual(self.run_main(args + ["--out", os.path.join(self.d, "c1")])[0], 0)
        self.assertEqual(self.run_main(args + ["--out", os.path.join(self.d, "c2")])[0], 3)

    def test_cli_refusal_exit_code(self):
        cfg = _write_config(self.d, self.subject, [("BOGUS", [101])])
        code, _ = self.run_main(["launch", cfg, "--ledger", self.ledger_path, "--contract", self.contract,
                                 "--out", os.path.join(self.d, "c1"), "--code-commit", COMMIT])
        self.assertEqual(code, 2)

    def test_subject_cli_prints_paths_and_seed_count_only(self):
        out = os.path.join(self.d, "s")
        code, text = self.run_main(["subject", "--world", "W4", "--P", "4", "--G", "1", "--eps", "2",
                                    "--seed", "1", "--out", out])
        self.assertEqual(code, 0)
        self.assertEqual(sorted(json.loads(text)), ["episode_seed_count", "genome_sha256", "out"])


if __name__ == "__main__":
    unittest.main()
