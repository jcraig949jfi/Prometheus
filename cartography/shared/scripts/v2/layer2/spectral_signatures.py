"""
Spectral Signatures — FFT-based invariant extraction for OEIS sequences.
=========================================================================
Strategy S5: Fourier decomposition. Each sequence is a discrete signal;
compute its power spectrum and extract a 14-float invariant signature.

Usage:
    python spectral_signatures.py --source oeis                # default
    python spectral_signatures.py --source oeis --max 50000
    python spectral_signatures.py --source oeis --min-length 64
    python spectral_signatures.py --cluster                    # also cluster
"""

import argparse
import gzip
import json
import sys
import time
import warnings
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[5]
OEIS_DATA = ROOT / "cartography" / "oeis" / "data"
STRIPPED_GZ = OEIS_DATA / "stripped_full.gz"
STRIPPED_FALLBACK = OEIS_DATA / "stripped.gz"
CONCEPT_IDS = ROOT / "cartography" / "convergence" / "data" / "concept_ids.json"

OUT_DIR = ROOT / "cartography" / "convergence" / "data"
OUT_SIGS = OUT_DIR / "spectral_signatures.jsonl"
OUT_CLUSTERS = OUT_DIR / "spectral_clusters.jsonl"


# ---------------------------------------------------------------------------
# OEIS loader (mirrors ingest_and_landscape.py)
# ---------------------------------------------------------------------------

