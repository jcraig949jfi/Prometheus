"""Sweep parsimony alpha and measure Spearman(length, val_err).

Question: is the length-compensation artefact (Gate 4) defeatable by
parsimony alone, or is it asymptotic?

Protocol: for each alpha in a sweep, run a small evolutionary search and
measure the final Spearman correlation between length and -log10(val_err)
across the archive. Reset seeds between alphas so conditions are
comparable.

Uses evolve_tt_v4 in 2-family mode (no cross) to isolate the alpha effect.
"""

import json
import random
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

import evolve_tt_v4 as v4

HERE = Path(__file__).parent

ALPHAS = [0.0, 0.001, 0.002, 0.005, 0.01, 0.02]
POP = 20
GENS = 20


def run_one(alpha):
    v4.PARSIMONY = alpha
    # reset module-level RNGs so each alpha starts identically
    v4.rng = np.random.default_rng(v4.SEED)
    random.seed(v4.SEED)
    arc, hist = v4.run(pop_size=POP, gens=GENS, log_every=GENS)
    if not arc:
        return None
    cells = list(arc.values())
    lens = [len(c["genome"]) for c in cells]
    verrs = [-np.log10(c["val_err"] + 1e-15) for c in cells]
    rho, pv = spearmanr(lens, verrs)
    best = min(cells, key=lambda v: v["val_err"])
    return {
        "alpha": alpha,
        "rho": float(rho),
        "p": float(pv),
        "best_val": best["val_err"],
        "best_len": best["length"],
        "best_rank": best["rank"],
        "mean_len": float(np.mean(lens)),
        "median_len": float(np.median(lens)),
        "archive_size": len(cells),
    }


def main():
    rows = []
    for alpha in ALPHAS:
        print(f"\n{'='*60}")
        print(f"Alpha = {alpha}")
        print(f"{'='*60}", flush=True)
        r = run_one(alpha)
        if r is None:
            print("  archive empty")
            continue
        print(f"\n  rho={r['rho']:+.3f}  p={r['p']:.3f}  "
              f"best_val={r['best_val']:.3e}  best_len={r['best_len']}  "
              f"mean_len={r['mean_len']:.1f}  archive={r['archive_size']}",
              flush=True)
        rows.append(r)

    print(f"\n{'='*60}")
    print("ALPHA SWEEP SUMMARY")
    print(f"{'='*60}")
    print(f"{'alpha':<8} {'rho':<8} {'p':<8} {'best_val':<12} "
          f"{'best_len':<10} {'mean_len':<10} {'archive':<8}")
    for r in rows:
        print(f"{r['alpha']:<8.3f} {r['rho']:<+8.3f} {r['p']:<8.3f} "
              f"{r['best_val']:<12.3e} {r['best_len']:<10} "
              f"{r['mean_len']:<10.1f} {r['archive_size']:<8}")

    with open(HERE / "alpha_sweep.json", "w") as f:
        json.dump({"pop": POP, "gens": GENS, "rows": rows}, f, indent=2)
    print(f"\nSaved: {HERE / 'alpha_sweep.json'}")


if __name__ == "__main__":
    main()
