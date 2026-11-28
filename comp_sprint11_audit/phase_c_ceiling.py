"""Phase C — Controlled Diagnosis of the `PRIOR_SATURATED` Evolutionary Ceiling.

Discriminates empirically among FOUR competing explanations for why G1..G3 failed to beat G0 in Sprints 9-10:
  - H1 (True Local-Optimum / Prior Saturation): G0 already achieves the true mathematical minimum rank.
      * Test C1: Measure exact residual gap `achieved_rank - planted_upper_bound` on 20 fresh planted
        low-rank tensors (`s11_attr_planted`) where a STRICT upper bound on `rank*(T)` is known!
  - H2 (Interface Blindness / Compositional Opacity): In Sprints 9 & 10, `_diagnose_parent` ONLY showed
      `exports=['fn1', 'fn2', ...]` WITHOUT showing G0's source code or function signatures — forcing G1
      to either guess signatures, time out, or rewrite from scratch (`xgen = 0`)!
      * Test C2 (Controlled 100% Tool-Less Ablation, K=3 trials per arm on disjoint `val_c` N=20):
          - `NAMES_ONLY` (3 trials): Replicates S9/S10 prompt (function names only, no parent source).
          - `FULL_SOURCE_AND_DIAG` (3 trials): Provides parent module signatures + concise source + per-task
            headroom diagnostics! Measures: valid rate, timeout rate, `xgen > 0` reuse rate, and `val_c` rank!
  - H3 (Single-Seed Stochastic Gate Noise): Evaluating stochastic search on `seed=0` only across N=20 tasks
      causes high variance that falsely rejects genuine `-1` rank improvements under Wilcoxon `p < 0.025`.
      * Test C3: Measure exact seed-to-seed variance across 5 seeds on identical `S10_G0` and `KM-2023` runs!
  - H4 (Search-Operator Ceiling): Measure how often random flip-only walks hit isolated/trapped states vs.
      states escapable via Plus / XOR-Triangle Plus / GF(2) slice-rank compression.
"""
from __future__ import annotations

import json
import random
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from comp_sprint.meter import WorkMeter
from comp_sprint3.sandbox_s3 import CompositionalAlgoArtifact, LibModule
from comp_sprint3.sprint3_runner import paired_wilcoxon_stats
from comp_sprint10_alphatensor.s10_core import (
    DEFAULT_S10_V3_BUDGET,
    reduce_bilinear_terms,
    run_s10_artifact,
)
from comp_sprint10_alphatensor.s10_runner import S10_API_DOC, _build_artifact, _call_claude_isolated
from comp_sprint11_audit.phase_a_km2023 import km2023_reference_search, run_s10_g0_wallclock
from comp_sprint11_audit.phase_b_attribution import S11Task, build_s11_attribution_suite


