"""cw01-e07 - computational weather / brain damage: the world, the organism, the damage.

TASK. A lifetime of L episodes. A hidden theta in U[-R, R]^d is drawn once per lifetime.
Each episode presents o_t = Q_r theta + eps_t and a query q_t; the organism emits y_t and
scores max(0, 1 - |y_t - theta[q_t]|). Nearly all useful computation above the floor
lives in PERSISTENT STATE, which is what the damage family deletes.

ORGANISM. K persistent memory cells M, reset at lifetime start:
    M_t = clip(A M_{t-1} + B o_t + C e_{q_t} + b)
    y_t = clip(W[q_t] . M_t)
The layout of computation across the K cells is evolution's choice; nothing here reads
or prices it.

DAMAGE (one family, frozen). Between episodes, select k = max(1, round(f K)) distinct
cell indices uniformly at random and zero them. The selector's inputs are (K, k, rng)
ONLY: it never sees state values, the genome, activity or importance. The SHAM uses the
same selector and draws and writes each selected cell back to itself, so a sham
lifetime is bit-identical to its intact twin.

THREE MEASUREMENT LAYERS. TASK = intact score above floor. ROBUSTNESS = damaged score
above floor as a fraction of the same organism's intact score above floor on the same
episodes (ratio of means, window by window). ORGANISATION is recorded, never scored.

NEUTRALITY IN THREE LAYERS (e06 doctrine). Reward never mentions damage. The task
stream is keyed on (attempt, replicate, kind, index) and is identical across arms; the
weather stream is a separate seed component so consuming it cannot shift task draws
(CW01-D019). Bookkeeping (representative selection, test protocol) is one rule for all
arms.

CW01-D046: roots discovered by marker via lib/repopath, never by counting parents.
"""
from __future__ import annotations

import itertools
import pathlib
import sys
import warnings

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent


def _bootstrap_lib():
    """The one hand-written walk-up: find lib/ by its MARKER, then let repopath work."""
    for cand in [HERE] + list(HERE.parents):
        if (cand / "lib" / "repopath.py").exists():
            sys.path.insert(0, str(cand / "lib"))
            return cand / "lib"
    raise RuntimeError("cannot locate lib/repopath.py walking up from %s" % HERE)


_bootstrap_lib()
import repopath as RP          # noqa: E402
import seeds as S              # noqa: E402

CAMPAIGN = RP.find_campaign_root(HERE)
REPO = RP.find_root(HERE)

ARMS = ("STATIC", "WEATHER", "SHAMWEATHER")
WEATHER_ARMS = ("WEATHER", "SHAMWEATHER")


# ----------------------------------------------------------------- genome layout

def recurrence(cfg):
    """'full' (A is KxK) or 'diagonal' (A is a per-cell decay a_i, clipped to [-1, 1])."""
    return cfg.get("organism", {}).get("recurrence", "full")


def genome_layout(cfg):
    K, D = cfg["world"]["K"], cfg["world"]["d"]
    a_shape = (K,) if recurrence(cfg) == "diagonal" else (K, K)
    spec = [("A", a_shape), ("B", (K, D)), ("C", (K, D)), ("b", (K,)), ("W", (D, K))]
    out, off = {}, 0
    for name, shape in spec:
        n = int(np.prod(shape))
        out[name] = (off, off + n, shape)
        off += n
    return out, off


def genome_size(cfg):
    return genome_layout(cfg)[1]


def unpack(pop, cfg):
    """Views into a (N, G) population: A (N,K,K), B (N,K,D), C (N,K,D), b (N,K), W (N,D,K)."""
    lay, _ = genome_layout(cfg)
    N = pop.shape[0]
    return {name: pop[:, a:b].reshape((N,) + shape) for name, (a, b, shape) in lay.items()}


# ----------------------------------------------------------------- latent world

def attempt_Q(cfg, aid, r):
    """The replicate-level latent fact: a random orthogonal dxd, drawn ONCE per world."""
    D = cfg["world"]["d"]
    rng = S.rng(aid, "world|%s" % r)
    G = rng.normal(size=(D, D))
    Q, Rm = np.linalg.qr(G)
    return Q * np.sign(np.diag(Rm))[None, :]


