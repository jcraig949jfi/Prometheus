"""
keating_snaith_moments.py — Report 4 execution per Aporia deep_research_batch2.

Compute Keating-Snaith moments M_k(X) = mean(leading_term^k) for EC L-functions
binned by conductor decade, stratified by analytic_rank. Report the ratio
R_k(X) = M_k(X) / (log X)^{k(k-1)/2} per cell.

Per sessionA's hand-off (2026-04-18): moment-ratio convergence rate IS the
phoneme. Pattern 20 discipline is reflexive — DO NOT pool across conductor
decades OR across ranks.

Data source: prometheus_fire.zeros.object_zeros.leading_term (2,009,089 EC
rows, 100% coverage, all rank 0-4, conductor 10^1..10^6).

Interpretation anchor (Aporia Report 4):
  - leading_term is L^(r)(1,E)/r! — rank 0 ⇒ L(1,E); rank 1 ⇒ L'(1,E); etc.
  - Rank 0 aligns with SO_even symmetry type, rank 1 with SO_odd. Moments
    are family-conditional; stratifying by rank IS stratifying by symmetry
    type.
  - Keating-Snaith / Conrey-Keating exponent k(k-1)/2 applied per rank
    following Aporia's directive. The constant prefactor a_E(k)·g_SO(k) is
    NOT computed here; the output is the empirical ratio M_k(X) /
    (log X)^{k(k-1)/2}, which should approach that constant as X grows if
    the RMT prediction holds.

Discipline notes:
  - Pattern 20: report per (rank, decade) cell, never pooled. No "global
    moment" headline.
  - Pattern 4: bin boundaries on log10(conductor) are explicit; no LIMIT N.
  - Pattern 7: F003 BSD parity calibration untouched. No anchor breakage.
  - Pattern 1: leading_term and conductor are distinct observables; M_k vs
    log X is not a near-identity. But: leading_term is rank-dependent, so
    joint analysis with P023 rank is expected (not a tautology, an
    orthogonal-axis decomposition).
"""
import json
import math
import os
from datetime import datetime, timezone

import numpy as np
import psycopg2

PG = dict(host="192.168.1.176", port=5432, dbname="prometheus_fire",
          user="postgres", password="prometheus", connect_timeout=10)

RANKS = [0, 1, 2, 3]        # rank 4 has only 1 row; skip.
K_VALUES = [1, 2, 3, 4]     # Keating-Snaith moment orders.
DECADE_EDGES = [(100, 1000), (1000, 10_000), (10_000, 100_000),
                (100_000, 1_000_000), (1_000_000, 10_000_000)]
MIN_PER_CELL = 100


def load_cells():
    """For each (rank, decade) cell with n>=MIN_PER_CELL, return
    (rank, lo, hi, leading_term array)."""
    with psycopg2.connect(**PG) as conn:
        cur = conn.cursor()
        cells = []
        for rank in RANKS:
            for lo, hi in DECADE_EDGES:
                cur.execute("""
                    SELECT leading_term
                    FROM zeros.object_zeros
                    WHERE object_type = 'elliptic_curve'
                      AND analytic_rank = %s
                      AND conductor >= %s AND conductor < %s
                      AND leading_term IS NOT NULL
                      AND leading_term > 0
                """, (rank, lo, hi))
                vals = np.array([r[0] for r in cur.fetchall()], dtype=float)
                if vals.size >= MIN_PER_CELL:
                    cells.append((rank, lo, hi, vals))
    return cells


def cell_moments(vals, k_values):
    """Raw moments and their standard errors (SE via bootstrap-free
    delta-method formula: Var(mean X^k) ~ Var(X^k)/n)."""
    out = {}
    n = vals.size
    for k in k_values:
        xk = vals ** k
        mk = float(xk.mean())
        var_xk = float(xk.var(ddof=1))
        se = math.sqrt(var_xk / n) if n > 1 else 0.0
        out[str(k)] = {"M_k": mk, "se": se}
    return out


