"""
Spectral Scaling Law — Second Invariant via Fourier Signatures
==============================================================
Challenge: Does a spectral (FFT power spectrum) invariant produce a
second scaling law orthogonal to mod-p fingerprints?

Method:
1. For each OEIS sequence with 30+ terms, compute FFT power spectrum
   (first 32 frequencies of |FFT(first 64 terms)|^2).
2. Within algebraic family clusters (C08), compute cosine similarity
   of power spectra vs random baseline.
3. Measure spectral enrichment at increasing frequency resolution
   (4, 8, 16, 32 frequencies) — analogous to mod-p at increasing primes.
4. Cross-compare with mod-p enrichment to build 2D invariant map.

Usage:
    python spectral_scaling_law.py
"""

import json
import math
import os
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from numpy.fft import rfft

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[4]
V2_DIR = Path(__file__).resolve().parent
C08_RESULTS = V2_DIR / "recurrence_euler_factor_results.json"
OEIS_STRIPPED_TXT = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
SCALING_BATTERY = V2_DIR / "scaling_law_battery_results.json"
OUT_FILE = V2_DIR / "spectral_scaling_results.json"

FFT_LEN = 64       # take first 64 terms
N_FREQS = 32       # power spectrum has 33 frequencies (DC to Nyquist), use 1..32
MIN_TERMS = 30     # require at least 30 terms
FREQ_RESOLUTIONS = [4, 8, 16, 32]  # spectral resolution sweep
N_RANDOM_PAIRS = 10000
FP_LEN = 20        # mod-p fingerprint length (matching battery.py)
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23]

random.seed(42)
np.random.seed(42)


# ---------------------------------------------------------------------------
# Load OEIS
# ---------------------------------------------------------------------------
def load_oeis():
    """Load OEIS sequences into {id: terms_list}."""
    cache = {}
    src = OEIS_STRIPPED_TXT
    if not src.exists():
        print(f"  WARNING: {src} not found")
        return cache
    print(f"  Loading OEIS from {src.name}...")
    with open(src, "r", encoding="utf-8") as f:
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
    print(f"  Loaded {len(cache):,} sequences")
    return cache


# ---------------------------------------------------------------------------
# Spectral signature
# ---------------------------------------------------------------------------
def spectral_signature(terms, n_freqs=N_FREQS):
    """
    Compute power spectrum of first FFT_LEN terms.
    Returns normalized power spectrum (L2-norm = 1) for cosine similarity.
    Excludes DC component (frequency 0).
    """
    x = np.array(terms[:FFT_LEN], dtype=np.float64)
    if len(x) < MIN_TERMS:
        return None
    # Zero-pad to FFT_LEN
    if len(x) < FFT_LEN:
        x = np.concatenate([x, np.zeros(FFT_LEN - len(x))])
    # Remove mean to focus on oscillatory structure
    x = x - x.mean()
    # Compute FFT
    X = rfft(x)  # length FFT_LEN//2 + 1 = 33
    power = np.abs(X) ** 2
    # Skip DC (index 0), take first n_freqs
    sig = power[1:n_freqs + 1]
    # Normalize to unit norm for cosine similarity
    norm = np.linalg.norm(sig)
    if norm < 1e-15:
        return None
    return sig / norm


def spectral_signature_raw(terms, n_freqs=N_FREQS):
    """Same but unnormalized, for inspection."""
    x = np.array(terms[:FFT_LEN], dtype=np.float64)
    if len(x) < MIN_TERMS:
        return None
    if len(x) < FFT_LEN:
        x = np.concatenate([x, np.zeros(FFT_LEN - len(x))])
    x = x - x.mean()
    X = rfft(x)
    power = np.abs(X) ** 2
    return power[1:n_freqs + 1]


def cosine_sim(a, b):
    """Cosine similarity between two vectors (already L2-normalized)."""
    return float(np.dot(a, b))


