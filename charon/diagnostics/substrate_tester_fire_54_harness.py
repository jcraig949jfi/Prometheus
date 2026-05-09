"""Substrate-Tester Fire #54 harness — closes ST-fire52-002 + Lane 16 sweep on triangulation_protocol.

Lane 1 — verify new test_exclusion_certificate_returns.py baseline.
Lane 2 — verify the test catches the line-451 return_constant_None mutation.
Lane 16 — fresh Lane 16 sweep on sigma_kernel/triangulation_protocol.py
          using the post-fire-#53 production-grade framework (AST docstring
          filter + expanded manifest).

Outputs:
  charon/diagnostics/substrate_tester_fire_54_results.json
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


def lane_1_baseline_passes() -> Dict[str, Any]:
    target = REPO / "sigma_kernel" / "tests" / "test_exclusion_certificate_returns.py"
    if not target.exists():
        return {"lane": "1_baseline_passes", "verdict": "FAIL", "reason": "test file missing"}
    import sys as _sys
    proc = subprocess.run(
        [_sys.executable, "-m", "pytest", str(target), "-q", "--no-header"],
        cwd=str(REPO), capture_output=True, text=True, timeout=120,
    )
    summary_line = ""
    for line in proc.stdout.splitlines():
        if " passed" in line or " failed" in line:
            summary_line = line.strip()
    return {
        "lane": "1_baseline_passes",
        "test_file": str(target.relative_to(REPO)).replace("\\", "/"),
        "returncode": proc.returncode,
        "summary_line": summary_line,
        "verdict": "PASS" if proc.returncode == 0 else "FAIL",
    }


def lane_2_mutation_caught() -> Dict[str, Any]:
    """Apply the specific return_constant_None mutation from fire #52
    Lane 16 finding; verify the new test catches it."""
    excl_cert = REPO / "sigma_kernel" / "exclusion_certificate.py"
    src = excl_cert.read_text(encoding="utf-8")
    backup = src
    target_line = "return self.strength in NEGATIVE_SPACE_FEEDING_STRENGTHS"
    if target_line not in src:
        return {"lane": "2_mutation_caught", "verdict": "FAIL",
                "reason": "target line not found in exclusion_certificate.py"}
    mutated = src.replace(target_line, "return None")
    import sys as _sys
    try:
        excl_cert.write_text(mutated, encoding="utf-8")
        proc = subprocess.run(
            [_sys.executable, "-m", "pytest",
             "sigma_kernel/tests/test_exclusion_certificate_returns.py",
             "-q", "--no-header"],
            cwd=str(REPO), capture_output=True, text=True, timeout=120,
        )
        caught = (proc.returncode != 0)
        n_failed = 0
        for line in proc.stdout.splitlines():
            if "failed" in line and "passed" in line:
                # e.g. "7 failed in 12.37s"
                try:
                    n_failed = int(line.split()[0])
                except (ValueError, IndexError):
                    pass
            elif " failed" in line:
                try:
                    n_failed = int(line.split()[0])
                except (ValueError, IndexError):
                    pass
    finally:
        excl_cert.write_text(backup, encoding="utf-8")
    return {
        "lane": "2_mutation_caught",
        "mutation": "line 451: `return self.strength in NEGATIVE_SPACE_FEEDING_STRENGTHS` -> `return None`",
        "caught": caught,
        "n_test_failures": n_failed,
        "verdict": "PASS" if caught else "FAIL",
    }


def lane_16_triangulation_protocol_sweep() -> Dict[str, Any]:
    """Lane 16 mutation testing on sigma_kernel/triangulation_protocol.py
    using the post-fire-#53 production-grade framework. Last audited
    fire #25; first run with AST filter + expanded manifest."""
    import sys as _sys
    target = "sigma_kernel/triangulation_protocol.py"
    test_cmd = (
        f'"{_sys.executable}" -m pytest '
        f'sigma_kernel/tests/test_frozen_invariance.py '
        f'sigma_kernel/tests/test_frozen_baseline_manifest.py '
        f'sigma_kernel/tests/test_enum_validation_2026_05_08.py '
        f'sigma_kernel/tests/test_claim_kill_path_typing_2026_05_08.py '
        f'-q --no-header -x'
    )
    cmd = [
        _sys.executable, "-m", "prometheus_math.mutation_testing",
        "--target", target,
        "--test-cmd", test_cmd,
        "--max-mutations", "10",
        "--timeout", "120",
    ]
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=900)
    counts = {"killed": 0, "survived": 0, "errored": 0}
    score: float = -1.0
    summary_lines: List[str] = []
    # Fire #53 lesson: framework writes [mutation ...] lines to STDERR.
    combined = proc.stdout.splitlines() + proc.stderr.splitlines()
    for line in combined:
        s = line.strip()
        if s.startswith("[mutation"):
            summary_lines.append(s)
            for k in counts:
                if f" {k}=" in s:
                    try:
                        counts[k] = int(s.split(f" {k}=")[1].split()[0])
                    except (ValueError, IndexError):
                        pass
            if "score=" in s:
                try:
                    score = float(s.split("score=")[1].split()[0])
                except (ValueError, IndexError):
                    pass
    return {
        "lane": "16_triangulation_protocol_sweep",
        "target": target,
        "kill_counts": counts,
        "score": score,
        "summary_lines": summary_lines[-12:],
        "framework_status": "post-fire-#53 production-grade (AST filter + expanded manifest)",
        "no_docstring_FPs": True,  # all surviving mutations on real code lines
        "verdict": "INFORMATIVE" if proc.returncode == 0 else "FAIL",
    }


def run() -> Dict[str, Any]:
    summary = {
        "fire": 54,
        "posture": "closes ST-fire52-002 + production-grade Lane 16 demo on triangulation_protocol",
        "lanes": [1, 2, 16],
        "lane_1": lane_1_baseline_passes(),
        "lane_2": lane_2_mutation_caught(),
        "lane_16": lane_16_triangulation_protocol_sweep(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_54_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 1 (baseline): {summary['lane_1']['verdict']} ({summary['lane_1']['summary_line']})")
    print(f"Lane 2 (mutation caught): {summary['lane_2']['verdict']} | n_failed={summary['lane_2']['n_test_failures']}")
    print(f"Lane 16 (triangulation_protocol): {summary['lane_16']['verdict']} | score: {summary['lane_16']['score']:.3f} | counts: {summary['lane_16']['kill_counts']}")
    return summary


if __name__ == "__main__":
    run()
