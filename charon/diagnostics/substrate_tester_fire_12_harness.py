"""
Substrate-Tester Fire #12 — Lane 14 (replay-determinism, smoke) +
Lane 16 (concurrency-stress, smoke).

Coordination note: parallel substrate-tester instance ran fire #11
(commit 9e6ce41f) covering lanes 9 + 6. This fire = #12. Both instances
were running concurrently with overlapping lane plans — rotation
discipline still satisfied because the parallel instance picked
different lanes (9 + 6) than I planned (14 + 16). No conflict.

Lane 14 + 16 priority: both LIVE post-restart but never smoke-tested
across both substrate-tester instances. Closing the post-activation
rotation gap per fire-#10 standing rec.

Author: substrate-tester (Charon-aligned), fire #12, 2026-05-07
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from collections import Counter
from pathlib import Path

REPO = Path("F:/Prometheus")


def run_pytest(test_path: Path, label: str, timeout: int = 300) -> dict:
    """Run a pytest file; return rc, n_passed, n_failed, summary, wall_clock."""
    t0 = time.time()
    proc = subprocess.run(
        [
            "python", "-m", "pytest",
            str(test_path),
            "-v",
            "--tb=short",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
        env={"PYTHONPATH": str(REPO), **os.environ},
    )
    elapsed = time.time() - t0

    stdout = proc.stdout
    test_lines = [l for l in stdout.splitlines() if " PASSED" in l or " FAILED" in l]
    n_passed = sum(1 for l in test_lines if " PASSED" in l)
    n_failed = sum(1 for l in test_lines if " FAILED" in l)

    summary_line = ""
    for line in stdout.splitlines():
        if ("passed" in line or "failed" in line) and "==" in line:
            summary_line = line.strip("=").strip()

    test_names = []
    for line in test_lines:
        if "::" in line:
            name = line.split(" ")[0].split("::")[-1]
            verdict = "PASSED" if " PASSED" in line else "FAILED"
            test_names.append({"name": name, "verdict": verdict})

    return {
        "label": label,
        "test_path": str(test_path),
        "rc": proc.returncode,
        "wall_clock_seconds": elapsed,
        "n_passed": n_passed,
        "n_failed": n_failed,
        "summary_line": summary_line,
        "test_names": test_names,
        "stderr_tail": proc.stderr[-1000:] if proc.stderr else "",
    }


def lane_14_replay_determinism() -> dict:
    """Smoke-test the replay-capsule-determinism harness."""
    test_path = REPO / "prometheus_math" / "tests" / "test_replay_capsule_determinism.py"
    if not test_path.exists():
        return {
            "lane": "14_replay_determinism",
            "status": "DORMANT",
            "reason": f"test file not found at {test_path}",
        }

    r = run_pytest(test_path, "lane_14_replay_determinism", timeout=300)

    tests = []
    if r["rc"] == 0 and r["n_passed"] > 0 and r["n_failed"] == 0:
        tests.append({
            "id": "T1_replay_determinism_clean_run",
            "expected": "all replay-determinism property tests pass",
            "actual": f"{r['n_passed']} passed / 0 failed in {r['wall_clock_seconds']:.1f}s; {r['summary_line']}",
            "verdict": "PASS",
            "severity": None,
            "note": (
                "Properties: per-record replay determinism, cross-replay determinism "
                "(K replays sha256-identical), JSON round-trip stability, canonical-form "
                "determinism, replay timing soft-fail, full corpus coverage of 20 v2 "
                "KillVector component types, replay-does-not-mutate-capsule. "
                "Substrate-grade GREEN."
            ),
        })
    elif r["n_failed"] > 0:
        tests.append({
            "id": "T1_replay_determinism_clean_run",
            "expected": "all property tests pass",
            "actual": f"{r['n_passed']}/{r['n_passed']+r['n_failed']} passed; {r['summary_line']}",
            "verdict": "FAIL",
            "severity": "P0-blocker",
            "note": "Any replay-determinism failure = byte-divergent replay = substrate hash discipline broken.",
            "test_names": r["test_names"],
        })
    else:
        tests.append({
            "id": "T1_replay_determinism_clean_run",
            "expected": "harness completes",
            "actual": f"rc={r['rc']}; n_passed={r['n_passed']}; n_failed={r['n_failed']}",
            "verdict": "FAIL",
            "severity": "P1-high",
            "stderr_tail": r["stderr_tail"],
        })

    return {
        "lane": "14_replay_determinism",
        "status": "LIVE",
        "pytest_result": r,
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


def lane_16_concurrency_stress() -> dict:
    """Smoke-test the concurrency-stress harness."""
    test_path = REPO / "prometheus_math" / "tests" / "test_concurrency_stress.py"
    if not test_path.exists():
        return {
            "lane": "16_concurrency_stress",
            "status": "DORMANT",
            "reason": f"test file not found at {test_path}",
        }

    r = run_pytest(test_path, "lane_16_concurrency_stress", timeout=600)

    tests = []
    if r["rc"] == 0 and r["n_passed"] > 0 and r["n_failed"] == 0:
        tests.append({
            "id": "T1_concurrency_stress_clean_run",
            "expected": "all concurrency-stress property tests pass",
            "actual": f"{r['n_passed']} passed / 0 failed in {r['wall_clock_seconds']:.1f}s; {r['summary_line']}",
            "verdict": "PASS",
            "severity": None,
            "note": (
                "Properties: parallel CLAIMs against shared SQLite kernel "
                "raise-or-serialize (no silent data corruption), 100 parallel "
                "claims across 100 separate kernels succeed, identical inputs "
                "yield identical content across threads, distinct inputs yield "
                "distinct ids, thread-safety boundary documented. Substrate-grade GREEN."
            ),
        })
    elif r["n_failed"] > 0:
        tests.append({
            "id": "T1_concurrency_stress_clean_run",
            "expected": "all property tests pass",
            "actual": f"{r['n_passed']}/{r['n_passed']+r['n_failed']} passed; {r['summary_line']}",
            "verdict": "FAIL",
            "severity": "P1-high",
            "note": "Race condition or verdict-drift under parallel load.",
            "test_names": r["test_names"],
        })
    else:
        tests.append({
            "id": "T1_concurrency_stress_clean_run",
            "expected": "harness completes",
            "actual": f"rc={r['rc']}; n_passed={r['n_passed']}; n_failed={r['n_failed']}",
            "verdict": "FAIL",
            "severity": "P1-high",
            "stderr_tail": r["stderr_tail"],
        })

    return {
        "lane": "16_concurrency_stress",
        "status": "LIVE",
        "pytest_result": r,
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


def main():
    out_dir = REPO / "charon" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== Substrate-Tester Fire #12 ===")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n--- Lane 14: replay-determinism smoke ---")
    lane14 = lane_14_replay_determinism()
    print(f"Status: {lane14.get('status')}, verdicts: {lane14.get('verdict_counts')}")
    for t in lane14.get("tests", []):
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    print("\n--- Lane 16: concurrency-stress smoke ---")
    lane16 = lane_16_concurrency_stress()
    print(f"Status: {lane16.get('status')}, verdicts: {lane16.get('verdict_counts')}")
    for t in lane16.get("tests", []):
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    summary = {
        "fire_id": "fire_12_2026_05_07",
        "lanes": ["14_replay_determinism", "16_concurrency_stress"],
        "lane_14": lane14,
        "lane_16": lane16,
    }
    out_path = out_dir / "substrate_tester_fire_12_results.json"
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
