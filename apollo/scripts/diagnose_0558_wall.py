"""diagnose_0558_wall.py — falsification-first decomposition of the best_acc 0.558 plateau.

Three hypotheses for why best_acc plateaus at 0.558 after crossover found the
cross-tier solver:
  H-express : substrate/organism-model can't express a solver for the failed tasks
  H-eval    : the failed tasks are unsolvable/mislabeled (0.558 is the true max)
  H-operator: a solver IS expressible but neither single-step nor 1-pt crossover finds it

Diagnostic strategy:
  1. Rebuild the exact battery, tag each task by subset.
  2. Per-subset accuracy of the gen-400 elite + every seed specialist.
  3. ORACLE/PORTFOLIO coverage: if each task is routed to the archive occupant
     that solves it, what fraction of the battery is covered? This separates
     "no single organism can cover a heterogeneous battery" (organism-model
     ceiling — best_acc is the wrong metric) from "no organism anywhere solves
     these tasks" (true expressibility/eval ceiling).

Writes a structured report (per-cell flush) to stdout AND results JSON.
"""
from __future__ import annotations
import sys, json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from blackboard import BlackboardState, run_pipeline
import blackboard_evolve as ev
from composition_gauntlet import build_synthetic_canary
from inference_canary import build_inference_canary
from cross_tier_canary import build_cross_tier_canary

OUT = []
def emit(s=""):
    print(s, flush=True)
    OUT.append(s)

# ── rebuild battery with subset tags ─────────────────────────────────
canary = json.load(open(ROOT / "data" / "clean_canary_v01.json", encoding="utf-8"))["tasks"]
synth = build_synthetic_canary(n_each=15)
inference = build_inference_canary(n=20)
cross_tier = build_cross_tier_canary(n=20)

subsets = {"canary": canary, "synth": synth, "inference": inference, "cross_tier": cross_tier}
tagged = []
for name, ts in subsets.items():
    for t in ts:
        tagged.append((name, t))
tasks_all = [t for _, t in tagged]
N = len(tasks_all)

emit(f"=== BATTERY: {N} tasks ===")
for name, ts in subsets.items():
    emit(f"  {name:12s}: {len(ts)} tasks")
single_baseline = ev._single_primitive_baseline(tasks_all)
emit(f"  single-primitive baseline (oracle single answer field): {single_baseline:.3f}")
emit("")

def per_subset_acc(pipeline_names):
    ops = [ev.REGISTRY[n][0] for n in pipeline_names if n in ev.REGISTRY]
    if not ops:
        return {}, 0.0
    res = {}
    total_correct = 0
    for name, ts in subsets.items():
        nc = 0
        for t in ts:
            s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
            try:
                out = run_pipeline(ops, s)
                if out.selected_answer == t["correct"]:
                    nc += 1
                    total_correct += 1
            except Exception:
                pass
        res[name] = nc / max(len(ts), 1)
    return res, total_correct / max(N, 1)

# ── gen-400 elite ─────────────────────────────────────────────────────
ckpt = json.load(open(ROOT / "run_branch_c_xover" / "checkpoints" / "branch_c_gen_000400.json"))
archive = ckpt["archive"]
elite = max(archive, key=lambda e: e["acc"])
emit("=== GEN-400 ELITE (best_acc organism) ===")
emit(f"  pipeline: {elite['pipeline']}")
emit(f"  terminal: {elite['terminal_scorer']}   overall acc: {elite['acc']}")
ps, overall = per_subset_acc(elite["pipeline"])
emit(f"  recomputed overall: {overall:.3f}")
for k, v in ps.items():
    emit(f"    {k:12s}: {v:.3f}")
emit("")

# ── seed specialists ──────────────────────────────────────────────────
emit("=== SEED SPECIALISTS (per-subset) ===")
seeds = {
    "COMP_A (order)":       ["parse_names_and_relations","parse_ordinal","op_build_ordering","select_nth"],
    "COMP_C (aggregate)":   ["parse_box_items","op_aggregate_quantities","score_by_aggregate"],
    "COMP_R2 (inference)":  ["parse_rules","forward_chain","score_by_derivability"],
    "COMP_CROSS_TIER":      ["parse_rules","parse_ordinal","forward_chain","relations_from_facts","op_build_ordering","select_nth"],
}
for label, pl in seeds.items():
    ps, overall = per_subset_acc(pl)
    emit(f"  {label:22s} overall={overall:.3f}  " + "  ".join(f"{k}={v:.2f}" for k,v in ps.items()))
emit("")

# ── ORACLE / PORTFOLIO coverage over the whole archive ────────────────
# For each task, is there ANY archive occupant that solves it?
emit("=== ORACLE PORTFOLIO COVERAGE (archive as portfolio) ===")
# precompute each occupant's correctness vector
occupant_ops = []
for e in archive:
    ops = [ev.REGISTRY[n][0] for n in e["pipeline"] if n in ev.REGISTRY]
    occupant_ops.append((e, ops))

covered = 0
per_subset_cov = defaultdict(lambda: [0,0])
uncovered_examples = []
for name, t in tagged:
    per_subset_cov[name][1] += 1
    hit = False
    for e, ops in occupant_ops:
        s = BlackboardState(problem_text=t["prompt"], candidates=t["candidates"])
        try:
            out = run_pipeline(ops, s)
            if out.selected_answer == t["correct"]:
                hit = True
                break
        except Exception:
            pass
    if hit:
        covered += 1
        per_subset_cov[name][0] += 1
    elif len(uncovered_examples) < 12:
        uncovered_examples.append((name, t.get("prompt","")[:90], t.get("correct"), t.get("candidates")))

emit(f"  PORTFOLIO coverage (any archive occupant solves task): {covered}/{N} = {covered/N:.3f}")
for name in subsets:
    c, tot = per_subset_cov[name]
    emit(f"    {name:12s}: {c}/{tot} = {c/max(tot,1):.3f}")
emit(f"  (single best organism = {elite['acc']}; gap to portfolio = {covered/N - elite['acc']:.3f})")
emit("")

emit("=== UNCOVERED TASKS (solved by NO archive occupant) ===")
if not uncovered_examples:
    emit("  none — every task is solved by at least one archive organism.")
for name, prompt, correct, cands in uncovered_examples:
    emit(f"  [{name}] correct={correct!r} cands={cands}")
    emit(f"      prompt: {prompt}")
emit("")

# count uncovered per subset
emit("=== INTERPRETATION GUIDE ===")
emit("  portfolio >> best_acc, ~all subsets covered  -> organism-model ceiling")
emit("        (best_acc tracks one fixed-terminal pipeline; battery is heterogeneous;")
emit("         fix = portfolio/dispatch metric or multi-terminal organism, NOT new primitive)")
emit("  portfolio ~= best_acc, a subset stuck at ~chance -> H-express or H-eval")
emit("        (inspect uncovered tasks: solvable-by-hand => operator gap; unsolvable => eval ceiling)")

json.dump({"battery_N": N, "subset_sizes": {k: len(v) for k,v in subsets.items()},
           "single_baseline": single_baseline,
           "elite_pipeline": elite["pipeline"], "elite_acc": elite["acc"],
           "elite_per_subset": per_subset_acc(elite["pipeline"])[0],
           "portfolio_coverage": covered/N,
           "portfolio_per_subset": {k: per_subset_cov[k][0]/max(per_subset_cov[k][1],1) for k in subsets},
           "n_uncovered": N - covered},
          open(ROOT / "pivot" / "diagnose_0558_result_2026-06-22.json", "w"), indent=2)
emit("\nwrote pivot/diagnose_0558_result_2026-06-22.json")
