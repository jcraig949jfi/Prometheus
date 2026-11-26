"""Sprint 6 Runner — Multi-Lineage Archive 4-Gen Compositional Evolution under Law 4b (`OpBudget v3`).

Directly attacks the 2-step compounding ceiling + container wall-clock gap:
  - Law 1 + Law 4b: `OpBudget v3` meters loops + 64-bit big-int words + container allocations/sorts + calls
    (`DEFAULT_S6_V3_BUDGET = 2,400,000` units/task) -> 0.000 jitter AND tight wall-clock parity!
  - Law 2: Four disjoint hidden validation splits `s6_val_g1..s6_val_g4` (N=20 each) + paired Wilcoxon
    `p_less < 0.05` (att1) / `< 0.025` (att2).
  - Law 3 (Multi-Lineage Orthogonal Archive):
      * Gen 0 (`A2_PRIOR_ONLY`): Prior-only modular library calibrated natively to Law 4b `OpBudget v3`.
      * Gen 1 (Lineage A — Functional/Algebraic Decomposition): Ashenhurst-Curtis / bi-decomp / linear GF(2) peeling.
      * Gen 2 (Lineage B — Incremental Mutable-Netlist Local Rewrite): TFO-only mutable netlist ODC/MFFC walk
        (using compact arrays/indices rather than bloated big-ints or dicts so Law 4b stays blazing fast!).
      * Gen 3 (Lineage C — Orthogonal Multi-Output Shared Subcone / SAT-Window / Algebraic Factoring):
        composes BOTH Lineage A + Lineage B modules!
      * Gen 4 (Archive Fusion & Feature-Gated Meta-Orchestration): synthesizes cross-lineage residual module +
        adaptive feature-gated budget router over the full verified archive!
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from comp_sprint.industry_abc import synthesize_with_abc
from comp_sprint.llm_proposer import call_claude_isolated
from comp_sprint.meter import WorkMeter
from comp_sprint2.phase3_compound import STRICT_JSON_SYSTEM_PROMPT
from comp_sprint2.reducer_s2 import compute_summary, make_row, verify_and_reduce
from comp_sprint2.sprint2_runner import _prompt_hash
from comp_sprint3.sandbox_s3 import CompositionalAlgoArtifact, LibModule
from comp_sprint3.sprint3_runner import (
    _format_existing_library,
    _parse_compositional_proposal,
    paired_wilcoxon_stats,
)
from comp_sprint4.ko_matched import knockout_generations_generic
from comp_sprint4.s4b_xag_engine import build_s4b_a3_artifact
from comp_sprint6_compound.law4b_meter import DEFAULT_S6_V3_BUDGET, synthesize_s6_xag
from comp_sprint6_compound.s6_benchmarks import build_s6_benchmarks, s6_manifest_sha256


def _build_s6_a5_sham_artifact() -> CompositionalAlgoArtifact:
    """Matched-wall random Davio restart SHAM (500 restarts/task under Law 4b, matching Sprint 3/4 ~60-90s wall)."""
    mod = LibModule.from_source(
        "s6_a5_sham", 0,
        "def sham_davio(circ, n_inputs, targets, seed):\n"
        "    rng = random.Random(seed * 10007 + 31337)\n"
        "    best = circ\n"
        "    base_ord = list(range(n_inputs))\n"
        "    iters = 0\n"
        "    while iters < 500 and budget.remaining() > 500:\n"
        "        iters += 1\n"
        "        ord_i = list(base_ord)\n"
        "        rng.shuffle(ord_i)\n"
        "        cand = davio_synth(n_inputs, targets, ord_i, greedy=(iters % 5 == 0))\n"
        "        if cand.gate_count() < best.gate_count():\n"
        "            if report_best(cand):\n"
        "                best = cand\n"
        "    return best\n",
        origin="sham_matched_compute",
    )
    orch = LibModule.from_source(
        "s6_a5_orch", 0,
        "def solve(circ, n_inputs, targets, seed, api, lib, budget):\n"
        "    return lib.sham_davio(circ, n_inputs, targets, seed)\n",
        required_fn="solve", origin="sham_matched_compute",
    )
    return CompositionalAlgoArtifact("A5_SHAM", "S6_XAG_LAW4B_ARCHIVE", 0, (mod,), orch)


S6_LAW4B_API_SPEC = """
SPRINT 6 DETERMINISTIC COMPOSITIONAL XAG API UNDER LAW 4b (`OpBudget v3` = 2,400,000 UNITS/TASK):
- Goal: Minimize flattened primitive `{AND, XOR}` gate count (NOT is free) on 8-to-10 input multi-output
  XAG circuits (256..1024-bit truth tables) with 100% bit-exact verification (`verify_truth_tables`).
