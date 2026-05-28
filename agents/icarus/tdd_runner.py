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
        # Q9: blind holdout oracle -- frozen, never seen by the Generator
        "holdout": _run_holdout(source_dir, tier_target),
    }

    total_passed = sum(r["passed"] for r in results.values())
    total_failed = sum(r["failed"] for r in results.values())
    total_errors = sum(r["errors"] for r in results.values())

    # A vacuous "0 passed, 0 failed" is NOT a real pass. Require at least one
    # test to actually have run AND no failures.
    all_passed = (total_passed > 0 and total_failed == 0 and total_errors == 0)

    # Holdout failures are the blind-oracle signal -- track separately so the
    # training object can distinguish "passed visible, failed blind" (Goodhart).
    holdout = results["holdout"]
    holdout_clean = (holdout["failed"] == 0 and holdout["errors"] == 0)

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
        "holdout_clean": holdout_clean,
        "per_source": results,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    try:
        with open(report_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(report_row, default=str) + "\n")
    except Exception as e:
        print(f"[tdd] report append failed: {e}", file=sys.stderr)

    return {
        # Holdout is a HARD gate: a cycle that fails the blind oracle has not
        # actually reached the tier, no matter what its visible tests say.
        "all_passed": all_passed and regression_clean and holdout_clean,
        "per_source": results,
        "report_path": str(report_path),
        "regression_clean": regression_clean,
        "holdout_clean": holdout_clean,
        "goodhart_flag": (all_passed and regression_clean and not holdout_clean),
    }


def _empty_result(report_path: Path, reason: str) -> dict:
    return {
        "all_passed": False,  # vacuous-pass is no longer treated as pass
        "per_source": {
            "tier_falsification": {"passed": 0, "failed": 0, "errors": 0, "skipped": 0},
            "generated": {"passed": 0, "failed": 0, "errors": 0, "skipped": 0},
            "frontier_supplied": {"passed": 0, "failed": 0, "errors": 0, "skipped": 0},
        },
        "report_path": str(report_path),
        "regression_clean": True,
        "note": reason,
    }


_HOLDOUT_DIR = Path(r"D:\Prometheus\agents\icarus\holdout")

# Which holdout suites apply at each tier target (cumulative: higher tiers
# also run lower-tier holdouts as regression).
_HOLDOUT_BY_TIER = {
    "R0": ["test_holdout_R1.py"],   # R0 has no dedicated holdout; R1 covers basics
    "R1": ["test_holdout_R1.py"],
    "R2": ["test_holdout_R1.py", "test_holdout_R2.py"],
    "R3": ["test_holdout_R1.py", "test_holdout_R2.py"],
}


def _run_holdout(source_dir: Path, tier_target: str) -> dict:
    """Q9: run the BLIND holdout oracle against the candidate. The holdout
    tests live in a frozen dir outside any cycle; they locate the candidate
    via ICARUS_CANDIDATE_DIR. Tier-matched + cumulative."""
    import os
    suites = _HOLDOUT_BY_TIER.get(tier_target, ["test_holdout_R1.py"])
    files = [_HOLDOUT_DIR / s for s in suites if (_HOLDOUT_DIR / s).exists()]
    if not files:
        return {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "note": "no_holdout"}

    args = ["python", "-m", "pytest", "-q", "--tb=no", "--no-header",
            "--import-mode=importlib"]
    args.extend(str(p) for p in files)
    env = dict(os.environ)
    env["ICARUS_CANDIDATE_DIR"] = str(source_dir)
    try:
        proc = subprocess.run(
            args, capture_output=True, text=True, timeout=120,
            cwd=str(_HOLDOUT_DIR), env=env,
        )
        return _parse_pytest_output(proc.stdout + proc.stderr)
    except subprocess.TimeoutExpired:
        return {"passed": 0, "failed": 0, "errors": len(files), "skipped": 0, "note": "holdout_timeout"}
    except Exception as e:
        return {"passed": 0, "failed": 0, "errors": len(files), "skipped": 0, "note": f"holdout_error: {e}"}


def _run_pytest(test_files: list[Path], source_dir: Path, cycle_n: int,
                source_category: str) -> dict:
    """Run pytest on the given test files; return aggregate counts."""
    if not test_files:
        return {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}

    # Run pytest as subprocess to isolate; capture stdout + stderr; parse
    # the summary line. Important: cwd must be the cycle's code/ dir so the
    # test's `from reasoner import Reasoner` resolves.
    args = ["python", "-m", "pytest", "-v", "--tb=line", "--no-header",
            "--import-mode=importlib"]
    args.extend(str(p) for p in test_files)
    try:
        proc = subprocess.run(
            args, capture_output=True, text=True, timeout=120,
            cwd=str(source_dir),   # code/ -- where reasoner.py lives
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
