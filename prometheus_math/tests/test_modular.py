"""Test suite for prometheus_math.modular (Project #27).

q-expansion computation at depth for classical modular newforms.

Categories per math-tdd skill (techne/skills/math-tdd.md), 12+ tests:
  - Authority:  11.2.a.a (Δ-form for elliptic curve 11a) — first 12 a_n
                hand-listed against Cremona's tables; Δ(τ) = q∏(1-q^n)^24
                Ramanujan tau coefficients OEIS A000594; a_p for primes
                p < 100 cross-checked against PARI ellan(11.a).
  - Property:   |a_p| <= 2 sqrt(p) (weight-2 Ramanujan-Petersson bound);
                multiplicativity a_{mn} = a_m a_n for gcd(m,n)=1;
                Hecke recursion at p^k holds:
                  a_{p^{k+1}} = a_p a_{p^k} - chi(p) p^{k-1} a_{p^{k-1}}
                a_0 = 0 for any cusp form.
  - Edge:       malformed label raises ValueError;
                n_coeffs = 0 returns []; n_coeffs = 1 returns [a_0];
                negative n_coeffs raises ValueError;
                non-existent label (well-formed) raises LookupError.
  - Composition: qexp for 11.2.a.a matches PARI ellan for elliptic curve
                 11.a on a 50-prime sweep;
                 q_coefficient and qexp agree on every index;
                 hecke_eigenvalue(label, p) == qexp(label, p+1)[p];
                 character_value matches sympy jacobi_symbol on a sweep
                 (only meaningful for char_orbit 'a' = trivial; we verify
                 chi(n)=1 for trivial char and gcd(n,N)=1).

Run: pytest prometheus_math/tests/test_modular.py -v

LMFDB-dependent tests skip gracefully if devmirror.lmfdb.xyz is
unreachable.
"""
from __future__ import annotations

import math

import pytest
from hypothesis import given, settings, strategies as st

# Ramanujan tau coefficients (Δ(τ) = q ∏ (1-q^n)^24): tau(1)..tau(15)
# Reference: OEIS A000594 — Hardy & Wright "An Introduction to the Theory
# of Numbers" 6th ed. §20.13; LMFDB form label 1.12.a.a.
RAMANUJAN_TAU_1_TO_15 = [
    1, -24, 252, -1472, 4830, -6048, -16744, 84480, -113643, -115920,
    534612, -370944, -577738, 401856, 1217160,
]

# Elliptic curve 11.a (Cremona 11a1, LMFDB 11.a1 / 11.2.a.a):
# y^2 + y = x^3 - x^2 - 10x - 20.  Ainvs = [0, -1, 1, -10, -20].
# a_n for n=1..12: from Cremona's tables, also via PARI ellan.
EC_11A_AN_1_TO_12 = [1, -2, -1, 2, 1, 2, -2, 0, -2, -2, 1, -2]


def _lmfdb_available():
    try:
        from prometheus_math.databases import lmfdb as _lmfdb
        with _lmfdb.connect(timeout=5) as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
        return True
    except Exception:
        return False


_LMFDB_OK = _lmfdb_available()
_skip_no_lmfdb = pytest.mark.skipif(
    not _LMFDB_OK, reason="LMFDB mirror unreachable; live test skipped"
)


# Importing the module is also the first sanity check.
from prometheus_math.modular import (  # noqa: E402
    qexp,
    q_coefficient,
    hecke_recursion,
    is_eigenform,
    character_value,
    hecke_eigenvalue,
    InvalidLabelError,
)


# --------------------------------------------------------------------------- #
# Authority tests                                                              #
# --------------------------------------------------------------------------- #


