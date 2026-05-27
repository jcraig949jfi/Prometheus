"""Synthetic-control tests for G02 contrast loader's permutation-null
binary-split mechanism.

Per ITER-16 substrate-refinement push: the G02-family loaders
(composition_g02_lehmer_salem, _smyth, _degree_parity, _band_high,
g04_tightened) all build on the same `run_binary_split_permutation_
null` kernel in _mahler_composition_helpers.py. Until ITER-16 this
kernel was tested only by smoke-running it against the live
Mossinghoff catalog. These tests validate decision logic against
SYNTHETIC distributions with known divergence properties.
"""
from __future__ import annotations

import pytest

from charon.agents.stygian.loaders._mahler_composition_helpers import (
    permutation_null_divergence,
    run_binary_split_permutation_null,
    survival_fraction,
)


# ---------------------------------------------------------------------
# survival_fraction primitive
# ---------------------------------------------------------------------

def test_survival_fraction_empty():
    assert survival_fraction([], 1.0) == 0.0


def test_survival_fraction_all_above():
    assert survival_fraction([2.0, 3.0, 4.0], 1.0) == 1.0


def test_survival_fraction_all_below():
    assert survival_fraction([0.5, 0.7, 0.9], 1.0) == 0.0


def test_survival_fraction_threshold_inclusive():
    """Threshold is >= (inclusive)."""
    assert survival_fraction([1.0, 2.0, 3.0], 1.0) == 1.0


def test_survival_fraction_half():
    assert survival_fraction([0.5, 1.5], 1.0) == 0.5


# ---------------------------------------------------------------------
# permutation_null_divergence
# ---------------------------------------------------------------------

def test_permutation_null_returns_distribution_of_correct_size():
    pooled = [0.0] * 50 + [2.0] * 50
    nulls = permutation_null_divergence(
        pooled, n_a=50, threshold=1.0, n_perm=100, seed=42,
    )
    assert len(nulls) == 100


def test_permutation_null_seed_reproducibility():
    """Same seed -> same divergences."""
    pooled = [0.0, 1.0, 2.0, 3.0, 4.0] * 10
    a = permutation_null_divergence(pooled, n_a=25, threshold=2.0, n_perm=50, seed=42)
    b = permutation_null_divergence(pooled, n_a=25, threshold=2.0, n_perm=50, seed=42)
    assert a == b


def test_permutation_null_different_seeds_differ():
    pooled = [0.0, 1.0, 2.0, 3.0, 4.0] * 10
    a = permutation_null_divergence(pooled, n_a=25, threshold=2.0, n_perm=50, seed=42)
    b = permutation_null_divergence(pooled, n_a=25, threshold=2.0, n_perm=50, seed=43)
    assert a != b


def test_permutation_null_centered_near_zero_for_random_pool():
    """Random-pool shuffles produce divergences concentrated near 0."""
    pooled = list(range(100))
    nulls = permutation_null_divergence(
        pooled, n_a=50, threshold=50, n_perm=500, seed=42,
    )
    mean_div = sum(nulls) / len(nulls)
    # Mean divergence under shuffles of [0..99] at threshold 50 should
    # be small (theoretical: hypergeometric variance / N -> O(1/sqrt(N)))
    assert mean_div < 0.2


# ---------------------------------------------------------------------
# run_binary_split_permutation_null end-to-end with synthetic predicates
# ---------------------------------------------------------------------

def test_perfect_separator_predicate_promoted(monkeypatch):
    """If predicate perfectly separates above/below threshold,
    observed divergence is near 1.0 — much higher than null p95."""
    import charon.agents.stygian.loaders._mahler_composition_helpers as helpers

    # Synthetic catalog: 100 entries with M=0.5 marked "True", 100 with
    # M=2.0 marked "False". The predicate is salem_class.
    def fake_loader(upper_M=2.0):
        out = []
        for i in range(100):
            out.append({"mahler_measure": 0.5 + 1e-6, "salem_class": True})
        for i in range(100):
            out.append({"mahler_measure": 2.0, "salem_class": False})
        return out

    monkeypatch.setattr(
        helpers, "load_non_cyclotomic_mahler_entries", fake_loader
    )

    result = run_binary_split_permutation_null(
        predicate=lambda e: bool(e.get("salem_class")),
        group_a_label="salem",
        group_b_label="non_salem",
        threshold=1.0,
        n_perm=200,
        seed=42,
    )
    assert result["verdict"] == "PROMOTED"
    assert result["kill_pattern"] is None
    # Perfect separator: surv_a (M=0.5+1e-6 below threshold 1.0) = 0,
    # surv_b (M=2.0 above) = 1.0. Divergence = 1.0.
    assert abs(result["observed_divergence"] - 1.0) < 1e-3


