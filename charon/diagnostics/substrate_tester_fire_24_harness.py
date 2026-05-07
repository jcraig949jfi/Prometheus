"""
Substrate-Tester Fire #24 — Lane 16 (concurrency-stress re-probe) +
Lane 4 (cross-domain-leak T-ST003 regression check, my-instance).

Coordination: parallel substrate-tester ran fire #23 (commit 27cb9c5f,
Lane 14 + Lane 7). My fire = #24, lanes 16 + 4.

Lane 16 priority: re-probe concurrency contracts post-restart. Last
covered fire #12 (mine). Verify substrate's parallel-CLAIM safety still
holds under property-based stress.

Lane 4 priority: my-instance regression check on T-ST003 fix. Parallel
instance fire #19 reported "third T-ST003 regression PASS"; this is my
fourth check. Cheap to re-confirm; demonstrates ticket-flow durability.

Author: substrate-tester (Charon-aligned), fire #24, 2026-05-07
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from collections import Counter
from pathlib import Path

REPO = Path("F:/Prometheus")


# ---------------------------------------------------------------------------
# Lane 16 — concurrency-stress re-probe
# ---------------------------------------------------------------------------


def lane_16_concurrency_stress() -> dict:
    test_path = REPO / "prometheus_math" / "tests" / "test_concurrency_stress.py"
    if not test_path.exists():
        return {
            "lane": "16_concurrency_stress",
            "status": "DORMANT",
            "reason": f"test file missing: {test_path}",
        }

    t0 = time.time()
    proc = subprocess.run(
        ["python", "-m", "pytest", str(test_path), "-v", "--tb=short"],
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
    summary_line = ""
    for line in stdout.splitlines():
        if ("passed" in line or "failed" in line) and "==" in line:
            summary_line = line.strip("=").strip()

    tests = []
    if proc.returncode == 0 and n_passed > 0 and n_failed == 0:
        tests.append({
            "id": "T1_concurrency_stress_clean_run",
            "expected": "all concurrency-stress property tests pass",
            "actual": f"{n_passed} passed / 0 failed in {elapsed:.1f}s; {summary_line}",
            "verdict": "PASS",
            "severity": None,
            "note": (
                "Concurrency contracts (parallel CLAIMs against shared SQLite kernel "
                "raise-or-serialize, distinct ids preserved across threads, thread-safety "
                "boundary documented) re-verified post-fire-#12 baseline."
            ),
        })
    elif n_failed > 0:
        tests.append({
            "id": "T1_concurrency_stress_clean_run",
            "expected": "all property tests pass",
            "actual": f"{n_passed} passed / {n_failed} FAILED",
            "verdict": "FAIL",
            "severity": "P1-high",
            "note": "Race condition or verdict-drift under parallel load.",
        })
    else:
        tests.append({
            "id": "T1_concurrency_stress_clean_run",
            "expected": "harness completes",
            "actual": f"rc={proc.returncode}",
            "verdict": "FAIL",
            "severity": "P1-high",
            "stderr_tail": proc.stderr[-500:],
        })

    return {
        "lane": "16_concurrency_stress",
        "status": "LIVE",
        "wall_clock_seconds": elapsed,
        "rc": proc.returncode,
        "n_passed": n_passed,
        "n_failed": n_failed,
        "summary_line": summary_line,
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Lane 4 — T-ST003 regression
# ---------------------------------------------------------------------------


def lane_4_st003_regression() -> dict:
    """Confirm get_raw_invariant_keys still raises on unknown domain."""
    from prometheus_math.learner_corpus import get_raw_invariant_keys

    tests = []

    # T1: unknown domain raises
    try:
        keys = get_raw_invariant_keys("nonexistent_xyz_fire24")
        tests.append({
            "id": "T1_unknown_domain_raises",
            "expected": "KeyError or ValueError raised",
            "actual": f"silently returned {keys}",
            "verdict": "FAIL",
            "severity": "P2-normal",
            "note": "REGRESSION — T-ST003 fix appears to have been reverted",
        })
    except (KeyError, ValueError) as exc:
        tests.append({
            "id": "T1_unknown_domain_raises",
            "expected": "KeyError or ValueError raised",
            "actual": f"{type(exc).__name__}: {str(exc)[:140]}",
            "verdict": "PASS",
            "severity": None,
        })
    except Exception as exc:
        tests.append({
            "id": "T1_unknown_domain_raises",
            "expected": "KeyError or ValueError raised",
            "actual": f"{type(exc).__name__}: {exc}",
            "verdict": "PARTIAL",
            "severity": "P3-low",
        })

    # T2: registered domain still works (no over-blocking)
    try:
        keys = get_raw_invariant_keys("lehmer")
        if isinstance(keys, tuple) and len(keys) > 0 and "__unregistered__" not in keys:
            tests.append({
                "id": "T2_registered_domain_works",
                "expected": "lehmer returns valid keys",
                "actual": f"{len(keys)} keys; first={keys[0]}",
                "verdict": "PASS",
                "severity": None,
            })
        else:
            tests.append({
                "id": "T2_registered_domain_works",
                "expected": "lehmer returns valid keys",
                "actual": f"suspicious return: {keys}",
                "verdict": "FAIL",
                "severity": "P0-blocker",
            })
    except Exception as exc:
        tests.append({
            "id": "T2_registered_domain_works",
            "expected": "no over-blocking",
            "actual": f"{type(exc).__name__}: {exc}",
            "verdict": "FAIL",
            "severity": "P0-blocker",
        })

    return {
        "lane": "4_st003_regression",
        "n_tests": len(tests),
        "verdict_counts": dict(Counter(t["verdict"] for t in tests)),
        "tests": tests,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main():
    out_dir = REPO / "charon" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== Substrate-Tester Fire #24 ===")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n--- Lane 16: concurrency-stress re-probe ---")
    lane16 = lane_16_concurrency_stress()
    print(f"Status: {lane16.get('status')}, verdicts: {lane16.get('verdict_counts')}")
    for t in lane16.get("tests", []):
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    print("\n--- Lane 4: T-ST003 regression ---")
    lane4 = lane_4_st003_regression()
    print(f"Tests: {lane4['n_tests']}, verdicts: {lane4['verdict_counts']}")
    for t in lane4["tests"]:
        print(f"  [{t['verdict']}] {t['id']}: {t['actual'][:140]}")

    summary = {
        "fire_id": "fire_24_2026_05_07",
        "lanes": ["16_concurrency_stress", "4_st003_regression"],
        "lane_16": lane16,
        "lane_4": lane4,
    }
    out_path = out_dir / "substrate_tester_fire_24_results.json"
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
