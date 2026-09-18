"""The FOSSIL PACKET validator (Amendment 2, R17/R18/R21/R22/R25/R30).
Positive: the gzip pilot packet validates. Cheats: rounding TECHNE_STATE up to BEHAVIOR_REPRODUCED
without evidence fails; a state below the handoff requirement fails; an image digest offered as
FOSSIL_WORLD_ID fails; one preservation copy fails; a missing downstream key fails; an absent
measured_and_rejected list fails (empty is a statement, absence is not). World id is stable
under image-digest change and moves under manifest change.
"""
from __future__ import annotations

import copy
import json
import pathlib

from techne.fossils import packet, vault

GZ = json.loads((vault.SPECIMENS / "gzip-1.2.4-1993" / "FOSSIL_PACKET.json").read_text(encoding="utf-8"))


def test_gzip_packet_is_valid():
    assert packet.validate(GZ) == []


def test_cheat_round_up_state_without_evidence_fails():
    p = copy.deepcopy(GZ); p["TECHNE_STATE"] = "BEHAVIOR_REPRODUCED"
    assert any("BEHAVIOR_EVIDENCE" in w for w in packet.validate(p))


def test_state_below_handoff_requirement_fails_only_when_handoff_requested():
    p = copy.deepcopy(GZ); p["TECHNE_STATE"] = "WORLD_EXECUTABLE"
    assert p["HANDOFF_REQUESTED"] is True
    assert any("below REQUIRED_STATE_FOR_HANDOFF" in w for w in packet.validate(p))
    p["HANDOFF_REQUESTED"] = False
    assert packet.validate(p) == [], "parked below its requirement is a valid packet"


def test_image_digest_is_not_a_world_id():
    p = copy.deepcopy(GZ); p["FOSSIL_WORLD_ID"] = "sha256:5d33974496e0"
    assert any("measurement-based" in w for w in packet.validate(p))


def test_single_failure_domain_fails_r25():
    p = copy.deepcopy(GZ); p["PRESERVATION"]["copies"] = [c for c in p["PRESERVATION"]["copies"] if c["failure_domain"] == "M1"]
    assert any("R25" in w for w in packet.validate(p))


def test_missing_downstream_key_fails():
    p = copy.deepcopy(GZ); del p["CUT_ID"]
    assert any("CUT_ID" in w for w in packet.validate(p))


def test_absent_rejected_list_fails_but_empty_passes():
    p = copy.deepcopy(GZ); del p["SCAFFOLDING_LEDGER"]["measured_and_rejected"]
    assert any("measured_and_rejected" in w for w in packet.validate(p))
    assert packet.validate(GZ) == []


def test_world_id_stable_under_witness_change_and_moves_under_manifest_change():
    a = packet.fossil_world_id("d" * 64, "m" * 64, ["gcc 12"])
    assert a == packet.fossil_world_id("d" * 64, "m" * 64, ["gcc 12"])      # image digest is not an input at all
    assert a != packet.fossil_world_id("d" * 64, "n" * 64, ["gcc 12"])
    assert a != packet.fossil_world_id("d" * 64, "m" * 64, ["gcc 13"])


def test_capability_matrix_must_match_worlds_registry():
    p = copy.deepcopy(GZ); p["CAPABILITY_MATRIX"]["STEP"] = "yes"
    assert any("differs from WORLDS.json" in w for w in packet.validate(p))
    p = copy.deepcopy(GZ); p["FOSSIL_WORLD"]["name"] = "prometheus-fossil-nonexistent:bookworm"
    assert any("not in techne/fossils/WORLDS.json" in w for w in packet.validate(p))


def test_worlds_registry_covers_every_dockerfile_and_every_verb():
    reg = packet.worlds_registry()["worlds"]
    import glob
    dfs = {pathlib.Path(x).as_posix() for x in glob.glob("techne/fossils/environment/*.Dockerfile")} | {"techne/fossils/specimens/go-explore-uber-2022/environment/go-explore-min.Dockerfile"}
    # container worlds are identified by their Dockerfile; a native world (R36, 2026-09-18) by its canonical manifest
    assert {w["dockerfile"] for w in reg.values() if "dockerfile" in w} == dfs
    for name, w in reg.items():
        if "dockerfile" not in w:
            assert w.get("class") == "native_python" and pathlib.Path(w["manifest"]).exists(), name
            assert str(w.get("FOSSIL_WORLD_ID", "")).startswith("fw2-"), name
    for name, w in reg.items():
        assert set(w["capabilities"]) == set(packet.VERBS), name
        assert set(w["capabilities"].values()) <= {"yes", "no", "partial"}, name
