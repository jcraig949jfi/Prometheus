"""Sprint 5 Track S5-Q Runner — 3rd Formal Substrate: Quantum/Reversible GL(n, F_2) CNOT Synthesis under ALL FOUR LAWS.

  - Law 1 + Law 4: `OpBudget v2` word-width deterministic metering (0.000 jitter + wall-clock parity!).
  - Law 2: Disjoint hidden validation splits `s5q_val_g1`, `s5q_val_g2`, `s5q_val_g3` (N=20 each) +
           exact paired Wilcoxon `p_less < 0.05` (att1) / `< 0.025` (att2).
  - Law 3: Compositional `LibModule` library + Matched-Op Causal Knockouts (`KO_MATCHED_LAST`, `KO_MATCHED_G2PLUS`).
  - Industry Baseline: Published Patel-Markov-Hayes (`A1_PMH`, 2008) O(n^2 / log n) quantum compiler!
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from comp_sprint.llm_proposer import call_claude_isolated
from comp_sprint.meter import WorkMeter
from comp_sprint2.phase3_compound import STRICT_JSON_SYSTEM_PROMPT
from comp_sprint2.reducer_s2 import compute_summary, make_row, verify_and_reduce
from comp_sprint2.sprint2_runner import _prompt_hash
from comp_sprint3.sandbox_s3 import CompositionalAlgoArtifact
from comp_sprint3.sprint3_runner import (
    _format_existing_library,
    _parse_compositional_proposal,
    paired_wilcoxon_stats,
)
from comp_sprint4.ko_matched import knockout_generations_generic
from comp_sprint5_quantum.s5q_benchmarks import build_s5q_benchmarks, s5q_manifest_sha256
from comp_sprint5_quantum.s5q_core import (
    DEFAULT_S5Q_WORD_BUDGET,
    build_s5q_a3_artifact,
    build_s5q_a5_sham_artifact,
    pmh_cnot_synth,
    synthesize_s5q_with_artifact,
)


S5Q_API_SPEC = """
SPRINT 5 TRACK S5-Q DETERMINISTIC COMPOSITIONAL QUANTUM CNOT SYNTHESIS API (ALL FOUR LAWS — OpBudget v2):
- Goal: Minimize exact primitive `CNOT` gate count (`len(circ.gates)`, ZERO discount!) to synthesize an
  exact invertible binary matrix `target_rows: Tuple[int, ...]` in GL(n, F_2) (`n = 12..18` qubits; bit c
  of row r is M[r, c]). Each gate `(ctrl, targ)` (`0 <= ctrl, targ < n`, `ctrl != targ`) applies row
  operation `row[targ] ^= row[ctrl]`, starting from identity `I_n` (`rows[i] = 1 << i`), until `rows == target_rows`.
- HARD LAW 1 + LAW 4 RULE: `time` is REMOVED! Every loop iteration AND every integer op > 64 bits charges
  exact 64-bit word-ops to `budget` (limit = 140,000 word-ops/task). Thus 0.000 jitter AND tight wall-clock parity!
  Never use `import`, dunder/private attributes, or bare `except:`.
- Available stdlib: `math`, `itertools`, `collections`, `Counter`, `defaultdict`, `deque`, `heapq`, `random`.
- Available `budget` methods: `budget.remaining()`, `budget.global_remaining()`, `budget.spent`, `budget.limit`.
- Available `lib` compositional runtime:
    * Every public `def fn(...)` in ANY module is exposed on `lib.<fn>(...)`.
    * `lib.run("fn_name", *args, op_cap=30000, **kwargs)` executes with a deterministic soft sub-cap.
    * Gen k modules CAN and SHOULD directly compose on top of Gen 0..k-1 helpers via `lib.<fn>(...)`!