- HARD LAW 1 + LAW 4b METERING (`OpBudget v3` — ZERO WALL-CLOCK JITTER & TIGHT WALL-CLOCK PARITY!):
    * `time` is REMOVED from the sandbox!
    * Every loop iteration charges 1 unit; every function call charges 3 units.
    * Every integer op (`&`, `|`, `^`, `+`, `-`, `*`, `<<`, `>>`, `~`) > 64 bits charges `(bits - 1) // 64`
      word-ops! (So a 512-bit int charges 7 units, a 1024-bit int charges 15 units, and a huge 50,000-bit
      packed int charges 781 units — DO NOT try big-int packing tricks; they pay full word cost!)
    * Every `dict`/`set` creation charges `4 + 2*len`, `list`/`tuple` charges `2 + len`, `sorted` charges
      `4 + n*log2(n)`. Write lean, allocation-frugal Python (mutate preallocated lists/arrays in place)!
    * Global budget = `2,400,000` v3 units/task. Use `lib.run("fn", ..., op_cap=400000)` for soft slices!
- Available stdlib: `math`, `itertools`, `collections`, `Counter`, `defaultdict`, `deque`, `heapq`, `random`.
- Available `budget`: `budget.remaining()`, `budget.global_remaining()`, `budget.spent`, `budget.limit`.
- Available `lib`: Every public `def fn(...)` in ANY library module is exposed on `lib.<fn>(...)`.
- Available domain API:
    * `XAGCircuit`, `StrashBuilder`, `Gate`, `full_mask(n)`, `input_masks(n)`, `cofactor(tt, var, val)`
    * `node_tts(circ)`, `verify_truth_tables(circ, targets)`, `circuit_features(circ)`
    * `report_best(cand) -> bool`, `best_solution() -> XAGCircuit`, `best_cost() -> int`
    * `davio_synth(n_in, targets, var_order, greedy=False)`, `enumerate_cuts(circ, max_k=4, max_cuts_per_node=16)`
    * `eval_cut_tt(circ, nid, leaves)`, `npn4_canonical(tt4)`, `sat_exact_4in(tt4, max_gates=6)`
    * `sat_exact_multi(n_in, targets, max_gates=5)`, `splice_cut(...)`, `splice_npn4(...)`, `cone_size(...)`
