"""The height family's DOMAIN, tested as a family rather than one function at a time.

WHY THIS FILE EXISTS. `prometheus_math/polynomial_length.py`'s module docstring makes a load-
bearing claim: *"Its domain deliberately matches `mahler_measure`'s rather than being wider...
a screen whose domain exceeds the thing it screens will pass inputs the expensive step then
rejects, and the caller discovers the mismatch at the far end."*

Cycle 060 measured the family across the full non-finite input grid and the claim was FALSE:
on 6 of 9 non-finite inputs `mahler_measure` refused and `polynomial_length` returned a number.
The docstring described an intention; nothing tested it. These tests test it.

The four categories, per `.claude/skills/math-tdd`:
  authority    -- Mossinghoff's published M(Lehmer); the guard must not perturb it
  property     -- hypothesis: ANY sequence carrying a non-finite entry is refused by ALL of them
  edge         -- the full non-finite grid, str/bytes, complex-with-nan-part, numpy scalars
  composition  -- house <= M <= L requires all three to AGREE ON THEIR DOMAIN, which is the
                  actual subject of this file
"""
from __future__ import annotations

import math

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from techne.lib.coefficient_domain import (NonFiniteCoefficient,
                                           require_finite_coefficients)
from techne.lib.mahler_measure import (is_cyclotomic, log_mahler_measure,
                                       mahler_measure, mahler_measure_batch,
                                       mahler_measure_padded)
from prometheus_math.house import house
from prometheus_math.polynomial_length import polynomial_length

NAN, INF, NINF = float("nan"), float("inf"), float("-inf")

# Lehmer's polynomial, the family's standing authority case.
LEHMER = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
LEHMER_M = 1.1762808182599175          # Mossinghoff, "Lehmer's Problem", published table

#: Every scalar entry point in the height family. The point of the file is that this is a
#: FAMILY and its members must not disagree about where they are defined.
FAMILY = [
    ("mahler_measure", mahler_measure),
    ("log_mahler_measure", log_mahler_measure),
    ("is_cyclotomic", is_cyclotomic),
    ("polynomial_length", polynomial_length),
    ("house", house),
]

NON_FINITE_GRID = [
    [NAN], [INF], [NINF],
    [NAN, 1.0, -1.0], [INF, 1.0, -1.0], [NINF, 1.0, -1.0],
    [1.0, -1.0, NAN], [1.0, -1.0, INF], [1.0, -1.0, NINF],
    [1.0, NAN, -1.0],
    [1, 2, 3, NAN, 5],
]


# --------------------------------------------------------------------------------------
# 1. AUTHORITY
# --------------------------------------------------------------------------------------

def test_authority_lehmer_measure_unchanged_by_the_domain_guard():
    """M(Lehmer) is unchanged to 1e-12 after the guard is installed.

    Reference: Mossinghoff, M. J., "Lehmer's Problem" table of small Mahler measures --
    M = 1.1762808182599175 for x^10 + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1, the smallest
    known Mahler measure > 1. This is an EXTERNAL value, not a snapshot of our own output, so
    it adjudicates the fix independently of the code that implements it.

    A domain guard that changed a height would be a regression, not a guard; this is the test
    that says so.
    """
    assert abs(mahler_measure(LEHMER) - LEHMER_M) < 1e-12
    assert abs(math.exp(log_mahler_measure(LEHMER)) - LEHMER_M) < 1e-12
    assert not is_cyclotomic(LEHMER)                     # Kronecker: M > 1 => not cyclotomic
    # L = sum |a_i| = 9: the eleven coefficients of x^10 + x^9 - x^7 - x^6 - x^5 - x^4 - x^3
    # + x + 1 include TWO zeros (at x^8 and x^2), leaving nine terms of unit modulus.
    # This line asserted 8.0 when first written -- I counted the non-zero terms wrong, and the
    # test failed against correct code. Recorded rather than quietly fixed: it is a
    # false-block, the cost side the campaign is required to report, and the authority value
    # was the thing in error, not the implementation.
    assert polynomial_length(LEHMER) == 9.0
    assert abs(house(LEHMER) - LEHMER_M) < 1e-9          # Lehmer's poly is Salem: house = M