# ---------------------------------------------------------------------------
# Load families from C08 polynomial clusters
# ---------------------------------------------------------------------------
def load_families(oeis_data):
    """Load polynomial clusters and return {poly_str: [seq_ids]}."""
    if not C08_RESULTS.exists():
        print("  WARNING: C08 results not found")
        return {}, {}

    with open(C08_RESULTS, "r") as f:
        c08 = json.load(f)

    clusters = c08.get("polynomial_clusters", {})
    top_clusters = clusters.get("top_clusters", [])

    families = {}
    family_meta = {}  # poly_str -> metadata
    for cluster in top_clusters:
        if not isinstance(cluster, dict):
            continue
        coeffs = cluster.get("char_poly_coeffs", [])
        seq_ids = cluster.get("sequences", [])
        poly_str = str(coeffs)
        # Keep only sequences we have terms for
        valid = [s for s in seq_ids if isinstance(s, str) and s in oeis_data
                 and len(oeis_data[s]) >= MIN_TERMS]
        if len(valid) >= 2:
            families[poly_str] = valid
            family_meta[poly_str] = {
                "degree": cluster.get("degree", 0),
                "n_total": cluster.get("n_sequences", 0),
                "n_valid": len(valid),
                "is_ec": cluster.get("is_ec_euler", False),
                "is_genus2": cluster.get("is_genus2_euler", False),
                "coeffs": coeffs,
            }

    total_seqs = sum(len(v) for v in families.values())
    print(f"  Loaded {len(families)} families, {total_seqs} sequences")
    return families, family_meta


# ---------------------------------------------------------------------------
# Mod-p fingerprint (from battery.py)
# ---------------------------------------------------------------------------
def fingerprint(terms, p):
    window = terms[:FP_LEN]
    if len(window) < FP_LEN:
        return None
    return tuple(t % p for t in window)


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------
def compute_spectral_enrichment(families, oeis_data, n_freqs):
    """
    Compute within-family vs random cosine similarity at given freq resolution.
    Returns (family_mean_sim, random_mean_sim, enrichment_ratio).
    """
    # Within-family pairs
    family_sims = []
    for poly, seq_ids in families.items():
        sigs = {}
        for sid in seq_ids:
            sig = spectral_signature(oeis_data[sid], n_freqs=n_freqs)
            if sig is not None:
                sigs[sid] = sig
        sids = list(sigs.keys())
        for i in range(len(sids)):
            for j in range(i + 1, len(sids)):
                family_sims.append(cosine_sim(sigs[sids[i]], sigs[sids[j]]))

    # Random pairs
    all_sigs = {}
    all_seq_ids = []
    for seq_ids in families.values():
        for sid in seq_ids:
            if sid not in all_sigs:
                sig = spectral_signature(oeis_data[sid], n_freqs=n_freqs)
                if sig is not None:
                    all_sigs[sid] = sig
                    all_seq_ids.append(sid)

    random_sims = []
    for _ in range(N_RANDOM_PAIRS):
        i, j = random.sample(range(len(all_seq_ids)), 2)
        random_sims.append(cosine_sim(all_sigs[all_seq_ids[i]], all_sigs[all_seq_ids[j]]))

    fam_mean = float(np.mean(family_sims)) if family_sims else 0
    rnd_mean = float(np.mean(random_sims)) if random_sims else 0
    enrichment = fam_mean / rnd_mean if rnd_mean > 1e-10 else float('inf')

    return {
        "n_freqs": n_freqs,
        "family_mean_sim": fam_mean,
        "family_median_sim": float(np.median(family_sims)) if family_sims else 0,
        "family_std": float(np.std(family_sims)) if family_sims else 0,
        "random_mean_sim": rnd_mean,
        "random_median_sim": float(np.median(random_sims)) if random_sims else 0,
        "random_std": float(np.std(random_sims)) if random_sims else 0,
        "enrichment": enrichment,
        "n_family_pairs": len(family_sims),
        "n_random_pairs": len(random_sims),
    }


