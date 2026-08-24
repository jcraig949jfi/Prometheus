"""The scalar and batch Mahler APIs must not disagree about the same polynomial.

**Why this file exists.** Cycle 051 routed exactly-repeated roots through an exact squarefree
decomposition in the SCALAR path. The batch path kept naive root-finding, so one module's two
public APIs returned different answers for one input:

    mahler_measure([1,2,-1,-4,-1,2,1])         = 1.0          exact
    mahler_measure_batch([[1,2,-1,-4,-1,2,1]]) = 1.000146...  the old defect

Sharper than a stale duplicate: `mahler_measure_batch(method='individual')` delegates to the
scalar function and is CORRECT, while `method='companion_batch'` is not — and `'auto'` picks
between them on a **degree-spread heuristic**. So which answer a caller gets depends on the
shape of the batch their polynomial happens to travel in.

Prereg: `techne/loop/rung_notes/CYCLE052_BATCH_DIVERGENCE_PREREG.md`.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from techne.lib.mahler_measure import (  # noqa: E402
    mahler_measure,
    mahler_measure_batch,
    mahler_measure_padded,
)

# (x+1)^4 (x-1)^2 -- all roots on the unit circle, so M = 1 EXACTLY by Kronecker.
KRONECKER_WITNESS = [1, 2, -1, -4, -1, 2, 1]
LEHMER = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
LEHMER_M = 1.1762808182599175


def _poly_mul(f, g):
    out = [0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        for j, b in enumerate(g):
            out[i + j] += a * b
    return out


# ------------------------------------------------------------------- 1. AUTHORITY

@pytest.mark.parametrize("method", ["auto", "companion_batch", "individual"])
def test_authority_kronecker_witness_is_exactly_one_under_every_method(method):
    """M((x+1)^4 (x-1)^2) = 1 EXACTLY, whichever batch strategy is chosen.

    Reference: Kronecker's theorem (Everest & Ward 1999, Ch.1) — a monic integer polynomial
    with all roots on the unit circle has M = 1. Here the roots are -1 (x4) and +1 (x2).

    Parametrised over the method because the defect is method-dependent: 'individual'
    delegates to the fixed scalar path and already passes, so a single-method test would
    have reported success while 'auto' still returned 1.000146 in production.
    """
    got = mahler_measure_batch([KRONECKER_WITNESS], method=method)
    assert float(got[0]) == pytest.approx(1.0, abs=1e-12)


def test_authority_padded_entry_point_is_also_exact():
    """`mahler_measure_padded` is the same companion stack exposed directly.

    Prediction 5 of the prereg: fixing `mahler_measure_batch` alone would leave this broken.
    Charon's Lehmer scan calls this entry point, so it is a real consumer surface, not an
    internal detail.
    """
    got = mahler_measure_padded(np.array([KRONECKER_WITNESS], dtype=float))
    assert float(got[0]) == pytest.approx(1.0, abs=1e-12)


def test_authority_lehmer_unchanged_in_batch():
    """M(Lehmer) = 1.1762808182599175 (Mossinghoff).

    The squarefree majority must keep the fast path AND its accuracy — a fix that perturbed
    ordinary Salem polynomials to buy the repeated-root case would be a bad trade.
    """
    got = mahler_measure_batch([LEHMER], method="companion_batch")
    assert float(got[0]) == pytest.approx(LEHMER_M, rel=1e-12)


# ------------------------------------------------------------------- 2. PROPERTY

@settings(max_examples=100, deadline=None)
@given(st.lists(
    st.lists(st.integers(min_value=-3, max_value=3), min_size=2, max_size=5),
    min_size=1, max_size=6))
def test_property_batch_equals_scalar_elementwise(polys):
    """Every batch method agrees with the scalar path, entry by entry.

    The invariant the module should always have had: batching is an implementation
    strategy, and a strategy must not change the answer.
    """
    assume(all(any(c != 0 for c in p) and p[0] != 0 for p in polys))
    expected = [mahler_measure(p) for p in polys]
    for method in ("auto", "companion_batch", "individual"):
        got = mahler_measure_batch(polys, method=method)
        for g, e in zip(got, expected):
            assert float(g) == pytest.approx(e, rel=1e-12), (method, polys)


@settings(max_examples=60, deadline=None)
@given(st.lists(st.integers(min_value=-3, max_value=3), min_size=2, max_size=4))
def test_property_squared_polynomials_agree_across_apis(coeffs):
    """f*f is non-squarefree BY CONSTRUCTION, so this targets the defect directly.

    A random sweep mostly draws squarefree polynomials and would exercise the repaired path
    only by luck; squaring guarantees every drawn case has a repeated root.
    """
    assume(any(c != 0 for c in coeffs) and coeffs[0] != 0)
    sq = _poly_mul(coeffs, coeffs)
    expected = mahler_measure(sq)
    got = mahler_measure_batch([sq], method="companion_batch")
    assert float(got[0]) == pytest.approx(expected, rel=1e-12)


# ------------------------------------------------------------------- 3. EDGE CASES

def test_edge_cases_of_the_batched_repeated_root_path():
    """Edges enumerated:

    - empty batch              -> empty array, no exception
    - all-zero row             -> NaN preserved (batch is forgiving where scalar raises)
    - mixed valid/degenerate   -> the NaN does not contaminate its neighbours
    - mixed squarefree/not     -> both are right IN THE SAME CALL, which is the case a
                                  per-batch (rather than per-entry) gate would get wrong
    - a single-entry batch     -> the degree-spread heuristic is degenerate at n=1
    - wide degree spread       -> forces method='auto' down the 'individual' branch
    """
    assert len(mahler_measure_batch([])) == 0

    got = mahler_measure_batch([[0, 0], KRONECKER_WITNESS])
    assert np.isnan(float(got[0]))
    assert float(got[1]) == pytest.approx(1.0, abs=1e-12)

    mixed = mahler_measure_batch([KRONECKER_WITNESS, LEHMER], method="companion_batch")
    assert float(mixed[0]) == pytest.approx(1.0, abs=1e-12)
    assert float(mixed[1]) == pytest.approx(LEHMER_M, rel=1e-12)

    assert float(mahler_measure_batch([KRONECKER_WITNESS])[0]) == pytest.approx(1.0, abs=1e-12)

    wide = mahler_measure_batch([KRONECKER_WITNESS, [1, -2]] * 40, method="auto")
    assert float(wide[0]) == pytest.approx(1.0, abs=1e-12)


# ------------------------------------------------------------------- 4. COMPOSITION

def test_composition_multiplicativity_holds_in_batch():
    """M(fg) = M(f)M(g) computed entirely through the batch API.

    f = (x-2)(x-3), g = (x-2)(x-5): the product has a double root at 2 even though neither
    factor is itself non-squarefree. Hand-verified M(f) = 6, M(g) = 10, M(fg) = 60.
    """
    f = _poly_mul([1, -2], [1, -3])
    g = _poly_mul([1, -2], [1, -5])
    got = mahler_measure_batch([f, g, _poly_mul(f, g)], method="companion_batch")
    assert float(got[0]) == pytest.approx(6.0, rel=1e-9)
    assert float(got[1]) == pytest.approx(10.0, rel=1e-9)
    assert float(got[2]) == pytest.approx(60.0, rel=1e-9)
    assert float(got[2]) == pytest.approx(float(got[0]) * float(got[1]), rel=1e-9)


def test_composition_batch_agrees_with_padded_on_the_same_input():
    """The two batch entry points must not disagree with each other either.

    `mahler_measure_batch` and `mahler_measure_padded` are separate public surfaces over one
    companion stack. Cycle 051's lesson: after a numerical fix, ask which OTHER functions
    read the same quantity and whether they now disagree.
    """
    polys = [KRONECKER_WITNESS, LEHMER, _poly_mul([1, -2], [1, -2])]
    width = max(len(p) for p in polys)
    padded = np.array([[0] * (width - len(p)) + list(p) for p in polys], dtype=float)

    a = mahler_measure_batch(polys, method="companion_batch")
    b = mahler_measure_padded(padded)
    for x, y in zip(a, b):
        assert float(x) == pytest.approx(float(y), rel=1e-12)