def test_authority_guard_is_transparent_on_the_known_small_cases():
    """Hand-computed values that do not depend on any implementation here.

    x - 2      : single root at 2, so M = 2, house = 2, L = 3
    x^2 - 1    : roots +-1, both ON the circle, so M = 1 (Kronecker: cyclotomic factors), L = 2
    constant 3 : M = L = 3 by convention; house REFUSES (no roots)
    """
    assert mahler_measure([1, -2]) == pytest.approx(2.0, abs=1e-12)
    assert house([1, -2]) == pytest.approx(2.0, abs=1e-9)
    assert polynomial_length([1, -2]) == 3.0
    assert mahler_measure([1, 0, -1]) == pytest.approx(1.0, abs=1e-9)
    assert polynomial_length([1, 0, -1]) == 2.0
    assert mahler_measure([3]) == 3.0
    assert polynomial_length([3]) == 3.0
    with pytest.raises(ValueError):
        house([3])


# --------------------------------------------------------------------------------------
# 2. PROPERTY (hypothesis)
# --------------------------------------------------------------------------------------

@settings(max_examples=200, deadline=None)
@given(finite=st.lists(st.integers(min_value=-4, max_value=4), min_size=0, max_size=6),
       bad=st.sampled_from([NAN, INF, NINF]),
       pos=st.integers(min_value=0, max_value=6))
def test_property_every_family_member_refuses_any_sequence_carrying_a_non_finite(
        finite, bad, pos):
    """INVARIANT: a sequence with >=1 non-finite entry is out of the family's domain, and
    EVERY member refuses it -- regardless of where in the sequence it sits.

    Position is randomised because the pre-guard behaviour was position-dependent: a leading
    inf produced `inf` from `mahler_measure` and `0.0` from `house`, while the same inf in a
    trailing slot produced a numpy ValueError from both. Position-dependent domains are how a
    family stops agreeing with itself.
    """
    coeffs = list(finite)
    coeffs.insert(min(pos, len(coeffs)), bad)
    for name, fn in FAMILY:
        with pytest.raises(NonFiniteCoefficient):
            fn(coeffs)


@settings(max_examples=200, deadline=None)
@given(st.lists(st.integers(min_value=-5, max_value=5), min_size=1, max_size=8))
def test_property_finite_integer_input_is_untouched_and_still_satisfies_M_ge_1(coeffs):
    """The guard must be INVISIBLE on the finite integer inputs the arsenal actually uses.

    Kronecker: a non-zero integer polynomial has M >= 1. If the guard had started rejecting
    legitimate input this fails immediately, which is the false-block cost this campaign is
    required to report beside the benefit.
    """
    if all(c == 0 for c in coeffs):
        with pytest.raises(ValueError):
            mahler_measure(coeffs)
        return
    m = mahler_measure(coeffs)
    assert math.isfinite(m)
    assert m >= 1.0 - 1e-9


@settings(max_examples=100, deadline=None)
@given(st.lists(st.integers(min_value=-3, max_value=3), min_size=2, max_size=6))
def test_property_guard_returns_the_same_coefficients_it_was_given(coeffs):
    """`require_finite_coefficients` is a GUARD, not a transform: it may refuse, never alter."""
    if all(c == 0 for c in coeffs):
        return
    assert require_finite_coefficients(coeffs, function="t") == list(coeffs)


# --------------------------------------------------------------------------------------
# 3. EDGE
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize("coeffs", NON_FINITE_GRID)
@pytest.mark.parametrize("name,fn", FAMILY)
def test_edge_full_non_finite_grid_is_refused_by_every_member(name, fn, coeffs):
    """The exact grid cycle 060 measured: {nan, +inf, -inf} x {deg 0, leading, trailing, mid}.

    Pre-guard tally over the 5x9 enumeration was RETURNS_NONFINITE 19 / RAISES 19 /
    RETURNS_BOOL 5 / RETURNS_FINITE 2. The two RETURNS_FINITE were `house([+-inf, 1, -1])
    -> 0.0`, a plausible in-range wrong answer meaning "all roots at the origin".
    """
    with pytest.raises(NonFiniteCoefficient):
        fn(list(coeffs))


