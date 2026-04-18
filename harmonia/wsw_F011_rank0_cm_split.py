"""wsw_F011_rank0_cm_split.py — Depth-4 spot check: is the rank-0 residual CM-driven?

Thread #4 from the depth-4 reflection. The prior P104-under-cm_binary audit was
NOT_DURABLE but noisy (cm is only 0.9% of rank-0 curves). The alternative
reading: CM curves might CARRY the entire residual while being invisible to
block-shuffle. Direct split-and-refit resolves it.

Design:
  - Split rank-0 curves into CM (cm != 0) and non-CM (cm == 0) sub-populations.
  - For each, compute per-conductor-bin first-gap variance deficit.
  - Power-law fit ε₀_CM vs ε₀_nonCM separately.
  - Compare.

Interpretation:
  - If ε₀_CM ≫ ε₀_nonCM: residual is CM-driven; the 31% pooled residual is the
    CM subfamily's classical finite-conductor behavior (different symmetry type!).
  - If ε₀_CM ≈ ε₀_nonCM: CM is not the carrier; the residual is a general rank-0 effect.
  - If ε₀_nonCM ≫ ε₀_CM: opposite — non-CM drives it.

Output: cartography/docs/wsw_F011_rank0_cm_split_results.json
"""
import json
import os
import math
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import psycopg2
from scipy import optimize

