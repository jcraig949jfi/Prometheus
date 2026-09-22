"""P-H01 [T-X17, deformation B]: TRANSPLANT MAP of representatives of the four non-immune geometries into
three worlds under immediate read, a neutral walk (depth 16, archived 4/8/16) and selection (20
generations, 4 representatives per geometry per world). Geometry (full curve set), reward on all three
worlds and ancestry tracked separately. Computational scope: integer programs on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import manifold as MF          # noqa: E402
import evolver as EV           # noqa: E402
A, L = CM.A, CM.L

PID, TID = "P-H01", "T-X17"
SHAPES = {0: "start_anchored", 4: "periodic", 5: "ask_time", 1: "schedule"}
NREP, NSEL, WORLDS = 8, 4, MF.WORLDS3


def walk_job(j):
    m, w = j["m"], j["world"]
    eps = A.episodes(w)
    wk = A.C5.walk(m, "%s|%s" % (j["pid"], w), 1, eps, 16, 32)
    out = {"pid": j["pid"], "shape": j["shape"], "world": w, "stage": "neutral", "depth_reached": wk["depth"], "curves": {}, "rewards": {}}
    for d in (0, 4, 8, 16):
        mm = wk["archived"].get(d) or (wk["archived"].get(wk["depth"]) if d > wk["depth"] else None)
        if mm is not None:
            out["curves"][str(d)] = MF.curve(mm)[0]
            out["rewards"][str(d)] = MF.rewards3(mm)
    return out


def sel_job(j):
    init = [{"m": j["m"], "anc": 0, "anc_parent": None, "anc_stratum": None, "anc_walker": None} for _ in range(EV.N)]
    r = EV.run("select", 1, init, G_=20, env=j["world"], label="nestor.ph01|" + j["pid"])
    tops = sorted(r["final"], key=lambda x: -x["reward"])[:16]
    return {"pid": j["pid"], "shape": j["shape"], "world": j["world"], "stage": "selection", "curves": [MF.curve(x["m"])[0] for x in tops], "rewards": [MF.rewards3(x["m"]) for x in tops], "reward_mean": r["history"][-1]["reward_mean"]}


def native_job(j):
    init, _ = EV.init_population()
    r = EV.run("select", 1, init, G_=20, env=j["world"], label="nestor.ph01.native")
    tops = sorted(r["final"], key=lambda x: -x["reward"])[:16]
    return {"world": j["world"], "curves": [MF.curve(x["m"])[0] for x in tops]}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "B", "requires": ["P-G11"], "scope": CM.SCOPE, "claim_type": "transplant-map",
                         "representatives": {v: NREP for v in SHAPES.values()}, "worlds": WORLDS, "conditions": {"immediate": "curve + rewards on 3 worlds", "neutral": "C4-05 band walk in the world, depth 16, archived 4/8/16", "selection": "20 generations from the representative (N 96 copies), top-16 curves; 4 representatives per shape"},
                         "native": "each world's native geometry = top-16 of a 20-generation plain selection from the init walkers", "distances": "L1 over the 30-key curve set to the representative's own depth-0 curve and to the world-native centroid",
                         "readouts": "per shape x world x condition: mean distance to origin and to native; reward on the three worlds; named from the curves only", "material_rule": "always material: the map is the result", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    reps = {c: MF.representatives(c, NREP) for c in SHAPES}
    jobs = [{"pid": r["organism_id"], "shape": SHAPES[c], "m": A.canonical(r["manifest"]), "world": w} for c, rs in reps.items() for r in rs for w in WORLDS]
    with A.pool(8) as ex:
        walks = list(ex.map(walk_job, jobs))
        natives = {n["world"]: n for n in ex.map(native_job, [{"world": w} for w in WORLDS])}
    sjobs = [{"pid": r["organism_id"], "shape": SHAPES[c], "m": A.canonical(r["manifest"]), "world": w} for c, rs in reps.items() for r in rs[:NSEL] for w in WORLDS]
    with A.pool(6) as ex:
        sels = list(ex.map(sel_job, sjobs))
    nat_cent = {w: np.nanmean(np.array(n["curves"], float), axis=0).tolist() for w, n in natives.items()}
    table = {}
    for c, sh in SHAPES.items():
        for w in WORLDS:
            ws = [x for x in walks if x["shape"] == sh and x["world"] == w]
            ss = [x for x in sels if x["shape"] == sh and x["world"] == w]
            ent = {"n_neutral": len(ws), "reward0": {ww: float(np.mean([x["rewards"]["0"][ww] for x in ws if "0" in x["rewards"]])) for ww in WORLDS}}
            for d in ("4", "8", "16"):
                xs = [x for x in ws if d in x["curves"]]
                ent["neutral_d%s" % d] = {"d_origin": float(np.mean([MF.dist(x["curves"][d], x["curves"]["0"]) for x in xs])) if xs else None, "d_native": float(np.mean([MF.dist(x["curves"][d], nat_cent[w]) for x in xs])) if xs else None,
                                          "reward_in_world": float(np.mean([x["rewards"][d][w] for x in xs])) if xs else None}
            if ss:
                ent["selection"] = {"d_origin": float(np.mean([MF.dist(v, next(x for x in ws if x["pid"] == s["pid"])["curves"]["0"]) for s in ss for v in s["curves"]])),
                                    "d_native": float(np.mean([MF.dist(v, nat_cent[w]) for s in ss for v in s["curves"]])), "reward_in_world": float(np.mean([s["reward_mean"] for s in ss])),
                                    "centroid": np.nanmean(np.array([v for s in ss for v in s["curves"]], float), axis=0).tolist()}
            table["%s|%s" % (sh, w)] = ent
    out = {"perturbation_id": PID, "parent": TID, "table": table, "native_centroids": nat_cent, "keys": MF.KEYS, "material": True, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps({"walks": walks, "selection": sels, "reps": {str(c): [r["organism_id"] for r in rs] for c, rs in reps.items()}}, ensure_ascii=True, default=CM.js), encoding="utf-8")
    summ = {k: (round(v["neutral_d16"]["d_origin"], 2) if v.get("neutral_d16") and v["neutral_d16"]["d_origin"] is not None else None, round(v["neutral_d16"]["d_native"], 2) if v.get("neutral_d16") and v["neutral_d16"]["d_native"] is not None else None,
                round(v["selection"]["d_origin"], 2) if v.get("selection") else None, round(v["selection"]["d_native"], 2) if v.get("selection") else None, round(v["selection"]["reward_in_world"], 2) if v.get("selection") else None) for k, v in table.items()}
    L.append_evidence(TID, PID, "transplant map (shape|world: neutral-16 d_origin, d_native; selection d_origin, d_native, reward): %s" % summ, True, detail={"table": {k: {kk: vv for kk, vv in v.items() if kk != "selection"} | {"selection": {a: b for a, b in v.get("selection", {}).items() if a != "centroid"}} for k, v in table.items()}})
    print("DONE (%.0f s) %s" % (time.time() - t0, summ))


if __name__ == "__main__":
    main()
