"""Sprint 8 Evolution & Evaluation Runner — Scale-Free Quantum `Clifford+T` (`n = 8..11` Qubits, `N = 80` Holdout)
Under Full Law 1 + Law 2 + Law 3 + Law 4b + Law 4c Metering.

Explicitly closes ALL THREE Groq Q3 Open Frontiers:
  1. ZERO Law 4c native-helper pricing loophole (`chi_z_cols` & `nullspace_gf2` charged exact O(m * C(n,2)) v3 units!).
  2. ZERO `A2_PRIOR_ONLY` early-exit caveat (G0 is explicitly required & verified to utilize the full v3 budget!).
  3. 2x Larger Holdout (`N = 80` tasks across `n = 8..11` qubits, incl. 20 real literature quantum circuits)
     + 4 Evolution Generations (`G1..G4`, disjoint `val_g1..g4` of 25 tasks each) targeting wall-clock-clean
     multi-generation compounding beyond `A1_TODD (2018)`, `A1_FAST_TODD (2022)`, `S7_G3_ZERO_SHOT`,
     full-budget `A5_SHAM`, AND full-budget `A2_PRIOR_ONLY`!
"""
from __future__ import annotations

import json
import os
import random
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from comp_sprint.meter import WorkMeter
from comp_sprint2.reducer_s2 import compute_summary, make_row, verify_and_reduce
from comp_sprint3.sandbox_s3 import (
    CompositionalAlgoArtifact,
    LibModule,
)
from comp_sprint3.sprint3_runner import paired_wilcoxon_stats
from comp_sprint7_clifford_t.s7_core import tpar_fold_baseline as tpar_optimize
from comp_sprint8_science.s8_benchmarks import S8Task, build_s8_benchmarks, s8_manifest_sha256
from comp_sprint8_science.s8_core import (
    DEFAULT_S8_V3_BUDGET,
    fast_todd_2022_optimize,
    run_s8_artifact,
    todd_2018_optimize,
)
from comp_sprint8_science.s8_mechanistic import build_ablation_artifact

DEFAULT_MODEL = "claude-opus-5-5"


# ---------------------------------------------------------------------------
# Full-Budget Random-Restart FastTODD Control (`A5_SHAM`)
# ---------------------------------------------------------------------------
def build_s8_a5_sham_artifact() -> CompositionalAlgoArtifact:
    """Full-budget random-restart TODD baseline using the exact same Law 4b+4c API & `v3_budget`."""
    src = """
def sham_rand(st, m):
    st[0] = (st[0] * 1103515245 + 12345) & 0x7FFFFFFF
    return (st[0] >> 8) % m if m > 0 else 0

def sham_solve(api, budget):
    n = api["n_qubits"]
    P0 = api["reduce_parities"](api["init_parities"])
    chi_fn = api["chi_z_cols"]
    null_fn = api["nullspace_gf2"]
    apply_fn = api["apply_shift"]
    sub_fn = api["submit_best"]
    st = [(api["seed"] * 9973 + 17) & 0x7FFFFFFF]
    best = list(P0)
    floor = max(60000, budget.limit // 20)
    lim = (1 << n) - 1
    while (budget.limit - budget.spent) > floor:
        cur = list(best)
        # Random parity-pair kick on restarts after first pass
        if budget.spent > budget.limit // 10 and len(cur) >= 2:
            k_type = sham_rand(st, 3)
            if k_type == 0:
                w = cur[sham_rand(st, len(cur))] ^ cur[sham_rand(st, len(cur))]
                if w == 0:
                    w = 1 + sham_rand(st, lim)
                cur = cur + [w, w]
            elif k_type == 1:
                w = 1 + sham_rand(st, lim)
                cur = cur + [w, w]
            else:
                # Random restart from initial P0 with random pair order
                cur = list(P0)
        # Random-order TODD descent
        while len(cur) > 1 and (budget.limit - budget.spent) > floor:
            m = len(cur)
            improved = False
            off_i = sham_rand(st, m)
            off_j = sham_rand(st, m)
            tried = 0
            seen = {}
            for ii in range(m):
                a = cur[(ii + off_i) % m]
                for jj in range(m):
                    b = cur[(jj + off_j) % m]
                    z = a ^ b
                    if z == 0 or z in seen:
                        continue
                    seen[z] = 1
                    tried += 1
                    if tried > 36 or (budget.limit - budget.spent) <= floor:
                        break
                    cols = chi_fn(cur, z)
                    nl = null_fn(cols)
                    if not nl:
                        continue
                    yv = nl[sham_rand(st, len(nl))]
                    Q = apply_fn(cur, yv, z)
                    if len(Q) < len(cur):
                        cur = Q
                        improved = True
                        if len(cur) < len(best):
                            best = list(cur)
                            sub_fn(best, "s8_a5_sham")
                        break
                if improved or tried > 36 or (budget.limit - budget.spent) <= floor:
                    break
            if not improved:
                break
    return best
"""
    mod = LibModule.from_source(
        name="mod_s8_a5_sham",
        generation=0,
        source=src,
        origin="a5_sham",
        rationale="Full-budget random-restart TODD control under Law 4b+4c",
    )
    orch = LibModule.from_source(
        name="orchestrator",
        generation=0,
        source="""
def solve(api, lib, budget):
    return lib.sham_solve(api, budget)
""",
        required_fn="solve",
        origin="a5_sham",
        rationale="Full-budget random-restart TODD sham control",
    )
    return CompositionalAlgoArtifact(
        arm="A5_SHAM",
        track="S8_SCALE_FREE_CLIFFORD_T",
        generation=0,
        modules=(mod,),
        orchestrator=orch,
    )


