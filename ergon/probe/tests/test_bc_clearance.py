"""Acceptance tests for the co-sign condition ledger (BC-1, BC-2, BC-3, BC-6, BC-8).

Each test pins a condition raised by a co-signer against a defect they MEASURED. The tests
exist so the clearance is verifiable in one command rather than asserted in a commit message.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from ergon.probe import analysis as A                       # noqa: E402
from ergon.probe import fixtures as F                       # noqa: E402
from ergon.probe.assemble import (                          # noqa: E402
    ResidueRecord, _order, _order_per_task_stratified,
)


def _pool(n_theseus=300, n_forge=120, n_sig=80):
    """A D3-shaped pool with the ledger-id ordering that produced Charon's finding."""
    recs = []
    for i in range(n_theseus):
        recs.append(ResidueRecord(
            record_id=f"th-{i:04d}", source="theseus_corpus",
            ledger_id=f"batch-2026-05-{18 + i % 10:02d}-abc", seq=i,
            body=f"theseus record {i}", obstruction_class="asserted-equality",
        ))
    for i in range(n_forge):
        recs.append(ResidueRecord(
            record_id=f"fg-{i:04d}", source="hephaestus_forge",
            ledger_id="hephaestus_forge", seq=i,
            body=f"forge scrap {i}", obstruction_class="surface-plausible",
        ))
    for i in range(n_sig):
        recs.append(ResidueRecord(
            record_id=f"si-{i:04d}", source="signature_index",
            ledger_id="signature_index", seq=i,
            body=f"signature class {i}", obstruction_class="near-miss-margin",
        ))
    return recs


# ----------------------------------------------------------------- BC-2 (Charon C5)

def test_plain_order_reproduces_the_defect_charon_measured():
    """Baseline: the old path ships one source, oldest end, identical for every task."""
    pool = _pool()
    head = _order(pool)[:25]
    assert {r.source for r in head} == {"theseus_corpus"}, (
        "if this ever stops being true the regression test below is testing nothing")


def test_bc2_d3_packets_vary_per_task():
    """A constant packet measures topic priming, not retrieval — and degrades the pairing."""
    pool = _pool()
    a = [r.record_id for r in _order_per_task_stratified(pool, target_uid="task-0001")[:25]]
    b = [r.record_id for r in _order_per_task_stratified(pool, target_uid="task-0002")[:25]]
    assert a != b, "D3 selection must be per-task, or the paired design is partly degenerate"


def test_bc2_d3_selection_mixes_all_three_sources():
    """Charon: forge and signature_index could never ship — their ledger ids sort last."""
    pool = _pool()
    head = _order_per_task_stratified(pool, target_uid="task-0001")[:25]
    assert {r.source for r in head} == {
        "theseus_corpus", "hephaestus_forge", "signature_index"}


def test_bc2_spans_the_timeline_not_just_the_oldest_batches():
    pool = _pool()
    head = _order_per_task_stratified(pool, target_uid="task-0007")[:25]
    ledgers = {r.ledger_id for r in head if r.source == "theseus_corpus"}
    assert len(ledgers) >= 3, f"timeline should be spanned, saw {sorted(ledgers)}"


def test_bc2_is_deterministic_and_reproducible():
    pool = _pool()
    one = _order_per_task_stratified(pool, target_uid="task-0042")
    two = _order_per_task_stratified(pool, target_uid="task-0042")
    assert [r.record_id for r in one] == [r.record_id for r in two]


def test_bc2_is_lossless_a_permutation_not_a_filter():
    pool = _pool()
    out = _order_per_task_stratified(pool, target_uid="task-0001")
    assert sorted(r.record_id for r in out) == sorted(r.record_id for r in pool)


# ----------------------------------------------------------------- BC-8 / Charon §3

def test_charon_31_strong_but_harmful_class_exists():
    """The gap: Δ=+10pp with failing harm previously matched no class at all."""
    v, why = A.classify(0.10, 0.04, 0.16, harm_rate=0.30, gain_rate=0.33)
    assert v == "CARRY-STRONG-BUT-HARMFUL", v
    assert "harm" in why and "Path alpha" in why