- Orchestrator signature MUST be: `def solve(circ, n_inputs, targets, seed, api, lib, budget):`
- Never use `import`, dunder/private names, or bare `except:`.
"""

LINEAGE_DIRECTIVES = {
    1: (
        "LINEAGE A — CONSTRUCTIVE FUNCTIONAL & LINEAR DECOMPOSITION:\n"
        "Focus strictly on CONSTRUCTIVE synthesis before local rewriting: e.g., multi-output Ashenhurst-Curtis\n"
        "functional peeling (2-4 var bound sets with column multiplicity <= 4), bi-decomposition, or GF(2)\n"
        "linear input/output basis reduction / XOR-forest extraction feeding into `lib` Davio/KFDD helpers."
    ),
    2: (
        "LINEAGE B — INCREMENTAL MUTABLE-NETLIST ODC REWRITING (ALLOCATION-FRUGAL FOR LAW 4b!):\n"
        "Focus strictly on INCREMENTAL local graph rewriting: keep compact parallel lists (op, left, right, tt, refs)\n"
        "mutated IN PLACE (avoid creating fresh dicts/sets inside inner loops or packing giant >2048-bit ints!), update\n"
        "ONLY the transitive fanout (TFO) of changed nodes, and compose `lib` ODC/match helpers for fast plateau walks."
    ),
    3: (
        "LINEAGE C — ORTHOGONAL MULTI-OUTPUT SHARED-SUBCONE / EXACT SAT-WINDOW RESTRUCTURING:\n"
        "Build a THIRD genuinely orthogonal mechanism that composes BOTH Lineage A (G1) AND Lineage B (G2):\n"
        "e.g., exact 2-output or 4-5 input window SAT resynthesis (`sat_exact_4in` / `sat_exact_multi` with NPN4 cache),\n"
        "multi-output shared algebraic kernel / common-divisor extraction, or alternating decomp + mutable-netlist\n"
        "restarts that escape local minima neither G1 nor G2 alone can escape!"
    ),
    4: (
        "LINEAGE D — CROSS-LINEAGE ARCHIVE FUSION & ADAPTIVE FEATURE-GATED META-SOLVER:\n"
        "Inspect the full verified archive (G0 + G1 + G2 + G3) and residual telemetry across structured vs procedural\n"
        "circuits. Synthesize a cross-lineage residual pass (e.g., targeted multi-gate MFFC refactoring / XOR-tree\n"
        "reassociation / ODC-guided cut merging) + an adaptive feature-gated `orchestrator` that dynamically routes\n"
        "`OpBudget v3` across the highest-yield archive modules per circuit profile!"
    ),
}


def _eval_split(tasks, art, v3_budget, seed=0):
    total = 0
    per_task, metas = {}, {}
    for t in tasks:
        c, m = synthesize_s6_xag(t.n_inputs, t.targets, artifact=art, seed=seed, v3_budget=v3_budget)
        cost = c.gate_count()
        total += cost
        per_task[t.task_id] = cost
        metas[t.task_id] = m
    return total, per_task, metas


def _summarize_telem(tasks, a0_costs, cur_costs, cur_metas, v3_budget):
    rows = []
    for t in tasks:
        m = cur_metas[t.task_id]
        rows.append((
            cur_costs[t.task_id], t.task_id, t.stratum, t.n_inputs, len(t.targets), a0_costs[t.task_id],
            m.get("ops_spent", 0), m.get("status", ""), m.get("mod_gate_drops", {}), m.get("cross_gen_calls", {}), m.get("fn_error_msgs", {}),
        ))
    rows.sort(reverse=True)
    lines = ["PER-TASK TRAINING TELEMETRY (sorted by hardest residual gate count):"]
    for cost, tid, strat, nin, nout, c0, ops, st, drops, xgen, ferrs in rows:
        lines.append(
            f"  - {tid} [{strat}, {nin}in->{nout}out]: cur={cost} (A0={c0}, saved={c0-cost}), "
            f"v3_units={ops}/{v3_budget} ({st}), drops={drops}, xgen={xgen}"
            + (f", fn_errs={ferrs}" if ferrs else "")
        )
    return "\n".join(lines)


def run_propose(out_path: Path, model: str = "opus", timeout_sec: int = 480, v3_budget: int = DEFAULT_S6_V3_BUDGET) -> Dict[str, Any]:
    suites = build_s6_benchmarks()
    manifest_sha = s6_manifest_sha256(suites)
    meter = WorkMeter()
    trace: List[Dict[str, Any]] = []
    ckpt: Dict[str, Any] = {}

    if out_path.exists():
        try:
            prev = json.loads(out_path.read_text(encoding="utf-8"))
            if prev.get("manifest_sha256") == manifest_sha:
                ckpt = prev
                trace = list(prev.get("llm_trace", []))
                print(f"[s6] Loaded checkpoint keys={sorted(prev.get('artifacts', {}).keys())}", flush=True)
        except Exception:
            ckpt = {}

    artifacts: Dict[str, CompositionalAlgoArtifact] = {
        k: CompositionalAlgoArtifact.from_dict(d) for k, d in ckpt.get("artifacts", {}).items()
    }
    gen_records: Dict[str, Any] = dict(ckpt.get("generation_records", {}))

    def _save() -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps({
            "track": "S6_XAG_LAW4B_ARCHIVE",
            "manifest_sha256": manifest_sha,
            "v3_budget": v3_budget,
            "artifacts": {k: v.to_dict() for k, v in artifacts.items()},
            "generation_records": gen_records,
            "llm_trace": trace,
            "sleep_meter": meter.snapshot(),
        }, indent=2), encoding="utf-8")

    # ---------------- GEN 0: A2_PRIOR_ONLY ----------------
    if "A2_PRIOR_ONLY" not in artifacts:
        p0 = (
            "You are designing a Compositional Executable XAG Synthesis Library (Generation 0: PRIOR-ONLY under Law 4b OpBudget v3).\n"
            "You have ZERO access to benchmark tasks or telemetry.\n"
            f"{S6_LAW4B_API_SPEC}\n\n"
            "TASK (Generation 0 - Compiled Priors Only):\n"
            "Write 3 clean, lean, allocation-frugal reusable Python modules (40-100 lines each) AND 1 orchestrator `solve`:\n"
            "  - Module 1: Reusable structural/ODC/MFFC/divisor helpers reusable via `lib.<fn>`.\n"
            "  - Module 2: Constructive Davio / XOR-preconditioning synthesis pass.\n"
            "  - Module 3: Local ODC resubstitution / 4-cut rewrite pass calling Module 1 via `lib.<fn>`.\n"
            "  - Orchestrator `solve(circ, n_inputs, targets, seed, api, lib, budget)` calibrated to `2,400,000` v3 units.\n"
            "Output ONLY raw JSON matching:\n"
            '{"new_modules": [{"name": "mod_g0_...", "rationale": "...", "source": "def ..."}], '
            '"orchestrator": {"name": "orch_g0", "rationale": "...", "source": "def solve(circ, n_inputs, targets, seed, api, lib, budget):\\n    ..."}}'
        )
        t0 = time.perf_counter()
        res = call_claude_isolated(p0, model=model, timeout_sec=timeout_sec, system_prompt=STRICT_JSON_SYSTEM_PROMPT)
        cost_usd = float(res["cost_usd"])
        meter.charge_cpu(time.perf_counter() - t0, phase="s6_g0_prior")
        try:
            a2_raw, errs = _parse_compositional_proposal(res["text"], generation=0, origin="A2_PRIOR_ONLY", base_modules=())
            a2 = CompositionalAlgoArtifact("A2_PRIOR_ONLY", "S6_XAG_LAW4B_ARCHIVE", 0, a2_raw.modules, a2_raw.orchestrator)
            meter.charge_llm_proposal(cost_usd, accepted=True, phase="s6_g0_prior")
        except Exception:
            meter.charge_llm_proposal(cost_usd, accepted=False, phase="s6_g0_prior")
            raise
        artifacts["A2_PRIOR_ONLY"] = a2
        a0_v1, _, _ = _eval_split(suites["s6_val_g1"], None, v3_budget=v3_budget, seed=0)
        v1_sum, _, v1_ms = _eval_split(suites["s6_val_g1"], a2, v3_budget=v3_budget, seed=0)
        ferrs = sum(sum(m.get("fn_errors", {}).values()) for m in v1_ms.values())
        trace.append({"step": "A2_PRIOR_ONLY", "cost_usd": cost_usd, "models_used": res.get("models_used", []), "a0_val_g1": a0_v1, "val_g1_sum": v1_sum, "fn_errors": ferrs, "parse_errors": errs})
        gen_records["G0"] = {"artifact_sha256": a2.sha256(), "val_g1_sum": v1_sum, "modules": [m.name for m in a2.modules], "fn_errors": ferrs}
        print(f"[s6] G0 A2_PRIOR_ONLY built ({len(a2.modules)} mods, val_g1 {a0_v1}->{v1_sum}, fn_errs={ferrs}, ${cost_usd:.3f})", flush=True)
        _save()

    # ---------------- GENERATIONS 1..4 (MULTI-LINEAGE ARCHIVE) ----------------
    current = artifacts["A2_PRIOR_ONLY"]
    for gen in (1, 2, 3, 4):
        gk = f"G{gen}"
        if gk in artifacts:
            current = artifacts[gk]
            continue

        train_tasks = suites[f"s6_train_g{gen}"]
        val_tasks = suites[f"s6_val_g{gen}"]
        a0_tr_sum, a0_tr_costs, _ = _eval_split(train_tasks, None, v3_budget=v3_budget, seed=0)
        cur_tr_sum, cur_tr_costs, cur_tr_metas = _eval_split(train_tasks, current, v3_budget=v3_budget, seed=0)
        cur_val_sum, cur_val_costs, _ = _eval_split(val_tasks, current, v3_budget=v3_budget, seed=0)
        telem = _summarize_telem(train_tasks, a0_tr_costs, cur_tr_costs, cur_tr_metas, v3_budget)
        lib_text = _format_existing_library(current)

        promoted = False
        best_cand: Optional[CompositionalAlgoArtifact] = None
        best_val_stats: Dict[str, Any] = {}
        attempt_logs: List[Dict[str, Any]] = []
        prior_fail_note = ""

        for attempt in (1, 2):
            p_thresh = 0.05 if attempt == 1 else 0.025
            pg = (
                f"You are evolving a Multi-Lineage Compositional XAG Library under Law 4b OpBudget v3 — Generation {gen}/4 (Attempt {attempt}/2).\n"
                f"{S6_LAW4B_API_SPEC}\n\n"
                f"{lib_text}\n\n"
                f"GENERATION {gen} TRAINING SET (`s6_train_g{gen}`, 12 tasks; A0={a0_tr_sum}, current={cur_tr_sum}):\n"
                f"{telem}\n\n"
                f"{prior_fail_note}"
                f"{LINEAGE_DIRECTIVES[gen]}\n\n"
                f"STRICT RULES:\n"
                f"1. Keep all existing Gen 0..{gen-1} modules intact in `lib` and DIRECTLY COMPOSE on top of them!\n"
                f"2. Be allocation-frugal under Law 4b (avoid giant >2048-bit ints or allocating fresh dicts inside tight inner loops).\n"
                f"3. NEVER hardcode task names! Improve broadly across BOTH structured AND 100% procedural DAGs.\n"
                f"4. PROMOTION GATE (Law 2): Evaluated on HIDDEN disjoint 20-task `s6_val_g{gen}`. Promoted ONLY IF\n"
                f"   net gates < 0 AND exact paired Wilcoxon `p_less < {p_thresh}`!\n"
                "Output ONLY raw JSON matching:\n"
                '{"new_modules": [{"name": "mod_g' + str(gen) + '_...", "rationale": "...", "source": "def ..."}], '
                '"orchestrator": {"name": "orch_g' + str(gen) + '", "rationale": "...", "source": "def solve(circ, n_inputs, targets, seed, api, lib, budget):\\n    ..."}}'
            )
            t0 = time.perf_counter()
            res = call_claude_isolated(pg, model=model, timeout_sec=timeout_sec, system_prompt=STRICT_JSON_SYSTEM_PROMPT)
            cost_usd = float(res["cost_usd"])
            meter.charge_cpu(time.perf_counter() - t0, phase=f"s6_g{gen}_att{attempt}")
            try:
                cand_raw, errs = _parse_compositional_proposal(res["text"], generation=gen, origin=f"G{gen}_att{attempt}", base_modules=current.modules)
                cand = CompositionalAlgoArtifact(gk, "S6_XAG_LAW4B_ARCHIVE", gen, cand_raw.modules, cand_raw.orchestrator)
                cand_tr_sum, cand_tr_costs, _ = _eval_split(train_tasks, cand, v3_budget=v3_budget, seed=0)
                cand_val_sum, cand_val_costs, cand_val_metas = _eval_split(val_tasks, cand, v3_budget=v3_budget, seed=0)

                val_deltas = [cand_val_costs[t.task_id] - cur_val_costs[t.task_id] for t in val_tasks]
                vstats = paired_wilcoxon_stats(val_deltas)
                xgen_total = sum(sum(m.get("cross_gen_calls", {}).values()) for m in cand_val_metas.values())
                ferr_total = sum(sum(m.get("fn_errors", {}).values()) for m in cand_val_metas.values())

                passed = (vstats["sum_delta"] < 0) and (vstats["p_less"] < p_thresh)
                meter.charge_llm_proposal(cost_usd, accepted=passed, phase=f"s6_g{gen}_att{attempt}")
                rec = {
                    "attempt": attempt, "cost_usd": cost_usd, "models_used": res.get("models_used", []),
                    "train_sum": cand_tr_sum, "train_delta": cand_tr_sum - cur_tr_sum,
                    "val_sum": cand_val_sum, "val_delta": cand_val_sum - cur_val_sum,
                    "val_wilcoxon": vstats, "p_thresh": p_thresh, "passed_gate": passed,
                    "xgen_calls_val": xgen_total, "fn_errors_val": ferr_total,
                    "new_modules": [m.name for m in cand.modules if m.generation == gen], "parse_errors": errs,
                }
                attempt_logs.append(rec)
                trace.append({"step": f"G{gen}_att{attempt}", **rec})
                print(
                    f"[s6] G{gen} att{attempt}: train {cur_tr_sum}->{cand_tr_sum} ({cand_tr_sum-cur_tr_sum:+d}), "
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
                    tr_deltas = sorted((cand_tr_costs[t.task_id] - cur_tr_costs[t.task_id], t.task_id) for t in train_tasks)
                    prior_fail_note = (
                        f"PREVIOUS ATTEMPT 1 FAILED HIDDEN `val_g{gen}` GATE "
                        f"(val delta={vstats['sum_delta']:+.0f}, {vstats['wins']}W/{vstats['ties']}T/{vstats['losses']}L, "
                        f"p_less={vstats['p_less']:.4f} >= 0.05; xgen={xgen_total}; fn_errs={ferr_total}).\n"
                        f"On train_g{gen}, attempt 1 delta={cand_tr_sum - cur_tr_sum:+d} (best={tr_deltas[:3]}, worst={tr_deltas[-3:]}).\n"
                        f"Avoid starving Gen 0..{gen-1} passes and design a CLEANER, HIGHER-LEVERAGE Gen {gen} upgrade!\n\n"
                    )
            except Exception as exc:
                meter.charge_llm_proposal(cost_usd, accepted=False, phase=f"s6_g{gen}_att{attempt}")
                err_rec = {"attempt": attempt, "cost_usd": cost_usd, "error": str(exc)[:220], "passed_gate": False}
                attempt_logs.append(err_rec)
                trace.append({"step": f"G{gen}_att{attempt}", **err_rec})
                print(f"[s6] G{gen} att{attempt} ERROR: {exc}", flush=True)
                prior_fail_note = f"PREVIOUS ATTEMPT 1 FAILED VALIDATION: {str(exc)[:180]}. Fix syntax/schema!\n\n"

        if promoted and best_cand is not None:
            current = CompositionalAlgoArtifact(gk, "S6_XAG_LAW4B_ARCHIVE", gen, best_cand.modules, best_cand.orchestrator, parent_sha256=current.sha256())
        else:
            current = CompositionalAlgoArtifact(gk, "S6_XAG_LAW4B_ARCHIVE", gen, current.modules, current.orchestrator, parent_sha256=current.sha256())
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


def run_evaluate(proposal_path: Path, packet_out: Path, seeds: Sequence[int] = (0, 1, 2)) -> Dict[str, Any]:
    """100% OFFLINE 1,452-row evaluation under Law 4b + Matched-Op Knockouts + Wall-Clock Parity Check + RSO 6/6."""
    prop = json.loads(proposal_path.read_text(encoding="utf-8"))
    suites = build_s6_benchmarks()
    manifest_sha = s6_manifest_sha256(suites)
    if prop["manifest_sha256"] != manifest_sha:
        raise ValueError("Manifest SHA mismatch!")
    v3_budget = int(prop.get("v3_budget", DEFAULT_S6_V3_BUDGET))
    hold_suites = ("s6_hold_struct", "s6_hold_proc_shared", "s6_hold_proc_comp")

    a2 = CompositionalAlgoArtifact.from_dict(prop["artifacts"]["A2_PRIOR_ONLY"])
    g_arts = [CompositionalAlgoArtifact.from_dict(prop["artifacts"][f"G{g}"]) for g in (1, 2, 3, 4)]
    g4 = g_arts[-1]
    gen_recs = prop.get("generation_records", {})
    promoted_gens = [g for g in (1, 2, 3, 4) if gen_recs.get(f"G{g}", {}).get("promoted")]
    last_p = promoted_gens[-1] if promoted_gens else 1
    parent_of_last = a2 if last_p == 1 else g_arts[last_p - 2]

    ko_last = knockout_generations_generic(g4, {last_p}, "XAGCircuit", "KO_MATCHED_LAST")
    ko_g2plus = knockout_generations_generic(g4, {2, 3, 4}, "XAGCircuit", "KO_MATCHED_G2PLUS")

    arm_specs: List[Tuple[str, Optional[CompositionalAlgoArtifact], Optional[CompositionalAlgoArtifact]]] = [
        ("A0_BASE", None, None),
        ("A1_ABC_XAG", None, None),
        ("A3_ZERO_LLM", build_s4b_a3_artifact(), None),
        ("A5_SHAM", _build_s6_a5_sham_artifact(), None),
        ("A2_PRIOR_ONLY", a2, None),
        ("G1", g_arts[0], None),
        ("G2", g_arts[1], None),
        ("G3", g_arts[2], None),
        ("G4", g4, None),
        ("KO_MATCHED_LAST", ko_last, parent_of_last),
        ("KO_MATCHED_G2PLUS", ko_g2plus, g_arts[0]),
    ]

    det_tasks = [suites[s][i] for s in hold_suites for i in range(2)]
    det_mismatches = 0
    for dt in det_tasks:
        c1, m1 = synthesize_s6_xag(dt.n_inputs, dt.targets, g4, seed=0, v3_budget=v3_budget)
        c2, m2 = synthesize_s6_xag(dt.n_inputs, dt.targets, g4, seed=0, v3_budget=v3_budget)
        if c1.gate_count() != c2.gate_count() or c1.sha256() != c2.sha256() or m1["ops_spent"] != m2["ops_spent"]:
            det_mismatches += 1
    assert det_mismatches == 0, f"LAW 1 VIOLATION on s6: {det_mismatches}"

    rows: List[Dict[str, Any]] = []
    wall_by_arm: Dict[str, float] = {}
    telemetry_by_arm: Dict[str, Dict[str, Any]] = {}
    t_all = time.perf_counter()

    for arm_name, art, fb in arm_specs:
        t0 = time.perf_counter()
        agg_ops = 0
        agg_xgen: Dict[str, int] = {}
        agg_mdrops: Dict[str, int] = {}
        agg_ferrs: Dict[str, int] = {}
        for sname in hold_suites:
            for t in suites[sname]:
                spec_sha = t.sha256()
                if arm_name == "A1_ABC_XAG":
                    cx = synthesize_with_abc(t.n_inputs, t.targets)["xag"]
                    icost, isha = cx.gate_count(), cx.sha256()
                    for sd in seeds:
                        rows.append(make_row(arm=arm_name, suite=sname, task_id=t.task_id, stratum=t.stratum, split=t.split, seed=sd, spec_sha256=spec_sha, cost=icost, verified_exact=True, solution_sha256=isha))
                else:
                    for sd in seeds:
                        c, meta = synthesize_s6_xag(t.n_inputs, t.targets, artifact=art, seed=sd, v3_budget=v3_budget, fallback_artifact=fb)
                        rows.append(make_row(arm=arm_name, suite=sname, task_id=t.task_id, stratum=t.stratum, split=t.split, seed=sd, spec_sha256=spec_sha, cost=c.gate_count(), verified_exact=True, solution_sha256=c.sha256()))
                        agg_ops += int(meta.get("ops_spent", 0))
                        for k, v in meta.get("cross_gen_calls", {}).items():
                            agg_xgen[k] = agg_xgen.get(k, 0) + v
                        for k, v in meta.get("mod_gate_drops", {}).items():
                            agg_mdrops[k] = agg_mdrops.get(k, 0) + v
                        for k, v in meta.get("fn_errors", {}).items():
                            agg_ferrs[k] = agg_ferrs.get(k, 0) + v
        wall = round(time.perf_counter() - t0, 3)
        wall_by_arm[arm_name] = wall
        telemetry_by_arm[arm_name] = {"total_ops_spent": agg_ops, "cross_gen_calls": agg_xgen, "mod_gate_drops": agg_mdrops, "fn_errors": agg_ferrs}
        arm_meds = compute_summary([r for r in rows if r["arm"] == arm_name])
        hold_sum = sum(arm_meds[arm_name][s]["mean_median_cost"] * arm_meds[arm_name][s]["n_tasks"] for s in hold_suites)
        print(f"[s6 eval] {arm_name:18s}: holdout_sum={hold_sum:7.1f} | wall={wall:6.2f}s | v3_ops={agg_ops:10d} | xgen={sum(agg_xgen.values()):7d} | ferr={sum(agg_ferrs.values())}", flush=True)

    summary = compute_summary(rows)
    packet = {
        "track": "S6_XAG_LAW4B_ARCHIVE",
        "manifest_sha256": manifest_sha,
        "v3_budget": v3_budget,
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
        "artifacts": prop["artifacts"],
        "summary": summary,
        "rows": rows,
    }
    reduced = verify_and_reduce(packet, canonical_suites=suites, canonical_manifest_sha256=manifest_sha, expected_arms=[a for a, _, _ in arm_specs], expected_suites=list(hold_suites), expected_seeds=list(seeds))
    assert reduced["summary"] == summary
    packet_out.parent.mkdir(parents=True, exist_ok=True)
    packet_out.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    print(f"[s6 eval] Wrote verified {len(rows)}-row packet to {packet_out} in {packet['total_eval_sec']:.2f}s", flush=True)
    return packet


def main() -> None:
    ap = argparse.ArgumentParser(description="Sprint 6 Law 4b Multi-Lineage Archive Runner")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_prop = sub.add_parser("propose")
    p_prop.add_argument("--out", required=True)
    p_prop.add_argument("--model", default="opus")
    p_prop.add_argument("--timeout", type=int, default=480)
    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("--proposals", required=True)
    p_eval.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.cmd == "propose":
        run_propose(Path(args.out), model=args.model, timeout_sec=args.timeout)
    elif args.cmd == "evaluate":
        run_evaluate(Path(args.proposals), Path(args.out))


if __name__ == "__main__":
    main()