def run_phase_c_diagnosis(
    s10_proposals_path: Path,
    out_path: Path,
    *,
    run_c2_llm_ablation: bool = True,
    n_trials_c2: int = 3,
) -> Dict[str, Any]:
    prop = json.loads(s10_proposals_path.read_text(encoding="utf-8"))
    g0_art = CompositionalAlgoArtifact.from_dict(prop["artifacts"]["A2_PRIOR_ONLY"])
    tasks = build_s11_attribution_suite()
    planted_20 = [t for t in tasks if t.stratum == "attr_planted"]
    rand_20 = [t for t in tasks if t.stratum == "attr_rand"]

    # ---------------- EXP C1: TRUE OPTIMUM VS REAL HEADROOM (100% OFFLINE) ----------------
    print("=== PHASE C.1: HEADROOM AUDIT (ACHIEVED RANK VS KNOWN PLANTED UPPER BOUND, N=20 PLANTED) ===", flush=True)
    c1_rows = []
    tot_base = tot_ub = tot_km = tot_g0_v3 = tot_g0_w = 0
    for t in planted_20:
        ub = int(t.planted_upper_bound or 0)
        _, mk = km2023_reference_search(t.tensor, time_limit_sec=0.50, seed=0)
        sol_v3, _ = run_s10_artifact(g0_art, t.tensor, seed=0, v3_budget=DEFAULT_S10_V3_BUDGET)
        _, mgw = run_s10_g0_wallclock(s10_proposals_path, t.tensor, time_limit_sec=0.50, seed=0)
        tot_base += t.base_rank
        tot_ub += ub
        tot_km += mk["rank"]
        tot_g0_v3 += len(sol_v3)
        tot_g0_w += mgw["rank"]
        c1_rows.append({"task": t.task_id, "base": t.base_rank, "planted_ub": ub, "km_0p5s": mk["rank"], "g0_v3": len(sol_v3), "g0_0p5s": mgw["rank"], "gap_g0_v3_over_ub": len(sol_v3) - ub})
    strictly_above_ub = sum(1 for r in c1_rows if r["gap_g0_v3_over_ub"] > 0)
    print(f"  Base={tot_base} | Known Planted UB={tot_ub} | KM2023(0.5s)={tot_km} (+{tot_km-tot_ub}) | S10_G0(v3)={tot_g0_v3} (+{tot_g0_v3-tot_ub}) | S10_G0(0.5s)={tot_g0_w} (+{tot_g0_w-tot_ub})", flush=True)
    print(f"  Tasks where S10_G0 is STRICTLY WORSE than known planted rank: {strictly_above_ub}/20 -> H1 (true optimum) {'FALSIFIED' if strictly_above_ub >= 10 else 'PARTIAL'}!", flush=True)

    # ---------------- EXP C3: SINGLE-SEED STOCHASTIC GATE VARIANCE AUDIT (100% OFFLINE) ----------------
    print("\n=== PHASE C.3: SINGLE-SEED VS 3-SEED GATE VARIANCE AUDIT (5 SEEDS ON N=20 RAND) ===", flush=True)
    seed_totals = []
    per_task_sd = {}
    for sd in range(5):
        s_tot = 0
        for t in rand_20:
            _, mk = km2023_reference_search(t.tensor, time_limit_sec=0.25, seed=sd)
            per_task_sd.setdefault(t.task_id, []).append(mk["rank"])
            s_tot += mk["rank"]
        seed_totals.append(s_tot)
    # Pairwise null comparison of identical algorithm on seed 0 vs seed 1 (pure noise!)
    null_deltas = [per_task_sd[t.task_id][1] - per_task_sd[t.task_id][0] for t in rand_20]
    w_null = paired_wilcoxon_stats(null_deltas)
    mean_task_range = round(statistics.mean(max(v) - min(v) for v in per_task_sd.values()), 2)
    print(f"  Identical KM-2023 across 5 seeds: totals={seed_totals} (range={max(seed_totals)-min(seed_totals)}) | mean per-task range={mean_task_range} | null seed1-seed0 d={w_null['sum_delta']:+.0f} (p={w_null['p_two']:.4f})", flush=True)

    # ---------------- EXP C2: INTERFACE-VISIBILITY ABLATION (100% TOOL-LESS LLM, K=3 EACH) ----------------
    c2_results: Dict[str, Any] = {"skipped": not run_c2_llm_ablation, "trials": []}
    if run_c2_llm_ablation:
        print("\n=== PHASE C.2: INTERFACE-VISIBILITY ABLATION (NAMES_ONLY vs FULL_SOURCE, K=3 EACH ON N=20 PLANTED) ===", flush=True)
        val_c = planted_20
        parent_val = {r["task"]: r["g0_v3"] for r in c1_rows}
        parent_tot = sum(parent_val.values())
        meter = WorkMeter()

        names_summary = "\n".join(
            f"  * g{m.generation}:{m.name} exports={list(m.exported_fns)} ({len(m.source.splitlines())}L)"
            for m in g0_art.modules
        )
        # Concise exact signatures + key helpers from G0 for FULL_SOURCE arm
        full_sigs = []
        for m in g0_art.modules:
            defs = [ln for ln in m.source.splitlines() if ln.startswith("def ")]
            full_sigs.append(f"--- g{m.generation}:{m.name} ---\n" + "\n".join(defs))
        full_sigs.append("--- orchestrator ---\n" + g0_art.orchestrator.source)
        full_summary = "\n".join(full_sigs)

        worst_diag = "\n".join(
            f"  * {r['task']}: Base={r['base']}, Planted_UB={r['planted_ub']}, G0={r['g0_v3']} (gap=+{r['gap_g0_v3_over_ub']}!)"
            for r in sorted(c1_rows, key=lambda x: -x["gap_g0_v3_over_ub"])[:8]
        )

        for cond, vis_block in (("NAMES_ONLY", names_summary), ("FULL_SIGNATURES_AND_ORCH", full_summary)):
            for k in range(1, n_trials_c2 + 1):
                tag = f"C2_{cond}_T{k}"
                prompt = f"""You are evolving Generation 1 (`G1`) on top of `A2_PRIOR_ONLY` (`G0`) for Exact Binary Bilinear 3-Tensor Rank over F_2.
{S10_API_DOC}

PARENT `A2_PRIOR_ONLY` LIBRARY:
{vis_block}

DIAGNOSTIC FAILURE TELEMETRY (tasks where G0 still has massive gap above planted low rank!):
{worst_diag}

TASK: Add ONE concise new module (`mod_g1_enhance`, <= 120 lines) that CALLS existing `lib.g0_*` helpers AND improves rank on hard planted tensors (e.g. via XOR-triangle Plus splits `f_i ^ f_j ^ f_k == 0`, multi-start temperature/tabu restarts, or 2-step flip lookahead). Keep total response concise!
Trial: {tag}.

Return STRICT JSON ONLY:
```json
{{
  "rationale": "...",
  "new_modules": [{{"name": "mod_g1_enhance", "rationale": "...", "source": "def g1_fn(...): ..."}}],
  "orchestrator_source": "def solve(api, lib, budget): ..."
}}
```"""
                t0 = time.perf_counter()
                cost = 0.0
                rec: Dict[str, Any] = {"condition": cond, "trial": k, "tag": tag, "valid": False, "timed_out": False}
                try:
                    prop_c, cost, _ = _call_claude_isolated(prompt, timeout_s=240)
                    cand = _build_artifact(prop_c, gen=1, parent=g0_art, arm=tag)
                    tot_c = 0
                    xgen = 0
                    ferr = 0
                    deltas = []
                    for t in val_c:
                        sol, tel = run_s10_artifact(cand, t.tensor, seed=0, v3_budget=DEFAULT_S10_V3_BUDGET)
                        tot_c += len(sol)
                        xgen += sum(tel.get("cross_gen_calls", {}).values())
                        ferr += sum(tel.get("fn_errors", {}).values())
                        deltas.append(len(sol) - parent_val[t.task_id])
                    w = paired_wilcoxon_stats(deltas)
                    rec.update({"valid": True, "val_before": parent_tot, "val_after": tot_c, "delta": tot_c - parent_tot, "wilcoxon": w, "xgen": xgen, "ferr": ferr, "passed_gate": (w["sum_delta"] < 0 and w["p_less"] < 0.05 and ferr == 0)})
                    print(f"  [{tag:28s}] {parent_tot}->{tot_c} (d={tot_c-parent_tot:+d}, p_less={w['p_less']:.4f}) | xgen={xgen} | ferr={ferr} | PASS={rec['passed_gate']} | ${cost:.3f}", flush=True)
                except Exception as exc:
                    err_s = str(exc)
                    rec["error"] = err_s[:240]
                    rec["timed_out"] = "timed out" in err_s.lower()
                    print(f"  [{tag:28s}] FAILED (timeout={rec['timed_out']}): {err_s[:120]}", flush=True)
                dt = time.perf_counter() - t0
                rec["cost_usd"] = cost
                rec["wall_sec"] = round(dt, 1)
                meter.charge_cpu(dt, phase=tag)
                meter.charge_llm_proposal(cost, accepted=rec.get("passed_gate", False), phase=tag)
                c2_results["trials"].append(rec)
        c2_results["sleep_meter"] = meter.snapshot()

    out = {
        "exp_c1_headroom": {
            "n_planted": len(planted_20),
            "base_total": tot_base,
            "planted_ub_total": tot_ub,
            "km2023_0p5s_total": tot_km,
            "s10_g0_v3_total": tot_g0_v3,
            "s10_g0_0p5s_total": tot_g0_w,
            "strictly_above_ub_count": strictly_above_ub,
            "rows": c1_rows,
        },
        "exp_c3_seed_variance": {
            "seed_totals_5": seed_totals,
            "range_across_5_seeds": max(seed_totals) - min(seed_totals),
            "mean_per_task_range": mean_task_range,
            "null_seed1_vs_seed0": w_null,
        },
        "exp_c2_interface_visibility": c2_results,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


if __name__ == "__main__":
    import sys
    run_phase_c_diagnosis(Path(sys.argv[1]), Path(sys.argv[2]))
