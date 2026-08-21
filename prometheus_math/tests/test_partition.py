"""TDD suite for prometheus_math.partition — the four required categories."""
from __future__ import annotations

import math
import pathlib
import sys

import pytest
from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.partition import (  # noqa: E402
    PartitionError, entropy, induced_partition, mutual_information, refines,
    variation_of_information,
)

P = lambda *blocks: tuple(frozenset(b) for b in blocks)


# ---- 1. authority --------------------------------------------------------------------------

def test_entropy_of_a_uniform_partition_is_log2_of_the_block_count():
    """Hand computation. Four singleton blocks over four points: H = -4 * (1/4) log2(1/4) = 2.
    Two equal blocks over four points: H = 1. The one-block partition: H = 0."""
    assert entropy(P([0], [1], [2], [3]), 4) == pytest.approx(2.0)
    assert entropy(P([0, 1], [2, 3]), 4) == pytest.approx(1.0)
    assert entropy(P([0, 1, 2, 3]), 4) == pytest.approx(0.0)


def test_variation_of_information_on_meila_style_extremes():
    """Reference: Meilă (2007), J. Multivariate Anal. 98, 873–895, §2.

    VI between the all-singletons partition and the one-block partition over n points is
    H(singletons) + H(one block) − 2·I = log2(n) + 0 − 0 = log2(n). Hand-checked at n = 4:
    the two partitions share no information, so VI = 2.0 bits.
    """
    singles, whole = P([0], [1], [2], [3]), P([0, 1, 2, 3])
    assert mutual_information(singles, whole, 4) == pytest.approx(0.0)
    assert variation_of_information(singles, whole, 4) == pytest.approx(2.0)


def test_refinement_identity_VI_equals_entropy_difference():
    """Meilă (2007) §3: when P refines Q, I(P, Q) = H(Q), so VI(P, Q) = H(P) − H(Q).
    Hand-checked: P = singletons (H = 2), Q = two pairs (H = 1), VI must be exactly 1."""
    fine, coarse = P([0], [1], [2], [3]), P([0, 1], [2, 3])
    assert refines(fine, coarse, 4)
    assert mutual_information(fine, coarse, 4) == pytest.approx(entropy(coarse, 4))
    assert variation_of_information(fine, coarse, 4) == pytest.approx(
        entropy(fine, 4) - entropy(coarse, 4))


# ---- 2. property (Hypothesis) ----------------------------------------------------------------

def _partition_from_labels(labels):
    buckets = {}
    for i, lab in enumerate(labels):
        buckets.setdefault(lab, []).append(i)
    return tuple(frozenset(v) for v in buckets.values())


labels = st.lists(st.integers(min_value=0, max_value=4), min_size=2, max_size=12)


@settings(max_examples=200, deadline=None)
@given(labels, labels)
def test_VI_is_a_pseudometric_nonneg_symmetric_and_zero_on_identity(a, b):
    """Meilă's central property. Checked here: non-negativity, symmetry, and VI(P, P) = 0."""
    n = min(len(a), len(b))
    p, q = _partition_from_labels(a[:n]), _partition_from_labels(b[:n])
    vi = variation_of_information(p, q, n)
    assert vi >= -1e-12
    assert vi == pytest.approx(variation_of_information(q, p, n))
    assert variation_of_information(p, p, n) == pytest.approx(0.0)


@settings(max_examples=120, deadline=None)
@given(labels, labels, labels)
def test_VI_satisfies_the_triangle_inequality(a, b, c):
    """The property that makes it a METRIC rather than a similarity — and the reason it can be
    chained across a sequence of evaluator views without the comparison degrading."""
    n = min(len(a), len(b), len(c))
    p, q, r = (_partition_from_labels(x[:n]) for x in (a, b, c))
    ab = variation_of_information(p, q, n)
    bc = variation_of_information(q, r, n)
    ac = variation_of_information(p, r, n)
    assert ac <= ab + bc + 1e-9


@settings(max_examples=150, deadline=None)
@given(labels)
def test_entropy_and_MI_bounds(a):
    n = len(a)
    p = _partition_from_labels(a)
    singles = tuple(frozenset([i]) for i in range(n))
    assert 0.0 - 1e-12 <= entropy(p, n) <= math.log2(n) + 1e-12
    assert mutual_information(p, p, n) == pytest.approx(entropy(p, n))
    assert refines(singles, p, n)                      # singletons refine everything


