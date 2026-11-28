"""Phase B — Controlled Attribution Experiment: Minimal-Specification (Unguided) vs. Mathematically Guided Synthesis.

Primary Scientific Question:
  Can the model autonomously discover a useful algorithmic mechanism for binary bilinear 3-tensor rank
  over F_2 that was NOT supplied in the prompt?

Strict Controls:
  1. Brand-new, fresh, disjoint, immutable benchmark suite (`N = 40` distinct tensors, seed `20261128_ATTRIB`,
     ZERO overlap with Sprint 10: 20 planted low-rank tensors with known planted rank 11..15 & canonical rank
     22..36 + 20 sparse random tensors of dims 5x6x6..6x6x6). Repeated seeds are NEVER counted as independent tasks.
  2. Two strictly matched conditions (100% tool-less `--tools ""`, empty `TemporaryDirectory`, identical model
     `claude-opus-5-5`, identical 1-call budget per trial, `K = 4` independent trials per condition = 8 total calls!):
       - `UNGUIDED_MINIMAL_SPEC` (4 independent trials): States ONLY the exact mathematical problem definition,
         exact API (`na, nb, nc, init_terms, seed, v3_budget, reduce_terms, flip_pair, plus_split, submit_best,
         rem_budget`), and AST sandbox rules. ZERO algorithmic strategy hints (no mention of lookahead, pair maps,
         GF(2) slice rank, Kauers-Moosbauer, Strassen, or Plus schedules!).
       - `GUIDED_MATH_HINTS` (4 independent trials): Identical API + AST rules, PLUS explicit algorithmic hints
         matching Sprint 10's `S10_API_DOC` (reduction-seeking lookahead flips, incremental pair maps, GF(2)
         matrix-rank bucket compression, targeted Plus+Flip funnels).
  3. Preserve EVERY success AND EVERY failure (compilation/AST/runtime errors logged explicitly).
  4. Equalized Dual Evaluation (100% Offline, `$0.00` LLM):
       - **Actual Wall-Clock Equalized:** `0.50s` per tensor (un-throttled Python!) vs Faithful KM-2023 (`0.50s`/tensor).
       - **OpBudget v3 Equalized:** `1,800,000` `v3_ops` per tensor under Law 4b+4c.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import re
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from comp_sprint.meter import WorkMeter
from comp_sprint3.sandbox_s3 import CompositionalAlgoArtifact, LibModule
from comp_sprint3.sprint3_runner import paired_wilcoxon_stats
from comp_sprint10_alphatensor.s10_benchmarks import (
    _canonical_slice_terms,
    _sample_planted_tensor,
    _sample_sparse_rand_tensor,
    build_s10_benchmarks,
)
from comp_sprint10_alphatensor.s10_core import (
    BilinearTensorF2,
    DEFAULT_S10_V3_BUDGET,
    apply_flip,
    apply_plus,
    reduce_bilinear_terms,
    run_s10_artifact,
    verify_bilinear_decomp,
)
from comp_sprint11_audit.phase_a_km2023 import km2023_reference_search

DEFAULT_MODEL = "claude-opus-5-5"


@dataclass(frozen=True)
class S11Task:
    task_id: str
    stratum: str
    tensor: BilinearTensorF2
    base_rank: int
    planted_upper_bound: Optional[int]  # exact known upper bound for planted tensors (None for random)

    def sha256(self) -> str:
        return self.tensor.sha256()


def build_s11_attribution_suite() -> List[S11Task]:
    """Deterministically build 40 fresh, immutable bilinear 3-tensors over F_2 with ZERO overlap with Sprint 10!"""
    s10 = build_s10_benchmarks()
    forbidden_shas: Set[str] = {t.sha256() for tasks in s10.values() for t in tasks}
    seen: Set[str] = set(forbidden_shas)
    tasks: List[S11Task] = []

    # 20 fresh hard planted low-rank tensors (5x6x6..6x6x6, planted rank 11..15 -> guaranteed headroom!)
    planted_specs = [(5, 6, 5, 11), (5, 6, 6, 12), (6, 6, 6, 13), (6, 6, 6, 15)]
    rng_p = random.Random(20261128_001)
    k = 0
    while len(tasks) < 20:
        na, nb, nc, pr = planted_specs[len(tasks) % len(planted_specs)]
        ten = _sample_planted_tensor(rng_p, na, nb, nc, pr, f"s11_attr_pl_{k:02d}")
        k += 1
        if ten.tensor_mask and ten.base_rank() >= pr + 7 and ten.sha256() not in seen:
            seen.add(ten.sha256())
            tasks.append(S11Task(ten.name, "attr_planted", ten, ten.base_rank(), pr))

    # 20 fresh hard sparse random tensors (5x6x6..6x6x6)
    rand_specs = [(5, 6, 5), (5, 6, 6), (6, 5, 6), (6, 6, 6)]
    rng_r = random.Random(20261128_002)
    k = 0
    while len(tasks) < 40:
        na, nb, nc = rand_specs[(len(tasks) - 20) % len(rand_specs)]
        ten = _sample_sparse_rand_tensor(rng_r, na, nb, nc, f"s11_attr_rn_{k:02d}")
        k += 1
        if ten.tensor_mask and ten.base_rank() >= 18 and ten.sha256() not in seen:
            seen.add(ten.sha256())
            tasks.append(S11Task(ten.name, "attr_rand", ten, ten.base_rank(), None))

    return tasks


def s11_attr_manifest_sha256(tasks: Sequence[S11Task]) -> str:
    payload = [{"id": t.task_id, "sha": t.sha256(), "base": t.base_rank, "ub": t.planted_upper_bound} for t in tasks]
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


# ---------------------------------------------------------------------------
# Strictly Separated Prompts: UNGUIDED (Minimal Math Spec Only) vs GUIDED
# ---------------------------------------------------------------------------
COMMON_CONTRACT = """
PROBLEM DEFINITION:
- Input: A 3D binary tensor T in F_2^{na x nb x nc}, given as an initial valid rank-R decomposition
  `api["init_terms"]` — a list of triples `(u, v, w)` of nonzero integer bitmasks (`0 < u < 2^na`,
  `0 < v < 2^nb`, `0 < w < 2^nc`) such that `sum_{r=1}^R (u_r (x) v_r (x) w_r) == T (mod 2)`.
