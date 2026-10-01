"""TASK 2 (analytic; no engine run): timing + light-cone ceilings for every RELAY and MAJ evolve row.

Model (an UPPER bound on per-trial accuracy for ANY program), engine facts used:
 * SENSE enters only via an awake site's registers (engine.py:303-316); not latched while asleep.
 * Packets are latched in Acc until the receiver is awake (engine.py:296, 321-322).
 * S changes only at awake ticks (engine.py:369); the readout is S0 of the actuator at ro (engine.py:441).
 * delay >= max(1, lat_base + lat_hop*dist) (engine.py:512-513); sync wake = (t % period == 0).
 * async wake per (site, tick) independent with p = p16(update_p)/65536 (engine.py:309).
Optimistic assumptions (keep it an upper bound): no loss, no cap/collision, jitter 0, any neighbour
reachable, intermediate relays process at arrival, the program knows which sensor votes arrived.
Per trial: sync -> deterministic earliest processing tick at the actuator for each sensor (identical to
H-PLANT lightcone.earliest); async -> sensor i's first awake tick in the cue window j (prob p(1-p)^j)
gives availability base_i + j at the actuator; the actuator must be awake at some tick in
[base_i + j, ro]; condition on the actuator's last awake tick L <= ro (sensors independent given L).
MAJ accuracy given k arrived votes = Bayes (majority, ties .5) with per-vote reliability 1 - flip_p.
Ceiling averaged over scored trials of 128 fresh worlds (64 mirror pairs; twins share positions).
Components: lc (sync parity + transport, async optimistic = H-PLANT model), cue (async cue loss alone,
no transport), joint (both).
SIGNAL-attainable: W2-B attain.min_true_to_cross(.55, P=M_held/2, K=#scored trials, power .5)."""
from w2p_common import *
import heapq, math
import attain as A

WORLDS = 128
_TOPO = {}


def topo(ph):
    key = (ph.topology, ph.n_sites, ph.radius, ph.k_random, ph.rewire, ph.topo_seed)
    if key not in _TOPO:
        from prometheus.ananke import topology
        _TOPO[key] = topology.build(ph)
    return _TOPO[key]


def next_awake(t, ph):
    if ph.update_mode != "sync" or ph.update_period == 1:
        return t
    p = ph.update_period
    return t + ((-t) % p)


def earliest(ph, src, t_cue, cue_len):
    """same logic as H-PLANT lightcone.earliest, with the topology cached."""
    nbr, dist = topo(ph)
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
        if nbr is None:
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


def maj_acc(k, q):
    r = 1 - q
    return sum(math.comb(k, c) * r ** c * q ** (k - c) * (1.0 if 2 * c > k else .5 if 2 * c == k else 0.)
               for c in range(k + 1))


def poisson_binom(ps):
    dist = np.zeros(len(ps) + 1)
    dist[0] = 1
    for p in ps:
        dist[1:] = dist[1:] * (1 - p) + dist[:-1] * p
        dist[0] *= (1 - p)
    return dist


def ceilings(ph, env, seeds, inward_place=False):
    if inward_place:
        with inward():
            ep = envs.build(ph, env, seeds)
    else:
        ep = envs.build(ph, env, seeds)
    sidx = ep.schedule.sense_idx.numpy()
    ridx = ep.schedule.read_idx.numpy()[:, 0]
    fam = env.family
    nsens = 1 if fam == "RELAY" else env.n_maj
    q = env.flip_p if fam == "MAJ" else 0.0
    acck = [maj_acc(k, q) for k in range(nsens + 1)] if fam == "MAJ" else [0.5, 1.0]
    Pd = env.period()
    cl = env.cue_len
    sync = ph.update_mode == "sync"
    per = ph.update_period if sync else 1
    p = ph.p16(ph.update_p) / 65536.0 if not sync else 1.0
    cache = {}

    def rel(s, phase):
        key = (int(s), phase)
        if key not in cache:
            cache[key] = earliest(ph, int(s), phase, cl) - phase
        return cache[key]

    lc, cue, joint = [], [], []
    for b in range(0, len(seeds), 2):
        a = int(ridx[b])
        ss = [int(x) for x in sidx[b][:nsens]]
        for k in range(env.trials):
            if not ep.scored[b, k]:
                continue
            t0 = k * Pd
            ro_rel = int(ep.ro_tick[b, k]) - t0
            phase = t0 % per
            arr = [int(rel(s, phase)[a]) for s in ss]   # earliest processing tick at actuator - t0
            kk = sum(x <= ro_rel for x in arr)
            lc.append(acck[kk])
            if sync:
                cue.append(acck[nsens])
                joint.append(acck[kk])
                continue
            pc = 1 - (1 - p) ** cl
            dist = poisson_binom([pc] * nsens)
            cue.append(float(sum(dist[i] * acck[i] for i in range(nsens + 1))))
            tot = (1 - p) ** (ro_rel + 1) * acck[0]   # actuator never awake in [t0, ro]
            for m in range(ro_rel + 1):
                L = ro_rel - m
                pL = p * (1 - p) ** m
                ps = []
                for s, base in zip(ss, arr):
                    if s == a:   # optimistic: actuator senses its own cue whenever it is awake at all
                        ps.append(1.0)
                        continue
                    ps.append(sum(p * (1 - p) ** j for j in range(cl) if base + j <= L))
                d2 = poisson_binom(ps)
                tot += pL * float(sum(d2[i] * acck[i] for i in range(nsens + 1)))
            joint.append(tot)
    return {"lc": float(np.mean(lc)), "cue": float(np.mean(cue)), "joint": float(np.mean(joint)),
            "n_trials": len(joint)}


