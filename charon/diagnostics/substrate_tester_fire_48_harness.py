"""Substrate-Tester Fire #48 harness — third pivot fire (Tier D test-suite stub).

Per fire #46 substrate_v3 stub doc + fire #47 Tier B test-suite stub:
write Tier D core test-suite (DistributionObject + StatisticalTestSpec
+ ProbabilityMeasure + PhaseTransitionThreshold + AlgorithmThresholdCert)
for Techne pickup. Completes the planned design-prep pivot.

Lane 1 — Tier D core test-suite stub.
Lane 11 — canon-fuzz pytest fresh seed 20260508_12.

Outputs:
  charon/diagnostics/substrate_tester_fire_48_results.json
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict

REPO = Path("F:/Prometheus")


def lane_1_tier_D_test_suite_stub() -> Dict[str, Any]:
    target = REPO / "sigma_kernel" / "tests" / "test_distribution_object_stub.py"
    if not target.exists():
        return {"lane": "1_tier_D_test_suite_stub", "verdict": "FAIL", "reason": "stub file missing"}

    import sys as _sys
    proc = subprocess.run(
        [_sys.executable, "-m", "pytest", str(target), "-q", "--no-header"],
        cwd=str(REPO), capture_output=True, text=True, timeout=120,
    )
    summary_line = ""
    for line in proc.stdout.splitlines():
        if " skipped" in line or " passed" in line or " failed" in line:
            summary_line = line.strip()

    text = target.read_text(encoding="utf-8")
    n_lines = text.count("\n")
    n_test_classes = text.count("class Test")
    n_test_methods = text.count("    def test_")

    return {
        "lane": "1_tier_D_test_suite_stub",
        "target_path": str(target.relative_to(REPO)).replace("\\", "/"),
        "filed": True,
        "n_lines": n_lines,
        "n_test_classes": n_test_classes,
        "n_test_methods": n_test_methods,
        "pytest_collect_summary": summary_line,
        "pytest_returncode": proc.returncode,
        "design_coverage": [
            "DistributionObject contract (5 tests: parametric instantiation gaussian + spike model, seeded reproducibility, registry collision, content-addressed ID)",
            "StatisticalTestSpec (3 tests: known-test registry, run returns p-value, below-sample-size raises)",
            "ProbabilityMeasure / RandomVariable (2 tests: Lebesgue construction, pushforward)",
            "GenericityAlmostEverywhereCert specialization (1 test: fire #45 refinement)",
            "PhaseTransitionThreshold (3 tests: construction, classify regime, dual-threshold gap region)",
            "AlgorithmThresholdCert (2 tests: fields + MethodSpec consistency)",
            "TierDIntegration smoke (1 test: distribution + threshold + cert reference same parameter_axis)",
        ],
        "verdict": "PASS" if proc.returncode == 0 else "FAIL",
    }


def lane_11_canon_fuzz_smoke() -> Dict[str, Any]:
    seed = "20260508_12"
    import sys as _sys
    cmd = [
        _sys.executable, "-m", "pytest",
        "prometheus_math/tests/test_canonicalization_fuzz.py",
        "-q", "--no-header", "-x", f"--hypothesis-seed={seed}",
    ]
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=240)
    summary_line = ""
    for line in proc.stdout.splitlines():
        if " passed" in line or " failed" in line or " error" in line:
            summary_line = line.strip()
    return {
        "lane": "11_canon_fuzz_smoke", "seed": seed,
        "returncode": proc.returncode, "summary_line": summary_line,
        "verdict": "PASS" if proc.returncode == 0 else "FAIL",
    }


def run() -> Dict[str, Any]:
    summary = {
        "fire": 48,
        "posture": "third-pivot-fire (Tier D core test-suite stub; design-prep pivot complete)",
        "lanes": [1, 11],
        "lane_1": lane_1_tier_D_test_suite_stub(),
        "lane_11": lane_11_canon_fuzz_smoke(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_48_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 1: {summary['lane_1']['verdict']} - "
          f"{summary['lane_1']['n_test_classes']} classes, "
          f"{summary['lane_1']['n_test_methods']} tests, "
          f"{summary['lane_1']['pytest_collect_summary']}")
    print(f"Lane 11: {summary['lane_11']['verdict']} ({summary['lane_11']['summary_line']})")
    return summary


if __name__ == "__main__":
    run()