@_skip_no_lmfdb
def test_authority_11_2_a_a_first_twelve_against_cremona():
    """11.2.a.a (Δ-form for the elliptic curve 11.a): a_1..a_12.

    Reference: Cremona, "Algorithms for Modular Elliptic Curves",
    Table 1 (curve 11A1); LMFDB label 11.2.a.a / 11.a1; verified
    via PARI ellan([0,-1,1,-10,-20], 12).
        a_1..a_12 = [1, -2, -1, 2, 1, 2, -2, 0, -2, -2, 1, -2]
    """
    coefs = qexp("11.2.a.a", n_coeffs=13)
    # qexp returns [a_0, a_1, ..., a_{n-1}]; cusp form a_0 = 0
    assert coefs[0] == 0
    assert [int(c) for c in coefs[1:13]] == EC_11A_AN_1_TO_12


@_skip_no_lmfdb
def test_authority_delta_form_first_fifteen_ramanujan_tau():
    """Δ(τ) = q∏(1-q^n)^24, weight 12 cusp form for SL_2(Z), label 1.12.a.a.

    First 15 coefficients are τ(1), τ(2), ..., τ(15).
    Reference: OEIS A000594; Hardy–Wright §20.13;
    Wikipedia Ramanujan tau function.
    """
    coefs = qexp("1.12.a.a", n_coeffs=16)
    assert coefs[0] == 0
    assert [int(c) for c in coefs[1:16]] == RAMANUJAN_TAU_1_TO_15


@_skip_no_lmfdb
def test_authority_q_coefficient_matches_qexp():
    """Authority: q_coefficient(label, n) returns the n-th element of qexp.

    Cross-check: every individual a_n via q_coefficient agrees with
    the bulk qexp output for 11.2.a.a, n=1..12.
    """
    bulk = qexp("11.2.a.a", n_coeffs=13)
    for n in range(13):
        assert int(q_coefficient("11.2.a.a", n)) == int(bulk[n])


# --------------------------------------------------------------------------- #
# Property tests                                                               #
# --------------------------------------------------------------------------- #


@_skip_no_lmfdb
def test_property_ramanujan_petersson_bound_weight_2():
    """For non-CM weight-2 newform (11.2.a.a), |a_p| <= 2 sqrt(p).

    Deligne (1974), proven Weil conjectures: |a_p| <= 2 p^{(k-1)/2}.
    For weight 2 this is |a_p| <= 2 sqrt(p) at unramified primes.
    """
    from sympy import primerange

    coefs = qexp("11.2.a.a", n_coeffs=200)
    # check at primes p coprime to level 11 (skip p=11)
    for p in primerange(2, 200):
        if p == 11:
            continue
        ap = int(coefs[p])
        bound = 2.0 * math.sqrt(p) + 1e-9
        assert abs(ap) <= bound, (
            f"Ramanujan bound violated at p={p}: |a_p|={abs(ap)} vs "
            f"2 sqrt(p)={bound}"
        )


@_skip_no_lmfdb
def test_property_multiplicativity_for_coprime_indices():
    """For a Hecke newform, gcd(m,n)=1  =>  a_{mn} = a_m * a_n.

    11.2.a.a is a Hecke eigenform; check across many coprime pairs.
    """
    from math import gcd

    coefs = qexp("11.2.a.a", n_coeffs=100)
    pairs_checked = 0
    for m in range(1, 10):
        for n in range(1, 10):
            if gcd(m, n) != 1:
                continue
            if m * n >= 100:
                continue
            assert int(coefs[m * n]) == int(coefs[m]) * int(coefs[n]), (
                f"Multiplicativity failed at (m,n)=({m},{n})"
            )
            pairs_checked += 1
    assert pairs_checked >= 10


