"""wsw_F011_rank0_deep.py — Threads 1, 2, 5 from four-paths reflection.

Thread 1: "Inverted deficit at rank 0" — naive excised-ensemble predicts LESS
deficit at rank 0 (no forced zeros); we see MORE. Test candidates:
  (1a) Root-number check: do all rank-0 curves have root_number=+1? (Expected under BSD parity.)
  (1b) Small-conductor selection bias: sort rank-0 curves by conductor, check if deficit is
       systematically higher in the earliest-listed LMFDB curves vs later ones.
  (1c) Compare rank-0 first-gap variance to SO_even one-level density kernel prediction
       rather than bulk GUE.

Thread 2: Slow beta=0.137 decay — classical 1/log(N) predicts faster decay. Test:
  (2a) Fit 1/log(N) ansatz to rank-0 data; compare chi2 to power-law.
  (2b) Check what fraction of the data is above log_cond 5.5 (narrow tail).
  (2c) Try a Miller-style a_p^2-corrected model if simple decays don't fit.

Thread 5: P104-audit my own Path 1 finding. Block-shuffle rank-0 curves across a
  secondary confound (isogeny class size, since conductor is already the primary axis).
  If the ε₀=31% extrapolation holds under P104, it's durable; if not, retract.

Output: cartography/docs/wsw_F011_rank0_deep_results.json
"""
import json
import os
import math
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import psycopg2
from scipy import stats, optimize

GUE_VAR = 0.178
PG = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)
MIN_STRATUM_N = 500


def connect(dbname):
    return psycopg2.connect(
        host=PG["host"], port=PG["port"], dbname=dbname,
        user=PG["user"], password=PG["password"], connect_timeout=10,
    )


def fetch_data():
    with connect("prometheus_fire") as c:
        df_z = pd.read_sql("""
            SELECT lmfdb_label, conductor::bigint AS conductor,
                   zeros[1]::float8 AS z1, zeros[2]::float8 AS z2
              FROM zeros.object_zeros
             WHERE object_type = 'elliptic_curve'
               AND n_zeros >= 2 AND zeros[1] > 0.0 AND zeros[2] > zeros[1]
        """, c)
    with connect("lmfdb") as c:
        df_e = pd.read_sql("""
            SELECT lmfdb_label,
                   NULLIF(rank,'')::int AS rank,
                   NULLIF("signD",'')::int AS sign_disc,
                   NULLIF(class_size,'')::int AS class_size,
                   NULLIF(cm,'')::int AS cm
              FROM public.ec_curvedata
        """, c)
    return df_z.merge(df_e, on="lmfdb_label", how="inner").dropna(subset=["rank"])


