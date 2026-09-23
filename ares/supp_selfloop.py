"""EXPLORATORY post-hoc (2026-09-21, after the cycle-1 disposition): the
four W4 champions with no load-bearing HIDDEN node all carry self-loop
edges (a node feeding itself), often on an OUTPUT node, which node
ablation never removes. Test across every present champion of W4, W13,
W5: count self-loops; zero all self-loop edges and re-evaluate. If the
carrier is self-recurrence, this ablation collapses W4 the way
no_activation_mem does. Writes runs/sweep_c1/selfloop.json. Changes no
disposition; explains it.

    python -m ares.supp_selfloop
"""
import json
import os

import numpy as np

from . import search as R
from . import substrate as S
from .validate import FLOOR, OUT, SEEDS, seeds_for


def main():
    rows = []
    for w in ("W4", "W13", "W5"):
        world = R.make_world(w, "present")
        seeds = seeds_for(w, "present")
        for sd in SEEDS:
            p = os.path.join(OUT, f"{w}_present_s{sd}.json")
            if not os.path.exists(p):
                continue
            g = json.load(open(p))["final"]["genome"]
            pop = S.Population.from_genomes([g])
            n = pop.cfg.n
            diag = np.arange(n)
            self_edges = [(int(i), g["op"][i], "out" if i >= n - 3 else "hid") for i in diag
                          if (pop.W1[0, i, i] != 0 or pop.W2[0, i, i] != 0) and pop.alive[0, i]]
            intact = float(R.rollout(pop, world, seeds)[0])
            cut = pop.copy()
            cut.W1[0, diag, diag] = 0; cut.W2[0, diag, diag] = 0; cut.R[0, diag, diag] = 0
            no_self = float(R.rollout(cut, world, seeds)[0])
            # keep-only ablation: zero keep everywhere, self-loops intact
            kp = pop.copy(); kp.keep[:] = 0
            no_keep = float(R.rollout(kp, world, seeds)[0])
            n_keep = int(((pop.keep[0] > 0.3) & pop.alive[0]).sum())
            rows.append(dict(world=w, seed=sd, intact=intact, no_self_loops=no_self, no_keep=no_keep,
                             self_loops=self_edges, n_self=len(self_edges), n_keep_nodes=n_keep,
                             self_out=sum(1 for e in self_edges if e[2] == "out")))
            print(f"{w} s{sd:<2d} intact {intact:6.2f} no_self {no_self:6.2f} no_keep {no_keep:6.2f} "
                  f"self_loops {len(self_edges)} (on outputs {rows[-1]['self_out']}) keep_nodes {n_keep} {[e[1] for e in self_edges]}")
    for w in ("W4", "W13", "W5"):
        rs = [r for r in rows if r["world"] == w]
        gain = lambda r: max(r["intact"] - FLOOR[w], 1e-9)
        coll_self = sum(1 for r in rs if (r["no_self_loops"] - FLOOR[w]) <= 0.25 * gain(r))
        coll_keep = sum(1 for r in rs if (r["no_keep"] - FLOOR[w]) <= 0.25 * gain(r))
        has_self = sum(1 for r in rs if r["n_self"] > 0)
        print(f"{w}: champions with self-loops {has_self}/{len(rs)}; collapse under self-loop cut {coll_self}/{len(rs)}; "
              f"collapse under keep cut {coll_keep}/{len(rs)}")
    json.dump(dict(note="EXPLORATORY post-hoc; see ARES_CYCLE1_REPORT s3", rows=rows,
                   receipt=R.receipt(S.Config(), "selfloop", "present", 1, 0, 32, 0)),
              open(os.path.join(OUT, "selfloop.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
