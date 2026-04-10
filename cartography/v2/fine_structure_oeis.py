#!/usr/bin/env python3
"""
Fine-Structure Constant Neighborhood in OEIS Fingerprint Space.

alpha ≈ 1/137.036 ≈ 0.0072973525693...

1. Extract continued fraction partial quotients and decimal digits as integer sequences.
2. Compute mod-p fingerprints for both at p=2,3,5,7,11.
3. Search full OEIS (394K sequences) for nearest neighbors in fingerprint space.
4. Test whether 137 appears in significantly more OEIS sequences than random 3-digit numbers.
"""

import json
import os
import sys
import time
import numpy as np
from collections import Counter
from pathlib import Path
from mpmath import mp, mpf, floor as mpfloor

# ---------------------------------------------------------------------------
# 1. Alpha representations
# ---------------------------------------------------------------------------

# CODATA 2018 recommended value of the fine-structure constant
ALPHA_INV = mpf("137.035999084")  # 1/alpha
mp.dps = 60  # enough precision for 50+ digits

alpha = 1 / ALPHA_INV

# Continued fraction of 1/alpha (more natural: the integer part is 137)
def continued_fraction(x, n_terms=20):
    """Return first n_terms partial quotients of x."""
    cf = []
    for _ in range(n_terms):
        a = int(mpfloor(x))
        cf.append(a)
        frac = x - a
        if frac < mpf("1e-30"):
            break
        x = 1 / frac
    return cf

cf_alpha_inv = continued_fraction(ALPHA_INV, 20)
print(f"CF(1/alpha) = {cf_alpha_inv}")

# Continued fraction of alpha itself
cf_alpha = continued_fraction(alpha, 20)
print(f"CF(alpha)   = {cf_alpha}")

# Decimal digits of alpha (after the leading 0.)
alpha_str = mp.nstr(alpha, 50, strip_zeros=False)
# alpha ~ 0.0072973525693...
# Extract digits: skip "0." then take digits
raw = alpha_str.replace("0.", "", 1).replace(".", "")
alpha_digits = [int(d) for d in raw[:50]]
print(f"alpha digits (first 50): {alpha_digits}")

# Decimal digits of 1/alpha
alpha_inv_str = mp.nstr(ALPHA_INV, 50, strip_zeros=False)
# 137.035999084...
all_digits_inv = alpha_inv_str.replace(".", "")
alpha_inv_digits = [int(d) for d in all_digits_inv[:50]]
print(f"1/alpha digits (first 50): {alpha_inv_digits}")

# ---------------------------------------------------------------------------
# 2. Mod-p fingerprint computation
# ---------------------------------------------------------------------------

PRIMES = [2, 3, 5, 7, 11]

def mod_p_fingerprint(seq, p, max_terms=30):
    """Compute distribution of seq mod p for first max_terms terms."""
    terms = seq[:max_terms]
    residues = [t % p for t in terms]
    counts = Counter(residues)
    total = len(residues)
    dist = [counts.get(r, 0) / total for r in range(p)]
    return dist

def fingerprint_vector(seq, primes=PRIMES, max_terms=30):
    """Concatenated mod-p distributions -> single vector."""
    vec = []
    for p in primes:
        vec.extend(mod_p_fingerprint(seq, p, max_terms))
    return np.array(vec, dtype=np.float64)

# Our target fingerprints
targets = {
    "cf_alpha_inv": cf_alpha_inv,
    "cf_alpha": cf_alpha,
    "alpha_digits": alpha_digits,
    "alpha_inv_digits": alpha_inv_digits,
}

target_fps = {}
for name, seq in targets.items():
    fp = fingerprint_vector(seq)
    target_fps[name] = fp
    print(f"\nFingerprint [{name}] (dim={len(fp)}):")
    offset = 0
    for p in PRIMES:
        dist = fp[offset:offset+p]
        print(f"  mod {p}: {[f'{x:.3f}' for x in dist]}")
        offset += p

# ---------------------------------------------------------------------------
# 3. Load OEIS and compute fingerprints for all sequences
# ---------------------------------------------------------------------------

OEIS_PATH = os.path.join(os.path.dirname(__file__), "..", "oeis", "data", "stripped_new.txt")

def load_oeis(path, min_terms=10):
    """Load OEIS sequences, keeping only those with >= min_terms integer terms."""
    seqs = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            aid = parts[0]
            raw_terms = parts[1].strip().strip(",").split(",")
            terms = []
            for t in raw_terms:
                t = t.strip()
                if t == "" or t == "":
                    continue
                try:
                    terms.append(int(t))
                except ValueError:
                    continue
            if len(terms) >= min_terms:
                seqs[aid] = terms
    return seqs

print("\nLoading OEIS...")
t0 = time.time()
oeis = load_oeis(OEIS_PATH, min_terms=10)
print(f"Loaded {len(oeis)} sequences with >= 10 terms in {time.time()-t0:.1f}s")