# ---- 3. edge cases ---------------------------------------------------------------------------

def test_partition_edges():
    """Edges covered:
    - empty ground set: PartitionError (not 0 bits — undefined)
    - empty block: PartitionError
    - overlapping blocks: PartitionError (a cover is not a partition)
    - incomplete cover: PartitionError
    - singleton ground set: entropy 0, VI 0
    - the two lattice extremes: singletons refine everything, everything refines the one-block
    - refinement is NOT symmetric
    """
    with pytest.raises(PartitionError):
        entropy((), 0)
    with pytest.raises(PartitionError):
        entropy(P([0, 1], []), 2)
    with pytest.raises(PartitionError):
        entropy(P([0, 1], [1]), 2)
    with pytest.raises(PartitionError):
        entropy(P([0]), 2)

    assert entropy(P([0]), 1) == pytest.approx(0.0)
    assert variation_of_information(P([0]), P([0]), 1) == pytest.approx(0.0)

    fine, coarse = P([0], [1], [2], [3]), P([0, 1], [2, 3])
    assert refines(fine, coarse, 4) and not refines(coarse, fine, 4)


def test_incomparable_partitions_refine_in_neither_direction():
    """The case the cycle-019 correction is about: two evaluator views that are INCOMPARABLE,
    so there is no finest projection short of the join and incapacity must be argued per
    observation class."""
    a, b = P([0, 1], [2, 3]), P([0, 2], [1, 3])
    assert not refines(a, b, 4) and not refines(b, a, 4)
    assert variation_of_information(a, b, 4) > 0.0


def test_pathological_scale():
    """1,000 points in 250 blocks; the refinement identity still holds exactly."""
    n = 1000
    fine = tuple(frozenset([i]) for i in range(n))
    coarse = tuple(frozenset(range(k, k + 4)) for k in range(0, n, 4))
    assert refines(fine, coarse, n)
    assert variation_of_information(fine, coarse, n) == pytest.approx(
        entropy(fine, n) - entropy(coarse, n))


# ---- 4. composition ---------------------------------------------------------------------------

def test_composes_with_the_aliasing_factorization_check():
    """Chain: `refines` and `aliasing.verify_factorization` must agree on the same data, by two
    different code paths — one partition-theoretic, one pairwise."""
    from techne.ladder_circuits.aliasing import verify_factorization
    items = list(range(12))
    fine_key, coarse_key = lambda i: i % 6, lambda i: i % 2
    fine = induced_partition(items, fine_key)
    coarse = induced_partition(items, coarse_key)
    assert refines(fine, coarse, len(items))
    assert verify_factorization(items, coarse_key, fine_key)
    assert not refines(coarse, fine, len(items))
    assert not verify_factorization(items, fine_key, coarse_key)


def test_composes_with_induced_partition_over_a_real_rung_projection():
    """Chain into the R0 circuit's own key functions: the canonical key induces a strictly
    COARSER partition than the exact AST key, which is precisely what canonicalisation is for.
    Two code paths again — sympy's srepr and the partition lattice."""
    import sympy as sp
    from techne.ladder_circuits.r0_pattern import ast_key, canonical_key
    x, y, a, b = sp.symbols("x y a b")
    # canonical_key quotients by variable RENAMING, so renamed twins merge and nothing else does
    exprs = [x + y, a + b, x * y, a * b, x + 1, a + 1]
    fine = induced_partition(exprs, ast_key)
    coarse = induced_partition(exprs, canonical_key)
    assert refines(fine, coarse, len(exprs))
    assert len(fine) == 6 and len(coarse) == 3
    assert variation_of_information(fine, coarse, len(exprs)) == pytest.approx(
        entropy(fine, 6) - entropy(coarse, 6))


# ---- cycle 023: conditional entropy and the sweep-direction identity ---------------------------

def test_conditional_entropy_hand_computed():
    """H(P|Q) = H(P) - I(P,Q). Singletons given two pairs over four points:
    H(P) = 2, I = H(Q) = 1, so H(P|Q) = 1 — the one bit of "which member of the pair"."""
    from prometheus_math.partition import conditional_entropy
    fine, coarse = P([0], [1], [2], [3]), P([0, 1], [2, 3])
    assert conditional_entropy(fine, coarse, 4) == pytest.approx(1.0)
    assert conditional_entropy(coarse, fine, 4) == pytest.approx(0.0)   # fine refines coarse


