"""Shared code for HT-79e904e13a / W1: community generator, OU substrate,
estimator, observable, criteria. No treatment (gLV) code lives here."""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, time
import numpy as np
from scipy.linalg import logm, solve_continuous_lyapunov, cholesky
from scipy.stats import spearmanr, wilcoxon

HERE = os.path.dirname(os.path.abspath(__file__))
N_SP = 12
DT = 0.01
N_OBS = 200_000
TAU = 1.0
LAG = int(round(TAU / DT))
DISTANCES = (-0.5, -0.2, -0.05, -0.01)
SEEDS = tuple(range(30))
PRESS = 0.02
OU_SIGMA = 0.05
LEVELS = (6, 4, 2)


def community(seed, draw=0):
    rng = np.random.default_rng([seed, 101, draw])
    A = np.zeros((N_SP, N_SP))
    A[np.diag_indices(N_SP)] = -rng.uniform(0.5, 1.0, N_SP)
    idx, start = [], 0
    for n in LEVELS:
        idx.append(list(range(start, start + n)))
        start += n
    for i in idx[0]:
        for j in idx[0]:
            if i != j and rng.random() < 0.3:
                A[i, j] = -rng.uniform(0, 0.2)
    for lv in (1, 2):
        for i in idx[lv]:
            prey = [j for j in idx[lv - 1] if rng.random() < 0.5]
            if not prey:
                prey = [int(rng.choice(idx[lv - 1]))]
            for j in prey:
                a = rng.uniform(0.2, 1.0)
                A[j, i] = -a
                A[i, j] = 0.5 * a
    xstar = rng.uniform(0.5, 1.5, N_SP)
    return A, xstar


def lead_re(J):
    return float(np.max(np.linalg.eigvals(J).real))


def ou_J(seed, d):
    A, xs = community(seed)
    J0 = np.diag(xs) @ A
    return J0 - (lead_re(J0) - d) * np.eye(N_SP), xs


def true_press_responses(J, xs):
    """Column k = exact mean shift under constant press PRESS*xs[k] on species k."""
    return -np.linalg.solve(J, np.diag(PRESS * xs))


def simulate_ou(Js, rngs, sigma=OU_SIGMA, n=N_OBS):
    """Batched Euler-Maruyama for S OU systems dx = J x dt + sigma dW, started
    from the exact stationary law. Returns float32 array (n, S, N_SP)."""
    S = len(Js)
    Jb = np.stack(Js)
    x = np.empty((S, N_SP))
    for s in range(S):
        Q = sigma ** 2 * np.eye(N_SP)
        P = solve_continuous_lyapunov(Js[s], -Q)
        L = cholesky((P + P.T) / 2 + 1e-12 * np.eye(N_SP), lower=True)
        x[s] = L @ rngs[s].standard_normal(N_SP)
    out = np.empty((n, S, N_SP), dtype=np.float32)
    sq = sigma * np.sqrt(DT)
    CH = 5000
    for c0 in range(0, n, CH):
        m = min(CH, n - c0)
        noise = np.stack([r.standard_normal((m, N_SP)) for r in rngs], axis=1) * sq
        for t in range(m):
            x = x + DT * np.einsum("sij,sj->si", Jb, x) + noise[t]
            out[c0 + t] = x
    return out


def estimate_J(X, lag=LAG, tau=TAU):
    """X: (n, N_SP) series. J = logm(C(tau) C(0)^{-1}) / tau with
    C(tau) = E[x(t+tau) x(t)^T]. Returns (J_real, max_abs_imag)."""
    X = np.asarray(X, dtype=np.float64)
    X = X - X.mean(axis=0)
    n = X.shape[0]
    C0 = X.T @ X / n
    Ct = X[lag:].T @ X[:-lag] / (n - lag)
    M = Ct @ np.linalg.inv(C0)
    L = logm(M)
    imag = float(np.max(np.abs(np.imag(L))))
    return np.real(L) / tau, imag


def predict_responses(J, xs):
    return -np.linalg.solve(J, np.diag(PRESS * xs))


def circular_shift(X, rng):
    n = X.shape[0]
    Y = np.empty_like(X)
    for i in range(X.shape[1]):
        Y[:, i] = np.roll(X[:, i], int(rng.integers(0, n)))
    return Y


def press_spearmans(pred, true):
    out = []
    for k in range(pred.shape[1]):
        r = spearmanr(pred[:, k], true[:, k]).statistic
        out.append(float(0.0 if np.isnan(r) else r))
    return out


# ---------------- observable and criteria ----------------

def per_seed_medians(rows):
    """rows: list of dicts with 'spearman' = {str(d): [12 values]} ->
    {d: array over seeds (seed order)}."""
    rows = sorted(rows, key=lambda r: r["seed"])
    return {d: np.array([np.median(r["spearman"][str(d)]) for r in rows]) for d in DISTANCES}


def arm_summary(rows):
    ps = per_seed_medians(rows)
    med = {str(d): float(np.median(ps[d])) for d in DISTANCES}
    diff = float(np.median(ps[-0.5]) - np.median(ps[-0.01]))
    dvec = ps[-0.5] - ps[-0.01]
    if np.all(dvec == 0):
        p = 1.0
    else:
        p = float(wilcoxon(ps[-0.5], ps[-0.01], alternative="greater").pvalue)
    return {"median": med, "decline": diff, "wilcoxon_p": p, "n_seeds": len(rows)}


def arm_level_success(summ):
    m = summ["median"]
    return bool(m["-0.5"] >= 0.8 and m["-0.2"] >= 0.8
                and summ["decline"] >= 0.3 and summ["wilcoxon_p"] < 0.01)


def null_le_02(null_summ):
    m = null_summ["median"]
    return bool(m["-0.5"] <= 0.2 and m["-0.2"] <= 0.2)


def success(treat_summ, null_summ):
    return bool(arm_level_success(treat_summ) and null_le_02(null_summ))


def failure(treat_summ, null_summ):
    m, n = treat_summ["median"], null_summ["median"]
    return bool(m["-0.5"] < 0.5 or abs(m["-0.5"] - n["-0.5"]) < 0.2
                or treat_summ["decline"] < 0.1)


def positive_meets(pos_summ):
    m = pos_summ["median"]
    return bool(m["-0.5"] >= 0.95 and m["-0.2"] >= 0.95)


# ---------------- io ----------------

def append_row(path, row):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def read_rows(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def log_cpu(script, t0_cpu, t0_wall, extra=None):
    rec = {"script": script, "cpu_s": time.process_time() - t0_cpu,
           "wall_s": time.time() - t0_wall, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if extra:
        rec.update(extra)
    append_row(os.path.join(HERE, "cpu_ledger.jsonl"), rec)
    return rec


def core_minutes():
    p = os.path.join(HERE, "cpu_ledger.jsonl")
    if not os.path.exists(p):
        return 0.0
    return sum(r["cpu_s"] for r in read_rows(p)) / 60.0
