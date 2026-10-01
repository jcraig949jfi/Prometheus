"""Analytic light-cone bound for a task at a physics (PLAN s2, P-XOR (i)).

For each world and scored trial: earliest tick at which information from each sensor's cue
can be PROCESSED at the actuator, using the fastest possible transport of this physics
(no loss, no caps, jitter 0, fanout reaching any neighbour, every site relays at its first
awake tick). Information counts only if processed at an awake tick <= readout tick.
XOR needs both sensors; acc <= .5 + f/2 where f = fraction of scored trials in reach.
usage: python lightcone.py <cell_id> [<cell_id> ...]"""
import heapq
import sys

import numpy as np

import hp_common as hc
from hp_common import save, row
from prometheus.ananke import assays, envs, topology
from prometheus.ananke.physics import Physics


def next_awake(t, ph):
    if ph.update_mode != "sync" or ph.update_period == 1:
        return t   # async: optimistic (could wake any tick)
    p = ph.update_period
    return t + ((-t) % p)


def earliest(ph, src, t_cue, cue_len):
    """earliest processing tick at every site for a cue at src during [t_cue, t_cue+cue_len)."""
    nbr, dist = topology.build(ph)
    N = ph.n_sites
    best = np.full(N, 10 ** 9)
    t_emit = next_awake(t_cue, ph)
    if t_emit >= t_cue + cue_len:
        return best
    best[src] = t_emit
    pq = [(t_emit, src)]
    while pq:
        t, u = heapq.heappop(pq)
        if t > best[u]:
            continue
        if nbr is None:   # global: any site
            vs, ds = [v for v in range(N) if v != u], [1] * (N - 1)
        else:
            vs, ds = nbr[u], dist[u]
        for v, d in zip(vs, ds):
            delay = max(1, ph.lat_base + ph.lat_hop * int(d))
            tv = next_awake(t + delay, ph)
            if tv < best[v]:
                best[v] = tv
                heapq.heappush(pq, (tv, v))
    return best


def bound(cell, M=256):
    r = row(cell)
    ph = Physics.from_dict(r["physics"])
    env = envs.EnvSpec(**r["env"])
    seeds = assays.world_seeds(hc.SCORE_NS, M)
    ep = envs.build(ph, env, seeds)
    sidx = ep.schedule.sense_idx.numpy()
    ridx = ep.schedule.read_idx.numpy()[:, 0]
    Pd = env.period()
    cache = {}
    inreach = []
    for b in range(0, M, 2):            # mirror twins share positions
        for k in range(env.trials):
            if not ep.scored[b, k]:
                continue
            t0 = k * Pd
            ro = int(ep.ro_tick[b, k])
            ok = True
            for s in sidx[b][:2 if env.family == "XOR" else 1]:
                key = (int(s), t0 % (ph.update_period if ph.update_mode == "sync" else 1))
                if key not in cache:
                    cache[key] = earliest(ph, int(s), t0 % ph.update_period if ph.update_mode == "sync" else 0, env.cue_len) - (t0 % ph.update_period if ph.update_mode == "sync" else 0)
                arr = cache[key][ridx[b]] + t0
                ok &= bool(arr <= ro)
            inreach.append(ok)
    f = float(np.mean(inreach))
    return {"cell": cell, "physics": ph.to_dict(), "env": env.to_dict(), "f_in_reach": f,
            "acc_upper_bound": 0.5 + f / 2, "n_trials": len(inreach)}


if __name__ == "__main__":
    out = [bound(c) for c in sys.argv[1:]]
    for o in out:
        print(o["cell"], o["env"]["family"], "f_in_reach=%.4f  acc<=%.4f" % (o["f_in_reach"], o["acc_upper_bound"]))
    save("lightcone_" + "_".join(c[:8] for c in sys.argv[1:]) + ".json", out)