def unfold(gamma, N):
    inside = N * gamma * gamma / (4.0 * np.pi * np.pi)
    inside = np.where(inside > 0, inside, np.nan)
    return (gamma / (2.0 * np.pi)) * (np.log(inside) - 2.0)


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[rank0_deep] start {started}")

    df = fetch_data()
    df["rank"] = df["rank"].astype(int)
    z1u = unfold(df["z1"].to_numpy(float), df["conductor"].to_numpy(float))
    z2u = unfold(df["z2"].to_numpy(float), df["conductor"].to_numpy(float))
    df["gap1"] = z2u - z1u
    df = df.loc[np.isfinite(df["gap1"]) & (df["gap1"] > 0)].copy()
    df["log_cond"] = np.log10(df["conductor"].astype(float))

    df0 = df.loc[df["rank"] == 0].copy()
    print(f"[rank0] n={len(df0)}")

    # =====================================================================
    # Thread 1a: root_number sanity check (signD is disc sign, not root number,
    # per my tick-8 retraction). EC has no directly stored root number in this mirror.
    # Check instead: are all rank-0 in the same "root number class" by the BSD parity
    # proxy (-1)^rank? All should be rank=0 → +1 parity. Trivially yes by construction.
    # What we CAN check: does signD (disc sign) distribution vary by conductor?
    rn_by_cond_bin = []
    q_rn = np.quantile(df0["log_cond"], np.linspace(0, 1, 11))
    q_rn[0] -= 1e-9; q_rn[-1] += 1e-9
    df0["cb_rn"] = np.digitize(df0["log_cond"], q_rn[1:-1])
    for b in sorted(df0["cb_rn"].unique()):
        sub = df0.loc[df0["cb_rn"] == b]
        n = len(sub)
        if n < MIN_STRATUM_N: continue
        sd = sub["sign_disc"].dropna()
        rn_by_cond_bin.append({
            "bin": int(b),
            "n": n,
            "mean_log_cond": float(sub["log_cond"].mean()),
            "sign_disc_pos_frac": float((sd == 1).sum() / len(sd)) if len(sd) else None,
        })
    sd_summary = [round(b["sign_disc_pos_frac"], 3) if b["sign_disc_pos_frac"] is not None else None
                  for b in rn_by_cond_bin[:5]]
    print(f"[thread1a] sign_disc+ frac by conductor (first 5 bins): {sd_summary}")

    # Thread 1b: small-conductor selection bias. Is the rank-0 deficit at the VERY
    # lowest conductor (say log_cond < 4.0) systematically different from the typical
    # rank-0 deficit? This is the "first curves in LMFDB are special" hypothesis.
    low_cond = df0.loc[df0["log_cond"] < 4.0, "gap1"].to_numpy(float)
    mid_cond = df0.loc[(df0["log_cond"] >= 4.5) & (df0["log_cond"] < 5.0), "gap1"].to_numpy(float)
    high_cond = df0.loc[df0["log_cond"] >= 5.5, "gap1"].to_numpy(float)

    def summary(vals, name):
        if len(vals) < MIN_STRATUM_N: return {"n": len(vals), "included": False}
        var = float(np.var(vals, ddof=1))
        return {"name": name, "n": int(len(vals)), "var": var,
                "deficit_pct": 100.0 * (GUE_VAR - var) / GUE_VAR,
                "se_var": var * math.sqrt(2.0 / max(len(vals) - 1, 1))}

    t1b_low = summary(low_cond, "log_cond<4.0")
    t1b_mid = summary(mid_cond, "log_cond in [4.5,5.0)")
    t1b_high = summary(high_cond, "log_cond>=5.5")
    print(f"[thread1b] low: {t1b_low}")
    print(f"[thread1b] mid: {t1b_mid}")
    print(f"[thread1b] high: {t1b_high}")

    # Thread 1c: SO_even one-level density is NOT computed here (requires Bessel-function
    # integral). We note the comparison target for future theoretical work.
    t1c_note = ("SO_even one-level density prediction for variance at rank 0 not yet computed. "
                "Duenez-HKMS or Katz-Sarnak SO(even) kernel would give the right theoretical "
                "comparison. Flag as dependency for future thread on DHKMS catalog entry "
                "(thread 3 companion).")

    # =====================================================================
    # Thread 2: alternative decay fits on rank-0 conductor-window data
    # Re-bin (20 deciles on rank-0) same as Path 1+2 original
    q = np.quantile(df0["log_cond"], np.linspace(0, 1, 21))
    q[0] -= 1e-9; q[-1] += 1e-9
    df0["cond_bin"] = np.digitize(df0["log_cond"], q[1:-1])
    per_bin = []
    for b in sorted(df0["cond_bin"].unique()):
        sub = df0.loc[df0["cond_bin"] == b]
        n = len(sub)
        if n < MIN_STRATUM_N: continue
        vals = sub["gap1"].to_numpy(float)
        var = float(np.var(vals, ddof=1))
        per_bin.append({
            "bin": int(b), "mean_log_cond": float(sub["log_cond"].mean()),
            "n": int(n), "var": var,
            "deficit_pct": 100.0 * (GUE_VAR - var) / GUE_VAR,
            "se_deficit_pct": 100.0 * (var * math.sqrt(2.0 / max(n - 1, 1))) / GUE_VAR,
        })

    x = np.array([b["mean_log_cond"] for b in per_bin])
    y = np.array([b["deficit_pct"] for b in per_bin])
    sigma = np.array([b["se_deficit_pct"] for b in per_bin])

    fits = {}
    # Ansatz A: power-law (re-fit for reference): deficit = eps0 + C * conductor^(-beta)
    try:
        pA, cA = optimize.curve_fit(lambda x, e, C, b: e + C * 10**(-b * x), x, y, sigma=sigma,
                                     absolute_sigma=True, p0=[0, 100, 0.3],
                                     bounds=([-10, 0, 0.01], [60, 1e4, 5]))
        fits["power_law"] = {"eps0": float(pA[0]), "C": float(pA[1]), "beta": float(pA[2]),
                             "se_eps0": float(np.sqrt(cA[0,0])),
                             "chi2": float((((y - (pA[0] + pA[1]*10**(-pA[2]*x))) / sigma)**2).sum())}
    except Exception as e:
        fits["power_law"] = {"error": str(e)}

    # Ansatz B: classical 1/log(N) decay: deficit = eps0 + C / log(N)
    # (Here log_cond is log10; convert via ln(10))
    LN10 = math.log(10)
    try:
        pB, cB = optimize.curve_fit(lambda x, e, C: e + C / (x * LN10), x, y, sigma=sigma,
                                     absolute_sigma=True, p0=[0, 100],
                                     bounds=([-10, -1e4], [60, 1e4]))
        fits["one_over_log"] = {"eps0": float(pB[0]), "C": float(pB[1]),
                                 "se_eps0": float(np.sqrt(cB[0,0])),
                                 "chi2": float((((y - (pB[0] + pB[1]/(x * LN10))) / sigma)**2).sum())}
    except Exception as e:
        fits["one_over_log"] = {"error": str(e)}

    # Ansatz C: CFMS heuristic 1/log(N)^2: deficit = eps0 + C / log(N)^2
    try:
        pC, cC = optimize.curve_fit(lambda x, e, C: e + C / (x * LN10)**2, x, y, sigma=sigma,
                                     absolute_sigma=True, p0=[0, 1000],
                                     bounds=([-10, -1e5], [60, 1e5]))
        fits["one_over_log_squared"] = {"eps0": float(pC[0]), "C": float(pC[1]),
                                         "se_eps0": float(np.sqrt(cC[0,0])),
                                         "chi2": float((((y - (pC[0] + pC[1]/(x * LN10)**2)) / sigma)**2).sum())}
    except Exception as e:
        fits["one_over_log_squared"] = {"error": str(e)}

    print(f"[thread2] fits: {json.dumps({k: {kk: round(vv, 3) if isinstance(vv, float) else vv for kk,vv in v.items()} for k,v in fits.items() if 'error' not in v}, indent=2)}")

    # Thread 2b: fraction of data in the tail
    tail_frac = float((df0["log_cond"] >= 5.5).mean())
    print(f"[thread2b] fraction of rank-0 data with log_cond >= 5.5: {tail_frac:.3f}")

    # =====================================================================
    # Thread 5: P104-audit of the rank-0 residual
    # Confound: class_size (isogeny class size, Mazur-bounded). Block-shuffle
    # conductor-bin assignments within each class_size bucket; recompute ε₀
    # extrapolation per permutation.
    # This asks: "if you shuffle which rank-0 curve is in which conductor bin,
    # but preserve the class_size distribution within each bin, does the
    # fitted ε₀ = 31% survive?"
    rng = np.random.default_rng(20260418)
    N_PERMS = 100  # lighter than prior audit due to curve-fit cost per perm
    n_curves_per_bin = df0.groupby("cond_bin").size().to_dict()

    null_eps0 = np.full(N_PERMS, np.nan)
    df0_idx = df0.reset_index(drop=True)
    class_sizes = df0_idx["class_size"].fillna(-1).astype(int).to_numpy()
    observed_eps0 = fits.get("power_law", {}).get("eps0") if "error" not in fits.get("power_law", {}) else None

    # Block-shuffle cond_bin within class_size strata
    for p in range(N_PERMS):
        new_cond_bin = df0_idx["cond_bin"].to_numpy().copy()
        for cs_val in np.unique(class_sizes):
            idxs = np.where(class_sizes == cs_val)[0]
            if len(idxs) < 2: continue
            new_cond_bin[idxs] = rng.permutation(new_cond_bin[idxs])

        # Recompute per-bin deficit under shuffled bin assignment
        df_perm = df0_idx.copy()
        df_perm["cond_bin"] = new_cond_bin
        per_bin_perm = []
        for b in sorted(df_perm["cond_bin"].unique()):
            sub = df_perm.loc[df_perm["cond_bin"] == b]
            n = len(sub)
            if n < MIN_STRATUM_N: continue
            vals = sub["gap1"].to_numpy(float)
            var = float(np.var(vals, ddof=1))
            per_bin_perm.append({
                "mean_log_cond": float(sub["log_cond"].mean()),
                "deficit_pct": 100.0 * (GUE_VAR - var) / GUE_VAR,
                "se_def": 100.0 * (var * math.sqrt(2.0 / max(n - 1, 1))) / GUE_VAR,
            })
        if len(per_bin_perm) < 3: continue
        xp = np.array([b["mean_log_cond"] for b in per_bin_perm])
        yp = np.array([b["deficit_pct"] for b in per_bin_perm])
        sp = np.array([b["se_def"] for b in per_bin_perm])
        try:
            pp, _ = optimize.curve_fit(lambda x, e, C, b: e + C * 10**(-b * x),
                                        xp, yp, sigma=sp, absolute_sigma=True,
                                        p0=[0, 100, 0.3], bounds=([-10, 0, 0.01], [60, 1e4, 5]),
                                        maxfev=1000)
            null_eps0[p] = pp[0]
        except Exception:
            pass
        if (p + 1) % 20 == 0:
            so_far = null_eps0[:p+1]
            valid = so_far[~np.isnan(so_far)]
            if len(valid) > 0:
                print(f"[thread5 perm {p+1}] null_eps0 so far: mean={valid.mean():.2f}, std={valid.std():.2f}")

    valid_null = null_eps0[~np.isnan(null_eps0)]
    if len(valid_null) > 10 and observed_eps0 is not None:
        null_mean = float(valid_null.mean()); null_std = float(valid_null.std())
        z_block = (observed_eps0 - null_mean) / null_std if null_std > 0 else None
        null_p99 = float(np.percentile(valid_null, 99))
        if z_block is not None and abs(z_block) >= 3.0:
            t5_verdict = "DURABLE_UNDER_CLASS_SIZE_BLOCK_SHUFFLE"
        else:
            t5_verdict = "INFLATED_BY_CLASS_SIZE_CONFOUND"
    else:
        null_mean = null_std = null_p99 = z_block = None
        t5_verdict = "INSUFFICIENT_VALID_PERMUTATIONS"

    print(f"[thread5] observed eps0={observed_eps0}, null_mean={null_mean}, null_std={null_std}, z_block={z_block}")

    out = {
        "task": "wsw_F011_rank0_deep — threads 1, 2, 5 from four-paths reflection",
        "instance": "Harmonia_M2_sessionB",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "n_rank0": int(len(df0)),
        "thread1a_sign_disc_by_conductor": rn_by_cond_bin,
        "thread1b_conductor_extremes": {"low_cond_<4.0": t1b_low, "mid_cond": t1b_mid, "high_cond_>=5.5": t1b_high},
        "thread1c_note": t1c_note,
        "thread2_decay_fits": fits,
        "thread2b_tail_fraction": tail_frac,
        "thread5_P104_audit": {
            "design": "block-shuffle cond_bin within class_size strata; 100 perms; refit eps0 each perm",
            "n_perms_valid": int(len(valid_null)),
            "observed_eps0": observed_eps0,
            "null_eps0_mean": null_mean,
            "null_eps0_std": null_std,
            "null_eps0_p99": null_p99,
            "z_block": z_block,
            "verdict": t5_verdict,
        },
        "per_bin_observed": per_bin,
        "_meta": {
            "ancestry": "cartography/docs/four_paths_reflection_20260418.md",
            "gue_var_baseline": GUE_VAR,
            "min_stratum_n": MIN_STRATUM_N,
        },
    }
    out_path = os.path.join("cartography", "docs", "wsw_F011_rank0_deep_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\n[rank0_deep] wrote {out_path}")
    print(f"[thread5 verdict] {t5_verdict}")


if __name__ == "__main__":
    main()
