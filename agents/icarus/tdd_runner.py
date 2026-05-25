"""
Icarus TDD runner -- spec v0.1 sect 2.4 (unchanged in v0.2).

Three test sources, all must pass:
  1. Built-in tier-falsification tests: cycle_<N>/code/tests/test_tier_R*_falsification.py
  2. Icarus-generated tests:           cycle_<N>/code/tests/generated/*.py
  3. Frontier-supplied tests:          cycle_<N>/code/tests/frontier_supplied/*.py

Also enforces lower-tier regression: if tier_target is R3, must also pass
all R0/R1/R2 tests. Any regression -> automatic park (spec v0.2 #14).

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def run_all_tests(
    source_dir: Path,
    cycle_n: int,
    tier_target: str,
) -> dict:
    """Discover + run all 3 test sources via pytest. Returns:
        {
          "all_passed": bool,
          "per_source": {
            "tier_falsification": {"passed": int, "failed": int, "errors": int, "skipped": int},
            "generated": {...},
            "frontier_supplied": {...},
          },
          "report_path": str,
          "regression_clean": bool,
        }
    """
    tests_dir = source_dir / "tests"
    report_path = source_dir.parent / "tests_run.jsonl"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    if not tests_dir.exists():
        return _empty_result(report_path, reason="no_tests_dir")

    # Discover test files per source
    tier_tests = list(tests_dir.glob("test_tier_*_falsification.py"))
    generated_tests = list((tests_dir / "generated").glob("test_*.py")) if (tests_dir / "generated").exists() else []
    frontier_tests = list((tests_dir / "frontier_supplied").glob("test_*.py")) if (tests_dir / "frontier_supplied").exists() else []

    results: dict[str, dict] = {
        "tier_falsification": _run_pytest(tier_tests, source_dir, cycle_n, "tier_falsification"),
        "generated": _run_pytest(generated_tests, source_dir, cycle_n, "generated"),
        "frontier_supplied": _run_pytest(frontier_tests, source_dir, cycle_n, "frontier_supplied"),
    }

    all_passed = all(
        r["failed"] == 0 and r["errors"] == 0
        for r in results.values()
    )

    # Lower-tier regression check (spec v0.2 #14)
    regression_clean = _check_lower_tier_regression(
        tier_target=tier_target,
        tier_results=results["tier_falsification"],
    )

    # Append rolled-up report row
    report_row = {
        "cycle_n": cycle_n,
        "tier_target": tier_target,
        "all_passed": all_passed,
        "regression_clean": regression_clean,
        "per_source": results,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    try:
        with open(report_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(report_row, default=str) + "\n")
    except Exception as e:
        print(f"[tdd] report append failed: {e}", file=sys.stderr)

    return {
        "all_passed": all_passed and regression_clean,
        "per_source": results,
        "report_path": str(report_path),
        "regression_clean": regression_clean,
    }


def _empty_result(report_path: Path, reason: str) -> dict:
    return {
        "all_passed": True,  # vacuously
        "per_source": {
            "tier_falsification": {"passed": 0, "failed": 0, "errors": 0, "skipped": 0},
            "generated": {"passed": 0, "failed": 0, "errors": 0, "skipped": 0},
            "frontier_supplied": {"passed": 0, "failed": 0, "errors": 0, "skipped": 0},
        },
        "report_path": str(report_path),
        "regression_clean": True,
        "note": reason,
    }


def _run_pytest(test_files: list[Path], source_dir: Path, cycle_n: int,
                source_category: str) -> dict:
    """Run pytest on the given test files; return aggregate counts."""
    if not test_files:
        return {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}

    # Run pytest as subprocess to isolate; capture JSON-report-like output
    # via -q + parse summary. We use a simple approach: count test outcomes
    # from the verbose output.
    args = ["python", "-m", "pytest", "-v", "--tb=line", "--no-header"]
    args.extend(str(p) for p in test_files)
    try:
        proc = subprocess.run(
            args, capture_output=True, text=True, timeout=120,
            cwd=str(source_dir.parent),
        )
        return _parse_pytest_output(proc.stdout + proc.stderr)
    except subprocess.TimeoutExpired:
        return {"passed": 0, "failed": 0, "errors": len(test_files), "skipped": 0,
                "note": "pytest_timeout"}
    except Exception as e:
        return {"passed": 0, "failed": 0, "errors": len(test_files), "skipped": 0,
                "note": f"pytest_invocation_error: {e}"}


def _parse_pytest_output(output: str) -> dict:
    """Parse pytest summary line like:
       '5 passed, 2 failed, 1 skipped in 0.12s'
    """
    out = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    import re
    summary = re.search(r"(\d+) passed", output)
    if summary:
        out["passed"] = int(summary.group(1))
    failed = re.search(r"(\d+) failed", output)
    if failed:
        out["failed"] = int(failed.group(1))
    errors = re.search(r"(\d+) error", output)
    if errors:
        out["errors"] = int(errors.group(1))
    skipped = re.search(r"(\d+) skipped", output)
    if skipped:
        out["skipped"] = int(skipped.group(1))
    return out


def _check_lower_tier_regression(tier_target: str, tier_results: dict) -> bool:
    """Per spec v0.2 #14: lower-tier tests must continue to pass. Phase 0
    stub: assume clean if zero failures."""
    return tier_results.get("failed", 0) == 0 and tier_results.get("errors", 0) == 0
