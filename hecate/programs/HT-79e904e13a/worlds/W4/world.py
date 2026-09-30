"""HT-79e904e13a / W4 world: backtracking vs forward counterfactual identifiability.

Arms: TREATMENT, CONTROL, NULL_TWIN, POSITIVE_CONTROL, CHEAT.
Writes rows.jsonl (one JSON object per (arm, level, seed)), flushed per row.
See IMPLEMENTATION_NOTES.md for every parameter's rationale.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import json
import time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")

# ---- frozen parameters (IMPLEMENTATION_NOTES.md) ----
RHO = np.array([3.3, 2.2, 1.8])
ALPHA = 0.05
D_LEVELS = [float(x) for x in np.linspace(0.0, 0.21, 8)]
NG = 47                      # 47^3 = 103,823 grid points
TMAX = 30
SEEDS = list(range(10))
K_FWD = 64
LY_TRANS, LY_STEPS = 500, 4000
TW_K = np.linspace(0.02, 1.5, 150)
TW_STARTS, TW_STEPS = 8, 3000
PC_SIGMA = 0.95
PC_RATE = float(-3 * np.log(PC_SIGMA))
ARM_CODE = {"TREATMENT": 1, "CONTROL": 2, "NULL_TWIN": 3, "POSITIVE_CONTROL": 4, "CHEAT": 5}

T0 = time.process_time()


def cpu_s():
    return time.process_time() - T0


# ---------------- maps ----------------
def ricker(X, d):
    """X: (..., 3). Coupled Ricker with relaxation d."""
    s = X.sum(axis=-1, keepdims=True)
    others = s - X
    E = np.exp(RHO * (1.0 - X - ALPHA * others))
    return (1.0 - d) * X * E + d


def ricker_jac(x, d):
    """x: (B,3) -> J: (B,3,3)."""
    s = x.sum(axis=-1, keepdims=True)
    E = np.exp(RHO * (1.0 - x - ALPHA * (s - x)))
    B = x.shape[0]
    J = np.empty((B, 3, 3))
    for i in range(3):
        for j in range(3):
            if i == j:
                J[:, i, j] = (1 - d) * E[:, i] * (1 - RHO[i] * x[:, i])
            else:
                J[:, i, j] = (1 - d) * E[:, i] * x[:, i] * (-RHO[i] * ALPHA)
    return J


TWO_PI = 2 * np.pi


def twin(X, k):
    """Volume-preserving shear map on unit 3-torus. k scalar or broadcastable."""
    x1 = np.mod(X[..., 0] + k * np.sin(TWO_PI * X[..., 1]), 1.0)
    x2 = np.mod(X[..., 1] + k * np.sin(TWO_PI * X[..., 2]), 1.0)
    x3 = np.mod(X[..., 2] + k * np.sin(TWO_PI * x1), 1.0)
    return np.stack([x1, x2, x3], axis=-1)


def twin_jac(x, k):
    """x: (B,3), k: (B,) -> J (B,3,3) = J3 J2 J1."""
    B = x.shape[0]
    J1 = np.tile(np.eye(3), (B, 1, 1))
    J1[:, 0, 1] = TWO_PI * k * np.cos(TWO_PI * x[:, 1])
    J2 = np.tile(np.eye(3), (B, 1, 1))
    J2[:, 1, 2] = TWO_PI * k * np.cos(TWO_PI * x[:, 2])
    x1n = np.mod(x[:, 0] + k * np.sin(TWO_PI * x[:, 1]), 1.0)
    J3 = np.tile(np.eye(3), (B, 1, 1))
    J3[:, 2, 0] = TWO_PI * k * np.cos(TWO_PI * x1n)
    return J3 @ J2 @ J1


def lyap(step, jac, x0, steps, trans):
    """Batched Lyapunov spectrum by QR. Returns (lam (B,3) sorted desc, mean log|det| (B,))."""
    x = x0.copy()
    for _ in range(trans):
        x = step(x)
    B = x.shape[0]
    Q = np.tile(np.eye(3), (B, 1, 1))
    acc = np.zeros((B, 3))
    ldet = np.zeros(B)
    for _ in range(steps):
        J = jac(x)
        ldet += np.log(np.abs(np.linalg.det(J)) + 1e-300)
        Q, Rm = np.linalg.qr(J @ Q)
        diag = np.abs(np.diagonal(Rm, axis1=1, axis2=2))
        acc += np.log(diag + 1e-300)
        x = step(x)
    lam = np.sort(acc / steps, axis=1)[:, ::-1]
    return lam, ldet / steps


# ---------------- grid + backward query ----------------
def make_grid(lo, side, rng):
    h = side / NG
    off = rng.uniform(0, 1, size=3)
    ax = [lo + (np.arange(NG) + off[a]) * h for a in range(3)]
    G = np.stack(np.meshgrid(*ax, indexing="ij"), axis=-1).reshape(-1, 3)
    return G, h ** 3, off


def unit(rng, n=None):
    v = rng.normal(size=(3,) if n is None else (n, 3))
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def backward_series(G, ref_idx, step, r, delta, rng, periodic=False):
    """Returns N_match(T) for T=1..TMAX and count of infeasible images (any coord <= 0)."""
    u = unit(rng)
    X = G.copy()
    counts, infeasible = [], []
    for _ in range(TMAX):
        X = step(X)
        target = X[ref_idx] + delta * u
        diff = X - target
        if periodic:
            target = np.mod(target, 1.0)
            diff = X - target
            diff -= np.round(diff)
        d2 = np.einsum("ij,ij->i", diff, diff)
        counts.append(int((d2 <= r * r).sum()))
        infeasible.append(int((X <= 0).any(axis=1).sum()) if not periodic else 0)
    return counts, infeasible, u.tolist()


def forward_series(x0, step, delta, rng, periodic=False):
    U = unit(rng, K_FWD)
    if not periodic:
        # attempt-2 bug fix: resample directions that would start outside the
        # feasible (positive) region; negative Ricker states diverge to inf.
        bad = np.any(x0[None, :] + delta * U <= 0, axis=1)
        while bad.any():
            U[bad] = unit(rng, int(bad.sum()))
            bad = np.any(x0[None, :] + delta * U <= 0, axis=1)
    C = x0[None, :] + delta * U
    xr = x0.copy()[None, :]
    if periodic:
        C = np.mod(C, 1.0)
    out = []
    for _ in range(TMAX):
        C = step(C)
        xr = step(xr)
        diff = C - xr
        if periodic:
            diff -= np.round(diff)
        out.append(float(0.5 * np.log(np.mean(np.einsum("ij,ij->i", diff, diff)) + 1e-300)))
    return out


def rng_for(arm, level, seed):
    return np.random.default_rng([ARM_CODE[arm], level, seed])


# ---------------- main ----------------
def main():
    if os.path.exists(ROWS):
        raise SystemExit("rows.jsonl exists; refusing to overwrite (attempts are recorded by hand)")
    fh = open(ROWS, "w", encoding="utf-8")

    def write(row):
        row["cpu_s_cumulative"] = round(cpu_s(), 3)
        fh.write(json.dumps(row) + "\n")
        fh.flush()

    common = {"rho": RHO.tolist(), "alpha": ALPHA, "ng": NG, "n_grid": NG ** 3, "tmax": TMAX}

    # ---- treatment Lyapunov / contraction per (level, seed) ----
    lyap_treat = {}
    for li, d in enumerate(D_LEVELS):
        starts = np.stack([rng_for("TREATMENT", li, s).uniform(0.2, 2.0, size=3) for s in SEEDS])
        lam, mld = lyap(lambda x: ricker(x, d), lambda x: ricker_jac(x, d), starts, LY_STEPS, LY_TRANS)
        lyap_treat[li] = (lam, mld)

    # ---- twin k-grid lambda_max table ----
    kk = np.repeat(TW_K, TW_STARTS)
    tw_rng = np.random.default_rng([ARM_CODE["NULL_TWIN"], 999])
    tw_starts = tw_rng.uniform(0, 1, size=(kk.size, 3))
    lam_tw, _ = lyap(lambda x: _twin_vec(x, kk), lambda x: twin_jac(x, kk), tw_starts, TW_STEPS, 200)
    lmax_table = lam_tw[:, 0].reshape(TW_K.size, TW_STARTS).mean(axis=1)

    # ---- TREATMENT + CONTROL ----
    side_t, lo_t = 3.0, 0.0
    r_t = side_t / 30
    delta_t = r_t / 2
    for li, d in enumerate(D_LEVELS):
        lam, mld = lyap_treat[li]
        step = lambda X, d=d: ricker(X, d)
        for s in SEEDS:
            rng = rng_for("TREATMENT", li, s)
            _ = rng.uniform(0.2, 2.0, size=3)  # consumed by Lyapunov start
            G, cellv, off = make_grid(lo_t, side_t, rng)
            ref = int(rng.integers(G.shape[0]))
            counts, infeas, u = backward_series(G, ref, step, r_t, delta_t, rng)
            write({"arm": "TREATMENT", "level": li, "d": d, "seed": s, **common,
                   "domain_lo": lo_t, "domain_side": side_t, "r": r_t, "delta": delta_t,
                   "grid_offset": off.tolist(), "ref_idx": ref, "ref_x0": G[ref].tolist(), "perturb_dir": u,
                   "log_cell_volume": float(np.log(cellv)), "n_match": counts,
                   "H": [float(np.log(c) + np.log(cellv)) for c in counts],
                   "n_infeasible_images": infeas,
                   "lyap": lam[s].tolist(), "lambda_max": float(lam[s, 0]),
                   "net_contraction": float(-mld[s]), "net_contraction_qr": float(-lam[s].sum())})
            rngc = rng_for("CONTROL", li, s)
            fwd = forward_series(G[ref], step, delta_t, rngc)
            write({"arm": "CONTROL", "level": li, "d": d, "seed": s, **common, "r": r_t, "delta": delta_t,
                   "ref_x0": G[ref].tolist(), "k_fwd": K_FWD, "log_spread": fwd,
                   "net_contraction": float(-mld[s]), "lambda_max": float(lam[s, 0])})

    # ---- NULL_TWIN ----
    side_w, lo_w = 1.0, 0.0
    r_w = side_w / 30
    delta_w = r_w / 2
    for li, d in enumerate(D_LEVELS):
        lam, mld = lyap_treat[li]
        target = float(lam[:, 0].mean())
        ki = int(np.argmin(np.abs(lmax_table - target)))
        k = float(TW_K[ki])
        starts = np.stack([rng_for("NULL_TWIN", li, s).uniform(0, 1, size=3) for s in SEEDS])
        lamw, mldw = lyap(lambda x: twin_k(x, k), lambda x: twin_jac(x, np.full(x.shape[0], k)),
                          starts, LY_STEPS, LY_TRANS)
        step = lambda X, k=k: twin_k(X, k)
        for s in SEEDS:
            rng = rng_for("NULL_TWIN", li, s)
            _ = rng.uniform(0, 1, size=3)
            G, cellv, off = make_grid(lo_w, side_w, rng)
            ref = int(rng.integers(G.shape[0]))
            counts, _inf, u = backward_series(G, ref, step, r_w, delta_w, rng, periodic=True)
            write({"arm": "NULL_TWIN", "level": li, "d_matched": d, "seed": s, "k": k,
                   "lambda_max_target_level_mean": target, "lambda_max_table_at_k": float(lmax_table[ki]),
                   "ng": NG, "n_grid": NG ** 3, "tmax": TMAX,
                   "domain_lo": lo_w, "domain_side": side_w, "r": r_w, "delta": delta_w,
                   "grid_offset": off.tolist(), "ref_idx": ref, "perturb_dir": u,
                   "log_cell_volume": float(np.log(cellv)), "n_match": counts,
                   "H": [float(np.log(c) + np.log(cellv)) for c in counts],
                   "lyap": lamw[s].tolist(), "lambda_max": float(lamw[s, 0]),
                   "net_contraction": float(-mldw[s])})

    # ---- POSITIVE_CONTROL ----
    side_p, lo_p = 2.0, -1.0
    r_p = side_p / 30
    delta_p = r_p / 2
    for s in SEEDS:
        rng = rng_for("POSITIVE_CONTROL", 0, s)
        Qr, Rr = np.linalg.qr(rng.normal(size=(3, 3)))
        Qr = Qr * np.sign(np.diag(Rr))
        if np.linalg.det(Qr) < 0:
            Qr[:, 0] *= -1
        A = PC_SIGMA * Qr
        G, cellv, off = make_grid(lo_p, side_p, rng)
        inner = np.where(np.all(np.abs(G) < 0.3, axis=1))[0]
        ref = int(inner[rng.integers(inner.size)])
        step = lambda X, A=A: X @ A.T
        counts, _inf, u = backward_series(G, ref, step, r_p, delta_p, rng)
        sv = np.linalg.svd(A, compute_uv=False)
        write({"arm": "POSITIVE_CONTROL", "level": 0, "seed": s, "ng": NG, "n_grid": NG ** 3, "tmax": TMAX,
               "A": A.tolist(), "known_rate": float(-np.log(sv).sum()),
               "domain_lo": lo_p, "domain_side": side_p, "r": r_p, "delta": delta_p,
               "grid_offset": off.tolist(), "ref_idx": ref, "perturb_dir": u,
               "log_cell_volume": float(np.log(cellv)), "n_match": counts,
               "H": [float(np.log(c) + np.log(cellv)) for c in counts]})

    # ---- CHEAT: success injected into the observable, bypassing every map ----
    for li, d in enumerate(D_LEVELS):
        lam, mld = lyap_treat[li]
        for s in SEEDS:
            C = float(-mld[s])
            H0 = float(np.log(15.0) + np.log((3.0 / NG) ** 3))
            write({"arm": "CHEAT", "level": li, "d": d, "seed": s,
                   "H": [H0 + C * T for T in range(1, TMAX + 1)],
                   "H_twin": [H0 for _ in range(1, TMAX + 1)],
                   "net_contraction": C, "lambda_max": float(lam[s, 0]),
                   "note": "synthetic series H = H0 + C*T; twin flat"})
    fh.close()
    print("done cpu_s", round(cpu_s(), 2))


def twin_k(X, k):
    return twin(X, k)


def _twin_vec(X, k):
    x1 = np.mod(X[:, 0] + k * np.sin(TWO_PI * X[:, 1]), 1.0)
    x2 = np.mod(X[:, 1] + k * np.sin(TWO_PI * X[:, 2]), 1.0)
    x3 = np.mod(X[:, 2] + k * np.sin(TWO_PI * x1), 1.0)
    return np.stack([x1, x2, x3], axis=-1)


if __name__ == "__main__":
    main()
