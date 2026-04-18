"""wsw_F011_lit_followup.py — threads A & B from literature correspondence audit.

Thread A: does the CFMS 1/log(N)^2 heuristic outperform 1/log(N) SPECIFICALLY
  at log_cond < 4.5 (where F7's 57% excess sits)? Fit both on low-cond subset
  and compare χ².

Thread B: does rank 2's first listed zero (γ₁) sit systematically FURTHER from
  s=1/2 than rank 0's γ₁? If yes, the forced central block displaces γ₁
  outward and explains why rank 2's first gap (γ₂-γ₁) has smaller variance
  deficit (it's measured in a more bulk-like region, less repelled).

Output: cartography/docs/wsw_F011_lit_followup_results.json
"""
import json
import os
import math
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import psycopg2
from scipy import optimize, stats

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
            SELECT lmfdb_label, NULLIF(rank,'')::int AS rank
              FROM public.ec_curvedata
        """, c)
    return df_z.merge(df_e, on="lmfdb_label", how="inner").dropna(subset=["rank"])


def unfold(gamma, N):
    inside = N * gamma * gamma / (4.0 * np.pi * np.pi)
    inside = np.where(inside > 0, inside, np.nan)
    return (gamma / (2.0 * np.pi)) * (np.log(inside) - 2.0)


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[lit_followup] start {started}")

    df = fetch_data()
    df["rank"] = df["rank"].astype(int)
    df["z1_unf"] = unfold(df["z1"].to_numpy(float), df["conductor"].to_numpy(float))
    df["z2_unf"] = unfold(df["z2"].to_numpy(float), df["conductor"].to_numpy(float))
    df["gap1"] = df["z2_unf"] - df["z1_unf"]
    df = df.loc[np.isfinite(df["gap1"]) & (df["gap1"] > 0) &
                np.isfinite(df["z1_unf"]) & (df["z1_unf"] > 0)].copy()
    df["log_cond"] = np.log10(df["conductor"].astype(float))

    # ============ THREAD B: rank-conditioned gamma_1 location ============
    # Literature (F2 audit): "forced zeros may absorb repulsion rather than
    # propagate it outward." Test: is the median / mean of gamma_1_unf for
    # rank 2 curves systematically LARGER than for rank 0?
    thread_b = {}
    for r in [0, 1, 2, 3]:
        sub = df.loc[df["rank"] == r, "z1_unf"]
        if len(sub) < 200:
            thread_b[f"rank_{r}"] = {"n": int(len(sub)), "included": False}
            continue
        thread_b[f"rank_{r}"] = {
            "n": int(len(sub)),
            "mean_z1_unf": float(sub.mean()),
            "median_z1_unf": float(sub.median()),
            "std_z1_unf": float(sub.std()),
        }
    print("[thread_b] rank-conditioned gamma_1 location:")
    for k, v in thread_b.items():
        if v.get("included", True):
            print(f"  {k}: n={v['n']:>7}  mean_z1_unf={v.get('mean_z1_unf', 0):.4f}  "
                  f"median={v.get('median_z1_unf', 0):.4f}  std={v.get('std_z1_unf', 0):.4f}")

    # Pairwise comparison rank 0 vs rank 2 (the key inversion pair)
    r0 = df.loc[df["rank"] == 0, "z1_unf"].to_numpy()
    r2 = df.loc[df["rank"] == 2, "z1_unf"].to_numpy()
    if len(r0) > 100 and len(r2) > 100:
        t_stat, p_val = stats.ttest_ind(r2, r0, equal_var=False)
        d_means = float(r2.mean() - r0.mean())
        pooled_se = math.sqrt(r0.std() ** 2 / len(r0) + r2.std() ** 2 / len(r2))
        z_displacement = d_means / pooled_se
    else:
        t_stat = p_val = z_displacement = d_means = None
    thread_b["rank_2_minus_rank_0_mean_z1"] = d_means
    thread_b["z_displacement"] = float(z_displacement) if z_displacement else None
    thread_b["t_test_p_value"] = float(p_val) if p_val is not None else None
    print(f"[thread_b] rank 2 vs rank 0 gamma_1 displacement: delta={d_means:.4f}, z={z_displacement:.2f}")

    # Interpretation of B
    if z_displacement is not None:
        if z_displacement > 3.0:
            thread_b["verdict"] = "DISPLACEMENT_CONFIRMED"
            thread_b["reading"] = (
                f"Rank 2 γ₁ sits delta={d_means:.4f} higher than rank 0 γ₁ at z={z_displacement:.2f}. "
                f"Supports the literature hypothesis: the forced central zeros in rank-2 curves "
                f"PUSH γ₁ outward, so rank-2's first nontrivial gap is measured in a less-repelled "
                f"region. This explains the inverted deficit ordering F2: rank-0's γ₁ sits closer "
                f"to s=1/2 where the excised-ensemble repulsion is strongest."
            )
        elif abs(z_displacement) < 2.0:
            thread_b["verdict"] = "NO_DISPLACEMENT"
            thread_b["reading"] = (
                f"Rank 2 γ₁ does NOT sit higher than rank 0 γ₁ (delta={d_means:.4f}, z={z_displacement:.2f}). "
                f"Literature hypothesis is not supported by this test; alternative explanations "
                f"needed for F2 inversion."
            )
        else:
            thread_b["verdict"] = "AMBIGUOUS"
            thread_b["reading"] = f"z={z_displacement:.2f} between 2 and 3; direction correct but weak."

    # ============ THREAD A: CFMS 1/log^2 vs 1/log at low conductor ============
    # F7 showed 57% deficit at log_cond<4.0, exceeding 1/log(N) extrapolation.
    # Literature suggests 1/log^2(N) heuristic may fit low-cond better.
    # Fit BOTH ansätze on the low_cond<4.5 rank-0 subset.
    low = df.loc[(df["rank"] == 0) & (df["log_cond"] < 4.5)].copy()
    print(f"[thread_a] low_cond<4.5 rank-0 n={len(low)}")

    # 10 bins across log_cond [~3, 4.5)
    q = np.quantile(low["log_cond"], np.linspace(0, 1, 11))
    q[0] -= 1e-9; q[-1] += 1e-9
    low["cb"] = np.digitize(low["log_cond"], q[1:-1])
    per_bin = []
    for b in sorted(low["cb"].unique()):
        sub = low.loc[low["cb"] == b]
        n = len(sub)
        if n < MIN_STRATUM_N: continue
        vals = sub["gap1"].to_numpy(float)
        var = float(np.var(vals, ddof=1))
        per_bin.append({
            "bin": int(b), "mean_log_cond": float(sub["log_cond"].mean()),
            "n": int(n),
            "deficit_pct": 100.0 * (GUE_VAR - var) / GUE_VAR,
            "se_def": 100.0 * (var * math.sqrt(2.0 / max(n - 1, 1))) / GUE_VAR,
        })
    print(f"[thread_a] bins with n>={MIN_STRATUM_N}: {len(per_bin)}")

    x = np.array([b["mean_log_cond"] for b in per_bin])
    y = np.array([b["deficit_pct"] for b in per_bin])
    sigma = np.array([b["se_def"] for b in per_bin])

    LN10 = math.log(10)
    # 1/log(N) fit
    try:
        pA, cA = optimize.curve_fit(lambda xv, e, C: e + C / (xv * LN10),
                                     x, y, sigma=sigma, absolute_sigma=True,
                                     p0=[0, 100], bounds=([-20, -1e4], [100, 1e4]))
        chi2_A = float((((y - (pA[0] + pA[1] / (x * LN10))) / sigma) ** 2).sum())
        fit_1overlog = {"eps0": float(pA[0]), "C": float(pA[1]),
                         "se_eps0": float(np.sqrt(cA[0, 0])), "chi2": chi2_A}
    except Exception as e:
        fit_1overlog = {"error": str(e)}
    # 1/log(N)^2 fit
    try:
        pB, cB = optimize.curve_fit(lambda xv, e, C: e + C / (xv * LN10) ** 2,
                                     x, y, sigma=sigma, absolute_sigma=True,
                                     p0=[0, 1000], bounds=([-20, -1e5], [100, 1e5]))
        chi2_B = float((((y - (pB[0] + pB[1] / (x * LN10) ** 2)) / sigma) ** 2).sum())
        fit_1overlog2 = {"eps0": float(pB[0]), "C": float(pB[1]),
                          "se_eps0": float(np.sqrt(cB[0, 0])), "chi2": chi2_B}
    except Exception as e:
        fit_1overlog2 = {"error": str(e)}

    print(f"[thread_a] 1/log fit:    {fit_1overlog}")
    print(f"[thread_a] 1/log² fit:   {fit_1overlog2}")

    # Pick winner by χ² (since same DOF = n_bins - 2)
    if "error" not in fit_1overlog and "error" not in fit_1overlog2:
        if fit_1overlog2["chi2"] < fit_1overlog["chi2"]:
            thread_a_winner = "1/log(N)^2 (CFMS heuristic)"
            thread_a_winner_chi2 = fit_1overlog2["chi2"]
        else:
            thread_a_winner = "1/log(N) (classical Miller)"
            thread_a_winner_chi2 = fit_1overlog["chi2"]
    else:
        thread_a_winner = "UNDETERMINED"
        thread_a_winner_chi2 = None

    thread_a = {
        "domain": "rank 0, log_cond < 4.5",
        "n_total": int(len(low)),
        "n_bins": len(per_bin),
        "per_bin": per_bin,
        "fit_one_over_log": fit_1overlog,
        "fit_one_over_log_squared": fit_1overlog2,
        "winner_by_chi2": thread_a_winner,
        "winner_chi2": thread_a_winner_chi2,
        "reading": (
            f"At low conductor (log_cond<4.5), the {thread_a_winner} ansatz gives the lower chi². "
            "If 1/log² wins, it supports the literature hint that CFMS-style lower-order terms "
            "dominate at small N. If 1/log wins, classical Miller leading order is sufficient "
            "even at the extreme."
        ),
    }

    out = {
        "task": "literature-correspondence-followup threads A and B",
        "instance": "Harmonia_M2_sessionB",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "thread_A_low_conductor_ansatz_comparison": thread_a,
        "thread_B_rank_conditioned_gamma1_displacement": thread_b,
        "_meta": {
            "literature_source": "cartography/docs/literature_correspondence_F011.md (F2 and F7 audit entries)",
            "rationale": (
                "F2 audit: 'forced zeros may absorb repulsion rather than propagate it outward.' "
                "Test B: does rank 2 γ₁ sit higher than rank 0 γ₁? "
                "F7 audit: 'a 57% deficit at log_cond<4 exceeds 1/log extrapolation; test CFMS 1/log²'. "
                "Test A: fit both ansätze on low_cond subset."
            ),
        },
    }

    out_path = os.path.join("cartography", "docs", "wsw_F011_lit_followup_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\n[lit_followup] wrote {out_path}")
    print(f"[thread A winner] {thread_a_winner}")
    print(f"[thread B verdict] {thread_b.get('verdict', 'n/a')}")


if __name__ == "__main__":
    main()
