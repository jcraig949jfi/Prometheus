"""Pytest configuration for the benchmark suite.

Defaults:
- Benchmarks are *opt-in*. Plain `pytest prometheus_math/` will not
  trigger them (we mark them and skip unless `--run-benchmarks` or
  `--benchmark-only` is on the command line, or env var
  `PROMETHEUS_RUN_BENCHMARKS=1` is set).
- Per-benchmark timeout: 30 s (Tier-2 candidates should be obviously
  slow without going terminal).
- pytest-benchmark statistics are emitted as JSON in
  `prometheus_math/benchmarks/.benchmarks/`.

Add a new benchmark by writing a function `def bench_*(benchmark, ...)`
in any `bench_*.py` file in this directory. The auto-collected mark
`benchmark` will be applied; researcher-facing categorization (e.g.
"hot", "cold", "io") goes via `pytest.mark.<name>`.
"""

from __future__ import annotations

import os
import pathlib

import pytest


_BENCH_DIR = pathlib.Path(__file__).parent
_BENCH_OUT = _BENCH_DIR / ".benchmarks"


def pytest_addoption(parser):
    """Register --run-benchmarks. Defaults to off so casual `pytest`
    runs do not pay the (potentially minute-long) benchmark cost.
    """
    parser.addoption(
        "--run-benchmarks",
        action="store_true",
        default=False,
        help="Actually execute prometheus_math benchmarks (opt-in).",
    )


def pytest_configure(config):
    """Register custom marks and ensure benchmark output dir exists."""
    config.addinivalue_line(
        "markers",
        "benchmark: mark test as a performance benchmark (opt-in)",
    )
    config.addinivalue_line(
        "markers",
        "tier2_candidate: operation suspected of being a Tier-2 "
        "promotion candidate (slow Python loop)",
    )
    _BENCH_OUT.mkdir(parents=True, exist_ok=True)


def pytest_collection_modifyitems(config, items):
    """Auto-tag items in this benchmark dir, and skip them unless
    benchmarks are explicitly requested."""
    run_benchmarks = (
        config.getoption("--run-benchmarks", default=False)
        or config.getoption("--benchmark-only", default=False)
        or os.environ.get("PROMETHEUS_RUN_BENCHMARKS", "0") == "1"
    )
    bench_marker = pytest.mark.benchmark
    skip_marker = pytest.mark.skip(
        reason="benchmark (use --run-benchmarks or --benchmark-only)"
    )
    bench_root_str = str(_BENCH_DIR.resolve())
    for item in items:
        item_path = str(pathlib.Path(item.fspath).resolve())
        if not item_path.startswith(bench_root_str):
            continue
        # Smoke tests under benchmarks/tests/ are NOT benchmarks
        # themselves — they exercise the harness, so always run.
        if "benchmarks" + os.sep + "tests" in item_path:
            continue
        item.add_marker(bench_marker)
        if not run_benchmarks:
            item.add_marker(skip_marker)


@pytest.fixture(scope="session")
def benchmark_timeout_s() -> float:
    """Per-benchmark soft timeout. Hard timeout is left to pytest."""
    return 30.0


@pytest.fixture(scope="session")
def tier2_threshold_ms() -> float:
    """Operations slower than this median are flagged as Tier-2
    promotion candidates."""
    return 100.0
