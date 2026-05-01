"""Tests for descriptor_collapse_audit.py — substrate primitive v0.1.

Run from repo root:

    PYTHONPATH=. PYTHONIOENCODING=utf-8 \
    python -m pytest harmonia/memory/diagnostics/test_descriptor_collapse_audit.py -v

Acceptance criteria from
`harmonia/memory/protocols/descriptor_collapse_audit_proposal.md`:

  AC1. Reproduces zoo Pearson behavior on a fixed input.
  AC2. Catches a constructed collapsed pair (linear + nonlinear).
  AC3. Doesn't false-flag independent uniforms.
  AC4. Verdict logic test — boundary-explained vs structural.
  AC5. Validator companion (separate file).
"""
from __future__ import annotations

import numpy as np
import pytest

from harmonia.memory.diagnostics.descriptor_collapse_audit import (
    descriptor_collapse_audit,
    pearson_audit,
    dcor_audit,
    ksg_mi_audit,
    shuffled_null_pair,
    conditional_mi_pair,
    distance_correlation,
    knn_mutual_information,
)


# -----------------------------------------------------------------------------
# AC1 — Pearson layer reproduces zoo behavior on a fixed-seed input
# -----------------------------------------------------------------------------

def test_pearson_layer_reproduces_zoo_correlation_audit_on_fixed_input():
    """Constructs the kind of (avg_rank, log_params, log_error) triple the
    zoo `correlation_audit` operates on. Verifies the new pearson_audit
    returns the same flags within float tolerance.
    """
    rng = np.random.default_rng(0)
    n = 100
    avg_rank = rng.uniform(1.0, 5.0, n)
    log_params = np.log10(rng.uniform(50.0, 5000.0, n))
    # log_error correlates strongly with log_params (collapse-like)
    log_error = -log_params + 0.05 * rng.normal(0, 1, n)
    cols = {
        "avg_rank": avg_rank,
        "log_params": log_params,
        "log_error": log_error,
    }

    out = pearson_audit(cols, threshold=0.9)

    # Zoo's correlation_audit at threshold 0.9 would flag log_params|log_error
    flagged_pairs = {tuple(sorted(f["pair"])) for f in out["flagged"]}
    assert ("log_error", "log_params") in flagged_pairs
    assert ("avg_rank", "log_params") not in flagged_pairs
    assert ("avg_rank", "log_error") not in flagged_pairs


# -----------------------------------------------------------------------------
# AC2 — Constructed collapsed pair: linear AND nonlinear collapse caught
# -----------------------------------------------------------------------------

def test_constructed_linear_collapse_flagged_by_pearson_dcor_mi():
    rng = np.random.default_rng(7)
    n = 250
    u = rng.uniform(-1.0, 1.0, n)
    v = u + 0.005 * rng.normal(0, 1, n)
    out = descriptor_collapse_audit({"u": u, "v": v}, rng_seed=7)
    layers = (out["layer_1_pearson"], out["layer_2_dcor"], out["layer_3_ksg_mi"])
    for layer in layers:
        assert any(
            tuple(sorted(f["pair"])) == ("u", "v") for f in layer["flagged"]
        ), f"Linear-collapsed pair (u, v) missed by layer with flagged={layer['flagged']}"


def test_constructed_nonlinear_collapse_caught_by_dcor_or_mi_not_pearson():
    rng = np.random.default_rng(8)
    n = 400
    u = rng.uniform(-1.5, 1.5, n)
    v = u**2 + 0.05 * rng.normal(0, 1, n)
    pearson = pearson_audit({"u": u, "v": v}, threshold=0.9)
    dcor = dcor_audit({"u": u, "v": v}, threshold=0.5)
    ksg = ksg_mi_audit({"u": u, "v": v}, threshold_nats=0.5)
    # Pearson must NOT flag this (parabolic has near-zero linear correlation)
    assert pearson["flagged"] == []
    # At least one of dCor or KSG must flag it
    flagged_by_nonlinear = bool(dcor["flagged"]) or bool(ksg["flagged"])
    assert flagged_by_nonlinear, (
        f"Nonlinear collapse missed: pearson={pearson['flagged']}, "
        f"dcor={dcor['flagged']}, ksg={ksg['flagged']}"
    )


# -----------------------------------------------------------------------------
# AC3 — Independent uniforms must NOT false-flag (across multiple seeds)
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("seed", [0, 1, 2, 3, 4])
def test_independent_uniforms_do_not_false_flag(seed):
    rng = np.random.default_rng(seed)
    n = 500
    descs = {"a": rng.uniform(0, 1, n), "b": rng.uniform(0, 1, n)}
    out = descriptor_collapse_audit(descs, rng_seed=seed)
    # No shallow flags expected -> CLEAR verdict
    assert out["audit_summary"]["verdict"] == "CLEAR", (
        f"seed={seed}: false-flagged independent uniforms; "
        f"shallow_flags={out['audit_summary']['shallow_flags']}"
    )
    # Sanity: layers' matrices are present and finite
    for layer_key in ("layer_1_pearson", "layer_2_dcor", "layer_3_ksg_mi"):
        for v in out[layer_key]["matrix"].values():
            assert np.isfinite(v)


