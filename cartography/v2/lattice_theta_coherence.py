"""
DS7: Lattice Theta Function Phase Coherence

For each lattice, the theta series coefficients a_n are non-negative integers
(counts of lattice vectors of norm n). We compute phase coherence by mapping
coefficients to unit-circle phases via z_n = exp(2*pi*i * a_n / P) for
several small primes P, then measuring the mean resultant length:

    R_P = |mean(z_n)|

This is the standard circular statistics "concentration parameter". High R means
the a_n cluster modulo P; low R means they are uniformly spread mod P.

We also compute a multi-prime coherence as the geometric mean over P in {2,3,5,7}.

We group by lattice dimension and find the threshold where coherence drops below 0.5.
"""

import json
import numpy as np
from collections import defaultdict
from pathlib import Path
from scipy import stats

DATA_PATH = Path(__file__).parent.parent / "lmfdb_dump" / "lat_lattices.json"
OUT_PATH = Path(__file__).parent / "lattice_theta_coherence_results.json"

PRIMES = [2, 3, 5, 7]


def compute_coherence(theta_series, P):
    """Mean resultant length of exp(2*pi*i * a_n / P), skipping a_0."""
    coeffs = np.array(theta_series[1:], dtype=float)  # skip constant term a_0=1
    if len(coeffs) == 0:
        return np.nan
    phases = np.exp(2j * np.pi * coeffs / P)
    return float(np.abs(np.mean(phases)))


def compute_sign_coherence(theta_series):
    """Fraction of nonzero coefficients (all are >= 0, so sign coherence is trivial).
    Instead, compute coherence of zero/nonzero pattern as binary phase."""
    coeffs = np.array(theta_series[1:], dtype=float)
    if len(coeffs) == 0:
        return np.nan
    binary = (coeffs > 0).astype(float)
    # Map: 0 -> exp(0) = 1, 1 -> exp(i*pi) = -1
    phases = np.exp(1j * np.pi * binary)
    return float(np.abs(np.mean(phases)))


