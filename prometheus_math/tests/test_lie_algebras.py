"""Tests for prometheus_math.algebra_lie_algebras (project #88 phase 1).

Test categories per techne/skills/math-tdd.md (>= 2 in each):

- Authority: Cartan matrices for A_2, B_2, G_2 from Humphreys
  "Introduction to Lie Algebras", Section 11.4 / Bourbaki Lie IV-VI
  Plates I-IX. Weyl group orders for A_n, B_n, D_n, E_6, E_7, E_8
  from Humphreys 2.10. Number of positive roots from Bourbaki Plates.
  Adjoint representation dimensions (e.g. dim E_8 = 248).
- Property: Cartan diagonal == 2; Cartan off-diagonals are non-positive
  integers; |all_roots| == 2 * |positive_roots|; reflections are
  involutions; |W(A_n)| matches (n+1)!; rho relation 2*rho = sum of
  positive roots; weights satisfy duality with simple roots.
- Edge: invalid type raises ValueError; rank < 1 raises; rank > 8 for
  E raises; D_1 raises; G_n with n != 2 raises; F_n with n != 4 raises;
  is_dominant_weight on negative weight returns False.
- Composition: weyl_dim_formula(0,...,0) == 1; weyl_dim_formula(highest
  root of A_n) == n^2 + 2n (adjoint); 2 * sum(fundamental_weights) ==
  sum(positive_roots); root_height(highest_root) == h - 1 where h is
  Coxeter number.
"""
from __future__ import annotations

import math

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from prometheus_math.algebra_lie_algebras import (
    cartan_matrix,
    simple_roots,
    positive_roots,
    all_roots,
    fundamental_weights,
    weyl_group_order,
    weyl_group_generators,
    weyl_dim_formula,
    dynkin_diagram_string,
    is_dominant_weight,
    longest_weyl_element,
    root_height,
)


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_cartan_matrix_a2_against_humphreys_11_4():
    """A_2 Cartan matrix is [[2,-1],[-1,2]].

    Reference: Humphreys, "Introduction to Lie Algebras and
    Representation Theory", Section 11.4, Table 1. Also Bourbaki Lie
    IV-VI Plate I (sl_3).
    """
    C = cartan_matrix("A", 2)
    assert C.shape == (2, 2)
    assert np.array_equal(C, np.array([[2, -1], [-1, 2]]))


def test_cartan_matrix_b2_against_bourbaki_plate_ii():
    """B_2 Cartan matrix has [[2,-2],[-1,2]] (long-short convention).

    Reference: Bourbaki Lie IV-VI Plate II. We adopt the convention
    a_{ij} = 2(alpha_i, alpha_j)/(alpha_j, alpha_j); for B_2 with
    alpha_1 long and alpha_2 short, this gives a_{12} = -2, a_{21} = -1.
    Equivalent to Humphreys Table after possibly transposing rows/cols.
    """
    C = cartan_matrix("B", 2)
    # Either [[2,-2],[-1,2]] or its transpose, depending on root ordering
    # convention. Either way, off-diagonal product is +2.
    assert C[0, 0] == 2 and C[1, 1] == 2
    assert C[0, 1] * C[1, 0] == 2
    assert {int(C[0, 1]), int(C[1, 0])} == {-1, -2}


def test_cartan_matrix_g2_against_humphreys():
    """G_2 has the unique 2x2 Cartan matrix with a_{ij}*a_{ji} = 3.

    Reference: Humphreys, Section 11.4. The (long, short) angle
    encodes |a_{12}|*|a_{21}| = 3 (cos^2 = 3/4).
    """
    C = cartan_matrix("G", 2)
    assert C[0, 0] == 2 and C[1, 1] == 2
    assert C[0, 1] * C[1, 0] == 3
    assert {int(C[0, 1]), int(C[1, 0])} == {-1, -3}


def test_weyl_group_orders_classical_against_humphreys_2_10():
    """Classical Weyl group orders.

    Reference: Humphreys, Section 2.10 / Section 12.2. Bourbaki Lie
    IV-VI Plates I-IV.
    - |W(A_n)| = (n+1)!
    - |W(B_n)| = |W(C_n)| = 2^n n!
    - |W(D_n)| = 2^{n-1} n!
    """
    assert weyl_group_order("A", 1) == 2  # = 2!
    assert weyl_group_order("A", 4) == 120  # = 5!
    assert weyl_group_order("A", 5) == 720  # = 6!
    assert weyl_group_order("B", 3) == 48  # = 2^3 * 3!
    assert weyl_group_order("B", 4) == 384  # = 2^4 * 4!
    assert weyl_group_order("C", 3) == 48
    assert weyl_group_order("D", 4) == 192  # = 2^3 * 4!
    assert weyl_group_order("D", 5) == 1920  # = 2^4 * 5!


