"""Sprint 3 Runner — Compositional 3-Generation Evolution Fixing All Three Compounding Laws.

Law 1 (Zero Wall-Clock Jitter):
  - Deterministic integer `OpBudget` (`DEFAULT_S3_OP_BUDGET = 120_000`) enforced on every
    loop iteration and API call; `time` is removed from sandbox.
  - Explicit determinism audit checks 0.000 variance across repeated runs.

Law 2 (Disjoint Per-Generation Validation + Statistical Promotion Gate):
  - Gen 1 trains on `s3_train_g1` (15), gated ONLY on hidden `s3_val_g1` (25).
  - Gen 2 trains on `s3_train_g2` (15), gated ONLY on hidden `s3_val_g2` (25).
  - Gen 3 trains on `s3_train_g3` (15), gated ONLY on hidden `s3_val_g3` (25).
  - Promotion requires `delta_sum < 0` AND one-sided paired Wilcoxon `p_less < 0.05`
    (Attempt 1) or `p_less < 0.025` (Attempt 2, Bonferroni-adjusted).
  - Final evaluation runs 100% OFFLINE (LLM unplugged) on 50 brand-new untouched holdout
    tasks (`s3_hold_struct[18]`, `s3_hold_proc_shared[16]`, `s3_hold_proc_comp[16]`) x 3 seeds.

Law 3 (Compositional Module Library + Causal Knockouts):
  - Artifacts store generation-tagged `LibModule`s + an adaptive `orchestrator`.
  - Gen k modules directly invoke Gen 0..k-1 helpers via `lib.<fn>(...)` / `lib.run(..., op_cap=...)`.
  - Evaluates causal knockouts `G3_KO_G2G3` and `G3_KO_G3` (stubbing Gen 2+3 or Gen 3 modules
    while keeping `G3`'s exact orchestrator intact).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from comp_sprint.industry_abc import synthesize_with_abc
from comp_sprint.llm_proposer import call_claude_isolated
from comp_sprint.meter import WorkMeter
from comp_sprint2.phase3_compound import STRICT_JSON_SYSTEM_PROMPT
from comp_sprint2.reducer_s2 import compute_summary, make_row, verify_and_reduce
from comp_sprint2.sprint2_runner import _prompt_hash
from comp_sprint3.s3_benchmarks import build_s3_benchmarks, s3_manifest_sha256
from comp_sprint3.s3_engine import (
    DEFAULT_S3_OP_BUDGET,
    build_s3_a3_artifact,
    build_s3_a5_sham_artifact,
    synthesize_s3_with_artifact,
)
from comp_sprint3.sandbox_s3 import (
    CompositionalAlgoArtifact,
    LibModule,
    knockout_generations,
)


def paired_wilcoxon_stats(deltas: Sequence[float]) -> Dict[str, Any]:
    """Exact paired Wilcoxon signed-rank test (`deltas = cand - base`, negative = improvement).

    Computes exact p-values via DP over rank sums for `n_nz <= 25` (handling ties via average ranks),
    falling back to continuity-corrected normal approximation for `n_nz > 25`.
    """
    nz = [float(d) for d in deltas if abs(float(d)) > 1e-12]
    n_pos = sum(1 for d in nz if d > 0)
    n_neg = sum(1 for d in nz if d < 0)
    n_ties = len(deltas) - len(nz)
    n = len(nz)
    s_delta = float(sum(deltas))
    if n == 0:
        return {
            "n": len(deltas), "wins": 0, "ties": n_ties, "losses": 0,
            "sum_delta": 0.0, "p_less": 1.0, "p_two": 1.0,
        }

    # Assign average ranks to |d|
    indexed = sorted(((abs(d), i, d) for i, d in enumerate(nz)), key=lambda x: x[0])
    ranks_x2: List[Tuple[int, float]] = []  # store 2*rank as exact integer!
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(indexed[j + 1][0] - indexed[i][0]) <= 1e-12:
            j += 1
        avg_r_x2 = (i + 1) + (j + 1)  # 2 * ((i+1 + j+1)/2)
        for k in range(i, j + 1):
            ranks_x2.append((avg_r_x2, indexed[k][2]))
        i = j + 1

    w_pos_x2 = sum(rx2 for rx2, d in ranks_x2 if d > 0)
    w_neg_x2 = sum(rx2 for rx2, d in ranks_x2 if d < 0)
    total_x2 = w_pos_x2 + w_neg_x2

    if n <= 25:
        # Exact distribution of W+ (scaled by 2) under sign-flip null
        dp: Dict[int, int] = {0: 1}
        for rx2, _ in ranks_x2:
            ndp: Dict[int, int] = {}
            for s, cnt in dp.items():
                ndp[s] = ndp.get(s, 0) + cnt
                ndp[s + rx2] = ndp.get(s + rx2, 0) + cnt
            dp = ndp
        denom = 1 << n
        # H1 (cand < base): W+ is small (<= w_pos_x2)
        p_less = sum(cnt for s, cnt in dp.items() if s <= w_pos_x2) / denom
        w_min_x2 = min(w_pos_x2, w_neg_x2)
        p_two = min(1.0, 2.0 * sum(cnt for s, cnt in dp.items() if s <= w_min_x2) / denom)
    else:
        w_pos = w_pos_x2 / 2.0
        mean_w = total_x2 / 4.0
        var_w = sum((rx2 / 2.0) ** 2 for rx2, _ in ranks_x2) / 4.0
        sd_w = math.sqrt(max(var_w, 1e-12))
        z_less = (w_pos + 0.5 - mean_w) / sd_w
        p_less = 0.5 * (1.0 + math.erf(z_less / math.sqrt(2.0)))
        z_two = (abs(w_pos - mean_w) - 0.5) / sd_w
        p_two = min(1.0, math.erfc(max(0.0, z_two) / math.sqrt(2.0)))

    return {
        "n": len(deltas),
        "wins": n_neg,
        "ties": n_ties,
        "losses": n_pos,
        "sum_delta": round(s_delta, 4),
        "p_less": round(float(p_less), 6),
        "p_two": round(float(p_two), 6),
    }


S3_API_SPEC = """
SPRINT 3 DETERMINISTIC COMPOSITIONAL XAG API (ZERO WALL-CLOCK, EXACT OP BUDGET):
- Goal: Minimize flattened primitive `{AND, XOR}` gate count (NOT is free) on 7-to-9 input
  multi-output XAG circuits (128..512-bit exact Python-int truth tables) while preserving
  100% bit-exact truth-table equivalence (`verify_truth_tables(cand, targets)`).
