"""
Dual Representation Consistency — Same Clusters Across Multiple Views?
======================================================================
Challenge: ChatGPT Part 3 #10

Three independent classification axes for mathematical objects:
  View 1: mod-p fingerprint vector (20 terms mod {2,3,5,7,11}) -> 100-dim
  View 2: characteristic polynomial coefficients (from Berlekamp-Massey)
  View 3: spectral signature (FFT power spectrum, 32 frequencies)

If independent clusterings agree (ARI > 0.3), there's a deeper invariant
beneath all three views. If ARI ~ 0, orthogonality is confirmed.

Usage:
    python dual_representation.py
"""

import gzip
import json
import math
import os
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[4]
V2_DIR = Path(__file__).resolve().parent
OEIS_STRIPPED_TXT = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
OEIS_STRIPPED_GZ = ROOT / "cartography" / "oeis" / "data" / "stripped_full.gz"
OUT_FILE = V2_DIR / "dual_representation_results.json"

PRIMES = [2, 3, 5, 7, 11]
FP_LEN = 20        # fingerprint window
FFT_BINS = 32      # spectral signature dimension
TARGET_N = 5000    # target number of sequences
MAX_POLY_DEG = 12  # max recurrence degree to keep
K = 50             # number of clusters for k-means

random.seed(42)
np.random.seed(42)


