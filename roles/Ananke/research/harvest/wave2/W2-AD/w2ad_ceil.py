"""W2-AD joint ceiling = MIN over the valid upper bounds that apply to a candidate cell (PREREG_PTE_C2_DRAFT s2.2).

Components (all imported READ-ONLY or copied with attribution; none modified):
  t2   : W2-P task2_timing.ceilings  (RELAY, MAJ; sync parity + transport + async cue loss + actuator wake).
         MAJ uses inward placement (inward_place=True; == W2-I/W2-A1 SEMANTIC placement, M[:, a]).
  w2u  : W2-U w2u_ceil.ceilings      (RELAY, FLIP block scope, XOR; joint async terms).
  lc2k : W2-J lc2.reach_trial generalised from 2 to K sensor bits (copied below, logic unchanged otherwise):
         Monte-Carlo optimistic flood with per-copy loss, finite fanout, dup, latency jitter, async wake of
         every site incl. sensors.  Bound per trial = acc_K(#informed sensors at the actuator by ro).
         It is an estimate of an expectation (MC noise), not a deterministic bound: reported with n.
  epi  : W2-S epidemic_bound.bound (global topology), copied verbatim (that module runs I/O on import).
         MAJ: expected informed votes <= 5q, so acc <= concave majorant of acc_k at 5q (Jensen).
q (MAJ per-vote timely-delivery probability) = min(t2-model marginal availability, lc2k informed fraction).
"""
from w2ad_common import *
import math
import task2_timing as T2
import w2u_ceil as WU
from prometheus.ananke import topology


# ------------------------------------------------ W2-S epidemic bound, verbatim logic (dicts p, e)
def epi_bound(p, e):
    N, F = p["n_sites"], p["fanout"]; dmin = max(1, p["lat_base"] + p["lat_hop"])
    best = 0.0
    phases = range(p["update_period"]) if p["update_mode"] == "sync" else [0]
    for ph0 in phases:
        def w(tau):
            if p["update_mode"] == "sync": return 1.0 if (ph0 + tau) % p["update_period"] == 0 else 0.0
            return p["update_p"]
        ts = [t for t in range(e["cue_len"]) if w(t) > 0]
        if not ts: continue
        I = [0.0] * (e["delta"] + 1)
        for tau in range(e["delta"] + 1):
            prev = I[tau - 1] if tau > 0 else 0.0
            if tau == ts[0]: prev = max(prev, 1.0)
            src = tau - dmin
            new = F * w(src) * I[src] if src >= 0 else 0.0
            I[tau] = min(N, prev + new)
        q = min(1.0, max(0.0, (I[-1] - 1) / (N - 1)))
        best = max(best, q)
    return best


def concave_majorant(vals, x):
    """Least concave majorant of points (k, vals[k]) evaluated at x in [0, K]."""
    pts = list(enumerate(vals))
    hull = []
    for p in pts:
        while len(hull) >= 2:
            (x1, y1), (x2, y2) = hull[-2], hull[-1]
            if (y2 - y1) * (p[0] - x1) <= (p[1] - y1) * (x2 - x1):
                hull.pop()
            else:
                break
        hull.append(p)
    for (x1, y1), (x2, y2) in zip(hull, hull[1:]):
        if x1 <= x <= x2:
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    return hull[-1][1]


# ------------------------------------------------ LC2 generalised to K bits (W2-J lc2.py logic)
def _targets(ph, nbr, dist, sites, rng, mode):
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


