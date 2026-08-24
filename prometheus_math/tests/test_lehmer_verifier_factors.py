"""The Lehmer band verifier must factor before certifying.

**Why this file exists.** `lehmer_brute_force.mpmath_recheck` escalates precision three
times (dps 15/30/60, extraprec 50/100/200, maxsteps 300/600/1000) and **never factors**. On a
polynomial with a repeated root ON the unit circle, `mpmath.polyroots` fails to converge at any
of those settings and the function returns NaN.

Those NaNs set `verification_failed=True` on 17 deg-14 band entries and drive the run's
published **INCONCLUSIVE** verdict, written up as *"without high-precision certification we
cannot decide H5 vs H2 cleanly."*

Measured, cycle 052: `Lehmer x (x+1)^2` -> ladder returns `nan`, squarefree factoring returns
`1.1762808182599176` exactly. Measured, cycle 053: **all 17 entries carry a repeated root**,
with factor multiplicities up to 6 — the mechanism explains the whole category.

**More precision does not resolve a clustered repeated root. Factoring does.** That is a
mechanism, not an observation (cycle 052's rule).

Prereg: `techne/loop/rung_notes/CYCLE053_LEHMER_VERIFIER_PREREG.md`.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.lehmer_brute_force import (  # noqa: E402
    build_palindrome_descending,
    mpmath_recheck,
    mpmath_recheck_descending,
)

LEHMER_M = 1.1762808182599175
PATH_B_RESULTS = (pathlib.Path(__file__).resolve().parents[1]
                  / "_lehmer_brute_force_path_b_results.json")


def _poly_mul(f, g):
    out = [0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        for j, b in enumerate(g):
            out[i + j] += a * b
    return out


def _load_path_b():
    if not PATH_B_RESULTS.exists():                              # pragma: no cover
        pytest.skip("path B results snapshot unavailable")
    return json.loads(PATH_B_RESULTS.read_text(encoding="utf-8"))["results"]


# ----------------------------------------------------------------- 1. AUTHORITY

def test_authority_the_17_stored_entries_all_verify_finitely():
    """Every one of the 17 `verification_failed` entries returns a finite measure.

    Reference: `_lehmer_brute_force_path_b_results.json`, the stored snapshot of the deg-14
    band run. These are the exact polynomials whose NaNs produced the INCONCLUSIVE verdict.

    This is the whole population, enumerated — not a sample. There are 17 of them.
    """
    entries = _load_path_b()
    assert len(entries) == 17, "the stored population changed; re-read before trusting this"

    failures = []
    for e in entries:
        half = e["source_entry"]["half_coeffs"]
        m = mpmath_recheck(half, dps=30)
        if not math.isfinite(m):
            failures.append((half, m))
    assert not failures, f"{len(failures)} of 17 still return NaN: {failures[:3]}"


def test_authority_lehmer_times_a_squared_cyclotomic_is_lehmers_measure():
    """M(Lehmer x (x+1)^2) = M(Lehmer) = 1.1762808182599175.

    Reference: Mossinghoff's table gives M(Lehmer) = 1.176280818..., the smallest known
    measure exceeding 1; multiplicativity (Everest & Ward 1999, Lemma 1.6) plus M(x+1) = 1
    fixes the product. This is cycle 052's witness, which the escalation ladder returned NaN
    for at every precision it tries.

    Uses the general entry point rather than the deg-14 palindrome builder because the
    witness is degree 12.
    """
    lehmer = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    witness = _poly_mul(_poly_mul(lehmer, [1, 1]), [1, 1])
    assert mpmath_recheck_descending(witness, dps=30) == pytest.approx(LEHMER_M, rel=1e-9)


# ----------------------------------------------------------------- 2. PROPERTY

@pytest.mark.parametrize("k", [1, 2, 3, 4])
def test_property_repeated_cyclotomic_factors_never_change_the_measure(k):
    """M(f * Phi^k) = M(f) for any cyclotomic Phi and any multiplicity k.

    M is multiplicative and every cyclotomic polynomial has M = 1, so raising a cyclotomic
    factor's multiplicity changes the polynomial and not its measure — while making the root
    cluster arbitrarily worse for a root-finder. This is the exact structure of all 17.
    """
    lehmer = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    p = lehmer
    for _ in range(k):
        p = _poly_mul(p, [1, 1])
    assert mpmath_recheck_descending(p, dps=30) == pytest.approx(LEHMER_M, rel=1e-9)


def test_property_squarefree_input_is_unchanged_by_the_fix():
    """Lehmer itself is a Salem polynomial with simple roots: the fix must be a no-op.

    A correctness fix that perturbed well-conditioned input to buy the repeated-root case
    would be a bad trade, and this is the guard against it.
    """
    lehmer = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    assert mpmath_recheck_descending(lehmer, dps=30) == pytest.approx(LEHMER_M, rel=1e-12)


# ----------------------------------------------------------------- 3. EDGE CASES

def test_edge_cases_of_the_factoring_verifier():
    """Edges enumerated:

    - all-cyclotomic product      -> exactly 1.0 (Kronecker), the B1 class's shape
    - a pure high power (x-1)^14  -> exactly 1.0; every root on the circle, multiplicity 14
    - degree-0 / degenerate input -> NaN preserved, the documented sentinel
    - a genuinely non-convergent  -> still NaN rather than a fabricated number
    - large multiplicity          -> (x-2)^12, M = 4096, roots OFF the circle
    """
    cyclo = _poly_mul(_poly_mul([1, 1], [1, 1]), _poly_mul([1, -1], [1, -1]))
    assert mpmath_recheck_descending(cyclo, dps=30) == pytest.approx(1.0, abs=1e-12)

    p = [1]
    for _ in range(14):
        p = _poly_mul(p, [1, -1])
    assert mpmath_recheck_descending(p, dps=30) == pytest.approx(1.0, abs=1e-12)

    assert math.isnan(mpmath_recheck_descending([], dps=30))
    assert math.isnan(mpmath_recheck_descending([0, 0], dps=30))

    q = [1]
    for _ in range(12):
        q = _poly_mul(q, [1, -2])
    assert mpmath_recheck_descending(q, dps=30) == pytest.approx(4096.0, rel=1e-9)


# ----------------------------------------------------------------- 4. COMPOSITION

def test_composition_verifier_agrees_with_path_b_on_all_17():
    """THE KILL TEST. Two independent routes to the same quantity must agree.

    Path B reached its published `H5_CONFIRMED` by symbolic `factor_list` over Z[x] followed
    by a cyclotomic-aware product. The fixed verifier reaches its answer by squarefree
    decomposition then high-precision root-finding per factor. Agreement on all 17 is a real
    cross-check; a disagreement means either this fix is wrong or the published verdict is,
    and neither may pass silently.
    """
    entries = _load_path_b()
    disagreements = []
    for e in entries:
        half = e["source_entry"]["half_coeffs"]
        got = mpmath_recheck(half, dps=30)
        expected = float(e["M_non_cyclotomic_product"])
        if not (math.isfinite(got) and abs(got - expected) <= 1e-9 * max(1.0, abs(expected))):
            disagreements.append((half, got, expected))
    assert not disagreements, (
        f"{len(disagreements)} of 17 disagree with Path B: {disagreements[:3]}")


def test_composition_agrees_with_the_scalar_arsenal_measure():
    """The verifier and `techne.lib.mahler_measure` must not disagree about the same input.

    Cycle 051's lesson, applied across module boundaries: after a numerical fix, ask which
    OTHER functions read the same quantity. Both now factor first, by different routes
    (mpmath per factor vs numpy per factor), so agreement is a check and not a tautology.
    """
    from techne.lib.mahler_measure import mahler_measure
    entries = _load_path_b()
    for e in entries[:6]:
        desc = list(reversed(e["coeffs_ascending"]))
        assert mpmath_recheck_descending(desc, dps=30) == pytest.approx(
            mahler_measure(desc), rel=1e-9)
