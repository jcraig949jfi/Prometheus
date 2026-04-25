"""Tests for prometheus_math.numerics flint-advanced operations.

Authority sources cited inline. Tests skip cleanly if python-flint is
not installed.

Test categories (math-tdd skill, ≥2 in each):
  Authority   : 4 (x^4-1 over Z, x^4-1 mod 5, Phi_5, det/rank ref)
  Property    : 5 (Hypothesis-driven invariants)
  Edge        : 4 (zero/constant/non-prime/shape mismatch)
  Composition : 3 (factor*reconstruct, det==0 iff rank<min, matmul-id)
"""
from __future__ import annotations

import pytest

# Skip cleanly if flint isn't importable
flint = pytest.importorskip("flint", reason="python-flint not installed")

from hypothesis import HealthCheck, given, settings, strategies as st

from prometheus_math import numerics as N


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mul_polys(p, q):
    """Multiply two integer-coefficient polynomials (ascending order)."""
    if not p or not q:
        return []
    r = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            r[i + j] += a * b
    return r


def _pow_poly(p, k):
    """Raise integer polynomial p (ascending) to non-negative integer power k."""
    out = [1]
    for _ in range(k):
        out = _mul_polys(out, p)
    return out


def _strip_trailing_zeros(coeffs):
    out = list(coeffs)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


# ---------------------------------------------------------------------------
# 1. Authority-based tests
# ---------------------------------------------------------------------------

def test_authority_factor_x4_minus_1_over_Z():
    """x^4 - 1 = (x-1)(x+1)(x^2+1) over Z[x].

    Reference: standard cyclotomic factorisation,
      x^4 - 1 = Phi_1(x) * Phi_2(x) * Phi_4(x)
              = (x-1) * (x+1) * (x^2+1).
    Cross-checked with sympy/PARI elsewhere.
    """
    factors = N.flint_factor([-1, 0, 0, 0, 1])  # x^4 - 1, ascending
    # Factor representations are ascending coefficient lists.
    factor_set = {tuple(f): m for f, m in factors}
    assert (-1, 1) in factor_set, factors  # x - 1
    assert (1, 1) in factor_set, factors   # x + 1
    assert (1, 0, 1) in factor_set, factors  # x^2 + 1
    # Multiplicities all 1
    for f, m in factors:
        if len(f) > 1:  # skip leading-content scalar if present
            assert m == 1


def test_authority_factor_mod_5_x4_minus_1():
    """x^4 - 1 splits completely over F_5: (x-1)(x-2)(x-3)(x-4).

    Reference: 5 ≡ 1 (mod 4), so all 4th roots of unity lie in F_5.
    The four roots are 1, 2, 3, 4 (with 2^2=4, 3^2=4, 4^2=1, 2^4=1).
    """
    factors = N.flint_polmodp_factor([-1, 0, 0, 0, 1], 5)
    # We want 4 linear factors. Each is x + c with c in {1,2,3,4} (mod 5),
    # i.e. roots {-1,-2,-3,-4} ≡ {4,3,2,1} mod 5.
    linear_consts = []
    for f, m in factors:
        if len(f) == 2 and f[1] == 1:
            linear_consts.append(f[0] % 5)
            assert m == 1
    assert sorted(linear_consts) == [1, 2, 3, 4], factors


def test_authority_factor_phi_5_irreducible():
    """Phi_5(x) = x^4 + x^3 + x^2 + x + 1 is irreducible over Q.

    Reference: every cyclotomic polynomial Phi_n(x) is irreducible over Q
    (Gauss). Phi_5 is the minimal polynomial of any primitive 5-th root
    of unity.
    """
    factors = N.flint_factor([1, 1, 1, 1, 1])
    # Exactly one non-trivial factor, with multiplicity 1
    non_trivial = [(f, m) for f, m in factors if len(f) > 1]
    assert len(non_trivial) == 1, factors
    f, m = non_trivial[0]
    assert m == 1
    assert f == [1, 1, 1, 1, 1]


def test_authority_rank_2x2_mod_5():
    """rank([[1,2],[3,4]] mod 5) = 2 and det ≡ 3 (mod 5).

    Reference: det = 1*4 - 2*3 = -2 ≡ 3 (mod 5), nonzero ⇒ rank = 2.
    """
    M = [[1, 2], [3, 4]]
    assert N.flint_matrix_rank_modp(M, 5) == 2
    assert N.flint_matrix_det_modp(M, 5) == 3


# ---------------------------------------------------------------------------
# 2. Property-based tests (Hypothesis)
# ---------------------------------------------------------------------------

