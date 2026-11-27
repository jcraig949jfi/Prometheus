"""Sprint 10 Runner — 5th Independent Formal Domain: Exact Binary Bilinear 3-Tensor Rank over F_2
(Strassen / Laderman / AlphaTensor Matrix Multiplication & General Bilinear Tensors vs.
Published Kauers-Moosbauer Flip-Graph 2023 under All 4 Laws + 100% Tool-Less Isolation!)."""
from __future__ import annotations

import hashlib
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
from comp_sprint10_alphatensor.s10_benchmarks import S10Task, build_s10_benchmarks, s10_manifest_sha256
from comp_sprint10_alphatensor.s10_core import (
    DEFAULT_S10_V3_BUDGET,
    build_s10_a1_flip_graph_artifact,
    reduce_bilinear_terms,
    run_s10_artifact,
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
    with tempfile.TemporaryDirectory(prefix="prometheus_s10_iso_") as tmpdir:
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


def build_s10_a5_sham_artifact() -> CompositionalAlgoArtifact:
    """Pure blind random flip-only sham (no Plus transitions, no reduction-aware targeting)."""
    src = """
def sh_rand(st, m):
    st[0] = (st[0] * 1103515245 + 12345) & 0x7FFFFFFF
    return (st[0] >> 8) % m if m > 0 else 0

def sh_solve(api, budget):
    red = api["reduce_terms"]
    flp = api["flip_pair"]
    sub = api["submit_best"]
    best = red(api["init_terms"])
    sub(best, "s10_a5_sham")
    cur = list(best)
    st = [(api["seed"] * 9973 + 31) & 0x7FFFFFFF]
    floor = max(40000, budget.limit // 25)
    stale = 0
    while (budget.limit - budget.spent) > floor:
        m = len(cur)
        if m <= 1:
            break
        mode = sh_rand(st, 3)
        i = sh_rand(st, m)
        j = sh_rand(st, m)
        if i != j and cur[i][mode] == cur[j][mode]:
            nxt = flp(cur, i, j, mode, sh_rand(st, 2))
            if nxt is not None:
                cur = red(nxt)
                if len(cur) < len(best):
                    best = list(cur)
                    sub(best, "s10_a5_sham")
                    stale = 0
                    continue
        stale += 1
        if stale > 300:
            cur = list(best)
            stale = 0
    return best
"""
    mod = LibModule.from_source("mod_s10_a5_sham", 0, src, origin="a5_sham", rationale="Blind random flip sham")
    orch = LibModule.from_source("orchestrator", 0, "def solve(api, lib, budget):\n    return lib.sh_solve(api, budget)\n", required_fn="solve", origin="a5_sham")
    return CompositionalAlgoArtifact(arm="A5_SHAM", track="S10_ALPHATENSOR_F2", generation=0, modules=(mod,), orchestrator=orch)


S10_API_DOC = """
EXECUTION ENVIRONMENT & API CONTRACT (SPRINT 10 — EXACT BINARY BILINEAR 3-TENSOR RANK OVER F_2, ALPHATENSOR / STRASSEN DOMAIN):
- Goal: Minimize exact bilinear tensor rank `R = len(terms)` of a 3D binary tensor `T in F_2^{na x nb x nc}`
  where `terms = [(u_r, v_r, w_r)]` are nonzero integer bitmask triples (`0 < u < 2^na`, `0 < v < 2^nb`, `0 < w < 2^nc`)
  satisfying `sum_r (u_r (x) v_r (x) w_r) == T (mod 2)` identically!
- Budget: `v3_budget = api["v3_budget"] = 1,800,000` OpBudget v3 units per task (Law 4b + Law 4c).
  * Metered costs: loops=1, calls=3, big-int >64b=(bits-1)//64, dict/set=4+2*len, list/tuple=2+len, sorted=4+n*log2(n).
  * API helpers (exact compute-proportional charges):
      - `api["na"]`, `api["nb"]`, `api["nc"]` (int, typically 4..9), `api["init_terms"]` (list of `(u, v, w)` tuples), `api["seed"]` (int), `api["v3_budget"]` (int).
      - `api["reduce_terms"](terms)` -> merges any pairs sharing 2 of 3 factors `(u,v)`, `(u,w)`, `(v,w)` until fixed point (`6*R + 8` ops).
      - `api["flip_pair"](terms, i, j, shared_mode, twist)` -> exact Kauers-Moosbauer Flip on terms `i, j` sharing `shared_mode in {0, 1, 2}`, `twist in {0, 1}` (`R + 12` ops).
      - `api["plus_split"](terms, i, mode, vec)` -> exact Kauers-Moosbauer Plus split (`R -> R + 1`) (`R + 12` ops).
      - `api["submit_best"](terms, tag)` -> verifies exact 3D binary tensor equality and updates best if `len(terms)` decreased!
      - `api["rem_budget"]()` -> remaining `v3_ops`.
- CRITICAL ALGORITHMIC INSIGHT (HOW TO CRUSH PUBLISHED KAUERS-MOOSBAUER RANDOM FLIP-GRAPH WALK!):
  1. **Direct Reduction-Seeking Flips (1-Step & 2-Step Lookahead!):** Standard Kauers-Moosbauer flips random shared-factor pairs blindly. Instead, maintain hash maps of `(u, v)`, `(u, w)`, `(v, w)` and **target flips where `v_i ^ v_j` or `w_i ^ w_j` ALREADY EXISTS in another term sharing a second factor** -> immediate `R -> R - 1` or `R -> R - 2` reduction!
  2. **In-Place O(1) Flip + Incremental Bucket Maintenance (Zero Redundant `reduce_terms` Calls!):** Instead of rebuilding `buckets` and calling `api["reduce_terms"](cur)` (`6*R` ops + list alloc) on every single flip, maintain pure-Python tuples + index maps and do fast local flip/reduction checks — 5-10x higher flip throughput per `v3_budget`!
  3. **Targeted Low-Rank Sub-Tensor / Strassen / 2x2-Block & Linear-Dependency Moves:**
     - **Linear-Combination Reduction (Exact F_2 Gaussian Elimination on Factors!):** Whenever `k` terms share ONE factor (say `u_1 == ... == u_k == u`), their sub-tensor is a 2D matrix `M = sum_{r=1}^k v_r (x) w_r`! Re-factoring `M` into its **exact minimal matrix rank** `rk(M) <= k` via GF(2) row echelon form **INSTANTLY drops `k - rk(M)` bilinear multiplications** AND lets you change basis inside `M` to create NEW factor collisions with the rest of the tensor!!
     - **Targeted Plus-Split (`u_i -> u_j, u_i ^ u_j`):** Choose `vec = u_j` specifically where `(u_j, v_i)` or `(u_j, w_i)` already matches a third term (2-step Plus+Flip+Reduce funnel)!
     - **3-Term / 4-Term Triangle Flip (`(u,v,w) + (u,v',w') + ...`) & Elite Archive Restarts!**
- CRITICAL AST SANDBOX RULES:
  * NO `import` statements!
  * FORBIDDEN builtins: `getattr`, `hasattr`, `setattr`, `delattr`, `eval`, `exec`, `compile`, `open`, `__import__`, `globals`, `locals`, `vars`, `type`, `object`, `super`, `dir`, `chr`, `ord`.
  * Use `lib.has("fn_name")` — NEVER `hasattr`/`getattr`!
  * Keep safety floor `rem_budget() > 60000` and USE THE FULL BUDGET (>= 60%)!
"""


def _build_artifact(prop: Dict[str, Any], gen: int, parent: Optional[CompositionalAlgoArtifact], arm: str) -> CompositionalAlgoArtifact:
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
        mods.append(LibModule.from_source(mn, gen, str(mr["source"]), origin=f"s10_g{gen}", rationale=str(mr.get("rationale", ""))[:200]))
    orch_src = str(prop["orchestrator_source"])
    if "def solve(" not in orch_src and "def optimize(" in orch_src:
        orch_src = orch_src.replace("def optimize(", "def solve(", 1)
    orch = LibModule.from_source("orchestrator", gen, orch_src, required_fn="solve", origin=f"s10_g{gen}", rationale=str(prop.get("rationale", ""))[:250])
    return CompositionalAlgoArtifact(arm=arm, track="S10_ALPHATENSOR_F2", generation=gen, modules=tuple(mods), orchestrator=orch, parent_sha256=parent.sha256() if parent else None)


def _eval_split(art: CompositionalAlgoArtifact, tasks: Sequence[S10Task], seeds: Sequence[int] = (0,)) -> Dict[str, Any]:
    t0 = time.perf_counter()
    per_task: Dict[str, float] = {}
    tot_ops = 0
    xgen: Dict[str, int] = {}
    ferr: Dict[str, int] = {}
    fb = 0
    for task in tasks:
        cs = []
        for sd in seeds:
            sol, tel = run_s10_artifact(art, task.tensor, seed=sd, v3_budget=DEFAULT_S10_V3_BUDGET)
            cs.append(len(sol))
            tot_ops += int(tel.get("ops_spent", 0))
            if tel.get("verifier_fallback"):
                fb += 1
            for k, v in tel.get("cross_gen_calls", {}).items():
                xgen[k] = xgen.get(k, 0) + int(v)
            for k, v in tel.get("fn_errors", {}).items():
                ferr[k] = ferr.get(k, 0) + int(v)
        per_task[task.task_id] = float(statistics.median(cs))
    return {
        "total_r": sum(per_task.values()),
        "per_task": per_task,
        "wall_sec": round(time.perf_counter() - t0, 2),
        "avg_ops_frac": round(tot_ops / max(1, len(tasks) * len(seeds) * DEFAULT_S10_V3_BUDGET), 4),
        "total_ops": tot_ops,
        "cross_gen_calls": xgen,
        "fn_errors": ferr,
        "fallbacks": fb,
    }


def _diagnose_parent(parent: CompositionalAlgoArtifact, diag_tasks: Sequence[S10Task], fg_scores: Dict[str, float]) -> str:
    res = _eval_split(parent, diag_tasks, seeds=(0,))
    lines = [
        f"CURRENT PARENT `{parent.arm}` (gen={parent.generation}) ON `dev_diag` (N={len(diag_tasks)}):",
        f"  - Total Bilinear Rank: {res['total_r']:.0f} (Published Kauers-Moosbauer Flip-Graph = {sum(fg_scores.values()):.0f}; Base = {sum(t.base_rank for t in diag_tasks)})",
        f"  - Avg v3_budget utilization: {res['avg_ops_frac']*100:.1f}% | wall: {res['wall_sec']:.2f}s | fn_errors: {res['fn_errors']} | cross_gen_calls: {res['cross_gen_calls']}",
        "  - Existing library modules (COMPOSE BY CALLING VIA `lib.<fn>(...)`!):",
    ]
    for m in parent.modules:
        lines.append(f"      * g{m.generation}:{m.name} exports={list(m.exported_fns)} ({len(m.source.splitlines())}L)")
    ranked = sorted(diag_tasks, key=lambda t: (res["per_task"][t.task_id] - fg_scores[t.task_id], res["per_task"][t.task_id]), reverse=True)
    lines.append("  - Hardest diagnostic tensors:")
    for t in ranked[:8]:
        lines.append(f"      * {t.task_id} ({t.tensor.na}x{t.tensor.nb}x{t.tensor.nc}, {t.family}): Base={t.base_rank}, FlipGraph={fg_scores[t.task_id]:.0f}, Parent={res['per_task'][t.task_id]:.0f}")
    return "\n".join(lines)


def evolve_s10_proposals(out_path: Path, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    suites = build_s10_benchmarks()
    msha = s10_manifest_sha256(suites)
    meter = WorkMeter()
    llm_trace: List[Dict[str, Any]] = []
    gen_records: List[Dict[str, Any]] = []

    diag_tasks = suites["dev_diag"]
    fg_art = build_s10_a1_flip_graph_artifact()
    fg_diag = _eval_split(fg_art, diag_tasks, seeds=(0,))["per_task"]
    print(f"[S10 EVOLVE] Manifest {msha[:16]}... | dev_diag Base={sum(t.base_rank for t in diag_tasks)}, Published FlipGraph={sum(fg_diag.values()):.0f}", flush=True)

    # ---------------- G0: FULL-BUDGET A2_PRIOR_ONLY ----------------
    g0_art: Optional[CompositionalAlgoArtifact] = None
    for att in (1, 2):
        extra = "" if att == 1 else "\nRETRY: Keep code concise, zero AST errors, >=50% budget usage!"
        p_g0 = f"""Design Generation 0 (`A2_PRIOR_ONLY`) — a clean, FULL-BUDGET compiled prior solver for Exact Binary Bilinear 3-Tensor Rank minimization over F_2.
{S10_API_DOC}
REQUIREMENT FOR G0 (`A2_PRIOR_ONLY`):
- Build 2–3 clean reusable library modules (`mod_g0_rng`, `mod_g0_flip`, `mod_g0_search`) implementing fast reduction-aware flip-graph search + Plus transitions using >= 60% of the `1,800,000` `v3_budget`, calling `api["submit_best"]` on every improvement, and exporting clean helpers so future generations (`G1..G3`) can compose on top of G0 via `lib.<fn>(...)`!
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
            meter.charge_cpu(dt, phase=f"s10_g0_att{att}")
            meter.charge_llm_proposal(cost, accepted=ok, phase=f"s10_g0_att{att}")
            llm_trace.append({"phase": f"s10_g0_att{att}", "cost_usd": cost, "accepted": ok, "diag_r": ev["total_r"], "ops_frac": ev["avg_ops_frac"], "ferr": ev["fn_errors"]})
            print(f"[S10 G0 att{att}] diag_R={ev['total_r']:.0f} (FlipGraph={sum(fg_diag.values()):.0f}) | ops={ev['avg_ops_frac']*100:.1f}% | wall={ev['wall_sec']}s | ok={ok} | ${cost:.3f}", flush=True)
            if ok or att == 2:
                g0_art = art
                if ok:
                    break
        except Exception as exc:
            dt = time.perf_counter() - t0
            meter.charge_cpu(dt, phase=f"s10_g0_att{att}")
            meter.charge_llm_proposal(cost, accepted=False, phase=f"s10_g0_att{att}")
            llm_trace.append({"phase": f"s10_g0_att{att}", "cost_usd": cost, "error": str(exc)[:300]})
            print(f"[S10 G0 att{att}] ERROR: {exc}", flush=True)

    assert g0_art is not None, "Failed to build S10 G0!"
    artifacts: Dict[str, CompositionalAlgoArtifact] = {"A2_PRIOR_ONLY": g0_art}
    gen_records.append({"gen": 0, "name": "A2_PRIOR_ONLY", "promoted": None, "modules": [f"g{m.generation}:{m.name}" for m in g0_art.modules]})
    current = g0_art

    # ---------------- G1..G3: 3 COMPOSITIONAL GENERATIONS ----------------
    gen_themes = {
        1: "Exact Slice-Matrix GF(2) Rank Compression + 1-Step Reduction-Seeking Flips: Add `mod_g1_slice_gauss` that CALLS G0's helpers (`lib.<fn>(...)`) AND adds (a) exact GF(2) bilinear matrix-rank compression over any group of terms sharing a factor in mode 0, 1, or 2 (instantly collapsing rank-deficient sub-matrices AND basis-aligning factors to maximize collisions!), and (b) greedy 1-step reduction-seeking flips prioritizing pairs whose XORed factor matches an existing term!",
        2: "Targeted Plus+Flip+Reduce Funnel & Pairwise-Collision Scoring: Add `mod_g2_funnel` that COMPOSES G1 & G0 via `lib.<fn>(...)` AND replaces random Plus splits with **collision-targeted Plus+Flip funnels** (choosing split vector `vec` from existing factors so the split creates immediate 2-step rank-reducing flip chains!) + multi-mode potential scoring (counting duplicate factor frequencies across all 3 modes to steer the flip walk toward high-collision basins!).",
        3: "Elite-Pool Beam / Bidirectional Basin Search & Multi-Step Lookahead: Add `mod_g3_elite_beam` that COMPOSES G2/G1/G0 via `lib.<fn>(...)` — maintaining a diverse archive of minimum-rank decompositions (distinct canonical hashes) and running targeted high-collision Plus+Flip+GF(2)-slice-compression trajectories from the highest-potential elite states!",
    }

    for g in (1, 2, 3):
        val_tasks = suites[f"val_g{g}"]
        parent_val = _eval_split(current, val_tasks, seeds=(0,))
        diag_str = _diagnose_parent(current, diag_tasks, fg_diag)
        promoted = False
        best_cand: Optional[CompositionalAlgoArtifact] = None
        best_w: Dict[str, Any] = {}
        last_err = ""

        for att in (1, 2):
            p_thresh = 0.05 if att == 1 else 0.025
            retry_note = f"\nRETRY (Bonferroni gate p_less < 0.025): Attempt 1 failed: {last_err}" if att == 2 else ""
            prompt = f"""You are evolving Generation {g} (`G{g}`) on top of `{current.arm}` for Exact Binary Bilinear 3-Tensor Rank minimization over F_2 (AlphaTensor / Strassen domain).
{S10_API_DOC}

{diag_str}

GENERATION {g} SCIENTIFIC OBJECTIVE:
{gen_themes[g]}

STRICT COMPOSITIONAL RULES (Law 3 — COMPOSE ON PARENT LIBRARY!):
1. All existing modules from `{current.arm}` remain in `lib` automatically; CALL their exported helpers via `lib.<fn>(...)`!
2. Add 1 concise, focused new module (`mod_g{g}_...`, <= 180 lines) + `orchestrator_source` (`def solve(api, lib, budget): ...`) strictly reducing bilinear tensor rank on unseen tensors at the SAME `1,800,000` `v3_budget`!
3. Zero hardcoding, zero forbidden builtins (`getattr`/`hasattr` forbidden — use `lib.has(...)`), zero `fn_errors`!
{retry_note}

Return STRICT JSON ONLY:
```json
{{
  "rationale": "brief mathematical explanation",
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
                passed = (w["sum_delta"] < 0 and w["p_less"] < p_thresh and len(cand_val["fn_errors"]) == 0 and cand_val["fallbacks"] == 0)
                meter.charge_cpu(dt, phase=f"s10_g{g}_att{att}")
                meter.charge_llm_proposal(cost, accepted=passed, phase=f"s10_g{g}_att{att}")
                llm_trace.append({
                    "phase": f"s10_g{g}_att{att}", "cost_usd": cost, "passed": passed,
                    "val_before": parent_val["total_r"], "val_after": cand_val["total_r"],
                    "wilcoxon": w, "wall_sec": cand_val["wall_sec"], "parent_wall_sec": parent_val["wall_sec"],
                    "ops_frac": cand_val["avg_ops_frac"], "xgen_tot": xgen_tot, "xgen_map": cand_val["cross_gen_calls"],
                    "fn_errors": cand_val["fn_errors"],
                })
                print(
                    f"[S10 G{g} att{att}] val_g{g}: {parent_val['total_r']:.0f} -> {cand_val['total_r']:.0f} "
                    f"(d={w['sum_delta']:+.0f}, {w['wins']}W/{w['ties']}T/{w['losses']}L, p_less={w['p_less']:.6f} < {p_thresh}) "
                    f"| wall={cand_val['wall_sec']:.1f}s vs {parent_val['wall_sec']:.1f}s | xgen={xgen_tot} | ferr={len(cand_val['fn_errors'])} | PASS={passed} | ${cost:.3f}",
                    flush=True,
                )
                if passed:
                    promoted = True
                    best_cand = cand
                    best_w = w
                    break
                last_err = f"val_g{g} {parent_val['total_r']:.0f}->{cand_val['total_r']:.0f} (d={w['sum_delta']:+.0f}, p={w['p_less']:.4f}, xgen={xgen_tot}, ferr={cand_val['fn_errors']})"
            except Exception as exc:
                dt = time.perf_counter() - t0
                meter.charge_cpu(dt, phase=f"s10_g{g}_att{att}")
                meter.charge_llm_proposal(cost, accepted=False, phase=f"s10_g{g}_att{att}")
                llm_trace.append({"phase": f"s10_g{g}_att{att}", "cost_usd": cost, "error": str(exc)[:300]})
                last_err = str(exc)[:200]
                print(f"[S10 G{g} att{att}] ERROR: {last_err}", flush=True)

        if promoted and best_cand is not None:
            current = best_cand
        artifacts[f"G{g}"] = CompositionalAlgoArtifact(arm=f"G{g}", track="S10_ALPHATENSOR_F2", generation=current.generation, modules=current.modules, orchestrator=current.orchestrator, parent_sha256=current.parent_sha256)
        gen_records.append({"gen": g, "promoted": promoted, "val_before": parent_val["total_r"], "val_after": parent_val["total_r"] + (best_w.get("sum_delta", 0.0) if promoted else 0.0), "val_wilcoxon": best_w, "modules": [f"g{m.generation}:{m.name}" for m in current.modules]})

    payload = {
        "track": "S10_ALPHATENSOR_F2",
        "manifest_sha256": msha,
        "v3_budget": DEFAULT_S10_V3_BUDGET,
        "model": model,
        "artifacts": {k: v.to_dict() for k, v in artifacts.items()},
        "generation_records": gen_records,
        "llm_trace": llm_trace,
        "sleep_meter": meter.snapshot(),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[S10 EVOLVE DONE] Wrote {out_path} | total_usd=${payload['sleep_meter']['total_usd']:.4f}", flush=True)
    return payload


def evaluate_s10_packet(proposals_path: Path, packet_path: Path) -> Dict[str, Any]:
    """Evaluate all Sprint 10 arms across 60 untouched bilinear 3-tensors x 3 seeds = 1,620 verified offline rows!"""
    prop = json.loads(proposals_path.read_text(encoding="utf-8"))
    suites = build_s10_benchmarks()
    msha = s10_manifest_sha256(suites)
    assert prop["manifest_sha256"] == msha
    v3_budget = int(prop["v3_budget"])

    art_map = {k: CompositionalAlgoArtifact.from_dict(v) for k, v in prop["artifacts"].items()}
    promoted_gens = [r["gen"] for r in prop["generation_records"] if r.get("promoted")]
    ko_last_gen = promoted_gens[-1] if promoted_gens else 0
    ko_last_art = art_map[f"G{ko_last_gen - 1}"] if ko_last_gen >= 2 else art_map["A2_PRIOR_ONLY"]
    fg_art = build_s10_a1_flip_graph_artifact()
    a5_art = build_s10_a5_sham_artifact()

    hold_suites = ("s10_hold_matmul", "s10_hold_proc_planted", "s10_hold_proc_rand")
    hold_tasks = [t for sn in hold_suites for t in suites[sn]]
    seeds = [0, 1, 2]

    # Determinism audit
    det_tasks = [suites["s10_hold_matmul"][0], suites["s10_hold_matmul"][6], suites["s10_hold_proc_planted"][0], suites["s10_hold_proc_planted"][1], suites["s10_hold_proc_rand"][0], suites["s10_hold_proc_rand"][1]]
    det_mismatches = 0
    for t in det_tasks:
        s1, tel1 = run_s10_artifact(art_map["G3"], t.tensor, seed=0, v3_budget=v3_budget)
        s2, tel2 = run_s10_artifact(art_map["G3"], t.tensor, seed=0, v3_budget=v3_budget)
        if len(s1) != len(s2) or tel1["ops_spent"] != tel2["ops_spent"]:
            det_mismatches += 1
    det_audit = {"checked_tasks": len(det_tasks), "mismatches": det_mismatches, "passed": det_mismatches == 0}
    print(f"[S10 EVAL] Determinism: {det_audit} | promoted_gens={promoted_gens}", flush=True)

    arm_order = ["A0_BASE", "A1_FLIP_GRAPH", "A5_SHAM", "A2_PRIOR_ONLY", "G1", "G2", "G3", "KO_MATCHED_LAST"]
    rows: List[Dict[str, Any]] = []
    wall_by_arm: Dict[str, float] = {}
    tel_by_arm: Dict[str, Dict[str, Any]] = {}
    art_cache: Dict[str, Tuple[List[Tuple[str, int, int, str]], float, Dict[str, Any]]] = {}
    t_all = time.perf_counter()

    for arm in arm_order:
        w0 = time.perf_counter()
        if arm == "A0_BASE":
            for sd in seeds:
                for t in hold_tasks:
                    rows.append(make_row(arm=arm, suite=t.stratum, task_id=t.task_id, stratum=t.stratum, split=t.split, seed=sd, spec_sha256=t.sha256(), cost=t.base_rank, verified_exact=True, solution_sha256=t.sha256()))
            wall_by_arm[arm] = round(time.perf_counter() - w0, 3)
            tel_by_arm[arm] = {"total_ops_spent": 0, "cross_gen_calls": {}, "mod_gate_drops": {}, "fn_errors": {}, "verifier_fallbacks": 0}
        else:
            art = fg_art if arm == "A1_FLIP_GRAPH" else (a5_art if arm == "A5_SHAM" else (ko_last_art if arm == "KO_MATCHED_LAST" else art_map[arm]))
            asha = hashlib.sha256(json.dumps({"mods": [m.sha256 for m in art.modules], "orch": art.orchestrator.sha256}, sort_keys=True).encode("ascii")).hexdigest()
            if asha in art_cache:
                cached, cwall, ctel = art_cache[asha]
                tmap = {t.task_id: t for t in hold_tasks}
                for tid, sd, cv, ssha in cached:
                    t = tmap[tid]
                    rows.append(make_row(arm=arm, suite=t.stratum, task_id=tid, stratum=t.stratum, split=t.split, seed=sd, spec_sha256=t.sha256(), cost=cv, verified_exact=True, solution_sha256=ssha))
                wall_by_arm[arm] = cwall
                tel_by_arm[arm] = dict(ctel)
            else:
                tot_ops = 0; xgen: Dict[str, int] = {}; mdrops: Dict[str, int] = {}; ferr: Dict[str, int] = {}; fb = 0
                res_list: List[Tuple[str, int, int, str]] = []
                for sd in seeds:
                    for t in hold_tasks:
                        sol, tel = run_s10_artifact(art, t.tensor, seed=sd, v3_budget=v3_budget)
                        cv = len(sol)
                        ssha = hashlib.sha256(json.dumps(sorted(sol), separators=(",", ":")).encode("ascii")).hexdigest()
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
                        rows.append(make_row(arm=arm, suite=t.stratum, task_id=t.task_id, stratum=t.stratum, split=t.split, seed=sd, spec_sha256=t.sha256(), cost=cv, verified_exact=True, solution_sha256=ssha))
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
        print(f"[S10 EVAL] {arm:16s}: TOT={med_tot:6.1f} | wall={wall_by_arm[arm]:6.2f}s | v3={tl['total_ops_spent']:>10d} | xgen={sum(tl['cross_gen_calls'].values()):>7d} | ferr={sum(tl['fn_errors'].values())} | fb={tl['verifier_fallbacks']}", flush=True)

    summary = compute_summary(rows)
    pkt = {
        "track": "S10_ALPHATENSOR_F2", "manifest_sha256": msha, "v3_budget": v3_budget,
        "promoted_gens": promoted_gens, "ko_last_target_gen": ko_last_gen,
        "determinism_audit": det_audit, "seeds": seeds, "n_rows": len(rows),
        "wall_by_arm_sec": wall_by_arm, "total_eval_sec": round(time.perf_counter() - t_all, 3),
        "telemetry_by_arm": tel_by_arm, "generation_records": prop["generation_records"],
        "sleep_meter": prop["sleep_meter"], "artifacts": prop["artifacts"],
        "summary": summary, "rows": rows,
    }
    reduced = verify_and_reduce(pkt, canonical_suites=suites, canonical_manifest_sha256=msha, expected_arms=arm_order, expected_suites=list(hold_suites), expected_seeds=list(seeds))
    assert reduced["summary"] == summary
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(json.dumps(pkt), encoding="utf-8")
    print(f"[S10 EVAL DONE] Wrote verified {len(rows)}-row packet to {packet_path} in {pkt['total_eval_sec']}s", flush=True)
    return pkt


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "evolve":
        evolve_s10_proposals(Path(sys.argv[2]))
    elif mode == "eval":
        evaluate_s10_packet(Path(sys.argv[2]), Path(sys.argv[3]))
    else:
        raise SystemExit("Usage: python -m comp_sprint10_alphatensor.s10_runner <evolve|eval> ...")
