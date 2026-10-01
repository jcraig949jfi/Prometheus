"""HT-056d3ac561 / W1: stride-consistency metamorphic relation in a Kalman filter.

See IMPLEMENTATION_NOTES.md. Writes rows.jsonl (one JSON object per arm x run),
flushed per row. No shell redirection.
"""
import json
import os
import time

import numpy as np
from scipy.linalg import solve_discrete_lyapunov
from sklearn.linear_model import Lasso

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")

N = 4
T = 500
BURN = 50
Q = np.eye(N)
R = np.eye(N)
DELTAS = [0.05, 0.1, 0.2]
MATCHED_SEEDS = list(range(0, 50))
MISMATCH_SEEDS = list(range(1000, 1050))
EPS = 1e-5
ALPHA_FRAC = 0.1
CHEAT_BUMP = 100.0
A_SEED = 20260929
EVAL_T = np.arange(BURN, T, 2)  # even t in [50, 498]
EVAL_T = EVAL_T[EVAL_T % 2 == 0]


def make_A():
    M = np.random.default_rng(A_SEED).normal(size=(N, N))
    return 0.9 * M / np.max(np.abs(np.linalg.eigvals(M)))


A_TRUE = make_A()


def stationary_cov(A, Qm):
    if np.max(np.abs(np.linalg.eigvals(A))) >= 1.0:
        return 10.0 * np.eye(N)
    return solve_discrete_lyapunov(A, Qm)


def gains(Am, Qm, steps, P0):
    """Time-varying KF quantities (C = I) for a model; data-independent."""
    K = np.empty((steps, N, N))
    Pp = np.empty((steps, N, N))
    Sinv = np.empty((steps, N, N))
    P = P0.copy()
    I = np.eye(N)
    for k in range(steps):
        S = P + R
        Si = np.linalg.inv(S)
        Kk = P @ Si
        Ppost = (I - Kk) @ P
        K[k], Pp[k], Sinv[k] = Kk, Ppost, Si
        P = Am @ Ppost @ Am.T + Qm
    return K, Pp, Sinv


_cache = {}


