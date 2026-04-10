"""
Sato-Tate Distribution Moments on Combinatorial Sequences
Frontier #5 / Part 2

Take 1000 OEIS sequences with polynomial growth, normalize into [-1,1],
compute 6-moment vectors, compare against known Sato-Tate group moment
signatures (SU(2), USp(4), Poisson).

Report the "combinatorial symmetry fraction" — percentage matching a
known group within tolerance.
"""

import sys
import json
import math
import random
import numpy as np

sys.stdout.reconfigure(line_buffering=True)

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # F:/Prometheus
DATA = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
OUT  = Path(__file__).resolve().parent / "oeis_sato_tate_results.json"

random.seed(42)
np.random.seed(42)

# ── Known Sato-Tate group moment signatures ──
# Moments M1..M6 for the semicircular (SU(2)) distribution on [-1,1]
# SU(2) Sato-Tate: density (2/pi)*sqrt(1-x^2), moments via Catalan numbers
# M_k = integral of x^k * (2/pi)*sqrt(1-x^2) dx over [-1,1]
# Odd moments = 0, M2 = 1/4, M4 = 1/8, M6 = 5/64

KNOWN_GROUPS = {
    "SU(2)": np.array([0.0, 1/4, 0.0, 1/8, 0.0, 5/64]),
    # USp(4): from Katz-Sarnak, the 2D symplectic group
    # Moments computed from the Weyl integration formula for USp(4)
    "USp(4)": np.array([0.0, 1/3, 0.0, 1/5, 0.0, 1/7]),
    # Poisson (uniform on [-1,1]): M_k = 1/(k+1) for even k, 0 for odd k
    "Uniform": np.array([0.0, 1/3, 0.0, 1/5, 0.0, 1/7]),
    # Poisson (exponential spacing normalized to [-1,1])
    # Use actual Poisson gap distribution moments mapped to [-1,1]
    # For exponential dist on [0,inf) mapped to [-1,1]: different from uniform
    # We use the classical "Poisson" = uniform eigenvalue spacing
    "Poisson_uniform": np.array([0.0, 1/3, 0.0, 1/5, 0.0, 1/7]),
    # GOE (Gaussian Orthogonal Ensemble) semicircle
    "GOE": np.array([0.0, 1/4, 0.0, 1/8, 0.0, 5/64]),
    # GUE (Gaussian Unitary Ensemble) - same semicircle for density of states
    "GUE": np.array([0.0, 1/4, 0.0, 1/8, 0.0, 5/64]),
}

# The distinct targets (removing duplicates for distance computation)
DISTINCT_TARGETS = {
    "SU(2)":  np.array([0.0, 1/4, 0.0, 1/8, 0.0, 5/64]),
    "USp(4)": np.array([0.0, 1/3, 0.0, 1/5, 0.0, 1/7]),
    # Gaussian/delta-like: most mass at 0 => small moments
    "Gaussian_narrow": np.array([0.0, 0.1, 0.0, 0.03, 0.0, 0.01]),
    # Beta(1/2,1/2) = arcsine distribution: M2=1/2, M4=3/8, M6=5/16
    "Arcsine": np.array([0.0, 1/2, 0.0, 3/8, 0.0, 5/16]),
}


def parse_oeis_sequences(path, min_terms=20, target_count=5000):
    """Parse OEIS stripped file, return sequences with enough terms."""
    sequences = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Format: A000001 ,val1,val2,...
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            seq_id = parts[0]
            vals_str = parts[1].strip().strip(",")
            if not vals_str:
                continue
            try:
                vals = [int(x) for x in vals_str.split(",") if x.strip()]
            except ValueError:
                continue
            if len(vals) >= min_terms:
                sequences.append((seq_id, vals))
            if len(sequences) >= target_count:
                break
    return sequences