def test_edge_complex_coefficient_with_a_non_finite_part_is_refused():
    """A complex coefficient is in-domain (input is cast to complex128 on entry), but one with
    a non-finite REAL or IMAGINARY part is not. `math.isfinite` cannot be called on a complex,
    so this is the case a naive guard silently lets through.
    """
    for bad in (complex(1.0, NAN), complex(NAN, 1.0), complex(1.0, INF), complex(INF, 0.0)):
        with pytest.raises(NonFiniteCoefficient):
            mahler_measure([bad, 1.0])
        with pytest.raises(NonFiniteCoefficient):
            polynomial_length([bad, 1.0])


def test_edge_numpy_scalar_non_finite_is_refused():
    """np.float64('nan') and np.complex128(nan) must be caught, not just Python floats.

    Batch callers hold numpy arrays; a guard that only understood Python builtins would be
    exactly the kind of partial control this campaign is measuring.
    """
    for bad in (np.float64(NAN), np.float64(INF), np.complex128(complex(NAN, 0))):
        with pytest.raises(NonFiniteCoefficient):
            mahler_measure([bad, 1.0])


def test_edge_string_input_is_a_type_error_not_a_silent_parse():
    """MEASURED, cycle 060: `mahler_measure(["1.0", "-2.0"])` returned **2.0** -- the CORRECT
    answer, from string input, because numpy parses numeric strings on cast. And
    `polynomial_length("123")` returned **6.0** by iterating the characters.

    That is the cycle-059 double-encoding fault (`json.dumps(json.dumps(...))` delivered every
    function a string) arriving at a function that CANNOT reveal it: it answers correctly. A
    guard that only checks finiteness would leave that hole open, so str/bytes is rejected by
    type, and a bare string is rejected as a coefficient SEQUENCE too.
    """
    for fn in (mahler_measure, polynomial_length, house, is_cyclotomic, log_mahler_measure):
        with pytest.raises(TypeError):
            fn(["1.0", "-2.0"])
        with pytest.raises(TypeError):
            fn("123")
        with pytest.raises(TypeError):
            fn(b"123")


def test_edge_zero_polynomial_still_refuses_with_its_own_reason():
    """The pre-existing zero-polynomial refusal is untouched, and keeps its OWN message.

    Two different out-of-domain reasons must stay distinguishable: "there is no polynomial
    here" and "this coefficient is not a number". Collapsing them would lose information the
    caller needs.
    """
    for fn in (mahler_measure, polynomial_length, house):
        with pytest.raises(ValueError, match="[Zz]ero polynomial"):
            fn([0, 0, 0])
    with pytest.raises(ValueError):
        mahler_measure([])


def test_edge_batch_reserves_nan_for_degenerate_rows_only():
    """THE SCALAR/BATCH CONTRACT, made checkable.

    `mahler_measure_padded` uses NaN in its OUTPUT as the in-band signal for an all-zero row.
    If non-finite INPUT were also allowed to produce NaN, one output symbol would mean two
    different things and no caller could tell "this row was degenerate" from "this row's
    coefficients were garbage". So the batch path refuses non-finite input at the front door
    and NaN-out keeps exactly one meaning.
    """
    out = mahler_measure_padded(np.array([[0.0, 0.0, 0.0], [0.0, 1.0, -2.0]]))
    assert math.isnan(out[0])                 # degenerate row -> NaN, unchanged
    assert out[1] == pytest.approx(2.0, abs=1e-9)
    with pytest.raises(NonFiniteCoefficient):
        mahler_measure_padded(np.array([[1.0, 0.0, NAN], [0.0, 1.0, -2.0]]))
    with pytest.raises(NonFiniteCoefficient):
        mahler_measure_batch([[1.0, -2.0], [1.0, INF]])


# --------------------------------------------------------------------------------------
# 4. COMPOSITION
# --------------------------------------------------------------------------------------