@settings(max_examples=250, deadline=None)
@given(labels, labels)
def test_THE_IDENTITY_conditional_entropy_vanishes_exactly_on_refinement(a, b):
    """**The identity the cycle-023 sweep rests on.** H(P|Q) = 0 if and only if Q refines P.

    This is what makes the two sweep directions one measurement: aliasing is H(T|P) > 0 and
    splitting is H(P|T) > 0, and VI is their sum.
    """
    from prometheus_math.partition import conditional_entropy
    n = min(len(a), len(b))
    p, q = _partition_from_labels(a[:n]), _partition_from_labels(b[:n])
    assert (conditional_entropy(p, q, n) < 1e-12) == refines(q, p, n)
    assert (conditional_entropy(q, p, n) < 1e-12) == refines(p, q, n)


@settings(max_examples=200, deadline=None)
@given(labels, labels)
def test_VI_decomposes_into_the_two_sweep_directions(a, b):
    """VI(P, Q) = H(P|Q) + H(Q|P), exactly. Excess plus deficit."""
    from prometheus_math.partition import conditional_entropy
    n = min(len(a), len(b))
    p, q = _partition_from_labels(a[:n]), _partition_from_labels(b[:n])
    assert variation_of_information(p, q, n) == pytest.approx(
        conditional_entropy(p, q, n) + conditional_entropy(q, p, n))


# ---- cycle 024: chains and the data-processing inequality --------------------------------------

def test_refinement_chain_detection():
    """A pipeline induces a chain automatically; a stage reading something it was not handed
    breaks the property. Hand-checked on the two extremes plus a violation."""
    from prometheus_math.partition import is_refinement_chain
    singles, pairs, whole = P([0], [1], [2], [3]), P([0, 1], [2, 3]), P([0, 1, 2, 3])
    assert is_refinement_chain([singles, pairs, whole], 4)
    assert not is_refinement_chain([whole, pairs, singles], 4)
    assert not is_refinement_chain([pairs, P([0, 2], [1, 3])], 4)   # incomparable


def test_DATA_PROCESSING_INEQUALITY_on_a_hand_built_chain():
    """Reference: Cover & Thomas, *Elements of Information Theory* 2nd ed., Thm 2.8.1.

    Along a refinement chain, deficit H(T|P) can only rise and excess H(P|T) can only fall.
    Hand-checked: truth = the two pairs. Singletons see it exactly (deficit 0, excess 1);
    the pairs partition IS the truth (0, 0); the one-block partition has lost it (deficit 1,
    excess 0).
    """
    from prometheus_math.partition import information_profile
    singles, pairs, whole = P([0], [1], [2], [3]), P([0, 1], [2, 3]), P([0, 1, 2, 3])
    prof = information_profile([singles, pairs, whole], pairs, 4)
    assert prof[0] == pytest.approx((0.0, 1.0))
    assert prof[1] == pytest.approx((0.0, 0.0))
    assert prof[2] == pytest.approx((1.0, 0.0))
    deficits = [d for d, _ in prof]
    excesses = [e for _, e in prof]
    assert deficits == sorted(deficits)
    assert excesses == sorted(excesses, reverse=True)


@settings(max_examples=120, deadline=None)
@given(labels, labels)
def test_DPI_holds_for_any_chain_built_by_coarsening(a, b):
    """Property form: build a chain by successively coarsening, and the two columns must move
    in opposite directions for ANY truth partition."""
    from prometheus_math.partition import information_profile, is_refinement_chain
    n = min(len(a), len(b))
    fine = tuple(frozenset([i]) for i in range(n))
    mid = _partition_from_labels(a[:n])
    whole = (frozenset(range(n)),)
    chain = [fine, mid, whole]
    assert is_refinement_chain(chain, n)
    prof = information_profile(chain, _partition_from_labels(b[:n]), n)
    for k in range(len(prof) - 1):
        assert prof[k][0] <= prof[k + 1][0] + 1e-9
        assert prof[k][1] >= prof[k + 1][1] - 1e-9
