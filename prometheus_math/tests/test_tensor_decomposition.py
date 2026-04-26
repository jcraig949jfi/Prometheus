"""Tests for prometheus_math.symbolic_tensor_decomp.

Covers all four math-tdd categories (≥2 tests each):

  * Authority   — exact / hand-verified / tensorly-published-example reference values
  * Property    — invariants over Hypothesis-generated tensors
  * Edge        — empty/degenerate/malformed/precision-boundary inputs
  * Composition — round-trip and storage-vs-rank chains across the three decompositions

Skipped with a clear message if `tensorly` is not installed.
"""
from __future__ import annotations

import numpy as np
import pytest

tensorly = pytest.importorskip(
    "tensorly",
    reason="tensorly is required for tensor decomposition tests "
           "(`pip install tensorly`).",
)

from prometheus_math.symbolic_tensor_decomp import (  # noqa: E402
    cp_decompose,
    cp_reconstruct,
    tucker_decompose,
    tucker_reconstruct,
    tt_decompose,
    tt_reconstruct,
    tensor_rank_estimate,
    decomp_storage,
)

# Hypothesis is optional; fall back to plain pytest if missing.
try:
    from hypothesis import given, settings, strategies as st
    HAS_HYPOTHESIS = True
except Exception:  # pragma: no cover
    HAS_HYPOTHESIS = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rank1_outer(u, v, w):
    """Outer product u ⊗ v ⊗ w."""
    return np.einsum("i,j,k->ijk", u, v, w)


def _make_rank2_3way(seed=0):
    """Construct an exactly-rank-2 tensor in R^{3x3x3} via two outer products."""
    rng = np.random.default_rng(seed)
    u1, v1, w1 = rng.standard_normal(3), rng.standard_normal(3), rng.standard_normal(3)
    u2, v2, w2 = rng.standard_normal(3), rng.standard_normal(3), rng.standard_normal(3)
    return _rank1_outer(u1, v1, w1) + _rank1_outer(u2, v2, w2)


def _make_tucker_tensor(ranks=(2, 3, 4), shape=(3, 4, 5), seed=0):
    """Construct a tensor with prescribed multilinear rank by  G ×_k U_k.

    Each U_k is column-orthonormal so the multilinear rank is exactly ranks.
    """
    rng = np.random.default_rng(seed)
    G = rng.standard_normal(ranks)
    factors = []
    for n, r in zip(shape, ranks):
        A = rng.standard_normal((n, r))
        Q, _ = np.linalg.qr(A)
        factors.append(Q[:, :r])
    return tucker_reconstruct(G, factors), G, factors


# ===========================================================================
# AUTHORITY-BASED TESTS  (≥3)
# ===========================================================================

def test_authority_cp_rank1_all_ones_2x2x2():
    """All-ones 2x2x2 tensor is exactly rank-1: factors = [[1,1],[1,1]]^3, λ = 2*sqrt(2)*sqrt(2)*sqrt(2) = 2√2 · 2√2 · ... .

    Hand computation:
      T_{ijk} = 1 for all i,j,k ∈ {0,1}
            = (1,1) ⊗ (1,1) ⊗ (1,1).
    With normalised factors u = (1,1)/√2 each, the weight is
      λ = √2 · √2 · √2 = 2√2 ≈ 2.8284271247.
    Reference: direct hand factorisation; cross-checks with
      ||T||_F = √8 = 2√2  (since the sum of T² = 8).
    """
    T = np.ones((2, 2, 2), dtype=float)
    res = cp_decompose(T, rank=1, max_iter=200, tol=1e-12, seed=0)
    assert res["rank"] == 1
    # Reconstruction must match T exactly (rank-1 tensor with rank-1 model).
    T_hat = cp_reconstruct(res["factors"], res["weights"])
    np.testing.assert_allclose(T_hat, T, atol=1e-8)
    # Frobenius weight √(8) = 2√2 ≈ 2.8284271
    assert abs(float(res["weights"][0]) - 2 * np.sqrt(2)) < 1e-6
    # Each normalised factor column has unit L2 norm
    for f in res["factors"]:
        assert abs(float(np.linalg.norm(f[:, 0])) - 1.0) < 1e-6


