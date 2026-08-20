"""type_bridge_cycle.py — the Apollo type-bridge metabolic cycle, T0 -> T1.

Executes the preregistered 2x2 in `apollo/cycles/type_bridge/PREREGISTRATION.md`:

    BRIDGE {present, absent} x XOVER {0.3, 0.0}, five seeds, deterministic.

    A0 bridge absent  / xover off  -> the reproduced T0 state (June's 481-gen flat run)
    A1 bridge absent  / xover on   -> falsifier of C1 (expressivity)
    A2 bridge present / xover off  -> the classification call (search_operator vs not)
    A3 bridge present / xover on   -> T1, and the replay of the 2026-06-16 A/B treatment

Config matches `apollo/pivot/recombination_ab_result_2026-06-16.json` exactly (gens=400,
pop=24, seed_variant=ingredients, dispatch=False, seeds [20260616,1,7,42,101]) so A2/A3 are
a true replay rather than a fresh experiment that merely resembles one.

NO NEW ARCHITECTURE (heredity rule): the bridge ablation reuses `wall_corpus.remove_ops`,
which rebinds module globals on a freshly imported `blackboard_evolve` inside a throwaway
subprocess. The substrate is not edited on disk. The discovery signal is the substrate's
own pre-existing `novel_multitier` (blackboard_evolve.py:629) — no new meter.

DETERMINISTIC ONLY. `--mode llm` fired its own kill condition on 2026-06-28 and is not
reachable from this script.

Usage:
    python type_bridge_cycle.py --arm A3 --seed 42     # one cell, in-process
    python type_bridge_cycle.py --all                  # all 20, subprocess each
    python type_bridge_cycle.py --report               # analyse against the prereg
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src"
OUT = HERE.parent / "cycles" / "type_bridge"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(HERE))

SEEDS = [20260616, 1, 7, 42, 101]

ARMS = {
    "A0": {"bridge": False, "crossover_frac": 0.0, "role": "reproduced T0"},
    "A1": {"bridge": False, "crossover_frac": 0.3, "role": "C1 falsifier"},
    "A2": {"bridge": True,  "crossover_frac": 0.0, "role": "classification call"},
    "A3": {"bridge": True,  "crossover_frac": 0.3, "role": "T1 / A/B replay"},
}

BASE = dict(gens=400, pop_size=24, mode="deterministic",
            seed_variant="ingredients", dispatch=False, log_every=50)

BRIDGE_OP = "relations_from_facts"
# The substrate's own cross-tier predicate (blackboard_evolve.py:629) — not redefined here.
CROSS_TIER_OPS = ("forward_chain", "op_build_ordering")
# Pre-existing graduation threshold (n_distinct_real_shapes), not invented for this cycle.
GRAD_COMP_LIFT = 0.05
GRAD_MIN_LOAD_BEARING = 1


def run_cell(arm, seed):
    cfg = ARMS[arm]
    import blackboard_evolve as be
    import wall_corpus as wc

    if not cfg["bridge"]:
        # Same ablation as wall-corpus EX-02. Non-dispatch run, so replacement random
        # seeds must draw from the plain scorer pool to match an unablated run.
        wc.remove_ops(be, [BRIDGE_OP], scorer_pool=list(be.SCORERS))

    run_dir = OUT / "runs" / f"{arm}_seed{seed}"
    if run_dir.exists():
        for f in run_dir.glob("*.jsonl"):
            f.unlink()

    console = open(OUT / "runs" / f"{arm}_seed{seed}_console.log", "w", encoding="utf-8")
    old, t0 = sys.stdout, time.time()
    try:
        sys.stdout = console
        history = be.evolve(gens=BASE["gens"], pop_size=BASE["pop_size"],
                            mode=BASE["mode"], seed=seed, run_dir=str(run_dir),
                            log_every=BASE["log_every"], checkpoint_every=BASE["gens"],
                            crossover_frac=cfg["crossover_frac"],
                            seed_variant=BASE["seed_variant"], dispatch=BASE["dispatch"])
    finally:
        sys.stdout = old
        console.flush()
        console.close()

    nm = [h["novel_multitier"] for h in history]
    first = next((i + 1 for i, v in enumerate(nm) if v > 0), None)

    # Graduation check. MUST agree with the primary outcome: an organism counts only if it
    # is de-novo (lineage is not a bare seed), carries both tier ops, ACTUALLY SOLVES the
    # cross-tier canary at the substrate's own >=0.9 bar, and clears the pre-existing
    # graduation threshold. A looser check counted 321 "graduating" organisms in a run whose
    # novel_multitier was 0 — the two must never be allowed to disagree.
    ckpt = run_dir / "checkpoints" / f"branch_c_gen_{BASE['gens']:06d}.json"
    graduating = []
    if ckpt.exists():
        sys.path.insert(0, str(HERE))
        from cross_tier_canary import build_cross_tier_canary
        xt_tasks = build_cross_tier_canary(n=20)
        arch = json.loads(ckpt.read_text(encoding="utf-8"))["archive"]
        for e in arch:
            pl, lin = e["pipeline"], e.get("lineage", [])
            is_seed = len(lin) <= 1 and all(x.startswith("seed:") for x in lin)
            if is_seed or not all(o in pl for o in CROSS_TIER_OPS):
                continue
            if e["comp_lift"] <= GRAD_COMP_LIFT or e["n_load_bearing"] < GRAD_MIN_LOAD_BEARING:
                continue
            ops = [be.REGISTRY[n][0] for n in pl if n in be.REGISTRY]
            xt_acc = be._evaluate_acc(ops, xt_tasks)
            if xt_acc >= 0.9:
                graduating.append({"pipeline": pl, "acc": e["acc"],
                                   "cross_tier_acc": round(xt_acc, 3),
                                   "comp_lift": e["comp_lift"],
                                   "n_load_bearing": e["n_load_bearing"],
                                   "lineage": lin})
    graduating.sort(key=lambda g: -g["comp_lift"])

    disc = run_dir / "novel_discovery.jsonl"
    first_rec = None
    if disc.exists():
        lines = [l for l in disc.read_text(encoding="utf-8").splitlines() if l.strip()]
        if lines:
            first_rec = json.loads(lines[0])

    final = history[-1]
    rec = {
        "arm": arm, "seed": seed, "role": cfg["role"],
        "bridge_present": cfg["bridge"], "crossover_frac": cfg["crossover_frac"],
        "discovered": bool(nm and max(nm) > 0),
        "first_novel_gen": first,
        "final_novel_count": final["novel_multitier"],
        "n_graduating_cross_tier": len(graduating),
        "graduating_top3": graduating[:3],
        "first_discovery_record": first_rec,
        "max_acc": final["max_acc"],
        "best_comp_lift": final["best_comp_lift"],
        "best_n_load_bearing": final["best_n_load_bearing"],
        "best_ccs": final["best_causal_composition_score"],
        "portfolio_per_subset": final.get("portfolio_per_subset"),
        "archive_cells": final["archive_cells"],
        "wall_clock_s": round(time.time() - t0, 1),
        "config": {**BASE, "crossover_frac": cfg["crossover_frac"],
                   "bridge_op_present": cfg["bridge"], "seed": seed},
    }
    (OUT / "cells").mkdir(parents=True, exist_ok=True)
    with open(OUT / "cells" / f"{arm}_seed{seed}.json", "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    return rec


def report():
    cells = sorted((OUT / "cells").glob("*.json"))
    recs = [json.loads(c.read_text(encoding="utf-8")) for c in cells]
    by_arm = {}
    for r in recs:
        by_arm.setdefault(r["arm"], []).append(r)

    print(f"{'arm':4s} {'bridge':7s} {'xover':6s} {'disc':6s} {'grad':5s} "
          f"{'first_gen':>22s}  {'max_acc':>8s} {'comp_lift':>10s} {'lb':>3s}  role")
    summary = {}
    for arm in ("A0", "A1", "A2", "A3"):
        rs = sorted(by_arm.get(arm, []), key=lambda r: SEEDS.index(r["seed"]))
        if not rs:
            continue
        n = sum(1 for r in rs if r["discovered"])
        ngrad = sum(1 for r in rs if r["n_graduating_cross_tier"] > 0)
        gens = [str(r["first_novel_gen"]) if r["first_novel_gen"] else "-" for r in rs]
        cfg = ARMS[arm]
        summary[arm] = {"discovery_rate": f"{n}/{len(rs)}", "n_discovered": n,
                        "n_seeds": len(rs), "n_graduating": ngrad,
                        "first_novel_gens": [r["first_novel_gen"] for r in rs],
                        "max_acc": [r["max_acc"] for r in rs],
                        "best_comp_lift": [r["best_comp_lift"] for r in rs]}
        print(f"{arm:4s} {str(cfg['bridge']):7s} {cfg['crossover_frac']:<6} "
              f"{n}/{len(rs):<4} {ngrad}/{len(rs):<3} {','.join(gens):>22s}  "
              f"{max(r['max_acc'] for r in rs):>8} "
              f"{max(r['best_comp_lift'] for r in rs):>10} "
              f"{max(r['best_n_load_bearing'] for r in rs):>3}  {cfg['role']}")

    # ── Pre-committed decision rules (PREREGISTRATION.md §4) ──
    a0, a1, a2, a3 = (summary.get(k, {}).get("n_discovered") for k in ("A0", "A1", "A2", "A3"))
    grad3 = summary.get("A3", {}).get("n_graduating", 0)
    verdicts = {}

    if a3 is not None and a0 is not None:
        verdicts["cycle"] = ("SUCCESS" if (a3 >= 3 and grad3 >= 1 and a0 == 0)
                             else "FAILURE-REPLAY" if a3 == 0
                             else "INCONCLUSIVE")
    if a1 is not None:
        verdicts["C1_expressivity"] = ("FALSIFIED — cross-tier reachable without the bridge"
                                       if a1 >= 3 else
                                       "INCONCLUSIVE" if a1 >= 1 else
                                       "SURVIVES — no discovery without the bridge")
    if a2 is not None and a3 is not None:
        verdicts["classification"] = (
            "search_operator — crossover NECESSARY; kill count stays 5; lane REDIRECTS"
            if (a2 == 0 and a3 >= 3) else
            "part_of_evolutionary_search — mutation suffices; count RESETS; lane CONTINUES"
            if a2 >= 3 else
            "INCONCLUSIVE — A2 landed 1-2/5; both sensitivities reported, no ruling")

    print("\nPre-committed verdicts (PREREGISTRATION.md §4):")
    for k, v in verdicts.items():
        print(f"  {k:18s} {v}")

    out = {"summary": summary, "verdicts": verdicts,
           "prereg": "apollo/cycles/type_bridge/PREREGISTRATION.md",
           "generated": "2026-08-19", "generator": "Apollo (M2)"}
    with open(OUT / "RESULT.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=list(ARMS))
    ap.add_argument("--seed", type=int)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    (OUT / "runs").mkdir(parents=True, exist_ok=True)

    if args.report:
        report()
        return

    if args.arm and args.seed is not None:
        r = run_cell(args.arm, args.seed)
        print(f"{args.arm} seed={args.seed}: discovered={r['discovered']} "
              f"first_gen={r['first_novel_gen']} novel={r['final_novel_count']} "
              f"grad={r['n_graduating_cross_tier']} max_acc={r['max_acc']} "
              f"({r['wall_clock_s']}s)")
        return

    if args.all:
        for arm in ("A0", "A1", "A2", "A3"):
            for seed in SEEDS:
                r = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                    "--arm", arm, "--seed", str(seed)],
                                   capture_output=True, text=True)
                if r.returncode == 0:
                    print(f"  {r.stdout.strip()}", flush=True)
                else:
                    print(f"  {arm} seed={seed}: FAILED\n{r.stderr[-1200:]}", flush=True)
        print()
        report()


if __name__ == "__main__":
    main()
