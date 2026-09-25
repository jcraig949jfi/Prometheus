"""TECHNE-124: one canonical far-end key on lineage edges ("to"), the drifted "target" refused,
the migration byte-safe and idempotent, and the tracked tree clean of the drift."""
from __future__ import annotations

import json
import pathlib
import re
import shutil

import pytest

from techne.fossils import record
from techne.fossils import migrate_lineage_key_20260925 as mig
from techne.fossils import vault

SPEC = vault.REPO / "techne" / "fossils" / "specimens"
FOSSILS_PKG = vault.REPO / "techne" / "fossils"


def _edge_problems(e):
    return [p for p in record.lineage_edge_problems(e)]


def test_validator_accepts_canonical_key():
    assert _edge_problems({"relation": "derived_from", "to": "lenia-chan-2019", "note": ""}) == []


def test_validator_refuses_drifted_key_by_name():
    probs = _edge_problems({"relation": "derived_from", "target": "lenia-chan-2019", "note": ""})
    assert any("'target'" in p and "canonical key is 'to'" in p for p in probs), probs


def test_validator_refuses_missing_or_empty_to():
    assert _edge_problems({"relation": "derived_from", "note": ""})
    assert _edge_problems({"relation": "derived_from", "to": "   "})
    assert _edge_problems({"relation": "derived_from", "to": None})


def test_record_validate_surfaces_edge_problem():
    rec = record.skeleton("x-spec")
    rec["lineage_relations"] = [{"relation": "derived_from", "target": "y"}]
    assert any("canonical key is 'to'" in p for p in record.validate(rec))


def test_rename_edge_preserves_position_and_other_bytes():
    e = {"relation": "derived_from", "target": "x", "note": "n", "extra": 1}
    out, changed = mig.rename_edge(e)
    assert changed and list(out) == ["relation", "to", "note", "extra"] and out["to"] == "x" and out["extra"] == 1


def test_rename_edge_refuses_ambiguous_and_empty():
    with pytest.raises(ValueError):
        mig.rename_edge({"relation": "r", "target": "x", "to": "y"})
    with pytest.raises(ValueError):
        mig.rename_edge({"relation": "r", "target": ""})


def _fixture_tree(tmp_path: pathlib.Path) -> pathlib.Path:
    d = tmp_path / "specimens"
    (d / "a").mkdir(parents=True)
    rec = {"specimen_id": "a", "lineage_relations": [{"relation": "derived_from", "target": "b", "note": ""},
                                                     {"relation": "algorithm_from", "to": "c", "note": ""}]}
    (d / "a" / "record.json").write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8", newline="\n")
    cap = {"specimen_id": "a", "lineage": {"stage": "S0", "relations": [{"relation": "derived_from", "target": "b", "note": ""}]}}
    (d / "a" / "CAPSULE.json").write_text(json.dumps(cap, indent=1) + "\n", encoding="utf-8", newline="\n")
    return d


def test_migration_renames_then_is_idempotent(tmp_path):
    d = _fixture_tree(tmp_path)
    r1 = mig.run(d, write=True)
    assert r1["edges_renamed"] == 2 and r1["by_status"] == {"RENAMED": 2}
    rec = json.loads((d / "a" / "record.json").read_text(encoding="utf-8"))
    assert [list(e) for e in rec["lineage_relations"]] == [["relation", "to", "note"], ["relation", "to", "note"]]
    cap = json.loads((d / "a" / "CAPSULE.json").read_text(encoding="utf-8"))
    assert cap["lineage"]["relations"][0]["to"] == "b" and "target" not in cap["lineage"]["relations"][0]
    r2 = mig.run(d, write=True)
    assert r2["edges_renamed"] == 0 and r2["by_status"] == {"UNCHANGED": 2}


def test_migration_dry_run_writes_nothing(tmp_path):
    d = _fixture_tree(tmp_path)
    before = (d / "a" / "record.json").read_bytes()
    r = mig.run(d, write=False)
    assert r["by_status"] == {"WOULD_RENAME": 2}
    assert (d / "a" / "record.json").read_bytes() == before


def test_migration_refuses_to_reformat(tmp_path):
    """Control: a record whose on-disk formatting is not the writer's convention is left alone."""
    d = _fixture_tree(tmp_path)
    p = d / "a" / "record.json"
    doc = json.loads(p.read_text(encoding="utf-8"))
    p.write_text(json.dumps(doc, indent=4) + "\n", encoding="utf-8", newline="\n")   # not indent=2
    before = p.read_bytes()
    r = mig.run(d, write=True)
    rows = {x["path"].split("/")[-1] if "/" in x["path"] else x["path"]: x for x in r["files"]}
    assert any(x["status"] == "FORMAT_MISMATCH" for x in r["files"])
    assert p.read_bytes() == before


@pytest.mark.skipif(not SPEC.exists(), reason="no specimens on this tree")
def test_tracked_tree_has_no_drifted_key():
    hits = []
    for p in list(SPEC.glob("*/record.json")) + list(SPEC.glob("*/CAPSULE.json")):
        doc = json.loads(p.read_text(encoding="utf-8"))
        for e in mig._edges(doc, p.name):
            if "target" in e or "to" not in e:
                hits.append((p.name, p.parent.name, e))
    assert not hits, hits[:5]


def test_no_writer_in_the_package_emits_the_drifted_key():
    """Cheat control on the source: no lineage edge literal in techne/fossils uses "target"."""
    pat = re.compile(r'"relation"\s*:\s*"[a-z_]+"\s*,\s*"target"\s*:')
    bad = [str(p) for p in FOSSILS_PKG.rglob("*.py") if pat.search(p.read_text(encoding="utf-8", errors="replace"))]
    assert not bad, bad
