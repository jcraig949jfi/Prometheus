"""Tests for the Harmonia integration surface: registry contract, determinism, and the two
architectural guarantees that are easy to break by accident.

The two guarantees under test are not stylistic:

  1. EXTRINSIC OBSERVATION CANNOT ALTER IDENTITY. If this breaks, phenotype data starts changing
     organism ids and the whole "UNKNOWN is a permanent legitimate state" design collapses.

  2. NO SEMANTIC TAXONOMY EXISTS. A scan asserts that no authored player-type vocabulary appears
     anywhere in the registry. If someone later adds "explorer" or a quality score, this fails.
"""
from __future__ import annotations

import json
import os

import pytest

from proteus.foundry.vm import ManifestError, Player, validate_manifest
from proteus.integration import menagerie, registry as R

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(HERE, "integration", "PLAYER_REGISTRY.json")

#: Vocabulary that must never appear in the registry. Proteus players are semantically sterile;
#: what a specimen is FOR is the arena's discovery, not an attribute of the specimen.
FORBIDDEN = ("explorer", "predator", "learner", "cooperator", "strategist", "memory-player",
             "random-player", "arithmetic-player", "fitness", "quality", "rank", "score",
             "best", "worst", "useful", "useless", "garbage")


@pytest.fixture(scope="module")
def reg():
    return R.load(REGISTRY_PATH)


# ------------------------------------------------------------------ contract

def test_registry_validates(reg):
    R.validate_registry(reg)
    assert reg["schema_version"] == R.REGISTRY_SCHEMA
    assert len(reg["entries"]) == menagerie.POPULATION_SIZE


def test_organism_id_is_hash_of_manifest(reg):
    from proteus.foundry.identity import hash_obj
    for e in reg["entries"]:
        assert hash_obj(e["manifest"]) == e["organism_id"]


def test_every_manifest_is_valid_under_the_authoritative_validator(reg):
    for e in reg["entries"]:
        validate_manifest(e["manifest"])
        assert e["validation"]["manifest_valid"] is True
        assert e["validation"]["validator"] == "proteus.foundry.vm.validate_manifest"


def test_resource_envelope_matches_manifest(reg):
    for e in reg["entries"]:
        assert R.resource_envelope(e["manifest"]) == e["resource_envelope"]


def test_ids_unique(reg):
    ids = R.enumerate_ids(reg)
    assert len(ids) == len(set(ids))


# ------------------------------------------------------------------ fail closed

def test_unknown_field_rejected(reg):
    with pytest.raises(R.RegistryError, match="unknown field"):
        R.validate_entry(dict(reg["entries"][0], surprise=1))


def test_unknown_schema_version_rejected(reg):
    with pytest.raises(R.RegistryError, match="unknown entry schema_version"):
        R.validate_entry(dict(reg["entries"][0], schema_version="proteus.v999"))
    with pytest.raises(R.RegistryError, match="unknown registry schema_version"):
        R.validate_registry(dict(reg, schema_version="proteus.v999"))


def test_missing_field_rejected(reg):
    broken = {k: v for k, v in reg["entries"][0].items() if k != "provenance"}
    with pytest.raises(R.RegistryError, match="missing required field"):
        R.validate_entry(broken)


def test_tampered_manifest_rejected(reg):
    e = json.loads(json.dumps(reg["entries"][0]))
    e["manifest"]["tick_budget"] = 32
    with pytest.raises(R.RegistryError):
        R.validate_entry(e)


def test_tampered_registry_id_rejected(reg):
    with pytest.raises(R.RegistryError, match="registry_id"):
        R.validate_registry(dict(reg, registry_id="0" * 64))


def test_duplicate_organism_rejected(reg):
    dup = dict(reg)
    dup["entries"] = [reg["entries"][0], reg["entries"][0]]
    dup["registry_id"] = R.hash_obj({"schema_version": dup["schema_version"],
                                     "build": dup["build"],
                                     "entry_ids": [e["entry_id"] for e in dup["entries"]]})
    with pytest.raises(R.RegistryError, match="duplicate"):
        R.validate_registry(dup)


def test_unknown_organism_id_raises(reg):
    with pytest.raises(R.RegistryError, match="unknown organism_id"):
        R.get_manifest(reg, "0" * 64)


def test_missing_registry_file_raises(tmp_path):
    with pytest.raises(R.RegistryError, match="no registry"):
        R.load(str(tmp_path / "nope.json"))


# ------------------------------------------------------------------ guarantee 1: identity

def test_extrinsic_write_cannot_change_entry_id(reg):
    e = json.loads(json.dumps(reg["entries"][0]))
    before = e["entry_id"]
    e["extrinsic"]["phenotype"] = "explorer"
    e["extrinsic"]["score"] = 0.99
    e["extrinsic"]["encounters"] = [{"world": "anything", "result": "won"}]
    assert R.compute_entry_id(e) == before
    R.validate_entry(e)          # extrinsic is the one OPEN namespace: this must still validate


def test_extrinsic_write_cannot_change_organism_id(reg):
    e = json.loads(json.dumps(reg["entries"][0]))
    e["extrinsic"]["phenotype"] = "predator"
    from proteus.foundry.identity import hash_obj
    assert hash_obj(e["manifest"]) == e["organism_id"]


def test_phenotype_defaults_to_unknown(reg):
    for e in reg["entries"]:
        assert e["extrinsic"]["phenotype"] == "UNKNOWN"


