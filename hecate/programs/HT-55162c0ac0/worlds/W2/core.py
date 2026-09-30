"""HT-55162c0ac0 / W2 shared core: map, UPOs, LS controller fit, simulator, criterion.
See NOTES.md for every reading (A1..A9)."""
import os
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np

R = 3.9
DELTA = 0.02
NTRAIN = 20000
TOL = 1e-3
RUN = 200
NSTEPS = 5000
NTRIALS = 50
CS = list(range(1, 9))
PS = list(range(1, 9))
POS_C = 16
POS_PS = [1, 2, 3, 4]
EPS_FIT = 0.01
BURN = 100
CHEAT_START = 100
SEEDS = [0, 1, 2, 3, 4]
ARM_CODE = {"POSITIVE_CONTROL": 1, "CHEAT": 2, "NULL_TWIN": 3, "TREATMENT": 4, "CONTROL": 5}
PARAMS = dict(R=R, DELTA=DELTA, NTRAIN=NTRAIN, TOL=TOL, RUN=RUN, NSTEPS=NSTEPS,
              NTRIALS=NTRIALS, EPS_FIT=EPS_FIT, BURN=BURN, CHEAT_START=CHEAT_START,
              POS_C=POS_C)


def fmap(x, u=0.0):
    return (R + u) * x * (1.0 - x)


def _fp(x, n):
    for _ in range(n):
        x = fmap(x)
    return x


_UPO_CACHE = {}


def find_upo(p):
    """Least-unstable prime-period-p orbit, in dynamical order starting at its smallest point."""
    if p in _UPO_CACHE:
        return _UPO_CACHE[p]
    xs = np.linspace(1e-9, 1 - 1e-9, 2_000_001)
    g = _fp(xs, p) - xs
    idx = np.where(np.sign(g[:-1]) * np.sign(g[1:]) < 0)[0]
    lo, hi = xs[idx].copy(), xs[idx + 1].copy()
    glo = g[idx]
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        gm = _fp(mid, p) - mid
        same = np.sign(gm) == np.sign(glo)
        lo = np.where(same, mid, lo)
        glo = np.where(same, gm, glo)
        hi = np.where(same, hi, mid)
    roots = 0.5 * (lo + hi)
    orbits = {}
    for x0 in roots:
        prime = all(abs(_fp(x0, d) - x0) > 1e-8 for d in range(1, p) if p % d == 0)
        if not prime:
            continue
        orb = [x0]
        for _ in range(p - 1):
            orb.append(fmap(orb[-1]))
        key = round(min(orb), 7)
        if key not in orbits:
            i0 = int(np.argmin(orb))
            orb = orb[i0:] + orb[:i0]
            orbits[key] = np.array(orb)
    best = None
    for key in sorted(orbits):
        o = orbits[key]
        mult = float(np.prod(R * (1 - 2 * o)))
        if best is None or abs(mult) < abs(best[1]) - 1e-12:
            best = (o, mult)
    o, mult = best
    resid = float(np.max(np.abs(_fp(o, p) - o)))
    info = dict(p=p, n_orbits=len(orbits), multiplier=mult, residual=resid, orbit=o.tolist())
    _UPO_CACHE[p] = (o, info)
    return o, info


def training_series(rng):
    """Open-loop series (A1): u_t iid U(-delta, delta), no feedback."""
    x = rng.uniform(0.01, 0.99)
    for _ in range(BURN):
        x = fmap(x, rng.uniform(-DELTA, DELTA))
    xs = np.empty(NTRAIN)
    us = rng.uniform(-DELTA, DELTA, NTRAIN)
    for t in range(NTRAIN):
        xs[t] = x
        x = fmap(x, us[t])
    return xs, us


def fit_controller(xs, us, orb, C, shuffle=False, rng=None):
    """A2/A3: per-phase least squares of the one-step model, deadbeat weights w = -a/b."""
    if shuffle:
        perm = rng.permutation(len(xs))
        xs, us = xs[perm], us[perm]
    p = len(orb)
    N = len(xs)
    d = np.abs(xs[:, None] - orb[None, :])
    ph = np.argmin(d, axis=1)
    dm = d[np.arange(N), ph]
    W = np.zeros((p, C))
    nrows = []
    for phi in range(p):
        ts = np.where((ph == phi) & (dm < EPS_FIT))[0]
        ts = ts[(ts >= C - 1) & (ts < N - 1)]
        nrows.append(int(len(ts)))
        if len(ts) < C + 6:
            continue
        # REPAIR (pilot attempt 2, NOTES.md): intercept column fitted, then discarded
        X = np.empty((len(ts), C + 2))
        for k in range(C):
            X[:, k] = xs[ts - k] - orb[(phi - k) % p]
        X[:, C] = us[ts]
        X[:, C + 1] = 1.0
        y = xs[ts + 1] - orb[(phi + 1) % p]
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        b = coef[C]
        if b == 0:
            continue
        W[phi] = -coef[:C] / b
    return W, nrows


