"""P-D05: replicate P-A07's mutual invasibility at recombination rate 1.0.

Parent T-E06. 6 attempt ids x geometry {operation-graph targets, legacy tree target} x rate {0.5,
1.0}; e06's corrected invasion analysis in both directions (evolve each substrate alone 40
generations, introduce the other at 10%, 20 generations). Every band verified non-empty
(D070). Statistic: count of (id, geometry) cells with mutual invasibility per rate; exact
relabelling of rate labels within (id, geometry) pairs (sign-flip over 12 pairs).
"""
from __future__ import annotations

import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402

W6 = L.import_world("cw01-e06", "world_e06")
PID, TID = "P-D05", "T-E06"
IDS, RATES, GEOS = ["cw01-loop2-PD05-%d" % i for i in range(6)], (0.5, 1.0), ("graph", "legacy")


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "replication-confirmatory",
                         "delta": "6 attempt ids x 2 geometries x rates 0.5/1.0; invasion both directions", "unchanged": "e06 world, sharing, prices, tournament, protocol",
                         "attacks": "P-A07 rested on ONE attempt id and ONE target", "decision": {"ROBUST": "mutual invasibility in >= 8/12 cells at rate 1.0 and the paired count difference (1.0 minus 0.5) above p95", "PARTIAL": "3-7/12", "NOT_REPLICATED": "<= 2/12"},
                         "continuation": ["rates 0.75/0.9", "n_org 48/192", "80-generation mixed runs at the winning rate"]})
    rows = []
    for aid in IDS:
        base = L.load_cfg("cw01-e06", aid)
        targets = {"graph": W6.attempt_target(base, S.seed), "legacy": [W6.legacy_tree_target(base, S.seed)]}
        if any(t.get("graph") is None for t in targets["graph"]):
            targets["graph"] = [t for t in targets["graph"] if t.get("graph") is not None]
        for geo in GEOS:
            for rate in RATES:
                cfg = L.load_cfg("cw01-e06", aid)
                cfg["ecology"]["recombination_rate"] = rate
                t1 = time.time()
                inv = W6.invasion_analysis(cfg, S.seed, "%s|%s|rr%.1f" % (aid, geo, rate), gens_resident=40, gens_invade=20, n_org=96, target=targets[geo])
                d = inv["directions"]
                rows.append({"aid": aid, "geo": geo, "rate": rate, "TAPE_into_TREE": d["TAPE_into_TREE"]["final"], "TREE_into_TAPE": d["TREE_into_TAPE"]["final"],
                             "tape_invades": d["TAPE_into_TREE"]["invaded"], "tree_invades": d["TREE_into_TAPE"]["invaded"], "mutual": inv["mutually_invasible"], "wall_s": round(time.time() - t1, 1)})
                print("   %s %-6s rate %.1f  TAPE->TREE %.3f (%s)  TREE->TAPE %.3f (%s)  mutual %s" % (aid[-1], geo, rate, rows[-1]["TAPE_into_TREE"], rows[-1]["tape_invades"], rows[-1]["TREE_into_TAPE"], rows[-1]["tree_invades"], rows[-1]["mutual"]), flush=True)
    counts = {r: sum(1 for x in rows if x["rate"] == r and x["mutual"]) for r in RATES}
    tree_inv = {r: sum(1 for x in rows if x["rate"] == r and x["tree_invades"]) for r in RATES}
    pairs = {}
    for x in rows:
        pairs.setdefault((x["aid"], x["geo"]), {})[x["rate"]] = int(x["mutual"])
    diffs = [v[1.0] - v[0.5] for v in pairs.values() if 1.0 in v and 0.5 in v]
    sf = None
    if diffs:
        d = np.array(diffs, float)
        rng = np.random.Generator(np.random.PCG64(0))
        null = np.array([(d * rng.choice([-1.0, 1.0], size=len(d))).mean() for _ in range(5000)])
        sf = {"mean_diff": float(d.mean()), "p95": float(np.percentile(null, 95)), "above_p95": bool(d.mean() > np.percentile(null, 95)), "n": len(d)}
    n10 = counts[1.0]
    disp = "ROBUST" if (n10 >= 8 and sf and sf["above_p95"]) else "PARTIAL" if n10 >= 3 else "NOT_REPLICATED"
    by_geo = {g: {r: sum(1 for x in rows if x["rate"] == r and x["geo"] == g and x["mutual"]) for r in RATES} for g in GEOS}
    out = {"perturbation_id": PID, "parent": TID, "disposition": disp, "mutual_by_rate": counts, "tree_invades_by_rate": tree_inv, "mutual_by_geo_rate": by_geo,
           "paired_signflip": sf, "rows": rows, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "recombination-1.0 mutual invasibility replication: %s; mutual cells rate 1.0 %d/12 vs 0.5 %d/12; TREE invades %s; by geometry %s"
                      % (disp, counts[1.0], counts[0.5], tree_inv, by_geo), disp != "NOT_REPLICATED", detail=out["mutual_by_geo_rate"])
    print("DISPOSITION %s %s %s (%.0f s)" % (disp, counts, by_geo, time.time() - t0))


if __name__ == "__main__":
    main()
