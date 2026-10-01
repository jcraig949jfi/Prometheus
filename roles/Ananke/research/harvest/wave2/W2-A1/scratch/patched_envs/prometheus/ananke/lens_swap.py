"""Carrier-swap instrument, mixture census (T-INS-6 -> T-INS-7). Promoted from
roles/Ananke/research/workers/W-M/lens_ins6.py (report workers/W-M/REPORT.md)
after principal review; code unchanged except this header and two cosmetic
fixes. Use SINGLE-trial arms (Arm.trial=k) by default: EVERY-trial swaps let
cross-trial history break the mirror identity (W-M: 5/7 census-JOINT cells).

Original header: batched carrier-swap arms,
single-trial swaps, the mixture census (pattern fractions + phi + identity
check) and the two-axis twin profile. Promoted from W-I traj.py; reuses
prometheus.ananke.lens by import and never edits engine / lens code.

Why a census and not the sum. Mirror partners A, B share every exogenous
draw and have negated targets. Site swap gives A' = (site_B, chan_A),
B' = (site_A, chan_B); channel swap gives A'' = (site_A, chan_B) = B' and
B'' = A'. If no mirror-different input arrives between the swap and the
readout, out(A, chan) == out(B, site) (IDENTITY) and site_acc + chan_acc = 1
by construction. Each (pair, trial) is then one of
    S  site-follow     (sA, sB, cA, cB) = (0, 0, 1, 1)
    C  channel-follow  (1, 1, 0, 0)
    N  neither         (1, 0, 1, 0) or (0, 1, 0, 1): both chimeras give the
                       same answer, so neither carrier alone decides
(s = site-swap arm correct, c = channel-swap arm correct). Pair-level
site_acc = fC + fN/2 and chan_acc = fS + fN/2, so "both at chance" is
produced equally by a 50/50 S/C per-trial mixture and by 100% N. The census
separates them.

All interventions act between ticks; physics untouched.
"""
from __future__ import annotations

import dataclasses

import numpy as np
import torch

from prometheus.ananke import assays, envs, lens
from prometheus.ananke.engine import Controls, Schedule, World

SITE = list(lens.SITE_ARRAYS)
FLIGHT = list(lens.FLIGHT_ARRAYS)
ARMS = {
    "site_all": SITE,
    "channel_all": FLIGHT,
    "joint": SITE + FLIGHT,
    "S": ["S"],
    "inbox": ["Acc_sum", "Acc_cnt"],
    "Kp": ["Kp"],
    "E": ["E"],
    "r": ["r"],
    "w": ["w"],
    "channel_content": ["Msum"],
    "channel_count": ["Mcnt"],
}


def arm_names(ph):
    """Arms that can act in this physics (W-I traj.arm_names)."""
    a = ["site_all", "channel_all", "joint", "S", "inbox", "channel_content", "channel_count"]
    if ph.wimm or ph.mut_site > 0:
        a.append("Kp")
    if ph.rules > 1 and ph.setrule:
        a.append("r")
    if ph.plastic_route and ph.table_width() > 0:
        a.append("w")
    if ph.economy_on:
        a.append("E")
    return a


@dataclasses.dataclass(frozen=True)
class Arm:
    """label; names (arrays to swap, None = normal arm); offset (ticks after
    trial onset t0; the swap is applied AFTER tick t0+offset); trial (None =
    EVERY trial, W-I's design; k = SINGLE: only trial k is swapped and only
    trial k is scored for this arm)."""
    label: str
    names: tuple | None = None
    offset: int = 0
    trial: int | None = None


def swap_rows(w: World, names, rows: torch.Tensor):
    """Mirror-pair swap restricted to world rows `rows` (a whole block)."""
    p = rows ^ 1
    for n in names:
        if n == "w" and not w.R:
            continue
        a = getattr(w, n)
        if n in lens.FLIGHT_ARRAYS:
            a[:, rows] = a[:, p]
        else:
            a[rows] = a[p]


def tile_schedule(sch: Schedule, K: int) -> Schedule:
    return Schedule(sch.sense_idx.repeat(K, 1), sch.sense_val.repeat(1, K, 1), sch.read_idx.repeat(K, 1))