def test_charon_32_detectable_but_inert_does_not_route():
    v, why = A.classify(0.02, 0.005, 0.04, harm_rate=0.05, gain_rate=0.20)
    assert v == "DETECTABLE-BUT-INERT"
    assert v in A.NON_ROUTING_CLASSES
    assert "routes to no program direction" in why


def test_weak_now_requires_the_practical_floor():
    v, _ = A.classify(0.06, 0.01, 0.11, harm_rate=0.05, gain_rate=0.25)
    assert v == "CARRY-WEAK"


def test_charon_34_harm_ratio_undefined_at_zero_gain():
    v, why = A.classify(0.06, 0.01, 0.11, harm_rate=0.0, gain_rate=0.0)
    assert "UNDEFINED" in why


def test_charon_33_verdict_classes_are_pooled_endpoint_only():
    """Refuse to label a 0.40-power stratum — evidence of absence is not absence."""
    strat = A.Comparison("D3", 100, 0.01, -0.09, 0.11, 0.8, exploratory=True)
    with pytest.raises(ValueError, match="pooled-primary-endpoint only"):
        A.classify_pooled_only(strat, 0.1, 0.2)
    pooled = A.Comparison("PRIMARY", 400, 0.10, 0.04, 0.16, 0.001, exploratory=False)
    assert A.classify_pooled_only(pooled, 0.05, 0.30)[0] == "CARRY-STRONG"


def test_bc8_unrouted_when_whole_arm_cannot_separate_rows():
    wide = A.Comparison("whole-null", 150, 0.04, -0.06, 0.14, 0.4)
    row, why = A.route_matrix_row(wide, None, exploratory_only=False)
    assert row == A.UNROUTED
    assert "spans both readings" in why


def test_bc8_exploratory_only_bars_routing_regardless_of_point_estimate():
    strong = A.Comparison("whole-null", 150, 0.20, 0.12, 0.28, 0.0001)
    row, why = A.route_matrix_row(strong, None, exploratory_only=True)
    assert row == A.UNROUTED
    assert "EXPLORATORY-ONLY" in why


def test_row_3_requires_whole_to_beat_null_while_retrieved_does_not():
    whole = A.Comparison("whole-null", 300, 0.12, 0.05, 0.19, 0.001)
    retr = A.Comparison("retr-null", 400, 0.01, -0.04, 0.06, 0.7)
    row, _ = A.route_matrix_row(whole, retr, exploratory_only=False)
    assert row == "ROW-3-RETRIEVAL-FAILURE"


# ----------------------------------------------------------------- BC-6 / BC-3

def test_bc6_harm_and_gain_split_by_gold_label():
    """The detector for the polarity confound: a negative prime trades errors by label."""
    recs = F.synthetic_run(n_tasks=200, seed=31)
    for r in recs:
        r.synthetic = False
    out = A.harm_gain_by_gold(recs, "F-prom-retrieved")
    assert set(out) == {"gold_true", "gold_false", "pooled"}
    assert out["gold_true"]["n"] + out["gold_false"]["n"] == out["pooled"]["n"]
    for k in ("harm_rate", "gain_rate", "solved_to_unsolved", "unsolved_to_solved"):
        assert k in out["pooled"]


def test_bc3_strict_screen_reanalysis_runs_on_a_subset():
    recs = F.synthetic_run(n_tasks=200, seed=32)
    for r in recs:
        r.synthetic = False
    excluded = {f"synth-{i:04d}" for i in range(0, 200, 4)}
    strict = A.strict_screen_reanalysis(recs, excluded)
    assert strict is not None
    assert strict.n_tasks == 150
    assert "strict-screened" in strict.label


def test_bc3_reanalysis_still_refuses_synthetic_records():
    """The firewall is not bypassed by the second read."""
    from ergon.probe.schema import FirewallViolation
    with pytest.raises(FirewallViolation):
        A.analyze(F.synthetic_run(n_tasks=4))
