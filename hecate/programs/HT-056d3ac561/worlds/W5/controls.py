"""HT-056d3ac561 / W5 -- controls only (no treatment code).

World: 8 independent random-walk states, identity observation, filter
correctly specified but overconfident by design (tiny Q -> gain ~0.01,
"collapsed").  At t_c two of eight states jump by +/-J (sparse regime
change).  Every arm that "reopens" does so by the SAME action: add RHO to
the filter variance P_jj of the chosen components at the chosen step.
Arms differ only in WHEN and WHICH components are reopened.

Arms written here:
  POSITIVE_CONTROL  oracle reopening: at exactly t_c, on exactly the two
                    changed components (effect present by construction).
  CHEAT             the observable itself overwritten with success
                    (latency 0, no false alarm).
  NULL_TWIN         one reopening of two components at a uniformly random
                    step in [BURN, T) on two uniformly random components:
                    same action count, size and sparsity as the oracle,
                    relation to the change destroyed.
  REFERENCE_NIS     the spec's CONTROL (not the treatment): windowed-NIS
                    alarm, threshold calibrated on separate calibration
                    seeds to a 5% pre-change run-level false-alarm rate,
                    isotropic reopening of all 8 components.  Needed here
                    because clause S3 is a ratio to it.

All arms of one seed run on the same true trajectories and noise.
Rows: control_rows.jsonl, one row per (arm, seed), flushed per row.
"""
import json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "control_rows.jsonl")

# ---- world constants (frozen with the spec) -----------------------------
N = 8            # state dim
Q = 1e-4         # true AND model process noise variance per component
R = 1.0          # measurement noise variance per component
T = 600          # steps
TC = 300         # change step (jump applied to x_TC)
BURN = 50        # false alarms counted in [BURN, TC)
J = 1.5          # jump magnitude (sign random)
KCHG = 2         # changed components
RHO = 1.0        # reopening action: P_jj += RHO
BAND = 0.5       # recovered when |err| <= BAND*J ...
RUN = 10         # ... on every changed component for RUN consecutive steps
CAP = T - TC - RUN   # latency cap (never recovered)
NIS_W = 20       # NIS window
FA_TARGET = 0.05
RUNS = 200       # runs per seed
SEEDS = [0, 1, 2, 3, 4]
CAL_SEED = 999   # calibration seed (NIS threshold), disjoint from SEEDS
CAL_RUNS = 1000


def p_steady():
    p = 1.0
    for _ in range(10000):
        pm = p + Q
        p = pm * R / (pm + R)
    return p


PSS = p_steady()


def make_data(rng, runs, jump=True):
    x = np.zeros((runs, T, N))
    w = rng.normal(0, np.sqrt(Q), (runs, T, N))
    x = np.cumsum(w, axis=1)
    chg = np.zeros((runs, N), bool)
    if jump:
        for i in range(runs):
            c = rng.choice(N, KCHG, replace=False)
            chg[i, c] = True
        sgn = rng.choice([-1.0, 1.0], (runs, N))
        x[:, TC:, :] += (chg * sgn * J)[:, None, :]
    z = x + rng.normal(0, np.sqrt(R), (runs, T, N))
    x0hat = x[:, 0, :] + rng.normal(0, np.sqrt(PSS), (runs, N))
    return x, z, chg, x0hat


def run_filter(z, x0hat, reopen_fn):
    """reopen_fn(t, state) -> bool mask (runs,N) of components to reopen
    BEFORE the update at step t.  Returns estimates and alarm times."""
    runs = z.shape[0]
    xh = x0hat.copy()
    P = np.full((runs, N), PSS)
    est = np.zeros_like(z)
    est[:, 0] = xh
    alarms = [[] for _ in range(runs)]
    state = {"nis_buf": np.zeros((runs, NIS_W)), "nis_n": np.zeros(runs, int)}
    for t in range(1, T):
        Pm = P + Q
        e = z[:, t] - xh
        S = Pm + R
        state["e"], state["S"] = e, S
        m = reopen_fn(t, state)
        if m is not None and m.any():
            Pm = Pm + RHO * m
            S = Pm + R
            for i in np.where(m.any(axis=1))[0]:
                alarms[i].append(t)
        K = Pm / S
        xh = xh + K * e
        P = (1 - K) * Pm
        est[:, t] = xh
    return est, alarms