def test_random_predicate_rejected(monkeypatch):
    """If predicate is uncorrelated with M, divergence is null-level."""
    import charon.agents.stygian.loaders._mahler_composition_helpers as helpers

    # Same M distribution, predicate assigned by index parity (random
    # vs M)
    def fake_loader(upper_M=2.0):
        out = []
        for i in range(200):
            m = 0.5 + 0.01 * (i % 50)  # spread M values
            out.append({"mahler_measure": m, "salem_class": (i % 2 == 0)})
        return out

    monkeypatch.setattr(
        helpers, "load_non_cyclotomic_mahler_entries", fake_loader
    )

    result = run_binary_split_permutation_null(
        predicate=lambda e: bool(e.get("salem_class")),
        group_a_label="even_idx",
        group_b_label="odd_idx",
        threshold=0.75,
        n_perm=500,
        seed=42,
    )
    assert result["verdict"] == "REJECTED"
    assert result["kill_pattern"] == "permutation_null"


def test_insufficient_sample_unverified(monkeypatch):
    """Groups below min_group_size -> UNVERIFIED with insufficient_sample."""
    import charon.agents.stygian.loaders._mahler_composition_helpers as helpers

    def fake_loader(upper_M=2.0):
        return [
            {"mahler_measure": 1.5, "salem_class": True},
            {"mahler_measure": 1.8, "salem_class": False},
        ]

    monkeypatch.setattr(
        helpers, "load_non_cyclotomic_mahler_entries", fake_loader
    )

    result = run_binary_split_permutation_null(
        predicate=lambda e: bool(e.get("salem_class")),
        group_a_label="a",
        group_b_label="b",
        threshold=1.0,
        n_perm=100,
        seed=42,
        min_group_size=10,
    )
    assert result["verdict"] == "UNVERIFIED"
    assert "insufficient_sample" in result["kill_pattern"]


def test_empty_catalog_unverified(monkeypatch):
    import charon.agents.stygian.loaders._mahler_composition_helpers as helpers

    monkeypatch.setattr(
        helpers, "load_non_cyclotomic_mahler_entries", lambda upper_M=2.0: []
    )

    result = run_binary_split_permutation_null(
        predicate=lambda e: True,
        group_a_label="a",
        group_b_label="b",
        threshold=1.0,
        n_perm=10,
        seed=42,
    )
    assert result["verdict"] == "UNVERIFIED"
    assert "data_load_failed" in result["kill_pattern"]


def test_in_band_restriction(monkeypatch):
    """in_band filter restricts the catalog to a Mahler-measure band
    before computing divergence."""
    import charon.agents.stygian.loaders._mahler_composition_helpers as helpers

    # Catalog has entries at M=0.5, 1.5, 2.5. in_band = (1.0, 2.0)
    # restricts to M=1.5 only.
    def fake_loader(upper_M=2.0):
        out = []
        for _ in range(50):
            out.append({"mahler_measure": 0.5, "salem_class": True})
            out.append({"mahler_measure": 1.5, "salem_class": True})
            out.append({"mahler_measure": 2.5, "salem_class": False})
        return out

    monkeypatch.setattr(
        helpers, "load_non_cyclotomic_mahler_entries", fake_loader
    )

    result = run_binary_split_permutation_null(
        predicate=lambda e: bool(e.get("salem_class")),
        group_a_label="salem",
        group_b_label="non_salem",
        threshold=1.7,
        in_band=(1.0, 2.0),
        n_perm=200,
        seed=42,
        min_group_size=10,
    )
    # In-band catalog has 50 Salem (M=1.5, all below 1.7) and 0 non-salem.
    # So n_group_b < min -> UNVERIFIED.
    assert result["verdict"] == "UNVERIFIED"
    assert "insufficient_sample" in result["kill_pattern"]
