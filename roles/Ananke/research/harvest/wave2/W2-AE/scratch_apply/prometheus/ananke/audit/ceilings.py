"""Analytic accuracy CEILINGS for PTE cells: one API over the five Wave-2 ceiling models.

    from prometheus.ananke.audit import ceilings as CL
    CL.ceiling(ph, env, seeds, model="lightcone")                 # H-PLANT light cone (deterministic)
    CL.ceiling(ph, env, seeds, model="lightcone", wake="exact")   # + the engine's exact WAKE mask (W2-T)
    CL.ceiling(ph, env, seeds, model="joint")                     # + async cue loss / actuator wake / FLIP
                                                                  #   teacher terms in expectation (W2-P, W2-U)
    CL.ceiling(ph, env, seeds, model="mc")                        # Monte-Carlo with loss / fanout / dup /
                                                                  #   jitter (W2-J lc2; an ESTIMATE)
    CL.ceiling(ph, env, model="epidemic")                         # global-topology fanout epidemic (W2-S)
    CL.ceilings(ph, env, seeds)                                   # every applicable model + the tightest

Every model is an UPPER bound on the accuracy ANY program can reach at the cell, under optimistic transport:
no loss / caps / collisions / energy / noise / decay unless the model says otherwise, jitter 0, any neighbour
reachable, every informed site relays at its first awake tick, the inbox latches while asleep (engine step 1
accumulates Acc_sum/Acc_cnt and clears only on an awake tick), SENSE is never latched (step 2 writes it for the
current tick only), S changes only at awake ticks and the readout is the actuator's S0 at the readout tick.
Information counts only once PROCESSED at an awake tick <= the readout tick.

Per trial, the value given the set of needed cues that can be in reach:
  RELAY / FLIP: sensor 0 (the FLIP teacher is ignored by 'lightcone': still an upper bound); HOLD: sensor ==
  actuator; XOR: both sensors (missing either gives exactly 1/2); MAJ: Bayes value of the majority of the r
  sensors in reach under flip_p (ties .5).  A cell bound is the mean over the scored trials of the mirror-pair
  lead worlds (twins share positions and wake seeds).

Kinds (what the number bounds):
  deterministic  holds for every program on THESE seeds ('lightcone'; with wake="exact" for the engine's own
                 wake draws);
  expectation    holds in expectation over the modelled randomness (iid wake with p = p16(update_p)/65536,
                 'joint'; the epidemic's mean infected count, 'epidemic');
  estimate       a Monte-Carlo expectation of an optimistic flood ('mc'); it carries sampling error and is
                 never folded into a tightest bound.

Known answers kept as tests (prometheus/ananke/audit/tests/test_ceilings.py):
  * lightcone(wake="opt") reproduces H-PLANT lc_census.json exactly (SCORE_NS, M = 64);
  * joint(terms=()) reproduces the same light cone (W2-U KA1), and joint reproduces the recorded W2-P
    (RELAY / MAJ) and W2-U (XOR / FLIP) ceilings;
  * lightcone(wake="exact") reproduces W2-T's held-set bounds, and no recorded SIGNAL exceeds it;
  * mc in the deterministic limit (loss 0, dup 0, dest all, sync, jitter 0) equals the light cone trial by
    trial (W2-J 768/768), and must fail (f = 0) when latency exceeds the readout delay;
  * epidemic reproduces W2-S epidemic_bound.json;  the closed forms .788 / .837 / .875 / .98 (W2-P KA2).

Deduplication: one transport routine (_reach) replaces four copies of H-PLANT lightcone.earliest (Dijkstra in
H-PLANT, W2-P and W2-U; vectorised Bellman-Ford in W2-T); one maj_bayes replaces W2-P maj_acc / W2-T maj_bayes.
Seeds are always explicit; MAJ inward placement and other schedule variants are passed as a prebuilt `ep`.
"""
from __future__ import annotations

import math

import numpy as np

from prometheus.ananke import envs, rng, topology

INF = 10 ** 9
NEED_FAMILIES = ("RELAY", "FLIP", "HOLD", "XOR", "MAJ")
DETERMINISTIC, EXPECTATION, ESTIMATE = "deterministic", "expectation", "estimate"