- HARD DETERMINISM RULE: `time` is REMOVED from the sandbox! Every `for`/`while`/comprehension
  iteration charges 1 op and every API call charges a deterministic op cost to `budget`
  (total limit = 120,000 ops per task). Never use `import`, dunder/private names, or bare `except:`.
- Available stdlib: `math`, `itertools`, `collections`, `Counter`, `defaultdict`, `deque`, `heapq`, `random`.
- Available `budget` methods:
    * `budget.remaining() -> int` (ops left in current soft sub-cap or global cap)
    * `budget.global_remaining() -> int` (ops left globally)
    * `budget.spent -> int`, `budget.limit -> int`
- Available `lib` compositional runtime:
    * Every public `def fn(...)` defined in ANY library module is exposed on `lib.<fn>(...)`.
    * `lib.run("fn_name", *args, op_cap=25000, **kwargs)` executes `lib.<fn_name>` with a
      deterministic soft sub-budget (`SubBudgetExhausted` is caught safely and returns `None`),
      preventing one subroutine from starving later subroutines!
    * Modules in Gen k CAN and SHOULD directly call helpers in Gen 0..k-1 via `lib.<fn>(...)`!
- Available domain API functions (also injected as globals in every module & orchestrator):
    * `XAGCircuit` (`n_inputs`, `gates` of `Gate(op, left, left_inv, right, right_inv)`, `outputs`, `.gate_count()`, `.truth_tables()`)
    * `StrashBuilder(n_inputs)`: `.add_gate(op, left, left_inv, right, right_inv) -> (nid, inv)` (2 ops), `.build(outputs, prune_dead=True) -> XAGCircuit`
    * `full_mask(n_inputs) -> int`, `input_masks(n_inputs) -> Tuple[int, ...]`
    * `node_tts(circ) -> Dict[int, int]` (full truth table bitmask for `-1`, `0..n_in-1`, and every gate `n_in+gi`)
    * `verify_truth_tables(circ, targets) -> bool`
    * `report_best(cand) -> bool` (ALWAYS call `report_best(cand)` whenever you build an improved candidate — globally tracks the verified minimum even if `budget` later runs out!)
    * `best_solution() -> XAGCircuit`, `best_cost() -> int`
    * `circuit_features(circ) -> dict` (`n_inputs, n_outputs, gate_count, and_count, xor_count, xor_ratio`)
    * `davio_synth(n_inputs, targets, var_order, greedy=False) -> XAGCircuit` (180 ops)
    * `enumerate_cuts(circ, max_k=4, max_cuts_per_node=16) -> Dict[int, List[Tuple[int, ...]]]`
    * `eval_cut_tt(circ, nid, leaves) -> Optional[int]` (5 ops)
    * `npn4_canonical(tt4) -> int` (3 ops)
    * `sat_exact_4in(tt4, max_gates=6) -> Optional[XAGCircuit]` (400 ops)
    * `sat_exact_multi(n_in, targets, max_gates=5) -> Optional[XAGCircuit]` (500 ops)
    * `splice_cut(circ, target_nid, leaves, repl_circ) -> Optional[XAGCircuit]`
    * `splice_npn4(circ, target_nid, leaves, canon_circ, cut_tt4) -> Optional[XAGCircuit]`
    * `cone_size(circ, root_nid, leaves) -> int` (4 ops)
- Orchestrator signature MUST be:
    `def solve(circ, n_inputs, targets, seed, api, lib, budget):`
    returning the best `XAGCircuit` (or `best_solution()`).
