"""Tests for prometheus_math.combinatorics_partitions.

Test categories per techne/skills/math-tdd.md (>= 2 in each):

- Authority: known partition counts, hook-length formula values,
  Frame-Robinson-Thrall, Stanley hook-content, classical Schur
  polynomials. References cited per test.
- Property: conjugate involution, partition sum, RSK shape equality,
  RSK round-trip, hook-length positivity, sum-of-squares = n!.
- Edge: empty partition, n=0, malformed cells, max_var=0, max_entry=0,
  RSK on empty.
- Composition: RSK + inverse, hook-content vs direct enumeration,
  Jacobi-Trudi check, Schur expansion vs SSYT enumeration.
"""
from __future__ import annotations

from math import factorial

import pytest
import sympy
from hypothesis import HealthCheck, given, settings, strategies as st

from prometheus_math.combinatorics_partitions import (
    partitions_of,
    num_partitions,
    conjugate,
    hook_length,
    hook_length_array,
    num_standard_young_tableaux,
    num_ssyt,
    all_standard_young_tableaux,
    rsk,
    inverse_rsk,
    schur_polynomial,
    bulgey,
)


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_num_partitions_zero():
    """p(0) = 1 (empty partition).

    Reference: Andrews, "The Theory of Partitions" (1976), Ch. 1, where
    p(n) is defined with p(0) = 1 by convention (vacuous product /
    empty sum). Also OEIS A000041 a(0) = 1.
    """
    assert num_partitions(0) == 1


def test_num_partitions_one():
    """p(1) = 1.

    Reference: OEIS A000041 a(1) = 1; the only partition of 1 is (1).
    """
    assert num_partitions(1) == 1


def test_num_partitions_five():
    """p(5) = 7.

    Reference: OEIS A000041 a(5) = 7. Partitions of 5:
    (5), (4,1), (3,2), (3,1,1), (2,2,1), (2,1,1,1), (1,1,1,1,1).
    """
    assert num_partitions(5) == 7


def test_num_partitions_one_hundred():
    """p(100) = 190569292.

    Reference: OEIS A000041 a(100) = 190569292. Famous Hardy-Ramanujan
    asymptotic test point; also the value Ramanujan computed by hand.
    """
    assert num_partitions(100) == 190569292


def test_num_syt_two_one():
    """f^{(2,1)} = 2.

    Reference: Sagan, "The Symmetric Group" (2nd ed., 2001), eqn 3.10.
    The two SYT of shape (2,1):
        [[1,2],[3]]   and   [[1,3],[2]].
    Frame-Robinson-Thrall: 3! / (3 * 1 * 1) = 6/3 = 2.
    """
    assert num_standard_young_tableaux((2, 1)) == 2


def test_num_syt_three_two():
    """f^{(3,2)} = 5.

    Reference: Sagan (2001), Example 3.10.4. Hook lengths of (3,2):
        [[4, 3, 1],
         [2, 1]]
    f = 5! / (4*3*1*2*1) = 120/24 = 5.
    """
    assert num_standard_young_tableaux((3, 2)) == 5


def test_num_syt_single_row():
    """f^{(n,)} = 1 for any n (only one way to fill a row 1..n).

    Reference: Stanley, EC2, Prop. 7.10.6 (single-row case).
    """
    for n in [1, 2, 3, 5, 8]:
        assert num_standard_young_tableaux((n,)) == 1


def test_num_syt_single_column():
    """f^{(1^n)} = 1 for any n (only one way to fill a column 1..n).

    Reference: Stanley, EC2, Prop. 7.10.6 (single-column case, equivalent
    via conjugation to the single-row case).
    """
    for n in [1, 2, 3, 5, 8]:
        assert num_standard_young_tableaux(tuple([1] * n)) == 1


def test_num_ssyt_two_one_max_three():
    """SSYT count for shape (2,1), entries in {1,2,3}: 8.

    Reference: Stanley hook-content formula (EC2, Cor. 7.21.4):
    s_lambda(1,1,1) = product_c (max_entry + content(c)) / hook(c).
    For lambda = (2,1), cells are (0,0), (0,1), (1,0).
    Contents: 0, 1, -1. Hooks: 3, 1, 1.
    Product = (3+0)(3+1)(3-1) / (3 * 1 * 1) = 3 * 4 * 2 / 3 = 8.

    Direct enumeration gives the same: SSYT of shape (2,1) with
    entries <= 3 are (writing rows top-down, left-justified):
    row1=[1,1] row2=[2]; row1=[1,1] row2=[3];
    row1=[1,2] row2=[2]; row1=[1,2] row2=[3];
    row1=[1,3] row2=[2]; row1=[1,3] row2=[3];
    row1=[2,2] row2=[3]; row1=[2,3] row2=[3]. Total 8.
    """
    assert num_ssyt((2, 1), max_entry=3) == 8


