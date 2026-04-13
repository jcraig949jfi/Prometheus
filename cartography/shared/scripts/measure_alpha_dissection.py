#!/usr/bin/env python3
"""
measure_alpha_dissection.py — Measure the Arithmos signal ratio (alpha) in the
M1 dissection tensor and compare with M2's measurement of 1.577 in the 5D
phoneme space.

Alpha = structured_residual_variance / null_variance
after removing the magnitude axis (Megethos).

Two methods:
  A) "Explicit Megethos": use s13 dim 0 (log magnitude) directly as the axis
  B) "PC1 Megethos": use PCA-PC1 (as M2 did in the 5D phoneme space)

If alpha matches across M1 (182-dim raw tensor) and M2 (5-dim phoneme projection),
the constant is intrinsic to the data, not to the projection.
"""

import json
import time
from pathlib import Path

import numpy as np
import torch
from sklearn.decomposition import PCA

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TENSOR_PATH = Path("F:/Prometheus/cartography/convergence/data/dissection_tensor.pt")
OUTPUT_PATH = Path("F:/Prometheus/cartography/convergence/data/alpha_dissection_results.json")
MIN_FILL_RATE = 0.50
DEFAULT_SUBSAMPLE = 50_000
N_NULL = 100
S13_DIM0_COL = 129  # s13 slice starts at 129; dim 0 = log magnitude
M2_ALPHA = 1.577
M2_ALPHA_ERR = 0.10
RNG_SEED = 42


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_and_filter(tensor_path: Path, min_fill: float):
    """Load tensor, filter to dims with >min_fill fill rate, return dense array."""
    data = torch.load(tensor_path, map_location="cpu", weights_only=False)
    tensor = data["tensor"].numpy()
    mask = data["mask"].numpy().astype(bool)
    domains = np.array(data["domains"])

    fill_rates = mask.mean(axis=0)
    keep_dims = np.where(fill_rates > min_fill)[0]
    print(f"Dimensions with >{min_fill*100:.0f}% fill: {len(keep_dims)} / {tensor.shape[1]}")

    row_mask = mask[:, keep_dims].all(axis=1)
    print(f"Objects with full coverage on kept dims: {row_mask.sum()} / {tensor.shape[0]}")

    X = tensor[row_mask][:, keep_dims]
    doms = domains[row_mask]

    s13_idx = np.where(keep_dims == S13_DIM0_COL)[0]
    s13_col = int(s13_idx[0]) if len(s13_idx) > 0 else None

    return X, doms, keep_dims, s13_col


def subsample(X, domains, n, rng):
    if len(X) <= n:
        return X, domains
    idx = rng.choice(len(X), size=n, replace=False)
    return X[idx], domains[idx]


def compute_alpha_in_bins(X_resid, bin_assignments, n_null, rng):
    """
    Within each bin, measure variance explained by residual-PC1.
    Null: shuffle rows globally, recompute.
    Returns: alpha, structured_var, null_var, null_std, per_bin_vars
    """
    unique_bins = np.unique(bin_assignments)

    # --- Structured variance ---
    per_bin_var = []
    for b in unique_bins:
        Xb = X_resid[bin_assignments == b]
        if Xb.shape[0] < 10 or Xb.shape[1] < 2:
            continue
        pca = PCA(n_components=1)
        pca.fit(Xb)
        per_bin_var.append(pca.explained_variance_ratio_[0])

    structured_var = float(np.mean(per_bin_var))

    # --- Null variance ---
    null_vars = []
    for _ in range(n_null):
        perm_resid = X_resid[rng.permutation(len(X_resid))]
        bv = []
        for b in unique_bins:
            Xb = perm_resid[bin_assignments == b]
            if Xb.shape[0] < 10 or Xb.shape[1] < 2:
                continue
            pca = PCA(n_components=1)
            pca.fit(Xb)
            bv.append(pca.explained_variance_ratio_[0])
        null_vars.append(float(np.mean(bv)))

    null_var = float(np.mean(null_vars))
    null_std = float(np.std(null_vars))

    alpha = structured_var / null_var if null_var > 0 else float("inf")
    return alpha, structured_var, null_var, null_std, per_bin_var


