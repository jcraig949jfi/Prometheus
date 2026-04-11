"""
Cross-Domain: Number Field Discriminants as OEIS Sequences
==========================================================
Do NF discriminant sequences (sorted |disc| per degree) appear in OEIS?
Tests whether the arithmetic of discriminants has combinatorial structure.

Data:
  - NF: cartography/number_fields/data/number_fields.json (9K fields)
  - OEIS: cartography/oeis/data/stripped_new.txt (394K sequences)

Approach:
  1. For each degree d=2,3,4,5: extract sorted unique |disc| -> sequence
  2. Search OEIS for substring matches on first 15 terms
  3. Compute mod-p fingerprints of disc sequences, compare to OEIS fingerprint distribution
  4. MI between disc fingerprints and OEIS fingerprints
  5. Null test via random permutation
"""

import json
import os
import sys
import numpy as np

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

# ── 1. Load NF data ──────────────────────────────────────────────────────────

nf_path = BASE / "number_fields" / "data" / "number_fields.json"
with open(nf_path) as f:
    nf_data = json.load(f)

print(f"Loaded {len(nf_data)} number fields")

# Extract sorted unique |disc| per degree
disc_by_degree = defaultdict(set)
for rec in nf_data:
    d = rec["degree"]
    disc = int(rec["disc_abs"])
    if disc > 0:
        disc_by_degree[d].add(disc)

disc_sequences = {}
for d in [2, 3, 4, 5]:
    seq = sorted(disc_by_degree[d])
    disc_sequences[d] = seq
    print(f"  degree {d}: {len(seq)} unique |disc| values, first 10: {seq[:10]}")

# ── 2. Load OEIS stripped data ────────────────────────────────────────────────

oeis_path = BASE / "oeis" / "data" / "stripped_new.txt"
print(f"\nLoading OEIS from {oeis_path}...")

