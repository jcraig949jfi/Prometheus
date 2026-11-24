"""Sprint 4 Unified Checkpointed Runner — Track S4-A (16-Bit Deterministic Z3 BV, 3 Gens) & Track S4-B (9-11in XAG, 4 Gens).

Implements all three compounding laws + Matched-Op Causal Knockouts across BOTH tracks:
  - Law 1: Deterministic integer `OpBudget` + isolated Z3 Context `rlimit` (0.000 variance!).
  - Law 2: Disjoint per-generation hidden validation splits (`val_g1..val_gK`, N=20 each) +
           exact one-sided paired Wilcoxon promotion gate (`p_less < 0.05` att1 / `< 0.025` att2).
  - Law 3: Compositional `LibModule` library with cross-gen call telemetry + Matched-Op Causal
           Knockouts (routing unused op budget back to surviving parent so total ops stay matched!).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from comp_sprint.industry_abc import synthesize_with_abc
from comp_sprint.llm_proposer import call_claude_isolated
from comp_sprint.meter import WorkMeter
from comp_sprint2.phase3_compound import STRICT_JSON_SYSTEM_PROMPT
from comp_sprint2.reducer_s2 import compute_summary, make_row, verify_and_reduce
from comp_sprint2.s2b_bv import simplify_bv_with_z3_industry
from comp_sprint2.sprint2_runner import _prompt_hash
from comp_sprint3.sandbox_s3 import CompositionalAlgoArtifact, LibModule
from comp_sprint3.sprint3_runner import (
    S3_API_SPEC,
    _format_existing_library,
    _parse_compositional_proposal,
    paired_wilcoxon_stats,
)
from comp_sprint4.ko_matched import knockout_generations_generic
from comp_sprint4.s4a_bv_benchmarks import build_s4a_bv_benchmarks, s4a_manifest_sha256
from comp_sprint4.s4a_bv_engine import (
    DEFAULT_S4A_OP_BUDGET,
    build_s4a_a3_artifact,
    build_s4a_a5_sham_artifact,
    optimize_s4a_with_artifact,
)
from comp_sprint4.s4b_xag_benchmarks import build_s4b_xag_benchmarks, s4b_manifest_sha256
from comp_sprint4.s4b_xag_engine import (
    DEFAULT_S4B_OP_BUDGET,
    build_s4b_a3_artifact,
    build_s4b_a5_sham_artifact,
    synthesize_s4b_with_artifact,
)


S4A_BV_API_SPEC = """
SPRINT 4 TRACK S4-A DETERMINISTIC COMPOSITIONAL 16-BIT Z3 BV API (ZERO WALL-CLOCK, EXACT OP BUDGET):
- Goal: Minimize live primitive BV op count (`prog.op_count()`, ZERO discount; inputs & constants = 0,
  every primitive op in {NOT, NEG, AND, OR, XOR, ADD, SUB, MUL, SHL, LSHR, ASHR, ULT, EQ, ITE} = 1)
  on hard multi-stage 16-bit BV programs (5..10 op cores obfuscated to 14..34 ops) while preserving
  100% mathematical equivalence across ALL 2^(16*n_inputs) inputs via deterministic Z3 `UNSAT`!
- HARD DETERMINISM RULE: `time` is REMOVED from sandbox! Every `for`/`while`/comprehension iteration
  charges 1 op and every API/Z3 call charges deterministic ops to `budget` (limit = 60,000 ops/task).
  Z3 uses isolated deterministic `rlimit` (ZERO wall-clock jitter!). Never use `import`, dunders, or bare `except:`.
- Available stdlib: `math`, `itertools`, `collections`, `Counter`, `defaultdict`, `deque`, `heapq`, `random`.
- Available `budget` methods: `budget.remaining()`, `budget.global_remaining()`, `budget.spent`, `budget.limit`.
- Available `lib` compositional runtime:
    * Every public `def fn(...)` defined in ANY library module is exposed on `lib.<fn>(...)`.
    * `lib.run("fn_name", *args, op_cap=15000, **kwargs)` executes with a deterministic soft sub-cap.
    * Gen k modules CAN and SHOULD directly call Gen 0..k-1 helpers via `lib.<fn>(...)`!
