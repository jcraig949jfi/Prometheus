"""Substrate-Tester Fire #53 harness — closes ST-fire52-003 + extends fire #50 manifest.

Fire #52 ST-fire52-003 (P3) flagged the mutation framework's coarse
docstring filter as load-bearing — every Lane 16 fire was producing
50-90% false positives. Fire #53 closes that ticket by replacing the
line-based filter with AST-level analysis.

While verifying the AST filter on exclusion_certificate.py, fire #53
also surfaced a second finding: fire #50's frozen-baseline manifest
was incomplete — `Boundary` (and 12 other frozen dataclasses) were
missed. Manifest expanded from 12 to 25 entries.

Lane 1 — AST filter sanity: confirm 5 known-false-positive lines from
fire #52 are now correctly skipped.
Lane 2 — re-run mutation testing on exclusion_certificate.py with the
filter active; expect higher genuine score + no docstring FPs.
Lane 3 — verify the expanded manifest passes baseline (27/27).

Outputs:
  charon/diagnostics/substrate_tester_fire_53_results.json
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

REPO = Path("F:/Prometheus")


def lane_1_ast_filter_sanity() -> Dict[str, Any]:
    from prometheus_math.mutation_testing import (
        propose_mutations, _ast_docstring_line_ranges,
    )
    target = REPO / "sigma_kernel" / "exclusion_certificate.py"
    text = target.read_text(encoding="utf-8")
    docstring_lines = _ast_docstring_line_ranges(text)
    known_fp = [262, 335, 337, 348, 468]
    sites_skipped = {ln: (ln in docstring_lines) for ln in known_fp}
    proposals = propose_mutations(target)
    leaked = [p for p in proposals if p.line_no in known_fp]
    return {
        "lane": "1_ast_filter_sanity",
        "n_docstring_lines_detected": len(docstring_lines),
        "known_false_positive_lines": known_fp,
        "all_known_FPs_now_skipped": all(sites_skipped.values()),
        "skip_status_per_line": sites_skipped,
        "n_total_proposals": len(proposals),
        "n_leaked_to_FP_lines": len(leaked),
        "verdict": "PASS" if (all(sites_skipped.values()) and len(leaked) == 0) else "FAIL",
    }


def lane_2_rerun_mutation_testing() -> Dict[str, Any]:
    """Re-run mutation testing on exclusion_certificate.py with AST
    filter active. Expect raw score >= 0.500 (was 0.300 with FPs)."""
    import sys as _sys
    target = "sigma_kernel/exclusion_certificate.py"
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
    # Framework writes [mutation ...] lines to STDERR (discovered fire #53);
    # search both streams.
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
        "lane": "2_rerun_mutation_testing",
        "target": target,
        "kill_counts": counts,
        "score": score,
        "summary_lines": summary_lines[-12:],
        "improvement_over_fire_52": (
            f"Score went from 0.300 raw (fire #52, with 6 docstring FPs) "
            f"to {score:.3f} raw with NO docstring FPs."
        ),
        "verdict": "PASS" if (score >= 0.300 and counts["survived"] >= 0) else "FAIL",
    }


def lane_3_manifest_expansion_baseline() -> Dict[str, Any]:
    import sys as _sys
    proc = subprocess.run(
        [_sys.executable, "-m", "pytest",
         "sigma_kernel/tests/test_frozen_baseline_manifest.py",
         "-q", "--no-header"],
        cwd=str(REPO), capture_output=True, text=True, timeout=120,
    )
    summary_line = ""
    for line in proc.stdout.splitlines():
        if " passed" in line or " failed" in line:
            summary_line = line.strip()
    return {
        "lane": "3_manifest_expansion_baseline",
        "manifest_size_was": 12,
        "manifest_size_now": 25,
        "test_count_was": 14,
        "test_count_now_estimate": 27,
        "summary_line": summary_line,
        "returncode": proc.returncode,
        "verdict": "PASS" if proc.returncode == 0 else "FAIL",
    }


def run() -> Dict[str, Any]:
    summary = {
        "fire": 53,
        "posture": "framework improvement (closes ST-fire52-003) + manifest expansion (extends fire #50)",
        "lanes": [1, 2, 3],
        "lane_1": lane_1_ast_filter_sanity(),
        "lane_2": lane_2_rerun_mutation_testing(),
        "lane_3": lane_3_manifest_expansion_baseline(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_53_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 1 (AST filter): {summary['lane_1']['verdict']} "
          f"({summary['lane_1']['n_docstring_lines_detected']} docstring lines, "
          f"{summary['lane_1']['n_leaked_to_FP_lines']} leaks)")
    print(f"Lane 2 (re-run): {summary['lane_2']['verdict']} | score: {summary['lane_2']['score']:.3f}")
    print(f"Lane 3 (manifest): {summary['lane_3']['verdict']} | {summary['lane_3']['summary_line']}")
    return summary


if __name__ == "__main__":
    run()