# Compute fingerprints for all OEIS sequences
print("Computing OEIS fingerprints...")
t0 = time.time()
oeis_fps = {}
for aid, terms in oeis.items():
    oeis_fps[aid] = fingerprint_vector(terms)
elapsed = time.time() - t0
print(f"Computed {len(oeis_fps)} fingerprints in {elapsed:.1f}s")

# ---------------------------------------------------------------------------
# 4. Find nearest neighbors
# ---------------------------------------------------------------------------

def find_nearest(target_fp, oeis_fps, top_k=20):
    """Find top_k nearest OEIS sequences by L2 distance in fingerprint space."""
    distances = []
    for aid, fp in oeis_fps.items():
        d = np.linalg.norm(target_fp - fp)
        distances.append((d, aid))
    distances.sort()
    return distances[:top_k]

print("\n" + "="*70)
print("NEAREST NEIGHBORS IN FINGERPRINT SPACE")
print("="*70)

nn_results = {}
for name, fp in target_fps.items():
    neighbors = find_nearest(fp, oeis_fps, top_k=20)
    nn_results[name] = [(d, aid) for d, aid in neighbors]
    print(f"\n--- {name} ---")
    for rank, (d, aid) in enumerate(neighbors[:10], 1):
        terms_preview = oeis[aid][:8]
        print(f"  {rank:2d}. {aid}  dist={d:.6f}  terms={terms_preview}")

# ---------------------------------------------------------------------------
# 5. Null model: how close are random fingerprint distances?
# ---------------------------------------------------------------------------

print("\n" + "="*70)
print("NULL MODEL: Random fingerprint distances")
print("="*70)

# Sample random pairs to establish baseline distances
rng = np.random.default_rng(42)
all_aids = list(oeis_fps.keys())
n_sample = 50000
d_random = []
for _ in range(n_sample):
    i, j = rng.choice(len(all_aids), size=2, replace=False)
    d = np.linalg.norm(oeis_fps[all_aids[i]] - oeis_fps[all_aids[j]])
    d_random.append(d)
d_random = np.array(d_random)

print(f"Random pair distances (n={n_sample}):")
print(f"  mean={d_random.mean():.4f}  std={d_random.std():.4f}")
print(f"  p5={np.percentile(d_random, 5):.4f}  p50={np.percentile(d_random, 50):.4f}  p95={np.percentile(d_random, 95):.4f}")

# For each target, what percentile is the nearest neighbor?
for name, fp in target_fps.items():
    best_d = nn_results[name][0][0]
    pct = (d_random < best_d).mean() * 100
    print(f"  {name}: nearest d={best_d:.6f}, percentile={pct:.2f}% of random pairs")

# ---------------------------------------------------------------------------
# 6. 137-frequency enrichment test
# ---------------------------------------------------------------------------

print("\n" + "="*70)
print("137-FREQUENCY ENRICHMENT TEST")
print("="*70)

def count_seqs_containing(oeis, value):
    """Count how many sequences contain the given value as a term."""
    count = 0
    for terms in oeis.values():
        if value in terms:
            count += 1
    return count

# Count sequences containing 137
n_137 = count_seqs_containing(oeis, 137)
total = len(oeis)
print(f"Sequences containing 137: {n_137} / {total} = {n_137/total*100:.2f}%")

# Compare with other 3-digit numbers (100-999, sample)
test_numbers = list(range(100, 200)) + list(range(200, 300, 5)) + list(range(300, 999, 10))
# Also include specific controls
controls = [127, 131, 139, 149, 151, 157, 163, 167, 173, 179,  # nearby primes
            100, 128, 200, 256, 500, 512, 999,  # round/power-of-2
            113, 142, 155, 168, 183, 197, 211, 223]  # arbitrary
test_numbers = sorted(set(test_numbers + controls))

print(f"Testing {len(test_numbers)} comparison numbers...")
freq_map = {}
for v in test_numbers:
    freq_map[v] = count_seqs_containing(oeis, v)

# Statistics
freqs = np.array(list(freq_map.values()))
mean_freq = freqs.mean()
std_freq = freqs.std()
z_137 = (n_137 - mean_freq) / std_freq if std_freq > 0 else 0

print(f"\n3-digit number frequency stats (n={len(test_numbers)}):")
print(f"  mean={mean_freq:.1f}  std={std_freq:.1f}  min={freqs.min()}  max={freqs.max()}")
print(f"  137 count={n_137}  z-score={z_137:.2f}")

# Where does 137 rank?
sorted_freqs = sorted(freq_map.items(), key=lambda x: -x[1])
rank_137 = next(i for i, (v, _) in enumerate(sorted_freqs, 1) if v == 137)
print(f"  137 rank: {rank_137} / {len(sorted_freqs)}")

# Show top 20
print("\nTop 20 most-appearing 3-digit numbers:")
for rank, (v, c) in enumerate(sorted_freqs[:20], 1):
    marker = " <-- 137" if v == 137 else ""
    print(f"  {rank:2d}. {v:4d}: {c:6d} sequences{marker}")