def test_schur_polynomial_one_box():
    """s_(1)(x_1, x_2) = x_1 + x_2 = e_1 = h_1 = p_1.

    Reference: Macdonald, "Symmetric Functions and Hall Polynomials"
    (2nd ed., 1995), I.3, eqn 3.1.
    """
    x1, x2 = sympy.symbols("x_1 x_2")
    expr = sympy.expand(schur_polynomial((1,), max_var=2))
    assert sympy.simplify(expr - (x1 + x2)) == 0


def test_schur_polynomial_two_columns():
    """s_(1,1)(x_1, x_2) = x_1 * x_2 = e_2.

    Reference: Macdonald (1995), I.3.4. The conjugate of (1,1) is (2),
    and s_{(1^k)} = e_k.
    """
    x1, x2 = sympy.symbols("x_1 x_2")
    expr = sympy.expand(schur_polynomial((1, 1), max_var=2))
    assert sympy.simplify(expr - (x1 * x2)) == 0


def test_schur_polynomial_two_row():
    """s_(2)(x_1, x_2) = x_1^2 + x_1 x_2 + x_2^2 = h_2.

    Reference: Macdonald (1995), I.3.4. s_{(n)} = h_n (complete
    homogeneous).
    """
    x1, x2 = sympy.symbols("x_1 x_2")
    expr = sympy.expand(schur_polynomial((2,), max_var=2))
    expected = x1 ** 2 + x1 * x2 + x2 ** 2
    assert sympy.simplify(expr - expected) == 0


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


@given(st.integers(min_value=0, max_value=12))
def test_num_partitions_matches_enumeration(n):
    """len(partitions_of(n)) == num_partitions(n)."""
    assert len(partitions_of(n)) == num_partitions(n)


@given(st.integers(min_value=0, max_value=10))
def test_partitions_sum_to_n(n):
    """Each partition of n sums to n."""
    for p in partitions_of(n):
        assert sum(p) == n


_partition_strategy = st.lists(
    st.integers(min_value=1, max_value=8), min_size=0, max_size=6
).map(lambda xs: tuple(sorted(xs, reverse=True)))


@given(_partition_strategy)
def test_conjugate_involution(partition):
    """conjugate(conjugate(p)) == p."""
    assert conjugate(conjugate(partition)) == partition


@given(_partition_strategy)
def test_hook_lengths_positive(partition):
    """All hook lengths are positive integers."""
    if not partition:
        return
    arr = hook_length_array(partition)
    for row in arr:
        for h in row:
            assert h >= 1


@given(st.integers(min_value=0, max_value=6))
def test_sum_of_squares_of_syt_equals_factorial(n):
    """RSK / Burnside: sum_{lambda |- n} (f^lambda)^2 = n!.

    The classical result; see Sagan (2001), Thm 3.6.4.
    """
    total = sum(num_standard_young_tableaux(p) ** 2 for p in partitions_of(n))
    assert total == factorial(n)


@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(st.permutations(list(range(1, 6))))
def test_rsk_shape_equality(perm):
    """RSK: shape(P) == shape(Q)."""
    P, Q = rsk(perm)
    shape_p = tuple(len(r) for r in P)
    shape_q = tuple(len(r) for r in Q)
    assert shape_p == shape_q


@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(st.permutations(list(range(1, 6))))
def test_rsk_inverse_roundtrip(perm):
    """inverse_rsk(rsk(perm)) == perm."""
    P, Q = rsk(perm)
    assert inverse_rsk(P, Q) == list(perm)


# ---------------------------------------------------------------------------
# Edge tests
# ---------------------------------------------------------------------------


def test_partitions_of_zero():
    """partitions_of(0) == [()] — the empty partition is the only
    partition of 0, and it is non-empty as a list (it has one element,
    the empty tuple).
    """
    assert partitions_of(0) == [()]


def test_partitions_of_zero_with_k_zero():
    """partitions_of(0, k=0) == [()] (only the empty partition).
    For n=0 and k>0, no partitions exist (empty list).
    """
    assert partitions_of(0, k=0) == [()]
    assert partitions_of(0, k=1) == []


def test_num_syt_empty_partition():
    """f^{()} = 1 (the unique empty tableau)."""
    assert num_standard_young_tableaux(()) == 1


def test_hook_length_out_of_bounds():
    """Out-of-bounds (i, j) raises ValueError."""
    with pytest.raises(ValueError):
        hook_length((3, 2), 5, 0)
    with pytest.raises(ValueError):
        hook_length((3, 2), 0, 10)
    with pytest.raises(ValueError):
        hook_length((3, 2), 1, 2)  # row 1 has only 2 cells (j=0,1)


def test_rsk_empty_permutation():
    """RSK on the empty permutation yields a pair of empty tableaux."""
    P, Q = rsk([])
    assert P == []
    assert Q == []


def test_num_ssyt_max_entry_zero():
    """num_ssyt(empty_partition, max_entry=0) == 1; for non-empty,
    max_entry=0 returns 0.
    """
    assert num_ssyt((), max_entry=0) == 1
    assert num_ssyt((1,), max_entry=0) == 0
    assert num_ssyt((2, 1), max_entry=0) == 0


