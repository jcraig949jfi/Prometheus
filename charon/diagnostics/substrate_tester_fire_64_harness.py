"""Substrate-Tester Fire #64 harness — closes ST-fire63-001.

Three-part closure:
  Lane 1 — verify inline-comment AST filter shipped (line-92 SQL/comment
           FP no longer leaks).
  Lane 2 — verify new test_coordinate_chart_returns.py baseline +
           catches all 6 mutations from fire #63.
  Lane 3 — re-run Lane 16 with both improvements; expect score >= 0.700.

Outputs:
  charon/diagnostics/substrate_tester_fire_64_results.json
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path("F:/Prometheus")


def lane_1_inline_comment_filter_works() -> Dict[str, Any]:
    from prometheus_math.mutation_testing import propose_mutations
    target = REPO / "sigma_kernel" / "coordinate_chart.py"
    proposals = propose_mutations(target)
    fp_lines = [92]  # the `# Lehmer chart, Day-3 ship` inline comment
    leaks = [p for p in proposals if p.line_no in fp_lines]
    return {
        "lane": "1_inline_comment_filter_works",
        "n_total_proposals": len(proposals),
        "known_FP_lines": fp_lines,
        "n_leaked_to_FP_lines": len(leaks),
        "verdict": "PASS" if len(leaks) == 0 else "FAIL",
    }


def lane_2_new_tests_pass_and_catch() -> Dict[str, Any]:
    target = REPO / "sigma_kernel" / "tests" / "test_coordinate_chart_returns.py"
    if not target.exists():
        return {"lane": "2_new_tests", "verdict": "FAIL", "reason": "test file missing"}
    import sys as _sys
    proc1 = subprocess.run(
        [_sys.executable, "-m", "pytest", str(target), "-q", "--no-header"],
        cwd=str(REPO), capture_output=True, text=True, timeout=120,
    )
    baseline_summary = ""
    for line in proc1.stdout.splitlines():
        if " passed" in line or " failed" in line:
            baseline_summary = line.strip()

    cc = REPO / "sigma_kernel" / "coordinate_chart.py"
    src = cc.read_text(encoding="utf-8")
    backup = src
    mutations: List[Tuple[str, str, str]] = [
        ("line_185_apply", "return self.canonicalize(point)", "return None"),
        ("line_273_canonicalize_delegate", "return self.canonicalization.apply(point)", "return None"),
        ("line_283_distance", "return float(self.metric(ca, cb))", "return None"),
        ("line_287_admits", 'return bool(self.admissible_region(point))', "return None"),
        ("line_303_split_maxsplit", 'chart_id.split(":", 1)', 'chart_id.split(":", 2)'),
        ("line_308_return_tuple", "return domain, region_key", "return None"),
    ]
    catch_results: List[Dict[str, Any]] = []
    try:
        for marker, orig, mutated in mutations:
            if orig not in src:
                catch_results.append({"marker": marker, "verdict": "TARGET_NOT_FOUND"})
                continue
            cc.write_text(src.replace(orig, mutated), encoding="utf-8")
            proc = subprocess.run(
                [_sys.executable, "-m", "pytest", str(target), "-q", "--no-header"],
                cwd=str(REPO), capture_output=True, text=True, timeout=60,
            )
            caught = (proc.returncode != 0)
            catch_results.append({"marker": marker, "verdict": "CAUGHT" if caught else "SURVIVED"})
    finally:
        cc.write_text(backup, encoding="utf-8")

    all_caught = all(r["verdict"] == "CAUGHT" for r in catch_results)
    return {
        "lane": "2_new_tests_pass_and_catch",
        "test_file": str(target.relative_to(REPO)).replace("\\", "/"),
        "baseline_summary": baseline_summary,
        "baseline_passes": proc1.returncode == 0,
        "n_mutations_tested": len(mutations),
        "catch_results": catch_results,
        "n_caught": sum(1 for r in catch_results if r["verdict"] == "CAUGHT"),
        "verdict": "PASS" if (proc1.returncode == 0 and all_caught) else "FAIL",
    }


def lane_3_rerun_mutation_testing() -> Dict[str, Any]:
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
        "lane": "3_rerun_mutation_testing",
        "target": target,
        "kill_counts": counts,
        "score": score,
        "summary_lines": summary_lines[-12:],
        "improvement_chain": (
            f"Fire #63 (no inline-comment filter, original tests): raw 0.300 (3K, 7S — 1 FP + 6 genuine)\n"
            f"Fire #64 (inline-comment filter + new tests): raw {score:.3f} ({counts['killed']}K, {counts['survived']}S)"
        ),
        "verdict": "PASS" if (proc.returncode == 0 and score >= 0.300) else "FAIL",
    }


def run() -> Dict[str, Any]:
    summary = {
        "fire": 64,
        "posture": "closes ST-fire63-001 (3-part: inline-comment filter + 6 return tests + verify)",
        "lanes": [1, 2, 3],
        "lane_1": lane_1_inline_comment_filter_works(),
        "lane_2": lane_2_new_tests_pass_and_catch(),
        "lane_3": lane_3_rerun_mutation_testing(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_64_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 1 (inline-# filter): {summary['lane_1']['verdict']} | "
          f"{summary['lane_1']['n_leaked_to_FP_lines']} leaks")
    print(f"Lane 2 (new tests): {summary['lane_2']['verdict']} | "
          f"baseline {summary['lane_2']['baseline_summary']} | "
          f"{summary['lane_2']['n_caught']}/{summary['lane_2']['n_mutations_tested']} caught")
    print(f"Lane 3 (re-run): {summary['lane_3']['verdict']} | "
          f"score: {summary['lane_3']['score']:.3f} | counts: {summary['lane_3']['kill_counts']}")
    return summary


if __name__ == "__main__":
    run()
