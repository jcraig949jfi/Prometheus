"""LC2: Monte-Carlo reach bound for XOR at a row's physics (W2-J).

Extends H-PLANT lightcone.bound (topology + latency + sync wake) with:
  - async wake drawn per site per tick (Bernoulli update_p), including the SENSORS: a cue is seen only
    if the sensor is awake at a tick of the cue window (SENSE is not accumulated, engine.py step 2);
  - per-copy loss (surv = (1-loss)^dist if loss_per_hop else 1-loss, engine.py __init__),
  - finite fanout (dest sample: F uniform draws over the neighbour table; global: F uniform draws over
    the other N-1 sites), dup copies (independent survival, delay+1).
Optimistic everywhere else (an UPPER bound on the fraction f of scored trials in which the actuator can
have processed both cues by the readout tick):
  - every informed site emits at EVERY awake tick (maximal flood), one packet carries both bits;
  - latency jitter sampled per copy as the engine does (JITTER=True; lc2_min.json has jitter 0), no
    caps/collisions, no noise, no economy, no decay;
  - plastic routing rows: dest sample is ALSO computed as dest all (any routing table a program could
    write), and the larger f is the bound used ("f_opt").
  Information counts only once PROCESSED at an awake tick <= readout tick (as in lightcone.py).
acc <= 0.5 + f/2 (XOR with one input unknown scores 1/2 by mirror symmetry).
"""
import numpy as np
from wj_common import *
from prometheus.ananke import assays, envs, topology
from prometheus.ananke.physics import Physics


def _targets(ph, nbr, dist, sites, rng, mode):
    """-> list of (rec [n,F], dist [n,F]) for emitting sites."""
    N = ph.n_sites
    n = len(sites)
    if ph.topology == "global":
        F = ph.fanout
        rec = (sites[:, None] + 1 + rng.integers(0, N - 1, size=(n, F))) % N
        return rec, np.ones_like(rec)
    if mode == "all":
        return nbr[sites], dist[sites]
    R = nbr.shape[1]
    j = rng.integers(0, R, size=(n, ph.fanout))
    return nbr[sites][np.arange(n)[:, None], j], dist[sites][np.arange(n)[:, None], j]


JITTER = True   # sample per-copy latency jitter U{0..lat_jitter} (exact physics); False = min latency


def reach_trial(ph, env, s_list, a, t0, rng, nbr, dist, mode):
    """One MC replicate of one trial: -> (informed_1, informed_2) at actuator by readout."""
    N = ph.n_sites
    p = ph.update_period
    ro = t0 + env.delta
    base = 1.0 - ph.loss
    surv_tab = np.array([(base ** d if ph.loss_per_hop else base) for d in range(ph.max_dist() + 1)])
    T = ro + 1
    # wake table [ticks t0..ro] shared by both floods
    ticks = np.arange(t0, ro + 1)
    if ph.update_mode == "sync":
        awake = np.broadcast_to((ticks % p == 0)[:, None], (len(ticks), N))
    else:
        awake = rng.random((len(ticks), N)) < ph.update_p
    # informed[bit] [N] bool; pending arrivals: arr[bit][tick_idx] set of sites
    L = len(ticks)
    pend = np.zeros((2, L + 64, N), dtype=bool)
    inf = np.zeros((2, N), dtype=bool)
    for k, s in enumerate(s_list):
        for c in range(env.cue_len):
            ti = c
            if ti < L and awake[ti, s]:
                pend[k, ti, s] = True
                break
    for ti in range(L):
        aw = awake[ti]
        newly = pend[:, ti] & aw[None, :]
        inf |= newly
        # carry pending to next tick for asleep sites (inbox accumulates while asleep)
        if ti + 1 < L + 64:
            pend[:, ti + 1] |= pend[:, ti] & ~aw[None, :]
        em = (inf[0] | inf[1]) & aw
        es = np.flatnonzero(em)
        if es.size == 0:
            continue
        rec, dd = _targets(ph, nbr, dist, es, rng, mode)
        sv = surv_tab[np.minimum(dd, len(surv_tab) - 1)]
        delay = np.maximum(1, ph.lat_base + ph.lat_hop * dd)
        for extra, prob in ((0, 1.0), (1, ph.dup)):
            if prob <= 0:
                continue
            ok = (rng.random(rec.shape) < sv) & (rng.random(rec.shape) < prob)
            jit = rng.integers(0, ph.lat_jitter + 1, size=rec.shape) if (JITTER and ph.lat_jitter > 0) else 0
            ta = ti + delay + extra + jit
            for b in range(2):
                carr = inf[b][es][:, None] & ok
                r_, t_ = rec[carr], ta[carr]
                keep = t_ < L
                pend[b, t_[keep], r_[keep]] = True
    return bool(inf[0, a]), bool(inf[1, a])


def bound(r, M=32, R=4, seed=0):
    """Expected-f upper bound over M worlds (M/2 position pairs) x scored trials x R replicates."""
    ph = Physics.from_dict(r["physics"])
    env = envs.EnvSpec(**r["env"])
    seeds = assays.world_seeds(WJ_NS + 7, M)
    ep = envs.build(ph, env, seeds)
    sidx = ep.schedule.sense_idx.numpy()
    ridx = ep.schedule.read_idx.numpy()[:, 0]
    nbr, dist = topology.build(ph)
    Pd = env.period()
    rng = np.random.default_rng(seed)
    modes = ["all" if (ph.dest_mode == "all" and ph.topology != "global") else "sample"]
    if modes[0] == "sample" and ph.plastic_route and ph.topology != "global":
        modes.append("all")
    res = {}
    for mode in modes:
        both, one1, one2 = [], [], []
        for b in range(0, M, 2):
            for k in range(env.trials):
                if not ep.scored[b, k]:
                    continue
                for _ in range(R):
                    i1, i2 = reach_trial(ph, env, sidx[b][:2], int(ridx[b]), k * Pd, rng, nbr, dist, mode)
                    both.append(i1 and i2); one1.append(i1); one2.append(i2)
        f = float(np.mean(both))
        res[mode] = {"f_both": f, "f_s1": float(np.mean(one1)), "f_s2": float(np.mean(one2)),
                     "acc_ub": 0.5 + f / 2, "n": len(both)}
    f_opt = max(v["f_both"] for v in res.values())
    return {"cell": r["cell_id"], "modes": res, "f_opt": f_opt, "acc_ub": 0.5 + f_opt / 2}


if __name__ == "__main__":
    import sys, time
    t0 = time.process_time()
    L = lc()
    rows = [r for r in xor_evolve()]
    only = [a for a in sys.argv[1:] if a != "--min"]
    JITTER = "--min" not in sys.argv
    globals()["JITTER"] = JITTER
    out = []
    for r in rows:
        if only and r["cell_id"][:8] not in only:
            continue
        b = bound(r)
        b["lc1_bound"] = L[r["cell_id"]]["bound"]
        out.append(b)
        print(r["cell_id"][:8], "lc1=%.3f" % b["lc1_bound"], {m: round(v["acc_ub"], 3) for m, v in b["modes"].items()}, flush=True)
    print("cpu_s", time.process_time() - t0)
    if not only:
        save("lc2.json" if JITTER else "lc2_min.json", {"rows": out, "cpu_s": time.process_time() - t0})
