"""P-G05 [T-X17, deformation B]: NEUTRAL TRANSPLANT - lineages of distinct temporal classes moved into
the alternate world under NO selection (a neutral-band walk in the host world, depth 16, archived
0/2/4/8/16), the raw 7-vector at each archive; then, separately, selection on the C4-08 lineage (idle-tick
selection in W2, 40 gens; plain W0 selection, 20 gens). Computational scope: integer programs on a
bounded VM.
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
import evolver as EV           # noqa: E402
import ticks as TK             # noqa: E402
A, L = CM.A, CM.L
sys.path.insert(0, str(HERE.parent / "P-D01"))
sys.path.insert(0, str(HERE.parent / "P-F03"))
from run_PD01 import c408_tops   # noqa: E402
from run_PF03 import idle_transform, centroid, dist   # noqa: E402

PID, TID = "P-G05", "T-X17"
NPER, DEPTHS = 16, (0, 4, 8, 16)


def lineages():
    tops = json.loads((HERE.parent / "P-F03" / "tops.json").read_text(encoding="utf-8"))
    pick = lambda env, mode: [t["m"] for x in tops if x["stage"] == "evolve" and x["env"] == env and x["mode"] == mode and x["seed"] == 1 for t in x["tops"]][:NPER]   # noqa: E731
    return {"W0_plain": {"ms": pick("W0", "plain"), "host": "W2_K2"}, "W0_idle": {"ms": pick("W0", "idle"), "host": "W2_K2"},
            "W2_plain": {"ms": pick("W2_K2", "plain"), "host": "W0"}, "C408": {"ms": [A.canonical(p["manifest"]) for p in c408_tops(n=NPER)], "host": "W0"}}


def walk_job(j):
    m, host, lin, i = j["m"], j["host"], j["lineage"], j["i"]
    eps = A.episodes(host)
    r0 = A.evaluate(m, eps, rng_seed=0, reward_mode="per_ask")
    wk = A.C5.walk(m, "%s-%d" % (lin, i), 1, eps, 16, 32)
    out = {"lineage": lin, "host": host, "i": i, "host_r0": r0["reward_per_ask"], "host_answered": r0["answered_share"], "depth_reached": wk["depth"], "vectors": {}}
    for d in DEPTHS:
        mm = wk["archived"].get(d)
        if mm is None:
            mm = wk["archived"].get(wk["depth"]) if d > wk["depth"] else None
        if mm is not None:
            out["vectors"][str(d)] = TK.response_vector(mm)["vector"]
    return out


def evo_job(j):
    r = EV.run("select", j["seed"], j["init"], G_=j["G"], env=j["env"], ep_transform=(idle_transform(j["env"]) if j["mode"] == "idle" else None), label="nestor.pg05")
    tops = sorted(r["final"], key=lambda x: -x["reward"])[:32]
    return {"env": j["env"], "mode": j["mode"], "seed": j["seed"], "G": j["G"], "vectors": [TK.response_vector(x["m"])["vector"] for x in tops], "reward_mean": r["history"][-1]["reward_mean"]}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "B", "scope": CM.SCOPE, "claim_type": "transplant-without-selection",
                         "lineages": {"W0_plain": "ask-time bound (P-F03 seed 1 tops) -> host W2_K2", "W0_idle": "immune -> host W2_K2", "W2_plain": "immune (evolver) -> host W0", "C408": "input-schedule bound (C4-08 ordinary top-16) -> host W0"},
                         "neutral_window": "C4-05 neutral-band walk in the host world (reward within band of the program's own host reward), depth 16, archived 0/2/4/8/16; no fitness ordering",
                         "vector": TK.VECTOR_KEYS, "centroids": "origin = the lineage's own depth-0 vectors; host-native = the host world's plain-evolved tops (P-F03: W2_plain for host W2, W0_plain for host W0)",
                         "readings_per_lineage": {"TRAVELS_WITH_ORGANISM": "at depth 16 mean distance to origin <= .10 and < distance to host", "DECAYS_WITHOUT_SELECTION": "distance to origin grows by >= .20 from depth 0 to 16 without approaching the host centroid",
                                                  "CONTEXT_REMAPS_IMMEDIATELY": "not applicable by construction (the vector reads every world at once); recorded as such", "REBUILT_BY_SELECTION": "under host selection the tops' centroid is nearer the host than the origin", "MIXED": "otherwise"},
                         "selection_stage": "C4-08 tops under idle-tick selection in W2_K2 (40 gens, seeds 1-2) and under plain W0 selection (20 gens, seeds 1-2); W0/W2 lineages' selection stage is P-F03's transplant (cited)",
                         "material_rule": "any lineage reads DECAYS or REBUILT, or the origin-vs-host distances separate at depth 16", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    lin = lineages()
    jobs = [{"m": m, "host": v["host"], "lineage": k, "i": i} for k, v in lin.items() for i, m in enumerate(v["ms"])]
    with A.pool(8) as ex:
        rows = list(ex.map(walk_job, jobs))
    tops = json.loads((HERE.parent / "P-F03" / "tops.json").read_text(encoding="utf-8"))
    host_native = {"W2_K2": centroid([TK.response_vector(t["m"])["vector"] for x in tops if x["stage"] == "evolve" and x["env"] == "W2_K2" and x["mode"] == "plain" for t in x["tops"][:16]]),
                   "W0": centroid([TK.response_vector(t["m"])["vector"] for x in tops if x["stage"] == "evolve" and x["env"] == "W0" and x["mode"] == "plain" for t in x["tops"][:16]])}
    readings = {}
    for k, v in lin.items():
        rs = [r for r in rows if r["lineage"] == k]
        origin = centroid([r["vectors"]["0"] for r in rs if "0" in r["vectors"]])
        host = host_native[v["host"]]
        by_depth = {}
        for d in DEPTHS:
            vs = [r["vectors"][str(d)] for r in rs if str(d) in r["vectors"]]
            by_depth[str(d)] = {"n": len(vs), "centroid": centroid(vs), "d_origin": float(np.mean([dist(x, origin) for x in vs])) if vs else None, "d_host": float(np.mean([dist(x, host) for x in vs])) if vs else None}
        d0, d16 = by_depth["0"]["d_origin"], by_depth["16"]["d_origin"]
        h16 = by_depth["16"]["d_host"]
        if d16 is not None and d16 <= 0.10 and d16 < h16:
            rd = "TRAVELS_WITH_ORGANISM"
        elif d16 is not None and d16 - d0 >= 0.20 and h16 >= d16:
            rd = "DECAYS_WITHOUT_SELECTION"
        elif d16 is not None and h16 < d16:
            rd = "MIXED_TOWARD_HOST_WITHOUT_SELECTION"
        else:
            rd = "MIXED"
        readings[k] = {"host": v["host"], "n": len(rs), "host_answered": float(np.mean([r["host_answered"] for r in rs])), "depth_reached": float(np.mean([r["depth_reached"] for r in rs])), "origin_centroid": origin, "host_centroid": host, "by_depth": by_depth, "reading": rd, "context_remaps_immediately": "not applicable (vector reads all worlds)"}
    # selection stage on the C4-08 lineage
    init = [{"m": m, "anc": i % NPER, "anc_parent": None, "anc_stratum": None, "anc_walker": None} for i, m in enumerate([lin["C408"]["ms"][i % NPER] for i in range(EV.N)])]
    with A.pool(4) as ex:
        sel = list(ex.map(evo_job, [{"env": "W2_K2", "mode": "idle", "seed": s, "init": init, "G": 40} for s in (1, 2)] + [{"env": "W0", "mode": "plain", "seed": s, "init": init, "G": 20} for s in (1, 2)]))
    origin = readings["C408"]["origin_centroid"]
    sel_read = {}
    for r in sel:
        c = centroid(r["vectors"])
        host = host_native["W0"] if r["env"] == "W0" else [0.0] * 7
        sel_read["%s|%s|s%d" % (r["env"], r["mode"], r["seed"])] = {"centroid": c, "d_origin": dist(c, origin), "d_host_or_immune": dist(c, host), "reward": r["reward_mean"], "reading": "REBUILT_BY_SELECTION" if dist(c, host) < dist(c, origin) else "PERSISTS_UNDER_SELECTION"}
    material = bool(any(v["reading"] in ("DECAYS_WITHOUT_SELECTION", "MIXED_TOWARD_HOST_WITHOUT_SELECTION") for v in readings.values()) or any(v["reading"] == "REBUILT_BY_SELECTION" for v in sel_read.values()))
    out = {"perturbation_id": PID, "parent": TID, "neutral": readings, "selection_C408": sel_read, "host_native_centroids": host_native, "vector_keys": TK.VECTOR_KEYS, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "neutral transplant: %s | C4-08 under selection: %s"
                      % ({k: (v["reading"], round(v["by_depth"]["0"]["d_origin"], 3) if v["by_depth"]["0"]["d_origin"] is not None else None, round(v["by_depth"]["16"]["d_origin"], 3) if v["by_depth"]["16"]["d_origin"] is not None else None, round(v["by_depth"]["16"]["d_host"], 3) if v["by_depth"]["16"]["d_host"] is not None else None, round(v["depth_reached"], 1)) for k, v in readings.items()},
                         {k: (v["reading"], round(v["d_origin"], 3), round(v["d_host_or_immune"], 3), round(v["reward"], 3)) for k, v in sel_read.items()}), material, detail={"neutral": {k: v["reading"] for k, v in readings.items()}, "selection": {k: v["reading"] for k, v in sel_read.items()}})
    print("DONE material=%s (%.0f s) %s | %s" % (material, time.time() - t0, {k: v["reading"] for k, v in readings.items()}, {k: v["reading"] for k, v in sel_read.items()}))


if __name__ == "__main__":
    main()
