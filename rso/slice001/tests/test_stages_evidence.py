"""Stage records and fire tests of the evidence-plane and ruler instruments (C-004-T023B).

Acceptance: 5 records valid (receipt.validate_stage_record), fire tests reproduce (re-running them gives the
committed receipt bytes), version hashes equal committed blobs, RETENTION's fire test has a POSITIVE, a
NEGATIVE and a NOT_SHOWN case. Plus a cheat control (a broken instrument cannot get a record) and the
consumer-side use (evidence.gate_authority finds the record; A2 binds the fire receipt). Records and receipts
here are committed files; nothing is registered with the custody store (V8). Stdlib only; uses git.
"""
import hashlib
import json
import os
import unittest
from unittest import mock

from rso.slice001 import evidence as EV
from rso.slice001 import receipt as R
from rso.slice001 import rulers as P
from rso.slice001.stages import evidence_plane as SE
from rso.slice001.stages import version as V


def read(path):
    with open(os.path.join(V.REPO_ROOT, *path.split("/")), "rb") as f:
        return f.read().replace(b"\r\n", b"\n")


def record(i):
    return json.loads(read(SE.record_path(i)).decode("utf-8"))


class TestRecords(unittest.TestCase):
    def test_five_records_valid(self):
        for i in SE.INSTRUMENTS:
            rec = record(i)
            R.validate_stage_record(rec)
            self.assertEqual((rec["instrument"], rec["stage"], rec["first_sight"], rec["closure"]),
                             (SE.RECORD_ID[i], "AUTHOR_TESTED", None, None))
            self.assertTrue(rec["fire_test"]["must_accept"] and rec["fire_test"]["must_reject"], i)

    def test_version_equals_committed_blob(self):
        for i in SE.INSTRUMENTS:
            refs = record(i)["version"]
            self.assertEqual(sorted(r["role"][len("code:"):] for r in refs), sorted(V.SOURCES[i]), i)
            for ref in refs:
                self.assertEqual(ref["commit"], V.PINNED, i)
                blob = V.committed_blob(ref["role"][len("code:"):], ref["commit"])
                self.assertEqual((hashlib.sha256(blob).hexdigest(), len(blob)), (ref["sha256"], ref["length"]), i)
            self.assertEqual(refs, V.instrument_version(i), "%s: source changed since" % i)

    def test_version_covers_every_imported_slice_file(self):
        # T023A's rule: every file the instrument imports and executes is part of its version.
        for i, entry in V.ENTRY.items():
            self.assertEqual(sorted(V.slice_imports(entry) | {entry}), sorted(V.SOURCES[i]), i)

    def test_pin_is_on_main_history(self):
        import subprocess
        r = subprocess.run(["git", "merge-base", "--is-ancestor", V.PINNED, "HEAD"], cwd=V.REPO_ROOT)
        self.assertEqual(r.returncode, 0)

    def test_fire_receipt_binds(self):
        for i in SE.INSTRUMENTS:
            ref = record(i)["fire_test"]["receipt"]
            self.assertEqual(ref["path"], SE.fire_path(i))
            data = V.committed_blob(ref["path"], ref["commit"])
            self.assertEqual(hashlib.sha256(data).hexdigest(), ref["blob_sha256"], i)
            self.assertEqual(data, read(ref["path"]), i)
            rc = json.loads(data.decode("utf-8"))
            self.assertTrue(rc["all_ok"], i)
            self.assertEqual(rc["version"], record(i)["version"], i)


class TestFireTests(unittest.TestCase):
    def test_fire_tests_reproduce(self):
        for i in SE.INSTRUMENTS:
            self.assertEqual(SE.dump(SE.fire_receipt(i)), read(SE.fire_path(i)), i)

    def test_ruler_has_positive_negative_not_shown(self):
        rc = json.loads(read(SE.fire_path("RETENTION")).decode("utf-8"))
        self.assertEqual(sorted(c["observed_value"] for c in rc["cases"]), ["NEGATIVE", "NOT_SHOWN", "POSITIVE"])
        neg = [c for c in rc["cases"] if c["observed_value"] == "NEGATIVE"][0]
        self.assertEqual(neg["observed_reason"], "1/2")

    def test_every_gate_rejects_with_its_reason(self):
        for i in SE.INSTRUMENTS:
            rc = json.loads(read(SE.fire_path(i)).decode("utf-8"))
            rej = [c for c in rc["cases"] if c["polarity"] == "REJECT"]
            self.assertTrue(rej, i)
            for c in rej:
                self.assertEqual(c["observed_reason"], c["expected_reason"], (i, c["case_id"]))

    def test_broken_instrument_gets_no_record(self):
        # Cheat control: a RETENTION that collapses NEGATIVE into NOT_SHOWN fails its fire test, and no stage
        # record can be written from that receipt.
        real = P.retention

        def broken(answer, variant="STANDARD"):
            o = real(answer, variant)
            return dict(o, value="NOT_SHOWN") if o["value"] == "NEGATIVE" else o

        with mock.patch.object(P, "retention", broken):
            rc = SE.fire_receipt("RETENTION")
        self.assertFalse(rc["all_ok"])
        with self.assertRaises(RuntimeError):
            SE.stage_record("RETENTION", SE.dump(rc), "0" * 40, "2026-10-04T00:00:00Z")


class TestConsumerUse(unittest.TestCase):
    def test_gate_authority_qualified_from_these_records(self):
        recs = [record(i) for i in SE.INSTRUMENTS]
        store = EV.FixtureStore([{"record_kind": "STAGE_RECORD", "blob_sha256": EV.record_blob(r),
                                  "registered_at_utc": "2026-10-04T00:00:00Z", "repo_path": "stage",
                                  "registrar": "fixture", "commit_sha": "0" * 40, "row_id": n}
                                 for n, r in enumerate(recs, 1)])
        blobs = {SE.fire_path(i): read(SE.fire_path(i)) for i in SE.INSTRUMENTS}
        bundle = EV.Bundle({}, {}, [], stage_records=recs, blobs=blobs)
        reg = EV.Registry(bundle, store)
        for p, name in (("P1", "CALIBRATION"), ("P2", "RETENTION")):
            self.assertEqual(EV._stage_for(p, V.instrument_version(name), reg)["stage"], "AUTHOR_TESTED", p)
        for g in ("G-BIND", "G-INV", "G-RECOMP"):
            self.assertEqual(EV.gate_authority(g, V.instrument_version(g), reg),
                             {"status": "QUALIFIED", "stage": "AUTHOR_TESTED"}, g)
        # Without the fire receipt bytes A2 does not hold.
        reg = EV.Registry(EV.Bundle({}, {}, [], stage_records=recs, blobs={}), store)
        self.assertIn("NO_FIRE_TEST", EV.gate_authority("G-BIND", V.instrument_version("G-BIND"), reg)["why"])


if __name__ == "__main__":
    unittest.main()
