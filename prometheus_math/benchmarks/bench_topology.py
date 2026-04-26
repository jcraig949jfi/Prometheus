"""Benchmarks for prometheus_math.topology.

Inputs come from KnotInfo (local mirror); we sample the first
`crossing_max <= 13` knots and slice. Each benchmark cleanly skips if
the local KnotInfo mirror is missing.
"""

from __future__ import annotations

import pytest

try:
    import prometheus_math as pm

    _PM_OK = True
except Exception:  # pragma: no cover
    _PM_OK = False


pytestmark = pytest.mark.skipif(
    not _PM_OK, reason="prometheus_math import failed"
)


def _hyperbolic_knot_names(n: int) -> list[str]:
    """Return up to `n` hyperbolic knot names from KnotInfo."""
    try:
        from prometheus_math.databases import knotinfo as ki

        knots = ki.all_knots(crossing_max=13, hyperbolic_only=True)
        return [k["name"] for k in knots[:n]]
    except Exception:
        return []


def _all_knot_names(n: int) -> list[str]:
    """Return up to `n` knot names (any topological type)."""
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
def bench_hyperbolic_volume(benchmark):
    """First 100 hyperbolic knots, hyperbolic_volume."""
    names = _hyperbolic_knot_names(100)
    if len(names) < 10:
        pytest.skip("not enough hyperbolic knots in local KnotInfo mirror")

    def go():
        out = []
        for nm in names:
            try:
                out.append(pm.topology.hyperbolic_volume(nm))
            except Exception:
                out.append(None)
        return out

    result = benchmark(go)
    assert len(result) == len(names)


@pytest.mark.tier2_candidate
def bench_alexander_polynomial(benchmark):
    """First 100 knots (any), Alexander polynomial."""
    names = _all_knot_names(100)
    if len(names) < 10:
        pytest.skip("not enough knots in local KnotInfo mirror")

    def go():
        out = []
        for nm in names:
            try:
                out.append(pm.topology.alexander_polynomial(nm))
            except Exception:
                out.append(None)
        return out

    result = benchmark(go)
    assert len(result) == len(names)


@pytest.mark.tier2_candidate
def bench_knot_shape_field_max_deg_8(benchmark):
    """First 50 hyperbolic knots, knot_shape_field with max_deg=8.

    Suspected slow operation: snappy.shape_field(bits_prec=300) +
    polredabs round-trip per knot, no caching across knots.
    """
    names = _hyperbolic_knot_names(50)
    if len(names) < 5:
        pytest.skip("not enough hyperbolic knots in local KnotInfo mirror")

    def go():
        out = []
        for nm in names:
            try:
                out.append(
                    pm.topology.knot_shape_field(
                        nm, bits_prec=200, max_deg=8
                    )
                )
            except Exception:
                out.append(None)
        return out

    result = benchmark(go)
    assert len(result) == len(names)