- Available domain API (injected as globals in every module & orchestrator):
    * `BVBuilder(width, n_inputs, fold_constants=True)`: `.inp(i)`, `.const(val)`, `.op(op_name, *args)`, `.build(out_id) -> BVProgram`
    * `BVNode(op, args)`, `BVProgram` (`.width`, `.n_inputs`, `.nodes`, `.out_id`, `.op_count()`, `.eval_one(tv)`, `.eval_vectors(tvs)`, `.sha256()`)
    * `UNARY_OPS`, `BINARY_OPS`, `ALL_BV_OPS`
    * `default_test_vectors(width, n_inputs, seed=..., n_rand=...) -> Tuple[Tuple[int, ...], ...]`
    * `eval_all_nodes(prog, test_vectors) -> List[Tuple[int, ...]]` (fast concrete eval of every SSA node)
    * `replace_node(prog, target_idx, repl_prog, arg_map) -> Optional[BVProgram]` (DAG node splice)
    * `verify_equiv_z3(spec, cand) -> Tuple[bool, Optional[Tuple[int, ...]]]` (deterministic Z3 rlimit=120,000, 350 ops; returns `(True, None)` iff UNSAT, `(False, cex)` if SAT, `(False, None)` if rlimit hit!)
    * `bv_features(prog) -> dict` (`width, n_inputs, op_count, has_mul, has_ite, has_shift, n_consts`)
    * `report_best(cand) -> bool` (ALWAYS call on candidate improvements — verifies exact Z3 UNSAT and updates monotonic best!)
    * `best_solution() -> BVProgram`, `best_cost() -> int`
- Orchestrator signature MUST be:
    `def solve(prog, spec, seed, api, lib, budget):`
    returning `best_solution()`.
