"""Tests for prometheus_math.research.tensor Phase 2 scorers (project #44).

Test categories (math-tdd skill, see techne/skills/math-tdd.md):

- **Authority** (3+):
  * distributional_distance with same domain on both sides == 0.
  * js distance between identical samples ~ 0.
  * js distance between N(0,1) and N(5,1) bounded but high.
  * identity_join on a tensor with shared key returns non-empty DataFrame.
  * cross_domain_correlation matches scipy.stats.pearsonr on a
    single-cell tensor flatten.

- **Property** (3+):
  * distributional_distance is symmetric across all four metrics.
  * distributional_matrix is symmetric and zero-diagonal.
  * distributional_distance >= 0 for all metrics.
  * identity_join row count <= n_object (key-uniqueness bound).

- **Edge** (3+):
  * empty domains / NaN cells / unknown metric / unknown key /
    single observation correlation.

- **Composition** (2+):
  * distributional_matrix(t, ph, inv) == distributional_distance(t, dA, dB,
    ph, inv) for each (dA, dB).
  * tensor_silent_islands(t) ⊆ {pairs with distributional_matrix >= threshold}.
  * tensor_phoneme_score(t, ph) summary respects mean_correlation magnitude.
  * tensor_anomaly_surface(t) records align with surface_anomalies on
    flattened cells.

References
----------
- project_silent_islands.md (memory): silent-island concept.
- project_megethos.md (memory): canonical phoneme.
- scipy.stats.pearsonr / wasserstein_distance / ks_2samp /
  scipy.spatial.distance.jensenshannon — canonical authorities for the
  distributional metrics.
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import pytest
from scipy.spatial.distance import jensenshannon
from scipy.stats import ks_2samp, pearsonr, wasserstein_distance

from prometheus_math.research import tensor as T
from prometheus_math.research.tensor import (
    DomainSpec,
    InvariantSpec,
    PhonemeSpec,
    build_tensor,
    cross_domain_correlation,
    distributional_distance,
    distributional_matrix,
    identity_join,
    tensor_anomaly_surface,
    tensor_phoneme_score,
    tensor_silent_islands,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_records(rng, n=5, mean=0.0, scale=1.0):
    """Synthetic records: gaussian samples plus a per-record key index."""
    out = []
    xs = rng.normal(loc=mean, scale=scale, size=n)
    ys = rng.normal(loc=mean, scale=scale, size=n)
    for i, (x, y) in enumerate(zip(xs, ys)):
        out.append({"id": f"obj{i}", "x": float(x), "y": float(y), "key": float(i)})
    return out


def _domain(name, records):
    return DomainSpec(
        name=name,
        fetch_fn=lambda n=None, _r=records: _r if n is None else _r[:n],
        n_objects=len(records),
        primary_id_field="id",
        version="phase2-fixture",
    )


def _phoneme_all(name="ph1"):
    return PhonemeSpec(name=name, description="test phoneme", applies_to_domains=("*",))


def _inv(name, key):
    return InvariantSpec(
        name=name,
        kind="numeric",
        compute_fn=lambda rec, _ph: float(rec.get(key, float("nan"))),
        normalization="none",
    )


@pytest.fixture
def tiny_tensor():
    """3 domains x 5 objects x 2 phonemes x 3 invariants (x, y, key)."""
    rng = np.random.default_rng(42)
    da = _domain("A", _make_records(rng, n=5, mean=0.0, scale=1.0))
    db = _domain("B", _make_records(rng, n=5, mean=0.0, scale=1.0))
    dc = _domain("C", _make_records(rng, n=5, mean=10.0, scale=1.0))  # far
    phonemes = [_phoneme_all("ph1"), _phoneme_all("ph2")]
    invariants = [_inv("x", "x"), _inv("y", "y"), _inv("key", "key")]
    return build_tensor([da, db, dc], phonemes, invariants, n_per_domain=5)


@pytest.fixture
def shared_key_tensor():
    """Two domains share the integer key 0..4 but with different x/y values."""
    rng = np.random.default_rng(7)
    da = _domain("A", _make_records(rng, n=5, mean=0.0, scale=1.0))
    db = _domain("B", _make_records(rng, n=5, mean=2.0, scale=1.0))
    phonemes = [_phoneme_all("ph1")]
    invariants = [_inv("x", "x"), _inv("key", "key")]
    return build_tensor([da, db], phonemes, invariants, n_per_domain=5)


# ===========================================================================
# AUTHORITY TESTS (3+)
# ===========================================================================


def test_authority_distributional_distance_self_is_zero(tiny_tensor):
    """Authority: d(A, A) == 0 by construction.

    Reference: any proper metric d satisfies d(x,x) = 0. Tested for all
    four metrics in the supported set.
    """
    for metric in ("js", "ks", "wass", "mmd"):
        v = distributional_distance(tiny_tensor, "A", "A", "ph1", "x", metric=metric)
        assert v == 0.0, f"{metric}: self-distance must be 0, got {v}"


def test_authority_js_identical_distributions_near_zero():
    """Authority: JS(N(0,1), N(0,1)) ~ 0 for shared sample.

    Reference: scipy.spatial.distance.jensenshannon on equal probability
    vectors returns exactly 0.
    """
    rng = np.random.default_rng(0)
    rec = [{"id": str(i), "x": float(v), "key": float(i)} for i, v in enumerate(rng.normal(0, 1, 50))]
    da = _domain("A", rec)
    db = _domain("B", rec)  # identical sample
    t = build_tensor(
        [da, db],
        [_phoneme_all()],
        [_inv("x", "x")],
        n_per_domain=50,
    )
    d = distributional_distance(t, "A", "B", "ph1", "x", metric="js")
    assert d == 0.0


def test_authority_js_far_distributions_high():
    """Authority: JS(N(0,1), N(5,1)) is large (close to upper bound).

    Reference: two well-separated gaussians have nearly disjoint
    histogram support, so JS distance approaches sqrt(ln 2) ~ 0.83
    (base 2 -> max 1.0). Confirms the metric is sensitive to mean shift.
    """
    rng = np.random.default_rng(1)
    rA = [{"id": str(i), "x": float(v)} for i, v in enumerate(rng.normal(0, 1, 200))]
    rB = [{"id": str(i), "x": float(v)} for i, v in enumerate(rng.normal(5, 1, 200))]
    da = _domain("A", rA)
    db = _domain("B", rB)
    t = build_tensor([da, db], [_phoneme_all()], [_inv("x", "x")], n_per_domain=200)
    d = distributional_distance(t, "A", "B", "ph1", "x", metric="js")
    assert d > 0.5, f"expected JS distance > 0.5, got {d}"


def test_authority_identity_join_returns_nonempty_on_shared_key(shared_key_tensor):
    """Authority: identity_join on two domains with key={0..4} returns 5 rows.

    Reference: by construction, both domains share key values 0,1,2,3,4
    via the synthetic 'key' field. Hand-computed: 5 distinct keys, each
    appearing in both domains, so DataFrame has 5 rows.
    """
    df = identity_join(shared_key_tensor, key_invariant="key")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5
    # Both domains' value columns exist (x is the only non-key value invariant).
    assert "A__x" in df.columns and "B__x" in df.columns


def test_authority_cross_domain_correlation_matches_scipy_pearsonr(tiny_tensor):
    """Authority: pearson_r matches scipy.stats.pearsonr on flattened cells.

    Reference: for the tiny_tensor, cells (ph1, x) and (ph1, y) flatten
    to (D*N,) arrays. pearsonr gives the canonical Pearson r on the
    paired finite values; cross_domain_correlation must agree.
    """
    res = cross_domain_correlation(
        tiny_tensor, "ph1", "x", "ph1", "y", n_bootstrap=100, seed=0,
    )
    # Pull the same flattened paired values directly
    data = tiny_tensor["data"]
    masks = tiny_tensor["masks"]
    pi = tiny_tensor["axes"]["phoneme"].index("ph1")
    iia = tiny_tensor["axes"]["invariant"].index("x")
    iib = tiny_tensor["axes"]["invariant"].index("y")
    a = data[:, :, pi, iia].ravel()
    b = data[:, :, pi, iib].ravel()
    ma = masks[:, :, pi, iia].ravel()
    mb = masks[:, :, pi, iib].ravel()
    valid = ma & mb & np.isfinite(a) & np.isfinite(b)
    expected_r, expected_p = pearsonr(a[valid], b[valid])
    assert res["pearson_r"] == pytest.approx(float(expected_r), abs=1e-12)
    assert res["p_value"] == pytest.approx(float(expected_p), abs=1e-12)
    assert res["n_observations"] == int(valid.sum())


# ===========================================================================
# PROPERTY TESTS (3+)
# ===========================================================================


@pytest.mark.parametrize("metric", ["js", "ks", "wass", "mmd"])
def test_property_distributional_distance_is_symmetric(tiny_tensor, metric):
    """Property: d(A, B) == d(B, A) for all metrics in the supported set."""
    d_ab = distributional_distance(tiny_tensor, "A", "B", "ph1", "x", metric=metric)
    d_ba = distributional_distance(tiny_tensor, "B", "A", "ph1", "x", metric=metric)
    assert d_ab == pytest.approx(d_ba, abs=1e-9)


@pytest.mark.parametrize("metric", ["js", "ks", "wass", "mmd"])
def test_property_distributional_matrix_symmetric_and_zero_diag(tiny_tensor, metric):
    """Property: pairwise matrix is symmetric with zero diagonal."""
    M = distributional_matrix(tiny_tensor, "ph1", "x", metric=metric)
    assert M.shape == (3, 3)
    assert np.allclose(M, M.T, equal_nan=False)
    assert np.allclose(np.diag(M), 0.0)


@pytest.mark.parametrize("metric", ["js", "ks", "wass", "mmd"])
def test_property_distributional_distance_nonnegative(tiny_tensor, metric):
    """Property: d(A, B) >= 0 for all metrics."""
    for da in ("A", "B", "C"):
        for db in ("A", "B", "C"):
            v = distributional_distance(
                tiny_tensor, da, db, "ph1", "x", metric=metric
            )
            assert v >= -1e-12, f"{metric}: d({da},{db}) = {v} negative"


def test_property_identity_join_row_count_bound(shared_key_tensor):
    """Property: identity_join row count <= n_object_per_domain.

    Each unique key can match at most one record per domain, so the
    output never exceeds the per-domain object count.
    """
    df = identity_join(shared_key_tensor, key_invariant="key")
    n_obj = shared_key_tensor["data"].shape[1]
    assert len(df) <= n_obj


def test_property_distributional_matrix_dim_matches_domain_axis(tiny_tensor):
    """Property: matrix shape == (n_domain, n_domain) for all metrics."""
    n = len(tiny_tensor["axes"]["domain"])
    for metric in ("js", "ks", "wass", "mmd"):
        M = distributional_matrix(tiny_tensor, "ph1", "x", metric=metric)
        assert M.shape == (n, n)


# ===========================================================================
# EDGE TESTS (3+)
# ===========================================================================


def test_edge_unknown_metric_raises():
    """Edge: unknown metric -> ValueError listing legal options."""
    rng = np.random.default_rng(0)
    rec = _make_records(rng, n=3)
    da = _domain("A", rec)
    db = _domain("B", rec)
    t = build_tensor([da, db], [_phoneme_all()], [_inv("x", "x")], n_per_domain=3)
    with pytest.raises(ValueError, match="unknown metric"):
        distributional_distance(t, "A", "B", "ph1", "x", metric="unknown")


def test_edge_unknown_domain_raises():
    """Edge: unknown domain in distributional_distance -> KeyError."""
    rng = np.random.default_rng(0)
    rec = _make_records(rng, n=3)
    da = _domain("A", rec)
    db = _domain("B", rec)
    t = build_tensor([da, db], [_phoneme_all()], [_inv("x", "x")], n_per_domain=3)
    with pytest.raises(KeyError):
        distributional_distance(t, "Z", "A", "ph1", "x", metric="js")


def test_edge_identity_join_unknown_key_raises():
    """Edge: identity_join with key_invariant not in invariants -> KeyError."""
    rng = np.random.default_rng(0)
    rec = _make_records(rng, n=3)
    da = _domain("A", rec)
    db = _domain("B", rec)
    t = build_tensor([da, db], [_phoneme_all()], [_inv("x", "x")], n_per_domain=3)
    with pytest.raises(KeyError):
        identity_join(t, key_invariant="not_a_real_key")


def test_edge_all_nan_cell_returns_nan():
    """Edge: domain with all-NaN values yields NaN distance."""
    nan_inv = InvariantSpec(
        name="nan_only",
        kind="numeric",
        compute_fn=lambda rec, ph: float("nan"),
    )
    rng = np.random.default_rng(0)
    rec = _make_records(rng, n=3)
    da = _domain("A", rec)
    db = _domain("B", rec)
    t = build_tensor([da, db], [_phoneme_all()], [nan_inv], n_per_domain=3)
    v = distributional_distance(t, "A", "B", "ph1", "nan_only", metric="js")
    assert np.isnan(v)


def test_edge_cross_domain_correlation_single_observation_warns(tiny_tensor):
    """Edge: when there are <3 paired observations, return NaN with warning."""
    # Build a tensor with only 1 object so flattening yields tiny n.
    rng = np.random.default_rng(0)
    rec = _make_records(rng, n=1)
    da = _domain("A", rec)
    db = _domain("B", rec)
    t = build_tensor(
        [da, db], [_phoneme_all()], [_inv("x", "x"), _inv("y", "y")], n_per_domain=1
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        res = cross_domain_correlation(t, "ph1", "x", "ph1", "y", n_bootstrap=10)
    assert np.isnan(res["pearson_r"])
    assert any("n_observations" in str(wi.message) for wi in w)


def test_edge_empty_domains_distributional_matrix():
    """Edge: tensor with unique-domain set produces 1x1 zero matrix."""
    rng = np.random.default_rng(0)
    rec = _make_records(rng, n=3)
    da = _domain("A", rec)
    t = build_tensor([da], [_phoneme_all()], [_inv("x", "x")], n_per_domain=3)
    M = distributional_matrix(t, "ph1", "x", metric="js")
    assert M.shape == (1, 1)
    assert M[0, 0] == 0.0


# ===========================================================================
# COMPOSITION TESTS (2+)
# ===========================================================================


@pytest.mark.parametrize("metric", ["js", "ks", "wass", "mmd"])
def test_composition_matrix_reduces_to_pairwise_distance(tiny_tensor, metric):
    """Composition: distributional_matrix[i,j] == distributional_distance(d_i, d_j).

    Verifies the matrix is built from the scalar pairwise primitive.
    """
    domains = tiny_tensor["axes"]["domain"]
    M = distributional_matrix(tiny_tensor, "ph1", "x", metric=metric)
    for i, da in enumerate(domains):
        for j, db in enumerate(domains):
            expected = distributional_distance(
                tiny_tensor, da, db, "ph1", "x", metric=metric
            )
            assert M[i, j] == pytest.approx(expected, abs=1e-12)


def test_composition_silent_islands_subset_of_threshold(tiny_tensor):
    """Composition: every silent-islands pair has distance >= threshold.

    Cross-checks that tensor_silent_islands correctly filters by the
    distributional_matrix it composes against.
    """
    threshold = 0.3
    pairs = tensor_silent_islands(
        tiny_tensor, threshold=threshold, metric="js", phoneme="ph1", invariant="x"
    )
    M = distributional_matrix(tiny_tensor, "ph1", "x", metric="js")
    domains = list(tiny_tensor["axes"]["domain"])
    for (da, db), score in pairs:
        i = domains.index(da)
        j = domains.index(db)
        assert M[i, j] >= threshold
        assert score == pytest.approx(M[i, j], abs=1e-12)


def test_composition_phoneme_score_summary_respects_correlation():
    """Composition: tensor_phoneme_score summary tracks |mean correlation|.

    Build a tensor where x and y are perfectly correlated -> mean |r| ~ 1
    -> 'strong link'. Build another where x and y are independent ->
    mean |r| ~ 0 -> 'weak'.
    """
    rng = np.random.default_rng(0)
    # Strongly linked: y = x (perfectly correlated)
    rec_strong = [{"id": str(i), "x": float(v), "y": float(v)} for i, v in enumerate(rng.normal(0, 1, 20))]
    # Independent
    rec_weak = [
        {"id": str(i), "x": float(rng.normal()), "y": float(rng.normal())}
        for i in range(20)
    ]

    def mk(records, name):
        d = _domain(name, records)
        t = build_tensor([d], [_phoneme_all()], [_inv("x", "x"), _inv("y", "y")], n_per_domain=20)
        return tensor_phoneme_score(t, "ph1")

    strong = mk(rec_strong, "S")
    weak = mk(rec_weak, "W")
    assert strong["mean_correlation"] >= weak["mean_correlation"]
    assert strong["summary"] == "strong link"
    # weak should not be 'strong link' (could be 'weak' or 'partial' due to small-sample noise)
    assert weak["summary"] in ("weak", "partial")


def test_composition_anomaly_surface_aligns_with_surface_anomalies(tiny_tensor):
    """Composition: tensor_anomaly_surface output is the union of the
    surface_anomalies output applied per (phoneme, invariant) cell.

    Re-computes surface_anomalies directly on the same flattened arrays
    and checks the labels overlap.
    """
    from prometheus_math.research.anomaly_surface import surface_anomalies

    # Build the same per-cell records the function builds internally.
    phonemes = list(tiny_tensor["axes"]["phoneme"])
    invariants = list(tiny_tensor["axes"]["invariant"])
    data = tiny_tensor["data"]
    masks = tiny_tensor["masks"]
    records = []
    for pi, ph in enumerate(phonemes):
        for ii, iv in enumerate(invariants):
            a = data[:, :, pi, ii].ravel()
            m = masks[:, :, pi, ii].ravel()
            valid = m & np.isfinite(a)
            zeros = a[valid].astype(float)
            if zeros.size < 10:
                continue
            zeros = np.sort(zeros)
            records.append({"label": f"{ph}/{iv}", "zeros": zeros.tolist()})

    direct = []
    if records:
        try:
            direct = surface_anomalies(
                family_query={},
                n_zeros=max(10, max(len(r["zeros"]) for r in records)),
                p_threshold=0.05,
                n_skip=0,
                zeros_records=records,
            )
        except Exception:
            direct = []

    indirect = tensor_anomaly_surface(tiny_tensor, p_threshold=0.05, n_skip=0)
    direct_labels = sorted(d.get("label") for d in direct)
    indirect_labels = sorted(d.get("label") for d in indirect)
    assert direct_labels == indirect_labels
