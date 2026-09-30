"""HT-ae38c641b1 / W3 evaluator. Reads rows.jsonl only; writes OUTCOME.json."""
import json
import math
import os
import warnings

import numpy as np
from scipy.optimize import curve_fit

HERE = os.path.dirname(os.path.abspath(__file__))
WIN = list(range(10, 17))  # delta = 2^-10 .. 2^-16 (last 6 octaves)
BETA_PC = math.log(2) / math.log(3)


def aic(rss, n, k=2):
    return n * math.log(max(rss, 1e-300) / n) + 2 * k


def fit(Nd):
    ks = np.array(WIN, float)
    N = np.array([Nd[str(k)] for k in WIN], float)
    res = {"N_window": N.tolist()}
    if np.any(N <= 0):
        res.update(beta=None, r2=None, aic_pow=None, aic_log=None, aic_sat=None,
                   dAIC_log=None, dAIC_sat=None, note="N=0 in window")
        return res
    x = 2.0 ** ks
    y = np.log(N)
    lx = np.log(x)
    n = len(ks)
    # power: OLS of log N on log x  (beta = slope in log2-log2 == slope in ln-ln)
    A = np.vstack([np.ones(n), lx]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    rss_p = float(np.sum((y - pred) ** 2))
    tss = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - rss_p / tss if tss > 0 else 0.0
    beta = float(coef[1])

    def logm(xx, a, b):
        return np.log(np.maximum(a + b * np.log(xx), 1e-12))

    def satm(xx, nmax, x0):
        return np.log(np.maximum(nmax * (1 - np.exp(-xx / x0)), 1e-12))

    best_log = math.inf
    for a0, b0 in [(N[0], (N[-1] - N[0]) / (lx[-1] - lx[0]) + 1e-9), (0.0, N.mean() / lx.mean()),
                   (N.mean(), 1.0)]:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                p, _ = curve_fit(logm, x, y, p0=[a0, b0], maxfev=20000)
            best_log = min(best_log, float(np.sum((y - logm(x, *p)) ** 2)))
        except Exception:
            pass
    if not math.isfinite(best_log):
        best_log = tss
    best_sat = math.inf
    ub = [1e6 * N.max(), 1e6 * x.max()]
    for nm0, x00 in [(2 * N.max(), np.median(x)), (1.01 * N.max(), x[0]), (10 * N.max(), x[-1]),
                     (100 * N.max(), 10 * x[-1])]:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                p, _ = curve_fit(satm, x, y, p0=[min(nm0, ub[0] * 0.5), min(x00, ub[1] * 0.5)],
                                 bounds=([1e-12, 1e-12], ub), maxfev=20000)
            best_sat = min(best_sat, float(np.sum((y - satm(x, *p)) ** 2)))
        except Exception:
            pass
    if not math.isfinite(best_sat):
        best_sat = tss
    ap, al, as_ = aic(rss_p, n), aic(best_log, n), aic(best_sat, n)
    res.update(beta=beta, r2=r2, aic_pow=ap, aic_log=al, aic_sat=as_,
               dAIC_log=al - ap, dAIC_sat=as_ - ap)
    return res


def S(f):
    return (f["beta"] is not None and f["beta"] >= 0.2 and f["r2"] >= 0.95
            and f["dAIC_log"] >= 10 and f["dAIC_sat"] >= 10)


def new_frac(Nd):
    n16, n13 = Nd["16"], Nd["13"]
    return 0.0 if n16 == 0 else (n16 - n13) / n16


def main():
    rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8")]
    by = {}
    for r in rows:
        key = r["arm"] if r["arm"] not in ("TREATMENT_VARIANT", "NULL_TWIN_VARIANT") else (
            r["arm"] + ":" + json.dumps(r["config"], sort_keys=True))
        f = fit(r["N"])
        f["seed"] = r["seed"]
        f["new_frac_last3"] = new_frac(r["N"])
        f["N_all"] = r["N"]
        f["finite_frac"] = r.get("finite_frac")
        f["S"] = S(f)
        by.setdefault(key, []).append((r, f))

    def med(key, fld):
        v = [f[fld] for _, f in by[key] if f[fld] is not None]
        return float(np.median(v)) if v else None

    stats = {}
    for key, lst in by.items():
        stats[key] = {"n": len(lst), "median_beta": med(key, "beta"),
                      "median_r2": med(key, "r2"), "median_dAIC_log": med(key, "dAIC_log"),
                      "median_dAIC_sat": med(key, "dAIC_sat"),
                      "all_seeds_S": all(f["S"] for _, f in lst),
                      "per_seed": [{k: f[k] for k in ("seed", "beta", "r2", "dAIC_log",
                                                        "dAIC_sat", "new_frac_last3",
                                                        "finite_frac", "S")} for _, f in lst],
                      "N_seed0": lst[0][1]["N_all"]}

    T, NT = by["TREATMENT"], by["NULL_TWIN"]
    bT, bN = med("TREATMENT", "beta"), med("NULL_TWIN", "beta")
    nt_beta_ok = bN is None or bN < 0.1
    success = all(f["S"] for _, f in T) and nt_beta_ok
    fail_reasons = []
    if any(f["new_frac_last3"] < 0.05 for _, f in T):
        fail_reasons.append("last 3 octaves add <5% new breakpoints (some seed)")
    if any(f["dAIC_log"] is not None and -f["dAIC_log"] >= 10 for _, f in T):
        fail_reasons.append("log model wins by AIC>=10 (some seed)")
    if bT is not None and bN is not None and abs(bT - bN) < 0.1:
        fail_reasons.append("null twin beta within 0.1 of treatment")
    failure = bool(fail_reasons)
    nt_meets = all(f["S"] for _, f in NT)
    pc = all(f["beta"] is not None and abs(f["beta"] - BETA_PC) <= 0.05
             for _, f in by["POSITIVE_CONTROL"])
    cheat = all(f["S"] for _, f in by["CHEAT"])

    if not (pc and cheat):
        outcome = "INSTRUMENT_FAIL"
    elif nt_meets:
        outcome = "CONFOUNDED"
    elif success and not failure:
        outcome = "SIGNAL"
    else:
        outcome = "NULL"

    anomalies = []
    bC = med("CONTROL", "beta")
    if bC is not None and bC >= 0.2:
        anomalies.append(f"CONTROL (continuous concrete hull) has median beta {bC:.3f} >= 0.2: "
                         "the |dW|>1e-9*median counter registers continuous variation as "
                         "breakpoints at every grid pair")
    t0 = [r for r, _ in T if r["seed"] == 0][0]
    ex = t0.get("exact_recheck")
    if ex and ex["agree"] != ex["n_pairs"]:
        anomalies.append(f"exact rational recheck disagrees on {ex['n_pairs'] - ex['agree']}"
                         f"/{ex['n_pairs']} pairs")
    ffT = float(np.median([r["finite_frac"] for r, _ in T]))
    anomalies.append(f"TREATMENT finite fraction of theta = {ffT:.3f}; rest of circle W=inf "
                     "(box expansion r(|cos|+|sin|)>1)")
    ndT = [r.get("n_distinct_finite_W") for r, _ in T]
    anomalies.append(f"TREATMENT distinct finite W values per seed: {ndT}")
    ndN = [r.get("n_distinct_finite_W") for r, _ in NT]
    anomalies.append(f"NULL_TWIN distinct finite W values per seed: {ndN}")
    if any(r.get("unconverged", 0) for r, _ in NT):
        anomalies.append("NULL_TWIN had Kleene-cap unconverged theta: "
                         + str([r["unconverged"] for r, _ in NT]))
    if any(r.get("ascent_cap_hits", 0) for r, _ in T):
        anomalies.append("ascent cap hit in TREATMENT")

    fj = [r.get("frac_jumps_with_iter_change") for r, _ in T]
    stupid = [
        {"text": "floating-point jitter produces fake breakpoints (recheck a subsample in exact "
                 "rational arithmetic)", "addressed_by_this_run": bool(ex),
         "how": f"exact Fraction re-run of 64 finest-grid pairs (seed 0): agree "
                f"{ex['agree']}/{ex['n_pairs']}" if ex else "not run"},
        {"text": "count grows because the threshold set is the only source of steps and the fit "
                 "window is too short to see saturation", "addressed_by_this_run": False,
         "how": "partially: 13 vs 50 threshold variants and NULL_TWIN reported; window fixed at "
                "2^-10..2^-16, no longer window tested"},
        {"text": "iteration-count changes give dense but non-scaling breakpoints",
         "addressed_by_this_run": True,
         "how": f"fraction of finest-grid TREATMENT jumps coinciding with an ascent iteration-count "
                f"change, per seed: {[round(v, 4) for v in fj]}"},
    ]
    comp = json.load(open(os.path.join(HERE, "compute.json"), encoding="utf-8"))
    crit = ("Per seed S = beta>=0.2 & R2>=0.95 & AIC_log-AIC_pow>=10 & AIC_sat-AIC_pow>=10, "
            "fits on delta=2^-10..2^-16 (7 points), beta=OLS slope log N vs log(1/delta). "
            "SUCCESS = S for all 5 TREATMENT (d=3, 13 thresholds) seeds and median NULL_TWIN "
            "beta<0.1. FAILURE = any seed (N16-N13)/N16<0.05, or any seed log beats power by "
            "AIC>=10, or |median beta_T - median beta_NULL|<0.1. PC detected: all seeds "
            "|beta-0.6309|<=0.05. CHEAT detected: S for all seeds. null_twin_meets_success: S "
            "for all NULL_TWIN seeds.")
    notes = (f"Default analyzer median beta={bT}, null twin median beta={bN}, control median "
             f"beta={bC}. success={success}, failure reasons={fail_reasons}. Outcome decided by "
             "PREREG class rules in code.")
    out = {"triplicateId": "HT-ae38c641b1", "world": "W3", "outcome": outcome,
           "statistics": stats, "criterion_as_applied": crit,
           "positive_control_detected": pc, "cheat_detected": cheat,
           "null_twin_meets_success": nt_meets,
           "treatment_success": success, "treatment_failure_reasons": fail_reasons,
           "stupid_explanations_status": stupid, "anomalies": anomalies,
           "core_minutes": round(comp["cpu_seconds"] / 60.0, 3),
           "attempts": comp["attempt"], "notes": notes}
    with open(os.path.join(HERE, "OUTCOME.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("outcome", "positive_control_detected",
                                          "cheat_detected", "null_twin_meets_success",
                                          "treatment_success", "treatment_failure_reasons",
                                          "core_minutes")}, indent=1))
    for k, v in stats.items():
        print(k, v["median_beta"], v["median_r2"], v["median_dAIC_log"], v["median_dAIC_sat"],
              v["all_seeds_S"])


if __name__ == "__main__":
    main()
