"""
Charon Frontier Batch 4: 5 hypothesis tests on nf_fields (22M rows).
Tests: H11 (ADE gatekeeping), H47 (r2/degree phase transition),
       H82 (Mahler measure floor), H83 (hR/sqrt(d) product law),
       H15 (tower termination).
"""

import json
import math
import time
import warnings
from pathlib import Path

import numpy as np
import psycopg2
from scipy import stats

warnings.filterwarnings("ignore")

DB = dict(host="localhost", port=5432, dbname="lmfdb", user="postgres", password="prometheus")
RESULTS = {}

# Known transitive group identifiers for S_n, A_n, C_n, D_n
# Format: galois_label = "nTk"
# C_n: always T1 for degree n
# D_n (dihedral): degree 3: T1(=C3, skip); degree 4: T3; degree 5: T2; degree 6: T3; degree 7: T2; degree 8: T6
# S_n: last transitive group: deg2=T1, deg3=T2, deg4=T5, deg5=T5, deg6=T16, deg7=T7, deg8=T50
# A_n: second-to-last: deg3=T1(=C3 overlap), deg4=T4, deg5=T4, deg6=T15, deg7=T6, deg8=T49

# For classification we use galt (transitive group number) and degree
# S_n groups by degree
S_N = {2: 1, 3: 2, 4: 5, 5: 5, 6: 16, 7: 7, 8: 50, 9: 34, 10: 45}
# A_n groups by degree
A_N = {3: 1, 4: 4, 5: 4, 6: 15, 7: 6, 8: 49, 9: 33, 10: 44}
# D_n (dihedral) by degree (n >= 4)
D_N = {4: 3, 5: 2, 6: 3, 7: 2, 8: 6, 9: 2, 10: 3}
# C_n (cyclic) always T1
C_N_GALT = 1


def get_conn():
    return psycopg2.connect(**DB)


def classify_galois(degree, galt):
    """Classify into Dynkin-adjacent (S_n, A_n, D_n) vs cyclic vs other."""
    d, g = int(degree), int(galt)
    if S_N.get(d) == g:
        return "S_n"
    if A_N.get(d) == g:
        return "A_n"
    if D_N.get(d) == g:
        return "D_n"
    if g == C_N_GALT:
        return "C_n"
    return "other"


def test_h11():
    """H11: ADE Gatekeeping — Dynkin-type Galois groups have lower disc_abs/degree! ratios."""
    print("\n=== H11: ADE Gatekeeping in NF Discriminants ===")
    t0 = time.time()
    conn = get_conn()
    cur = conn.cursor()

    # Sample 300K rows with degree 3-8 (where we have reliable group classification)
    cur.execute("""
        SELECT degree, galt, disc_abs
        FROM nf_fields TABLESAMPLE SYSTEM(2)
        WHERE degree IN ('3','4','5','6','7','8')
          AND disc_abs IS NOT NULL AND galt IS NOT NULL
        LIMIT 300000
    """)
    rows = cur.fetchall()
    conn.close()
    print(f"  Fetched {len(rows)} rows in {time.time()-t0:.1f}s")

    dynkin_ratios = []  # S_n, A_n, D_n
    other_ratios = []

    for degree_s, galt_s, disc_abs_s in rows:
        try:
            d = int(degree_s)
            g = int(galt_s)
            disc = float(disc_abs_s)
            if disc <= 0:
                continue
            ratio = math.log(disc) - sum(math.log(i) for i in range(1, d + 1))  # log(disc/d!)
            cls = classify_galois(d, g)
            if cls in ("S_n", "A_n", "D_n"):
                dynkin_ratios.append(ratio)
            elif cls == "other":
                other_ratios.append(ratio)
        except (ValueError, OverflowError):
            continue

    dynkin_ratios = np.array(dynkin_ratios)
    other_ratios = np.array(other_ratios)
    print(f"  Dynkin-adjacent: {len(dynkin_ratios)}, Other: {len(other_ratios)}")

    if len(dynkin_ratios) < 100 or len(other_ratios) < 100:
        result = {"verdict": "INCONCLUSIVE", "reason": "insufficient samples"}
        RESULTS["H11"] = result
        print(f"  INCONCLUSIVE: insufficient samples")
        return

    # Mann-Whitney U
    u_stat, p_val = stats.mannwhitneyu(dynkin_ratios, other_ratios, alternative="less")
    # Cohen's d
    pooled_std = np.sqrt((np.var(dynkin_ratios) * len(dynkin_ratios) + np.var(other_ratios) * len(other_ratios)) /
                         (len(dynkin_ratios) + len(other_ratios)))
    cohens_d = (np.mean(other_ratios) - np.mean(dynkin_ratios)) / pooled_std if pooled_std > 0 else 0

    killed = cohens_d < 0.1 or p_val > 0.01
    verdict = "KILLED" if killed else "SURVIVES"

    result = {
        "verdict": verdict,
        "dynkin_mean_log_ratio": float(np.mean(dynkin_ratios)),
        "other_mean_log_ratio": float(np.mean(other_ratios)),
        "cohens_d": float(cohens_d),
        "mann_whitney_p": float(p_val),
        "n_dynkin": len(dynkin_ratios),
        "n_other": len(other_ratios),
        "kill_criterion": "d<0.1 or p>0.01",
        "killed": killed,
    }
    RESULTS["H11"] = result
    print(f"  Cohen's d = {cohens_d:.4f}, p = {p_val:.2e}")
    print(f"  Dynkin mean(log ratio) = {np.mean(dynkin_ratios):.2f}, Other = {np.mean(other_ratios):.2f}")
    print(f"  Verdict: {verdict}")


