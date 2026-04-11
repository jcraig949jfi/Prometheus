"""
Hecke-Lattice Theta Resonance
==============================

Correlates EC Hecke eigenvalue vectors with lattice theta series
coefficients after aligning by prime index.

EC side:  a_p / (2*sqrt(p)) for primes p = 2,3,5,...,97  (25 values)
Lattice:  theta_p / mean(theta_primes) for same primes    (25 values)
Metric:   cosine similarity between all EC-lattice pairs   (sampled 1000x1000)

Null model: permuted lattice vectors (column-wise shuffle).

Expected peak alignment: ~0.08-0.15 (weak but structured).
"""

import json
import math
import os
import sys
import time
import numpy as np
from pathlib import Path

# ---------- paths ----------
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[0]  # cartography/
CHARON_DB = ROOT.parent / "charon" / "data" / "charon.duckdb"
LATTICE_PATH = ROOT / "lmfdb_dump" / "lat_lattices.json"
OUT_JSON = SCRIPT_DIR / "hecke_theta_resonance_results.json"

# ---------- primes up to 97 ----------
PRIMES_25 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
             31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
             73, 79, 83, 89, 97]
assert len(PRIMES_25) == 25

SQRT_PRIMES = np.array([math.sqrt(p) for p in PRIMES_25])

# sampling
N_EC_SAMPLE = 1000
N_LAT_SAMPLE = 1000
N_NULL_TRIALS = 20
RNG = np.random.default_rng(42)


# ------------------------------------------------------------------ #
#  Data loading                                                       #
# ------------------------------------------------------------------ #
def load_ec_vectors():
    """Load EC Hecke eigenvalue vectors from DuckDB, normalized by 2*sqrt(p)."""
    import duckdb
    db = duckdb.connect(str(CHARON_DB), read_only=True)
    rows = db.execute("""
        SELECT lmfdb_iso, aplist
        FROM elliptic_curves
        WHERE aplist IS NOT NULL AND len(aplist) >= 25
    """).fetchall()
    db.close()

    # Deduplicate by isogeny class (all curves in a class share aplist)
    seen = set()
    vectors = []
    labels = []
    for iso, aplist in rows:
        if iso in seen:
            continue
        seen.add(iso)
        ap = np.array(aplist[:25], dtype=np.float64)
        # Normalize: a_p / (2 * sqrt(p))
        normed = ap / (2.0 * SQRT_PRIMES)
        vectors.append(normed)
        labels.append(iso)

    print(f"  EC: {len(vectors)} isogeny classes loaded")
    return np.array(vectors), labels


def load_lattice_vectors():
    """Load lattice theta series vectors at prime indices, normalized by mean."""
    with open(LATTICE_PATH) as f:
        obj = json.loads(f.readline())

    records = obj["records"]
    vectors = []
    labels = []
    skipped = 0

    for rec in records:
        theta = rec.get("theta_series", [])
        if len(theta) < 98:  # need index up to 97
            skipped += 1
            continue

        # Extract theta coefficients at prime indices
        theta_primes = np.array([theta[p] for p in PRIMES_25], dtype=np.float64)

        # Skip all-zero vectors (can't normalize)
        if np.all(theta_primes == 0):
            skipped += 1
            continue

        # Normalize by mean of nonzero values to preserve shape
        mean_val = np.mean(np.abs(theta_primes[theta_primes != 0]))
        if mean_val == 0:
            skipped += 1
            continue
        normed = theta_primes / mean_val
        vectors.append(normed)
        labels.append(rec.get("label", rec.get("id", "?")))

    print(f"  Lattices: {len(vectors)} loaded, {skipped} skipped")
    return np.array(vectors), labels


# ------------------------------------------------------------------ #
#  Core computation                                                   #
# ------------------------------------------------------------------ #
def cosine_similarity_matrix(A, B):
    """Cosine similarity between rows of A and rows of B."""
    # Normalize rows
    A_norm = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-12)
    B_norm = B / (np.linalg.norm(B, axis=1, keepdims=True) + 1e-12)
    return A_norm @ B_norm.T


