"""TDD suite for prometheus_math.tensor_train — TT ranks with the correct null baked in.

Written FIRST (math-tdd). Wraps quimb's MatrixProductState.from_dense (Standing Order #1).

The doctrinal point this module exists to enforce (feedback_null_must_perturb_the_statistics_axis,
REQ-028): TT bond rank measures CROSS-AXIS COUPLING, and a null that permutes whole slices
along an axis is *provably rank-invariant* — a degenerate null that "kills" nothing. The
correct structure-destroying null shuffles entries independently within fibers, preserving
per-fiber marginals while destroying alignment. The API ships only the correct null, and a
property test proves WHY the tempting one is degenerate.

Categories: authority (hand-computed TT ranks + numpy matricization-rank theorem as second
tool), property (Hypothesis), edge, composition (real signature_index occupancy + planted-
structure null detection).
"""
from __future__ import annotations

import math
import pathlib
import sys

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.tensor_train import (  # noqa: E402
    tt_ranks,
    tt_reconstruct,
    tt_rank_null_test,
    signature_occupancy_tensor,
)

RNG = np.random.default_rng(20260821)


def rank1(dims):
    vecs = [RNG.random(d) + 0.1 for d in dims]
    out = vecs[0]
    for v in vecs[1:]:
        out = np.multiply.outer(out, v)
    return out


# ------------------------------------------------------------------ authority

def test_rank_one_tensor_has_all_bond_ranks_one():
    """Hand computation: an outer product a⊗b⊗c factors exactly with bond dimension 1 at
    every cut (each TT core is the corresponding vector). Reference: definition of TT rank;
    verified by hand for dims (4,5,6)."""
    assert tt_ranks(rank1((4, 5, 6)), cutoff=1e-12) == [1, 1]


def test_sum_of_three_rank_ones_has_bond_ranks_three():
    """Hand computation: TT rank at each cut <= CP rank, with equality generically for random
    terms. Sum of 3 independent rank-1 tensors on dims (5,6,7): unfoldings are sums of 3
    generic outer products -> matrix rank 3 at both cuts."""
    t = sum(rank1((5, 6, 7)) for _ in range(3))
    assert tt_ranks(t, cutoff=1e-10) == [3, 3]


def test_delta_tensor_bond_ranks_equal_dimension():
    """Hand computation: δ_ijk on (4,4,4). Unfolding at cut 1 is the 4x16 matrix with rows
    e_i ⊗ e_i — rank 4. TT ranks are [4,4]."""
    d = np.zeros((4, 4, 4))
    for i in range(4):
        d[i, i, i] = 1.0
    assert tt_ranks(d, cutoff=1e-12) == [4, 4]


def test_tt_rank_equals_numpy_matricization_rank_second_tool():
    """Cross-tool authority (rubric score 3): the TT-SVD theorem — bond rank at cut k equals
    the matrix rank of the k-th unfolding. quimb's ranks must match numpy.linalg.matrix_rank
    computed independently on the unfoldings, for a structured low-rank tensor."""
    t = sum(rank1((4, 5, 6, 3)) for _ in range(2))
    ranks = tt_ranks(t, cutoff=1e-10)
    dims = t.shape
    for k in range(1, len(dims)):
        unf = t.reshape(int(np.prod(dims[:k])), -1)
        assert ranks[k - 1] == np.linalg.matrix_rank(unf, tol=1e-8), f"cut {k}"


# ------------------------------------------------------------------ property (Hypothesis)

dims_strategy = st.lists(st.integers(min_value=2, max_value=5), min_size=3, max_size=4)


@given(dims_strategy)
@settings(max_examples=25, deadline=None)
def test_reconstruction_within_tolerance(dims):
    """The TT at cutoff c reconstructs the tensor to relative Frobenius error ~c."""
    t = sum(rank1(dims) for _ in range(2))
    err = np.linalg.norm(tt_reconstruct(t, cutoff=1e-9) - t) / np.linalg.norm(t)
    assert err < 1e-6


