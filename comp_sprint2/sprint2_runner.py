"""Sprint 2 Unified Proposer & 100% Offline Evaluator for Track S2-A (6-8in XAG) & Track S2-B (Z3 3B-BV).

Evolves VERIFIED EXECUTABLE PYTHON OPTIMIZATION ALGORITHMS (`AlgoArtifact`, AST-sandboxed)
and evaluates all 6 arms 100% OFFLINE (LLM COMPLETELY UNPLUGGED) at IDENTICAL per-task
wall-clock caps across 3 paired seeds with hardened 3-seed RSO verification.

Subcommands:
  - `propose --track {s2a,s2b} --model opus --out <proposals.json>`
      1. `A2_PRIOR_ONLY` (1 isolated Claude call, spec + API ONLY, ZERO tasks/traces!)
      2. `A4_MG_UNPLUGGED` (2 iterative sleep rounds inspecting `dev_train` failure traces ONLY;
         every proposed pass must pass AST sandbox + exact verification + strictly improve hidden
         `dev_val` at the IDENTICAL per-task wall-clock cap as `A2_PRIOR_ONLY`!)
  - `evaluate --track {s2a,s2b} --proposals <proposals.json> --out <packet.json>`
      100% OFFLINE (LLM OFF) 6-arm x all-tasks x 3-seed evaluation + hardened RSO verify_and_reduce.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from comp_sprint.industry_abc import synthesize_with_abc
from comp_sprint.llm_proposer import call_claude_isolated, extract_json_payload
from comp_sprint.meter import WorkMeter
from comp_sprint2.reducer_s2 import compute_summary, make_row, verify_and_reduce
from comp_sprint2.s2a_benchmarks import build_s2a_benchmarks, s2a_manifest_sha256
from comp_sprint2.s2a_engine import (
    build_s2a_a3_artifact,
    build_s2a_a5_sham_artifact,
    synthesize_s2a_with_artifact,
)
from comp_sprint2.s2b_benchmarks import build_s2b_benchmarks, s2b_manifest_sha256
from comp_sprint2.s2b_bv import simplify_bv_with_z3_industry
from comp_sprint2.s2b_engine import (
    build_s2b_a3_artifact,
    build_s2b_a5_sham_artifact,
    optimize_s2b_with_artifact,
)
from comp_sprint2.sandbox_exec import AlgoArtifact, AlgoPass, validate_algo_source


S2A_SPEC_BLOCK = """
TRACK S2-A SUBSTRATE SPECIFICATION (Hard 6-to-8 Input Multi-Output XAG Circuit Synthesis):
- Primitive 2-input gates: AND (&), XOR (^), with free wire inversions (~). ZERO macro-call discount:
  cost = `circ.gate_count() == circ.and_count() + circ.xor_count()`.
- Every returned `XAGCircuit` is verified 100% bit-exact over all 2^n_inputs truth-table rows.
- You are writing VERIFIED EXECUTABLE PYTHON OPTIMIZATION PASSES that run 100% OFFLINE (LLM OFF)
  under a shared per-task wall-clock deadline (`0.60s` total across all passes!).

EXACT PYTHON PASS INTERFACE (AST-SANDBOXED — NO `import` STATEMENTS, NO DUNDER/PRIVATE ATTRS!):
Define a top-level function:
  def optimize(circ, n_inputs, targets, seed, deadline):
      # circ: current best verified XAGCircuit (circ.n_inputs, circ.gates, circ.outputs, circ.gate_count())
      #   Each gate g in circ.gates has attributes: g.op ("AND"|"XOR"), g.left, g.left_inv, g.right, g.right_inv
      #   Node IDs: -1 = CONST0, 0..n_inputs-1 = primary inputs, n_inputs+idx = gate idx.
      #   Each output in circ.outputs is (node_id, inv_bool).
      # targets: tuple of int bitmasks (length n_outputs, bit r = output on input row r)
      # seed: int
      # deadline: float (check `time.perf_counter() >= deadline` frequently to stay fast!)
      # Return: an improved XAGCircuit (or `circ` if no improvement).

