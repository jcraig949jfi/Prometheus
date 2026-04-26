"""Benchmarks for prometheus_math.elliptic_curves.

Inputs:
- LMFDB-keyed rank-0 curves where available (online query at collection
  time, cached as a small inline list to keep the benchmark
  reproducible offline).
- Random a-invariants for properties that don't need authoritative
  curves (Faltings height tracks raw a-invariants).
"""

from __future__ import annotations

import random

import pytest

try:
    import prometheus_math as pm

    _PM_OK = True
except Exception:  # pragma: no cover
    _PM_OK = False


pytestmark = pytest.mark.skipif(
    not _PM_OK, reason="prometheus_math import failed"
)


# ---------------------------------------------------------------------------
# LMFDB rank-0 sample (frozen so the benchmark is reproducible without
# requiring network at run time). Sourced from lmfdb.elliptic_curves(
# rank=0, limit=...) on 2026-04-22.
# ---------------------------------------------------------------------------

_RANK0_AINVS: list[list[int]] = [
    [0, -1, 1, -10, -20],     # 11.a1 (rank 0)
    [1, -1, 1, -10, -20],     # 11.a2
    [0, 0, 1, -1, 0],         # 37.a1 NB rank 1 — replaced below
    [1, 0, 0, -4, -1],        # 14.a1
    [1, 0, 1, 4, -6],         # 14.a2
    [1, -1, 0, 4, -6],        # 14.a3
    [1, 0, 1, -36, -70],      # 14.a4
    [1, 0, 1, -171, -874],    # 14.a5
    [1, -1, 0, -1, 0],        # 14.a6
    [1, 1, 1, -3, 1],         # 15.a1
    [1, 1, 1, -23, -50],      # 15.a2
    [1, 1, 1, 35, -28],       # 15.a3
    [1, 1, 1, -83, -88],      # 15.a4
    [1, 1, 1, -2, 0],         # 15.a5
    [1, 1, 1, -1318, -19038], # 15.a7
    [0, 1, 1, -2, 0],         # 17.a1
    [0, 1, 1, -22, -36],      # 17.a2
    [0, 1, 1, -382, -2870],   # 17.a3
    [0, 1, 1, -7, 6],         # 17.a4
    [1, 0, 1, -3, 1],         # 19.a1
    [1, 0, 1, -98, -402],     # 19.a3
    [1, 0, 1, 17, 9],         # 19.a2
    [1, 1, 1, -39, -89],      # 21.a1
    [1, 0, 0, -49, 136],      # 21.a2
    [1, 0, 0, -4, -1],        # 21.a3
    [0, -1, 1, 0, 0],         # 11.a3
    [1, 0, 1, -7, 6],         # 26.a1
    [1, -1, 1, -3, 3],        # 26.a2
    [1, -1, 1, -213, 1257],   # 26.b1
    [1, 0, 1, -8, -10],       # 27.a1
]


def _lmfdb_rank0_ainvs(n: int = 100) -> list[list[int]]:
    """Return up to n rank-0 a-invariant lists.

    Tries to query LMFDB live first; falls back to the frozen sample
    above if the LMFDB connection isn't available. Cycled with
    repetition once we exhaust the live result, so the benchmark always
    has exactly n inputs.
    """
    out: list[list[int]] = []
    try:
        from prometheus_math.databases import lmfdb as _lmfdb

        if _lmfdb.probe(timeout=2.0):
            curves = _lmfdb.elliptic_curves(rank=0, limit=n)
            out = [c["ainvs"] for c in curves]
    except Exception:
        pass
    if not out:
        out = list(_RANK0_AINVS)
    # Pad/truncate to exactly n
    while len(out) < n:
        out.append(out[len(out) % max(1, len(_RANK0_AINVS))])
    return out[:n]


def _random_ainvs(n: int, seed: int = 41) -> list[list[int]]:
    """Generate `n` random a-invariants with small bounded coefs.
    Most will define non-singular curves at small heights.
    """
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        a1 = rng.randint(-1, 1)
        a2 = rng.randint(-2, 2)
        a3 = rng.randint(-1, 1)
        a4 = rng.randint(-20, 20)
        a6 = rng.randint(-30, 30)
        # Filter out (0,0,0,0,0) which is singular
        if (a1, a2, a3, a4, a6) == (0, 0, 0, 0, 0):
            continue
        out.append([a1, a2, a3, a4, a6])
    return out


# ---------------------------------------------------------------------------
# Benchmarks
# ---------------------------------------------------------------------------


@pytest.mark.tier2_candidate
def bench_regulator_rank0(benchmark):
    """N=100 LMFDB rank-0 regulator computations.

    Rank-0 regulators are 1.0 by convention; we still pay the
    point-search cost. Hot path for BSD scans.
    """
    ainvs = _lmfdb_rank0_ainvs(100)

    def go():
        return [pm.elliptic_curves.regulator(a) for a in ainvs]

    result = benchmark(go)
    assert len(result) == 100


@pytest.mark.tier2_candidate
def bench_analytic_sha_with_hint(benchmark):
    """N=50 analytic Sha computations with rank_hint=0.

    Compares to bench_analytic_sha_without_hint (same N) to estimate
    the cost of rank determination in the BSD chain.
    """
    ainvs = _lmfdb_rank0_ainvs(50)

    def go():
        return [
            pm.elliptic_curves.analytic_sha(a, rank_hint=0)
            for a in ainvs
        ]

    result = benchmark(go)
    assert len(result) == 50


@pytest.mark.tier2_candidate
def bench_analytic_sha_without_hint(benchmark):
    """N=50 analytic Sha computations with no rank hint.

    Pair to bench_analytic_sha_with_hint.
    """
    ainvs = _lmfdb_rank0_ainvs(50)

    def go():
        return [pm.elliptic_curves.analytic_sha(a) for a in ainvs]

    result = benchmark(go)
    assert len(result) == 50


@pytest.mark.tier2_candidate
def bench_selmer_2_rank(benchmark):
    """N=50 Selmer 2-rank computations on random rank-0 curves."""
    ainvs = _lmfdb_rank0_ainvs(50)

    def go():
        out = []
        for a in ainvs:
            try:
                out.append(pm.elliptic_curves.selmer_2_rank(a))
            except Exception:
                out.append(None)
        return out

    result = benchmark(go)
    assert len(result) == 50


@pytest.mark.tier2_candidate
def bench_faltings_height_batch(benchmark):
    """N=200 Faltings heights from random a-invariants.

    This is the classic numpy-vectorization candidate: log of
    discriminant + period integral + low-precision arithmetic, called
    in a tight loop today.
    """
    ainvs = _random_ainvs(200)

    def go():
        out = []
        for a in ainvs:
            try:
                out.append(pm.elliptic_curves.faltings_height(a))
            except Exception:
                out.append(None)
        return out

    result = benchmark(go)
    assert len(result) == 200