def latency(x, est, chg):
    runs = x.shape[0]
    err = np.abs(est - x)
    out = np.full(runs, CAP, float)
    for i in range(runs):
        ok = np.all(err[i, TC:, chg[i]] <= BAND * J, axis=0)  # (T-TC,)
        for s in range(0, T - TC - RUN + 1):
            if ok[s:s + RUN].all():
                out[i] = s
                break
    return out


def mse_unchanged(x, est, chg):
    se = (est[:, TC:TC + 50, :] - x[:, TC:TC + 50, :]) ** 2
    m = ~chg[:, None, :]
    return (se * m).sum(axis=(1, 2)) / m.sum(axis=(1, 2))


def fa_flag(alarms):
    return np.array([any(BURN <= a < TC for a in al) for al in alarms], float)


# ---- arms ---------------------------------------------------------------
def oracle_fn(chg):
    def f(t, st):
        return chg if t == TC else None
    return f


def twin_fn(rng, runs):
    tt = rng.integers(BURN, T, runs)
    mask = np.zeros((runs, N), bool)
    for i in range(runs):
        mask[i, rng.choice(N, KCHG, replace=False)] = True

    def f(t, st):
        sel = (tt == t)
        if not sel.any():
            return None
        return mask & sel[:, None]
    return f


def nis_fn(h):
    def f(t, st):
        nis = np.sum(st["e"] ** 2 / st["S"], axis=1)
        buf = st["nis_buf"]
        buf[:, t % NIS_W] = nis
        st["nis_n"] += 1
        full = st["nis_n"] >= NIS_W
        fire = full & (buf.sum(axis=1) > h) & (t >= BURN)
        if not fire.any():
            return None
        buf[fire] = 0.0
        st["nis_n"][fire] = 0
        return np.repeat(fire[:, None], N, axis=1)
    return f


def calibrate_nis():
    rng = np.random.default_rng(CAL_SEED)
    x, z, chg, x0 = make_data(rng, CAL_RUNS, jump=False)
    # no-alarm filter: max windowed NIS over [BURN, TC)
    xh = x0.copy(); P = np.full((CAL_RUNS, N), PSS)
    nis = np.zeros((CAL_RUNS, TC))
    for t in range(1, TC):
        Pm = P + Q; e = z[:, t] - xh; S = Pm + R
        nis[:, t] = np.sum(e ** 2 / S, axis=1)
        K = Pm / S; xh = xh + K * e; P = (1 - K) * Pm
    cs = np.cumsum(nis, axis=1)
    win = cs[:, NIS_W:] - cs[:, :-NIS_W]          # window ending at t=NIS_W..TC-1
    ends = np.arange(NIS_W, TC)
    win = win[:, ends >= BURN]
    mx = win.max(axis=1)
    return float(np.quantile(mx, 1 - FA_TARGET))


def main():
    t0 = time.process_time()
    open(OUT, "w").close()
    h = calibrate_nis()
    with open(OUT, "a") as fo:
        for seed in SEEDS:
            rng = np.random.default_rng(seed)
            x, z, chg, x0 = make_data(rng, RUNS)
            arms = {}
            est, al = run_filter(z, x0, oracle_fn(chg)); arms["POSITIVE_CONTROL"] = (latency(x, est, chg), fa_flag(al), mse_unchanged(x, est, chg))
            est, al = run_filter(z, x0, twin_fn(np.random.default_rng(10_000 + seed), RUNS)); arms["NULL_TWIN"] = (latency(x, est, chg), fa_flag(al), mse_unchanged(x, est, chg))
            est, al = run_filter(z, x0, nis_fn(h)); arms["REFERENCE_NIS"] = (latency(x, est, chg), fa_flag(al), mse_unchanged(x, est, chg))
            est, al = run_filter(z, x0, lambda t, s: None); arms["NO_REOPEN"] = (latency(x, est, chg), fa_flag(al), mse_unchanged(x, est, chg))
            # CHEAT: success injected directly into the observable
            arms["CHEAT"] = (np.zeros(RUNS), np.zeros(RUNS), arms["NO_REOPEN"][2])
            for arm, (lat, fa, mu) in arms.items():
                row = {"arm": arm, "seed": seed, "runs": RUNS,
                       "latencies": lat.tolist(), "fa_flags": fa.tolist(),
                       "median_latency": float(np.median(lat)),
                       "fa_fraction": float(fa.mean()),
                       "mse_unchanged_mean": float(mu.mean()),
                       "nis_threshold": h, "J": J, "RHO": RHO}
                fo.write(json.dumps(row) + "\n"); fo.flush()
    print("cpu_s", round(time.process_time() - t0, 1), "h", round(h, 2))


if __name__ == "__main__":
    main()