- IMPORTANT: Filter candidates using concrete `eval_all_nodes` / `eval_vectors` (SWAR/packed vectors!) FIRST, and only call `verify_equiv_z3` (350 ops) on concrete matches that strictly reduce `op_count()`!
"""

S4B_XAG_API_SPEC = (
    S3_API_SPEC.replace("7-to-9 input", "9-to-11 input")
    .replace("128..512-bit", "512..2048-bit")
    .replace("120,000 ops", "160,000 ops")
    + "    * `cofactor(tt, var, val) -> int` (1 op: exact Shannon cofactor of `tt` for `x_var = val`)\n"
)


def _track_cfg(track: str) -> Dict[str, Any]:
    if track == "s4a":
        suites = build_s4a_bv_benchmarks()
        return {
            "track": "s4a",
            "track_tag": "S4A_BV_COMP",
            "n_gens": 3,
            "suites": suites,
            "manifest_sha": s4a_manifest_sha256(suites),
            "op_budget": DEFAULT_S4A_OP_BUDGET,
            "api_spec": S4A_BV_API_SPEC,
            "industry_arm": "A1_Z3_SIMPLIFY",
            "passthrough_type": "BVProgram",
            "hold_suites": ("s4a_hold_struct", "s4a_hold_proc"),
            "a3_art": build_s4a_a3_artifact(),
            "a5_art": build_s4a_a5_sham_artifact(),
            "g0_prompt_hint": (
                "  - Module 1: Fast concrete vector/SWAR evaluation, subnode divisor tables, MFFC/dependency\n"
                "    analysis, and counterexample-guided equivalence filtering helpers reusable via `lib.<fn>`.\n"
                "  - Module 2: Algebraic / linear-MBA / e-graph / term-rewriting / constant-mask simplification pass.\n"
                "  - Module 3: Local sub-DAG / window / MITM resubstitution & ODC-guided replacement pass calling Module 1 via `lib.<fn>`.\n"
                "  - Orchestrator `solve(prog, spec, seed, api, lib, budget)`."
            ),
            "gen_ideas": (
                "linear/polynomial MBA Gaussian elimination over mod 2^16; bottom-up sub-DAG MITM / 2-3 op cut\n"
                "resynthesis over internal SSA nodes; observability don't-care / bit-mask known-bits propagation\n"
                "(tracking known-0/1 bits and shift ranges); ITE/ULT/EQ branch-splitting & dead-branch simplification;\n"
                "multi-node e-graph / equality-saturation rewrite loop; incremental mutable SSA rewriting."
            ),
            "orch_sig": "def solve(prog, spec, seed, api, lib, budget):",
        }
    if track == "s4b":
        suites = build_s4b_xag_benchmarks()
        return {
            "track": "s4b",
            "track_tag": "S4B_XAG_4GEN",
            "n_gens": 4,
            "suites": suites,
            "manifest_sha": s4b_manifest_sha256(suites),
            "op_budget": DEFAULT_S4B_OP_BUDGET,
            "api_spec": S4B_XAG_API_SPEC,
            "industry_arm": "A1_ABC_XAG",
            "passthrough_type": "XAGCircuit",
            "hold_suites": ("s4b_hold_struct", "s4b_hold_proc_shared", "s4b_hold_proc_comp"),
            "a3_art": build_s4b_a3_artifact(),
            "a5_art": build_s4b_a5_sham_artifact(),
            "g0_prompt_hint": (
                "  - Module 1: Reusable structural analysis / ODC / MFFC / truth-table helper primitives reusable via `lib.<fn>`.\n"
                "  - Module 2: Constructive decomposition / Davio / XOR-preconditioning pass for 9-11 input circuits.\n"
                "  - Module 3: Local ODC resubstitution / SAT-4cut / plateau walk pass calling Module 1 via `lib.<fn>`.\n"
                "  - Orchestrator `solve(circ, n_inputs, targets, seed, api, lib, budget)`."
            ),
            "gen_ideas": (
                "Ashenhurst-Curtis / disjunctive / bi-decomposition with joint multi-output column multiplicity;\n"
                "incremental mutable-netlist ODC plateau walk (updating only TFO instead of full circuit rebuild);\n"
                "Gaussian GF(2) linear input/output basis reduction & XOR-forest factoring; multi-output shared\n"
                "subcone / algebraic kernel extraction; 5-6 input window exact/SAT resynthesis; adaptive\n"
                "circuit-feature-gated budget allocation across constructive + mutable-netlist + exact-cut stages."
            ),
            "orch_sig": "def solve(circ, n_inputs, targets, seed, api, lib, budget):",
        }
    raise ValueError(f"Unknown track {track!r}")


def _eval_one(
    track: str,
    task: Any,
    art: Optional[CompositionalAlgoArtifact],
    seed: int,
    op_budget: int,
    fallback_art: Optional[CompositionalAlgoArtifact] = None,
) -> Tuple[int, str, Dict[str, Any]]:
    if track == "s4a":
        p, meta = optimize_s4a_with_artifact(task.spec, artifact=art, seed=seed, op_budget=op_budget, fallback_artifact=fallback_art)
        return p.op_count(), p.sha256(), meta
    c, meta = synthesize_s4b_with_artifact(task.n_inputs, task.targets, artifact=art, seed=seed, op_budget=op_budget, fallback_artifact=fallback_art)
    return c.gate_count(), c.sha256(), meta


def _eval_split(
    track: str,
    tasks: Sequence[Any],
    art: Optional[CompositionalAlgoArtifact],
    op_budget: int,
    seed: int = 0,
) -> Tuple[int, Dict[str, int], Dict[str, Dict[str, Any]]]:
    total = 0
    per_task: Dict[str, int] = {}
    metas: Dict[str, Dict[str, Any]] = {}
    for t in tasks:
        cost, _, meta = _eval_one(track, t, art, seed=seed, op_budget=op_budget)
        total += cost
        per_task[t.task_id] = cost
        metas[t.task_id] = meta
    return total, per_task, metas


def _summarize_telemetry(
    tasks: Sequence[Any],
    a0_costs: Dict[str, int],
    cur_costs: Dict[str, int],
    cur_metas: Dict[str, Dict[str, Any]],
    op_budget: int,
) -> str:
    rows = []
    for t in tasks:
        m = cur_metas[t.task_id]
        rows.append((
            cur_costs[t.task_id], t.task_id, t.stratum, a0_costs[t.task_id],
            m.get("ops_spent", 0), m.get("status", ""), m.get("error", ""),
            m.get("mod_gate_drops", {}), m.get("cross_gen_calls", {}), m.get("fn_error_msgs", {}),
        ))
    rows.sort(reverse=True)
    lines = ["PER-TASK TRAINING TELEMETRY (sorted by hardest residual cost):"]
    for cost, tid, strat, c0, ops, st, err, drops, xgen, ferrs in rows:
        lines.append(
            f"  - {tid} [{strat}]: cur={cost} (A0={c0}, saved={c0-cost}), "
            f"ops={ops}/{op_budget} ({st}), drops={drops}, xgen={xgen}"
            + (f", err={err}" if err else "")
            + (f", fn_errs={ferrs}" if ferrs else "")
        )
    agg_drops: Dict[str, int] = {}
    agg_xgen: Dict[str, int] = {}
    for m in cur_metas.values():
        for k, v in m.get("mod_gate_drops", {}).items():
            agg_drops[k] = agg_drops.get(k, 0) + v
        for k, v in m.get("cross_gen_calls", {}).items():
            agg_xgen[k] = agg_xgen.get(k, 0) + v
    lines.append(f"AGGREGATE MODULE DROPS: {agg_drops}")
    lines.append(f"AGGREGATE CROSS-GEN CALLS: {agg_xgen}")
    return "\n".join(lines)


def run_propose(track: str, out_path: Path, model: str = "opus", timeout_sec: int = 480) -> Dict[str, Any]:
    cfg = _track_cfg(track)
    suites = cfg["suites"]
    manifest_sha = cfg["manifest_sha"]
    op_budget = cfg["op_budget"]
    n_gens = cfg["n_gens"]
    track_tag = cfg["track_tag"]
    meter = WorkMeter()
    trace: List[Dict[str, Any]] = []
    ckpt: Dict[str, Any] = {}

    if out_path.exists():
        try:
            prev = json.loads(out_path.read_text(encoding="utf-8"))
            if prev.get("manifest_sha256") == manifest_sha:
                ckpt = prev
                trace = list(prev.get("llm_trace", []))
                print(f"[{track}] Loaded checkpoint keys={sorted(prev.get('artifacts', {}).keys())}", flush=True)
        except Exception:
            ckpt = {}

    artifacts: Dict[str, CompositionalAlgoArtifact] = {
        k: CompositionalAlgoArtifact.from_dict(d) for k, d in ckpt.get("artifacts", {}).items()
    }
    gen_records: Dict[str, Any] = dict(ckpt.get("generation_records", {}))

    def _save() -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "track": track_tag,
            "manifest_sha256": manifest_sha,
            "op_budget": op_budget,
            "n_gens": n_gens,
            "artifacts": {k: v.to_dict() for k, v in artifacts.items()},
            "generation_records": gen_records,
            "llm_trace": trace,
            "sleep_meter": meter.snapshot(),
        }
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # ---------------- GEN 0: A2_PRIOR_ONLY (ZERO TRAINING FEEDBACK!) ----------------
    if "A2_PRIOR_ONLY" not in artifacts:
        p0 = (
            f"You are designing a Compositional Executable Algorithm Library ({track_tag}, Generation 0: PRIOR-ONLY).\n"
            f"You have ZERO access to benchmark tasks or telemetry.\n"
            f"{cfg['api_spec']}\n\n"
            f"TASK (Generation 0 - Compiled Priors Only):\n"
            f"Write 3 clean, modular, reusable Python library modules (each 40-110 lines) AND 1 orchestrator:\n"
            f"{cfg['g0_prompt_hint']}\n"
            f"Output ONLY raw JSON matching:\n"
            '{"new_modules": [{"name": "mod_g0_...", "rationale": "...", "source": "def ..."}], '
            f'"orchestrator": {{"name": "orch_g0", "rationale": "...", "source": "{cfg["orch_sig"]}\\n    ..."}}}}'
        )
        t0 = time.perf_counter()
        res = call_claude_isolated(p0, model=model, timeout_sec=timeout_sec, system_prompt=STRICT_JSON_SYSTEM_PROMPT)
        cost_usd = float(res["cost_usd"])
        meter.charge_cpu(time.perf_counter() - t0, phase=f"{track}_g0_prior")
        try:
            a2_raw, errs = _parse_compositional_proposal(res["text"], generation=0, origin="A2_PRIOR_ONLY", base_modules=())
            a2 = CompositionalAlgoArtifact("A2_PRIOR_ONLY", track_tag, 0, a2_raw.modules, a2_raw.orchestrator)
            meter.charge_llm_proposal(cost_usd, accepted=True, phase=f"{track}_g0_prior")
        except Exception:
            meter.charge_llm_proposal(cost_usd, accepted=False, phase=f"{track}_g0_prior")
            raise
        artifacts["A2_PRIOR_ONLY"] = a2
        a0_v1, _, _ = _eval_split(track, suites[f"{track}_val_g1"], None, op_budget=op_budget, seed=0)
        v1_sum, _, v1_ms = _eval_split(track, suites[f"{track}_val_g1"], a2, op_budget=op_budget, seed=0)
        ferrs = sum(sum(m.get("fn_errors", {}).values()) for m in v1_ms.values())
        trace.append({
            "step": "A2_PRIOR_ONLY", "cost_usd": cost_usd, "models_used": res.get("models_used", []),
            "prompt_hash": _prompt_hash(p0), "a0_val_g1": a0_v1, "val_g1_sum": v1_sum, "fn_errors": ferrs, "parse_errors": errs,
        })
        gen_records["G0"] = {"artifact_sha256": a2.sha256(), "val_g1_sum": v1_sum, "modules": [m.name for m in a2.modules], "fn_errors": ferrs}
        print(f"[{track}] G0 A2_PRIOR_ONLY built ({len(a2.modules)} mods, val_g1 {a0_v1}->{v1_sum}, fn_errs={ferrs}, ${cost_usd:.3f})", flush=True)
        _save()

    # ---------------- GENERATIONS 1..n_gens (DISJOINT TRAIN + DISJOINT VAL GATE p<0.05) ----------------
    current = artifacts["A2_PRIOR_ONLY"]
    for gen in range(1, n_gens + 1):
        gk = f"G{gen}"
        if gk in artifacts:
            current = artifacts[gk]
            continue

        train_tasks = suites[f"{track}_train_g{gen}"]
        val_tasks = suites[f"{track}_val_g{gen}"]

        a0_tr_sum, a0_tr_costs, _ = _eval_split(track, train_tasks, None, op_budget=op_budget, seed=0)
        cur_tr_sum, cur_tr_costs, cur_tr_metas = _eval_split(track, train_tasks, current, op_budget=op_budget, seed=0)
        cur_val_sum, cur_val_costs, _ = _eval_split(track, val_tasks, current, op_budget=op_budget, seed=0)

        telem = _summarize_telemetry(train_tasks, a0_tr_costs, cur_tr_costs, cur_tr_metas, op_budget)
        lib_text = _format_existing_library(current)

        promoted = False
        best_cand: Optional[CompositionalAlgoArtifact] = None
        best_val_stats: Dict[str, Any] = {}
        attempt_logs: List[Dict[str, Any]] = []
        prior_fail_note = ""

        for attempt in (1, 2):
            p_thresh = 0.05 if attempt == 1 else 0.025
            pg = (
                f"You are evolving a Compositional Executable Algorithm Library ({track_tag}) — Generation {gen}/{n_gens} (Attempt {attempt}/2).\n"
                f"{cfg['api_spec']}\n\n"
                f"{lib_text}\n\n"
                f"GENERATION {gen} TRAINING SET (`{track}_train_g{gen}`, {len(train_tasks)} tasks; A0={a0_tr_sum}, current={cur_tr_sum}):\n"
                f"{telem}\n\n"
                f"{prior_fail_note}"
                f"COMPOSITIONAL EVOLUTION OBJECTIVE (Generation {gen}):\n"
                f"1. DO NOT rewrite or duplicate existing Gen 0..{gen-1} modules — they remain intact in `lib`!\n"
                f"2. Write 1-2 NEW reusable Gen {gen} module(s) that DIRECTLY COMPOSE ON TOP OF existing `lib.<fn>(...)` helpers\n"
                f"   to attack genuine algorithmic/representation bottlenecks visible in the telemetry above (across BOTH\n"
                f"   structured AND 100% procedural tasks — NEVER hardcode task names!).\n"
                f"   High-leverage compositional ideas: {cfg['gen_ideas']}\n"
                f"3. Provide an updated `orchestrator` (`{cfg['orch_sig']}`) preserving all winning Gen 0..{gen-1} strengths\n"
                f"   and integrating your Gen {gen} module(s) with adaptive deterministic `op_cap` budgeting.\n"
                f"4. PROMOTION GATE (Law 2): Evaluated on a HIDDEN disjoint {len(val_tasks)}-task validation split (`{track}_val_g{gen}`).\n"
                f"   Promoted ONLY IF net cost < 0 AND exact paired Wilcoxon `p_less < {p_thresh}`!\n"
                f"Output ONLY raw JSON matching:\n"
                '{"new_modules": [{"name": "mod_g' + str(gen) + '_...", "rationale": "...", "source": "def ..."}], '
                f'"orchestrator": {{"name": "orch_g{gen}", "rationale": "...", "source": "{cfg["orch_sig"]}\\n    ..."}}}}'
            )
            t0 = time.perf_counter()
            res = call_claude_isolated(pg, model=model, timeout_sec=timeout_sec, system_prompt=STRICT_JSON_SYSTEM_PROMPT)
            cost_usd = float(res["cost_usd"])
            meter.charge_cpu(time.perf_counter() - t0, phase=f"{track}_g{gen}_att{attempt}")
            try:
                cand_raw, errs = _parse_compositional_proposal(res["text"], generation=gen, origin=f"G{gen}_att{attempt}", base_modules=current.modules)
                cand = CompositionalAlgoArtifact(gk, track_tag, gen, cand_raw.modules, cand_raw.orchestrator)
                cand_tr_sum, cand_tr_costs, cand_tr_metas = _eval_split(track, train_tasks, cand, op_budget=op_budget, seed=0)
                cand_val_sum, cand_val_costs, cand_val_metas = _eval_split(track, val_tasks, cand, op_budget=op_budget, seed=0)

                val_deltas = [cand_val_costs[t.task_id] - cur_val_costs[t.task_id] for t in val_tasks]
                vstats = paired_wilcoxon_stats(val_deltas)
                xgen_total = sum(sum(m.get("cross_gen_calls", {}).values()) for m in cand_val_metas.values())
                ferr_total = sum(sum(m.get("fn_errors", {}).values()) for m in cand_val_metas.values())
                gen_drop_total = sum(m.get("gen_gate_drops", {}).get(f"g{gen}", 0) for m in cand_val_metas.values())

                passed = (vstats["sum_delta"] < 0) and (vstats["p_less"] < p_thresh)
                meter.charge_llm_proposal(cost_usd, accepted=passed, phase=f"{track}_g{gen}_att{attempt}")
                rec = {
                    "attempt": attempt, "cost_usd": cost_usd, "models_used": res.get("models_used", []),
                    "prompt_hash": _prompt_hash(pg), "train_sum": cand_tr_sum, "train_delta": cand_tr_sum - cur_tr_sum,
                    "val_sum": cand_val_sum, "val_delta": cand_val_sum - cur_val_sum, "val_wilcoxon": vstats,
                    "p_thresh": p_thresh, "passed_gate": passed, "xgen_calls_val": xgen_total,
                    "gen_drops_val": gen_drop_total, "fn_errors_val": ferr_total,
                    "new_modules": [m.name for m in cand.modules if m.generation == gen], "parse_errors": errs,
                }
                attempt_logs.append(rec)
                trace.append({"step": f"G{gen}_att{attempt}", **rec})
                print(
                    f"[{track}] G{gen} att{attempt}: train {cur_tr_sum}->{cand_tr_sum} ({cand_tr_sum-cur_tr_sum:+d}), "
                    f"val_g{gen} {cur_val_sum}->{cand_val_sum} ({vstats['sum_delta']:+.0f}, "
                    f"{vstats['wins']}W/{vstats['ties']}T/{vstats['losses']}L, p_less={vstats['p_less']:.5f} vs {p_thresh}), "
                    f"xgen={xgen_total}, fn_errs={ferr_total}, passed={passed} (${cost_usd:.3f})",
                    flush=True,
                )
                if passed:
                    promoted = True
                    best_cand = cand
                    best_val_stats = vstats
                    break
                else:
                    tr_deltas = [(cand_tr_costs[t.task_id] - cur_tr_costs[t.task_id], t.task_id, cand_tr_metas[t.task_id].get("fn_error_msgs", {})) for t in train_tasks]
                    tr_deltas.sort()
                    prior_fail_note = (
                        f"PREVIOUS ATTEMPT 1 FAILED HIDDEN `val_g{gen}` GATE "
                        f"(val delta={vstats['sum_delta']:+.0f}, {vstats['wins']}W/{vstats['ties']}T/{vstats['losses']}L, "
                        f"p_less={vstats['p_less']:.4f} >= 0.05; xgen={xgen_total}; fn_errs={ferr_total}).\n"
                        f"On train_g{gen}, attempt 1 achieved delta={cand_tr_sum - cur_tr_sum:+d} "
                        f"(best: {tr_deltas[:3]} ... worst: {tr_deltas[-3:]}).\n"
                        f"Fix any fn_errs/budget starvation and design a CLEANER, HIGHER-LEVERAGE Gen {gen} upgrade!\n\n"
                    )
            except Exception as exc:
                meter.charge_llm_proposal(cost_usd, accepted=False, phase=f"{track}_g{gen}_att{attempt}")
                err_rec = {"attempt": attempt, "cost_usd": cost_usd, "models_used": res.get("models_used", []), "error": str(exc)[:220], "passed_gate": False}
                attempt_logs.append(err_rec)
                trace.append({"step": f"G{gen}_att{attempt}", **err_rec})
                print(f"[{track}] G{gen} att{attempt} ERROR: {exc}", flush=True)
                prior_fail_note = f"PREVIOUS ATTEMPT 1 FAILED VALIDATION/PARSE: {str(exc)[:180]}. Fix syntax/schema!\n\n"

        if promoted and best_cand is not None:
            current = CompositionalAlgoArtifact(
                gk, track_tag, gen, best_cand.modules, best_cand.orchestrator, parent_sha256=current.sha256()
            )
        else:
            current = CompositionalAlgoArtifact(
                gk, track_tag, gen, current.modules, current.orchestrator, parent_sha256=current.sha256()
            )
        artifacts[gk] = current
        gen_records[gk] = {
            "promoted": promoted,
            "artifact_sha256": current.sha256(),
            "parent_val_sum": cur_val_sum,
            "val_wilcoxon": best_val_stats,
            "modules": [f"g{m.generation}:{m.name}" for m in current.modules],
            "attempts": attempt_logs,
        }
        _save()

    return json.loads(out_path.read_text(encoding="utf-8"))


def run_evaluate(track: str, proposal_path: Path, packet_out: Path, seeds: Sequence[int] = (0, 1, 2)) -> Dict[str, Any]:
    """100% OFFLINE evaluation (LLM UNPLUGGED) + Law 1 Determinism Audit + Matched-Op Causal Knockouts + RSO 6/6."""
    cfg = _track_cfg(track)
    prop = json.loads(proposal_path.read_text(encoding="utf-8"))
    suites = cfg["suites"]
    manifest_sha = cfg["manifest_sha"]
    if prop["manifest_sha256"] != manifest_sha:
        raise ValueError(f"Manifest SHA mismatch! prop={prop['manifest_sha256']} vs current={manifest_sha}")
    op_budget = int(prop.get("op_budget", cfg["op_budget"]))
    n_gens = cfg["n_gens"]
    hold_suites = cfg["hold_suites"]

    a2 = CompositionalAlgoArtifact.from_dict(prop["artifacts"]["A2_PRIOR_ONLY"])
    gen_arts: List[CompositionalAlgoArtifact] = [
        CompositionalAlgoArtifact.from_dict(prop["artifacts"][f"G{g}"]) for g in range(1, n_gens + 1)
    ]
    g_final = gen_arts[-1]

    # Identify highest actually-promoted generation `last_p` for clean Matched-Op Causal Knockouts
    gen_recs = prop.get("generation_records", {})
    promoted_gens = [g for g in range(1, n_gens + 1) if gen_recs.get(f"G{g}", {}).get("promoted")]
    last_p = promoted_gens[-1] if promoted_gens else 1
    parent_of_last = a2 if last_p == 1 else gen_arts[last_p - 2]

    ko_last_matched = knockout_generations_generic(g_final, {last_p}, cfg["passthrough_type"], f"KO_MATCHED_G{last_p}")
    ko_g2plus_matched = knockout_generations_generic(g_final, set(range(2, n_gens + 1)), cfg["passthrough_type"], "KO_MATCHED_G2PLUS")

    # (arm_name, artifact, matched_op_fallback)
    arm_specs: List[Tuple[str, Optional[CompositionalAlgoArtifact], Optional[CompositionalAlgoArtifact]]] = [
        ("A0_BASE", None, None),
        (cfg["industry_arm"], None, None),
        ("A3_ZERO_LLM", cfg["a3_art"], None),
        ("A5_SHAM", cfg["a5_art"], None),
        ("A2_PRIOR_ONLY", a2, None),
    ]
    for g, ga in enumerate(gen_arts, start=1):
        arm_specs.append((f"G{g}", ga, None))
    arm_specs.append(("KO_MATCHED_LAST", ko_last_matched, parent_of_last))
    arm_specs.append(("KO_MATCHED_G2PLUS", ko_g2plus_matched, gen_arts[0]))

    # Law 1 Explicit Determinism Proof on 6 holdout tasks (0.000 variance!)
    det_tasks = [suites[s][i] for s in hold_suites for i in range(min(2, len(suites[s])))][:6]
    det_mismatches = 0
    for dt in det_tasks:
        c1, s1, m1 = _eval_one(track, dt, g_final, seed=0, op_budget=op_budget)
        c2, s2, m2 = _eval_one(track, dt, g_final, seed=0, op_budget=op_budget)
        if c1 != c2 or s1 != s2 or m1["ops_spent"] != m2["ops_spent"]:
            det_mismatches += 1
    assert det_mismatches == 0, f"LAW 1 VIOLATION on {track}: {det_mismatches} mismatches!"

    rows: List[Dict[str, Any]] = []
    wall_by_arm: Dict[str, float] = {}
    telemetry_by_arm: Dict[str, Dict[str, Any]] = {}
    t_all = time.perf_counter()

    for arm_name, art, fb in arm_specs:
        t0 = time.perf_counter()
        agg_ops = 0
        agg_xgen: Dict[str, int] = {}
        agg_gdrops: Dict[str, int] = {}
        agg_mdrops: Dict[str, int] = {}
        agg_ferrs: Dict[str, int] = {}

        for sname in hold_suites:
            for t in suites[sname]:
                spec_sha = t.sha256()
                if arm_name == cfg["industry_arm"]:
                    if track == "s4a":
                        p = simplify_bv_with_z3_industry(t.spec)
                        icost, isha = p.op_count(), p.sha256()
                    else:
                        cx = synthesize_with_abc(t.n_inputs, t.targets)["xag"]
                        icost, isha = cx.gate_count(), cx.sha256()
                    for sd in seeds:
                        rows.append(make_row(
                            arm=arm_name, suite=sname, task_id=t.task_id, stratum=t.stratum,
                            split=t.split, seed=sd, spec_sha256=spec_sha, cost=icost,
                            verified_exact=True, solution_sha256=isha,
                        ))
                else:
                    for sd in seeds:
                        cost, sol_sha, meta = _eval_one(track, t, art, seed=sd, op_budget=op_budget, fallback_art=fb)
                        rows.append(make_row(
                            arm=arm_name, suite=sname, task_id=t.task_id, stratum=t.stratum,
                            split=t.split, seed=sd, spec_sha256=spec_sha, cost=cost,
                            verified_exact=True, solution_sha256=sol_sha,
                        ))
                        agg_ops += int(meta.get("ops_spent", 0))
                        for k, v in meta.get("cross_gen_calls", {}).items():
                            agg_xgen[k] = agg_xgen.get(k, 0) + v
                        for k, v in meta.get("gen_gate_drops", {}).items():
                            agg_gdrops[k] = agg_gdrops.get(k, 0) + v
                        for k, v in meta.get("mod_gate_drops", {}).items():
                            agg_mdrops[k] = agg_mdrops.get(k, 0) + v
                        for k, v in meta.get("fn_errors", {}).items():
                            agg_ferrs[k] = agg_ferrs.get(k, 0) + v

        wall = round(time.perf_counter() - t0, 3)
        wall_by_arm[arm_name] = wall
        telemetry_by_arm[arm_name] = {
            "total_ops_spent": agg_ops,
            "cross_gen_calls": agg_xgen,
            "gen_gate_drops": agg_gdrops,
            "mod_gate_drops": agg_mdrops,
            "fn_errors": agg_ferrs,
        }
        arm_meds = compute_summary([r for r in rows if r["arm"] == arm_name])
        hold_sum = sum(arm_meds[arm_name][s]["mean_median_cost"] * arm_meds[arm_name][s]["n_tasks"] for s in hold_suites)
        print(
            f"[{track} eval] {arm_name:18s}: holdout_sum={hold_sum:7.1f} | wall={wall:6.2f}s | ops={agg_ops:9d} | xgen={sum(agg_xgen.values()):7d} | ferr={sum(agg_ferrs.values())}",
            flush=True,
        )

    summary = compute_summary(rows)
    packet = {
        "track": cfg["track_tag"],
        "manifest_sha256": manifest_sha,
        "op_budget": op_budget,
        "promoted_gens": promoted_gens,
        "ko_last_target_gen": last_p,
        "determinism_audit": {"checked_tasks": len(det_tasks), "mismatches": det_mismatches, "passed": det_mismatches == 0},
        "seeds": list(seeds),
        "n_rows": len(rows),
        "wall_by_arm_sec": wall_by_arm,
        "total_eval_sec": round(time.perf_counter() - t_all, 3),
        "telemetry_by_arm": telemetry_by_arm,
        "generation_records": gen_recs,
        "sleep_meter": prop.get("sleep_meter", {}),
        "artifacts": {k: v for k, v in prop["artifacts"].items()},
        "summary": summary,
        "rows": rows,
    }
    reduced = verify_and_reduce(
        packet,
        canonical_suites=suites,
        canonical_manifest_sha256=manifest_sha,
        expected_arms=[a for a, _, _ in arm_specs],
        expected_suites=list(hold_suites),
        expected_seeds=list(seeds),
    )
    assert reduced["summary"] == summary, "Tamper-evident reducer mismatch!"
    packet_out.parent.mkdir(parents=True, exist_ok=True)
    packet_out.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    print(f"[{track} eval] Wrote verified {len(rows)}-row packet to {packet_out} in {packet['total_eval_sec']:.2f}s", flush=True)
    return packet


def main() -> None:
    ap = argparse.ArgumentParser(description="Sprint 4 Dual-Track Compositional Runner")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_prop = sub.add_parser("propose")
    p_prop.add_argument("--track", choices=("s4a", "s4b"), required=True)
    p_prop.add_argument("--out", required=True)
    p_prop.add_argument("--model", default="opus")
    p_prop.add_argument("--timeout", type=int, default=480)

    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("--track", choices=("s4a", "s4b"), required=True)
    p_eval.add_argument("--proposals", required=True)
    p_eval.add_argument("--out", required=True)

    args = ap.parse_args()
    if args.cmd == "propose":
        run_propose(args.track, Path(args.out), model=args.model, timeout_sec=args.timeout)
    elif args.cmd == "evaluate":
        run_evaluate(args.track, Path(args.proposals), Path(args.out))


if __name__ == "__main__":
    main()
