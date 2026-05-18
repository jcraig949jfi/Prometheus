"""Tests for orchestration wiring (fail-soft on missing PG/Redis)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.orchestration.telemetry import (
    register_theseus,
    log_batch_work,
    maybe_emit_discoveries,
    _build_status_json,
    DEFAULT_DISCOVERY_WEIGHT_THRESHOLD,
)
from theseus.orchestration.lifetime import (
    load_lifetime_stats,
    save_lifetime_stats,
    update_lifetime_after_batch,
)
from theseus.scoring.metrics_schema import BatchMetrics, GeneratorMetrics


def _make_record(weight_target: str = "high") -> TheseusRecord:
    """High-weight record: parity SHADOW with step_trace.
    Low-weight: equality UNVERIFIED."""
    if weight_target == "high":
        return TheseusRecord(
            record_id="r1",
            generator_id="a1",
            batch_id="b",
            emitted_at="2026-05-18T00:00:00Z",
            claim_kind=ClaimKind.INVARIANT_EQUALITY.value,
            claim_payload={"relation": "equal_mod_2"},
            canonical_claim_text="text",
            verdict=Verdict.SHADOW_CATALOG.value,
            step_trace=[{"step_id": "s0", "step_kind": "x",
                         "step_method": "y", "step_info_density": 0.9}],
        )
    return TheseusRecord(
        record_id="r2",
        generator_id="a1",
        batch_id="b",
        emitted_at="2026-05-18T00:00:00Z",
        claim_kind=ClaimKind.INVARIANT_EQUALITY.value,
        claim_payload={"relation": "equal"},
        canonical_claim_text="text",
        verdict=Verdict.UNVERIFIED.value,
    )


def test_register_theseus_failsafe_with_no_pg():
    """Register call returns False if telemetry unreachable; never raises."""
    # Best-effort by design. We just verify no exception is raised.
    result = register_theseus(target_generators=["a1"])
    assert result in (True, False)


def test_log_batch_work_failsafe():
    bm = BatchMetrics(batch_id="b1", started_at="2026-05-18T00:00:00Z",
                      ended_at="2026-05-18T00:00:30Z", duration_hours=0.0083,
                      active_generators=["a1"])
    bm.add(GeneratorMetrics(generator_id="a1", records_emitted=100))
    result = log_batch_work(bm, requested_generators=["a1"])
    assert result in (True, False)


def test_maybe_emit_discoveries_returns_int():
    records = [_make_record("high"), _make_record("low")]
    n = maybe_emit_discoveries(records, weight_threshold=0.6)
    assert isinstance(n, int)
    assert n >= 0


def test_status_json_has_required_fields():
    """Per James's spec: operator, target_generators, sources,
    lifetime_records, dedup_rate, errors_this_cycle, next_cycle_at,
    triggered_by."""
    sj = _build_status_json(
        target_generators=["a1", "b5"],
        triggered_by="schedule",
        last_cycle_id="batch-x",
        next_cycle_at="2026-05-18T01:00:00Z",
        last_dedup_rate=0.7,
        errors_this_cycle=[],
    )
    required = [
        "operator", "target_generators", "sources",
        "lifetime_records", "dedup_rate", "errors_this_cycle",
        "next_cycle_at", "triggered_by",
    ]
    for k in required:
        assert k in sj, f"status_json missing required field: {k}"
    assert sj["operator"] == "James"  # default per env-var
    assert sj["target_generators"] == ["a1", "b5"]
    assert sj["dedup_rate"] == 0.7


def test_lifetime_stats_persist(tmp_path, monkeypatch):
    from theseus.orchestration import lifetime as lf
    monkeypatch.setattr(lf, "LIFETIME_PATH", tmp_path / "lifetime.json")

    initial = lf.load_lifetime_stats()
    assert initial["batches_completed"] == 0
    assert initial["lifetime_records"] == 0

    bm = BatchMetrics(batch_id="b1", started_at="2026-05-18T00:00:00Z",
                      ended_at="2026-05-18T00:00:30Z", duration_hours=0.0083,
                      active_generators=["a1"])
    # BatchMetrics.add() bumps the totals from the generator's metrics
    bm.add(GeneratorMetrics(
        generator_id="a1", records_emitted=1000,
        kills=500, confirmations=480, inconclusive=20,
    ))

    updated = lf.update_lifetime_after_batch(bm, n_discoveries_emitted=5)
    assert updated["batches_completed"] == 1
    assert updated["lifetime_records"] == 1000
    assert updated["lifetime_discoveries_emitted"] == 5
    assert updated["per_generator_lifetime"]["a1"] == 1000

    # Second batch accumulates
    bm2 = BatchMetrics(batch_id="b2", started_at="z", ended_at="z",
                       duration_hours=0.0, active_generators=["a1"])
    bm2.add(GeneratorMetrics(generator_id="a1", records_emitted=500))
    lf.update_lifetime_after_batch(bm2, n_discoveries_emitted=2)
    after_two = lf.load_lifetime_stats()
    assert after_two["batches_completed"] == 2
    assert after_two["lifetime_records"] == 1500
    assert after_two["lifetime_discoveries_emitted"] == 7


def test_discovery_threshold_default():
    """Per spec: high-relevance is training_weight >= 0.6."""
    assert DEFAULT_DISCOVERY_WEIGHT_THRESHOLD == 0.6
