"""
Charon Frontier Batch 1: Test 5 hypotheses against ec_curvedata.
H36, H40, H41, H43, H75
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import json
import numpy as np
import psycopg2
from scipy import stats
from collections import defaultdict

DB = dict(host="localhost", port=5432, dbname="lmfdb", user="postgres", password="prometheus")
RESULTS = {}

def get_conn():
    return psycopg2.connect(**DB)

# ─────────────────────────────────────────────────────────────────────────────
# H36: Bad-Prime Additive Persistence (Pareto Tails)
# ─────────────────────────────────────────────────────────────────────────────
def test_h36():
    print("\n=== H36: Bad-Prime Pareto Tails ===")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT CAST(num_bad_primes AS int) AS nbp,
               CAST(szpiro_ratio AS double precision) AS sz
        FROM ec_curvedata
        WHERE num_bad_primes IS NOT NULL
          AND szpiro_ratio IS NOT NULL
          AND CAST(szpiro_ratio AS double precision) > 0
    """)
    rows = cur.fetchall()
    conn.close()

    groups = defaultdict(list)
    for nbp, sz in rows:
        key = min(nbp, 3)  # 0, 1, 2, 3+
        groups[key].append(sz)

    # Fit Pareto tail exponent (alpha) for each group using top 10% of distribution
    alphas = {}
    for key in sorted(groups.keys()):
        data = np.array(groups[key])
        # Use values above 90th percentile for tail fitting
        threshold = np.percentile(data, 90)
        tail = data[data >= threshold]
        if len(tail) < 50:
            alphas[key] = (np.nan, np.nan, len(data))
            continue
        # MLE for Pareto alpha: alpha = n / sum(log(x/xmin))
        xmin = tail.min()
        alpha_mle = len(tail) / np.sum(np.log(tail / xmin))
        # SE of alpha MLE
        se = alpha_mle / np.sqrt(len(tail))
        alphas[key] = (alpha_mle, se, len(data))
        label = f"{key}+" if key == 3 else str(key)
        print(f"  num_bad_primes={label}: n={len(data):,}, tail_n={len(tail):,}, "
              f"alpha={alpha_mle:.3f} ± {se:.3f}")

    # Kill criterion: CI for tail exponents overlaps between ALL groups
    alpha_vals = [(a, se) for a, se, _ in alphas.values() if not np.isnan(a)]
    if len(alpha_vals) >= 2:
        # Check if 0-group and 3+-group CIs overlap
        a0, se0 = alphas.get(0, (np.nan, np.nan, 0))[:2]
        a3, se3 = alphas.get(3, (np.nan, np.nan, 0))[:2]
        if not np.isnan(a0) and not np.isnan(a3):
            ci0 = (a0 - 1.96*se0, a0 + 1.96*se0)
            ci3 = (a3 - 1.96*se3, a3 + 1.96*se3)
            overlap = ci0[1] > ci3[0] and ci3[1] > ci0[0]
            diff_z = abs(a0 - a3) / np.sqrt(se0**2 + se3**2)
            print(f"  Group 0 vs 3+ alpha difference z = {diff_z:.2f}, overlap={overlap}")
            killed = overlap  # killed if CIs overlap (no difference)
        else:
            killed = True
            diff_z = 0
    else:
        killed = True
        diff_z = 0

    verdict = "KILLED" if killed else "SURVIVES"
    print(f"  Verdict: {verdict}")
    RESULTS["H36"] = {
        "hypothesis": "Bad-Prime Additive Persistence (Pareto Tails)",
        "verdict": verdict,
        "alphas": {str(k): {"alpha": round(a, 4), "se": round(se, 4), "n": n}
                   for k, (a, se, n) in alphas.items()},
        "diff_z": round(diff_z, 3),
        "kill_criterion": "CI overlap between groups",
        "killed": killed
    }

