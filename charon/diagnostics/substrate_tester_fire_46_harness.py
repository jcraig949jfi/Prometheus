"""Substrate-Tester Fire #46 harness — pivot fire (matrix-filling -> test-suite design).

Per fire #45's saturation signal + pivot proposal (ST-fire45-002), fire
#46 shifts from Lane-12 catalog probes to test-suite-design-prep.

Lane 1 (NEW: design-doc preparation) — file substrate_v3_proposal stub
doc capturing the 5-tier model from fires #38-#45.

Lane 11 — canon-fuzz pytest fresh seed 20260508_10 (regression continues).

Outputs:
  charon/diagnostics/substrate_tester_fire_46_results.json
"""
from __future__ import annotations

import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Dict

REPO = Path("F:/Prometheus")


def lane_1_v3_proposal_stub() -> Dict[str, Any]:
    """Verify the v3 stub doc was filed and report key statistics."""
    target = REPO / "pivot" / "substrate_v3_proposal_stub_2026-05-08.md"
    exists = target.exists()
    n_lines = 0
    n_chars = 0
    section_count = 0
    if exists:
        text = target.read_text(encoding="utf-8")
        n_lines = text.count("\n")
        n_chars = len(text)
        section_count = sum(1 for line in text.splitlines() if line.startswith("## "))
    return {
        "lane": "1_v3_proposal_stub_design_prep",
        "target_path": str(target.relative_to(REPO)).replace("\\", "/"),
        "filed": exists,
        "n_lines": n_lines,
        "n_chars": n_chars,
        "n_sections": section_count,
        "deliverables": [
            "5-tier model (A/B/C/D/E) with ~22 primitives catalogued",
            "Tier-by-tier specs with shape + source-fire attribution",
            "Cross-tier composition (Tier B/D) documented",
            "Recommended scope: option (c) Tier B + Tier D + partial Tier A",
            "Test-suite design hooks for fires #47/#48",
            "5 open design questions for Techne/Aporia",
            "Catalog coverage estimate (~85-95%)",
            "Coordination ticket chain catalogued",
        ],
        "verdict": "PASS" if exists else "FAIL",
    }


def lane_11_canon_fuzz_smoke() -> Dict[str, Any]:
    seed = "20260508_10"
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
        "lane": "11_canon_fuzz_smoke",
        "seed": seed,
        "returncode": proc.returncode,
        "summary_line": summary_line,
        "verdict": "PASS" if proc.returncode == 0 else "FAIL",
    }


def run() -> Dict[str, Any]:
    summary = {
        "fire": 46,
        "posture": "PIVOT FIRE — matrix-filling phase ended at fire #45 saturation; test-suite-design-prep starts here",
        "lanes": [1, 11],
        "lane_1": lane_1_v3_proposal_stub(),
        "lane_11": lane_11_canon_fuzz_smoke(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_46_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 1 (design-prep): {summary['lane_1']['verdict']} — "
          f"{summary['lane_1']['n_lines']} lines, {summary['lane_1']['n_sections']} sections")
    print(f"Lane 11: {summary['lane_11']['verdict']} ({summary['lane_11']['summary_line']})")
    return summary


if __name__ == "__main__":
    run()
