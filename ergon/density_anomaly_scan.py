#!/usr/bin/env python3
"""
Aporia Void Detection Protocol — Step 2: Density Anomaly Scan

Finds "Mendeleev gaps" — regions in feature space where objects SHOULD exist
(by interpolation from neighbors) but don't.

For each domain:
  1. Extract non-NaN feature columns, PCA to 3D
  2. Build KDE in PCA space
  3. Identify low-density objects (bottom 5%) and void regions
  4. Report outliers and predicted-but-missing objects

Cross-domain:
  5. Shared PCA projection to find overlap regions predicting cross-domain objects

Usage:
    python ergon/density_anomaly_scan.py [--max-kde-samples 10000] [--grid-res 25]
"""
import sys
import json
import argparse
import warnings
from pathlib import Path

import numpy as np
from scipy.stats import gaussian_kde
from scipy.linalg import svd

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root / "ergon"))
sys.path.insert(0, str(_root))

from tensor_builder import TensorData

warnings.filterwarnings("ignore", category=RuntimeWarning)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pca_reduce(X, n_components=3):
    """PCA via SVD. Returns (projected, explained_variance_ratio, components).

    X: (n_samples, n_features) — assumed already centered/z-scored.
    """
    # Center
    mean = np.nanmean(X, axis=0)
    Xc = X - mean
    # Replace any residual NaN with 0 (shouldn't happen after col filtering)
    Xc = np.nan_to_num(Xc, nan=0.0)

    n = min(Xc.shape)
    k = min(n_components, n)

    U, s, Vt = svd(Xc, full_matrices=False)
    var_explained = (s ** 2) / max(np.sum(s ** 2), 1e-12)

    proj = U[:, :k] * s[:k]  # (n_samples, k)
    return proj, var_explained[:k], Vt[:k], mean


def build_kde(points, bw_method="scott"):
    """Build gaussian_kde on (n_samples, n_dims) points. Returns kde object."""
    # gaussian_kde expects (n_dims, n_samples)
    return gaussian_kde(points.T, bw_method=bw_method)


def find_voids(kde, points, grid_res=25):
    """Find void regions: grid cells where interpolated density > threshold but
    actual density is ~0.

    Returns list of (grid_point, predicted_density) for void cells.
    """
    mins = points.min(axis=0)
    maxs = points.max(axis=0)
    ndim = points.shape[1]

    # Build grid
    axes = [np.linspace(mins[d], maxs[d], grid_res) for d in range(ndim)]
    mesh = np.meshgrid(*axes, indexing="ij")
    grid_points = np.column_stack([m.ravel() for m in mesh])  # (grid_res^ndim, ndim)

    # Evaluate KDE on grid
    grid_density = kde(grid_points.T)

    # Threshold: median density of actual data points
    data_density = kde(points.T)
    threshold = np.median(data_density) * 0.1  # 10% of median = "should have something"

    # Find grid points where density is above threshold
    # Then check if any actual data point is nearby
    voids = []
    # "Nearby" = within 1 grid spacing in each dimension
    spacing = np.array([(maxs[d] - mins[d]) / grid_res for d in range(ndim)])

    for i in range(len(grid_points)):
        if grid_density[i] < threshold:
            continue
        # Check if any data point is within 1.5 spacing
        diffs = np.abs(points - grid_points[i])
        close = np.all(diffs < 1.5 * spacing, axis=1)
        if not np.any(close):
            voids.append((grid_points[i], float(grid_density[i])))

    # Sort by density descending (highest predicted density = strongest void)
    voids.sort(key=lambda x: -x[1])
    return voids


# ---------------------------------------------------------------------------
# Per-domain analysis
# ---------------------------------------------------------------------------