# ─────────────────────────────────────────────────────────────────────────────
# H40: Szpiro-Faltings Coupling (partial correlation)
# ─────────────────────────────────────────────────────────────────────────────
def test_h40():
    print("\n=== H40: Szpiro-Faltings Coupling ===")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT CAST(szpiro_ratio AS double precision),
               CAST(faltings_height AS double precision),
               CAST(conductor AS double precision),
               CAST(num_bad_primes AS int)
        FROM ec_curvedata
        WHERE szpiro_ratio IS NOT NULL
          AND faltings_height IS NOT NULL
          AND conductor IS NOT NULL
          AND num_bad_primes IS NOT NULL
          AND CAST(conductor AS double precision) > 0
        LIMIT 500000
    """)
    rows = cur.fetchall()
    conn.close()

    data = np.array(rows, dtype=float)
    sz, fh, cond, nbp = data[:, 0], data[:, 1], data[:, 2], data[:, 3]
    log_cond = np.log(cond + 1)

    # Partial correlation: residualize both sz and fh on log_cond and nbp
    def partial_corr(x, y, controls):
        """Partial correlation of x,y controlling for controls matrix."""
        # Add intercept
        C = np.column_stack([controls, np.ones(len(x))])
        # Residualize x
        bx = np.linalg.lstsq(C, x, rcond=None)[0]
        rx = x - C @ bx
        # Residualize y
        by = np.linalg.lstsq(C, y, rcond=None)[0]
        ry = y - C @ by
        return np.corrcoef(rx, ry)[0, 1]

    controls = np.column_stack([log_cond, nbp])
    rho_full = partial_corr(sz, fh, controls)
    print(f"  Full sample partial rho = {rho_full:.4f} (n={len(sz):,})")

    # By conductor decade
    decades = [(1, 100), (100, 1000), (1000, 10000), (10000, 100000), (100000, 1e12)]
    decade_rhos = {}
    killed = False
    for lo, hi in decades:
        mask = (cond >= lo) & (cond < hi)
        if mask.sum() < 100:
            continue
        rho_d = partial_corr(sz[mask], fh[mask],
                             np.column_stack([log_cond[mask], nbp[mask]]))
        label = f"{lo}-{hi:.0f}"
        decade_rhos[label] = round(rho_d, 4)
        print(f"  Decade {label}: rho={rho_d:.4f} (n={mask.sum():,})")

    # Kill: |rho_partial| < 0.05 in any decade
    for label, rho in decade_rhos.items():
        if abs(rho) < 0.05:
            print(f"  KILL: |rho|={abs(rho):.4f} < 0.05 in decade {label}")
            killed = True
            break

    # Also check threshold on full: |rho| > 0.15
    passes_threshold = abs(rho_full) > 0.15

    if not passes_threshold:
        print(f"  KILL: Full |rho|={abs(rho_full):.4f} < 0.15 threshold")
        killed = True

    verdict = "KILLED" if killed else "SURVIVES"
    print(f"  Verdict: {verdict}")
    RESULTS["H40"] = {
        "hypothesis": "Szpiro-Faltings Coupling",
        "verdict": verdict,
        "rho_partial_full": round(rho_full, 4),
        "decade_rhos": decade_rhos,
        "passes_threshold": passes_threshold,
        "kill_criterion": "|rho_partial| < 0.05 in any decade OR full |rho| < 0.15",
        "killed": killed
    }

# ─────────────────────────────────────────────────────────────────────────────
# H41: Rank-Regulator Super-Linear Scaling
# ─────────────────────────────────────────────────────────────────────────────
def test_h41():
    print("\n=== H41: Rank-Regulator Super-Linear Scaling ===")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT CAST(rank AS int),
               CAST(regulator AS double precision),
               CAST(conductor AS double precision)
        FROM ec_curvedata
        WHERE rank IS NOT NULL
          AND regulator IS NOT NULL
          AND CAST(rank AS int) BETWEEN 0 AND 4
          AND CAST(regulator AS double precision) > 0
          AND CAST(conductor AS double precision) > 0
    """)
    rows = cur.fetchall()
    conn.close()

    data = np.array(rows)
    ranks, regs, conds = data[:, 0].astype(int), data[:, 1], data[:, 2]
    log_regs = np.log(regs)

    # Full sample
    means = {}
    for r in range(5):
        mask = ranks == r
        if mask.sum() > 0:
            means[r] = np.mean(log_regs[mask])
            print(f"  rank={r}: E[log(reg)]={means[r]:.4f} (n={mask.sum():,})")

    # Second difference: D2 = E[r+1] - 2E[r] + E[r-1]
    delta2_full = {}
    for r in [1, 2, 3]:
        if r-1 in means and r in means and r+1 in means:
            d2 = means[r+1] - 2*means[r] + means[r-1]
            delta2_full[r] = d2
            print(f"  D2(r={r}) = {d2:.4f}")

    # By conductor decade
    decades = [(1, 100), (100, 1000), (1000, 10000), (10000, 100000), (100000, 1e12)]
    decade_delta2 = {}
    neg_count = 0

    for lo, hi in decades:
        cmask = (conds >= lo) & (conds < hi)
        if cmask.sum() < 100:
            continue
        means_d = {}
        for r in range(5):
            mask = cmask & (ranks == r)
            if mask.sum() > 10:
                means_d[r] = np.mean(log_regs[mask])

        label = f"{lo}-{hi:.0f}"
        d2_vals = {}
        for r in [1, 2, 3]:
            if r-1 in means_d and r in means_d and r+1 in means_d:
                d2 = means_d[r+1] - 2*means_d[r] + means_d[r-1]
                d2_vals[r] = round(d2, 4)
                if d2 <= 0:
                    neg_count += 1
        decade_delta2[label] = d2_vals
        print(f"  Decade {label}: D2 = {d2_vals}")

    killed = neg_count >= 2
    verdict = "KILLED" if killed else "SURVIVES"
    print(f"  Negative D2 count: {neg_count}, Kill threshold: ≥2")
    print(f"  Verdict: {verdict}")

    RESULTS["H41"] = {
        "hypothesis": "Rank-Regulator Super-Linear Scaling",
        "verdict": verdict,
        "means_full": {str(k): round(v, 4) for k, v in means.items()},
        "delta2_full": {str(k): round(v, 4) for k, v in delta2_full.items()},
        "decade_delta2": decade_delta2,
        "neg_decade_count": neg_count,
        "kill_criterion": "D2 ≤ 0 in ≥2 decades",
        "killed": killed
    }