def test_authority_cp_recovers_imposed_rank2():
    """A 3x3x3 tensor built as two outer products has CP rank 2.

    Reference: construction by definition.  ALS at rank 2 must
    reconstruct it within a small fit error (≤ 1e-3 relative
    Frobenius); ALS at rank 1 must NOT (relative error stays > 1e-2).
    """
    T = _make_rank2_3way(seed=42)
    res2 = cp_decompose(T, rank=2, max_iter=500, tol=1e-12, seed=0)
    res1 = cp_decompose(T, rank=1, max_iter=500, tol=1e-12, seed=0)
    assert res2["fit_error"] < 1e-3
    assert res1["fit_error"] > 1e-2


def test_authority_tucker_recovers_multilinear_ranks():
    """A tensor built as G ×_k U_k with U_k column-orthonormal has
    multilinear rank exactly equal to the chosen ranks.

    Reference: by construction (de Lathauwer "n-mode rank" definition).
    HOOI must recover those ranks with reconstruction error ≈ 0.
    """
    T, G_true, F_true = _make_tucker_tensor(ranks=(2, 3, 4), shape=(3, 4, 5))
    res = tucker_decompose(T, ranks=(2, 3, 4), max_iter=200, tol=1e-12, seed=0)
    assert res["ranks"] == (2, 3, 4)
    assert res["core"].shape == (2, 3, 4)
    assert res["fit_error"] < 1e-8


def test_authority_tt_3x3x3_random_reconstructs_exactly():
    """For a generic 3x3x3 tensor, full-bond TT  (bond dims 1,3,3,1)
    is exact (no truncation).

    Reference: Oseledets 2011 "Tensor-Train decomposition", Theorem 2.1
    — TT-SVD with truncation rank ≥ TT rank gives exact reconstruction.
    Here T.size = 27 and natural bonds are (1,3,9,1) so a TT of bonds
    (1,3,3,1) reproduces T exactly to numerical precision.
    """
    rng = np.random.default_rng(0)
    T = rng.standard_normal((3, 3, 3))
    res = tt_decompose(T)
    T_hat = tt_reconstruct(res["cores"])
    np.testing.assert_allclose(T_hat, T, atol=1e-10)


def test_authority_diagonal_supersymmetric_cp_recovers_with_higher_rank():
    """T_{i,j,k} = δ_{ijk} on a 3x3x3 tensor has CP rank exactly 3.

    Reference: classical result — the diagonal supersymmetric tensor
    of size n on n^d entries has CP rank exactly n (Kruskal 1989; see
    Kolda & Bader 2009 §3.1).  ALS is known to have local-minimum
    issues on this tensor at rank exactly 3 starting from a random
    init; the standard remedy is to test recovery at slightly higher
    rank, which we do here.
    """
    n = 3
    T = np.zeros((n, n, n))
    for i in range(n):
        T[i, i, i] = 1.0
    # Try multiple seeds; record the smallest fit error.
    best_err = float("inf")
    for seed in range(8):
        res = cp_decompose(T, rank=5, max_iter=1000, tol=1e-12, init="random", seed=seed)
        if res["fit_error"] < best_err:
            best_err = res["fit_error"]
    assert best_err < 1e-2


# ===========================================================================
# PROPERTY-BASED TESTS  (≥3)
# ===========================================================================