@dataclasses.dataclass
class ArmRun:
    ep: envs.Episode
    per_trial: dict      # label -> [M, trials] in {0, .5, 1}; NaN where not scored for the arm
    s0: dict             # label -> [M, trials] raw S0 readout (int64); -2**40 where not run
    trace: dict          # label -> [T, M, A] (ticks after the early stop are 0)


NOT_RUN = -(2 ** 40)


def run_arms(ph, genome, env, seeds, arms, device="cpu", ctrl=None, chunk=16, early_stop=True) -> ArmRun:
    """Run many arms batched: each arm owns a block of M = len(seeds) worlds
    (M/2 mirror pairs), swaps act only inside the block, so blocks are
    independent and each equals lens.run with the same hooks (selfcheck).
    Chunks containing only SINGLE arms stop after the latest readout they
    need (early_stop)."""
    arms = [a if isinstance(a, Arm) else Arm(a[0], None if a[1] is None else tuple(a[1]), *a[2:]) for a in arms]
    M = len(seeds)
    ep = envs.build(ph, env, seeds)
    ws1 = [seeds[m - (m % 2)] for m in range(M)]
    Pd = env.period()
    T = env.T()
    pt, s0s, trs = {}, {}, {}
    for c0 in range(0, len(arms), chunk):
        part = arms[c0:c0 + chunk]
        K = len(part)
        sch = tile_schedule(ep.schedule, K)
        g = np.repeat(genome[None], M * K, 0)
        w = World(ph, g, ws1 * K, device=device, ctrl=ctrl or Controls(), schedule=sch)
        hooks = {}
        tmax = 0
        for j, a in enumerate(part):
            if a.trial is None:
                tmax = T - 1
            else:
                tmax = max(tmax, int(ep.ro_tick[:, a.trial].max()))
            if a.names is None:
                continue
            rows = torch.arange(j * M, (j + 1) * M, device=w.dev)
            ks = range(env.trials) if a.trial is None else [a.trial]
            for k in ks:
                t = k * Pd + a.offset
                if 0 <= t < T:
                    hooks.setdefault(t, []).append((a.names, rows))
        if not early_stop:
            tmax = T - 1
        for t in range(tmax + 1):
            w.step()
            for names, rows in hooks.get(t, ()):
                swap_rows(w, names, rows)
        tr = w.trace.cpu().numpy()
        for j, a in enumerate(part):
            trj = tr[:, j * M:(j + 1) * M]
            p = envs.per_trial(ep, trj).astype(float)
            s0 = trj[ep.ro_tick, np.arange(M)[:, None], ep.ro_slot].astype(np.int64)
            ran = ep.ro_tick <= tmax
            p[~ran] = np.nan
            s0[~ran] = NOT_RUN
            if a.trial is not None:
                keep = np.zeros_like(ran)
                keep[:, a.trial] = True
                p[~keep] = np.nan
            p[~ep.scored] = np.nan
            pt[a.label], s0s[a.label], trs[a.label] = p, s0, trj
    return ArmRun(ep, pt, s0s, trs)


def selfcheck(ph, genome, env, seeds, offset, trial, device="cpu"):
    """Batched arms (EVERY and SINGLE) must be bit-identical to lens.run with
    the same hooks. Returns {label: bool}."""
    Pd = env.period()
    arms = [Arm("normal"), Arm("site_every", tuple(SITE), offset), Arm("chan_every", tuple(FLIGHT), offset),
            Arm("site_single", tuple(SITE), offset, trial), Arm("chan_single", tuple(FLIGHT), offset, trial)]
    r = run_arms(ph, genome, env, seeds, arms, device=device, early_stop=False)
    ok = {}
    for a in arms:
        if a.names is None:
            ref = lens.run(ph, genome, env, seeds, device=device)
        else:
            fn = (lambda nm: (lambda w: lens.swap(w, nm)))(list(a.names))
            ks = range(env.trials) if a.trial is None else [a.trial]
            ref = lens.run(ph, genome, env, seeds, device=device,
                           hooks={k * Pd + offset: fn for k in ks if k * Pd + offset >= 0})
        ok[a.label] = bool(np.array_equal(ref.trace, r.trace[a.label]))
    return ok


# ------------------------------------------------------------------ census
PATTERNS = ("S", "C", "N", "X", "tie")


