"""Sprint 7 Track S7-CT Runner — Quantum Clifford+T T-Count Minimization vs Published T-par & TODD (Law 4b).

Evaluates whether compositional evolution under ALL FOUR LAWS (`OpBudget v3` word+container+call metering)
can beat BOTH published **Amy-Maslov-Mosca-Roetteler (`A1_TPAR`, 2014)** AND published **Heyfron-Campbell
(`A1_TODD`, 2018)** AND `A2_PRIOR_ONLY` on 44 untouched n=6..8 qubit fault-tolerant quantum circuits!
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
from comp_sprint7_clifford_t.s7_benchmarks import build_s7_benchmarks, s7_manifest_sha256
from comp_sprint7_clifford_t.s7_core import (
    DEFAULT_S7_V3_BUDGET,
    build_s7_a3_artifact,
    build_s7_a5_sham_artifact,
    optimize_s7_with_artifact,
    todd_baseline_optimize,
    tpar_fold_baseline,
)


S7_CLIFFORD_T_API_SPEC = """
SPRINT 7 TRACK S7-CT QUANTUM CLIFFORD+T T-COUNT OPTIMIZATION API (LAW 4b `OpBudget v3` = 1,600,000 UNITS/TASK):
- Goal: Minimize exact primitive **`T`-count** (`circ.t_count()`, count of `T` and `Tdg` gates; ZERO discount!)
  on `n = 6..8` qubit `{CNOT, T, Tdg, S, Sdg, Z}` quantum circuits while preserving 100% exact unitary equivalence
  across ALL `2^n` computational basis states (up to global phase, checked by `verify_clifford_t_circuit`).
- MATHEMATICAL STRUCTURE (Amy-Mosca 2019 / Heyfron-Campbell 2018 `TODD` / AlphaTensor-Quantum):
    * A circuit's `T`-gates correspond to a set `S_T` of distinct non-zero n-bit parity masks (`1 <= y < 2^n`).
    * ANY set `S_T` whose symmetric cubic tensor `T_{ijk} = sum_{y in S_T} y_i y_j y_k (mod 2)` AND quadratic
      `Q_{ij} = sum_{y in S_T} y_i y_j (mod 2)` AND linear `L_i = sum_{y in S_T} y_i (mod 2)` match the target
      completes into an EXACT unitary with `T`-count `<= len(S_T)` using ONLY free Clifford `{CNOT, S, Sdg, Z}`
      gates via `synthesize_from_t_parities(S_T)`!
    * Even more generally: `sum_{y in S_T} (y . x) (mod 8)` only needs to match the target phase modulo pure
      Clifford phases (`2*L_i*x_i + 4*Q_{ij}*x_i*x_j mod 8`) — i.e., `T_{ijk}` mod 2, `Q_{ij}` mod 2, and `L_i` mod 2
      (Wait: adding a `T` gate `y` with `y_i y_j y_k` changes `T` mod 2, `Q` mod 2, `L` mod 2; adding TWO identical
      `y` cancels mod 2 into a free Clifford `S` gate! Adding a 4D linear subspace `V\\{0}` (15 vectors) changes
      NOTHING mod 8!).
    * Published greedy `TODD` (`todd_optimize`) finds proper pairs `(a, b)` in `chi_z` that drop `-2` T-gates,
      but gets STUCK in local minima! Beating `TODD` (Claim 4 SOTA frontier!) comes from:
        1. Non-greedy / lookahead / beam / best-drop TODD pair selection (`-4`, `-6` multi-collision moves!),
        2. **Improper / zero-gain TODD moves & `RM(n-4, n)` / 4D-subspace kicks** (temporarily shifting parities
           or inserting a zero-cost `y, y` duplicate pair to unlock a deeper TODD cascade — FastTODD / AlphaTensor-Quantum!),
        3. **Symmetric 3-tensor Waring / low-rank slice decomposition** directly from `cubic_tensor_bitmask`
           (factorizing `T_{ijk}` into `x_q * Q_q(x)` quadratic slices + optimal 2-rank / 3-rank gadgets, then
           polishing with TODD!)!
