"""Tests for the M0.5 promotion replay audit harness.

Locks the replay-classification logic and the cheap promote pre-filter so the
audit's verdicts cannot drift silently. The harness is substrate-grade (its
output enters the replay-or-it-didn't-promote doctrine), so it carries the same
test discipline as any forged tool.
"""
import random

from theseus.emit.record_schema import TheseusRecord, Verdict
from theseus.scripts.promotion_replay_audit import (
    _can_possibly_promote,
    _replay_content,
    _raw_is_direct,
    _raw_key_values,
)


def _rec(payload, *, kind="invariant_equality", verdict=Verdict.SHADOW_CATALOG.value,
         generator_id="a1", predicate_kind=None, step_trace=None):
    return TheseusRecord(
        record_id="r", generator_id=generator_id, batch_id="b", emitted_at="",
        claim_kind=kind, claim_payload=payload, canonical_claim_text="t",
        verdict=verdict, predicate_kind=predicate_kind, step_trace=step_trace,
    )


def _direct_payload(a, b, rel="divides"):
    return {
        "catalog_a": "knot", "invariant_a": "x", "catalog_b": "knot",
        "invariant_b": "y", "relation": rel, "value_a": a, "value_b": b,
    }


# --- pre-filter -------------------------------------------------------------

def test_prefilter_skips_plain_shadow():
    # No step_trace, not PROMOTED verdict → cannot reach 0.6, skipped.
    d = {"verdict": "SHADOW_CATALOG"}
    assert _can_possibly_promote(d) is False


def test_prefilter_passes_triangulated_and_promoted():
    assert _can_possibly_promote({"verdict": "SHADOW_CATALOG", "step_trace": [{}]}) is True
    assert _can_possibly_promote({"verdict": "PROMOTED"}) is True


# --- direct-predicate resolution (raw dict, no dataclass) -------------------

def test_raw_is_direct_uses_predicate_kind_then_denylist():
    assert _raw_is_direct({"generator_id": "a1", "claim_payload": {}}) is True
    # g4 is meta-relational by the legacy denylist
    assert _raw_is_direct({"generator_id": "g4", "claim_payload": {}}) is False
    # explicit predicate_kind overrides the denylist
    assert _raw_is_direct({"generator_id": "g4",
                           "claim_payload": {"predicate_kind": "direct"}}) is True


def test_raw_key_values_matches_payload():
    key, vals = _raw_key_values(_direct_payload(3, 12))
    assert key == ("knot", "x", "knot", "y", "divides")
    assert vals == (3, 12)
    # missing values → key present, values None
    p = _direct_payload(3, 12)
    del p["value_a"]
    key2, vals2 = _raw_key_values(p)
    assert key2 is not None and vals2 is None


# --- content replay classification ------------------------------------------

def test_still_valid_when_relation_holds_and_beats_null():
    rng = random.Random(0)
    rec = _rec(_direct_payload(3, 12, "divides"))  # 3 | 12 holds
    # null pool where 3∤b mostly (b values not multiples of 3) → null low → score high
    pools = {("knot", "x", "knot", "y", "divides"): ([3, 3, 3], [12, 1, 2])}
    out = _replay_content(rec, pools, rng, n_null_samples=200)
    assert out["class"] == "still_valid"


def test_content_mismatch_when_relation_fails():
    rng = random.Random(0)
    rec = _rec(_direct_payload(5, 12, "divides"))  # 5 ∤ 12 — record asserts confirmation it cannot support
    pools = {("knot", "x", "knot", "y", "divides"): ([5], [12])}
    out = _replay_content(rec, pools, rng, n_null_samples=50)
    assert out["class"] == "content_mismatch"


def test_not_direct_for_meta_relational_generator():
    rng = random.Random(0)
    rec = _rec(_direct_payload(3, 12), generator_id="g4")  # meta-relational
    out = _replay_content(rec, {}, rng, n_null_samples=10)
    assert out["class"] == "not_direct"


def test_missing_features_when_payload_lacks_key():
    rng = random.Random(0)
    rec = _rec({"relation": "divides"})  # no catalog/invariant/values
    out = _replay_content(rec, {}, rng, n_null_samples=10)
    assert out["class"] == "missing_features"


def test_self_tautology_detected():
    rng = random.Random(0)
    p = {"catalog_a": "k", "invariant_a": "x", "catalog_b": "k", "invariant_b": "x",
         "relation": "equal", "value_a": 7, "value_b": 7,
         "object_a": "o", "object_b": "o"}
    rec = _rec(p, kind="invariant_equality")
    out = _replay_content(rec, {}, rng, n_null_samples=10)
    assert out["class"] == "self_tautology"
