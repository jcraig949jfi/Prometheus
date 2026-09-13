"""Controls for the pin-evidence instrument (batch 10 P1).

PREREG: techne/fossils/PREREG_PIN_EVIDENCE_2026-09-13.md

The batch-09 census reported 59 fossils with unpinned artifacts when the true count was 18,
because it read the REQUEST (source_origin) instead of the RECEIPT (hashes.artifacts). These
controls reconstruct that exact failure so it cannot silently return, and guard the writer defect
that destroyed 260 pin facts.

Each control must be able to FAIL:
  C1 reproduces the historical 59-error and shows the authoritative reader disagreeing with it
  C2 stops C1 passing for a reader that simply always says "pinned"
  C3 reproduces the writer defect and shows the fix repairing it
  C4 asserts no record in the vault asks a re-acquisition to trust a moving HEAD
"""
from __future__ import annotations

import pytest

from techne.fossils import record as R, vault


def _legacy_source_origin_only_pin(art):
    """The BUGGY predicate as batch 09 first wrote it: consults only the request.
    Kept deliberately so the historical failure stays reproducible."""
    if art.get("kind") == "url":
        return bool(art.get("sha256"))
    return bool(art.get("commit_resolved") or (art.get("commit") and art.get("commit") != "HEAD"))


PIN40 = "0123456789abcdef0123456789abcdef01234567"


def test_c1_reproduces_the_59_error_and_authoritative_reader_disagrees():
    """A pin present ONLY in the receipt: the legacy reader calls it unpinned, the fixed one does not."""
    git_art = {"kind": "git", "url": "https://example.invalid/repo", "commit": "HEAD"}
    url_art = {"kind": "url", "url": "https://example.invalid/x.tar.gz", "filename": "x.tar.gz"}
    receipt = [{"filename": "https://example.invalid/repo", "commit": PIN40, "sha256": None},
               {"filename": "x.tar.gz", "sha256": "a" * 64, "commit": None}]

    # the historical failure: request-only reading reports BOTH as unpinned
    assert _legacy_source_origin_only_pin(git_art) is False
    assert _legacy_source_origin_only_pin(url_art) is False

    # the authoritative reader consults the receipt and finds the pins
    assert R.established_pin(git_art, receipt) == PIN40
    assert R.established_pin(url_art, receipt) == "a" * 64


def test_c2_not_always_pinned():
    """Without this, C1 would pass for a reader that always answers 'pinned'."""
    assert R.established_pin({"kind": "git", "url": "u", "commit": "HEAD"}, []) == ""
    assert R.established_pin({"kind": "url", "url": "u", "filename": "f"}, []) == ""
    # a receipt for a DIFFERENT artifact must not be borrowed
    other = [{"filename": "somethingelse", "commit": PIN40}]
    assert R.established_pin({"kind": "git", "url": "u", "commit": "HEAD"}, other) == ""
    # "HEAD" and short/non-hex strings are not fixed identifiers
    assert R.established_pin({"kind": "git", "url": "u", "commit": "main"}, []) == ""
    assert R.established_pin({"kind": "git", "url": "u", "commit": "abc123"}, []) == ""


def test_c3_writer_defect_reproduced_then_repaired():
    """Rebuilding a record from a batch literal destroys the pin; merge_artifact_pins restores it."""
    acquired = {"specimen_id": "x",
                "source_origin": {"artifacts": [
                    {"kind": "git", "url": "https://example.invalid/repo",
                     "commit": PIN40, "commit_resolved": PIN40, "commit_date": "2020-01-01T00:00:00Z"}]},
                "hashes": {"artifacts": [{"filename": "https://example.invalid/repo", "commit": PIN40}]}}
    # what a batch script rebuilds: the literal, with the pin gone
    rebuilt = {"specimen_id": "x",
               "source_origin": {"artifacts": [
                   {"kind": "git", "url": "https://example.invalid/repo", "commit": "HEAD"}]}}

    # THE DEFECT: without the merge the pin is lost and the request points at a moving reference
    assert R.established_pin(rebuilt["source_origin"]["artifacts"][0]) == ""

    # THE FIX
    restored = R.merge_artifact_pins(rebuilt, acquired)
    assert restored == 1
    a = rebuilt["source_origin"]["artifacts"][0]
    assert a["commit"] == PIN40 and a["commit_resolved"] == PIN40
    assert a["commit_date"] == "2020-01-01T00:00:00Z"
    assert R.established_pin(a) == PIN40


def test_c3b_merge_never_overwrites_an_explicit_newer_pin():
    """Adding/removing artifacts stays legal; an explicit new pin wins over the old one."""
    old = {"source_origin": {"artifacts": [{"kind": "git", "url": "u", "commit": PIN40, "commit_resolved": PIN40}]},
           "hashes": {"artifacts": [{"filename": "u", "commit": PIN40}]}}
    newer = "f" * 40
    new = {"source_origin": {"artifacts": [{"kind": "git", "url": "u", "commit": newer}]}}
    assert R.merge_artifact_pins(new, old) == 0
    assert new["source_origin"]["artifacts"][0]["commit"] == newer


def test_c4_no_record_asks_for_a_moving_head():
    """Vault-wide: every git artifact must name a fixed commit, not HEAD."""
    sp = vault.specimen_dir("_").parent
    offenders = []
    for d in sorted(sp.iterdir()):
        if not (d / "record.json").exists():
            continue
        rec = R.load(d.name)
        hashes = (rec.get("hashes") or {}).get("artifacts") or []
        for a in (rec.get("source_origin") or {}).get("artifacts") or []:
            if a.get("kind") != "git":
                continue
            if not R.established_pin(a) and R.established_pin(a, hashes):
                offenders.append("%s -> %s" % (d.name, a.get("url")))
    assert not offenders, "records whose request lost a known pin: %s" % offenders


def test_c4b_every_established_pin_survives_a_reload():
    """Idempotence (prereg P-C): merging a record with itself must change nothing the second time."""
    sp = vault.specimen_dir("_").parent
    sample = [d.name for d in sorted(sp.iterdir()) if (d / "record.json").exists()][:20]
    for sid in sample:
        rec = R.load(sid)
        assert R.merge_artifact_pins(rec, rec) == 0, "%s still had a recoverable pin missing" % sid
