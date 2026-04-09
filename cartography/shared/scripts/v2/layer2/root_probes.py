"""
Root Probes — Polynomial root distribution comparison across domains.
=====================================================================
Compares knot polynomial root distributions with elliptic curve
Sato-Tate angle distributions. Tests whether structural similarity
exists at the level of algebraic roots, immune to prime detrending.

Usage:
    python root_probes.py                     # full probe
    python root_probes.py --max-crossing 12   # limit knot complexity
    python root_probes.py --n-null 200        # more null iterations
"""

import argparse
import json


class _NumpyEncoder(json.JSONEncoder):
    """Handle numpy types in JSON output."""
    def default(self, obj):
        import numpy as np
        if isinstance(obj, (np.integer,)): return int(obj)
        if isinstance(obj, (np.floating,)): return float(obj)
        if isinstance(obj, (np.bool_,)): return bool(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super().default(obj)
import sys
import time
import warnings
import numpy as np
from collections import defaultdict
from pathlib import Path
from scipy import stats as sp_stats
from scipy.stats import wasserstein_distance

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
KNOTS_JSON = ROOT / "cartography" / "knots" / "data" / "knots.json"
CHARON_DB = ROOT / "charon" / "data" / "charon.duckdb"
OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_FILE = OUT_DIR / "root_probe_results.jsonl"

N_ANGLE_BINS = 36  # 10-degree bins
N_RADIAL_BINS = 20


# ---------------------------------------------------------------------------
# Knot polynomial roots
# ---------------------------------------------------------------------------

def load_knot_polynomials(max_crossing=16):
    """Load Alexander and Jones polynomial coefficients from knots.json."""
    print(f"Loading knot polynomials from {KNOTS_JSON} ...")
    if not KNOTS_JSON.exists():
        print(f"  WARNING: {KNOTS_JSON} not found, trying search_engine")
        try:
            from search_engine import dispatch_search
            results = dispatch_search("knotinfo_crossing", {"max_crossing": max_crossing})
            if results and "error" not in results[0]:
                return results
        except Exception as e:
            print(f"  search_engine fallback failed: {e}")
        return []

    with open(KNOTS_JSON) as f:
        data = json.load(f)

    knots = data.get("knots", [])
    # Filter by crossing number
    out = [k for k in knots if k.get("crossing_number", 99) <= max_crossing]
    n_alex = sum(1 for k in out if k.get("alexander"))
    n_jones = sum(1 for k in out if k.get("jones"))
    print(f"  {len(out)} knots (crossing <= {max_crossing}), {n_alex} Alexander, {n_jones} Jones")
    return out


def compute_knot_root_features(knots):
    """Compute root distributions for each knot polynomial."""
    features = []
    n_skip = 0

    for k in knots:
        for poly_type in ("alexander", "jones"):
            poly = k.get(poly_type)
            if not poly or not poly.get("coefficients"):
                continue

            coeffs = poly["coefficients"]
            if len(coeffs) < 2:
                continue

            try:
                roots = np.roots(coeffs)
            except Exception:
                n_skip += 1
                continue

            if len(roots) == 0:
                continue

            # Radial distribution: |root|
            radii = np.abs(roots)
            # Angular distribution: arg(root)
            angles = np.angle(roots)  # in [-pi, pi]

            # Nearest-neighbor spacing on unit circle
            unit_angles = np.sort(np.angle(roots[np.abs(np.abs(roots) - 1.0) < 0.3]))
            if len(unit_angles) >= 2:
                spacings = np.diff(unit_angles)
                mean_spacing = float(np.mean(spacings)) if len(spacings) > 0 else 0.0
            else:
                spacings = np.array([])
                mean_spacing = 0.0

            # Histograms
            angle_hist, _ = np.histogram(angles, bins=N_ANGLE_BINS, range=(-np.pi, np.pi), density=True)
            radial_hist, _ = np.histogram(radii, bins=N_RADIAL_BINS, range=(0, max(3.0, float(np.max(radii)))), density=True)

            features.append({
                "name": k.get("name", "?"),
                "poly_type": poly_type,
                "n_roots": len(roots),
                "root_angles": angles.tolist(),
                "root_radii": radii.tolist(),
                "angle_hist": angle_hist.tolist(),
                "radial_hist": radial_hist.tolist(),
                "spacings": spacings.tolist() if len(spacings) > 0 else [],
                "mean_spacing": mean_spacing,
                "mean_radius": float(np.mean(radii)),
                "n_on_unit_circle": int(np.sum(np.abs(radii - 1.0) < 0.05)),
            })

    if n_skip:
        print(f"  WARNING: skipped {n_skip} polynomials (root computation failed)")
    print(f"  Computed root features for {len(features)} polynomial instances")
    return features


# ---------------------------------------------------------------------------
# Elliptic curve Sato-Tate angles
# ---------------------------------------------------------------------------

def load_ec_sato_tate(conductor_max=50000):
    """Load a_p values from DuckDB and compute Sato-Tate angles."""
    print(f"Loading EC a_p data from DuckDB ...")

    try:
        import duckdb
        if not CHARON_DB.exists():
            raise FileNotFoundError(f"{CHARON_DB}")
        con = duckdb.connect(str(CHARON_DB), read_only=True)
    except Exception as e:
        print(f"  WARNING: DuckDB load failed: {e}")
        print(f"  Trying search_engine fallback ...")
        try:
            from search_engine import dispatch_search
            results = dispatch_search("lmfdb_conductor", {"low": 1, "high": min(conductor_max, 1000),
                                                           "object_type": "elliptic_curve"})
            if results and "error" not in results[0]:
                return _ec_results_to_sato_tate(results)
        except Exception as e2:
            print(f"  search_engine fallback failed: {e2}")
        return []

    try:
        rows = con.execute("""
            SELECT lmfdb_label, conductor, rank, aplist
            FROM elliptic_curves
            WHERE aplist IS NOT NULL AND conductor <= ?
        """, [conductor_max]).fetchall()
        con.close()
    except Exception as e:
        print(f"  WARNING: query failed: {e}")
        return []

    # Primes for a_p indexing (first 25 primes)
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
              53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

    features = []
    n_skip = 0
    for label, conductor, rank, aplist_raw in rows:
        try:
            if isinstance(aplist_raw, str):
                aplist = json.loads(aplist_raw)
            elif isinstance(aplist_raw, (list, tuple)):
                aplist = list(aplist_raw)
            else:
                n_skip += 1
                continue
        except (json.JSONDecodeError, TypeError):
            n_skip += 1
            continue

        if not aplist or len(aplist) < 5:
            n_skip += 1
            continue

        # Compute Sato-Tate angles: theta_p = arccos(a_p / (2*sqrt(p)))
        angles = []
        for i, ap in enumerate(aplist):
            if i >= len(primes):
                break
            p = primes[i]
            bound = 2.0 * np.sqrt(p)
            if bound == 0:
                continue
            x = ap / bound
            # Clamp to [-1, 1] for arccos
            x = max(-1.0, min(1.0, x))
            angles.append(np.arccos(x))

        if len(angles) < 3:
            n_skip += 1
            continue

        angles = np.array(angles)
        angle_hist, _ = np.histogram(angles, bins=N_ANGLE_BINS, range=(0, np.pi), density=True)

        # Spacing between consecutive angles (sorted)
        sorted_angles = np.sort(angles)
        spacings = np.diff(sorted_angles)

        features.append({
            "label": label,
            "conductor": conductor,
            "rank": rank,
            "n_angles": len(angles),
            "st_angles": angles.tolist(),
            "angle_hist": angle_hist.tolist(),
            "spacings": spacings.tolist(),
            "mean_spacing": float(np.mean(spacings)) if len(spacings) > 0 else 0.0,
            "mean_angle": float(np.mean(angles)),
        })

    if n_skip:
        print(f"  WARNING: skipped {n_skip} curves")
    print(f"  Computed Sato-Tate features for {len(features)} elliptic curves")
    return features


def _ec_results_to_sato_tate(results):
    """Convert search_engine results to Sato-Tate features."""
    # Minimal fallback
    return []


# ---------------------------------------------------------------------------
# Cross-domain comparison
# ---------------------------------------------------------------------------

def compare_distributions(knot_features, ec_features, n_null=100):
    """Compare knot root angle distributions vs EC Sato-Tate distributions."""
    t0 = time.time()
    comparisons = []

    if not knot_features or not ec_features:
        print("  WARNING: one or both feature sets empty, skipping comparison")
        return comparisons

    # Aggregate knot angle histograms by polynomial type
    knot_by_type = defaultdict(list)
    for kf in knot_features:
        knot_by_type[kf["poly_type"]].append(np.array(kf["angle_hist"]))

    # Aggregate EC angle histograms
    ec_hists = [np.array(ef["angle_hist"]) for ef in ec_features]
    ec_mean_hist = np.mean(ec_hists, axis=0)

    # Aggregate EC spacings
    ec_all_spacings = []
    for ef in ec_features:
        ec_all_spacings.extend(ef["spacings"])
    ec_all_spacings = np.array(ec_all_spacings) if ec_all_spacings else np.array([0.0])

    for poly_type, hists in knot_by_type.items():
        knot_mean_hist = np.mean(hists, axis=0)

        # Note: knot angles are in [-pi, pi], EC in [0, pi]
        # We compare the SHAPE of distributions, not the raw bins
        # Normalize both to same support for KS test
        # Use cumulative distributions for KS

        # Flatten to per-object angle values for KS test
        # Since we only have histograms, use Wasserstein on histogram vectors
        # Pad to same length if needed
        min_len = min(len(knot_mean_hist), len(ec_mean_hist))
        k_hist = knot_mean_hist[:min_len]
        e_hist = ec_mean_hist[:min_len]

        # Normalize
        k_sum = k_hist.sum()
        e_sum = e_hist.sum()
        if k_sum > 0:
            k_hist = k_hist / k_sum
        if e_sum > 0:
            e_hist = e_hist / e_sum

        # Wasserstein distance between histogram vectors
        w_dist = wasserstein_distance(k_hist, e_hist)

        # KS test on cumulative distributions
        k_cdf = np.cumsum(k_hist)
        e_cdf = np.cumsum(e_hist)
        ks_stat = float(np.max(np.abs(k_cdf - e_cdf)))

        # Spacing comparison
        knot_all_spacings = []
        for kf in knot_features:
            if kf["poly_type"] == poly_type:
                knot_all_spacings.extend(kf["spacings"])
        knot_all_spacings = np.array(knot_all_spacings) if knot_all_spacings else np.array([0.0])

        if len(knot_all_spacings) > 1 and len(ec_all_spacings) > 1:
            spacing_ks = sp_stats.ks_2samp(knot_all_spacings, ec_all_spacings)
            spacing_w = wasserstein_distance(knot_all_spacings, ec_all_spacings)
        else:
            spacing_ks = type("KS", (), {"statistic": 0.0, "pvalue": 1.0})()
            spacing_w = 0.0

        comp = {
            "knot_poly": poly_type,
            "n_knots": len(hists),
            "n_ec": len(ec_hists),
            "angle_wasserstein": round(float(w_dist), 6),
            "angle_ks_stat": round(ks_stat, 6),
            "spacing_ks_stat": round(float(spacing_ks.statistic), 6),
            "spacing_ks_pvalue": round(float(spacing_ks.pvalue), 6),
            "spacing_wasserstein": round(float(spacing_w), 6),
        }

        # Null test: shuffle labels, recompute
        print(f"  Running {n_null} null iterations for {poly_type} ...")
        null_w_dists = []
        all_hists = list(hists) + list(ec_hists)
        rng = np.random.default_rng(42)
        for _ in range(n_null):
            rng.shuffle(all_hists)
            split = len(hists)
            null_k = np.mean(all_hists[:split], axis=0)
            null_e = np.mean(all_hists[split:], axis=0)
            nk = null_k / null_k.sum() if null_k.sum() > 0 else null_k
            ne = null_e / null_e.sum() if null_e.sum() > 0 else null_e
            null_w_dists.append(wasserstein_distance(nk[:min_len], ne[:min_len]))

        null_mean = float(np.mean(null_w_dists))
        null_std = float(np.std(null_w_dists))
        z_score = (w_dist - null_mean) / null_std if null_std > 0 else 0.0

        comp["null_wasserstein_mean"] = round(null_mean, 6)
        comp["null_wasserstein_std"] = round(null_std, 6)
        comp["z_vs_null"] = round(z_score, 3)
        comp["significant"] = bool(abs(z_score) > 2.0)

        comparisons.append(comp)

    elapsed = time.time() - t0
    print(f"  {len(comparisons)} comparisons in {elapsed:.1f}s")
    return comparisons


def save_results(knot_features, ec_features, comparisons, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        # Header entry
        f.write(json.dumps(cls=_NumpyEncoder, obj={
            "type": "header",
            "n_knot_features": len(knot_features),
            "n_ec_features": len(ec_features),
            "n_comparisons": len(comparisons),
        }) + "\n")

        for comp in comparisons:
            f.write(json.dumps(cls=_NumpyEncoder, obj={"type": "comparison", **comp}) + "\n")

        # ALL knot features (full distributions for battery testing)
        for kf in knot_features:
            f.write(json.dumps(cls=_NumpyEncoder, obj={"type": "knot_feature", **kf}) + "\n")

        # ALL EC features
        for ef in ec_features:
            f.write(json.dumps(cls=_NumpyEncoder, obj={"type": "ec_feature", **ef}) + "\n")

    print(f"  Wrote results to {path}")


def main():
    parser = argparse.ArgumentParser(description="Root Probes — polynomial root distribution comparison")
    parser.add_argument("--max-crossing", type=int, default=16,
                        help="Max knot crossing number (default: 16)")
    parser.add_argument("--conductor-max", type=int, default=50000,
                        help="Max EC conductor (default: 50000)")
    parser.add_argument("--n-null", type=int, default=100,
                        help="Number of null iterations (default: 100)")
    args = parser.parse_args()

    t_start = time.time()

    # Load data
    knots = load_knot_polynomials(max_crossing=args.max_crossing)
    knot_features = compute_knot_root_features(knots)

    ec_features = load_ec_sato_tate(conductor_max=args.conductor_max)

    # Compare
    print("\n--- Cross-domain comparison ---")
    comparisons = compare_distributions(knot_features, ec_features, n_null=args.n_null)

    # Save
    save_results(knot_features, ec_features, comparisons, OUT_FILE)

    # Summary
    elapsed = time.time() - t_start
    n_sig = sum(1 for c in comparisons if c.get("significant"))
    print(f"\n{'='*60}")
    print(f"Root Probes Summary")
    print(f"  Knot polynomials: {len(knot_features)}")
    print(f"  EC Sato-Tate: {len(ec_features)}")
    print(f"  Comparisons: {len(comparisons)}")
    print(f"  Significant (|z| > 2): {n_sig}")
    for c in comparisons:
        print(f"    {c['knot_poly']}: W={c['angle_wasserstein']:.4f}, "
              f"z={c['z_vs_null']:.2f} {'***' if c['significant'] else ''}")
    print(f"  Total time: {elapsed:.1f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