def test_weyl_group_orders_exceptional_against_bourbaki():
    """Exceptional Weyl group orders.

    Reference: Bourbaki Lie IV-VI Plates V-IX.
    |W(E_6)| = 51840, |W(E_7)| = 2903040, |W(E_8)| = 696729600,
    |W(F_4)| = 1152, |W(G_2)| = 12.
    """
    assert weyl_group_order("E", 6) == 51840
    assert weyl_group_order("E", 7) == 2903040
    assert weyl_group_order("E", 8) == 696729600
    assert weyl_group_order("F", 4) == 1152
    assert weyl_group_order("G", 2) == 12


def test_positive_roots_count_against_bourbaki():
    """Number of positive roots.

    Reference: Bourbaki Lie IV-VI Plates I-IX.
    A_n: n(n+1)/2; B_n: n^2; C_n: n^2; D_n: n(n-1);
    E_6: 36; E_7: 63; E_8: 120; F_4: 24; G_2: 6.
    """
    assert len(positive_roots("A", 3)) == 6  # 3*4/2
    assert len(positive_roots("A", 4)) == 10  # 4*5/2
    assert len(positive_roots("B", 3)) == 9  # 3^2
    assert len(positive_roots("B", 4)) == 16
    assert len(positive_roots("C", 3)) == 9
    assert len(positive_roots("D", 4)) == 12  # 4*3
    assert len(positive_roots("D", 5)) == 20  # 5*4
    assert len(positive_roots("E", 6)) == 36
    assert len(positive_roots("E", 7)) == 63
    assert len(positive_roots("E", 8)) == 120
    assert len(positive_roots("F", 4)) == 24
    assert len(positive_roots("G", 2)) == 6


def test_e8_adjoint_dimension_equals_248():
    """dim E_8 = 248.

    Reference: Humphreys 12.2 / well-known. dim(g) = 2*|Phi^+| + rank
    = 2*120 + 8 = 248.
    """
    pos = positive_roots("E", 8)
    assert 2 * len(pos) + 8 == 248


def test_e7_adjoint_dimension_equals_133():
    """dim E_7 = 133 (= 2*63 + 7).

    Reference: Humphreys 12.2.
    """
    pos = positive_roots("E", 7)
    assert 2 * len(pos) + 7 == 133


# ---------------------------------------------------------------------------
# Property tests (Hypothesis)
# ---------------------------------------------------------------------------


# Strategy: pick a (type, rank) pair from the classical & exceptional list.
_VALID_PAIRS = [
    ("A", 1), ("A", 2), ("A", 3), ("A", 4), ("A", 5),
    ("B", 2), ("B", 3), ("B", 4),
    ("C", 2), ("C", 3), ("C", 4),
    ("D", 4), ("D", 5),
    ("E", 6), ("E", 7), ("E", 8),
    ("F", 4),
    ("G", 2),
]


@pytest.mark.parametrize("type_,rank", _VALID_PAIRS)
def test_cartan_matrix_diagonal_is_two(type_, rank):
    """Cartan matrices have 2 on the diagonal (definition).

    Reference: Humphreys 9.4, definition of Cartan matrix.
    """
    C = cartan_matrix(type_, rank)
    assert C.shape == (rank, rank)
    for i in range(rank):
        assert C[i, i] == 2


@pytest.mark.parametrize("type_,rank", _VALID_PAIRS)
def test_cartan_matrix_offdiagonal_nonpositive_integers(type_, rank):
    """Off-diagonal Cartan entries are non-positive integers in {0,-1,-2,-3}.

    Reference: Humphreys 9.4, axiom (C2).
    """
    C = cartan_matrix(type_, rank)
    for i in range(rank):
        for j in range(rank):
            if i == j:
                continue
            assert C[i, j] in (0, -1, -2, -3), (
                f"{type_}_{rank} C[{i},{j}] = {C[i,j]} out of range"
            )


@pytest.mark.parametrize("type_,rank", _VALID_PAIRS)
def test_all_roots_is_double_positive(type_, rank):
    """all_roots = positive_roots ∪ -positive_roots, |all| = 2 * |pos|."""
    pos = positive_roots(type_, rank)
    allr = all_roots(type_, rank)
    assert len(allr) == 2 * len(pos)
    # Each negative root is the negation of some positive one.
    pos_set = {tuple(p.tolist()) for p in pos}
    neg_set = {tuple((-p).tolist()) for p in pos}
    expected = pos_set | neg_set
    actual = {tuple(r.tolist()) for r in allr}
    assert actual == expected


