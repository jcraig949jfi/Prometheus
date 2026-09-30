"""D001-08 analysis (NOT RUN by the worker -- outputs unknown).

Inputs, all at repo commit 0424c372a6bb (receipts produced at code_commit
ab137f52b, cycle 2):
  ares/runs/sweep_c2/gates.txt
  ares/runs/sweep_c2/battery.json                 (robustness_cost)
  ares/runs/sweep_c2/W15_present_s{201..210}.json (snapshots, final genome)
  ares/runs/sweep_c2/W15_present_s{201..210}_dissect.json
  ares/runs/sweep_c2/c1_all_s{201..210}.json      (W4 control snapshots)
Code: ares/carriers.py, ares/search.py, ares/substrate.py, ares/cycle2.py
      (numpy only). Run with REPO=<repo root>:  python analysis.py [A|B|C]

PART A (stdlib only): exact Fisher tests quoted in REPORT.md s3.1, and
  the battery table (W15 score of W4-evolved champions by class).
PART B (imports ares): per-snapshot carrier ablation on W15 and W4
  lineages -> for each lineage, the first generation at which recurrence
  and plasticity each become load-bearing, and the fitness at that time.
PART C (imports ares): refined cuts that separate "plastic weight on a
  recurrent edge" from "recurrent wiring" in the final W15 champions.

DECISION RULES (fixed before running):
  B1 path-dependence / by-product: in >= 4 of the 6 W15 MIXED lineages,
     recurrence becomes load-bearing at or before plasticity, the
     fitness while only recurrence is load-bearing sits in the 5-15 band
     (the W15 score of W4 RECUR champions), and the jump to >= 36
     coincides with plasticity becoming load-bearing.
  B2 selected second carrier: in >= 4/6, plasticity is load-bearing first
     and recurrence becomes load-bearing later together with a fitness
     increase >= 4.0 (10% of cap).
  B3 drift/entanglement: recurrence becomes load-bearing AFTER fitness has
     reached >= 36 with no further fitness gain, in >= 4/6.
  Anything else: INDETERMINATE at n=6.
  C  If, with plastic R kept on recurrent edges (cut W1/W2 only), cut
     recurrence no longer collapses in >= 4/6 MIXED champions, then the
     reported co-dependence is largely an instrument artifact of
     carriers._cut zeroing R on recurrent edges.
"""
from __future__ import annotations

import json
import math
import os
import sys

REPO = os.environ.get("REPO", ".")
C2 = os.path.join(REPO, "ares", "runs", "sweep_c2")
SEEDS = list(range(201, 211))


def _load(name):
    with open(os.path.join(C2, name + ".json")) as f:
        return json.load(f)


# ---------------------------------------------------------------- PART A
def fisher_two_by_two(a, n1, b, n2):
    """Exact Fisher for a/n1 vs b/n2. Returns (one-sided P(X>=a), two-sided)."""
    K = a + b
    N = n1 + n2
    denom = math.comb(N, K)
    pmf = {k: math.comb(n1, k) * math.comb(n2, K - k) / denom
           for k in range(max(0, K - n2), min(n1, K) + 1)}
    one = sum(p for k, p in pmf.items() if k >= a)
    p_obs = pmf[a]
    two = sum(p for p in pmf.values() if p <= p_obs + 1e-12)
    return one, two