def analyze_domain(td, domain, start, end, max_kde_samples=10000, grid_res=25):
    """Run density anomaly scan on a single domain."""
    data = td.data[start:end]
    n_objects = end - start

    # Find non-NaN columns for this domain
    valid_mask = np.isfinite(data)
    col_valid = valid_mask.any(axis=0)
    valid_cols = np.where(col_valid)[0]

    if len(valid_cols) < 2:
        return {
            "domain": domain,
            "n_objects": n_objects,
            "n_features": len(valid_cols),
            "skip_reason": "too few features (<2)",
        }

    X = data[:, valid_cols]

    # Drop rows with any NaN in valid columns
    row_mask = np.all(np.isfinite(X), axis=1)
    X_clean = X[row_mask]
    clean_indices = np.where(row_mask)[0]  # indices relative to domain start

    if len(X_clean) < 10:
        return {
            "domain": domain,
            "n_objects": n_objects,
            "n_features": len(valid_cols),
            "skip_reason": f"too few clean rows ({len(X_clean)})",
        }

    n_clean = len(X_clean)
    n_dims = X_clean.shape[1]
    n_pca = min(3, n_dims)

    # PCA
    proj, var_explained, components, mean = pca_reduce(X_clean, n_components=n_pca)

    # Subsample for KDE if too large
    if n_clean > max_kde_samples:
        rng = np.random.RandomState(42)
        kde_idx = rng.choice(n_clean, max_kde_samples, replace=False)
        kde_points = proj[kde_idx]
    else:
        kde_idx = None
        kde_points = proj

    # Build KDE
    try:
        kde = build_kde(kde_points)
    except Exception as e:
        return {
            "domain": domain,
            "n_objects": n_objects,
            "n_features": n_dims,
            "n_pca_dims": n_pca,
            "var_explained": var_explained.tolist(),
            "skip_reason": f"KDE failed: {e}",
        }

    # Evaluate density at ALL points (not just subsample)
    density = kde(proj.T)

    # Bottom 5% = low-density objects
    threshold_5pct = np.percentile(density, 5)
    low_mask = density <= threshold_5pct
    low_indices = np.where(low_mask)[0]

    # Get the 5 lowest-density objects
    sorted_by_density = np.argsort(density)
    bottom5 = sorted_by_density[:5]

    outliers = []
    for idx in bottom5:
        outliers.append({
            "domain_row": int(clean_indices[idx]),
            "global_row": int(start + clean_indices[idx]),
            "density": float(density[idx]),
            "pca_coords": proj[idx].tolist(),
        })

    # Void detection
    try:
        voids = find_voids(kde, kde_points, grid_res=grid_res)
    except Exception:
        voids = []

    return {
        "domain": domain,
        "n_objects": n_objects,
        "n_clean": n_clean,
        "n_features": n_dims,
        "n_pca_dims": n_pca,
        "var_explained": var_explained.tolist(),
        "pct_low_density": float(np.sum(low_mask) / n_clean * 100),
        "n_low_density": int(np.sum(low_mask)),
        "outliers": outliers,
        "n_voids": len(voids),
        "top_voids": voids[:10],  # Top 10 strongest voids
        "density_stats": {
            "min": float(np.min(density)),
            "median": float(np.median(density)),
            "max": float(np.max(density)),
            "std": float(np.std(density)),
        },
    }


# ---------------------------------------------------------------------------
# Cross-domain analysis
# ---------------------------------------------------------------------------

