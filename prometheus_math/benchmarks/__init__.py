"""prometheus_math.benchmarks — performance benchmarks for the arsenal.

This package contains pytest-benchmark-driven micro/macro benchmarks for
the hot-path operations exposed by `prometheus_math`. The goal is to
identify Tier-2 promotion candidates: operations whose median runtime is
slow enough that numpy vectorization, numba JIT, or a C/Rust rewrite
would produce a measurable researcher-facing speedup.

Entry point:
    python -m prometheus_math.benchmarks.run_all

Layout:
    bench_number_theory.py    — class numbers, Galois, LLL, Mahler, ...
    bench_elliptic_curves.py  — regulator, sha, Selmer, faltings
    bench_topology.py         — hyperbolic vol, Alexander, shape fields
    bench_databases.py        — local OEIS/LMFDB/knotinfo lookups
    run_all.py                — driver + RESULTS.md emitter
    BENCHMARKS.md             — researcher-facing doc
    RESULTS.md                — auto-generated current results
    tests/                    — smoke tests for the harness itself

Tier-2 promotion threshold: median wall time > 100 ms.
"""

__all__ = []  # nothing publicly exported; this is internal tooling
