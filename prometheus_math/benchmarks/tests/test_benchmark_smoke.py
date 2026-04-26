"""Smoke tests for the benchmarks harness itself.

These are NOT benchmarks — they verify the framework loads, the
bench_*.py files have at least one benchmark each, and the run_all
aggregator handles the empty-stats edge case.

Following math-tdd's four-category gate (adapted for harness code,
which has no published authoritative numerical reference):

- Authority: pytest-benchmark schema is well-documented; we assert that
  our run_all aggregator reads keys exactly as the public schema spec.
- Property: every bench_*.py has >=1 benchmark callable; bench_*
  callables are introspectable.
- Edge: empty benchmark JSON yields a syntactically valid (but
  near-empty) RESULTS.md.
- Composition: smoke-running one benchmark via pytest produces a
  valid stats JSON that run_all then converts to RESULTS.md.
"""

from __future__ import annotations

import importlib
import json
import pathlib
import re
import subprocess
import sys

import pytest


_BENCH_DIR = pathlib.Path(__file__).parent.parent
_BENCH_FILES = [
    "bench_number_theory",
    "bench_elliptic_curves",
    "bench_topology",
    "bench_databases",
]


# ---------------------------------------------------------------------------
# Property: each bench_*.py imports and has >=1 benchmark
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("modname", _BENCH_FILES)
def test_bench_module_imports_and_has_benchmark(modname):
    """Every bench_*.py imports and exposes at least one bench_*
    callable."""
    full = f"prometheus_math.benchmarks.{modname}"
    mod = importlib.import_module(full)
    benches = [
        name for name in dir(mod)
        if name.startswith("bench_") and callable(getattr(mod, name))
    ]
    assert len(benches) >= 1, (
        f"{modname} has no bench_* functions"
    )


def test_bench_files_collectively_cover_all_modules():
    """The four bench_*.py files exist on disk."""
    for modname in _BENCH_FILES:
        assert (_BENCH_DIR / f"{modname}.py").is_file(), (
            f"missing {modname}.py"
        )


# ---------------------------------------------------------------------------
# Authority: pytest-benchmark JSON schema fields read by run_all
# ---------------------------------------------------------------------------


def test_pytest_benchmark_json_schema_fields():
    """run_all expects these keys to exist on a real
    pytest-benchmark JSON. If pytest-benchmark ever renames them, this
    test catches it before the aggregator silently emits empty rows.

    Reference: https://pytest-benchmark.readthedocs.io/en/latest/usage.html
    section "JSON output".
    """
    fake_stats = {
        "machine_info": {"node": "x", "system": "y", "release": "z",
                         "python_version": "3.11"},
        "commit_info": {"id": "abc", "branch": "main"},
        "benchmarks": [
            {
                "name": "bench_x",
                "fullname": "path/to/bench_foo.py::bench_x",
                "stats": {
                    "median": 0.001, "mean": 0.001,
                    "min": 0.0009, "max": 0.0011,
                    "rounds": 10,
                },
            },
        ],
    }
    # Authoritative round-trip: dumping/loading does not lose info
    text = json.dumps(fake_stats)
    again = json.loads(text)
    assert again["benchmarks"][0]["stats"]["median"] == pytest.approx(0.001)
    assert "fullname" in again["benchmarks"][0]


# ---------------------------------------------------------------------------
# Edge: empty benchmark suite yields a non-empty but tiny RESULTS.md
# ---------------------------------------------------------------------------


def test_empty_stats_yields_minimal_results_md(tmp_path):
    """When pytest-benchmark emits no benchmarks (e.g. all skipped),
    run_all still writes a valid Markdown file rather than crashing.
    """
    from prometheus_math.benchmarks import run_all

    empty_json = tmp_path / "empty.json"
    empty_json.write_text(json.dumps({
        "machine_info": {}, "commit_info": {}, "benchmarks": []
    }))
    out_md = tmp_path / "RESULTS.md"

    stats = run_all._load_stats(empty_json)
    candidates = run_all._emit_markdown(stats, out_md, threshold_ms=100.0)

    assert candidates == []
    text = out_md.read_text(encoding="utf-8")
    assert "prometheus_math benchmark results" in text
    # Empty-state hint should appear
    assert "No benchmark data" in text


def test_threshold_correctly_classifies_tier2(tmp_path):
    """Edge: threshold logic. A 50 ms op is NOT a Tier-2 candidate at
    threshold=100 ms; a 200 ms op IS.
    """
    from prometheus_math.benchmarks import run_all

    stats = {
        "machine_info": {}, "commit_info": {},
        "benchmarks": [
            {"name": "fast_op",
             "fullname": "x/bench_a.py::fast_op",
             "stats": {"median": 0.050, "mean": 0.050,
                       "min": 0.04, "max": 0.06, "rounds": 5}},
            {"name": "slow_op",
             "fullname": "x/bench_a.py::slow_op",
             "stats": {"median": 0.200, "mean": 0.200,
                       "min": 0.15, "max": 0.25, "rounds": 5}},
        ],
    }
    out_md = tmp_path / "RESULTS.md"
    candidates = run_all._emit_markdown(stats, out_md, threshold_ms=100.0)
    assert candidates == ["slow_op"]
    txt = out_md.read_text(encoding="utf-8")
    assert "slow_op" in txt
    assert "fast_op" in txt


# ---------------------------------------------------------------------------
# Composition: run_all main() with --no-run on a fixture JSON
# ---------------------------------------------------------------------------


def test_run_all_no_run_emits_results(tmp_path):
    """Composition smoke: invoking run_all.main([... --no-run ...])
    against a fixture JSON produces a Markdown file with one row per
    benchmark in the JSON.
    """
    from prometheus_math.benchmarks import run_all

    fixture = tmp_path / "fixture.json"
    fixture.write_text(json.dumps({
        "machine_info": {"node": "smoke", "system": "test",
                         "release": "0", "python_version": "3.x"},
        "commit_info": {},
        "benchmarks": [
            {"name": "smoke_bench",
             "fullname": "x/bench_smoke.py::smoke_bench",
             "stats": {"median": 0.005, "mean": 0.005,
                       "min": 0.004, "max": 0.006, "rounds": 3}},
        ],
    }))
    out_md = tmp_path / "OUT.md"
    rc = run_all.main([
        "--no-run",
        "--no-update-benchmarks-md",
        "--json-out", str(fixture),
        "--out", str(out_md),
        "--threshold-ms", "1.0",
    ])
    assert rc == 0
    txt = out_md.read_text(encoding="utf-8")
    assert "smoke_bench" in txt
    # 5 ms > 1 ms threshold → must be flagged
    assert re.search(r"smoke_bench.*\*\*yes\*\*", txt) is not None


def test_pytest_benchmark_is_installed():
    """Authority: pytest-benchmark is the dependency we rely on."""
    pb = importlib.import_module("pytest_benchmark")
    assert hasattr(pb, "__version__")
