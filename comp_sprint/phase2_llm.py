"""Step 3 — LLM Proposer Arms (A2_PRIOR_ONLY, A4_MG_UNPLUGGED, A6_SHADOW_NAKED) & Full 7-Arm Eval.

Two strictly separated subcommands:
  1. `propose`  -- Runs isolated `claude -p` calls for:
       * A2_PRIOR_ONLY   : 1 call given ONLY the XAG spec (zero tasks, zero traces).
       * A4_MG_UNPLUGGED : 2 sleep rounds inspecting DEV split ONLY (dev_structured +
                           dev_proc_shared; holdout 100% UNTOUCHED and UNMENTIONED).
       * A6_SHADOW_NAKED : Direct Claude + exact truth-table verifier tool (up to 2 tries/task)
                           on a predeclared 15-task holdout slice (5 per holdout stratum) for
                           the honest break-even amortization curve N* = F / (v_L - v_M).
  2. `evaluate` -- Runs 100% OFFLINE (LLM COMPLETELY UNPLUGGED!) across all 7 arms
                   (A0_BASE, A1_ABC_XAG, A2_PRIOR_ONLY, A3_ZERO_LLM, A4_MG_UNPLUGGED,
                   A5_SHAM_A3, A5_SHAM_A4) x 50 tasks x 3 paired seeds = 1,050 verified rows,
                   and validates end-to-end via `comp_sprint.reducer.verify_and_reduce`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from comp_sprint.benchmarks import BenchmarkTask, build_all_benchmarks, manifest_sha256
from comp_sprint.circuit import verify_truth_tables
from comp_sprint.industry_abc import synthesize_with_abc
from comp_sprint.library import (
    Artifact,
    build_sham_matched_library,
    mine_deterministic_library,
)
from comp_sprint.llm_proposer import (
    call_claude_isolated,
    compile_exprs_to_xag,
    extract_json_payload,
    parse_proposed_macros,
)
from comp_sprint.meter import WorkMeter
from comp_sprint.reducer import (
    compute_summary,
    evaluate_claim2_detector,
    make_row,
    verify_and_reduce,
)
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

XAG_SPEC_BLOCK = """
SUBSTRATE SPECIFICATION (XAG -- XOR-AND Graph with free wire inversions):
- Primitive 2-input gates: AND (&), XOR (^), plus free wire inversions (~). OR (a | b) costs 1 AND gate via ~(~a & ~b).
- Every macro you propose is FLATTENED to primitive {AND, XOR} gates with structural hashing (zero artificial gate discount!).
- Your library (up to 12 macros, each 2 <= n_inputs <= 4, 1 <= n_outputs <= 3, 2 <= gates <= 10) is used offline by a deterministic synthesizer in two ways:
  1. EXACT MACRO FUNCTIONAL FACTORIZATION (most powerful for multi-output circuits):
     Applies a multi-output macro M(w_1..w_k) -> (z_1..z_m) across layers whenever replacing consumed wires with Z
     STRICTLY reduces the number of reachable truth-table states |image(W')| < |image(W)| while preserving 100% of
     target output distinctions. Example: a 3-in 2-out Full Adder compresses 8 -> 4 states (2^3 -> 4); a 2-in 2-out
     Compare-And-Swap (a|b, a&b) compresses 4 -> 3 states. Composing these across layers solves multi-output circuits
     in dramatically fewer primitive gates than Davio decomposition!
  2. EXACT NPN4 / MULTI-OUTPUT k-CUT REWRITING (k <= 4):
     Matches any 3- or 4-input subfunction (modulo input permutation, input negation, and output negation) against
     single-output or 2-output macros in your library, accepting only strictly smaller flattened gate counts.

OUTPUT FORMAT (STRICT JSON ONLY):
Return a single JSON object with key "macros" containing a list of objects:
{
  "macros": [
    {
      "name": "short_snake_case_name",
      "n_inputs": 3,
      "exprs": ["(x0 ^ x1) ^ x2", "((x0 ^ x2) & (x1 ^ x2)) ^ x2"]
    }
  ]
}
Rules for `exprs`:
- Use ONLY variables x0..x{n_inputs-1}, constants 0/1, and bitwise Python operators &, |, ^, ~ with parentheses.
- Each macro must have 2 <= n_inputs <= 4, 1 <= len(exprs) <= 3, and 2..10 compiled gates.
- Do NOT include trivial 0-gate or 1-gate macros, duplicate truth tables, or constant outputs.
""".strip()


def _prompt_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _build_a2_prior_only_prompt() -> str:
    return (
        "You are proposing a general-purpose library of up to 12 reusable Boolean subcircuits (macros) "
        "purely from first principles and the substrate specification below. You are given NO specific "
        "tasks or benchmark traces.\n\n"
        + XAG_SPEC_BLOCK
        + "\n\nPropose up to 12 compact, high-leverage general-purpose macros (mix of state-compressing "
        "2- and 3-output cells plus key 3- and 4-input functions) that maximize flattened primitive gate "
        "reduction across diverse 4-to-6-input multi-output Boolean circuits. Return ONLY valid JSON."
    )


def _format_dev_diagnostics(
    suites: Dict[str, List[BenchmarkTask]],
    dev_scores: Dict[str, Tuple[int, int]],
    round1_scores: Dict[str, int] | None = None,
) -> str:
    lines = ["DEV SPLIT DIAGNOSTICS (20 dev tasks ONLY; holdout is sealed):"]
    lines.append("task_id                      | stratum     | in | out | BASE | ABC_XAG" + (" | R1_LIB" if round1_scores else "") + " | description")
    lines.append("-" * 105)
    for sname in DEV_SUITES:
        for t in suites[sname]:
            bg, ag = dev_scores[t.task_id]
            r1_col = f" | {round1_scores[t.task_id]:6d}" if round1_scores else ""
            lines.append(
                f"{t.task_id:28s} | {t.stratum:11s} | {t.n_inputs:2d} | {t.n_outputs:3d} | {bg:4d} | {ag:7d}{r1_col} | {t.description}"
            )
    # Include exact hex truth tables for the top-6 hardest / highest-headroom dev tasks
    hard = sorted(
        [t for s in DEV_SUITES for t in suites[s]],
        key=lambda t: (
            (round1_scores[t.task_id] if round1_scores else dev_scores[t.task_id][0]) - min(dev_scores[t.task_id][1], 10),
            dev_scores[t.task_id][0],
        ),
        reverse=True,
    )[:6]
    lines.append("\nEXACT TRUTH TABLES OF TOP-6 STUBBORN DEV TASKS (row r has x_k = (r >> k) & 1):")
    for t in hard:
        lines.append(f"  {t.task_id} (n_in={t.n_inputs}, n_out={t.n_outputs}): {[hex(x) for x in t.targets]}")
    return "\n".join(lines)


def _build_a4_round1_prompt(diag_text: str) -> str:
    return (
        "You are the sleep-phase abstraction proposer (Round 1 of 2) for a Boolean circuit synthesizer.\n"
        "Inspect the dev-split bottlenecks below and design up to 14 compact, reusable XAG macros that "
        "enable Exact Macro Functional Factorization and NPN4/multi-output cut rewriting to drop flattened "
        "primitive gate counts on BOTH structured multi-output circuits (arithmetic, sorting, comparators, "
        "S-boxes) AND procedural shared-cone multi-output DAGs.\n\n"
        + XAG_SPEC_BLOCK
        + "\n\n"
        + diag_text
        + "\n\nFocus on discovering genuine reusable state-compressing multi-output cells (2-to-2, 3-to-2, "
        "4-to-2, 4-to-3) and compact 4-input nonlinear/symmetric primitives that generalize beyond dev. "
        "Return ONLY valid JSON."
    )


def _build_a4_round2_prompt(
    diag_text: str,
    r1_macros: Sequence[Any],
    r1_rejected: Sequence[Dict[str, str]],
) -> str:
    m_lines = [
        f"  - {m.name}: in={m.n_inputs}, out={len(m.outputs)}, gates={len(m.gates)}, tt={[hex(x) for x in m.truth_tables]}"
        for m in r1_macros
    ]
    return (
        "You are the sleep-phase abstraction proposer (Round 2 of 2 -- Final Refinement).\n"
        "Review your Round-1 library's exact dev-split results below (`R1_LIB` vs `BASE` and `ABC_XAG`).\n"
        "Keep macros that produced real dev gate savings, replace dead-weight macros with sharper "
        "state-compressing multi-output cells or compact 4-input primitives targeting the remaining "
        "high-gate dev tasks (remember: final library is frozen at MAX 12 macros and evaluated OFFLINE "
        "with LLM UNPLUGGED on unseen holdout families).\n\n"
        + XAG_SPEC_BLOCK
        + "\n\nROUND-1 ACCEPTED MACROS:\n"
        + "\n".join(m_lines)
        + f"\nROUND-1 REJECTED COUNT: {len(r1_rejected)}\n\n"
        + diag_text
        + "\n\nEmit your FINAL refined library of up to 12 macros as strict JSON ONLY."
    )


def _run_shadow_naked_slice(
    suites: Dict[str, List[BenchmarkTask]],
    model: str,
    meter: WorkMeter,
    budget_per_task_usd: float = 0.50,
) -> Dict[str, Any]:
    """Arm A6_SHADOW_NAKED: Direct Claude + exact truth-table verifier tool (up to 2 tries/task)
    on a predeclared 15-task untouched holdout slice (5 structured, 5 proc_shared, 5 proc_rand)."""
    # Fixed deterministic slice BEFORE seeing any results: indices 0, 2, 4, 6, 8 of each holdout suite
    slice_tasks: List[Tuple[str, BenchmarkTask]] = []
    for sname in HOLDOUT_SUITES:
        for idx in (0, 2, 4, 6, 8):
            slice_tasks.append((sname, suites[sname][idx]))

    records: List[Dict[str, Any]] = []
    for sname, task in slice_tasks:
        n_rows = 1 << task.n_inputs
        # Compact truth table representation
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

        for attempt in range(2):
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
                    # Fair verifier tool feedback: report exact mismatch counts + up to 4 counterexample rows
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


def cmd_propose(model: str, out_path: Path, run_shadow: bool = True, budget: int = 8000) -> Dict[str, Any]:
    t0 = time.perf_counter()
    suites = build_all_benchmarks()
    man_sha = manifest_sha256(suites)
    meter = WorkMeter()

    # 1. Compute dev-only A0_BASE & A1_ABC diagnostics (ZERO holdout access!)
    dev_scores: Dict[str, Tuple[int, int]] = {}
    for sname in DEV_SUITES:
        for t in suites[sname]:
            cb = synthesize_with_library(t.n_inputs, t.targets, library=(), budget=budget, seed=0, meter=meter, phase="A4_dev_screen")
            ca = synthesize_with_abc(t.n_inputs, t.targets, meter=meter, phase="A4_dev_screen")
            dev_scores[t.task_id] = (cb.gate_count(), int(ca["xag_gates"]))

    # 2. Arm A2_PRIOR_ONLY: 1 isolated Claude call (spec ONLY, ZERO tasks!)
    p_a2 = _build_a2_prior_only_prompt()
    r_a2 = call_claude_isolated(p_a2, model=model, max_budget_usd=2.0)
    a2_macros, a2_rej = parse_proposed_macros(
        r_a2["text"], origin="claude_prior_only", max_macros=12,
        compress_exact=True, meter=meter, compress_phase="A2_compress"
    )
    meter.charge_llm_proposal(usd=r_a2["cost_usd"], accepted=len(a2_macros) > 0, phase="A2_PRIOR_ONLY_sleep")
    art_a2 = Artifact(arm="A2_PRIOR_ONLY", generation=1, macros=tuple(a2_macros))

    # 3. Arm A4_MG_UNPLUGGED Round 1 (DEV ONLY)
    diag_r1 = _format_dev_diagnostics(suites, dev_scores)
    p_a4_r1 = _build_a4_round1_prompt(diag_r1)
    r_a4_r1 = call_claude_isolated(p_a4_r1, model=model, max_budget_usd=2.0)
    a4_r1_macros, a4_r1_rej = parse_proposed_macros(
        r_a4_r1["text"], origin="claude_mg_r1", max_macros=14,
        compress_exact=True, meter=meter, compress_phase="A4_compress"
    )
    meter.charge_llm_proposal(usd=r_a4_r1["cost_usd"], accepted=len(a4_r1_macros) > 0, phase="A4_MG_sleep")

    # Screen Round-1 library strictly on DEV split (seed 0)
    r1_dev_scores: Dict[str, int] = {}
    for sname in DEV_SUITES:
        for t in suites[sname]:
            c1 = synthesize_with_library(
                t.n_inputs, t.targets, library=a4_r1_macros, budget=budget,
                seed=0, meter=meter, phase="A4_dev_screen"
            )
            r1_dev_scores[t.task_id] = c1.gate_count()

    # 4. Arm A4_MG_UNPLUGGED Round 2 Refinement (DEV ONLY)
    diag_r2 = _format_dev_diagnostics(suites, dev_scores, round1_scores=r1_dev_scores)
    p_a4_r2 = _build_a4_round2_prompt(diag_r2, a4_r1_macros, a4_r1_rej)
    r_a4_r2 = call_claude_isolated(p_a4_r2, model=model, max_budget_usd=2.0)
    a4_r2_macros, a4_r2_rej = parse_proposed_macros(
        r_a4_r2["text"], origin="claude_mg_r2", max_macros=12,
        compress_exact=True, meter=meter, compress_phase="A4_compress"
    )
    meter.charge_llm_proposal(usd=r_a4_r2["cost_usd"], accepted=len(a4_r2_macros) > 0, phase="A4_MG_sleep")

    # Pick strictly better dev artifact between R1[:12] and R2 (monotonic dev selection!)
    r2_dev_scores: Dict[str, int] = {}
    for sname in DEV_SUITES:
        for t in suites[sname]:
            c2 = synthesize_with_library(
                t.n_inputs, t.targets, library=a4_r2_macros, budget=budget,
                seed=0, meter=meter, phase="A4_dev_screen"
            )
            r2_dev_scores[t.task_id] = c2.gate_count()

    r1_total = sum(r1_dev_scores.values())
    r2_total = sum(r2_dev_scores.values())
    chosen_round = "R2" if (a4_r2_macros and r2_total <= r1_total) else "R1"
    final_a4_macros = a4_r2_macros if chosen_round == "R2" else a4_r1_macros[:12]
    art_a4 = Artifact(arm="A4_MG_UNPLUGGED", generation=1, macros=tuple(final_a4_macros))

    # 5. Optional A6_SHADOW_NAKED on predeclared 15-task holdout slice
    shadow_res = _run_shadow_naked_slice(suites, model=model, meter=meter) if run_shadow else None

    out_data = {
        "manifest_sha256": man_sha,
        "proposer_model_alias": model,
        "wall_seconds": round(time.perf_counter() - t0, 3),
        "a2_call": {
            "prompt_sha256": _prompt_hash(p_a2),
            "models_used": r_a2["models_used"],
            "cost_usd": r_a2["cost_usd"],
            "input_tokens": r_a2["input_tokens"],
            "output_tokens": r_a2["output_tokens"],
            "accepted_count": len(a2_macros),
            "rejected": a2_rej,
        },
        "a4_calls": {
            "r1": {
                "prompt_sha256": _prompt_hash(p_a4_r1),
                "models_used": r_a4_r1["models_used"],
                "cost_usd": r_a4_r1["cost_usd"],
                "input_tokens": r_a4_r1["input_tokens"],
                "output_tokens": r_a4_r1["output_tokens"],
                "accepted_count": len(a4_r1_macros),
                "rejected": a4_r1_rej,
                "dev_total_gates": r1_total,
            },
            "r2": {
                "prompt_sha256": _prompt_hash(p_a4_r2),
                "models_used": r_a4_r2["models_used"],
                "cost_usd": r_a4_r2["cost_usd"],
                "input_tokens": r_a4_r2["input_tokens"],
                "output_tokens": r_a4_r2["output_tokens"],
                "accepted_count": len(a4_r2_macros),
                "rejected": a4_r2_rej,
                "dev_total_gates": r2_total,
            },
            "chosen_round": chosen_round,
            "base_dev_total_gates": sum(v[0] for v in dev_scores.values()),
        },
        "artifacts": {
            "A2_PRIOR_ONLY": art_a2.to_dict(),
            "A4_MG_UNPLUGGED": art_a4.to_dict(),
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
    budget: int = 8000,
    seeds: tuple[int, ...] = (0, 1, 2),
) -> Dict[str, Any]:
    """100% OFFLINE (LLM COMPLETELY UNPLUGGED) 7-arm evaluation across all 50 tasks x 3 seeds."""
    t0 = time.perf_counter()
    prop = json.loads(proposals_path.read_text(encoding="utf-8"))
    suites = build_all_benchmarks()
    man_sha = manifest_sha256(suites)
    if prop["manifest_sha256"] != man_sha:
        raise ValueError("Proposals manifest SHA does not match current sealed benchmarks!")

    # Strictly reload and re-verify frozen LLM artifacts (ZERO LLM calls!)
    art_a2 = Artifact.from_dict(prop["artifacts"]["A2_PRIOR_ONLY"])
    art_a4 = Artifact.from_dict(prop["artifacts"]["A4_MG_UNPLUGGED"])

    meter = WorkMeter()
    rows: List[Dict[str, Any]] = []
    dev_circs_for_a3 = []

    # 1. A0_BASE
    for sname in EVAL_SUITES:
        for task in suites[sname]:
            for sd in seeds:
                c = synthesize_with_library(
                    task.n_inputs, task.targets, library=(), budget=budget,
                    seed=sd, meter=meter, phase="A0_BASE"
                )
                if sname in DEV_SUITES:
                    dev_circs_for_a3.append(c)
                rows.append(make_row(
                    arm="A0_BASE", suite=sname, task_id=task.task_id,
                    stratum=task.stratum, split=task.split, seed=sd,
                    n_inputs=task.n_inputs, n_outputs=task.n_outputs,
                    targets=task.targets, gate_count=c.gate_count(),
                    and_count=c.and_count(), xor_count=c.xor_count(),
                    verified_exact=True, circuit_sha256=c.sha256(),
                ))

    # 2. A3_ZERO_LLM (mined strictly on dev) + matched A5_SHAM_A4 (matched to A4's exact macro profile!)
    art_a3 = mine_deterministic_library(
        dev_circs_for_a3, max_macros=12, generation=1,
        compress_exact=True, meter=meter, phase="A3_sleep_mine"
    )
    art_a3 = Artifact.from_dict(art_a3.to_dict())
    art_sham = build_sham_matched_library(
        art_a4, seed=2026112301, compress_exact=True, meter=meter, phase="A5_sham_build"
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

    # 4. A1_ABC_XAG (Berkeley ABC 1.01 industry baseline)
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

    arms = ("A0_BASE", "A1_ABC_XAG", "A2_PRIOR_ONLY", "A3_ZERO_LLM", "A4_MG_UNPLUGGED", "A5_SHAM")
    summary = compute_summary(rows)

    # Compute exact amortization curve N* = F / (v_L - v_M) if shadow_naked ran
    amort = None
    shadow = prop.get("shadow_naked")
    if shadow and shadow.get("records"):
        a4_fixed_f = (
            float(prop["a4_calls"]["r1"]["cost_usd"])
            + float(prop["a4_calls"]["r2"]["cost_usd"])
            + float(prop["sleep_meter"]["cpu_usd"])
        )
        m_snap = meter.snapshot()
        a4_eval_cpu_usd = meter.cpu_usd(m_snap["by_phase"]["A4_MG_UNPLUGGED"]["cpu_seconds"])
        v_m = a4_eval_cpu_usd / (50 * len(seeds))

        solved_recs = [r for r in shadow["records"] if r["solved"]]
        v_l_all = shadow["total_usd"] / max(1, shadow["n_tasks"])
        # Compare A4_MG_UNPLUGGED median gates vs A6_SHADOW_NAKED gates on the EXACT common solved set
        a4_by_tid: Dict[str, List[int]] = {}
        for row in rows:
            if row["arm"] == "A4_MG_UNPLUGGED":
                a4_by_tid.setdefault(row["task_id"], []).append(int(row["gate_count"]))
        common_a6 = [int(r["gate_count"]) for r in solved_recs]
        common_a4 = [float(statistics.median(a4_by_tid[r["task_id"]])) for r in solved_recs]
        amort = {
            "fixed_crystallization_F_usd": round(a4_fixed_f, 6),
            "v_M_offline_usd_per_task": round(v_m, 8),
            "v_L_naked_usd_per_task": round(v_l_all, 6),
            "break_even_N_star": (
                round(WorkMeter.break_even_n(a4_fixed_f, v_l_all, v_m), 2)
                if WorkMeter.break_even_n(a4_fixed_f, v_l_all, v_m) is not None
                else None
            ),
            "shadow_solved": f"{shadow['n_solved']}/{shadow['n_tasks']}",
            "common_solved_mean_gates_A6_naked": round(statistics.mean(common_a6), 2) if common_a6 else None,
            "common_solved_mean_gates_A4_unplugged": round(statistics.mean(common_a4), 2) if common_a4 else None,
        }

    packet = {
        "manifest_sha256": man_sha,
        "budget": budget,
        "seeds": list(seeds),
        "arms": list(arms),
        "wall_seconds": round(time.perf_counter() - t0, 3),
        "proposer_provenance": {
            "model_alias": prop["proposer_model_alias"],
            "a2_models": prop["a2_call"]["models_used"],
            "a4_r1_models": prop["a4_calls"]["r1"]["models_used"],
            "a4_r2_models": prop["a4_calls"]["r2"]["models_used"],
            "a4_chosen_round": prop["a4_calls"]["chosen_round"],
        },
        "artifacts": {
            "A2_PRIOR_ONLY": art_a2.to_dict(),
            "A3_ZERO_LLM": art_a3.to_dict(),
            "A4_MG_UNPLUGGED": art_a4.to_dict(),
            "A5_SHAM": art_sham.to_dict(),
        },
        "amortization": amort,
        "offline_meter": meter.snapshot(),
        "sleep_meter": prop["sleep_meter"],
        "summary": summary,
        "rows": rows,
    }

    reduced = verify_and_reduce(
        packet,
        expected_arms=arms,
        expected_suites=EVAL_SUITES,
        expected_seeds=seeds,
    )
    assert reduced["licenses_verdict"] is True

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    return packet


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("propose")
    p1.add_argument("--model", default="opus")
    p1.add_argument("--out", required=True)
    p1.add_argument("--no-shadow", action="store_true")

    p2 = sub.add_parser("evaluate")
    p2.add_argument("--proposals", required=True)
    p2.add_argument("--out", required=True)

    args = ap.parse_args()
    if args.cmd == "propose":
        res = cmd_propose(model=args.model, out_path=Path(args.out), run_shadow=not args.no_shadow)
        print(json.dumps({
            "manifest_sha256": res["manifest_sha256"],
            "wall_seconds": res["wall_seconds"],
            "a2_call": res["a2_call"],
            "a4_calls": res["a4_calls"],
            "shadow_summary": (
                {k: v for k, v in res["shadow_naked"].items() if k != "records"}
                if res["shadow_naked"] else None
            ),
            "sleep_meter": res["sleep_meter"],
        }, indent=2))
    else:
        pkt = cmd_evaluate(proposals_path=Path(args.proposals), out_path=Path(args.out))
        print(json.dumps({
            "manifest_sha256": pkt["manifest_sha256"],
            "wall_seconds": pkt["wall_seconds"],
            "n_rows": len(pkt["rows"]),
            "proposer_provenance": pkt["proposer_provenance"],
            "amortization": pkt["amortization"],
            "summary": pkt["summary"],
        }, indent=2))