def _phi(x, y):
    if len(x) < 2 or x.std() == 0 or y.std() == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def pair_trial_table(normal, site, chan, s0_site, s0_chan, trials=None):
    """Per (pair, trial) arrays for the eligible set: both partners normal-
    correct, both arms scored and run. Returns dict of [P, trials] arrays."""
    Mw, nt = normal.shape
    tr = np.zeros(nt, bool)
    tr[list(range(nt)) if trials is None else list(trials)] = True
    A, B = slice(0, None, 2), slice(1, None, 2)
    ok = (normal[A] == 1) & (normal[B] == 1) & tr[None]
    for x in (site, chan):
        ok &= ~np.isnan(x[A]) & ~np.isnan(x[B])
    sA, sB, cA, cB = site[A], site[B], chan[A], chan[B]
    ident_out = (sB == 1 - cA) & (sA == 1 - cB)
    ident_s0 = (s0_site[B] == s0_chan[A]) & (s0_site[A] == s0_chan[B])
    dec = np.isin(sA, (0, 1)) & np.isin(sB, (0, 1)) & np.isin(cA, (0, 1)) & np.isin(cB, (0, 1))
    pat = np.full(ok.shape, "X", dtype="<U3")
    pat[(sA == 0) & (sB == 0) & (cA == 1) & (cB == 1)] = "S"
    pat[(sA == 1) & (sB == 1) & (cA == 0) & (cB == 0)] = "C"
    pat[(sA == cA) & (sB == cB) & (sA != sB) & dec] = "N"
    pat[~dec] = "tie"
    return {"ok": ok, "pat": pat, "ident_out": ident_out, "ident_s0": ident_s0}


def _stats(tab, normal, site, chan, pairs):
    ok = tab["ok"][pairs]
    n = int(ok.sum())
    res = {"eligible": n}
    if n == 0:
        res.update({f"f{p}": None for p in PATTERNS})
        res.update(identity=None, identity_s0=None)
    else:
        pat = tab["pat"][pairs][ok]
        for p in PATTERNS:
            res[f"f{p}"] = float(np.mean(pat == p))
        res["identity"] = float(tab["ident_out"][pairs][ok].mean())
        res["identity_s0"] = float(tab["ident_s0"][pairs][ok].mean())
    # world-level phi: cells with normal correct and both arms decisive
    wi = np.stack([2 * pairs, 2 * pairs + 1], 1).ravel()
    nw, sw, cw = normal[wi], site[wi], chan[wi]
    tr_ok = tab["ok"].any(0)          # trials in the chosen set that were scored for the arms
    cell = (nw == 1) & np.isin(sw, (0, 1)) & np.isin(cw, (0, 1)) & tr_ok[None]
    x, y = 1 - sw[cell], 1 - cw[cell]
    res["phi"] = _phi(x, y)
    res["cells"] = int(cell.sum())
    res["q"] = {"11": int(((x == 1) & (y == 1)).sum()), "10": int(((x == 1) & (y == 0)).sum()),
                "01": int(((x == 0) & (y == 1)).sum()), "00": int(((x == 0) & (y == 0)).sum())}
    return res


def census(normal, site, chan, s0_site, s0_chan, trials=None, n_boot=2000, seed=0, alpha=0.01):
    """Mixture census with pair-bootstrap (resampling mirror pairs) CIs."""
    tab = pair_trial_table(normal, site, chan, s0_site, s0_chan, trials)
    P = normal.shape[0] // 2
    allp = np.arange(P)
    res = _stats(tab, normal, site, chan, allp)
    rng = np.random.default_rng(seed)
    boots = {k: [] for k in ("fS", "fC", "fN", "phi", "identity")}
    undef_phi = 0
    for _ in range(n_boot):
        b = _stats(tab, normal, site, chan, rng.integers(P, size=P))
        for k in boots:
            if b[k] is None:
                if k == "phi":
                    undef_phi += 1
                continue
            boots[k].append(b[k])
    ci = {}
    for k, v in boots.items():
        ci[k] = None if not v else (float(np.quantile(v, alpha / 2)), float(np.quantile(v, 1 - alpha / 2)))
    res["ci99"] = ci
    res["phi_boot_undefined"] = undef_phi
    ok = tab["ok"]
    sa = np.nanmean(site[:, ok.any(0)]) if ok.any() else None
    res["site_acc"] = None if sa is None or np.isnan(sa) else float(sa)
    ca = np.nanmean(chan[:, ok.any(0)]) if ok.any() else None
    res["chan_acc"] = None if ca is None or np.isnan(ca) else float(ca)
    return res