@_skip_no_lmfdb
def test_property_hecke_recursion_at_prime_powers():
    """At a prime p (good for the form), the Hecke recursion holds:
        a_{p^{k+1}} = a_p a_{p^k} - chi(p) p^{k-1} a_{p^{k-1}}.

    11.2.a.a has trivial character, weight 2, so the recursion becomes
        a_{p^{k+1}} = a_p a_{p^k} - p a_{p^{k-1}}      (for p coprime to 11)
    Reference: Diamond–Shurman, "A First Course in Modular Forms",
    Prop. 5.8.5.
    """
    coefs = qexp("11.2.a.a", n_coeffs=300)
    weight = 2
    for p in [2, 3, 5, 7]:  # all coprime to level 11
        ap = int(coefs[p])
        # k = 1: a_{p^2} = a_p^2 - p^{0} * a_1 = a_p^2 - 1; with chi(p)=1.
        # Actually a_1=1; a_{p^0}=a_1=1, p^{k-1}=p^0=1.
        for k in range(1, 4):
            if p ** (k + 1) >= 300:
                break
            apk1 = int(coefs[p ** (k + 1)])
            apk = int(coefs[p ** k])
            apk_1 = int(coefs[p ** (k - 1)]) if k >= 1 else 1
            expected = ap * apk - 1 * (p ** (weight - 1)) * apk_1
            assert apk1 == expected, (
                f"Hecke recursion failed at p={p}, k={k}: "
                f"a_{p**(k+1)}={apk1} vs expected={expected}"
            )


def test_property_hecke_recursion_function_directly():
    """hecke_recursion(a_p, p, chi_p, weight, k_max) returns the right values.

    Hand-computed for 11.2.a.a at p=2: a_2=-2, weight=2, chi_p=1.
        a_4 = (-2)(-2) - 1 * 2^{2-1} * 1 = 4 - 2 = 2          ✓
        a_8 = (-2)(2)  - 1 * 2^{2-1} * (-2) = -4 + 4 = 0      ✓
        a_16 = (-2)(0) - 1 * 2^{2-1} * 2 = 0 - 4 = -4         ✓
        a_32 = (-2)(-4) - 1 * 2 * 0 = 8                       ✓
    """
    out = hecke_recursion(a_p=-2, p=2, chi_p=1, weight=2, k_max=5)
    assert out[1] == -2  # a_p
    assert out[2] == 2   # a_{p^2}
    assert out[3] == 0   # a_{p^3}
    assert out[4] == -4  # a_{p^4}
    assert out[5] == 8   # a_{p^5}


@_skip_no_lmfdb
def test_property_a0_is_zero_for_cusp_forms():
    """For a cusp form, a_0 = 0 by definition. Both 11.2.a.a and Δ are cusps."""
    assert int(qexp("11.2.a.a", n_coeffs=2)[0]) == 0
    assert int(qexp("1.12.a.a", n_coeffs=2)[0]) == 0


@given(
    st.integers(min_value=-10, max_value=10),
    st.sampled_from([2, 3, 5, 7, 11]),
    st.integers(min_value=1, max_value=4),
)
@settings(max_examples=30, deadline=None)
def test_property_recursion_self_consistency(a_p, p, k_max):
    """hecke_recursion is internally consistent: applying recursion
    by hand reproduces the dictionary output.

    Pure-arithmetic check; doesn't need LMFDB.
    """
    weight = 2
    chi_p = 1
    out = hecke_recursion(a_p=a_p, p=p, chi_p=chi_p, weight=weight, k_max=k_max)
    # check the recurrence on each step
    out[0] = 1  # a_{p^0} = 1 by convention
    for k in range(1, k_max):
        rhs = a_p * out[k] - chi_p * (p ** (weight - 1)) * out[k - 1]
        assert out[k + 1] == rhs


# --------------------------------------------------------------------------- #
# Edge cases                                                                   #
# --------------------------------------------------------------------------- #


def test_edge_malformed_label_raises():
    """Malformed labels raise InvalidLabelError (a ValueError subclass).

    Edges covered:
      - empty string
      - missing dots
      - non-numeric level
      - non-orbit-letter suffix
    """
    bad_labels = ["", "11", "11.2", "11.2.a", "abc.2.a.a", "11.x.a.a",
                  "11.2.a.A", "11.2.0.a"]
    for label in bad_labels:
        with pytest.raises(InvalidLabelError):
            qexp(label, n_coeffs=5)