PRE-INJECTED SAFE STDLIB & DOMAIN API (DO NOT IMPORT THEM — THEY ARE ALREADY GLOBALS):
- Stdlib: `math, itertools, collections, Counter, defaultdict, deque, heapq, random, time`
- Domain API:
  * `StrashBuilder(n_inputs)`: `.add_gate(op, left, left_inv, right, right_inv) -> (nid, inv)`, `.build(outputs, prune_dead=True) -> XAGCircuit`
  * `Gate(op, left, left_inv, right, right_inv)`, `XAGCircuit`
  * `full_mask(n_inputs) -> int`, `input_masks(n_inputs) -> tuple[int, ...]`
  * `npn4_canonical(tt4) -> int` (exact 4-input NPN canonicalizer)
  * `sat_exact_4in(tt4, max_gates=6) -> XAGCircuit | None` (exact CaDiCaL 4-in 1-out XAG solver!)
  * `sat_exact_multi(n_in, targets, max_gates=5) -> XAGCircuit | None` (exact CaDiCaL 2..4-in, 1..2-out!)
  * `davio_synth(n_inputs, targets, var_order, greedy=False) -> XAGCircuit`
  * `enumerate_cuts(circ, max_k=4, max_cuts_per_node=16) -> dict[int, list[tuple[int, ...]]]`
  * `eval_cut_tt(circ, root_nid, leaves) -> int | None` (16-bit 4-in embedded truth table)
  * `splice_cut(circ, target_nid, leaves, repl_circ) -> XAGCircuit | None`
  * `splice_npn4(circ, target_nid, leaves, canon_circ, cut_tt4) -> XAGCircuit | None`
  * `cone_size(circ, root_nid, leaves) -> int`
  * `node_tts(circ) -> dict[int, int]` (exact full 64..256-bit truth table of every node in `circ`!)
  * `verify_truth_tables(circ, targets) -> bool`

CRITICAL SANDBOX RULES:
- ZERO `import` / `from ... import` statements!
- ZERO leading-underscore attribute access (`obj._foo` is FORBIDDEN!) and ZERO dunder names!
- ZERO `eval`, `exec`, `open`, `getattr`, `setattr`, `hasattr`, `type`, `globals`, `locals`!

OUTPUT FORMAT (STRICT JSON ONLY):
{
  "passes": [
    {
      "name": "short_snake_case_name",
      "rationale": "1-sentence algorithmic rationale",
      "source": "def optimize(circ, n_inputs, targets, seed, deadline):\\n    ..."
    }
  ]
}
Emit 1 to 3 distinct, fast, concise algorithmic passes (each ~30-90 lines, <= 5,000 chars). Return ONLY valid JSON.
""".strip()


S2B_SPEC_BLOCK = """
TRACK S2-B SUBSTRATE SPECIFICATION (Verified 8/16-Bit Bit-Vector Superoptimization via Z3 UNSAT):
- Fixed primitive SSA BV ops (each op instruction costs 1; inputs & constants cost 0; ZERO macro discount!):
  Unary : "NOT" (~a), "NEG" (-a)
  Binary: "AND" (&), "OR" (|), "XOR" (^), "ADD" (+), "SUB" (-), "MUL" (*),
          "SHL" (<<), "LSHR" (logical >>), "ASHR" (arith >>), "ULT" (a <u b ? 1:0), "EQ" (a==b ? 1:0)
  Ternary: "ITE" (cond != 0 ? a : b)
- Every candidate `BVProgram` is proven 100% mathematically equivalent to `spec` across ALL 2^(width*n_inputs)
  inputs via exact Z3 `UNSAT` on `spec(x) != cand(x)`.
- You are writing VERIFIED EXECUTABLE PYTHON SUPEROPTIMIZATION PASSES that run 100% OFFLINE (LLM OFF)
  under a shared per-task wall-clock deadline (`0.70s` total across all passes!).

EXACT PYTHON PASS INTERFACE (AST-SANDBOXED — NO `import` STATEMENTS, NO DUNDER/PRIVATE ATTRS!):
Define a top-level function:
  def optimize(prog, spec, seed, deadline):
      # prog: current best verified BVProgram:
      #   prog.width (8 or 16), prog.n_inputs (1..3), prog.nodes (tuple of BVNode), prog.out_id (int)
      #   prog.op_count() -> int, prog.eval_one(inputs) -> int, prog.eval_vectors(tvs) -> tuple[int, ...]
      #   Each node nd in prog.nodes has: nd.op ("IN"|"CONST"|BV_OP), nd.args (tuple of ints)
      # spec: original specification BVProgram
      # seed: int
      # deadline: float (check `time.perf_counter() >= deadline` frequently!)
      # Return: an improved BVProgram (or `prog` if no improvement).