# ─────────────────────────────────────────────────────────────────────────────
# H43: Root Number Bias in High-Sha
# ─────────────────────────────────────────────────────────────────────────────
def test_h43():
    print("\n=== H43: Root Number Parity in High-Sha ===")
    conn = get_conn()
    cur = conn.cursor()
    # signD encodes root_number: sign of discriminant
    # root_number = +1 if even rank expected, -1 if odd
    cur.execute("""
        SELECT CAST(rank AS int),
               CAST(sha AS double precision),
               CAST("signD" AS int)
        FROM ec_curvedata
        WHERE rank IS NOT NULL
          AND sha IS NOT NULL
          AND "signD" IS NOT NULL
          AND CAST(sha AS double precision) >= 9
    """)
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("  No rows with sha >= 9!")
        RESULTS["H43"] = {"hypothesis": "Root Number Bias in High-Sha",
                          "verdict": "NO DATA", "killed": True}
        return

    data = np.array(rows)
    ranks, shas, signs = data[:, 0].astype(int), data[:, 1], data[:, 2].astype(int)

    # (-1)^rank should equal root_number (signD)
    expected_sign = np.where(ranks % 2 == 0, 1, -1)
    match = (expected_sign == signs)
    match_rate = match.mean()
    n = len(match)
    # Under perfect parity, expect match_rate = 1.0
    # SE under binomial
    se = np.sqrt(match_rate * (1 - match_rate) / n) if match_rate < 1 else 0

    # z-score: deviation from 1.0
    if se > 0:
        z_dev = (1.0 - match_rate) / se
    else:
        z_dev = 0.0

    print(f"  n = {n:,}")
    print(f"  Match rate = {match_rate:.6f}")
    print(f"  Deviation from perfect: z = {z_dev:.2f}")

    # Kill: deviation > 3σ from perfect match
    killed = z_dev > 3.0
    verdict = "KILLED" if killed else "SURVIVES"
    print(f"  Verdict: {verdict}")

    # Breakdown by sha value
    sha_vals = sorted(set(shas.astype(int)))[:10]
    breakdown = {}
    for sv in sha_vals:
        mask = shas.astype(int) == sv
        if mask.sum() > 0:
            mr = match[mask].mean()
            breakdown[str(sv)] = {"n": int(mask.sum()), "match_rate": round(mr, 6)}

    RESULTS["H43"] = {
        "hypothesis": "Root Number Parity in High-Sha",
        "verdict": verdict,
        "n": n,
        "match_rate": round(match_rate, 6),
        "z_deviation": round(z_dev, 3),
        "breakdown_by_sha": breakdown,
        "kill_criterion": "Deviation > 3σ from perfect match",
        "killed": killed
    }

