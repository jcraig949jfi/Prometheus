"""wsw_F011_rank0_residual.py — Paths 1 & 2 combined.

Path 1: the rank-0 deficit is the LARGEST of all ranks (46.4%), yet rank 0 has
NO forced central zero. This is backwards from naive excised-ensemble theory.
Test: does the rank-0-only deficit shrink monotonically with conductor like the
pooled deficit does? If yes → fully excised-ensemble consistent (rank 0 = SO_even
with its own finite-conductor correction). If it stays elevated at large conductor
→ rank-0 residual is the true non-excised-ensemble signature.

Path 2: fit a decay ansatz to the rank-0 deficit vs conductor. If deficit
extrapolates to ~0 at conductor → ∞, fully finite-conductor / consistent with
central-zero-forcing framework. If it extrapolates to a positive ε₀ > 0, that
ε₀ is the genuine residual frontier — the magnitude of unexplained structure.

Data: prometheus_fire.zeros.object_zeros × lmfdb.public.ec_curvedata with rank=0.
Output: cartography/docs/wsw_F011_rank0_residual_results.json
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
MIN_STRATUM_N = 500  # tighter than 100 for cleaner fits


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
    print(f"[rank0_residual] start {started}")

    df = fetch_data()
    df["rank"] = df["rank"].astype(int)
    z1u = unfold(df["z1"].to_numpy(float), df["conductor"].to_numpy(float))
    z2u = unfold(df["z2"].to_numpy(float), df["conductor"].to_numpy(float))
    df["gap1"] = z2u - z1u
    df = df.loc[np.isfinite(df["gap1"]) & (df["gap1"] > 0)].copy()
    df["log_cond"] = np.log10(df["conductor"].astype(float))
    print(f"[data] {len(df)} rows; rank dist: {dict(df['rank'].value_counts().head(5))}")

    # Focus on rank 0; finer conductor bins than pooled case (20 bins over observed log_cond range)
    df0 = df.loc[df["rank"] == 0].copy()
    print(f"[rank0] n={len(df0)}")
    q = np.quantile(df0["log_cond"], np.linspace(0, 1, 21))
    q[0] -= 1e-9; q[-1] += 1e-9
    df0["cond_bin"] = np.digitize(df0["log_cond"], q[1:-1])

    per_bin = []
    for b in sorted(df0["cond_bin"].unique()):
        sub = df0.loc[df0["cond_bin"] == b]
        n = len(sub)
        if n < MIN_STRATUM_N:
            continue
        vals = sub["gap1"].to_numpy(float)
        var = float(np.var(vals, ddof=1))
        deficit = 100.0 * (GUE_VAR - var) / GUE_VAR
        se_var = var * math.sqrt(2.0 / max(n - 1, 1))
        se_def = 100.0 * se_var / GUE_VAR
        mean_log_cond = float(sub["log_cond"].mean())
        per_bin.append({
            "bin": int(b), "mean_log_cond": mean_log_cond, "n": int(n),
            "var": var, "deficit_pct": deficit, "se_deficit_pct": se_def,
        })

    print("[rank0 per conductor bin]")
    for b in per_bin:
        print(f"  bin{b['bin']:>2}  log_cond={b['mean_log_cond']:.3f}  n={b['n']:>6}  "
              f"def={b['deficit_pct']:5.2f}% (se={b['se_deficit_pct']:.2f})")

    # ----- Path 2: decay fits -----
    x = np.array([b["mean_log_cond"] for b in per_bin])
    y = np.array([b["deficit_pct"] for b in per_bin])
    sigma = np.array([b["se_deficit_pct"] for b in per_bin])

    # Model A: linear in log_cond (pure scaling)
    # deficit = A * log_cond + B  → extrapolate to log_cond → ∞
    def linear(xv, A, B):
        return A * xv + B
    try:
        pA, covA = optimize.curve_fit(linear, x, y, sigma=sigma, absolute_sigma=True)
        seA = np.sqrt(np.diag(covA))
        residA = y - linear(x, *pA)
        chi2A = float(((residA / sigma) ** 2).sum())
    except Exception as e:
        pA = seA = None
        chi2A = None

    # Model B: power-law decay to asymptote ε₀
    # deficit = ε₀ + C * 10^(-β * log_cond) = ε₀ + C * cond^(-β)
    def power_decay(xv, eps0, C, beta):
        return eps0 + C * 10 ** (-beta * xv)
    try:
        pB, covB = optimize.curve_fit(power_decay, x, y, sigma=sigma, absolute_sigma=True,
                                       p0=[0.0, 100.0, 0.3],
                                       bounds=([-10, 0, 0.01], [60, 1e4, 5]))
        seB = np.sqrt(np.diag(covB))
        residB = y - power_decay(x, *pB)
        chi2B = float(((residB / sigma) ** 2).sum())
    except Exception as e:
        pB = seB = None
        chi2B = None

    print(f"[fit A linear]     A={pA[0]:.3f}±{seA[0]:.3f}, B={pA[1]:.3f}±{seA[1]:.3f}, chi2={chi2A:.1f}")
    if pB is not None:
        print(f"[fit B power]      eps0={pB[0]:.3f}±{seB[0]:.3f}, C={pB[1]:.2e}, beta={pB[2]:.3f}, chi2={chi2B:.1f}")

    # Residual at log_cond → ∞
    # Linear model: extrapolation = A * log_cond + B; meaningless as limit (diverges)
    # but interpretable at an "infinity" decade, say log_cond = 10:
    linear_at_inf_decade = float(linear(10.0, *pA)) if pA is not None else None

    # Power-law model: extrapolation = eps0
    power_eps0 = float(pB[0]) if pB is not None else None
    power_eps0_se = float(seB[0]) if seB is not None else None
    power_z_from_zero = (power_eps0 / power_eps0_se) if (power_eps0 is not None and power_eps0_se and power_eps0_se > 0) else None

    # ----- Path 1 verdict -----
    # If power-law ε₀ is significantly > 0 (z >= 3), rank-0 has a genuine residual.
    # If ε₀ is consistent with 0, rank 0 is fully excised-ensemble-decaying.
    if power_eps0 is not None and power_z_from_zero is not None:
        if power_eps0 < 3.0 and abs(power_z_from_zero) < 2.0:
            rank0_verdict = "FULLY_FINITE_CONDUCTOR"
            rank0_reading = (f"Power-law fit extrapolates rank-0 deficit to ε₀={power_eps0:.2f}% ± "
                             f"{power_eps0_se:.2f} at conductor → ∞ (z={power_z_from_zero:.2f} from 0). "
                             f"Rank 0 is fully consistent with finite-conductor central-zero-forcing "
                             f"decay — no non-excised-ensemble residual at this data.")
        elif power_eps0 >= 3.0 and power_z_from_zero >= 3.0:
            rank0_verdict = "RESIDUAL_NON_EXCISED"
            rank0_reading = (f"Power-law fit: rank-0 deficit extrapolates to ε₀={power_eps0:.2f}% ± "
                             f"{power_eps0_se:.2f} at conductor → ∞, z={power_z_from_zero:.2f} from 0. "
                             f"This is the genuine non-excised-ensemble residual at rank 0 — magnitude "
                             f"of unexplained structure in first-gap variance.")
        else:
            rank0_verdict = "MARGINAL"
            rank0_reading = (f"Power-law ε₀={power_eps0:.2f}%, z={power_z_from_zero:.2f}. "
                             f"Between the 'fully decaying' and 'significant residual' criteria.")
    else:
        rank0_verdict = "FIT_FAILED"
        rank0_reading = "Power-law fit failed to converge on the rank-0 data."

    # ----- Theoretical magnitude reference (Path 2 closure) -----
    # For EC L-functions at conductor N, the one-level density for SO(even) family
    # at the scaling γ·log(N)/(2π) predicts a first-zero density that deviates from
    # GUE at gamma_1 ~ 1/log(N). Heuristically, the first-gap variance deficit
    # scales like 1/log(N)^2 at leading order (Conrey-Farmer-Mezzadri-Snaith).
    # At log_cond = 5.2 (our pooled center), log(N) ≈ 12, so 1/log(N)^2 ≈ 0.007.
    # This is a HEURISTIC only; the Duenez-HKMS closed-form is more complex.
    # If our ε₀ > a few %, the power-law rank-0 fit disagrees with the
    # CFMS asymptotic leading order.
    theoretical_heuristic = {
        "leading_order_1_over_logN_squared": 1.0 / 12.0 ** 2 * 100.0,  # ~0.69% at log_cond=5.2
        "caveat": ("This is a 1/log(N)² heuristic, not the full Duenez-HKMS closed-form. "
                   "A proper comparison would require computing the one-level density "
                   "for SO(even) at γ=γ₁·log(N)/(2π) and integrating."),
    }

    out = {
        "task": "Path 1+2: rank-0 conductor-window decay and residual extrapolation",
        "instance": "Harmonia_M2_sessionB",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "n_rank0": int(len(df0)),
        "n_bins_used": len(per_bin),
        "per_conductor_bin": per_bin,
        "fit_linear": {
            "slope_A": float(pA[0]) if pA is not None else None,
            "intercept_B": float(pA[1]) if pA is not None else None,
            "se_A": float(seA[0]) if seA is not None else None,
            "se_B": float(seA[1]) if seA is not None else None,
            "chi2": chi2A,
            "extrapolation_at_log_cond_10": linear_at_inf_decade,
            "note": "Linear model has no well-defined limit; extrapolated only for reference.",
        },
        "fit_power_law": {
            "epsilon_0_asymptotic_deficit_pct": power_eps0,
            "se_epsilon_0": power_eps0_se,
            "z_from_zero": power_z_from_zero,
            "C_amplitude": float(pB[1]) if pB is not None else None,
            "beta_exponent": float(pB[2]) if pB is not None else None,
            "chi2": chi2B,
            "model": "deficit = eps_0 + C * conductor^(-beta)",
        },
        "rank0_verdict": rank0_verdict,
        "rank0_reading": rank0_reading,
        "theoretical_reference_heuristic": theoretical_heuristic,
        "path_1_finding": "rank 0 conductor-window scaling characterized with decay fit",
        "path_2_finding": (f"Power-law extrapolates to ε₀={power_eps0:.2f}%. "
                           f"Compare to CFMS heuristic ~0.7% at our conductor range. "
                           f"If ε₀ » 0.7%, the 1/log(N)² leading asymptotic is insufficient."),
        "_meta": {
            "aporia_source": "deep_research_batch1.md Report 1",
            "gue_var_baseline": GUE_VAR,
            "min_stratum_n": MIN_STRATUM_N,
            "notes": [
                "Rank 0 has SO_even / U symmetry depending on family definition; both predict a finite-conductor deficit that decays.",
                "20-bin conductor decile for rank 0 gives finer resolution than the 10-bin pooled analysis.",
                "Power-law is a phenomenological fit, not a derivation; epsilon_0 is an empirical frontier estimate.",
            ],
        },
    }

    out_path = os.path.join("cartography", "docs", "wsw_F011_rank0_residual_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\n[rank0_residual] wrote {out_path}")
    print(f"[verdict] {rank0_verdict}")
    print(f"[reading] {rank0_reading}")


if __name__ == "__main__":
    main()
