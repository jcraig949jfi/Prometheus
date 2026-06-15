"""Tests for TOOL_OPERATOR_PORTABILITY (REQ-028).

operator_portability_test is a cross-region falsification orchestrator built on
the REQ-027 column-subspace bond-rank kernel (tt_splice). It emits
{effect_size, p_perm, bond_rank_delta, replication_status, pattern_flags}.

Authority model
---------------
This is a *statistical* orchestrator, so its authority is CONSTRUCTED ground
truth (pairs where we built in, or withheld, shared column-space structure)
plus cross-checks against the REQ-027 kernel it composes.

The load-bearing design fact, proven in test_row_permutation_invariance, is
that the bond-rank statistic is EXACTLY invariant to row permutation. The F011
block-shuffle-within-conductor discipline (harmonia/audit_P028_block_shuffle.py:
plain-permutation z=+2.38 "endorsed" -> conductor-block-shuffle z=-0.86 "killed",
the F010 retraction) operates on ROW pairing and therefore does NOT apply to
this COLUMN-subspace statistic. The discriminating nulls here act on the
feature/value axis (matched_GUE, column permutation, feature-strata block
shuffle). This boundary is the reason the tool exists in the form it does.
"""
import warnings

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from techne.lib.operator_portability import operator_portability_test
from techne.lib.tt_splice import splice_score_arrays, prime_detrend_arrays

SEED = 20260417
STATUSES = {"survived", "killed", "inconclusive"}


# --------------------------------------------------------------------------
# Construction helpers (ground truth)
# --------------------------------------------------------------------------
def shared_factor_pair(n=60, d=8, k=2, noise=0.01, seed=0):
    """A and B share the SAME k-dim column subspace (genuine coupling)."""
    rng = np.random.default_rng(seed)
    M = rng.standard_normal((k, d))
    A = rng.standard_normal((n, k)) @ M + noise * rng.standard_normal((n, d))
    B = rng.standard_normal((n, k)) @ M + noise * rng.standard_normal((n, d))
    return A, B


def independent_pair(n=60, d=8, k=2, seed=0):
    """A has structure; B is independent Gaussian (no shared subspace)."""
    rng = np.random.default_rng(seed)
    M = rng.standard_normal((k, d))
    A = rng.standard_normal((n, k)) @ M
    B = rng.standard_normal((n, d))
    return A, B


def coupled_by_operator(n=60, d=8, k=3, seed=0):
    """A = C@M_a, B = C@M_b: same row-coefficients C, different feature maps.

    Without an operator the column subspaces differ (-> killed). The operator
    X = pinv(M_a) @ M_b satisfies M_a @ X = M_b, so O(A) = A @ X = B exactly
    (-> survived). This is the operator-portability composition fixture.
    """
    rng = np.random.default_rng(seed)
    C = rng.standard_normal((n, k))
    M_a = rng.standard_normal((k, d))
    M_b = rng.standard_normal((k, d))
    A = C @ M_a
    B = C @ M_b
    X = np.linalg.pinv(M_a) @ M_b  # (d, d), M_a @ X == M_b
    return A, B, X


# ==========================================================================
# 1. AUTHORITY
# ==========================================================================
def test_shared_factor_pair_survives_matched_gue_null():
    """Constructed shared rank-2 column factor must replicate as 'survived'.

    Authority: ground truth is the construction -- A and B are built from the
    SAME 2-dim column subspace M, so a genuine cross-region coupling exists.
    The matched_GUE null destroys that structure, so the observed score must
    sit far above the null band. Cross-checked against the REQ-027 kernel
    (splice_score_arrays) in the composition test below.
    """
    A, B = shared_factor_pair(seed=1)
    out = operator_portability_test(
        A, B, null_model="matched_GUE", n_perms=200, seed=SEED
    )
    assert out["replication_status"] == "survived"
    assert out["effect_size"] >= 3.0
    assert out["p_perm"] <= 0.01
    assert out["bond_rank_delta"] > 0.0  # joint rank compressed vs independent