# ─────────────────────────────────────────────────────────────────────────────
# H75: Torsion-Rank Anticorrelation
# ─────────────────────────────────────────────────────────────────────────────
def test_h75():
    print("\n=== H75: Torsion-Rank Anticorrelation ===")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT CAST(torsion AS int),
               CAST(rank AS int),
               CAST(conductor AS double precision)
        FROM ec_curvedata
        WHERE torsion IS NOT NULL
          AND rank IS NOT NULL
          AND conductor IS NOT NULL
          AND CAST(conductor AS double precision) > 0
    """)
    rows = cur.fetchall()
    conn.close()

    data = np.array(rows)
    torsion, ranks, conds = data[:, 0].astype(int), data[:, 1].astype(int), data[:, 2]

    # Full sample
    rho_full, p_full = stats.spearmanr(torsion, ranks)
    print(f"  Full sample: Spearman rho={rho_full:.4f}, p={p_full:.2e} (n={len(data):,})")

    # By conductor decade
    decades = [(1, 100), (100, 1000), (1000, 10000), (10000, 100000), (100000, 1e12)]
    decade_rhos = {}
    positive_count = 0

    for lo, hi in decades:
        mask = (conds >= lo) & (conds < hi)
        if mask.sum() < 100:
            continue
        rho, p = stats.spearmanr(torsion[mask], ranks[mask])
        label = f"{lo}-{hi:.0f}"
        decade_rhos[label] = {"rho": round(rho, 4), "p": float(f"{p:.2e}"),
                              "n": int(mask.sum())}
        print(f"  Decade {label}: rho={rho:.4f}, p={p:.2e}, n={mask.sum():,}")
        if rho > 0:
            positive_count += 1
            print(f"    WARNING: Positive rho!")

    # Kill: positive rho in any decade
    killed = positive_count > 0
    # Also check magnitude
    magnitude_ok = abs(rho_full) > 0.05

    if not magnitude_ok:
        print(f"  KILL: |rho_full| = {abs(rho_full):.4f} < 0.05")
        killed = True

    verdict = "KILLED" if killed else "SURVIVES"
    print(f"  Verdict: {verdict}")

    RESULTS["H75"] = {
        "hypothesis": "Torsion-Rank Anticorrelation",
        "verdict": verdict,
        "rho_full": round(rho_full, 4),
        "p_full": float(f"{p_full:.2e}"),
        "decade_rhos": decade_rhos,
        "positive_decades": positive_count,
        "magnitude_ok": magnitude_ok,
        "kill_criterion": "Positive rho in any decade OR |rho| < 0.05",
        "killed": killed
    }

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 70)
    print("CHARON FRONTIER BATCH 1 — 5 Hypotheses vs ec_curvedata")
    print("=" * 70)

    test_h36()
    test_h40()
    test_h41()
    test_h43()
    test_h75()

    # Save results
    out_path = "F:/Prometheus/charon/data/frontier_batch1.json"
    with open(out_path, "w") as f:
        json.dump(RESULTS, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")

    # Summary table
    print("\n" + "=" * 90)
    print(f"{'Hypothesis':<12} {'Name':<40} {'Verdict':<10} {'Key Stat':<25} {'Kill Met?'}")
    print("-" * 90)
    for hid, res in RESULTS.items():
        name = res["hypothesis"][:38]
        verdict = res["verdict"]
        killed = res["killed"]

        if hid == "H36":
            stat = f"z_diff={res.get('diff_z', 'N/A')}"
        elif hid == "H40":
            stat = f"rho={res.get('rho_partial_full', 'N/A')}"
        elif hid == "H41":
            stat = f"neg_decades={res.get('neg_decade_count', 'N/A')}"
        elif hid == "H43":
            stat = f"match={res.get('match_rate', 'N/A')}"
        elif hid == "H75":
            stat = f"rho={res.get('rho_full', 'N/A')}"
        else:
            stat = "?"

        print(f"{hid:<12} {name:<40} {verdict:<10} {stat:<25} {'YES' if killed else 'NO'}")
    print("=" * 90)