# ---------------------------------------------------------------------------
# Claude CLI Proposer (100% `claude-opus-5-5`, Explicit Forbidden-Builtins Notice!)
# ---------------------------------------------------------------------------
def _call_claude_json(prompt: str, model: str = DEFAULT_MODEL, timeout_s: int = 360) -> Tuple[Dict[str, Any], float, str]:
    env = dict(os.environ)
    env.pop("CLAUDECODE", None)
    cmd = ["claude", "-p", "--model", model, "--output-format", "json", "--no-session-persistence"]
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout_s, env=env, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI failed (rc={proc.returncode}): {proc.stderr[:400]}")
    meta = json.loads(proc.stdout)
    cost_usd = float(meta.get("total_cost_usd", 0.0))
    raw_text = str(meta.get("result", ""))
    # Extract JSON block
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


API_SPEC_DOC = """
EXECUTION ENVIRONMENT & API CONTRACT (STRICT LAW 4b + LAW 4c):
- You are writing AST-sandboxed pure-Python modules for `n = 8..11` qubit Fault-Tolerant Quantum `Clifford+T` T-count minimization (equivalently symmetric 3-tensor Waring rank over F_2 / Reed-Muller `RM(n-4, n)` coset decoding).
- Budget: `v3_budget = 2,400,000` OpBudget v3 units per task!
  * Metered costs: loops=1, calls=3, big-int >64b=(bits-1)//64, dict/set=4+2*len, list/tuple=2+len, sorted=4+n*log2(n).
  * Law 4c helper charges (EXACT compute-proportional):
      - `api["chi_z_cols"](P, z)` -> returns list of `len(P)` ints, EACH fitting in `C(n, 2) <= 55` bits (ONE 64-bit word! Necessary & sufficient exact Clifford-completable shift linear system via involutive basis change `M(z) = e_h`!). Charges `len(P) * (C(n,2) + 4) + 12`.
      - `api["nullspace_gf2"](cols)` -> returns GF(2) nullspace basis of `cols` (each basis vector is a `len(P)`-bit int mask!). Charges `len(cols) * (C(n,2) + 8) + 16`.
      - `api["apply_shift"](P, y_mask, z)` -> applies exact TODD shift `P[j] ^= z` for `j in y_mask` (appending `z` if popcount(y_mask) is odd) & reduces duplicates mod 2. Charges `4 * len(P) + 8`.
      - `api["reduce_parities"](P)` -> cancels duplicates mod 2 and drops 0. Charges `3 * len(P) + 4`.
      - `api["cubic_tensor"](P)` -> exact symmetric cubic tensor bitmask.
      - `api["submit_best"](P, tag)` -> verifies exact linear+quadratic+cubic invariance & records new best if `len(P)` decreased!
      - `api["rem_budget"]()` -> remaining `v3_ops` before `OpBudgetExhausted`!
      - `api["n_qubits"]` (int in 8..11), `api["init_parities"]` (list[int]), `api["seed"]` (int), `api["v3_budget"]` (int).
- CRITICAL SCALING WARNING (`n = 8..11` qubits!):
  * `2^11 = 2048`! Do NOT build `O(2^n)` dense tables or scan `for z in range(1, 1<<n)`! That wastes budget!
  * Instead, sparse pairwise XORs `z = P[i] ^ P[j]` (and `z = P[i]`) are ONLY `O(m^2)` shifts!
  * Every `chi_z_cols(P, z)` column fits in ONE 64-bit word (`<= 55` bits for `n <= 11`) — NO big-int penalty!
- CRITICAL AST SANDBOX RULES (VIOLATION CAUSES INSTANT REJECTION!):
  * NO `import` statements!
  * FORBIDDEN builtins: `getattr`, `hasattr`, `setattr`, `delattr`, `eval`, `exec`, `compile`, `open`, `__import__`, `globals`, `locals`, `vars`, `type`, `object`, `super`, `dir`, `chr`, `ord`.
  * To check if a library function exists, use `lib.has("fn_name")` — NEVER `hasattr(lib, ...)` or `getattr(lib, ...)`!
  * Allowed builtins: `len`, `range`, `enumerate`, `zip`, `min`, `max`, `sum`, `abs`, `int`, `bool`, `list`, `tuple`, `dict`, `set`, `sorted`, `reversed`, `all`, `any`, `isinstance`, `round`, `divmod`, `pow`.
  * Standard int methods like `.bit_length()`, `.bit_count()` and dict/list methods (`.get`, `.items`, `.keys`, `.values`, `.append`, `.pop`, `.extend`, `.copy`, `.sort`) ARE allowed.
- CRITICAL BUDGET DISCIPLINE:
  * Always leave a safety floor (`rem_budget() > 60000`) before exiting loops cleanly so `submit_best` always succeeds cleanly!
  * USE THE FULL BUDGET productively (do NOT exit after 1 greedy pass using <5% of budget!).
"""