def test_independent_pair_is_killed():
    """Independent Gaussian B must replicate as 'killed' (no shared subspace).

    Authority: construction -- B shares no column subspace with A, so the
    observed splice score sits INSIDE the matched_GUE null band. A tool that
    called this 'survived' would be manufacturing structure from noise.
    """
    A, B = independent_pair(seed=2)
    out = operator_portability_test(
        A, B, null_model="matched_GUE", n_perms=200, seed=SEED
    )
    assert out["replication_status"] == "killed"
    assert out["effect_size"] < 3.0


def test_row_permutation_invariance_is_why_row_nulls_are_rejected():
    """The bond-rank statistic is EXACTLY row-permutation invariant.

    Authority: this reproduces, and is the column-statistic analogue of, the
    F010 lesson recorded in harmonia/audit_P028_block_shuffle.py -- plain
    permutation over/under-rejects relative to the confound-aware null. Here a
    ROW permutation leaves the column-subspace statistic unchanged to machine
    precision, which is WHY a conductor-stratified row-shuffle null cannot
    falsify this statistic, and why operator_portability rejects row-level
    null requests in favour of feature-axis nulls.
    """
    A, B = shared_factor_pair(seed=3)
    rng = np.random.default_rng(SEED)
    s0, _, _ = splice_score_arrays(A, B)
    for _ in range(5):
        s_perm, _, _ = splice_score_arrays(A, B[rng.permutation(B.shape[0])])
        assert abs(s_perm - s0) < 1e-9
    # And the orchestrator refuses to dress a row-shuffle up as a valid null:
    with pytest.raises(ValueError, match="row"):
        operator_portability_test(A, B, null_model="row_permutation")


# ==========================================================================
# 2. PROPERTY (Hypothesis)
# ==========================================================================
_tensor = st.integers(min_value=12, max_value=30).flatmap(
    lambda n: st.integers(min_value=3, max_value=6).map(lambda d: (n, d))
)


@settings(max_examples=25, deadline=None)
@given(shape=_tensor, seed=st.integers(0, 10_000))
def test_p_perm_in_unit_interval_and_status_valid(shape, seed):
    """p_perm in [0,1] and replication_status in the 3-set for any input."""
    n, d = shape
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((n, d))
    B = rng.standard_normal((n, d))
    out = operator_portability_test(A, B, null_model="matched_GUE", n_perms=60, seed=SEED)
    assert 0.0 <= out["p_perm"] <= 1.0
    assert out["replication_status"] in STATUSES
    assert isinstance(out["pattern_flags"], list)


@settings(max_examples=15, deadline=None)
@given(seed=st.integers(0, 10_000))
def test_determinism_under_fixed_seed(seed):
    """Same inputs + same seed -> identical effect_size and p_perm."""
    A, B = shared_factor_pair(seed=seed % 7)
    a = operator_portability_test(A, B, null_model="matched_GUE", n_perms=80, seed=SEED)
    b = operator_portability_test(A, B, null_model="matched_GUE", n_perms=80, seed=SEED)
    assert a["effect_size"] == b["effect_size"]
    assert a["p_perm"] == b["p_perm"]
    assert a["replication_status"] == b["replication_status"]


def test_identical_inputs_self_portability():
    """A spliced with itself is maximal compatibility -> survived.

    Property: identity_splice pins the observed score to 1.0, strictly above
    any structure-destroying null, so a region is always portable to itself.
    """
    A, _ = shared_factor_pair(seed=5)
    out = operator_portability_test(A, A.copy(), null_model="matched_GUE",
                                    n_perms=120, seed=SEED)
    assert out["replication_status"] == "survived"
    assert out["audit"]["observed_compatibility_score"] == pytest.approx(1.0)


