"""HT-056d3ac561 / W4 core: mirror Kalman filters, MR residual, fault recovery.

Shared by pilot.py and world.py. Contains no treatment arm.
Parameters are fixed here (see NOTES.md) and written into every row.
"""
import json
import time
import warnings

import numpy as np
from scipy.linalg import solve_discrete_are, sqrtm
from sklearn.linear_model import Lasso
from sklearn.exceptions import ConvergenceWarning

warnings.filterwarnings("ignore", category=ConvergenceWarning)

PARAMS = {
    "state_dim": 20,
    "fault_atoms": 40,
    "kernel_dim": 8,
    "trials": 200,
    "sparsity_levels": [1, 2, 3, 6, 10],
    "steps": 200,
    "q": 0.1,
    "r": 0.1,
    "theta_range": [np.pi / 3, np.pi],
    "coef_mag_range": [1.0, 2.0],
    "lasso_alpha_rule": "max_j||P_j|| * sqrt(2 ln(2*p)) / n, n=20, p=40",
    "lasso_err_thr": 0.20,
    "mn_err_thr": 0.50,
    "rate_hi": 0.80,
    "nt_rate_lo": 0.20,
}
SEEDS = [0, 1, 2, 3, 4]
ARM_CODE = {"POSITIVE_CONTROL": 1, "CHEAT": 2, "NULL_TWIN": 3, "TREATMENT": 4, "CONTROL": 5}


def _orth(rng, n):
    q, rr = np.linalg.qr(rng.standard_normal((n, n)))
    return q * np.sign(np.diag(rr))