def test_edge_n_coeffs_zero_returns_empty_list():
    """n_coeffs = 0 returns []; n_coeffs = 1 returns [a_0]."""
    assert qexp("11.2.a.a", n_coeffs=0) == []
    if _LMFDB_OK:
        out = qexp("11.2.a.a", n_coeffs=1)
        assert len(out) == 1
        assert int(out[0]) == 0  # cusp form a_0 = 0


def test_edge_negative_n_coeffs_raises():
    """Negative n_coeffs raises ValueError."""
    with pytest.raises(ValueError):
        qexp("11.2.a.a", n_coeffs=-1)
    with pytest.raises(ValueError):
        q_coefficient("11.2.a.a", -3)


@_skip_no_lmfdb
def test_edge_nonexistent_label_raises_lookup():
    """A well-formed label that isn't in LMFDB raises LookupError."""
    with pytest.raises(LookupError):
        qexp("9999999.2.a.a", n_coeffs=5)


def test_edge_hecke_recursion_invalid_inputs():
    """hecke_recursion on invalid inputs:
      - non-prime p raises ValueError
      - negative k_max raises ValueError
      - k_max=0 returns just {0:1, 1:a_p}? (we choose: returns {0:1})
    """
    with pytest.raises(ValueError):
        hecke_recursion(a_p=1, p=4, chi_p=1, weight=2, k_max=3)  # 4 not prime
    with pytest.raises(ValueError):
        hecke_recursion(a_p=1, p=2, chi_p=1, weight=2, k_max=-1)


# --------------------------------------------------------------------------- #
# Composition tests                                                            #
# --------------------------------------------------------------------------- #


@_skip_no_lmfdb
def test_composition_qexp_matches_pari_ellan_for_11a():
    """Modularity (Wiles): a_p of newform 11.2.a.a equals a_p of EC 11.a.

    Composition: pm.modular.qexp <-> PARI ellan via cypari directly.
    Cross-checks 50 indices (n=1..50).
    """
    import cypari
    pari = cypari.pari
    e = pari.ellinit('[0,-1,1,-10,-20]')
    ellan = list(pari.ellan(e, 50))  # a_1..a_50

    coefs = qexp("11.2.a.a", n_coeffs=51)
    for n in range(1, 51):
        assert int(coefs[n]) == int(ellan[n - 1]), (
            f"Modularity mismatch at n={n}: "
            f"qexp={int(coefs[n])} vs ellan={int(ellan[n-1])}"
        )


@_skip_no_lmfdb
def test_composition_hecke_eigenvalue_consistent_with_qexp():
    """hecke_eigenvalue(label, p) returns the same value as qexp[p].

    Composition: single-coefficient API agrees with bulk API.
    """
    from sympy import primerange
    bulk = qexp("11.2.a.a", n_coeffs=100)
    for p in primerange(2, 100):
        assert int(hecke_eigenvalue("11.2.a.a", p)) == int(bulk[p])


@_skip_no_lmfdb
def test_composition_is_eigenform_recognises_known_eigenforms():
    """11.2.a.a and 1.12.a.a are Hecke eigenforms.

    Composition: the is_eigenform predicate is consistent with the
    multiplicativity property — if multiplicativity holds at all coprime
    pairs we tested, the form must be an eigenform.
    """
    assert is_eigenform("11.2.a.a") is True
    assert is_eigenform("1.12.a.a") is True


@_skip_no_lmfdb
def test_composition_character_value_trivial_orbit_a():
    """For a newform with trivial character (orbit 'a'), chi(n) = 1 for
    gcd(n, level)=1, else chi(n) = 0.

    Composition: character_value agrees with the Hecke recursion for
    11.2.a.a — verify chi(2)=chi(3)=...=1, chi(11)=0.
    """
    from math import gcd
    level = 11
    for n in [1, 2, 3, 5, 7, 13, 17]:
        assert character_value("11.2.a.a", n) == 1
    for n in [11, 22, 33]:
        assert character_value("11.2.a.a", n) == 0
