"""Phase 2C — Full `(L, T, S)` Unplugged Experiment on Fresh Sealed v2c Manifest.

Directly addresses Phase 2B's `COMPILED_PRIORS_ONLY` diagnosis with zero holdout leakage:
  1. Fresh sealed v2c manifest (`build_benchmarks_v2c`, 76 tasks: 36 dev + 40 unseen holdout
     across 4 holdout strata: structured, proc_shared, proc_comp, proc_rand).
  2. Internal dev split (`dev_train` = 24 tasks shown to learners; `dev_val` = 12 tasks NEVER
     shown in prompts, used ONLY for scalar selection & greedy leave-one-out pruning).
  3. Full verified `(L, T, S)` offline artifacts across ALL arms (`A2`, `A3`, `A4`, `A5`):
     - `L`: up to 20 SAT-compressed verified XAG macros (2..4 in, 1..3 out)
     - `T`: up to 8 verified sound rewrite rules (`lhs == rhs` checked by exhaustive truth table,
            including global-strash algebraic bridge rules)
     - `S`: typed search strategy (`enable_linear_precond`, `enable_bijective_factor`,
            `enable_bridge_rewrites`, `max_factor_depth`)
  4. `A5_SHAM` matches `A4`'s exact `strategy S` verbatim while replacing `L` and `T` with
     size/arity-matched SAT-optimal random task-irrelevant macros/rewrites.
  5. Hardened 3-seed RSO tamper-evident verification (`verify_and_reduce` with all-seed checksums).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from comp_sprint.benchmarks import BenchmarkTask, build_benchmarks_v2c, manifest_sha256
from comp_sprint.circuit import Macro, verify_truth_tables
from comp_sprint.industry_abc import synthesize_with_abc
from comp_sprint.library import (
    Artifact,
    RewriteRule,
    SearchStrategy,
    build_sham_matched_artifact,
    extract_dev_cofactor_partitions,
    mine_deterministic_artifact,
    prune_artifact_on_val,
)
from comp_sprint.llm_proposer import (
    call_claude_isolated,
    compile_exprs_to_xag,
    extract_json_payload,
    parse_proposed_artifact,
)
from comp_sprint.meter import WorkMeter
from comp_sprint.npn import npn4_canonical
from comp_sprint.reducer import (
    compute_summary,
    evaluate_claim2_detector,
    make_row,
    verify_and_reduce,
)
from comp_sprint.sat_exact import sat_exact_synthesize
from comp_sprint.synth_base import (
    _enumerate_cuts,
    _eval_cut_tt,
    synthesize_with_artifact,
)

DEV_SUITES = ("dev_structured", "dev_proc_shared", "dev_proc_comp")
HOLDOUT_SUITES = (
    "holdout_structured",
    "holdout_proc_shared",
    "holdout_proc_comp",
    "holdout_proc_rand",
)
EVAL_SUITES = DEV_SUITES + HOLDOUT_SUITES

LTS_SPEC_BLOCK = """
SUBSTRATE SPECIFICATION (XAG -- XOR-AND Graph with free wire inversions, Full (L, T, S) Artifact):
- Primitive 2-input gates: AND (&), XOR (^), plus free wire inversions (~). OR (a | b) costs 1 AND gate via ~(~a & ~b).
- Every macro and rewrite rule is FLATTENED to primitive {AND, XOR} gates with structural hashing (ZERO artificial gate discount!).
- Your frozen offline artifact A = (L, T, S) is executed deterministically with LLM COMPLETELY UNPLUGGED:
  1. `macros` (L, up to 20 macros; each 2 <= n_inputs <= 4, 1 <= n_outputs <= 3, 2 <= gates <= 10):
     Used in THREE ways by the offline synthesizer:
       (a) Exact Macro Functional Factorization (multi-output state-compressing M(subset) -> Z reducing
           reachable states |image(W')| < |image(W)| across up to 6 layers, matching modulo input permutation & polarity!),
       (b) Bijective Multi-Output Peeling (if enabled in `strategy`, applies invertible k->k cells when they
           reduce flattened gates),
       (c) Exact NPN4 single-output & 2-output shared k-cut rewriting (k <= 4, strictly monotonic!).
  2. `rewrites` (T, up to 8 verified sound rewrite rules `lhs_exprs -> rhs_exprs`, 2 <= n_inputs <= 4, 1..2 outputs):
     STRICTLY VERIFIED BY EXHAUSTIVE TRUTH TABLE (`lhs == rhs` and `gates(rhs) <= gates(lhs)`).
     Includes BOTH shrinking rules AND equal-gate algebraic bridge rules (e.g. `(x0 & x1) ^ (x0 & x2)` <-> `x0 & (x1 ^ x2)`,
     `x0 | x1` <-> `(x0 ^ x1) ^ (x0 & x1)`), which trigger whenever global StrashBuilder deduplication shrinks the whole DAG!
  3. `strategy` (S, typed config):
     {
       "enable_linear_precond": true/false,   // invertible 1-XOR / 2-XOR basis preconditioning before Davio
       "enable_bijective_factor": true/false, // allow invertible multi-output peeling layers
       "enable_bridge_rewrites": true/false,  // apply equal-gate algebraic bridge rules for global strash sharing
       "max_factor_depth": 6                  // 2..8
     }

OUTPUT FORMAT (STRICT JSON ONLY):
{
  "macros": [
    {"name": "snake_case", "n_inputs": 3, "exprs": ["(x0 ^ x1) ^ x2", "((x0 ^ x2) & (x1 ^ x2)) ^ x2"]}
  ],
  "rewrites": [
    {"name": "xor_dist", "n_inputs": 3, "lhs_exprs": ["(x0 & x1) ^ (x0 & x2)"], "rhs_exprs": ["x0 & (x1 ^ x2)"]}
  ],
  "strategy": {
    "enable_linear_precond": true,
    "enable_bijective_factor": true,
    "enable_bridge_rewrites": true,
    "max_factor_depth": 6
  }
}
Rules for `exprs` / `lhs_exprs` / `rhs_exprs`:
- Use ONLY variables x0..x{n_inputs-1}, constants 0/1, and bitwise Python operators &, |, ^, ~ with parentheses.
- No trivial 0/1-gate macros, no constant outputs, no duplicate truth tables, no unsound rewrites!
""".strip()


def _prompt_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _split_dev_train_val(
    suites: Dict[str, List[BenchmarkTask]],
) -> Tuple[List[BenchmarkTask], List[BenchmarkTask]]:
    """Deterministic internal dev split: first 8/suite = dev_train (24), last 4/suite = dev_val (12)."""
    train: List[BenchmarkTask] = []
    val: List[BenchmarkTask] = []
    for sname in DEV_SUITES:
        train.extend(suites[sname][:8])
        val.extend(suites[sname][8:])
    return train, val


def _build_a2_prior_only_prompt() -> str:
    return (
        "You are proposing a general-purpose offline Boolean synthesis artifact A = (L, T, S) "
        "purely from first principles and the substrate specification below. You are given NO "
        "specific tasks, traces, or benchmark distributions.\n\n"
        + LTS_SPEC_BLOCK
        + "\n\nDesign your strongest general-purpose library of up to 20 compact, high-leverage macros "
        "(combine universal 2-gate 3-input atoms, key 3..4-input NPN classes, and state-compressing "
        "2- and 3-output cells), up to 8 verified algebraic rewrite rules, and optimal `strategy` flags "
        "for 4-to-6-input multi-output Boolean circuits. Return ONLY valid JSON."
    )


def _compute_dev_train_empirical_diagnostics(
    dev_train: Sequence[BenchmarkTask],
    base_circs: Dict[str, Any],
    base_scores: Dict[str, Tuple[int, int]],
    a2_scores: Dict[str, int],
    cur_scores: Dict[str, int] | None,
    meter: WorkMeter,
) -> Tuple[str, List[Macro]]:
    """Compute black-box empirical diagnostics strictly on `dev_train` (ZERO dev_val or holdout access!).

    Returns (formatted_diagnostic_text, discovered_ac_macros) so A4 can inspect:
      1. Exact per-task scores on the 24 `dev_train` tasks.
      2. Recurring black-box Ashenhurst-Curtis 3->2 cofactor partitions discovered on `dev_train`
         (exact expressions / truth tables + recurrence counts across dev_train tasks!).
      3. Top high-savings bloated 3..4-input NPN4 cuts observed in `A0_BASE` circuits on `dev_train`.
    """
    lines = ["DEV-TRAIN EMPIRICAL DIAGNOSTICS (24 dev_train tasks ONLY; dev_val & holdout are SEALED):"]
    hdr = "task_id                      | stratum     | in | out | BASE | ABC | A2_PRIOR"
    if cur_scores is not None:
        hdr += " | CUR_A4"
    lines.append(hdr)
    lines.append("-" * len(hdr))
    for t in dev_train:
        bg, ag = base_scores[t.task_id]
        a2g = a2_scores[t.task_id]
        row = f"{t.task_id:28s} | {t.stratum:11s} | {t.n_inputs:2d} | {t.n_outputs:3d} | {bg:4d} | {ag:3d} | {a2g:8d}"
        if cur_scores is not None:
            row += f" | {cur_scores[t.task_id]:6d}"
        lines.append(row)

    # 1. Black-box Ashenhurst-Curtis 3->2 partitions on dev_train
    ac_parts = extract_dev_cofactor_partitions(dev_train, max_partitions=8, meter=meter, phase="A4_dev_diag")
    ac_macros: List[Macro] = []
    lines.append("\n1. DISCOVERED RECURRING 3-IN / 2-OUT STATE-COMPRESSING COFACTOR PARTITIONS ON DEV-TRAIN (BLACK-BOX):")
    lines.append("   (Each cell compresses 8 input states -> 3..4 equivalence classes across multiple dev_train tasks!)")
    for idx, item in enumerate(ac_parts[:6]):
        m: Macro = item["macro"]
        if len(m.gates) < 2:
            continue
        ac_macros.append(m)
        # Render exact gate expressions so the LLM can inspect and reproduce/refine them verbatim!
        exprs = _circuit_to_exprs(m)
        lines.append(
            f"   - AC_CELL_{idx}: recurred in {item['count']} dev_train tasks ({item['tasks']}), "
            f"exact min gates={item['gates']}, truth_tables={item['truth_tables_hex']}, "
            f"exprs={exprs}"
        )

    # 2. Top high-savings bloated NPN4 cuts observed in A0_BASE circuits on dev_train
    npn_hits: Counter[int] = Counter()
    npn_max_cone: Dict[int, int] = {}

    def cone_size(circ, root_nid, leaves):
        lset = set(leaves)
        seen = set()
        stack = [root_nid]
        n_in = circ.n_inputs
        while stack:
            u = stack.pop()
            if u in seen or u in lset or u < n_in:
                continue
            seen.add(u)
            g = circ.gates[u - n_in]
            stack.append(g.left)
            stack.append(g.right)
        return len(seen)

    for t in dev_train:
        circ = base_circs[t.task_id]
        cuts = _enumerate_cuts(circ, max_k=4, max_cuts_per_node=16)
        n_in = circ.n_inputs
        seen_in_c: Dict[int, int] = {}
        for gi in range(circ.gate_count()):
            nid = n_in + gi
            for leaves in cuts.get(nid, ()):
                if not (3 <= len(leaves) <= 4):
                    continue
                cs = cone_size(circ, nid, leaves)
                if cs < 3:
                    continue
                tt4 = _eval_cut_tt(circ, nid, leaves)
                if tt4 is None:
                    continue
                c = npn4_canonical(tt4)
                if c in (0x0000, 0x00FF, 0x000F, 0x0FF0):
                    continue
                if cs > seen_in_c.get(c, 0):
                    seen_in_c[c] = cs
        for c, cs in seen_in_c.items():
            npn_hits[c] += 1
            if cs > npn_max_cone.get(c, 0):
                npn_max_cone[c] = cs

    lines.append("\n2. TOP BLOATED 3..4-INPUT NPN4 CUTS OBSERVED IN DEV-TRAIN BASE CIRCUITS:")
    shown = 0
    for c, freq in npn_hits.most_common(20):
        opt = sat_exact_synthesize(4, (c,), basis="XAG", min_gates=2, max_gates=5, meter=meter, phase="A4_dev_diag")
        if opt is None:
            continue
        saving = npn_max_cone[c] - opt.gate_count()
        if saving <= 0:
            continue
        m_tmp = Macro.from_circuit(f"npn_{c:04x}", opt)
        lines.append(
            f"   - NPN4 0x{c:04x}: in {freq} dev_train tasks, Davio cone up to {npn_max_cone[c]}g -> "
            f"exact min {opt.gate_count()}g (save {saving}g), expr={_circuit_to_exprs(m_tmp)[0]}"
        )
        shown += 1
        if shown >= 10:
            break

    return "\n".join(lines), ac_macros


def _circuit_to_exprs(m: Macro) -> List[str]:
    """Render a compact Macro into exact Python bitwise expressions over x0..x{n-1}."""
    names: Dict[int, str] = {-1: "0"}
    for i in range(m.n_inputs):
        names[i] = f"x{i}"
    for gi, g in enumerate(m.gates):
        ls = names[g.left]
        if g.left_inv:
            ls = f"(~{ls})"
        rs = names[g.right]
        if g.right_inv:
            rs = f"(~{rs})"
        op_s = "&" if g.op == "AND" else "^"
        names[m.n_inputs + gi] = f"({ls} {op_s} {rs})"
    out_exprs = []
    for onode, oinv in m.outputs:
        s = names[onode]
        if oinv:
            s = f"(~{s})"
        out_exprs.append(s)
    return out_exprs


def _format_artifact_summary(art: Artifact, label: str) -> str:
    lines = [f"{label} ({len(art.macros)} macros, {len(art.rewrites)} rewrites, strategy={art.strategy.to_dict()}):"]
    for m in art.macros:
        lines.append(
            f"  - {m.name:22s}: in={m.n_inputs} out={len(m.outputs)} g={len(m.gates)} exprs={_circuit_to_exprs(m)}"
        )
    for rw in art.rewrites:
        lines.append(
            f"  * RW {rw.name:18s}: in={rw.n_inputs} {len(rw.lhs_gates)}g -> {len(rw.rhs_gates)}g"
        )
    return "\n".join(lines)


def _eval_tasks_sum(
    tasks: Sequence[BenchmarkTask],
    art: Artifact | None,
    budget: int,
    meter: WorkMeter,
    phase: str,
) -> Tuple[int, Dict[str, int]]:
    scores: Dict[str, int] = {}
    for t in tasks:
        c = synthesize_with_artifact(t.n_inputs, t.targets, artifact=art, budget=budget, seed=0, meter=meter, phase=phase)
        scores[t.task_id] = c.gate_count()
    return sum(scores.values()), scores


def _build_a4_round1_prompt(diag_text: str, art_a2: Artifact, a2_val_by_suite: Dict[str, int]) -> str:
    return (
        "You are the sleep-phase abstraction & mechanism proposer (Round 1 of 2) for a Boolean circuit synthesizer.\n"
        "You start from the frozen `A2_PRIOR_ONLY` baseline artifact below and inspect empirical `dev_train` "
        "diagnostics (recurring black-box 3->2 state-compressing cofactor partitions + bloated NPN4 cuts + stubborn tasks).\n\n"
        "CRITICAL GENERALIZATION RULE:\n"
        "- Your proposed artifact will be screened & utility-pruned on a HIDDEN `dev_val` split (12 unseen tasks across "
        "structured, proc_shared, and proc_comp) and then evaluated OFFLINE (LLM UNPLUGGED) on a sealed 40-task holdout.\n"
        "- DO NOT evict general low-arity universal atoms (like 2-gate 3-input atoms `and_or`, `xor3`, `xor_and`, `half_adder`, "
        "`compare_swap`, `full_adder`) to memorize single dev_structured tasks! Instead, KEEP high-value universal priors "
        "AND ADD the recurring empirical abstractions discovered across `dev_train` (especially recurring AC_CELL_* 3->2 "
        "state-compressing partitions and top high-savings recurring NPN4 cuts + verified algebraic bridge rewrites)!\n\n"
        + LTS_SPEC_BLOCK
        + "\n\nSTARTING BASELINE (`A2_PRIOR_ONLY`):\n"
        + _format_artifact_summary(art_a2, "A2_PRIOR_ONLY")
        + f"\n`A2_PRIOR_ONLY` hidden dev_val totals by suite (lower=better): {a2_val_by_suite} (total={sum(a2_val_by_suite.values())})\n\n"
        + diag_text
        + "\n\nEmit your improved full artifact A4_R1 (up to 20 macros, up to 8 verified rewrites, strategy) as strict JSON ONLY."
    )


def _build_a4_round2_prompt(
    diag_text: str,
    r1_kept: Artifact,
    r1_dropped_names: Sequence[str],
    a2_val_by_suite: Dict[str, int],
    r1_val_by_suite: Dict[str, int],
) -> str:
    return (
        "You are the sleep-phase abstraction & mechanism proposer (Round 2 of 2 -- Final Refinement).\n"
        "Your Round-1 artifact was automatically utility-pruned on the hidden `dev_val` split.\n"
        f"- `A2_PRIOR_ONLY` hidden dev_val totals: {a2_val_by_suite} (total={sum(a2_val_by_suite.values())})\n"
        f"- `A4_R1_PRUNED`  hidden dev_val totals: {r1_val_by_suite} (total={sum(r1_val_by_suite.values())})\n"
        f"- Macros PRUNED as dead weight on hidden dev_val: {list(r1_dropped_names)}\n\n"
        "KEEP all surviving macros below that contributed on hidden `dev_val`, and fill remaining free slots (up to 20 "
        "total macros and 8 verified rewrites) with sharper recurring empirical abstractions from `dev_train` (remaining "
        "AC_CELL partitions, top recurring NPN4 cuts, or multi-output/algebraic bridge rules) to push BOTH structured AND "
        "procedural holdout gates even lower.\n\n"
        + LTS_SPEC_BLOCK
        + "\n\nSURVIVING `A4_R1_PRUNED` ARTIFACT:\n"
        + _format_artifact_summary(r1_kept, "A4_R1_PRUNED")
        + "\n\n"
        + diag_text
        + "\n\nEmit your FINAL refined artifact A4_R2 (up to 20 macros, up to 8 verified rewrites, strategy) as strict JSON ONLY."
    )


def _run_shadow_naked_v2c(
    suites: Dict[str, List[BenchmarkTask]],
    model: str,
    meter: WorkMeter,
    budget_per_task_usd: float = 0.50,
) -> Dict[str, Any]:
    """Arm A6_SHADOW_NAKED on predeclared 16-task v2c holdout slice (4 per holdout stratum: indices 0, 3, 6, 9)."""
    slice_tasks: List[Tuple[str, BenchmarkTask]] = []
    for sname in HOLDOUT_SUITES:
        for idx in (0, 3, 6, 9):
            slice_tasks.append((sname, suites[sname][idx]))

    records: List[Dict[str, Any]] = []
    for sname, task in slice_tasks:
        n_rows = 1 << task.n_inputs
        tt_hex = [hex(t) for t in task.targets]
        base_prompt = (
            f"Synthesize a minimal-gate XAG Boolean circuit (ops: &, |, ^, ~ over x0..x{task.n_inputs - 1}) "
            f"implementing this exact {task.n_inputs}-input, {task.n_outputs}-output Boolean function:\n"
            f"- n_inputs = {task.n_inputs} (row r in 0..{n_rows - 1} has x_k = (r >> k) & 1)\n"
            f"- target truth-table bitmasks (hex): {tt_hex}\n"
            + (f"- hint (structured task): {task.description}\n" if task.stratum == "structured" else "- procedural target (no description)\n")
            + 'Return ONLY JSON: {"exprs": ["expr_for_out0", ...]} minimizing total {AND, XOR} gates after structural hashing.'
        )

        solved = False
        best_gates: int | None = None
        task_usd = 0.0
        models_seen = set()
        attempts = 0
        feedback = ""

        for _attempt in range(2):
            attempts += 1
            prompt = base_prompt if not feedback else (base_prompt + "\n\nVERIFIER FEEDBACK FROM PREVIOUS ATTEMPT:\n" + feedback)
            resp_usd = 0.0
            try:
                resp = call_claude_isolated(prompt, model=model, max_budget_usd=budget_per_task_usd, timeout_sec=120)
                resp_usd = float(resp["cost_usd"])
                task_usd += resp_usd
                models_seen.update(resp["models_used"])
                payload = extract_json_payload(resp["text"])
                exprs = payload["exprs"] if isinstance(payload, dict) else payload
                circ = compile_exprs_to_xag(task.n_inputs, exprs)
                actual = circ.truth_tables()
                if verify_truth_tables(circ, task.targets, meter=meter, phase="A6_verify"):
                    solved = True
                    best_gates = circ.gate_count()
                    meter.charge_llm_proposal(usd=resp_usd, accepted=True, phase="A6_SHADOW_NAKED")
                    break
                else:
                    diffs = []
                    for h, (a_tt, t_tt) in enumerate(zip(actual, task.targets)):
                        xor_d = a_tt ^ t_tt
                        if xor_d:
                            bad_rows = [r for r in range(n_rows) if (xor_d >> r) & 1][:4]
                            diffs.append(f"out{h}: {xor_d.bit_count()}/{n_rows} wrong rows, e.g. r={bad_rows}")
                    feedback = "Exact verifier REJECTED circuit:\n" + "\n".join(diffs)
                    meter.charge_llm_proposal(usd=resp_usd, accepted=False, phase="A6_SHADOW_NAKED")
            except Exception as exc:
                feedback = f"Parser/compiler error: {exc}"
                meter.charge_llm_proposal(usd=resp_usd, accepted=False, phase="A6_SHADOW_NAKED")

        records.append({
            "suite": sname,
            "task_id": task.task_id,
            "stratum": task.stratum,
            "solved": solved,
            "gate_count": best_gates,
            "attempts": attempts,
            "usd": round(task_usd, 6),
            "models_used": sorted(models_seen),
        })

    return {
        "n_tasks": len(records),
        "n_solved": sum(1 for r in records if r["solved"]),
        "total_usd": round(sum(r["usd"] for r in records), 6),
        "records": records,
    }


def _suite_totals(tasks: Sequence[BenchmarkTask], scores: Dict[str, int]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for t in tasks:
        out[t.stratum] = out.get(t.stratum, 0) + scores[t.task_id]
    return out


def cmd_propose(model: str, out_path: Path, run_shadow: bool = True, budget: int = 12000) -> Dict[str, Any]:
    t0 = time.perf_counter()
    suites = build_benchmarks_v2c()
    man_sha = manifest_sha256(suites)
    dev_train, dev_val = _split_dev_train_val(suites)
    meter = WorkMeter()

    # 1. Compute dev_train A0_BASE & A1_ABC diagnostics (ZERO dev_val / ZERO holdout access!)
    base_circs: Dict[str, Any] = {}
    base_scores: Dict[str, Tuple[int, int]] = {}
    for t in dev_train:
        cb = synthesize_with_artifact(t.n_inputs, t.targets, artifact=None, budget=budget, seed=0, meter=meter, phase="A4_dev_screen")
        ca = synthesize_with_abc(t.n_inputs, t.targets, meter=meter, phase="A4_dev_screen")
        base_circs[t.task_id] = cb
        base_scores[t.task_id] = (cb.gate_count(), int(ca["xag_gates"]))

    # 2. Arm A2_PRIOR_ONLY: 1 isolated Claude call (full (L, T, S) spec ONLY, ZERO tasks!)
    p_a2 = _build_a2_prior_only_prompt()
    r_a2 = call_claude_isolated(p_a2, model=model, max_budget_usd=2.0)
    a2_macros, a2_rws, a2_strat, a2_rej = parse_proposed_artifact(
        r_a2["text"], origin="claude_prior_only_v2c", max_macros=20, max_rewrites=8,
        compress_exact=True, meter=meter, compress_phase="A2_compress"
    )
    meter.charge_llm_proposal(usd=r_a2["cost_usd"], accepted=len(a2_macros) > 0, phase="A2_PRIOR_ONLY_sleep")
    art_a2 = Artifact(
        arm="A2_PRIOR_ONLY", generation=1, macros=tuple(a2_macros),
        rewrites=tuple(a2_rws), strategy=a2_strat,
    )

    # Evaluate A2 on dev_train & hidden dev_val
    _, a2_train_scores = _eval_tasks_sum(dev_train, art_a2, budget, meter, "A4_dev_screen")
    a2_val_total, a2_val_scores = _eval_tasks_sum(dev_val, art_a2, budget, meter, "A4_dev_val")
    a2_val_by_s = _suite_totals(dev_val, a2_val_scores)

    # 3. Empirical dev_train diagnostics + Arm A4 Round 1
    diag_r1, _ = _compute_dev_train_empirical_diagnostics(
        dev_train, base_circs, base_scores, a2_train_scores, cur_scores=None, meter=meter
    )
    p_a4_r1 = _build_a4_round1_prompt(diag_r1, art_a2, a2_val_by_s)
    r_a4_r1 = call_claude_isolated(p_a4_r1, model=model, max_budget_usd=2.0)
    r1_macros, r1_rws, r1_strat, r1_rej = parse_proposed_artifact(
        r_a4_r1["text"], origin="claude_mg_v2c_r1", max_macros=20, max_rewrites=8,
        compress_exact=True, meter=meter, compress_phase="A4_compress"
    )
    meter.charge_llm_proposal(usd=r_a4_r1["cost_usd"], accepted=len(r1_macros) > 0, phase="A4_MG_sleep")
    art_r1_raw = Artifact(
        arm="A4_MG_UNPLUGGED", generation=1, macros=tuple(r1_macros),
        parent_sha256=art_a2.sha256(), rewrites=tuple(r1_rws), strategy=r1_strat,
    )
    # Utility-prune R1 strictly on hidden dev_val!
    art_r1_pruned, r1_val_total = prune_artifact_on_val(
        art_r1_raw, dev_val, budget=budget, seed=0, meter=meter, phase="A4_dev_val_prune"
    )
    _, r1_val_scores = _eval_tasks_sum(dev_val, art_r1_pruned, budget, meter, "A4_dev_val")
    r1_val_by_s = _suite_totals(dev_val, r1_val_scores)
    kept_r1_shas = {m.sha256 for m in art_r1_pruned.macros}
    r1_dropped = [m.name for m in art_r1_raw.macros if m.sha256 not in kept_r1_shas]
    _, r1_train_scores = _eval_tasks_sum(dev_train, art_r1_pruned, budget, meter, "A4_dev_screen")

    # 4. Arm A4 Round 2 Refinement (sees dev_train scores + aggregate dev_val delta + pruned list)
    diag_r2, _ = _compute_dev_train_empirical_diagnostics(
        dev_train, base_circs, base_scores, a2_train_scores, cur_scores=r1_train_scores, meter=meter
    )
    p_a4_r2 = _build_a4_round2_prompt(diag_r2, art_r1_pruned, r1_dropped, a2_val_by_s, r1_val_by_s)
    r_a4_r2 = call_claude_isolated(p_a4_r2, model=model, max_budget_usd=2.0)
    r2_macros, r2_rws, r2_strat, r2_rej = parse_proposed_artifact(
        r_a4_r2["text"], origin="claude_mg_v2c_r2", max_macros=20, max_rewrites=8,
        compress_exact=True, meter=meter, compress_phase="A4_compress"
    )
    meter.charge_llm_proposal(usd=r_a4_r2["cost_usd"], accepted=len(r2_macros) > 0, phase="A4_MG_sleep")
    art_r2_raw = Artifact(
        arm="A4_MG_UNPLUGGED", generation=1, macros=tuple(r2_macros),
        parent_sha256=art_r1_pruned.sha256(), rewrites=tuple(r2_rws), strategy=r2_strat,
    )
    art_r2_pruned, r2_val_total = prune_artifact_on_val(
        art_r2_raw, dev_val, budget=budget, seed=0, meter=meter, phase="A4_dev_val_prune"
    )
    _, r2_val_scores = _eval_tasks_sum(dev_val, art_r2_pruned, budget, meter, "A4_dev_val")
    r2_val_by_s = _suite_totals(dev_val, r2_val_scores)

    # Monotonic hidden dev_val selection across {A2_PRIOR_ONLY, R1_pruned, R2_pruned}!
    candidates = [
        ("A2_FALLBACK", a2_val_total, art_a2),
        ("R1_PRUNED", r1_val_total, art_r1_pruned),
        ("R2_PRUNED", r2_val_total, art_r2_pruned),
    ]
    # Prefer strictly lower dev_val total; break ties in favor of R2 > R1 > A2
    chosen_label, chosen_val, chosen_art = min(
        candidates,
        key=lambda item: (item[1], {"R2_PRUNED": 0, "R1_PRUNED": 1, "A2_FALLBACK": 2}[item[0]]),
    )
    art_a4_final = Artifact(
        arm="A4_MG_UNPLUGGED",
        generation=1,
        macros=chosen_art.macros,
        parent_sha256=art_a2.sha256(),
        rewrites=chosen_art.rewrites,
        strategy=chosen_art.strategy,
    )

    # 5. Optional A6_SHADOW_NAKED on predeclared 16-task untouched holdout slice
    shadow_res = _run_shadow_naked_v2c(suites, model=model, meter=meter) if run_shadow else None

    out_data = {
        "manifest_version": "v2c",
        "manifest_sha256": man_sha,
        "proposer_model_alias": model,
        "wall_seconds": round(time.perf_counter() - t0, 3),
        "a2_call": {
            "prompt_sha256": _prompt_hash(p_a2),
            "models_used": r_a2["models_used"],
            "cost_usd": r_a2["cost_usd"],
            "input_tokens": r_a2["input_tokens"],
            "output_tokens": r_a2["output_tokens"],
            "accepted_macros": len(a2_macros),
            "accepted_rewrites": len(a2_rws),
            "rejected": a2_rej,
            "dev_val_total_gates": a2_val_total,
            "dev_val_by_stratum": a2_val_by_s,
        },
        "a4_calls": {
            "r1": {
                "prompt_sha256": _prompt_hash(p_a4_r1),
                "models_used": r_a4_r1["models_used"],
                "cost_usd": r_a4_r1["cost_usd"],
                "input_tokens": r_a4_r1["input_tokens"],
                "output_tokens": r_a4_r1["output_tokens"],
                "accepted_macros_raw": len(r1_macros),
                "kept_macros_pruned": len(art_r1_pruned.macros),
                "pruned_names": r1_dropped,
                "accepted_rewrites": len(r1_rws),
                "rejected": r1_rej,
                "dev_val_total_gates": r1_val_total,
                "dev_val_by_stratum": r1_val_by_s,
            },
            "r2": {
                "prompt_sha256": _prompt_hash(p_a4_r2),
                "models_used": r_a4_r2["models_used"],
                "cost_usd": r_a4_r2["cost_usd"],
                "input_tokens": r_a4_r2["input_tokens"],
                "output_tokens": r_a4_r2["output_tokens"],
                "accepted_macros_raw": len(r2_macros),
                "kept_macros_pruned": len(art_r2_pruned.macros),
                "accepted_rewrites": len(r2_rws),
                "rejected": r2_rej,
                "dev_val_total_gates": r2_val_total,
                "dev_val_by_stratum": r2_val_by_s,
            },
            "chosen": chosen_label,
            "chosen_dev_val_total": chosen_val,
        },
        "artifacts": {
            "A2_PRIOR_ONLY": art_a2.to_dict(),
            "A4_MG_UNPLUGGED": art_a4_final.to_dict(),
        },
        "shadow_naked": shadow_res,
        "sleep_meter": meter.snapshot(),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    return out_data


def cmd_evaluate(
    proposals_path: Path,
    out_path: Path,
    budget: int = 12000,
    seeds: tuple[int, ...] = (0, 1, 2),
) -> Dict[str, Any]:
    """100% OFFLINE (LLM COMPLETELY UNPLUGGED) 6-arm evaluation across all 76 v2c tasks x 3 seeds = 1,368 rows."""
    t0 = time.perf_counter()
    prop = json.loads(proposals_path.read_text(encoding="utf-8"))
    suites = build_benchmarks_v2c()
    man_sha = manifest_sha256(suites)
    if prop["manifest_sha256"] != man_sha:
        raise ValueError("Proposals manifest SHA does not match current sealed v2c benchmarks!")

    dev_train, dev_val = _split_dev_train_val(suites)

    # Strictly reload and re-verify frozen LLM artifacts (ZERO LLM calls!)
    art_a2 = Artifact.from_dict(prop["artifacts"]["A2_PRIOR_ONLY"])
    art_a4 = Artifact.from_dict(prop["artifacts"]["A4_MG_UNPLUGGED"])

    meter = WorkMeter()
    rows: List[Dict[str, Any]] = []
    dev_train_circs_for_a3 = []
    dev_train_ids = {t.task_id for t in dev_train}

    # 1. A0_BASE
    for sname in EVAL_SUITES:
        for task in suites[sname]:
            for sd in seeds:
                c = synthesize_with_artifact(
                    task.n_inputs, task.targets, artifact=None, budget=budget,
                    seed=sd, meter=meter, phase="A0_BASE"
                )
                if sd == 0 and task.task_id in dev_train_ids:
                    dev_train_circs_for_a3.append(c)
                rows.append(make_row(
                    arm="A0_BASE", suite=sname, task_id=task.task_id,
                    stratum=task.stratum, split=task.split, seed=sd,
                    n_inputs=task.n_inputs, n_outputs=task.n_outputs,
                    targets=task.targets, gate_count=c.gate_count(),
                    and_count=c.and_count(), xor_count=c.xor_count(),
                    verified_exact=True, circuit_sha256=c.sha256(),
                ))

    # 2. A3_ZERO_LLM (mined strictly on dev_train, pruned on dev_val) + matched A5_SHAM (matched to A4's L, T, S!)
    art_a3 = mine_deterministic_artifact(
        dev_train, dev_train_circs_for_a3, dev_val_tasks=dev_val,
        max_macros=20, max_rewrites=8, generation=1, meter=meter, phase="A3_sleep_mine"
    )
    art_a3 = Artifact.from_dict(art_a3.to_dict())
    art_sham = build_sham_matched_artifact(
        art_a4, seed=2026112391, compress_exact=True, meter=meter, phase="A5_sham_build"
    )
    art_sham = Artifact.from_dict(art_sham.to_dict())

    # 3. Evaluate A2_PRIOR_ONLY, A3_ZERO_LLM, A4_MG_UNPLUGGED, A5_SHAM (LLM COMPLETELY OFF!)
    for arm_name, art in (
        ("A2_PRIOR_ONLY", art_a2),
        ("A3_ZERO_LLM", art_a3),
        ("A4_MG_UNPLUGGED", art_a4),
        ("A5_SHAM", art_sham),
    ):
        for sname in EVAL_SUITES:
            for task in suites[sname]:
                for sd in seeds:
                    c = synthesize_with_artifact(
                        task.n_inputs, task.targets, artifact=art, budget=budget,
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

    # 4. A1_ABC_XAG (Berkeley ABC 1.01 deterministic industry baseline)
    for sname in EVAL_SUITES:
        for task in suites[sname]:
            res_abc = synthesize_with_abc(task.n_inputs, task.targets, meter=meter, phase="A1_ABC")
            cx = res_abc["xag"]
            for sd in seeds:
                rows.append(make_row(
                    arm="A1_ABC_XAG", suite=sname, task_id=task.task_id,
                    stratum=task.stratum, split=task.split, seed=sd,
                    n_inputs=task.n_inputs, n_outputs=task.n_outputs,
                    targets=task.targets, gate_count=cx.gate_count(),
                    and_count=cx.and_count(), xor_count=cx.xor_count(),
                    verified_exact=True, circuit_sha256=cx.sha256(),
                ))

    arms_all = ("A0_BASE", "A1_ABC_XAG", "A2_PRIOR_ONLY", "A3_ZERO_LLM", "A4_MG_UNPLUGGED", "A5_SHAM")
    summary = compute_summary(rows)

    # Compute exact amortization N* vs A6_SHADOW_NAKED (if present)
    sleep_snap = prop["sleep_meter"]
    off_snap = meter.snapshot()
    a4_fixed_usd = float(sleep_snap["by_phase"].get("A4_MG_sleep", {}).get("llm_usd", 0.0)) + (
        float(sleep_snap["by_phase"].get("A4_compress", {}).get("cpu_seconds", 0.0))
        + float(sleep_snap["by_phase"].get("A4_dev_screen", {}).get("cpu_seconds", 0.0))
        + float(sleep_snap["by_phase"].get("A4_dev_val", {}).get("cpu_seconds", 0.0))
        + float(sleep_snap["by_phase"].get("A4_dev_val_prune", {}).get("cpu_seconds", 0.0))
        + float(sleep_snap["by_phase"].get("A4_dev_diag", {}).get("cpu_seconds", 0.0))
    ) * (meter.cpu_usd_per_core_hour / 3600.0)
    a2_fixed_usd = float(sleep_snap["by_phase"].get("A2_PRIOR_ONLY_sleep", {}).get("llm_usd", 0.0)) + (
        float(sleep_snap["by_phase"].get("A2_compress", {}).get("cpu_seconds", 0.0))
    ) * (meter.cpu_usd_per_core_hour / 3600.0)

    n_eval_runs = len(seeds) * sum(len(suites[s]) for s in EVAL_SUITES)
    v_M_usd = (
        float(off_snap["by_phase"].get("A4_MG_UNPLUGGED", {}).get("cpu_seconds", 0.0))
        * (meter.cpu_usd_per_core_hour / 3600.0)
        / max(1, n_eval_runs)
    )

    amortization: Dict[str, Any] = {
        "fixed_A2_F_usd": round(a2_fixed_usd, 6),
        "fixed_A4_F_usd": round(a4_fixed_usd, 6),
        "v_M_offline_usd_per_task": round(v_M_usd, 8),
    }
    sh = prop.get("shadow_naked")
    if sh and sh["n_tasks"] > 0:
        v_L_usd = float(sh["total_usd"]) / float(sh["n_tasks"])
        amortization["v_L_naked_usd_per_task"] = round(v_L_usd, 6)
        amortization["break_even_N_star_A2"] = round(a2_fixed_usd / max(1e-9, v_L_usd - v_M_usd), 2)
        amortization["break_even_N_star_A4"] = round(a4_fixed_usd / max(1e-9, v_L_usd - v_M_usd), 2)
        amortization["shadow_solved"] = f"{sh['n_solved']}/{sh['n_tasks']}"
        by_arm_task: Dict[Tuple[str, str], List[int]] = {}
        for r in rows:
            by_arm_task.setdefault((r["arm"], r["task_id"]), []).append(int(r["gate_count"]))
        solved_recs = [r for r in sh["records"] if r["solved"] and r["gate_count"] is not None]
        if solved_recs:
            amortization["common_solved_mean_A6_naked"] = round(
                statistics.mean(float(r["gate_count"]) for r in solved_recs), 2
            )
            for ak in ("A0_BASE", "A1_ABC_XAG", "A2_PRIOR_ONLY", "A3_ZERO_LLM", "A4_MG_UNPLUGGED", "A5_SHAM"):
                amortization[f"common_solved_mean_{ak}"] = round(
                    statistics.mean(float(statistics.median(by_arm_task[(ak, r["task_id"])])) for r in solved_recs), 2
                )

    packet = {
        "manifest_version": "v2c",
        "manifest_sha256": man_sha,
        "budget": budget,
        "seeds": list(seeds),
        "arms": list(arms_all),
        "wall_seconds": round(time.perf_counter() - t0, 3),
        "proposer_provenance": {
            "model_alias": prop["proposer_model_alias"],
            "a2_models": prop["a2_call"]["models_used"],
            "a4_r1_models": prop["a4_calls"]["r1"]["models_used"],
            "a4_r2_models": prop["a4_calls"]["r2"]["models_used"],
            "a4_chosen": prop["a4_calls"]["chosen"],
        },
        "artifacts": {
            "A2_PRIOR_ONLY": art_a2.to_dict(),
            "A3_ZERO_LLM": art_a3.to_dict(),
            "A4_MG_UNPLUGGED": art_a4.to_dict(),
            "A5_SHAM": art_sham.to_dict(),
        },
        "amortization": amortization,
        "offline_meter": off_snap,
        "sleep_meter": sleep_snap,
        "summary": summary,
        "rows": rows,
    }

    # Strictly validate with hardened 3-seed tamper-evident reducer!
    verdict = verify_and_reduce(
        packet,
        expected_arms=arms_all,
        expected_suites=EVAL_SUITES,
        expected_seeds=seeds,
        suites_override=suites,
    )
    assert verdict["licenses_verdict"] is True

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    return packet


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 2C Full (L, T, S) Proposer & Unplugged Evaluator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_prop = sub.add_parser("propose")
    p_prop.add_argument("--model", default="opus")
    p_prop.add_argument("--out", required=True, type=Path)
    p_prop.add_argument("--budget", type=int, default=12000)
    p_prop.add_argument("--no-shadow", action="store_true")

    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("--proposals", required=True, type=Path)
    p_eval.add_argument("--out", required=True, type=Path)
    p_eval.add_argument("--budget", type=int, default=12000)

    args = parser.parse_args()
    if args.cmd == "propose":
        res = cmd_propose(model=args.model, out_path=args.out, run_shadow=not args.no_shadow, budget=args.budget)
        print(json.dumps({
            "manifest_sha256": res["manifest_sha256"],
            "wall_seconds": res["wall_seconds"],
            "a2_call": {k: v for k, v in res["a2_call"].items() if k != "rejected"},
            "a4_calls": res["a4_calls"],
            "shadow_solved": (
                f"{res['shadow_naked']['n_solved']}/{res['shadow_naked']['n_tasks']} (${res['shadow_naked']['total_usd']})"
                if res["shadow_naked"] else "skipped"
            ),
            "sleep_total_usd": res["sleep_meter"]["total_usd"],
        }, indent=2))
    else:
        pkt = cmd_evaluate(proposals_path=args.proposals, out_path=args.out, budget=args.budget)
        print(json.dumps({
            "manifest_sha256": pkt["manifest_sha256"],
            "wall_seconds": pkt["wall_seconds"],
            "n_rows": len(pkt["rows"]),
            "proposer_provenance": pkt["proposer_provenance"],
            "amortization": pkt["amortization"],
            "summary": {
                arm: {s: v["mean_median_gates"] for s, v in smap.items()}
                for arm, smap in pkt["summary"].items()
            },
        }, indent=2))


if __name__ == "__main__":
    main()