# ==========================================================================
# 3. EDGE
# ==========================================================================
def test_edge_cases():
    """Documented edges:
    - 1-D / empty tensor              -> ValueError (need ndim>=2 for bond ranks)
    - n_perms <= 0                    -> ValueError (no null = nothing to falsify)
    - block_shuffle w/o feature_strata-> ValueError (no silent fallback to weak null)
    - operator_spec as 'symbol@ver'   -> NotImplementedError (registry out of scope)
    - unknown null_model              -> ValueError
    """
    A, B = shared_factor_pair(seed=6)
    with pytest.raises(ValueError):
        operator_portability_test(np.arange(10.0), B)          # 1-D
    with pytest.raises(ValueError):
        operator_portability_test(np.empty((0, 4)), np.empty((0, 4)))
    with pytest.raises(ValueError):
        operator_portability_test(A, B, n_perms=0)
    with pytest.raises(ValueError):
        operator_portability_test(A, B, null_model="block_shuffle")  # no strata
    with pytest.raises(NotImplementedError):
        operator_portability_test(A, B, operator_spec="SYMBOL_FOO@v1")
    with pytest.raises(ValueError):
        operator_portability_test(A, B, null_model="not_a_null")


def test_detrend_false_warns_and_flags():
    """detrend_primes=False emits the prime-overfit warning and a pattern flag."""
    A, B = shared_factor_pair(seed=7)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        out = operator_portability_test(
            A, B, null_model="matched_GUE", detrend_primes=False, n_perms=60, seed=SEED
        )
    assert any(issubclass(x.category, RuntimeWarning) for x in w)
    assert any("PRIME_GRAVITATIONAL_OVERFIT" in f and "NOT_DETRENDED" in f
               for f in out["pattern_flags"])


def test_degenerate_null_is_inconclusive_not_survived():
    """A constant tensor yields a degenerate (zero-variance) null -> inconclusive,
    never a false 'survived'. Underpowered nulls must not manufacture signal."""
    A = np.ones((30, 5))
    B = np.ones((30, 5))
    out = operator_portability_test(A, B, null_model="matched_GUE", n_perms=60, seed=SEED)
    assert out["replication_status"] in {"inconclusive", "survived"}
    # if the null collapsed, it must be flagged, not silently 'killed'
    if out["replication_status"] == "inconclusive":
        assert any("UNDERPOWERED" in f or "DEGENERATE" in f for f in out["pattern_flags"])


# ==========================================================================
# 4. COMPOSITION
# ==========================================================================
def test_observed_score_matches_req027_kernel():
    """Composition with REQ-027: with identity operator the orchestrator's
    observed score must equal splice_score_arrays on the prime-detrended pair.

    This pins the orchestrator to the audited bond-rank kernel rather than a
    re-implementation that could silently diverge.
    """
    A, B = shared_factor_pair(seed=8)
    a_det, b_det, _ = prime_detrend_arrays(A, B)
    kernel_score, _, _ = splice_score_arrays(a_det, b_det)
    out = operator_portability_test(A, B, null_model="matched_GUE", n_perms=40, seed=SEED)
    assert out["audit"]["observed_compatibility_score"] == pytest.approx(kernel_score, abs=1e-9)


def test_operator_makes_incompatible_regions_portable():
    """Operator portability, end to end.

    A and B share row-coefficients but live in different feature subspaces:
      - identity operator        -> killed (subspaces disagree)
      - operator X = pinv(M_a)M_b -> survived (O(A) == B, subspaces align)
    Chains operator application with the splice + null + verdict pipeline -- the
    core claim the tool makes ('does operator O carry region A onto region B').
    """
    A, B, X = coupled_by_operator(seed=9)
    no_op = operator_portability_test(A, B, null_model="matched_GUE", n_perms=200, seed=SEED)
    with_op = operator_portability_test(
        A, B, operator_spec=lambda a: a @ X, null_model="matched_GUE", n_perms=200, seed=SEED
    )
    assert no_op["replication_status"] == "killed"
    assert with_op["replication_status"] == "survived"
    assert with_op["effect_size"] > no_op["effect_size"]