def test_h47():
    """H47: r2/degree phase transition — non-differentiable transition at ~1.3."""
    print("\n=== H47: NF r2/degree Phase Transition ===")
    t0 = time.time()
    conn = get_conn()
    cur = conn.cursor()

    # Get r2, degree, disc_abs for 500K NF, need disc_abs sortable
    # disc_abs can be huge, so sort by log(disc_abs) proxy: length of string + first digits
    # Actually: cast to numeric for sorting on a sample
    cur.execute("""
        SELECT r2, degree, disc_abs
        FROM nf_fields TABLESAMPLE SYSTEM(3)
        WHERE r2 IS NOT NULL AND degree IS NOT NULL AND disc_abs IS NOT NULL
        LIMIT 500000
    """)
    rows = cur.fetchall()
    conn.close()
    print(f"  Fetched {len(rows)} rows in {time.time()-t0:.1f}s")

    # Parse and sort by disc_abs
    data = []
    for r2_s, deg_s, disc_s in rows:
        try:
            r2 = int(r2_s)
            deg = int(deg_s)
            disc = float(disc_s)
            if deg > 0 and disc > 0:
                data.append((disc, r2 / deg))
        except (ValueError, OverflowError):
            continue

    data.sort(key=lambda x: x[0])
    ratios = np.array([d[1] for d in data])
    print(f"  Parsed {len(ratios)} valid rows")

    if len(ratios) < 5000:
        RESULTS["H47"] = {"verdict": "INCONCLUSIVE", "reason": "insufficient data"}
        print("  INCONCLUSIVE")
        return

    # Moving average
    window = 1000
    ma = np.convolve(ratios, np.ones(window) / window, mode="valid")

    # Second derivative (discrete)
    d1 = np.diff(ma)
    d2 = np.diff(d1)
    abs_d2 = np.abs(d2)

    # Find max |d2| location
    max_d2_idx = np.argmax(abs_d2)
    max_d2_val = abs_d2[max_d2_idx]

    # What ratio value is at that point?
    transition_ratio = ma[max_d2_idx + 1]

    # Is derivative continuous? Check ratio of max |d2| to robust scale (IQR-based)
    median_d2 = np.median(abs_d2)
    iqr_d2 = np.percentile(abs_d2, 75) - np.percentile(abs_d2, 25)
    robust_scale = iqr_d2 if iqr_d2 > 1e-15 else np.std(abs_d2)
    spike_ratio = max_d2_val / robust_scale if robust_scale > 1e-15 else 0.0

    # For a true non-differentiable point, spike should be very large AND near predicted ratio
    near_target = abs(transition_ratio - 1.3) < 0.3  # within 0.3 of predicted 1.3
    killed = spike_ratio < 10 or not near_target  # derivative continuous OR not at predicted location
    verdict = "KILLED" if killed else "SURVIVES"

    # Also check the overall range of the moving average
    ma_range = float(np.max(ma) - np.min(ma))

    result = {
        "verdict": verdict,
        "max_second_deriv": float(max_d2_val),
        "median_second_deriv": float(median_d2),
        "spike_ratio": float(spike_ratio),
        "transition_ratio_at_spike": float(transition_ratio),
        "near_target_1.3": near_target,
        "target_ratio": 1.3,
        "ma_range": ma_range,
        "ma_mean": float(np.mean(ma)),
        "robust_scale_d2": float(robust_scale),
        "n_points": len(ratios),
        "kill_criterion": "spike_ratio < 10 OR transition not near 1.3",
        "killed": killed,
    }
    RESULTS["H47"] = result
    print(f"  MA range: {ma_range:.4f}, MA mean: {np.mean(ma):.4f}")
    print(f"  Max |d²| = {max_d2_val:.6f}, Median |d²| = {median_d2:.6f}")
    print(f"  Spike ratio = {spike_ratio:.1f}, Transition ratio = {transition_ratio:.4f}")
    print(f"  Verdict: {verdict}")