@pytest.mark.parametrize("type_,rank", _VALID_PAIRS)
def test_weyl_generators_are_involutions(type_, rank):
    """Each simple reflection s_i satisfies s_i^2 = I."""
    gens = weyl_group_generators(type_, rank)
    for s in gens:
        prod = s @ s
        assert np.allclose(prod, np.eye(prod.shape[0]), atol=1e-9)


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_weyl_an_is_symmetric_group(n):
    """|W(A_n)| = (n+1)!."""
    assert weyl_group_order("A", n) == math.factorial(n + 1)


@pytest.mark.parametrize("type_,rank", _VALID_PAIRS)
def test_two_rho_equals_sum_positive_roots(type_, rank):
    """2*rho = sum of positive roots, where rho = sum of fundamental weights.

    Reference: Humphreys 13.3 / Bourbaki Lie VI Section 1.10.
    """
    weights = fundamental_weights(type_, rank)
    pos = positive_roots(type_, rank)
    two_rho = 2 * weights.sum(axis=0)
    sum_pos = pos.sum(axis=0)
    assert np.allclose(two_rho, sum_pos, atol=1e-8), (
        f"{type_}_{rank}: 2*rho = {two_rho}, sum_pos = {sum_pos}"
    )


@pytest.mark.parametrize("type_,rank", _VALID_PAIRS)
def test_weight_simple_root_duality(type_, rank):
    """⟨ω_j, alpha_i^∨⟩ = δ_ij where alpha_i^∨ = 2 alpha_i / (alpha_i,alpha_i).

    Reference: Humphreys 13.1, definition of fundamental weights.
    """
    weights = fundamental_weights(type_, rank)
    roots = simple_roots(type_, rank)
    rank_ = roots.shape[0]
    for j in range(rank_):
        for i in range(rank_):
            ai = roots[i]
            wj = weights[j]
            pairing = 2 * np.dot(wj, ai) / np.dot(ai, ai)
            expected = 1.0 if i == j else 0.0
            assert abs(pairing - expected) < 1e-8, (
                f"{type_}_{rank}: <omega_{j}, alpha_{i}^v> = {pairing}, "
                f"expected {expected}"
            )


# ---------------------------------------------------------------------------
# Edge tests
# ---------------------------------------------------------------------------


def test_invalid_type_raises():
    """Edge: type must be one of A, B, C, D, E, F, G."""
    with pytest.raises(ValueError, match="type"):
        cartan_matrix("X", 3)
    with pytest.raises(ValueError, match="type"):
        positive_roots("Z", 2)
    with pytest.raises(ValueError, match="type"):
        weyl_group_order("", 4)


def test_rank_below_one_raises():
    """Edge: rank must be >= 1 (and >= 2 for some types)."""
    with pytest.raises(ValueError):
        cartan_matrix("A", 0)
    with pytest.raises(ValueError):
        cartan_matrix("A", -1)
    with pytest.raises(ValueError):
        positive_roots("A", 0)


def test_e_rank_out_of_range_raises():
    """Edge: E_n only exists for n in {6, 7, 8}."""
    with pytest.raises(ValueError):
        cartan_matrix("E", 5)
    with pytest.raises(ValueError):
        cartan_matrix("E", 9)
    with pytest.raises(ValueError):
        weyl_group_order("E", 4)


def test_f_rank_must_be_four():
    """Edge: F_n only exists for n = 4."""
    with pytest.raises(ValueError):
        cartan_matrix("F", 3)
    with pytest.raises(ValueError):
        cartan_matrix("F", 5)


def test_g_rank_must_be_two():
    """Edge: G_n only exists for n = 2."""
    with pytest.raises(ValueError):
        cartan_matrix("G", 1)
    with pytest.raises(ValueError):
        cartan_matrix("G", 3)


def test_b_c_rank_one_raises_or_falls_back_to_a1():
    """Edge: B_1, C_1 are isomorphic to A_1 — we require rank >= 2.

    D_1 is trivial (one-dimensional torus, no roots), and D_2 = A_1 x A_1
    is reducible — we require rank >= 2 for B/C and rank >= 3 for D
    (or we accept rank == 2 returning the A_1 x A_1 reducible case).
    """
    with pytest.raises(ValueError):
        cartan_matrix("B", 1)
    with pytest.raises(ValueError):
        cartan_matrix("C", 1)
    with pytest.raises(ValueError):
        cartan_matrix("D", 1)
    with pytest.raises(ValueError):
        cartan_matrix("D", 2)


