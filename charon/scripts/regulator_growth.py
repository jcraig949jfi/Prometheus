"""
Regulator Growth Law Investigation
Charon — 2026-04-15

Five-phase investigation of regulator scaling with rank and conductor:
  Phase 1: log-log scaling law characterization
  Phase 2: Distribution of log(regulator) by rank
  Phase 3: Regulator vs leading_term (BSD link)
  Phase 4: Lower bound on regulator vs conductor
  Phase 5: Reg × Sha / Tor² product distribution
"""

import json
import math
import sys
import time
import numpy as np
import psycopg2
from collections import defaultdict
from scipy import stats

DB = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')
OUT = r"F:\Prometheus\charon\data\regulator_growth.json"

def get_conn():
    return psycopg2.connect(**DB)


# ── Phase 1: Scaling law characterization ──────────────────────────────────

def phase1_scaling_law():
    """Fit log(reg) = a + b*log(cond) for each rank 1-5."""
    print("\n" + "="*70)
    print("PHASE 1: Scaling Law — log(reg) vs log(cond)")
    print("="*70)

    conn = get_conn()
    cur = conn.cursor()

    results = {}
    for r in range(1, 6):
        cur.execute("""
            SELECT regulator::double precision, conductor::double precision
            FROM ec_curvedata
            WHERE rank::int = %s
              AND regulator IS NOT NULL
              AND regulator::double precision > 0
              AND conductor::double precision > 0
        """, (r,))
        rows = cur.fetchall()
        if len(rows) < 10:
            print(f"  Rank {r}: only {len(rows)} curves, skipping")
            results[str(r)] = {"n": len(rows), "verdict": "INSUFFICIENT_DATA"}
            continue

        log_reg = np.array([math.log(row[0]) for row in rows])
        log_cond = np.array([math.log(row[1]) for row in rows])

        # Linear fit
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_cond, log_reg)

        # Check for curvature: fit quadratic
        coeffs = np.polyfit(log_cond, log_reg, 2)
        quad_coeff = coeffs[0]

        # Spearman (rank correlation, robust to outliers)
        rho_s, p_s = stats.spearmanr(log_cond, log_reg)

        # Residual analysis
        predicted = intercept + slope * log_cond
        residuals = log_reg - predicted
        res_skew = stats.skew(residuals)
        res_kurt = stats.kurtosis(residuals)

        print(f"  Rank {r}: n={len(rows):>8,}  slope(b)={slope:.4f}  "
              f"R²={r_value**2:.4f}  rho_s={rho_s:.4f}  quad={quad_coeff:.6f}")

        results[str(r)] = {
            "n": len(rows),
            "slope_b": round(slope, 6),
            "intercept_a": round(intercept, 6),
            "R_squared": round(r_value**2, 6),
            "std_err": round(std_err, 6),
            "spearman_rho": round(rho_s, 6),
            "spearman_p": float(p_s),
            "quadratic_coeff": round(quad_coeff, 8),
            "residual_skew": round(res_skew, 4),
            "residual_kurtosis": round(res_kurt, 4),
        }

    conn.close()

    # Test: does slope increase linearly with rank?
    slopes = [(int(r), v["slope_b"]) for r, v in results.items() if "slope_b" in v]
    if len(slopes) >= 3:
        ranks_arr = np.array([s[0] for s in slopes])
        slopes_arr = np.array([s[1] for s in slopes])
        sl2, int2, r2, p2, se2 = stats.linregress(ranks_arr, slopes_arr)
        print(f"\n  Slope vs rank: slope_of_slopes={sl2:.4f}  R²={r2**2:.4f}")
        results["slope_vs_rank"] = {
            "slope_of_slopes": round(sl2, 6),
            "intercept": round(int2, 6),
            "R_squared": round(r2**2, 6),
            "p_value": float(p2),
            "verdict": "LINEAR_SCALING" if r2**2 > 0.9 else "NONLINEAR"
        }

    return {"phase": "scaling_law", "results": results}


# ── Phase 2: Distribution characterization ─────────────────────────────────