PRE-INJECTED SAFE STDLIB & DOMAIN API (DO NOT IMPORT THEM — THEY ARE ALREADY GLOBALS):
- Stdlib: `math, itertools, collections, Counter, defaultdict, deque, heapq, random, time`
- Domain API:
  * `BVBuilder(width, n_inputs, fold_constants=True)`:
      `.inp(i) -> node_id`, `.const(val) -> node_id`, `.op(op_name, *args) -> node_id`, `.build(out_id) -> BVProgram`
  * `BVNode`, `BVProgram`, `UNARY_OPS`, `BINARY_OPS`, `ALL_BV_OPS`
  * `default_test_vectors(width, n_inputs, seed=..., n_rand=24) -> tuple[tuple[int, ...], ...]`
  * `eval_all_nodes(prog, test_vectors) -> list[tuple[int, ...]]` (fast concrete vector for EVERY SSA node in `prog`!)
  * `replace_node(prog, target_idx, repl_prog, arg_map) -> BVProgram | None`
      (replaces SSA node `target_idx` in `prog` with a smaller `repl_prog` wired to existing node indices `arg_map`!)
  * `verify_equiv_z3(spec, cand) -> (is_unsat_bool, counterexample_tuple_or_None)`
      (exact Z3 UNSAT proof! Always pre-filter with concrete `eval_vectors` BEFORE calling Z3 so you stay fast!)

CRITICAL SANDBOX RULES:
- ZERO `import` / `from ... import` statements!
- ZERO leading-underscore attribute access (`obj._foo` is FORBIDDEN!) and ZERO dunder names!
- ZERO `eval`, `exec`, `open`, `getattr`, `setattr`, `hasattr`, `type`, `globals`, `locals`!

