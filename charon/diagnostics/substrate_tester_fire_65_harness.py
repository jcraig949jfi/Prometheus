"""Substrate-Tester Fire #65 harness — maintenance Lane 16 on operator_portability.

First post-trilogy Lane 16 fire (fires #53/#62/#64 closed all 3 known
FP classes). Expect direct-actionable findings without per-fire FP
triage.

Lane 16 — sigma_kernel/operator_portability.py (351 LoC, substrate
v2.3 §6.3 P6 primitive bundling OperatorPortabilityCertificate +
PortabilityEvidence + PortabilityReplay).

Lane 11 — canon-fuzz pytest fresh seed 20260509_06.

Outputs:
  charon/diagnostics/substrate_tester_fire_65_results.json
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


def lane_16_operator_portability_sweep() -> Dict[str, Any]:
    import sys as _sys
    target = "sigma_kernel/operator_portability.py"
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
        "lane": "16_operator_portability_sweep",
        "target": target,
        "loc": 351,
        "framework_status": "post-trilogy production-grade (3 FP classes resolved)",
        "kill_counts": counts,
        "score": score,
        "summary_lines": summary_lines[-12:],
        "verdict": "INFORMATIVE" if proc.returncode == 0 else "FAIL",
    }


def lane_11_canon_fuzz_smoke() -> Dict[str, Any]:
    seed = "20260509_06"
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
        "fire": 65,
        "posture": "maintenance: Lane 16 on operator_portability.py (post-trilogy)",
        "lanes": [16, 11],
        "lane_16": lane_16_operator_portability_sweep(),
        "lane_11": lane_11_canon_fuzz_smoke(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_65_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 16: {summary['lane_16']['verdict']} | "
          f"score: {summary['lane_16']['score']:.3f} | counts: {summary['lane_16']['kill_counts']}")
    print(f"Lane 11: {summary['lane_11']['verdict']} ({summary['lane_11']['summary_line']})")
    return summary


if __name__ == "__main__":
    run()
