"""Acceptance for C-004-T023A: AUTHOR_TESTED stage records of the world-plane instruments.

7 records (P0 BOUNDS, P3 ERASE, P4 PRESERVE, P5 CHANNEL, P6 RESTART, P7 OBSERVER, P8 TWIN_EQ) are valid
(receipt.validate_stage_record), their version and fire-receipt hashes equal the blobs committed at the cited
commits, a record with a wrong version or receipt hash is refused, and the fire tests reproduce at the current
sources (about 20 CPU-s: P6 RESTART on REG and the P8 outcome vectors dominate).
Python >= 3.8, standard library only.
"""
import copy
import hashlib
import json
import os
import subprocess
import unittest

from rso.slice001 import adapter as AD
from rso.slice001 import receipt as R
from rso.slice001.stages import fire_world as FW

INSTRUMENTS = ("P0", "P3", "P4", "P5", "P6", "P7", "P8")


def _load(path):
    with open(os.path.join(FW.ROOT, *path.split("/")), "r", encoding="utf-8") as f:
        return json.load(f)


def _records():
    return {i: _load(FW.record_path(i)) for i in INSTRUMENTS}


def _is_ancestor(commit):
    r = subprocess.run(["git", "merge-base", "--is-ancestor", commit, "HEAD"], cwd=FW.ROOT,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    return r.returncode == 0


class TestStageRecords(unittest.TestCase):
    def test_seven_records_valid_and_author_tested(self):
        recs = _records()
        self.assertEqual(sorted(recs), list(INSTRUMENTS))
        for inst, rec in recs.items():
            with self.subTest(instrument=inst):
                R.validate_stage_record(rec)
                self.assertEqual(rec["instrument"], inst)
                self.assertEqual(rec["stage"], "AUTHOR_TESTED")
                self.assertIsNone(rec["first_sight"])
                self.assertEqual([c["role"] for c in rec["version"]],
                                 ["code:" + p for p in FW.SOURCES[inst]])

    def test_hashes_equal_the_committed_blobs(self):
        for inst, rec in _records().items():
            with self.subTest(instrument=inst):
                FW.check_record(rec)
                self.assertTrue(_is_ancestor(rec["version"][0]["commit"]))
                self.assertTrue(_is_ancestor(rec["fire_test"]["receipt"]["commit"]))

    def test_versions_are_the_current_sources(self):
        # a source change after the record resets the stage (B4.1); this test makes that visible
        for inst, rec in _records().items():
            for ref in rec["version"]:
                path = ref["role"][len("code:"):]
                cur = AD.file_code_ref(path, ref["commit"], FW.ROOT)
                self.assertEqual((cur["sha256"], cur["length"]), (ref["sha256"], ref["length"]), path)

    def test_a_wrong_version_hash_is_refused(self):
        rec = copy.deepcopy(_records()["P3"])
        rec["version"][1]["sha256"] = "0" * 64
        with self.assertRaises(FW.VersionMismatch) as cm:
            FW.check_record(rec)
        self.assertEqual(cm.exception.code, "STAGE_VERSION_MISMATCH:rso/slice001/reset.py")

    def test_a_wrong_receipt_hash_is_refused(self):
        rec = copy.deepcopy(_records()["P6"])
        rec["fire_test"]["receipt"]["blob_sha256"] = "f" * 64
        with self.assertRaises(FW.VersionMismatch) as cm:
            FW.check_record(rec)
        self.assertEqual(cm.exception.code, "STAGE_RECEIPT_MISMATCH:" + FW.RECEIPT_PATH)

    def test_a_record_without_a_reject_case_is_refused(self):
        rec = copy.deepcopy(_records()["P4"])
        rec["fire_test"]["must_reject"] = []
        with self.assertRaises(R.StageError):
            R.validate_stage_record(rec)


STAGE_DIR = os.path.join(FW.ROOT, "rso", "slice001", "stages")


def _stage_record_files():
    """Every stage record file (one per instrument; fire receipts are not stage records)."""
    return sorted(n for n in os.listdir(STAGE_DIR) if n.endswith(".json") and n != "FIRE_RECEIPT_world.json")


class TestCanonicalFiles(unittest.TestCase):
    """C-004-T027: a registered row binds sha256(file); the consumer looks up record_blob(record). They must agree."""

    def test_every_stage_record_file_is_its_record_blob(self):
        from rso.slice001 import evidence as EVD
        names = _stage_record_files()
        self.assertEqual(len(names), 12)
        for n in names:
            with self.subTest(file=n):
                with open(os.path.join(STAGE_DIR, n), "rb") as f:
                    raw = f.read()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), EVD.record_blob(json.loads(raw)))

    def test_content_unchanged_by_the_canonical_rewrite(self):
        base = subprocess.run(["git", "rev-parse", "e4042c2a2"], cwd=FW.ROOT, stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, universal_newlines=True, timeout=60).stdout.strip()
        for n in _stage_record_files():
            with self.subTest(file=n):
                old = FW.committed_blob("rso/slice001/stages/" + n, base)
                self.assertIsNotNone(old)
                with open(os.path.join(STAGE_DIR, n), "rb") as f:
                    self.assertEqual(json.loads(f.read()), json.loads(old))

    def test_the_world_writer_emits_canonical_bytes(self):
        rec = _records()["P3"]
        self.assertEqual(FW.record_bytes(rec), R.canonical_bytes(rec))


class TestFireReceipt(unittest.TestCase):
    def test_receipt_is_all_ok_and_matches_the_records(self):
        doc = _load(FW.RECEIPT_PATH)
        self.assertTrue(doc["all_ok"])
        self.assertEqual(len(doc["cases"]), len(FW.CASES))
        for inst, rec in _records().items():
            rows = [r for r in doc["cases"] if r["instrument"] == inst]
            self.assertEqual(rec["fire_test"]["must_accept"], [r["case_id"] for r in rows if r["expected"] == "ACCEPT"])
            self.assertEqual(rec["fire_test"]["must_reject"],
                             [{"case_id": r["case_id"], "expected_reason": r["expected_reason"]}
                              for r in rows if r["expected"] == "REJECT"])
            self.assertEqual(doc["versions"][inst], rec["version"])

    def test_fire_tests_reproduce(self):
        doc = _load(FW.RECEIPT_PATH)
        again = FW.run_cases()
        keep = ("instrument", "case_id", "expected", "expected_reason", "observed_value", "observed_reason", "ok")
        self.assertEqual([{k: r[k] for k in keep} for r in again], [{k: r[k] for k in keep} for r in doc["cases"]])


if __name__ == "__main__":
    unittest.main()