oeis_seqs = {}  # A-number -> list of ints
with open(oeis_path, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Format: A000001 ,0,1,1,1,2,...,
        parts = line.split(" ", 1)
        if len(parts) < 2:
            continue
        a_num = parts[0]
        terms_str = parts[1].strip().strip(",")
        if not terms_str:
            continue
        try:
            terms = [int(x) for x in terms_str.split(",") if x.strip()]
            if len(terms) >= 5:
                oeis_seqs[a_num] = terms
        except ValueError:
            continue

print(f"Loaded {len(oeis_seqs)} OEIS sequences with >= 5 terms")

# ── 3. Exact subsequence search ──────────────────────────────────────────────

def find_oeis_matches(disc_seq, n_terms=15, min_match=8):
    """Search OEIS for sequences whose first terms contain disc_seq prefix."""
    query = disc_seq[:n_terms]
    query_str = ",".join(str(x) for x in query)

    matches = []
    # Also build a set-based lookup for the first few terms
    query_set = set(query)

    for a_num, terms in oeis_seqs.items():
        # Check if query appears as a contiguous subsequence
        terms_str = ",".join(str(x) for x in terms)
        if query_str in terms_str:
            matches.append({"id": a_num, "type": "exact_substring", "matched_terms": n_terms})
            continue

        # Partial: check overlap of first N terms
        oeis_first = terms[:n_terms]
        overlap = len(set(oeis_first) & query_set)
        if overlap >= min_match:
            matches.append({
                "id": a_num,
                "type": "set_overlap",
                "overlap": overlap,
                "oeis_first": oeis_first[:10]
            })

    return matches

print("\n── Searching OEIS for discriminant sequence matches ──")
all_matches = {}
for d in [2, 3, 4, 5]:
    seq = disc_sequences[d]
    if len(seq) < 15:
        print(f"  degree {d}: only {len(seq)} terms, skipping exact search")
        # Still try with what we have
        n_use = min(len(seq), 15)
        matches = find_oeis_matches(seq, n_terms=n_use, min_match=max(4, n_use // 2))
    else:
        matches = find_oeis_matches(seq, n_terms=15, min_match=8)

    exact = [m for m in matches if m["type"] == "exact_substring"]
    overlap = [m for m in matches if m["type"] == "set_overlap"]
    print(f"  degree {d}: {len(exact)} exact substring matches, {len(overlap)} set-overlap matches")
    if exact:
        for m in exact[:5]:
            print(f"    EXACT: {m['id']}")
    if overlap:
        for m in overlap[:3]:
            print(f"    OVERLAP: {m['id']} ({m['overlap']} terms)")

    all_matches[d] = {"exact": exact[:20], "set_overlap": overlap[:20]}

# Known OEIS sequences for discriminants:
# A006557: discriminants of quadratic fields (imaginary)
# A003657: fundamental discriminants of imaginary quadratic fields
# A003658: fundamental discriminants of real quadratic fields
known_disc_seqs = ["A006557", "A003657", "A003658", "A037449", "A028892"]
print("\n── Checking known discriminant OEIS sequences ──")
for a_num in known_disc_seqs:
    if a_num in oeis_seqs:
        terms = oeis_seqs[a_num][:15]
        print(f"  {a_num}: {terms}")

# ── 4. Mod-p fingerprints ────────────────────────────────────────────────────

PRIMES = [2, 3, 5, 7, 11, 13]

def modp_fingerprint(seq, primes=PRIMES, n_terms=30):
    """Compute mod-p residue distribution for first n_terms of a sequence."""
    vals = seq[:n_terms]
    if len(vals) < 5:
        return None
    fp = {}
    for p in primes:
        residues = [v % p for v in vals]
        counts = Counter(residues)
        # Normalize to distribution
        total = len(residues)
        dist = tuple(counts.get(r, 0) / total for r in range(p))
        fp[p] = dist
    return fp

print("\n── Computing mod-p fingerprints ──")

# Fingerprints for disc sequences
disc_fps = {}
for d in [2, 3, 4, 5]:
    fp = modp_fingerprint(disc_sequences[d])
    if fp:
        disc_fps[d] = fp
        for p in [2, 3, 5]:
            print(f"  degree {d}, mod {p}: {[f'{x:.3f}' for x in fp[p]]}")

# Sample OEIS fingerprints (use all sequences, but only first 30 terms)
print("\nComputing OEIS fingerprints (sampling)...")
oeis_fps = {}
for a_num, terms in oeis_seqs.items():
    # Only positive-valued sequences for fair comparison
    if all(t >= 0 for t in terms[:30]):
        fp = modp_fingerprint(terms)
        if fp:
            oeis_fps[a_num] = fp

print(f"Computed fingerprints for {len(oeis_fps)} OEIS sequences")

# ── 5. Fingerprint distance + MI ─────────────────────────────────────────────

def fp_distance(fp1, fp2, primes=PRIMES):
    """L2 distance between two mod-p fingerprint vectors."""
    dist = 0.0
    for p in primes:
        if p in fp1 and p in fp2:
            d1, d2 = fp1[p], fp2[p]
            dist += sum((a - b) ** 2 for a, b in zip(d1, d2))
    return np.sqrt(dist)

def find_nearest_oeis(disc_fp, oeis_fps, top_k=10):
    """Find OEIS sequences with most similar mod-p fingerprint."""
    dists = []
    for a_num, ofp in oeis_fps.items():
        d = fp_distance(disc_fp, ofp)
        dists.append((d, a_num))
    dists.sort()
    return dists[:top_k]

print("\n── Nearest OEIS by mod-p fingerprint ──")
nearest_results = {}
for d in [2, 3, 4, 5]:
    if d not in disc_fps:
        continue
    nearest = find_nearest_oeis(disc_fps[d], oeis_fps)
    nearest_results[d] = [(dist, a_num) for dist, a_num in nearest]
    print(f"\n  degree {d} nearest OEIS:")
    for dist, a_num in nearest[:5]:
        terms_preview = oeis_seqs[a_num][:8]
        print(f"    {a_num} (dist={dist:.4f}): {terms_preview}")

# ── 6. MI: discretize fingerprints into bins, compute MI ──────────────────────

def discretize_fp(fp, n_bins=5):
    """Convert a mod-p fingerprint into a discrete bin tuple for MI."""
    if fp is None:
        return None
    # Flatten all mod-p distributions into one vector
    vec = []
    for p in PRIMES:
        if p in fp:
            vec.extend(fp[p])
    if not vec:
        return None
    # Discretize into bins
    bins = tuple(int(min(v * n_bins, n_bins - 1)) for v in vec)
    return bins

def compute_mi(labels_a, labels_b):
    """Mutual information between two categorical label arrays."""
    n = len(labels_a)
    if n == 0:
        return 0.0

    joint = Counter(zip(labels_a, labels_b))
    margin_a = Counter(labels_a)
    margin_b = Counter(labels_b)

    mi = 0.0
    for (a, b), n_ab in joint.items():
        p_ab = n_ab / n
        p_a = margin_a[a] / n
        p_b = margin_b[b] / n
        if p_ab > 0 and p_a > 0 and p_b > 0:
            mi += p_ab * np.log2(p_ab / (p_a * p_b))
    return mi

print("\n── MI between disc fingerprints and OEIS ──")

# For each degree: assign disc fingerprint as "label A",
# find OEIS sequences close to it and compute MI between
# the disc-proximity label and the OEIS mod-2 residue pattern.

# Strategy: bin all OEIS sequences by their distance to each disc fingerprint,
# and compute MI between that distance bin and their mod-2 residue pattern.

N_BINS = 5
mi_results = {}

for d in [2, 3, 4, 5]:
    if d not in disc_fps:
        continue

    # Compute distances from disc_fp[d] to all OEIS fps
    distances = []
    mod2_labels = []
    for a_num, ofp in oeis_fps.items():
        dist = fp_distance(disc_fps[d], ofp)
        distances.append(dist)
        # Use mod-2 balance as a simple categorical label
        if 2 in ofp:
            balance = ofp[2][0]  # fraction of even terms
            mod2_labels.append(int(min(balance * N_BINS, N_BINS - 1)))
        else:
            mod2_labels.append(-1)

    distances = np.array(distances)
    # Bin distances
    try:
        percentiles = np.percentile(distances, np.linspace(0, 100, N_BINS + 1))
        dist_bins = np.digitize(distances, percentiles[1:-1])
    except Exception:
        dist_bins = np.zeros(len(distances), dtype=int)

    mi_val = compute_mi(list(dist_bins), mod2_labels)

    # Null: shuffle distance bins
    n_null = 1000
    null_mis = []
    rng = np.random.default_rng(42 + d)
    for _ in range(n_null):
        shuffled = rng.permutation(dist_bins)
        null_mis.append(compute_mi(list(shuffled), mod2_labels))

    null_mean = np.mean(null_mis)
    null_std = np.std(null_mis)
    z_score = (mi_val - null_mean) / null_std if null_std > 0 else 0.0

    mi_results[d] = {
        "mi_bits": round(float(mi_val), 6),
        "null_mean": round(float(null_mean), 6),
        "null_std": round(float(null_std), 6),
        "z_score": round(float(z_score), 2),
        "n_oeis_compared": len(distances),
        "significant": bool(abs(z_score) > 3.0),
        "NOTE": "TAUTOLOGICAL: distance metric includes mod-2 balance, then tests MI against mod-2 labels. High z is circular, not meaningful."
    }

    print(f"  degree {d}: MI={mi_val:.6f} bits, null={null_mean:.6f}+/-{null_std:.6f}, z={z_score:.2f} (TAUTOLOGICAL - see note)")

# ── 7. Additional: direct term-level MI ───────────────────────────────────────
# For each degree, compare the mod-p residue *sequence* of discriminants
# against random OEIS sequences' mod-p residue sequences

print("\n── Term-level mod-p MI (disc residues vs OEIS residues) ──")
term_mi_results = {}

for d in [2, 3, 4, 5]:
    seq = disc_sequences[d][:30]
    if len(seq) < 10:
        print(f"  degree {d}: too few terms ({len(seq)}), skipping")
        continue

    n_terms = len(seq)
    disc_mod5 = [v % 5 for v in seq]

    # Compare against random sample of OEIS sequences
    rng = np.random.default_rng(100 + d)
    oeis_keys = list(oeis_seqs.keys())
    sample_size = min(50000, len(oeis_keys))
    sample_idx = rng.choice(len(oeis_keys), size=sample_size, replace=False)

    real_mis = []
    for idx in sample_idx:
        a_num = oeis_keys[idx]
        oeis_terms = oeis_seqs[a_num][:n_terms]
        if len(oeis_terms) < n_terms:
            continue
        oeis_mod5 = [v % 5 for v in oeis_terms]
        mi = compute_mi(disc_mod5, oeis_mod5)
        real_mis.append((mi, a_num))

    real_mis.sort(reverse=True)

    # Null: random pairs of OEIS sequences
    null_mis = []
    for _ in range(min(5000, len(oeis_keys))):
        i1, i2 = rng.choice(len(oeis_keys), size=2, replace=False)
        t1 = oeis_seqs[oeis_keys[i1]][:n_terms]
        t2 = oeis_seqs[oeis_keys[i2]][:n_terms]
        if len(t1) < n_terms or len(t2) < n_terms:
            continue
        m1 = [v % 5 for v in t1]
        m2 = [v % 5 for v in t2]
        null_mis.append(compute_mi(m1, m2))

    if real_mis and null_mis:
        real_median = np.median([m for m, _ in real_mis])
        null_median = np.median(null_mis)
        null_std = np.std(null_mis)
        z = (real_median - null_median) / null_std if null_std > 0 else 0.0

        term_mi_results[d] = {
            "real_median_mi": round(float(real_median), 6),
            "null_median_mi": round(float(null_median), 6),
            "null_std": round(float(null_std), 6),
            "z_score": round(float(z), 2),
            "n_compared": len(real_mis),
            "top5_oeis": [(round(float(mi), 4), a) for mi, a in real_mis[:5]],
            "significant": bool(abs(z) > 3.0)
        }

        print(f"  degree {d}: median MI={real_median:.6f}, null={null_median:.6f}, z={z:.2f}")
        for mi, a_num in real_mis[:3]:
            print(f"    top match: {a_num} MI={mi:.4f}")

# ── 8. Compile results ───────────────────────────────────────────────────────

results = {
    "experiment": "nf_oeis_disc_mi",
    "description": "Cross-domain: Number field discriminant sequences vs OEIS",
    "data": {
        "nf_source": str(nf_path),
        "oeis_source": str(oeis_path),
        "n_nf_fields": len(nf_data),
        "n_oeis_sequences": len(oeis_seqs)
    },
    "disc_sequences": {
        str(d): {
            "n_unique_disc": len(disc_sequences[d]),
            "first_15": disc_sequences[d][:15],
        }
        for d in [2, 3, 4, 5]
    },
    "exact_oeis_matches": {
        str(d): all_matches.get(d, {})
        for d in [2, 3, 4, 5]
    },
    "nearest_by_fingerprint": {
        str(d): [
            {"oeis_id": a_num, "distance": round(float(dist), 6),
             "first_terms": oeis_seqs[a_num][:8]}
            for dist, a_num in nearest_results.get(d, [])[:5]
        ]
        for d in [2, 3, 4, 5]
    },
    "fingerprint_mi": {str(d): v for d, v in mi_results.items()},
    "term_level_mi": {str(d): v for d, v in term_mi_results.items()},
    "verdict": None
}

# Determine verdict
any_exact = any(
    len(all_matches.get(d, {}).get("exact", [])) > 0
    for d in [2, 3, 4, 5]
)
any_mi_sig = any(
    v.get("significant", False)
    for v in mi_results.values()
)
any_term_sig = any(
    v.get("significant", False)
    for v in term_mi_results.values()
)

if any_exact and any_term_sig:
    results["verdict"] = "POSITIVE: Discriminant sequences in OEIS AND unexpected mod-p MI signal"
elif any_exact:
    results["verdict"] = "EXPECTED: Discriminant sequences found in OEIS (they are catalogued there), but NO unexpected combinatorial structure beyond known cataloguing"
elif any_term_sig:
    results["verdict"] = "WEAK_POSITIVE: No exact matches but significant mod-p MI signal"
else:
    results["verdict"] = "NULL: No novel combinatorial structure. Known disc sequences (A023679, A023685) are in OEIS by construction. Term-level MI shows no signal above random pairing baseline."

print(f"\n{'='*60}")
print(f"VERDICT: {results['verdict']}")
print(f"{'='*60}")

# Save (convert numpy types)
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.bool_, np.integer)):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

out_path = BASE / "v2" / "nf_oeis_disc_mi_results.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2, cls=NumpyEncoder)
print(f"\nSaved to {out_path}")