def model_quantities(Ap):
    key = Ap.tobytes()
    if key in _cache:
        return _cache[key]
    P0 = stationary_cov(Ap, Q)
    A2 = Ap @ Ap
    Q2 = Ap @ Q @ Ap.T + Q
    g1 = gains(Ap, Q, T, P0)
    g2 = gains(A2, Q2, T // 2, P0)
    out = (Ap, A2, g1, g2)
    _cache[key] = out
    return out


def run_filters(Ap, y):
    """Return stride-1 posteriors (T,N), stride-2 posteriors at even t (T/2,N),
    stride-1 NIS series, and the covariances."""
    Ap, A2, (K1, P1, S1i), (K2, P2, _) = model_quantities(Ap)
    x1 = np.empty((T, N))
    nis = np.empty(T)
    x = np.zeros(N)
    for t in range(T):
        e = y[t] - x
        nis[t] = e @ S1i[t] @ e
        xp = x + K1[t] @ e
        x1[t] = xp
        x = Ap @ xp
    x2 = np.empty((T // 2, N))
    x = np.zeros(N)
    for k in range(T // 2):
        e = y[2 * k] - x
        xp = x + K2[k] @ e
        x2[k] = xp
        x = A2 @ xp
    return x1, x2, nis, P1, P2


def simulate(seed):
    rng = np.random.default_rng(seed)
    x = rng.multivariate_normal(np.zeros(N), stationary_cov(A_TRUE, Q))
    xs = np.empty((T, N))
    for t in range(T):
        xs[t] = x
        x = A_TRUE @ x + rng.normal(size=N)
    y = xs + rng.normal(size=(T, N))
    return xs, y


def whiteners(P1, P2):
    """For each evaluated even t: W_t = (P2_t - P1_t)^{-1/2}, and inverse."""
    Ws = []
    for t in EVAL_T:
        Dc = P2[t // 2] - P1[t]
        Dc = 0.5 * (Dc + Dc.T)
        w, V = np.linalg.eigh(Dc)
        Ws.append((V / np.sqrt(w)) @ V.T)
    return np.array(Ws), float(np.min([np.linalg.eigvalsh(P2[t // 2] - P1[t]).min() for t in EVAL_T]))


def disagreement(x1, x2):
    return x1[EVAL_T] - x2[EVAL_T // 2]  # (n_eval, N)


def lasso_top1(X, z):
    n = X.shape[0]
    alpha_max = np.max(np.abs(X.T @ z)) / n
    if alpha_max <= 0:
        return int(np.argmax(np.linalg.norm(X, axis=0))), [0.0] * X.shape[1]
    m = Lasso(alpha=ALPHA_FRAC * alpha_max, fit_intercept=False, max_iter=20000)
    m.fit(X, z)
    c = m.coef_
    if np.all(c == 0):
        return int(np.argmax(np.abs(X.T @ z))), c.tolist()
    return int(np.argmax(np.abs(c))), c.tolist()


def one_run(seed, delta, entry):
    t0 = time.process_time()
    xs, y = simulate(seed)
    Ap = A_TRUE.copy()
    if entry is not None:
        Ap[entry // N, entry % N] += delta
    x1, x2, nis, P1, P2 = run_filters(Ap, y)
    W, min_eig = whiteners(P1, P2)
    d = disagreement(x1, x2)
    z = np.einsum("tij,tj->ti", W, d)
    Dt = np.sum(z * z, axis=1)
    D = float(Dt.mean())
    NIS = float(nis[BURN:].mean())
    rmse = float(np.sqrt(np.mean(np.sum((x1[BURN:] - xs[BURN:]) ** 2, axis=1))))
    # null twin: stride-1 estimate at a permuted even time
    perm = np.random.default_rng(seed + 777).permutation(len(EVAL_T))
    d_null = x1[EVAL_T[perm]] - x2[EVAL_T // 2]
    z_null = np.einsum("tij,tj->ti", W, d_null)
    D_null = float(np.sum(z_null * z_null, axis=1).mean())
    # sensitivities by central finite differences on A'
    cols, cols_mean = [], []
    for e in range(N * N):
        E = np.zeros((N, N))
        E[e // N, e % N] = EPS
        xa1, xa2, _, _, _ = run_filters(Ap + E, y)
        xb1, xb2, _, _, _ = run_filters(Ap - E, y)
        dd = (disagreement(xa1, xa2) - disagreement(xb1, xb2)) / (2 * EPS)
        zz = np.einsum("tij,tj->ti", W, dd)
        cols.append(zz.ravel())
        cols_mean.append(zz.mean(axis=0))
    X = np.array(cols).T
    top1, coef = lasso_top1(X, z.ravel())
    Xm = np.array(cols_mean).T
    top1_literal, _ = lasso_top1(Xm, z.mean(axis=0))
    top1_normonly = int(np.argmax(np.linalg.norm(X, axis=0)))
    return {
        "D": D, "NIS": NIS, "oracle_rmse": rmse, "D_null": D_null,
        "top1": top1, "top1_literal_mean_reading": top1_literal,
        "top1_sensitivity_norm_only": top1_normonly,
        "lasso_coef": coef, "min_eig_P2_minus_P1": min_eig,
        "run_cpu_s": time.process_time() - t0,
    }


def main():
    if os.path.exists(ROWS):
        os.remove(ROWS)
    cpu0 = time.process_time()
    runs = [(s, 0.0, None) for s in MATCHED_SEEDS]
    for dl in DELTAS:
        for s in MISMATCH_SEEDS:
            entry = int(np.random.default_rng(s).integers(0, N * N))
            runs.append((s, dl, entry))
    runs.sort(key=lambda r: (r[2] is not None, r[2] if r[2] is not None else -1, r[1], r[0]))
    params = {"N": N, "T": T, "burn": BURN, "Q": "I", "R": "I", "C": "I",
              "A_seed": A_SEED, "A_true": A_TRUE.tolist(), "eps": EPS,
              "alpha_frac": ALPHA_FRAC, "cheat_bump": CHEAT_BUMP}
    last_model = None
    with open(ROWS, "w", encoding="utf-8") as f:
        for seed, dl, entry in runs:
            key = (entry, dl)
            if key != last_model:
                _cache.clear()
                last_model = key
            r = one_run(seed, dl, entry)
            mism = entry is not None
            base = {"seed": seed, "delta": dl, "true_entry": entry,
                    "mismatched": mism, "params": params,
                    "cpu_cum_s": time.process_time() - cpu0,
                    "run_cpu_s": r["run_cpu_s"],
                    "min_eig_P2_minus_P1": r["min_eig_P2_minus_P1"]}
            arm_rows = [
                ("TREATMENT" if mism else "CONTROL",
                 {"D": r["D"], "NIS": r["NIS"], "top1": r["top1"],
                  "top1_literal_mean_reading": r["top1_literal_mean_reading"],
                  "top1_sensitivity_norm_only": r["top1_sensitivity_norm_only"],
                  "lasso_coef": r["lasso_coef"]}),
                ("NULL_TWIN", {"D_null": r["D_null"], "NIS": r["NIS"]}),
                ("POSITIVE_CONTROL", {"oracle_rmse": r["oracle_rmse"]}),
                ("CHEAT", {"D_cheat": r["D"] + (CHEAT_BUMP if mism else 0.0),
                           "top1_cheat": entry if mism else r["top1"],
                           "NIS": r["NIS"]}),
            ]
            for arm, obs in arm_rows:
                row = dict(base)
                row["arm"] = arm
                row.update(obs)
                f.write(json.dumps(row) + "\n")
                f.flush()
    print("done cpu_s", time.process_time() - cpu0)


if __name__ == "__main__":
    main()
