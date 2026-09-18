"""Executable fossil packet HANDOFF block (operator directive 4 s5, 2026-09-18): positive, cheat, absent."""
from __future__ import annotations

import copy

from techne.fossils import packet

GOOD = {
    "runtime": {"python_major": 3, "native_deps": [], "host_class": "any"},
    "entry_point": {"path": "x.py", "symbol": "f"},
    "demonstration": {"command": "python x.py", "observable": "prints 1", "runs_the_body": True, "claims": "none"},
    "license_constraints": {"spdx": "MIT", "constraints": []},
    "preservation_cost": {"class": "CHEAP", "basis": "small"},
    "fixtures": [{"name": "a", "path_or_url": "a.bin", "sha256": "0" * 64}],
}


def test_positive_block_passes():
    assert packet.validate_handoff(copy.deepcopy(GOOD)) == []


def test_absent_block_is_legacy_not_failure():
    assert packet.validate_handoff(None) == []


def test_cheat_demonstration_that_claims_a_mechanism_is_refused():
    h = copy.deepcopy(GOOD); h["demonstration"]["claims"] = "shows PATA-EC is relational"
    assert any("claims must be 'none'" in w for w in packet.validate_handoff(h))


def test_cheat_port_declared_as_the_body_is_caught_by_type():
    h = copy.deepcopy(GOOD); h["demonstration"]["runs_the_body"] = "yes"
    assert any("runs_the_body" in w for w in packet.validate_handoff(h))


def test_missing_runtime_and_cost_class_are_defects():
    h = copy.deepcopy(GOOD); del h["runtime"]["native_deps"]; h["preservation_cost"]["class"] = "FREE"
    why = packet.validate_handoff(h)
    assert any("native_deps" in w for w in why) and any("preservation_cost" in w for w in why)


def test_world_id_accepts_r36_form_and_gate_open_single_copy(monkeypatch):
    # minimal packet-level checks through validate(): fw2- id and PRESERVATION_GATE_OPEN with one copy
    from techne.tests import test_fossil_packet as tfp
    p = copy.deepcopy(tfp.GZ)
    p["FOSSIL_WORLD_ID"] = "fw2-" + "a" * 64
    p["PRESERVATION"]["copies"] = [c for c in p["PRESERVATION"]["copies"] if c["failure_domain"] == "M1"]
    why = packet.validate(p)
    assert any("fewer than 2" in w for w in why)
    p["PRESERVATION_STATUS"] = "PRESERVATION_GATE_OPEN"
    why = packet.validate(p)
    assert not any("fewer than 2" in w for w in why) and not any("FOSSIL_WORLD_ID" in w for w in why)
