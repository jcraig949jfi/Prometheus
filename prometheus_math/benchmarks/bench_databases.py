"""Benchmarks for prometheus_math.databases lookup operations.

These are designed to measure local-mirror lookup paths (OEIS local,
LMFDB Postgres, KnotInfo cached). Network paths are NOT benchmarked
here — those are dominated by external latency, not our code.
"""

from __future__ import annotations

import random

import pytest

try:
    import prometheus_math as pm  # noqa: F401

    _PM_OK = True
except Exception:  # pragma: no cover
    _PM_OK = False


pytestmark = pytest.mark.skipif(
    not _PM_OK, reason="prometheus_math import failed"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _random_a_numbers(n: int, seed: int = 43) -> list[str]:
    """Generate `n` random A-numbers in [A000001, A350000]. Some will
    miss the mirror; that's part of realistic load.
    """
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        idx = rng.randint(1, 350_000)
        out.append(f"A{idx:06d}")
    return out


def _ec_labels_from_lmfdb(n: int) -> list[str]:
    """Return up to `n` real LMFDB EC labels (rank=0).

    Falls back to a small frozen list if LMFDB is unreachable.
    """
    try:
        from prometheus_math.databases import lmfdb as _lmfdb

        if _lmfdb.probe(timeout=2.0):
            curves = _lmfdb.elliptic_curves(rank=0, limit=n)
            return [c["lmfdb_label"] for c in curves]
    except Exception:
        pass
    fallback = [
        "11.a1", "11.a2", "11.a3", "14.a1", "14.a2",
        "14.a3", "15.a1", "15.a2", "17.a1", "17.a2",
        "19.a1", "19.a2", "21.a1", "26.a1", "26.b1",
        "27.a1", "32.a1", "33.a1", "34.a1", "35.a1",
    ]
    return (fallback * ((n // len(fallback)) + 1))[:n]


def _knot_names(n: int) -> list[str]:
    try:
        from prometheus_math.databases import knotinfo as ki

        knots = ki.all_knots(crossing_max=13, hyperbolic_only=False)
        return [k["name"] for k in knots[:n]]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Benchmarks
# ---------------------------------------------------------------------------


@pytest.mark.tier2_candidate
def bench_oeis_local_lookup(benchmark):
    """1000 random A-number lookups against local OEIS mirror."""
    from prometheus_math.databases import oeis

    if not oeis.has_local_mirror():
        pytest.skip("local OEIS mirror not present")

    a_numbers = _random_a_numbers(1000)

    # Force local-first mode for the duration of the benchmark
    prev = oeis.use_local_first(True)
    try:

        def go():
            return [oeis.lookup(a) for a in a_numbers]

        result = benchmark(go)
        assert len(result) == 1000
    finally:
        oeis.use_local_first(prev)


def bench_lmfdb_ec_query(benchmark):
    """50 random label queries against LMFDB.

    Deliberately not marked tier2_candidate: this is I/O-dominated.
    Useful as a baseline for "is the wrapper itself slow?" rather than
    a Tier-2 promotion candidate.
    """
    from prometheus_math.databases import lmfdb

    if not lmfdb.probe(timeout=2.0):
        pytest.skip("LMFDB Postgres mirror unreachable")

    labels = _ec_labels_from_lmfdb(50)

    def go():
        out = []
        for label in labels:
            try:
                out.append(
                    lmfdb.elliptic_curves(lmfdb_label=label, limit=1)
                )
            except Exception:
                out.append(None)
        return out

    result = benchmark(go)
    assert len(result) == 50


@pytest.mark.tier2_candidate
def bench_knotinfo_lookup(benchmark):
    """First 100 knot lookups via KnotInfo."""
    from prometheus_math.databases import knotinfo as ki

    names = _knot_names(100)
    if len(names) < 10:
        pytest.skip("local KnotInfo mirror missing or too small")

    def go():
        return [ki.lookup(nm) for nm in names]

    result = benchmark(go)
    assert len(result) == len(names)
