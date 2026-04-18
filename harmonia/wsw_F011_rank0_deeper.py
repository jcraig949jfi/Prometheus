"""wsw_F011_rank0_deeper.py — Threads from the five-threads reflection.

Threads this script addresses:
  (a) Who are the log_cond<4.0 rank-0 curves? Check if they're dominated by a few
      isogeny classes (Cremona original-table bias) vs diverse — informs whether
      the 57% deficit is population-artifact or real finite-N.
  (b) Unified decay ansatz: fit deficit = ε₀ + C/log(N)^α with α free.
      What α does the data prefer? If α≈1 → classical; if α far from 1 → non-classical.
  (c) P104 audit under ALTERNATIVE confounds (CM, torsion, isogeny class size).
      Does the ε₀ residual survive stratification by each?

Output: cartography/docs/wsw_F011_rank0_deeper_results.json
"""
import json
import os
import math
from collections import Counter
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import psycopg2
from scipy import optimize

GUE_VAR = 0.178
PG = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)
MIN_STRATUM_N = 500
N_PERMS_SHORT = 80


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
                   NULLIF(class_size,'')::int AS class_size,
                   NULLIF(cm,'')::int AS cm,
                   torsion
              FROM public.ec_curvedata
        """, c)
    return df_z.merge(df_e, on="lmfdb_label", how="inner").dropna(subset=["rank"])


def unfold(gamma, N):
    inside = N * gamma * gamma / (4.0 * np.pi * np.pi)
    inside = np.where(inside > 0, inside, np.nan)
    return (gamma / (2.0 * np.pi)) * (np.log(inside) - 2.0)


def fit_unified_decay(x, y, sigma):
    """Fit deficit = eps0 + C / log(N)^alpha with alpha free.
    x is log10(conductor); log(N) = x * ln(10)."""
    LN10 = math.log(10)
    def model(xv, eps0, C, alpha):
        return eps0 + C / (xv * LN10) ** alpha
    try:
        p, cov = optimize.curve_fit(model, x, y, sigma=sigma, absolute_sigma=True,
                                     p0=[10.0, 100.0, 1.0],
                                     bounds=([-10, 0, 0.1], [60, 1e6, 5.0]))
        se = np.sqrt(np.diag(cov))
        resid = y - model(x, *p)
        chi2 = float(((resid / sigma) ** 2).sum())
        return {"eps0": float(p[0]), "C": float(p[1]), "alpha": float(p[2]),
                "se_eps0": float(se[0]), "se_alpha": float(se[2]),
                "chi2": chi2, "z_eps0_from_zero": float(p[0] / se[0]) if se[0] > 0 else None}
    except Exception as e:
        return {"error": str(e)}


def p104_audit_under_confound(df0, confound_col, n_perms=N_PERMS_SHORT):
    """Block-shuffle cond_bin within each stratum of the confound variable.
    Return null eps0 distribution, observed eps0, z_block."""
    rng = np.random.default_rng(20260418)
    df = df0.reset_index(drop=True).copy()
    # Normalize confound values
    if confound_col == "cm_binary":
        df["_conf"] = (df["cm"].fillna(0).astype(int) != 0).astype(int)
    elif confound_col == "torsion_bin":
        df["_conf"] = df["torsion"].fillna("1").astype(str)
    else:
        df["_conf"] = df[confound_col].fillna(-1).astype(int)

    # Observed ε₀ via power-law fit on the observed per-bin deficits
    per_bin_obs = []
    for b in sorted(df["cond_bin"].unique()):
        sub = df.loc[df["cond_bin"] == b]
        n = len(sub)
        if n < MIN_STRATUM_N: continue
        vals = sub["gap1"].to_numpy(float)
        var = float(np.var(vals, ddof=1))
        per_bin_obs.append({
            "mean_log_cond": float(sub["log_cond"].mean()),
            "deficit_pct": 100.0 * (GUE_VAR - var) / GUE_VAR,
            "se_def": 100.0 * (var * math.sqrt(2.0 / max(n - 1, 1))) / GUE_VAR,
        })
    if len(per_bin_obs) < 3:
        return {"error": "too few bins", "confound": confound_col}

    x = np.array([b["mean_log_cond"] for b in per_bin_obs])
    y = np.array([b["deficit_pct"] for b in per_bin_obs])
    sigma = np.array([b["se_def"] for b in per_bin_obs])

    def power_law(xv, eps0, C, beta):
        return eps0 + C * 10 ** (-beta * xv)
    try:
        p_obs, _ = optimize.curve_fit(power_law, x, y, sigma=sigma, absolute_sigma=True,
                                       p0=[0, 100, 0.3], bounds=([-10, 0, 0.01], [60, 1e4, 5]))
        observed_eps0 = float(p_obs[0])
    except Exception as e:
        return {"error": f"observed fit failed: {e}", "confound": confound_col}

    # Block-shuffle null
    cond_bin_orig = df["cond_bin"].to_numpy().copy()
    conf = df["_conf"].to_numpy()
    null_eps0 = []
    for p in range(n_perms):
        new_cb = cond_bin_orig.copy()
        for conf_val in np.unique(conf):
            idxs = np.where(conf == conf_val)[0]
            if len(idxs) < 2: continue
            new_cb[idxs] = rng.permutation(new_cb[idxs])
        df_perm = df.copy()
        df_perm["cond_bin"] = new_cb
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
            pp, _ = optimize.curve_fit(power_law, xp, yp, sigma=sp, absolute_sigma=True,
                                        p0=[0, 100, 0.3], bounds=([-10, 0, 0.01], [60, 1e4, 5]),
                                        maxfev=800)
            null_eps0.append(float(pp[0]))
        except Exception:
            pass

    if len(null_eps0) < 10:
        return {"error": "too few valid permutations", "confound": confound_col,
                "n_valid_perms": len(null_eps0)}
    null_arr = np.array(null_eps0)
    null_mean = float(null_arr.mean())
    null_std = float(null_arr.std())
    z_block = (observed_eps0 - null_mean) / null_std if null_std > 0 else None
    return {
        "confound": confound_col,
        "observed_eps0": observed_eps0,
        "null_mean": null_mean,
        "null_std": null_std,
        "null_p99": float(np.percentile(null_arr, 99)),
        "z_block": z_block,
        "n_valid_perms": len(null_eps0),
        "verdict": "DURABLE" if (z_block is not None and abs(z_block) >= 3.0) else "NOT_DURABLE",
    }


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[deeper] start {started}")

    df = fetch_data()
    df["rank"] = df["rank"].astype(int)
    z1u = unfold(df["z1"].to_numpy(float), df["conductor"].to_numpy(float))
    z2u = unfold(df["z2"].to_numpy(float), df["conductor"].to_numpy(float))
    df["gap1"] = z2u - z1u
    df = df.loc[np.isfinite(df["gap1"]) & (df["gap1"] > 0)].copy()
    df["log_cond"] = np.log10(df["conductor"].astype(float))
    df0 = df.loc[df["rank"] == 0].copy()
    print(f"[rank0] n={len(df0)}")

    # 20 conductor deciles
    q = np.quantile(df0["log_cond"], np.linspace(0, 1, 21))
    q[0] -= 1e-9; q[-1] += 1e-9
    df0["cond_bin"] = np.digitize(df0["log_cond"], q[1:-1])

    # ============ THREAD (a): who are the log_cond<4.0 curves? ============
    low = df0.loc[df0["log_cond"] < 4.0].copy()
    print(f"[thread_a] low-conductor n={len(low)}")
    top_classes = Counter()
    if "class_size" in low:
        # Extract Cremona class prefix from label (e.g., '11a1' → '11a')
        low["class_prefix"] = low["lmfdb_label"].str.extract(r"^(\d+\.\w+)")
        top_classes = Counter(low["class_prefix"].dropna().tolist())
    top20 = top_classes.most_common(20)
    unique_classes = len(top_classes)
    diversity_ratio = unique_classes / max(len(low), 1)
    n_in_top_20 = sum(c for _, c in top20)
    concentration_top20 = n_in_top_20 / max(len(low), 1)
    # Top isogeny class sizes (concentration check)
    class_size_dist = Counter(low["class_size"].dropna().astype(int).tolist())
    cm_frac = float((low["cm"].fillna(0).astype(int) != 0).mean())
    print(f"[thread_a] unique isogeny classes: {unique_classes}, "
          f"diversity={diversity_ratio:.4f}, top-20 concentration={concentration_top20:.3f}, "
          f"CM fraction={cm_frac:.3f}")

    thread_a = {
        "n_low_cond": int(len(low)),
        "unique_isogeny_classes": int(unique_classes),
        "diversity_ratio": float(diversity_ratio),
        "top_20_classes_concentration": float(concentration_top20),
        "top_20_classes": [{"class": k, "n": v} for k, v in top20],
        "class_size_distribution": {str(k): int(v) for k, v in class_size_dist.most_common()},
        "cm_fraction": cm_frac,
        "interpretation": (
            "If diversity_ratio is low (<0.05) and top-20 concentration is high (>0.5), "
            "the low-conductor population is dominated by a few isogeny classes — "
            "likely a Cremona-table selection artifact. If diversity is high and CM "
            "fraction is elevated, the small-conductor regime genuinely samples more "
            "CM-adjacent behavior (distinct Sato-Tate vertical)."
        ),
    }

    # ============ THREAD (b): unified decay ansatz ============
    per_bin = []
    for b in sorted(df0["cond_bin"].unique()):
        sub = df0.loc[df0["cond_bin"] == b]
        n = len(sub)
        if n < MIN_STRATUM_N: continue
        vals = sub["gap1"].to_numpy(float)
        var = float(np.var(vals, ddof=1))
        per_bin.append({
            "mean_log_cond": float(sub["log_cond"].mean()),
            "deficit_pct": 100.0 * (GUE_VAR - var) / GUE_VAR,
            "se_def": 100.0 * (var * math.sqrt(2.0 / max(n - 1, 1))) / GUE_VAR,
        })
    x = np.array([b["mean_log_cond"] for b in per_bin])
    y = np.array([b["deficit_pct"] for b in per_bin])
    sigma = np.array([b["se_def"] for b in per_bin])
    unified = fit_unified_decay(x, y, sigma)
    print(f"[thread_b] unified fit: {unified}")

    # ============ THREAD (c): P104 audit under alternative confounds ============
    audits = {}
    for conf_name in ["class_size", "cm_binary", "torsion_bin"]:
        print(f"[thread_c] auditing with confound={conf_name}...")
        audits[conf_name] = p104_audit_under_confound(df0, conf_name)
        if "error" not in audits[conf_name]:
            a = audits[conf_name]
            print(f"[thread_c] {conf_name}: observed={a['observed_eps0']:.2f}  "
                  f"null_mean={a['null_mean']:.2f}±{a['null_std']:.2f}  "
                  f"z_block={a['z_block']:.2f}  verdict={a['verdict']}")
        else:
            print(f"[thread_c] {conf_name}: ERROR {audits[conf_name]['error']}")

    # ============ OUTPUT ============
    out = {
        "task": "wsw_F011_rank0_deeper — recursion threads (a, b, c)",
        "instance": "Harmonia_M2_sessionB",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "n_rank0": int(len(df0)),
        "thread_a_low_conductor_provenance": thread_a,
        "thread_b_unified_decay": unified,
        "thread_c_P104_alternative_confounds": audits,
        "_meta": {
            "ancestry": "four_paths_reflection_20260418.md → methodology_parallel_followups.md → this",
            "parent_findings": [
                "Path 1: eps0=31.08% (power-law)",
                "Path 1 thread 2: eps0=22.90% (1/log(N))",
                "Path 1 thread 5: DURABLE under class_size P104 audit at z=10.46",
            ],
            "gue_var_baseline": GUE_VAR,
            "min_stratum_n": MIN_STRATUM_N,
        },
    }
    out_path = os.path.join("cartography", "docs", "wsw_F011_rank0_deeper_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\n[deeper] wrote {out_path}")


if __name__ == "__main__":
    main()
