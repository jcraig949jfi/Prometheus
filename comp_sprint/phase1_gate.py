"""Phase 1 Qualification & Non-Saturation Gate:
Runs A0 (BASE, 3 seeds) vs A1 (INDUSTRY: Berkeley ABC) across all 50 benchmark tasks,
checks Order-2 multi-output sharing demand, and emits the sealed Phase 1 receipt.
"""
from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path
from typing import Dict, List

from comp_sprint.benchmarks import BenchmarkTask, build_all_benchmarks, manifest_sha256
from comp_sprint.industry_abc import synthesize_with_abc
from comp_sprint.meter import WorkMeter
from comp_sprint.synth_base import synthesize_with_library


def run_phase1_gate(
    out_path: Path | None = None,
    base_budget: int = 8000,
    seeds: tuple[int, ...] = (0, 1, 2),
) -> Dict[str, object]:
    t0 = time.perf_counter()
    suites = build_all_benchmarks()
    man_sha = manifest_sha256(suites)
    meter = WorkMeter()

    rows: List[Dict[str, object]] = []
    by_suite: Dict[str, Dict[str, float]] = {}

    for suite_name, tasks in suites.items():
        base_medians = []
        base_indep_medians = []
        abc_aigs = []
        abc_xags = []
        sharing_gains = 0

        for task in tasks:
            # A0 BASE (joint multi-output across 3 paired seeds)
            seed_gates = []
            for sd in seeds:
                c = synthesize_with_library(
                    task.n_inputs, task.targets, library=(), budget=base_budget,
                    seed=sd, meter=meter, phase="a0_base"
                )
                seed_gates.append(c.gate_count())
            base_med = float(statistics.median(seed_gates))

            # Independent per-output BASE (Order-2 sharing diagnostic: seed 0)
            indep_total = 0
            for tgt in task.targets:
                ci = synthesize_with_library(
                    task.n_inputs, (tgt,), library=(), budget=max(1500, base_budget // task.n_outputs),
                    seed=0, meter=meter, phase="a0_indep_diag"
                )
                indep_total += ci.gate_count()

            # A1 INDUSTRY (Berkeley ABC)
            abc_res = synthesize_with_abc(task.n_inputs, task.targets, meter=meter, phase="a1_abc")
            abc_aig = int(abc_res["aig_gates"])
            abc_xag = int(abc_res["xag_gates"])

            if base_med < indep_total:
                sharing_gains += 1

            base_medians.append(base_med)
            base_indep_medians.append(float(indep_total))
            abc_aigs.append(float(abc_aig))
            abc_xags.append(float(abc_xag))

            rows.append({
                "suite": suite_name,
                "task_id": task.task_id,
                "stratum": task.stratum,
                "split": task.split,
                "n_inputs": task.n_inputs,
                "n_outputs": task.n_outputs,
                "base_seed_gates": seed_gates,
                "base_median_gates": base_med,
                "base_indep_gates": indep_total,
                "abc_aig_gates": abc_aig,
                "abc_xag_gates": abc_xag,
                "headroom_vs_abc_xag": round(base_med - abc_xag, 2),
                "hidden_witness_gates": task.hidden_witness_gates,
            })

        by_suite[suite_name] = {
            "n_tasks": len(tasks),
            "base_mean_gates": round(statistics.mean(base_medians), 2),
            "base_indep_mean_gates": round(statistics.mean(base_indep_medians), 2),
            "abc_aig_mean_gates": round(statistics.mean(abc_aigs), 2),
            "abc_xag_mean_gates": round(statistics.mean(abc_xags), 2),
            "mean_gap_base_minus_abc_xag": round(
                statistics.mean(b - a for b, a in zip(base_medians, abc_xags)), 2
            ),
            "tasks_joint_beats_indep": sharing_gains,
        }

    wall_s = round(time.perf_counter() - t0, 3)
    report = {
        "manifest_sha256": man_sha,
        "base_budget": base_budget,
        "seeds": list(seeds),
        "wall_seconds": wall_s,
        "summary_by_suite": by_suite,
        "meter": meter.snapshot(),
        "rows": rows,
    }
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    rep = run_phase1_gate(out_path=out)
    print(json.dumps({
        "manifest_sha256": rep["manifest_sha256"],
        "wall_seconds": rep["wall_seconds"],
        "summary_by_suite": rep["summary_by_suite"],
    }, indent=2))
