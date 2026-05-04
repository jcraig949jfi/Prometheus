"""Tests for prometheus_math.kill_vector_learner (Day 4 of the 5-day plan).

Math-tdd skill rubric: ≥3 each in authority/property/edge/composition.

Authority (≥3): predicting all-triggered for an obviously-rejected
candidate works; mean baseline returns a constant; logistic regression
on a separable subset achieves >90% accuracy.

Property (≥3): determinism with fixed seed; predictions are valid
(probs in [0, 1], margins finite); train and test indices are disjoint.

Edge (≥3): empty dataset handled; missing margins propagate as None;
degenerate region with one operator handled.

Composition (≥3): full pipeline (load -> backfill -> split -> train ->
eval -> report) end-to-end; learner outperforms or matches mean
baseline; per-region eval well-formed.
"""
from __future__ import annotations

import json
import math
import os
import tempfile

import numpy as np
import pytest

from prometheus_math.kill_vector_learner import (
    CANONICAL_COMPONENTS,
    LEGACY_UPSTREAM_TO_COMPONENT,
    Baselines,
    Dataset,
    Learner,
    LearnerEvalResult,
    LearnerRecord,
    _aggregated_to_records,
    _build_feature_matrix,
    _canonical_component_for_legacy_kp,
    _verdict_from_mae,
    build_dataset,
    operator_chart_recovery,
    overall_kill_vector_mae,
    per_component_metrics,
    render_report,
    run_learner,
    stratified_split,
    write_report,
)


# ---------------------------------------------------------------------------
# Test fixtures: synthetic small datasets
# ---------------------------------------------------------------------------


def _synth_aggregated_records():
    """Synthetic (region, operator, kill_pattern, count) aggregates with
    enough variety for the learner to train on."""
    return [
        {"region": "R1", "operator": "OP_A", "kill_pattern": "upstream:cyclotomic_or_large",
         "count": 100, "file": "four_counts_pilot_run.json"},
        {"region": "R1", "operator": "OP_B", "kill_pattern": "F6_kill:trivial",
         "count": 50, "file": "four_counts_pilot_run.json"},
        {"region": "R2", "operator": "OP_A", "kill_pattern": "F1_kill:perm",
         "count": 80, "file": "four_counts_pilot_run.json"},
        {"region": "R2", "operator": "OP_B", "kill_pattern": "F11_kill:cv_drift",
         "count": 30, "file": "four_counts_pilot_run.json"},
        {"region": "R3", "operator": "OP_A", "kill_pattern": "known_in_catalog:Mossinghoff entry x",
         "count": 60, "file": "four_counts_pilot_run.json"},
        {"region": "R1", "operator": "OP_A", "kill_pattern": "F9_kill:cyclo",
         "count": 40, "file": "four_counts_pilot_run.json"},
    ]


def _make_synth_dataset(*, max_per_cell: int = 50):
    records = _aggregated_to_records(
        _synth_aggregated_records(),
        expand_to_individual=True,
        max_per_cell=max_per_cell,
    )
    regions = sorted({r.region for r in records})
    ops = sorted({r.operator for r in records})
    return Dataset(
        records=records,
        component_names=CANONICAL_COMPONENTS,
        region_to_idx={r: i for i, r in enumerate(regions)},
        operator_to_idx={o: i for i, o in enumerate(ops)},
    )


# ---------------------------------------------------------------------------
# Authority tests (≥3)
# ---------------------------------------------------------------------------


def test_authority_legacy_known_kill_routes_to_canonical_component():
    """An obviously-rejected candidate's legacy kill_pattern routes to
    the correct canonical kill_vector component."""
    # F6 kill -> F6_base_rate
    assert _canonical_component_for_legacy_kp("F6_kill:trivial") == "F6_base_rate"
    # known_in_catalog:Mossinghoff -> catalog:Mossinghoff
    assert (_canonical_component_for_legacy_kp(
        "known_in_catalog:matches Mossinghoff entry Lehmer"
    ) == "catalog:Mossinghoff")
    # upstream:cyclotomic_or_large -> out_of_band (env-level rejection)
    assert (_canonical_component_for_legacy_kp("upstream:cyclotomic_or_large")
            == "out_of_band")
    # upstream:cyclotomic -> F9_simpler_explanation (cyclotomic)
    assert (_canonical_component_for_legacy_kp("upstream:cyclotomic")
            == "F9_simpler_explanation")


