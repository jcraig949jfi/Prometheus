"""Synthetic-control tests for selection_discipline.py.

Per Erebos v3 Phase 0 ITER-21. Locks in the contract that loaders
cannot pick first-alphabetical / random / argmax-scalar without
declaring a SelectionMetric and a metric_callable.
"""
from __future__ import annotations

import math

import pytest

from charon.agents.stygian.loaders._selection_discipline import (
    ArbitraryScalarSelectionError,
    SelectionMetric,
    disciplined_select,
    known_data_types,
    register_metric_pair,
    validate_metric_for_data_type,
)


# ---------------------------------------------------------------------
# Happy path: distance-minimizing on persistence diagrams
# ---------------------------------------------------------------------

def test_select_distance_minimizing_on_persistence_diagram():
    """Smallest distance wins under DISTANCE_MINIMIZING."""
    candidates = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    distances = {"a": 0.5, "b": 0.1, "c": 0.3}
    chosen, prov = disciplined_select(
        candidates,
        metric=SelectionMetric.DISTANCE_MINIMIZING,
        metric_callable=lambda c: distances[c["id"]],
        data_type="persistence_diagram",
    )
    assert chosen["id"] == "b"
    assert prov["chosen_score"] == 0.1
    assert sorted(prov["rejected_scores"]) == [0.3, 0.5]
    assert prov["metric"] == "distance_minimizing"


def test_select_attribution_ranked_on_feature_vector():
    """Largest attribution wins under ATTRIBUTION_RANKED."""
    candidates = ["feat_a", "feat_b", "feat_c"]
    shapley = {"feat_a": 0.05, "feat_b": 0.40, "feat_c": 0.15}
    chosen, prov = disciplined_select(
        candidates,
        metric=SelectionMetric.ATTRIBUTION_RANKED,
        metric_callable=lambda c: shapley[c],
        data_type="feature_vector",
    )
    assert chosen == "feat_b"
    assert prov["chosen_score"] == 0.40
    assert prov["smallest_wins"] is False


def test_select_percentile_based_on_scalar_axis():
    """Smallest distance-to-target percentile wins."""
    candidates = [1.10, 1.20, 1.30, 1.40, 1.50]
    target = 1.25
    chosen, prov = disciplined_select(
        candidates,
        metric=SelectionMetric.PERCENTILE_BASED,
        metric_callable=lambda c: abs(c - target),
        data_type="scalar_axis_value",
    )
    assert chosen == 1.20
    assert prov["smallest_wins"] is True


def test_select_posterior_maximizing_on_ledger_rows():
    """Largest posterior wins under POSTERIOR_MAXIMIZING."""
    candidates = [{"row_id": "r1"}, {"row_id": "r2"}]
    posteriors = {"r1": 0.30, "r2": 0.70}
    chosen, prov = disciplined_select(
        candidates,
        metric=SelectionMetric.POSTERIOR_MAXIMIZING,
        metric_callable=lambda c: posteriors[c["row_id"]],
        data_type="ledger_row_set",
    )
    assert chosen["row_id"] == "r2"


# ---------------------------------------------------------------------
# EXHAUSTIVE mode
# ---------------------------------------------------------------------

def test_select_exhaustive_returns_all_candidates():
    candidates = ["a", "b", "c"]
    chosen, prov = disciplined_select(
        candidates,
        metric=SelectionMetric.EXHAUSTIVE,
        metric_callable=None,  # ignored in exhaustive mode
        data_type="ledger_row_set",
    )
    assert chosen == ["a", "b", "c"]
    assert prov["exhaustive_mode"] is True
    assert prov["n_candidates"] == 3


# ---------------------------------------------------------------------
# Error cases — the discipline gate
# ---------------------------------------------------------------------

def test_select_raises_on_undeclared_metric():
    """Selecting from >1 candidates without a metric → error."""
    with pytest.raises(ArbitraryScalarSelectionError, match="no SelectionMetric"):
        disciplined_select(
            ["a", "b"],
            metric=None,
            metric_callable=lambda c: 1.0,
            data_type="feature_vector",
        )


def test_select_raises_on_missing_callable():
    """Declared metric (non-EXHAUSTIVE) but no callable → error."""
    with pytest.raises(ArbitraryScalarSelectionError, match="metric_callable"):
        disciplined_select(
            ["a", "b"],
            metric=SelectionMetric.DISTANCE_MINIMIZING,
            metric_callable=None,
            data_type="feature_vector",
        )


def test_select_raises_on_incompatible_metric_data_type():
    """persistence_diagram + POSTERIOR_MAXIMIZING is not registered → error."""
    with pytest.raises(ArbitraryScalarSelectionError, match="not valid for data_type"):
        disciplined_select(
            ["a", "b"],
            metric=SelectionMetric.POSTERIOR_MAXIMIZING,
            metric_callable=lambda c: 1.0,
            data_type="persistence_diagram",
        )