def phase2_distribution():
    """Full distribution of log(regulator) by rank."""
    print("\n" + "="*70)
    print("PHASE 2: Distribution of log(regulator)")
    print("="*70)

    conn = get_conn()
    cur = conn.cursor()

    results = {}
    for r in range(0, 6):
        cur.execute("""
            SELECT regulator::double precision
            FROM ec_curvedata
            WHERE rank::int = %s
              AND regulator IS NOT NULL
              AND regulator::double precision > 0
        """, (r,))
        rows = cur.fetchall()
        if len(rows) < 10:
            results[str(r)] = {"n": len(rows), "verdict": "INSUFFICIENT_DATA"}
            continue

        regs = np.array([row[0] for row in rows])
        log_regs = np.log(regs)

        # Moments
        mean_lr = np.mean(log_regs)
        var_lr = np.var(log_regs)
        std_lr = np.std(log_regs)
        skew_lr = float(stats.skew(log_regs)) if std_lr > 1e-12 else 0.0
        kurt_lr = float(stats.kurtosis(log_regs)) if std_lr > 1e-12 else 0.0

        # Normality test on log(reg)
        if std_lr < 1e-12:
            shapiro_stat, shapiro_p = 1.0, 1.0  # degenerate (all same value)
        elif len(log_regs) <= 5000:
            shapiro_stat, shapiro_p = stats.shapiro(log_regs)
        else:
            # Shapiro breaks on large samples; use KS test against normal
            shapiro_stat, shapiro_p = stats.kstest(
                log_regs, 'norm', args=(mean_lr, std_lr))

        # Percentiles
        pcts = np.percentile(regs, [1, 5, 10, 25, 50, 75, 90, 95, 99])

        # Min regulator
        min_reg = float(np.min(regs))

        print(f"  Rank {r}: n={len(rows):>8,}  mean(log_r)={mean_lr:>8.3f}  "
              f"std={std_lr:.3f}  skew={skew_lr:.3f}  min_reg={min_reg:.6f}")

        results[str(r)] = {
            "n": len(rows),
            "min_regulator": min_reg,
            "max_regulator": float(np.max(regs)),
            "log_reg_mean": round(mean_lr, 6),
            "log_reg_variance": round(var_lr, 6),
            "log_reg_std": round(std_lr, 6),
            "log_reg_skewness": round(skew_lr, 4),
            "log_reg_kurtosis": round(kurt_lr, 4),
            "normality_stat": round(float(shapiro_stat), 6),
            "normality_p": float(shapiro_p),
            "normality_verdict": "NORMAL" if shapiro_p > 0.05 else "NON_NORMAL",
            "percentiles": {
                "p1": round(pcts[0], 6), "p5": round(pcts[1], 6),
                "p10": round(pcts[2], 6), "p25": round(pcts[3], 6),
                "p50": round(pcts[4], 6), "p75": round(pcts[5], 6),
                "p90": round(pcts[6], 6), "p95": round(pcts[7], 6),
                "p99": round(pcts[8], 6),
            },
        }

    conn.close()

    # Variance trend
    var_by_rank = [(int(r), v["log_reg_variance"])
                   for r, v in results.items() if "log_reg_variance" in v and int(r) >= 1]
    if len(var_by_rank) >= 3:
        ranks_arr = np.array([v[0] for v in var_by_rank])
        vars_arr = np.array([v[1] for v in var_by_rank])
        sl, it, rv, pv, se = stats.linregress(ranks_arr, vars_arr)
        print(f"\n  Variance vs rank: slope={sl:.4f}  R²={rv**2:.4f}")
        results["variance_trend"] = {
            "slope": round(sl, 4),
            "R_squared": round(rv**2, 4),
            "verdict": "VARIANCE_GROWS" if sl > 0 and pv < 0.05 else "NO_TREND"
        }

    return {"phase": "distribution", "results": results}


# ── Phase 3: Regulator vs leading_term ──────────────────────────────────────