- HARD LAW 1 + LAW 4b METERING (`OpBudget v3` = 1,600,000 units/task):
    * `time` is REMOVED! Loops=1, calls=3, big-int ops >64b=(bits-1)//64, dict/set=4+2*len, list/tuple=2+len, sorted=4+n*log2(n).
    * Write allocation-frugal Python (note: `cubic_tensor_bitmask` fits in ONE 64-bit int for n <= 8 -> 0 big-int surcharge!).
- Available stdlib: `math`, `itertools`, `collections`, `Counter`, `defaultdict`, `deque`, `heapq`, `random`.
- Available `budget`: `budget.remaining()`, `budget.global_remaining()`, `budget.spent`, `budget.limit`.
- Available `lib`: All public module functions exposed on `lib.<fn>(...)`; use `lib.run("fn", ..., op_cap=300000)`.
- Available domain API:
    * `CliffordTCircuit` (`.n_qubits`, `.gates`, `.t_count()`, `.cnot_count()`, `.sha256()`)
    * `extract_phase_poly(circ) -> (poly_dict, final_matrix)`
    * `synthesize_from_t_parities(t_parities) -> Optional[CliffordTCircuit]` (exact Clifford completion + verification!)
    * `verify_clifford_t_circuit(circ) -> bool`
    * `cubic_tensor_bitmask(parities) -> int` (exact C(n,3)-bit cubic tensor packed into <= 56 bits!)
    * `parity_cubic_signature(y) -> int` (exact <= 56-bit cubic contribution of single parity `y`!)
    * `solve_todd_step(parities, idx_a, idx_b) -> Optional[List[int]]` (exact Heyfron-Campbell `chi_z` solver!)
    * `tpar_fold(circ) -> CliffordTCircuit`, `todd_optimize(circ) -> CliffordTCircuit`, `t_features(parities) -> dict`
    * `report_best(cand) -> bool`, `best_solution() -> CliffordTCircuit`, `best_cost() -> int`
