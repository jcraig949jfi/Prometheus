"""TECHNE-129: a fossil record may not ship with an empty nyx_handoff unless a CAPSULE.json is its
handoff. Harmonia #1064 found poet-original-2019 empty; 49 of 169 records were (every record since
batch 14), and nothing failed because test_fossils.py only checks that the five KEYS exist.

Controls:
  tree      every tracked record has a non-empty handoff, or a CAPSULE.json beside it
  cheat     a fresh skeleton (the state every batch script writes) is detected as empty
  positive  handoff_of() on a pinned git record fills all five fields and names source type + pin
  guard     fill() never overwrites a handoff that already says something; no drive letter is written
"""
import json
import re

import pytest

from techne.fossils import record, vault
from techne.fossils.batches import finalize_handoff_20260930 as fin

SPECIMENS = vault.specimen_dir("_").parent
_DRIVE = re.compile(r"[A-Za-z]:[\\/]")


def _skeleton(**kw):
    base = dict(
        canonical_name="X", aliases=[], lineage="l", domain=["d"], era="2026", version="v",
        source_origin={"artifacts": [{"kind": "git", "url": "https://example.org/x", "commit": "a" * 40}]},
        source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "example.org/x"},
        license={"spdx": "MIT", "status": "permissive", "evidence": "LICENSE"},
        language=["Python"], build_system="none", compiler_or_interpreter="CPython 3", dependencies=[],
        entry_points=["main.py"], example={"command": "python main.py", "input": "", "output": ""},
        environment={"runner": "native"}, upstream_docs=["README"],
        human_capability_summary={"built_to": "do the thing", "pressure": "p", "success_means": "s"})
    base.update(kw)
    return record.skeleton("x-test", **base)


def test_cheat_control_a_fresh_skeleton_is_detected_as_empty():
    assert fin.is_empty(_skeleton()) is True


def test_positive_control_handoff_fills_all_five_fields_from_the_record():
    rec = _skeleton()
    rec["hashes"] = {"tree_sha256": "b" * 64}
    h = fin.handoff_of(rec)
    assert set(h) == set(fin.FIELDS) and all(h[k].strip() for k in fin.FIELDS)
    assert "ORIGINAL_AUTHORITATIVE_RELEASE" in h["where_it_came_from"]
    assert "commit " + "a" * 40 in h["where_it_came_from"] and "licence MIT" in h["where_it_came_from"]
    assert h["what_humans_used_it_for"] == "do the thing"
    assert "we do not" in h["how_we_know_it_runs"]            # NOT_ATTEMPTED is never reported as running
    rec["nyx_handoff"] = h
    assert fin.is_empty(rec) is False


def test_handoff_carries_no_drive_letter_or_host_path():
    h = fin.handoff_of(_skeleton())
    for k, v in h.items():
        assert not _DRIVE.search(v.replace("https://", "")), (k, v)
    assert "<vault>/x-test" in h["here_is_the_machine"]


def test_fill_never_overwrites_an_existing_handoff(tmp_path, monkeypatch):
    monkeypatch.setattr(vault, "SPECIMENS", tmp_path)
    monkeypatch.setattr(vault, "specimen_dir", lambda sid: tmp_path / sid)
    monkeypatch.setattr(record, "path", lambda sid: tmp_path / sid / "record.json")
    rec = _skeleton()
    rec["hashes"] = {"tree_sha256": "b" * 64, "n_files": 1, "bytes": 1, "artifacts": []}
    rec["nyx_handoff"]["where_it_came_from"] = "a human wrote this"
    record.save(rec)
    before = (tmp_path / "x-test" / "record.json").read_bytes()
    assert fin.fill("x-test", write=True) == "KEPT"
    assert (tmp_path / "x-test" / "record.json").read_bytes() == before


def test_tracked_tree_has_no_empty_handoff_without_a_capsule():
    bad = []
    for d in sorted(SPECIMENS.iterdir()):
        rp = d / "record.json"
        if not rp.exists():
            continue
        rec = json.loads(rp.read_text(encoding="utf-8"))
        if fin.is_empty(rec) and not (d / "CAPSULE.json").exists():
            bad.append(d.name)
    assert not bad, ("records with an empty nyx_handoff and no CAPSULE.json (run a finalize step "
                     "before committing a new record): %s" % bad)