- Objective: Return (and call `api["submit_best"](terms, tag)` whenever improved) a valid decomposition
  of the EXACT SAME binary tensor T with MINIMUM possible rank `len(terms)`.
- Available API keys in `api`:
  * `api["na"]`, `api["nb"]`, `api["nc"]` (ints, 4..9)
  * `api["init_terms"]` (list of `(u, v, w)` int tuples)
  * `api["seed"]` (int)
  * `api["v3_budget"]` (int, budget cap)
  * `api["rem_budget"]()` -> remaining budget units (stop cleanly while `rem_budget() > 60000`)
  * `api["submit_best"](terms, tag)` -> verifies exact equality with T mod 2 and records new best if `len(terms)` decreased
  * Primitive algebraic helper functions (optional to call; you may also manipulate `(u, v, w)` tuples directly in pure Python):
      - `api["reduce_terms"](terms)`: merges pairs of terms agreeing on 2 of 3 factors mod 2 and drops zero terms.
      - `api["flip_pair"](terms, i, j, shared_mode, twist)`: given terms `i, j` sharing `shared_mode in {0, 1, 2}`, replaces `(u, v1, w1) + (u, v2, w2)` by `(u, v1, w1^w2) + (u, v1^v2, w2)` (for twist=0; symmetric for twist=1 and modes 1, 2).
      - `api["plus_split"](terms, i, mode, vec)`: replaces term `i` along `mode in {0, 1, 2}` by two terms summing to it (`x -> (x^vec) + vec`).
- AST SANDBOX RULES:
  * NO `import` statements!
  * FORBIDDEN builtins: `getattr`, `hasattr`, `setattr`, `delattr`, `eval`, `exec`, `compile`, `open`, `__import__`, `globals`, `locals`, `vars`, `type`, `object`, `super`, `dir`, `chr`, `ord`.
  * Use `lib.has("fn_name")` to check library functions.
  * Allowed builtins: `len`, `range`, `enumerate`, `zip`, `min`, `max`, `sum`, `abs`, `int`, `bool`, `list`, `tuple`, `dict`, `set`, `sorted`, `reversed`, `all`, `any`, `isinstance`, `round`, `divmod`, `pow`.
  * Use the available budget productively (`rem_budget() > 60000` safety floor).