def compute_max_cosine_stats(ec_vecs, lat_vecs, n_ec, n_lat):
    """Sample n_ec x n_lat pairs, compute max cosine similarity per EC."""
    ec_idx = RNG.choice(len(ec_vecs), size=min(n_ec, len(ec_vecs)), replace=False)
    lat_idx = RNG.choice(len(lat_vecs), size=min(n_lat, len(lat_vecs)), replace=False)

    ec_sample = ec_vecs[ec_idx]
    lat_sample = lat_vecs[lat_idx]

    sim = cosine_similarity_matrix(ec_sample, lat_sample)

    max_per_ec = np.max(sim, axis=1)
    max_per_lat = np.max(sim, axis=0)
    mean_sim = np.mean(sim)

    return {
        "max_per_ec_mean": float(np.mean(max_per_ec)),
        "max_per_ec_median": float(np.median(max_per_ec)),
        "max_per_ec_std": float(np.std(max_per_ec)),
        "max_per_ec_95pct": float(np.percentile(max_per_ec, 95)),
        "max_per_lat_mean": float(np.mean(max_per_lat)),
        "mean_similarity": float(mean_sim),
        "global_max": float(np.max(sim)),
        "n_ec_sampled": int(len(ec_idx)),
        "n_lat_sampled": int(len(lat_idx)),
    }, sim, ec_idx, lat_idx


def compute_null(ec_vecs, lat_vecs, n_ec, n_lat, n_trials):
    """Null model: column-wise permutation of lattice vectors."""
    ec_idx = RNG.choice(len(ec_vecs), size=min(n_ec, len(ec_vecs)), replace=False)
    lat_idx = RNG.choice(len(lat_vecs), size=min(n_lat, len(lat_vecs)), replace=False)

    ec_sample = ec_vecs[ec_idx]
    lat_sample = lat_vecs[lat_idx].copy()

    null_maxes = []
    for _ in range(n_trials):
        shuffled = lat_sample.copy()
        for col in range(shuffled.shape[1]):
            RNG.shuffle(shuffled[:, col])
        sim = cosine_similarity_matrix(ec_sample, shuffled)
        null_maxes.append(float(np.mean(np.max(sim, axis=1))))

    return {
        "null_max_per_ec_mean": float(np.mean(null_maxes)),
        "null_max_per_ec_std": float(np.std(null_maxes)),
        "null_trials": n_trials,
        "null_values": null_maxes,
    }


def find_top_pairs(sim, ec_labels, lat_labels, ec_idx, lat_idx, top_k=20):
    """Find top-k most similar EC-lattice pairs."""
    flat = sim.flatten()
    top_indices = np.argsort(flat)[-top_k:][::-1]
    rows, cols = np.unravel_index(top_indices, sim.shape)

    pairs = []
    for r, c in zip(rows, cols):
        pairs.append({
            "ec_label": ec_labels[ec_idx[r]],
            "lat_label": str(lat_labels[lat_idx[c]]),
            "cosine_sim": float(sim[r, c]),
        })
    return pairs


# ------------------------------------------------------------------ #
#  Distribution analysis                                              #
# ------------------------------------------------------------------ #
def analyze_distribution(sim):
    """Analyze the full similarity matrix distribution."""
    flat = sim.flatten()
    return {
        "mean": float(np.mean(flat)),
        "std": float(np.std(flat)),
        "skew": float(np.mean(((flat - np.mean(flat)) / (np.std(flat) + 1e-12)) ** 3)),
        "kurtosis": float(np.mean(((flat - np.mean(flat)) / (np.std(flat) + 1e-12)) ** 4) - 3),
        "min": float(np.min(flat)),
        "max": float(np.max(flat)),
        "pct_above_01": float(np.mean(flat > 0.1) * 100),
        "pct_above_02": float(np.mean(flat > 0.2) * 100),
        "pct_above_03": float(np.mean(flat > 0.3) * 100),
        "pct_above_05": float(np.mean(flat > 0.5) * 100),
        "histogram_bins": [float(x) for x in np.linspace(-1, 1, 41)],
        "histogram_counts": [int(x) for x in np.histogram(flat, bins=np.linspace(-1, 1, 41))[0]],
    }