def reach_trial_k(ph, env, s_list, a, t0, rng, nbr, dist, mode):
    N = ph.n_sites
    K = len(s_list)
    p = ph.update_period
    ro = t0 + env.delta
    base = 1.0 - ph.loss
    surv_tab = np.array([(base ** d if ph.loss_per_hop else base) for d in range(ph.max_dist() + 1)])
    ticks = np.arange(t0, ro + 1)
    if ph.update_mode == "sync":
        awake = np.broadcast_to((ticks % p == 0)[:, None], (len(ticks), N))
    else:
        awake = rng.random((len(ticks), N)) < ph.update_p
    L = len(ticks)
    pend = np.zeros((K, L + 64, N), dtype=bool)
    inf = np.zeros((K, N), dtype=bool)
    for k, s in enumerate(s_list):
        for c in range(env.cue_len):
            if c < L and awake[c, s]:
                pend[k, c, s] = True
                break
    for ti in range(L):
        aw = awake[ti]
        newly = pend[:, ti] & aw[None, :]
        inf |= newly
        pend[:, ti + 1] |= pend[:, ti] & ~aw[None, :]
        em = inf.any(0) & aw
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
            jit = rng.integers(0, ph.lat_jitter + 1, size=rec.shape) if ph.lat_jitter > 0 else 0
            ta = ti + delay + extra + jit
            for b in range(K):
                carr = inf[b][es][:, None] & ok
                r_, t_ = rec[carr], ta[carr]
                keep = t_ < L
                pend[b, t_[keep], r_[keep]] = True
    return inf[:, a].copy()


def lc2k(ph, env, ep, npairs=16, R=1, seed=0):
    """-> (mean bound on accuracy, mean informed fraction per sensor, n trials)."""
    fam = env.family
    nsens = {"RELAY": 1, "FLIP": 1, "XOR": 2, "MAJ": env.n_maj}[fam]
    sidx = ep.schedule.sense_idx.numpy()
    ridx = ep.schedule.read_idx.numpy()[:, 0]
    nbr, dist = topology.build(ph)
    Pd = env.period()
    rng = np.random.default_rng(seed)
    modes = ["all" if (ph.dest_mode == "all" and ph.topology != "global") else "sample"]
    if modes[0] == "sample" and ph.plastic_route and ph.topology != "global":
        modes.append("all")
    acck = [T2.maj_acc(k, env.flip_p) for k in range(nsens + 1)] if fam == "MAJ" else None
    best = None
    for mode in modes:
        accs, fr = [], []
        for b in range(0, min(2 * npairs, len(ridx)), 2):
            for k in range(env.trials):
                if not ep.scored[b, k]:
                    continue
                for _ in range(R):
                    inf = reach_trial_k(ph, env, [int(x) for x in sidx[b][:nsens]], int(ridx[b]), k * Pd,
                                        rng, nbr, dist, mode)
                    fr.append(inf.mean())
                    if fam == "MAJ":
                        accs.append(acck[int(inf.sum())])
                    else:
                        accs.append(0.5 + 0.5 * float(inf.all()))
        o = (float(np.mean(accs)), float(np.mean(fr)), len(accs))
        if best is None or o[0] > best[0]:
            best = o
    return best


# ------------------------------------------------ MAJ q from the W2-P timing model (marginal per vote)
def maj_q_t2(ph, env, ep):
    sidx = ep.schedule.sense_idx.numpy()
    ridx = ep.schedule.read_idx.numpy()[:, 0]
    Pd, cl = env.period(), env.cue_len
    sync = ph.update_mode == "sync"
    per = ph.update_period if sync else 1
    p = 1.0 if sync else ph.p16(ph.update_p) / 65536.0
    cache = {}

    def rel(s, phase):
        key = (int(s), phase)
        if key not in cache:
            cache[key] = T2.earliest(ph, int(s), phase, cl) - phase
        return cache[key]
    qs = []
    for b in range(0, len(ridx), 2):
        a = int(ridx[b])
        for k in range(env.trials):
            t0 = k * Pd
            ro_rel = int(ep.ro_tick[b, k]) - t0
            for s in sidx[b][:env.n_maj]:
                base = int(rel(s, t0 % per)[a])
                if sync:
                    qs.append(float(base <= ro_rel)); continue
                if int(s) == a:
                    qs.append(1 - (1 - p) ** (ro_rel + 1)); continue
                tot = 0.0
                for m in range(ro_rel + 1):
                    L = ro_rel - m
                    tot += p * (1 - p) ** m * sum(p * (1 - p) ** j for j in range(cl) if base + j <= L)
                qs.append(tot)
    return float(np.mean(qs))


