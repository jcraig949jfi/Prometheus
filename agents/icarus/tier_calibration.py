"""
Tier discrimination calibration (Q10).

A tier-n falsification test is VALID only if it discriminates: a reasoner that
has genuinely reached tier n passes it, and a reasoner below tier n fails it.
If an early/low-tier reasoner passes the R2 test, the R2 test is too weak --
which is the suspected cause of the whitepaper's R2-easier-than-R1 anomaly.

This runs every tier falsification test + blind holdout against a set of
reasoner versions (bootstrap + each stable cycle in lineage) and builds a
discrimination matrix. A test that everything passes (or everything fails) is
non-discriminating and should be hardened.

Run:  python agents/icarus/tier_calibration.py
FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ICARUS = Path(r"D:\Prometheus\agents\icarus")
CYCLES = ICARUS / "cycles"
HOLDOUT = ICARUS / "holdout"

# The frozen tier falsification tests live in the bootstrap cycle's tests dir.
_TIER_TESTS = {
    "R0": "test_tier_R0_falsification.py",
    "R1": "test_tier_R1_falsification.py",
    "R2": "test_tier_R2_falsification.py",
}
_HOLDOUT_TESTS = {
    "R1": "test_holdout_R1.py",
    "R2": "test_holdout_R2.py",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_test_against(code_dir: Path, test_file: Path, holdout: bool) -> dict:
    """Run one test file against one reasoner code dir. Returns pass/fail."""
    if not code_dir.exists() or not test_file.exists():
        return {"passed": 0, "failed": 0, "skipped": 0, "ran": False}
    args = ["python", "-m", "pytest", "-q", "--tb=no", "--no-header",
            "--import-mode=importlib", str(test_file)]
    env = dict(os.environ)
    if holdout:
        env["ICARUS_CANDIDATE_DIR"] = str(code_dir)
        cwd = str(HOLDOUT)
    else:
        cwd = str(code_dir)
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=120,
                              cwd=cwd, env=env)
        out = proc.stdout + proc.stderr
        return {
            "passed": _count(out, "passed"),
            "failed": _count(out, "failed"),
            "skipped": _count(out, "skipped"),
            "ran": True,
        }
    except Exception as e:
        return {"passed": 0, "failed": 0, "skipped": 0, "ran": False, "error": str(e)}


def _count(output: str, kind: str) -> int:
    import re
    m = re.search(rf"(\d+) {kind}", output)
    return int(m.group(1)) if m else 0


def _verdict(res: dict) -> str:
    if not res.get("ran"):
        return "n/a"
    if res["failed"] > 0:
        return "FAIL"
    if res["passed"] == 0:
        return "vacuous"  # all skipped / nothing ran
    return "PASS"


def discover_reasoner_versions() -> list[tuple[str, Path]]:
    """Bootstrap + each stable cycle's code dir, oldest first."""
    versions = [("bootstrap_000", CYCLES / "cycle_000" / "code")]
    if CYCLES.exists():
        for cp in sorted(CYCLES.iterdir()):
            if not cp.is_dir() or not cp.name.startswith("cycle_") or cp.name == "cycle_000":
                continue
            outcome = cp / "outcome.json"
            if not outcome.exists():
                continue
            try:
                o = json.loads(outcome.read_text(encoding="utf-8"))
            except Exception:
                continue
            if o.get("decision") == "mark_stable":
                versions.append((cp.name, cp / "code"))
    return versions


def run_calibration() -> dict:
    versions = discover_reasoner_versions()
    bootstrap_tests_dir = CYCLES / "cycle_000" / "code" / "tests"

    matrix = {}  # test_name -> {version -> verdict}
    all_tests = []

    for tier, fname in _TIER_TESTS.items():
        tf = bootstrap_tests_dir / fname
        all_tests.append((f"tier_{tier}", tf, False))
    for tier, fname in _HOLDOUT_TESTS.items():
        all_tests.append((f"holdout_{tier}", HOLDOUT / fname, True))

    for test_name, test_file, is_holdout in all_tests:
        matrix[test_name] = {}
        for vname, vdir in versions:
            res = _run_test_against(vdir, test_file, is_holdout)
            matrix[test_name][vname] = _verdict(res)

    # Discrimination analysis: a test discriminates if it has BOTH a PASS and
    # a FAIL across versions. All-PASS = too weak; all-FAIL = too hard/unreached.
    diagnosis = {}
    for test_name, row in matrix.items():
        verdicts = [v for v in row.values() if v in ("PASS", "FAIL")]
        passes = verdicts.count("PASS")
        fails = verdicts.count("FAIL")
        if passes > 0 and fails > 0:
            status = "discriminating"
        elif passes > 0 and fails == 0:
            status = "too_weak_all_pass"
        elif fails > 0 and passes == 0:
            status = "unreached_all_fail"
        else:
            status = "inconclusive"
        diagnosis[test_name] = {
            "status": status, "passes": passes, "fails": fails,
        }

    # The key anomaly check: does the bootstrap pass any tier-R2+ test?
    bootstrap_overreach = []
    for test_name, row in matrix.items():
        if ("R2" in test_name) and row.get("bootstrap_000") == "PASS":
            bootstrap_overreach.append(test_name)

    summary = {
        "generated_at": _now_iso(),
        "versions_tested": [v[0] for v in versions],
        "matrix": matrix,
        "diagnosis": diagnosis,
        "bootstrap_overreach": bootstrap_overreach,
        "anomaly_detected": len(bootstrap_overreach) > 0
            or any(d["status"] == "too_weak_all_pass" for d in diagnosis.values()),
    }

    out = ICARUS / "state" / "tier_calibration.json"
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    except Exception:
        pass
    return summary


def _print_matrix(summary: dict) -> None:
    versions = summary["versions_tested"]
    print(f"Tier discrimination matrix ({len(versions)} reasoner versions)")
    print("=" * 70)
    header = "test".ljust(16) + " | " + " | ".join(v[:12] for v in versions)
    print(header)
    print("-" * len(header))
    for test_name, row in summary["matrix"].items():
        line = test_name.ljust(16) + " | " + " | ".join(
            row.get(v, "n/a")[:12].ljust(12) for v in versions
        )
        print(line)
    print()
    print("Diagnosis:")
    for test_name, d in summary["diagnosis"].items():
        print(f"  {test_name.ljust(16)}: {d['status']} (pass={d['passes']} fail={d['fails']})")
    if summary["bootstrap_overreach"]:
        print()
        print(f"ANOMALY: bootstrap reasoner PASSES tier-R2+ tests: "
              f"{summary['bootstrap_overreach']}")
        print("  -> these tests do not discriminate R2 from baseline; harden them.")
    print()
    print(f"anomaly_detected = {summary['anomaly_detected']}")


if __name__ == "__main__":
    s = run_calibration()
    _print_matrix(s)