OUTPUT FORMAT (STRICT JSON ONLY):
{
  "passes": [
    {
      "name": "short_snake_case_name",
      "rationale": "1-sentence algorithmic rationale",
      "source": "def optimize(prog, spec, seed, deadline):\\n    ..."
    }
  ]
}
Emit 1 to 3 distinct, fast, concise algorithmic passes (each ~30-90 lines, <= 5,000 chars). Return ONLY valid JSON.
""".strip()


def _prompt_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _parse_passes(raw_text: str, track_tag: str, origin: str, max_passes: int = 3) -> Tuple[List[AlgoPass], List[Dict[str, str]]]:
    payload = extract_json_payload(raw_text)
    items = payload["passes"] if isinstance(payload, dict) and "passes" in payload else payload
    if not isinstance(items, list):
        raise ValueError("Expected JSON object with 'passes' list")
    accepted: List[AlgoPass] = []
    rejected: List[Dict[str, str]] = []
    seen_shas = set()
    for idx, item in enumerate(items):
        name = str(item.get("name", f"{origin}_{idx}")) if isinstance(item, dict) else f"{origin}_{idx}"
        try:
            if not isinstance(item, dict):
                raise ValueError("pass entry is not a dict")
            src = str(item["source"])
            rat = str(item.get("rationale", ""))
            p = AlgoPass.from_source(name=name, track=track_tag, source=src, origin=origin, rationale=rat)
            if p.sha256 in seen_shas:
                raise ValueError("duplicate pass source")
            seen_shas.add(p.sha256)
            accepted.append(p)
            if len(accepted) >= max_passes:
                break
        except Exception as exc:
            rejected.append({"name": name, "reason": str(exc)})
    return accepted, rejected


def _track_config(track: str) -> Dict[str, Any]:
    if track == "s2a":
        suites = build_s2a_benchmarks()
        return {
            "track_tag": "S2A_XAG",
            "suites": suites,
            "manifest_sha": s2a_manifest_sha256(suites),
            "dev_suites": ("s2a_dev_struct", "s2a_dev_proc"),
            "hold_suites": ("s2a_hold_struct", "s2a_hold_proc_shared", "s2a_hold_proc_comp"),
            "spec_block": S2A_SPEC_BLOCK,
            "time_budget": 0.60,
            "industry_arm": "A1_ABC_XAG",
            "a3_art": build_s2a_a3_artifact(),
            "a5_art": build_s2a_a5_sham_artifact(),
        }
    if track == "s2b":
        suites = build_s2b_benchmarks()
        return {
            "track_tag": "S2B_BV",
            "suites": suites,
            "manifest_sha": s2b_manifest_sha256(suites),
            "dev_suites": ("s2b_dev_struct", "s2b_dev_proc"),
            "hold_suites": ("s2b_hold_struct", "s2b_hold_proc_mba", "s2b_hold_proc_comp"),
            "spec_block": S2B_SPEC_BLOCK,
            "time_budget": 0.70,
            "industry_arm": "A1_Z3_SIMPLIFY",
            "a3_art": build_s2b_a3_artifact(),
            "a5_art": build_s2b_a5_sham_artifact(),
        }
    raise ValueError(f"Unknown track {track!r}")


def _eval_one_task(track: str, task: Any, art: AlgoArtifact | None, seed: int, time_budget: float) -> Tuple[int, str, Dict[str, Any]]:
    if track == "s2a":
        c, meta = synthesize_s2a_with_artifact(task.n_inputs, task.targets, artifact=art, seed=seed, time_budget_sec=time_budget)
        return c.gate_count(), c.sha256(), meta
    p, meta = optimize_s2b_with_artifact(task.spec, artifact=art, seed=seed, time_budget_sec=time_budget)
    return p.op_count(), p.sha256(), meta


def _eval_industry_task(track: str, task: Any) -> Tuple[int, str]:
    if track == "s2a":
        cx = synthesize_with_abc(task.n_inputs, task.targets)["xag"]
        return cx.gate_count(), cx.sha256()
    p = simplify_bv_with_z3_industry(task.spec)
    return p.op_count(), p.sha256()


def _eval_split(
    track: str,
    tasks: Sequence[Any],
    art: AlgoArtifact | None,
    time_budget: float,
) -> Tuple[int, Dict[str, int], Dict[str, List[Dict[str, Any]]]]:
    scores: Dict[str, int] = {}
    pstats: Dict[str, List[Dict[str, Any]]] = {}
    for t in tasks:
        cost, _sha, meta = _eval_one_task(track, t, art, seed=0, time_budget=time_budget)
        scores[t.task_id] = cost
        pstats[t.task_id] = meta.get("pass_stats", [])
    return sum(scores.values()), scores, pstats


def _summarize_pass_telemetry(pstats: Dict[str, List[Dict[str, Any]]]) -> str:
    by_name: Dict[str, Dict[str, Any]] = {}
    for _tid, plist in pstats.items():
        for st in plist:
            e = by_name.setdefault(st["name"], {"improved": 0, "gain": 0, "errors": 0, "unsound": 0, "ms": 0.0, "sample_err": ""})
            if st["status"] == "improved":
                e["improved"] += 1
                e["gain"] += int(st["gain"])
            elif st["status"] == "error":
                e["errors"] += 1
                if not e["sample_err"]:
                    e["sample_err"] = st["error"]
            elif st["status"] == "rejected_unsound":
                e["unsound"] += 1
            e["ms"] += float(st["elapsed_ms"])
    lines = []
    for name, e in by_name.items():
        lines.append(
            f"  - {name:28s}: improved={e['improved']:2d} tasks, total_gain=-{e['gain']:3d}, "
            f"errors={e['errors']}, unsound={e['unsound']}, total_ms={e['ms']:.0f}"
            + (f" | err={e['sample_err']}" if e["sample_err"] else "")
        )
    return "\n".join(lines) if lines else "  (no passes)"


def _format_dev_train_diag(
    track: str,
    dev_train: Sequence[Any],
    base_scores: Dict[str, int],
    ind_scores: Dict[str, int],
    a2_scores: Dict[str, int],
    cur_scores: Dict[str, int] | None = None,
) -> str:
    hdr = "task_id                    | stratum    | BASE | IND  | A2_PRIOR" + (" | CUR_A4" if cur_scores else "") + " | detail"
    lines = [f"DEV-TRAIN BOTTLENECK DIAGNOSTICS ({len(dev_train)} dev_train tasks ONLY; dev_val & holdout SEALED):", hdr, "-" * len(hdr)]
    for t in dev_train:
        tid = t.task_id
        detail = t.description if track == "s2a" else f"w={t.width} in={t.n_inputs} expr={t.spec.to_expr_str()[:85]}"
        row = f"{tid:26s} | {t.stratum:10s} | {base_scores[tid]:4d} | {ind_scores[tid]:4d} | {a2_scores[tid]:8d}"
        if cur_scores:
            row += f" | {cur_scores[tid]:6d}"
        lines.append(row + f" | {detail}")
    return "\n".join(lines)


def _greedy_select_best_pipeline(
    track: str,
    track_tag: str,
    base_passes: Sequence[AlgoPass],
    cand_passes: Sequence[AlgoPass],
    dev_train: Sequence[Any],
    dev_val: Sequence[Any],
    time_budget: float,
    max_total_passes: int = 4,
    parent_sha: str | None = None,
) -> Tuple[AlgoArtifact, int, int, List[str]]:
    """Strict anti-overfitting additive/replacement pass selection on hidden `dev_val`.

    Starts from `base_passes` (preserving prior passes so we NEVER suffer Phase 2C's
    over-pruning bug!). Evaluates each newly proposed pass individually on top of the
    current pipeline, accepting it ONLY if it strictly reduces BOTH `dev_train` AND hidden
    `dev_val` totals (or reduces `dev_val` strictly without degrading `dev_train`) within
    the EXACT SAME `time_budget`!
    """
    cur_passes = list(base_passes)
    cur_art = AlgoArtifact(arm="A4_MG_UNPLUGGED", track=track_tag, generation=1, passes=tuple(cur_passes), parent_sha256=parent_sha)
    best_tr, _, _ = _eval_split(track, dev_train, cur_art, time_budget)
    best_val, _, _ = _eval_split(track, dev_val, cur_art, time_budget)
    log: List[str] = [f"init({len(cur_passes)} passes): dev_train={best_tr}, dev_val={best_val}"]

    for cp in cand_passes:
        if any(p.sha256 == cp.sha256 for p in cur_passes):
            continue
        # Try 1: append `cp` if under cap
        trial_options: List[Tuple[str, List[AlgoPass]]] = []
        if len(cur_passes) < max_total_passes:
            trial_options.append((f"append:{cp.name}", cur_passes + [cp]))
            # Also try prepending `cp` (if fast pass unlocks later passes!)
            trial_options.append((f"prepend:{cp.name}", [cp] + cur_passes))
        # Try 2: replace any single existing pass if `cp` strictly improves dev_val!
        for rep_idx in range(len(cur_passes)):
            trial_options.append((f"replace[{cur_passes[rep_idx].name}->{cp.name}]", cur_passes[:rep_idx] + [cp] + cur_passes[rep_idx + 1:]))

        best_opt = None
        for label, plist in trial_options:
            cand_art = AlgoArtifact(arm="A4_MG_UNPLUGGED", track=track_tag, generation=1, passes=tuple(plist), parent_sha256=parent_sha)
            val_tot, _, _ = _eval_split(track, dev_val, cand_art, time_budget)
            if val_tot < best_val:
                tr_tot, _, _ = _eval_split(track, dev_train, cand_art, time_budget)
                if tr_tot <= best_tr:
                    if best_opt is None or (val_tot, tr_tot) < (best_opt[0], best_opt[1]):
                        best_opt = (val_tot, tr_tot, label, plist, cand_art)
        if best_opt is not None:
            best_val, best_tr, label, cur_passes, cur_art = best_opt
            log.append(f"ACCEPTED {label}: dev_train={best_tr}, dev_val={best_val}")
        else:
            log.append(f"REJECTED {cp.name}: no strict dev_val improvement under matched {time_budget}s cap")

    return cur_art, best_tr, best_val, log


def cmd_propose(track: str, model: str, out_path: Path) -> Dict[str, Any]:
    t0 = time.perf_counter()
    cfg = _track_config(track)
    suites = cfg["suites"]
    dev_train = [t for s in cfg["dev_suites"] for t in suites[s][:8]]
    dev_val = [t for s in cfg["dev_suites"] for t in suites[s][8:]]
    tb = cfg["time_budget"]
    meter = WorkMeter()

    # 1. Baseline scores on dev_train ONLY
    base_scores: Dict[str, int] = {}
    ind_scores: Dict[str, int] = {}
    for t in dev_train:
        base_scores[t.task_id], _, _ = _eval_one_task(track, t, None, seed=0, time_budget=tb)
        ind_scores[t.task_id], _ = _eval_industry_task(track, t)

    # 2. Arm A2_PRIOR_ONLY: 1 isolated Claude call (SPEC + API ONLY, ZERO tasks/traces!)
    p_a2 = (
        "You are designing a frozen offline optimization pipeline (1 to 3 executable Python passes) "
        "purely from first principles and the substrate specification below. You are given NO "
        "specific benchmark tasks or failure traces.\n\n"
        + cfg["spec_block"]
        + "\n\nDesign your strongest, fastest general-purpose algorithmic optimization passes that "
        "respect `deadline`, avoid errors/unsoundness, and maximize primitive cost reduction on unseen "
        "targets. Return ONLY valid JSON."
    )
    resp_a2 = call_claude_isolated(p_a2, model=model, max_budget_usd=2.5, timeout_sec=420)
    a2_passes, a2_rej = [], []
    try:
        a2_passes, a2_rej = _parse_passes(resp_a2["text"], cfg["track_tag"], "claude_prior_only_s2", max_passes=3)
    except Exception as exc:
        a2_rej.append({"name": "parse_error", "reason": str(exc)})
    meter.charge_llm_proposal(usd=resp_a2["cost_usd"], accepted=len(a2_passes) > 0, phase="A2_PRIOR_ONLY_sleep")
    art_a2 = AlgoArtifact(arm="A2_PRIOR_ONLY", track=cfg["track_tag"], generation=1, passes=tuple(a2_passes))

    a2_tr_tot, a2_tr_scores, a2_tr_pstats = _eval_split(track, dev_train, art_a2, tb)
    a2_val_tot, _, _ = _eval_split(track, dev_val, art_a2, tb)

    # 3. Arm A4_MG_UNPLUGGED Round 1 (inspects A2's actual code + dev_train failure traces & pass telemetry!)
    diag_r1 = _format_dev_train_diag(track, dev_train, base_scores, ind_scores, a2_tr_scores)
    a2_code_view = "\n\n".join(f"# PASS {p.name}\n{p.source}" for p in art_a2.passes)
    p_a4_r1 = (
        "You are the sleep-phase executable algorithm evolver (Round 1 of 2).\n"
        "Inspect the current `A2_PRIOR_ONLY` Python passes, their EXACT per-pass telemetry on `dev_train`, "
        "and the remaining stubborn high-cost `dev_train` tasks below.\n\n"
        "GOAL: Propose 2 to 3 NEW or UPGRADED fast, general-purpose executable Python passes that directly "
        "attack the remaining algorithmic bottlenecks on BOTH structured AND procedural tasks (without "
        "hardcoding task IDs or constants specific to one task!). Every candidate pass will be tested "
        "monotonically and accepted ONLY if it strictly reduces cost on a HIDDEN `dev_val` split under the "
        f"EXACT SAME `{tb}s`/task wall-clock cap!\n\n"
        + cfg["spec_block"]
        + "\n\nCURRENT `A2_PRIOR_ONLY` PASSES:\n" + a2_code_view
        + "\n\n`A2_PRIOR_ONLY` DEV-TRAIN TELEMETRY:\n" + _summarize_pass_telemetry(a2_tr_pstats)
        + f"\nTotals: dev_train={a2_tr_tot} (base={sum(base_scores.values())}), hidden dev_val={a2_val_tot}\n\n"
        + diag_r1
        + "\n\nEmit 2 to 3 sharper, bug-free, general-purpose algorithmic passes as strict JSON ONLY."
    )
    resp_r1 = call_claude_isolated(p_a4_r1, model=model, max_budget_usd=2.5, timeout_sec=420)
    r1_passes, r1_rej = [], []
    try:
        r1_passes, r1_rej = _parse_passes(resp_r1["text"], cfg["track_tag"], "claude_mg_s2_r1", max_passes=3)
    except Exception as exc:
        r1_rej.append({"name": "parse_error", "reason": str(exc)})
    meter.charge_llm_proposal(usd=resp_r1["cost_usd"], accepted=len(r1_passes) > 0, phase="A4_MG_sleep")

    art_r1, r1_tr_tot, r1_val_tot, r1_sel_log = _greedy_select_best_pipeline(
        track, cfg["track_tag"], art_a2.passes, r1_passes, dev_train, dev_val, tb,
        max_total_passes=4, parent_sha=art_a2.sha256(),
    )
    _, r1_tr_scores, r1_tr_pstats = _eval_split(track, dev_train, art_r1, tb)

    # 4. Arm A4_MG_UNPLUGGED Round 2 Refinement (inspects R1 telemetry + remaining stubborn dev_train gaps!)
    diag_r2 = _format_dev_train_diag(track, dev_train, base_scores, ind_scores, a2_tr_scores, cur_scores=r1_tr_scores)
    r1_code_view = "\n\n".join(f"# PASS {p.name} ({p.origin})\n{p.source}" for p in art_r1.passes)
    p_a4_r2 = (
        "You are the sleep-phase executable algorithm evolver (Round 2 of 2 -- Final Refinement).\n"
        f"Round-1 selection log on hidden dev_val: {r1_sel_log}\n"
        f"Current best pipeline: dev_train={r1_tr_tot} (A2={a2_tr_tot}), hidden dev_val={r1_val_tot} (A2={a2_val_tot}).\n\n"
        "Inspect the surviving passes, their exact dev_train telemetry (errors/gains/timing), and the remaining "
        "high-cost dev_train tasks below. Propose 2 to 3 targeted, general-purpose algorithmic passes (fixing "
        "any slow/buggy bottleneck or adding a genuinely new optimization paradigm!) to push hidden `dev_val` "
        f"even lower within the identical `{tb}s`/task cap.\n\n"
        + cfg["spec_block"]
        + "\n\nCURRENT SURVIVING PIPELINE:\n" + r1_code_view
        + "\n\nCURRENT PIPELINE DEV-TRAIN TELEMETRY:\n" + _summarize_pass_telemetry(r1_tr_pstats)
        + "\n\n" + diag_r2
        + "\n\nEmit 2 to 3 refined algorithmic passes as strict JSON ONLY."
    )
    resp_r2 = call_claude_isolated(p_a4_r2, model=model, max_budget_usd=2.5, timeout_sec=420)
    r2_passes, r2_rej = [], []
    try:
        r2_passes, r2_rej = _parse_passes(resp_r2["text"], cfg["track_tag"], "claude_mg_s2_r2", max_passes=3)
    except Exception as exc:
        r2_rej.append({"name": "parse_error", "reason": str(exc)})
    meter.charge_llm_proposal(usd=resp_r2["cost_usd"], accepted=len(r2_passes) > 0, phase="A4_MG_sleep")

    art_r2, r2_tr_tot, r2_val_tot, r2_sel_log = _greedy_select_best_pipeline(
        track, cfg["track_tag"], art_r1.passes, r2_passes, dev_train, dev_val, tb,
        max_total_passes=4, parent_sha=art_r1.sha256(),
    )

    out_data = {
        "track": track,
        "track_tag": cfg["track_tag"],
        "manifest_sha256": cfg["manifest_sha"],
        "time_budget_sec": tb,
        "proposer_model_alias": model,
        "wall_seconds": round(time.perf_counter() - t0, 3),
        "a2_call": {
            "prompt_sha256": _prompt_hash(p_a2),
            "models_used": resp_a2["models_used"],
            "cost_usd": resp_a2["cost_usd"],
            "accepted_passes": [p.name for p in a2_passes],
            "rejected": a2_rej,
            "dev_train_total": a2_tr_tot,
            "dev_val_total": a2_val_tot,
        },
        "a4_calls": {
            "r1": {
                "prompt_sha256": _prompt_hash(p_a4_r1),
                "models_used": resp_r1["models_used"],
                "cost_usd": resp_r1["cost_usd"],
                "proposed_passes": [p.name for p in r1_passes],
                "rejected": r1_rej,
                "selection_log": r1_sel_log,
                "dev_train_total": r1_tr_tot,
                "dev_val_total": r1_val_tot,
            },
            "r2": {
                "prompt_sha256": _prompt_hash(p_a4_r2),
                "models_used": resp_r2["models_used"],
                "cost_usd": resp_r2["cost_usd"],
                "proposed_passes": [p.name for p in r2_passes],
                "rejected": r2_rej,
                "selection_log": r2_sel_log,
                "dev_train_total": r2_tr_tot,
                "dev_val_total": r2_val_tot,
            },
            "final_passes": [p.name for p in art_r2.passes],
        },
        "artifacts": {
            "A2_PRIOR_ONLY": art_a2.to_dict(),
            "A4_MG_UNPLUGGED": art_r2.to_dict(),
        },
        "sleep_meter": meter.snapshot(),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    return out_data


def cmd_evaluate(
    track: str,
    proposals_path: Path,
    out_path: Path,
    seeds: Tuple[int, ...] = (0, 1, 2),
) -> Dict[str, Any]:
    """100% OFFLINE (LLM COMPLETELY UNPLUGGED) 6-arm x all-tasks x 3-seed evaluation + hardened RSO check."""
    t0 = time.perf_counter()
    cfg = _track_config(track)
    suites = cfg["suites"]
    man_sha = cfg["manifest_sha"]
    prop = json.loads(proposals_path.read_text(encoding="utf-8"))
    if prop["manifest_sha256"] != man_sha:
        raise ValueError("Proposals manifest SHA mismatch!")

    art_a2 = AlgoArtifact.from_dict(prop["artifacts"]["A2_PRIOR_ONLY"])
    art_a4 = AlgoArtifact.from_dict(prop["artifacts"]["A4_MG_UNPLUGGED"])
    art_a3 = cfg["a3_art"]
    art_a5 = cfg["a5_art"]
    tb = float(prop["time_budget_sec"])
    eval_suites = cfg["dev_suites"] + cfg["hold_suites"]
    ind_arm = cfg["industry_arm"]

    rows: List[Dict[str, Any]] = []
    arm_wall: Dict[str, float] = {}

    # 1. Offline algorithmic arms (identical wall-clock cap `tb`!)
    for arm_name, art in (
        ("A0_BASE", None),
        ("A2_PRIOR_ONLY", art_a2),
        ("A3_ZERO_LLM", art_a3),
        ("A4_MG_UNPLUGGED", art_a4),
        ("A5_SHAM", art_a5),
    ):
        at0 = time.perf_counter()
        for sname in eval_suites:
            for task in suites[sname]:
                for sd in seeds:
                    cost, sol_sha, _meta = _eval_one_task(track, task, art, seed=sd, time_budget=tb)
                    rows.append(make_row(
                        arm=arm_name, suite=sname, task_id=task.task_id,
                        stratum=task.stratum, split=task.split, seed=sd,
                        spec_sha256=task.sha256(), cost=cost,
                        verified_exact=True, solution_sha256=sol_sha,
                    ))
        arm_wall[arm_name] = round(time.perf_counter() - at0, 3)

    # 2. Deterministic industry baseline (A1_ABC_XAG or A1_Z3_SIMPLIFY)
    at0 = time.perf_counter()
    for sname in eval_suites:
        for task in suites[sname]:
            cost, sol_sha = _eval_industry_task(track, task)
            for sd in seeds:
                rows.append(make_row(
                    arm=ind_arm, suite=sname, task_id=task.task_id,
                    stratum=task.stratum, split=task.split, seed=sd,
                    spec_sha256=task.sha256(), cost=cost,
                    verified_exact=True, solution_sha256=sol_sha,
                ))
    arm_wall[ind_arm] = round(time.perf_counter() - at0, 3)

    arms_all = ("A0_BASE", ind_arm, "A2_PRIOR_ONLY", "A3_ZERO_LLM", "A4_MG_UNPLUGGED", "A5_SHAM")
    summary = compute_summary(rows)
    packet = {
        "track": track,
        "track_tag": cfg["track_tag"],
        "manifest_sha256": man_sha,
        "time_budget_sec": tb,
        "seeds": list(seeds),
        "arms": list(arms_all),
        "wall_seconds": round(time.perf_counter() - t0, 3),
        "arm_wall_seconds": arm_wall,
        "proposer_provenance": {
            "model_alias": prop["proposer_model_alias"],
            "a2_models": prop["a2_call"]["models_used"],
            "a4_r1_models": prop["a4_calls"]["r1"]["models_used"],
            "a4_r2_models": prop["a4_calls"]["r2"]["models_used"],
            "a4_final_passes": prop["a4_calls"]["final_passes"],
        },
        "artifacts": {
            "A2_PRIOR_ONLY": art_a2.to_dict(),
            "A3_ZERO_LLM": art_a3.to_dict(),
            "A4_MG_UNPLUGGED": art_a4.to_dict(),
            "A5_SHAM": art_a5.to_dict(),
        },
        "sleep_meter": prop["sleep_meter"],
        "summary": summary,
        "rows": rows,
    }

    verdict = verify_and_reduce(
        packet,
        canonical_suites=suites,
        canonical_manifest_sha256=man_sha,
        expected_arms=arms_all,
        expected_suites=eval_suites,
        expected_seeds=seeds,
    )
    assert verdict["licenses_verdict"] is True

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    return packet


def main() -> None:
    p = argparse.ArgumentParser(description="Sprint 2 Executable Algorithm Evolution Runner (S2-A & S2-B)")
    sub = p.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("propose")
    pp.add_argument("--track", required=True, choices=("s2a", "s2b"))
    pp.add_argument("--model", default="opus")
    pp.add_argument("--out", required=True, type=Path)

    pe = sub.add_parser("evaluate")
    pe.add_argument("--track", required=True, choices=("s2a", "s2b"))
    pe.add_argument("--proposals", required=True, type=Path)
    pe.add_argument("--out", required=True, type=Path)

    args = p.parse_args()
    if args.cmd == "propose":
        res = cmd_propose(track=args.track, model=args.model, out_path=args.out)
        print(json.dumps({
            "track": res["track"],
            "manifest_sha256": res["manifest_sha256"],
            "wall_seconds": res["wall_seconds"],
            "a2_call": res["a2_call"],
            "a4_calls": res["a4_calls"],
            "sleep_total_usd": res["sleep_meter"]["total_usd"],
        }, indent=2))
    else:
        pkt = cmd_evaluate(track=args.track, proposals_path=args.proposals, out_path=args.out)
        print(json.dumps({
            "track": pkt["track"],
            "manifest_sha256": pkt["manifest_sha256"],
            "wall_seconds": pkt["wall_seconds"],
            "n_rows": len(pkt["rows"]),
            "arm_wall_seconds": pkt["arm_wall_seconds"],
            "proposer_provenance": pkt["proposer_provenance"],
            "summary": {
                arm: {s: v["mean_median_cost"] for s, v in smap.items()}
                for arm, smap in pkt["summary"].items()
            },
        }, indent=2))


if __name__ == "__main__":
    main()
