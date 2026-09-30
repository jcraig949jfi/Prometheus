"""W6 Pass 4: generalised carrier (map scale r, additive common noise sigma).

v_i' = (1-KAPPA-eps) r T(v_i) + KAPPA v_p v_q + eps mean_j r T(v_j) + sigma xi_i,
clipped to [-1, 1] only when sigma > 0 (so r = 1, sigma = 0 IS controls.py's
world, bit for bit). Readouts, clustering and ARI are imported from the frozen
controls.py. Generic: no arm is run here.
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import controls as C  # frozen, read-only

LLE_STEPS = 2000
NOISE_SEED_BASE = 10000


def dT(v):
    return 12.0 * v ** 2 - 3.0


def step(V, P, eps, r):
    if r == 1.0:
        TV = C.T(V)
    else:
        TV = r * C.T(V)
    return (1.0 - C.KAPPA - eps) * TV + C.KAPPA * V[..., P[:, 0]] * V[..., P[:, 1]] \
        + eps * TV.mean(axis=-1, keepdims=True)


def noise(seed, n, sigma):
    if sigma == 0.0:
        return np.zeros((n, C.N))
    return sigma * np.random.default_rng(NOISE_SEED_BASE + seed).standard_normal((n, C.N))


def trajectory(v0, P, eps, r, xi, sigma):
    n = xi.shape[0]
    out = np.empty((n, C.N))
    v = v0.copy()
    for t in range(n):
        v = step(v, P, eps, r)
        if sigma > 0:
            v = np.clip(v + xi[t], -1.0, 1.0)
        out[t] = v
    return out


def ftle_matrix(traj, P, eps, r, xi, sigma):
    bidx = C.BURN + C.SPACING * np.arange(C.K)
    ref = traj[bidx].copy()
    pert = np.repeat(ref[:, None, :], C.N, axis=1)
    idx = np.arange(C.N)
    pert[:, idx, idx] += C.DELTA
    for s in range(1, C.TAU + 1):
        ref = step(ref, P, eps, r)
        pert = step(pert, P, eps, r)
        if sigma > 0:
            z = xi[bidx + s]                      # common noise, as in the trajectory
            ref = np.clip(ref + z, -1.0, 1.0)
            pert = np.clip(pert + z[:, None, :], -1.0, 1.0)
    d = np.abs(pert - ref[:, None, :])
    return np.log10(d + 1e-18).mean(axis=0)


def lle(traj, P, eps, r, xi, sigma):
    """largest Lyapunov exponent (per step, natural log) along the trajectory."""
    w = np.ones(C.N) / np.sqrt(C.N)
    tot = 0.0
    a = (1.0 - C.KAPPA - eps) * r
    for t in range(C.BURN, C.BURN + LLE_STEPS):
        v = traj[t]
        J = np.diag(a * dT(v))
        rows = np.arange(C.N)
        J[rows, P[:, 0]] += C.KAPPA * v[P[:, 1]]
        J[rows, P[:, 1]] += C.KAPPA * v[P[:, 0]]
        J += eps * r * dT(v)[None, :] / C.N
        if sigma > 0:
            nxt = traj[t + 1]
            J[np.abs(nxt) >= 1.0, :] = 0.0       # clipped coordinates
        w = J @ w
        nrm = np.linalg.norm(w)
        if nrm == 0.0:
            return -np.inf
        tot += np.log(nrm)
        w /= nrm
    return tot / LLE_STEPS


def run(arm, seed, P, eps, r, sigma, extra=None):
    rng = np.random.default_rng(seed)
    v0 = rng.uniform(-1, 1, C.N)
    n = C.BURN + max(C.L, C.SPACING * C.K + C.TAU + 1, LLE_STEPS + 1)
    n_orig = C.BURN + max(C.L, C.SPACING * C.K + C.TAU + 1)
    assert n == n_orig  # trajectory length identical to controls.py
    xi = noise(seed, n, sigma)
    traj = trajectory(v0, P, eps, r, xi, sigma)
    D = ftle_matrix(traj, P, eps, r, xi, sigma)
    Sf = D + D.T
    np.fill_diagonal(Sf, np.nan)
    Sf = np.where(np.isnan(Sf), np.nanmax(Sf), Sf)
    part_f = C.average_linkage(Sf, C.G)
    Cm = C.corr_matrix(traj) if np.all(traj[C.BURN:].std(0) > 0) else np.zeros((C.N, C.N))
    part_c = C.average_linkage(Cm, C.G)
    off = ~np.eye(C.N, dtype=bool)
    same = (C.LABELS[:, None] == C.LABELS[None, :]) & off
    row = {"arm": arm, "seed": seed, "eps_g": eps, "kappa": C.KAPPA, "r": r, "sigma": sigma,
           "partners": P.tolist(),
           "partition_ftle": part_f.tolist(), "partition_corr": part_c.tolist(),
           "ari_ftle": C.ari(part_f, C.LABELS), "ari_corr": C.ari(part_c, C.LABELS),
           "ftle_within_mean": float(D[same].mean()), "ftle_between_mean": float(D[off & ~same].mean()),
           "corr_within_mean": float(Cm[same].mean()), "corr_between_mean": float(Cm[off & ~same].mean()),
           "traj_min": float(traj.min()), "traj_max": float(traj.max()),
           "traj_std_mean": float(traj[C.BURN:].std(0).mean()),
           "lle": float(lle(traj, P, eps, r, xi, sigma)),
           "params": {"N": C.N, "G": C.G, "KAPPA": C.KAPPA, "DELTA": C.DELTA, "TAU": C.TAU, "K": C.K,
                      "SPACING": C.SPACING, "BURN": C.BURN, "L": C.L, "LLE_STEPS": LLE_STEPS,
                      "noise_seed": NOISE_SEED_BASE + seed if sigma > 0 else None,
                      "clip": sigma > 0}}
    if extra:
        row.update(extra)
    return row


def spearman(x, y):
    from scipy.stats import rankdata
    rx, ry = rankdata(x), rankdata(y)
    if np.std(rx) == 0 or np.std(ry) == 0:
        return 0.0
    return float(np.corrcoef(rx, ry)[0, 1])