def task_stream(cfg, aid, r, kind, index, n, Q):
    """n lifetimes: theta (n,d), obs (n,L,d), q (n,L). Keyed on (attempt, r, kind, index)."""
    w = cfg["world"]
    D, L, R, sig = w["d"], w["L"], w["theta_range"], w["obs_sigma"]
    rng = S.rng(aid, "task|%s|%s" % (r, kind), index)
    theta = rng.uniform(-R, R, size=(n, D))
    eps = rng.normal(0.0, sig, size=(n, L, D))
    q = rng.integers(0, D, size=(n, L))
    obs = (theta @ Q.T)[:, None, :] + eps         # obs[l, t] = Q theta[l] + eps[l, t]
    return {"theta": theta, "obs": obs, "q": q, "n": n}


def floor_scores(stream):
    """Score of the constant-zero organism on the same episodes: (n, L)."""
    n = stream["n"]
    tq = stream["theta"][np.arange(n)[:, None], stream["q"]]
    return np.maximum(0.0, 1.0 - np.abs(tq))


# ----------------------------------------------------------------- operators

def select_cells(K, k, rng, M=None):
    """PRODUCTION selector. Inputs (K, k, rng) only; M is accepted and IGNORED so that the
    blindness test can hand every selector the same call signature."""
    if k <= 0:
        return np.zeros(0, dtype=int)
    return np.sort(rng.choice(K, size=int(k), replace=False))


def severity_k(f, K):
    return max(1, int(round(f * K)))


def damage_op(M, l, idx):
    """Transient deletion: zero the selected cells of lifetime l for every organism."""
    if len(idx):
        M[:, l, idx] = 0.0


def sham_op(M, l, idx):
    """Cost-matched sham: same selection, identity write."""
    if len(idx):
        M[:, l, idx] = M[:, l, idx]


PRODUCTION_OPS = {"select": select_cells, "damage": damage_op, "sham": sham_op,
                  "lethal": False}


# ----------------------------------------------------------------- schedules
# A schedule is {episode t: [(lifetime l, idx array), ...]}, applied BEFORE episode t.

def train_schedule(cfg, rng, n, select):
    d, K = cfg["damage"], cfg["world"]["K"]
    lo, hi = d["train_episode_range"]
    ev_lo, ev_hi = d["train_events"]
    sched = {}
    for l in range(n):
        n_ev = int(rng.integers(ev_lo, ev_hi + 1))
        ts = rng.choice(np.arange(lo, hi + 1), size=n_ev, replace=False)
        for t in sorted(int(x) for x in ts):
            f = float(rng.choice(d["sweep"]))
            idx = select(K, severity_k(f, K), rng)
            sched.setdefault(t, []).append((l, idx))
    return sched


def event_schedule(cfg, rng, n, f, episodes, select):
    K = cfg["world"]["K"]
    sched = {}
    for l in range(n):
        for t in episodes:
            idx = select(K, severity_k(f, K), rng)
            sched.setdefault(int(t), []).append((l, idx))
    return sched


def lethal_schedule(cfg, n):
    """FIXTURE ONLY (F3): every cell, every episode from T_d on."""
    d, K, L = cfg["damage"], cfg["world"]["K"], cfg["world"]["L"]
    allc = np.arange(K)
    return {t: [(l, allc) for l in range(n)] for t in range(d["T_d"], L)}


# ----------------------------------------------------------------- lifetime runner