# -----------------------------------------------------------------------------
# AC4 — Verdict logic: boundary-explained vs structural-coupling
# -----------------------------------------------------------------------------

def test_boundary_explained_verdict_on_geometric_constraint():
    """Two variables coupled only by a wedge boundary: x in [0, 1],
    y = some_independent_uniform but conditional on x > 0.5.

    This is the kind of dependence where the global MI is non-zero but
    within-band MI drops to baseline because the conditioning restricts
    the joint support.

    Construction: x ~ U(0, 1); for each i, y_i = independent_uniform conditioned
    so that {y_i < x_i + 0.05}. The dependence is purely a boundary
    effect — within narrow x bands, y is uniform on a known interval and
    has no residual structure.
    """
    rng = np.random.default_rng(101)
    n = 800
    x = rng.uniform(0.0, 1.0, n)
    # y is uniform on [0, x] — pure boundary effect
    y = rng.uniform(0.0, 1.0, n) * x
    out = descriptor_collapse_audit(
        {"x": x, "y": y},
        n_shuffles=80,
        n_bands=5,
        rng_seed=101,
    )
    summary = out["audit_summary"]
    # Some shallow flag must fire (the construction has dependence)
    assert summary["any_pair_flagged_shallow"] is True, (
        f"Boundary-coupled construction missed at shallow tier: {summary}"
    )
    # And verdict should NOT be STRUCTURAL_COUPLING_SUSPECTED — the
    # within-band MI should drop because the boundary restriction
    # removes the residual structure.
    # (We allow either BOUNDARY_EXPLAINED or, if the test stochastic-
    # ally lands on a borderline, at least a non-structural verdict.)
    assert summary["verdict"] in ("BOUNDARY_EXPLAINED", "CLEAR"), (
        f"Boundary-coupled construction wrongly classified as structural: {summary}"
    )


def test_structural_coupling_verdict_on_persistent_within_band_dependence():
    """Two variables with strong dependence that PERSISTS within bands
    of either: y = x + small_noise. This must classify as
    STRUCTURAL_COUPLING_SUSPECTED.
    """
    rng = np.random.default_rng(202)
    n = 600
    x = rng.uniform(-1, 1, n)
    y = x + 0.02 * rng.normal(0, 1, n)
    out = descriptor_collapse_audit(
        {"x": x, "y": y},
        n_shuffles=80,
        n_bands=4,
        rng_seed=202,
    )
    assert out["audit_summary"]["verdict"] == "STRUCTURAL_COUPLING_SUSPECTED", (
        f"Persistent within-band coupling missed: {out['audit_summary']}"
    )


# -----------------------------------------------------------------------------
# Layer-4 / Layer-5 unit tests
# -----------------------------------------------------------------------------

def test_shuffled_null_p_value_low_for_strong_coupling():
    rng = np.random.default_rng(303)
    n = 200
    x = rng.uniform(-1, 1, n)
    y = x + 0.02 * rng.normal(0, 1, n)
    out = shuffled_null_pair(x, y, n_shuffles=100, k_mi=3, rng_seed=303)
    assert out["mi_observed"] > 1.0  # strong coupling -> high MI in nats
    assert out["mi_p_value"] < 0.05
    assert out["mi_z"] > 3.0


def test_shuffled_null_p_value_high_for_independent():
    rng = np.random.default_rng(404)
    n = 200
    x = rng.uniform(0, 1, n)
    y = rng.uniform(0, 1, n)
    out = shuffled_null_pair(x, y, n_shuffles=100, k_mi=3, rng_seed=404)
    # Observed should be in the bulk of the null
    assert out["mi_p_value"] > 0.05


def test_conditional_mi_skips_small_bands():
    rng = np.random.default_rng(505)
    n = 30  # too small for default min_n_per_band=20 across n_bands=4
    x = rng.uniform(-1, 1, n)
    y = x + 0.05 * rng.normal(0, 1, n)
    out = conditional_mi_pair(x, y, n_bands=4, min_n_per_band=20)
    # All bands should be skipped (n=30 with 4 bands averages 7.5/band)
    assert out["n_bands_valid"] == 0
    assert out["mean_within_band_mi"] is None


def test_conditional_mi_with_explicit_condition_on():
    rng = np.random.default_rng(606)
    n = 400
    x = rng.uniform(0, 1, n)
    z = rng.uniform(0, 1, n)
    # y depends on x linearly; conditioning on z (independent) should NOT
    # reduce within-band MI
    y = x + 0.02 * rng.normal(0, 1, n)
    out = conditional_mi_pair(x, y, condition_on=z, n_bands=4)
    valid = [b for b in out["bands"] if b["mi_within_band"] is not None]
    assert len(valid) >= 3
    # Conditioning on independent z preserves the x|y coupling within each z-band
    assert out["mean_within_band_mi"] is not None
    assert out["mean_within_band_mi"] > 0.5


