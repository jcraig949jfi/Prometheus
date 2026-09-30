"""Shared GM + coupling-plastic simulator for HT-faa9277e02/W1 (see NOTES.md)."""
import numpy as np

N = 48
PARAMS = dict(N=N, mu=2.0, D0=0.5, Dh=10.0, dt=0.02, steps=3000,
              eta=0.1, lam=0.1, gmin=0.2, gmax=5.0, noise=0.01,
              h_floor=1e-6, carve_z=1.0)  # carve_z: repair after pilot attempt 1 (was 0.0)


def edge_diff(a, gh, gv):
    """sum over incident edges of g_e*(a_j - a_i); no-flux open grid."""
    out = np.zeros_like(a)
    fh = gh * (a[:, 1:] - a[:, :-1])  # flux on horizontal edges
    out[:, :-1] += fh
    out[:, 1:] -= fh
    fv = gv * (a[1:, :] - a[:-1, :])
    out[:-1, :] += fv
    out[1:, :] -= fv
    return out


def init_fields(seed):
    rng = np.random.default_rng(seed)
    a = 1.0 + PARAMS["noise"] * rng.standard_normal((N, N))
    h = 1.0 + PARAMS["noise"] * rng.standard_normal((N, N))
    return a, h


def run(gh, gv, seed, plastic):
    p = PARAMS
    a, h = init_fields(seed)
    gh = gh.copy(); gv = gv.copy()
    ones_h = np.ones_like(gh); ones_v = np.ones_like(gv)
    anomalies = {"h_floor_hits": 0, "a_floor_hits": 0, "nonfinite": False}
    dt = p["dt"]
    for _ in range(p["steps"]):
        da = p["D0"] * edge_diff(a, gh, gv) + a * a / h - a
        dh = p["Dh"] * edge_diff(h, ones_h, ones_v) + p["mu"] * (a * a - h)
        if plastic:
            m2 = a.mean() ** 2
            dgh = p["eta"] * (a[:, 1:] * a[:, :-1] / m2 - 1) - p["lam"] * (gh - 1)
            dgv = p["eta"] * (a[1:, :] * a[:-1, :] / m2 - 1) - p["lam"] * (gv - 1)
            gh = np.clip(gh + dt * dgh, p["gmin"], p["gmax"])
            gv = np.clip(gv + dt * dgv, p["gmin"], p["gmax"])
        a = a + dt * da
        h = h + dt * dh
        nh = int((h < p["h_floor"]).sum()); na = int((a < 0).sum())
        if nh: anomalies["h_floor_hits"] += nh; h = np.maximum(h, p["h_floor"])
        if na: anomalies["a_floor_hits"] += na; a = np.maximum(a, 0.0)
    if not (np.isfinite(a).all() and np.isfinite(h).all()):
        anomalies["nonfinite"] = True
    return a, gh, gv, anomalies


def uniform_graph():
    return np.ones((N, N - 1)), np.ones((N - 1, N))


def phase_a(seed):
    gh, gv = uniform_graph()
    return run(gh, gv, seed, plastic=True)


def phase_b(gh, gv, seed):
    a, _, _, anom = run(gh, gv, seed + 1000, plastic=False)
    return a, anom


def carved_graph(amap, z_thresh=None):
    zt = PARAMS["carve_z"] if z_thresh is None else z_thresh
    high = (amap - amap.mean()) / amap.std() > zt
    def g_for(x, y):
        g = np.ones(x.shape)
        g[x & y] = PARAMS["gmax"]
        g[x != y] = PARAMS["gmin"]
        return g
    return g_for(high[:, 1:], high[:, :-1]), g_for(high[1:, :], high[:-1, :])


def permuted_graph(gh, gv, seed):
    rng = np.random.default_rng(seed + 2000)
    flat = np.concatenate([gh.ravel(), gv.ravel()])
    flat = flat[rng.permutation(flat.size)]
    return flat[:gh.size].reshape(gh.shape), flat[gh.size:].reshape(gv.shape)


def pearson_z(x, y):
    sx, sy = x.std(), y.std()
    if sx == 0 or sy == 0 or not (np.isfinite(sx) and np.isfinite(sy)):
        return 0.0, True
    return float(np.mean((x - x.mean()) / sx * (y - y.mean()) / sy)), False


def gstats(gh, gv):
    f = np.concatenate([gh.ravel(), gv.ravel()])
    return {"g_mean": float(f.mean()), "g_std": float(f.std()),
            "g_frac_at_min": float((f <= PARAMS["gmin"] + 1e-12).mean()),
            "g_frac_at_max": float((f >= PARAMS["gmax"] - 1e-12).mean())}
