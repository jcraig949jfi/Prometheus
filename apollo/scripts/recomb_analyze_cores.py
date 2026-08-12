"""Characterize distinct load-bearing cores among novel multi-tier solvers per
A/B run, so we report genuine discovery rather than padding-inflated cell counts."""
import json, glob, os, sys

ROOT = r"D:\Prometheus\apollo\run_recomb"
SEEDS = [20260616, 1, 7, 42, 101]


def analyze(arm, seed):
    d = os.path.join(ROOT, f"ab_{arm}_seed{seed}", "checkpoints")
    fs = sorted(glob.glob(os.path.join(d, "*.json")))
    if not fs:
        return None
    a = json.load(open(fs[-1], encoding="utf-8"))
    cells = a["archive"]
    solv = [c for c in cells
            if "forward_chain" in c["pipeline"] and "op_build_ordering" in c["pipeline"]]
    cores = set(tuple(c["load_bearing_core"]) for c in solv)
    shortest = min(solv, key=lambda c: len(c["pipeline"])) if solv else None
    return {"total_cells": a["n_cells"], "mt_solver_cells": len(solv),
            "distinct_LB_cores": len(cores), "shortest": shortest}


def main():
    for arm in ("control", "treatment"):
        print(f"=== {arm} ===")
        for seed in SEEDS:
            r = analyze(arm, seed)
            if r is None:
                print(f"  seed {seed}: (no checkpoint)")
                continue
            line = (f"  seed {seed:>9}: cells={r['total_cells']:>3} "
                    f"mt_solver_cells={r['mt_solver_cells']:>3} "
                    f"distinct_cores={r['distinct_LB_cores']:>2}")
            print(line)
            if r["shortest"]:
                print(f"      shortest solver (acc={r['shortest']['acc']}): "
                      f"{' -> '.join(r['shortest']['pipeline'])}")


if __name__ == "__main__":
    main()