def test_h82():
    """H82: Mahler measure floor accumulation — density near Lehmer's constant."""
    print("\n=== H82: Mahler Measure Floor Accumulation ===")
    t0 = time.time()
    conn = get_conn()
    cur = conn.cursor()

    # Compute Mahler measures from coefficients for a sample
    # Mahler measure = exp(mean of log|roots| for |roots|>1)
    # = product of max(1, |root|) for all roots
    cur.execute("""
        SELECT coeffs FROM nf_fields TABLESAMPLE SYSTEM(3)
        WHERE coeffs IS NOT NULL
        LIMIT 200000
    """)
    rows = cur.fetchall()
    conn.close()
    print(f"  Fetched {len(rows)} coefficient sets in {time.time()-t0:.1f}s")

    LEHMER = 1.17628081825991
    mahler_measures = []

    for (coeffs_s,) in rows:
        try:
            # coeffs is stored as '{c0,c1,...,cn}' — parse it
            coeffs_str = coeffs_s.strip("{}")
            coeffs = [int(c) for c in coeffs_str.split(",")]
            # numpy roots wants highest-degree first
            coeffs_rev = coeffs[::-1]
            if len(coeffs_rev) < 2 or coeffs_rev[0] == 0:
                continue
            roots = np.roots(coeffs_rev)
            # Mahler measure = |leading coeff| * product of max(1, |root|)
            M = abs(coeffs_rev[0])
            for r in roots:
                ar = abs(r)
                if ar > 1:
                    M *= ar
            if M > 0:
                mahler_measures.append(M)
        except (ValueError, OverflowError, np.linalg.LinAlgError):
            continue

    mahler_measures = np.array(mahler_measures)
    print(f"  Computed {len(mahler_measures)} Mahler measures")

    if len(mahler_measures) < 1000:
        RESULTS["H82"] = {"verdict": "INCONCLUSIVE", "reason": "insufficient Mahler measures"}
        print("  INCONCLUSIVE")
        return

    # For epsilon values, count density near Lehmer's constant
    epsilons = [0.001, 0.01, 0.1, 1.0]
    counts = []
    for eps in epsilons:
        c = np.sum((mahler_measures >= LEHMER) & (mahler_measures < LEHMER + eps))
        counts.append(int(c))

    print(f"  Counts near Lehmer ({LEHMER}):")
    for eps, c in zip(epsilons, counts):
        print(f"    eps={eps}: count={c}")

    # Fit power law: count ~ eps^beta
    # log(count) = beta * log(eps) + const
    # Only use eps values with count > 0
    valid = [(eps, c) for eps, c in zip(epsilons, counts) if c > 0]

    if len(valid) < 3:
        killed = True
        beta = float("nan")
        r_squared = float("nan")
        verdict = "KILLED"
        reason = f"Only {len(valid)} epsilon bins with nonzero counts — gap near Lehmer"
    else:
        log_eps = np.log([v[0] for v in valid])
        log_counts = np.log([v[1] for v in valid])
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_eps, log_counts)
        beta = slope
        r_squared = r_value ** 2

        killed = beta < 0.2 or beta > 1.2
        verdict = "KILLED" if killed else "SURVIVES"
        reason = f"beta={beta:.3f}, R²={r_squared:.3f}"

    result = {
        "verdict": verdict,
        "epsilons": epsilons,
        "counts": counts,
        "beta": float(beta) if not math.isnan(beta) else None,
        "r_squared": float(r_squared) if not math.isnan(r_squared) else None,
        "n_measures": len(mahler_measures),
        "lehmer_constant": LEHMER,
        "kill_criterion": "beta outside [0.2, 1.2] or gap",
        "killed": killed,
        "reason": reason,
    }
    RESULTS["H82"] = result
    print(f"  {reason}")
    print(f"  Verdict: {verdict}")


