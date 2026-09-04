"""The specimen gate must refuse the attack Harmonia actually landed, not a sanitised version.

Her finding (I-CLIENT-GATE-UNENFORCED): SFE accepts corrupt organism bytes when the caller
supplies a plausible client-asserted blob_hash. Every test here is that attack, or a near miss
around it.
"""
from __future__ import annotations

import json
import os
import unittest

from proteus.foundry.affordances import AFFORDANCE_HASH
from proteus.foundry.identity import RUNTIME_HASH, hash_obj
from proteus.integration.specimen_gate import canonical_blob, verify_specimen

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.join(os.path.dirname(HERE), "integration", "PLAYER_REGISTRY.json")


def _specimen():
    reg = json.load(open(REG, encoding="utf-8"))
    e = reg["entries"][0]
    return e["manifest"], e["organism_id"]


class TheAttack(unittest.TestCase):
    def test_honest_specimen_passes(self):
        m, oid = _specimen()
        r = verify_specimen(canonical_blob(m), "sha256:" + oid)
        self.assertTrue(r["ok"])
        self.assertTrue(r["bytes"]["ok"])
        self.assertTrue(r["shape"]["ok"])

    def test_corrupt_bytes_with_plausible_claimed_hash_are_refused(self):
        """Harmonia's exact probe."""
        m, oid = _specimen()
        blob = bytearray(canonical_blob(m))
        blob[20] = (blob[20] + 1) % 128
        r = verify_specimen(bytes(blob), "sha256:" + oid)
        self.assertFalse(r["ok"])
        self.assertFalse(r["bytes"]["ok"])

    def test_valid_but_non_canonical_bytes_are_refused(self):
        """Parses, validates, and would hash differently on the next hop. That is a defect."""
        m, _ = _specimen()
        pretty = json.dumps(m, sort_keys=True, indent=2).encode("utf-8")
        r = verify_specimen(pretty)
        self.assertFalse(r["ok"])
        self.assertFalse(r["shape"]["ok"])
        self.assertIn("canonical", r["shape"]["reason"])

    def test_bytes_that_are_not_a_manifest_are_refused(self):
        r = verify_specimen(b'{"schema_version":"proteus.player_manifest.v0"}')
        self.assertFalse(r["ok"])
        self.assertFalse(r["shape"]["ok"])

    def test_non_json_is_refused_without_raising(self):
        r = verify_specimen(b"\xff\xfe not json at all")
        self.assertFalse(r["ok"])
        self.assertFalse(r["shape"]["ok"])

    def test_malformed_claim_form_is_refused(self):
        m, oid = _specimen()
        r = verify_specimen(canonical_blob(m), oid)          # missing the sha256: prefix
        self.assertFalse(r["ok"])
        self.assertIn("sha256:", r["bytes"]["reason"])


class MeaningIsNeverSilentlyTrue(unittest.TestCase):
    def test_meaning_is_unverified_when_nothing_is_claimed(self):
        m, oid = _specimen()
        r = verify_specimen(canonical_blob(m), "sha256:" + oid)
        self.assertIsNone(r["meaning"]["ok"])
        self.assertIn("UNVERIFIED", r["meaning"]["reason"])

    def test_wrong_affordance_table_is_refused(self):
        m, oid = _specimen()
        r = verify_specimen(canonical_blob(m), "sha256:" + oid,
                            expect_affordance_hash="0" * 64)
        self.assertFalse(r["ok"])
        self.assertFalse(r["meaning"]["ok"])

    def test_wrong_runtime_is_refused(self):
        m, oid = _specimen()
        r = verify_specimen(canonical_blob(m), "sha256:" + oid, expect_runtime_hash="0" * 64)
        self.assertFalse(r["ok"])
        self.assertFalse(r["meaning"]["ok"])

    def test_matching_interpretation_passes(self):
        m, oid = _specimen()
        r = verify_specimen(canonical_blob(m), "sha256:" + oid,
                            expect_runtime_hash=RUNTIME_HASH,
                            expect_affordance_hash=AFFORDANCE_HASH)
        self.assertTrue(r["ok"])
        self.assertTrue(r["meaning"]["ok"])


class CanonicalBlobIsTheOnlySerialiser(unittest.TestCase):
    def test_blob_hash_equals_sha256_prefix_plus_organism_id(self):
        """The property Harmonia relied on across worlds: blob_hash == 'sha256:' + organism_id."""
        m, oid = _specimen()
        r = verify_specimen(canonical_blob(m))
        self.assertEqual(r["bytes"]["computed_blob_hash"], "sha256:" + oid)
        self.assertEqual(hash_obj(m), oid)

    def test_all_committed_specimens_round_trip_through_the_gate(self):
        reg = json.load(open(REG, encoding="utf-8"))
        for e in reg["entries"]:
            r = verify_specimen(canonical_blob(e["manifest"]), "sha256:" + e["organism_id"])
            self.assertTrue(r["ok"], e["organism_id"])


if __name__ == "__main__":
    unittest.main()