- Available domain API (injected as globals):
    * `CNOTCircuit` (`.n_qubits`, `.gates`, `.gate_count()`, `.matrix_rows()`, `.sha256()`)
    * `make_circuit(gates) -> CNOTCircuit` (where `gates` is sequence of `(ctrl, targ)` pairs)
    * `apply_cnot_seq(gates, init_rows=None) -> Tuple[int, ...]`
    * `verify_cnot_circuit(circ) -> bool`
    * `gauss_synth(rows) -> CNOTCircuit` (standard Gauss-Jordan)
    * `pmh_synth(rows, m=3) -> CNOTCircuit` (Patel-Markov-Hayes 2008 block-Gaussian compiler!)
    * `invert_gf2(rows) -> Tuple[int, ...]` (exact GF(2) matrix inverse; note: reversing gates that reduce `M` to `I` builds `M`, and forward gates reducing `M^-1` to `I` ALSO build `M`!)
    * `transpose_gf2(rows) -> Tuple[int, ...]` (note: transposing & reversing `(c,t)->(t,c)` synthesizes `M^T`!)
    * `matrix_features(rows) -> dict` (`n_qubits, hamming_weight, density, diag_ones`)
    * `report_best(circ) -> bool` (ALWAYS call on improvements — verifies exact matrix equality & tracks monotonic best!)
    * `best_solution() -> CNOTCircuit`, `best_cost() -> int`
- Orchestrator signature MUST be:
    `def solve(circ, target_rows, seed, api, lib, budget):`
    returning `best_solution()`.