def test_intrinsic_view_excludes_extrinsic(reg):
    v = R.intrinsic_view(reg["entries"][0])
    assert "extrinsic" not in v and "entry_id" not in v
    assert "manifest" in v and "provenance" in v


# ------------------------------------------------------------------ guarantee 2: no taxonomy

def test_no_semantic_taxonomy_anywhere_in_registry():
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        blob = f.read().lower()
    # 'phenotype' appears only as the literal UNKNOWN placeholder; the vocabulary below must not.
    found = [w for w in FORBIDDEN if w in blob]
    assert not found, f"semantic/quality vocabulary leaked into the registry: {found}"


def test_registry_has_no_ordering_or_ranking_field(reg):
    for e in reg["entries"]:
        assert not any(k in e for k in ("rank", "score", "quality", "fitness", "tier"))


# ------------------------------------------------------------------ qualification visibility

def test_source_qualification_states_the_v0_6_limitation(reg):
    q = reg["source_qualification"]
    assert q["mutation_neutrality"] == "NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT"
    assert q["operational_significance"] == "NOT_YET_ADJUDICATED"
    assert q["permitted_use"] == "USE_A_FROZEN_SPECIMEN_SOURCE"
    assert q["prohibited_use"] == "USE_B_NEUTRAL_EVOLUTIONARY_OPERATOR"
    assert "not reversible" in q["plain_statement"].lower()


# ------------------------------------------------------------------ determinism

def test_population_rebuild_is_identical(reg):
    rebuilt, _ = menagerie.build_population()
    assert rebuilt["registry_id"] == reg["registry_id"]
    assert [e["organism_id"] for e in rebuilt["entries"]] == R.enumerate_ids(reg)


def test_serialization_is_deterministic(reg, tmp_path):
    from proteus.foundry.identity import canonical_json
    a = canonical_json(reg)
    b = canonical_json(R.load(REGISTRY_PATH))
    assert a == b


def test_population_retains_structural_variety(reg):
    env = [e["resource_envelope"] for e in reg["entries"]]
    assert len({x["tape_words"] for x in env}) >= 5
    assert len({x["persist"] for x in env}) == 4
    assert len({x["code_writable"] for x in env}) == 2
    assert len({x["tick_budget"] for x in env}) >= 3


def test_no_specimen_was_filtered_out(reg):
    b = reg["build"]
    assert b["generated"] == b["requested"]
    assert b["registered"] == b["generated"]
    assert b["rejected_invalid_manifest"] == 0
    assert "NONE beyond manifest validity" in b["selection_rule"]


# ------------------------------------------------------------------ ABI round trip

def test_checkpoint_restore_round_trip(reg):
    from proteus.foundry.lineage import checkpoint, restore
    from proteus.foundry.prng import SplitMix64
    e = reg["entries"][0]
    p = Player(e["manifest"])
    st = p.fresh_state()
    p.run_tick(st, [[1, 2]], 1, SplitMix64(7))
    snap = checkpoint(e["organism_id"], st, "t", 1)
    assert restore(snap) == st


def test_restore_refuses_foreign_runtime():
    from proteus.foundry.lineage import restore
    with pytest.raises(ValueError, match="different runtime"):
        restore({"runtime_hash": "0" * 64,
                 "state": {"tape": [], "regs": [], "ip": 0, "ticks": 0}})


def test_player_rejects_invalid_manifest(reg):
    with pytest.raises(ManifestError):
        Player(dict(reg["entries"][0]["manifest"], tape_words=7))


def test_budget_cannot_exceed_manifest(reg):
    from proteus.foundry.prng import SplitMix64
    from proteus.foundry.vm import Meter
    e = reg["entries"][0]
    p = Player(e["manifest"])
    st = p.fresh_state()
    m = Meter()
    p.run_tick(st, [[1]], 1, SplitMix64(3), meter=m, budget=10 ** 9)
    assert m.ops <= e["resource_envelope"]["tick_budget"]


def test_out_cap_respected(reg):
    from proteus.foundry.prng import SplitMix64
    for e in reg["entries"][:12]:
        p = Player(e["manifest"])
        st = p.fresh_state()
        outs, _ = p.run_tick(st, [[5, 9]], 3, SplitMix64(11))
        for ch in outs:
            assert len(ch) <= e["resource_envelope"]["out_cap"]


# ------------------------------------------------------------------ schema doc cannot drift

def test_schema_document_matches_the_code():
    """The contract doc is descriptive; this binds it to the authoritative Python constants."""
    p = os.path.join(HERE, "contracts", "player_registry.schema.v1.json")
    with open(p, encoding="utf-8") as f:
        doc = json.load(f)
    assert doc["properties"]["schema_version"]["const"] == R.REGISTRY_SCHEMA
    assert doc["required"] == list(R.REGISTRY_REQUIRED)
    e = doc["$defs"]["entry"]
    assert e["properties"]["schema_version"]["const"] == R.ENTRY_SCHEMA
    assert e["required"] == list(R.ENTRY_REQUIRED)
    assert e["properties"]["identity"]["required"] == list(R.IDENTITY_REQUIRED)
    assert e["properties"]["provenance"]["required"] == list(R.PROVENANCE_REQUIRED)
    assert e["properties"]["resource_envelope"]["required"] == list(R.ENVELOPE_REQUIRED)
    assert e["properties"]["validation"]["required"] == list(R.VALIDATION_REQUIRED)
    # extrinsic must remain the ONLY open namespace
    assert e["properties"]["extrinsic"]["additionalProperties"] is True
    assert e["additionalProperties"] is False
    assert doc["additionalProperties"] is False