def regress_out_axis(X, axis_scores):
    """Regress a 1D axis out of X. Returns residuals."""
    # OLS: project each column onto axis_scores
    axis_norm = axis_scores / (np.dot(axis_scores, axis_scores) + 1e-30)
    coeffs = X.T @ axis_norm  # (D,)
    projections = np.outer(axis_scores, coeffs)
    return X - projections


def measure_alpha_explicit_megethos(X, s13_col, n_bins, n_null, rng):
    """
    Method A: Use s13 dim 0 directly as the magnitude axis.
    Regress it out, then measure alpha.
    """
    mag_scores = X[:, s13_col].copy()

    # Remove s13_col from feature set to avoid trivial self-correlation
    other_cols = [i for i in range(X.shape[1]) if i != s13_col]
    X_feat = X[:, other_cols]

    # Regress out magnitude
    X_resid = regress_out_axis(X_feat, mag_scores)

    # Bin by magnitude
    bin_edges = np.percentile(mag_scores, np.linspace(0, 100, n_bins + 1))
    bin_assignments = np.digitize(mag_scores, bin_edges[1:-1])

    alpha, struct_var, null_var, null_std, per_bin_var = compute_alpha_in_bins(
        X_resid, bin_assignments, n_null, rng
    )

    return {
        "method": "explicit_megethos",
        "alpha": alpha,
        "structured_variance": struct_var,
        "null_variance": null_var,
        "null_std": null_std,
        "per_bin_variance": [float(v) for v in per_bin_var],
        "n_bins": n_bins,
        "n_objects": X.shape[0],
        "n_dims": len(other_cols),
    }


def measure_alpha_pc1(X, s13_col, n_bins, n_null, rng):
    """
    Method B: Use PCA-PC1 as the magnitude axis (how M2 did it).
    """
    pca_full = PCA(n_components=min(10, X.shape[1]))
    scores = pca_full.fit_transform(X)
    pc1_scores = scores[:, 0]
    pc1_var_explained = pca_full.explained_variance_ratio_[0]

    megethos_corr = None
    if s13_col is not None:
        megethos_corr = float(np.corrcoef(pc1_scores, X[:, s13_col])[0, 1])

    # Regress out PC1
    pc1_vec = pca_full.components_[0]
    X_resid = X - np.outer(pc1_scores, pc1_vec)

    bin_edges = np.percentile(pc1_scores, np.linspace(0, 100, n_bins + 1))
    bin_assignments = np.digitize(pc1_scores, bin_edges[1:-1])

    alpha, struct_var, null_var, null_std, per_bin_var = compute_alpha_in_bins(
        X_resid, bin_assignments, n_null, rng
    )

    return {
        "method": "pc1_megethos",
        "alpha": alpha,
        "structured_variance": struct_var,
        "null_variance": null_var,
        "null_std": null_std,
        "pc1_variance_explained": float(pc1_var_explained),
        "megethos_correlation": megethos_corr,
        "per_bin_variance": [float(v) for v in per_bin_var],
        "n_bins": n_bins,
        "n_objects": X.shape[0],
        "n_dims": X.shape[1],
    }