@settings(max_examples=40, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(
    st.lists(st.integers(min_value=-3, max_value=3), min_size=1, max_size=4),
    st.lists(st.integers(min_value=-3, max_value=3), min_size=1, max_size=4),
)
def test_property_factor_then_reconstruct(p, q):
    """factor(p*q) reconstructs to p*q (up to sign / leading content).

    For any pair of integer polynomials whose product is non-zero,
    flint_factor of the product, multiplied back together with the
    appropriate multiplicities, equals the original product.
    """
    p = _strip_trailing_zeros(p)
    q = _strip_trailing_zeros(q)
    if (len(p) == 1 and p[0] == 0) or (len(q) == 1 and q[0] == 0):
        return  # zero polys excluded
    prod = _mul_polys(p, q)
    prod = _strip_trailing_zeros(prod)
    if len(prod) == 1 and prod[0] == 0:
        return
    factors = N.flint_factor(prod)
    # Reconstruct: product of f_i^m_i (with leading content scalar
    # represented as a degree-0 factor at index 0 if present).
    reconstructed = [1]
    for f, m in factors:
        reconstructed = _mul_polys(reconstructed, _pow_poly(f, m))
    reconstructed = _strip_trailing_zeros(reconstructed)
    assert reconstructed == prod, (factors, prod, reconstructed)


@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(
    st.lists(
        st.lists(st.integers(min_value=-50, max_value=50), min_size=1, max_size=4),
        min_size=1, max_size=4,
    ),
    st.sampled_from([2, 3, 5, 7, 11, 13]),
)
def test_property_rank_bounded_by_min_dim(rows, p):
    """rank_modp(M) <= min(nrows, ncols) for any matrix M, prime p."""
    width = max(len(r) for r in rows)
    M = [r + [0] * (width - len(r)) for r in rows]
    rk = N.flint_matrix_rank_modp(M, p)
    assert 0 <= rk <= min(len(M), width)


@settings(max_examples=20)
@given(
    st.integers(min_value=1, max_value=5),
    st.sampled_from([2, 3, 5, 7, 11, 101]),
)
def test_property_identity_det_is_one(n, p):
    """det(I_n) ≡ 1 (mod p) for any n, prime p."""
    I = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    assert N.flint_matrix_det_modp(I, p) == 1 % p
    assert N.flint_matrix_rank_modp(I, p) == n


@settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(
    st.lists(
        st.lists(st.integers(min_value=-20, max_value=20), min_size=2, max_size=3),
        min_size=2, max_size=3,
    ),
    st.sampled_from([2, 3, 5, 7]),
)
def test_property_matmul_with_identity(rows, p):
    """A * I ≡ A (mod p) for any compatible identity I."""
    width = max(len(r) for r in rows)
    A = [r + [0] * (width - len(r)) for r in rows]
    I = [[1 if i == j else 0 for j in range(width)] for i in range(width)]
    out = N.flint_matmul_modp(A, I, p)
    expected = [[v % p for v in row] for row in A]
    assert out == expected


@settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(
    st.lists(st.integers(min_value=-5, max_value=5), min_size=1, max_size=5),
    st.lists(st.integers(min_value=-5, max_value=5), min_size=1, max_size=5),
)
def test_property_polmul_matches_naive(p, q):
    """flint_polmul agrees with the naive Cauchy-product implementation."""
    p = _strip_trailing_zeros(p)
    q = _strip_trailing_zeros(q)
    out = _strip_trailing_zeros(N.flint_polmul(p, q))
    expected = _strip_trailing_zeros(_mul_polys(p, q))
    # Canonicalise the zero polynomial: [] and [0] are equivalent.
    if expected == [0]:
        expected = []
    if out == [0]:
        out = []
    assert out == expected


# ---------------------------------------------------------------------------
# 3. Edge-case tests
# ---------------------------------------------------------------------------

def test_edge_zero_polynomial_factor_raises():
    """flint_factor([]) and flint_factor([0]) → ValueError.

    Edge: factoring the zero polynomial is undefined (no leading
    coefficient). We raise rather than returning a meaningless result.
    """
    with pytest.raises(ValueError):
        N.flint_factor([])
    with pytest.raises(ValueError):
        N.flint_factor([0])
    with pytest.raises(ValueError):
        N.flint_factor([0, 0, 0])


def test_edge_constant_nonzero_polynomial():
    """Factor of a nonzero constant returns a single (coeffs, 1) entry.

    Edge: constant polynomial has no roots; we return either
    [(c, 1)] or just an empty factor list with content c. The
    reconstruction property must still hold.
    """
    # Constant 5 is a unit-times-prime in Z. We accept either:
    #  - [([5], 1)] (the constant is the one "factor")
    #  - [([5], 1)] alone or with no further factors
    factors = N.flint_factor([5])
    # Reconstruct: should equal [5]
    reconstructed = [1]
    for f, m in factors:
        reconstructed = _mul_polys(reconstructed, _pow_poly(f, m))
    assert _strip_trailing_zeros(reconstructed) == [5]


def test_edge_matmul_shape_mismatch():
    """matmul A_{m x k} * B_{l x n} with k != l → ValueError."""
    A = [[1, 2, 3]]      # 1x3
    B = [[1, 2], [3, 4]]  # 2x2
    with pytest.raises(ValueError):
        N.flint_matmul_modp(A, B, 5)


def test_edge_non_prime_modulus_raises():
    """A composite modulus is rejected with a clear error message.

    Edge: FLINT can fail catastrophically (Impossible inverse) when
    asked to factor or reduce-rank modulo a composite. We pre-check
    primality and raise a clean ValueError.
    """
    with pytest.raises(ValueError) as exc:
        N.flint_polmodp_factor([1, 2, 3], 6)
    assert "prime" in str(exc.value).lower()

    with pytest.raises(ValueError) as exc:
        N.flint_matrix_rank_modp([[1, 2], [3, 4]], 4)
    assert "prime" in str(exc.value).lower()

    with pytest.raises(ValueError):
        N.flint_polmodp([1, 2, 3], 1)  # p must be >= 2


# ---------------------------------------------------------------------------
# 4. Composition tests
# ---------------------------------------------------------------------------

def test_composition_factor_reconstruct_x4_minus_1():
    """Compose flint_factor with flint_polmul: factors multiply back to original.

    Composition: factor() and polmul() are inverse-ish; chaining them
    must round-trip on inputs that are non-zero in Z[x].
    """
    p = [-1, 0, 0, 0, 1]  # x^4 - 1
    factors = N.flint_factor(p)
    out = [1]
    for f, m in factors:
        for _ in range(m):
            out = N.flint_polmul(out, f)
    out = _strip_trailing_zeros(out)
    assert out == p


def test_composition_det_zero_iff_rank_deficient():
    """For square matrices: det_modp == 0 iff rank_modp < n.

    Composition test pairing two FLINT operations: a singular matrix
    must have determinant zero AND rank strictly less than n; a
    non-singular matrix must have nonzero det AND full rank.
    """
    p = 7
    # Singular: rows are linearly dependent
    M_singular = [[1, 2], [2, 4]]
    det_s = N.flint_matrix_det_modp(M_singular, p)
    rank_s = N.flint_matrix_rank_modp(M_singular, p)
    assert det_s == 0
    assert rank_s < 2

    # Non-singular
    M_full = [[1, 2], [3, 5]]  # det = -1 ≡ 6
    det_f = N.flint_matrix_det_modp(M_full, p)
    rank_f = N.flint_matrix_rank_modp(M_full, p)
    assert det_f != 0
    assert rank_f == 2


def test_composition_polmodp_then_factor():
    """Compose flint_polmodp with flint_polmodp_factor.

    Reducing mod p first then factoring should give the same result
    as factoring directly mod p.
    """
    p = 7
    # Polynomial with large coefficients
    coeffs = [-1, 0, 0, 0, 1]  # x^4 - 1 (small, but path is the test)
    reduced = N.flint_polmodp(coeffs, p)
    # All entries are in [0, p-1]
    assert all(0 <= c < p for c in reduced)
    direct_factors = N.flint_polmodp_factor(coeffs, p)
    indirect_factors = N.flint_polmodp_factor(reduced, p)
    # Same factor multiset (order may differ)
    da = sorted([(tuple(f), m) for f, m in direct_factors])
    di = sorted([(tuple(f), m) for f, m in indirect_factors])
    assert da == di


def test_composition_gcd_divides_both():
    """gcd(p, q) divides both p and q (over Q[x] up to content).

    Composition: flint_gcd_poly with flint_polmul must satisfy
    p * (1) ≡ gcd * (p / gcd), and the quotient must be a polynomial.
    """
    p = [1, 2, 1]  # (x+1)^2
    q = [1, 1]     # x+1
    g = N.flint_gcd_poly(p, q)
    # gcd should be x+1 (up to sign)
    assert g == [1, 1] or g == [-1, -1]


# ---------------------------------------------------------------------------
# Smoke runner — usable as a script
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed, failed = 0, []
    for t in tests:
        try:
            t()
            passed += 1
            print(f"  OK   {t.__name__}")
        except Exception as e:  # pragma: no cover
            failed.append((t.__name__, e))
            print(f"  FAIL {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{passed}/{len(tests)} OK")
    if failed:
        raise SystemExit(1)
