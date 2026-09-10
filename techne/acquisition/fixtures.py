"""Fixture acquisition: the upstream data a first-useful-check or a reproduction needs.

A fixture is pinned by TWO independent identities:

    repo_blob_sha   git's own object id for the file at the pinned revision
    sha256          the digest of the bytes we received

The first is what upstream can be asked about; the second is what we actually hold. On
the first acquisition `expected_sha256` is null and the observed digest is RECORDED; the
manifest is then amended with it, and every later acquisition VERIFIES instead of
recording. That sequence is stated rather than hidden, because a "verified" hash that was
written by the same run that fetched the bytes verifies nothing.
"""
from __future__ import annotations

import hashlib
import urllib.request

from . import paths
from .budget import Budget

_UA = {"User-Agent": "prometheus-techne-acquisition/1"}


def acquire(entry: dict, budget: Budget) -> list[dict]:
    out = []
    dest_dir = paths.tool_cache() / "fixtures" / entry["id"]
    dest_dir.mkdir(parents=True, exist_ok=True)
    for fx in entry.get("fixtures", []):
        dest = dest_dir / fx["filename"]
        rec = {"id": fx["id"], "purpose": fx["purpose"], "url": fx["url"],
               "filename": fx["filename"], "repo_blob_sha": fx.get("repo_blob_sha"),
               "expected_sha256": fx.get("expected_sha256"),
               "path": str(dest)}
        if dest.exists():
            raw = dest.read_bytes()
            rec["transferred"] = False
        else:
            budget.require_network()
            budget.tick()
            req = urllib.request.Request(fx["url"], headers=_UA)
            with urllib.request.urlopen(req, timeout=180) as r:
                raw = r.read()
            budget.count_download(len(raw))
            dest.write_bytes(raw)
            rec["transferred"] = True
        rec["bytes"] = len(raw)
        rec["sha256_observed"] = hashlib.sha256(raw).hexdigest()
        # git's blob id is sha1("blob <len>\0" + bytes) -- an independent identity that can
        # be compared against what the GitHub contents API reported for the pinned revision.
        rec["git_blob_sha1_computed"] = hashlib.sha1(
            b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        if rec["expected_sha256"]:
            rec["verified"] = rec["sha256_observed"] == rec["expected_sha256"]
            rec["status"] = "VERIFIED" if rec["verified"] else "DIGEST_MISMATCH"
        else:
            rec["verified"] = None
            rec["status"] = ("RECORDED_FIRST_ACQUISITION -- expected_sha256 was null; this "
                             "run RECORDS the digest and does not verify it. Amend the "
                             "manifest with sha256_observed so the next run verifies.")
        if rec.get("repo_blob_sha"):
            rec["blob_id_matches_upstream"] = (
                rec["git_blob_sha1_computed"].startswith(rec["repo_blob_sha"])
                or rec["repo_blob_sha"].startswith(rec["git_blob_sha1_computed"][:12]))
        out.append(rec)
    return out
