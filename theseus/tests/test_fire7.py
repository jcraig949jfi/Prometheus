"""Smoke tests for Fire #7: step_trace schema, info_density blending, B3, B4."""
from __future__ import annotations

import json

import pytest

from theseus.emit.record_schema import (
    TheseusRecord,
    StepRecord,
    ClaimKind,
    Verdict,
)
from theseus.scoring.info_density import info_density_score
from theseus.generators.b3_inverse_test import B3InverseTestGenerator
from theseus.generators.b4_fixed_point_hunt import B4FixedPointHuntGenerator


def _make_record(verdict: str, step_trace=None) -> TheseusRecord:
    return TheseusRecord(
        record_id=TheseusRecord.compute_record_id("text", "g"),
        generator_id="g",
        batch_id="b",
        emitted_at="2026-05-18T00:00:00Z",
        claim_kind=ClaimKind.INVARIANT_EQUALITY.value,
        claim_payload={},
        canonical_claim_text="text",
        verdict=verdict,
        step_trace=step_trace,
    )


def test_step_record_to_dict_roundtrip():
    s = StepRecord(
        step_id="step_0",
        step_kind="resample",
        step_method="numpy_polyfit",
        step_input={"x": 1},
        step_output={"y": 2},
        step_info_density=0.7,
    )
    d = s.to_dict()
    assert d["step_id"] == "step_0"
    assert d["step_info_density"] == 0.7
    assert d["step_input"] == {"x": 1}


def test_theseus_record_step_trace_serializes():
    s = StepRecord(
        step_id="step_0",
        step_kind="resample",
        step_method="x",
        step_info_density=0.5,
    )
    r = _make_record(Verdict.SHADOW_CATALOG.value, step_trace=[s.to_dict()])
    line = r.to_jsonl()
    parsed = json.loads(line)
    assert parsed["step_trace"] is not None
    assert parsed["step_trace"][0]["step_id"] == "step_0"


def test_info_density_uses_step_trace_when_present():
    no_trace = _make_record(Verdict.SHADOW_CATALOG.value)
    base_score = info_density_score(no_trace)

    high_step = StepRecord(
        step_id="step_0", step_kind="resample", step_method="x",
        step_info_density=1.0,
    )
    high_record = _make_record(
        Verdict.SHADOW_CATALOG.value, step_trace=[high_step.to_dict()]
    )
    high_score = info_density_score(high_record)

    low_step = StepRecord(
        step_id="step_0", step_kind="resample", step_method="x",
        step_info_density=0.0,
    )
    low_record = _make_record(
        Verdict.SHADOW_CATALOG.value, step_trace=[low_step.to_dict()]
    )
    low_score = info_density_score(low_record)

    # Blended score: high step trace lifts above base, low pulls below
    assert high_score > base_score
    assert low_score < base_score


def test_b3_neg_self_inverse_everywhere():
    """neg(neg(v)) == v for all v."""
    g = B3InverseTestGenerator(batch_id="t", seed=0)
    saw_neg = False
    for _ in range(200):
        r = g.next()
        if r is None:
            continue
        p = r.claim_payload
        if p["operator"] == "neg":
            assert p["self_inverse_at_v"] is True
            saw_neg = True
    assert saw_neg


def test_b3_log2_floor_not_self_inverse_for_large():
    """log2_floor(log2_floor(v)) != v for most v (lossy)."""
    g = B3InverseTestGenerator(batch_id="t", seed=0)
    found_kill = False
    for _ in range(200):
        r = g.next()
        if r is None:
            continue
        p = r.claim_payload
        if p["operator"] == "log2_floor" and not p["self_inverse_at_v"]:
            found_kill = True
            break
    assert found_kill


def test_b4_identity_always_fixed_point():
    g = B4FixedPointHuntGenerator(batch_id="t", seed=0)
    for _ in range(50):
        r = g.next()
        if r is None:
            continue
        if r.claim_payload["operator"] == "identity":
            assert r.claim_payload["is_fixed_point"] is True


def test_b4_neg_only_zero_fixed():
    """neg has only one fixed point: v=0."""
    g = B4FixedPointHuntGenerator(batch_id="t", seed=42)
    for _ in range(500):
        r = g.next()
        if r is None:
            continue
        p = r.claim_payload
        if p["operator"] == "neg":
            if p["input_value"] == 0:
                assert p["is_fixed_point"] is True
            else:
                assert p["is_fixed_point"] is False


def test_b3_b4_registered_as_active():
    from theseus.registry import list_active

    actives = list_active()
    assert "b3" in actives
    assert "b4" in actives
