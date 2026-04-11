#!/usr/bin/env python3
"""
List2 #15: Lattice Gram Matrix Eigenvalue Repulsion

For each lattice in the LMFDB dump (39,293 lattices with Gram matrices):
1. Compute eigenvalues of the Gram matrix
2. Compute normalized nearest-neighbor spacings s_i = (lam_{i+1} - lam_i) / mean_spacing
3. Pool spacings by dimension
4. Compare pooled spacing distribution to GOE (Wigner surmise) and Poisson via KL divergence

GOE Wigner surmise: P(s) = (pi/2) * s * exp(-pi*s^2/4)
Poisson:            P(s) = exp(-s)
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).resolve().parent.parent / "lmfdb_dump" / "lat_lattices.json"
OUT_PATH = Path(__file__).resolve().parent / "lattice_gram_repulsion_results.json"

# ── Load data ─────────────────────────────────────────────────────────────────
print("Loading lattice data...")
with open(DATA_PATH) as f:
    data = json.load(f)

records = data["records"]
print(f"Total records: {len(records)}")

# ── Collect eigenvalues per dimension ─────────────────────────────────────────
dim_eigenvalues = defaultdict(list)  # dim -> list of sorted eigenvalue arrays
skipped = 0

for rec in records:
    gram = rec.get("gram")
    if not gram or not isinstance(gram, list):
        skipped += 1
        continue

    dim = rec["dim"]
    try:
        G = np.array(gram, dtype=float)
        if G.shape[0] != G.shape[1] or G.shape[0] != dim:
            skipped += 1
            continue
        eigs = np.linalg.eigvalsh(G)  # real symmetric -> real eigenvalues, sorted
        dim_eigenvalues[dim].append(eigs)
    except Exception:
        skipped += 1
        continue

print(f"Skipped: {skipped}")
for d in sorted(dim_eigenvalues):
    print(f"  dim {d}: {len(dim_eigenvalues[d])} lattices, {d} eigenvalues each")

# ── Compute normalized nearest-neighbor spacings per dimension ────────────────
def compute_spacings(eig_list):
    """Given list of sorted eigenvalue arrays, return pooled normalized spacings."""
    all_spacings = []
    for eigs in eig_list:
        if len(eigs) < 2:
            continue
        gaps = np.diff(eigs)
        mean_gap = np.mean(gaps)
        if mean_gap > 1e-15:
            all_spacings.extend(gaps / mean_gap)
    return np.array(all_spacings)


# ── Distribution functions ────────────────────────────────────────────────────
def wigner_surmise(s):
    """GOE Wigner surmise P(s) = (pi/2) s exp(-pi s^2 / 4)"""
    return (np.pi / 2) * s * np.exp(-np.pi * s**2 / 4)

def poisson_dist(s):
    """Poisson P(s) = exp(-s)"""
    return np.exp(-s)

def kl_divergence_from_reference(spacings, ref_pdf, n_bins=50, s_max=4.0):
    """
    Compute KL(empirical || reference) using histogram binning.
    Uses midpoint of bins for reference PDF evaluation.
    Adds small epsilon to avoid log(0).
    """
    eps = 1e-12
    bin_edges = np.linspace(0, s_max, n_bins + 1)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    bin_width = bin_edges[1] - bin_edges[0]

    # Empirical histogram (density)
    counts, _ = np.histogram(spacings, bins=bin_edges, density=True)
    p = counts * bin_width  # probability mass per bin
    p = np.clip(p, eps, None)
    p = p / p.sum()  # renormalize

    # Reference distribution
    q = ref_pdf(bin_centers) * bin_width
    q = np.clip(q, eps, None)
    q = q / q.sum()

    # KL divergence
    kl = np.sum(p * np.log(p / q))
    return float(kl)


# ── Main analysis ─────────────────────────────────────────────────────────────
results_by_dim = {}
all_kl_goe = []

MIN_SPACINGS = 20  # need enough spacings for meaningful KL

for dim in sorted(dim_eigenvalues):
    spacings = compute_spacings(dim_eigenvalues[dim])
    n_spacings = len(spacings)
    n_lattices = len(dim_eigenvalues[dim])

    if n_spacings < MIN_SPACINGS:
        print(f"  dim {dim}: only {n_spacings} spacings, skipping KL")
        results_by_dim[str(dim)] = {
            "n_lattices": n_lattices,
            "n_spacings": n_spacings,
            "skipped": True,
            "reason": "too few spacings"
        }
        continue

    kl_goe = kl_divergence_from_reference(spacings, wigner_surmise)
    kl_poisson = kl_divergence_from_reference(spacings, poisson_dist)

    mean_spacing = float(np.mean(spacings))
    std_spacing = float(np.std(spacings))

    # Spacing statistics
    p_zero = float(np.mean(spacings < 0.01))  # fraction near zero (repulsion indicator)

    results_by_dim[str(dim)] = {
        "n_lattices": n_lattices,
        "n_spacings": n_spacings,
        "mean_spacing": round(mean_spacing, 6),
        "std_spacing": round(std_spacing, 6),
        "kl_from_goe": round(kl_goe, 6),
        "kl_from_poisson": round(kl_poisson, 6),
        "closer_to": "GOE" if kl_goe < kl_poisson else "Poisson",
        "p_near_zero": round(p_zero, 6),
    }

    all_kl_goe.append(kl_goe)
    print(f"  dim {dim}: {n_spacings} spacings | KL(GOE)={kl_goe:.4f} KL(Poi)={kl_poisson:.4f} -> {results_by_dim[str(dim)]['closer_to']}")

# ── Summary ───────────────────────────────────────────────────────────────────
mean_kl_goe = float(np.mean(all_kl_goe)) if all_kl_goe else None
median_kl_goe = float(np.median(all_kl_goe)) if all_kl_goe else None

# Also pool ALL spacings across dimensions >= 2
all_spacings_pooled = []
for dim in sorted(dim_eigenvalues):
    if dim >= 2:
        sp = compute_spacings(dim_eigenvalues[dim])
        if len(sp) > 0:
            all_spacings_pooled.extend(sp)

all_spacings_pooled = np.array(all_spacings_pooled)
if len(all_spacings_pooled) > 0:
    global_kl_goe = kl_divergence_from_reference(all_spacings_pooled, wigner_surmise)
    global_kl_poisson = kl_divergence_from_reference(all_spacings_pooled, poisson_dist)
else:
    global_kl_goe = None
    global_kl_poisson = None

summary = {
    "test": "Lattice Gram Matrix Eigenvalue Repulsion",
    "list": "List2 #15",
    "description": "KL divergence of normalized NNS from Gram matrix eigenvalues vs GOE and Poisson",
    "total_lattices": len(records),
    "lattices_with_gram": sum(len(v) for v in dim_eigenvalues.values()),
    "skipped": skipped,
    "dimensions_analyzed": len(all_kl_goe),
    "mean_kl_from_goe": round(mean_kl_goe, 6) if mean_kl_goe is not None else None,
    "median_kl_from_goe": round(median_kl_goe, 6) if median_kl_goe is not None else None,
    "expected_mean_kl_goe": 0.055,
    "global_pooled_kl_goe": round(global_kl_goe, 6) if global_kl_goe is not None else None,
    "global_pooled_kl_poisson": round(global_kl_poisson, 6) if global_kl_poisson is not None else None,
    "global_closer_to": ("GOE" if global_kl_goe < global_kl_poisson else "Poisson") if global_kl_goe is not None else None,
    "verdict": None,
}

# Verdict
if mean_kl_goe is not None:
    if mean_kl_goe < 0.1:
        summary["verdict"] = f"PASS: mean KL from GOE = {mean_kl_goe:.4f} < 0.1 (close to GOE)"
    else:
        summary["verdict"] = f"MIXED: mean KL from GOE = {mean_kl_goe:.4f} (not strongly GOE-like)"

print(f"\n=== Summary ===")
print(f"Mean KL from GOE:   {summary['mean_kl_from_goe']}")
print(f"Median KL from GOE: {summary['median_kl_from_goe']}")
print(f"Global pooled KL(GOE):     {summary['global_pooled_kl_goe']}")
print(f"Global pooled KL(Poisson): {summary['global_pooled_kl_poisson']}")
print(f"Global closer to: {summary['global_closer_to']}")
print(f"Verdict: {summary['verdict']}")

# ── Save ──────────────────────────────────────────────────────────────────────
output = {
    "summary": summary,
    "by_dimension": results_by_dim,
}

# ── Theta-series approach: Hecke eigenvalue proxy ─────────────────────────────
# Theta series coefficients at prime indices are eigenvalues of Hecke operators
# on the space of theta functions. These should show GOE-like repulsion.
print("\n=== Theta-series Hecke eigenvalue approach ===")

def sieve_primes(n):
    """Return list of primes up to n."""
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n + 1, i):
                sieve[j] = False
    return [i for i in range(n + 1) if sieve[i]]

primes = sieve_primes(200)

dim_theta_spacings = defaultdict(list)
theta_skipped = 0

for rec in records:
    ts = rec.get("theta_series")
    if not ts:
        theta_skipped += 1
        continue
    if isinstance(ts, str):
        ts = json.loads(ts)

    dim = rec["dim"]
    # Extract theta coefficients at prime indices
    prime_coeffs = []
    for p in primes:
        if p < len(ts):
            prime_coeffs.append(float(ts[p]))

    if len(prime_coeffs) < 5:
        theta_skipped += 1
        continue

    # These are the "Hecke eigenvalues" - compute NNS
    vals = np.array(prime_coeffs)
    # Sort and compute spacings
    sorted_vals = np.sort(vals)
    # Remove duplicates (many theta coeffs are 0)
    unique_vals = np.unique(sorted_vals)
    if len(unique_vals) < 3:
        continue

    gaps = np.diff(unique_vals)
    mean_gap = np.mean(gaps)
    if mean_gap > 1e-15:
        normalized = gaps / mean_gap
        dim_theta_spacings[dim].extend(normalized)

print(f"Theta-series approach: {theta_skipped} skipped")
theta_results = {}
theta_kl_goe_list = []

for dim in sorted(dim_theta_spacings):
    sp = np.array(dim_theta_spacings[dim])
    if len(sp) < MIN_SPACINGS:
        theta_results[str(dim)] = {"n_spacings": len(sp), "skipped": True}
        continue
    kl_g = kl_divergence_from_reference(sp, wigner_surmise)
    kl_p = kl_divergence_from_reference(sp, poisson_dist)
    theta_results[str(dim)] = {
        "n_spacings": len(sp),
        "kl_from_goe": round(kl_g, 6),
        "kl_from_poisson": round(kl_p, 6),
        "closer_to": "GOE" if kl_g < kl_p else "Poisson",
        "mean_spacing": round(float(np.mean(sp)), 6),
    }
    theta_kl_goe_list.append(kl_g)
    print(f"  dim {dim}: {len(sp)} spacings | KL(GOE)={kl_g:.4f} KL(Poi)={kl_p:.4f} -> {'GOE' if kl_g < kl_p else 'Poisson'}")

theta_mean_kl = float(np.mean(theta_kl_goe_list)) if theta_kl_goe_list else None
print(f"Theta approach mean KL(GOE): {theta_mean_kl}")

output["theta_hecke_approach"] = {
    "description": "Theta series coefficients at prime indices as Hecke eigenvalue proxies",
    "by_dimension": theta_results,
    "mean_kl_from_goe": round(theta_mean_kl, 6) if theta_mean_kl else None,
}

# Update summary with both approaches
summary["theta_mean_kl_from_goe"] = round(theta_mean_kl, 6) if theta_mean_kl else None
output["summary"] = summary

with open(OUT_PATH, "w") as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {OUT_PATH}")
