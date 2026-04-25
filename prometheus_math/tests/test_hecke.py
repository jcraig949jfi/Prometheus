"""Tests for prometheus_math.hecke (project #28).

Test rubric (math-tdd skill, >= 2 in every category):

  Authority   : 11.2.a.a a_2 = -2 (LMFDB / PARI); Δ a_2/a_3/a_5 = -24/252/4830;
                cross_check_lmfdb 11.2.a.a p<=100 -> 0 disagreements;
                23.2.a.a a_2 power-basis coeffs match LMFDB.
  Property    : Ramanujan-Petersson |a_p| <= 2*sqrt(p) for weight-2 newform
                without CM (11.2.a.a, 37.2.a.a) at many primes;
                bad-prime bound |a_p| <= p when p | level;
                eigenvalues_table values match eigenvalue_at_prime;
                bulk_eigenvalues consistency.
  Edge        : non-prime p; malformed label; non-trivial char raises
                NotImplementedError; out-of-range letter; p_max < 2;
                bad newform letter chars; non-string label.
  Composition : eigenvalue_at_prime composes with eigenvalues_table;
                hecke_polynomial composes with eigenvalue_at_prime;
                bulk_eigenvalues composes with eigenvalue_at_prime;
                LMFDB authority + PARI compute roundtrip.
"""
from __future__ import annotations

import math

import pytest
from hypothesis import given, settings, strategies as st

# Import the module under test. If cypari is missing, skip the entire file.
try:
    from prometheus_math import hecke
except Exception as e:  # pragma: no cover
    pytest.skip(f"prometheus_math.hecke unavailable: {e}", allow_module_level=True)


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #


def _lmfdb_reachable() -> bool:
    try:
        from prometheus_math.databases import lmfdb as _lmfdb
        return _lmfdb.probe(timeout=3.0)
    except Exception:
        return False


requires_lmfdb = pytest.mark.skipif(
    not _lmfdb_reachable(), reason="LMFDB Postgres mirror unreachable"
)


# --------------------------------------------------------------------------- #
# 1. Authority tests                                                           #
# --------------------------------------------------------------------------- #


def test_authority_11_2_a_a_a2():
    """11.2.a.a Hecke eigenvalue at p=2.

    Reference: LMFDB mf_hecke_traces table, n=2, label '11.2.a.a':
    trace_an = -2. (Cross-checks against Cremona-table 11a's L-function
    coefficient sequence: 1, -2, -1, 2, 1, ...)
    """
    assert hecke.eigenvalue_at_prime("11.2.a.a", 2) == -2


def test_authority_delta_first_three_eigenvalues():
    """Ramanujan's tau function at p=2,3,5.

    Reference: Δ(τ) = sum tau(n) q^n is the unique normalised
    weight-12 cusp form of level 1 (label '1.12.a.a' in LMFDB).
    Standard tau values:
        tau(2) = -24, tau(3) = 252, tau(5) = 4830.
    See e.g. Serre "A Course in Arithmetic" VII.4, Table p.95, or
    OEIS A000594.
    """
    label = "1.12.a.a"
    assert hecke.eigenvalue_at_prime(label, 2) == -24
    assert hecke.eigenvalue_at_prime(label, 3) == 252
    assert hecke.eigenvalue_at_prime(label, 5) == 4830


@requires_lmfdb
def test_authority_cross_check_11_2_a_a_p_le_100():
    """cross_check_lmfdb on 11.2.a.a, p <= 100 reports 0 disagreements.

    Reference: every prime p <= 100 has an entry in LMFDB's
    mf_hecke_nf.ap (maxp=997 for 11.2.a.a). We expect ALL of them to
    agree exactly with PARI.
    """
    result = hecke.cross_check_lmfdb("11.2.a.a", p_max=100)
    # 25 primes <= 100
    assert result["n_primes"] == 25
    assert result["agreed"] == 25, f"unexpected disagreements: {result['disagreed']}"
    assert result["disagreed"] == []
    # All primes are within LMFDB's stored range, so missing should be empty.
    assert result["missing"] == []


@requires_lmfdb
def test_authority_23_2_a_a_dim2_power_basis():
    """23.2.a.a is dim=2 with Hecke field Q(y)/(y^2-y-1) (golden field).

    Reference: LMFDB mf_hecke_nf.ap[0] for 23.2.a.a is [0, -1] meaning
    a_2 = 0 + (-1)*y = -y where y is a root of y^2 - y - 1.

    PARI computes a_2 = Mod(-y, y^2 - y - 1); coefficients in ascending
    power basis are [0, -1].
    """
    coeffs = hecke.eigenvalue_at_prime("23.2.a.a", 2, prec="coeffs")
    assert coeffs == [0, -1]
    # And LMFDB lookup returns the same thing
    lmfdb_val = hecke.lmfdb_eigenvalue("23.2.a.a", 2)
    assert lmfdb_val == [0, -1]


# --------------------------------------------------------------------------- #
# 2. Property tests                                                            #
# --------------------------------------------------------------------------- #


