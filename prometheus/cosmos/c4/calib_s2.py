"""Planted calibration of the S0-A (A1) and S2 (A4) statistics. SYNTHETIC ONLY.

Planted worlds (5 families unless stated). A world has a physical score s and a label y.
  UNIVERSAL     y ~ Bernoulli(sigmoid(beta (s - c))), the SAME beta and c in every family; the families
                differ only in where their s values lie (allowed: a universal law may see different
                coordinate distributions per family).
  FAM_OFFSET    as UNIVERSAL but c_f differs by family (spread `shift`): the law needs a family term.
  FAM_SLOPE     beta_f differs by family.
  FAM_CONSTANT  the A1 cheat: the candidate predicts one class per family, chosen by the family's base rate.
The law is fitted on held-out-family folds (LOFO) on s alone; S2 sees its held-out p.

    python -m prometheus.cosmos.c4.calib_s2 [nsim]   ->  JSON of pass rates
"""
from __future__ import annotations

import json
import sys

import numpy as np

from prometheus.cosmos.c4 import stats as S

NFAM = 5


def _sig(x):
    return 1 / (1 + np.exp(-x))


def planted(kind, n, rng, shift=1.0, beta=3.0):
    fam = np.arange(n) % NFAM
    loc = np.linspace(-0.6, 0.6, NFAM)[fam]
    s = loc + rng.standard_normal(n)
    c = np.zeros(n)
    b = np.full(n, beta)
    if kind == "FAM_OFFSET":
        c = np.linspace(-shift / 2, shift / 2, NFAM)[rng.permutation(NFAM)][fam]
    elif kind == "FAM_SLOPE":
        b = np.array([0.5, 1.0, 3.0, 6.0, 12.0])[fam]
    y = (rng.random(n) < _sig(b * (s - c))).astype(int)
    return y, s, fam


def lofo_p(y, s, fam):
    p = np.empty(len(y))
    one = np.ones((len(y), 1))
    X = np.hstack([one, s[:, None]])
    for f in np.unique(fam):
        tr = fam != f
        beta, _ = S._logit_fit(X[tr], y[tr].astype(float))
        p[~tr] = _sig(X[~tr] @ beta)
    return p


def s2_pass_rate(kind, n, nsim, rng, nperm=300, **kw):
    ok = 0
    for _ in range(nsim):
        y, s, fam = planted(kind, n, rng, **kw)
        p = lofo_p(y, s, fam)
        ok += S.s2_verdict(y, s, p, fam, rng, nperm=nperm)["pass"]
    return ok / nsim


def naive_s2_pass_rate(kind, n, nsim, rng, **kw):
    """The v0.2 rule (A4): fail if ANY per-family intercept or slope CI excludes the pooled value (Wald, 95%,
    no correction), approximated by per-family offset/calibration fits."""
    ok = 0
    for _ in range(nsim):
        y, s, fam = planted(kind, n, rng, **kw)
        p = lofo_p(y, s, fam)
        lp = np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))
        X = np.hstack([np.ones((n, 1)), lp[:, None]])
        b0, _ = S._logit_fit(X, y.astype(float))
        bad = False
        for f in range(NFAM):
            m = fam == f
            bf, _ = S._logit_fit(X[m], y[m].astype(float))
            mu = _sig(np.clip(X[m] @ bf, -30, 30))
            cov = np.linalg.pinv(X[m].T @ (X[m] * (mu * (1 - mu))[:, None]))
            se = np.sqrt(np.diag(cov))
            bad |= bool(np.any(np.abs(bf - b0) > 1.96 * se))
        ok += not bad
    return ok / nsim


def s0a_pass_rate(kind, n, nsim, rng, acc=0.70):
    """S0-A inside the REGISTERED stratum: baseline T3 predicts 1 everywhere."""
    ok = 0
    base = np.array([.8, .7, .5, .3, .2])
    for _ in range(nsim):
        fam = np.arange(n) % NFAM
        y = (rng.random(n) < base[fam]).astype(int)
        t3 = np.ones(n, int)
        if kind == "FAM_CONSTANT":
            c = (base[fam] >= .5).astype(int)
        else:   # a genuine within-family predictor, right with probability acc on each world
            c = np.where(rng.random(n) < acc, y, 1 - y)
        ok += S.s0a_verdict(y, c, t3, fam, rng, nflip=2000, nboot=400)["pass"]
    return ok / nsim


def main(nsim=200):
    rng = np.random.default_rng(20261008)
    out = {"nsim": nsim, "S0A": {}, "S2": {}, "S2_naive_v02": {}}
    for kind, acc in (("FAM_CONSTANT", None), ("WITHIN_0.62", .62), ("WITHIN_0.70", .70), ("WITHIN_0.80", .80)):
        for n in (160, 240):
            out["S0A"][f"{kind}_n{n}"] = s0a_pass_rate(kind if acc is None else "WITHIN", n, nsim, rng,
                                                       acc=acc or .7)
    for kind in ("UNIVERSAL", "FAM_OFFSET", "FAM_SLOPE"):
        for n in (160, 240, 400):
            out["S2"][f"{kind}_n{n}"] = s2_pass_rate(kind, n, nsim, rng)
            out["S2_naive_v02"][f"{kind}_n{n}"] = naive_s2_pass_rate(kind, n, nsim, rng)
    for shift in (0.25, 0.5):
        out["S2"][f"FAM_OFFSET_shift{shift}_n240"] = s2_pass_rate("FAM_OFFSET", 240, nsim, rng, shift=shift)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 200)


def s0a_power_realistic(n, nsim, rng, uplift=0.10, fam_sd=0.75, nflip=2000, nboot=400, cheat=False, carried=False):
    """A3: per-family accuracy logit-normal around the level giving a mean within-family BA of .5 + uplift,
    per-family base rates that differ, and errors concentrated near the boundary (a latent margin m ~ N(0,1);
    error probability doubles for |m| < .5). The baseline (T3-DOWN in the REGISTERED stratum) predicts 1."""
    ok = 0
    base = np.array([.75, .6, .5, .4, .25])
    lvl = np.log((.5 + uplift) / (.5 - uplift))
    for _ in range(nsim):
        fam = np.arange(n) % NFAM
        y = (rng.random(n) < base[fam]).astype(int)
        if cheat:
            c = (base[fam] >= .5).astype(int)
        elif carried:   # one family carries everything: accuracy .5 + 5*uplift there, .5 elsewhere
            acc_f = np.full(NFAM, .5)
            acc_f[0] = min(.99, .5 + NFAM * uplift)
            c = np.where(rng.random(n) < acc_f[fam], y, 1 - y)
        else:
            acc_f = 1 / (1 + np.exp(-(lvl + fam_sd * rng.standard_normal(NFAM))))
            m = rng.standard_normal(n)
            perr = (1 - acc_f[fam]) * np.where(np.abs(m) < .5, 2.0, 1.0)
            for f in range(NFAM):                                    # keep each family's mean error at 1 - acc_f
                mf = fam == f
                perr[mf] = perr[mf] * (1 - acc_f[f]) / np.mean(perr[mf])
            c = np.where(rng.random(n) < np.clip(perr, 0, 1), 1 - y, y)
        ok += S.s0a_verdict(y, c, np.ones(n, int), fam, rng, nflip=nflip, nboot=nboot)["pass"]
    return ok / nsim