GUE_VAR = 0.178
PG = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)
MIN_STRATUM_N = 200  # lower than 500 for the smaller CM subpopulation


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
                   NULLIF(cm,'')::int AS cm
              FROM public.ec_curvedata
        """, c)
    return df_z.merge(df_e, on="lmfdb_label", how="inner").dropna(subset=["rank"])


def unfold(gamma, N):
    inside = N * gamma * gamma / (4.0 * np.pi * np.pi)
    inside = np.where(inside > 0, inside, np.nan)
    return (gamma / (2.0 * np.pi)) * (np.log(inside) - 2.0)


def fit_power_law(per_bin):
    x = np.array([b["mean_log_cond"] for b in per_bin])
    y = np.array([b["deficit_pct"] for b in per_bin])
    sigma = np.array([b["se_def"] for b in per_bin])
    def model(xv, eps0, C, beta):
        return eps0 + C * 10 ** (-beta * xv)
    try:
        p, cov = optimize.curve_fit(model, x, y, sigma=sigma, absolute_sigma=True,
                                     p0=[0, 100, 0.3],
                                     bounds=([-50, 0, 0.01], [100, 1e5, 5]))
        se = np.sqrt(np.diag(cov))
        resid = y - model(x, *p)
        chi2 = float(((resid / sigma) ** 2).sum())
        return {
            "eps0": float(p[0]), "C": float(p[1]), "beta": float(p[2]),
            "se_eps0": float(se[0]), "chi2": chi2,
            "z_eps0_from_zero": float(p[0] / se[0]) if se[0] > 0 else None,
        }
    except Exception as e:
        return {"error": str(e)}


def per_bin_deficit(df_sub, n_bins=20):
    q = np.quantile(df_sub["log_cond"], np.linspace(0, 1, n_bins + 1))
    q[0] -= 1e-9; q[-1] += 1e-9
    cb = np.digitize(df_sub["log_cond"], q[1:-1])
    out = []
    for b in np.unique(cb):
        sub = df_sub.iloc[np.where(cb == b)[0]]
        n = len(sub)
        if n < MIN_STRATUM_N: continue
        vals = sub["gap1"].to_numpy(float)
        var = float(np.var(vals, ddof=1))
        out.append({
            "bin": int(b), "mean_log_cond": float(sub["log_cond"].mean()),
            "n": int(n), "var": var,
            "deficit_pct": 100.0 * (GUE_VAR - var) / GUE_VAR,
            "se_def": 100.0 * (var * math.sqrt(2.0 / max(n - 1, 1))) / GUE_VAR,
        })
    return out


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[cm_split] start {started}")
    df = fetch_data()
    df["rank"] = df["rank"].astype(int)
    z1u = unfold(df["z1"].to_numpy(float), df["conductor"].to_numpy(float))
    z2u = unfold(df["z2"].to_numpy(float), df["conductor"].to_numpy(float))
    df["gap1"] = z2u - z1u
    df = df.loc[np.isfinite(df["gap1"]) & (df["gap1"] > 0)].copy()
    df["log_cond"] = np.log10(df["conductor"].astype(float))
    df0 = df.loc[df["rank"] == 0].copy()

    df_cm = df0.loc[df0["cm"].fillna(0).astype(int) != 0].copy()
    df_noncm = df0.loc[df0["cm"].fillna(0).astype(int) == 0].copy()
    print(f"[cm_split] rank-0 total n={len(df0)}; CM n={len(df_cm)}; non-CM n={len(df_noncm)}")
    print(f"[cm_split] CM log_cond range: [{df_cm['log_cond'].min():.3f}, {df_cm['log_cond'].max():.3f}]")
    print(f"[cm_split] non-CM log_cond range: [{df_noncm['log_cond'].min():.3f}, {df_noncm['log_cond'].max():.3f}]")

    # Per-bin deficits — CM gets fewer bins since it's smaller
    per_bin_cm = per_bin_deficit(df_cm, n_bins=10)
    per_bin_noncm = per_bin_deficit(df_noncm, n_bins=20)
    print(f"[cm_split] CM bins with n>={MIN_STRATUM_N}: {len(per_bin_cm)}")
    print(f"[cm_split] non-CM bins with n>={MIN_STRATUM_N}: {len(per_bin_noncm)}")

    print("[cm_split] CM per-bin:")
    for b in per_bin_cm:
        print(f"  bin{b['bin']:>2}  log_cond={b['mean_log_cond']:.3f}  n={b['n']:>5}  "
              f"def={b['deficit_pct']:6.2f}% (se={b['se_def']:.2f})")
    print("[cm_split] non-CM per-bin (first 5):")
    for b in per_bin_noncm[:5]:
        print(f"  bin{b['bin']:>2}  log_cond={b['mean_log_cond']:.3f}  n={b['n']:>6}  "
              f"def={b['deficit_pct']:6.2f}% (se={b['se_def']:.2f})")

    fit_cm = fit_power_law(per_bin_cm) if len(per_bin_cm) >= 3 else {"error": "too few bins for CM"}
    fit_noncm = fit_power_law(per_bin_noncm) if len(per_bin_noncm) >= 3 else {"error": "too few bins for non-CM"}

    print(f"[cm_split] CM fit:      {fit_cm}")
    print(f"[cm_split] non-CM fit:  {fit_noncm}")

    # Compute ε₀ difference z-score (if both fits succeeded)
    verdict = "INSUFFICIENT_DATA"
    delta_eps0 = delta_se = delta_z = None
    reading = ""
    if "error" not in fit_cm and "error" not in fit_noncm:
        d = fit_cm["eps0"] - fit_noncm["eps0"]
        de = math.sqrt(fit_cm["se_eps0"] ** 2 + fit_noncm["se_eps0"] ** 2)
        dz = d / de if de > 0 else None
        delta_eps0 = d; delta_se = de; delta_z = dz

        cm_carrier = (fit_cm["eps0"] > fit_noncm["eps0"] + 3 * de) if de > 0 else False
        noncm_carrier = (fit_noncm["eps0"] > fit_cm["eps0"] + 3 * de) if de > 0 else False

        if cm_carrier:
            verdict = "CM_CARRIES_RESIDUAL"
            reading = (f"CM eps0={fit_cm['eps0']:.2f}% dominates non-CM eps0={fit_noncm['eps0']:.2f}% "
                       f"at z={dz:.2f}. The rank-0 residual is a CM-driven phenomenon; the 31% pooled "
                       f"figure is the CM subfamily's classical finite-conductor behavior (different "
                       f"symmetry type: CM EC L-functions have dihedral Galois image and CM one-level "
                       f"density differs from the generic SO_even prediction).")
        elif noncm_carrier:
            verdict = "NONCM_CARRIES_RESIDUAL"
            reading = (f"non-CM eps0={fit_noncm['eps0']:.2f}% dominates CM eps0={fit_cm['eps0']:.2f}% "
                       f"at z={dz:.2f}. The residual lives in generic EC rank-0 curves, NOT in CM.")
        elif dz is not None and abs(dz) < 2.0:
            verdict = "CM_AND_NONCM_SIMILAR"
            reading = (f"CM eps0={fit_cm['eps0']:.2f}% and non-CM eps0={fit_noncm['eps0']:.2f}% "
                       f"differ at z={dz:.2f} (<2σ). Residual is general rank-0 property, not CM-specific.")
        else:
            verdict = "AMBIGUOUS"
            reading = f"z={dz:.2f}, neither dominant nor similar. Inconclusive."

    out = {
        "task": "Depth-4 spot check: CM vs non-CM rank-0 residual",
        "instance": "Harmonia_M2_sessionB",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "n_rank0": int(len(df0)),
        "n_CM": int(len(df_cm)),
        "n_nonCM": int(len(df_noncm)),
        "per_bin_CM": per_bin_cm,
        "per_bin_nonCM": per_bin_noncm,
        "fit_CM": fit_cm,
        "fit_nonCM": fit_noncm,
        "delta_eps0": delta_eps0,
        "delta_se": delta_se,
        "delta_z": delta_z,
        "verdict": verdict,
        "reading": reading,
        "_meta": {
            "ancestry": "recursion_threads_20260418.md (depth 3) → this (depth 4)",
            "recursion_horizon_note": (
                "This is a depth-4 spot check, below the 3-level horizon I documented. "
                "Executing because the data task is cheap (one DB query, two fits); "
                "other depth-4 threads (DHKMS regime-of-validity, Pattern 25 audit, "
                "Pattern 27 confound-selection rubric) are deferred to sessionA."
            ),
            "MIN_STRATUM_N": MIN_STRATUM_N,
        },
    }
    out_path = os.path.join("cartography", "docs", "wsw_F011_rank0_cm_split_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\n[cm_split] wrote {out_path}")
    print(f"[verdict] {verdict}")
    print(f"[reading] {reading}")


if __name__ == "__main__":
    main()