def test_authority_global_baseline_returns_constant():
    """The global mean baseline returns the same vector for every input."""
    ds = _make_synth_dataset()
    baselines = Baselines.fit(ds.records, ds.n_components)
    preds = baselines.predict(ds.records[:10], kind="global")
    # All rows identical
    assert preds.shape == (10, ds.n_components)
    for i in range(1, 10):
        np.testing.assert_array_equal(preds[i], preds[0])
    # And the constant equals the train mean
    Y = np.stack([r.y_triggered for r in ds.records])
    W = np.array([r.weight for r in ds.records])
    expected = (Y * W[:, None]).sum(axis=0) / W.sum()
    np.testing.assert_allclose(preds[0], expected, atol=1e-9)


def test_authority_logistic_regression_separable_subset_high_accuracy():
    """When the (region, operator) -> kill_pattern relationship is
    perfectly deterministic in the training data, the logistic regression
    achieves >90% test accuracy on the same regions/operators."""
    # Build a deterministic dataset: every R1+OP_A -> upstream:* (out_of_band),
    # every R1+OP_B -> F1_kill (F1_permutation_null).
    deterministic = [
        {"region": "R1", "operator": "OP_A", "kill_pattern":
         "upstream:cyclotomic_or_large",
         "count": 200, "file": "four_counts_pilot_run.json"},
        {"region": "R1", "operator": "OP_B", "kill_pattern": "F1_kill:perm",
         "count": 200, "file": "four_counts_pilot_run.json"},
    ]
    records = _aggregated_to_records(deterministic, max_per_cell=200)
    ds = Dataset(
        records=records,
        component_names=CANONICAL_COMPONENTS,
        region_to_idx={"R1": 0},
        operator_to_idx={"OP_A": 0, "OP_B": 1},
    )
    train_idx, _, test_idx = stratified_split(ds, random_state=42)
    learner = Learner.fit([ds.records[i] for i in train_idx], random_state=42)
    test_records = [ds.records[i] for i in test_idx]
    preds = learner.predict_proba(test_records)
    # For F1_permutation_null component, OP_B records should predict ~1
    # and OP_A records should predict ~0.
    f1_idx = list(CANONICAL_COMPONENTS).index("F1_permutation_null")
    Y = np.array([r.y_triggered[f1_idx] for r in test_records])
    P = (preds[:, f1_idx] >= 0.5).astype(float)
    accuracy = float((P == Y).mean())
    assert accuracy > 0.9


# ---------------------------------------------------------------------------
# Property tests (≥3)
# ---------------------------------------------------------------------------


def test_property_determinism_with_fixed_seed():
    """Same seed -> identical predictions across two runs."""
    ds1 = _make_synth_dataset()
    ds2 = _make_synth_dataset()
    train_idx_a, _, test_idx_a = stratified_split(ds1, random_state=42)
    train_idx_b, _, test_idx_b = stratified_split(ds2, random_state=42)
    assert train_idx_a == train_idx_b
    assert test_idx_a == test_idx_b

    learner_a = Learner.fit([ds1.records[i] for i in train_idx_a], random_state=42)
    learner_b = Learner.fit([ds2.records[i] for i in train_idx_b], random_state=42)

    p_a = learner_a.predict_proba([ds1.records[i] for i in test_idx_a])
    p_b = learner_b.predict_proba([ds2.records[i] for i in test_idx_b])
    np.testing.assert_allclose(p_a, p_b, atol=1e-9)


def test_property_predictions_are_valid():
    """All predicted probabilities are in [0, 1] and finite."""
    ds = _make_synth_dataset()
    train_idx, _, test_idx = stratified_split(ds, random_state=42)
    learner = Learner.fit([ds.records[i] for i in train_idx], random_state=42)
    preds = learner.predict_proba([ds.records[i] for i in test_idx])
    assert np.all(preds >= 0.0)
    assert np.all(preds <= 1.0)
    assert np.all(np.isfinite(preds))


def test_property_train_test_indices_disjoint():
    """Stratified split returns disjoint index sets that union to the full
    record set."""
    ds = _make_synth_dataset()
    train_idx, val_idx, test_idx = stratified_split(ds, random_state=42)
    s_train = set(train_idx)
    s_val = set(val_idx)
    s_test = set(test_idx)
    assert s_train.isdisjoint(s_val)
    assert s_train.isdisjoint(s_test)
    assert s_val.isdisjoint(s_test)
    assert s_train | s_val | s_test == set(range(ds.n))


