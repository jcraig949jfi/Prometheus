"""C4 S0 v0.2 power design aid (SYNTHETIC ONLY: reads no world data, no withheld material, no D2).

Two strata (operator review 2026-09-30, s1):
  S0-A challenge stratum: every world has the shortcut precondition registered, so T3-DOWN predicts
       FUNCTIONAL throughout (BA .5). The candidate is right with probability `s` on each world, both
       classes. PASS = BA margin >= DELTA_A, family-stratified paired-bootstrap 95% lower bound > 0,
       and a paired sign-flip randomization test of the BA difference p < .05 (McNemar tests accuracy, not
       BA, and fails on class-imbalanced strata; v0.1 finding, reported descriptively only).
  S0-B natural stratum: T3-DOWN is wrong on a share `t3err` of worlds (false positives, as observed in
       C3 visible: 7/113). The candidate fixes `fix` of those and breaks `e` of the rest.
       PASS = one-sided 95% bootstrap lower bound of BA(cand) - BA(T3) > -EPS_B.

    python -m prometheus.cosmos.c4.power_s0   ->  prints a JSON table
"""
import json

import numpy as np

SEED, NSIM, NBOOT, NFAM = 20260930, 200, 400, 5
DELTA_A, EPS_B = 0.10, 0.03


def ba(y, p):
    pos, neg = y == 1, y == 0
    return (np.mean(p[pos] == 1) + np.mean(p[neg] == 0)) / 2


def boot(y, a, b, fam, rng):
    idx = [np.flatnonzero(fam == f) for f in range(NFAM)]
    d = []
    for _ in range(NBOOT):
        s = np.concatenate([rng.choice(v, len(v)) for v in idx])
        d.append(ba(y[s], a[s]) - ba(y[s], b[s]))
    return np.asarray(d)


def stratum_a(n, q, s, rng):
    fam = np.arange(n) % NFAM
    y = (rng.random(n) < q).astype(int)
    t3 = np.ones(n, int)
    c = np.where(rng.random(n) < s, y, 1 - y)
    if ba(y, c) - ba(y, t3) < DELTA_A:
        return False
    if signflip_p(y, c, t3, fam, rng) >= .05:
        return False
    return bool(np.percentile(boot(y, c, t3, fam, rng), 2.5) > 0)


def signflip_p(y, a, b, fam, rng, nflip=NBOOT):
    """Paired sign-flip randomization test of BA(a) - BA(b) (one-sided); independent per-world sign flips. Each world
    contributes (1[a right] - 1[b right]) / (2 n_class)."""
    w = np.where(y == 1, 1 / (2 * max(1, y.sum())), 1 / (2 * max(1, (1 - y).sum())))
    d = w * ((a == y).astype(float) - (b == y).astype(float))
    obs = d.sum()
    null = np.array([(d * rng.choice((-1, 1), len(d))).sum() for _ in range(nflip)])
    return float((1 + np.sum(null >= obs)) / (1 + nflip))


def stratum_b(n, t3err, fix, e, rng):
    fam = np.arange(n) % NFAM
    y = (rng.random(n) < .6).astype(int)
    t3 = y.copy()
    t3[(y == 0) & (rng.random(n) < t3err / .4)] = 1
    wrong = t3 != y
    c = np.where(wrong & (rng.random(n) < fix), y, t3)
    c = np.where(~wrong & (rng.random(n) < e), 1 - y, c)
    return bool(np.percentile(boot(y, c, t3, fam, rng), 5) > -EPS_B)


def main():
    rng = np.random.default_rng(SEED)
    out = {"DELTA_A": DELTA_A, "EPS_B": EPS_B, "nsim": NSIM, "nboot": NBOOT, "families": NFAM, "A": {}, "B": {}}
    for n in (80, 160, 240):
        for q in (.4, .5, .6):
            for s in (.62, .70, .80):
                out["A"][f"n{n}_q{q}_s{s}"] = float(np.mean([stratum_a(n, q, s, rng) for _ in range(NSIM)]))
    for n in (120, 240):
        for e in (0.0, .02, .04, .06):
            out["B"][f"n{n}_t3err.06_fix.5_e{e}"] = float(np.mean([stratum_b(n, .06, .5, e, rng) for _ in range(NSIM)]))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
