"""Sprint 9 Runner — Breaking the Exponential Barrier (`n = 12..16` Qubits, `N = 200` Untouched Holdout,
Polynomial Exact `O(m * n^3)` Verification, Scale-Adaptive Law 4b+4c Budget, 100% Tool-Less Isolation!).

Design Highlights:
  1. STRICT TOOL-LESS ISOLATION: `_call_claude_isolated` enforces `--tools ""` inside an empty
     `tempfile.TemporaryDirectory` (zero workspace file/shell access, locked by unit test!).
  2. EXACT POLYNOMIAL VERIFICATION & CLIFFORD COMPLETION: Works natively on `n = 12..16` qubits
     (`2^16 = 65,536` basis states!) with zero exponential simulation cost.
  3. SCALE-ADAPTIVE LAW 4b+4c BUDGET: `s9_budget_for_n(n) = 35_000 * C(n, 2)` (`2.31M` at `n=12`
     to `4.20M` at `n=16`), keeping exact compute-proportional parity as `n` scales!
  4. ZERO-SHOT TRANSFER OF `S8_G2_FLAT_KICK`: Frozen Sprint 8 `mod_g2_escape` is embedded directly
     as a benchmark arm alongside `A1_TODD_2018`, `A1_FAST_TODD_2022`, full-budget `A5_SHAM`,
     full-budget `A2_PRIOR_ONLY`, `G1..G4`, and `KO_MATCHED_LAST`!
  5. COMPOSITIONAL COMPOUNDING GATE: Each generation `G1..G4` is prompted to compose on existing
     library helpers (`lib.<fn>(...)`), passing Law 2 disjoint paired Wilcoxon (`p_less < 0.05` /
     `< 0.025` Bonferroni on retry) across 25 unseen `n = 12..16` validation circuits!
"""
from __future__ import annotations

import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from comp_sprint.meter import WorkMeter
from comp_sprint2.reducer_s2 import compute_summary, make_row, verify_and_reduce
from comp_sprint3.sandbox_s3 import CompositionalAlgoArtifact, LibModule
from comp_sprint3.sprint3_runner import paired_wilcoxon_stats
from comp_sprint8_science.s8_runner import build_s8_a5_sham_artifact
from comp_sprint9_poly_scale.s9_benchmarks import S9Task, build_s9_benchmarks, s9_manifest_sha256
from comp_sprint9_poly_scale.s9_poly_core import (
    fast_todd_2022_poly_optimize,
    run_s9_artifact,
    s9_budget_for_n,
    todd_2018_poly_optimize,
    tpar_poly_optimize,
)

DEFAULT_MODEL = "claude-opus-5-5"