def test_property_baseline_predictions_in_unit_interval():
    """All four baselines (global, region, operator, cell) return values
    in [0, 1] for held-out records."""
    ds = _make_synth_dataset()
    train_idx, _, test_idx = stratified_split(ds, random_state=42)
    train_records = [ds.records[i] for i in train_idx]
    test_records = [ds.records[i] for i in test_idx]
    baselines = Baselines.fit(train_records, ds.n_components)
    for kind in ("global", "region", "operator", "cell"):
        preds = baselines.predict(test_records, kind=kind)
        assert np.all(preds >= 0.0), f"baseline {kind} produced negative"
        assert np.all(preds <= 1.0), f"baseline {kind} produced > 1"


# ---------------------------------------------------------------------------
# Edge tests (≥3)
# ---------------------------------------------------------------------------


def test_edge_empty_dataset_handled():
    """run_learner on an empty base_dir returns a structured result with
    nan MAE rather than crashing."""
    # Use a tempdir with no pilot JSONs.
    with tempfile.TemporaryDirectory() as tmp:
        res = run_learner(base_dir=tmp)
    assert res.dataset_stats["n_records"] == 0
    assert res.n_train == 0
    assert res.n_test == 0
    assert math.isnan(res.learner_kv_mae)
    assert res.verdict == "C_REPRESENTATION_ISSUE"


def test_edge_missing_margins_propagate_as_nan():
    """Records built from legacy aggregates have NaN margins (the
    aggregated ledger doesn't persist margin); the learner records this
    correctly, doesn't fabricate a value."""
    records = _aggregated_to_records(
        _synth_aggregated_records(), max_per_cell=10
    )
    assert records, "fixture should produce some records"
    for r in records:
        assert r.y_margin.shape == (len(CANONICAL_COMPONENTS),)
        # Every margin should be NaN (legacy aggregates don't carry margin)
        assert np.all(np.isnan(r.y_margin))


def test_edge_degenerate_region_one_operator():
    """A dataset with a single (region, operator) cell still trains
    without crashing; predictions degenerate to the constant mean."""
    deterministic = [
        {"region": "R_solo", "operator": "OP_solo",
         "kill_pattern": "upstream:cyclotomic_or_large",
         "count": 50, "file": "four_counts_pilot_run.json"},
    ]
    records = _aggregated_to_records(deterministic, max_per_cell=50)
    ds = Dataset(
        records=records,
        component_names=CANONICAL_COMPONENTS,
        region_to_idx={"R_solo": 0},
        operator_to_idx={"OP_solo": 0},
    )
    train_idx, _, test_idx = stratified_split(ds, random_state=42)
    learner = Learner.fit([ds.records[i] for i in train_idx], random_state=42)
    test_records = [ds.records[i] for i in test_idx]
    preds = learner.predict_proba(test_records)
    assert preds.shape == (len(test_records), len(CANONICAL_COMPONENTS))
    # Everything triggered=False except out_of_band; predict_proba should
    # reflect that.
    oob_idx = list(CANONICAL_COMPONENTS).index("out_of_band")
    assert float(preds[:, oob_idx].mean()) > 0.9
    # Other components should be ~0 (degenerate logistic returns train mean)
    for j, name in enumerate(CANONICAL_COMPONENTS):
        if name == "out_of_band":
            continue
        assert float(preds[:, j].mean()) < 0.05


def test_edge_unknown_legacy_kill_pattern_dropped():
    """Unknown legacy kill_patterns are dropped, not crashed."""
    aggs = [
        {"region": "R1", "operator": "OP_X", "kill_pattern": "totally_made_up",
         "count": 100, "file": "four_counts_pilot_run.json"},
        {"region": "R1", "operator": "OP_X", "kill_pattern": "F6_kill:ok",
         "count": 30, "file": "four_counts_pilot_run.json"},
    ]
    records = _aggregated_to_records(aggs, max_per_cell=30)
    # Only the F6_kill row produces records; "totally_made_up" is dropped.
    assert len(records) > 0
    assert all(r.operator == "OP_X" for r in records)
    # Every record's triggered is at the F6_base_rate index
    f6_idx = list(CANONICAL_COMPONENTS).index("F6_base_rate")
    for r in records:
        assert r.y_triggered[f6_idx] == 1.0
        # All other components are 0
        zero_count = int((r.y_triggered == 0.0).sum())
        assert zero_count == len(CANONICAL_COMPONENTS) - 1