def test_property_ramanujan_petersson_11_2_a_a():
    """Ramanujan-Petersson: |a_p| <= 2*sqrt(p) for weight-2 newform,
    NON-CM, p coprime to level. The label 11.2.a.a is non-CM, level=11.

    Tests across the first 20 primes coprime to 11. Bound is sharp
    in the limit (Sato-Tate distribution), so we apply it directly.
    """
    bad_primes = {11}  # level | level
    table = hecke.eigenvalues_table("11.2.a.a", p_max=80)
    checked = 0
    for p, a_p in table.items():
        if p in bad_primes:
            continue
        bound = 2.0 * math.sqrt(p)
        assert abs(a_p) <= bound + 1e-9, (
            f"Ramanujan-Petersson VIOLATED at p={p}: |a_p|={abs(a_p)} > 2*sqrt({p})={bound}"
        )
        checked += 1
    assert checked >= 15  # Sanity: we did test enough primes


def test_property_ramanujan_petersson_37_2_a_a():
    """Same RP test on 37.2.a.a (rank-1 EC newform, also non-CM)."""
    bad_primes = {37}
    table = hecke.eigenvalues_table("37.2.a.a", p_max=60)
    checked = 0
    for p, a_p in table.items():
        if p in bad_primes:
            continue
        bound = 2.0 * math.sqrt(p)
        assert abs(a_p) <= bound + 1e-9, (
            f"RP violated at p={p} for 37.2.a.a"
        )
        checked += 1
    assert checked >= 10


def test_property_bad_prime_bound_for_level_11():
    """For 11.2.a.a, p=11 is the unique bad prime (p | N).

    The bound at bad primes is |a_p| <= p (not 2*sqrt(p)).  In fact for
    the EC 11a, a_11 = 1 (split multiplicative reduction → a_p = +/-1).

    We assert the weaker bound |a_11| <= 11 to catch any sign-error or
    numeric blowup.
    """
    a_11 = hecke.eigenvalue_at_prime("11.2.a.a", 11)
    # Stronger fact for this curve:
    assert a_11 in (-1, 1), f"11a has multiplicative reduction; a_11 should be +/-1, got {a_11}"
    assert abs(a_11) <= 11


@settings(max_examples=10, deadline=None)
@given(st.sampled_from([2, 3, 5, 7, 13, 17, 19]))
def test_property_table_consistency_with_single(p):
    """For any prime p in the test sample, eigenvalues_table at primes=[p]
    equals eigenvalue_at_prime(label, p).

    This is a thin but powerful invariant: it catches table-construction
    bugs (off-by-one indexing, prime-list miscounts, coercion drift).
    """
    label = "11.2.a.a"
    single = hecke.eigenvalue_at_prime(label, p)
    table = hecke.eigenvalues_table(label, primes=[p])
    assert table[p] == single


def test_property_bulk_matches_individual():
    """bulk_eigenvalues over multiple labels at p_max=20 agrees with
    eigenvalue_at_prime called label-by-label, prime-by-prime."""
    labels = ["11.2.a.a", "37.2.a.a"]
    bulk = hecke.bulk_eigenvalues(labels, p_max=20)
    for lbl in labels:
        for p in [2, 3, 5, 7, 11, 13, 17, 19]:
            expected = hecke.eigenvalue_at_prime(lbl, p)
            assert bulk[lbl][p] == expected, (
                f"bulk vs single mismatch at {lbl} p={p}: "
                f"bulk={bulk[lbl][p]} single={expected}"
            )


# --------------------------------------------------------------------------- #
# 3. Edge-case tests                                                           #
# --------------------------------------------------------------------------- #


def test_edge_non_prime_p():
    """Non-prime p must raise ValueError.

    Edges covered: composite (4, 9, 15), unit (1), zero (0), negative (-2).
    """
    for bad_p in [4, 9, 15, 1, 0]:
        with pytest.raises(ValueError, match=r"not prime|>= ?[0-9]"):
            hecke.eigenvalue_at_prime("11.2.a.a", bad_p)
    # Negative: depending on sympy.isprime, could fail at isprime() check
    with pytest.raises(ValueError):
        hecke.eigenvalue_at_prime("11.2.a.a", -2)


def test_edge_malformed_label():
    """Malformed labels raise ValueError.

    Edges: empty, missing pieces, wrong types, extra dots, non-numeric level.
    """
    bad = ["", "11", "11.2", "11.2.a", "11.2.a.a.x", "11..a.a", "abc.2.a.a"]
    for label in bad:
        with pytest.raises(ValueError, match=r"malformed|empty|must be"):
            hecke.eigenvalue_at_prime(label, 2)


def test_edge_non_string_label():
    """label must be a string (not int, not None, not list)."""
    for bad in [123, None, ["11", "2", "a", "a"]]:
        with pytest.raises(ValueError, match=r"must be a string"):
            hecke.eigenvalue_at_prime(bad, 2)


