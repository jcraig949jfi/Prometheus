"""P-H04 [T-X19 x T-X17 x T-ARCH4/M1, deformation C]: MINIMAL CAUSAL TRANSPLANTATION. Localise the machinery
of the START-ANCHORED (delay_general, W1_d4) and ASK-TIME (w0_solver, W0) geometries by per-instruction
disable probes (geometry-necessary and reward-necessary sets, with the HALT-probe reach map), take the
smallest contiguous span covering the geometry-necessary set, insert it into naive hosts at start /
middle / end (plus a sham span from an unrelated immune program), and read the host's curve set and
reward on the source world. Computational scope: integer programs on a bounded VM.
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
import scatter as SC           # noqa: E402
A, L = CM.A, CM.L

PID, TID = "P-H04", "T-X19"
SOURCES = {0: ("start_anchored", "W1_d4"), 5: ("ask_time", "W0")}
NSRC, FLOOR, BAND = 6, A.C1.FLOOR, A.C1.BAND


def hosts():
    progs = MF.census_programs()
    byid = {p["organism_id"]: p for p in progs}
    rv = MF.rows()
    imm = [pid for pid, r in rv.items() if all(x == x for x in r["vector"]) and max(r["vector"]) < 0.1]
    gen0 = [p for p in progs if p["lineage"] == "parent:gen0_random"][:2]
    shelf = [byid[pid] for pid in imm if pid in byid and byid[pid]["lineage"] == "parent:shelf"][:4]
    w2 = [byid[pid] for pid in imm if pid in byid and byid[pid]["lineage"] == "pf03:W2_K2:plain:evolve"][:4]
    return [dict(h, role="gen0") for h in gen0] + [dict(h, role="shelf_immune") for h in shelf] + [dict(h, role="w2_immune") for h in w2]


def localise(m, world):
    eps = A.episodes(world)
    v0 = MF.curve(m)[0]
    r0 = A.evaluate(m, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
    n = CM.n_instr(m)
    reach = SC.reach_map(m, eps)
    geo, rew = [], []
    for i in range(n):
        c = json.loads(json.dumps(m))
        c["genome"][i * A.IW] = A.NOP
        v = MF.curve(c)[0]
        r = A.evaluate(c, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
        geo.append(MF.dist(v, v0) > 0.3)
        rew.append(r < r0 - BAND)
    G = [i for i in range(n) if geo[i]]
    span = (min(G), max(G) + 1) if G else None
    return {"v0": v0, "r0": r0, "n": n, "reach": reach, "geo_necessary": G, "reward_necessary": [i for i in range(n) if rew[i]], "span": span, "span_len": (span[1] - span[0]) if span else 0}


def transplant(host, span_genome, where):
    c = json.loads(json.dumps(host))
    g = c["genome"]
    n = len(g) // A.IW
    at = {"start": 0, "middle": (n // 2) * A.IW, "end": len(g)}[where]
    c["genome"] = g[:at] + list(span_genome) + g[at:]
    if len(c["genome"]) > c["tape_words"]:
        c["tape_words"] = min(4096, ((len(c["genome"]) + 3) // 4) * 4 + 4)
    return c


def job(j):
    src = A.canonical(j["src"]["manifest"])
    loc = localise(src, j["world"])
    out = {"src": j["src"]["organism_id"], "shape": j["shape"], "world": j["world"], "loc": {k: v for k, v in loc.items() if k != "v0"}, "transplants": []}
    if loc["span"] is None:
        return out
    a, b = loc["span"]
    seg = src["genome"][a * A.IW:b * A.IW]
    eps = A.episodes(j["world"])
    cent = MF.centroids()[j["cluster"]]
    for h in j["hosts"]:
        hm = A.canonical(h["manifest"])
        hv = MF.curve(hm)[0]
        hr = A.evaluate(hm, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
        sham = j["sham"]["genome"][:len(seg)] if len(j["sham"]["genome"]) >= len(seg) else (j["sham"]["genome"] * (len(seg) // max(1, len(j["sham"]["genome"])) + 1))[:len(seg)]
        for where in ("start", "middle", "end"):
            for kind, segment in (("span", seg), ("sham", sham)):
                c = transplant(hm, segment, where)
                try:
                    v = MF.curve(c)[0]
                    r = A.evaluate(c, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
                except Exception as e:      # noqa: BLE001
                    out["transplants"].append({"host": h["organism_id"], "role": h["role"], "where": where, "kind": kind, "valid": False, "err": str(e)[:60]})
                    continue
                out["transplants"].append({"host": h["organism_id"], "role": h["role"], "where": where, "kind": kind, "valid": True, "d_source_class": MF.dist(v, cent), "d_host_before": MF.dist(v, hv), "host_r0": hr, "reward": r,
                                           "geometry": bool(MF.dist(v, cent) < 0.2), "competence": bool(r >= FLOOR and r > hr + BAND), "vector": v})
    return out


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-X17", "T-ARCH4/M1"], "deformation": "C", "requires": ["P-G11"], "scope": CM.SCOPE, "claim_type": "minimal-causal-transplantation",
                         "sources": {v[0]: (NSRC, v[1]) for v in SOURCES.values()}, "localisation": "per-instruction disable (opcode := NOP): geometry lost if curve distance > .3; reward lost if below r0 - band; HALT-probe reach map; span = smallest contiguous cover of the geometry-necessary set",
                         "hosts": "2 gen0_random parents, 4 immune shelf parents, 4 immune W2-evolver tops; insertion at start / middle / end; SHAM = same-length segment from an unrelated immune program",
                         "success": "geometry: distance to the source class centroid < .2; competence: reward on the source world >= floor and > host baseline + band", "readouts": "per source x host x position x kind: geometry / competence flags; span lengths; necessary-set sizes; reach",
                         "material_rule": "span transplants show geometry or competence in >= 20 percent of host insertions and sham transplants in fewer than half that share", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    H = hosts()
    sham_src = A.canonical(H[-1]["manifest"]) if H else None
    jobs = []
    for c, (shape, world) in SOURCES.items():
        for r in MF.representatives(c, NSRC):
            jobs.append({"src": r, "shape": shape, "world": world, "cluster": c, "hosts": H, "sham": sham_src})
    with A.pool(8) as ex:
        rows = list(ex.map(job, jobs))
    summ = {}
    for shape in ("start_anchored", "ask_time"):
        rs = [r for r in rows if r["shape"] == shape]
        tr = [t for r in rs for t in r["transplants"] if t["valid"]]
        for kind in ("span", "sham"):
            tk = [t for t in tr if t["kind"] == kind]
            summ["%s|%s" % (shape, kind)] = {"n": len(tk), "geometry": float(np.mean([t["geometry"] for t in tk])) if tk else None, "competence": float(np.mean([t["competence"] for t in tk])) if tk else None,
                                             "both": float(np.mean([t["geometry"] and t["competence"] for t in tk])) if tk else None, "d_source_class": float(np.mean([t["d_source_class"] for t in tk])) if tk else None,
                                             "by_role": {role: float(np.mean([t["geometry"] for t in tk if t["role"] == role])) for role in ("gen0", "shelf_immune", "w2_immune") if any(t["role"] == role for t in tk)},
                                             "by_where": {w: float(np.mean([t["geometry"] for t in tk if t["where"] == w])) for w in ("start", "middle", "end") if any(t["where"] == w for t in tk)}}
        summ["%s|localisation" % shape] = {"n_sources": len(rs), "geo_necessary_mean": float(np.mean([len(r["loc"]["geo_necessary"]) for r in rs])), "reward_necessary_mean": float(np.mean([len(r["loc"]["reward_necessary"]) for r in rs])),
                                           "span_len_mean": float(np.mean([r["loc"]["span_len"] for r in rs])), "n_mean": float(np.mean([r["loc"]["n"] for r in rs])), "reach_share": float(np.mean([np.mean(r["loc"]["reach"]) for r in rs])),
                                           "geo_subset_of_reward": float(np.mean([set(r["loc"]["geo_necessary"]) <= set(r["loc"]["reward_necessary"]) for r in rs])), "r0_mean": float(np.mean([r["loc"]["r0"] for r in rs]))}
    def ok(shape):
        s, h = summ.get("%s|span" % shape), summ.get("%s|sham" % shape)
        return bool(s and s["n"] and h and h["n"] and max(s["geometry"] or 0, s["competence"] or 0) >= 0.2 and max(h["geometry"] or 0, h["competence"] or 0) < 0.5 * max(s["geometry"] or 0, s["competence"] or 0))
    material = ok("start_anchored") or ok("ask_time")
    out = {"perturbation_id": PID, "parent": TID, "summary": summ, "transfer": {sh: ok(sh) for sh in ("start_anchored", "ask_time")}, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "minimal causal transplantation: %s; transfer %s" % ({k: {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk not in ("by_role", "by_where")} for k, v in summ.items()}, out["transfer"]), material, detail=summ)
    for tid in ("T-X17", "T-ARCH4/M1"):
        L.append_evidence(tid, PID, "cross: localisation (geometry-necessary vs reward-necessary sets) %s; transfer %s" % ({k: v for k, v in summ.items() if k.endswith("localisation")}, out["transfer"]), material)
    print("DONE material=%s transfer=%s (%.0f s) %s" % (material, out["transfer"], time.time() - t0, {k: (v.get("geometry"), v.get("competence")) for k, v in summ.items() if "|s" in k}))


if __name__ == "__main__":
    main()