Return STRICT JSON ONLY:
```json
{
  "rationale": "concise explanation of your algorithmic design",
  "new_modules": [
    {"name": "mod_algo", "rationale": "...", "source": "def helper(...): ..."}
  ],
  "orchestrator_source": "def solve(api, lib, budget): ..."
}
```
"""

UNGUIDED_PROMPT_TEMPLATE = """Design a standalone, deterministic, pure-Python algorithm for minimizing exact bilinear tensor rank over F_2.
{common}
Design your own algorithm from first principles. Keep total code clean and self-contained (<= 350 lines).
Trial identifier: {trial_tag} (use your own independent algorithmic design!).
"""

GUIDED_PROMPT_TEMPLATE = """Design a standalone, deterministic, pure-Python algorithm for minimizing exact bilinear tensor rank over F_2.
{common}
MATHEMATICAL STRATEGY GUIDANCE (apply these techniques):
1. Maintain an incremental always-reduced state with hash maps of `(u, v)`, `(u, w)`, `(v, w)` pairs and per-mode factor buckets so flips and reductions execute in O(1) without rebuilding dicts.
2. Use 1-step reduction-seeking lookahead flips: prefer flips `(i, j)` where the XORed factor matches an existing term sharing a second factor (immediate rank drop R -> R - 1 or R - 2).
3. Apply exact GF(2) matrix-rank bucket compression: whenever multiple terms share one factor (say `u`), refactor their 2D bilinear slice `M = sum v_r (x) w_r` via GF(2) row echelon form to collapse rank-deficient slices immediately.
4. Use collision-targeted Plus escapes (`vec` chosen from another existing factor in the same mode) on stagnation plus restarts from the best decomposition.

