"""P-A07: e06 variation-regime swap holding world and price list fixed.

Parent T-E06. Delta: recombination_rate 0.0 (mutation only) and 1.0 (crossover-heavy; e06 ran
0.5) with the corrected invasion analysis in both directions. Unchanged: operation-graph
generator, sharing, prices, tournament size, mutation, gens 40/20, n_org 96. Descriptive:
does the regime change whether TREE can invade TAPE (D055: TREE's only plausible advantage
is dynamic, subtree crossover)?
"""
from __future__ import annotations

import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402

W6 = L.import_world("cw01-e06", "world_e06")
PID, TID, AID = "P-A07", "T-E06", "cw01-loop1-PA07"
RATES = (0.0, 0.5, 1.0)


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "search-boundary-descriptive",
                         "delta": "recombination_rate in %s (0.5 = as e06 ran)" % (RATES,),
                         "unchanged": "generator, sharing, prices, tournament, mutation, invasion protocol",
                         "attacks": "D055: TREE's dynamic advantage (subtree crossover) never had the chance to matter",
                         "statistic": "per rate: invasion both directions, mutual invasibility",
                         "decision": "descriptive; TREE invading TAPE at any rate, or mutual invasibility, is material"})
    # ONE target for every rate (the world is held fixed; only the variation regime moves). Run 1 drew a
    # target per rate and the generator returned an EMPTY graph for one band under the "|rr0.0" attempt id
    # (world_e06._make_graph can return None; CW01-D070), which crashed tree_eval. Verified non-empty here.
    base_cfg = L.load_cfg("cw01-e06", AID)
    target = W6.attempt_target(base_cfg, S.seed)
    if any(t.get("graph") is None for t in target):
        raise RuntimeError("attempt_target returned an empty band for %s (CW01-D070)" % AID)
    rows = []
    for rate in RATES:
        cfg = L.load_cfg("cw01-e06", AID)
        cfg["ecology"]["recombination_rate"] = rate
        t1 = time.time()
        inv = W6.invasion_analysis(cfg, S.seed, AID + "|rr%.1f" % rate, gens_resident=40, gens_invade=20, n_org=96, target=target)
        d = inv["directions"]
        rec = {"recombination_rate": rate, "TAPE_into_TREE": d["TAPE_into_TREE"]["final"], "TREE_into_TAPE": d["TREE_into_TAPE"]["final"],
               "tape_invades": d["TAPE_into_TREE"]["invaded"], "tree_invades": d["TREE_into_TAPE"]["invaded"], "mutual": inv["mutually_invasible"],
               "wall_s": round(time.time() - t1, 1)}
        rows.append(rec)
        print("   rate %.1f  TAPE->TREE %.3f (%s)  TREE->TAPE %.3f (%s)  mutual %s  (%.0f s)"
              % (rate, rec["TAPE_into_TREE"], rec["tape_invades"], rec["TREE_into_TAPE"], rec["tree_invades"], rec["mutual"], rec["wall_s"]), flush=True)
    material = any(r["tree_invades"] or r["mutual"] for r in rows)
    res = {"perturbation_id": PID, "parent": TID, "rows": rows, "material": material, "elapsed_s": round(time.time() - t0, 1),
           "reading": ("TREE invades under some variation regime" if material else "no variation regime lets TREE invade; the boundary is not the search regime")}
    L.result(HERE, res, ph)
    L.append_evidence(TID, PID, "variation regime swap: %s; rows %s" % (res["reading"], [(r["recombination_rate"], r["tree_invades"], r["tape_invades"]) for r in rows]),
                      material, detail={"rows": rows},
                      state="ACTIVE" if material else "TEMPORAL_STASIS",
                      state_reason=("search regime matters; next: locate the rate/geometry pair" if material else
                                    "four world iterations, a geometry interpolation and three variation regimes strike the same boundary: TREE cannot invade; the next informative perturbation needs a different price list or a third substrate"))
    print("DONE %s (%.0f s)" % (res["reading"], time.time() - t0))


if __name__ == "__main__":
    main()
