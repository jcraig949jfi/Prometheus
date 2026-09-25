"""One replicate block: all five arms stepped in lockstep on the same inflow tape stream, base environment stream and schedule."""
from __future__ import annotations

import hashlib
import time
from collections import Counter

from archaeon.z80atlas.grammar import FROZEN as F
from archaeon.envgate import mechanism as M
from archaeon.envgate.engine import World, Memo, EnvStream, inflow_stream, tape_sha, N, ORIGIN_INFLOW
from archaeon.envgate.ruler import measure, HIT


def run_block(block: int, schedule: dict, arms=None, progress=None, tapes=None) -> dict:
    """schedule = {K_chambers, dwell, refills}. `tapes` overrides the inflow stream (controls only: never used for treatment)."""
    arms = arms or M.ARM_ORDER; K = schedule["K_chambers"]; dwell = schedule["dwell"]; E_in = schedule["refills"] * dwell
    tail = M.DEFAULTS["persistence_multiple"] * F["max_age"] + 1
    memo = Memo(); env = EnvStream(block); worlds = {a: World(a, block, K) for a in arms}
    stream = tapes if tapes is not None else inflow_stream(block); origin = "control_inserted" if tapes is not None else ORIGIN_INFLOW
    arrival = 0; ruler_counts = Counter(); hits = {}; pair = {a: hashlib.sha256() for a in arms}; t0 = time.time()
    for epoch in range(E_in + tail):
        if epoch < E_in and epoch % dwell == 0:
            for c in range(K):
                t = next(stream); rv = measure(t, memo); ruler_counts[rv["class"]] += 1
                if rv["class"] in HIT: hits[arrival] = dict(rv, tape=t.hex(), epoch_in=epoch, cell=N + c)
                for a, w in worlds.items():
                    w.arrive(N + c, t, arrival, epoch, origin); pair[a].update(arrival.to_bytes(8, "big") + epoch.to_bytes(8, "big") + t)
                arrival += 1
        if epoch == E_in:
            for w in worlds.values(): w.clear_chambers(epoch)
        for w in worlds.values(): w.step(epoch, env, memo)
        if progress and epoch % 2000 == 0: progress(epoch, time.time() - t0, memo)
    out = {"block": block, "schedule": schedule, "arrivals": arrival, "epochs": E_in + tail, "ruler_counts": dict(ruler_counts), "hits": hits,
           "pairing_sha256": {a: h.hexdigest() for a, h in pair.items()}, "wall_s": round(time.time() - t0, 1), "memo": {"hits": memo.hits, "miss": memo.miss}, "arms": {}}
    for a, w in worlds.items():
        est = set(w.established()); lineages = []
        for f, rec in w.founder.items():
            st = w.lstat[f]
            row = dict(rec, births=st["births"], exact_births=st["exact"], mean_fid=round(st["fid_sum"] / st["births"], 3) if st["births"] else None,
                       peak=st["peak"], peak_epoch=st["peak_epoch"], last_alive=st["last_alive"], max_gen=st["max_gen"], established=f in est,
                       copy_out_inputs=st["inputs"], chamber_births=st["chamber_births"], chamber_exact=st["chamber_exact"], chamber_exact_inputs=st["exact_inputs"], tape_sha=tape_sha(bytes.fromhex(rec["tape"])) if rec["tape"] else None)
            if f in est:
                row["traj"] = st["traj"]; row["final_tapes"] = dict(sorted(w.ecology_tapes(f).items(), key=lambda kv: -kv[1])[:10])
            lineages.append(row)
        ex_in = Counter()
        for st in w.lstat.values(): ex_in.update(st["exact_inputs"])
        out["arms"][a] = {"established_arrivals": sorted(w.founder[f]["arrival"] for f in est), "n_established": len(est),
                          "chamber_births_total": sum(st["chamber_births"] for st in w.lstat.values()),
                          "chamber_exact_total": sum(st["chamber_exact"] for st in w.lstat.values()), "chamber_exact_inputs": dict(ex_in),
                          "founders_with_births": len(w.founder), "births": w.births, "refused_into_chamber": w.refused_into_chamber,
                          "final_ecology_pop": sum(1 for i in range(N) if w.genomes[i] is not None), "telemetry": w.telemetry,
                          "lineages": [r for r in lineages if r["established"] or r["births"] >= 5 or r["arrival"] in hits]}
    return out