def phase3_leading_term():
    """Correlation between regulator and leading_term via lfunc_lfunctions."""
    print("\n" + "="*70)
    print("PHASE 3: Regulator vs Leading Term (BSD link)")
    print("="*70)

    conn = get_conn()
    cur = conn.cursor()

    # Pre-load leading_term lookup from lfunc_lfunctions (much faster than SQL join)
    print("  Loading lfunc leading_term lookup...")
    cur.execute("""
        SELECT origin, leading_term::double precision
        FROM lfunc_lfunctions
        WHERE origin LIKE 'EllipticCurve/Q/%%'
          AND leading_term IS NOT NULL
          AND leading_term::double precision > 0
    """)
    lt_lookup = {}
    for origin, lt in cur:
        lt_lookup[origin] = lt  # last one wins for duplicates, fine
    print(f"  Loaded {len(lt_lookup)} L-function leading terms")

    results = {}
    for r in range(1, 4):
        # Get ec_curvedata for this rank, one per iso class
        cur.execute("""
            SELECT regulator::double precision,
                   conductor::double precision,
                   lmfdb_iso,
                   sha::double precision,
                   torsion::double precision
            FROM ec_curvedata
            WHERE rank::int = %s
              AND regulator IS NOT NULL
              AND regulator::double precision > 0
            ORDER BY lmfdb_iso, lmfdb_label
        """, (r,))

        # Deduplicate: one curve per iso class
        seen_iso = set()
        matched = []
        for reg, cond, iso, sha, tor in cur:
            if iso in seen_iso:
                continue
            seen_iso.add(iso)
            # Build origin: '630.a' -> 'EllipticCurve/Q/630/a'
            origin = 'EllipticCurve/Q/' + iso.replace('.', '/')
            lt = lt_lookup.get(origin)
            if lt and lt > 0:
                matched.append((reg, cond, lt, sha, tor))

        rows = matched

        if len(rows) < 10:
            print(f"  Rank {r}: only {len(rows)} matched rows, skipping")
            results[str(r)] = {"n": len(rows), "verdict": "INSUFFICIENT_MATCH"}
            continue

        log_reg = np.array([math.log(row[0]) for row in rows])
        log_cond = np.array([math.log(row[1]) for row in rows])
        log_lt = np.array([math.log(row[2]) for row in rows])

        # Correlation: log(reg) vs log(leading_term)
        rho_rl, p_rl = stats.spearmanr(log_reg, log_lt)

        # BSD: leading_term ∝ Reg * Sha * (stuff) / Tor²
        # So log(leading_term) ≈ log(Reg) + log(Sha) + ...
        # If Sha = 1 for most curves, leading_term ∝ Reg * (Omega * c_p) / Tor²
        # Linear fit
        sl, it, rv, pv, se = stats.linregress(log_reg, log_lt)

        print(f"  Rank {r}: n={len(rows):>6,}  rho(log_r,log_lt)={rho_rl:.4f}  "
              f"slope={sl:.4f}  R²={rv**2:.4f}")

        results[str(r)] = {
            "n": len(rows),
            "spearman_rho_reg_lt": round(rho_rl, 6),
            "p_value": float(p_rl),
            "linreg_slope": round(sl, 6),
            "linreg_R2": round(rv**2, 6),
        }

    conn.close()
    return {"phase": "leading_term", "results": results}


# ── Phase 4: Lower bound on regulator ──────────────────────────────────────

