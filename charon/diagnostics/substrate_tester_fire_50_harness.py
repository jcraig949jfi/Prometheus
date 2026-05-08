"""Substrate-Tester Fire #50 harness — investigates fire #49 frozen-mutation puzzle.

Fire #49 Lane 16 mutation-testing on sigma_kernel/method_spec.py
surfaced 8/10 surviving mutations, including 3 frozen=True->False
flips (lines 80, 151, 262) that test_frozen_invariance.py's
auto-enrollment audit SHOULD HAVE caught but didn't.

Fire #50 diagnoses the cause + ships a fix:

Lane 1 — root-cause diagnosis: read test_frozen_invariance.py's
_is_frozen_dataclass filter; trace why mutated classes drop out of
enrollment; manually flip + run audit to confirm silent pass.

Lane 2 — fix: ship sigma_kernel/tests/test_frozen_baseline_manifest.py
with explicit baseline manifest of expected-frozen classes. Test
asserts each manifest entry has frozen=True directly. Catches flips
the auto-enrollment misses.

Outputs:
  charon/diagnostics/substrate_tester_fire_50_results.json
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict

REPO = Path("F:/Prometheus")


def lane_1_diagnosis() -> Dict[str, Any]:
    """Confirm the root cause: with frozen=True->False mutations applied
    to method_spec.py, test_frozen_invariance.py audit silently passes."""
    method_spec = REPO / "sigma_kernel" / "method_spec.py"
    src = method_spec.read_text(encoding="utf-8")
    backup = src
    mutated = re.sub(r"@dataclass\(frozen=True\)", "@dataclass(frozen=False)", src)
    n_flips = mutated.count("@dataclass(frozen=False)") - src.count("@dataclass(frozen=False)")

    import sys as _sys
    try:
        method_spec.write_text(mutated, encoding="utf-8")
        proc = subprocess.run(
            [_sys.executable, "-m", "pytest",
             "sigma_kernel/tests/test_frozen_invariance.py",
             "-q", "--no-header"],
            cwd=str(REPO), capture_output=True, text=True, timeout=120,
        )
        audit_passed_under_mutation = (proc.returncode == 0)
        audit_summary = ""
        for line in proc.stdout.splitlines():
            if " passed" in line or " failed" in line or " error" in line:
                audit_summary = line.strip()
    finally:
        method_spec.write_text(backup, encoding="utf-8")

    return {
        "lane": "1_diagnosis",
        "n_frozen_flips_applied": n_flips,
        "audit_passed_under_mutation": audit_passed_under_mutation,
        "audit_summary_under_mutation": audit_summary,
        "root_cause": (
            "test_frozen_invariance._is_frozen_dataclass filters "
            "for cls.__dataclass_params__.frozen is True. Mutated "
            "classes (frozen=False) drop out of enrollment, so the "
            "audit only walks classes that ARE frozen and asserts "
            "they STAY frozen. Mutation never reaches the assertion."
        ),
        "verdict": "DIAGNOSIS_CONFIRMED" if audit_passed_under_mutation else "DIAGNOSIS_REJECTED",
    }


def lane_2_ship_baseline_manifest_fix() -> Dict[str, Any]:
    """Verify the ship: test_frozen_baseline_manifest.py exists +
    passes baseline + catches the same mutation that audit silently
    accepted."""
    target = REPO / "sigma_kernel" / "tests" / "test_frozen_baseline_manifest.py"
    if not target.exists():
        return {"lane": "2_ship_baseline_manifest_fix", "verdict": "FAIL",
                "reason": "manifest test file missing"}

    import sys as _sys

    # Step 1: baseline pass
    proc1 = subprocess.run(
        [_sys.executable, "-m", "pytest",
         "sigma_kernel/tests/test_frozen_baseline_manifest.py",
         "-q", "--no-header"],
        cwd=str(REPO), capture_output=True, text=True, timeout=120,
    )
    baseline_summary = ""
    for line in proc1.stdout.splitlines():
        if " passed" in line or " failed" in line:
            baseline_summary = line.strip()

    # Step 2: catches mutation
    method_spec = REPO / "sigma_kernel" / "method_spec.py"
    src = method_spec.read_text(encoding="utf-8")
    backup = src
    mutated = re.sub(r"@dataclass\(frozen=True\)", "@dataclass(frozen=False)", src)
    try:
        method_spec.write_text(mutated, encoding="utf-8")
        proc2 = subprocess.run(
            [_sys.executable, "-m", "pytest",
             "sigma_kernel/tests/test_frozen_baseline_manifest.py",
             "-q", "--no-header"],
            cwd=str(REPO), capture_output=True, text=True, timeout=120,
        )
        manifest_caught_mutation = (proc2.returncode != 0)
        mutation_summary = ""
        for line in proc2.stdout.splitlines():
            if " passed" in line or " failed" in line:
                mutation_summary = line.strip()
    finally:
        method_spec.write_text(backup, encoding="utf-8")

    return {
        "lane": "2_ship_baseline_manifest_fix",
        "manifest_path": str(target.relative_to(REPO)).replace("\\", "/"),
        "baseline_pass_summary": baseline_summary,
        "baseline_passes": proc1.returncode == 0,
        "manifest_caught_mutation": manifest_caught_mutation,
        "mutation_failure_summary": mutation_summary,
        "verdict": "PASS" if (proc1.returncode == 0 and manifest_caught_mutation) else "FAIL",
        "fix_design": (
            "EXPECTED_FROZEN_CLASSES manifest = 12 qualified class names. "
            "Parametrized test asserts each cls.__dataclass_params__.frozen "
            "is True directly. Mutation that flips the flag fails the "
            "assertion. Manifest is hand-maintained — adding a new "
            "frozen dataclass requires an append to the list (forces "
            "explicit substrate-design intent)."
        ),
    }


def run() -> Dict[str, Any]:
    summary = {
        "fire": 50,
        "posture": "investigation + fix (closes fire #49 frozen-mutation puzzle)",
        "lanes": [1, 2],
        "lane_1": lane_1_diagnosis(),
        "lane_2": lane_2_ship_baseline_manifest_fix(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_50_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 1 (diagnosis): {summary['lane_1']['verdict']}")
    print(f"  audit passed under {summary['lane_1']['n_frozen_flips_applied']} flips: {summary['lane_1']['audit_passed_under_mutation']}")
    print(f"Lane 2 (fix): {summary['lane_2']['verdict']}")
    print(f"  baseline: {summary['lane_2']['baseline_passes']} | mutation caught: {summary['lane_2']['manifest_caught_mutation']}")
    return summary


if __name__ == "__main__":
    run()
