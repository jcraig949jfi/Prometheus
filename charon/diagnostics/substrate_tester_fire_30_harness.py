"""
Substrate-Tester Fire #30 — Lane 14 (replay-determinism re-probe) +
Lane 13 (canonicalization-fuzz with fresh hypothesis seed 20260601).

Coordination: parallel substrate-tester ran fire #29 (commit af0ea34f)
covering Lane 2 + Lane 10 with 2 new input-validation gap tickets.
My fire = #30, lanes 14 + 13.

Both lanes are pytest-based. Single pytest invocation runs both:
  pytest test_replay_capsule_determinism.py test_canonicalization_fuzz.py
         --hypothesis-seed=20260601

Author: substrate-tester (Charon-aligned), fire #30, 2026-05-07
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from collections import Counter
from pathlib import Path

REPO = Path("F:/Prometheus")


def lane_14_and_13_combined() -> dict:
    """Run both replay-determinism + canonicalization-fuzz in one pytest."""
    test_paths = [
        REPO / "prometheus_math" / "tests" / "test_replay_capsule_determinism.py",
        REPO / "prometheus_math" / "tests" / "test_canonicalization_fuzz.py",
    ]

    seed = "20260601"
    t0 = time.time()
    proc = subprocess.run(
        ["python", "-m", "pytest"]
        + [str(p) for p in test_paths]
        + ["--hypothesis-seed=" + seed, "-v", "--tb=short"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=600,
        env={"PYTHONPATH": str(REPO), **os.environ},
    )
    elapsed = time.time() - t0

    stdout = proc.stdout
    test_lines = [l for l in stdout.splitlines() if " PASSED" in l or " FAILED" in l]
    n_passed = sum(1 for l in test_lines if " PASSED" in l)
    n_failed = sum(1 for l in test_lines if " FAILED" in l)

    # Per-lane breakdown
    n_replay_passed = sum(1 for l in test_lines if " PASSED" in l and "test_replay_capsule_determinism" in l)
    n_canon_passed = sum(1 for l in test_lines if " PASSED" in l and "test_canonicalization_fuzz" in l)

    summary_line = ""
    for line in stdout.splitlines():
        if ("passed" in line or "failed" in line) and "==" in line:
            summary_line = line.strip("=").strip()

    lane_14_tests = []
    lane_13_tests = []

    if n_replay_passed >= 7 and n_failed == 0:
        lane_14_tests.append({
            "id": "T1_replay_determinism_clean_run",
            "expected": "all 7 replay-determinism tests pass",
            "actual": f"{n_replay_passed} passed",
            "verdict": "PASS",
            "severity": None,
        })
    else:
        lane_14_tests.append({
            "id": "T1_replay_determinism_clean_run",
            "expected": "7 tests pass",
            "actual": f"{n_replay_passed} passed, {n_failed} failed",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })

    if n_canon_passed >= 13 and n_failed == 0:
        lane_13_tests.append({
            "id": "T1_fuzzer_clean_run_seed_20260601",
            "expected": "all 13 fuzz properties pass",
            "actual": f"{n_canon_passed} passed at seed=20260601",
            "verdict": "PASS",
            "severity": None,
            "note": "6th independent hypothesis seed for cumulative coverage",
        })
    else:
        lane_13_tests.append({
            "id": "T1_fuzzer_clean_run_seed_20260601",
            "expected": "13 fuzz properties pass",
            "actual": f"{n_canon_passed} passed, {n_failed} failed",
            "verdict": "FAIL",
            "severity": "P1-high",
        })

    return {
        "wall_clock_seconds": elapsed,
        "rc": proc.returncode,
        "n_total_passed": n_passed,
        "n_total_failed": n_failed,
        "n_replay_passed": n_replay_passed,
        "n_canon_passed": n_canon_passed,
        "summary_line": summary_line,
        "lane_14": {
            "n_tests": len(lane_14_tests),
            "verdict_counts": dict(Counter(t["verdict"] for t in lane_14_tests)),
            "tests": lane_14_tests,
        },
        "lane_13": {
            "n_tests": len(lane_13_tests),
            "verdict_counts": dict(Counter(t["verdict"] for t in lane_13_tests)),
            "tests": lane_13_tests,
        },
    }


def main():
    out_dir = REPO / "charon" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== Substrate-Tester Fire #30 ===")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("--- Lane 14 (replay-det) + Lane 13 (canon-fuzz seed 20260601), combined pytest ---")

    r = lane_14_and_13_combined()

    print(f"Total: {r['n_total_passed']} passed, {r['n_total_failed']} failed in {r['wall_clock_seconds']:.1f}s")
    print(f"  Lane 14 (replay-det): {r['n_replay_passed']} passed")
    print(f"  Lane 13 (canon-fuzz):  {r['n_canon_passed']} passed")
    print()
    for t in r["lane_14"]["tests"]:
        print(f"  Lane 14 [{t['verdict']}] {t['id']}: {t['actual'][:120]}")
    for t in r["lane_13"]["tests"]:
        print(f"  Lane 13 [{t['verdict']}] {t['id']}: {t['actual'][:120]}")

    summary = {
        "fire_id": "fire_30_2026_05_07",
        "lanes": ["14_replay_determinism", "13_canonicalization_fuzz"],
        "hypothesis_seed": "20260601",
        "combined_pytest_result": r,
    }
    out_path = out_dir / "substrate_tester_fire_30_results.json"
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