def cross_domain_analysis(td, max_per_domain=2000):
    """Project all domains into shared PCA space, check for overlaps."""
    all_points = []
    all_labels = []

    for domain, (start, end) in td.domain_boundaries.items():
        data = td.data[start:end]
        n = end - start

        # Subsample large domains
        if n > max_per_domain:
            rng = np.random.RandomState(hash(domain) % 2**31)
            idx = rng.choice(n, max_per_domain, replace=False)
            data = data[idx]
            n = max_per_domain

        # Replace NaN with 0 for shared projection
        data_filled = np.nan_to_num(data, nan=0.0)
        all_points.append(data_filled)
        all_labels.extend([domain] * n)

    X_all = np.vstack(all_points)
    labels = np.array(all_labels)

    # Shared PCA
    proj, var_explained, _, _ = pca_reduce(X_all, n_components=3)

    # For each domain pair, compute overlap: fraction of domain A's points
    # that fall within the convex hull approximation of domain B
    # Simplified: use bounding box overlap in PCA space
    domains = list(td.domain_boundaries.keys())
    domain_bounds = {}
    for d in domains:
        mask = labels == d
        if mask.sum() < 2:
            continue
        pts = proj[mask]
        domain_bounds[d] = {
            "min": pts.min(axis=0),
            "max": pts.max(axis=0),
            "centroid": pts.mean(axis=0),
            "n": int(mask.sum()),
        }

    # Find overlapping domain pairs (bounding box intersection)
    overlaps = []
    domain_list = list(domain_bounds.keys())
    for i in range(len(domain_list)):
        for j in range(i + 1, len(domain_list)):
            d1, d2 = domain_list[i], domain_list[j]
            b1, b2 = domain_bounds[d1], domain_bounds[d2]

            # Check 3D bounding box overlap
            overlap_min = np.maximum(b1["min"], b2["min"])
            overlap_max = np.minimum(b1["max"], b2["max"])
            overlap_vol = np.prod(np.maximum(overlap_max - overlap_min, 0))

            if overlap_vol > 0:
                vol1 = np.prod(np.maximum(b1["max"] - b1["min"], 1e-10))
                vol2 = np.prod(np.maximum(b2["max"] - b2["min"], 1e-10))
                overlap_frac = overlap_vol / min(vol1, vol2)

                if overlap_frac > 0.01:  # At least 1% overlap
                    overlaps.append({
                        "domain_a": d1,
                        "domain_b": d2,
                        "overlap_fraction": float(overlap_frac),
                        "centroid_dist": float(np.linalg.norm(
                            b1["centroid"] - b2["centroid"]
                        )),
                    })

    overlaps.sort(key=lambda x: -x["overlap_fraction"])

    return {
        "n_domains": len(domain_bounds),
        "total_points": len(labels),
        "shared_var_explained": var_explained.tolist(),
        "n_overlapping_pairs": len(overlaps),
        "top_overlaps": overlaps[:15],
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(results, cross):
    """Print formatted report to stdout."""
    print("=" * 78)
    print("  APORIA VOID DETECTION PROTOCOL — Step 2: Density Anomaly Scan")
    print("=" * 78)
    print()

    # Per-domain results
    for r in results:
        domain = r["domain"]
        print(f"{'-' * 78}")
        print(f"  DOMAIN: {domain}")
        print(f"{'-' * 78}")
        print(f"  Objects: {r['n_objects']:,}    Features: {r['n_features']}")

        if "skip_reason" in r:
            print(f"  SKIPPED: {r['skip_reason']}")
            print()
            continue

        n_clean = r.get("n_clean", r["n_objects"])
        print(f"  Clean rows: {n_clean:,}    PCA dims: {r['n_pca_dims']}")

        ve = r["var_explained"]
        ve_str = ", ".join(f"{v:.1%}" for v in ve)
        print(f"  Variance explained (top {len(ve)} PCs): [{ve_str}]")
        print(f"  Cumulative: {sum(ve):.1%}")

        ds = r["density_stats"]
        print(f"  Density — min: {ds['min']:.2e}  median: {ds['median']:.2e}  "
              f"max: {ds['max']:.2e}  std: {ds['std']:.2e}")

        print(f"\n  Low-density objects (bottom 5%): {r['n_low_density']:,} "
              f"({r['pct_low_density']:.1f}%)")

        print(f"\n  Top 5 outliers (lowest density):")
        for i, o in enumerate(r["outliers"]):
            coords = ", ".join(f"{c:.3f}" for c in o["pca_coords"])
            print(f"    {i+1}. row {o['global_row']:>8,}  "
                  f"density={o['density']:.2e}  PCA=[{coords}]")

        print(f"\n  Void regions found: {r['n_voids']}")
        if r["top_voids"]:
            print(f"  Top void regions (predicted density > threshold, no objects nearby):")
            for i, (pt, dens) in enumerate(r["top_voids"][:5]):
                coords = ", ".join(f"{c:.3f}" for c in pt)
                print(f"    {i+1}. PCA=[{coords}]  predicted_density={dens:.2e}")

        print()

    # Summary table
    print(f"{'=' * 78}")
    print(f"  SUMMARY TABLE")
    print(f"{'=' * 78}")
    print(f"  {'Domain':<20s} {'Objects':>8s} {'Feats':>5s} {'Low%':>6s} "
          f"{'Voids':>6s} {'PC1%':>6s} {'PC1+2+3%':>8s}")
    print(f"  {'-' * 20} {'-' * 8} {'-' * 5} {'-' * 6} {'-' * 6} {'-' * 6} {'-' * 8}")

    for r in results:
        if "skip_reason" in r:
            print(f"  {r['domain']:<20s} {r['n_objects']:>8,} {r['n_features']:>5} "
                  f"{'SKIP':>6s} {'':>6s} {'':>6s} {'':>8s}")
            continue

        ve = r["var_explained"]
        cum = sum(ve)
        n_clean = r.get("n_clean", r["n_objects"])
        print(f"  {r['domain']:<20s} {n_clean:>8,} {r['n_features']:>5} "
              f"{r['pct_low_density']:>5.1f}% {r['n_voids']:>6} "
              f"{ve[0]:>5.1%} {cum:>7.1%}")

    # Cross-domain
    print()
    print(f"{'=' * 78}")
    print(f"  CROSS-DOMAIN ANALYSIS")
    print(f"{'=' * 78}")
    print(f"  Domains projected: {cross['n_domains']}")
    print(f"  Total points: {cross['total_points']:,}")

    cve = cross["shared_var_explained"]
    cve_str = ", ".join(f"{v:.1%}" for v in cve)
    print(f"  Shared PCA variance explained: [{cve_str}]")
    print(f"  Overlapping domain pairs (bbox >1%): {cross['n_overlapping_pairs']}")

    if cross["top_overlaps"]:
        print(f"\n  Top cross-domain overlaps (predict cross-domain objects):")
        for i, o in enumerate(cross["top_overlaps"]):
            print(f"    {i+1}. {o['domain_a']:<18s} x {o['domain_b']:<18s}  "
                  f"overlap={o['overlap_fraction']:.1%}  "
                  f"centroid_dist={o['centroid_dist']:.2f}")
    else:
        print(f"\n  No significant bounding-box overlaps found.")

    print()
    print(f"{'=' * 78}")
    print(f"  END OF DENSITY ANOMALY SCAN")
    print(f"{'=' * 78}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Aporia Void Detection: Density Anomaly Scan")
    parser.add_argument("--tensor", type=str, default=str(_root / "ergon" / "tensor.npz"),
                        help="Path to tensor.npz")
    parser.add_argument("--max-kde-samples", type=int, default=10000,
                        help="Max samples for KDE fitting (subsample large domains)")
    parser.add_argument("--grid-res", type=int, default=25,
                        help="Grid resolution per PCA axis for void detection")
    parser.add_argument("--domains", type=str, default=None,
                        help="Comma-separated domain names (default: all)")
    args = parser.parse_args()

    # Load tensor
    print(f"Loading tensor from {args.tensor} ...")
    td = TensorData.load(args.tensor)
    print(f"  Shape: ({td.n_objects:,}, {td.n_features})")
    print(f"  Domains: {len(td.domain_boundaries)}")
    print()

    # Select domains
    if args.domains:
        selected = [d.strip() for d in args.domains.split(",")]
    else:
        selected = list(td.domain_boundaries.keys())

    # Per-domain analysis
    results = []
    for domain in selected:
        if domain not in td.domain_boundaries:
            print(f"  WARNING: domain '{domain}' not in tensor, skipping")
            continue

        start, end = td.domain_boundaries[domain]
        n = end - start
        print(f"  Scanning {domain} ({n:,} objects) ...", end="", flush=True)

        r = analyze_domain(
            td, domain, start, end,
            max_kde_samples=args.max_kde_samples,
            grid_res=args.grid_res,
        )
        results.append(r)

        if "skip_reason" in r:
            print(f" SKIPPED ({r['skip_reason']})")
        else:
            print(f" {r['n_voids']} voids, {r['n_low_density']} low-density")

    # Cross-domain analysis
    print(f"\n  Running cross-domain analysis ...", flush=True)
    cross = cross_domain_analysis(td)
    print(f"  Done: {cross['n_overlapping_pairs']} overlapping pairs")
    print()

    # Print full report
    print_report(results, cross)


if __name__ == "__main__":
    main()