def part_a():
    # W15 both-rec-and-plast-necessary 6/10 vs W4 c1_all 2/10 (gates.txt:1,13)
    print("fisher 6/10 vs 2/10:", fisher_two_by_two(6, 10, 2, 10))
    # any multi-carrier (MIXED or REDUNDANT): W15 7/10 vs W4 c1_all 4/10
    print("fisher 7/10 vs 4/10:", fisher_two_by_two(7, 10, 4, 10))
    # REDUNDANT proper: W15 1/10 vs W4 c1_all 1/10
    print("fisher 1/10 vs 1/10:", fisher_two_by_two(1, 10, 1, 10))
    bat = _load("battery")["robustness_cost"]
    by = {}
    for r in bat:
        by.setdefault(r["carrier_class"], []).append(r["on_W15"])
    for k, v in sorted(by.items()):
        v = sorted(v)
        print(f"W4-evolved class {k:28s} n={len(v):2d} on_W15 min {v[0]:6.2f} "
              f"median {v[len(v)//2]:6.2f} max {v[-1]:6.2f}")
    for sd in SEEDS:
        d = _load(f"W15_present_s{sd}_dissect")
        print(sd, d["carrier_class"], d["base"], d["cut_recurrent"], d["cut_plasticity"],
              d["cut_keep"], d["inventory"]["recurrent_edges"], d["inventory"]["plastic_edges"])


# ---------------------------------------------------------------- PART B
def part_b(world="W15", arm="W15_present", step=5):
    sys.path.insert(0, REPO)
    from ares import carriers as C
    from ares import cycle2 as Y
    seeds = Y.seeds_for(world, "present")
    out = {}
    for sd in SEEDS:
        res = _load(f"{arm}_s{sd}")
        rows = []
        for snap in res["snapshots"]:
            if snap["gen"] % step and snap["gen"] != res["G"] - 1:
                continue
            a = C.carrier_ablation(snap["genome"], world, "present", seeds, floor=0.0)
            rows.append(dict(gen=snap["gen"], base=a["base"], cls=a["carrier_class"],
                             rec=a["collapses"]["recurrent"], plast=a["collapses"]["plasticity"],
                             keep=a["collapses"]["keep"],
                             n_rec=a["inventory"]["recurrent_edges"]))
        first = lambda key: next((r["gen"] for r in rows if r[key] and r["base"] >= 8.0), None)
        out[sd] = dict(rows=rows, first_rec=first("rec"), first_plast=first("plast"),
                       final_cls=rows[-1]["cls"] if rows else None)
        print(sd, out[sd]["final_cls"], "first_rec", out[sd]["first_rec"],
              "first_plast", out[sd]["first_plast"])
    json.dump(out, open(f"d001_08_trajectories_{arm}.json", "w"), indent=1)
    return out


# ---------------------------------------------------------------- PART C
def part_c():
    sys.path.insert(0, REPO)
    import numpy as np
    from ares import substrate as S
    from ares import search as R
    from ares import cycle2 as Y
    seeds = Y.seeds_for("W15", "present")
    world = R.make_world("W15", "present")
    for sd in SEEDS:
        g = _load(f"W15_present_s{sd}")["final"]["genome"]
        pop = S.Population.from_genomes([g])
        m = S.recurrent_edge_mask(pop)[0]
        plastic = (pop.R[0] != 0)
        overlap = int((m & plastic).sum())
        base = float(R.rollout(pop, world, seeds)[0])
        # C1: cut recurrent base weights only, keep plastic R
        q = pop.copy(); q.W1[0][m] = 0; q.W2[0][m] = 0
        c1 = float(R.rollout(q, world, seeds)[0])
        # C2: cut only NON-plastic recurrent edges
        mm = m & ~plastic
        q = pop.copy(); q.W1[0][mm] = 0; q.W2[0][mm] = 0
        c2 = float(R.rollout(q, world, seeds)[0])
        # C3: cut plasticity only on non-recurrent edges
        q = pop.copy(); q.R[0][~m] = 0
        c3 = float(R.rollout(q, world, seeds)[0])
        print(f"s{sd} base {base:6.2f} plastic_on_recurrent {overlap} "
              f"cutRecW_keepR {c1:6.2f} cutNonPlasticRec {c2:6.2f} cutPlastNonRec {c3:6.2f}")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "A"
    if which == "A":
        part_a()
    elif which == "B":
        part_b("W15", "W15_present"); part_b("W4", "c1_all")
    elif which == "C":
        part_c()