# ------------------------------------------------ reachability / hop audit
def hop_audit(ph, env, ep):
    """Directed BFS hop count sensor -> actuator for every world (pairs share positions).
    -> dict(min_hops, max_hops, impossible_worlds, hop1_all)."""
    fam = env.family
    nsens = {"RELAY": 1, "FLIP": 1, "XOR": 2, "MAJ": env.n_maj}[fam]
    sidx = ep.schedule.sense_idx.numpy()
    ridx = ep.schedule.read_idx.numpy()[:, 0]
    hops, imp, cache = [], 0, {}
    for b in range(0, len(ridx), 2):
        a = int(ridx[b]); bad = False
        for s in sidx[b][:nsens]:
            s = int(s)
            if s not in cache:
                cache[s] = topology_graph_dist(ph, s)
            h = int(cache[s][a])
            if h < 0:
                bad = True
            else:
                hops.append(h)
        imp += bad
    hops = np.asarray(hops) if hops else np.asarray([-1])
    return {"min_hops": int(hops.min()), "max_hops": int(hops.max()), "mean_hops": float(hops.mean()),
            "impossible_pairs": int(imp)}


def topology_graph_dist(ph, s):
    from prometheus.ananke import topology as tp
    return tp.graph_distances(ph, s)


# ------------------------------------------------ the joint ceiling
def build_ep(ph, env, seeds, inward):
    if inward:
        real = envs.dist_matrix
        envs.dist_matrix = lambda ph_: real(ph_).T.copy()
        try:
            return envs.build(ph, env, seeds)
        finally:
            envs.dist_matrix = real
    return envs.build(ph, env, seeds)


def needs_lc2(ph):
    tw = ph.table_width()
    sample_thin = ph.topology == "global" or (ph.dest_mode == "sample" and ph.fanout < tw)
    return ph.loss > 0 or sample_thin or ph.dup > 0 or ph.lat_jitter > 0


def joint_ceiling(ph, env, seeds, lc2_pairs=16, do_lc2=True):
    fam = env.family
    inward = fam == "MAJ"
    ep = build_ep(ph, env, seeds, inward)
    comp = {}
    if fam in ("RELAY", "MAJ"):
        c = T2.ceilings(ph, env, seeds, inward_place=inward)
        comp["t2_joint"] = c["joint"]; comp["t2_lc"] = c["lc"]
    if fam in ("RELAY", "FLIP", "XOR"):
        c = WU.ceilings(ph, env, seeds)
        if fam == "FLIP":
            comp["w2u_block"] = c["joint_block"]; comp["w2u_episode"] = c["joint_episode"]
            comp["w2u_copy_block"] = c["copy_block"]
        else:
            comp["w2u_joint"] = c["joint"]
    q_t2 = maj_q_t2(ph, env, ep) if fam == "MAJ" else None
    q_lc2 = None
    if do_lc2 and needs_lc2(ph):
        b, fr, n = lc2k(ph, env, ep, npairs=lc2_pairs)
        comp["lc2k"] = b; comp["lc2k_n"] = n
        q_lc2 = fr
    if ph.topology == "global":
        q = epi_bound(ph.to_dict(), env.to_dict())
        comp["epi_q"] = q
        if fam == "MAJ":
            acck = [T2.maj_acc(k, env.flip_p) for k in range(env.n_maj + 1)]
            comp["epi"] = concave_majorant(acck, env.n_maj * q)
        elif fam == "XOR":
            comp["epi"] = 0.5 + 0.5 * q   # both cues needed; one sensor's q is a valid looser bound
        else:
            comp["epi"] = 0.5 + 0.5 * q
    keys = [k for k in ("t2_joint", "w2u_joint", "w2u_block", "lc2k", "epi") if k in comp]
    ceil = min(comp[k] for k in keys)
    binding = min(keys, key=lambda k: comp[k])
    out = {"ceiling": ceil, "binding": binding, "components": comp, "hops": hop_audit(ph, env, ep)}
    if fam == "MAJ":
        qq = [x for x in (q_t2, q_lc2, comp.get("epi_q")) if x is not None]
        out["q"] = min(qq); out["q_t2"] = q_t2; out["q_lc2"] = q_lc2
    return out
