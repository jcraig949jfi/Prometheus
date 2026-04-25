# prometheus_math benchmarks

Performance benchmarks for the `prometheus_math` arsenal, used to find
**Tier-2 promotion candidates**: operations slow enough that numpy
vectorization, numba JIT, or rewriting in C/Rust would deliver a
researcher-felt speedup.

## How to run

The whole suite (driver script):

```bash
python -m prometheus_math.benchmarks.run_all
```

Quick mode (1 round per bench, ~minutes instead of ~hour):

```bash
python -m prometheus_math.benchmarks.run_all --quick
```

Or invoke pytest directly:

```bash
pytest prometheus_math/benchmarks/ \
    --run-benchmarks \
    --benchmark-only \
    --benchmark-json=prometheus_math/benchmarks/.benchmarks/latest.json
```

Pure `pytest prometheus_math/` will *skip* every benchmark — they are
opt-in via `--run-benchmarks`, `--benchmark-only`, or the env var
`PROMETHEUS_RUN_BENCHMARKS=1`. This keeps the unit-test suite fast.

## Benchmark categories

| File | Module | Notes |
|---|---|---|
| `bench_number_theory.py` | `pm.number_theory` | class numbers, Galois, LLL, Mahler, HCF, CM orders |
| `bench_elliptic_curves.py` | `pm.elliptic_curves` | regulator, analytic Sha (with/without hint), Selmer, Faltings |
| `bench_topology.py` | `pm.topology` | hyperbolic volume, Alexander polynomial, knot shape field |
| `bench_databases.py` | `pm.databases` | local OEIS, LMFDB EC query, KnotInfo lookup |

Each benchmark sets a deterministic seed, runs against representative
input volumes (N=20 to N=1000 depending on per-call cost), and asserts
that the output cardinality matches the input — so a benchmark
disappearing into a silent error is caught.

## Methodology

- **Tool:** [pytest-benchmark](https://pytest-benchmark.readthedocs.io/)
  v5.x. Median wall time is the primary metric; min / max / mean are
  reported for context.
- **Threshold:** an operation is flagged Tier-2 iff its median runtime
  exceeds **100 ms** (configurable via `--threshold-ms`). Choice of
  100 ms is the inflection point above which interactive researcher
  workflows feel laggy.
- **Inputs:** seeded random plus authoritative database fixtures
  (LMFDB rank-0 curves, KnotInfo crossing-number-13 census). When a
  database is unavailable the benchmark is skipped, not failed.
- **Backends:** the benchmark runs against whichever PARI / SnapPy /
  numpy install is present. Re-run after a backend swap to compare.

## Reproducibility notes

- The full suite takes **>30 minutes** on a workstation with
  PARI 2.15 + SnapPy 3.x installed; use `--quick` for CI-friendly runs.
- Each benchmark caps individual wall time at 30 s (see
  `conftest.py:benchmark_timeout_s`). Slow operations should still
  finish a single iteration within that bound; if not, drop the input
  size or split the benchmark.
- pytest-benchmark stores raw stats in `.benchmarks/latest.json`; this
  is the source of truth for `RESULTS.md`.
- LMFDB benchmarks query the live Postgres mirror at collection time,
  caching the result in memory. They will skip cleanly when the mirror
  is unreachable.

## Current Tier-2 promotion candidates

The list below is **auto-refreshed** by `run_all.py`. Don't edit by
hand — re-run the suite.

<!-- BENCHMARKS_AUTO_BEGIN -->
- _no candidates yet — run the suite at least once_
<!-- BENCHMARKS_AUTO_END -->

## Promotion workflow (after a candidate is identified)

1. Open a backlog entry under `techne/PROJECT_BACKLOG_1000.md` of the
   form "Tier-2 *<technique>* of `<op>`" (numpy / numba / Rust).
2. Implement the optimization behind the same public API. The
   benchmark is the regression test.
3. Re-run `python -m prometheus_math.benchmarks.run_all` and confirm
   the operation drops below the 100 ms threshold (or, for ops that
   stay above, that the speedup is at least 5x).
4. Commit with the new `RESULTS.md` checked in so the speedup is
   visible in the diff.