def compute_per_family_spectral(families, oeis_data, n_freqs=N_FREQS):
    """Compute spectral enrichment per family (mean within-family sim)."""
    all_sigs = {}
    for seq_ids in families.values():
        for sid in seq_ids:
            if sid not in all_sigs:
                sig = spectral_signature(oeis_data[sid], n_freqs=n_freqs)
                if sig is not None:
                    all_sigs[sid] = sig

    # Global random baseline
    all_seq_ids = list(all_sigs.keys())
    random_sims = []
    for _ in range(N_RANDOM_PAIRS):
        i, j = random.sample(range(len(all_seq_ids)), 2)
        random_sims.append(cosine_sim(all_sigs[all_seq_ids[i]], all_sigs[all_seq_ids[j]]))
    rnd_mean = float(np.mean(random_sims))

    per_family = {}
    for poly, seq_ids in families.items():
        sigs = {}
        for sid in seq_ids:
            if sid in all_sigs:
                sigs[sid] = all_sigs[sid]
        sids = list(sigs.keys())
        if len(sids) < 2:
            continue
        sims = []
        for i in range(len(sids)):
            for j in range(i + 1, len(sids)):
                sims.append(cosine_sim(sigs[sids[i]], sigs[sids[j]]))
        fam_mean = float(np.mean(sims))
        per_family[poly] = {
            "mean_sim": fam_mean,
            "enrichment": fam_mean / rnd_mean if rnd_mean > 1e-10 else float('inf'),
            "n_pairs": len(sims),
            "n_seqs": len(sids),
        }

    return per_family, rnd_mean


def compute_per_family_modp(families, oeis_data):
    """Compute mod-p enrichment per family at each prime."""
    # Random baseline per prime
    all_seq_ids = []
    for seq_ids in families.values():
        all_seq_ids.extend(seq_ids)
    all_seq_ids = list(set(s for s in all_seq_ids if len(oeis_data.get(s, [])) >= FP_LEN))

    random_rates = {}
    for p in PRIMES:
        matches = 0
        for _ in range(N_RANDOM_PAIRS):
            i, j = random.sample(range(len(all_seq_ids)), 2)
            fp_i = fingerprint(oeis_data[all_seq_ids[i]], p)
            fp_j = fingerprint(oeis_data[all_seq_ids[j]], p)
            if fp_i is not None and fp_j is not None and fp_i == fp_j:
                matches += 1
        random_rates[p] = matches / N_RANDOM_PAIRS

    per_family = {}
    for poly, seq_ids in families.items():
        valid = [s for s in seq_ids if len(oeis_data.get(s, [])) >= FP_LEN]
        if len(valid) < 2:
            continue
        family_result = {}
        for p in PRIMES:
            fps = {}
            for sid in valid:
                fp = fingerprint(oeis_data[sid], p)
                if fp is not None:
                    fps[sid] = fp
            sids = list(fps.keys())
            matches = 0
            total = 0
            for i in range(len(sids)):
                for j in range(i + 1, len(sids)):
                    total += 1
                    if fps[sids[i]] == fps[sids[j]]:
                        matches += 1
            rate = matches / total if total > 0 else 0
            rnd = random_rates[p]
            family_result[str(p)] = {
                "match_rate": rate,
                "enrichment": rate / rnd if rnd > 1e-10 else (float('inf') if rate > 0 else 1.0),
            }
        # Summary: geometric mean of enrichment across primes 3..23
        enrichments = [family_result[str(p)]["enrichment"]
                       for p in PRIMES[1:]  # skip p=2 (noisy)
                       if family_result[str(p)]["enrichment"] < float('inf')]
        if enrichments:
            geo_mean = float(np.exp(np.mean(np.log(np.array(enrichments) + 1e-10))))
        else:
            geo_mean = float('inf')
        per_family[poly] = {
            "per_prime": family_result,
            "geo_mean_enrichment": geo_mean,
        }

    return per_family


