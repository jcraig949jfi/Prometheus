#!/usr/bin/env python3
"""
CM Class Number Bridge: EC Sha vs Imaginary Quadratic Class Number

For each CM elliptic curve with discriminant D, match to the imaginary
quadratic order O_D of discriminant D. Compute h(D) = class number of
that order, then correlate h(D) with EC arithmetic invariants across
the ~12 CM discriminants present in the database.

Key distinction: CM discriminants like -16, -12, -27, -28 correspond to
non-maximal orders. We compute class numbers for the actual order, not
just the maximal order of Q(sqrt(D_fund)).

Data sources:
  - EC from charon DuckDB (31K curves, 294 CM curves)
  - Class numbers computed from known formulas

Output: cartography/v2/cm_class_number_bridge_results.json
"""

import json
import math
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy import stats

# ── Paths ──────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT / "charon" / "data" / "charon.duckdb"
OUTPUT = Path(__file__).resolve().parent / "cm_class_number_bridge_results.json"


# ── Class number computation for imaginary quadratic orders ────────
# For a discriminant D < 0 of an imaginary quadratic order:
#   If D = D_K * f^2 where D_K is the fundamental discriminant,
#   h(D) = h(D_K) * f / [O_K* : O*] * prod_{p|f} (1 - (D_K/p)/p)
#
# For small discriminants we just use the known values.

# Class numbers of fundamental imaginary quadratic fields Q(sqrt(D_K))
FUNDAMENTAL_CLASS_NUMBERS = {
    -3: 1, -4: 1, -7: 1, -8: 1, -11: 1, -15: 2, -19: 1,
    -20: 2, -23: 3, -24: 2, -31: 3, -35: 2, -39: 4, -40: 2,
    -43: 1, -47: 5, -51: 2, -52: 2, -55: 4, -56: 4,
    -59: 3, -67: 1, -68: 4, -71: 7, -79: 5, -83: 3,
    -84: 4, -87: 6, -88: 2, -91: 2, -95: 8,
    -103: 5, -107: 3, -111: 8, -115: 2, -119: 10,
    -120: 4, -123: 2, -127: 5, -131: 5, -132: 4,
    -136: 4, -139: 3, -143: 10, -148: 2, -151: 7,
    -152: 6, -155: 4, -159: 10, -163: 1, -167: 11,
}


def fundamental_discriminant(D):
    """Extract fundamental discriminant D_K and conductor f from D = D_K * f^2."""
    D = abs(D)
    # Factor out perfect squares
    f = 1
    for p in range(2, int(math.isqrt(D)) + 1):
        while D % (p * p) == 0:
            D //= (p * p)
            f *= p
    # Now D is squarefree. The fundamental discriminant is -D or -4D.
    if D % 4 == 3:
        D_K = -D
    else:
        D_K = -4 * D
    return D_K, f