def simulate(orb, Ws, Cs, rng, ntrials=NTRIALS, inject=None):
    """Run len(Ws) controllers x ntrials lanes on orbit orb.
    Ws[i]: (p, Cs[i]) weights. inject[i]: True -> CHEAT lane (observable overwritten by the
    exact orbit after CHEAT_START, controller off). Returns per-controller success fraction,
    per-lane first-success time, mean abs kick."""
    p = len(orb)
    nC = len(Ws)
    Cmax = max(Cs)
    L = nC * ntrials
    Wl = np.zeros((nC, p, Cmax))
    for i, (W, C) in enumerate(zip(Ws, Cs)):
        Wl[i, :, :C] = W
    Wl = np.repeat(Wl, ntrials, axis=0)
    inj = np.zeros(L, bool)
    if inject is not None:
        inj = np.repeat(np.array(inject, bool), ntrials)
    # pre-history: Cmax-1 free steps so the delay buffer is full at step 0
    buf = np.zeros((L, Cmax))
    x = rng.uniform(0.01, 0.99, L)
    hist = [x]
    for _ in range(Cmax - 1):
        hist.append(fmap(hist[-1]))
    for k in range(Cmax):
        buf[:, k] = hist[Cmax - 1 - k]
    x = buf[:, 0].copy()
    run = np.zeros(L, int)
    first = np.full(L, -1)
    kicksum = np.zeros(L)
    lanes = np.arange(L)
    karr = np.arange(Cmax)
    for t in range(NSTEPS):
        d = np.abs(x[:, None] - orb[None, :])
        ph = np.argmin(d, axis=1)
        dm = d[lanes, ph]
        run = np.where(dm < TOL, run + 1, 0)
        newly = (run >= RUN) & (first < 0)
        first[newly] = t
        if np.all(first >= 0):
            break
        refs = orb[(ph[:, None] - karr[None, :]) % p]
        u = np.sum(Wl[lanes, ph, :] * (buf - refs), axis=1)
        u = np.clip(u, -DELTA, DELTA)
        u[inj] = 0.0
        kicksum += np.abs(u)
        xn = fmap(x, u)
        if t >= CHEAT_START and inj.any():
            xn[inj] = orb[(ph[inj] + 1) % p]
        buf[:, 1:] = buf[:, :-1]
        buf[:, 0] = xn
        x = xn
    steps = t + 1
    succ = (first >= 0).reshape(nC, ntrials)
    return dict(frac=succ.mean(axis=1).tolist(),
                first=first.reshape(nC, ntrials).tolist(),
                mean_kick=(kicksum / steps).reshape(nC, ntrials).mean(axis=1).tolist(),
                steps_run=steps)


def pmax(frac_by_p):
    """frac_by_p: dict p -> fraction. Largest p with fraction >= 0.8, else 0 (A7)."""
    ok = [p for p, f in frac_by_p.items() if f >= 0.8]
    return max(ok) if ok else 0


def criterion(main, twin):
    """main, twin: dict C -> dict p -> pooled fraction (C in 1..8, p in 1..8)."""
    pm = {C: pmax(main[C]) for C in CS}
    nondec = all(pm[CS[i]] <= pm[CS[i + 1]] for i in range(len(CS) - 1))
    spread = pm[8] - pm[1]
    partA = bool(nondec and spread >= 3)
    twin_long = [twin[C][p] for C in CS for p in PS if p >= 2]
    twin_max = max(twin_long)
    partB = bool(twin_max <= 0.1)
    failure = bool(spread <= 1 or twin_max >= 0.5)
    return dict(p_max={str(C): pm[C] for C in CS}, nondecreasing=bool(nondec), spread=spread,
                partA=partA, twin_max_frac_p_ge_2=twin_max, partB=partB,
                success=bool(partA and partB), failure=failure)


def pool(rows, arm, key="grid"):
    """Pool per-seed grids (C -> p -> frac) over seeds (equal trials per seed)."""
    rs = [r for r in rows if r["arm"] == arm]
    out = {}
    for r in rs:
        for C, byp in r[key].items():
            for p, f in byp.items():
                out.setdefault(int(C), {}).setdefault(int(p), []).append(f)
    return {C: {p: float(np.mean(v)) for p, v in byp.items()} for C, byp in out.items()}
