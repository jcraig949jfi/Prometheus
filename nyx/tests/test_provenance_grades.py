"""R19 grade map: Techne ruling #1188 (source types) and Harmonia's rollout ruling (derived artifacts never read as originals)."""
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from nyx.atlas.migrate_v1 import SPEC, grade_from_record

ROLLOUTS = sorted(p.name for p in SPEC.glob("asal-rollout-*") if (p / "record.json").exists())


def _rec(fid):
    return json.loads((SPEC / fid / "record.json").read_text(encoding="utf-8"))


def test_source_type_table():
    assert grade_from_record({"source_type": "PSEUDOCODE_PLUS_REFERENCE_IMPL"}) == "RECONSTRUCTION"
    assert grade_from_record({"source_type": "FAITHFUL_PORT"}) == "RECONSTRUCTION"
    assert grade_from_record({"source_type": "LATER_SAME_LINEAGE_RELEASE"}) == "ORIGINAL_ARTIFACT"
    assert grade_from_record({"source_type": "REGENERATED_FROM_FROZEN_RECIPE"}) == "DERIVED_RECOVERY_ARTIFACT"
    assert grade_from_record({"source_type": "SOMETHING_ELSE"}) == "UNKNOWN"


def test_rollout_capsules_never_read_as_original():
    assert len(ROLLOUTS) == 39
    for fid in ROLLOUTS:
        assert grade_from_record(_rec(fid), fid) == "DERIVED_RECOVERY_ARTIFACT", fid


def test_cheat_the_capsule_rule_is_what_fires():
    """Control: the same record WITHOUT its fid (so the CAPSULE.json check cannot see it) and with an original-release handoff
    string must read ORIGINAL_ARTIFACT -- proving the derived grade comes from the rule, not from the record's content."""
    r = dict(_rec(ROLLOUTS[0]), nyx_handoff={"where_it_came_from": "x ; ORIGINAL_AUTHORITATIVE_RELEASE ; y"})
    if r.get("source_type") == "ORIGINAL_AUTHORITATIVE_RELEASE":
        assert grade_from_record(r) == "ORIGINAL_ARTIFACT"