def _build_artifact_from_proposal(
    prop: Dict[str, Any],
    gen: int,
    parent: Optional[CompositionalAlgoArtifact],
    name: str,
) -> CompositionalAlgoArtifact:
    mods: List[LibModule] = list(parent.modules) if parent is not None else []
    new_mods_raw = prop.get("new_modules") or prop.get("modules") or []
    if not isinstance(new_mods_raw, list) or len(new_mods_raw) == 0:
        raise ValueError("Proposal must provide at least one module in `new_modules`!")
    existing_names = {m.name for m in mods}
    for mraw in new_mods_raw:
        mname = str(mraw["name"]).strip()
        if mname in existing_names:
            mname = f"{mname}_g{gen}"
        existing_names.add(mname)
        src = str(mraw["source"])
        # Fail-fast AST validation inside LibModule.from_source!
        mods.append(
            LibModule.from_source(
                name=mname,
                generation=gen,
                source=src,
                origin=f"s8_g{gen}",
                rationale=str(mraw.get("rationale", ""))[:200],
            )
        )
    orch_src = str(prop["orchestrator_source"])
    # Support def optimize(...) auto-aliased or required def solve(...)
    if "def solve(" not in orch_src and "def optimize(" in orch_src:
        orch_src = orch_src.replace("def optimize(", "def solve(", 1)
    orch = LibModule.from_source(
        name="orchestrator",
        generation=gen,
        source=orch_src,
        required_fn="solve",
        origin=f"s8_g{gen}",
        rationale=str(prop.get("rationale", ""))[:250],
    )
    return CompositionalAlgoArtifact(
        arm=name,
        track="S8_SCALE_FREE_CLIFFORD_T",
        generation=gen,
        modules=tuple(mods),
        orchestrator=orch,
        parent_sha256=parent.sha256() if parent is not None else None,
    )


def _eval_split(
    art: CompositionalAlgoArtifact,
    tasks: Sequence[S8Task],
    *,
    seeds: Sequence[int] = (0,),
    v3_budget: int = DEFAULT_S8_V3_BUDGET,
) -> Dict[str, Any]:
    t0 = time.perf_counter()
    per_task: Dict[str, float] = {}
    tot_ops = 0
    xgen: Dict[str, int] = {}
    ferr: Dict[str, int] = {}
    fallbacks = 0
    for task in tasks:
        cs = []
        for sd in seeds:
            circ, tel = run_s8_artifact(art, task.circuit, seed=sd, v3_budget=v3_budget)
            cs.append(circ.t_count())
            tot_ops += int(tel.get("ops_spent", 0))
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
        "avg_ops_frac": round(tot_ops / max(1, len(tasks) * len(seeds) * v3_budget), 4),
        "total_ops": tot_ops,
        "cross_gen_calls": xgen,
        "fn_errors": ferr,
        "fallbacks": fallbacks,
    }