def test_schur_polynomial_max_var_zero():
    """Schur poly with no variables: 0 for non-empty partition,
    1 for empty partition.
    """
    assert schur_polynomial((), max_var=0) == 1
    assert schur_polynomial((1,), max_var=0) == 0
    assert schur_polynomial((2, 1), max_var=0) == 0


def test_num_partitions_with_distinct_parts():
    """Number of partitions of n with distinct parts equals number of
    partitions into odd parts (Euler).

    For n=5: distinct parts -> {(5), (4,1), (3,2)} = 3 partitions.
    Reference: Euler's classical theorem; OEIS A000009 a(5) = 3.
    """
    parts = partitions_of(5, distinct=True)
    assert len(parts) == 3
    assert all(len(set(p)) == len(p) for p in parts)


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


def test_rsk_composition_burnside_check():
    """Composition: sum over partitions of n of f^lambda^2 = n!,
    AND each permutation of S_n produces a valid (P, Q) pair whose
    common shape is some partition of n. Both invariants must hold;
    this composition test asserts both.
    """
    from itertools import permutations as iperm
    n = 4
    # Burnside identity:
    total = sum(num_standard_young_tableaux(p) ** 2 for p in partitions_of(n))
    assert total == factorial(n)
    # Every permutation has an RSK pair of the same shape, and that
    # shape is a partition of n:
    for perm in iperm(range(1, n + 1)):
        P, Q = rsk(list(perm))
        shape = tuple(len(r) for r in P)
        assert sum(shape) == n
        assert shape in [tuple(p) for p in partitions_of(n)]


def test_rsk_full_roundtrip_explicit():
    """Direct RSK + inverse_rsk roundtrip on a hand-traced example.

    Reference example: Schensted's original 1961 paper, the permutation
    [1, 4, 2, 5, 3] should yield insertion tableau
        P = [[1, 2, 3], [4, 5]]
    and recording tableau
        Q = [[1, 2, 4], [3, 5]].
    See Sagan (2001), Example 3.5.4.
    """
    perm = [1, 4, 2, 5, 3]
    P, Q = rsk(perm)
    assert P == [[1, 2, 3], [4, 5]]
    assert Q == [[1, 2, 4], [3, 5]]
    assert inverse_rsk(P, Q) == perm


def test_hook_content_matches_direct_enumeration():
    """Hook-content formula matches direct SSYT enumeration for small
    shapes.

    Reference: Stanley EC2, Cor. 7.21.4. We check several shapes against
    the count of all SSYT enumerated explicitly.
    """
    from prometheus_math.combinatorics_partitions import (
        all_semi_standard_young_tableaux,
    )
    for shape in [(1,), (2,), (1, 1), (2, 1), (2, 2), (3, 1)]:
        for max_entry in [1, 2, 3]:
            direct = len(all_semi_standard_young_tableaux(shape, max_entry))
            formula = num_ssyt(shape, max_entry)
            assert direct == formula, (shape, max_entry, direct, formula)


def test_jacobi_trudi_check():
    """Jacobi-Trudi: s_lambda = det(h_{lambda_i + j - i})_{i,j=1..ell}.

    Reference: Macdonald (1995), I.3.4 (eqn 3.4). We verify on shape
    (2, 1) with two variables.
    """
    x1, x2 = sympy.symbols("x_1 x_2")
    # h_n(x1, x2) = sum of x1^i * x2^(n-i) for i in [0, n]
    def h(n):
        if n < 0:
            return sympy.Integer(0)
        if n == 0:
            return sympy.Integer(1)
        return sum(x1 ** i * x2 ** (n - i) for i in range(n + 1))

    # lambda = (2, 1), ell = 2
    # JT matrix M[i][j] = h_{lambda_i + j - i} for i,j in 1..2
    # M = [[h_{2 + 1 - 1}, h_{2 + 2 - 1}],
    #      [h_{1 + 1 - 2}, h_{1 + 2 - 2}]]
    #    = [[h_2, h_3],
    #       [h_0, h_1]]
    M = sympy.Matrix([
        [h(2), h(3)],
        [h(0), h(1)],
    ])
    jt = sympy.expand(M.det())
    sch = sympy.expand(schur_polynomial((2, 1), max_var=2))
    assert sympy.simplify(jt - sch) == 0


def test_bulgey_summary():
    """bulgey returns (n, length) — composition of sum + len; trivial
    but exercises the public summary surface alongside partitions_of.
    """
    for p in partitions_of(7)[:5]:
        n, ell = bulgey(p)
        assert n == sum(p)
        assert ell == len(p)


def test_all_syt_count_matches_formula():
    """Composition: len(all_standard_young_tableaux(lambda)) ==
    num_standard_young_tableaux(lambda) for several shapes.

    Cross-checks the brute-force generator against the FRT formula.
    """
    for shape in [(1,), (2,), (1, 1), (2, 1), (3, 1), (2, 2), (3, 2)]:
        direct = len(all_standard_young_tableaux(shape))
        formula = num_standard_young_tableaux(shape)
        assert direct == formula, (shape, direct, formula)