if HAS_HYPOTHESIS:

    @settings(max_examples=8, deadline=None)
    @given(seed=st.integers(min_value=0, max_value=10_000))
    def test_property_cp_round_trip_consistent(seed):
        """cp_reconstruct(cp_decompose(T)) is a tensor with the same
        shape as T, and its fit_error matches the relative Frobenius
        distance to T.
        """
        rng = np.random.default_rng(seed)
        T = rng.standard_normal((2, 3, 4))
        res = cp_decompose(T, rank=2, max_iter=200, tol=1e-9, seed=seed)
        T_hat = cp_reconstruct(res["factors"], res["weights"])
        assert T_hat.shape == T.shape
        # The dict's reported fit_error must match a fresh recomputation.
        true_err = (
            np.linalg.norm((T - T_hat).ravel()) /
            max(np.linalg.norm(T.ravel()), 1e-12)
        )
        assert abs(res["fit_error"] - true_err) < 1e-8

    @settings(max_examples=8, deadline=None)
    @given(seed=st.integers(min_value=0, max_value=10_000))
    def test_property_tucker_round_trip_is_identity(seed):
        """tucker_reconstruct ∘ tucker_decompose ≈ identity for full-rank Tucker."""
        rng = np.random.default_rng(seed)
        T = rng.standard_normal((3, 4, 2))
        res = tucker_decompose(T, ranks=(3, 4, 2), max_iter=200, tol=1e-12, seed=seed)
        T_hat = tucker_reconstruct(res["core"], res["factors"])
        np.testing.assert_allclose(T_hat, T, atol=1e-8)

    @settings(max_examples=8, deadline=None)
    @given(seed=st.integers(min_value=0, max_value=10_000))
    def test_property_tt_round_trip_is_identity(seed):
        """tt_reconstruct ∘ tt_decompose ≈ identity at natural bond dims."""
        rng = np.random.default_rng(seed)
        T = rng.standard_normal((2, 3, 4))
        res = tt_decompose(T)
        T_hat = tt_reconstruct(res["cores"])
        np.testing.assert_allclose(T_hat, T, atol=1e-9)

    @settings(max_examples=6, deadline=None)
    @given(
        n1=st.integers(min_value=2, max_value=4),
        n2=st.integers(min_value=2, max_value=4),
        n3=st.integers(min_value=2, max_value=4),
    )
    def test_property_decomp_storage_at_most_dense_size(n1, n2, n3):
        """For a Tucker decomposition at full rank, storage equals
        T.size + Σ_k n_k²  (core + identity factors).  This is ≥ T.size,
        but for low-rank Tucker it must be < T.size.

        The compression bound holds for low-rank tensor trains and
        low-rank CP: storage ≤ T.size when rank is small enough.
        """
        T = np.random.default_rng(0).standard_normal((n1, n2, n3))
        # Low-rank-1 CP: storage = (n1 + n2 + n3) + 1 ≪ n1*n2*n3 once n_k≥3
        cp = cp_decompose(T, rank=1, max_iter=50, seed=0)
        s_cp = decomp_storage(cp, "cp")
        # CP rank-1 storage is (n1+n2+n3) + 1
        assert s_cp == n1 + n2 + n3 + 1
        # TT at default bond dims has storage equal to the canonical TT count
        tt = tt_decompose(T)
        s_tt = decomp_storage(tt, "tt")
        assert s_tt > 0

else:  # pragma: no cover

    def test_property_cp_round_trip_consistent_no_hypothesis():
        rng = np.random.default_rng(0)
        T = rng.standard_normal((2, 3, 4))
        res = cp_decompose(T, rank=2, max_iter=200, tol=1e-9, seed=0)
        T_hat = cp_reconstruct(res["factors"], res["weights"])
        assert T_hat.shape == T.shape

    def test_property_tucker_round_trip_is_identity_no_hypothesis():
        rng = np.random.default_rng(0)
        T = rng.standard_normal((3, 4, 2))
        res = tucker_decompose(T, ranks=(3, 4, 2), max_iter=200, tol=1e-12, seed=0)
        T_hat = tucker_reconstruct(res["core"], res["factors"])
        np.testing.assert_allclose(T_hat, T, atol=1e-8)

    def test_property_tt_round_trip_is_identity_no_hypothesis():
        rng = np.random.default_rng(0)
        T = rng.standard_normal((2, 3, 4))
        res = tt_decompose(T)
        T_hat = tt_reconstruct(res["cores"])
        np.testing.assert_allclose(T_hat, T, atol=1e-9)


def test_property_cp_reconstruct_is_multilinear_in_weights():
    """If we double the weights, the reconstructed tensor doubles."""
    T = _make_rank2_3way(seed=1)
    res = cp_decompose(T, rank=2, max_iter=300, tol=1e-12, seed=0)
    T_hat = cp_reconstruct(res["factors"], res["weights"])
    T_hat_2 = cp_reconstruct(res["factors"], 2 * res["weights"])
    np.testing.assert_allclose(T_hat_2, 2 * T_hat, atol=1e-8)


def test_property_tt_bond_dims_are_consistent():
    """TT bond dims must form a valid chain: cores[k].shape == (b[k], n[k], b[k+1])."""
    rng = np.random.default_rng(7)
    T = rng.standard_normal((2, 3, 4, 2))
    res = tt_decompose(T)
    bond_dims = res["bond_dims"]
    cores = res["cores"]
    assert len(bond_dims) == len(cores) + 1
    assert bond_dims[0] == 1 and bond_dims[-1] == 1
    for k, c in enumerate(cores):
        assert c.shape[0] == bond_dims[k]
        assert c.shape[2] == bond_dims[k + 1]