@given(dims_strategy, st.integers(0, 3))
@settings(max_examples=25, deadline=None)
def test_slice_permutation_along_any_axis_is_rank_invariant(dims, axis_seed):
    """THE DEGENERATE-NULL PROOF, as a property: permuting whole slices along one axis is a
    relabeling — TT ranks are invariant. This is exactly why slice-permutation must never be
    used as the null for a rank statistic (F011 lesson, REQ-028)."""
    t = sum(rank1(dims) for _ in range(2))
    axis = axis_seed % t.ndim
    perm = RNG.permutation(t.shape[axis])
    shuffled = np.take(t, perm, axis=axis)
    assert tt_ranks(shuffled, cutoff=1e-10) == tt_ranks(t, cutoff=1e-10)


@given(dims_strategy)
@settings(max_examples=20, deadline=None)
def test_ranks_bounded_by_unfolding_dimensions(dims):
    t = np.abs(RNG.standard_normal(tuple(dims)))
    ranks = tt_ranks(t, cutoff=1e-12)
    for k in range(1, len(dims)):
        bound = min(int(np.prod(dims[:k])), int(np.prod(dims[k:])))
        assert 1 <= ranks[k - 1] <= bound


@given(dims_strategy)
@settings(max_examples=15, deadline=None)
def test_looser_cutoff_never_increases_ranks(dims):
    t = np.abs(RNG.standard_normal(tuple(dims)))
    tight = tt_ranks(t, cutoff=1e-12)
    loose = tt_ranks(t, cutoff=1e-2)
    assert all(l <= s for l, s in zip(loose, tight))


# ------------------------------------------------------------------ edge

def test_edge_cases():
    """Edges: scalar/1-D input (no cut exists) -> ValueError; NaN -> ValueError; negative
    cutoff -> ValueError; zero tensor -> ValueError (rank undefined, refuse rather than
    fabricate); integer dtype (occupancy counts) accepted and cast."""
    with pytest.raises(ValueError, match="ndim"):
        tt_ranks(np.array(3.0))
    with pytest.raises(ValueError, match="ndim"):
        tt_ranks(np.arange(5.0))
    with pytest.raises(ValueError, match="NaN"):
        bad = np.ones((3, 3, 3))
        bad[0, 0, 0] = np.nan
        tt_ranks(bad)
    with pytest.raises(ValueError, match="cutoff"):
        tt_ranks(np.ones((2, 2, 2)), cutoff=-1)
    with pytest.raises(ValueError, match="zero"):
        tt_ranks(np.zeros((3, 3, 3)))
    counts = np.arange(24).reshape(2, 3, 4)  # int occupancy
    assert all(r >= 1 for r in tt_ranks(counts))


# ------------------------------------------------------------------ composition

def test_null_test_detects_planted_structure_and_calibrates_on_noise():
    """Composition of the whole pipeline: a planted low-rank tensor must sit BELOW the null
    distribution (low percentile: coupling exists); the same test on an already-shuffled
    tensor must NOT report structure (calibration: percentile not extreme)."""
    planted = sum(rank1((6, 6, 6)) for _ in range(2)) + 0.01 * np.abs(
        RNG.standard_normal((6, 6, 6))
    )
    res = tt_rank_null_test(planted, cutoff=1e-3, n_null=40, seed=7)
    assert res["percentile"] <= 0.05, res
    assert res["null"] == "fiber_shuffle"

    destroyed = res["one_null_sample"]
    res2 = tt_rank_null_test(destroyed, cutoff=1e-3, n_null=40, seed=11)
    assert res2["percentile"] > 0.05, res2


def test_signature_index_occupancy_composes_end_to_end():
    """Real-substrate composition: load the Theseus signature_index ledger into an occupancy
    tensor (generator x claim_kind x verdict_class) and run the full rank+null pipeline.
    Asserts structural sanity, not a discovery: shape matches the vocabulary sizes, total
    count equals the 3,311 ledger rows, ranks within unfolding bounds."""
    db = pathlib.Path(__file__).resolve().parents[2] / "theseus/orchestration/signature_index.sqlite"
    if not db.exists():
        pytest.skip("signature_index.sqlite not on this machine")
    t, axes = signature_occupancy_tensor(db)
    assert t.ndim == 3 and t.sum() == 3311
    assert [len(a) for a in axes.values()] == list(t.shape)
    ranks = tt_ranks(t, cutoff=1e-6)
    for k, r in enumerate(ranks, start=1):
        assert 1 <= r <= min(int(np.prod(t.shape[:k])), int(np.prod(t.shape[k:])))