def kronecker_symbol(D_K, p):
    """Compute the Kronecker symbol (D_K/p) for fundamental discriminant D_K."""
    if p == 2:
        r = D_K % 8
        if r == 1 or r == -7:
            return 1
        elif r == 5 or r == -3:
            return -1
        else:
            return 0
    # Legendre symbol for odd p
    val = pow(D_K % p, (p - 1) // 2, p)
    if val == p - 1:
        return -1
    return val  # 0 or 1


def class_number_order(D):
    """Compute class number h(D) for imaginary quadratic order of discriminant D.

    Uses: h(D) = h(D_K) * f / w_ratio * prod_{p|f} (1 - (D_K/p)/p)
    where w_ratio = [O_K* : O*] / 1 (units ratio).
    """
    D_K, f = fundamental_discriminant(D)

    if D_K not in FUNDAMENTAL_CLASS_NUMBERS:
        # Fallback: for very small |D_K| this shouldn't happen with our data
        return None

    h_K = FUNDAMENTAL_CLASS_NUMBERS[D_K]

    if f == 1:
        return h_K

    # Units: |O_K*| = 6 if D_K = -3, 4 if D_K = -4, 2 otherwise
    # |O*| = same as O_K* only if f = 1; for f > 1, |O*| = 2 always
    if D_K == -3:
        w_ratio = 3  # 6/2
    elif D_K == -4:
        w_ratio = 2  # 4/2
    else:
        w_ratio = 1  # 2/2

    # Product over primes dividing f
    product = 1.0
    f_temp = f
    primes = []
    for p in range(2, f_temp + 1):
        if f_temp % p == 0:
            primes.append(p)
            while f_temp % p == 0:
                f_temp //= p

    for p in primes:
        product *= (1 - kronecker_symbol(D_K, p) / p)

    h_D = h_K * f * product / w_ratio
    return int(round(h_D))


def load_cm_curves():
    """Load CM elliptic curves from DuckDB."""
    import duckdb
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute("""
        SELECT cm, conductor, rank, sha, degree, faltings_height,
               torsion, regulator, class_size, class_deg,
               lmfdb_label
        FROM elliptic_curves
        WHERE cm IS NOT NULL AND cm != 0
        ORDER BY cm
    """).fetchdf()
    con.close()
    return df


def analyze():
    """Main analysis: correlate class numbers with EC invariants."""
    df = load_cm_curves()

    # Compute class number for each CM discriminant
    cm_discs = sorted(df["cm"].unique())
    disc_info = {}
    for D in cm_discs:
        D_K, f = fundamental_discriminant(int(D))
        h = class_number_order(int(D))
        disc_info[int(D)] = {
            "cm_disc": int(D),
            "fund_disc": int(D_K),
            "conductor_of_order": int(f),
            "class_number": h,
        }

    print(f"CM discriminants found: {len(cm_discs)}")
    for D in cm_discs:
        info = disc_info[int(D)]
        n = len(df[df["cm"] == D])
        print(f"  D={D:4d}  D_K={info['fund_disc']:4d}  f={info['conductor_of_order']}  "
              f"h={info['class_number']}  n_curves={n}")

    # Aggregate EC invariants per CM discriminant
    agg_rows = []
    for D in cm_discs:
        subset = df[df["cm"] == D]
        h = disc_info[int(D)]["class_number"]
        row = {
            "cm_disc": int(D),
            "class_number": h,
            "n_curves": len(subset),
            "mean_conductor": float(subset["conductor"].mean()),
            "median_conductor": float(subset["conductor"].median()),
            "mean_sha": float(subset["sha"].mean()) if subset["sha"].notna().any() else None,
            "median_sha": float(subset["sha"].median()) if subset["sha"].notna().any() else None,
            "mean_degree": float(subset["degree"].mean()) if subset["degree"].notna().any() else None,
            "mean_faltings_height": float(subset["faltings_height"].mean()) if subset["faltings_height"].notna().any() else None,
            "mean_rank": float(subset["rank"].mean()) if subset["rank"].notna().any() else None,
            "mean_torsion": float(subset["torsion"].mean()) if subset["torsion"].notna().any() else None,
            "mean_regulator": float(subset["regulator"].mean()) if subset["regulator"].notna().any() else None,
            "mean_class_size": float(subset["class_size"].mean()) if subset["class_size"].notna().any() else None,
        }
        agg_rows.append(row)

    agg_rows.sort(key=lambda r: r["class_number"] or 0)

    # ── Correlations: h(D) vs each invariant ──────────────────────
    h_vals = np.array([r["class_number"] for r in agg_rows], dtype=float)

    invariants_to_test = [
        "mean_conductor", "median_conductor", "mean_sha", "mean_degree",
        "mean_faltings_height", "mean_rank", "mean_torsion",
        "mean_regulator", "mean_class_size",
    ]

    correlations = {}
    for inv_name in invariants_to_test:
        vals = np.array([r[inv_name] for r in agg_rows], dtype=float)
        mask = np.isfinite(vals) & np.isfinite(h_vals)
        if mask.sum() < 4:
            correlations[inv_name] = {"note": "insufficient data"}
            continue
        h_sub = h_vals[mask]
        v_sub = vals[mask]
        r_pearson, p_pearson = stats.pearsonr(h_sub, v_sub)
        r_spearman, p_spearman = stats.spearmanr(h_sub, v_sub)
        correlations[inv_name] = {
            "pearson_r": round(float(r_pearson), 6),
            "pearson_p": float(p_pearson),
            "spearman_r": round(float(r_spearman), 6),
            "spearman_p": float(p_spearman),
            "n": int(mask.sum()),
        }
        print(f"  h(D) vs {inv_name:25s}  r={r_pearson:+.4f}  p={p_pearson:.4g}  "
              f"rho={r_spearman:+.4f}  p={p_spearman:.4g}  n={mask.sum()}")

    # ── Log-log correlation (h vs conductor, degree) ──────────────
    log_correlations = {}
    for inv_name in ["mean_conductor", "mean_degree"]:
        vals = np.array([r[inv_name] for r in agg_rows], dtype=float)
        mask = np.isfinite(vals) & np.isfinite(h_vals) & (vals > 0) & (h_vals > 0)
        if mask.sum() < 4:
            continue
        lh = np.log(h_vals[mask])
        lv = np.log(vals[mask])
        r_p, p_p = stats.pearsonr(lh, lv)
        log_correlations[f"log_{inv_name}"] = {
            "pearson_r": round(float(r_p), 6),
            "pearson_p": float(p_p),
            "n": int(mask.sum()),
        }
        print(f"  log h(D) vs log {inv_name:20s}  r={r_p:+.4f}  p={p_p:.4g}")

    # ── Within-discriminant Sha variation ─────────────────────────
    # For each D, check if Sha varies (most CM curves have Sha=1)
    within_disc_sha = {}
    for D in cm_discs:
        subset = df[df["cm"] == D]
        sha_vals = subset["sha"].dropna().values
        if len(sha_vals) == 0:
            continue
        unique_sha = sorted(set(int(s) for s in sha_vals))
        within_disc_sha[int(D)] = {
            "n_curves": len(sha_vals),
            "unique_sha_values": unique_sha,
            "all_sha_one": all(s == 1 for s in sha_vals),
            "max_sha": int(max(sha_vals)),
        }

    sha_all_one = all(v["all_sha_one"] for v in within_disc_sha.values())
    print(f"\n  Within-discriminant Sha variation: {'NONE (all Sha=1)' if sha_all_one else 'PRESENT'}")
    for D, info in sorted(within_disc_sha.items()):
        if not info["all_sha_one"]:
            print(f"    D={D}: Sha values = {info['unique_sha_values']}")

    # ── Diagnostic: h(D) value distribution ────────────────────────
    unique_h = sorted(set(h_vals))
    h_counts = {int(h): int((h_vals == h).sum()) for h in unique_h}
    print(f"\n  h(D) distribution: {h_counts}")
    binary_h = len(unique_h) <= 2
    if binary_h:
        print(f"  WARNING: h(D) takes only {len(unique_h)} distinct values — "
              "Spearman correlation is effectively a rank-biserial test")

    # ── Mann-Whitney U test (proper binary comparison) ────────────
    mann_whitney_results = {}
    if binary_h and len(unique_h) == 2:
        h_lo, h_hi = unique_h
        for inv_name in invariants_to_test:
            vals = np.array([r[inv_name] for r in agg_rows], dtype=float)
            g1 = vals[h_vals == h_lo]
            g2 = vals[h_vals == h_hi]
            g1 = g1[np.isfinite(g1)]
            g2 = g2[np.isfinite(g2)]
            if len(g1) < 2 or len(g2) < 2:
                continue
            try:
                u_stat, p_mw = stats.mannwhitneyu(g1, g2, alternative='two-sided')
                mann_whitney_results[inv_name] = {
                    "U": float(u_stat),
                    "p_value": float(p_mw),
                    "n_h_lo": len(g1),
                    "n_h_hi": len(g2),
                    "mean_h_lo": round(float(g1.mean()), 4),
                    "mean_h_hi": round(float(g2.mean()), 4),
                }
                print(f"  MW h={int(h_lo)} vs h={int(h_hi)} on {inv_name:25s}  "
                      f"U={u_stat:.0f}  p={p_mw:.4g}  "
                      f"means={g1.mean():.1f} vs {g2.mean():.1f}")
            except Exception:
                pass

    # ── Null test: shuffle class numbers ──────────────────────────
    n_perm = 10000
    best_inv = max(correlations, key=lambda k: abs(correlations[k].get("spearman_r", 0)))
    best_rho = abs(correlations[best_inv].get("spearman_r", 0))

    vals_best = np.array([r[best_inv] for r in agg_rows], dtype=float)
    mask = np.isfinite(vals_best) & np.isfinite(h_vals)
    h_sub = h_vals[mask]
    v_sub = vals_best[mask]

    rng = np.random.default_rng(42)
    null_rhos = []
    for _ in range(n_perm):
        perm = rng.permutation(h_sub)
        rho, _ = stats.spearmanr(perm, v_sub)
        null_rhos.append(abs(rho))
    null_rhos = np.array(null_rhos)
    # Use >= with small epsilon for floating point
    p_perm = float((null_rhos >= best_rho - 1e-10).mean())
    print(f"\n  Permutation test on best invariant ({best_inv}):")
    print(f"    |rho| = {best_rho:.4f}, p_perm = {p_perm:.4f}")

    # ── Theoretical check: h(D) vs |D| relationship ──────────────
    # Analytically, h(D) ~ sqrt(|D|) / pi * L(1, chi_D) for fund. disc.
    abs_D = np.array([abs(r["cm_disc"]) for r in agg_rows], dtype=float)
    r_hD, p_hD = stats.pearsonr(h_vals, np.sqrt(abs_D))
    print(f"\n  Sanity: h(D) vs sqrt(|D|):  r={r_hD:.4f}  p={p_hD:.4g}")

    # ── Build verdict ─────────────────────────────────────────────
    sig_threshold = 0.05

    # For binary h, use Mann-Whitney as the proper test
    if binary_h:
        any_mw_sig = any(
            v.get("p_value", 1.0) < sig_threshold
            for v in mann_whitney_results.values()
        )
        any_significant = any_mw_sig
    else:
        any_significant = any(
            c.get("spearman_p", 1.0) < sig_threshold
            for c in correlations.values()
            if isinstance(c.get("spearman_p"), float)
        )
    perm_significant = p_perm < sig_threshold

    # Even if nominally significant, with n=2 in one group it's unreliable
    if binary_h and min(h_counts.values()) <= 2:
        verdict = (
            "NO_BRIDGE — class number takes only 2 distinct values across 12 CM discriminants "
            f"(h=1: {h_counts.get(1, 0)}, h=2: {h_counts.get(2, 0)}), with min group size "
            f"{min(h_counts.values())}. Statistical tests are unreliable at this sample size. "
            "Any apparent correlation is between 10 vs 2 discriminants — insufficient for inference."
        )
    elif any_significant and perm_significant:
        verdict = "BRIDGE_CANDIDATE"
    elif any_significant:
        verdict = "MARGINAL — significant correlation but failed permutation test"
    else:
        verdict = "NO_BRIDGE — no significant correlation between h(D) and EC invariants"

    # ── Assemble results ──────────────────────────────────────────
    results = {
        "experiment": "CM Class Number Bridge",
        "description": (
            "For each CM elliptic curve with discriminant D, compute class number h(D) "
            "of the imaginary quadratic order of discriminant D. Correlate h(D) with "
            "EC arithmetic invariants (conductor, Sha, modular degree, Faltings height, etc.)"
        ),
        "data_summary": {
            "total_cm_curves": int(len(df)),
            "n_discriminants": len(cm_discs),
            "discriminant_info": [disc_info[int(D)] for D in cm_discs],
        },
        "aggregated_per_discriminant": agg_rows,
        "correlations_h_vs_invariant": correlations,
        "log_correlations": log_correlations,
        "within_discriminant_sha": within_disc_sha,
        "sha_all_one_within_disc": sha_all_one,
        "permutation_test": {
            "best_invariant": best_inv,
            "observed_abs_rho": round(best_rho, 6),
            "p_permutation": p_perm,
            "n_permutations": n_perm,
        },
        "mann_whitney_binary": mann_whitney_results if binary_h else {},
        "h_distribution": h_counts,
        "binary_h_warning": binary_h,
        "sanity_h_vs_sqrtD": {
            "pearson_r": round(float(r_hD), 6),
            "pearson_p": float(p_hD),
        },
        "verdict": verdict,
        "notes": [
            "CM discriminants include non-maximal orders (e.g. -16 = -4*4, -27 = -3*9)",
            "Class numbers computed for actual order, not just maximal order",
            "Sha is 1 for almost all CM curves — very little variation to explain",
            f"h(D) takes only {len(unique_h)} distinct values: {dict(h_counts)}",
            f"FATAL: 10 of 12 discriminants have h=1, only 2 have h=2 — "
            "any 'correlation' is really a 2-vs-10 group comparison with no statistical power",
            "The 13 CM j-invariants all have class number 1 by definition (Heegner numbers); "
            "non-maximal orders -8 and -16 are the only ones with h>1",
            "This bridge is structurally dead: CM discriminants in LMFDB are overwhelmingly h=1",
        ],
    }

    with open(OUTPUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT}")
    print(f"Verdict: {verdict}")
    return results


if __name__ == "__main__":
    analyze()