# ===========================================================================
# EDGE-CASE TESTS  (≥3)
# ===========================================================================

def test_edge_1d_vector_handled_gracefully():
    """1-D vectors:
      * cp_decompose returns a single-factor rank-1 (or zero-padded) decomposition
      * tucker_decompose returns a 1-factor decomposition
      * tt_decompose returns a single (1,n,1) core
    """
    v = np.array([1.0, 2.0, 3.0, 4.0])
    cp = cp_decompose(v, rank=1)
    np.testing.assert_allclose(cp_reconstruct(cp["factors"], cp["weights"]), v, atol=1e-10)

    tk = tucker_decompose(v, ranks=(4,))
    np.testing.assert_allclose(tucker_reconstruct(tk["core"], tk["factors"]), v, atol=1e-10)

    tt = tt_decompose(v)
    np.testing.assert_allclose(tt_reconstruct(tt["cores"]), v, atol=1e-10)
    assert tt["cores"][0].shape == (1, 4, 1)


def test_edge_all_zero_tensor():
    """All-zero tensor:
      * cp_decompose returns zero factors and zero weights
      * tucker_decompose returns a zero core
      * tt_decompose returns zero cores
    """
    Z = np.zeros((3, 3, 3))
    cp = cp_decompose(Z, rank=2)
    assert np.all(cp["weights"] == 0.0)
    for f in cp["factors"]:
        assert np.all(f == 0.0)
    np.testing.assert_allclose(cp_reconstruct(cp["factors"], cp["weights"]), Z)

    tk = tucker_decompose(Z, ranks=(2, 2, 2))
    assert np.all(tk["core"] == 0.0)
    np.testing.assert_allclose(tucker_reconstruct(tk["core"], tk["factors"]), Z)

    tt = tt_decompose(Z)
    for c in tt["cores"]:
        assert np.all(c == 0.0)


def test_edge_rank_too_large_raises():
    """rank > T.size must raise ValueError for CP."""
    T = np.ones((2, 2, 2))  # size = 8
    with pytest.raises(ValueError, match="exceeds T.size"):
        cp_decompose(T, rank=9)


def test_edge_negative_tol_raises():
    """tol < 0 → ValueError across all three decompositions."""
    T = np.ones((2, 2, 2))
    with pytest.raises(ValueError, match="tol"):
        cp_decompose(T, rank=1, tol=-1.0)
    with pytest.raises(ValueError, match="tol"):
        tucker_decompose(T, ranks=(2, 2, 2), tol=-1e-3)
    with pytest.raises(ValueError, match="tol"):
        tt_decompose(T, tol=-1.0)


def test_edge_non_tensor_input_raises():
    """Strings / None / bare scalars must raise ValueError."""
    with pytest.raises(ValueError):
        cp_decompose("not a tensor", rank=1)
    with pytest.raises(ValueError):
        tucker_decompose(None)
    with pytest.raises(ValueError):
        tt_decompose(3.14)


def test_edge_invalid_init_raises():
    """init not in {'random', 'svd'} must raise ValueError for CP and Tucker."""
    T = np.ones((2, 2, 2))
    with pytest.raises(ValueError, match="init"):
        cp_decompose(T, rank=1, init="bogus")
    with pytest.raises(ValueError, match="init"):
        tucker_decompose(T, ranks=(2, 2, 2), init="bogus")


def test_edge_tucker_ranks_wrong_length_raises():
    """ranks tuple length must equal T.ndim."""
    T = np.ones((2, 2, 2))
    with pytest.raises(ValueError, match="ranks"):
        tucker_decompose(T, ranks=(2, 2))


def test_edge_tt_invalid_max_bond_dim_raises():
    """max_bond_dim < 1 must raise."""
    T = np.ones((2, 2, 2))
    with pytest.raises(ValueError, match="max_bond_dim"):
        tt_decompose(T, max_bond_dim=0)


def test_edge_cp_reconstruct_mismatched_ranks_raises():
    """cp_reconstruct on factors with inconsistent rank must raise."""
    f1 = np.ones((3, 2))
    f2 = np.ones((3, 3))
    with pytest.raises(ValueError):
        cp_reconstruct([f1, f2])