def run_lifetimes(pop, cfg, stream, schedule=None, op=None, lesion=False):
    """Scores (N, n, L) for a population over n lifetimes, vectorised over both.

    schedule events are applied BEFORE the episode's update (between episodes). With
    lesion=True they are applied AFTER the update as well - the F3 fixture path only.
    """
    w = cfg["world"]
    K, L, clip = w["K"], w["L"], w["clip"]
    g = unpack(pop, cfg)
    diag = recurrence(cfg) == "diagonal"
    if diag:
        a = np.clip(g["A"], -1.0, 1.0)[:, None, :]   # (N,1,K) per-cell decay
    else:
        At = g["A"].transpose(0, 2, 1)            # (N,K,K)
    Bt = g["B"].transpose(0, 2, 1)                # (N,D,K)
    C, b, W = g["C"], g["b"], g["W"]
    theta, obs, q, n = stream["theta"], stream["obs"], stream["q"], stream["n"]
    N = pop.shape[0]
    M = np.zeros((N, n, K))
    scores = np.zeros((N, n, L))
    ar = np.arange(n)
    for t in range(L):
        if schedule is not None and t in schedule:
            for l, idx in schedule[t]:
                op(M, l, idx)
        o = obs[:, t, :]                          # (n,D)
        qt = q[:, t]                              # (n,)
        rec = (a * M) if diag else (M @ At)
        pre = rec + (o[None] @ Bt) + C[:, :, qt].transpose(0, 2, 1) + b[:, None, :]
        M = np.clip(pre, -clip, clip)
        if lesion and schedule is not None and t in schedule:
            for l, idx in schedule[t]:
                op(M, l, idx)
        Wq = W[:, qt, :]                          # (N,n,K)
        y = np.clip((Wq * M).sum(-1), -clip, clip)
        tq = theta[ar, qt]                        # (n,)
        scores[:, :, t] = np.maximum(0.0, 1.0 - np.abs(y - tq[None, :]))
    return scores


# ----------------------------------------------------------------- robustness

