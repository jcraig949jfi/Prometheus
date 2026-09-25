"""P-A08 (anti-gravity): interpolate e06's target geometry and look for the invasion crossing.

Parent T-X04 (<- T-E06). Delta: items are drawn from the legacy tree-native target with
probability phi and from the operation-graph targets otherwise, phi in {0, .25, .5, .75, 1};
e06's corrected invasion analysis (evolve each substrate alone 40 generations, introduce the
other at 10%, 20 generations) is run at each phi in both directions. Unchanged: both
substrates, resource sharing, price list, tournament selection, recombination rate.
Descriptive: the phi at which the invasion asymmetry flips, and whether any phi gives
mutual invasibility.
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
PID, TID, AID = "P-A08", "T-X04", "cw01-loop1-PA08"
PHIS = (0.0, 0.25, 0.5, 0.75, 1.0)
MIX = {"phi": 0.0, "legacy": None}
_orig_make = W6.make_items


def make_items_mixed(cfg, rng, target):
    t = cfg["task"]
    lo, hi = t["input_domain"]
    graph_targets = target if isinstance(target, list) else [target]
    out = []
    for _ in range(t["items_per_episode"]):
        use_legacy = rng.random() < MIX["phi"]            # one draw ALWAYS (streams aligned across phi)
        tt = graph_targets[int(rng.integers(0, len(graph_targets)))]
        x = [float(v) for v in rng.integers(lo, hi + 1, size=t["n_inputs"])]
        core = MIX["legacy"] if use_legacy else (tt["graph"] if (isinstance(tt, dict) and "graph" in tt) else tt)
        out.append((x, W6.target_eval(core, x)))
    return out


W6.make_items = make_items_mixed


def main():
    t0 = time.time()
    cfg = L.load_cfg("cw01-e06", AID)
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "claim_type": "exploratory-descriptive",
                         "delta": "item mixture between legacy tree-native target (phi) and operation-graph targets (1-phi)", "phis": PHIS,
                         "unchanged": "substrates, sharing, prices, tournament, recombination, gens_resident 40, gens_invade 20, n_org 96",
                         "attacks": "the invasion-direction reversal between the two generators: is there a crossing with mutual invasibility?",
                         "statistic": "per phi: final invader frequency in both directions; invaded flags; mutual invasibility",
                         "decision": "descriptive; any phi with mutual invasibility is material (e06 becomes posable there)"})
    MIX["legacy"] = W6.legacy_tree_target(cfg, S.seed)
    graph = W6.attempt_target(cfg, S.seed)
    rows = []
    for phi in PHIS:
        MIX["phi"] = phi
        t1 = time.time()
        inv = W6.invasion_analysis(cfg, S.seed, AID + "|phi%.2f" % phi, gens_resident=40, gens_invade=20, n_org=96, target=graph)
        d = inv["directions"]
        rec = {"phi": phi, "TAPE_into_TREE": d["TAPE_into_TREE"]["final"], "TREE_into_TAPE": d["TREE_into_TAPE"]["final"],
               "tape_invades": d["TAPE_into_TREE"]["invaded"], "tree_invades": d["TREE_into_TAPE"]["invaded"],
               "mutual": inv["mutually_invasible"], "wall_s": round(time.time() - t1, 1)}
        rows.append(rec)
        print("   phi %.2f  TAPE->TREE %.3f (%s)  TREE->TAPE %.3f (%s)  mutual %s  (%.0f s)"
              % (phi, rec["TAPE_into_TREE"], rec["tape_invades"], rec["TREE_into_TAPE"], rec["tree_invades"], rec["mutual"], rec["wall_s"]), flush=True)
    any_mutual = any(r["mutual"] for r in rows)
    flips = [(rows[i]["phi"], rows[i + 1]["phi"]) for i in range(len(rows) - 1)
             if (rows[i]["tape_invades"], rows[i]["tree_invades"]) != (rows[i + 1]["tape_invades"], rows[i + 1]["tree_invades"])]
    res = {"perturbation_id": PID, "parent": TID, "rows": rows, "any_mutual": any_mutual, "asymmetry_flips_between": flips,
           "elapsed_s": round(time.time() - t0, 1),
           "reading": ("a phi with mutual invasibility exists" if any_mutual else "no phi gives mutual invasibility; the asymmetry flips between %s" % flips)}
    L.result(HERE, res, ph)
    L.append_evidence(TID, PID, "target-geometry interpolation: %s" % res["reading"], any_mutual or bool(flips), detail={"rows": rows},
                      state="ACTIVE" if any_mutual else "TEMPORAL_STASIS",
                      state_reason=("mutual invasibility located; e06 is posable at that phi" if any_mutual else
                                    "no interpolation of target geometry yields mutual invasibility; every available intervention on the target strikes the same surface"))
    L.append_evidence("T-E06", PID, "geometry interpolation result: %s" % res["reading"], any_mutual)
    print("DONE %s (%.0f s)" % (res["reading"], time.time() - t0))


if __name__ == "__main__":
    main()