# SECONDARY census (deviation D1, LOG A6): "follow" census. The frozen
# census needs BOTH partners normal-correct; a partner that abstains (S0 = 0)
# on one cue sign makes every pair-trial ineligible (78f3b0ec). Generalised
# with signs: eligible iff the partners' normal readout signs differ (so a
# chimera's output can be attributed); an arm "follows partner" iff its
# readout sign equals the partner's normal sign, "follows own" iff it equals
# its own. With both partners correct this reduces exactly to census().
def census_follow(n_s0, site_s0, chan_s0, scored, trials=None, n_boot=2000, seed=0, alpha=0.01):
    Mw, nt = n_s0.shape
    tr = np.zeros(nt, bool)
    tr[list(range(nt)) if trials is None else list(trials)] = True
    sg = lambda x: np.sign(x)
    A, B = slice(0, None, 2), slice(1, None, 2)
    nA, nB = sg(n_s0[A]), sg(n_s0[B])
    ran = (site_s0 != NOT_RUN) & (chan_s0 != NOT_RUN)
    ok = (nA != nB) & tr[None] & scored[A] & ran[A] & ran[B]
    sA, sB, cA, cB = sg(site_s0[A]), sg(site_s0[B]), sg(chan_s0[A]), sg(chan_s0[B])
    code = lambda v, own, par: np.where(v == par, "P", np.where(v == own, "O", "?"))
    ksA, ksB, kcA, kcB = code(sA, nA, nB), code(sB, nB, nA), code(cA, nA, nB), code(cB, nB, nA)
    key = np.char.add(np.char.add(ksA, ksB), np.char.add(kcA, kcB))
    pat = np.full(ok.shape, "X", dtype="<U3")
    pat[key == "PPOO"] = "S"
    pat[key == "OOPP"] = "C"
    pat[(key == "OPOP") | (key == "POPO")] = "N"
    ident = (sB == cA) & (sA == cB)                 # sign-level (outcome) identity, as census()
    ident_raw = (site_s0[B] == chan_s0[A]) & (site_s0[A] == chan_s0[B])
    x = np.stack([ksA == "P", ksB == "P"], 1).astype(float)      # site arm follows partner
    y = np.stack([kcA == "P", kcB == "P"], 1).astype(float)      # chan arm follows partner

    def st(pairs):
        o = ok[pairs]
        n = int(o.sum())
        r = {"eligible": n}
        if n == 0:
            r.update({f"f{q}": None for q in ("S", "C", "N", "X")}, identity=None, identity_s0=None, phi=None)
            return r
        pt = pat[pairs][o]
        for q in ("S", "C", "N", "X"):
            r[f"f{q}"] = float(np.mean(pt == q))
        r["ftie"] = 0.0
        r["identity"] = float(ident[pairs][o].mean())
        r["identity_s0"] = float(ident_raw[pairs][o].mean())
        oo = np.stack([o, o], 1)
        r["phi"] = _phi(x[pairs][oo], y[pairs][oo])
        return r
    P = Mw // 2
    res = st(np.arange(P))
    rng = np.random.default_rng(seed)
    boots = {k: [] for k in ("fS", "fC", "fN", "phi", "identity")}
    for _ in range(n_boot):
        b = st(rng.integers(P, size=P))
        for k in boots:
            if b.get(k) is not None:
                boots[k].append(b[k])
    res["ci99"] = {k: (None if not v else (float(np.quantile(v, alpha / 2)), float(np.quantile(v, 1 - alpha / 2))))
                   for k, v in boots.items()}
    return res


# FROZEN decision rule (PLAN.md s1 iii)
MIN_ELIGIBLE = 20
MIN_IDENTITY = 0.90


def classify(c: dict) -> str:
    if c["eligible"] < MIN_ELIGIBLE:
        return "UNDEFINED"
    if c["identity"] < MIN_IDENTITY:
        return "IDENTITY-BROKEN"
    fS, fC, fN = c["fS"], c["fC"], c["fN"]
    if fS >= 0.80:
        return "SITE"
    if fC >= 0.80:
        return "CHANNEL"
    phi_hi = c["ci99"]["phi"][1] if c["ci99"].get("phi") else None
    if fS >= 0.15 and fC >= 0.15 and fS + fC >= 0.70 and phi_hi is not None and phi_hi < -0.30:
        return "MIXTURE"
    if fN >= 0.50:
        return "NEITHER"
    return "UNRESOLVED"