# ---------------------------------------------------------------------------
# Composition tests (≥3)
# ---------------------------------------------------------------------------


def test_composition_full_pipeline_end_to_end():
    """Load -> backfill -> split -> train -> eval -> report runs end-to-end
    on the real ledger, returns a well-formed LearnerEvalResult."""
    res = run_learner()
    assert isinstance(res, LearnerEvalResult)
    assert res.dataset_stats["n_records"] > 0
    assert res.n_train > 0
    assert res.n_test > 0
    assert res.n_train + res.n_val + res.n_test == res.dataset_stats["n_records"]
    assert res.learner_kv_mae >= 0.0
    for kind in ("global", "region", "operator", "cell"):
        assert kind in res.baseline_kv_mae
        assert res.baseline_kv_mae[kind] >= 0.0
    assert res.verdict in (
        "A_BEATS_CELL_MEAN",
        "B_MATCHES_CELL_MEAN",
        "C_UNDERPERFORMS_CELL_MEAN",
        "C_REPRESENTATION_ISSUE",
    )


def test_composition_learner_at_least_matches_mean_baseline():
    """The learner's MAE should be no worse than the global mean baseline
    (a well-fit model generalises better than predicting the constant)."""
    res = run_learner()
    # eps tolerance because the dataset is dominated by out_of_band; both
    # learner and mean baseline are pulled to ~the same value.
    eps = 1e-3
    assert res.learner_kv_mae <= res.baseline_kv_mae["global"] + eps


def test_composition_per_region_eval_well_formed():
    """The per-region breakdown contains every region present in the
    test set, with valid MAE and macro-accuracy fields."""
    res = run_learner()
    assert res.per_region_metrics, "per-region breakdown should be non-empty"
    for region, m in res.per_region_metrics.items():
        assert "n" in m and m["n"] > 0
        assert "kv_mae" in m and m["kv_mae"] >= 0.0
        assert "macro_accuracy" in m
        assert 0.0 <= m["macro_accuracy"] <= 1.0


def test_composition_render_report_writes_markdown():
    """The end-to-end render_report produces a non-empty Markdown
    document that includes the verdict and the dataset stats."""
    res = run_learner()
    md = render_report(res)
    assert isinstance(md, str)
    assert len(md) > 100
    assert res.verdict in md
    # Heading and section markers
    assert md.startswith("# Kill Vector Learner")
    assert "## Dataset" in md
    assert "## Verdict" in md
    assert "## Operator coordinate chart recovery" in md


def test_composition_write_report_persists_files():
    """write_report writes both JSON + Markdown to disk."""
    res = run_learner()
    with tempfile.TemporaryDirectory() as tmp:
        json_path = os.path.join(tmp, "results.json")
        md_path = os.path.join(tmp, "results.md")
        j_out, m_out = write_report(res, json_path=json_path, md_path=md_path)
        assert j_out == json_path and os.path.exists(json_path)
        assert m_out == md_path and os.path.exists(md_path)
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Round-trips: verdict made it through
        assert data["verdict"] == res.verdict
        with open(md_path, "r", encoding="utf-8") as f:
            md = f.read()
        assert res.verdict in md


# ---------------------------------------------------------------------------
# Verdict-dispatcher unit tests (extra coverage)
# ---------------------------------------------------------------------------


def test_verdict_dispatcher_a_b_c():
    """The verdict dispatcher returns A when learner clearly beats cell,
    B when within epsilon, C when learner is clearly worse."""
    # A: learner beats cell-mean by > eps (eps = 0.005)
    v, _ = _verdict_from_mae(0.10, 0.20, 0.18)
    assert v == "A_BEATS_CELL_MEAN"
    # B: within eps
    v, _ = _verdict_from_mae(0.10, 0.103, 0.12)
    assert v == "B_MATCHES_CELL_MEAN"
    # C: learner clearly worse
    v, _ = _verdict_from_mae(0.20, 0.10, 0.12)
    assert v == "C_UNDERPERFORMS_CELL_MEAN"
    # C: NaN guards
    v, _ = _verdict_from_mae(float("nan"), 0.10, 0.12)
    assert v == "C_REPRESENTATION_ISSUE"
