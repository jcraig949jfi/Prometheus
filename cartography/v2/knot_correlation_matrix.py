#!/usr/bin/env python3
"""
Knot Invariant Correlation Matrix
==================================
Build full Spearman correlation matrix between all derivable knot invariants.
PCA to find effective dimensionality. Identify most/least correlated pairs
and most unique invariant.

Data: cartography/knots/data/knots.json (Postgres envelope, 12965 knots)
"""

import json
import re
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "knots" / "data" / "knots.json"
OUT_PATH = Path(__file__).parent / "knot_correlation_matrix_results.json"


def extract_crossing_from_name(name: str) -> int | None:
    """Extract true crossing number from knot name like '11*a_1' or '13*n_4954'."""
    m = re.match(r"(\d+)\*?[an]_", name)
    if m:
        return int(m.group(1))
    # Fallback patterns like '3_1', '4_1', etc.
    m = re.match(r"(\d+)_", name)
    if m:
        return int(m.group(1))
    return None


def poly_summary(poly_dict: dict | None) -> dict:
    """Extract summary statistics from a polynomial dict with min_power, max_power, coefficients."""
    if poly_dict is None or not poly_dict.get("coefficients"):
        return {"degree": np.nan, "span": np.nan, "max_abs_coeff": np.nan,
                "n_terms": np.nan, "coeff_sum": np.nan, "coeff_l2": np.nan}
    coeffs = poly_dict["coefficients"]
    min_p = poly_dict.get("min_power", 0)
    max_p = poly_dict.get("max_power", len(coeffs) - 1)
    abs_coeffs = [abs(c) for c in coeffs]
    return {
        "degree": max_p,
        "span": max_p - min_p,
        "max_abs_coeff": max(abs_coeffs),
        "n_terms": sum(1 for c in coeffs if c != 0),
        "coeff_sum": sum(coeffs),
        "coeff_l2": np.sqrt(sum(c**2 for c in coeffs)),
    }


def build_feature_matrix(knots: list[dict]) -> pd.DataFrame:
    """Build numeric feature matrix from knot data."""
    rows = []
    for k in knots:
        name = k["name"]

        # True crossing number from name
        crossing = extract_crossing_from_name(name)

        # Determinant
        det = k.get("determinant")

        # Alexander polynomial summary
        alex = poly_summary(k.get("alexander"))

        # Jones polynomial summary
        jones = poly_summary(k.get("jones"))

        # Conway polynomial summary
        conway = poly_summary(k.get("conway"))

        # Signature proxy: for Alexander poly, signature relates to eval at -1
        # Alexander evaluated at t=-1 gives determinant (up to sign)
        # We can derive: alex_eval_neg1 = alternating sum of coefficients
        alex_coeffs = k.get("alex_coeffs", [])
        alex_alternating = sum(c * (-1)**i for i, c in enumerate(alex_coeffs)) if alex_coeffs else np.nan

        # Jones span (max_power - min_power)
        jones_dict = k.get("jones", {}) or {}
        jones_span = (jones_dict.get("max_power", 0) - jones_dict.get("min_power", 0)) if jones_dict.get("coefficients") else np.nan

        # Jones writhe proxy: for alternating knots, writhe = (max_power + min_power)/2
        jones_writhe_proxy = ((jones_dict.get("max_power", 0) + jones_dict.get("min_power", 0)) / 2.0) if jones_dict.get("coefficients") else np.nan

        # Bridge number lower bound: from Alexander degree
        # bridge_number >= alexander_degree + 1 (actually degree/2 + 1 for some conventions)
        alex_dict = k.get("alexander", {}) or {}
        alex_degree = alex_dict.get("max_power", np.nan) if alex_dict.get("coefficients") else np.nan

        # Braid index lower bound: Morton-Williams-Franks bound from Jones polynomial
        # braid_index >= (jones_span + 2) / 2
        mwf_bound = (jones_span + 2) / 2.0 if not np.isnan(jones_span) else np.nan

        # Conway degree
        conway_dict = k.get("conway", {}) or {}
        conway_degree = conway_dict.get("max_power", np.nan) if conway_dict.get("coefficients") else np.nan

        row = {
            "name": name,
            "crossing_number": crossing,
            "determinant": det,
            "alex_degree": alex_degree,
            "alex_span": alex["span"],
            "alex_max_abs_coeff": alex["max_abs_coeff"],
            "alex_n_terms": alex["n_terms"],
            "alex_coeff_l2": alex["coeff_l2"],
            "jones_span": jones_span,
            "jones_max_abs_coeff": jones["max_abs_coeff"],
            "jones_n_terms": jones["n_terms"],
            "jones_coeff_l2": jones["coeff_l2"],
            "jones_writhe_proxy": jones_writhe_proxy,
            "conway_degree": conway_degree,
            "conway_max_abs_coeff": conway["max_abs_coeff"],
            "conway_n_terms": conway["n_terms"],
            "mwf_braid_bound": mwf_bound,
            "alex_alternating_eval": alex_alternating,
            "log_determinant": np.log(det) if det and det > 0 else np.nan,
        }
        rows.append(row)

    return pd.DataFrame(rows)