def make_world(seed):
    """Build T, A, KF gain, dictionary D, exact P and whitening for one seed."""
    p = PARAMS
    n, m, kd, N = p["state_dim"], p["fault_atoms"], p["kernel_dim"], p["steps"]
    rng = np.random.default_rng([seed, 999])
    U = _orth(rng, n)
    blocks = np.eye(n)
    thetas = rng.uniform(*p["theta_range"], size=(n - kd) // 2)
    for i, th in enumerate(thetas):
        j = kd + 2 * i
        c, s = np.cos(th), np.sin(th)
        blocks[j:j + 2, j:j + 2] = [[c, -s], [s, c]]
    T = U @ blocks @ U.T
    A = 0.9 * np.eye(n) + 0.05 * (T + T.T)
    Q = p["q"] * np.eye(n)
    R = p["r"] * np.eye(n)
    Pp = solve_discrete_are(A.T, np.eye(n), Q, R)
    K = Pp @ np.linalg.inv(Pp + R)
    F = (np.eye(n) - K) @ A
    # C_s = (1/N) sum_{t=s}^{N} F^{t-s} K
    S = [None] * (N + 1)
    S[N] = K.copy()
    for s in range(N - 1, 0, -1):
        S[s] = K + F @ S[s + 1]
    C = [S[s] / N for s in range(1, N + 1)]
    Gbar = sum(C)
    Sigma = 2 * p["r"] * sum(c @ c.T for c in C)
    W = np.real(np.linalg.inv(sqrtm(Sigma)))
    D = rng.standard_normal((n, m))
    D /= np.linalg.norm(D, axis=0)
    P = W @ Gbar @ (T - np.eye(n)) @ D
    Uu, sv, Vt = np.linalg.svd(P)
    rank = n - kd
    Vr = Vt[:rank].T                       # row(P) basis (40 x 12)
    Prow = Vr @ Vr.T
    Pker = np.eye(m) - Prow
    Ppinv = Vr @ np.diag(1.0 / sv[:rank]) @ Uu[:, :rank].T
    colnorm = np.linalg.norm(P, axis=0)
    alpha = colnorm.max() * np.sqrt(2 * np.log(2 * m)) / n
    Dn = D / np.linalg.norm(D, axis=0)
    Pn = P / colnorm
    world = dict(T=T, A=A, K=K, F=F, W=W, D=D, P=P, Prow=Prow, Pker=Pker,
                 Ppinv=Ppinv, alpha=alpha, sv=sv, rank=rank)
    world["meta"] = {
        "alpha": float(alpha),
        "P_singular_values": [round(float(x), 6) for x in sv],
        "P_rank_used": rank,
        "coherence_D": float(np.max(np.abs(Dn.T @ Dn) - np.eye(m))),
        "coherence_P": float(np.max(np.abs(Pn.T @ Pn) - np.eye(m))),
        "kf_gain_diag_mean": float(np.mean(np.diag(K))),
        "thetas": [round(float(t), 6) for t in thetas],
    }
    return world


def simulate_y(world, F_true, rng):
    """Run the two mirror filters over `steps` for a batch of faults.

    F_true: (trials, 40) fault coefficients. Returns whitened accumulated
    MR residual y (trials, 20).
    """
    p = PARAMS
    n, N = p["state_dim"], p["steps"]
    nt = F_true.shape[0]
    T, A, K, D, W = world["T"], world["A"], world["K"], world["D"], world["W"]
    B = F_true @ D.T                       # sensor biases (trials, 20)
    x = rng.standard_normal((nt, n))
    xa = np.zeros((nt, n))
    xb = np.zeros((nt, n))
    acc = np.zeros((nt, n))
    sq, sr = np.sqrt(p["q"]), np.sqrt(p["r"])
    IK = np.eye(n) - K
    for _ in range(N):
        x = x @ A.T + sq * rng.standard_normal((nt, n))
        za = x + B + sr * rng.standard_normal((nt, n))
        zb = x @ T.T + B + sr * rng.standard_normal((nt, n))
        xa = (xa @ A.T) @ IK.T + za @ K.T
        xb = (xb @ A.T) @ IK.T + zb @ K.T
        acc += xa @ T.T - xb
    ybar = acc / N
    return ybar @ W.T


def sparse_faults(rng, k, nt):
    p = PARAMS
    m = p["fault_atoms"]
    Fs = np.zeros((nt, m))
    for i in range(nt):
        S = rng.choice(m, size=k, replace=False)
        Fs[i, S] = rng.choice([-1.0, 1.0], size=k) * rng.uniform(*p["coef_mag_range"], size=k)
    return Fs


def dense_twin(world, Fs, rng):
    """Dense Gaussian faults with the same total energy and same ker(P) energy."""
    G = rng.standard_normal(Fs.shape)
    Pk, Pr = world["Pker"], world["Prow"]
    gk, gr = G @ Pk, G @ Pr
    fk, fr = Fs @ Pk, Fs @ Pr
    sk = np.linalg.norm(fk, axis=1) / np.linalg.norm(gk, axis=1)
    sr_ = np.linalg.norm(fr, axis=1) / np.linalg.norm(gr, axis=1)
    return gk * sk[:, None] + gr * sr_[:, None]


def rowspace_faults(world, Fs):
    """Spec positive control: faults entirely outside ker(P), same energy."""
    Fr = Fs @ world["Prow"]
    return Fr * (np.linalg.norm(Fs, axis=1) / np.linalg.norm(Fr, axis=1))[:, None]


def recover_lasso(world, Y):
    out = np.zeros((Y.shape[0], PARAMS["fault_atoms"]))
    for i in range(Y.shape[0]):
        las = Lasso(alpha=world["alpha"], fit_intercept=False, max_iter=20000, tol=1e-7)
        las.fit(world["P"], Y[i])
        out[i] = las.coef_
    return out


def recover_minnorm(world, Y):
    return Y @ world["Ppinv"].T


def recover_oracle_support(world, Y, Fs):
    out = np.zeros_like(Fs)
    for i in range(Y.shape[0]):
        S = np.flatnonzero(Fs[i])
        coef, *_ = np.linalg.lstsq(world["P"][:, S], Y[i], rcond=None)
        out[i, S] = coef
    return out


def observables(world, Ftrue, Fhat):
    rel = np.linalg.norm(Fhat - Ftrue, axis=1) / np.linalg.norm(Ftrue, axis=1)
    fk = Ftrue @ world["Pker"]
    hk = Fhat @ world["Pker"]
    ek = np.sum(fk * fk, axis=1)
    rkf = np.sum(hk * fk, axis=1) / np.where(ek > 1e-12, ek, np.nan)
    vis = 1.0 - ek / np.sum(Ftrue * Ftrue, axis=1)
    return rel, rkf, vis


def summarize(rel, rkf, vis, kind):
    p = PARAMS
    d = {
        f"{kind}_success_rate": float(np.mean(rel <= p["lasso_err_thr"])) if kind == "lasso"
        else float(np.mean(rel >= p["mn_err_thr"])),
        f"{kind}_err_median": float(np.median(rel)),
        f"{kind}_err_mean": float(np.mean(rel)),
        f"{kind}_rkf_mean": float(np.nanmean(rkf)) if np.any(np.isfinite(rkf)) else None,
        f"{kind}_err": [round(float(v), 4) for v in rel],
    }
    if kind == "lasso":
        d["lasso_le_0.20_rate"] = d["lasso_success_rate"]
    else:
        d["mn_ge_0.50_rate"] = d["mn_success_rate"]
    d["visibility_mean"] = float(np.mean(vis))
    return d


def stream(seed, family, k):
    return np.random.default_rng([seed, family, k])


FAM_SPARSE, FAM_DENSE, FAM_NOISE_PC, FAM_NOISE_NT, FAM_NOISE_TR = 1, 2, 3, 4, 5


def arm_data(world, seed, k, arm, pc_mode):
    """Return (Ftrue, Y, Fs) for a control arm (no treatment arm here)."""
    nt = PARAMS["trials"]
    Fs = sparse_faults(stream(seed, FAM_SPARSE, k), k, nt)
    if arm == "POSITIVE_CONTROL":
        Ft = rowspace_faults(world, Fs) if pc_mode == "spec_rowspace" else Fs
        Y = simulate_y(world, Ft, stream(seed, FAM_NOISE_PC, k))
    elif arm in ("NULL_TWIN", "CHEAT"):
        Ft = dense_twin(world, Fs, stream(seed, FAM_DENSE, k))
        Y = simulate_y(world, Ft, stream(seed, FAM_NOISE_NT, k))
    else:
        raise ValueError(arm)
    return Ft, Y, Fs


def run_control_arm(world, seed, arm, pc_mode):
    per_k = {}
    for k in PARAMS["sparsity_levels"]:
        Ft, Y, Fs = arm_data(world, seed, k, arm, pc_mode)
        if arm == "POSITIVE_CONTROL" and pc_mode == "oracle_support":
            Fh = recover_oracle_support(world, Y, Fs)
        elif arm == "CHEAT":
            Fh = Ft.copy()                 # success injected into the observable
        else:
            Fh = recover_lasso(world, Y)
        rel, rkf, vis = observables(world, Ft, Fh)
        d = summarize(rel, rkf, vis, "lasso")
        Fm = recover_minnorm(world, Y)
        rel2, rkf2, vis2 = observables(world, Ft, Fm)
        d.update(summarize(rel2, rkf2, vis2, "mn"))
        per_k[str(k)] = d
    return per_k


def make_row(arm, seed, world, per_k, attempt, pc_mode, phase):
    return {
        "arm": arm, "seed": seed, "phase": phase, "attempt": attempt,
        "pc_mode": pc_mode, "params": {kk: (list(v) if isinstance(v, (list, tuple)) else v)
                                        for kk, v in PARAMS.items()},
        "world_meta": world["meta"], "per_k": per_k,
        "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def check_simulation(world, seed):
    """Empirical mean of y over a big batch vs P f (one fault) -- instrument sanity."""
    rng = np.random.default_rng([seed, 77])
    f = sparse_faults(rng, 3, 1)
    Fb = np.repeat(f, 400, axis=0)
    Y = simulate_y(world, Fb, rng)
    emp_mean = Y.mean(axis=0)
    pred = world["P"] @ f[0]
    emp_cov = np.cov((Y - pred).T)
    return {
        "mean_err_rel": float(np.linalg.norm(emp_mean - pred) / np.linalg.norm(pred)),
        "whitened_cov_diag_mean": float(np.mean(np.diag(emp_cov))),
        "whitened_cov_offdiag_absmax": float(np.max(np.abs(emp_cov - np.diag(np.diag(emp_cov))))),
    }


def append_row(path, row):
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
        fh.flush()