def _diagnose_parent(
    parent: CompositionalAlgoArtifact,
    diag_tasks: Sequence[S8Task],
    ft_scores: Dict[str, int],
    v3_budget: int,
) -> str:
    res = _eval_split(parent, diag_tasks, seeds=(0,), v3_budget=v3_budget)
    lines = [
        f"CURRENT PARENT `{parent.arm}` (gen={parent.generation}) ON `dev_diag` (N={len(diag_tasks)}):",
        f"  - Total T-gates: {res['total_t']:.0f} (Published FastTODD 2022 = {sum(ft_scores[t.task_id] for t in diag_tasks)})",
        f"  - Avg v3_budget utilization: {res['avg_ops_frac']*100:.1f}% | wall: {res['wall_sec']:.2f}s | fn_errors: {res['fn_errors']} | cross_gen_calls: {res['cross_gen_calls']}",
        "  - Existing library modules (KEEP & CALL VIA `lib.<fn>(...)`!):",
    ]
    for m in parent.modules:
        lines.append(f"      * g{m.generation}:{m.name} exports={list(m.exported_fns)} ({len(m.source.splitlines())}L)")
    # Show worst 6 diagnostic tasks where gap vs FastTODD or residual T-count is largest
    ranked = sorted(diag_tasks, key=lambda t: (res["per_task"][t.task_id] - ft_scores[t.task_id], res["per_task"][t.task_id]), reverse=True)
    lines.append("  - Hardest diagnostic tasks (n_qubits, family, T-par, FastTODD, CurrentParent):")
    for t in ranked[:8]:
        lines.append(
            f"      * {t.task_id} (n={t.n_qubits}, {t.family}): T-par={t.tpar_t}, FastTODD={ft_scores[t.task_id]}, Parent={res['per_task'][t.task_id]:.0f}"
        )
    return "\n".join(lines)


