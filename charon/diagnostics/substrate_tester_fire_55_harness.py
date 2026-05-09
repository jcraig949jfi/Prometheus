"""Substrate-Tester Fire #55 harness — closes ST-fire54-002.

Lane 1 — verify new test_triangulation_protocol_returns.py baseline passes.
Lane 2 — verify each of the 4 surviving mutations from fire #54 is now caught.

Outputs:
  charon/diagnostics/substrate_tester_fire_55_results.json
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path("F:/Prometheus")


def lane_1_baseline_passes() -> Dict[str, Any]:
    target = REPO / "sigma_kernel" / "tests" / "test_triangulation_protocol_returns.py"
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


def lane_2_each_mutation_caught() -> Dict[str, Any]:
    """For each of the 4 surviving mutations from fire #54, apply,
    run new test, confirm caught."""
    tp = REPO / "sigma_kernel" / "triangulation_protocol.py"
    src = tp.read_text(encoding="utf-8")
    backup = src

    targets: List[Tuple[str, str, str]] = [
        ("line_149_return_None",
         "return INDEPENDENCE_TO_METHOD_CLASS[key]",
         "return None"),
        ("line_281_neq_flip",
         "return self.method_class == MethodClass.PROOF_BEARING",
         "return self.method_class != MethodClass.PROOF_BEARING"),
        ("line_292_eq_flip",
         "return self.method_class != MethodClass.EXPLORATORY",
         "return self.method_class == MethodClass.EXPLORATORY"),
        ("line_388_gt_flip",
         "if len(paths_tuple) < 3:",
         "if len(paths_tuple) > 3:"),
    ]
    results: List[Dict[str, Any]] = []
    import sys as _sys

    try:
        for marker, original, mutated in targets:
            if original not in src:
                results.append({
                    "marker": marker, "verdict": "TARGET_NOT_FOUND",
                    "note": "source line text changed since fire #54",
                })
                continue
            tp.write_text(src.replace(original, mutated), encoding="utf-8")
            proc = subprocess.run(
                [_sys.executable, "-m", "pytest",
                 "sigma_kernel/tests/test_triangulation_protocol_returns.py",
                 "-q", "--no-header"],
                cwd=str(REPO), capture_output=True, text=True, timeout=60,
            )
            caught = (proc.returncode != 0)
            results.append({
                "marker": marker, "verdict": "CAUGHT" if caught else "SURVIVED",
            })
    finally:
        tp.write_text(backup, encoding="utf-8")

    all_caught = all(r["verdict"] == "CAUGHT" for r in results)
    return {
        "lane": "2_each_mutation_caught",
        "n_mutations_tested": len(targets),
        "n_caught": sum(1 for r in results if r["verdict"] == "CAUGHT"),
        "results": results,
        "verdict": "PASS" if all_caught else "FAIL",
    }


def run() -> Dict[str, Any]:
    summary = {
        "fire": 55,
        "posture": "closes ST-fire54-002 (triangulation_protocol return-value gaps)",
        "lanes": [1, 2],
        "lane_1": lane_1_baseline_passes(),
        "lane_2": lane_2_each_mutation_caught(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_55_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 1 (baseline): {summary['lane_1']['verdict']} ({summary['lane_1']['summary_line']})")
    print(f"Lane 2 (mutations): {summary['lane_2']['verdict']} - {summary['lane_2']['n_caught']}/{summary['lane_2']['n_mutations_tested']} caught")
    return summary


if __name__ == "__main__":
    run()