def convergence_fit(x_log, y, label):
    """Linear fit of y vs x_log (log of decade midpoint). Slope + SE.
    Positive slope ⇒ ratio growing with log X (phoneme: slow convergence).
    Slope near zero ⇒ already-convergent (phoneme: fast convergence)."""
    if len(x_log) < 2:
        return {"label": label, "n_points": len(x_log), "skipped": "n<2"}
    x = np.asarray(x_log, dtype=float)
    y = np.asarray(y, dtype=float)
    mx = x.mean()
    my = y.mean()
    num = ((x - mx) * (y - my)).sum()
    den = ((x - mx) ** 2).sum()
    if den == 0:
        return {"label": label, "n_points": len(x_log), "skipped": "zero variance in x"}
    slope = float(num / den)
    intercept = float(my - slope * mx)
    pred = slope * x + intercept
    resid = y - pred
    if len(x_log) > 2:
        s2 = float((resid ** 2).sum() / (len(x_log) - 2))
        slope_se = math.sqrt(s2 / den) if den > 0 else 0.0
    else:
        s2 = 0.0
        slope_se = 0.0
    return {
        "label": label,
        "n_points": len(x_log),
        "slope": slope,
        "slope_se": slope_se,
        "intercept": intercept,
        "resid_rms": float(math.sqrt((resid ** 2).mean())),
        "convergence_reading": (
            "FAST (slope near 0; ratio stable)" if abs(slope) < 2 * max(slope_se, 1e-12) else
            "SLOW (slope growing with log X)" if slope > 0 else
            "SHRINKING (ratio decreasing — over-estimated prediction exponent?)"
        ),
    }