def test_h83():
    """H83: Class number × Regulator product law for degree-4 totally real NF."""
    print("\n=== H83: Class Number × Regulator Product Law ===")
    t0 = time.time()
    conn = get_conn()
    cur = conn.cursor()

    # degree=4, r2=0 (totally real), need class_number, regulator, disc_abs all non-null
    cur.execute("""
        SELECT class_number, regulator, disc_abs
        FROM nf_fields
        WHERE degree = '4' AND r2 = '0'
          AND class_number IS NOT NULL
          AND regulator IS NOT NULL
          AND disc_abs IS NOT NULL
        LIMIT 500000
    """)
    rows = cur.fetchall()
    conn.close()
    print(f"  Fetched {len(rows)} degree-4 totally real NF in {time.time()-t0:.1f}s")

    products = []
    for cn_s, reg_s, disc_s in rows:
        try:
            cn = float(cn_s)
            reg = float(reg_s)
            disc = float(disc_s)
            if cn > 0 and reg > 0 and disc > 0:
                prod = cn * reg / math.sqrt(disc)
                products.append(prod)
        except (ValueError, OverflowError):
            continue

    products = np.array(products)
    print(f"  Computed {len(products)} valid products")

    if len(products) < 100:
        RESULTS["H83"] = {"verdict": "INCONCLUSIVE", "reason": "insufficient data"}
        print("  INCONCLUSIVE")
        return

    # Moments
    moments = {
        "mean": float(np.mean(products)),
        "var": float(np.var(products)),
        "skew": float(stats.skew(products)),
        "kurtosis": float(stats.kurtosis(products)),
    }
    # Second moment finite?
    m2 = float(np.mean(products ** 2))
    m4 = float(np.mean(products ** 4)) if np.max(products) < 1e150 else float("inf")

    # Hill estimator for tail exponent
    # Sort descending, use top 10%
    sorted_prods = np.sort(products)[::-1]
    k = max(10, len(sorted_prods) // 10)
    top_k = sorted_prods[:k]
    threshold = sorted_prods[k]

    if threshold > 0 and all(top_k > 0):
        log_ratios = np.log(top_k / threshold)
        hill_alpha = 1.0 / np.mean(log_ratios) if np.mean(log_ratios) > 0 else float("inf")
    else:
        hill_alpha = float("nan")

    killed = not (1.5 <= hill_alpha <= 3.0) if not math.isnan(hill_alpha) else True
    verdict = "KILLED" if killed else "SURVIVES"

    result = {
        "verdict": verdict,
        "moments": moments,
        "second_moment": m2,
        "hill_alpha": float(hill_alpha),
        "hill_k": k,
        "n_products": len(products),
        "product_median": float(np.median(products)),
        "product_p95": float(np.percentile(products, 95)),
        "kill_criterion": "Hill alpha outside [1.5, 3.0]",
        "killed": killed,
    }
    RESULTS["H83"] = result
    print(f"  Moments: mean={moments['mean']:.4f}, var={moments['var']:.4f}")
    print(f"  Hill estimator alpha = {hill_alpha:.3f} (k={k})")
    print(f"  Median product = {np.median(products):.4f}, P95 = {np.percentile(products, 95):.4f}")
    print(f"  Verdict: {verdict}")


def test_h15():
    """H15: NF Tower Termination — S_n/A_n have lower class numbers than exotic groups."""
    print("\n=== H15: NF Tower Termination ===")
    t0 = time.time()
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT galois_label, class_number, degree, galt
        FROM nf_fields TABLESAMPLE SYSTEM(1.5)
        WHERE class_number IS NOT NULL AND galois_label IS NOT NULL
          AND degree IN ('3','4','5','6','7','8')
        LIMIT 200000
    """)
    rows = cur.fetchall()
    conn.close()
    print(f"  Fetched {len(rows)} rows in {time.time()-t0:.1f}s")

    dynkin_cn = []  # S_n, A_n
    other_cn = []

    for gl_s, cn_s, deg_s, galt_s in rows:
        try:
            cn = float(cn_s)
            d = int(deg_s)
            g = int(galt_s)
            cls = classify_galois(d, g)
            if cls in ("S_n", "A_n"):
                dynkin_cn.append(cn)
            elif cls == "other":
                other_cn.append(cn)
        except (ValueError, OverflowError):
            continue

    dynkin_cn = np.array(dynkin_cn)
    other_cn = np.array(other_cn)
    print(f"  S_n/A_n: {len(dynkin_cn)}, Other: {len(other_cn)}")

    if len(dynkin_cn) < 100 or len(other_cn) < 100:
        RESULTS["H15"] = {"verdict": "INCONCLUSIVE", "reason": "insufficient samples"}
        print("  INCONCLUSIVE")
        return

    # Wilcoxon rank-sum (= Mann-Whitney)
    u_stat, p_val = stats.mannwhitneyu(dynkin_cn, other_cn, alternative="less")

    # Effect size: rank-biserial correlation
    n1, n2 = len(dynkin_cn), len(other_cn)
    r_rb = 1 - (2 * u_stat) / (n1 * n2)

    killed = p_val > 0.01
    verdict = "KILLED" if killed else "SURVIVES"

    result = {
        "verdict": verdict,
        "dynkin_median_cn": float(np.median(dynkin_cn)),
        "other_median_cn": float(np.median(other_cn)),
        "dynkin_mean_cn": float(np.mean(dynkin_cn)),
        "other_mean_cn": float(np.mean(other_cn)),
        "mann_whitney_U": float(u_stat),
        "p_value": float(p_val),
        "rank_biserial_r": float(r_rb),
        "n_dynkin": n1,
        "n_other": n2,
        "kill_criterion": "p > 0.01",
        "killed": killed,
    }
    RESULTS["H15"] = result
    print(f"  S_n/A_n median CN = {np.median(dynkin_cn):.1f}, Other median CN = {np.median(other_cn):.1f}")
    print(f"  S_n/A_n mean CN = {np.mean(dynkin_cn):.2f}, Other mean CN = {np.mean(other_cn):.2f}")
    print(f"  Mann-Whitney p = {p_val:.2e}, rank-biserial r = {r_rb:.4f}")
    print(f"  Verdict: {verdict}")


def main():
    print("=" * 70)
    print("CHARON FRONTIER BATCH 4 — 5 Hypothesis Tests on nf_fields")
    print("=" * 70)
    t_start = time.time()

    test_h11()
    test_h47()
    test_h82()
    test_h83()
    test_h15()

    elapsed = time.time() - t_start

    # Summary table
    print("\n" + "=" * 70)
    print(f"{'Hypothesis':<12} {'Verdict':<12} {'Key Statistic':<35} {'Kill?'}")
    print("-" * 70)

    for h in ["H11", "H47", "H82", "H83", "H15"]:
        r = RESULTS.get(h, {})
        v = r.get("verdict", "N/A")
        k = "YES" if r.get("killed", False) else "NO"

        if h == "H11":
            stat = f"Cohen's d = {r.get('cohens_d', 'N/A')}"
        elif h == "H47":
            stat = f"spike ratio = {r.get('spike_ratio', 'N/A')}"
        elif h == "H82":
            beta = r.get("beta")
            stat = f"beta = {beta:.3f}" if beta is not None else r.get("reason", "N/A")
        elif h == "H83":
            stat = f"Hill alpha = {r.get('hill_alpha', 'N/A')}"
        elif h == "H15":
            stat = f"p = {r.get('p_value', 'N/A')}"
        else:
            stat = "N/A"

        print(f"{h:<12} {v:<12} {str(stat):<35} {k}")

    print("-" * 70)
    print(f"Total runtime: {elapsed:.1f}s")

    # Save results
    output = {
        "batch": "frontier_batch4",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "runtime_seconds": elapsed,
        "results": RESULTS,
    }
    out_path = Path("F:/Prometheus/charon/data/frontier_batch4.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
