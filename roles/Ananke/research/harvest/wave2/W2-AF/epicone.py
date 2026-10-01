"""RELAY epidemic-cone certificate (EC): an upper bound on ANY program's accuracy at a RELAY cell's actual physics,
including sampled fanout, loss (per hop), wake (sync period / async p), latency + jitter, and dup.
Argument: targets are i.i.d. per trial, so information about trial k's cue exists only at the sensor from its
first awake cue tick, and leaves it only through packets. Destination, loss, latency, dup and wake draws come
from physics streams (ROUTE/LOSS/LAT/DUP/WAKE) that no program can influence (engine._emit / _tick), except
table weights under plastic_route, handled optimistically (every neighbour reached). So the set of sites that
CAN depend on the cue by tick t is the epidemic in which every informed site emits on every awake tick
(ignoring energy, caps, collisions, noise; each only removes packets). The actuator's S0 at the readout
depends on the cue only if it processed (was awake at) a delivery from that set at some tick <= readout;
otherwise its sign is independent of the target and scores .5 in expectation. Hence
    acc <= .5 + .5 * P(actuator informed by readout).
P is estimated by Monte Carlo over physics draws at the actual sensor/actuator positions of the row's own HELD
worlds (64 worlds = 32 mirror pairs; twins share positions and physics), REPS draws per trial; the reported
bound uses the binomial 99.9% upper limit on P (so it is conservative about MC error).
usage: python epicone.py [cells-file]   (default: the 35 task-2 cells plus the 6 rescued refresh_check cells)"""
import json, sys
import af_common as c
import numpy as np
from prometheus.ananke import envs, topology
from prometheus.ananke.physics import Physics

REPS = 256

def trial_probs(ph, env, seeds, rng, reps=REPS):
    N = ph.n_sites
    nbr, dist = topology.build(ph)
    glob = nbr is None
    ep = envs.build(ph, env, seeds)
    si = ep.schedule.sense_idx.numpy()[:, 0]; ri = ep.schedule.read_idx.numpy()[:, 0]
    Pd = env.period(); tr = env.trials
    base_s = 1.0 - ph.loss
    if glob:
        F = ph.fanout
    else:
        R = nbr.shape[1]
        allnb = ph.dest_mode == "all" or ph.plastic_route   # plastic: optimistic, every neighbour reached
        F = R if allnb else ph.fanout
    maxd = 1 if glob else int(dist.max())
    LMx = ph.lat_base + ph.lat_hop * maxd + 2 * ph.lat_jitter + 3
    LMeng = ph.lm()
    out = np.zeros((len(seeds) // 2, tr))
    for wi, b in enumerate(range(0, len(seeds), 2)):
        s, a = int(si[b]), int(ri[b])
        Rw = tr * reps
        t0s = np.repeat(np.arange(tr) * Pd, reps)          # [Rw]
        inf = np.zeros((Rw, N), bool); pend = np.zeros((Rw, N), bool)
        arr = np.zeros((LMx + env.delta + 2, Rw, N), bool)
        rows = np.arange(Rw)
        for dt in range(env.delta + 1):
            t = t0s + dt
            pend |= arr[dt]
            if ph.update_mode == "sync":
                awake = np.broadcast_to(((t % ph.update_period) == 0)[:, None], (Rw, N))
            else:
                awake = rng.random((Rw, N)) < ph.update_p
            inf |= awake & pend
            pend &= ~awake
            if dt < env.cue_len:
                inf[:, s] |= awake[:, s]
            em = inf & awake
            r_i, n_i = np.nonzero(em)
            if r_i.size == 0 or dt == env.delta:
                continue
            r_c = np.repeat(r_i, F); n_c = np.repeat(n_i, F)
            if glob:
                dst = (n_c + 1 + rng.integers(0, N - 1, r_c.size)) % N; dd = np.ones_like(dst)
            elif allnb:
                dst = nbr[n_i].reshape(-1); dd = dist[n_i].reshape(-1)
            else:
                j = rng.integers(0, R, r_c.size); dst = nbr[n_c, j]; dd = dist[n_c, j]
            surv = base_s ** dd if ph.loss_per_hop else np.full(dd.shape, base_s)
            jit = rng.integers(0, ph.lat_jitter + 1, r_c.size)
            dl = np.clip(ph.lat_base + ph.lat_hop * dd + jit, 1, LMeng - 1)
            ok = rng.random(r_c.size) < surv
            for keep, d_ in ((ok, dl),):
                tt = dt + d_
                m = keep & (tt <= env.delta)
                arr[tt[m], r_c[m], dst[m]] = True
            if ph.dup > 0:
                isd = rng.random(r_c.size) < ph.dup
                ok2 = rng.random(r_c.size) < surv
                dl2 = np.clip(dl + 1 + rng.integers(0, ph.lat_jitter + 1, r_c.size), 1, LMeng - 1)
                tt = dt + dl2
                m = isd & ok2 & (tt <= env.delta)
                arr[tt[m], r_c[m], dst[m]] = True
        out[wi] = inf[:, a].reshape(tr, reps).mean(1)
    return out

def bound(ph, env, seeds, rng, reps=REPS):
    P = trial_probs(ph, env, seeds, rng, reps)
    n = P.size * reps; k = P.mean() * n
    # Clopper-Pearson-like upper limit via normal approx with continuity (n large)
    p = P.mean(); se = np.sqrt(max(p * (1 - p), 1.0 / n) / n)
    pu = min(1.0, p + 3.29 * se)
    return {"P_informed": float(p), "P_upper999": float(pu), "EC_bound": float(.5 + .5 * p),
            "EC_bound_upper": float(.5 + .5 * pu), "P_by_world_min": float(P.mean(1).min()), "reps": reps}

if __name__ == "__main__":
    rc = json.load(open(c.HERE.parent / "W2-W/out/refresh_check.json"))["rows"]
    R = {r["cell_id"]: r for r in c.hc.rows()}
    ck = c.Clock(); res = []
    rng = np.random.default_rng(0xAFEC)
    for o in rc:
        r = R[o["cell"]]; ph = Physics.from_dict(r["physics"]).validate(); env = envs.EnvSpec(**r["env"])
        held = c.held_seeds(r)
        bnd = bound(ph, env, held, rng)
        rec = {"cell": o["cell"], "rescued_by_refresh": bool(o["refresh"] >= .6 and o["refresh_lo99"] > .55),
               "refresh": o["refresh"], "flood_decay0": o["flood_decay0"], "recorded_flood": o["recorded_flood"],
               "champ_held": r["result"]["held"]["acc"], "champ_hi99": r["result"]["held"]["hi99"], **bnd}
        mx = max(o["refresh"], o["flood_decay0"], o["recorded_flood"], r["result"]["held"]["acc"])
        rec["sound_vs_measured"] = bool(rec["EC_bound_upper"] >= mx - 0.02)
        res.append(rec)
        print(o["cell"][:8], ph.topology, "P %.3f EC %.3f (up %.3f)  max-measured %.3f  sound %s" % (
            bnd["P_informed"], bnd["EC_bound"], bnd["EC_bound_upper"], mx, rec["sound_vs_measured"]), flush=True)
        c.save("epicone.json", {"rows": res, "compute": ck.done()})
    print(ck.done())