def phase4_lower_bound():
    """Min regulator by conductor decade and rank; fit min_reg ~ N^alpha."""
    print("\n" + "="*70)
    print("PHASE 4: Lower Bound — min(regulator) vs conductor")
    print("="*70)

    conn = get_conn()
    cur = conn.cursor()

    results = {}
    for r in range(1, 6):
        cur.execute("""
            SELECT conductor::double precision, regulator::double precision
            FROM ec_curvedata
            WHERE rank::int = %s
              AND regulator IS NOT NULL
              AND regulator::double precision > 0
              AND conductor::double precision > 0
            ORDER BY conductor::double precision
        """, (r,))
        rows = cur.fetchall()
        if len(rows) < 50:
            results[str(r)] = {"n": len(rows), "verdict": "INSUFFICIENT_DATA"}
            continue

        conds = np.array([row[0] for row in rows])
        regs = np.array([row[1] for row in rows])

        # Bin by conductor decade (powers of 10)
        max_log = math.log10(max(conds))
        bins = []
        for decade_start in range(1, int(max_log) + 1):
            lo = 10 ** decade_start
            hi = 10 ** (decade_start + 1)
            mask = (conds >= lo) & (conds < hi)
            if np.sum(mask) >= 5:
                min_r = float(np.min(regs[mask]))
                med_cond = float(np.median(conds[mask]))
                bins.append({
                    "decade": decade_start,
                    "n": int(np.sum(mask)),
                    "min_reg": min_r,
                    "median_cond": med_cond,
                    "p5_reg": float(np.percentile(regs[mask], 5)),
                })

        # Fit min_reg vs conductor: log(min_reg) = alpha * log(median_cond) + beta
        if len(bins) >= 3:
            log_mc = np.array([math.log(b["median_cond"]) for b in bins])
            log_mr = np.array([math.log(b["min_reg"]) for b in bins])
            sl, it, rv, pv, se = stats.linregress(log_mc, log_mr)

            # Also fit p5 (more robust)
            log_p5 = np.array([math.log(b["p5_reg"]) for b in bins])
            sl5, it5, rv5, pv5, se5 = stats.linregress(log_mc, log_p5)

            print(f"  Rank {r}: {len(bins)} decades  alpha_min={sl:.4f}(R²={rv**2:.3f})  "
                  f"alpha_p5={sl5:.4f}(R²={rv5**2:.3f})")
        else:
            sl, rv, sl5, rv5 = None, None, None, None
            print(f"  Rank {r}: only {len(bins)} decades, insufficient for fit")

        results[str(r)] = {
            "n": len(rows),
            "n_decades": len(bins),
            "bins": bins,
            "alpha_min": round(sl, 6) if sl is not None else None,
            "alpha_min_R2": round(rv**2, 4) if rv is not None else None,
            "alpha_p5": round(sl5, 6) if sl5 is not None else None,
            "alpha_p5_R2": round(rv5**2, 4) if rv5 is not None else None,
        }

    conn.close()

    # Does alpha increase with rank?
    alphas = [(int(r), v["alpha_min"]) for r, v in results.items()
              if v.get("alpha_min") is not None]
    if len(alphas) >= 3:
        ra = np.array([a[0] for a in alphas])
        aa = np.array([a[1] for a in alphas])
        sl, it, rv, pv, se = stats.linregress(ra, aa)
        print(f"\n  Alpha vs rank: slope={sl:.4f}  R²={rv**2:.4f}")
        results["alpha_vs_rank"] = {
            "slope": round(sl, 6),
            "R_squared": round(rv**2, 4),
            "verdict": "BOUND_TIGHTENS" if sl > 0 and pv < 0.1 else "NO_TREND"
        }

    return {"phase": "lower_bound", "results": results}


# ── Phase 5: Reg × Sha / Tor² product ─────────────────────────────────────