Keep total code clean and self-contained (<= 350 lines). Trial identifier: {trial_tag}.
"""


def _call_claude_isolated(prompt: str, model: str = DEFAULT_MODEL, timeout_s: int = 360) -> Tuple[Dict[str, Any], float, str]:
    env = dict(os.environ)
    env.pop("CLAUDECODE", None)
    cmd = ["claude", "-p", "--model", model, "--output-format", "json", "--no-session-persistence", "--tools", ""]
    with tempfile.TemporaryDirectory(prefix="prometheus_s11_attr_") as tmpdir:
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout_s, env=env, cwd=tmpdir, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI failed (rc={proc.returncode}): {proc.stderr[:300]}")
    meta = json.loads(proc.stdout)
    cost = float(meta.get("total_cost_usd", 0.0))
    raw = str(meta.get("result", ""))
    m = re.search(r"```json\s*(\{.*?\})\s*```", raw, re.DOTALL)
    body = m.group(1) if m else raw[raw.find("{") : raw.rfind("}") + 1]
    return json.loads(body), cost, raw


def _parse_trial_artifact(prop: Dict[str, Any], arm: str) -> CompositionalAlgoArtifact:
    mods_raw = prop.get("new_modules") or prop.get("modules") or []
    if not mods_raw:
        raise ValueError("Missing new_modules")
    mods = []
    seen_n = set()
    for i, mr in enumerate(mods_raw):
        mn = str(mr.get("name", f"mod_{i}")).strip()
        if mn in seen_n:
            mn = f"{mn}_{i}"
        seen_n.add(mn)
        mods.append(LibModule.from_source(mn, 0, str(mr["source"]), origin=arm, rationale=str(mr.get("rationale", ""))[:200]))
    orch_src = str(prop["orchestrator_source"])
    if "def solve(" not in orch_src and "def optimize(" in orch_src:
        orch_src = orch_src.replace("def optimize(", "def solve(", 1)
    orch = LibModule.from_source("orchestrator", 0, orch_src, required_fn="solve", origin=arm, rationale=str(prop.get("rationale", ""))[:250])
    return CompositionalAlgoArtifact(arm=arm, track="S11_ATTRIBUTION", generation=0, modules=tuple(mods), orchestrator=orch)


def _run_artifact_wallclock(art: CompositionalAlgoArtifact, target: BilinearTensorF2, time_limit_sec: float = 0.50, seed: int = 0) -> Tuple[int, float, int]:
    """Run an artifact un-throttled under an EXACT real wall-clock budget `time_limit_sec`."""
    ns: Dict[str, Any] = {}
    for m in art.modules:
        exec(compile(m.source, m.name, "exec"), ns)
    exec(compile(art.orchestrator.source, "orchestrator", "exec"), ns)
    init_red = reduce_bilinear_terms(target.init_terms)
    best_box = [list(init_red)]
    t0 = time.perf_counter()

    class _WB:
        limit = 10_000_000
        @property
        def spent(self) -> int:
            return int(min(1.0, (time.perf_counter() - t0) / max(1e-6, time_limit_sec)) * self.limit)

    class _Lib:
        def __getattr__(self, name: str) -> Any:
            return ns[name]
        def has(self, name: str) -> bool:
            return name in ns

    def api_submit(terms: Sequence[Tuple[int, int, int]], tag: str = "t") -> bool:
        red = reduce_bilinear_terms(terms)
        if len(red) < len(best_box[0]) and verify_bilinear_decomp(target, red):
            best_box[0] = red
            return True
        return False

    wb = _WB()
    api = {
        "na": target.na, "nb": target.nb, "nc": target.nc,
        "init_terms": list(init_red), "seed": seed, "v3_budget": wb.limit,
        "reduce_terms": reduce_bilinear_terms,
        "flip_pair": apply_flip,
        "plus_split": apply_plus,
        "submit_best": api_submit,
        "rem_budget": lambda: max(0, wb.limit - wb.spent),
    }
    err_cnt = 0
    try:
        out = ns["solve"](api, _Lib(), wb)
        if isinstance(out, (list, tuple)):
            api_submit(out, "final")
    except Exception:
        err_cnt = 1
    assert verify_bilinear_decomp(target, best_box[0])
    return len(best_box[0]), round(time.perf_counter() - t0, 4), err_cnt


def run_phase_b_propose(out_path: Path, n_trials: int = 4, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """Generate K=4 independent UNGUIDED trials + K=4 independent GUIDED trials (100% tool-less, 1 call each)."""
    tasks = build_s11_attribution_suite()
    msha = s11_attr_manifest_sha256(tasks)
    meter = WorkMeter()
    trials: List[Dict[str, Any]] = []

    for cond, tmpl in (("UNGUIDED", UNGUIDED_PROMPT_TEMPLATE), ("GUIDED", GUIDED_PROMPT_TEMPLATE)):
        for k in range(1, n_trials + 1):
            tag = f"{cond}_T{k}"
            prompt = tmpl.format(common=COMMON_CONTRACT, trial_tag=tag)
            t0 = time.perf_counter()
            cost = 0.0
            rec: Dict[str, Any] = {"condition": cond, "trial": k, "tag": tag, "valid": False}
            try:
                prop, cost, _ = _call_claude_isolated(prompt, model=model)
                art = _parse_trial_artifact(prop, arm=tag)
                # Quick 1-task smoke check (just to record valid vs runtime error; NEVER retry!)
                sol, tel = run_s10_artifact(art, tasks[0].tensor, seed=0, v3_budget=300_000)
                rec["valid"] = True
                rec["rationale"] = str(prop.get("rationale", ""))[:500]
                rec["artifact"] = art.to_dict()
                rec["smoke_rank"] = len(sol)
                rec["smoke_ops"] = tel.get("ops_spent", 0)
                rec["smoke_ferr"] = tel.get("fn_errors", {})
                rec["total_lines"] = sum(len(m.source.splitlines()) for m in art.modules) + len(art.orchestrator.source.splitlines())
                print(f"[PHASE B PROPOSE] {tag:12s}: VALID ({rec['total_lines']}L) | smoke={tasks[0].base_rank}->{len(sol)} | ferr={len(rec['smoke_ferr'])} | ${cost:.3f}", flush=True)
            except Exception as exc:
                rec["error"] = str(exc)[:400]
                print(f"[PHASE B PROPOSE] {tag:12s}: FAILED -> {rec['error'][:140]} | ${cost:.3f}", flush=True)
            dt = time.perf_counter() - t0
            rec["cost_usd"] = cost
            rec["wall_sec"] = round(dt, 2)
            meter.charge_cpu(dt, phase=tag)
            meter.charge_llm_proposal(cost, accepted=rec["valid"], phase=tag)
            trials.append(rec)

    payload = {
        "track": "S11_PHASE_B_ATTRIBUTION",
        "manifest_sha256": msha,
        "n_tasks": len(tasks),
        "n_trials_per_condition": n_trials,
        "model": model,
        "trials": trials,
        "sleep_meter": meter.snapshot(),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[PHASE B PROPOSE DONE] Wrote {out_path} | total_usd=${payload['sleep_meter']['total_usd']:.4f}", flush=True)
    return payload


def run_phase_b_eval(proposals_path: Path, out_path: Path) -> Dict[str, Any]:
    """Evaluate ALL 8 trials (preserving successes & failures!) + Faithful KM-2023 on the N=40 fresh suite
    under BOTH (1) equalized real wall-clock (0.50s/task) AND (2) equalized OpBudget v3 (1.8M ops/task)!"""
    prop = json.loads(proposals_path.read_text(encoding="utf-8"))
    tasks = build_s11_attribution_suite()
    assert s11_attr_manifest_sha256(tasks) == prop["manifest_sha256"]

    # 1. Faithful KM-2023 Reference at 0.50s/task (3-seed median per distinct task, N=40 tasks!)
    km_wall_scores: Dict[str, int] = {}
    km_w_tot = 0.0
    for t in tasks:
        rs = []
        for sd in (0, 1, 2):
            _, mk = km2023_reference_search(t.tensor, time_limit_sec=0.50, seed=sd)
            rs.append(mk["rank"]); km_w_tot += mk["wall_sec"]
        km_wall_scores[t.task_id] = int(statistics.median(rs))
    km_tot = sum(km_wall_scores.values())
    base_tot = sum(t.base_rank for t in tasks)
    planted_ub_tot = sum(t.planted_upper_bound for t in tasks if t.planted_upper_bound is not None)
    km_planted = sum(km_wall_scores[t.task_id] for t in tasks if t.stratum == "attr_planted")
    print(f"[PHASE B EVAL] N={len(tasks)} distinct tasks | Base={base_tot} | Planted_UB(20)={planted_ub_tot} | KM2023_ref(0.50s)={km_tot} (Planted={km_planted}, wall={km_w_tot:.1f}s)", flush=True)

    results = []
    for tr in prop["trials"]:
        tag = tr["tag"]
        if not tr.get("valid"):
            results.append({"tag": tag, "condition": tr["condition"], "valid": False, "error": tr.get("error"), "wall_tot": base_tot, "v3_tot": base_tot})
            print(f"  {tag:12s}: INVALID (preserved failure -> base_rank={base_tot})", flush=True)
            continue
        art = CompositionalAlgoArtifact.from_dict(tr["artifact"])
        # Equalized Real Wall-Clock (0.50s/run, 3-seed median -> 1 score per distinct task!)
        w_scores: Dict[str, int] = {}
        w_sec = 0.0
        w_errs = 0
        for t in tasks:
            rs = []
            for sd in (0, 1, 2):
                r, dt, ec = _run_artifact_wallclock(art, t.tensor, time_limit_sec=0.50, seed=sd)
                rs.append(r); w_sec += dt; w_errs += ec
            w_scores[t.task_id] = int(statistics.median(rs))
        # Equalized OpBudget v3 (1.8M ops/task, seed=0)
        v3_scores: Dict[str, int] = {}
        v3_sec = 0.0
        v3_ops = 0
        v3_ferr = 0
        for t in tasks:
            t0 = time.perf_counter()
            sol, tel = run_s10_artifact(art, t.tensor, seed=0, v3_budget=DEFAULT_S10_V3_BUDGET)
            v3_sec += time.perf_counter() - t0
            v3_scores[t.task_id] = len(sol)
            v3_ops += int(tel.get("ops_spent", 0))
            v3_ferr += sum(tel.get("fn_errors", {}).values())
        wtot = sum(w_scores.values())
        v3tot = sum(v3_scores.values())
        w_pl = sum(w_scores[t.task_id] for t in tasks if t.stratum == "attr_planted")
        w_vs_km = paired_wilcoxon_stats([w_scores[t.task_id] - km_wall_scores[t.task_id] for t in tasks])
        # Automated mechanism fingerprint audit on source code
        all_src = "\n".join(m.source for m in art.modules) + "\n" + art.orchestrator.source
        mech_flags = _detect_mechanisms(all_src)
        rec = {
            "tag": tag, "condition": tr["condition"], "valid": True,
            "lines": tr.get("total_lines"), "cost_usd": tr.get("cost_usd"),
            "wall_tot": wtot, "wall_planted": w_pl, "wall_sec": round(w_sec, 1), "wall_errs": w_errs,
            "v3_tot": v3tot, "v3_sec": round(v3_sec, 1), "v3_ops": v3_ops, "v3_ferr": v3_ferr,
            "vs_km2023_wall": w_vs_km,
            "mechanisms": mech_flags,
            "per_task_wall": w_scores,
            "per_task_v3": v3_scores,
        }
        results.append(rec)
        print(
            f"  {tag:12s} ({tr['condition']:8s}): WALL(0.5s)={wtot:4d} (Pl={w_pl:3d}, vs KM={w_vs_km['sum_delta']:+4.0f} p={w_vs_km['p_two']:.4f}, {w_sec:5.1f}s) "
            f"| V3={v3tot:4d} ({v3_sec:5.1f}s, ferr={v3_ferr}) | mech={mech_flags}",
            flush=True,
        )

    # Compare best & median UNGUIDED vs GUIDED
    ung = [r for r in results if r["condition"] == "UNGUIDED" and r["valid"]]
    gui = [r for r in results if r["condition"] == "GUIDED" and r["valid"]]
    summary = {
        "n_distinct_tasks": len(tasks),
        "base_total": base_tot,
        "planted_upper_bound_20": planted_ub_tot,
        "km2023_wall_total": km_tot,
        "km2023_planted_20": km_planted,
        "unguided_valid": len(ung),
        "guided_valid": len(gui),
        "unguided_wall_totals": [r["wall_tot"] for r in ung],
        "guided_wall_totals": [r["wall_tot"] for r in gui],
        "unguided_v3_totals": [r["v3_tot"] for r in ung],
        "guided_v3_totals": [r["v3_tot"] for r in gui],
    }
    if ung and gui:
        best_u = min(ung, key=lambda r: r["wall_tot"])
        best_g = min(gui, key=lambda r: r["wall_tot"])
        summary["best_unguided_vs_best_guided_wall"] = paired_wilcoxon_stats(
            [best_u["per_task_wall"][t.task_id] - best_g["per_task_wall"][t.task_id] for t in tasks]
        )
        summary["best_unguided_tag"] = best_u["tag"]
        summary["best_guided_tag"] = best_g["tag"]

    out = {"summary": summary, "km2023_per_task": km_wall_scores, "trials": results}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def _detect_mechanisms(src: str) -> Dict[str, bool]:
    low = src.lower()
    return {
        "incremental_pair_maps": any(k in low for k in ("uv", "by_pair", "pair_map", "pairs")),
        "gf2_gauss_slice_rank": any(k in low for k in ("piv", "echelon", "gauss", "mat_decomp", "row_red", "rref")),
        "lookahead_reduction": any(k in low for k in ("lookahead", "gain", "hits", "cand_flip", "best_flip", "score")),
        "plus_escape": any(k in low for k in ("plus", "split")),
        "tabu_or_sa": any(k in low for k in ("tabu", "temp", "anneal", "visited")),
        "direct_pure_flip": "api[\"flip_pair\"]" not in src and "api['flip_pair']" not in src,
    }


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "propose":
        run_phase_b_propose(Path(sys.argv[2]))
    elif mode == "eval":
        run_phase_b_eval(Path(sys.argv[2]), Path(sys.argv[3]))
    else:
        raise SystemExit("Usage: python -m comp_sprint11_audit.phase_b_attribution <propose|eval> ...")