- Keep code compact, fast, bug-free, and strictly budget-aware (check `budget.remaining()` inside loops!).
"""


def _extract_json_obj(raw_text: str) -> Dict[str, Any]:
    s = raw_text.strip()
    if s.startswith("```"):
        lines = s.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        s = "\n".join(lines).strip()
    start = s.find("{")
    end = s.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("No JSON object found in response")
    return json.loads(s[start : end + 1])


def _parse_compositional_proposal(
    raw_text: str,
    generation: int,
    origin: str,
    base_modules: Sequence[LibModule],
) -> Tuple[CompositionalAlgoArtifact, List[str]]:
    """Parse JSON with `new_modules` (list) and `orchestrator` (dict) into a validated artifact."""
    data = _extract_json_obj(raw_text)
    errors: List[str] = []

    kept_mods = list(base_modules)
    existing_names = {m.name for m in kept_mods}

    for idx, md in enumerate(data.get("new_modules", [])):
        if not isinstance(md, dict):
            continue
        name = str(md.get("name", f"mod_g{generation}_{idx}")).strip() or f"mod_g{generation}_{idx}"
        src = str(md.get("source", ""))
        rat = str(md.get("rationale", ""))
        try:
            mod = LibModule.from_source(name=name, generation=generation, source=src, origin=origin, rationale=rat)
            if name in existing_names:
                # Replace same-gen only; never silently overwrite earlier generation modules!
                replaced = False
                for i, em in enumerate(kept_mods):
                    if em.name == name and em.generation == generation:
                        kept_mods[i] = mod
                        replaced = True
                        break
                if not replaced:
                    mod = LibModule.from_source(
                        name=f"{name}_g{generation}", generation=generation, source=src, origin=origin, rationale=rat
                    )
                    kept_mods.append(mod)
            else:
                kept_mods.append(mod)
                existing_names.add(mod.name)
        except Exception as exc:
            errors.append(f"module {name!r} rejected: {exc}")

    orch_d = data.get("orchestrator")
    if not isinstance(orch_d, dict) or not orch_d.get("source"):
        raise ValueError(f"Missing valid orchestrator in JSON (module errors: {errors})")

    orch = LibModule.from_source(
        name=str(orch_d.get("name", f"orch_g{generation}")),
        generation=generation,
        source=str(orch_d["source"]),
        required_fn="solve",
        origin=origin,
        rationale=str(orch_d.get("rationale", "")),
    )

    art = CompositionalAlgoArtifact(
        arm=f"G{generation}" if generation > 0 else "A2_PRIOR_ONLY",
        track="S3_XAG_COMP",
        generation=generation,
        modules=tuple(kept_mods),
        orchestrator=orch,
    )
    return art, errors


def _eval_split(
    tasks: Sequence[Any],
    art: Optional[CompositionalAlgoArtifact],
    op_budget: int = DEFAULT_S3_OP_BUDGET,
    seed: int = 0,
) -> Tuple[int, Dict[str, int], Dict[str, Dict[str, Any]]]:
    total = 0
    per_task: Dict[str, int] = {}
    metas: Dict[str, Dict[str, Any]] = {}
    for t in tasks:
        c, meta = synthesize_s3_with_artifact(t.n_inputs, t.targets, artifact=art, seed=seed, op_budget=op_budget)
        cost = c.gate_count()
        total += cost
        per_task[t.task_id] = cost
        metas[t.task_id] = meta
    return total, per_task, metas


def _summarize_train_telemetry(
    tasks: Sequence[Any],
    a0_costs: Dict[str, int],
    cur_costs: Dict[str, int],
    cur_metas: Dict[str, Dict[str, Any]],
) -> str:
    rows = []
    for t in tasks:
        m = cur_metas[t.task_id]
        rows.append((
            cur_costs[t.task_id],
            t.task_id,
            t.stratum,
            t.n_inputs,
            len(t.targets),
            a0_costs[t.task_id],
            m.get("ops_spent", 0),
            m.get("status", ""),
            m.get("error", ""),
            m.get("mod_gate_drops", {}),
            m.get("cross_gen_calls", {}),
            m.get("fn_error_msgs", {}),
        ))
    rows.sort(reverse=True)
    lines = ["PER-TASK TRAINING TELEMETRY (sorted by hardest residual gate count):"]
    for cost, tid, strat, nin, nout, c0, ops, st, err, drops, xgen, ferrs in rows:
        lines.append(
            f"  - {tid} [{strat}, {nin}in->{nout}out]: cur={cost} (A0={c0}, saved={c0-cost}), "
            f"ops={ops}/{DEFAULT_S3_OP_BUDGET} ({st}), drops={drops}, xgen={xgen}"
            + (f", err={err}" if err else "")
            + (f", fn_errs={ferrs}" if ferrs else "")
        )
    # Aggregate module effectiveness
    agg_drops: Dict[str, int] = {}
    agg_calls: Dict[str, int] = {}
    agg_xgen: Dict[str, int] = {}
    for m in cur_metas.values():
        for k, v in m.get("mod_gate_drops", {}).items():
            agg_drops[k] = agg_drops.get(k, 0) + v
        for k, v in m.get("module_calls", {}).items():
            agg_calls[k] = agg_calls.get(k, 0) + v
        for k, v in m.get("cross_gen_calls", {}).items():
            agg_xgen[k] = agg_xgen.get(k, 0) + v
    lines.append(f"AGGREGATE MODULE DROPS: {agg_drops}")
    lines.append(f"AGGREGATE MODULE CALLS: {agg_calls}")
    lines.append(f"AGGREGATE CROSS-GEN CALLS: {agg_xgen}")
    return "\n".join(lines)


def _format_existing_library(art: CompositionalAlgoArtifact) -> str:
    parts = [f"CURRENT VERIFIED COMPOSITIONAL LIBRARY (Gen {art.generation}, {len(art.modules)} modules):"]
    for m in art.modules:
        parts.append(
            f"\n### Module `{m.name}` (gen={m.generation}, exports={list(m.exported_fns)})\n"
            f"# rationale: {m.rationale}\n"
            f"{m.source}"
        )
    parts.append(
        f"\n### Current Orchestrator `{art.orchestrator.name}` (gen={art.orchestrator.generation})\n"
        f"{art.orchestrator.source}"
    )
    return "\n".join(parts)


def run_propose(
    out_path: Path,
    model: str = "opus",
    timeout_sec: int = 480,
    op_budget: int = DEFAULT_S3_OP_BUDGET,
) -> Dict[str, Any]:
    """Run Sprint 3 compositional evolution: A2_PRIOR (Gen 0) -> G1 -> G2 -> G3 with Law 2 gates."""
    suites = build_s3_benchmarks()
    manifest_sha = s3_manifest_sha256(suites)
    meter = WorkMeter()
    trace: List[Dict[str, Any]] = []
    ckpt: Dict[str, Any] = {}

    if out_path.exists():
        try:
            prev = json.loads(out_path.read_text(encoding="utf-8"))
            if prev.get("manifest_sha256") == manifest_sha:
                ckpt = prev
                trace = list(prev.get("llm_trace", []))
                print(f"[s3] Loaded checkpoint keys={sorted(prev.get('artifacts', {}).keys())}", flush=True)
        except Exception:
            ckpt = {}

    artifacts: Dict[str, CompositionalAlgoArtifact] = {}
    for k, d in ckpt.get("artifacts", {}).items():
        artifacts[k] = CompositionalAlgoArtifact.from_dict(d)
    gen_records: Dict[str, Any] = dict(ckpt.get("generation_records", {}))

    def _save() -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "track": "S3_XAG_COMP",
            "manifest_sha256": manifest_sha,
            "op_budget": op_budget,
            "artifacts": {k: v.to_dict() for k, v in artifacts.items()},
            "generation_records": gen_records,
            "llm_trace": trace,
            "sleep_meter": meter.snapshot(),
        }
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # ---------------- GEN 0: A2_PRIOR_ONLY (ZERO TRAINING FEEDBACK!) ----------------
    if "A2_PRIOR_ONLY" not in artifacts:
        p0 = (
            "You are designing a Compositional Executable XAG Synthesis Library (Generation 0: PRIOR-ONLY).\n"
            "You have ZERO access to benchmark tasks or telemetry.\n"
            f"{S3_API_SPEC}\n\n"
            "TASK (Generation 0 - Compiled Priors Only):\n"
            "Write 3 clean, modular, reusable Python library modules (each 40-100 lines) AND 1 orchestrator `solve`:\n"
            "  - Module 1: Reusable structural analysis / ODC / MFFC / truth-table helper primitives (e.g., computing\n"
            "    observability don't-care masks, fanout/MFFC cones, divisor tables) that LATER generations can import via `lib.<fn>`!\n"
            "  - Module 2: Constructive decomposition / basis-reduction or multi-output Davio/XOR-preconditioning pass.\n"
            "  - Module 3: Local rewriting / ODC resubstitution / SAT-4cut or plateau walk pass calling Module 1 helpers via `lib.<fn>`.\n"
            "  - Orchestrator `solve(circ, n_inputs, targets, seed, api, lib, budget)`: adaptively runs your modules using\n"
            "    `lib.run(..., op_cap=...)` within `budget` (120,000 ops), calling `report_best(cand)` on improvements.\n"
            "Output ONLY raw JSON matching:\n"
            '{"new_modules": [{"name": "mod_g0_...", "rationale": "...", "source": "def ..."}], '
            '"orchestrator": {"name": "orch_g0", "rationale": "...", "source": "def solve(circ, n_inputs, targets, seed, api, lib, budget):\\n    ..."}}'
        )
        t0 = time.perf_counter()
        res = call_claude_isolated(p0, model=model, timeout_sec=timeout_sec, system_prompt=STRICT_JSON_SYSTEM_PROMPT)
        raw = res["text"]
        cost_usd = float(res["cost_usd"])
        models_used = res.get("models_used", [])
        meter.charge_cpu(time.perf_counter() - t0, phase="s3_g0_prior")
        try:
            a2, errs = _parse_compositional_proposal(raw, generation=0, origin="A2_PRIOR_ONLY", base_modules=())
            meter.charge_llm_proposal(cost_usd, accepted=True, phase="s3_g0_prior")
        except Exception:
            meter.charge_llm_proposal(cost_usd, accepted=False, phase="s3_g0_prior")
            raise
        artifacts["A2_PRIOR_ONLY"] = a2
        # Evaluate A2 on val_g1 only as baseline reference
        v1_sum, _, _ = _eval_split(suites["s3_val_g1"], a2, op_budget=op_budget, seed=0)
        trace.append({
            "step": "A2_PRIOR_ONLY", "cost_usd": cost_usd, "models_used": models_used,
            "prompt_hash": _prompt_hash(p0), "val_g1_sum": v1_sum, "parse_errors": errs,
        })
        gen_records["G0"] = {"artifact_sha256": a2.sha256(), "val_g1_sum": v1_sum, "modules": [m.name for m in a2.modules]}
        print(f"[s3] G0 A2_PRIOR_ONLY built ({len(a2.modules)} mods, val_g1={v1_sum}, ${cost_usd:.3f}, models={models_used})", flush=True)
        _save()

    # ---------------- GENERATIONS 1, 2, 3 (DISJOINT TRAIN + DISJOINT VAL GATE p<0.05) ----------------
    current = artifacts["A2_PRIOR_ONLY"]
    for gen in (1, 2, 3):
        gk = f"G{gen}"
        if gk in artifacts:
            current = artifacts[gk]
            continue

        train_tasks = suites[f"s3_train_g{gen}"]
        val_tasks = suites[f"s3_val_g{gen}"]

        a0_tr_sum, a0_tr_costs, _ = _eval_split(train_tasks, None, op_budget=op_budget, seed=0)
        cur_tr_sum, cur_tr_costs, cur_tr_metas = _eval_split(train_tasks, current, op_budget=op_budget, seed=0)
        cur_val_sum, cur_val_costs, _ = _eval_split(val_tasks, current, op_budget=op_budget, seed=0)

        telem = _summarize_train_telemetry(train_tasks, a0_tr_costs, cur_tr_costs, cur_tr_metas)
        lib_text = _format_existing_library(current)

        promoted = False
        best_cand: Optional[CompositionalAlgoArtifact] = None
        best_val_stats: Dict[str, Any] = {}
        attempt_logs: List[Dict[str, Any]] = []
        prior_fail_note = ""

        for attempt in (1, 2):
            p_thresh = 0.05 if attempt == 1 else 0.025
            pg = (
                f"You are evolving a Compositional Executable XAG Library — Generation {gen} (Attempt {attempt}/2).\n"
                f"{S3_API_SPEC}\n\n"
                f"{lib_text}\n\n"
                f"GENERATION {gen} TRAINING SET (`s3_train_g{gen}`, 15 brand-new tasks; A0={a0_tr_sum}, current={cur_tr_sum}):\n"
                f"{telem}\n\n"
                f"{prior_fail_note}"
                f"COMPOSITIONAL EVOLUTION OBJECTIVE (Generation {gen}):\n"
                f"1. DO NOT rewrite or duplicate existing Gen 0..{gen-1} modules — they remain intact in `lib`!\n"
                f"2. Write 1-2 NEW reusable Gen {gen} module(s) that DIRECTLY COMPOSE ON TOP OF existing `lib.<fn>(...)` helpers\n"
                f"   to attack genuine structural/algorithmic bottlenecks visible in the telemetry above (for BOTH structured\n"
                f"   7-9in arithmetic/mod/sort/crypto AND 100% procedural random DAGs — NEVER hardcode task names!).\n"
                f"   High-leverage compositional ideas: linear/XOR-layer basis extraction or affine input/output preconditioning\n"
                f"   feeding into `lib` synthesis; Ashenhurst-Curtis / disjunctive / bi-decomposition; multi-output shared\n"
                f"   divisor/subcone extraction; SAT-guided 4-cut or 2-output window restructuring; ODC-guided algebraic\n"
                f"   factorization or iterative alternating construct+ODC-polish loops with adaptive `op_cap` allocation.\n"
                f"3. Provide an updated `orchestrator` (`def solve(circ, n_inputs, targets, seed, api, lib, budget)`) that\n"
                f"   preserves all winning Gen 0..{gen-1} strengths AND integrates your new Gen {gen} module(s) with smart\n"
                f"   deterministic `op_cap` budgeting (never starving earlier winning passes!).\n"
                f"4. PROMOTION GATE (Law 2): Your candidate will be evaluated on a HIDDEN disjoint 25-task validation set\n"
                f"   (`s3_val_g{gen}`, mixed structured + procedural). It is promoted ONLY IF net gates < 0 AND exact\n"
                f"   paired Wilcoxon `p_less < {p_thresh}`!\n"
                "Output ONLY raw JSON matching:\n"
                '{"new_modules": [{"name": "mod_g' + str(gen) + '_...", "rationale": "...", "source": "def ..."}], '
                '"orchestrator": {"name": "orch_g' + str(gen) + '", "rationale": "...", "source": "def solve(circ, n_inputs, targets, seed, api, lib, budget):\\n    ..."}}'
            )
            t0 = time.perf_counter()
            res = call_claude_isolated(pg, model=model, timeout_sec=timeout_sec, system_prompt=STRICT_JSON_SYSTEM_PROMPT)
            raw = res["text"]
            cost_usd = float(res["cost_usd"])
            models_used = res.get("models_used", [])
            meter.charge_cpu(time.perf_counter() - t0, phase=f"s3_g{gen}_att{attempt}")
            try:
                cand, errs = _parse_compositional_proposal(raw, generation=gen, origin=f"G{gen}_att{attempt}", base_modules=current.modules)
                cand_tr_sum, cand_tr_costs, cand_tr_metas = _eval_split(train_tasks, cand, op_budget=op_budget, seed=0)
                cand_val_sum, cand_val_costs, cand_val_metas = _eval_split(val_tasks, cand, op_budget=op_budget, seed=0)

                val_deltas = [cand_val_costs[t.task_id] - cur_val_costs[t.task_id] for t in val_tasks]
                vstats = paired_wilcoxon_stats(val_deltas)
                xgen_total = sum(sum(m.get("cross_gen_calls", {}).values()) for m in cand_val_metas.values())
                gen_drop_total = sum(m.get("gen_gate_drops", {}).get(f"g{gen}", 0) for m in cand_val_metas.values())

                passed = (vstats["sum_delta"] < 0) and (vstats["p_less"] < p_thresh)
                meter.charge_llm_proposal(cost_usd, accepted=passed, phase=f"s3_g{gen}_att{attempt}")
                rec = {
                    "attempt": attempt,
                    "cost_usd": cost_usd,
                    "models_used": models_used,
                    "prompt_hash": _prompt_hash(pg),
                    "train_sum": cand_tr_sum,
                    "train_delta": cand_tr_sum - cur_tr_sum,
                    "val_sum": cand_val_sum,
                    "val_delta": cand_val_sum - cur_val_sum,
                    "val_wilcoxon": vstats,
                    "p_thresh": p_thresh,
                    "passed_gate": passed,
                    "xgen_calls_val": xgen_total,
                    "gen_drops_val": gen_drop_total,
                    "new_modules": [m.name for m in cand.modules if m.generation == gen],
                    "parse_errors": errs,
                }
                attempt_logs.append(rec)
                trace.append({"step": f"G{gen}_att{attempt}", **rec})
                print(
                    f"[s3] G{gen} att{attempt}: train {cur_tr_sum}->{cand_tr_sum} ({cand_tr_sum-cur_tr_sum:+d}), "
                    f"val_g{gen} {cur_val_sum}->{cand_val_sum} ({vstats['sum_delta']:+.0f}, "
                    f"{vstats['wins']}W/{vstats['ties']}T/{vstats['losses']}L, p_less={vstats['p_less']:.5f} vs {p_thresh}), "
                    f"xgen={xgen_total}, passed={passed} (${cost_usd:.3f})",
                    flush=True,
                )
                if passed:
                    promoted = True
                    best_cand = cand
                    best_val_stats = vstats
                    break
                else:
                    # Honest diagnostic feedback using ONLY train_g{gen} details + aggregate val gate result (NO val tasks!)
                    tr_deltas = [(cand_tr_costs[t.task_id] - cur_tr_costs[t.task_id], t.task_id, cand_tr_metas[t.task_id].get("error", "")) for t in train_tasks]
                    tr_deltas.sort()
                    prior_fail_note = (
                        f"PREVIOUS ATTEMPT 1 FAILED THE HIDDEN `val_g{gen}` GATE "
                        f"(aggregate val delta={vstats['sum_delta']:+.0f}, {vstats['wins']}W/{vstats['ties']}T/{vstats['losses']}L, "
                        f"p_less={vstats['p_less']:.4f} >= 0.05; cross_gen_calls={xgen_total}; new_gen_drops={gen_drop_total}).\n"
                        f"On train_g{gen}, attempt 1 achieved delta={cand_tr_sum - cur_tr_sum:+d} "
                        f"(top train deltas: {tr_deltas[:4]} ... worst: {tr_deltas[-3:]}).\n"
                        f"Diagnose why Attempt 1 lost budget/regressed on some circuits or had too few wins, and design a\n"
                        f"CLEANER, HIGHER-LEVERAGE Gen {gen} compositional upgrade that strictly avoids regressions (never\n"
                        f"starves Gen 0..{gen-1} passes) and beats parent broadly across BOTH structured and procedural circuits!\n\n"
                    )
            except Exception as exc:
                meter.charge_llm_proposal(cost_usd, accepted=False, phase=f"s3_g{gen}_att{attempt}")
                err_rec = {"attempt": attempt, "cost_usd": cost_usd, "models_used": models_used, "error": str(exc)[:220], "passed_gate": False}
                attempt_logs.append(err_rec)
                trace.append({"step": f"G{gen}_att{attempt}", **err_rec})
                print(f"[s3] G{gen} att{attempt} ERROR: {exc}", flush=True)
                prior_fail_note = f"PREVIOUS ATTEMPT 1 FAILED VALIDATION/PARSE: {str(exc)[:180]}. Fix syntax/schema strictly!\n\n"

        if promoted and best_cand is not None:
            current = CompositionalAlgoArtifact(
                arm=gk,
                track="S3_XAG_COMP",
                generation=gen,
                modules=best_cand.modules,
                orchestrator=best_cand.orchestrator,
                parent_sha256=current.sha256(),
            )
            artifacts[gk] = current
        else:
            # Law 2 honesty: reject noisy promotion and retain parent cleanly
            current = CompositionalAlgoArtifact(
                arm=gk,
                track="S3_XAG_COMP",
                generation=gen,
                modules=current.modules,
                orchestrator=current.orchestrator,
                parent_sha256=current.sha256(),
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


def run_evaluate(
    proposal_path: Path,
    packet_out: Path,
    seeds: Sequence[int] = (0, 1, 2),
) -> Dict[str, Any]:
    """100% OFFLINE evaluation on untouched 50-task holdout (LLM UNPLUGGED) + Law 1 Determinism Audit + RSO 6/6."""
    prop = json.loads(proposal_path.read_text(encoding="utf-8"))
    suites = build_s3_benchmarks()
    manifest_sha = s3_manifest_sha256(suites)
    if prop["manifest_sha256"] != manifest_sha:
        raise ValueError(f"Manifest SHA mismatch! prop={prop['manifest_sha256']} vs current={manifest_sha}")
    op_budget = int(prop.get("op_budget", DEFAULT_S3_OP_BUDGET))

    a2 = CompositionalAlgoArtifact.from_dict(prop["artifacts"]["A2_PRIOR_ONLY"])
    g1 = CompositionalAlgoArtifact.from_dict(prop["artifacts"]["G1"])
    g2 = CompositionalAlgoArtifact.from_dict(prop["artifacts"]["G2"])
    g3 = CompositionalAlgoArtifact.from_dict(prop["artifacts"]["G3"])
    a3 = build_s3_a3_artifact()
    a5 = build_s3_a5_sham_artifact()

    # Causal Knockouts: keep G3's exact orchestrator, stub out Gen 2+3 or Gen 3 modules!
    g3_ko_g2g3 = knockout_generations(g3, {2, 3}, arm_name="G3_KO_G2G3")
    g3_ko_g3 = knockout_generations(g3, {3}, arm_name="G3_KO_G3")

    arm_specs: List[Tuple[str, Optional[CompositionalAlgoArtifact]]] = [
        ("A0_BASE", None),
        ("A1_ABC_XAG", None),
        ("A3_ZERO_LLM", a3),
        ("A5_SHAM", a5),
        ("A2_PRIOR_ONLY", a2),
        ("G1", g1),
        ("G2", g2),
        ("G3", g3),
        ("G3_KO_G2G3", g3_ko_g2g3),
        ("G3_KO_G3", g3_ko_g3),
    ]

    hold_suites = ("s3_hold_struct", "s3_hold_proc_shared", "s3_hold_proc_comp")
    rows: List[Dict[str, Any]] = []
    wall_by_arm: Dict[str, float] = {}
    telemetry_by_arm: Dict[str, Dict[str, Any]] = {}
    t_all = time.perf_counter()

    # Law 1 Explicit Determinism Proof on 6 holdout tasks (run G3 twice, assert 0.000 diff!)
    det_tasks = suites["s3_hold_struct"][:2] + suites["s3_hold_proc_shared"][:2] + suites["s3_hold_proc_comp"][:2]
    det_mismatches = 0
    for dt in det_tasks:
        c1, m1 = synthesize_s3_with_artifact(dt.n_inputs, dt.targets, artifact=g3, seed=0, op_budget=op_budget)
        c2, m2 = synthesize_s3_with_artifact(dt.n_inputs, dt.targets, artifact=g3, seed=0, op_budget=op_budget)
        if c1.gate_count() != c2.gate_count() or c1.sha256() != c2.sha256() or m1["ops_spent"] != m2["ops_spent"]:
            det_mismatches += 1
    assert det_mismatches == 0, f"LAW 1 VIOLATION: {det_mismatches} determinism mismatches!"

    for arm_name, art in arm_specs:
        t0 = time.perf_counter()
        art_sha = art.sha256() if art is not None else hashlib.sha256(arm_name.encode("ascii")).hexdigest()
        agg_ops = 0
        agg_xgen: Dict[str, int] = {}
        agg_gdrops: Dict[str, int] = {}
        agg_mdrops: Dict[str, int] = {}
        agg_mcalls: Dict[str, int] = {}

        for sname in hold_suites:
            for t in suites[sname]:
                spec_sha = t.sha256()
                if arm_name == "A1_ABC_XAG":
                    cx = synthesize_with_abc(t.n_inputs, t.targets)["xag"]
                    c_abc, s_abc = cx.gate_count(), cx.sha256()
                    for sd in seeds:
                        rows.append(make_row(
                            arm=arm_name, suite=sname, task_id=t.task_id, stratum=t.stratum,
                            split=t.split, seed=sd, spec_sha256=spec_sha, cost=c_abc,
                            verified_exact=True, solution_sha256=s_abc,
                        ))
                else:
                    for sd in seeds:
                        c, meta = synthesize_s3_with_artifact(t.n_inputs, t.targets, artifact=art, seed=sd, op_budget=op_budget)
                        rows.append(make_row(
                            arm=arm_name, suite=sname, task_id=t.task_id, stratum=t.stratum,
                            split=t.split, seed=sd, spec_sha256=spec_sha, cost=c.gate_count(),
                            verified_exact=True, solution_sha256=c.sha256(),
                        ))
                        agg_ops += int(meta.get("ops_spent", 0))
                        for k, v in meta.get("cross_gen_calls", {}).items():
                            agg_xgen[k] = agg_xgen.get(k, 0) + v
                        for k, v in meta.get("gen_gate_drops", {}).items():
                            agg_gdrops[k] = agg_gdrops.get(k, 0) + v
                        for k, v in meta.get("mod_gate_drops", {}).items():
                            agg_mdrops[k] = agg_mdrops.get(k, 0) + v
                        for k, v in meta.get("module_calls", {}).items():
                            agg_mcalls[k] = agg_mcalls.get(k, 0) + v

        wall = round(time.perf_counter() - t0, 3)
        wall_by_arm[arm_name] = wall
        telemetry_by_arm[arm_name] = {
            "total_ops_spent": agg_ops,
            "cross_gen_calls": agg_xgen,
            "gen_gate_drops": agg_gdrops,
            "mod_gate_drops": agg_mdrops,
            "module_calls": agg_mcalls,
        }
        arm_meds = compute_summary([r for r in rows if r["arm"] == arm_name])
        hold_sum = sum(arm_meds[arm_name][s]["mean_median_cost"] * arm_meds[arm_name][s]["n_tasks"] for s in hold_suites)
        print(f"[s3 eval] {arm_name:14s}: holdout_sum={hold_sum:6.1f} | wall={wall:6.2f}s | ops={agg_ops} | xgen={sum(agg_xgen.values())}", flush=True)

    summary = compute_summary(rows)
    packet = {
        "track": "S3_XAG_COMP",
        "manifest_sha256": manifest_sha,
        "op_budget": op_budget,
        "determinism_audit": {"checked_tasks": len(det_tasks), "mismatches": det_mismatches, "passed": det_mismatches == 0},
        "seeds": list(seeds),
        "n_rows": len(rows),
        "wall_by_arm_sec": wall_by_arm,
        "total_eval_sec": round(time.perf_counter() - t_all, 3),
        "telemetry_by_arm": telemetry_by_arm,
        "generation_records": prop.get("generation_records", {}),
        "sleep_meter": prop.get("sleep_meter", {}),
        "artifacts": {
            "A2_PRIOR_ONLY": a2.to_dict(),
            "G1": g1.to_dict(),
            "G2": g2.to_dict(),
            "G3": g3.to_dict(),
            "G3_KO_G2G3": g3_ko_g2g3.to_dict(),
            "G3_KO_G3": g3_ko_g3.to_dict(),
        },
        "summary": summary,
        "rows": rows,
    }
    reduced = verify_and_reduce(
        packet,
        canonical_suites=suites,
        canonical_manifest_sha256=manifest_sha,
        expected_arms=[a for a, _ in arm_specs],
        expected_suites=list(hold_suites),
        expected_seeds=list(seeds),
    )
    assert reduced["summary"] == summary, "Tamper-evident reducer mismatch!"
    packet_out.parent.mkdir(parents=True, exist_ok=True)
    packet_out.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    print(f"[s3 eval] Wrote verified {len(rows)}-row packet to {packet_out} in {packet['total_eval_sec']:.2f}s", flush=True)
    return packet


def main() -> None:
    ap = argparse.ArgumentParser(description="Sprint 3 Compositional Deterministic Runner")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_prop = sub.add_parser("propose")
    p_prop.add_argument("--out", required=True)
    p_prop.add_argument("--model", default="opus")
    p_prop.add_argument("--timeout", type=int, default=480)
    p_prop.add_argument("--op-budget", type=int, default=DEFAULT_S3_OP_BUDGET)

    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("--proposals", required=True)
    p_eval.add_argument("--out", required=True)

    args = ap.parse_args()
    if args.cmd == "propose":
        run_propose(Path(args.out), model=args.model, timeout_sec=args.timeout, op_budget=args.op_budget)
    elif args.cmd == "evaluate":
        run_evaluate(Path(args.proposals), Path(args.out))


if __name__ == "__main__":
    main()