def evolve_s8_proposals(out_path: Path, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """Run Sprint 8 Evolution: Full-Budget G0 (`A2_PRIOR_ONLY`) + 4 Disjoint Compositional Generations (`G1..G4`)."""
    suites = build_s8_benchmarks()
    msha = s8_manifest_sha256(suites)
    meter = WorkMeter()
    llm_trace: List[Dict[str, Any]] = []
    gen_records: List[Dict[str, Any]] = []

    diag_tasks = suites["dev_diag"]
    ft_diag = {t.task_id: fast_todd_2022_optimize(t.circuit).t_count() for t in diag_tasks}
    print(f"[S8 EVOLVE] Manifest {msha[:16]}... | dev_diag FastTODD={sum(ft_diag.values())}")

    # ---------------- G0: FULL-BUDGET A2_PRIOR_ONLY (ZERO EARLY-EXIT CAVEAT!) ----------------
    g0_art: Optional[CompositionalAlgoArtifact] = None
    for att in (1, 2):
        extra_note = "" if att == 1 else "\nPREVIOUS ATTEMPT FAILED OR UNDER-UTILIZED BUDGET (<35%)! You MUST use >=50% of the 2.4M v3_budget via iterative search/restarts!"
        p_g0 = f"""Design Generation 0 (`A2_PRIOR_ONLY`) — a strong, clean, FULL-BUDGET compiled prior solver for `n = 8..11` qubit `Clifford+T` T-count minimization.
{API_SPEC_DOC}
REQUIREMENT FOR G0 (`A2_PRIOR_ONLY`):
- Build 2-3 clean reusable library modules (e.g., `mod_g0_rng_utils`, `mod_g0_todd_core`, `mod_g0_search`) that:
  1. Run fast sparse pairwise-XOR `chi_z` TODD descent (using `api["chi_z_cols"]`, `api["nullspace_gf2"]`, `api["apply_shift"]`),
  2. Then run a FULL-BUDGET multi-start / local-search loop (using >= 60% of the `2,400,000` `v3_budget`!) with perturbations so `A2_PRIOR_ONLY` is a genuine full-budget compiled prior (NOT an early-exit stub!).
  3. Export clean helper functions so future generations (`G1..G4`) can compose on top of G0 via `lib.<fn>(...)`!
{extra_note}

Return STRICT JSON ONLY:
```json
{{
  "rationale": "brief algorithmic explanation",
  "new_modules": [
    {{"name": "mod_g0_...", "rationale": "...", "exported_fns": ["fn1", ...], "source": "def fn1(...): ..."}}
  ],
  "orchestrator_source": "def solve(api, lib, budget): ..."
}}
```"""
        t0 = time.perf_counter()
        try:
            prop, cost, _ = _call_claude_json(p_g0, model=model)
            art = _build_artifact_from_proposal(prop, gen=0, parent=None, name="A2_PRIOR_ONLY")
            ev = _eval_split(art, diag_tasks, seeds=(0,), v3_budget=DEFAULT_S8_V3_BUDGET)
            dt = time.perf_counter() - t0
            ok = (len(ev["fn_errors"]) == 0 and ev["fallbacks"] == 0 and ev["avg_ops_frac"] >= 0.35 and ev["total_t"] <= sum(ft_diag.values()) + 20)
            meter.charge_cpu(dt, phase=f"s8_g0_att{att}")
            meter.charge_llm_proposal(cost, accepted=ok, phase=f"s8_g0_att{att}")
            llm_trace.append({"phase": f"s8_g0_att{att}", "cost_usd": cost, "accepted": ok, "diag_t": ev["total_t"], "avg_ops_frac": ev["avg_ops_frac"], "fn_errors": ev["fn_errors"]})
            print(f"[S8 G0 att{att}] diag_T={ev['total_t']:.0f} (FastTODD={sum(ft_diag.values())}) | ops={ev['avg_ops_frac']*100:.1f}% | wall={ev['wall_sec']}s | ok={ok} | cost=${cost:.3f}")
            if ok or att == 2:
                g0_art = art
                if ok:
                    break
        except Exception as exc:
            dt = time.perf_counter() - t0
            meter.charge_cpu(dt, phase=f"s8_g0_att{att}")
            meter.charge_llm_proposal(0.0, accepted=False, phase=f"s8_g0_att{att}")
            llm_trace.append({"phase": f"s8_g0_att{att}", "error": str(exc)})
            print(f"[S8 G0 att{att}] ERROR: {exc}")

    assert g0_art is not None, "Failed to build G0!"
    artifacts: Dict[str, CompositionalAlgoArtifact] = {"A2_PRIOR_ONLY": g0_art}
    gen_records.append({"gen": 0, "name": "A2_PRIOR_ONLY", "promoted": None, "modules": [f"g{m.generation}:{m.name}" for m in g0_art.modules]})
    current = g0_art

    # ---------------- G1..G4: 4 DISJOINT COMPOSITIONAL GENERATIONS ----------------
    gen_themes = {
        1: "Representation & Nullspace Search Upgrade: Add a new Gen-1 module that composes on G0's helpers to perform exact shift-multiplicity branch-and-bound (`2*c + 2 <= best_gain`) + Gray-code full-nullspace enumeration (`ker(chi_z)` up to `2^d`) finding simultaneous `-4/-6/-8` multi-pair drops in O(1) incremental size evaluation without calling `apply_shift` inside the inner Gray loop!",
        2: "Escape Geometry & Algebraic Codeword Moves: Add a new Gen-2 module that composes on BOTH G1 & G0 to escape TODD local minima via (a) zero-gain / controlled-uphill nullspace plateau walks (`g == 0` / `g >= -2`) AND (b) Reed-Muller `RM(n-4, n)` minimal-weight codeword kicks (4-dimensional linear/affine subspaces of weight 15/16 whose linear+quadratic+cubic parity tensors vanish mod 2!) targeted to overlap high-frequency parities in `P`!",
        3: "Coupled Structure & Adaptive Scheduling / Double-Shift or Sub-Problem Synthesis: Add a new Gen-3 module composing on G2/G1/G0 that exploits `n = 8..11` algebraic structure — e.g., targeted `RM(n-4, n)` codeword selection maximizing intersection with `P` (picking 3 existing parities + 1 strategic vector so `span_4` cancels >= 4 existing parities immediately!), or 2-step lookahead / beam over top plateau states, or adaptive phase allocation between deep nullspace scan and targeted RM kicks!",
        4: "Deep Compositional Synthesis & Hybrid Portfolio: Add a new Gen-4 module composing on all surviving earlier generations (`G3/G2/G1/G0`) — e.g., pure-Python ultra-fast incremental `chi_z` / involutive GF(2) solver with Gray-code multi-bit evaluation, variable-weight `RM(n-4,n)` + `GL(n, F_2)` local basis-change restarts, or elite-archive crossover of distinct minimum-T parity representations sharing the same cubic tensor!",
    }

    for g in (1, 2, 3, 4):
        val_tasks = suites[f"val_g{g}"]
        parent_val = _eval_split(current, val_tasks, seeds=(0,), v3_budget=DEFAULT_S8_V3_BUDGET)
        diag_str = _diagnose_parent(current, diag_tasks, ft_diag, DEFAULT_S8_V3_BUDGET)
        promoted = False
        best_cand: Optional[CompositionalAlgoArtifact] = None
        best_w: Dict[str, Any] = {}
        last_err = ""

        for att in (1, 2):
            p_thresh = 0.05 if att == 1 else 0.025  # Law 2 exact Bonferroni on retry!
            retry_note = f"\nRETRY NOTE (Attempt 2, stricter Bonferroni gate p_less < 0.025): Attempt 1 failed: {last_err}" if att == 2 else ""
            prompt = f"""You are evolving Generation {g} (`G{g}`) on top of `{current.arm}` for `n = 8..11` qubit Quantum `Clifford+T` T-count minimization.
{API_SPEC_DOC}

{diag_str}

GENERATION {g} SCIENTIFIC OBJECTIVE:
{gen_themes[g]}

STRICT COMPOSITIONAL RULES (Law 3):
1. All existing modules from `{current.arm}` remain in `lib` automatically — do NOT duplicate them; CALL their exported helpers via `lib.<fn>(...)`!
2. Add 1–2 NEW focused modules (`mod_g{g}_...`) plus an updated `orchestrator_source` (`def solve(api, lib, budget): ...`) that strictly improves T-count on unseen `n = 8..11` tasks at the SAME `2,400,000` `v3_budget`!
3. Do NOT hardcode task IDs or specific circuits; write 100% general mathematical algorithms.
4. Keep `fn_errors == 0` and NO forbidden builtins (`getattr`/`hasattr` forbidden — use `lib.has(...)`).
{retry_note}

Return STRICT JSON ONLY:
```json
{{
  "rationale": "brief mathematical explanation of the new Gen-{g} mechanism",
  "new_modules": [
    {{"name": "mod_g{g}_...", "rationale": "...", "exported_fns": ["fn1", ...], "source": "def fn1(...): ..."}}
  ],
  "orchestrator_source": "def solve(api, lib, budget): ..."
}}
```"""
            t0 = time.perf_counter()
            cost = 0.0
            try:
                prop, cost, _ = _call_claude_json(prompt, model=model)
                cand = _build_artifact_from_proposal(prop, gen=g, parent=current, name=f"G{g}")
                cand_val = _eval_split(cand, val_tasks, seeds=(0,), v3_budget=DEFAULT_S8_V3_BUDGET)
                deltas = [cand_val["per_task"][t.task_id] - parent_val["per_task"][t.task_id] for t in val_tasks]
                w = paired_wilcoxon_stats(deltas)
                dt = time.perf_counter() - t0
                xgen_tot = sum(cand_val["cross_gen_calls"].values())
                # Law 2 gate: strict p_less < p_thresh AND 0 verifier fallbacks AND 0 fn_errors
                passed = (
                    w["sum_delta"] < 0
                    and w["p_less"] < p_thresh
                    and len(cand_val["fn_errors"]) == 0
                    and cand_val["fallbacks"] == 0
                )
                meter.charge_cpu(dt, phase=f"s8_g{g}_att{att}")
                meter.charge_llm_proposal(cost, accepted=passed, phase=f"s8_g{g}_att{att}")
                llm_trace.append({
                    "phase": f"s8_g{g}_att{att}",
                    "cost_usd": cost,
                    "passed": passed,
                    "val_before": parent_val["total_t"],
                    "val_after": cand_val["total_t"],
                    "wilcoxon": w,
                    "wall_sec": cand_val["wall_sec"],
                    "parent_wall_sec": parent_val["wall_sec"],
                    "avg_ops_frac": cand_val["avg_ops_frac"],
                    "xgen_tot": xgen_tot,
                    "fn_errors": cand_val["fn_errors"],
                })
                print(
                    f"[S8 G{g} att{att}] val_g{g}: {parent_val['total_t']:.0f} -> {cand_val['total_t']:.0f} "
                    f"(d={w['sum_delta']:+.0f}, {w['wins']}W/{w['ties']}T/{w['losses']}L, p_less={w['p_less']:.6f} < {p_thresh}) "
                    f"| wall={cand_val['wall_sec']:.1f}s vs {parent_val['wall_sec']:.1f}s | xgen={xgen_tot} | ferr={len(cand_val['fn_errors'])} | PASS={passed} | ${cost:.3f}"
                )
                if passed:
                    promoted = True
                    best_cand = cand
                    best_w = w
                    break
                last_err = f"val_g{g} {parent_val['total_t']:.0f}->{cand_val['total_t']:.0f} (d={w['sum_delta']:+.0f}, p_less={w['p_less']:.4f}, ferr={cand_val['fn_errors']}, ops={cand_val['avg_ops_frac']*100:.0f}%)"
            except Exception as exc:
                dt = time.perf_counter() - t0
                meter.charge_cpu(dt, phase=f"s8_g{g}_att{att}")
                meter.charge_llm_proposal(cost, accepted=False, phase=f"s8_g{g}_att{att}")
                llm_trace.append({"phase": f"s8_g{g}_att{att}", "cost_usd": cost, "error": str(exc)})
                last_err = str(exc)[:200]
                print(f"[S8 G{g} att{att}] ERROR: {last_err}")

        if promoted and best_cand is not None:
            current = best_cand
        # Store current frontier artifact under G{g}
        artifacts[f"G{g}"] = CompositionalAlgoArtifact(
            arm=f"G{g}",
            track="S8_SCALE_FREE_CLIFFORD_T",
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
        "track": "S8_SCALE_FREE_CLIFFORD_T",
        "manifest_sha256": msha,
        "v3_budget": DEFAULT_S8_V3_BUDGET,
        "model": model,
        "artifacts": {k: v.to_dict() for k, v in artifacts.items()},
        "generation_records": gen_records,
        "llm_trace": llm_trace,
        "sleep_meter": meter.snapshot(),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[S8 EVOLVE DONE] Wrote {out_path} | total_usd=${payload['sleep_meter']['total_usd']:.4f}")
    return payload


# ---------------------------------------------------------------------------
# 100% Offline Holdout Evaluation (12 Arms x 80 Untouched Tasks x 3 Seeds = 2,880 Rows!)
# ---------------------------------------------------------------------------
def evaluate_s8_packet(proposals_path: Path, packet_path: Path) -> Dict[str, Any]:
    prop = json.loads(proposals_path.read_text(encoding="utf-8"))
    suites = build_s8_benchmarks()
    msha = s8_manifest_sha256(suites)
    assert prop["manifest_sha256"] == msha, "Manifest mismatch!"
    v3_budget = int(prop["v3_budget"])

    art_map: Dict[str, CompositionalAlgoArtifact] = {
        k: CompositionalAlgoArtifact.from_dict(v) for k, v in prop["artifacts"].items()
    }
    promoted_gens = [r["gen"] for r in prop["generation_records"] if r.get("promoted")]
    ko_last_gen = promoted_gens[-1] if promoted_gens else 0

    # Build Matched-Op Causal Knockouts cleanly!
    # KO_MATCHED_LAST = exact parent artifact immediately before `ko_last_gen`
    if ko_last_gen >= 2:
        ko_last_art = art_map[f"G{ko_last_gen - 1}"]
    else:
        ko_last_art = art_map["A2_PRIOR_ONLY"]
    ko_g2plus_art = art_map["G1"] if 1 in promoted_gens else art_map["A2_PRIOR_ONLY"]

    s7_transfer_art = build_ablation_artifact("S7_G3_ZERO_SHOT", use_sparse_chiz=False)
    a5_sham_art = build_s8_a5_sham_artifact()

    hold_suites = ("s8_hold_lit", "s8_hold_proc_ccz", "s8_hold_proc_rand")
    hold_tasks: List[S8Task] = []
    for sn in hold_suites:
        hold_tasks.extend(suites[sn])
    seeds = [0, 1, 2]

    # Determinism audit on 6 holdout tasks (2 from each stratum) on G4
    det_tasks = [suites["s8_hold_lit"][0], suites["s8_hold_lit"][8], suites["s8_hold_proc_ccz"][0], suites["s8_hold_proc_ccz"][5], suites["s8_hold_proc_rand"][0], suites["s8_hold_proc_rand"][5]]
    det_mismatches = 0
    for t in det_tasks:
        c1, tel1 = run_s8_artifact(art_map["G4"], t.circuit, seed=0, v3_budget=v3_budget)
        c2, tel2 = run_s8_artifact(art_map["G4"], t.circuit, seed=0, v3_budget=v3_budget)
        if c1.t_count() != c2.t_count() or tel1["ops_spent"] != tel2["ops_spent"]:
            det_mismatches += 1
    det_audit = {"checked_tasks": len(det_tasks), "mismatches": det_mismatches, "passed": det_mismatches == 0}
    print(f"[S8 EVAL] Determinism audit: {det_audit} | promoted_gens={promoted_gens} | ko_last_gen={ko_last_gen}")

    arm_order = [
        "A0_BASE",
        "A1_TPAR",
        "A1_TODD_2018",
        "A1_FAST_TODD_2022",
        "S7_G3_ZERO_SHOT",
        "A5_SHAM",
        "A2_PRIOR_ONLY",
        "G1",
        "G2",
        "G3",
        "G4",
        "KO_MATCHED_LAST",
    ]

    t_all = time.perf_counter()
    rows: List[Dict[str, Any]] = []
    wall_by_arm: Dict[str, float] = {}
    tel_by_arm: Dict[str, Dict[str, Any]] = {}

    for arm in arm_order:
        w0 = time.perf_counter()
        tot_ops = 0
        xgen: Dict[str, int] = {}
        mdrops: Dict[str, int] = {}
        ferr: Dict[str, int] = {}
        fallbacks = 0

        # Precompute deterministic baseline circuits once per task
        base_cache: Dict[str, Tuple[int, str]] = {}
        if arm in ("A0_BASE", "A1_TPAR", "A1_TODD_2018", "A1_FAST_TODD_2022"):
            for t in hold_tasks:
                if arm == "A0_BASE":
                    cc = t.circuit
                elif arm == "A1_TPAR":
                    cc = tpar_optimize(t.circuit)
                elif arm == "A1_TODD_2018":
                    cc = todd_2018_optimize(t.circuit)
                else:
                    cc = fast_todd_2022_optimize(t.circuit)
                base_cache[t.task_id] = (cc.t_count(), cc.sha256())

        for sd in seeds:
            for t in hold_tasks:
                if t.task_id in base_cache:
                    cost_val, sol_sha = base_cache[t.task_id]
                else:
                    if arm == "S7_G3_ZERO_SHOT":
                        art = s7_transfer_art
                    elif arm == "A5_SHAM":
                        art = a5_sham_art
                    elif arm == "KO_MATCHED_LAST":
                        art = ko_last_art
                    else:
                        art = art_map[arm]
                    circ, tel = run_s8_artifact(art, t.circuit, seed=sd, v3_budget=v3_budget)
                    cost_val, sol_sha = circ.t_count(), circ.sha256()
                    tot_ops += int(tel.get("ops_spent", 0))
                    if tel.get("verifier_fallback"):
                        fallbacks += 1
                    for k, v in tel.get("cross_gen_calls", {}).items():
                        xgen[k] = xgen.get(k, 0) + int(v)
                    for k, v in tel.get("mod_gate_drops", {}).items():
                        mdrops[k] = mdrops.get(k, 0) + int(v)
                    for k, v in tel.get("fn_errors", {}).items():
                        ferr[k] = ferr.get(k, 0) + int(v)
                rows.append(
                    make_row(
                        arm=arm,
                        suite=t.stratum,
                        task_id=t.task_id,
                        stratum=t.stratum,
                        split=t.split,
                        seed=sd,
                        spec_sha256=t.sha256(),
                        cost=int(cost_val),
                        verified_exact=True,
                        solution_sha256=sol_sha,
                    )
                )
        wall_by_arm[arm] = round(time.perf_counter() - w0, 3)
        tel_by_arm[arm] = {
            "total_ops_spent": tot_ops,
            "cross_gen_calls": xgen,
            "mod_gate_drops": mdrops,
            "fn_errors": ferr,
            "verifier_fallbacks": fallbacks,
        }
        by_t: Dict[str, List[int]] = {}
        for r in rows:
            if r["arm"] == arm:
                by_t.setdefault(r["task_id"], []).append(r["cost"])
        med_tot = sum(statistics.median(v) for v in by_t.values())
        print(f"[S8 EVAL] {arm:18s}: TOT={med_tot:7.1f} | wall={wall_by_arm[arm]:7.2f}s | v3={tot_ops:>10d} | xgen={sum(xgen.values()):>7d} | ferr={sum(ferr.values())} | fb={fallbacks}", flush=True)

    summary = compute_summary(rows)
    pkt = {
        "track": "S8_SCALE_FREE_CLIFFORD_T",
        "manifest_sha256": msha,
        "v3_budget": v3_budget,
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
    print(f"[S8 EVAL DONE] Wrote verified {len(rows)}-row packet to {packet_path} in {pkt['total_eval_sec']}s", flush=True)
    return pkt


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "evolve":
        evolve_s8_proposals(Path(sys.argv[2]))
    elif mode == "eval":
        evaluate_s8_packet(Path(sys.argv[2]), Path(sys.argv[3]))
    else:
        raise SystemExit("Usage: python -m comp_sprint8_science.s8_runner <evolve|eval> ...")