def load_oeis_sequences(min_length=32, max_seqs=None):
    """Parse OEIS stripped format, keep sequences with >= min_length terms."""
    gz = STRIPPED_GZ if STRIPPED_GZ.exists() else STRIPPED_FALLBACK
    if not gz.exists():
        print(f"  ERROR: no stripped file at {STRIPPED_GZ} or {STRIPPED_FALLBACK}")
        return {}

    print(f"  Loading OEIS sequences from {gz.name} (min_length={min_length}) ...")
    seqs = {}
    with gzip.open(gz, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            sid = parts[0].strip()
            if not sid.startswith("A"):
                continue
            terms_str = parts[1].strip().strip(",")
            try:
                terms = [int(t) for t in terms_str.split(",") if t.strip()]
            except ValueError:
                continue
            if len(terms) >= min_length:
                seqs[sid] = terms
            if max_seqs and len(seqs) >= max_seqs:
                break
    print(f"  Loaded {len(seqs):,} sequences with >= {min_length} terms")
    return seqs


# ---------------------------------------------------------------------------
# Spectral signature extraction
# ---------------------------------------------------------------------------

def _next_pow2(n):
    """Smallest power of 2 >= n."""
    p = 1
    while p < n:
        p <<= 1
    return p


def spectral_signature(signal, top_k=10):
    """
    Compute 14-float spectral signature from a 1-D real signal.

    Returns: dict with signature_vector (14 floats), top_frequencies, or None
    if the signal is degenerate.
    """
    x = np.asarray(signal, dtype=np.float64)

    # Skip constant or trivially short sequences
    if len(x) < 8:
        return None
    if np.std(x) < 1e-15:
        return None

    # Normalize to zero-mean, unit-variance
    x = (x - np.mean(x)) / (np.std(x) + 1e-30)

    # Pad to power-of-2, apply Hann window
    n = _next_pow2(len(x))
    padded = np.zeros(n)
    padded[:len(x)] = x
    window = np.hanning(n)
    windowed = padded * window

    # FFT (real input -> rfft)
    spectrum = np.fft.rfft(windowed)
    magnitudes = np.abs(spectrum)
    freqs = np.fft.rfftfreq(n)

    # Power spectrum (skip DC component)
    power = magnitudes[1:] ** 2
    freq_axis = freqs[1:]

    if power.sum() < 1e-30:
        return None

    # Normalize power to a distribution
    power_norm = power / power.sum()

    # Top-K frequency magnitudes (indices of largest)
    k = min(top_k, len(power))
    top_idx = np.argsort(power)[-k:][::-1]
    top_freqs = freq_axis[top_idx].tolist()
    top_mags = power[top_idx].tolist()

    # Pad if fewer than top_k
    while len(top_freqs) < top_k:
        top_freqs.append(0.0)
        top_mags.append(0.0)

    # Spectral centroid: weighted mean frequency
    centroid = float(np.dot(freq_axis, power_norm))

    # Spectral bandwidth: weighted std of frequency
    bandwidth = float(np.sqrt(np.dot(freq_axis ** 2, power_norm) - centroid ** 2))

    # Spectral entropy: Shannon entropy of normalized power
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pn = power_norm[power_norm > 0]
        entropy = float(-np.dot(pn, np.log2(pn)))

    # Spectral rolloff: frequency below which 85% of energy lives
    cumulative = np.cumsum(power_norm)
    rolloff_idx = np.searchsorted(cumulative, 0.85)
    rolloff = float(freq_axis[min(rolloff_idx, len(freq_axis) - 1)])

    sig_vec = top_freqs + [centroid, bandwidth, entropy, rolloff]

    return {
        "signature_vector": sig_vec,
        "top_frequencies": top_freqs,
        "top_magnitudes": top_mags,
        "centroid": centroid,
        "bandwidth": bandwidth,
        "entropy": entropy,
        "rolloff": rolloff,
    }


def batch_signatures(sequences, max_seqs=None):
    """Compute spectral signatures for a dict of {id: terms}."""
    results = []
    skipped = 0
    items = list(sequences.items())
    if max_seqs:
        items = items[:max_seqs]
    total = len(items)
    t0 = time.time()

    for i, (sid, terms) in enumerate(items):
        sig = spectral_signature(terms)
        if sig is None:
            skipped += 1
            continue
        results.append({
            "id": sid,
            "source": "oeis",
            "n_terms": len(terms),
            **sig,
        })
        if (i + 1) % 50000 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            print(f"    {i+1:>8,}/{total:,}  ({rate:.0f}/s)  sigs={len(results):,}  skip={skipped:,}")

    elapsed = time.time() - t0
    print(f"  Done: {len(results):,} signatures, {skipped:,} skipped, {elapsed:.1f}s")
    return results


# ---------------------------------------------------------------------------
# Clustering by spectral similarity
# ---------------------------------------------------------------------------

def cluster_signatures(results, n_clusters=200, max_for_clustering=100000):
    """K-means on signature vectors. Returns cluster assignments."""
    from sklearn.cluster import MiniBatchKMeans
    from sklearn.preprocessing import StandardScaler

    vecs = np.array([r["signature_vector"] for r in results], dtype=np.float64)
    if len(vecs) > max_for_clustering:
        idx = np.random.default_rng(42).choice(len(vecs), max_for_clustering, replace=False)
        vecs_sample = vecs[idx]
    else:
        vecs_sample = vecs
        idx = np.arange(len(vecs))

    scaler = StandardScaler()
    vecs_scaled = scaler.fit_transform(vecs_sample)

    k = min(n_clusters, len(vecs_scaled) // 5)
    if k < 2:
        print("  Too few signatures for clustering")
        return []

    print(f"  Clustering {len(vecs_scaled):,} signatures into {k} clusters ...")
    km = MiniBatchKMeans(n_clusters=k, batch_size=4096, random_state=42, n_init=3)
    labels = km.fit_predict(vecs_scaled)

    # If we subsampled, predict on full set
    if len(vecs) > max_for_clustering:
        vecs_all_scaled = scaler.transform(vecs)
        labels_all = km.predict(vecs_all_scaled)
    else:
        labels_all = labels

    # Build cluster records
    from collections import defaultdict
    clusters = defaultdict(list)
    for i, lab in enumerate(labels_all):
        clusters[int(lab)].append(results[i]["id"])

    # Load concept_ids for cross-domain check
    concept_map = {}
    if CONCEPT_IDS.exists():
        try:
            concept_map = json.loads(CONCEPT_IDS.read_text(encoding="utf-8"))
        except Exception:
            pass

    cluster_records = []
    for cid in sorted(clusters):
        members = clusters[cid]
        # Check if members span different concept domains
        domains = set()
        for m in members[:100]:
            if m in concept_map:
                d = concept_map[m]
                if isinstance(d, str):
                    domains.add(d.split("/")[0] if "/" in d else d)
        cluster_records.append({
            "cluster_id": cid,
            "size": len(members),
            "members_sample": members[:20],
            "domains": sorted(domains) if domains else [],
            "cross_domain": len(domains) > 1,
        })

    cross = sum(1 for c in cluster_records if c["cross_domain"])
    print(f"  {len(cluster_records)} clusters, {cross} cross-domain")
    return cluster_records


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

class _Enc(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, cls=_Enc) + "\n")
    print(f"  Wrote {len(records):,} records -> {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Spectral signature extraction (Strategy S5)")
    ap.add_argument("--source", choices=["oeis", "formulas", "both"], default="oeis")
    ap.add_argument("--max", type=int, default=None, help="Max sequences to process")
    ap.add_argument("--min-length", type=int, default=32, help="Min terms for FFT")
    ap.add_argument("--cluster", action="store_true", help="Also run spectral clustering")
    ap.add_argument("--n-clusters", type=int, default=200, help="Number of clusters")
    args = ap.parse_args()

    print("=" * 70)
    print("  Spectral Signatures — Strategy S5")
    print("=" * 70)

    all_results = []

    if args.source in ("oeis", "both"):
        seqs = load_oeis_sequences(min_length=args.min_length, max_seqs=args.max)
        if seqs:
            sigs = batch_signatures(seqs, max_seqs=args.max)
            all_results.extend(sigs)

    if args.source in ("formulas", "both"):
        print("  Formula source: not yet implemented (needs formula_to_executable.py)")
        # Stub for future: evaluate formulas on grid, compute spectral signatures

    if not all_results:
        print("  No results. Exiting.")
        return

    write_jsonl(OUT_SIGS, all_results)

    # Summary stats
    entropies = [r["entropy"] for r in all_results]
    centroids = [r["centroid"] for r in all_results]
    print(f"\n  Summary:")
    print(f"    Signatures:  {len(all_results):,}")
    print(f"    Entropy:     mean={np.mean(entropies):.3f}  std={np.std(entropies):.3f}")
    print(f"    Centroid:    mean={np.mean(centroids):.4f}  std={np.std(centroids):.4f}")

    if args.cluster:
        clusters = cluster_signatures(all_results, n_clusters=args.n_clusters)
        if clusters:
            write_jsonl(OUT_CLUSTERS, clusters)

    print("\n  Done.")


if __name__ == "__main__":
    main()