def build_2d_invariant(spectral_per_family, modp_per_family, family_meta):
    """Build 2D (mod-p, spectral) map for each family."""
    points = []
    for poly in spectral_per_family:
        if poly not in modp_per_family:
            continue
        sp = spectral_per_family[poly]
        mp = modp_per_family[poly]
        meta = family_meta.get(poly, {})

        sp_enrich = sp["enrichment"]
        mp_enrich = mp["geo_mean_enrichment"]

        # Classify quadrant
        sp_high = sp_enrich > 2.0
        mp_high = mp_enrich > 2.0

        if sp_high and mp_high:
            quadrant = "both_visible"
        elif sp_high and not mp_high:
            quadrant = "spectrally_visible_only"
        elif not sp_high and mp_high:
            quadrant = "arithmetically_visible_only"
        else:
            quadrant = "neither"

        points.append({
            "family": poly,
            "coeffs": meta.get("coeffs", []),
            "degree": meta.get("degree", 0),
            "n_seqs": sp["n_seqs"],
            "is_ec": meta.get("is_ec", False),
            "is_genus2": meta.get("is_genus2", False),
            "spectral_enrichment": sp_enrich,
            "spectral_mean_sim": sp["mean_sim"],
            "modp_geo_enrichment": mp_enrich,
            "quadrant": quadrant,
        })

    return points


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("SPECTRAL SCALING LAW — Second Invariant via Fourier Signatures")
    print("=" * 70)

    # Load data
    oeis_data = load_oeis()
    families, family_meta = load_families(oeis_data)

    if not families:
        print("ERROR: No families loaded. Aborting.")
        return

    # -----------------------------------------------------------------------
    # 1. Spectral enrichment at increasing frequency resolution
    # -----------------------------------------------------------------------
    print("\n--- Spectral enrichment vs frequency resolution ---")
    spectral_curve = {}
    for n_f in FREQ_RESOLUTIONS:
        print(f"  Computing at {n_f} frequencies...")
        result = compute_spectral_enrichment(families, oeis_data, n_freqs=n_f)
        spectral_curve[n_f] = result
        print(f"    Family mean sim: {result['family_mean_sim']:.4f}, "
              f"Random: {result['random_mean_sim']:.4f}, "
              f"Enrichment: {result['enrichment']:.2f}x")

    # Does enrichment grow with resolution?
    enrichments = [spectral_curve[n_f]["enrichment"] for n_f in FREQ_RESOLUTIONS]
    monotonic = all(enrichments[i] <= enrichments[i+1] for i in range(len(enrichments)-1))
    print(f"\n  Enrichment curve: {[f'{e:.2f}x' for e in enrichments]}")
    print(f"  Monotonically increasing: {monotonic}")

    # -----------------------------------------------------------------------
    # 2. Per-family spectral enrichment
    # -----------------------------------------------------------------------
    print("\n--- Per-family spectral enrichment ---")
    spectral_per_family, spectral_random_baseline = compute_per_family_spectral(
        families, oeis_data, n_freqs=N_FREQS)
    print(f"  Computed for {len(spectral_per_family)} families")
    print(f"  Random baseline sim: {spectral_random_baseline:.4f}")

    # Top spectral families
    sorted_spectral = sorted(spectral_per_family.items(),
                             key=lambda x: x[1]["enrichment"], reverse=True)
    print("\n  Top 10 spectral families:")
    for poly, data in sorted_spectral[:10]:
        meta = family_meta.get(poly, {})
        print(f"    {meta.get('coeffs', poly)}: enrichment={data['enrichment']:.2f}x, "
              f"n={data['n_seqs']}, deg={meta.get('degree', '?')}")

    # -----------------------------------------------------------------------
    # 3. Per-family mod-p enrichment
    # -----------------------------------------------------------------------
    print("\n--- Per-family mod-p enrichment ---")
    modp_per_family = compute_per_family_modp(families, oeis_data)
    print(f"  Computed for {len(modp_per_family)} families")

    # Top mod-p families
    sorted_modp = sorted(modp_per_family.items(),
                         key=lambda x: x[1]["geo_mean_enrichment"], reverse=True)
    print("\n  Top 10 mod-p families:")
    for poly, data in sorted_modp[:10]:
        meta = family_meta.get(poly, {})
        geo = data["geo_mean_enrichment"]
        geo_str = f"{geo:.2f}x" if geo < float('inf') else "inf"
        print(f"    {meta.get('coeffs', poly)}: geo_mean={geo_str}, deg={meta.get('degree', '?')}")

    # -----------------------------------------------------------------------
    # 4. Build 2D invariant map
    # -----------------------------------------------------------------------
    print("\n--- 2D Invariant Map (mod-p vs spectral) ---")
    points_2d = build_2d_invariant(spectral_per_family, modp_per_family, family_meta)

    quadrant_counts = defaultdict(int)
    for pt in points_2d:
        quadrant_counts[pt["quadrant"]] += 1

    print(f"  Total families mapped: {len(points_2d)}")
    for q, c in sorted(quadrant_counts.items()):
        print(f"    {q}: {c}")

    # Correlation between spectral and mod-p enrichment
    sp_vals = []
    mp_vals = []
    for pt in points_2d:
        sp = pt["spectral_enrichment"]
        mp = pt["modp_geo_enrichment"]
        if sp < float('inf') and mp < float('inf'):
            sp_vals.append(sp)
            mp_vals.append(mp)

    if len(sp_vals) > 3:
        correlation = float(np.corrcoef(sp_vals, mp_vals)[0, 1])
        # Also rank correlation
        from scipy.stats import spearmanr
        spearman_r, spearman_p = spearmanr(sp_vals, mp_vals)
    else:
        correlation = float('nan')
        spearman_r, spearman_p = float('nan'), float('nan')

    print(f"\n  Pearson correlation: {correlation:.4f}")
    print(f"  Spearman correlation: {spearman_r:.4f} (p={spearman_p:.4e})")

    # -----------------------------------------------------------------------
    # 5. Identify interesting cases
    # -----------------------------------------------------------------------
    print("\n--- Spectrally visible, arithmetically invisible ---")
    speconly = [pt for pt in points_2d if pt["quadrant"] == "spectrally_visible_only"]
    for pt in sorted(speconly, key=lambda x: x["spectral_enrichment"], reverse=True)[:5]:
        print(f"  {pt['coeffs']}: spectral={pt['spectral_enrichment']:.2f}x, "
              f"modp={pt['modp_geo_enrichment']:.2f}x, n={pt['n_seqs']}")

    print("\n--- Arithmetically visible, spectrally invisible ---")
    arithonly = [pt for pt in points_2d if pt["quadrant"] == "arithmetically_visible_only"]
    for pt in sorted(arithonly, key=lambda x: x["modp_geo_enrichment"], reverse=True)[:5]:
        mp = pt["modp_geo_enrichment"]
        mp_str = f"{mp:.2f}x" if mp < float('inf') else "inf"
        print(f"  {pt['coeffs']}: spectral={pt['spectral_enrichment']:.2f}x, "
              f"modp={mp_str}, n={pt['n_seqs']}")

    # -----------------------------------------------------------------------
    # Save results
    # -----------------------------------------------------------------------
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "parameters": {
            "fft_len": FFT_LEN,
            "n_freqs": N_FREQS,
            "min_terms": MIN_TERMS,
            "freq_resolutions": FREQ_RESOLUTIONS,
            "n_random_pairs": N_RANDOM_PAIRS,
            "fp_len": FP_LEN,
            "primes": PRIMES,
        },
        "n_families": len(families),
        "n_sequences": sum(len(v) for v in families.values()),
        "spectral_enrichment_curve": {
            str(n_f): spectral_curve[n_f] for n_f in FREQ_RESOLUTIONS
        },
        "spectral_scaling": {
            "enrichments": enrichments,
            "monotonically_increasing": monotonic,
        },
        "per_family_spectral": {
            poly: data for poly, data in sorted_spectral
        },
        "per_family_modp_summary": {
            poly: {"geo_mean_enrichment": data["geo_mean_enrichment"]}
            for poly, data in sorted_modp
        },
        "invariant_2d": {
            "points": points_2d,
            "quadrant_counts": dict(quadrant_counts),
            "pearson_r": correlation,
            "spearman_r": float(spearman_r),
            "spearman_p": float(spearman_p),
        },
        "spectrally_visible_only": [
            {k: v for k, v in pt.items()}
            for pt in sorted(speconly, key=lambda x: x["spectral_enrichment"], reverse=True)
        ],
        "arithmetically_visible_only": [
            {k: v for k, v in pt.items()}
            for pt in sorted(arithonly, key=lambda x: x["modp_geo_enrichment"], reverse=True)
        ],
    }

    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2, default=str)

    elapsed = time.time() - t0
    print(f"\n{'=' * 70}")
    print(f"Results saved to {OUT_FILE}")
    print(f"Elapsed: {elapsed:.1f}s")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