def test_edge_non_trivial_char_raises():
    """char_orbit_index 'b', 'c', ... raises NotImplementedError.

    LMFDB labels with char_orbit != 'a' encode newforms on Gamma_1(N) /
    non-trivial nebentypus; PARI handles them but this module's API is
    Gamma_0-only for now and should fail loudly.
    """
    # Smallest non-trivial-char level/weight pair: weight-1 forms of conductor 23.
    # We don't actually need it to exist in PARI; the parser should reject.
    with pytest.raises(NotImplementedError, match=r"non-trivial character"):
        hecke.eigenvalue_at_prime("23.1.b.a", 2)


def test_edge_p_max_too_small():
    """p_max < 2 raises ValueError in eigenvalues_table and cross_check_lmfdb."""
    with pytest.raises(ValueError, match=r"p_max"):
        hecke.eigenvalues_table("11.2.a.a", p_max=1)
    with pytest.raises(ValueError, match=r"p_max"):
        hecke.cross_check_lmfdb("11.2.a.a", p_max=0)


def test_edge_letter_out_of_range():
    """A letter beyond the actual newform count raises ValueError.

    11.2.a has only one newform ('a'); '11.2.a.b' should fail.
    """
    with pytest.raises(ValueError, match=r"out of range|invalid"):
        hecke.eigenvalue_at_prime("11.2.a.b", 2)


def test_edge_lmfdb_eigenvalue_returns_none_for_unknown():
    """lmfdb_eigenvalue on a non-existent label returns None, not raise.

    This is the documented behaviour: "missing" entries are signalled
    via None so the caller can iterate over a label list without
    try/except.
    """
    # 999983.2.a.a is not in LMFDB (and 999983 is prime so the level is valid)
    # but the call should not raise — just return None.
    result = hecke.lmfdb_eigenvalue("999983.2.a.zzzz", 2)
    assert result is None


# --------------------------------------------------------------------------- #
# 4. Composition tests                                                         #
# --------------------------------------------------------------------------- #


def test_composition_table_equals_single_chain():
    """eigenvalues_table[p] == eigenvalue_at_prime(label, p) for every p
    in the table. This is the SPEC composition test from the task.
    """
    label = "11.2.a.a"
    table = hecke.eigenvalues_table(label, p_max=50)
    for p, a_p in table.items():
        assert hecke.eigenvalue_at_prime(label, p) == a_p


def test_composition_hecke_polynomial_via_eigenvalue():
    """hecke_polynomial(label, p) == [-eigenvalue_at_prime(label, p), 1].

    Composition: hecke_polynomial is implemented in terms of
    eigenvalue_at_prime; this asserts the two stay in lockstep.
    """
    for p in [2, 3, 5, 7, 13]:
        a_p = hecke.eigenvalue_at_prime("11.2.a.a", p)
        poly = hecke.hecke_polynomial("11.2.a.a", p)
        # T_p(x) = x - a_p, ascending-coeff [-a_p, 1]
        assert poly == [-a_p, 1]


def test_composition_bulk_then_single():
    """bulk_eigenvalues result lookup ≡ eigenvalue_at_prime called fresh
    AFTER cache eviction. This catches caching bugs that would let a stale
    eigenform leak between calls.
    """
    labels = ["11.2.a.a", "37.2.a.a"]
    bulk = hecke.bulk_eigenvalues(labels, p_max=15)
    hecke.clear_cache()
    for lbl in labels:
        for p, expected in bulk[lbl].items():
            actual = hecke.eigenvalue_at_prime(lbl, p)
            assert actual == expected, (
                f"post-cache-clear mismatch at {lbl} p={p}: "
                f"bulk_pre_clear={expected} fresh_post_clear={actual}"
            )


@requires_lmfdb
def test_composition_lmfdb_authority_chain():
    """For every prime p <= 50, lmfdb_eigenvalue == eigenvalue_at_prime
    on 11.2.a.a (dim=1) — independent code path through Postgres
    vs through PARI must agree.

    Composition: LMFDB DB layer + PARI compute layer both agree on
    the same mathematical object.
    """
    label = "11.2.a.a"
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        pari_val = hecke.eigenvalue_at_prime(label, p)
        lmfdb_val = hecke.lmfdb_eigenvalue(label, p)
        assert lmfdb_val is not None, f"LMFDB missing a_{p} for 11.2.a.a"
        assert pari_val == lmfdb_val, f"PARI vs LMFDB disagree at p={p}"


@requires_lmfdb
def test_composition_cross_check_delta():
    """cross_check_lmfdb on Δ (1.12.a.a) for primes <= 50 reports zero
    disagreements: PARI computation matches LMFDB's stored Ramanujan-tau
    values exactly across the full range.

    Composition: cross_check internally chains _select_form ↔
    eigenvalue_at_prime ↔ lmfdb_eigenvalue.
    """
    result = hecke.cross_check_lmfdb("1.12.a.a", p_max=50)
    assert result["n_primes"] == 15  # primes <= 50
    assert result["disagreed"] == []
    assert result["agreed"] == 15