# --------------------------------------------------------------------------------------------- shared math
def maj_bayes(r: int, q: float) -> float:
    """P(correct) of the majority of r received copies, each correct w.p. 1 - q; ties -> .5; r = 0 -> .5."""
    p = 1 - q
    return sum(math.comb(r, j) * p ** j * q ** (r - j) * (1.0 if 2 * j > r else 0.5 if 2 * j == r else 0.0)
               for j in range(r + 1))


def poisson_binom(ps) -> np.ndarray:
    """Distribution of the number of successes of independent Bernoulli(ps[i])."""
    dist = np.zeros(len(ps) + 1)
    dist[0] = 1.0
    for p in ps:
        dist[1:] = dist[1:] * (1 - p) + dist[:-1] * p
        dist[0] *= (1 - p)
    return dist


def n_needed(env) -> int:
    if env.family not in NEED_FAMILIES:
        raise ValueError(f"no ceiling model for family {env.family!r}")
    return {"RELAY": 1, "FLIP": 1, "HOLD": 1, "XOR": 2, "MAJ": getattr(env, "n_maj", 0)}[env.family]


def value_table(env) -> list:
    """acc_k = per-trial ceiling given k of the needed cues in reach (k = 0..K)."""
    K = n_needed(env)
    if env.family == "MAJ":
        return [maj_bayes(k, env.flip_p) for k in range(K + 1)]
    return [0.5] * K + [1.0]


def _p_awake(ph) -> float:
    return 1.0 if ph.update_mode == "sync" else ph.p16(ph.update_p) / 65536.0


# --------------------------------------------------------------------------------------------- transport
def edge_list(ph):
    """(U, V, delay) for every directed neighbour edge, sorted by V (global: every ordered pair, hop 1)."""
    N = ph.n_sites
    nbr, dist = topology.build(ph)
    if nbr is None:
        U, V = np.nonzero(1 - np.eye(N, dtype=np.int64))
        D = np.ones_like(U)
    else:
        U = np.repeat(np.arange(N), nbr.shape[1])
        V = nbr.reshape(-1)
        D = dist.reshape(-1)
    delay = np.maximum(1, ph.lat_base + ph.lat_hop * D)
    o = np.argsort(V, kind="stable")
    return U[o], V[o], delay[o]


def wake_mask(ph, lead_seeds, T: int, mode: str) -> np.ndarray:
    """[W, T, N] bool. sync: t % update_period == 0. async: mode 'opt' = always awake (H-PLANT), mode 'exact' =
    the engine's per-site per-tick WAKE hash (rng.WAKE; W2-O verified it against engine stats['awake'])."""
    if mode not in ("opt", "exact"):
        raise ValueError(mode)
    W, N = len(lead_seeds), ph.n_sites
    if ph.update_mode == "sync":
        a = (np.arange(T) % ph.update_period == 0)
        return np.broadcast_to(a[None, :, None], (W, T, N)).copy()
    if mode == "opt":
        return np.ones((W, T, N), dtype=bool)
    import torch
    ws = torch.as_tensor(np.asarray(lead_seeds, dtype=np.int64))
    st = torch.as_tensor(np.arange(N, dtype=np.int64))
    p = ph.p16(ph.update_p)
    out = np.zeros((W, T, N), dtype=bool)
    for t in range(T):
        hw = rng.chain(rng.site_base(ws, rng.WAKE, t, st), 0)
        out[:, t] = ((hw & 0xFFFF) < p).numpy()
    return out


def next_awake_table(aw: np.ndarray) -> np.ndarray:
    """nxt[w, t, v] = smallest t' >= t with aw[w, t', v], else INF; t in [0, T] (row T = INF)."""
    W, T, N = aw.shape
    nxt = np.full((W, T + 1, N), INF, dtype=np.int64)
    for t in range(T - 1, -1, -1):
        nxt[:, t] = np.where(aw[:, t], t, nxt[:, t + 1])
    return nxt