def robustness(s_int, s_dmg, F, cfg, lifetimes=None):
    """Per-organism retention/recovery, as RATIOS OF MEANS window by window.

    r(j) = (mean s_dmg(j) - mean F(j)) / (mean s_int(j) - mean F(j)), clipped [-1, 2].
    AURC = mean_j r(j); rho0 = r(0); rhoH = r(last); T_rec = first j with r >= threshold.
    """
    d, tcfg = cfg["damage"], cfg["test"]
    T_d, H, wdt = d["T_d"], d["H"], d["window"]
    nwin = H // wdt
    if lifetimes is not None:
        s_int, s_dmg, F = s_int[:, lifetimes], s_dmg[:, lifetimes], F[lifetimes]
    post = slice(T_d, T_d + H)
    Fp = float(F[:, post].mean())
    I = s_int[:, :, post].mean(axis=(1, 2))
    useful = (I - Fp) >= tcfg["useful_delta"]
    N = s_int.shape[0]
    r = np.full((N, nwin), np.nan)
    for j in range(nwin):
        sl = slice(T_d + j * wdt, T_d + (j + 1) * wdt)
        fj = float(F[:, sl].mean())
        num = s_dmg[:, :, sl].mean(axis=(1, 2)) - fj
        den = s_int[:, :, sl].mean(axis=(1, 2)) - fj
        ok = den > 1e-6
        r[ok, j] = np.clip(num[ok] / den[ok], -1.0, 2.0)
    with np.errstate(all="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)    # all-nan rows -> nan AURC, by design
        aurc = np.nanmean(r, axis=1)
    thr = tcfg["recover_threshold"]
    t_rec = np.full(N, nwin, dtype=int)
    for i in range(N):
        hit = np.where(r[i] >= thr)[0]
        if len(hit):
            t_rec[i] = int(hit[0])
    return {"I": I, "F_post": Fp, "useful": useful, "r": r, "AURC": aurc,
            "rho0": r[:, 0], "rhoH": r[:, -1], "T_rec": t_rec, "nwin": nwin}


# ----------------------------------------------------------------- evolution

def next_generation(pop, fit, rng, ev):
    N = pop.shape[0]
    order = np.argsort(-fit)
    elites = pop[order[:ev["elite"]]]
    n_child = N - ev["elite"]
    cand = rng.integers(0, N, size=(n_child, ev["tournament"]))
    winners = cand[np.arange(n_child), np.argmax(fit[cand], axis=1)]
    children = pop[winners].copy()
    mask = rng.random(children.shape) < ev["mut_prob"]
    children += mask * rng.normal(0.0, ev["mut_sigma"], size=children.shape)
    return np.concatenate([elites, children], axis=0)


def evolve(cfg, aid, r, arm, lineage, Q, generations=None, n_org=None,
           seed_component="evo", stream_kind="train", ops=PRODUCTION_OPS):
    """One lineage. Arms differ ONLY in the between-episode operator during evaluation."""
    if arm not in ARMS:
        raise ValueError("unknown arm %r" % arm)
    ev = cfg["evolution"]
    G = generations or ev["generations"]
    N = n_org or ev["n_org"]
    nl = ev["lifetimes_per_eval"]
    rng = S.rng(aid, "%s|%s|%s|%d" % (seed_component, r, arm, lineage))
    pop = rng.normal(0.0, ev["init_sigma"], size=(N, genome_size(cfg)))
    hist = []
    fit = None
    for g in range(G):
        stream = task_stream(cfg, aid, r, stream_kind, g, nl, Q)
        schedule, op = None, None
        if arm in WEATHER_ARMS:
            wr = S.rng(aid, "weather|%s|%s" % (r, stream_kind), g)
            schedule = train_schedule(cfg, wr, nl, ops["select"])
            op = ops["damage"] if arm == "WEATHER" else ops["sham"]
        scores = run_lifetimes(pop, cfg, stream, schedule, op)
        fit = scores.mean(axis=(1, 2))
        hist.append({"gen": g, "mean": float(fit.mean()), "max": float(fit.max()),
                     "min": float(fit.min()), "sd": float(fit.std())})
        if g == G - 1:
            break
        pop = next_generation(pop, fit, rng, ev)
    return {"pop": pop, "fit": fit, "history": hist, "arm": arm, "lineage": lineage}


# ----------------------------------------------------------------- representatives + test

def intact_score(cfg, aid, r, pop, Q, kind="select", n=None):
    stream = task_stream(cfg, aid, r, kind, 0, n or cfg["test"]["n_select"], Q)
    return run_lifetimes(pop, cfg, stream).mean(axis=(1, 2))


def select_representatives(cfg, aid, r, pop, Q, top_k=None):
    """Top-k by INTACT score on the selection stream. One rule for every arm."""
    s = intact_score(cfg, aid, r, pop, Q)
    idx = np.argsort(-s)[:(top_k or cfg["test"]["top_k"])]
    return pop[idx], s[idx]


def test_protocol(cfg, aid, r, reps, Q, ops=PRODUCTION_OPS, conditions=None):
    """The SAME protocol for every organism of every arm.

    Returns intact I, the sham-vs-intact maximum deviation, and per-condition robustness
    on all lifetimes plus even/odd halves (for retest noise).
    """
    tcfg, d = cfg["test"], cfg["damage"]
    n = tcfg["n_test"]
    stream = task_stream(cfg, aid, r, "test", 0, n, Q)
    F = floor_scores(stream)
    s_int = run_lifetimes(reps, cfg, stream)
    sched_p = event_schedule(cfg, S.rng(aid, "testweather|%s|primary" % r), n,
                             d["primary"], [d["T_d"]], ops["select"])
    s_sham = run_lifetimes(reps, cfg, stream, sched_p, ops["sham"])
    even, odd = np.arange(0, n, 2), np.arange(1, n, 2)
    out = {"sham_max_abs_diff": np.abs(s_sham - s_int).max(axis=(1, 2)),
           "conditions": {}}
    for cond in (conditions or d["test_conditions"]):
        if ops.get("lethal"):
            sched, lesion = lethal_schedule(cfg, n), True
        else:
            sched = event_schedule(cfg, S.rng(aid, "testweather|%s|%s" % (r, cond["name"])), n,
                                   cond["f"], cond["episodes"], ops["select"])
            lesion = False
        s_d = run_lifetimes(reps, cfg, stream, sched, ops["damage"], lesion=lesion)
        rb = robustness(s_int, s_d, F, cfg)
        rb_e = robustness(s_int, s_d, F, cfg, lifetimes=even)
        rb_o = robustness(s_int, s_d, F, cfg, lifetimes=odd)
        out["conditions"][cond["name"]] = {
            "f": cond["f"], "episodes": list(cond["episodes"]), "role": cond["role"],
            "I": rb["I"], "F_post": rb["F_post"], "useful": rb["useful"], "r": rb["r"],
            "AURC": rb["AURC"], "rho0": rb["rho0"], "rhoH": rb["rhoH"], "T_rec": rb["T_rec"],
            "AURC_even": rb_e["AURC"], "AURC_odd": rb_o["AURC"]}
    prim = out["conditions"]["primary"] if "primary" in out["conditions"] else \
        next(iter(out["conditions"].values()))
    out["I"], out["F_post"], out["useful"] = prim["I"], prim["F_post"], prim["useful"]
    return out


# ----------------------------------------------------------------- statistics

def separability(I, aurc, aurc_even, aurc_odd, cfg):
    """P4. Conditional variance of AURC given ability, against retest noise."""
    gc = cfg["gate"]
    order = np.argsort(I)
    I_s, a_s = I[order], aurc[order]
    diffs = []
    for i in range(len(I_s) - 1):
        if abs(I_s[i + 1] - I_s[i]) <= gc["p4_pair_tol"] and np.isfinite(a_s[i]) and np.isfinite(a_s[i + 1]):
            diffs.append((a_s[i] - a_s[i + 1]) ** 2)
    n_pairs = len(diffs)
    fin = np.isfinite(aurc_even) & np.isfinite(aurc_odd)
    v_noise = float(np.mean((aurc_even[fin] - aurc_odd[fin]) ** 2) / 4.0) if fin.any() else float("nan")
    v_cond = float(np.mean(diffs) / 2.0) if n_pairs else float("nan")
    ratio = (v_cond / v_noise) if (n_pairs and v_noise > 0) else float("nan")
    if n_pairs < gc["p4_min_pairs"]:
        outcome = "NOT_VERIFIED"
    else:
        outcome = "PASS" if ratio >= gc["p4_ratio_min"] else "FAIL"
    return {"outcome": outcome, "n_pairs": n_pairs, "v_cond": v_cond, "v_noise": v_noise,
            "ratio": ratio, "ratio_min": gc["p4_ratio_min"], "n_orgs": int(len(I))}


def _fit_c(y, I, mask_t):
    X = np.column_stack([np.ones_like(y), I, mask_t.astype(float)])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    return beta


def ancova_contrast(A_s, I_s, A_t, I_t):
    """c in AURC_l = a + b I_l + c [treated], with the EXACT relabelling null (control A)."""
    y = np.concatenate([A_s, A_t]).astype(float)
    I = np.concatenate([I_s, I_t]).astype(float)
    n_s, n_t = len(A_s), len(A_t)
    n = n_s + n_t
    labels = np.zeros(n, dtype=bool)
    labels[n_s:] = True
    beta = _fit_c(y, I, labels)
    null = []
    for comb in itertools.combinations(range(n), n_t):
        m = np.zeros(n, dtype=bool)
        m[list(comb)] = True
        null.append(_fit_c(y, I, m)[2])
    null = np.array(null)
    p05, p95 = float(np.percentile(null, 5)), float(np.percentile(null, 95))
    c = float(beta[2])
    return {"c": c, "a": float(beta[0]), "b": float(beta[1]), "p05": p05, "p95": p95,
            "n_null": int(len(null)), "n_s": n_s, "n_t": n_t,
            "clears_positive": bool(c > p95), "clears_negative": bool(c < p05)}


def mean_contrast(x_s, x_t):
    """Difference of means with the same exact relabelling null."""
    x = np.concatenate([x_s, x_t]).astype(float)
    n_s, n_t = len(x_s), len(x_t)
    n = n_s + n_t
    d = float(np.mean(x_t) - np.mean(x_s))
    null = []
    for comb in itertools.combinations(range(n), n_t):
        m = np.zeros(n, dtype=bool)
        m[list(comb)] = True
        null.append(float(x[m].mean() - x[~m].mean()))
    null = np.array(null)
    p05, p95 = float(np.percentile(null, 5)), float(np.percentile(null, 95))
    return {"delta": d, "p05": p05, "p95": p95, "n_null": int(len(null)),
            "clears_positive": bool(d > p95), "clears_negative": bool(d < p05)}


def overlap(I_s, I_t, k_min):
    lo_s, hi_s = float(np.min(I_s)), float(np.max(I_s))
    lo_t, hi_t = float(np.min(I_t)), float(np.max(I_t))
    t_in = int(np.sum((I_t >= lo_s) & (I_t <= hi_s)))
    s_in = int(np.sum((I_s >= lo_t) & (I_s <= hi_t)))
    return {"treated_inside_static_range": t_in, "static_inside_treated_range": s_in,
            "required": k_min, "ok": bool(t_in >= k_min and s_in >= k_min),
            "static_range": [lo_s, hi_s], "treated_range": [lo_t, hi_t]}


# ----------------------------------------------------------------- hand-built probes

def probe_genomes(cfg, Q):
    """Best cases, allowed to know Q. ACCUMULATOR is competent and state-dependent;
    STATELESS is competent-ish and state-free; ZERO is incompetent."""
    K, D = cfg["world"]["K"], cfg["world"]["d"]
    lay, G = genome_layout(cfg)

    def build(A=None, B=None, W=None):
        g = np.zeros(G)
        v = unpack(g[None], cfg)
        if A is not None:
            if recurrence(cfg) == "diagonal":
                v["A"][0][:D] = np.diag(A)
            else:
                v["A"][0][:D, :D] = A
        if B is not None:
            v["B"][0][:D, :] = B
        if W is not None:
            for qq in range(D):
                v["W"][0][qq, qq] = W
        return g

    return {"ACCUMULATOR": build(A=0.9 * np.eye(D), B=0.1 * Q.T, W=1.0),
            "STATELESS": build(A=np.zeros((D, D)), B=Q.T, W=1.0),
            "ZERO": build()}


def gain_family(cfg, Q):
    """FIXTURE F4: ACCUMULATOR copies with readout gain g in [lo, hi]. Damage response is a
    deterministic function of intact ability BY CONSTRUCTION; P4 must refuse it."""
    gc = cfg["gate"]
    lo, hi = gc["gain_family_range"]
    base = probe_genomes(cfg, Q)["ACCUMULATOR"]
    D = cfg["world"]["d"]
    fam = []
    for gval in np.linspace(lo, hi, gc["gain_family_n"]):
        g = base.copy()
        v = unpack(g[None], cfg)
        for qq in range(D):
            v["W"][0][qq, qq] = gval
        fam.append(g)
    return np.array(fam)


# ----------------------------------------------------------------- organisation record

def organisation(pop, cfg):
    """Descriptive only. Never a criterion."""
    v = unpack(pop, cfg)
    K = cfg["world"]["K"]
    if recurrence(cfg) == "diagonal":
        eig = np.max(np.abs(np.clip(v["A"], -1.0, 1.0)), axis=1)
    else:
        eig = np.array([np.max(np.abs(np.linalg.eigvals(v["A"][i]))) for i in range(pop.shape[0])])
    w_abs = np.abs(v["W"])                        # (N,D,K)
    w_norm = w_abs / np.maximum(w_abs.sum(-1, keepdims=True), 1e-12)
    ent = -(w_norm * np.log(np.maximum(w_norm, 1e-12))).sum(-1)      # per query
    n_eff = np.exp(ent).mean(-1)                  # effective cells read per query
    b_abs = np.abs(v["B"]).sum(-1)                # (N,K) input drive per cell
    cells_driven = (b_abs > 0.05).sum(-1)
    return {"spectral_radius_A": eig, "effective_cells_read": n_eff,
            "cells_driven_by_input": cells_driven}