# Show neighbors of 137
print("\nNumbers near 137:")
for v in [130, 131, 133, 135, 136, 137, 138, 139, 140, 141, 143, 145]:
    if v in freq_map:
        print(f"  {v}: {freq_map[v]} sequences")

# ---------------------------------------------------------------------------
# 7. Structural match analysis
# ---------------------------------------------------------------------------

print("\n" + "="*70)
print("STRUCTURAL MATCH ANALYSIS")
print("="*70)

# For top neighbors, check if they have any known connection to physics/constants
# Load OEIS names if available
names_path = os.path.join(os.path.dirname(__file__), "..", "oeis", "data", "oeis_names.json")
oeis_names = {}
if os.path.exists(names_path):
    with open(names_path, encoding="utf-8") as f:
        oeis_names = json.load(f)

for name in target_fps:
    print(f"\n--- Top 10 neighbors of {name} (with names) ---")
    for rank, (d, aid) in enumerate(nn_results[name][:10], 1):
        seq_name = oeis_names.get(aid, oeis_names.get(aid.replace("A", ""), "???"))
        print(f"  {rank:2d}. {aid} (d={d:.4f}): {seq_name}")

# ---------------------------------------------------------------------------
# 8. Save results
# ---------------------------------------------------------------------------

results = {
    "description": "Fine-structure constant neighborhood in OEIS fingerprint space",
    "alpha": str(alpha),
    "alpha_inv": str(ALPHA_INV),
    "representations": {
        "cf_alpha_inv": cf_alpha_inv,
        "cf_alpha": cf_alpha,
        "alpha_digits": alpha_digits[:30],
        "alpha_inv_digits": alpha_inv_digits[:30],
    },
    "fingerprints": {
        name: {
            f"mod_{p}": mod_p_fingerprint(targets[name], p)
            for p in PRIMES
        }
        for name in targets
    },
    "nearest_neighbors": {
        name: [
            {"rank": i+1, "oeis_id": aid, "distance": round(d, 6),
             "terms_preview": oeis[aid][:10],
             "name": oeis_names.get(aid, "")}
            for i, (d, aid) in enumerate(nn_results[name][:20])
        ]
        for name in nn_results
    },
    "null_model": {
        "n_random_pairs": n_sample,
        "mean_distance": round(float(d_random.mean()), 4),
        "std_distance": round(float(d_random.std()), 4),
        "p5": round(float(np.percentile(d_random, 5)), 4),
        "p50": round(float(np.percentile(d_random, 50)), 4),
        "p95": round(float(np.percentile(d_random, 95)), 4),
        "target_percentiles": {
            name: round(float((d_random < nn_results[name][0][0]).mean() * 100), 2)
            for name in nn_results
        }
    },
    "enrichment_137": {
        "count_137": n_137,
        "total_sequences": total,
        "fraction": round(n_137 / total, 6),
        "comparison_mean": round(float(mean_freq), 1),
        "comparison_std": round(float(std_freq), 1),
        "z_score": round(float(z_137), 2),
        "rank_among_tested": rank_137,
        "n_tested": len(test_numbers),
        "top_20": [{"value": int(v), "count": int(c)} for v, c in sorted_freqs[:20]],
    },
    "verdict": {}
}

# Verdicts
nn_verdicts = {}
for name in nn_results:
    best_d = nn_results[name][0][0]
    pct = (d_random < best_d).mean() * 100
    if pct < 1:
        nn_verdicts[name] = f"NOTABLE: nearest neighbor at d={best_d:.4f} is below 1st percentile of random pairs"
    elif pct < 5:
        nn_verdicts[name] = f"INTERESTING: nearest neighbor at d={best_d:.4f} is below 5th percentile"
    else:
        nn_verdicts[name] = f"NULL: nearest neighbor at d={best_d:.4f} is at {pct:.1f}th percentile (not unusual)"

results["verdict"]["nearest_neighbors"] = nn_verdicts

if abs(z_137) > 3:
    results["verdict"]["enrichment_137"] = f"SIGNIFICANT: z={z_137:.2f}, 137 appears in {n_137} sequences vs mean {mean_freq:.0f}"
elif abs(z_137) > 2:
    results["verdict"]["enrichment_137"] = f"MARGINAL: z={z_137:.2f}, 137 appears in {n_137} sequences vs mean {mean_freq:.0f}"
else:
    results["verdict"]["enrichment_137"] = f"NULL: z={z_137:.2f}, 137 frequency is unremarkable vs other 3-digit numbers"

out_path = os.path.join(os.path.dirname(__file__), "fine_structure_oeis_results.json")
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {out_path}")

print("\n" + "="*70)
print("VERDICTS")
print("="*70)
for k, v in results["verdict"].items():
    if isinstance(v, dict):
        for k2, v2 in v.items():
            print(f"  {k}.{k2}: {v2}")
    else:
        print(f"  {k}: {v}")
