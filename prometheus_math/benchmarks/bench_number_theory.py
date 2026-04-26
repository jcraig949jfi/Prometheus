"""Benchmarks for prometheus_math.number_theory hot-path operations.

Each `bench_*` function is a pytest-benchmark target. Inputs are sampled
deterministically (seeded) so the same researcher rerunning the suite
gets comparable wall-clock numbers.

Skipped automatically when an underlying backend is missing (e.g. PARI
not installed). Skipped under plain `pytest`; opt in with
`--run-benchmarks` or `pytest --benchmark-only`.
"""

from __future__ import annotations

import random

import pytest

try:
    import prometheus_math as pm

    _PM_OK = True
except Exception as exc:  # pragma: no cover
    _PM_OK = False
    _PM_ERR = exc


pytestmark = pytest.mark.skipif(
    not _PM_OK, reason="prometheus_math import failed"
)


# ---------------------------------------------------------------------------
# Random input generators (seeded)
# ---------------------------------------------------------------------------


def _imag_quadratic_polys(n: int, seed: int = 17) -> list[str]:
    """Generate `n` polynomials defining imaginary quadratic fields:
    x^2 + d for d in a fundamental-disc-friendly set.
    """
    rng = random.Random(seed)
    fund_d = [1, 2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21, 22, 23,
              26, 29, 30, 31, 33, 34, 35, 37, 38, 39, 41, 42, 43, 46, 47]
    polys = []
    for _ in range(n):
        d = rng.choice(fund_d)
        polys.append(f"x^2 + {d}")
    return polys


def _quartic_polys(n: int, seed: int = 19) -> list[str]:
    """Generate `n` random monic quartics with small integer coefs.
    Picks irreducibility-likely choices (constant term odd, etc.) but
    accepts that some will be reducible — that's part of realistic load.
    """
    rng = random.Random(seed)
    polys = []
    while len(polys) < n:
        a = rng.randint(-3, 3)
        b = rng.randint(-3, 3)
        c = rng.randint(-3, 3)
        d = rng.randint(1, 5) * rng.choice([-1, 1])
        # Drop x^4 + 0x^3 + 0x^2 + 0x + 1 (reducible) etc; mild filter
        if d == 0:
            continue
        polys.append(f"x^4 + {a}*x^3 + {b}*x^2 + {c}*x + {d}")
    return polys


def _deg10_polys(n: int, seed: int = 23) -> list[list[int]]:
    """Generate `n` integer polynomials of degree exactly 10.
    Coefficients in [-3, 3]; leading coef is nonzero.
    """
    rng = random.Random(seed)
    polys = []
    while len(polys) < n:
        coeffs = [rng.randint(-3, 3) for _ in range(11)]
        if coeffs[0] == 0:
            coeffs[0] = rng.choice([-1, 1])
        if coeffs[-1] == 0:
            coeffs[-1] = rng.choice([-1, 1])
        polys.append(coeffs)
    return polys


def _random_5x5_lattices(n: int, seed: int = 29) -> list[list[list[int]]]:
    """Generate `n` random 5x5 integer bases. Diagonal-dominant so we
    avoid degenerate (non-full-rank) matrices.
    """
    import numpy as np

    rng = np.random.default_rng(seed)
    bases = []
    for _ in range(n):
        B = rng.integers(low=-5, high=6, size=(5, 5))
        # Make diagonal-dominant for safety
        for i in range(5):
            B[i, i] = abs(B[i, i]) + 5
        bases.append(B.tolist())
    return bases


def _small_h_polys(n: int, seed: int = 31) -> list[str]:
    """Imaginary-quadratic polys with small (likely <= 10) class number."""
    rng = random.Random(seed)
    # All have h <= 10, hand-picked from Cohen Table 1.1
    h_le_10 = [1, 2, 3, 7, 11, 15, 19, 23, 43, 67, 163,  # h=1
               5, 6, 10, 13, 22, 35, 37, 51, 58, 91, 115,  # h=2
               14, 17, 21, 30, 33, 34, 39, 46, 55, 57]
    polys = []
    for _ in range(n):
        d = rng.choice(h_le_10)
        polys.append(f"x^2 + {d}")
    return polys


def _cm_discs(n: int, seed: int = 37) -> list[int]:
    """Random CM discriminants (negative integers, mod 4 \\in {0, 1})."""
    rng = random.Random(seed)
    discs = []
    base_pool = [-3, -4, -7, -8, -11, -15, -19, -20, -23, -24, -31,
                 -35, -39, -40, -43, -47, -51, -52, -55, -56, -67,
                 -68, -71, -79, -83, -84, -87, -88, -91, -95]
    for _ in range(n):
        discs.append(rng.choice(base_pool))
    return discs


# ---------------------------------------------------------------------------
# Benchmarks
# ---------------------------------------------------------------------------


@pytest.mark.tier2_candidate
def bench_class_number_quadratic(benchmark):
    """N=100 random imaginary-quadratic class numbers."""
    polys = _imag_quadratic_polys(100)

    def go():
        return [pm.number_theory.class_number(p) for p in polys]

    result = benchmark(go)
    assert len(result) == 100
    assert all(h >= 1 for h in result)


@pytest.mark.tier2_candidate
def bench_galois_group_quartic(benchmark):
    """N=50 random quartic Galois groups."""
    polys = _quartic_polys(50)

    def go():
        out = []
        for p in polys:
            try:
                out.append(pm.number_theory.galois_group(p))
            except Exception:
                out.append(None)
        return out

    result = benchmark(go)
    assert len(result) == 50


@pytest.mark.tier2_candidate
def bench_mahler_measure_deg10(benchmark):
    """N=200 random degree-10 Mahler measures.

    Suspected Tier-2 candidate: pure Python loop over numpy roots(),
    no batching across polynomials.
    """
    polys = _deg10_polys(200)

    def go():
        return [pm.number_theory.mahler_measure(c) for c in polys]

    result = benchmark(go)
    assert len(result) == 200
    assert all(m >= 1.0 - 1e-9 for m in result)


@pytest.mark.tier2_candidate
def bench_lll_5x5(benchmark):
    """N=100 random 5x5 LLL reductions."""
    bases = _random_5x5_lattices(100)

    def go():
        return [pm.number_theory.lll(B) for B in bases]

    result = benchmark(go)
    assert len(result) == 100


@pytest.mark.tier2_candidate
def bench_hilbert_class_field_h_le_10(benchmark):
    """N=20 imaginary-quadratic Hilbert class fields, h <= 10.

    This is the canonical slow operation in the NT module — degree-h
    relative extension, polredabs, then absolute polynomial. Anything
    we can do here pays off for many downstream callers.
    """
    polys = _small_h_polys(20)

    def go():
        return [pm.number_theory.hilbert_class_field(p) for p in polys]

    result = benchmark(go)
    assert len(result) == 20


@pytest.mark.tier2_candidate
def bench_cm_order_data(benchmark):
    """N=200 random CM-discriminant lookups."""
    discs = _cm_discs(200)

    def go():
        return [pm.number_theory.cm_order_data(D) for D in discs]

    result = benchmark(go)
    assert len(result) == 200
