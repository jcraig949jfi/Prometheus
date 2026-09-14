"""Manifest verification with uncovered-file report (LAYER: NECROPOLIS ADAPTER).

ORIGINAL SCIENTIFIC LOGIC: comms/manifest.py -- artifact_hash (sha256 over
LF-normalised bytes), entries, verify, LINE.  Called UNCHANGED.  The adapter
adds what verify() does not report: files in the directory the manifest never
lists, files in subdirectories (never covered by design), and the manifest's
own hash (nothing anchors it -- a rewritten MANIFEST.md passes verify; see
run_controls.py::comms_manifest.LAUNDERING.*).

NECROPOLIS VALIDATION: engine/necropolis/workshop/tests/run_controls.py::adapters_manifest_verify.*

Reads: one directory.  Writes: nothing.
"""
from __future__ import annotations

import importlib
from pathlib import Path


def verify_with_coverage(dirpath) -> dict:
    M = importlib.import_module("comms.manifest")
    dirpath = Path(dirpath)
    mf = dirpath / "MANIFEST.md"
    if not mf.exists():
        return {"dir": str(dirpath), "manifest_present": False, "verdict": "NO_MANIFEST"}
    checked, bad = M.verify(dirpath)
    listed = set()
    for line in mf.read_text(encoding="utf-8").splitlines():
        m = M.LINE.match(line)
        if m:
            listed.add(m.group(1))
    top_files = {p.name for p in M.entries(dirpath)}
    unlisted = sorted(top_files - listed)
    sub_files = sorted(p.relative_to(dirpath).as_posix() for p in dirpath.rglob("*")
                       if p.is_file() and p.parent != dirpath)
    verdict = "HASH_MISMATCH" if bad else ("UNCOVERED_FILES" if (unlisted or sub_files) else "COVERED")
    return {"dir": str(dirpath), "manifest_present": True, "checked": checked, "bad": bad,
            "unlisted_top_level": unlisted, "uncovered_subdirectory_files": sub_files,
            "manifest_self_hash_lf": M.artifact_hash(mf), "verdict": verdict,
            "forbidden_inference": "COVERED means every LISTED top-level file matches; it is not evidence "
                                   "that the manifest is the one originally written (no anchor outside the dir)."}