- Orchestrator signature MUST be: `def solve(circ, n_qubits, seed, api, lib, budget):`
- FORBIDDEN NAMES (STRICTLY AST-REJECTED!): NEVER use `import`, dunder/private names, bare `except:`, or ANY of `getattr`, `hasattr`, `setattr`, `delattr`, `type`, `vars`, `dir`, `eval`, `exec`, `compile`, `open`, `globals`, `locals`. To check if a lib function exists, use `lib.has("fn_name")` and call `lib.fn_name(...)` directly!
- NOTE: Your `A2_PRIOR_ONLY` and `G1..G3` solvers MUST beat `A1_TODD` (`todd_optimize(circ)`) AND random-restart TODD (`A5_SHAM`), so always ensure `todd_optimize(circ)` (or a superior fast TODD descent) is run or beat!
"""


def _eval_split(tasks, art, v3_budget, seed=0):
    total = 0
    per_task, metas = {}, {}
    for t in tasks:
        c, m = optimize_s7_with_artifact(t.circuit, artifact=art, seed=seed, v3_budget=v3_budget)
        cost = c.t_count()
        total += cost
        per_task[t.task_id] = cost
        metas[t.task_id] = m
    return total, per_task, metas


def _summarize_telem(tasks, tpar_costs, todd_costs, cur_costs, cur_metas, v3_budget):
    rows = []
    for t in tasks:
        m = cur_metas[t.task_id]
        rows.append((
            cur_costs[t.task_id], t.task_id, t.stratum, t.n_qubits, tpar_costs[t.task_id], todd_costs[t.task_id],
            m.get("ops_spent", 0), m.get("status", ""), m.get("mod_gate_drops", {}), m.get("cross_gen_calls", {}), m.get("fn_error_msgs", {}),
        ))
    rows.sort(reverse=True)
    lines = ["PER-TASK TRAINING TELEMETRY (sorted by hardest residual T-count):"]
    for cost, tid, strat, nq, ctp, ctd, ops, st, drops, xgen, ferrs in rows:
        lines.append(
            f"  - {tid} [{strat}, {nq}q]: cur={cost} (T-par={ctp}, TODD={ctd}, vs_TODD={cost-ctd:+d}), "
            f"v3_units={ops}/{v3_budget} ({st}), drops={drops}, xgen={xgen}"
            + (f", fn_errs={ferrs}" if ferrs else "")
        )
    return "\n".join(lines)


def run_propose(out_path: Path, model: str = "opus", timeout_sec: int = 480, v3_budget: int = DEFAULT_S7_V3_BUDGET) -> Dict[str, Any]:
    suites = build_s7_benchmarks()
    manifest_sha = s7_manifest_sha256(suites)
    meter = WorkMeter()
    trace: List[Dict[str, Any]] = []
    ckpt: Dict[str, Any] = {}

    if out_path.exists():
        try:
            prev = json.loads(out_path.read_text(encoding="utf-8"))
            if prev.get("manifest_sha256") == manifest_sha:
                ckpt = prev
                trace = list(prev.get("llm_trace", []))
                print(f"[s7] Loaded checkpoint keys={sorted(prev.get('artifacts', {}).keys())}", flush=True)
        except Exception:
            ckpt = {}

    artifacts: Dict[str, CompositionalAlgoArtifact] = {
        k: CompositionalAlgoArtifact.from_dict(d) for k, d in ckpt.get("artifacts", {}).items()
    }
    gen_records: Dict[str, Any] = dict(ckpt.get("generation_records", {}))

    def _save() -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps({
            "track": "S7_CLIFFORD_T",
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
            "You are designing a Compositional Executable Quantum Clifford+T T-Count Optimizer (Generation 0: PRIOR-ONLY under Law 4b).\n"
            "You have ZERO access to benchmark tasks or telemetry.\n"
            f"{S7_CLIFFORD_T_API_SPEC}\n\n"
            "TASK (Generation 0 - Compiled Priors Only):\n"
            "Write 3 lean, modular, reusable Python modules (40-100 lines each) AND 1 orchestrator `solve`:\n"
            "  - Module 1: Reusable parity-vector, cubic-tensor signature, and fast GF(2) nullspace/TODD-move helpers via `lib.<fn>`.\n"
            "  - Module 2: Best-gain / multi-collision TODD descent or symmetric 3-tensor constructive synthesis pass.\n"
            "  - Module 3: Local search / RM-codeword / plateau-kick TODD escape pass calling Module 1 via `lib.<fn>`.\n"
            "  - Orchestrator `solve(circ, n_qubits, seed, api, lib, budget)` calibrated to `1,600,000` v3 units.\n"
            "Output ONLY raw JSON matching:\n"
            '{"new_modules": [{"name": "mod_g0_...", "rationale": "...", "source": "def ..."}], '
            '"orchestrator": {"name": "orch_g0", "rationale": "...", "source": "def solve(circ, n_qubits, seed, api, lib, budget):\\n    ..."}}'
        )
        t0 = time.perf_counter()
        res = call_claude_isolated(p0, model=model, timeout_sec=timeout_sec, system_prompt=STRICT_JSON_SYSTEM_PROMPT)
        cost_usd = float(res["cost_usd"])
        meter.charge_cpu(time.perf_counter() - t0, phase="s7_g0_prior")
        try:
            a2_raw, errs = _parse_compositional_proposal(res["text"], generation=0, origin="A2_PRIOR_ONLY", base_modules=())
            if errs:
                raise ValueError(f"G0 module parse errors: {errs}")
            a2 = CompositionalAlgoArtifact("A2_PRIOR_ONLY", "S7_CLIFFORD_T", 0, a2_raw.modules, a2_raw.orchestrator)
            meter.charge_llm_proposal(cost_usd, accepted=True, phase="s7_g0_prior")
        except Exception:
            meter.charge_llm_proposal(cost_usd, accepted=False, phase="s7_g0_prior")
            raise
        artifacts["A2_PRIOR_ONLY"] = a2
        todd_v1 = sum(todd_baseline_optimize(t.circuit).t_count() for t in suites["s7_val_g1"])
        v1_sum, _, v1_ms = _eval_split(suites["s7_val_g1"], a2, v3_budget=v3_budget, seed=0)
        ferrs = sum(sum(m.get("fn_errors", {}).values()) for m in v1_ms.values())
        trace.append({"step": "A2_PRIOR_ONLY", "cost_usd": cost_usd, "models_used": res.get("models_used", []), "todd_val_g1": todd_v1, "val_g1_sum": v1_sum, "fn_errors": ferrs, "parse_errors": errs})
        gen_records["G0"] = {"artifact_sha256": a2.sha256(), "todd_val_g1": todd_v1, "val_g1_sum": v1_sum, "modules": [m.name for m in a2.modules], "fn_errors": ferrs}
        print(f"[s7] G0 A2_PRIOR_ONLY built ({len(a2.modules)} mods, val_g1 TODD={todd_v1} -> A2={v1_sum}, fn_errs={ferrs}, ${cost_usd:.3f})", flush=True)
        _save()

    # ---------------- GENERATIONS 1..3 ----------------
    current = artifacts["A2_PRIOR_ONLY"]
    for gen in (1, 2, 3):
        gk = f"G{gen}"
        if gk in artifacts:
            current = artifacts[gk]
            continue

        train_tasks = suites[f"s7_train_g{gen}"]
        val_tasks = suites[f"s7_val_g{gen}"]
        tpar_tr = {t.task_id: tpar_fold_baseline(t.circuit).t_count() for t in train_tasks}
        todd_tr = {t.task_id: todd_baseline_optimize(t.circuit).t_count() for t in train_tasks}
        cur_tr_sum, cur_tr_costs, cur_tr_metas = _eval_split(train_tasks, current, v3_budget=v3_budget, seed=0)
        cur_val_sum, cur_val_costs, _ = _eval_split(val_tasks, current, v3_budget=v3_budget, seed=0)
        telem = _summarize_telem(train_tasks, tpar_tr, todd_tr, cur_tr_costs, cur_tr_metas, v3_budget)
        lib_text = _format_existing_library(current)

        promoted = False
        best_cand: Optional[CompositionalAlgoArtifact] = None
        best_val_stats: Dict[str, Any] = {}
        attempt_logs: List[Dict[str, Any]] = []
        prior_fail_note = ""

        for attempt in (1, 2):
            p_thresh = 0.05 if attempt == 1 else 0.025
            pg = (
                f"You are evolving a Compositional Quantum Clifford+T T-Count Optimizer (S7_CLIFFORD_T) — Generation {gen}/3 (Attempt {attempt}/2).\n"
                f"{S7_CLIFFORD_T_API_SPEC}\n\n"
                f"{lib_text}\n\n"
                f"GENERATION {gen} TRAINING SET (`s7_train_g{gen}`, 12 tasks; T-par={sum(tpar_tr.values())}, TODD={sum(todd_tr.values())}, current={cur_tr_sum}):\n"
                f"{telem}\n\n"
                f"{prior_fail_note}"
                f"COMPOSITIONAL EVOLUTION OBJECTIVE (Generation {gen} — Beating Published TODD & Prior Library):\n"
                f"1. Keep all Gen 0..{gen-1} modules intact in `lib` and DIRECTLY COMPOSE on top of `lib.<fn>(...)`!\n"
                f"2. Attack genuine T-count bottlenecks across BOTH structured quantum circuits AND uniform random cubic tensors:\n"
                f"   - Direct symmetric 3-tensor Waring / factor-slice synthesis (splitting `T` by a pivot qubit `x_p` into\n"
                f"     a quadratic slice `Q_p` + residual `T'`, synthesizing `Q_p` via minimal rank-2/rank-3 parity gadgets!),\n"
                f"   - Full nullspace enumeration of `chi_z` (searching linear combinations of nullspace basis vectors for\n"
                f"     maximum multi-pair cancellations `-4`, `-6`, or zero-gain plateau walks escaping TODD local optima!),\n"
                f"   - Improper TODD / Reed-Muller `RM(n-4, n)` 4D-subspace (weight-15) & duplicate-pair (`y, y`) kicks\n"
                f"     followed by fast TODD descent, or beam search over TODD trajectories!\n"
                f"   - NEVER hardcode task names; stay allocation-frugal under Law 4b!\n"
                f"3. PROMOTION GATE (Law 2): Evaluated on HIDDEN disjoint 20-task `s7_val_g{gen}`. Promoted ONLY IF\n"
                f"   net T-count < 0 AND exact paired Wilcoxon `p_less < {p_thresh}`!\n"
                "Output ONLY raw JSON matching:\n"
                '{"new_modules": [{"name": "mod_g' + str(gen) + '_...", "rationale": "...", "source": "def ..."}], '
                '"orchestrator": {"name": "orch_g' + str(gen) + '", "rationale": "...", "source": "def solve(circ, n_qubits, seed, api, lib, budget):\\n    ..."}}'
            )
            t0 = time.perf_counter()
            res = call_claude_isolated(pg, model=model, timeout_sec=timeout_sec, system_prompt=STRICT_JSON_SYSTEM_PROMPT)
            cost_usd = float(res["cost_usd"])
            meter.charge_cpu(time.perf_counter() - t0, phase=f"s7_g{gen}_att{attempt}")
            try:
                cand_raw, errs = _parse_compositional_proposal(res["text"], generation=gen, origin=f"G{gen}_att{attempt}", base_modules=current.modules)
                if errs:
                    raise ValueError(f"Module validation errors: {errs}")
                cand = CompositionalAlgoArtifact(gk, "S7_CLIFFORD_T", gen, cand_raw.modules, cand_raw.orchestrator)
                cand_tr_sum, cand_tr_costs, _ = _eval_split(train_tasks, cand, v3_budget=v3_budget, seed=0)
                cand_val_sum, cand_val_costs, cand_val_metas = _eval_split(val_tasks, cand, v3_budget=v3_budget, seed=0)

                val_deltas = [cand_val_costs[t.task_id] - cur_val_costs[t.task_id] for t in val_tasks]
                vstats = paired_wilcoxon_stats(val_deltas)
                xgen_total = sum(sum(m.get("cross_gen_calls", {}).values()) for m in cand_val_metas.values())
                ferr_total = sum(sum(m.get("fn_errors", {}).values()) for m in cand_val_metas.values())

                passed = (vstats["sum_delta"] < 0) and (vstats["p_less"] < p_thresh)
                meter.charge_llm_proposal(cost_usd, accepted=passed, phase=f"s7_g{gen}_att{attempt}")
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
                    f"[s7] G{gen} att{attempt}: train {cur_tr_sum}->{cand_tr_sum} ({cand_tr_sum-cur_tr_sum:+d}), "
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
                meter.charge_llm_proposal(cost_usd, accepted=False, phase=f"s7_g{gen}_att{attempt}")
                err_rec = {"attempt": attempt, "cost_usd": cost_usd, "error": str(exc)[:220], "passed_gate": False}
                attempt_logs.append(err_rec)
                trace.append({"step": f"G{gen}_att{attempt}", **err_rec})
                print(f"[s7] G{gen} att{attempt} ERROR: {exc}", flush=True)
                prior_fail_note = f"PREVIOUS ATTEMPT 1 FAILED VALIDATION: {str(exc)[:180]}. Fix syntax/schema!\n\n"

        if promoted and best_cand is not None:
            current = CompositionalAlgoArtifact(gk, "S7_CLIFFORD_T", gen, best_cand.modules, best_cand.orchestrator, parent_sha256=current.sha256())
        else:
            current = CompositionalAlgoArtifact(gk, "S7_CLIFFORD_T", gen, current.modules, current.orchestrator, parent_sha256=current.sha256())
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
    """100% OFFLINE evaluation on 44 untouched Clifford+T circuits x 11 arms x 3 seeds = 1,452 rows."""
    prop = json.loads(proposal_path.read_text(encoding="utf-8"))
    suites = build_s7_benchmarks()
    manifest_sha = s7_manifest_sha256(suites)
    if prop["manifest_sha256"] != manifest_sha:
        raise ValueError("Manifest SHA mismatch!")
    v3_budget = int(prop.get("v3_budget", DEFAULT_S7_V3_BUDGET))
    hold_suites = ("s7_hold_struct", "s7_hold_proc_ccz", "s7_hold_proc_rand")

    a2 = CompositionalAlgoArtifact.from_dict(prop["artifacts"]["A2_PRIOR_ONLY"])
    g1 = CompositionalAlgoArtifact.from_dict(prop["artifacts"]["G1"])
    g2 = CompositionalAlgoArtifact.from_dict(prop["artifacts"]["G2"])
    g3 = CompositionalAlgoArtifact.from_dict(prop["artifacts"]["G3"])
    gen_recs = prop.get("generation_records", {})
    promoted_gens = [g for g in (1, 2, 3) if gen_recs.get(f"G{g}", {}).get("promoted")]
    last_p = promoted_gens[-1] if promoted_gens else 1
    parent_of_last = a2 if last_p == 1 else (g1 if last_p == 2 else g2)

    ko_last = knockout_generations_generic(g3, {last_p}, "CliffordTCircuit", "KO_MATCHED_LAST")
    ko_g2plus = knockout_generations_generic(g3, {2, 3}, "CliffordTCircuit", "KO_MATCHED_G2PLUS")

    arm_specs: List[Tuple[str, Optional[CompositionalAlgoArtifact], Optional[CompositionalAlgoArtifact]]] = [
        ("A0_BASE", None, None),
        ("A1_TPAR", None, None),
        ("A1_TODD", None, None),
        ("A3_ZERO_LLM", build_s7_a3_artifact(), None),
        ("A5_SHAM", build_s7_a5_sham_artifact(), None),
        ("A2_PRIOR_ONLY", a2, None),
        ("G1", g1, None),
        ("G2", g2, None),
        ("G3", g3, None),
        ("KO_MATCHED_LAST", ko_last, parent_of_last),
        ("KO_MATCHED_G2PLUS", ko_g2plus, g1),
    ]

    det_tasks = [suites[s][i] for s in hold_suites for i in range(2)]
    det_mismatches = 0
    for dt in det_tasks:
        c1, m1 = optimize_s7_with_artifact(dt.circuit, g3, seed=0, v3_budget=v3_budget)
        c2, m2 = optimize_s7_with_artifact(dt.circuit, g3, seed=0, v3_budget=v3_budget)
        if c1.t_count() != c2.t_count() or c1.sha256() != c2.sha256() or m1["ops_spent"] != m2["ops_spent"]:
            det_mismatches += 1
    assert det_mismatches == 0, f"LAW 1 VIOLATION on s7: {det_mismatches}"

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
                if arm_name == "A1_TPAR":
                    ct = tpar_fold_baseline(t.circuit)
                    for sd in seeds:
                        rows.append(make_row(arm=arm_name, suite=sname, task_id=t.task_id, stratum=t.stratum, split=t.split, seed=sd, spec_sha256=spec_sha, cost=ct.t_count(), verified_exact=True, solution_sha256=ct.sha256()))
                elif arm_name == "A1_TODD":
                    ct = todd_baseline_optimize(t.circuit)
                    for sd in seeds:
                        rows.append(make_row(arm=arm_name, suite=sname, task_id=t.task_id, stratum=t.stratum, split=t.split, seed=sd, spec_sha256=spec_sha, cost=ct.t_count(), verified_exact=True, solution_sha256=ct.sha256()))
                else:
                    for sd in seeds:
                        c, meta = optimize_s7_with_artifact(t.circuit, artifact=art, seed=sd, v3_budget=v3_budget, fallback_artifact=fb)
                        rows.append(make_row(arm=arm_name, suite=sname, task_id=t.task_id, stratum=t.stratum, split=t.split, seed=sd, spec_sha256=spec_sha, cost=c.t_count(), verified_exact=True, solution_sha256=c.sha256()))
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
        print(f"[s7 eval] {arm_name:18s}: holdout_T={hold_sum:7.1f} | wall={wall:6.2f}s | v3_ops={agg_ops:10d} | xgen={sum(agg_xgen.values()):7d} | ferr={sum(agg_ferrs.values())}", flush=True)

    summary = compute_summary(rows)
    packet = {
        "track": "S7_CLIFFORD_T",
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
    print(f"[s7 eval] Wrote verified {len(rows)}-row packet to {packet_out} in {packet['total_eval_sec']:.2f}s", flush=True)
    return packet


def main() -> None:
    ap = argparse.ArgumentParser(description="Sprint 7 Track S7-CT Quantum Clifford+T Runner")
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