def measure_alpha_per_pair(X, domains, s13_col, n_bins, n_null, rng):
    """Measure alpha (explicit Megethos) for each domain pair."""
    dom_counts = {}
    for d in domains:
        dom_counts[d] = dom_counts.get(d, 0) + 1
    big_doms = sorted(d for d, c in dom_counts.items() if c >= 200)

    pair_results = {}
    for i, d1 in enumerate(big_doms):
        for d2 in big_doms[i + 1:]:
            sel = (domains == d1) | (domains == d2)
            Xp = X[sel]
            if Xp.shape[0] < 100:
                continue
            pair_rng = np.random.default_rng(RNG_SEED)
            res = measure_alpha_explicit_megethos(
                Xp, s13_col, n_bins, max(n_null // 2, 20), pair_rng
            )
            pair_results[f"{d1}-{d2}"] = {
                "alpha": res["alpha"],
                "n_objects": res["n_objects"],
                "structured_variance": res["structured_variance"],
                "null_variance": res["null_variance"],
            }
            print(f"  {d1}-{d2}: alpha={res['alpha']:.4f} (n={res['n_objects']})")

    return pair_results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    rng = np.random.default_rng(RNG_SEED)

    print("=" * 60)
    print("ALPHA DISSECTION — M1 vs M2 comparison")
    print("=" * 60)

    # Load
    print("\n[1] Loading tensor...")
    X_full, domains_full, keep_dims, s13_col = load_and_filter(TENSOR_PATH, MIN_FILL_RATE)
    print(f"    s13 dim 0 column in filtered space: {s13_col}")
    print(f"    Shape: {X_full.shape}")

    # Subsample
    print(f"\n[2] Subsampling to {DEFAULT_SUBSAMPLE}...")
    X, domains = subsample(X_full, domains_full, DEFAULT_SUBSAMPLE, rng)
    print(f"    Working shape: {X.shape}")

    # ===== Method A: Explicit Megethos =====
    print("\n[3A] Method A — Explicit Megethos (s13 dim 0 as magnitude axis)...")
    result_A = measure_alpha_explicit_megethos(X, s13_col, 10, N_NULL, np.random.default_rng(RNG_SEED))
    print(f"     Structured variance: {result_A['structured_variance']:.6f}")
    print(f"     Null variance:       {result_A['null_variance']:.6f} +/- {result_A['null_std']:.6f}")
    print(f"     >>> ALPHA (explicit) = {result_A['alpha']:.4f}")

    # ===== Method B: PC1 Megethos =====
    print("\n[3B] Method B — PC1 as magnitude axis...")
    result_B = measure_alpha_pc1(X, s13_col, 10, N_NULL, np.random.default_rng(RNG_SEED))
    print(f"     PC1 variance explained: {result_B['pc1_variance_explained']:.4f}")
    print(f"     PC1-Megethos corr:      {result_B['megethos_correlation']:.4f}")
    print(f"     Structured variance:    {result_B['structured_variance']:.6f}")
    print(f"     Null variance:          {result_B['null_variance']:.6f} +/- {result_B['null_std']:.6f}")
    print(f"     >>> ALPHA (PC1) = {result_B['alpha']:.4f}")

    # Use Method A as canonical (it regresses out the actual magnitude axis)
    m1_alpha = result_A["alpha"]

    # ===== Bin sweep (Method A) =====
    print("\n[4] Varying number of bins (Method A)...")
    bin_sweep = {}
    for nb in [5, 10, 20, 50]:
        r = measure_alpha_explicit_megethos(X, s13_col, nb, N_NULL, np.random.default_rng(RNG_SEED))
        bin_sweep[nb] = r["alpha"]
        print(f"    bins={nb:3d}: alpha={r['alpha']:.4f}")

    # ===== Size sweep (Method A) =====
    print("\n[5] Varying subsample size (Method A)...")
    size_sweep = {}
    for ns in [10_000, 20_000, 50_000]:
        Xs, ds = subsample(X_full, domains_full, ns, np.random.default_rng(RNG_SEED))
        r = measure_alpha_explicit_megethos(Xs, s13_col, 10, N_NULL, np.random.default_rng(RNG_SEED))
        size_sweep[ns] = r["alpha"]
        print(f"    n={ns:6d}: alpha={r['alpha']:.4f}")

    # ===== Per-bin profile =====
    print("\n[6] Per-bin alpha profile (Method A, does alpha change with magnitude?)...")
    per_bin = result_A["per_bin_variance"]
    for i, v in enumerate(per_bin):
        bar = "#" * int(v * 200)
        print(f"    bin {i:2d}: residual-PC1 var = {v:.4f}  {bar}")

    # ===== Per-pair alpha =====
    print("\n[7] Per-domain-pair alpha (Method A, 50 null iterations per pair)...")
    pair_results = measure_alpha_per_pair(X, domains, s13_col, 10, 50, rng)
    sorted_pairs = sorted(pair_results.items(), key=lambda x: x[1]["alpha"], reverse=True)

    # ===== Agreement check =====
    agreement = abs(m1_alpha - M2_ALPHA) <= M2_ALPHA_ERR
    agreement_delta = abs(m1_alpha - M2_ALPHA)

    # Compute pair mean/median
    pair_alphas = [v["alpha"] for v in pair_results.values()]
    pair_mean = float(np.mean(pair_alphas)) if pair_alphas else 0
    pair_median = float(np.median(pair_alphas)) if pair_alphas else 0
    pair_agreement = abs(pair_median - M2_ALPHA) <= M2_ALPHA_ERR

    # ===== Summary =====
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\n  --- Whole-tensor alpha ---")
    print(f"  Method A (explicit Megethos): {result_A['alpha']:.4f}")
    print(f"  Method B (PC1):               {result_B['alpha']:.4f}")
    print(f"  PC1-Megethos correlation:     {result_B['megethos_correlation']:.4f}")
    print(f"  NOTE: PC1 is NOT Megethos in 41-dim space (corr={result_B['megethos_correlation']:.3f})")
    print(f"        Method A (explicit) is the valid measurement.")
    print(f"\n  --- Comparison with M2 ---")
    print(f"  M1 alpha (explicit):     {m1_alpha:.4f}")
    print(f"  M2 alpha (phoneme):      {M2_ALPHA:.3f} +/- {M2_ALPHA_ERR:.2f}")
    print(f"  Delta:                   {agreement_delta:.4f}")
    print(f"  Within uncertainty:      {'YES' if agreement else 'NO'}")
    print(f"\n  --- Pairwise alpha ---")
    print(f"  Mean across pairs:       {pair_mean:.4f}")
    print(f"  Median across pairs:     {pair_median:.4f}")
    print(f"  Pair median vs M2:       delta={abs(pair_median - M2_ALPHA):.4f}, "
          f"within uncertainty: {'YES' if pair_agreement else 'NO'}")
    print(f"\n  Bin sweep: {bin_sweep}")
    print(f"  Size sweep: {size_sweep}")
    print(f"\n  Top 5 domain pairs by alpha:")
    for pair, info in sorted_pairs[:5]:
        print(f"    {pair:20s}: alpha={info['alpha']:.4f}  (n={info['n_objects']})")
    print(f"\n  Bottom 5 domain pairs by alpha:")
    for pair, info in sorted_pairs[-5:]:
        print(f"    {pair:20s}: alpha={info['alpha']:.4f}  (n={info['n_objects']})")

    elapsed = time.time() - t0
    print(f"\n  Elapsed: {elapsed:.1f}s")

    # ===== Save =====
    results = {
        "m1_alpha": m1_alpha,
        "m1_alpha_method": "explicit_megethos",
        "m2_alpha": M2_ALPHA,
        "m2_alpha_err": M2_ALPHA_ERR,
        "agreement_within_uncertainty": agreement,
        "delta": agreement_delta,
        "method_A_explicit": result_A,
        "method_B_pc1": result_B,
        "bin_sweep": {str(k): v for k, v in bin_sweep.items()},
        "size_sweep": {str(k): v for k, v in size_sweep.items()},
        "per_bin_profile": per_bin,
        "pair_alphas": pair_results,
        "pair_summary": {
            "mean": pair_mean,
            "median": pair_median,
            "median_within_m2_uncertainty": pair_agreement,
        },
        "top_pairs": [(p, d) for p, d in sorted_pairs[:10]],
        "config": {
            "min_fill_rate": MIN_FILL_RATE,
            "default_subsample": DEFAULT_SUBSAMPLE,
            "n_null": N_NULL,
            "seed": RNG_SEED,
            "n_kept_dims": int(result_A["n_dims"]),
            "n_available_objects": int(X_full.shape[0]),
        },
        "diagnostic": {
            "pc1_is_megethos": False,
            "pc1_megethos_corr": result_B["megethos_correlation"],
            "note": "In 41-dim filtered space, PC1 captures strategy covariance, not magnitude. "
                    "s13 dim 0 (log magnitude) loads on PC2/PC4. Method A (explicit regress-out) "
                    "is the valid measurement for the M1 tensor.",
        },
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