def phase5_bsd_product():
    """Investigate Reg × Sha / Tor² vs individual factors."""
    print("\n" + "="*70)
    print("PHASE 5: BSD Product — Reg × Sha / Tor²")
    print("="*70)

    conn = get_conn()
    cur = conn.cursor()

    results = {}
    for r in range(1, 6):
        cur.execute("""
            SELECT regulator::double precision,
                   sha::double precision,
                   torsion::double precision,
                   conductor::double precision
            FROM ec_curvedata
            WHERE rank::int = %s
              AND regulator IS NOT NULL
              AND regulator::double precision > 0
              AND sha IS NOT NULL
              AND sha::double precision > 0
              AND torsion IS NOT NULL
              AND torsion::double precision > 0
        """, (r,))
        rows = cur.fetchall()
        if len(rows) < 30:
            results[str(r)] = {"n": len(rows), "verdict": "INSUFFICIENT_DATA"}
            continue

        regs = np.array([row[0] for row in rows])
        shas = np.array([row[1] for row in rows])
        tors = np.array([row[2] for row in rows])
        conds = np.array([row[3] for row in rows])

        product = regs * shas / (tors ** 2)

        log_reg = np.log(regs)
        log_sha = np.log(shas)
        log_prod = np.log(product)
        log_cond = np.log(conds)

        # Coefficient of variation for each
        cv_reg = np.std(log_reg) / abs(np.mean(log_reg)) if abs(np.mean(log_reg)) > 1e-10 else float('inf')
        cv_sha = np.std(log_sha) / abs(np.mean(log_sha)) if abs(np.mean(log_sha)) > 1e-10 else float('inf')
        cv_prod = np.std(log_prod) / abs(np.mean(log_prod)) if abs(np.mean(log_prod)) > 1e-10 else float('inf')

        # Correlation with conductor
        rho_reg, _ = stats.spearmanr(log_cond, log_reg)
        rho_sha, _ = stats.spearmanr(log_cond, log_sha)
        rho_prod, _ = stats.spearmanr(log_cond, log_prod)

        # Is product tighter than individual?
        std_reg = np.std(log_reg)
        std_sha = np.std(log_sha)
        std_prod = np.std(log_prod)

        # After conditioning on conductor (residual variance)
        # Fit log(X) = a + b*log(N), measure residual std
        def residual_std(x, y):
            sl, it, _, _, _ = stats.linregress(y, x)
            return float(np.std(x - it - sl * y))

        res_reg = residual_std(log_reg, log_cond)
        res_sha = residual_std(log_sha, log_cond) if not np.all(shas == 1) else 0.0
        res_prod = residual_std(log_prod, log_cond)

        tighter = std_prod < std_reg and std_prod < std_sha

        print(f"  Rank {r}: n={len(rows):>6,}  std(log): reg={std_reg:.3f} sha={std_sha:.3f} "
              f"prod={std_prod:.3f}  tighter={'YES' if tighter else 'NO'}")

        # Sha distribution
        sha_vals, sha_counts = np.unique(shas, return_counts=True)
        sha_dist = {str(int(v)): int(c) for v, c in
                    sorted(zip(sha_vals, sha_counts), key=lambda x: -x[1])[:10]}
        sha1_frac = float(np.mean(shas == 1.0))

        results[str(r)] = {
            "n": len(rows),
            "std_log_reg": round(std_reg, 6),
            "std_log_sha": round(std_sha, 6),
            "std_log_product": round(std_prod, 6),
            "residual_std_reg": round(res_reg, 6),
            "residual_std_sha": round(res_sha, 6),
            "residual_std_product": round(res_prod, 6),
            "rho_cond_reg": round(rho_reg, 6),
            "rho_cond_sha": round(rho_sha, 6),
            "rho_cond_product": round(rho_prod, 6),
            "product_tighter": tighter,
            "sha_1_fraction": round(sha1_frac, 4),
            "sha_distribution_top10": sha_dist,
        }

    conn.close()
    return {"phase": "bsd_product", "results": results}


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print("Charon — Regulator Growth Law Investigation")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    all_results = {}

    all_results["phase1"] = phase1_scaling_law()
    all_results["phase2"] = phase2_distribution()
    all_results["phase3"] = phase3_leading_term()
    all_results["phase4"] = phase4_lower_bound()
    all_results["phase5"] = phase5_bsd_product()

    elapsed = time.time() - t0
    all_results["meta"] = {
        "elapsed_seconds": round(elapsed, 1),
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
    }

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    # Phase 1 slopes
    p1 = all_results["phase1"]["results"]
    slopes = {r: p1[r]["slope_b"] for r in ["1","2","3","4","5"] if "slope_b" in p1.get(r, {})}
    print(f"  Scaling slopes b(r): {slopes}")
    if "slope_vs_rank" in p1:
        print(f"  Slope-of-slopes: {p1['slope_vs_rank']}")

    # Phase 2 variance trend
    p2 = all_results["phase2"]["results"]
    if "variance_trend" in p2:
        print(f"  Variance trend: {p2['variance_trend']}")

    # Phase 4 alpha
    p4 = all_results["phase4"]["results"]
    alphas = {r: p4[r]["alpha_min"] for r in ["1","2","3","4","5"]
              if p4.get(r, {}).get("alpha_min") is not None}
    print(f"  Lower bound exponents alpha(r): {alphas}")

    # Phase 5 tightness
    p5 = all_results["phase5"]["results"]
    for r in ["1","2","3","4","5"]:
        if r in p5 and "product_tighter" in p5[r]:
            print(f"  Rank {r}: product tighter than individuals = {p5[r]['product_tighter']}")

    print(f"\n  Elapsed: {elapsed:.1f}s")

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, (np.bool_,)):
                return bool(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)

    with open(OUT, 'w') as f:
        json.dump(all_results, f, indent=2, cls=NumpyEncoder)
    print(f"\n  Results saved to {OUT}")


if __name__ == "__main__":
    main()