def main():
    print("Loading lattice data...")
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    records = data["records"]
    print(f"Loaded {len(records)} lattices")

    # Per-lattice coherence
    results_per_lattice = []
    dim_groups = defaultdict(list)

    for rec in records:
        dim = rec.get("dim")
        ts = rec.get("theta_series")
        kissing = rec.get("kissing")
        det = rec.get("det")
        label = rec.get("label", rec.get("name", ""))

        if not ts or len(ts) < 2:
            continue

        # Compute coherence for each prime
        coh = {}
        for P in PRIMES:
            coh[f"R_{P}"] = compute_coherence(ts, P)

        # Geometric mean of multi-prime coherences
        vals = [coh[f"R_{P}"] for P in PRIMES]
        coh["R_geomean"] = float(np.exp(np.mean(np.log(np.array(vals) + 1e-15))))

        # Zero-nonzero pattern coherence
        coh["R_binary"] = compute_sign_coherence(ts)

        # Sparsity: fraction of zero coefficients
        coeffs = ts[1:]
        coh["sparsity"] = sum(1 for c in coeffs if c == 0) / len(coeffs)

        entry = {
            "label": label,
            "dim": dim,
            "det": det,
            "kissing": kissing,
            "n_coeffs": len(ts) - 1,
            **coh,
        }
        results_per_lattice.append(entry)
        dim_groups[dim].append(entry)

    print(f"Processed {len(results_per_lattice)} lattices with valid theta series")

    # --- Aggregate by dimension ---
    dim_summary = {}
    for dim in sorted(dim_groups.keys()):
        group = dim_groups[dim]
        n = len(group)
        summary = {"n_lattices": n, "dim": dim}

        for key in ["R_2", "R_3", "R_5", "R_7", "R_geomean", "R_binary", "sparsity"]:
            vals = [g[key] for g in group if not np.isnan(g[key])]
            if vals:
                summary[f"{key}_mean"] = float(np.mean(vals))
                summary[f"{key}_std"] = float(np.std(vals))
                summary[f"{key}_median"] = float(np.median(vals))
            else:
                summary[f"{key}_mean"] = None

        # Kissing number stats
        kiss_vals = [g["kissing"] for g in group if g["kissing"] is not None]
        if kiss_vals:
            summary["kissing_mean"] = float(np.mean(kiss_vals))
            summary["kissing_median"] = float(np.median(kiss_vals))

        # Det stats
        det_vals = [g["det"] for g in group if g["det"] is not None]
        if det_vals:
            summary["det_mean"] = float(np.mean(det_vals))
            summary["det_median"] = float(np.median(det_vals))

        dim_summary[dim] = summary

    # --- Find threshold dimension where R_geomean drops below 0.5 ---
    threshold_dim = None
    dims_sorted = sorted(dim_summary.keys())
    for dim in dims_sorted:
        mean_coh = dim_summary[dim].get("R_geomean_mean")
        if mean_coh is not None and mean_coh < 0.5:
            threshold_dim = dim
            break

    # --- Correlations: coherence vs kissing, coherence vs det ---
    all_coh = np.array([r["R_geomean"] for r in results_per_lattice])
    all_kiss = np.array([r["kissing"] if r["kissing"] is not None else np.nan for r in results_per_lattice])
    all_det = np.array([float(r["det"]) if r["det"] is not None else np.nan for r in results_per_lattice])
    all_dim = np.array([r["dim"] for r in results_per_lattice])

    # Coherence vs kissing
    mask_k = ~np.isnan(all_kiss) & ~np.isnan(all_coh)
    if mask_k.sum() > 2:
        r_kiss, p_kiss = stats.spearmanr(all_coh[mask_k], all_kiss[mask_k])
    else:
        r_kiss, p_kiss = None, None

    # Coherence vs det
    mask_d = ~np.isnan(all_det) & ~np.isnan(all_coh)
    if mask_d.sum() > 2:
        r_det, p_det = stats.spearmanr(all_coh[mask_d], all_det[mask_d])
    else:
        r_det, p_det = None, None

    # Coherence vs dim
    mask_dim = ~np.isnan(all_coh)
    if mask_dim.sum() > 2:
        r_dim, p_dim = stats.spearmanr(all_coh[mask_dim], all_dim[mask_dim])
    else:
        r_dim, p_dim = None, None

    # --- Per-prime coherence by dimension (for detailed report) ---
    prime_by_dim = {}
    for dim in dims_sorted:
        prime_by_dim[dim] = {}
        for P in PRIMES:
            key = f"R_{P}_mean"
            prime_by_dim[dim][f"R_{P}"] = dim_summary[dim].get(key)

    # --- Print report ---
    print("\n" + "=" * 70)
    print("LATTICE THETA FUNCTION PHASE COHERENCE — DS7 RESULTS")
    print("=" * 70)

    print(f"\nTotal lattices processed: {len(results_per_lattice)}")
    print(f"\nPhase coherence method: R_P = |mean(exp(2*pi*i * a_n / P))|")
    print(f"Primes used: {PRIMES}")
    print(f"Multi-prime coherence: geometric mean over all primes")

    print(f"\n{'Dim':>4} {'N':>6} {'R_2':>8} {'R_3':>8} {'R_5':>8} {'R_7':>8} {'R_geo':>8} {'R_bin':>8} {'Spars':>8} {'Kiss':>8}")
    print("-" * 78)
    for dim in dims_sorted:
        s = dim_summary[dim]
        print(f"{dim:4d} {s['n_lattices']:6d} "
              f"{s.get('R_2_mean', 0):8.4f} "
              f"{s.get('R_3_mean', 0):8.4f} "
              f"{s.get('R_5_mean', 0):8.4f} "
              f"{s.get('R_7_mean', 0):8.4f} "
              f"{s.get('R_geomean_mean', 0):8.4f} "
              f"{s.get('R_binary_mean', 0):8.4f} "
              f"{s.get('sparsity_mean', 0):8.4f} "
              f"{s.get('kissing_mean', 0):8.1f}")

    print(f"\nThreshold dimension (R_geomean < 0.5): {threshold_dim}")

    print(f"\nCorrelations (Spearman):")
    print(f"  Coherence vs Kissing: r={r_kiss:.4f}, p={p_kiss:.2e}" if r_kiss is not None else "  Coherence vs Kissing: N/A")
    print(f"  Coherence vs Det:     r={r_det:.4f}, p={p_det:.2e}" if r_det is not None else "  Coherence vs Det: N/A")
    print(f"  Coherence vs Dim:     r={r_dim:.4f}, p={p_dim:.2e}" if r_dim is not None else "  Coherence vs Dim: N/A")

    # --- Save results ---
    output = {
        "challenge": "DS7",
        "description": "Lattice Theta Function Phase Coherence",
        "method": "R_P = |mean(exp(2*pi*i * a_n / P))| for P in {2,3,5,7}; geometric mean",
        "n_lattices": len(results_per_lattice),
        "primes_used": PRIMES,
        "dimension_summary": {str(k): v for k, v in dim_summary.items()},
        "threshold_dim_geomean_below_0.5": threshold_dim,
        "correlations": {
            "coherence_vs_kissing": {"spearman_r": r_kiss, "p_value": p_kiss},
            "coherence_vs_det": {"spearman_r": r_det, "p_value": p_det},
            "coherence_vs_dim": {"spearman_r": r_dim, "p_value": p_dim},
        },
        "per_prime_by_dim": {str(k): v for k, v in prime_by_dim.items()},
    }

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
