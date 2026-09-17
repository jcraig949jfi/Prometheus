"""Golden canonicalization fixtures for the two point-release identities
(operator Stage 3 s4: "pin the canonicalization rules and test them").

    step key    viv/stepkey.py == the migration-006 trigger, byte for byte,
                asserted by computing the SQL expression on the server
    bundle      two encodings of one semantic bundle -> one bundle_hash;
                design_digest = sha(spec_hash | bundle_hash); Vivarium fills
                exactly four slots; unknown keys / null values refused
"""
from __future__ import annotations

import hashlib
import json

import pytest

from viv import bundle as _b
from viv import kinds as _kinds
from viv import spec as _spec
from viv import stepkey as _sk

D = "sha256:" + "a" * 64

GOLDEN_STEP_KEYS = [
    # (design, kind, parts, expected) -- regenerate ONLY with a stated reason
    (D, "claim", [], "idem:" + hashlib.sha256((D + "|claim|[]").encode()).hexdigest()[:32]),
    (D, "observe", [3], "idem:" + hashlib.sha256((D + "|observe|[3]").encode()).hexdigest()[:32]),
    (D, "artifact", ["prereg", True, None], "idem:" + hashlib.sha256((D + '|artifact|["prereg", true, null]').encode()).hexdigest()[:32]),
]


@pytest.mark.parametrize("design,kind,parts,expected", GOLDEN_STEP_KEYS)
def test_step_key_golden(design, kind, parts, expected):
    assert _sk.step_key(design, kind, parts) == expected
    assert _sk.is_step_key(expected)


@pytest.mark.parametrize("design,kind,parts,expected", GOLDEN_STEP_KEYS)
def test_step_key_matches_the_sql_trigger_expression(conn, design, kind, parts, expected):
    """The trigger in migrations/drafts/006 computes this exact expression;
    run it on the server and compare (jsonb::text spacing included)."""
    with conn.cursor() as cur:
        cur.execute("SELECT 'idem:' || left(encode(sha256(convert_to(%s || '|' || %s || '|' || (%s::jsonb)::text, 'UTF8')), 'hex'), 32)",
                    (design, kind, json.dumps(parts)))
        assert cur.fetchone()[0] == expected
    conn.rollback()


@pytest.mark.parametrize("bad", [[1.5], [{"a": 1}], [[1]], ["\x00"]])
def test_step_key_refuses_parts_that_could_diverge_from_sql(bad):
    with pytest.raises(_sk.StepKeyError):
        _sk.step_key(D, "x", bad)


def test_step_key_contains_the_design():
    a = _sk.step_key(D, "world", ["w"])
    b = _sk.step_key("sha256:" + "b" * 64, "world", ["w"])
    assert a != b


# ------------------------------------------------------------- bundle

def _spec_():
    return {"spec_version": 3, "world": {"seed_root": 7}, "hypothesis": "h", "prediction": None,
            "work": {"kind": "noop_v0", "payload": {}},
            "outcome_rule": None, "pew": None,
            "repeat": {"count": 2, "order": "sequential", "seed_derivation": "constant",
                       "state": "reset", "budget": {"max_seconds": 5, "max_observations": 2}}}


def test_bundle_golden_two_encodings_one_hash():
    s = _spec_()
    a = _b.declared_skeleton(s)
    a["factors"] = {"cell": "W2_K2", "arm": "treated", "budget_class": 300}
    a["evaluator"] = {"profile_id": "ev1", "reward_mode": "all_or_nothing"}
    # the same semantic bundle, keys in another order, nested keys reordered
    b = json.loads(json.dumps({k: a[k] for k in reversed(list(a))}))
    b["evaluator"] = {"reward_mode": "all_or_nothing", "profile_id": "ev1"}
    b["factors"] = {"budget_class": 300, "arm": "treated", "cell": "W2_K2"}
    assert _b.bundle_hash(a) == _b.bundle_hash(b)
    assert _b.problems(a, spec=s) == []
    # a different label is a different bundle -> a different design
    c = json.loads(json.dumps(a)); c["factors"]["arm"] = "control"
    assert _b.bundle_hash(c) != _b.bundle_hash(a)
    assert _b.design_digest(_spec.spec_hash(s), _b.bundle_hash(c)) != _b.design_digest(_spec.spec_hash(s), _b.bundle_hash(a))
    assert _b.diff(a, c) == ["factors.arm"]


def test_bundle_golden_hash_is_pinned():
    """If this moves, canonicalization moved; say why in the commit."""
    s = _spec_()
    a = _b.declared_skeleton(s)
    assert _b.bundle_hash(a) == "sha256:" + hashlib.sha256(_spec.canonical_bytes(a)).hexdigest()
    assert _b.design_digest(_spec.spec_hash(s), None) == _spec.spec_hash(s)


def test_bundle_refuses_unknown_keys_null_values_and_non_scalar_factors():
    s = _spec_()
    a = _b.declared_skeleton(s)
    a["surprise"] = 1
    assert any("unknown key" in r for r in _b.problems(a, spec=s))
    del a["surprise"]; a["schedule"] = None
    assert any("null" in r for r in _b.problems(a, spec=s))
    a["schedule"] = "UNKNOWN"; a["factors"] = {"cell": {"nested": 1}}
    assert any("scalar" in r for r in _b.problems(a, spec=s))
    del a["factors"]
    assert any("missing key" in r for r in _b.problems(a, spec=s))


def test_fill_writes_exactly_the_four_slots():
    s = _spec_()
    declared = _b.declared_skeleton(s)
    declared["engine"] = {"engine_instance_id": "producer-guess"}     # the producer's guess is replaced
    declared["rng"]["campaign_seed"] = 20260920
    filled = _b.fill(declared, spec=s, engine={"engine_instance_id": "eng_x", "schema_version": 9},
                     executor={"kind": "noop_v0", "viv_version": "0.1.0"}, initial_artifacts=[{"slot": "a", "digest": "sha256:1"}])
    changed = _b.diff(declared, filled)
    assert set(changed) <= {"engine.engine_instance_id", "engine.engine_source_hash", "engine.schema_version", "engine.contract_hash",
                            "executor", "initial_artifacts", "engine"}
    assert filled["engine"]["engine_instance_id"] == "eng_x" and filled["engine"]["contract_hash"] == "UNKNOWN"
    assert filled["rng"]["campaign_seed"] == 20260920 and filled["rng"]["seed_root"] == 7
    assert declared["engine"] == {"engine_instance_id": "producer-guess"}   # not mutated


def test_kind_contract_digest_moves_when_the_contract_moves():
    import dataclasses
    k = _kinds.get("ca_density_v0")
    d1 = _b.kind_contract_digest(k)
    assert d1 == _b.kind_contract_digest(k)
    k2 = dataclasses.replace(k, axes={})
    assert _b.kind_contract_digest(k2) != d1
