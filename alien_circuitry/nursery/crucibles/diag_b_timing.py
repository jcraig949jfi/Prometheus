"""DIAGNOSTIC (not a result): time CRUCIBLE-B arms on VAL problems only (the steering set; no held problem is touched)
to size the repaired control. Uses crucible_b's MacroWorld unchanged. Explicit macro sets; never calls random_macros.
Usage: python -m alien_circuitry.nursery.crucibles.diag_b_timing [val_problems]
"""
from __future__ import annotations
import itertools, json, sys, time
import numpy as np
from ...ac01d.evaluate import Context
from . import crucible_b as B

MINED = [(1, 0), (0, 2), (0, 1), (0, 0), (2, 1), (2, 0)]   # recomputed FIT-only, see crucible_b_mining_and_control_feasibility.json


def main(n=20):
    t0 = time.perf_counter(); ctx = Context(per_set=n); D = ctx.U["D"]; print(f"context built {time.perf_counter()-t0:.1f}s", flush=True)
    all_len2 = list(itertools.product(range(3), repeat=2))
    alt = [m for m in all_len2 if m not in MINED] + MINED[:3]          # one arbitrary equal-size alternative subset
    arms = {"no_macros": [], "mined": MINED, "alt_subset": alt}
    pl = ctx.probs["VAL"]
    for arm, macros in arms.items():
        W = B.MacroWorld(ctx, macros)
        for kind, fn in (("DFS", W.dfs), ("GBFS", W.gbfs)):
            t = time.perf_counter(); R = [fn(s, j, D[:, j]) for s, j, d in pl]; dt = time.perf_counter() - t
            print(json.dumps({"set": "VAL", "arm": arm, "kind": kind, "problems": len(pl), "wall_s": round(dt, 2), "s_per_problem": round(dt / len(pl), 3),
                              "solve_rate": float(np.mean([r["solved"] for r in R])), "hit_budget": int(sum(r["exp"] > 40000 for r in R))}), flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 20)