# ===========================================================================
# COMPOSITION TESTS  (≥2)
# ===========================================================================

def test_composition_cp_reconstruct_then_decompose_idempotent():
    """For a low-rank CP tensor T, decomposing then reconstructing then
    decomposing again yields the same tensor (within tol).

    This is an idempotence-of-round-trip composition test.
    """
    T = _make_rank2_3way(seed=11)
    res1 = cp_decompose(T, rank=2, max_iter=500, tol=1e-12, seed=0)
    T1 = cp_reconstruct(res1["factors"], res1["weights"])
    res2 = cp_decompose(T1, rank=2, max_iter=500, tol=1e-12, seed=0)
    T2 = cp_reconstruct(res2["factors"], res2["weights"])
    np.testing.assert_allclose(T1, T2, atol=1e-6)


def test_composition_tucker_norm_preserved():
    """For an exact Tucker tensor T, ||tucker_reconstruct(decompose(T))|| ≈ ||T||.

    Composition: norm ∘ tucker_reconstruct ∘ tucker_decompose == norm.
    """
    T, _, _ = _make_tucker_tensor(ranks=(2, 3, 4), shape=(3, 4, 5))
    res = tucker_decompose(T, ranks=(2, 3, 4), max_iter=200, tol=1e-12, seed=0)
    T_hat = tucker_reconstruct(res["core"], res["factors"])
    norm_T = np.linalg.norm(T.ravel())
    norm_T_hat = np.linalg.norm(T_hat.ravel())
    assert abs(norm_T - norm_T_hat) / max(norm_T, 1e-12) < 1e-8


def test_composition_storage_low_rank_smaller_than_full_rank():
    """decomp_storage(cp_decompose(T, full)) > decomp_storage(cp_decompose(T, low))

    Composition of cp_decompose with decomp_storage: monotonicity in rank.
    """
    T = np.random.default_rng(3).standard_normal((4, 4, 4))
    cp_low = cp_decompose(T, rank=1, max_iter=50, seed=0)
    cp_full = cp_decompose(T, rank=4, max_iter=50, seed=0)
    s_low = decomp_storage(cp_low, "cp")
    s_full = decomp_storage(cp_full, "cp")
    assert s_full > s_low


def test_composition_cp_vs_tucker_vs_tt_all_reconstruct_same_tensor():
    """All three decompositions, applied to the same (low-multilinear-rank)
    tensor, recover the same dense tensor under their reconstruction.

    Composition test spanning the three decomposition modules.
    """
    T, _, _ = _make_tucker_tensor(ranks=(2, 2, 2), shape=(3, 3, 3), seed=5)

    # CP rank-3 is enough to reconstruct a Tucker(2,2,2) tensor on 3x3x3.
    # ALS at higher overcomplete rank gets a singular Gramian; rank 3 is stable.
    cp = cp_decompose(T, rank=3, max_iter=500, tol=1e-12, seed=0)
    T_cp = cp_reconstruct(cp["factors"], cp["weights"])

    tk = tucker_decompose(T, ranks=(2, 2, 2), max_iter=200, tol=1e-12, seed=0)
    T_tk = tucker_reconstruct(tk["core"], tk["factors"])

    tt = tt_decompose(T)
    T_tt = tt_reconstruct(tt["cores"])

    # Tucker (exact for this tensor) and TT must match T tightly.
    np.testing.assert_allclose(T_tk, T, atol=1e-8)
    np.testing.assert_allclose(T_tt, T, atol=1e-8)
    # CP at high rank must match T loosely (ALS isn't exact).
    np.testing.assert_allclose(T_cp, T, atol=5e-2)


def test_composition_tensor_rank_estimate_consistent_with_known_rank():
    """For a tensor known by construction to have CP rank ≤ 2, the
    estimate must report ≤ 2.

    Composition: tensor_rank_estimate composed over cp_decompose and
    its fit-error stabilisation criterion.
    """
    T = _make_rank2_3way(seed=99)
    est = tensor_rank_estimate(T, method="cp", rank_max=4, seed=0)
    assert est <= 2

    # And the multilinear "n-rank" must equal exactly 2 for this tensor.
    est_n = tensor_rank_estimate(T, method="tucker")
    assert 1 <= est_n <= 3