def _reach(ph, env, seeds, wake: str = "opt", emit: str = "live", ep=None) -> dict:
    """Earliest processing tick at the actuator for every (lead world, trial, needed sensor).

    emit 'live'  : the sensor emits at its first awake tick in the cue window that carries a non-zero cue value
                   (W2-T lcwake);
    emit 'start' : at its first awake tick in the cue window, cue value ignored (H-PLANT lightcone.earliest,
                   the base the 'joint' model shifts by the sensor's wake delay).
    Returns lead [W], sens [W, K], act [W], arr_rel [W, tr, K] (tick - t0, INF if never), ro_rel [W, tr],
    scored [W, tr], ok [W, tr, K] (arr_rel <= ro_rel), T."""
    if emit not in ("live", "start"):
        raise ValueError(emit)
    if ep is None:
        ep = envs.build(ph, env, seeds)
    K = n_needed(env)
    sidx = ep.schedule.sense_idx.numpy()
    ridx = ep.schedule.read_idx.numpy()[:, 0]
    sval = ep.schedule.sense_val.numpy()
    T = sval.shape[0]
    B = len(seeds)
    lead = np.arange(0, B, 2)                      # mirror twins share positions and wake seeds
    aw = wake_mask(ph, [seeds[b] for b in lead], T, wake)
    nxt = next_awake_table(aw)
    U, V, Dl = edge_list(ph)
    Pd, tr = env.period(), env.trials
    qw, qk, qs, qt = [], [], [], []
    for wi, b in enumerate(lead):
        for k in range(tr):
            t0 = k * Pd
            ts = np.arange(t0, min(t0 + env.cue_len, T))
            for j in range(K):
                s = int(sidx[b, j])
                cand = ts[sval[ts, b, j] != 0] if emit == "live" else ts
                cand = cand[aw[wi, cand, s]]
                qw.append(wi)
                qk.append(k)
                qs.append(s)
                qt.append(int(cand[0]) if cand.size else INF)
    qw, qk, qs, qt = map(np.asarray, (qw, qk, qs, qt))
    Q, N = len(qw), ph.n_sites
    best = np.full((Q, N), INF, dtype=np.int64)
    best[np.arange(Q), qs] = qt
    seg = np.r_[0, np.flatnonzero(np.diff(V)) + 1]         # V sorted: segment starts
    Vu = V[seg]
    CH = max(1, 2_000_000 // max(1, len(U)))
    for c0 in range(0, Q, CH):
        sl = slice(c0, min(Q, c0 + CH))
        bq, wq = best[sl], qw[sl]
        for _ in range(4 * N + 8):
            arr = np.minimum(bq[:, U] + Dl[None, :], T)      # nxt row T is INF
            cand = nxt[wq[:, None], arr, V[None, :]]
            newv = np.minimum(bq[:, Vu], np.minimum.reduceat(cand, seg, axis=1))
            if np.array_equal(newv, bq[:, Vu]):
                break
            bq[:, Vu] = newv
        else:
            raise RuntimeError("transport relaxation did not converge")
        best[sl] = bq
    W = len(lead)
    act = ridx[lead]
    at_act = best[np.arange(Q), act[qw]].reshape(W, tr, K)
    t0s = (np.arange(tr) * Pd)[None, :, None]
    arr_rel = np.where(at_act >= INF, INF, at_act - t0s)
    ro_rel = ep.ro_tick[lead] - (np.arange(tr) * Pd)[None, :]
    return {"lead": lead, "sens": sidx[lead][:, :K], "act": act, "arr_rel": arr_rel, "ro_rel": ro_rel,
            "scored": ep.scored[lead].astype(bool), "ok": arr_rel <= ro_rel[:, :, None], "T": T, "ep": ep}


# --------------------------------------------------------------------------------------------- models
def lightcone(ph, env, seeds, wake: str = "opt", ep=None, per_trial: bool = False) -> dict:
    """H-PLANT light cone (wake 'opt') or its exact-wake extension (wake 'exact', W2-T). Kind deterministic."""
    R = _reach(ph, env, seeds, wake=wake, emit="live", ep=ep)
    acck = np.asarray(value_table(env))
    nr = R["ok"].sum(-1)
    val = acck[nr]                                          # [W, tr]
    sc = R["scored"]
    out = {"model": "lightcone", "wake": wake, "kind": DETERMINISTIC, "bound": float(val[sc].mean()),
           "f_all_in_reach": float(R["ok"].all(-1)[sc].mean()), "n_trials": int(sc.sum())}
    if env.family == "MAJ":
        out["bound_any"] = float((0.5 + 0.5 * R["ok"].any(-1))[sc].mean())     # W2-O's looser 'any' rule
        out["bayes_full_info"] = maj_bayes(n_needed(env), env.flip_p)
        out["mean_sensors_in_reach"] = float(nr[sc].mean())
    if per_trial:
        out["per_trial_ok"] = R["ok"]
        out["scored"] = sc
    return out


def _ps(base: int, L: int, p: float, cl: int) -> float:
    """P(sensor's first awake tick j in the cue window, with base + j <= L)."""
    return sum(p * (1 - p) ** j for j in range(cl) if base + j <= L)


def joint(ph, env, seeds, terms=("cue", "wake", "teacher"), ep=None) -> dict:
    """Light cone + async terms in expectation over iid wake (W2-P task2_timing for RELAY / MAJ, W2-U w2u_ceil
    for XOR / FLIP / RELAY; one routine, algebraically identical on their overlap).

    terms: 'cue'     a sensor senses its cue only at an awake tick of the cue window (first awake j ~ geometric);
           'wake'    the actuator must be awake at a tick in [arrival, ro]: condition on its last awake tick L
                     (sensors independent given L; a sensor that IS the actuator is exempt, optimistically);
           'teacher' FLIP: the earlier (x_j, y_j) pair needs the sensor awake in cue window j and the actuator
                     awake in teacher window j.
    sync physics: every term is deterministic (period <= window or not), so joint == lightcone there.
    Returns lc (H-PLANT model), joint, cue (cue loss alone, no transport: W2-P), and for FLIP joint_episode
    (= joint; any program, m tracked across blocks), joint_block (no cross-block tracking) and copy_block
    (copy-class ceiling, W2-L F5). Kind expectation."""
    fam = env.family
    terms = set(terms)
    if not terms <= {"cue", "wake", "teacher"}:
        raise ValueError(terms)
    R = _reach(ph, env, seeds, wake="opt", emit="start", ep=ep)
    acck = value_table(env)
    K = n_needed(env)
    sync = ph.update_mode == "sync"
    p = _p_awake(ph)
    cl, Pd = env.cue_len, env.period()

    def awake_in(t_start):
        if sync:
            per = ph.update_period
            return 1.0 if t_start + ((-t_start) % per) < t_start + cl else 0.0
        return 1 - (1 - p) ** cl if "teacher" in terms else 1.0

    pc = 1 - (1 - p) ** cl
    cue_val = float(sum(poisson_binom([pc] * K)[i] * acck[i] for i in range(K + 1)))
    lc, jt, cue, jblk, jepi, cblk = [], [], [], [], [], []
    for wi in range(len(R["lead"])):
        a = int(R["act"][wi])
        ss = [int(x) for x in R["sens"][wi]]
        for k in range(env.trials):
            if not R["scored"][wi, k]:
                continue
            ro = int(R["ro_rel"][wi, k])
            arr = [int(x) for x in R["arr_rel"][wi, k]]
            kk = sum(x <= ro for x in arr)
            lc.append(acck[kk])
            cue.append(acck[K] if sync else cue_val)
            if sync or not ({"cue", "wake"} & terms):
                v = float(acck[kk])
                pa_all = float(kk == K)
            elif "wake" in terms:
                pcue = p if "cue" in terms else 1.0
                v = (1 - p) ** (ro + 1) * acck[0]               # actuator never awake in [t0, ro]
                pa_all = 0.0
                for m in range(ro + 1):
                    L = ro - m
                    pL = p * (1 - p) ** m
                    ps = [1.0 if s == a else (_ps(base, L, pcue, cl) if pcue < 1 else float(base <= L))
                          for s, base in zip(ss, arr)]
                    d = poisson_binom(ps)
                    v += pL * float(sum(d[i] * acck[i] for i in range(K + 1)))
                    pa_all += pL * float(np.prod(ps))
            else:                                               # cue loss only, actuator always awake
                ps = [_ps(base, ro, p, cl) for base in arr]
                d = poisson_binom(ps)
                v = float(sum(d[i] * acck[i] for i in range(K + 1)))
                pa_all = float(np.prod(ps))
            if fam != "FLIP":
                jt.append(v)
                continue

            def pm(js):
                q = 1.0
                for j in js:
                    tj = j * Pd
                    q *= 1 - awake_in(tj) * awake_in(tj + env.delta + 1)
                return 1 - q
            pmb = pm(range(k - (k % env.block), k))
            pme = pm(range(0, k))
            jblk.append(0.5 + 0.5 * pa_all * pmb)
            jepi.append(0.5 + 0.5 * pa_all * pme)
            cblk.append(0.5 + 0.25 * pa_all * pmb)
    out = {"model": "joint", "kind": EXPECTATION, "terms": sorted(terms), "lc": float(np.mean(lc)),
           "cue": float(np.mean(cue)), "n_trials": len(lc)}
    if fam == "FLIP":
        out.update(joint=float(np.mean(jepi)), joint_episode=float(np.mean(jepi)),
                   joint_block=float(np.mean(jblk)), copy_block=float(np.mean(cblk)))
    else:
        out["joint"] = float(np.mean(jt))
    out["bound"] = out["joint"]
    return out


def _mc_targets(ph, nbr, dist, sites, g, mode):
    N, n = ph.n_sites, len(sites)
    if ph.topology == "global":
        rec = (sites[:, None] + 1 + g.integers(0, N - 1, size=(n, ph.fanout))) % N
        return rec, np.ones_like(rec)
    if mode == "all":
        return nbr[sites], dist[sites]
    j = g.integers(0, nbr.shape[1], size=(n, ph.fanout))
    return nbr[sites][np.arange(n)[:, None], j], dist[sites][np.arange(n)[:, None], j]


def mc_trial(ph, env, sensors, a, t0, g, nbr, dist, mode, jitter=True):
    """One Monte-Carlo replicate of one trial (W2-J lc2.reach_trial, generalised from 2 to K cue bits): async
    wake drawn per site per tick (sensors included), per-copy loss, finite fanout, dup copies, sampled jitter;
    every informed site emits at every awake tick and one packet carries every bit. -> [K] bool informed."""
    N = ph.n_sites
    K = len(sensors)
    ro = t0 + env.delta
    base = 1.0 - ph.loss
    surv_tab = np.array([(base ** d if ph.loss_per_hop else base) for d in range(ph.max_dist() + 1)])
    ticks = np.arange(t0, ro + 1)
    L = len(ticks)
    if ph.update_mode == "sync":
        awake = np.broadcast_to((ticks % ph.update_period == 0)[:, None], (L, N))
    else:
        awake = g.random((L, N)) < ph.update_p
    pend = np.zeros((K, L + 64, N), dtype=bool)
    inf = np.zeros((K, N), dtype=bool)
    for k, s in enumerate(sensors):
        for c in range(env.cue_len):
            if c < L and awake[c, s]:
                pend[k, c, s] = True
                break
    for ti in range(L):
        aw = awake[ti]
        inf |= pend[:, ti] & aw[None, :]
        pend[:, ti + 1] |= pend[:, ti] & ~aw[None, :]          # inbox accumulates while asleep
        es = np.flatnonzero(inf.any(0) & aw)
        if es.size == 0:
            continue
        rec, dd = _mc_targets(ph, nbr, dist, es, g, mode)
        sv = surv_tab[np.minimum(dd, len(surv_tab) - 1)]
        delay = np.maximum(1, ph.lat_base + ph.lat_hop * dd)
        for extra, prob in ((0, 1.0), (1, ph.dup)):
            if prob <= 0:
                continue
            ok = (g.random(rec.shape) < sv) & (g.random(rec.shape) < prob)
            jit = g.integers(0, ph.lat_jitter + 1, size=rec.shape) if (jitter and ph.lat_jitter > 0) else 0
            ta = ti + delay + extra + jit
            for b in range(K):
                carr = inf[b][es][:, None] & ok
                r_, t_ = rec[carr], ta[carr]
                keep = t_ < L
                pend[b, t_[keep], r_[keep]] = True
    return inf[:, a].copy()


def mc(ph, env, seeds, reps: int = 4, rng_seed: int = 0, jitter: bool = True, ep=None) -> dict:
    """W2-J lc2: expected-f estimate over lead worlds x scored trials x reps. Plastic-routing rows with sampled
    destinations are also run with dest 'all' (any routing table a program could write); the larger value is
    used (f_opt). Kind estimate."""
    if ep is None:
        ep = envs.build(ph, env, seeds)
    K = n_needed(env)
    acck = np.asarray(value_table(env))
    sidx = ep.schedule.sense_idx.numpy()
    ridx = ep.schedule.read_idx.numpy()[:, 0]
    nbr, dist = topology.build(ph)
    Pd = env.period()
    g = np.random.default_rng(rng_seed)
    modes = ["all" if (ph.dest_mode == "all" and ph.topology != "global") else "sample"]
    if modes[0] == "sample" and ph.plastic_route and ph.topology != "global":
        modes.append("all")
    res = {}
    for mode in modes:
        cnt, per = [], []
        for b in range(0, len(seeds), 2):
            for k in range(env.trials):
                if not ep.scored[b, k]:
                    continue
                for _ in range(reps):
                    i = mc_trial(ph, env, [int(s) for s in sidx[b][:K]], int(ridx[b]), k * Pd, g, nbr, dist, mode,
                                 jitter)
                    per.append(i)
                    cnt.append(int(i.sum()))
        per = np.asarray(per)
        res[mode] = {"f_all": float(per.all(1).mean()), "f_each": per.mean(0).tolist(),
                     "acc_ub": float(acck[np.asarray(cnt)].mean()), "n": len(cnt)}
    best = max(res, key=lambda m: res[m]["acc_ub"])
    return {"model": "mc", "kind": ESTIMATE, "modes": res, "f_opt": res[best]["f_all"],
            "bound": res[best]["acc_ub"], "reps": reps, "jitter": jitter}


def epidemic(ph, env) -> dict:
    """W2-S: global-topology fanout epidemic, in expectation. I(tau) <= I(tau-1) + F w(tau - dmin) I(tau - dmin)
    (w = awake probability at the emission tick: sync phase maximised over trials, async update_p; recipients
    process immediately). The actuator is exchangeable with every other site, so q = P(informed) <=
    (I(delta) - 1)/(N - 1), and with no cue information the best FLIP / RELAY answer is a coin:
    acc <= 1/2 + q/2. Kind expectation."""
    p = ph.to_dict() if hasattr(ph, "to_dict") else dict(ph)
    e = env.to_dict() if hasattr(env, "to_dict") else dict(env)
    if p["topology"] != "global":
        raise ValueError("the epidemic bound assumes uniform random recipients (global topology)")
    N, F = p["n_sites"], p["fanout"]
    dmin = max(1, p["lat_base"] + p["lat_hop"])
    best = 0.0
    phases = range(p["update_period"]) if p["update_mode"] == "sync" else [0]
    for ph0 in phases:
        def w(tau):
            if p["update_mode"] == "sync":
                return 1.0 if (ph0 + tau) % p["update_period"] == 0 else 0.0
            return p["update_p"]
        ts = [t for t in range(e["cue_len"]) if w(t) > 0]
        if not ts:
            continue
        I = [0.0] * (e["delta"] + 1)
        for tau in range(e["delta"] + 1):
            prev = I[tau - 1] if tau > 0 else 0.0
            if tau == ts[0]:
                prev = max(prev, 1.0)
            src = tau - dmin
            I[tau] = min(N, prev + (F * w(src) * I[src] if src >= 0 else 0.0))
        best = max(best, min(1.0, max(0.0, (I[-1] - 1) / (N - 1))))
    return {"model": "epidemic", "kind": EXPECTATION, "q_max": best, "bound": 0.5 + best / 2}


MODELS = {"lightcone": lightcone, "joint": joint, "mc": mc, "epidemic": epidemic}


def ceiling(ph, env, seeds=None, model: str = "lightcone", **opts) -> dict:
    """One ceiling model by name (see the module docstring); every result carries 'model', 'kind', 'bound'."""
    if model not in MODELS:
        raise ValueError(f"model {model!r} not in {sorted(MODELS)}")
    if model == "epidemic":
        return epidemic(ph, env)
    if seeds is None:
        raise ValueError(f"model {model!r} needs explicit world seeds")
    return MODELS[model](ph, env, seeds, **opts)


def ceilings(ph, env, seeds, mc_reps: int = 0) -> dict:
    """Every applicable model; 'tightest' = min over deterministic bounds and min over deterministic +
    expectation bounds (the MC estimate is reported, never folded in)."""
    out = {"lightcone": lightcone(ph, env, seeds, wake="opt")}
    if ph.update_mode != "sync":
        out["lightcone_exact"] = lightcone(ph, env, seeds, wake="exact")
    out["joint"] = joint(ph, env, seeds)
    if ph.topology == "global" and env.family in ("FLIP", "RELAY"):
        out["epidemic"] = epidemic(ph, env)
    if mc_reps:
        out["mc"] = mc(ph, env, seeds, reps=mc_reps)
    det = {k: v["bound"] for k, v in out.items() if v["kind"] == DETERMINISTIC}
    exp_ = {k: v["bound"] for k, v in out.items() if v["kind"] in (DETERMINISTIC, EXPECTATION)}
    out["tightest"] = {DETERMINISTIC: min(det.items(), key=lambda kv: kv[1]),
                       EXPECTATION: min(exp_.items(), key=lambda kv: kv[1])}
    return out