def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[keating_snaith] start {started}")

    cells = load_cells()
    print(f"[keating_snaith] cells with n>={MIN_PER_CELL}: {len(cells)}")

    # per_cell[rank][decade] = {"M_k": {...}, "R_k": {...}, "n": N, "log_X_mid": ...}
    per_cell = {str(r): {} for r in RANKS}
    for rank, lo, hi, vals in cells:
        x_mid = math.sqrt(lo * hi)
        log_x = math.log(x_mid)
        mk = cell_moments(vals, K_VALUES)
        rk = {}
        for k in K_VALUES:
            expo = k * (k - 1) / 2.0
            denom = log_x ** expo if expo > 0 else 1.0  # k=1 ⇒ denom=1
            ratio = mk[str(k)]["M_k"] / denom
            # SE of ratio ≈ SE_Mk / denom (deterministic denom)
            ratio_se = mk[str(k)]["se"] / denom if denom > 0 else None
            rk[str(k)] = {"R_k": ratio, "se": ratio_se,
                          "exponent_k(k-1)/2": expo,
                          "denom_logX_to_exp": denom}
        key = f"{lo}-{hi}"
        per_cell[str(rank)][key] = {
            "n": int(vals.size),
            "conductor_range": [lo, hi],
            "log_X_mid": log_x,
            "M_k": mk,
            "R_k": rk,
        }
        print(f"  rank={rank} decade={key} n={vals.size} "
              f"M1={mk['1']['M_k']:.3f} M2={mk['2']['M_k']:.3f} "
              f"M3={mk['3']['M_k']:.3f} M4={mk['4']['M_k']:.3f}")

    # Convergence rate per (rank, k): slope of R_k(log X) vs log X across decades
    convergence = {}
    for rank_str, decades in per_cell.items():
        conv_k = {}
        decade_sorted = sorted(decades.keys(), key=lambda k: decades[k]["log_X_mid"])
        x_log = [decades[d]["log_X_mid"] for d in decade_sorted]
        for k in K_VALUES:
            y = [decades[d]["R_k"][str(k)]["R_k"] for d in decade_sorted]
            conv_k[str(k)] = convergence_fit(x_log, y, f"rank={rank_str}_k={k}")
            conv_k[str(k)]["decades_used"] = decade_sorted
            conv_k[str(k)]["R_k_sequence"] = y
        convergence[rank_str] = conv_k

    # Shape summary — per-rank phoneme read-out
    phoneme_lines = []
    for rank_str in per_cell:
        for k in K_VALUES:
            c = convergence[rank_str][str(k)]
            if "slope" in c:
                phoneme_lines.append(
                    f"rank={rank_str} k={k}: slope={c['slope']:+.3f}±{c['slope_se']:.3f} "
                    f"({c['convergence_reading'].split(' ')[0]})"
                )
            else:
                phoneme_lines.append(f"rank={rank_str} k={k}: {c.get('skipped','?')}")

    results = {
        "task": "keating_snaith_report4_moments",
        "instance": "Harmonia_M2_sessionC",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "data_source": "prometheus_fire.zeros.object_zeros (elliptic_curve, leading_term > 0)",
        "config": {
            "ranks": RANKS,
            "k_values": K_VALUES,
            "decade_edges": DECADE_EDGES,
            "min_per_cell": MIN_PER_CELL,
            "exponent_formula": "k(k-1)/2 per Aporia Report 4 (SO family)",
            "decade_midpoint": "geometric mean of [lo, hi)",
        },
        "per_cell": per_cell,
        "convergence_per_rank_k": convergence,
        "phoneme_summary": phoneme_lines,
        "interpretation": (
            "R_k(X) = M_k(X) / (log X)^{k(k-1)/2}. If Keating-Snaith / Conrey-Keating "
            "prediction holds, R_k approaches the constant a_E(k)·g_SO(k) as X grows. "
            "The SLOPE of R_k(log X) across conductor decades is the convergence rate — "
            "near-zero slope at large X means fast convergence (phoneme: 'RMT already "
            "dominant at this conductor'); growing slope means slow convergence "
            "(phoneme: 'finite-N corrections still large'); shrinking slope means "
            "the exponent k(k-1)/2 over-estimates the actual growth (phoneme: "
            "'different symmetry type' OR 'non-asymptotic regime')."
        ),
        "pattern_20_discipline": [
            "Moments computed PER (rank, conductor-decade) CELL — never pooled.",
            "Rank 0 (SO_even conjecture) and rank 1 (SO_odd conjecture) reported separately.",
            "No 'global moment' summary — all statistics are per-cell or per-rank trend.",
        ],
        "caveats": [
            "Aporia-specified exponent k(k-1)/2 applied uniformly across ranks. The "
            "actual RMT prediction for SO_even vs SO_odd ensembles can differ (e.g. "
            "Conrey-Snaith 2007 gives distinct forms for L(1/2) vs L'(1/2) moments). "
            "A finer Pattern-5 calibration pass against Conrey-Farmer-Keating-Rubinstein-Snaith "
            "predictions is the natural next step; this run reports empirical ratios.",
            "leading_term = L^(r)(1,E)/r! — rank matters: rank 0 is L(1,E), rank 1 is L'(1,E). "
            "Comparing moments across ranks without rank-conditioning is Pattern 20.",
            "Conductor bins are logarithmically natural but unit-arbitrary — rescaling to "
            "e-powers or 2-powers would shift R_k constants but not convergence-rate slopes.",
        ],
        "followups_motivated": [
            "keating_snaith_arithmetic_factor (compute a_E(k) Euler product for each curve → divide out → residual is pure RMT)",
            "wsw_F041_moment_convergence (nominate convergence rate as new live specimen F041 if any slope is significantly non-zero)",
            "block_shuffle_leading_term (sanity-check: shuffle leading_term within (rank, decade) cells; per-cell M_k is invariant by construction, so this is actually a Pattern 7 calibration — verifies pipeline)",
            "katz_sarnak_vs_rank (verify rank-0 leading_term distribution matches SO_even central-value distribution; rank-1 matches SO_odd derivative)",
            "arithmetic_factor_stratified_by_P021 (bad-prime-count) — Euler-product dependence on ramification",
        ],
    }

    out_path = os.path.join("cartography", "docs", "keating_snaith_moments_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"[keating_snaith] wrote {out_path}")
    print(f"[keating_snaith] phoneme lines:")
    for line in phoneme_lines:
        print(f"  {line}")


if __name__ == "__main__":
    main()
