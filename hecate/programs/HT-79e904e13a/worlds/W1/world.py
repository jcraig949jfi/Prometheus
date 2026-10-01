"""PHASE 2: TREATMENT and CONTROL on the stochastic gLV (plus rerun of the
three pilot arms via the same pilot code path). Writes rows.jsonl."""
import sys, time
from scipy.optimize import fsolve
from common import *  # noqa
from pilot import run_pilot_arms

GLV_SIGMA = 0.02
BURN = 50_000
FOCAL = 11
OUT = os.path.join(HERE, "rows.jsonl")


def lam_of_m(A, x0, v, m):
    return lead_re(np.diag(x0 + m * v) @ A)


def build_glv(seed):
    """Return A, x0, r0, v, {d: (m_d, x*_d)} and the draw index used."""
    for draw in range(50):
        A, x0 = community(seed, draw)
        r0 = -A @ x0
        v = np.linalg.solve(A, np.eye(N_SP)[:, FOCAL])  # x*(m) = x0 + m v
        ms = np.linspace(-20, 20, 4001)
        valid = np.array([np.all(x0 + m * v > 0) for m in ms])
        ms = ms[valid]
        lam = np.array([lam_of_m(A, x0, v, m) for m in ms])
        i0 = int(np.argmin(lam))
        if lam[i0] > -0.5:
            continue
        out, ok = {}, True
        for d in DISTANCES:
            idx = np.where((lam[i0:-1] <= d) & (lam[i0 + 1:] > d))[0]
            if len(idx) == 0:
                ok = False
                break
            j = i0 + int(idx[0])
            lo, hi = ms[j], ms[j + 1]
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                if lam_of_m(A, x0, v, mid) <= d:
                    lo = mid
                else:
                    hi = mid
            m = 0.5 * (lo + hi)
            xs = x0 + m * v
            if not np.all(xs > 0):
                ok = False
                break
            out[d] = (m, xs)
        if ok:
            return A, x0, r0, v, out, draw
    raise RuntimeError(f"seed {seed}: no draw reaches all distances")


def simulate_glv(As, rs, xss, rng_list, n=N_OBS, burn=BURN):
    """Batched gLV with CRN: run 0 unpressed (observational), run k+1 pressed
    on species k. Returns obs (n,S,N) float32 and mean abundance (S,13,N)."""
    S = len(As)
    Ab = np.stack(As)
    r = np.stack(rs)[:, None, :]
    xs = np.stack(xss)
    I = np.zeros((S, N_SP + 1, N_SP))
    for k in range(N_SP):
        I[:, k + 1, k] = PRESS * xs[:, k]
    x = np.repeat(xs[:, None, :], N_SP + 1, axis=1).copy()
    obs = np.empty((n, S, N_SP), dtype=np.float32)
    acc = np.zeros_like(x)
    sq = GLV_SIGMA * np.sqrt(DT)
    CH = 5000
    total = burn + n
    for c0 in range(0, total, CH):
        m = min(CH, total - c0)
        noise = np.stack([g.standard_normal((m, N_SP)) for g in rng_list], axis=1) * sq
        for t in range(m):
            drift = x * (r + np.einsum("sij,srj->sri", Ab, x)) + I
            x = x + DT * drift + x * noise[t][:, None, :]
            np.maximum(x, 1e-9, out=x)
            tt = c0 + t - burn
            if tt >= 0:
                obs[tt] = x[:, 0, :]
                acc += x
    return obs, acc / n


def det_shift(A, r, xs, k):
    I = np.zeros(N_SP)
    I[k] = PRESS * xs[k]
    f = lambda x: x * (r + A @ x) + I
    xn = fsolve(f, xs, xtol=1e-12)
    return xn - xs


def main():
    t0c, t0w = time.process_time(), time.time()
    if os.path.exists(OUT):
        raise SystemExit("rows.jsonl exists; refusing to overwrite")
    built = {s: build_glv(s) for s in SEEDS}
    keys = ("TREATMENT", "CONTROL", "ORACLE", "SE1_ABUNDANCE", "SE2_DIAGONAL",
            "DET_VS_STOCH", "SE4_LINEAR_VS_EXACT")
    acc = {a: {s: {} for s in SEEDS} for a in keys}
    extra = {s: {"imag": {}, "imag_control": {}, "min_x_over_xstar": {}, "m": {}} for s in SEEDS}
    for di, d in enumerate(DISTANCES):
        As, rs, xss = [], [], []
        for s in SEEDS:
            A, x0, r0, v, dm, draw = built[s]
            m, xs = dm[d]
            As.append(A); xss.append(xs)
            rs.append(r0 - m * np.eye(N_SP)[FOCAL])
        rngs = [np.random.default_rng([s, di, 505]) for s in SEEDS]
        obs, means = simulate_glv(As, rs, xss, rngs)
        for si, s in enumerate(SEEDS):
            A, xs, r = As[si], xss[si], rs[si]
            true = (means[si, 1:, :] - means[si, 0, :]).T  # column k = press k
            Jt = np.diag(xs) @ A
            Jh, im = estimate_J(obs[:, si, :])
            acc["TREATMENT"][s][str(d)] = press_spearmans(predict_responses(Jh, xs), true)
            Xn = circular_shift(obs[:, si, :], np.random.default_rng([s, di, 303]))
            Jn, imn = estimate_J(Xn)
            acc["CONTROL"][s][str(d)] = press_spearmans(predict_responses(Jn, xs), true)
            acc["ORACLE"][s][str(d)] = press_spearmans(predict_responses(Jt, xs), true)
            acc["SE1_ABUNDANCE"][s][str(d)] = press_spearmans(np.repeat(xs[:, None], N_SP, 1), true)
            acc["SE2_DIAGONAL"][s][str(d)] = press_spearmans(predict_responses(np.diag(np.diag(Jh)), xs) + 0.0, true)
            det = np.stack([det_shift(A, r, xs, k) for k in range(N_SP)], axis=1)
            acc["DET_VS_STOCH"][s][str(d)] = press_spearmans(det, true)
            acc["SE4_LINEAR_VS_EXACT"][s][str(d)] = press_spearmans(predict_responses(Jt, xs), det)
            extra[s]["imag"][str(d)] = im
            extra[s]["imag_control"][str(d)] = imn
            extra[s]["min_x_over_xstar"][str(d)] = float(np.min(obs[:, si, :].min(axis=0) / xs))
            extra[s]["m"][str(d)] = float(built[s][4][d][0])
        del obs
    params = {"N_SP": N_SP, "DT": DT, "N_OBS": N_OBS, "BURN": BURN, "TAU": TAU,
              "DISTANCES": DISTANCES, "PRESS": PRESS, "GLV_SIGMA": GLV_SIGMA, "FOCAL": FOCAL,
              "substrate": "stochastic gLV, multiplicative noise, CRN press runs"}
    for a in keys:
        for s in SEEDS:
            append_row(OUT, {"tag": "phase2", "attempt": 1, "arm": a, "seed": s,
                             "spearman": acc[a][s], "glv_draw": built[s][5],
                             "logm_max_imag": extra[s]["imag_control" if a == "CONTROL" else "imag"],
                             "min_x_over_xstar": extra[s]["min_x_over_xstar"],
                             "mortality_m": extra[s]["m"], "params": params})
    run_pilot_arms(out_path=OUT, attempt=2, tag="phase2_pilot_rerun")
    print(log_cpu("world.py", t0c, t0w))


if __name__ == "__main__":
    main()