def _call_claude_isolated(prompt: str, model: str = DEFAULT_MODEL, timeout_s: int = 420) -> Tuple[Dict[str, Any], float, str]:
    """100% tool-less isolated Claude CLI call (`--tools ""` in empty temp dir) — ZERO file/shell access!"""
    env = dict(os.environ)
    env.pop("CLAUDECODE", None)
    cmd = [
        "claude", "-p",
        "--model", model,
        "--output-format", "json",
        "--no-session-persistence",
        "--tools", "",
    ]
    with tempfile.TemporaryDirectory(prefix="prometheus_s9_iso_") as tmpdir:
        proc = subprocess.run(
            cmd, input=prompt, capture_output=True, text=True, timeout=timeout_s, env=env, cwd=tmpdir, check=False
        )
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI failed (rc={proc.returncode}): {proc.stderr[:400]}")
    meta = json.loads(proc.stdout)
    cost_usd = float(meta.get("total_cost_usd", 0.0))
    raw_text = str(meta.get("result", ""))
    m = re.search(r"```json\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    if m:
        body = m.group(1)
    else:
        i0 = raw_text.find("{")
        i1 = raw_text.rfind("}")
        if i0 < 0 or i1 <= i0:
            raise ValueError(f"No JSON object in claude output: {raw_text[:300]}")
        body = raw_text[i0 : i1 + 1]
    return json.loads(body), cost_usd, raw_text


S9_API_DOC = """
EXECUTION ENVIRONMENT & API CONTRACT (SPRINT 9 — `n = 12..16` QUBITS, SCALE-ADAPTIVE LAW 4b + LAW 4c):
- Domain: Large-scale Fault-Tolerant Quantum `Clifford+T` T-count minimization on `n = 12..16` qubits
  (`2^16 = 65,536` Hilbert space!), verified 100% EXACTLY in polynomial time `O(m * n^3)` via Z/8Z `(L, Q, T)` parity tensors.
- Scale-Adaptive Budget: `v3_budget = api["v3_budget"] = 35_000 * C(n, 2)` (`2.31M` at n=12, `3.18M` at n=14, `4.20M` at n=16).
  * Metered costs: loops=1, calls=3, big-int >64b=(bits-1)//64, dict/set=4+2*len, list/tuple=2+len, sorted=4+n*log2(n).
  * Law 4c exact compute-proportional helper charges:
      - `api["chi_z_cols"](P, z)` -> exact C(n, 2)-bit necessary & sufficient involutive `chi_z` columns (`66..120` bits for `n=12..16`!). Charges `len(P) * (C(n,2) + 4) + 12`.
      - `api["nullspace_gf2"](cols)` -> GF(2) nullspace basis of `cols` (each vector is a `len(P)`-bit int mask!). Charges `len(cols) * (C(n,2) + 8*words) + 16`.
      - `api["apply_shift"](P, y_mask, z)` -> applies exact TODD shift & reduces duplicates mod 2. Charges `4 * len(P) + 8`.
      - `api["reduce_parities"](P)` -> cancels duplicates mod 2 and drops 0. Charges `3 * len(P) + 4`.
      - `api["submit_best"](P, tag)` -> exact polynomial `(L, Q, T)` check + updates best if `len(P)` improved!
      - `api["rem_budget"]()` -> remaining `v3_ops`.
      - `api["n_qubits"]` (12..16), `api["init_parities"]` (list[int]), `api["seed"]` (int), `api["v3_budget"]` (int).
- CRITICAL SCALING REALITY AT `n = 12..16`:
  * `2^16 = 65,536` — NEVER build dense `2^n` tables! Use ONLY sparse `O(m^2)` pairwise XORs `z = P[i] ^ P[j]`.
  * At `n = 12..16`, `m = len(P)` is ~35..75 and `C(n, 2) = 66..120`, so ONE `chi_z_cols + nullspace_gf2` call costs ~`7,000..18,000` `v3_ops`!
  * Therefore budget allows ~`180..320` total `chi_z` calls per task — **EVERY SINGLE `chi_z` CALL MUST COUNT!**
  * High-leverage ideas at `n = 12..16`:
      1. **Priority shift ranking & exact `2*c + 2 <= best_gain` pruning** (avoid wasting `chi_z` calls on multiplicity-1 shifts `c == 1`!).
      2. **Zero-`chi_z`-cost Reed-Muller `RM(n-4, n)` Affine 4-Flat (`weight 15/16`) & 5-Flat (`weight 31/32`) Greedy Majority-Voting Moves!** Notice: voting on `d = f ^ p` to build an affine 4-flat `F` costs **ZERO `chi_z` calls** (`O(m)` Python ops!) and can directly reduce `T`-count OR tunnel to a strictly better TODD basin!
      3. **Checking multiple nullspace basis combinations (`b`, `b1 ^ b2`, Gray-code subset)** per `chi_z` call (since `apply_shift` costs only `~200` ops vs `12,000` ops for `chi_z` — **60× cheaper**, amortizing every `chi_z` call aggressively!).
      4. **Support-filtering `U = {i : P[i] == z or (P[i] ^ z) in P}`** before trying basis vectors (only basis vectors `b` with `b & U != 0` can ever cancel a pair!).
- CRITICAL AST SANDBOX RULES:
  * NO `import` statements!
  * FORBIDDEN builtins: `getattr`, `hasattr`, `setattr`, `delattr`, `eval`, `exec`, `compile`, `open`, `__import__`, `globals`, `locals`, `vars`, `type`, `object`, `super`, `dir`, `chr`, `ord`.
  * Use `lib.has("fn_name")` to check library functions — NEVER `hasattr`/`getattr`!
  * Keep safety floor `rem_budget() > max(80000, v3_budget // 25)` so `submit_best` always completes cleanly with `fn_errors == 0`!
"""


def _build_artifact(
    prop: Dict[str, Any],
    gen: int,
    parent: Optional[CompositionalAlgoArtifact],
    arm: str,
) -> CompositionalAlgoArtifact:
    mods: List[LibModule] = list(parent.modules) if parent is not None else []
    new_raw = prop.get("new_modules") or prop.get("modules") or []
    if not isinstance(new_raw, list) or not new_raw:
        raise ValueError("Proposal must provide `new_modules`!")
    existing = {m.name for m in mods}
    for mr in new_raw:
        mn = str(mr["name"]).strip()
        if mn in existing:
            mn = f"{mn}_g{gen}"
        existing.add(mn)
        mods.append(
            LibModule.from_source(
                name=mn,
                generation=gen,
                source=str(mr["source"]),
                origin=f"s9_g{gen}",
                rationale=str(mr.get("rationale", ""))[:200],
            )
        )
    orch_src = str(prop["orchestrator_source"])
    if "def solve(" not in orch_src and "def optimize(" in orch_src:
        orch_src = orch_src.replace("def optimize(", "def solve(", 1)
    orch = LibModule.from_source(
        name="orchestrator",
        generation=gen,
        source=orch_src,
        required_fn="solve",
        origin=f"s9_g{gen}",
        rationale=str(prop.get("rationale", ""))[:250],
    )
    return CompositionalAlgoArtifact(
        arm=arm,
        track="S9_POLY_SCALE_CLIFFORD_T",
        generation=gen,
        modules=tuple(mods),
        orchestrator=orch,
        parent_sha256=parent.sha256() if parent is not None else None,
    )


def _eval_split(art: CompositionalAlgoArtifact, tasks: Sequence[S9Task], seeds: Sequence[int] = (0,)) -> Dict[str, Any]:
    t0 = time.perf_counter()
    per_task: Dict[str, float] = {}
    tot_ops = 0
    tot_cap = 0
    xgen: Dict[str, int] = {}
    ferr: Dict[str, int] = {}
    fallbacks = 0
    for task in tasks:
        cap = s9_budget_for_n(task.n_qubits)
        cs = []
        for sd in seeds:
            circ, tel = run_s9_artifact(art, task.circuit, seed=sd, v3_budget=cap)
            cs.append(circ.t_count())
            tot_ops += int(tel.get("ops_spent", 0))
            tot_cap += cap
            if tel.get("verifier_fallback"):
                fallbacks += 1
            for k, v in tel.get("cross_gen_calls", {}).items():
                xgen[k] = xgen.get(k, 0) + int(v)
            for k, v in tel.get("fn_errors", {}).items():
                ferr[k] = ferr.get(k, 0) + int(v)
        per_task[task.task_id] = float(statistics.median(cs))
    return {
        "total_t": sum(per_task.values()),
        "per_task": per_task,
        "wall_sec": round(time.perf_counter() - t0, 2),
        "avg_ops_frac": round(tot_ops / max(1, tot_cap), 4),
        "total_ops": tot_ops,
        "cross_gen_calls": xgen,
        "fn_errors": ferr,
        "fallbacks": fallbacks,
    }


def _diagnose_parent(parent: CompositionalAlgoArtifact, diag_tasks: Sequence[S9Task], ft_scores: Dict[str, int]) -> str:
    res = _eval_split(parent, diag_tasks, seeds=(0,))
    lines = [
        f"CURRENT PARENT `{parent.arm}` (gen={parent.generation}) ON `dev_diag` (N={len(diag_tasks)}, n=12..16):",
        f"  - Total T-gates: {res['total_t']:.0f} (Published FastTODD 2022 = {sum(ft_scores[t.task_id] for t in diag_tasks)})",
        f"  - Avg v3_budget utilization: {res['avg_ops_frac']*100:.1f}% | wall: {res['wall_sec']:.2f}s | fn_errors: {res['fn_errors']} | cross_gen_calls: {res['cross_gen_calls']}",
        "  - Existing library modules (MUST COMPOSE BY CALLING VIA `lib.<fn>(...)`!):",
    ]
    for m in parent.modules:
        lines.append(f"      * g{m.generation}:{m.name} exports={list(m.exported_fns)} ({len(m.source.splitlines())}L)")
    by_q = {q: (sum(res["per_task"][t.task_id] for t in diag_tasks if t.n_qubits == q), sum(ft_scores[t.task_id] for t in diag_tasks if t.n_qubits == q)) for q in (12, 13, 14, 15, 16)}
    lines.append(f"  - By qubit count (Parent vs FastTODD): {by_q}")
    ranked = sorted(diag_tasks, key=lambda t: (res["per_task"][t.task_id] - ft_scores[t.task_id], res["per_task"][t.task_id]), reverse=True)
    lines.append("  - Hardest diagnostic tasks:")
    for t in ranked[:8]:
        lines.append(f"      * {t.task_id} (n={t.n_qubits}, {t.family}): T-par={t.tpar_t}, FastTODD={ft_scores[t.task_id]}, Parent={res['per_task'][t.task_id]:.0f}")
    return "\n".join(lines)


def evolve_s9_proposals(out_path: Path, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    suites = build_s9_benchmarks()
    msha = s9_manifest_sha256(suites)
    meter = WorkMeter()
    llm_trace: List[Dict[str, Any]] = []
    gen_records: List[Dict[str, Any]] = []

    diag_tasks = suites["dev_diag"]
    ft_diag = {t.task_id: fast_todd_2022_poly_optimize(t.circuit).t_count() for t in diag_tasks}
    print(f"[S9 EVOLVE] Manifest {msha[:16]}... | dev_diag FastTODD(n=12..16)={sum(ft_diag.values())}", flush=True)

    # ---------------- G0: FULL-BUDGET A2_PRIOR_ONLY ----------------
    g0_art: Optional[CompositionalAlgoArtifact] = None
    for att in (1, 2):
        extra = "" if att == 1 else "\nPREVIOUS ATTEMPT FAILED OR UNDER-UTILIZED BUDGET! Keep code concise, zero AST errors, >=50% budget usage!"
        p_g0 = f"""Design Generation 0 (`A2_PRIOR_ONLY`) — a clean, FULL-BUDGET compiled prior solver for large `n = 12..16` qubit Quantum `Clifford+T` T-count minimization.
{S9_API_DOC}
REQUIREMENT FOR G0 (`A2_PRIOR_ONLY`):
- Build 2–3 clean, modular, reusable library modules (`mod_g0_rng`, `mod_g0_todd`, `mod_g0_search`) that:
  1. Perform sparse pairwise-XOR `chi_z` TODD descent (prioritizing shifts `z` by multiplicity `c >= 2`, filtering nullspace basis vectors by active collision support `U`, checking basis vectors + pairwise XORs to amortize each `chi_z` call!),
  2. Use the FULL `v3_budget` (>= 60% utilization!) with perturbations/restarts and `api["submit_best"]` on every improvement,
  3. Export clean, well-documented helper functions so future generations (`G1..G4`) can directly call `lib.<fn>(...)` to compound compositionally!
{extra}

Return STRICT JSON ONLY:
```json
{{
  "rationale": "brief explanation",
  "new_modules": [
    {{"name": "mod_g0_...", "rationale": "...", "source": "def fn1(...): ..."}}
  ],
  "orchestrator_source": "def solve(api, lib, budget): ..."
}}
```"""
        t0 = time.perf_counter()
        cost = 0.0
        try:
            prop, cost, _ = _call_claude_isolated(p_g0, model=model)
            art = _build_artifact(prop, gen=0, parent=None, arm="A2_PRIOR_ONLY")
            ev = _eval_split(art, diag_tasks, seeds=(0,))
            dt = time.perf_counter() - t0
            ok = (len(ev["fn_errors"]) == 0 and ev["fallbacks"] == 0 and ev["avg_ops_frac"] >= 0.45)
            meter.charge_cpu(dt, phase=f"s9_g0_att{att}")
            meter.charge_llm_proposal(cost, accepted=ok, phase=f"s9_g0_att{att}")
            llm_trace.append({"phase": f"s9_g0_att{att}", "cost_usd": cost, "accepted": ok, "diag_t": ev["total_t"], "ops_frac": ev["avg_ops_frac"], "ferr": ev["fn_errors"]})
            print(f"[S9 G0 att{att}] diag_T={ev['total_t']:.0f} (FastTODD={sum(ft_diag.values())}) | ops={ev['avg_ops_frac']*100:.1f}% | wall={ev['wall_sec']}s | ok={ok} | ${cost:.3f}", flush=True)
            if ok or att == 2:
                g0_art = art
                if ok:
                    break
        except Exception as exc:
            dt = time.perf_counter() - t0
            meter.charge_cpu(dt, phase=f"s9_g0_att{att}")
            meter.charge_llm_proposal(cost, accepted=False, phase=f"s9_g0_att{att}")
            llm_trace.append({"phase": f"s9_g0_att{att}", "cost_usd": cost, "error": str(exc)[:300]})
            print(f"[S9 G0 att{att}] ERROR: {exc}", flush=True)

    assert g0_art is not None, "Failed to build S9 G0!"
    artifacts: Dict[str, CompositionalAlgoArtifact] = {"A2_PRIOR_ONLY": g0_art}
    gen_records.append({"gen": 0, "name": "A2_PRIOR_ONLY", "promoted": None, "modules": [f"g{m.generation}:{m.name}" for m in g0_art.modules]})
    current = g0_art

    # ---------------- G1..G4: 4 TRUE COMPOSITIONAL GENERATIONS (REQUIRING `lib.<fn>` REUSE!) ----------------
    gen_themes = {
        1: "Amortized Multi-Vector Nullspace Descent + Exact `2*c + 2` Branch-and-Bound: Add `mod_g1_deep_null` that CALLS G0's helpers (`lib.<fn>(...)`) and upgrades every expensive `chi_z` call by (a) computing exact `2*c + 2 <= best_gain` pruning over multiplicity-sorted shifts, (b) filtering nullspace vectors onto active support `U`, and (c) evaluating fast O(1) incremental size deltas across Gray-code combinations of top active nullspace vectors (finding `-4/-6/-8` multi-pair drops per single `chi_z` call without wasting `apply_shift` calls!).",
        2: "Zero-`chi_z`-Cost Reed-Muller `RM(n-4, n)` Greedy Majority-Voting Affine 4-Flat Decoder: Add `mod_g2_rm_flat` that CALLS G1/G0 descent helpers via `lib.<fn>(...)` AND performs zero-`chi_z`-cost greedy majority-voting affine 4-flat (`2->4->8->16`) codeword construction maximizing overlap `|F intersect P|` — BOTH as a direct `T`-reducing pass (`2k - w > 0`) BEFORE/AFTER TODD descent AND as low-energy tunneling kicks (`2k - w >= -2`) into new basins!",
        3: "Higher-Order & Coupled Escape (`RM` Multi-Flat + Visited-Set Nullspace Plateau Walk): Add `mod_g3_coupled_escape` that COMPOSES BOTH G2's affine 4-flat decoder AND G1/G0's deep nullspace descent via `lib.<fn>(...)` — combining (a) visited-set zero-gain (`g == 0`) nullspace plateau stepping, (b) targeted 2-flat/3-flat seed selection from high-degree parity cliques for `RM(n-4, n)` 4-flat expansion, and (c) adaptive budget allocation spending more search on larger `n = 14..16` tasks!",
        4: "Elite-Archive Compositional Portfolio & Scale-Aware Hybrid Refinement: Add `mod_g4_elite_portfolio` that COMPOSES ALL surviving earlier generations (`G3/G2/G1/G0` via `lib.<fn>(...)`) — maintaining a small elite pool of distinct minimum-T parity representations, applying symmetric-difference / common-subset guided RM 4-flat kicks across elite states, and running final greedy polish with remaining budget!",
    }

    for g in (1, 2, 3, 4):
        val_tasks = suites[f"val_g{g}"]
        parent_val = _eval_split(current, val_tasks, seeds=(0,))
        diag_str = _diagnose_parent(current, diag_tasks, ft_diag)
        promoted = False
        best_cand: Optional[CompositionalAlgoArtifact] = None
        best_w: Dict[str, Any] = {}
        last_err = ""

        for att in (1, 2):
            p_thresh = 0.05 if att == 1 else 0.025
            retry_note = f"\nRETRY (Bonferroni gate p_less < 0.025): Attempt 1 failed: {last_err}" if att == 2 else ""
            prompt = f"""You are evolving Generation {g} (`G{g}`) on top of `{current.arm}` for large-scale `n = 12..16` qubit Quantum `Clifford+T` T-count minimization.
{S9_API_DOC}

{diag_str}

GENERATION {g} SCIENTIFIC OBJECTIVE:
{gen_themes[g]}

STRICT COMPOSITIONAL RULES (Law 3 — MUST COMPOSE ON PARENT LIBRARY!):
1. All existing modules from `{current.arm}` remain in `lib` automatically.
2. Your new module(s) MUST genuinely CALL earlier-generation helper functions via `lib.<fn>(...)` (cross-generation composition, NOT rewriting the whole codebase from scratch!).
3. Add 1 focused new module (`mod_g{g}_...`, <= 180 lines!) plus a concise `orchestrator_source` (`def solve(api, lib, budget): ...`) that strictly improves T-count on unseen `n = 12..16` circuits at the SAME scale-adaptive `v3_budget`!
4. Zero hardcoding, zero forbidden builtins (`getattr`/`hasattr` forbidden — use `lib.has(...)`), zero `fn_errors`!
{retry_note}

Return STRICT JSON ONLY:
```json
{{
  "rationale": "brief mathematical explanation of the new Gen-{g} compositional mechanism",
  "new_modules": [
    {{"name": "mod_g{g}_...", "rationale": "...", "source": "def fn1(...): ..."}}
  ],
  "orchestrator_source": "def solve(api, lib, budget): ..."
}}
```"""
            t0 = time.perf_counter()
            cost = 0.0
            try:
                prop, cost, _ = _call_claude_isolated(prompt, model=model)
                cand = _build_artifact(prop, gen=g, parent=current, arm=f"G{g}")
                cand_val = _eval_split(cand, val_tasks, seeds=(0,))
                deltas = [cand_val["per_task"][t.task_id] - parent_val["per_task"][t.task_id] for t in val_tasks]
                w = paired_wilcoxon_stats(deltas)
                dt = time.perf_counter() - t0
                xgen_tot = sum(cand_val["cross_gen_calls"].values())
                passed = (
                    w["sum_delta"] < 0
                    and w["p_less"] < p_thresh
                    and len(cand_val["fn_errors"]) == 0
                    and cand_val["fallbacks"] == 0
                )
                meter.charge_cpu(dt, phase=f"s9_g{g}_att{att}")
                meter.charge_llm_proposal(cost, accepted=passed, phase=f"s9_g{g}_att{att}")
                llm_trace.append({
                    "phase": f"s9_g{g}_att{att}",
                    "cost_usd": cost,
                    "passed": passed,
                    "val_before": parent_val["total_t"],
                    "val_after": cand_val["total_t"],
                    "wilcoxon": w,
                    "wall_sec": cand_val["wall_sec"],
                    "parent_wall_sec": parent_val["wall_sec"],
                    "ops_frac": cand_val["avg_ops_frac"],
                    "xgen_tot": xgen_tot,
                    "xgen_map": cand_val["cross_gen_calls"],
                    "fn_errors": cand_val["fn_errors"],
                })
                print(
                    f"[S9 G{g} att{att}] val_g{g}: {parent_val['total_t']:.0f} -> {cand_val['total_t']:.0f} "
                    f"(d={w['sum_delta']:+.0f}, {w['wins']}W/{w['ties']}T/{w['losses']}L, p_less={w['p_less']:.6f} < {p_thresh}) "
                    f"| wall={cand_val['wall_sec']:.1f}s vs {parent_val['wall_sec']:.1f}s | xgen={xgen_tot} | ferr={len(cand_val['fn_errors'])} | PASS={passed} | ${cost:.3f}",
                    flush=True,
                )
                if passed:
                    promoted = True
                    best_cand = cand
                    best_w = w
                    break
                last_err = f"val_g{g} {parent_val['total_t']:.0f}->{cand_val['total_t']:.0f} (d={w['sum_delta']:+.0f}, p={w['p_less']:.4f}, xgen={xgen_tot}, ferr={cand_val['fn_errors']})"
            except Exception as exc:
                dt = time.perf_counter() - t0
                meter.charge_cpu(dt, phase=f"s9_g{g}_att{att}")
                meter.charge_llm_proposal(cost, accepted=False, phase=f"s9_g{g}_att{att}")
                llm_trace.append({"phase": f"s9_g{g}_att{att}", "cost_usd": cost, "error": str(exc)[:300]})
                last_err = str(exc)[:200]
                print(f"[S9 G{g} att{att}] ERROR: {last_err}", flush=True)

        if promoted and best_cand is not None:
            current = best_cand
        artifacts[f"G{g}"] = CompositionalAlgoArtifact(
            arm=f"G{g}",
            track="S9_POLY_SCALE_CLIFFORD_T",
            generation=current.generation,
            modules=current.modules,
            orchestrator=current.orchestrator,
            parent_sha256=current.parent_sha256,
        )
        gen_records.append({
            "gen": g,
            "promoted": promoted,
            "val_before": parent_val["total_t"],
            "val_after": parent_val["total_t"] + (best_w.get("sum_delta", 0.0) if promoted else 0.0),
            "val_wilcoxon": best_w,
            "modules": [f"g{m.generation}:{m.name}" for m in current.modules],
        })

    payload = {
        "track": "S9_POLY_SCALE_CLIFFORD_T",
        "manifest_sha256": msha,
        "budget_rule": "35_000 * C(n, 2)",
        "model": model,
        "artifacts": {k: v.to_dict() for k, v in artifacts.items()},
        "generation_records": gen_records,
        "llm_trace": llm_trace,
        "sleep_meter": meter.snapshot(),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[S9 EVOLVE DONE] Wrote {out_path} | total_usd=${payload['sleep_meter']['total_usd']:.4f}", flush=True)
    return payload


def evaluate_s9_packet(
    proposals_path: Path,
    packet_path: Path,
    s8_proposals_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Evaluate all Sprint 9 arms across `N = 200` untouched `n = 12..16` circuits x 3 paired seeds!"""
    prop = json.loads(proposals_path.read_text(encoding="utf-8"))
    suites = build_s9_benchmarks()
    msha = s9_manifest_sha256(suites)
    assert prop["manifest_sha256"] == msha, "S9 manifest mismatch!"

    art_map: Dict[str, CompositionalAlgoArtifact] = {
        k: CompositionalAlgoArtifact.from_dict(v) for k, v in prop["artifacts"].items()
    }
    promoted_gens = [r["gen"] for r in prop["generation_records"] if r.get("promoted")]
    ko_last_gen = promoted_gens[-1] if promoted_gens else 0
    ko_last_art = art_map[f"G{ko_last_gen - 1}"] if ko_last_gen >= 2 else art_map["A2_PRIOR_ONLY"]
    a5_sham_art = build_s8_a5_sham_artifact()

    s8_transfer_art: Optional[CompositionalAlgoArtifact] = None
    if s8_proposals_path is not None and s8_proposals_path.exists():
        s8p = json.loads(s8_proposals_path.read_text(encoding="utf-8"))
        s8_transfer_art = CompositionalAlgoArtifact.from_dict(s8p["artifacts"]["G2"])

    hold_suites = ("s9_hold_lit", "s9_hold_proc_ccz", "s9_hold_proc_rand")
    hold_tasks: List[S9Task] = [t for sn in hold_suites for t in suites[sn]]
    seeds = [0, 1, 2]

    # Determinism audit on 6 holdout tasks (n=12..16)
    det_tasks = [suites["s9_hold_lit"][0], suites["s9_hold_lit"][14], suites["s9_hold_proc_ccz"][0], suites["s9_hold_proc_ccz"][4], suites["s9_hold_proc_rand"][0], suites["s9_hold_proc_rand"][4]]
    det_mismatches = 0
    for t in det_tasks:
        c1, tel1 = run_s9_artifact(art_map["G4"], t.circuit, seed=0)
        c2, tel2 = run_s9_artifact(art_map["G4"], t.circuit, seed=0)
        if c1.t_count() != c2.t_count() or tel1["ops_spent"] != tel2["ops_spent"]:
            det_mismatches += 1
    det_audit = {"checked_tasks": len(det_tasks), "mismatches": det_mismatches, "passed": det_mismatches == 0}
    print(f"[S9 EVAL] Determinism: {det_audit} | promoted_gens={promoted_gens} | N_holdout={len(hold_tasks)}", flush=True)

    # Evaluate only distinct generations + baselines (copy identical rows for unpromoted gens to keep eval fast & exact!)
    arm_order = [
        "A0_BASE",
        "A1_TPAR",
        "A1_TODD_2018",
        "A1_FAST_TODD_2022",
    ]
    if s8_transfer_art is not None:
        arm_order.append("S8_G2_ZERO_SHOT")
    arm_order.extend(["A5_SHAM", "A2_PRIOR_ONLY", "G1", "G2", "G3", "G4", "KO_MATCHED_LAST"])

    t_all = time.perf_counter()
    rows: List[Dict[str, Any]] = []
    wall_by_arm: Dict[str, float] = {}
    tel_by_arm: Dict[str, Dict[str, Any]] = {}

    # Cache identical artifact SHA results so unpromoted identical G{k} == parent don't re-run 600 times unnecessarily
    # (deterministic bit-identical execution guaranteed by Law 1 + determinism audit!)
    art_cache: Dict[str, Tuple[List[Tuple[str, int, int, str]], float, Dict[str, Any]]] = {}

    for arm in arm_order:
        w0 = time.perf_counter()
        if arm in ("A0_BASE", "A1_TPAR", "A1_TODD_2018", "A1_FAST_TODD_2022"):
            base_cache: Dict[str, Tuple[int, str]] = {}
            for t in hold_tasks:
                if arm == "A0_BASE":
                    cc = t.circuit
                elif arm == "A1_TPAR":
                    cc = tpar_poly_optimize(t.circuit)
                elif arm == "A1_TODD_2018":
                    cc = todd_2018_poly_optimize(t.circuit)
                else:
                    cc = fast_todd_2022_poly_optimize(t.circuit)
                base_cache[t.task_id] = (cc.t_count(), cc.sha256())
            for sd in seeds:
                for t in hold_tasks:
                    cv, ssha = base_cache[t.task_id]
                    rows.append(make_row(arm=arm, suite=t.stratum, task_id=t.task_id, stratum=t.stratum, split=t.split, seed=sd, spec_sha256=t.sha256(), cost=int(cv), verified_exact=True, solution_sha256=ssha))
            wall_by_arm[arm] = round(time.perf_counter() - w0, 3)
            tel_by_arm[arm] = {"total_ops_spent": 0, "cross_gen_calls": {}, "mod_gate_drops": {}, "fn_errors": {}, "verifier_fallbacks": 0}
        else:
            art = s8_transfer_art if arm == "S8_G2_ZERO_SHOT" else (a5_sham_art if arm == "A5_SHAM" else (ko_last_art if arm == "KO_MATCHED_LAST" else art_map[arm]))
            assert art is not None
            asha = art.sha256()
            if asha in art_cache:
                cached_res, cwall, ctel = art_cache[asha]
                tmap = {t.task_id: t for t in hold_tasks}
                for tid, sd, cv, ssha in cached_res:
                    t = tmap[tid]
                    rows.append(make_row(arm=arm, suite=t.stratum, task_id=tid, stratum=t.stratum, split=t.split, seed=sd, spec_sha256=t.sha256(), cost=int(cv), verified_exact=True, solution_sha256=ssha))
                wall_by_arm[arm] = cwall
                tel_by_arm[arm] = dict(ctel)
            else:
                tot_ops = 0
                xgen: Dict[str, int] = {}
                mdrops: Dict[str, int] = {}
                ferr: Dict[str, int] = {}
                fb = 0
                res_list: List[Tuple[str, int, int, str]] = []
                for sd in seeds:
                    for t in hold_tasks:
                        circ, tel = run_s9_artifact(art, t.circuit, seed=sd)
                        cv, ssha = circ.t_count(), circ.sha256()
                        res_list.append((t.task_id, sd, cv, ssha))
                        tot_ops += int(tel.get("ops_spent", 0))
                        if tel.get("verifier_fallback"):
                            fb += 1
                        for k, v in tel.get("cross_gen_calls", {}).items():
                            xgen[k] = xgen.get(k, 0) + int(v)
                        for k, v in tel.get("mod_gate_drops", {}).items():
                            mdrops[k] = mdrops.get(k, 0) + int(v)
                        for k, v in tel.get("fn_errors", {}).items():
                            ferr[k] = ferr.get(k, 0) + int(v)
                        rows.append(make_row(arm=arm, suite=t.stratum, task_id=t.task_id, stratum=t.stratum, split=t.split, seed=sd, spec_sha256=t.sha256(), cost=int(cv), verified_exact=True, solution_sha256=ssha))
                cwall = round(time.perf_counter() - w0, 3)
                ctel = {"total_ops_spent": tot_ops, "cross_gen_calls": xgen, "mod_gate_drops": mdrops, "fn_errors": ferr, "verifier_fallbacks": fb}
                art_cache[asha] = (res_list, cwall, ctel)
                wall_by_arm[arm] = cwall
                tel_by_arm[arm] = ctel

        by_t: Dict[str, List[int]] = {}
        for r in rows:
            if r["arm"] == arm:
                by_t.setdefault(r["task_id"], []).append(r["cost"])
        med_tot = sum(statistics.median(v) for v in by_t.values())
        tl = tel_by_arm[arm]
        print(f"[S9 EVAL] {arm:18s}: TOT={med_tot:7.1f} | wall={wall_by_arm[arm]:7.2f}s | v3={tl['total_ops_spent']:>11d} | xgen={sum(tl['cross_gen_calls'].values()):>7d} | ferr={sum(tl['fn_errors'].values())} | fb={tl['verifier_fallbacks']}", flush=True)

    summary = compute_summary(rows)
    pkt = {
        "track": "S9_POLY_SCALE_CLIFFORD_T",
        "manifest_sha256": msha,
        "budget_rule": "35_000 * C(n, 2)",
        "promoted_gens": promoted_gens,
        "ko_last_target_gen": ko_last_gen,
        "determinism_audit": det_audit,
        "seeds": seeds,
        "n_rows": len(rows),
        "wall_by_arm_sec": wall_by_arm,
        "total_eval_sec": round(time.perf_counter() - t_all, 3),
        "telemetry_by_arm": tel_by_arm,
        "generation_records": prop["generation_records"],
        "sleep_meter": prop["sleep_meter"],
        "artifacts": prop["artifacts"],
        "summary": summary,
        "rows": rows,
    }
    reduced = verify_and_reduce(
        pkt,
        canonical_suites=suites,
        canonical_manifest_sha256=msha,
        expected_arms=arm_order,
        expected_suites=list(hold_suites),
        expected_seeds=list(seeds),
    )
    assert reduced["summary"] == summary
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(json.dumps(pkt), encoding="utf-8")
    print(f"[S9 EVAL DONE] Wrote verified {len(rows)}-row packet to {packet_path} in {pkt['total_eval_sec']}s", flush=True)
    return pkt


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "evolve":
        evolve_s9_proposals(Path(sys.argv[2]))
    elif mode == "eval":
        s8p = Path(sys.argv[4]) if len(sys.argv) > 4 else None
        evaluate_s9_packet(Path(sys.argv[2]), Path(sys.argv[3]), s8p)
    else:
        raise SystemExit("Usage: python -m comp_sprint9_poly_scale.s9_runner <evolve|eval> ...")