@settings(max_examples=150, deadline=None)
@given(st.lists(st.integers(min_value=-4, max_value=4), min_size=2, max_size=7))
def test_composition_height_chain_house_le_M_le_L(coeffs):
    """`house(f) <= M(f) <= L(f)` -- Everest & Ward ch.1 / Mahler (1960).

    A METAMORPHIC INVARIANT supplied by the domain, so it adjudicates the implementation
    without sharing its reasoning. It is stated for MONIC f; for a general integer f the right-
    hand half `M <= L` holds unconditionally (Mahler 1960) and is asserted always, while the
    left-hand half is asserted on the monic-in-absolute-value case where it is guaranteed.
    """
    while coeffs and coeffs[0] == 0:
        coeffs = coeffs[1:]
    if len(coeffs) < 2:
        return
    m, ell = mahler_measure(coeffs), polynomial_length(coeffs)
    assert m <= ell + 1e-9, f"M > L for {coeffs}: {m} > {ell}"
    if abs(coeffs[0]) == 1:
        assert house(coeffs) <= m + 1e-9, f"house > M for {coeffs}"


@pytest.mark.parametrize("coeffs", NON_FINITE_GRID)
def test_composition_the_family_agrees_on_its_domain(coeffs):
    """THE CLAIM `polynomial_length`'s DOCSTRING MAKES, FINALLY TESTED.

    "Its domain deliberately matches `mahler_measure`'s rather than being wider... a screen
    whose domain exceeds the thing it screens will pass inputs the expensive step then
    rejects." Measured pre-guard on this grid: `polynomial_length` returned a number on 9 of 9
    while `mahler_measure` refused on 6 of 9. The docstring stated an intention that the code
    did not implement.

    Rather than assert refusal member by member, this asserts AGREEMENT: whatever the family
    does with an input, it does uniformly. That is the property the screen actually needs.
    """
    verdicts = {}
    for name, fn in FAMILY:
        try:
            fn(list(coeffs))
            verdicts[name] = "accepts"
        except (ValueError, TypeError):
            verdicts[name] = "refuses"
    assert len(set(verdicts.values())) == 1, f"family disagrees on {coeffs}: {verdicts}"


@settings(max_examples=100, deadline=None)
@given(st.lists(st.integers(min_value=-3, max_value=3), min_size=2, max_size=5),
       st.lists(st.integers(min_value=-3, max_value=3), min_size=2, max_size=5))
def test_composition_mahler_multiplicativity_survives_the_guard(f, g):
    """`M(f*g) = M(f)*M(g)` -- multiplicativity, the strongest free oracle this domain has.

    Independent of the implementation: it is a theorem about the measure, so it fails
    differently from the code that computes it. It caught the repeated-root defect in cycle
    051 with zero inference, and it is here to certify that a domain guard did not disturb the
    mathematics it guards.
    """
    while f and f[0] == 0:
        f = f[1:]
    while g and g[0] == 0:
        g = g[1:]
    if len(f) < 2 or len(g) < 2:
        return
    prod = np.convolve(np.array(f, dtype=np.int64), np.array(g, dtype=np.int64)).tolist()
    lhs = mahler_measure(prod)
    rhs = mahler_measure(f) * mahler_measure(g)
    assert lhs == pytest.approx(rhs, rel=1e-7, abs=1e-9), f"M({f}*{g}) != M(f)M(g)"


@settings(max_examples=80, deadline=None)
@given(st.lists(st.integers(min_value=-2, max_value=2), min_size=3, max_size=7))
def test_composition_kronecker_M_equals_one_iff_cyclotomic(coeffs):
    """Kronecker: for a MONIC integer polynomial with non-zero constant term, M(f) = 1 iff
    every root is a root of unity, i.e. iff f is a product of cyclotomics.

    A second free oracle, and the one that keeps `mahler_measure` and `is_cyclotomic` from
    contradicting each other -- the failure cycle 051 fixed.
    """
    while coeffs and coeffs[0] == 0:
        coeffs = coeffs[1:]
    if len(coeffs) < 2 or abs(coeffs[0]) != 1 or coeffs[-1] == 0:
        return
    m = mahler_measure(coeffs)
    assert is_cyclotomic(coeffs) == (abs(m - 1.0) < 1e-8), (
        f"Kronecker violated for {coeffs}: M={m}, is_cyclotomic={is_cyclotomic(coeffs)}")
