"""Substrate-Tester Fire #63 harness — maintenance Lane 16 + regression.

Lane 16 — production-grade mutation testing on
sigma_kernel/coordinate_chart.py (491 LoC; substrate v2.3 §6.2 P0
primitive bundling CanonicalizationProtocol + CoordinateChart). Fresh
module under post-#62 framework (AST docstring + string-literal
filters both active).

Lane 11 — canon-fuzz pytest fresh seed 20260509_05.

Outputs:
  charon/diagnostics/substrate_tester_fire_63_results.json
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


def lane_16_coordinate_chart_sweep() -> Dict[str, Any]:
    import sys as _sys
    target = "sigma_kernel/coordinate_chart.py"
    test_cmd = (
        f'"{_sys.executable}" -m pytest sigma_kernel/tests/ '
        f'-q --no-header -x'
    )
    cmd = [
        _sys.executable, "-m", "prometheus_math.mutation_testing",
        "--target", target,
        "--test-cmd", test_cmd,
        "--max-mutations", "10",
        "--timeout", "180",
    ]
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=1800)
    counts = {"killed": 0, "survived": 0, "errored": 0}
    score: float = -1.0
    summary_lines: List[str] = []
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
        "lane": "16_coordinate_chart_sweep",
        "target": target,
        "loc": 491,
        "framework_status": "post-fire-#62 production-grade (AST docstring + string-literal filters)",
        "kill_counts": counts,
        "score": score,
        "summary_lines": summary_lines[-12:],
        "verdict": "INFORMATIVE" if proc.returncode == 0 else "FAIL",
    }


def lane_11_canon_fuzz_smoke() -> Dict[str, Any]:
    seed = "20260509_05"
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
        "fire": 63,
        "posture": "maintenance: Lane 16 on coordinate_chart.py (substrate v2.3 P0) + canon-fuzz hygiene",
        "lanes": [16, 11],
        "lane_16": lane_16_coordinate_chart_sweep(),
        "lane_11": lane_11_canon_fuzz_smoke(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_63_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 16: {summary['lane_16']['verdict']} | "
          f"score: {summary['lane_16']['score']:.3f} | counts: {summary['lane_16']['kill_counts']}")
    print(f"Lane 11: {summary['lane_11']['verdict']} ({summary['lane_11']['summary_line']})")
    return summary


if __name__ == "__main__":
    run()