# ------------------------------------------------------------------ #
#  Main                                                               #
# ------------------------------------------------------------------ #
def main():
    t0 = time.time()
    print("Hecke-Lattice Theta Resonance")
    print("=" * 50)

    # 1. Load data
    print("\n[1] Loading data...")
    ec_vecs, ec_labels = load_ec_vectors()
    lat_vecs, lat_labels = load_lattice_vectors()

    # 2. Real similarity
    print("\n[2] Computing cosine similarity (sampled)...")
    real_stats, sim, ec_idx, lat_idx = compute_max_cosine_stats(
        ec_vecs, lat_vecs, N_EC_SAMPLE, N_LAT_SAMPLE
    )
    print(f"  Max-per-EC mean:   {real_stats['max_per_ec_mean']:.4f}")
    print(f"  Max-per-EC median: {real_stats['max_per_ec_median']:.4f}")
    print(f"  Global max:        {real_stats['global_max']:.4f}")
    print(f"  Mean similarity:   {real_stats['mean_similarity']:.4f}")

    # 3. Null model
    print(f"\n[3] Null model ({N_NULL_TRIALS} trials, column-permuted)...")
    null_stats = compute_null(ec_vecs, lat_vecs, N_EC_SAMPLE, N_LAT_SAMPLE, N_NULL_TRIALS)
    print(f"  Null max-per-EC mean: {null_stats['null_max_per_ec_mean']:.4f} +/- {null_stats['null_max_per_ec_std']:.4f}")

    # 4. Effect size
    delta = real_stats["max_per_ec_mean"] - null_stats["null_max_per_ec_mean"]
    effect_ratio = delta / (null_stats["null_max_per_ec_std"] + 1e-12)
    print(f"\n  Delta (real - null): {delta:.4f}")
    print(f"  Effect size (delta/null_std): {effect_ratio:.2f}")

    # 5. Distribution analysis
    print("\n[4] Distribution analysis...")
    dist = analyze_distribution(sim)
    print(f"  Similarity mean={dist['mean']:.4f}, std={dist['std']:.4f}")
    print(f"  >0.1: {dist['pct_above_01']:.1f}%, >0.2: {dist['pct_above_02']:.1f}%, "
          f">0.3: {dist['pct_above_03']:.1f}%, >0.5: {dist['pct_above_05']:.1f}%")

    # 6. Top pairs
    print("\n[5] Top EC-lattice pairs...")
    top_pairs = find_top_pairs(sim, ec_labels, lat_labels, ec_idx, lat_idx, top_k=20)
    for i, p in enumerate(top_pairs[:5]):
        print(f"  #{i+1}: {p['ec_label']} <-> {p['lat_label']}  cos={p['cosine_sim']:.4f}")

    # 7. Assess
    in_expected = 0.05 <= real_stats["max_per_ec_mean"] <= 0.25
    verdict = "EXPECTED_RANGE" if in_expected else "OUTSIDE_RANGE"
    significant = effect_ratio > 2.0

    elapsed = time.time() - t0
    print(f"\n{'=' * 50}")
    print(f"Verdict: {verdict} (max-per-EC mean = {real_stats['max_per_ec_mean']:.4f})")
    print(f"Significant vs null: {'YES' if significant else 'NO'} (effect ratio = {effect_ratio:.2f})")
    print(f"Elapsed: {elapsed:.1f}s")

    # 8. Save
    results = {
        "experiment": "hecke_theta_resonance",
        "description": "Cosine similarity between EC Hecke eigenvalue vectors "
                       "and lattice theta series coefficients at prime indices",
        "normalization": {
            "ec": "a_p / (2 * sqrt(p)) — Hasse bound normalization to [-1,1]",
            "lattice": "theta_p / mean(|theta_primes|) — shape-preserving normalization",
        },
        "primes": PRIMES_25,
        "sample_size": {
            "ec_total": len(ec_vecs),
            "lat_total": len(lat_vecs),
            "ec_sampled": real_stats["n_ec_sampled"],
            "lat_sampled": real_stats["n_lat_sampled"],
        },
        "real_stats": real_stats,
        "null_stats": null_stats,
        "effect_size": {
            "delta": float(delta),
            "effect_ratio_sigma": float(effect_ratio),
            "significant": significant,
        },
        "distribution": dist,
        "top_pairs": top_pairs,
        "verdict": verdict,
        "elapsed_seconds": round(elapsed, 1),
    }

    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {OUT_JSON}")


if __name__ == "__main__":
    main()