# -----------------------------------------------------------------------------
# API and discipline checks
# -----------------------------------------------------------------------------

def test_caveats_block_is_always_present():
    rng = np.random.default_rng(0)
    out = descriptor_collapse_audit(
        {"a": rng.uniform(0, 1, 50), "b": rng.uniform(0, 1, 50)}
    )
    assert "caveats" in out
    assert isinstance(out["caveats"], list)
    assert len(out["caveats"]) >= 3
    # Specific anchor mentions required by discipline
    full = " ".join(out["caveats"])
    assert "Pattern 30" in full
    assert "NULL_BSWCD" in full or "block-shuffle" in full


def test_audit_summary_top_level_verdict_present():
    rng = np.random.default_rng(0)
    out = descriptor_collapse_audit(
        {"a": rng.uniform(0, 1, 100), "b": rng.uniform(0, 1, 100)}
    )
    assert out["audit_summary"]["verdict"] in (
        "CLEAR", "BOUNDARY_EXPLAINED", "STRUCTURAL_COUPLING_SUSPECTED",
        "SHALLOW_FLAGGED_DEEP_NOT_RUN",
    )


def test_shallow_flagged_but_deep_skipped_returns_special_verdict():
    """Self-dissent v0.1.2 fix: if shallow flags exist but the caller
    disabled deep tier and provided no deep_pairs, the verdict must NOT
    fall through to BOUNDARY_EXPLAINED (no evidence to claim that).

    Returns SHALLOW_FLAGGED_DEEP_NOT_RUN.
    """
    rng = np.random.default_rng(909)
    n = 200
    u = rng.uniform(-1, 1, n)
    descs = {"u": u, "v": u + 0.005 * rng.normal(0, 1, n)}
    out = descriptor_collapse_audit(
        descs, deep_on_flagged=False, deep_pairs=None, rng_seed=909,
    )
    assert out["audit_summary"]["any_pair_flagged_shallow"] is True
    assert out["audit_summary"]["verdict"] == "SHALLOW_FLAGGED_DEEP_NOT_RUN"
    assert out["audit_summary"]["deep_findings"] == []


def test_explicit_deep_pairs_still_runs_when_deep_on_flagged_false():
    """If caller passes deep_pairs explicitly with deep_on_flagged=False,
    those pairs DO get evaluated and the verdict reflects them."""
    rng = np.random.default_rng(910)
    n = 300
    u = rng.uniform(-1, 1, n)
    descs = {"u": u, "v": u + 0.02 * rng.normal(0, 1, n), "w": rng.uniform(-1, 1, n)}
    out = descriptor_collapse_audit(
        descs,
        deep_on_flagged=False,
        deep_pairs=[("u", "v")],
        rng_seed=910,
        n_shuffles=60,
    )
    # u|v IS in deep findings; verdict reflects deep evidence.
    keys = list(out["layer_4_5_per_pair"].keys())
    assert keys == ["u|v"]
    assert out["audit_summary"]["verdict"] in (
        "STRUCTURAL_COUPLING_SUSPECTED", "BOUNDARY_EXPLAINED",
    )


def test_validates_unequal_descriptor_lengths():
    with pytest.raises(ValueError, match="length"):
        descriptor_collapse_audit(
            {"a": np.array([1.0, 2.0, 3.0]), "b": np.array([1.0, 2.0])}
        )


def test_validates_too_few_samples():
    with pytest.raises(ValueError, match="at least 3"):
        descriptor_collapse_audit({"a": np.array([1.0, 2.0]), "b": np.array([1.0, 2.0])})


def test_deep_pairs_unknown_descriptor_raises():
    rng = np.random.default_rng(0)
    with pytest.raises(ValueError, match="unknown"):
        descriptor_collapse_audit(
            {"a": rng.uniform(0, 1, 50), "b": rng.uniform(0, 1, 50)},
            deep_pairs=[("a", "nonexistent")],
        )


def test_distance_correlation_independence_property():
    """dCor on two genuinely independent uniforms should be small."""
    rng = np.random.default_rng(909)
    x = rng.uniform(0, 1, 400)
    y = rng.uniform(0, 1, 400)
    d = distance_correlation(x, y)
    assert 0.0 <= d < 0.25


def test_distance_correlation_perfect_linear():
    rng = np.random.default_rng(910)
    x = rng.uniform(0, 1, 200)
    y = 2 * x + 1.0
    d = distance_correlation(x, y)
    assert d > 0.99


def test_ksg_mi_zero_for_independent():
    rng = np.random.default_rng(811)
    x = rng.uniform(0, 1, 300)
    y = rng.uniform(0, 1, 300)
    m = knn_mutual_information(x, y, k=3, rng_seed=811)
    # KSG can be slightly above 0 due to finite-sample bias
    assert m < 0.15


def test_ksg_mi_positive_for_dependent():
    rng = np.random.default_rng(812)
    x = rng.uniform(-1, 1, 300)
    y = x + 0.03 * rng.normal(0, 1, 300)
    m = knn_mutual_information(x, y, k=3, rng_seed=812)
    assert m > 1.0