def test_select_raises_on_unknown_data_type():
    """Unknown data_type → no valid metrics → error."""
    with pytest.raises(ArbitraryScalarSelectionError, match="not valid for data_type"):
        disciplined_select(
            ["a", "b"],
            metric=SelectionMetric.DISTANCE_MINIMIZING,
            metric_callable=lambda c: 1.0,
            data_type="unknown_data_type_xyz",
        )


def test_select_raises_on_empty_candidates():
    with pytest.raises(ArbitraryScalarSelectionError, match="empty candidates"):
        disciplined_select(
            [],
            metric=SelectionMetric.DISTANCE_MINIMIZING,
            metric_callable=lambda c: 1.0,
            data_type="feature_vector",
        )


def test_select_raises_on_non_finite_score():
    """metric_callable returning NaN → error."""
    with pytest.raises(ArbitraryScalarSelectionError, match="non-finite score"):
        disciplined_select(
            ["a", "b"],
            metric=SelectionMetric.DISTANCE_MINIMIZING,
            metric_callable=lambda c: float("nan"),
            data_type="feature_vector",
        )


def test_select_raises_on_inf_score():
    """metric_callable returning Inf → error."""
    with pytest.raises(ArbitraryScalarSelectionError, match="non-finite score"):
        disciplined_select(
            ["a", "b"],
            metric=SelectionMetric.DISTANCE_MINIMIZING,
            metric_callable=lambda c: math.inf,
            data_type="feature_vector",
        )


# ---------------------------------------------------------------------
# Single-candidate passthrough
# ---------------------------------------------------------------------

def test_select_with_single_candidate_skips_metric_check():
    """N=1 input passes through without declaring metric."""
    chosen, prov = disciplined_select(
        ["only_one"],
        metric=None,
        metric_callable=None,
        data_type="anything_at_all",
    )
    assert chosen == "only_one"
    assert prov["single_candidate_passthrough"] is True


def test_select_with_single_candidate_records_provenance():
    chosen, prov = disciplined_select(
        ["only_one"],
        metric=None,
        metric_callable=None,
        data_type="anything",
    )
    assert prov["rejected_scores"] == []
    assert prov["chosen_score"] is None


# ---------------------------------------------------------------------
# Provenance propagation
# ---------------------------------------------------------------------

def test_select_records_rejected_candidates_in_provenance():
    """All rejected scores are surfaced for downstream audit."""
    candidates = list(range(10))
    chosen, prov = disciplined_select(
        candidates,
        metric=SelectionMetric.PERCENTILE_BASED,
        metric_callable=lambda c: abs(c - 4.5),
        data_type="scalar_axis_value",  # PERCENTILE_BASED is valid here
        selection_provenance={"caller": "test_provenance"},
    )
    assert chosen in (4, 5)  # equidistant; sort-stable wins first one
    assert len(prov["rejected_scores"]) == 9
    assert prov["caller"] == "test_provenance"


def test_select_preserves_caller_provenance_keys():
    chosen, prov = disciplined_select(
        ["a", "b"],
        metric=SelectionMetric.ATTRIBUTION_RANKED,
        metric_callable=lambda c: 1.0 if c == "a" else 2.0,
        data_type="feature_vector",
        selection_provenance={"plugin_id": "g06_null_space", "iter": 99},
    )
    assert prov["plugin_id"] == "g06_null_space"
    assert prov["iter"] == 99


# ---------------------------------------------------------------------
# Registry validation helpers
# ---------------------------------------------------------------------

def test_validate_metric_for_data_type_known_pair():
    assert validate_metric_for_data_type(
        SelectionMetric.DISTANCE_MINIMIZING, "persistence_diagram"
    ) is True


def test_validate_metric_for_data_type_unknown_pair():
    assert validate_metric_for_data_type(
        SelectionMetric.POSTERIOR_MAXIMIZING, "persistence_diagram"
    ) is False


def test_validate_metric_for_data_type_unknown_data_type():
    assert validate_metric_for_data_type(
        SelectionMetric.DISTANCE_MINIMIZING, "nonexistent_type"
    ) is False


def test_register_metric_pair_extends_registry():
    register_metric_pair("brand_new_type", SelectionMetric.DISTANCE_MINIMIZING)
    assert validate_metric_for_data_type(
        SelectionMetric.DISTANCE_MINIMIZING, "brand_new_type"
    ) is True


def test_known_data_types_sorted():
    types = known_data_types()
    assert types == sorted(types)
    assert "persistence_diagram" in types
    assert "feature_vector" in types