if __name__ == "__main__":
    ck = Clock()
    lcj = json.load(open(ROOT / "roles/Ananke/research/harvest/H-PLANT/out/lc_census.json"))
    lcmap = {o["cell"]: o for o in lcj["rows"]}
    # ---- known answer 1: reproduce H-PLANT lc_census bounds (SCORE_NS, M=64) for RELAY rows exactly
    ka = []
    rel_rows = [r for r in hc.rows() if r["kind"] == "evolve" and r["env"]["family"] == "RELAY"]
    pick = rel_rows[::max(1, len(rel_rows) // 12)][:12] + [r for r in rel_rows if lcmap[r["cell_id"]]["bound"] < .6][:6]
    for r in pick:
        ph = Physics.from_dict(r["physics"])
        env = envs.EnvSpec(**r["env"])
        c = ceilings(ph, env, assays.world_seeds(hc.SCORE_NS, 64))
        b = lcmap[r["cell_id"]]["bound"]
        ka.append((r["cell_id"][:8], b, c["lc"], abs(c["lc"] - b) < 1e-12))
    print("KA vs H-PLANT lc bound:", sum(x[3] for x in ka), "/", len(ka), ka, flush=True)
    # ---- known answer 2: A1 F7 numbers
    pc = 1 - .25
    ka2 = {"MAJ_cue_only_p.5_5sensor": round(sum(poisson_binom([pc] * 5)[i] * maj_acc(i, .3) for i in range(6)), 4),
           "MAJ_sync_5sensor": round(maj_acc(5, .3), 4),
           "RELAY_single_p.5": 1 - .5 * .25, "RELAY_single_p.8": 1 - .5 * .04}
    print("KA2 (A1 F7: .788 / .837 / .875 / .98):", ka2, flush=True)
    out = []
    E = [r for r in hc.rows() if r["kind"] == "evolve" and r["env"]["family"] in ("RELAY", "MAJ")]
    thr_cache = {}
    for i, r in enumerate(E):
        ph = Physics.from_dict(r["physics"])
        env = envs.EnvSpec(**r["env"])
        seeds = fresh_seeds(r, WORLDS)
        c = ceilings(ph, env, seeds)
        held = r["result"]["held"]
        P = r["search"]["M_held"] // 2
        K = int(env.trials)
        if (P, K) not in thr_cache:
            thr_cache[(P, K)] = A.min_true_to_cross(0.55, P, K, "lo_gt", 0.5)
        o = {"cell": r["cell_id"], "wave": r["wave"], "family": env.family, "topology": ph.topology,
             "update_mode": ph.update_mode, "update_period": ph.update_period, "update_p": ph.update_p,
             "d": env.d, "delta": env.delta, "cue_len": env.cue_len, "trials": env.trials,
             "lat_base": ph.lat_base, "lat_hop": ph.lat_hop, "radius": ph.radius,
             "held_acc": held["acc"], "held_lo99": held["lo99"], "SIGNAL": bool(r["labels"]["SIGNAL"]),
             "ceil_lc": c["lc"], "ceil_cue": c["cue"], "ceil_joint": c["joint"],
             "signal_attainable": thr_cache[(P, K)],
             "hplant_lc_bound": lcmap.get(r["cell_id"], {}).get("bound")}
        if env.family == "MAJ" and ph.topology in ("random", "smallworld"):
            ci = ceilings(ph, env, seeds, inward_place=True)
            o.update({"ceil_lc_inward": ci["lc"], "ceil_joint_inward": ci["joint"]})
        if ph.update_mode == "sync":
            o["ceil_joint_heldset"] = ceilings(ph, env, held_seeds(r))["joint"]
        out.append(o)
        if i % 40 == 0:
            print(i, len(E), ck.done(), flush=True)
    save("task2_timing.json", {"rows": out, "ka_hplant": ka, "ka2": ka2, "compute": ck.done()})
    print(ck.done())
