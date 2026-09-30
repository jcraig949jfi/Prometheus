"""W5 controls (HT-e106e1603b, pass P3v2). NO TREATMENT CODE.

World: does the iteration count of an iterative decoder carry information
about the realised error weight w beyond what the syndrome weight s of the
received word already carries?

Statistic G (per seed):  G = 1 - CVMSE(w ~ poly(s, t)) / CVMSE(w ~ poly(s))
with 5-fold cross-validation, cubic polynomial features (see features()).

Arms implemented here (the treatment arm, t = real min-sum iteration count,
is NOT implemented here):
  POSITIVE_CONTROL: t built from the TRUE w with a critical-slowing-down
                    shape peaked at x_c (effect present by construction).
  NULL_TWIN:        t built by the same formula from w_hat(s), the error
                    weight inferred from the syndrome weight alone (all
                    nuisance statistics of t kept; information beyond s
                    destroyed).
  CHEAT:            t := w (success injected into the observable).

Every arm shares: the (3,6)-regular Tanner graph, the channel draw
(p ~ U[P_LO, P_HI], iid BSC flips), the syndrome weight, and the G code
path (g_statistic). Rows -> control_rows.jsonl, flushed per row.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "control_rows.jsonl")

N = 504            # variables
DV, DC = 3, 6      # regular degrees
M = N * DV // DC   # 252 checks
P_LO, P_HI = 0.02, 0.12
BLOCKS = 3000      # blocks per seed
TMAX = 60          # iteration cap shared with the treatment decoder
SEEDS = [0, 1, 2, 3, 4]
FOLDS = 5

# positive-control / twin slowing-down shape
X_C = 0.07         # location of the built-in slowing-down peak
A_SLOW = 0.5
DELTA = 0.005
SIGMA_T = 0.40     # multiplicative log-normal jitter on t


def make_graph(seed):
    """(3,6)-regular Tanner graph by configuration model + swap repair of
    repeated (check, variable) pairs. Returns check_vars (M x DC)."""
    rng = np.random.default_rng(10_000 + seed)
    var_sockets = np.repeat(np.arange(N), DV)
    for _ in range(1000):
        perm = rng.permutation(var_sockets)
        cv = perm.reshape(M, DC)
        bad = [c for c in range(M) if len(set(cv[c])) < DC]
        tries = 0
        while bad and tries < 20000:
            c = bad[0]
            row = cv[c]
            # find a duplicated slot and swap it with a random slot elsewhere
            seen = {}
            for j, v in enumerate(row):
                if v in seen:
                    c2 = rng.integers(M)
                    j2 = rng.integers(DC)
                    cv[c, j], cv[c2, j2] = cv[c2, j2], cv[c, j]
                    break
                seen[v] = j
            bad = [c for c in range(M) if len(set(cv[c])) < DC]
            tries += 1
        if not bad:
            return cv
    raise RuntimeError("graph repair failed")


def channel(cv, seed, blocks=BLOCKS):
    """Shared channel: p per block, iid flips, true weight w, syndrome weight s."""
    rng = np.random.default_rng(20_000 + seed)
    p = rng.uniform(P_LO, P_HI, size=blocks)
    e = (rng.random((blocks, N)) < p[:, None]).astype(np.uint8)
    w = e.sum(axis=1).astype(float)
    synd = e[:, cv].sum(axis=2) % 2          # blocks x M
    s = synd.sum(axis=1).astype(float)
    return p, w, s


def w_hat_from_s(s):
    """Invert E[s]/M = (1 - (1-2x)^DC)/2 -> x_hat, times N."""
    q = np.clip(s / M, 0.0, 0.499)
    x = (1.0 - (1.0 - 2.0 * q) ** (1.0 / DC)) / 2.0
    return x * N


def slowing_t(x, rng):
    base = A_SLOW / (np.abs(x - X_C) + DELTA)
    t = np.rint(base * np.exp(SIGMA_T * rng.standard_normal(x.shape)))
    return np.clip(t, 1, TMAX)


def features(s, t=None):
    zs = (s - s.mean()) / (s.std() + 1e-12)
    cols = [np.ones_like(zs), zs, zs ** 2, zs ** 3]
    if t is not None:
        lt = np.log1p(t)
        zt = (lt - lt.mean()) / (lt.std() + 1e-12)
        cols += [zt, zt ** 2, zt ** 3, zs * zt, zs ** 2 * zt, zs * zt ** 2]
    return np.column_stack(cols)


def cv_mse(X, y, seed):
    rng = np.random.default_rng(30_000 + seed)
    fold = rng.permutation(len(y)) % FOLDS
    err = np.empty_like(y)
    for f in range(FOLDS):
        tr, te = fold != f, fold == f
        beta, *_ = np.linalg.lstsq(X[tr], y[tr], rcond=None)
        err[te] = y[te] - X[te] @ beta
    return float(np.mean(err ** 2))


def g_statistic(w, s, t, seed):
    """The single G code path used by every arm (and by the treatment)."""
    mse_s = cv_mse(features(s), w, seed)
    mse_st = cv_mse(features(s, t), w, seed)
    return 1.0 - mse_st / mse_s, mse_s, mse_st


def arm_t(arm, w, s, seed):
    rng = np.random.default_rng(40_000 + seed)
    if arm == "POSITIVE_CONTROL":
        return slowing_t(w / N, rng)
    if arm == "NULL_TWIN":
        return slowing_t(w_hat_from_s(s) / N, rng)
    if arm == "CHEAT":
        return w.copy()
    raise ValueError(arm)


def main():
    t0, w0 = time.process_time(), time.time()
    open(ROWS, "w").close()
    with open(ROWS, "a", encoding="utf-8") as fh:
        for seed in SEEDS:
            cv = make_graph(seed)
            p, w, s = channel(cv, seed)
            for arm in ("POSITIVE_CONTROL", "NULL_TWIN", "CHEAT"):
                t = arm_t(arm, w, s, seed)
                g, mse_s, mse_st = g_statistic(w, s, t, seed)
                row = {"arm": arm, "seed": seed, "blocks": int(len(w)),
                       "G": g, "cvmse_s": mse_s, "cvmse_st": mse_st,
                       "mean_t": float(t.mean()), "sd_t": float(t.std()),
                       "mean_w": float(w.mean()), "mean_s": float(s.mean())}
                fh.write(json.dumps(row) + "\n")
                fh.flush()
                print(arm, seed, round(g, 4), flush=True)
    cpu = time.process_time() - t0
    with open(os.path.join(HERE, "controls_cpu.json"), "w") as fh:
        json.dump({"cpu_seconds": cpu, "wall_seconds": time.time() - w0}, fh)
    print("cpu_s", round(cpu, 1))


if __name__ == "__main__":
    sys.exit(main())
