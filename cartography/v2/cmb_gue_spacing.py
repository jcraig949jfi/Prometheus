"""
CMB Acoustic Peak Spacing vs GUE/Poisson distributions.

Computes normalized nearest-neighbor spacings of local maxima and minima
in the Planck CMB TT power spectrum, then measures KL divergence from
GUE (Wigner surmise) and Poisson distributions.

Honest caveat: ~8-10 extrema yield ~7-9 spacings — far too few for
reliable distributional inference. Results reported for completeness.
"""

import json
import math
import os
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "physics" / "data" / "planck" / "cmb_tt_spectrum.json"
OUT_PATH = Path(__file__).resolve().parent / "cmb_gue_spacing_results.json"


def load_cmb():
    with open(DATA_PATH) as f:
        data = json.load(f)
    ells = np.array([b["ell"] for b in data["bins"]])
    dls = np.array([b["Dl"] for b in data["bins"]])
    return ells, dls


def find_extrema(ells, dls):
    """Find local maxima and minima (interior points only)."""
    maxima_idx = []
    minima_idx = []
    for i in range(1, len(dls) - 1):
        if dls[i] > dls[i - 1] and dls[i] > dls[i + 1]:
            maxima_idx.append(i)
        elif dls[i] < dls[i - 1] and dls[i] < dls[i + 1]:
            minima_idx.append(i)
    return maxima_idx, minima_idx


def normalized_spacings(ells, indices):
    """Compute nearest-neighbor spacings in ell, normalized by mean spacing."""
    if len(indices) < 2:
        return np.array([])
    positions = ells[indices]
    spacings = np.diff(positions)
    mean_spacing = np.mean(spacings)
    if mean_spacing == 0:
        return spacings
    return spacings / mean_spacing


def poisson_pdf(s):
    """P(s) = exp(-s)"""
    return np.exp(-s)


def gue_wigner_pdf(s):
    """Wigner surmise for GUE: P(s) = (32/pi^2) * s^2 * exp(-4s^2/pi)"""
    return (32.0 / math.pi**2) * s**2 * np.exp(-4.0 * s**2 / math.pi)


def kl_divergence_from_sample(spacings, ref_pdf, n_bins=15, s_max=4.0):
    """
    Estimate KL(empirical || reference) using histogram binning.

    D_KL = sum_i p_i * log(p_i / q_i) where p is empirical, q is reference.
    Bins with zero empirical count contribute 0. Bins with zero reference
    density are skipped (would be infinite).
    """
    if len(spacings) < 2:
        return float("nan"), {}

    edges = np.linspace(0, s_max, n_bins + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    bin_width = edges[1] - edges[0]

    counts, _ = np.histogram(spacings, bins=edges)
    p = counts / (np.sum(counts) * bin_width)  # empirical density

    q = ref_pdf(centers)  # reference density

    kl = 0.0
    for pi, qi in zip(p, q):
        if pi > 0 and qi > 0:
            kl += pi * math.log(pi / qi) * bin_width

    return kl, {"centers": centers.tolist(), "empirical_density": p.tolist(),
                "reference_density": q.tolist()}


def main():
    ells, dls = load_cmb()
    maxima_idx, minima_idx = find_extrema(ells, dls)
    all_extrema_idx = sorted(set(maxima_idx + minima_idx))

    # Compute spacings for each group
    results = {}
    for label, indices in [("maxima", maxima_idx),
                           ("minima", minima_idx),
                           ("all_extrema", all_extrema_idx)]:
        s = normalized_spacings(ells, indices)
        n_extrema = len(indices)
        n_spacings = len(s)

        kl_poisson, hist_poisson = kl_divergence_from_sample(s, poisson_pdf)
        kl_gue, hist_gue = kl_divergence_from_sample(s, gue_wigner_pdf)

        if not math.isnan(kl_poisson) and not math.isnan(kl_gue):
            better_fit = "Poisson" if kl_poisson < kl_gue else "GUE"
        else:
            better_fit = "insufficient_data"

        positions = ells[indices].tolist() if len(indices) > 0 else []
        dl_values = dls[indices].tolist() if len(indices) > 0 else []

        results[label] = {
            "n_extrema": n_extrema,
            "n_spacings": n_spacings,
            "ell_positions": [round(x, 2) for x in positions],
            "Dl_values": [round(x, 2) for x in dl_values],
            "raw_spacings_ell": np.diff(ells[indices]).tolist() if n_spacings > 0 else [],
            "normalized_spacings": s.tolist(),
            "mean_spacing_ell": float(np.mean(np.diff(ells[indices]))) if n_spacings > 0 else None,
            "std_spacing_normalized": float(np.std(s)) if n_spacings > 0 else None,
            "kl_divergence_poisson": round(kl_poisson, 6) if not math.isnan(kl_poisson) else None,
            "kl_divergence_gue": round(kl_gue, 6) if not math.isnan(kl_gue) else None,
            "better_fit": better_fit,
        }

        print(f"\n=== {label.upper()} ===")
        print(f"  Count: {n_extrema} extrema -> {n_spacings} spacings")
        print(f"  ell positions: {[round(x, 1) for x in positions]}")
        if n_spacings > 0:
            print(f"  Mean spacing (ell): {np.mean(np.diff(ells[indices])):.1f}")
            print(f"  Normalized spacings: {[round(x, 3) for x in s]}")
            print(f"  KL(emp || Poisson) = {kl_poisson:.6f}")
            print(f"  KL(emp || GUE)     = {kl_gue:.6f}")
            print(f"  Better fit: {better_fit}")

    output = {
        "analysis": "CMB acoustic peak spacing vs GUE/Poisson",
        "source": "Planck Release 3.01, CMB TT power spectrum (83 bins)",
        "method": "Local extrema detection, normalized nearest-neighbor spacings, KL divergence",
        "caveat": "With only ~8-10 acoustic peaks in 83 bins, statistics are severely limited. "
                  "KL divergence estimates are unreliable at this sample size. "
                  "Results are directional only, not statistically significant.",
        "poisson_pdf": "P(s) = exp(-s)",
        "gue_wigner_pdf": "P(s) = (32/pi^2) * s^2 * exp(-4*s^2/pi)",
        "results": results,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
