"""HT-056d3ac561 / W5 probe round 3: TREATMENT (stride-MR sparse reopening)
plus rerun of every frozen control arm, in the controls.py code path.
Writes probe/rows.jsonl (one row per (arm, seed), flushed) and
probe/calibration.json.  See NOTES.md for the readings chosen."""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import json, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import controls as C  # frozen; main() is never called

OUT = os.path.join(HERE, "rows.jsonl")
CAL_OUT = os.path.join(HERE, "calibration.json")
MR_W = 10          # last 10 even steps
FLOOR = 1e-8
MR_Q = 0.95        # calibration quantile (spec)


def mr_fn(z, x0, h, record=False):
    """Treatment reopen_fn for controls.run_filter.  Carries the stride-2
    filter.  If record, alarms are disabled and the per-run max over
    components and even t in [BURN, TC) of S_j is kept in st['smax']."""
    runs = z.shape[0]
    st = {"xh2": x0.copy(), "P2": np.full((runs, C.N), C.PSS),
          "buf": np.zeros((runs, C.N, MR_W)), "n": np.zeros((runs, C.N), int),
          "k": 0, "smax": np.full(runs, -np.inf)}

    def f(t, s):
        if t % 2:
            return None
        e, S = s["e"], s["S"]
        Pm1 = S - C.R
        xprev1 = z[:, t] - e
        # tentative stride-1 posterior at t
        K1 = Pm1 / S
        xh1 = xprev1 + K1 * e
        P1 = (1 - K1) * Pm1
        # tentative stride-2 posterior at t (2-step model)
        P2m = st["P2"] + 2 * C.Q
        e2 = z[:, t] - st["xh2"]
        S2 = P2m + C.R
        K2 = P2m / S2
        xh2 = st["xh2"] + K2 * e2
        P2 = (1 - K2) * P2m
        zz = (xh1 - xh2) / np.sqrt(np.maximum(P2 - P1, FLOOR))
        slot = st["k"] % MR_W
        st["k"] += 1
        st["buf"][:, :, slot] = zz ** 2
        st["n"] += 1
        Ssum = st["buf"].sum(axis=2)
        full = st["n"] >= MR_W
        if record:
            if C.BURN <= t < C.TC:
                st["smax"] = np.maximum(st["smax"], np.where(full, Ssum, -np.inf).max(axis=1))
            fire = np.zeros_like(full)
        else:
            fire = full & (Ssum > h) & (t >= C.BURN)
        if fire.any():
            P2m = P2m + C.RHO * fire
            S2 = P2m + C.R
            K2 = P2m / S2
            xh2 = st["xh2"] + K2 * e2
            P2 = (1 - K2) * P2m
            st["buf"][fire] = 0.0     # clear alarmed components' windows
            st["n"][fire] = 0
        st["xh2"], st["P2"] = xh2, P2
        return fire if fire.any() else None

    f.st = st
    return f


def calibrate_mr():
    rng = np.random.default_rng(C.CAL_SEED)
    x, z, chg, x0 = C.make_data(rng, C.CAL_RUNS, jump=False)
    fn = mr_fn(z, x0, np.inf, record=True)
    C.run_filter(z, x0, fn)
    mx = fn.st["smax"]
    return float(np.quantile(mx, MR_Q)), mx


def main():
    t0 = time.process_time(); w0 = time.time()
    open(OUT, "w").close()
    h_nis = C.calibrate_nis()
    h_mr, mx = calibrate_mr()
    json.dump({"h_NIS": h_nis, "h_MR": h_mr, "cal_seed": C.CAL_SEED,
               "cal_runs": C.CAL_RUNS, "quantile": MR_Q,
               "h_MR_run_max_summary": {"min": float(mx.min()), "median": float(np.median(mx)),
                                        "max": float(mx.max())}},
              open(CAL_OUT, "w"), indent=1)
    params = {"N": C.N, "Q": C.Q, "R": C.R, "T": C.T, "TC": C.TC, "BURN": C.BURN,
              "J": C.J, "KCHG": C.KCHG, "RHO": C.RHO, "BAND": C.BAND, "RUN": C.RUN,
              "NIS_W": C.NIS_W, "MR_W": MR_W, "floor": FLOOR, "h_NIS": h_nis, "h_MR": h_mr}
    with open(OUT, "a") as fo:
        for seed in C.SEEDS:
            rng = np.random.default_rng(seed)
            x, z, chg, x0 = C.make_data(rng, C.RUNS)
            arms = {}
            est, al = C.run_filter(z, x0, C.oracle_fn(chg)); arms["POSITIVE_CONTROL"] = (C.latency(x, est, chg), C.fa_flag(al), C.mse_unchanged(x, est, chg), al)
            est, al = C.run_filter(z, x0, C.twin_fn(np.random.default_rng(10_000 + seed), C.RUNS)); arms["NULL_TWIN"] = (C.latency(x, est, chg), C.fa_flag(al), C.mse_unchanged(x, est, chg), al)
            est, al = C.run_filter(z, x0, C.nis_fn(h_nis)); arms["REFERENCE_NIS"] = (C.latency(x, est, chg), C.fa_flag(al), C.mse_unchanged(x, est, chg), al)
            est, al = C.run_filter(z, x0, lambda t, s: None); arms["NO_REOPEN"] = (C.latency(x, est, chg), C.fa_flag(al), C.mse_unchanged(x, est, chg), al)
            arms["CHEAT"] = (np.zeros(C.RUNS), np.zeros(C.RUNS), arms["NO_REOPEN"][2], [[] for _ in range(C.RUNS)])
            est, al = C.run_filter(z, x0, mr_fn(z, x0, h_mr)); arms["TREATMENT"] = (C.latency(x, est, chg), C.fa_flag(al), C.mse_unchanged(x, est, chg), al)
            for arm, (lat, fa, mu, al) in arms.items():
                nre = [len(a) for a in al]
                first_post = [min([a for a in als if a >= C.TC], default=None) for als in al]
                row = {"arm": arm, "seed": seed, "runs": C.RUNS,
                       "latencies": lat.tolist(), "fa_flags": fa.tolist(),
                       "median_latency": float(np.median(lat)),
                       "fa_fraction": float(fa.mean()),
                       "mse_unchanged_mean": float(mu.mean()),
                       "n_reopen_events_mean": float(np.mean(nre)),
                       "first_reopen_at_or_after_tc": first_post,
                       "params": params}
                fo.write(json.dumps(row) + "\n"); fo.flush()
    cpu = time.process_time() - t0
    json.dump({"cpu_s": cpu, "wall_s": time.time() - w0}, open(os.path.join(HERE, "cost.json"), "w"))
    print("cpu_s", round(cpu, 1), "h_NIS", round(h_nis, 3), "h_MR", round(h_mr, 3))


if __name__ == "__main__":
    main()