def mixture_scan(ph, genome, env, seeds, offsets, mode, trials, device="cpu", chunk=16, n_boot=2000, raw=None):
    """Census + class per offset for the site_all / channel_all pair of arms.
    mode 'every': W-I design, swap in every trial, census over `trials`.
    mode 'single': one block per (trial, offset, arm), census pools `trials`."""
    arms = [Arm("normal")]
    for o in offsets:
        if mode == "every":
            arms += [Arm(f"site@{o}", tuple(SITE), o), Arm(f"chan@{o}", tuple(FLIGHT), o)]
        else:
            for k in trials:
                arms += [Arm(f"site@{o}#{k}", tuple(SITE), o, k), Arm(f"chan@{o}#{k}", tuple(FLIGHT), o, k)]
    # normal arm runs full length; single arms sorted by trial so early stop bites
    head, rest = arms[:1], arms[1:]
    rest.sort(key=lambda a: (a.trial if a.trial is not None else -1))
    r = run_arms(ph, genome, env, seeds, head + rest, device=device, chunk=chunk)
    normal = r.per_trial["normal"]
    out = {}
    for o in offsets:
        if mode == "every":
            site, chan = r.per_trial[f"site@{o}"], r.per_trial[f"chan@{o}"]
            ss, sc = r.s0[f"site@{o}"], r.s0[f"chan@{o}"]
        else:
            site = np.full_like(normal, np.nan)
            chan = np.full_like(normal, np.nan)
            ss = np.full(normal.shape, NOT_RUN, np.int64)
            sc = ss.copy()
            for k in trials:
                site[:, k] = r.per_trial[f"site@{o}#{k}"][:, k]
                chan[:, k] = r.per_trial[f"chan@{o}#{k}"][:, k]
                ss[:, k] = r.s0[f"site@{o}#{k}"][:, k]
                sc[:, k] = r.s0[f"chan@{o}#{k}"][:, k]
        c = census(normal, site, chan, ss, sc, trials, n_boot=n_boot)
        c["class"] = classify(c)
        f = census_follow(r.s0["normal"], ss, sc, r.ep.scored, trials, n_boot=n_boot)
        f["class"] = classify(f)
        c["follow"] = f
        if raw is not None:
            raw[o] = {"site": site, "chan": chan, "s0_site": ss, "s0_chan": sc}
        out[o] = c
    if raw is not None:
        raw["normal"] = {"per_trial": normal, "s0": r.s0["normal"], "scored": r.ep.scored, "y": r.ep.y}
    return {"normal": lens.ci(np.nanmean(np.where(np.isnan(normal[:, list(trials)]), np.nan,
                                                  normal[:, list(trials)]), 1).reshape(-1, 2).mean(-1)),
            "offsets": out}


