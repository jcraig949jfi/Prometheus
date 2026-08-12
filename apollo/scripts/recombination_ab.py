"""recombination_ab.py — empirical A/B: does the crossover operator discover the
novel multi-tier organism single-step mutation cannot?

Both arms start from the SAME 'ingredients' seeding (the two splice-parents but
NOT the pre-assembled cross-tier solver) and run the SAME deterministic
single-step mutation. The ONLY difference is the operator under test:

  control   : crossover_frac = 0.0   (single-step mutation only — the Run 1+2 regime)
  treatment : crossover_frac = 0.3   (single-step + recombination)

Metric: gen of first de-novo multi-tier solver (novel_multitier > 0), i.e. an
archive organism that is NOT a seed, contains both an R2 inference op and an R1
ordering op, and solves the cross-tier subset (>=0.9). Run across several seeds
so the effect is statistical, not one lucky draw.

Deterministic mode isolates the operator (no LLM variance); the crossover claim
is about valley-crossing, which the falsification proved is mutation-type
independent. Granite stays warm for the production --mode llm run after this.

Usage:
    python recombination_ab.py
"""
import sys
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from blackboard_evolve import evolve

SEEDS = [20260616, 1, 7, 42, 101]
GENS = 400
POP = 24


def first_novel_gen(history):
    for rec in history:
        if rec.get("novel_multitier", 0) > 0:
            return rec["gen"]
    return None


def run_arm(arm, crossover_frac, seed):
    run_dir = ROOT / "run_recomb" / f"ab_{arm}_seed{seed}"
    hist = evolve(gens=GENS, pop_size=POP, mode="deterministic",
                  seed=seed, run_dir=str(run_dir), log_every=10_000,
                  checkpoint_every=GENS, crossover_frac=crossover_frac,
                  seed_variant="ingredients")
    g = first_novel_gen(hist)
    # best cross-tier-solving novel pipeline at the end, if any
    return {"seed": seed, "first_novel_gen": g,
            "discovered": g is not None,
            "final_novel_count": hist[-1].get("novel_multitier", 0)}


def main():
    print("=" * 78)
    print("RECOMBINATION A/B — gen of first de-novo multi-tier solver")
    print(f"  {len(SEEDS)} seeds x {GENS} gens, pop {POP}, deterministic, ingredients-seeded")
    print("=" * 78)

    results = {"control": [], "treatment": []}
    for seed in SEEDS:
        c = run_arm("control", 0.0, seed)
        t = run_arm("treatment", 0.3, seed)
        results["control"].append(c)
        results["treatment"].append(t)
        print(f"  seed {seed:>9} | control: {_fmt(c)}   | treatment: {_fmt(t)}")

    print()
    print("--- summary ---")
    for arm in ("control", "treatment"):
        rs = results[arm]
        n_disc = sum(r["discovered"] for r in rs)
        gens_found = [r["first_novel_gen"] for r in rs if r["discovered"]]
        med = sorted(gens_found)[len(gens_found) // 2] if gens_found else None
        print(f"  {arm:<10}: discovered {n_disc}/{len(rs)} seeds | "
              f"first-novel gens={gens_found} | median={med}")

    c_disc = sum(r["discovered"] for r in results["control"])
    t_disc = sum(r["discovered"] for r in results["treatment"])
    verdict = t_disc > c_disc
    print()
    if verdict and c_disc == 0:
        print("  RESULT = crossover discovers the novel multi-tier organism that")
        print("  single-step mutation never reaches. The operator is the lever; the")
        print("  Run 1+2 plateau was a search-operator failure, not substrate/eval.")
    elif verdict:
        print(f"  RESULT = crossover discovers MORE often ({t_disc} vs {c_disc}) and/or")
        print("  faster. Operator helps; control occasionally crosses by drift.")
    else:
        print(f"  RESULT = no crossover advantage ({t_disc} vs {c_disc}). Re-examine.")

    out = {
        "experiment": "recombination_ab",
        "date": "2026-06-16",
        "gens": GENS, "pop": POP, "seeds": SEEDS,
        "mode": "deterministic", "seed_variant": "ingredients",
        "control_crossover_frac": 0.0, "treatment_crossover_frac": 0.3,
        "results": results,
        "control_discovered": c_disc, "treatment_discovered": t_disc,
        "crossover_advantage": verdict,
    }
    art = ROOT / "pivot" / "recombination_ab_result_2026-06-16.json"
    with open(art, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\n  artifact -> {art}")
    return verdict


def _fmt(r):
    return f"first_novel_gen={r['first_novel_gen']}" if r["discovered"] else "NOT discovered"


if __name__ == "__main__":
    main()
