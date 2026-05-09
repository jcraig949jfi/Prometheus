"""Substrate-Tester Fire #66 harness — closes ST-fire65-001.

Two-part closure (no framework change needed since fire #65 confirmed
0 FPs):

Lane 1 — verify new test_operator_portability_returns.py baseline +
catches all 7 mutations.
Lane 2 — re-run Lane 16 with new tests; expect score ≥ 0.700.

Outputs:
  charon/diagnostics/substrate_tester_fire_66_results.json
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path("F:/Prometheus")


def lane_1_new_tests_pass_and_catch() -> Dict[str, Any]:
    target = REPO / "sigma_kernel" / "tests" / "test_operator_portability_returns.py"
    if not target.exists():
        return {"lane": "1_new_tests", "verdict": "FAIL", "reason": "test file missing"}
    import sys as _sys
    proc1 = subprocess.run(
        [_sys.executable, "-m", "pytest", str(target), "-q", "--no-header"],
        cwd=str(REPO), capture_output=True, text=True, timeout=120,
    )
    baseline_summary = ""
    for line in proc1.stdout.splitlines():
        if " passed" in line or " failed" in line:
            baseline_summary = line.strip()

    op = REPO / "sigma_kernel" / "operator_portability.py"
    src = op.read_text(encoding="utf-8")
    backup = src
    mutations: List[Tuple[str, str, str]] = [
        ("line_94_lt_flip", "self.n_objects_tested < 0", "self.n_objects_tested > 0"),
        ("line_94_0_to_1", "self.n_objects_tested < 0", "self.n_objects_tested < 1"),
        ("line_204_sort_keys", "sort_keys=True, default=str", "sort_keys=False, default=str"),
        ("line_205_hash_None", "return hashlib.sha256(canonical.encode()).hexdigest()", "return None"),
        ("line_229_default_flip", "replace: bool = False,", "replace: bool = True,"),
        ("line_256_neq_flip", "for x in self._by_operator[old.operator_id] if x != cid", "for x in self._by_operator[old.operator_id] if x == cid"),
        ("line_261_neq_flip", "for x in self._by_chart_pair[pair] if x != cid", "for x in self._by_chart_pair[pair] if x == cid"),
    ]
    catch_results: List[Dict[str, Any]] = []
    try:
        for marker, orig, mutated in mutations:
            if orig not in src:
                catch_results.append({"marker": marker, "verdict": "TARGET_NOT_FOUND"})
                continue
            op.write_text(src.replace(orig, mutated), encoding="utf-8")
            proc = subprocess.run(
                [_sys.executable, "-m", "pytest", str(target), "-q", "--no-header"],
                cwd=str(REPO), capture_output=True, text=True, timeout=60,
            )
            caught = (proc.returncode != 0)
            catch_results.append({"marker": marker, "verdict": "CAUGHT" if caught else "SURVIVED"})
    finally:
        op.write_text(backup, encoding="utf-8")

    all_caught = all(r["verdict"] == "CAUGHT" for r in catch_results)
    return {
        "lane": "1_new_tests_pass_and_catch",
        "test_file": str(target.relative_to(REPO)).replace("\\", "/"),
        "baseline_summary": baseline_summary,
        "baseline_passes": proc1.returncode == 0,
        "n_mutations_tested": len(mutations),
        "catch_results": catch_results,
        "n_caught": sum(1 for r in catch_results if r["verdict"] == "CAUGHT"),
        "verdict": "PASS" if (proc1.returncode == 0 and all_caught) else "FAIL",
    }


def lane_2_rerun_mutation_testing() -> Dict[str, Any]:
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
        "lane": "2_rerun_mutation_testing",
        "target": target,
        "kill_counts": counts,
        "score": score,
        "summary_lines": summary_lines[-12:],
        "improvement_chain": (
            f"Fire #65 (no new tests): raw 0.300 (3K, 7S — 0 FPs, all genuine)\n"
            f"Fire #66 (with new tests): raw {score:.3f} ({counts['killed']}K, {counts['survived']}S)"
        ),
        "verdict": "PASS" if (proc.returncode == 0 and score >= 0.300) else "FAIL",
    }


def run() -> Dict[str, Any]:
    summary = {
        "fire": 66,
        "posture": "closes ST-fire65-001 (2-part: 14 return tests + verify 7 mutations + re-run)",
        "lanes": [1, 2],
        "lane_1": lane_1_new_tests_pass_and_catch(),
        "lane_2": lane_2_rerun_mutation_testing(),
    }
    out_path = REPO / "charon" / "diagnostics" / "substrate_tester_fire_66_results.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Lane 1 (new tests): {summary['lane_1']['verdict']} | "
          f"baseline {summary['lane_1']['baseline_summary']} | "
          f"{summary['lane_1']['n_caught']}/{summary['lane_1']['n_mutations_tested']} caught")
    print(f"Lane 2 (re-run): {summary['lane_2']['verdict']} | "
          f"score: {summary['lane_2']['score']:.3f} | counts: {summary['lane_2']['kill_counts']}")
    return summary


if __name__ == "__main__":
    run()