# ------------------------------------------------------------------ axis (a)
def twin_profile(ph, genome, env, ns, trials=(3, 5, 7), M=64, device="cpu"):
    """Physical axis (W-I traj.twin_profile, semantics unchanged). Twins:
    world 2p+1 = world 2p with ONLY trial k's cue negated. Per offset o in
    [-1, ro-t0] and twin trial: fraction of twin pairs in which each state
    class differs (S, inbox, Kp, E, r, w, flight count/payload, fire, emitted
    payload/channel). Returns {'per_trial', 'avg'}."""
    seeds = assays.world_seeds(ns, M)
    ep0 = envs.build(ph, env, seeds)
    K = len(trials)
    Pd = env.period()
    sv = ep0.schedule.sense_val.clone().repeat(1, K, 1)
    sidx = ep0.schedule.sense_idx.clone().repeat(K, 1)
    ridx = ep0.schedule.read_idx.clone().repeat(K, 1)
    for j, k in enumerate(trials):
        tk0 = k * Pd
        for b in range(1, M, 2):
            B, A = j * M + b, j * M + b - 1
            sv[:, B] = sv[:, A]
            sv[tk0:tk0 + env.cue_len, B] = -sv[tk0:tk0 + env.cue_len, A]
            sidx[B], ridx[B] = sidx[A], ridx[A]
    ws = [seeds[m - (m % 2)] for m in range(M)] * K
    w = World(ph, np.repeat(genome[None], M * K, 0), ws, device=device, schedule=Schedule(sidx, sv, ridx))
    E0, E1 = slice(0, None, 2), slice(1, None, 2)
    tmin = min(k * Pd - 1 for k in trials)
    tmax = max(int(ep0.ro_tick[0, k]) for k in trials)
    rec = {j: {} for j in range(K)}

    def d_site(x):
        dd = x[E0] != x[E1]
        return dd.flatten(2).any(-1) if dd.dim() > 2 else dd
    for t in range(tmax + 1):
        w.step()
        if t < tmin:
            continue
        st = {"S": d_site(w.S), "inbox": d_site(w.Acc_sum) | d_site(w.Acc_cnt), "Kp": d_site(w.Kp),
              "E": d_site(w.E), "r": d_site(w.r)}
        st["w"] = d_site(w.w) if w.R else torch.zeros_like(st["S"])
        mc = w.Mcnt[:, E0] != w.Mcnt[:, E1]
        ms = (w.Msum[:, E0] != w.Msum[:, E1]).any(-1)
        st["fl_cnt"] = mc.any(0).any(-1)
        st["fl_pay"] = (ms & ~mc).any(0).any(-1)
        e = w.last_emit
        st["fire"] = e[E0] != e[E1]
        both = e[E0] & e[E1]
        st["emit_pay"] = both & (w.last_pay[E0] != w.last_pay[E1]).any(-1)
        st["emit_chan"] = both & (w.last_chan[E0] != w.last_chan[E1])
        for j, k in enumerate(trials):
            t0 = k * Pd
            ro = int(ep0.ro_tick[0, k])
            if not (t0 - 1 <= t <= ro):
                continue
            sl = slice(j * M // 2, (j + 1) * M // 2)
            rec[j][t - t0] = {key: float(v[sl].any(-1).float().mean()) for key, v in st.items()}
    all_o = sorted(set().union(*[set(v) for v in rec.values()]))
    keys = next(iter(rec[j][o] for j in rec for o in rec[j]))
    avg = {o: {key: float(np.mean([rec[j][o][key] for j in rec if o in rec[j]]))
               for key in keys} for o in all_o}
    return {"per_trial": {str(trials[j]): rec[j] for j in rec}, "avg": avg}


# ------------------------------------------------------------------ handoff
def handoff(offsets: dict, ro_off: int) -> dict:
    """Channel -> site handoff summary of a mixture_scan()['offsets'] dict.
    channel-dominant: class CHANNEL or fC >= 0.60. final SITE run: the
    longest suffix of offsets (ending at ro_off-1) that are all SITE.
    Frozen KA7 rule (PLAN.md s2): (a) a channel-dominant offset in [2, 7];
    (b) every offset in [ro_off-4, ro_off-1] is SITE; (c) last channel-
    dominant offset < first offset of the final SITE run; (d) that first
    offset lies at lag -8..-4 (o in [ro_off-8, ro_off-4])."""
    get = lambda o: offsets[o] if o in offsets else offsets[str(o)]
    # only offsets before the readout exist for the rule ("ending at ro_off-1")
    os_ = sorted(o for o in (int(x) for x in offsets) if o < ro_off)
    chan = [o for o in os_ if get(o)["class"] == "CHANNEL" or (get(o)["fC"] or 0) >= 0.60]
    run_start = None
    if os_ and os_[-1] == ro_off - 1:              # the final SITE run must END at ro_off-1
        for o in reversed(os_):
            if get(o)["class"] != "SITE":
                break
            run_start = o
    a = any(2 <= o <= 7 for o in chan)
    # (b) needs every offset in [ro_off-4, ro_off-1] MEASURED and SITE; an
    # unmeasured offset is not a pass (was vacuously True)
    b = all(o in os_ and get(o)["class"] == "SITE" for o in range(ro_off - 4, ro_off))
    c = bool(chan) and run_start is not None and max(chan) < run_start
    d = run_start is not None and ro_off - 8 <= run_start <= ro_off - 4
    return {"channel_offsets": chan, "site_run_start": run_start, "a": a, "b": b, "c": c, "d": d,
            "pass": bool(a and b and c and d)}
