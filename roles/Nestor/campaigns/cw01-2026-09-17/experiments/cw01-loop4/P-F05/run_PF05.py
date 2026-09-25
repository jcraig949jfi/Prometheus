"""P-F05 (T-E06 x T-X14 x T-X04 x T-X16): PRE-ADAPTED vs FROM-SCRATCH residents across the rate window,
and GEOMETRY x RATE.

(a) e06's invasion protocol (resident alone 40 generations, invader at 10 percent for 80 generations)
in both directions at rates .5-.8 (7 values) x 3 ids; (b) from-scratch mixing at f0 .1 / .9, the same
rates, 120 generations; (c) phi {0, .5, 1} (P-A08's mixture) x rate {.5..1.0} x f0 .1 x 2 ids, 160
generations. Does the exclusion window exist under pre-adapted residents; does it move with geometry.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "loop"))
import looprun as L            # noqa: E402
import seeds as S              # noqa: E402

W6 = L.import_world("cw01-e06", "world_e06")
PID, TID = "P-F05", "T-E06"
RATES, IDS, GEO_RATES, PHIS, GIDS = (0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8), ["cw01-loop4-PF05-%d" % i for i in range(3)], (0.5, 0.6, 0.7, 0.8, 0.9, 1.0), (0.0, 0.5, 1.0), ["cw01-loop4-PF05g-%d" % i for i in range(2)]
MIX = {"active": False, "phi": 0.0, "legacy": None}
_orig_make = W6.make_items


def make_items_mixed(cfg, rng, target):
    if not MIX["active"]:
        return _orig_make(cfg, rng, target)
    t = cfg["task"]
    lo, hi = t["input_domain"]
    graph_targets = target if isinstance(target, list) else [target]
    out = []
    for _ in range(t["items_per_episode"]):
        use_legacy = rng.random() < MIX["phi"]
        tt = graph_targets[int(rng.integers(0, len(graph_targets)))]
        x = [float(v) for v in rng.integers(lo, hi + 1, size=t["n_inputs"])]
        core = MIX["legacy"] if use_legacy else (tt["graph"] if (isinstance(tt, dict) and "graph" in tt) else tt)
        out.append((x, W6.target_eval(core, x)))
    return out


W6.make_items = make_items_mixed


def job(j):
    MIX["active"] = False
    cfg = L.load_cfg("cw01-e06", j["aid"])
    cfg["ecology"]["recombination_rate"] = j["rate"]
    targets = [t for t in W6.attempt_target(cfg, S.seed) if t.get("graph") is not None]
    if j["kind"] == "invasion":
        inv = W6.invasion_analysis(cfg, S.seed, "%s|inv|r%.2f" % (j["aid"], j["rate"]), gens_resident=40, gens_invade=80, n_org=96, target=targets)
        d = inv["directions"]
        return {"kind": "invasion", "aid": j["aid"], "rate": j["rate"], "TAPE_into_TREE": d["TAPE_into_TREE"]["final"], "TREE_into_TAPE": d["TREE_into_TAPE"]["final"],
                "tape_invades": d["TAPE_into_TREE"]["invaded"], "tree_invades": d["TREE_into_TAPE"]["invaded"], "mutual": inv["mutually_invasible"]}
    if j["kind"] == "scratch":
        run = W6.evolve(cfg, "mixed_assortative", 120, 96, S.seed, "%s|scr|r%.2f|f%.1f" % (j["aid"], j["rate"], j["f0"]), freq_first=j["f0"], target=targets)
        return {"kind": "scratch", "aid": j["aid"], "rate": j["rate"], "f0": j["f0"], "final": W6.final_frequency(run, "TREE"), "coexist": W6.coexisting(run)}
    MIX.update({"active": True, "phi": j["phi"], "legacy": W6.legacy_tree_target(cfg, S.seed)})
    run = W6.evolve(cfg, "mixed_assortative", 160, 96, S.seed, "%s|geo%.1f|r%.1f" % (j["aid"], j["phi"], j["rate"]), freq_first=0.1, target=targets)
    MIX["active"] = False
    return {"kind": "geometry", "aid": j["aid"], "phi": j["phi"], "rate": j["rate"], "final": W6.final_frequency(run, "TREE"), "coexist": W6.coexisting(run)}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-X14", "T-X04", "T-X16"], "claim_type": "protocol-separation",
                         "protocols": {"invasion": "resident alone 40 gens, invader 10 percent, 80 gens, both directions", "scratch": "mixed from f0 .1 / .9, 120 gens", "geometry": "phi {0,.5,1} x rate, f0 .1, 160 gens"},
                         "rates": RATES, "geometry_rates": GEO_RATES, "ids": IDS, "geometry_ids": GIDS,
                         "readouts": "per rate: TREE invades (from 10 percent, pre-adapted TAPE resident) vs from-scratch TREE gain from .1; TAPE invades vs from-scratch TAPE gain from .9; window presence per protocol; per phi the sign pattern over rate",
                         "material_rule": "the two protocols disagree on the direction at >= 2 rates, or the exclusion window (from-scratch, f0 .1) is absent under the invasion protocol, or the sign pattern over rate differs between phi values",
                         "continuation": ["gens_resident dose", "invader fraction dose"]})
    jobs = [{"kind": "invasion", "aid": a, "rate": r} for a in IDS for r in RATES] + [{"kind": "scratch", "aid": a, "rate": r, "f0": f} for a in IDS for r in RATES for f in (0.1, 0.9)] + \
           [{"kind": "geometry", "aid": a, "phi": p, "rate": r} for a in GIDS for p in PHIS for r in GEO_RATES]
    with ProcessPoolExecutor(max_workers=8) as ex:
        rows = list(ex.map(job, jobs, chunksize=2))
    inv = [x for x in rows if x["kind"] == "invasion"]
    scr = [x for x in rows if x["kind"] == "scratch"]
    geo = [x for x in rows if x["kind"] == "geometry"]
    table = {}
    for r in RATES:
        ii = [x for x in inv if x["rate"] == r]
        s1 = [x for x in scr if x["rate"] == r and x["f0"] == 0.1]
        s9 = [x for x in scr if x["rate"] == r and x["f0"] == 0.9]
        table["%.2f" % r] = {"tree_invades_preadapted": sum(x["tree_invades"] for x in ii), "tape_invades_preadapted": sum(x["tape_invades"] for x in ii), "mutual": sum(x["mutual"] for x in ii),
                             "TREE_into_TAPE_final": float(np.mean([x["TREE_into_TAPE"] for x in ii])), "TAPE_into_TREE_final": float(np.mean([x["TAPE_into_TREE"] for x in ii])),
                             "scratch_f0.1_final": float(np.mean([x["final"] for x in s1])), "scratch_f0.9_final": float(np.mean([x["final"] for x in s9])),
                             "tree_gains_scratch": sum(x["final"] > 0.1 for x in s1), "tape_gains_scratch": sum(x["final"] < 0.9 for x in s9)}
    disagree = sum(1 for r in RATES if (table["%.2f" % r]["tree_invades_preadapted"] >= 2) != (table["%.2f" % r]["tree_gains_scratch"] >= 2))
    window_scratch = [r for r in RATES if table["%.2f" % r]["tree_gains_scratch"] <= 1]
    window_inv = [r for r in RATES if table["%.2f" % r]["tree_invades_preadapted"] <= 1]
    gtab = {}
    for p in PHIS:
        gtab["%.1f" % p] = {"%.1f" % r: round(float(np.mean([x["final"] for x in geo if x["phi"] == p and x["rate"] == r])), 3) for r in GEO_RATES}
        gtab["%.1f" % p]["signs"] = [int(np.sign(np.mean([x["final"] for x in geo if x["phi"] == p and x["rate"] == r]) - 0.1)) for r in GEO_RATES]
    geo_differs = len({tuple(v["signs"]) for v in gtab.values()}) > 1
    material = bool(disagree >= 2 or (window_scratch and not window_inv) or geo_differs)
    out = {"perturbation_id": PID, "parent": TID, "by_rate": table, "protocols_disagree_at": disagree, "window_scratch": window_scratch, "window_preadapted": window_inv, "geometry": gtab, "geometry_differs": geo_differs,
           "rows": rows, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    L.append_evidence(TID, PID, "residents pre-adapted vs from-scratch: %s; disagree at %d/7 rates; window scratch %s vs pre-adapted %s; geometry x rate %s"
                      % ({k: (v["tree_invades_preadapted"], v["tape_invades_preadapted"], v["mutual"], v["tree_gains_scratch"], v["tape_gains_scratch"]) for k, v in table.items()}, disagree, window_scratch, window_inv, gtab), material, detail={"table": table, "geometry": gtab})
    for tid in ("T-X14", "T-X04"):
        L.append_evidence(tid, PID, "cross: protocol disagreement at %d/7 rates; windows scratch %s / pre-adapted %s; geometry signs %s" % (disagree, window_scratch, window_inv, {k: v["signs"] for k, v in gtab.items()}), material)
    print("DONE material=%s (%.0f s) disagree %d windows %s/%s geo %s" % (material, time.time() - t0, disagree, window_scratch, window_inv, {k: v["signs"] for k, v in gtab.items()}))


if __name__ == "__main__":
    main()
