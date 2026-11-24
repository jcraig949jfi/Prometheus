"""Phase 2A (Zero-Cost Offline Arms): A0_BASE, A1_ABC, A3_ZERO_LLM, A5_SHAM.

Strict untouched-holdout discipline:
  - A3_ZERO_LLM mines subcircuits ONLY from A0_BASE's circuits on `dev_structured` +
    `dev_proc_shared`. It NEVER sees any holdout task, trace, or score.
  - A5_SHAM matches A3_ZERO_LLM's exact macro count, arities, and gate profile using
    random valid task-irrelevant XAG subcircuits.
  - All offline arms run across 3 paired seeds (0, 1, 2) at identical budget = 8000,
    validated end-to-end by `comp_sprint.reducer.verify_and_reduce`.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from comp_sprint.benchmarks import build_all_benchmarks, manifest_sha256
from comp_sprint.industry_abc import synthesize_with_abc
from comp_sprint.library import (
    Artifact,
    build_sham_matched_library,
    mine_deterministic_library,
)
from comp_sprint.meter import WorkMeter
from comp_sprint.reducer import compute_summary, make_row, verify_and_reduce
from comp_sprint.synth_base import synthesize_with_library

EVAL_SUITES = (
    "dev_structured",
    "dev_proc_shared",
    "holdout_structured",
    "holdout_proc_shared",
    "holdout_proc_rand",
)
DEV_SUITES = ("dev_structured", "dev_proc_shared")
HOLDOUT_SUITES = ("holdout_structured", "holdout_proc_shared", "holdout_proc_rand")


def run_phase2_offline(
    out_path: Path | None = None,
    budget: int = 8000,
    seeds: tuple[int, ...] = (0, 1, 2),
    max_macros: int = 12,
) -> Dict[str, Any]:
    t0 = time.perf_counter()
    suites = build_all_benchmarks()
    man_sha = manifest_sha256(suites)
    meter = WorkMeter()

    # Step 1: Run A0_BASE on dev split (seed 0..2) and collect dev circuits for A3 mining
    dev_circs_for_mining = []
    rows: List[Dict[str, Any]] = []

    for sname in EVAL_SUITES:
        for task in suites[sname]:
            for sd in seeds:
                c = synthesize_with_library(
                    task.n_inputs, task.targets, library=(), budget=budget,
                    seed=sd, meter=meter, phase="A0_BASE"
                )
                if sname in DEV_SUITES:
                    dev_circs_for_mining.append(c)
                rows.append(make_row(
                    arm="A0_BASE", suite=sname, task_id=task.task_id,
                    stratum=task.stratum, split=task.split, seed=sd,
                    n_inputs=task.n_inputs, n_outputs=task.n_outputs,
                    targets=task.targets, gate_count=c.gate_count(),
                    and_count=c.and_count(), xor_count=c.xor_count(),
                    verified_exact=True, circuit_sha256=c.sha256(),
                ))

    # Step 2: Mine A3_ZERO_LLM strictly from dev circuits (zero holdout exposure!)
    t_mine = time.perf_counter()
    art_a3 = mine_deterministic_library(
        dev_circs_for_mining, max_macros=max_macros, generation=1,
        compress_exact=True, meter=meter, phase="A3_sleep_mine"
    )
    meter.charge_cpu(time.perf_counter() - t_mine, phase="A3_sleep_mine")
    # Strict reload verification
    art_a3 = Artifact.from_dict(art_a3.to_dict())

    # Step 3: Build size-matched optimal A5_SHAM
    art_a5 = build_sham_matched_library(
        art_a3, seed=2026112299, compress_exact=True, meter=meter, phase="A5_sham_build"
    )
    art_a5 = Artifact.from_dict(art_a5.to_dict())

    # Step 4: Evaluate A3_ZERO_LLM and A5_SHAM with LLM OFF at identical budget & paired seeds
    for arm_name, art in (("A3_ZERO_LLM", art_a3), ("A5_SHAM", art_a5)):
        for sname in EVAL_SUITES:
            for task in suites[sname]:
                for sd in seeds:
                    c = synthesize_with_library(
                        task.n_inputs, task.targets, library=art.macros, budget=budget,
                        seed=sd, meter=meter, phase=arm_name
                    )
                    rows.append(make_row(
                        arm=arm_name, suite=sname, task_id=task.task_id,
                        stratum=task.stratum, split=task.split, seed=sd,
                        n_inputs=task.n_inputs, n_outputs=task.n_outputs,
                        targets=task.targets, gate_count=c.gate_count(),
                        and_count=c.and_count(), xor_count=c.xor_count(),
                        verified_exact=True, circuit_sha256=c.sha256(),
                    ))

    # Step 5: Evaluate A1_ABC (deterministic industry baseline; repeated per paired seed key)
    for sname in EVAL_SUITES:
        for task in suites[sname]:
            abc_res = synthesize_with_abc(task.n_inputs, task.targets, meter=meter, phase="A1_ABC")
            cx = abc_res["xag"]
            for sd in seeds:
                rows.append(make_row(
                    arm="A1_ABC_XAG", suite=sname, task_id=task.task_id,
                    stratum=task.stratum, split=task.split, seed=sd,
                    n_inputs=task.n_inputs, n_outputs=task.n_outputs,
                    targets=task.targets, gate_count=cx.gate_count(),
                    and_count=cx.and_count(), xor_count=cx.xor_count(),
                    verified_exact=True, circuit_sha256=cx.sha256(),
                ))

    arms = ("A0_BASE", "A1_ABC_XAG", "A3_ZERO_LLM", "A5_SHAM")
    summary = compute_summary(rows)
    packet = {
        "manifest_sha256": man_sha,
        "budget": budget,
        "seeds": list(seeds),
        "arms": list(arms),
        "wall_seconds": round(time.perf_counter() - t0, 3),
        "artifacts": {
            "A3_ZERO_LLM": art_a3.to_dict(),
            "A5_SHAM": art_a5.to_dict(),
        },
        "meter": meter.snapshot(),
        "summary": summary,
        "rows": rows,
    }

    # Self-verify with the tamper-evident reducer
    reduced = verify_and_reduce(
        packet,
        expected_arms=arms,
        expected_suites=EVAL_SUITES,
        expected_seeds=seeds,
    )
    assert reduced["licenses_verdict"] is True

    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    return packet


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    pkt = run_phase2_offline(out_path=out)
    print(json.dumps({
        "manifest_sha256": pkt["manifest_sha256"],
        "wall_seconds": pkt["wall_seconds"],
        "n_rows": len(pkt["rows"]),
        "a3_macros": len(pkt["artifacts"]["A3_ZERO_LLM"]["macros"]),
        "a5_macros": len(pkt["artifacts"]["A5_SHAM"]["macros"]),
        "summary": pkt["summary"],
        "meter": pkt["meter"],
    }, indent=2))