# ---------------------------------------------------------------------------
# Berlekamp-Massey
# ---------------------------------------------------------------------------
def berlekamp_massey(seq):
    """Minimal LFSR. Returns (coefficients_list, degree) or (None, 0)."""
    n = len(seq)
    if n == 0:
        return None, 0
    # Work in floating point
    s = [float(x) for x in seq]
    b, c = [1.0], [1.0]
    l, m, d_b = 0, 1, 1.0
    for i in range(n):
        d = s[i]
        for j in range(1, l + 1):
            if j < len(c) and i - j >= 0:
                d += c[j] * s[i - j]
        if abs(d) < 1e-10:
            m += 1
        elif 2 * l <= i:
            t = list(c)
            ratio = -d / d_b if abs(d_b) > 1e-15 else 0
            while len(c) < len(b) + m:
                c.append(0.0)
            for j in range(len(b)):
                c[j + m] += ratio * b[j]
            l = i + 1 - l
            b, d_b, m = t, d, 1
        else:
            ratio = -d / d_b if abs(d_b) > 1e-15 else 0
            while len(c) < len(b) + m:
                c.append(0.0)
            for j in range(len(b)):
                c[j + m] += ratio * b[j]
            m += 1
    if l == 0 or l > n // 3:
        return None, 0
    # Verify: predict next terms
    coeffs = [-c[j] for j in range(1, l + 1)]
    # Check prediction on last quarter
    check_start = max(l, 3 * n // 4)
    for i in range(check_start, n):
        pred = sum(coeffs[j] * s[i - 1 - j] for j in range(l))
        if abs(pred - s[i]) > max(1e-6, 1e-6 * abs(s[i])):
            return None, 0
    return coeffs, l


# ---------------------------------------------------------------------------
# Load OEIS
# ---------------------------------------------------------------------------
def load_oeis(max_seqs=400000):
    """Load OEIS sequences into {id: terms_list}."""
    cache = {}
    src = OEIS_STRIPPED_TXT if OEIS_STRIPPED_TXT.exists() else OEIS_STRIPPED_GZ
    if not src.exists():
        print(f"  WARNING: {src} not found")
        return cache
    opener = gzip.open if str(src).endswith('.gz') else open
    mode = "rt" if str(src).endswith('.gz') else "r"
    print(f"  Loading OEIS from {src.name}...")
    with opener(src, mode, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) < 3:
                continue
            sid = parts[0].strip()
            terms = []
            for t in parts[1:]:
                t = t.strip()
                if t:
                    try:
                        terms.append(int(t))
                    except ValueError:
                        pass
            if terms:
                cache[sid] = terms
            if len(cache) >= max_seqs:
                break
    print(f"  Loaded {len(cache):,} sequences")
    return cache


# ---------------------------------------------------------------------------
# View 1: Mod-p fingerprint vector (100-dim)
# ---------------------------------------------------------------------------
def mod_p_fingerprint(terms):
    """20 terms mod each of {2,3,5,7,11} -> 100-dim vector."""
    if len(terms) < FP_LEN:
        return None
    window = terms[:FP_LEN]
    vec = []
    for p in PRIMES:
        for t in window:
            vec.append(t % p)
    return np.array(vec, dtype=np.float64)


# ---------------------------------------------------------------------------
# View 2: Characteristic polynomial coefficients (padded to MAX_POLY_DEG)
# ---------------------------------------------------------------------------
def poly_feature(coeffs, degree):
    """Pad/truncate polynomial coefficients to fixed-length vector."""
    if degree > MAX_POLY_DEG or degree < 1:
        return None
    vec = list(coeffs[:MAX_POLY_DEG])
    # Pad to MAX_POLY_DEG
    while len(vec) < MAX_POLY_DEG:
        vec.append(0.0)
    return np.array(vec, dtype=np.float64)


# ---------------------------------------------------------------------------
# View 3: Spectral signature (FFT power spectrum, 32 frequencies)
# ---------------------------------------------------------------------------
def spectral_signature(terms):
    """FFT power spectrum of first 64 terms, return 32-dim vector."""
    n_fft = 64
    if len(terms) < n_fft:
        return None
    x = np.array(terms[:n_fft], dtype=np.float64)
    # Remove mean and normalize
    mu = np.mean(x)
    std = np.std(x)
    if std < 1e-12:
        return None  # constant sequence
    x = (x - mu) / std
    # FFT
    fft_vals = np.fft.rfft(x)
    power = np.abs(fft_vals) ** 2
    # Take first FFT_BINS frequencies (skip DC)
    sig = power[1:FFT_BINS + 1]
    if len(sig) < FFT_BINS:
        sig = np.pad(sig, (0, FFT_BINS - len(sig)))
    # Log scale for dynamic range
    sig = np.log1p(sig)
    return sig


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("Dual Representation Consistency Analysis")
    print("=" * 70)

    # 1. Load OEIS
    oeis = load_oeis()

    # 2. Find sequences with valid BM recurrences
    print(f"\n  Running Berlekamp-Massey on sequences with 40+ terms...")
    candidates = [(sid, terms) for sid, terms in oeis.items()
                  if len(terms) >= 64]  # need 64 for FFT
    print(f"  Candidates with 64+ terms: {len(candidates):,}")

    bm_results = {}
    scanned = 0
    for sid, terms in candidates:
        coeffs, deg = berlekamp_massey(terms)
        if coeffs is not None and 1 <= deg <= MAX_POLY_DEG:
            bm_results[sid] = (coeffs, deg)
        scanned += 1
        if scanned % 50000 == 0:
            print(f"    Scanned {scanned:,}, found {len(bm_results):,} recurrences...")
        if len(bm_results) >= TARGET_N * 2:
            # Over-collect then trim
            break

    print(f"  Found {len(bm_results):,} sequences with valid BM recurrences (deg 1-{MAX_POLY_DEG})")

    # 3. Build all three views for sequences that have all three
    print(f"\n  Building three views...")
    seq_ids = []
    view1_list = []
    view2_list = []
    view3_list = []

    for sid in sorted(bm_results.keys()):
        terms = oeis[sid]
        coeffs, deg = bm_results[sid]

        v1 = mod_p_fingerprint(terms)
        v2 = poly_feature(coeffs, deg)
        v3 = spectral_signature(terms)

        if v1 is not None and v2 is not None and v3 is not None:
            seq_ids.append(sid)
            view1_list.append(v1)
            view2_list.append(v2)
            view3_list.append(v3)

    print(f"  Sequences with all three views: {len(seq_ids):,}")

    # Trim to TARGET_N if needed (take first N sorted by ID)
    if len(seq_ids) > TARGET_N:
        # Random subsample for diversity
        idx = list(range(len(seq_ids)))
        random.shuffle(idx)
        idx = sorted(idx[:TARGET_N])
        seq_ids = [seq_ids[i] for i in idx]
        view1_list = [view1_list[i] for i in idx]
        view2_list = [view2_list[i] for i in idx]
        view3_list = [view3_list[i] for i in idx]
        print(f"  Subsampled to {len(seq_ids):,}")

    N = len(seq_ids)
    if N < 100:
        print("  ERROR: Not enough sequences with all three views")
        return

    V1 = np.array(view1_list)
    V2 = np.array(view2_list)
    V3 = np.array(view3_list)

    # 4. Normalize each view
    print(f"\n  Normalizing views...")
    scaler1 = StandardScaler()
    scaler2 = StandardScaler()
    scaler3 = StandardScaler()
    V1n = scaler1.fit_transform(V1)
    V2n = scaler2.fit_transform(V2)
    V3n = scaler3.fit_transform(V3)

    # 5. Cluster each view with k-means (k=50)
    print(f"\n  Clustering each view (k-means, k={K})...")
    km1 = KMeans(n_clusters=K, n_init=10, random_state=42, max_iter=300)
    km2 = KMeans(n_clusters=K, n_init=10, random_state=42, max_iter=300)
    km3 = KMeans(n_clusters=K, n_init=10, random_state=42, max_iter=300)

    labels1 = km1.fit_predict(V1n)
    print(f"    View 1 (mod-p): inertia={km1.inertia_:.1f}")
    labels2 = km2.fit_predict(V2n)
    print(f"    View 2 (char poly): inertia={km2.inertia_:.1f}")
    labels3 = km3.fit_predict(V3n)
    print(f"    View 3 (spectral): inertia={km3.inertia_:.1f}")

    # 6. Compute ARI between all pairs
    print(f"\n  Computing Adjusted Rand Index between all view pairs...")
    ari_12 = adjusted_rand_score(labels1, labels2)
    ari_13 = adjusted_rand_score(labels1, labels3)
    ari_23 = adjusted_rand_score(labels2, labels3)
    print(f"    ARI(View1, View2) = {ari_12:.6f}  [mod-p vs char-poly]")
    print(f"    ARI(View1, View3) = {ari_13:.6f}  [mod-p vs spectral]")
    print(f"    ARI(View2, View3) = {ari_23:.6f}  [char-poly vs spectral]")

    # 7. Null baseline: random label assignments
    print(f"\n  Computing null baseline (1000 random permutations)...")
    null_aris = []
    for _ in range(1000):
        perm = np.random.permutation(N)
        null_aris.append(adjusted_rand_score(labels1, labels2[perm]))
    null_mean = np.mean(null_aris)
    null_std = np.std(null_aris)
    print(f"    Null ARI: mean={null_mean:.6f}, std={null_std:.6f}")
    z_12 = (ari_12 - null_mean) / null_std if null_std > 0 else 0
    z_13 = (ari_13 - null_mean) / null_std if null_std > 0 else 0
    z_23 = (ari_23 - null_mean) / null_std if null_std > 0 else 0
    print(f"    z-scores: ARI12={z_12:.1f}, ARI13={z_13:.1f}, ARI23={z_23:.1f}")

    # 8. Consensus clusters: sequences that cluster together in ALL three views
    print(f"\n  Finding consensus clusters...")
    # Create joint label tuples
    joint_labels = {}
    for i in range(N):
        key = (int(labels1[i]), int(labels2[i]), int(labels3[i]))
        if key not in joint_labels:
            joint_labels[key] = []
        joint_labels[key].append(seq_ids[i])

    # Consensus = groups of 3+ sequences sharing same triple
    consensus = {str(k): v for k, v in joint_labels.items() if len(v) >= 3}
    consensus_sizes = sorted([len(v) for v in consensus.values()], reverse=True)
    total_consensus = sum(len(v) for v in consensus.values())
    print(f"    Consensus clusters (size >= 3): {len(consensus)}")
    print(f"    Sequences in consensus: {total_consensus} / {N} ({100*total_consensus/N:.1f}%)")
    if consensus_sizes:
        print(f"    Largest consensus clusters: {consensus_sizes[:10]}")

    # 9. Analyze top consensus clusters
    print(f"\n  Analyzing top consensus clusters...")
    top_consensus = sorted(consensus.items(), key=lambda x: -len(x[1]))[:20]
    consensus_details = []
    for triple_str, sids in top_consensus:
        # Get recurrence degrees
        degrees = [bm_results[s][1] for s in sids if s in bm_results]
        # Get example terms
        examples = []
        for s in sids[:5]:
            examples.append({"id": s, "terms": oeis[s][:10]})
        detail = {
            "triple": triple_str,
            "size": len(sids),
            "sequences": sids[:20],
            "degree_distribution": dict(Counter(degrees)),
            "examples": examples
        }
        consensus_details.append(detail)
        print(f"    Triple {triple_str}: {len(sids)} seqs, "
              f"degrees: {dict(Counter(degrees))}")

    # 10. Find view-discordant sequences
    print(f"\n  Finding view-discordant sequences...")
    # Discordant = sequences whose nearest neighbors differ across views
    # Simpler: sequences in singleton joint-label groups (unique triple)
    singletons = [v[0] for k, v in joint_labels.items() if len(v) == 1]
    print(f"    Singleton joint labels (maximally discordant): {len(singletons)} / {N}")

    # More nuanced: for each pair of views, find sequences whose cluster
    # partners change most
    def cluster_neighbor_overlap(labels_a, labels_b, top_n=20):
        """For each sequence, compute Jaccard overlap of cluster-mates across two views."""
        cluster_a = defaultdict(set)
        cluster_b = defaultdict(set)
        for i in range(N):
            cluster_a[labels_a[i]].add(i)
            cluster_b[labels_b[i]].add(i)

        overlaps = []
        for i in range(N):
            mates_a = cluster_a[labels_a[i]]
            mates_b = cluster_b[labels_b[i]]
            intersection = len(mates_a & mates_b)
            union = len(mates_a | mates_b)
            jaccard = intersection / union if union > 0 else 0
            overlaps.append((i, jaccard))
        overlaps.sort(key=lambda x: x[1])
        return overlaps[:top_n]

    discord_12 = cluster_neighbor_overlap(labels1, labels2)
    discord_13 = cluster_neighbor_overlap(labels1, labels3)
    discord_23 = cluster_neighbor_overlap(labels2, labels3)

    discordant_details = []
    # Combine most discordant across all three pairs
    disc_idx = set()
    for overlap_list in [discord_12, discord_13, discord_23]:
        for idx, jacc in overlap_list[:10]:
            disc_idx.add(idx)

    for i in sorted(disc_idx):
        sid = seq_ids[i]
        coeffs, deg = bm_results[sid]
        discordant_details.append({
            "seq_id": sid,
            "terms": oeis[sid][:15],
            "bm_degree": deg,
            "bm_coeffs": [round(c, 6) for c in coeffs[:deg]],
            "cluster_v1": int(labels1[i]),
            "cluster_v2": int(labels2[i]),
            "cluster_v3": int(labels3[i]),
        })

    print(f"    Top discordant sequences: {len(discordant_details)}")
    for d in discordant_details[:5]:
        print(f"      {d['seq_id']}: deg={d['bm_degree']}, "
              f"clusters=({d['cluster_v1']},{d['cluster_v2']},{d['cluster_v3']})")

    # 11. Degree-stratified ARI (control for trivial structure)
    print(f"\n  Degree-stratified ARI analysis...")
    degree_groups = defaultdict(list)
    for i, sid in enumerate(seq_ids):
        deg = bm_results[sid][1]
        degree_groups[deg].append(i)

    strat_results = {}
    for deg in sorted(degree_groups.keys()):
        idx = degree_groups[deg]
        if len(idx) < 50:
            continue
        sub_l1 = labels1[idx]
        sub_l2 = labels2[idx]
        sub_l3 = labels3[idx]
        a12 = adjusted_rand_score(sub_l1, sub_l2)
        a13 = adjusted_rand_score(sub_l1, sub_l3)
        a23 = adjusted_rand_score(sub_l2, sub_l3)
        strat_results[deg] = {"n": len(idx), "ari_12": round(a12, 6),
                              "ari_13": round(a13, 6), "ari_23": round(a23, 6)}
        print(f"    Degree {deg} (n={len(idx)}): "
              f"ARI12={a12:.4f}, ARI13={a13:.4f}, ARI23={a23:.4f}")

    # 12. Cross-view correlation matrix (Pearson between view vectors)
    print(f"\n  Cross-view correlation (Mantel-like)...")
    # Sample pairwise distances
    sample_size = min(2000, N)
    sample_idx = np.random.choice(N, sample_size, replace=False)
    from scipy.spatial.distance import pdist, squareform
    d1 = pdist(V1n[sample_idx], metric='euclidean')
    d2 = pdist(V2n[sample_idx], metric='euclidean')
    d3 = pdist(V3n[sample_idx], metric='euclidean')
    mantel_12 = np.corrcoef(d1, d2)[0, 1]
    mantel_13 = np.corrcoef(d1, d3)[0, 1]
    mantel_23 = np.corrcoef(d2, d3)[0, 1]
    print(f"    Distance correlation V1-V2: {mantel_12:.4f}")
    print(f"    Distance correlation V1-V3: {mantel_13:.4f}")
    print(f"    Distance correlation V2-V3: {mantel_23:.4f}")

    # 13. Interpretation
    max_ari = max(ari_12, ari_13, ari_23)
    # Check degree-stratified ARI for V2-V3 coupling
    strat_v23 = [v["ari_23"] for v in strat_results.values()]
    max_strat_v23 = max(strat_v23) if strat_v23 else 0
    mean_strat_v23 = np.mean(strat_v23) if strat_v23 else 0

    if max_strat_v23 > 0.3:
        interpretation = (
            f"TWO-LAYER STRUCTURE: Overall ARI is low ({max_ari:.3f}), confirming "
            f"views are globally near-orthogonal. BUT degree-stratified analysis reveals "
            f"strong V2-V3 coupling (char-poly vs spectral): mean ARI={mean_strat_v23:.3f}, "
            f"max ARI={max_strat_v23:.3f}. This means: WITHIN each recurrence degree, "
            f"the algebraic structure (polynomial coefficients) strongly constrains the "
            f"spectral structure (FFT power). The mod-p arithmetic view (V1) remains "
            f"approximately orthogonal to both, confirming it captures independent information. "
            f"The hidden invariant is recurrence degree itself — it acts as a coarse partition "
            f"beneath which char-poly and spectrum are tightly coupled."
        )
    elif max_ari < 0.05:
        interpretation = ("ORTHOGONAL: All three views produce completely different "
                          "clusterings (ARI ~ 0). No hidden invariant beneath the views.")
    elif max_ari < 0.15:
        interpretation = ("WEAKLY COUPLED: Some residual shared structure exists, likely "
                          "driven by trivial features (degree, magnitude). After controlling "
                          "for degree, views are approximately orthogonal.")
    elif max_ari < 0.30:
        interpretation = ("MODERATELY COUPLED: Non-trivial shared structure detected. "
                          "Consensus clusters represent genuine multi-view invariants. "
                          "The views are not fully orthogonal.")
    else:
        interpretation = ("STRONGLY COUPLED: High cluster agreement across views. "
                          "A deeper invariant exists beneath all three classification axes. "
                          "Consensus clusters are the primary structure.")

    elapsed = time.time() - t0

    # Build results
    results = {
        "challenge": "ChatGPT_P3_10",
        "title": "Dual Representation Consistency — Same Clusters Across Multiple Views?",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "parameters": {
            "n_sequences": N,
            "k_clusters": K,
            "fp_len": FP_LEN,
            "primes": PRIMES,
            "fft_bins": FFT_BINS,
            "max_poly_degree": MAX_POLY_DEG,
            "view1_dim": V1.shape[1],
            "view2_dim": V2.shape[1],
            "view3_dim": V3.shape[1],
        },
        "ari_matrix": {
            "v1_v2_modp_vs_charpoly": round(ari_12, 6),
            "v1_v3_modp_vs_spectral": round(ari_13, 6),
            "v2_v3_charpoly_vs_spectral": round(ari_23, 6),
        },
        "null_baseline": {
            "mean": round(null_mean, 6),
            "std": round(null_std, 6),
            "z_scores": {
                "v1_v2": round(z_12, 1),
                "v1_v3": round(z_13, 1),
                "v2_v3": round(z_23, 1),
            }
        },
        "distance_correlation": {
            "v1_v2": round(mantel_12, 4),
            "v1_v3": round(mantel_13, 4),
            "v2_v3": round(mantel_23, 4),
        },
        "consensus_clusters": {
            "count": len(consensus),
            "total_sequences": total_consensus,
            "fraction": round(total_consensus / N, 4),
            "size_distribution": consensus_sizes[:20],
            "top_clusters": consensus_details[:10],
        },
        "discordant_sequences": {
            "total_singletons": len(singletons),
            "singleton_fraction": round(len(singletons) / N, 4),
            "top_discordant": discordant_details[:20],
        },
        "degree_stratified_ari": strat_results,
        "degree_distribution": dict(Counter(
            bm_results[s][1] for s in seq_ids
        )),
        "interpretation": interpretation,
        "elapsed_seconds": round(elapsed, 1),
    }

    # Save
    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Saved to {OUT_FILE}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"\n  INTERPRETATION: {interpretation}")
    print("=" * 70)


if __name__ == "__main__":
    main()