def test_dominant_weight_negative_returns_false():
    """Edge: weight with any negative coefficient is NOT dominant."""
    # In fundamental weight basis: (1, -1) is not dominant.
    assert not is_dominant_weight([1, -1], "A", 2)
    # Empty weight => ValueError
    with pytest.raises(ValueError):
        is_dominant_weight([], "A", 2)
    # Wrong length => ValueError
    with pytest.raises(ValueError):
        is_dominant_weight([1, 0, 0], "A", 2)


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("type_,rank", _VALID_PAIRS)
def test_weyl_dim_trivial_weight_is_one(type_, rank):
    """Trivial representation has dimension 1.

    Composition: weyl_dim_formula(0,...,0) == 1. Cross-check with
    rho computed via fundamental_weights.
    """
    zero_weight = [0] * rank
    assert weyl_dim_formula(type_, rank, zero_weight) == 1


@pytest.mark.parametrize("n", [2, 3, 4, 5])
def test_weyl_dim_adjoint_an_is_n_squared_plus_2n(n):
    """The adjoint rep of A_n has highest weight ω_1 + ω_n (theta).

    Reference: Humphreys 13.1, the adjoint rep of sl_{n+1} has dimension
    (n+1)^2 - 1 = n^2 + 2n.

    Composition: ties weyl_dim_formula to fundamental_weights and
    positive_roots.
    """
    # Highest root of A_n in fundamental weight basis: (1, 0, ..., 0, 1).
    hw = [0] * n
    hw[0] = 1
    hw[-1] = 1
    if n == 1:
        # A_1 special: highest root is 2*omega_1, dim = 3.
        hw = [2]
    expected = n * n + 2 * n
    assert weyl_dim_formula("A", n, hw) == expected


def test_root_height_highest_root_a3_equals_three():
    """Highest root of A_3 has height 3 = h - 1 where h = 4 is the
    Coxeter number.

    Reference: Humphreys 12.2, Coxeter number h(A_n) = n+1.

    Composition: ties root_height to positive_roots and simple_roots.
    """
    pos = positive_roots("A", 3)
    sroots = simple_roots("A", 3)
    heights = [root_height(p, sroots) for p in pos]
    # Highest root = max height
    assert max(heights) == 3  # h - 1 for A_3
    assert min(heights) == 1  # simple roots have height 1


def test_root_height_highest_root_e8_equals_29():
    """Highest root of E_8 has height 29 = 30 - 1, where 30 is the
    Coxeter number of E_8.

    Reference: Humphreys 12.2 / Bourbaki Lie VI Plate VII.
    """
    pos = positive_roots("E", 8)
    sroots = simple_roots("E", 8)
    heights = [root_height(p, sroots) for p in pos]
    assert max(heights) == 29


def test_dynkin_diagram_string_a3():
    """Dynkin diagram for A_3 should be 3 nodes in a line.

    Composition test: smoke-test that the diagram printer is consistent
    with rank.
    """
    s = dynkin_diagram_string("A", 3)
    assert isinstance(s, str)
    assert "A_3" in s or "A3" in s
    # 3 nodes
    assert s.count("o") + s.count("O") + s.count("*") >= 3


def test_longest_weyl_element_is_involution_or_minus_identity_on_an():
    """w_0^2 = e for any finite Weyl group.

    For A_n (n >= 2), w_0 acts as the diagram involution on simple
    roots; for B/C/D_{2k}/E_7/E_8/F_4/G_2, w_0 = -1 on the root lattice.

    Composition: ties longest_weyl_element to weyl_group_generators.
    """
    for type_, rank in [("A", 3), ("B", 3), ("D", 4), ("E", 6), ("G", 2)]:
        w0 = longest_weyl_element(type_, rank)
        # w_0 must be an involution
        I = np.eye(w0.shape[0])
        assert np.allclose(w0 @ w0, I, atol=1e-8)


def test_dominant_weight_consistency_with_simple_roots():
    """A weight is dominant iff its expansion in fundamental weights
    has non-negative coefficients.

    Composition: ties is_dominant_weight to fundamental_weights basis.
    """
    # In fundamental weight basis (Dynkin labels):
    assert is_dominant_weight([1, 1], "A", 2)
    assert is_dominant_weight([0, 0, 1], "A", 3)
    assert is_dominant_weight([1, 0, 0, 0, 0, 0, 0, 0], "E", 8)
    assert not is_dominant_weight([0, -1, 0, 0, 0, 0, 0, 0], "E", 8)