def main():
    print("Loading knot data...")
    with open(DATA_PATH) as f:
        data = json.load(f)

    knots = data["knots"]
    print(f"  {len(knots)} knots loaded")

    # Build feature matrix
    print("Building feature matrix...")
    df = build_feature_matrix(knots)

    # Select numeric columns only (drop name)
    numeric_cols = [c for c in df.columns if c != "name"]
    df_num = df[numeric_cols].copy()

    # Report coverage
    print("\nFeature coverage:")
    for col in numeric_cols:
        n_valid = df_num[col].notna().sum()
        print(f"  {col}: {n_valid}/{len(df)} ({100*n_valid/len(df):.1f}%)")

    # Drop rows with too many NaNs — keep rows with at least 10 valid features
    min_features = 10
    valid_mask = df_num.notna().sum(axis=1) >= min_features
    df_clean = df_num[valid_mask].copy()
    print(f"\nKnots with >= {min_features} valid features: {len(df_clean)}/{len(df)}")

    # Drop columns with too few valid entries
    min_knots = 100
    valid_cols = [c for c in df_clean.columns if df_clean[c].notna().sum() >= min_knots]
    df_clean = df_clean[valid_cols]
    print(f"Features with >= {min_knots} valid entries: {len(valid_cols)}")
    print(f"  Kept: {valid_cols}")

    # Compute Spearman correlation matrix (pairwise complete)
    print("\nComputing Spearman correlation matrix...")
    n = len(valid_cols)
    corr_matrix = np.full((n, n), np.nan)
    pval_matrix = np.full((n, n), np.nan)

    for i in range(n):
        for j in range(n):
            if i == j:
                corr_matrix[i, j] = 1.0
                pval_matrix[i, j] = 0.0
                continue
            mask = df_clean[valid_cols[i]].notna() & df_clean[valid_cols[j]].notna()
            if mask.sum() < 30:
                continue
            r, p = stats.spearmanr(df_clean.loc[mask, valid_cols[i]],
                                    df_clean.loc[mask, valid_cols[j]])
            corr_matrix[i, j] = r
            pval_matrix[i, j] = p

    corr_df = pd.DataFrame(corr_matrix, index=valid_cols, columns=valid_cols)

    print("\nSpearman Correlation Matrix:")
    print(corr_df.round(3).to_string())

    # Find most/least correlated pairs
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            if not np.isnan(corr_matrix[i, j]):
                pairs.append({
                    "var1": valid_cols[i],
                    "var2": valid_cols[j],
                    "rho": float(corr_matrix[i, j]),
                    "abs_rho": abs(float(corr_matrix[i, j])),
                    "p_value": float(pval_matrix[i, j]),
                })

    pairs.sort(key=lambda x: x["abs_rho"], reverse=True)

    print("\n=== TOP 10 MOST CORRELATED PAIRS ===")
    for p in pairs[:10]:
        print(f"  {p['var1']:25s} vs {p['var2']:25s}: rho={p['rho']:+.4f}")

    print("\n=== TOP 10 LEAST CORRELATED (MOST INDEPENDENT) PAIRS ===")
    for p in pairs[-10:]:
        print(f"  {p['var1']:25s} vs {p['var2']:25s}: rho={p['rho']:+.4f}")

    # Negative correlations
    neg_pairs = [p for p in pairs if p["rho"] < 0]
    print(f"\n=== NEGATIVE CORRELATIONS: {len(neg_pairs)} pairs ===")
    neg_pairs_sorted = sorted(neg_pairs, key=lambda x: x["rho"])
    for p in neg_pairs_sorted[:10]:
        print(f"  {p['var1']:25s} vs {p['var2']:25s}: rho={p['rho']:+.4f}")

    # Most unique invariant: lowest max |correlation| with any other
    print("\n=== INVARIANT UNIQUENESS (max |rho| with any other) ===")
    uniqueness = {}
    for i, col in enumerate(valid_cols):
        max_abs = 0
        for j in range(n):
            if i != j and not np.isnan(corr_matrix[i, j]):
                max_abs = max(max_abs, abs(corr_matrix[i, j]))
        uniqueness[col] = max_abs
        print(f"  {col:30s}: max|rho| = {max_abs:.4f}")

    most_unique = min(uniqueness, key=uniqueness.get)
    print(f"\n  Most unique invariant: {most_unique} (max|rho|={uniqueness[most_unique]:.4f})")

    # PCA
    print("\n=== PCA: Effective Dimensionality ===")
    # Impute NaN with column median for PCA
    df_pca = df_clean[valid_cols].copy()
    for col in valid_cols:
        med = df_pca[col].median()
        df_pca[col] = df_pca[col].fillna(med)

    # Standardize
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X = scaler.fit_transform(df_pca.values)

    # PCA
    from sklearn.decomposition import PCA
    pca = PCA()
    pca.fit(X)

    explained = pca.explained_variance_ratio_
    cumulative = np.cumsum(explained)

    print("  Component | Variance Explained | Cumulative")
    for i, (ev, cum) in enumerate(zip(explained, cumulative)):
        print(f"  PC{i+1:2d}      |     {ev:.4f}         |   {cum:.4f}")

    # Effective dimensions (>95% variance)
    n_95 = int(np.argmax(cumulative >= 0.95)) + 1
    n_90 = int(np.argmax(cumulative >= 0.90)) + 1
    n_80 = int(np.argmax(cumulative >= 0.80)) + 1

    print(f"\n  Dimensions for 80% variance: {n_80}")
    print(f"  Dimensions for 90% variance: {n_90}")
    print(f"  Dimensions for 95% variance: {n_95}")

    # PCA loadings for top components
    loadings = {}
    for i in range(min(3, len(valid_cols))):
        comp_loadings = {valid_cols[j]: float(pca.components_[i, j])
                        for j in range(len(valid_cols))}
        sorted_loadings = dict(sorted(comp_loadings.items(), key=lambda x: abs(x[1]), reverse=True))
        loadings[f"PC{i+1}"] = sorted_loadings

    print("\n  Top PCA loadings:")
    for pc, loads in loadings.items():
        top3 = list(loads.items())[:3]
        print(f"  {pc}: {', '.join(f'{k}={v:+.3f}' for k,v in top3)}")

    # Build results
    results = {
        "metadata": {
            "n_knots_total": len(knots),
            "n_knots_analyzed": int(len(df_clean)),
            "n_features": len(valid_cols),
            "features": valid_cols,
        },
        "correlation_matrix": {
            valid_cols[i]: {valid_cols[j]: round(float(corr_matrix[i, j]), 6)
                           for j in range(n) if not np.isnan(corr_matrix[i, j])}
            for i in range(n)
        },
        "top_10_most_correlated": [
            {"var1": p["var1"], "var2": p["var2"], "rho": round(p["rho"], 6)}
            for p in pairs[:10]
        ],
        "top_10_least_correlated": [
            {"var1": p["var1"], "var2": p["var2"], "rho": round(p["rho"], 6)}
            for p in pairs[-10:]
        ],
        "negative_correlations": [
            {"var1": p["var1"], "var2": p["var2"], "rho": round(p["rho"], 6)}
            for p in neg_pairs_sorted[:15]
        ],
        "invariant_uniqueness": {k: round(v, 6) for k, v in
                                  sorted(uniqueness.items(), key=lambda x: x[1])},
        "most_unique_invariant": {
            "name": most_unique,
            "max_abs_rho": round(uniqueness[most_unique], 6),
        },
        "pca": {
            "explained_variance_ratio": [round(float(v), 6) for v in explained],
            "cumulative_variance": [round(float(v), 6) for v in cumulative],
            "n_components_80pct": n_80,
            "n_components_90pct": n_90,
            "n_components_95pct": n_95,
            "effective_dimensions": n_90,
            "top_loadings": loadings,
        },
        "summary": {
            "most_correlated_pair": f"{pairs[0]['var1']} vs {pairs[0]['var2']} (rho={pairs[0]['rho']:.4f})",
            "most_independent_pair": f"{pairs[-1]['var1']} vs {pairs[-1]['var2']} (rho={pairs[-1]['rho']:.4f})",
            "n_negative_correlations": len(neg_pairs),
            "most_negative": f"{neg_pairs_sorted[0]['var1']} vs {neg_pairs_sorted[0]['var2']} (rho={neg_pairs_sorted[0]['rho']:.4f})" if neg_pairs_sorted else "none",
            "pca_effective_dimensions": n_90,
            "most_unique_invariant": most_unique,
        }
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