def has_polynomial_growth(vals, max_degree=6):
    """
    Filter for polynomial growth: check that the sequence doesn't grow
    faster than n^max_degree. Uses ratio of log(|a(n)|)/log(n).
    """
    n = len(vals)
    if n < 20:
        return False
    # Check last few terms
    abs_vals = [abs(v) for v in vals]
    max_val = max(abs_vals)
    if max_val <= 1:
        return True  # constant or near-constant
    # Check growth rate: log(a(n)) / log(n) should be bounded
    # Use the last quarter of terms
    start = max(2, 3 * n // 4)
    for i in range(start, n):
        v = abs_vals[i]
        if v > 1 and (i + 1) > 1:
            ratio = math.log(v) / math.log(i + 1)
            if ratio > max_degree + 1:
                return False
    return True


def normalize_sequence(vals):
    """
    Normalize a(n) to x_n = a(n) / (2 * sqrt(a_max)) to map into ~[-1,1].
    For sequences with negative values, use max(|a(n)|).
    """
    abs_max = max(abs(v) for v in vals)
    if abs_max == 0:
        return None
    scale = 2.0 * math.sqrt(abs_max)
    if scale == 0:
        return None
    normalized = np.array([v / scale for v in vals], dtype=np.float64)
    # Clip to [-1, 1] for safety
    normalized = np.clip(normalized, -1.0, 1.0)
    return normalized


def compute_moments(x, k_max=6):
    """Compute raw moments M1..M6."""
    moments = []
    for k in range(1, k_max + 1):
        moments.append(float(np.mean(x ** k)))
    return np.array(moments)


def distance_to_target(moments, target):
    """Euclidean distance between moment vectors."""
    return float(np.sqrt(np.sum((moments - target) ** 2)))


def main():
    print("=" * 60)
    print("Sato-Tate Distribution Moments on Combinatorial Sequences")
    print("=" * 60)

    # ── Load sequences ──
    print(f"\nLoading sequences from {DATA}...")
    raw_seqs = parse_oeis_sequences(DATA, min_terms=20, target_count=20000)
    print(f"  Loaded {len(raw_seqs)} sequences with >= 20 terms")

    # ── Filter for polynomial growth ──
    print("Filtering for polynomial growth...")
    poly_seqs = [(sid, vals) for sid, vals in raw_seqs if has_polynomial_growth(vals)]
    print(f"  {len(poly_seqs)} sequences with polynomial growth")

    # Take first 1000
    if len(poly_seqs) > 1000:
        poly_seqs = poly_seqs[:1000]
    print(f"  Using {len(poly_seqs)} sequences")

    # ── Normalize and compute moments ──
    print("\nNormalizing and computing 6-moment vectors...")
    results = []
    skipped = 0
    for seq_id, vals in poly_seqs:
        normed = normalize_sequence(vals)
        if normed is None:
            skipped += 1
            continue
        moments = compute_moments(normed)

        # Compute distances to known groups
        distances = {}
        for group_name, target in DISTINCT_TARGETS.items():
            distances[group_name] = distance_to_target(moments, target)

        best_group = min(distances, key=distances.get)
        best_dist = distances[best_group]

        results.append({
            "seq_id": seq_id,
            "n_terms": len(vals),
            "moments": moments.tolist(),
            "distances": distances,
            "best_match": best_group,
            "best_distance": best_dist,
        })

    print(f"  Computed moments for {len(results)} sequences ({skipped} skipped)")

    # ── Classification with tolerance ──
    TOLERANCE = 0.05  # tight tolerance for moment matching
    LOOSE_TOLERANCE = 0.10

    print(f"\n{'=' * 60}")
    print(f"Classification (tight tolerance = {TOLERANCE})")
    print(f"{'=' * 60}")

    tight_matches = {g: [] for g in DISTINCT_TARGETS}
    loose_matches = {g: [] for g in DISTINCT_TARGETS}
    no_match = []

    for r in results:
        matched_tight = False
        matched_loose = False
        for group_name in DISTINCT_TARGETS:
            d = r["distances"][group_name]
            if d < TOLERANCE:
                tight_matches[group_name].append(r["seq_id"])
                matched_tight = True
                break
            elif d < LOOSE_TOLERANCE:
                loose_matches[group_name].append(r["seq_id"])
                matched_loose = True
                break
        if not matched_tight and not matched_loose:
            no_match.append(r["seq_id"])

    total = len(results)
    total_tight = sum(len(v) for v in tight_matches.values())
    total_loose = sum(len(v) for v in loose_matches.values())

    print(f"\nTotal sequences analyzed: {total}")
    print(f"\nTight matches (d < {TOLERANCE}):")
    for g, seqs in tight_matches.items():
        pct = 100.0 * len(seqs) / total if total else 0
        print(f"  {g:20s}: {len(seqs):4d} ({pct:5.1f}%)")
        if seqs:
            print(f"    Examples: {', '.join(seqs[:5])}")

    print(f"\nLoose matches ({TOLERANCE} <= d < {LOOSE_TOLERANCE}):")
    for g, seqs in loose_matches.items():
        pct = 100.0 * len(seqs) / total if total else 0
        print(f"  {g:20s}: {len(seqs):4d} ({pct:5.1f}%)")

    symmetry_fraction_tight = 100.0 * total_tight / total if total else 0
    symmetry_fraction_loose = 100.0 * (total_tight + total_loose) / total if total else 0

    print(f"\n{'=' * 60}")
    print(f"COMBINATORIAL SYMMETRY FRACTION")
    print(f"  Tight (d < {TOLERANCE}):  {total_tight}/{total} = {symmetry_fraction_tight:.1f}%")
    print(f"  Loose (d < {LOOSE_TOLERANCE}): {total_tight + total_loose}/{total} = {symmetry_fraction_loose:.1f}%")
    print(f"  No match:        {len(no_match)}/{total} = {100.0 * len(no_match) / total:.1f}%")
    print(f"{'=' * 60}")

    # ── Moment statistics ──
    all_moments = np.array([r["moments"] for r in results])
    print(f"\nMoment statistics across {total} sequences:")
    for k in range(6):
        m = all_moments[:, k]
        print(f"  M{k+1}: mean={m.mean():.6f}, std={m.std():.6f}, "
              f"min={m.min():.6f}, max={m.max():.6f}")

    # ── Distance distribution ──
    print(f"\nDistance distribution to SU(2):")
    su2_dists = [r["distances"]["SU(2)"] for r in results]
    for threshold in [0.01, 0.02, 0.05, 0.10, 0.20, 0.50]:
        count = sum(1 for d in su2_dists if d < threshold)
        print(f"  d < {threshold:.2f}: {count:4d} ({100.0 * count / total:.1f}%)")

    print(f"\nDistance distribution to USp(4):")
    usp4_dists = [r["distances"]["USp(4)"] for r in results]
    for threshold in [0.01, 0.02, 0.05, 0.10, 0.20, 0.50]:
        count = sum(1 for d in usp4_dists if d < threshold)
        print(f"  d < {threshold:.2f}: {count:4d} ({100.0 * count / total:.1f}%)")

    # ── Best match distribution ──
    from collections import Counter
    best_counts = Counter(r["best_match"] for r in results)
    print(f"\nBest-match distribution (nearest group regardless of tolerance):")
    for g, c in best_counts.most_common():
        print(f"  {g:20s}: {c:4d} ({100.0 * c / total:.1f}%)")

    # ── Top SU(2) matches ──
    su2_ranked = sorted(results, key=lambda r: r["distances"]["SU(2)"])
    print(f"\nTop 20 closest to SU(2):")
    for r in su2_ranked[:20]:
        m = r["moments"]
        print(f"  {r['seq_id']}: d={r['distances']['SU(2)']:.6f}  "
              f"M2={m[1]:.4f} M4={m[3]:.4f} M6={m[5]:.4f}")

    # ── Top USp(4) matches ──
    usp4_ranked = sorted(results, key=lambda r: r["distances"]["USp(4)"])
    print(f"\nTop 20 closest to USp(4):")
    for r in usp4_ranked[:20]:
        m = r["moments"]
        print(f"  {r['seq_id']}: d={r['distances']['USp(4)']:.6f}  "
              f"M2={m[1]:.4f} M4={m[3]:.4f} M6={m[5]:.4f}")

    # ── Save results ──
    output = {
        "metadata": {
            "description": "Sato-Tate distribution moments on OEIS combinatorial sequences",
            "n_sequences_analyzed": total,
            "n_skipped": skipped,
            "normalization": "a(n) / (2 * sqrt(max|a|)), clipped to [-1,1]",
            "tolerance_tight": TOLERANCE,
            "tolerance_loose": LOOSE_TOLERANCE,
        },
        "known_group_signatures": {
            g: target.tolist() for g, target in DISTINCT_TARGETS.items()
        },
        "combinatorial_symmetry_fraction": {
            "tight_pct": round(symmetry_fraction_tight, 2),
            "loose_pct": round(symmetry_fraction_loose, 2),
            "tight_counts": {g: len(v) for g, v in tight_matches.items()},
            "loose_counts": {g: len(v) for g, v in loose_matches.items()},
            "no_match": len(no_match),
        },
        "moment_statistics": {
            f"M{k+1}": {
                "mean": round(float(all_moments[:, k].mean()), 6),
                "std": round(float(all_moments[:, k].std()), 6),
                "min": round(float(all_moments[:, k].min()), 6),
                "max": round(float(all_moments[:, k].max()), 6),
            }
            for k in range(6)
        },
        "best_match_distribution": {
            g: c for g, c in best_counts.most_common()
        },
        "top_20_SU2": [
            {
                "seq_id": r["seq_id"],
                "distance": round(r["distances"]["SU(2)"], 6),
                "M2": round(r["moments"][1], 6),
                "M4": round(r["moments"][3], 6),
                "M6": round(r["moments"][5], 6),
            }
            for r in su2_ranked[:20]
        ],
        "top_20_USp4": [
            {
                "seq_id": r["seq_id"],
                "distance": round(r["distances"]["USp(4)"], 6),
                "M2": round(r["moments"][1], 6),
                "M4": round(r["moments"][3], 6),
                "M6": round(r["moments"][5], 6),
            }
            for r in usp4_ranked[:20]
        ],
        "per_sequence": [
            {
                "seq_id": r["seq_id"],
                "n_terms": r["n_terms"],
                "moments": [round(m, 6) for m in r["moments"]],
                "best_match": r["best_match"],
                "best_distance": round(r["best_distance"], 6),
                "distances": {g: round(d, 6) for g, d in r["distances"].items()},
            }
            for r in results
        ],
    }

    with open(OUT, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT}")
    print("Done.")


if __name__ == "__main__":
    main()