- MATHEMATICAL TIP: Reducing `M` to `I` via row ops `(c, t)` (`a[t] ^= a[c]`) gives a synthesis of `M` when reversed (`reversed(ops)`). Even better: reducing `M` to ANY **permutation matrix `P`** (or using column ops / bidirectional reduction from both `M` and `M^T` and `M^-1`!) and repairing the permutation with 3-CNOT swaps or finding optimal pivot/row-pair chains (Paar / Boyar-Peralta / Syndrome / Lookahead-2 / Beam / Peephole window rewriting) dramatically beats Patel-Markov-Hayes (PMH)!
"""


def _eval_split(tasks: Sequence[Any], art: Optional[CompositionalAlgoArtifact], word_budget: int, seed: int = 0) -> Tuple[int, Dict[str, int], Dict[str, Dict[str, Any]]]:
    total = 0
    per_task: Dict[str, int] = {}
    metas: Dict[str, Dict[str, Any]] = {}
    for t in tasks:
        c, m = synthesize_s5q_with_artifact(t.target_rows, artifact=art, seed=seed, word_budget=word_budget)
        cost = c.gate_count()
        total += cost
        per_task[t.task_id] = cost
        metas[t.task_id] = m
    return total, per_task, metas


def _summarize_telemetry(tasks, a0_costs, pmh_costs, cur_costs, cur_metas, word_budget):
    rows = []
    for t in tasks:
        m = cur_metas[t.task_id]
        rows.append((
            cur_costs[t.task_id], t.task_id, t.stratum, t.n_qubits, a0_costs[t.task_id], pmh_costs[t.task_id],
            m.get("ops_spent", 0), m.get("status", ""), m.get("mod_gate_drops", {}), m.get("cross_gen_calls", {}), m.get("fn_error_msgs", {}),
        ))
    rows.sort(reverse=True)
    lines = ["PER-TASK TRAINING TELEMETRY (sorted by hardest residual CNOT count):"]
    for cost, tid, strat, nq, c0, cp, ops, st, drops, xgen, ferrs in rows:
        lines.append(
            f"  - {tid} [{strat}, {nq}q]: cur={cost} (Gauss={c0}, PMH={cp}, vs_PMH={cost-cp:+d}), "
            f"word_ops={ops}/{word_budget} ({st}), drops={drops}, xgen={xgen}"
            + (f", fn_errs={ferrs}" if ferrs else "")
        )
    return "\n".join(lines)


def run_propose(out_path: Path, model: str = "opus", timeout_sec: int = 480, word_budget: int = DEFAULT_S5Q_WORD_BUDGET) -> Dict[str, Any]:
    suites = build_s5q_benchmarks()
    manifest_sha = s5q_manifest_sha256(suites)
    meter = WorkMeter()
    trace: List[Dict[str, Any]] = []
    ckpt: Dict[str, Any] = {}

    if out_path.exists():
        try:
            prev = json.loads(out_path.read_text(encoding="utf-8"))
            if prev.get("manifest_sha256") == manifest_sha:
                ckpt = prev
                trace = list(prev.get("llm_trace", []))
                print(f"[s5q] Loaded checkpoint keys={sorted(prev.get('artifacts', {}).keys())}", flush=True)
        except Exception:
            ckpt = {}

    artifacts: Dict[str, CompositionalAlgoArtifact] = {
        k: CompositionalAlgoArtifact.from_dict(d) for k, d in ckpt.get("artifacts", {}).items()
    }
    gen_records: Dict[str, Any] = dict(ckpt.get("generation_records", {}))

    def _save() -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps({
            "track": "S5Q_CNOT_COMP",
            "manifest_sha256": manifest_sha,
            "word_budget": word_budget,
            "artifacts": {k: v.to_dict() for k, v in artifacts.items()},
            "generation_records": gen_records,
            "llm_trace": trace,
            "sleep_meter": meter.snapshot(),
        }, indent=2), encoding="utf-8")

    # ---------------- GEN 0: A2_PRIOR_ONLY ----------------
    if "A2_PRIOR_ONLY" not in artifacts:
        p0 = (
            "You are designing a Compositional Executable Quantum CNOT Synthesis Library (GL(n, F_2), Generation 0: PRIOR-ONLY).\n"
            "You have ZERO access to benchmark tasks or telemetry.\n"
            f"{S5Q_API_SPEC}\n\n"
            "TASK (Generation 0 - Compiled Priors Only):\n"
            "Write 3 clean, modular, reusable Python library modules (each 40-100 lines) AND 1 orchestrator `solve`:\n"
            "  - Module 1: Reusable GF(2) matrix/circuit primitives (e.g. fast bitmask row/col ops, syndrome/distance\n"
            "    scoring, circuit commutation/cancellation peephole cleaner, M/M^-1/M^T adapters) reusable via `lib.<fn>`.\n"
            "  - Module 2: Constructive CNOT synthesis pass (e.g. greedy Hamming-distance / Boyar-Peralta / LU / PMH-variant).\n"
            "  - Module 3: Local circuit optimization / peephole cancellation / window resynthesis calling Module 1 via `lib.<fn>`.\n"
            "  - Orchestrator `solve(circ, target_rows, seed, api, lib, budget)`.\n"
            "Output ONLY raw JSON matching:\n"
            '{"new_modules": [{"name": "mod_g0_...", "rationale": "...", "source": "def ..."}], '
            '"orchestrator": {"name": "orch_g0", "rationale": "...", "source": "def solve(circ, target_rows, seed, api, lib, budget):\\n    ..."}}'
        )
        t0 = time.perf_counter()
        res = call_claude_isolated(p0, model=model, timeout_sec=timeout_sec, system_prompt=STRICT_JSON_SYSTEM_PROMPT)
        cost_usd = float(res["cost_usd"])
        meter.charge_cpu(time.perf_counter() - t0, phase="s5q_g0_prior")
        try:
            a2_raw, errs = _parse_compositional_proposal(res["text"], generation=0, origin="A2_PRIOR_ONLY", base_modules=())
            a2 = CompositionalAlgoArtifact("A2_PRIOR_ONLY", "S5Q_CNOT_COMP", 0, a2_raw.modules, a2_raw.orchestrator)
            meter.charge_llm_proposal(cost_usd, accepted=True, phase="s5q_g0_prior")
        except Exception:
            meter.charge_llm_proposal(cost_usd, accepted=False, phase="s5q_g0_prior")
            raise
        artifacts["A2_PRIOR_ONLY"] = a2
        pmh_v1 = sum(pmh_cnot_synth(t.target_rows).gate_count() for t in suites["s5q_val_g1"])
        v1_sum, _, v1_ms = _eval_split(suites["s5q_val_g1"], a2, word_budget=word_budget, seed=0)
        ferrs = sum(sum(m.get("fn_errors", {}).values()) for m in v1_ms.values())
        trace.append({"step": "A2_PRIOR_ONLY", "cost_usd": cost_usd, "models_used": res.get("models_used", []), "pmh_val_g1": pmh_v1, "val_g1_sum": v1_sum, "fn_errors": ferrs, "parse_errors": errs})
        gen_records["G0"] = {"artifact_sha256": a2.sha256(), "pmh_val_g1": pmh_v1, "val_g1_sum": v1_sum, "modules": [m.name for m in a2.modules], "fn_errors": ferrs}
        print(f"[s5q] G0 A2_PRIOR_ONLY built ({len(a2.modules)} mods, val_g1 PMH={pmh_v1} -> A2={v1_sum}, fn_errs={ferrs}, ${cost_usd:.3f})", flush=True)
        _save()

    # ---------------- GENERATIONS 1..3 ----------------
    current = artifacts["A2_PRIOR_ONLY"]
    for gen in (1, 2, 3):
        gk = f"G{gen}"
        if gk in artifacts:
            current = artifacts[gk]
            continue

        train_tasks = suites[f"s5q_train_g{gen}"]
        val_tasks = suites[f"s5q_val_g{gen}"]

        a0_tr_sum, a0_tr_costs, _ = _eval_split(train_tasks, None, word_budget=word_budget, seed=0)
        pmh_tr_costs = {t.task_id: pmh_cnot_synth(t.target_rows).gate_count() for t in train_tasks}
        cur_tr_sum, cur_tr_costs, cur_tr_metas = _eval_split(train_tasks, current, word_budget=word_budget, seed=0)
        cur_val_sum, cur_val_costs, _ = _eval_split(val_tasks, current, word_budget=word_budget, seed=0)

        telem = _summarize_telemetry(train_tasks, a0_tr_costs, pmh_tr_costs, cur_tr_costs, cur_tr_metas, word_budget)
        lib_text = _format_existing_library(current)

        promoted = False
        best_cand: Optional[CompositionalAlgoArtifact] = None
        best_val_stats: Dict[str, Any] = {}
        attempt_logs: List[Dict[str, Any]] = []
        prior_fail_note = ""

        for attempt in (1, 2):
            p_thresh = 0.05 if attempt == 1 else 0.025
            pg = (
                f"You are evolving a Compositional Executable Quantum CNOT Library (S5Q_CNOT_COMP) — Generation {gen}/3 (Attempt {attempt}/2).\n"
                f"{S5Q_API_SPEC}\n\n"
                f"{lib_text}\n\n"
                f"GENERATION {gen} TRAINING SET (`s5q_train_g{gen}`, 12 tasks; Gauss={a0_tr_sum}, PMH={sum(pmh_tr_costs.values())}, current={cur_tr_sum}):\n"
                f"{telem}\n\n"
                f"{prior_fail_note}"
                f"COMPOSITIONAL EVOLUTION OBJECTIVE (Generation {gen}):\n"
                f"1. DO NOT rewrite or duplicate existing Gen 0..{gen-1} modules — they remain intact in `lib`!\n"
                f"2. Write 1-2 NEW reusable Gen {gen} module(s) that DIRECTLY COMPOSE ON TOP OF existing `lib.<fn>(...)` helpers\n"
                f"   to attack genuine bottlenecks visible above across BOTH structured cryptographic diffusion layers AND\n"
                f"   100% uniform random GL(n, F_2) matrices (NEVER hardcode task names!).\n"
                f"   High-leverage quantum CNOT synthesis ideas: Boyar-Peralta / Paar / Xiang-Zeng-Lin distance-metric\n"
                f"   heuristics with 2-step lookahead; bidirectional (row + column / M and M^-1 and M^T) meet-in-the-middle\n"
                f"   reduction; beam search over top-K CNOT moves with incremental row-distance tables; permutation-free\n"
                f"   target reduction + optimal cycle-swap embedding; sliding-window subcircuit resynthesis & commutation\n"
                f"   peephole rewriting (re-synthesizing k-gate sub-windows with fewer CNOTs!).\n"
                f"3. Provide an updated `orchestrator` (`def solve(circ, target_rows, seed, api, lib, budget)`) preserving all\n"
                f"   Gen 0..{gen-1} strengths with smart deterministic `op_cap` allocation.\n"
                f"4. PROMOTION GATE (Law 2): Evaluated on HIDDEN disjoint 20-task `s5q_val_g{gen}`. Promoted ONLY IF\n"
                f"   net CNOTs < 0 AND exact paired Wilcoxon `p_less < {p_thresh}`!\n"
                "Output ONLY raw JSON matching:\n"
                '{"new_modules": [{"name": "mod_g' + str(gen) + '_...", "rationale": "...", "source": "def ..."}], '
                '"orchestrator": {"name": "orch_g' + str(gen) + '", "rationale": "...", "source": "def solve(circ, target_rows, seed, api, lib, budget):\\n    ..."}}'
            )
            t0 = time.perf_counter()
            res = call_claude_isolated(pg, model=model, timeout_sec=timeout_sec, system_prompt=STRICT_JSON_SYSTEM_PROMPT)
            cost_usd = float(res["cost_usd"])
            meter.charge_cpu(time.perf_counter() - t0, phase=f"s5q_g{gen}_att{attempt}")
            try:
                cand_raw, errs = _parse_compositional_proposal(res["text"], generation=gen, origin=f"G{gen}_att{attempt}", base_modules=current.modules)
                cand = CompositionalAlgoArtifact(gk, "S5Q_CNOT_COMP", gen, cand_raw.modules, cand_raw.orchestrator)
                cand_tr_sum, cand_tr_costs, cand_tr_metas = _eval_split(train_tasks, cand, word_budget=word_budget, seed=0)
                cand_val_sum, cand_val_costs, cand_val_metas = _eval_split(val_tasks, cand, word_budget=word_budget, seed=0)

                val_deltas = [cand_val_costs[t.task_id] - cur_val_costs[t.task_id] for t in val_tasks]
                vstats = paired_wilcoxon_stats(val_deltas)
                xgen_total = sum(sum(m.get("cross_gen_calls", {}).values()) for m in cand_val_metas.values())
                ferr_total = sum(sum(m.get("fn_errors", {}).values()) for m in cand_val_metas.values())

                passed = (vstats["sum_delta"] < 0) and (vstats["p_less"] < p_thresh)
                meter.charge_llm_proposal(cost_usd, accepted=passed, phase=f"s5q_g{gen}_att{attempt}")
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
                    f"[s5q] G{gen} att{attempt}: train {cur_tr_sum}->{cand_tr_sum} ({cand_tr_sum-cur_tr_sum:+d}), "
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
                        f"Design a CLEANER, HIGHER-LEVERAGE Gen {gen} upgrade!\n\n"
                    )
            except Exception as exc:
                meter.charge_llm_proposal(cost_usd, accepted=False, phase=f"s5q_g{gen}_att{attempt}")
                err_rec = {"attempt": attempt, "cost_usd": cost_usd, "error": str(exc)[:220], "passed_gate": False}
                attempt_logs.append(err_rec)
                trace.append({"step": f"G{gen}_att{attempt}", **err_rec})
                print(f"[s5q] G{gen} att{attempt} ERROR: {exc}", flush=True)
                prior_fail_note = f"PREVIOUS ATTEMPT 1 FAILED VALIDATION: {str(exc)[:180]}. Fix syntax/schema!\n\n"

        if promoted and best_cand is not None:
            current = CompositionalAlgoArtifact(gk, "S5Q_CNOT_COMP", gen, best_cand.modules, best_cand.orchestrator, parent_sha256=current.sha256())
        else:
            current = CompositionalAlgoArtifact(gk, "S5Q_CNOT_COMP", gen, current.modules, current.orchestrator, parent_sha256=current.sha256())
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
    """100% OFFLINE evaluation on 44 untouched GL(n, F_2) holdout tasks x 10 arms x 3 seeds = 1,320 rows."""
    prop = json.loads(proposal_path.read_text(encoding="utf-8"))
    suites = build_s5q_benchmarks()
    manifest_sha = s5q_manifest_sha256(suites)
    if prop["manifest_sha256"] != manifest_sha:
        raise ValueError("Manifest SHA mismatch!")
    word_budget = int(prop.get("word_budget", DEFAULT_S5Q_WORD_BUDGET))
    hold_suites = ("s5q_hold_struct", "s5q_hold_proc_dense", "s5q_hold_proc_circ")

    a2 = CompositionalAlgoArtifact.from_dict(prop["artifacts"]["A2_PRIOR_ONLY"])
    g1 = CompositionalAlgoArtifact.from_dict(prop["artifacts"]["G1"])
    g2 = CompositionalAlgoArtifact.from_dict(prop["artifacts"]["G2"])
    g3 = CompositionalAlgoArtifact.from_dict(prop["artifacts"]["G3"])
    gen_recs = prop.get("generation_records", {})
    promoted_gens = [g for g in (1, 2, 3) if gen_recs.get(f"G{g}", {}).get("promoted")]
    last_p = promoted_gens[-1] if promoted_gens else 1
    parent_of_last = a2 if last_p == 1 else (g1 if last_p == 2 else g2)

    ko_last = knockout_generations_generic(g3, {last_p}, "CNOTCircuit", "KO_MATCHED_LAST")
    ko_g2plus = knockout_generations_generic(g3, {2, 3}, "CNOTCircuit", "KO_MATCHED_G2PLUS")

    arm_specs: List[Tuple[str, Optional[CompositionalAlgoArtifact], Optional[CompositionalAlgoArtifact]]] = [
        ("A0_BASE", None, None),
        ("A1_PMH", None, None),
        ("A3_ZERO_LLM", build_s5q_a3_artifact(), None),
        ("A5_SHAM", build_s5q_a5_sham_artifact(), None),
        ("A2_PRIOR_ONLY", a2, None),
        ("G1", g1, None),
        ("G2", g2, None),
        ("G3", g3, None),
        ("KO_MATCHED_LAST", ko_last, parent_of_last),
        ("KO_MATCHED_G2PLUS", ko_g2plus, g1),
    ]

    # Law 1+4 Determinism Audit
    det_tasks = [suites[s][i] for s in hold_suites for i in range(2)]
    det_mismatches = 0
    for dt in det_tasks:
        c1, m1 = synthesize_s5q_with_artifact(dt.target_rows, g3, seed=0, word_budget=word_budget)
        c2, m2 = synthesize_s5q_with_artifact(dt.target_rows, g3, seed=0, word_budget=word_budget)
        if c1.gate_count() != c2.gate_count() or c1.sha256() != c2.sha256() or m1["ops_spent"] != m2["ops_spent"]:
            det_mismatches += 1
    assert det_mismatches == 0, f"LAW 1 VIOLATION on s5q: {det_mismatches} mismatches!"

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
                if arm_name == "A1_PMH":
                    cp = pmh_cnot_synth(t.target_rows)
                    icost, isha = cp.gate_count(), cp.sha256()
                    for sd in seeds:
                        rows.append(make_row(
                            arm=arm_name, suite=sname, task_id=t.task_id, stratum=t.stratum,
                            split=t.split, seed=sd, spec_sha256=spec_sha, cost=icost,
                            verified_exact=True, solution_sha256=isha,
                        ))
                else:
                    for sd in seeds:
                        c, meta = synthesize_s5q_with_artifact(t.target_rows, artifact=art, seed=sd, word_budget=word_budget, fallback_artifact=fb)
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
            f"[s5q eval] {arm_name:18s}: holdout_sum={hold_sum:7.1f} | wall={wall:6.2f}s | word_ops={agg_ops:9d} | xgen={sum(agg_xgen.values()):7d} | ferr={sum(agg_ferrs.values())}",
            flush=True,
        )

    summary = compute_summary(rows)
    packet = {
        "track": "S5Q_CNOT_COMP",
        "manifest_sha256": manifest_sha,
        "word_budget": word_budget,
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
    reduced = verify_and_reduce(
        packet,
        canonical_suites=suites,
        canonical_manifest_sha256=manifest_sha,
        expected_arms=[a for a, _, _ in arm_specs],
        expected_suites=list(hold_suites),
        expected_seeds=list(seeds),
    )
    assert reduced["summary"] == summary
    packet_out.parent.mkdir(parents=True, exist_ok=True)
    packet_out.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    print(f"[s5q eval] Wrote verified {len(rows)}-row packet to {packet_out} in {packet['total_eval_sec']:.2f}s", flush=True)
    return packet


def main() -> None:
    ap = argparse.ArgumentParser(description="Sprint 5 Track S5-Q Quantum CNOT Runner")
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
