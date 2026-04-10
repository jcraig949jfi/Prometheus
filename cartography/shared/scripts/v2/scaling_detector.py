"""
Scaling Detector — Invert the Scaling Law into an Active Discovery Tool
========================================================================
Metrology Challenge M6 (ALL-039, DeepSeek R3-1)

The scaling law detects algebraic families (8x enrichment after detrending).
Can we INVERT this: given unlabeled OEIS sequences, predict which ones
belong to a hidden algebraic family?

Pipeline:
1. Load 10,000 OEIS sequences NOT in any known algebraic family cluster
   (no BM recurrence at degree <= 8).
2. Compute mod-p fingerprint at p=2,3,5,7,11 on first 20 terms.
3. Measure neighborhood enrichment: observed matches / expected under uniform.
4. Top 5% = predicted hidden algebraic structure.
5. Verify: BM at higher orders (up to 12), OEIS name check for "recurrence"
   or "algebraic" keywords.
6. Control: compare top 100 vs bottom 100 detection rates.

Usage:
    python scaling_detector.py
"""

import gzip
import json
import math
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[4]
V2_DIR = Path(__file__).resolve().parent
C08_RESULTS = V2_DIR / "recurrence_euler_factor_results.json"
OEIS_STRIPPED_GZ = ROOT / "cartography" / "oeis" / "data" / "stripped_full.gz"
OEIS_STRIPPED_TXT = ROOT / "cartography" / "oeis" / "data" / "stripped_new.txt"
OEIS_NAMES = ROOT / "cartography" / "oeis" / "data" / "oeis_names.json"
OUT_FILE = V2_DIR / "scaling_detector_results.json"

PRIMES = [2, 3, 5, 7, 11]
FP_LEN = 20  # fingerprint window length
N_SAMPLE = 10000
TOP_K = 100
BOTTOM_K = 100
BM_MAX_DEGREE = 12  # extended BM search

random.seed(42)
np.random.seed(42)


# ---------------------------------------------------------------------------
# Berlekamp-Massey (extended to higher degree)
# ---------------------------------------------------------------------------
def berlekamp_massey(seq, max_degree=8):
    """Minimal LFSR via Berlekamp-Massey. Returns (coeffs, degree) or None.

    Rejects if degree > max_degree or degree > n//3 (overfitting guard).
    """
    n = len(seq)
    if n == 0:
        return None
    # Work in floating point for generality
    b, c = [1.0], [1.0]
    l, m, d_b = 0, 1, 1.0
    for i in range(n):
        d = float(seq[i])
        for j in range(1, l + 1):
            if j < len(c) and i - j >= 0:
                d += c[j] * float(seq[i - j])
        if abs(d) < 1e-10:
            m += 1
        elif 2 * l <= i:
            t = list(c)
            ratio = -d / d_b if abs(d_b) > 1e-15 else 0.0
            while len(c) < len(b) + m:
                c.append(0.0)
            for j in range(len(b)):
                c[j + m] += ratio * b[j]
            l = i + 1 - l
            b, d_b, m = t, d, 1
        else:
            ratio = -d / d_b if abs(d_b) > 1e-15 else 0.0
            while len(c) < len(b) + m:
                c.append(0.0)
            for j in range(len(b)):
                c[j + m] += ratio * b[j]
            m += 1
    if l == 0 or l > max_degree or l > n // 3:
        return None
    return c[:l + 1], l


def verify_recurrence(seq, coeffs, degree):
    """Verify that BM coefficients reproduce the sequence exactly."""
    if degree >= len(seq):
        return False
    for i in range(degree, len(seq)):
        predicted = 0.0
        for j in range(1, degree + 1):
            if j < len(coeffs):
                predicted -= coeffs[j] * float(seq[i - j])
        if abs(predicted - float(seq[i])) > 0.5:
            return False
    return True


# ---------------------------------------------------------------------------
# Load OEIS
# ---------------------------------------------------------------------------
def load_oeis():
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
    print(f"  Loaded {len(cache):,} sequences")
    return cache


def load_names():
    """Load OEIS sequence names."""
    if not OEIS_NAMES.exists():
        print("  WARNING: oeis_names.json not found")
        return {}
    print(f"  Loading OEIS names...")
    with open(OEIS_NAMES, "r", encoding="utf-8") as f:
        names = json.load(f)
    print(f"  Loaded {len(names):,} names")
    return names


# ---------------------------------------------------------------------------
# Extract known algebraic family members from C08
# ---------------------------------------------------------------------------
def get_known_algebraic_ids():
    """Get set of OEIS IDs already in known polynomial clusters (degree <= 8)."""
    known = set()
    if not C08_RESULTS.exists():
        print("  WARNING: C08 results not found")
        return known
    with open(C08_RESULTS, "r") as f:
        c08 = json.load(f)

    # All sequences that had BM match at degree <= 8
    clusters = c08.get("polynomial_clusters", {})
    top_clusters = clusters.get("top_clusters", []) if isinstance(clusters, dict) else []
    for cluster in top_clusters:
        if not isinstance(cluster, dict):
            continue
        seq_ids = cluster.get("sequences", [])
        known.update(seq_ids)

    # Also collect from ec/genus2 matches
    for key in ["ec_euler_factor", "genus2_euler_factor"]:
        section = c08.get(key, {})
        for entry in section.get("sequences", []):
            if isinstance(entry, dict):
                known.add(entry.get("seq_id", ""))

    # Also get all scanned sequences (coverage.total_sequences_scanned = 55497)
    # These had BM run. We want those that had NO recurrence detected or degree > 8.
    # The known set has those WITH recurrence. So the complement is our target.

    print(f"  Known algebraic family members: {len(known):,}")
    return known


# ---------------------------------------------------------------------------
# Mod-p fingerprint
# ---------------------------------------------------------------------------
def mod_p_fingerprint(terms, p, length=20):
    """Compute mod-p fingerprint on first `length` terms."""
    usable = terms[:length]
    if len(usable) < length:
        return None
    return tuple(t % p for t in usable)


def multi_prime_fingerprint(terms, primes=PRIMES, length=20):
    """Compute fingerprints at all primes. Returns dict {p: tuple}."""
    fps = {}
    for p in primes:
        fp = mod_p_fingerprint(terms, p, length)
        if fp is None:
            return None
        fps[p] = fp
    return fps


# ---------------------------------------------------------------------------
# Enrichment scoring
# ---------------------------------------------------------------------------
def compute_enrichment_scores(fingerprints, primes=PRIMES):
    """
    For each sequence, count how many others share its mod-p fingerprint
    at each prime. Compute enrichment = observed / expected.

    Expected under uniform for mod-p fingerprint of length L: 1/p^L
    (extremely small), so we use empirical bucket frequencies instead.
    """
    n = len(fingerprints)
    seq_ids = list(fingerprints.keys())

    # For each prime, build bucket counts
    bucket_counts = {}  # {p: {fingerprint: count}}
    for p in primes:
        counts = Counter()
        for sid in seq_ids:
            fp = fingerprints[sid].get(p)
            if fp is not None:
                counts[fp] += 1
        bucket_counts[p] = counts

    # For each sequence, compute enrichment score
    # enrichment at prime p = bucket_size / expected_bucket_size
    # expected = n / n_distinct_fingerprints (uniform assumption)
    scores = {}
    for sid in seq_ids:
        total_enrichment = 0.0
        n_primes_used = 0
        per_prime = {}
        for p in primes:
            fp = fingerprints[sid].get(p)
            if fp is None:
                continue
            bucket_size = bucket_counts[p][fp]
            n_distinct = len(bucket_counts[p])
            expected = n / n_distinct if n_distinct > 0 else 1.0
            enrichment = bucket_size / expected if expected > 0 else 0.0
            per_prime[p] = {
                "bucket_size": bucket_size,
                "n_distinct": n_distinct,
                "expected": round(expected, 4),
                "enrichment": round(enrichment, 4)
            }
            total_enrichment += enrichment
            n_primes_used += 1

        # Combined score: geometric mean of per-prime enrichments
        if n_primes_used > 0:
            enrichments = [per_prime[p]["enrichment"] for p in primes if p in per_prime]
            # Use geometric mean (more sensitive to consistent enrichment)
            log_sum = sum(math.log(max(e, 1e-10)) for e in enrichments)
            geo_mean = math.exp(log_sum / len(enrichments))
            scores[sid] = {
                "geo_mean_enrichment": round(geo_mean, 6),
                "mean_enrichment": round(total_enrichment / n_primes_used, 6),
                "per_prime": per_prime
            }
        else:
            scores[sid] = {"geo_mean_enrichment": 0.0, "mean_enrichment": 0.0, "per_prime": {}}

    return scores


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------
RECURRENCE_KEYWORDS = [
    "recurrence", "linear recurrence", "satisfies", "recurrence relation",
    "algebraic", "l.g.f.", "g.f.", "generating function",
    "fibonacci", "lucas", "pell", "chebyshev", "bernoulli",
    "characteristic polynomial", "constant-recursive",
    "c-finite", "holonomic", "d-finite", "p-recursive"
]

def check_name_for_algebraic(name):
    """Check if OEIS name suggests algebraic/recurrence structure."""
    if not name:
        return False, []
    name_lower = name.lower()
    matched = [kw for kw in RECURRENCE_KEYWORDS if kw in name_lower]
    return len(matched) > 0, matched


def verify_sequence(sid, terms, names_db, max_bm_degree=BM_MAX_DEGREE):
    """Run verification suite on a single sequence."""
    result = {
        "seq_id": sid,
        "n_terms": len(terms),
        "bm_degree": None,
        "bm_verified": False,
        "bm_was_missed": False,  # True if degree 9-12 (missed by C08's deg<=8)
        "bm_low_degree": False,  # True if degree 1-8 (should have been caught)
        "name_match": False,
        "name_keywords": [],
        "name": ""
    }

    # 1. Extended BM (up to degree 12)
    if len(terms) >= 2 * max_bm_degree + 1:
        bm_result = berlekamp_massey(terms, max_degree=max_bm_degree)
        if bm_result is not None:
            coeffs, degree = bm_result
            if verify_recurrence(terms, coeffs, degree):
                result["bm_degree"] = degree
                result["bm_verified"] = True
                result["bm_was_missed"] = degree > 8  # genuine discovery
                result["bm_low_degree"] = degree <= 8

    # 2. Name check
    name = names_db.get(sid, "")
    result["name"] = name[:200]  # truncate for output
    has_match, keywords = check_name_for_algebraic(name)
    result["name_match"] = has_match
    result["name_keywords"] = keywords

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    print("=" * 70)
    print("M6: Scaling Detector — Inverting the Scaling Law")
    print("=" * 70)

    # Step 1: Load data
    print("\n[1] Loading data...")
    oeis = load_oeis()
    names_db = load_names()
    known_ids = get_known_algebraic_ids()

    # Step 2: Select 10,000 sequences NOT in known families
    print("\n[2] Selecting candidate sequences...")
    # Requirements: not in known families, has >= 20 terms, has >= 2*BM_MAX_DEGREE+1 terms for verification
    # Also filter out trivial sequences (all zeros, all ones, constant)
    candidates = {}
    for sid, terms in oeis.items():
        if sid in known_ids:
            continue
        if len(terms) < FP_LEN:
            continue
        # Filter trivial
        unique_vals = set(terms[:FP_LEN])
        if len(unique_vals) <= 1:
            continue
        # Filter sequences with extremely large terms (overflow risk)
        if any(abs(t) > 10**15 for t in terms[:FP_LEN]):
            continue
        candidates[sid] = terms

    print(f"  Eligible candidates: {len(candidates):,}")

    # Sample 10,000
    if len(candidates) > N_SAMPLE:
        sampled_ids = sorted(random.sample(list(candidates.keys()), N_SAMPLE))
    else:
        sampled_ids = sorted(candidates.keys())
        print(f"  WARNING: only {len(sampled_ids)} candidates available, using all")

    sampled = {sid: candidates[sid] for sid in sampled_ids}
    print(f"  Sampled {len(sampled):,} sequences")

    # Step 3: Compute mod-p fingerprints
    print("\n[3] Computing mod-p fingerprints...")
    fingerprints = {}
    for sid, terms in sampled.items():
        fp = multi_prime_fingerprint(terms, PRIMES, FP_LEN)
        if fp is not None:
            fingerprints[sid] = fp
    print(f"  Fingerprinted {len(fingerprints):,} sequences")

    # Step 4: Compute enrichment scores
    print("\n[4] Computing enrichment scores...")
    scores = compute_enrichment_scores(fingerprints, PRIMES)

    # Sort by geometric mean enrichment
    ranked = sorted(scores.items(), key=lambda x: x[1]["geo_mean_enrichment"], reverse=True)

    # Report score distribution
    all_geo = [s[1]["geo_mean_enrichment"] for s in ranked]
    print(f"  Score distribution:")
    print(f"    Min: {min(all_geo):.4f}")
    print(f"    Median: {np.median(all_geo):.4f}")
    print(f"    Mean: {np.mean(all_geo):.4f}")
    print(f"    Max: {max(all_geo):.4f}")
    print(f"    Std: {np.std(all_geo):.4f}")

    top_5pct_threshold = all_geo[int(len(all_geo) * 0.05)] if len(all_geo) > 20 else 0
    print(f"    Top 5% threshold: {top_5pct_threshold:.4f}")

    n_top_5pct = sum(1 for g in all_geo if g >= top_5pct_threshold)
    print(f"    Sequences in top 5%: {n_top_5pct}")

    # Step 5: Extract top and bottom groups
    top_ids = [sid for sid, _ in ranked[:TOP_K]]
    bottom_ids = [sid for sid, _ in ranked[-BOTTOM_K:]]

    print(f"\n  Top {TOP_K} enrichment scores: {[round(scores[s]['geo_mean_enrichment'], 3) for s in top_ids[:10]]}...")
    print(f"  Bottom {BOTTOM_K} enrichment scores: {[round(scores[s]['geo_mean_enrichment'], 3) for s in bottom_ids[:10]]}...")

    # Step 6: Verify top and bottom groups
    print(f"\n[5] Verifying top {TOP_K} sequences (extended BM + name check)...")
    top_results = []
    for i, sid in enumerate(top_ids):
        terms = sampled[sid]
        result = verify_sequence(sid, terms, names_db, BM_MAX_DEGREE)
        result["enrichment_score"] = scores[sid]["geo_mean_enrichment"]
        result["enrichment_rank"] = i + 1
        result["group"] = "top"
        top_results.append(result)
        if (i + 1) % 20 == 0:
            print(f"    Verified {i + 1}/{TOP_K}...")

    print(f"\n[6] Verifying bottom {BOTTOM_K} sequences (control group)...")
    bottom_results = []
    for i, sid in enumerate(bottom_ids):
        terms = sampled[sid]
        result = verify_sequence(sid, terms, names_db, BM_MAX_DEGREE)
        result["enrichment_score"] = scores[sid]["geo_mean_enrichment"]
        result["enrichment_rank"] = len(ranked) - BOTTOM_K + i + 1
        result["group"] = "bottom"
        bottom_results.append(result)
        if (i + 1) % 20 == 0:
            print(f"    Verified {i + 1}/{BOTTOM_K}...")

    # Step 7: Analyze results
    print("\n[7] Analyzing detection rates...")

    top_bm_all = sum(1 for r in top_results if r["bm_verified"])
    top_bm_missed = sum(1 for r in top_results if r["bm_was_missed"])  # deg 9-12
    top_bm_low = sum(1 for r in top_results if r["bm_low_degree"])  # deg 1-8
    top_name = sum(1 for r in top_results if r["name_match"])
    top_either = sum(1 for r in top_results if r["bm_verified"] or r["name_match"])
    top_novel = sum(1 for r in top_results if r["bm_was_missed"] or (r["name_match"] and not r["bm_verified"]))

    bottom_bm_all = sum(1 for r in bottom_results if r["bm_verified"])
    bottom_bm_missed = sum(1 for r in bottom_results if r["bm_was_missed"])
    bottom_bm_low = sum(1 for r in bottom_results if r["bm_low_degree"])
    bottom_name = sum(1 for r in bottom_results if r["name_match"])
    bottom_either = sum(1 for r in bottom_results if r["bm_verified"] or r["name_match"])
    bottom_novel = sum(1 for r in bottom_results if r["bm_was_missed"] or (r["name_match"] and not r["bm_verified"]))

    print(f"\n  {'Metric':<35} {'Top 100':>10} {'Bottom 100':>12} {'Ratio':>8}")
    print(f"  {'-'*35} {'-'*10} {'-'*12} {'-'*8}")
    print(f"  {'BM recurrence (ALL degrees)':<35} {top_bm_all:>10} {bottom_bm_all:>12} {top_bm_all/max(bottom_bm_all,1):>8.1f}x")
    print(f"  {'  deg 1-8 (low, already known)':<35} {top_bm_low:>10} {bottom_bm_low:>12} {top_bm_low/max(bottom_bm_low,1):>8.1f}x")
    print(f"  {'  deg 9-12 (HIDDEN, missed by C08)':<35} {top_bm_missed:>10} {bottom_bm_missed:>12} {top_bm_missed/max(bottom_bm_missed,1):>8.1f}x")
    print(f"  {'Name match (algebraic keywords)':<35} {top_name:>10} {bottom_name:>12} {top_name/max(bottom_name,1):>8.1f}x")
    print(f"  {'Either signal':<35} {top_either:>10} {bottom_either:>12} {top_either/max(bottom_either,1):>8.1f}x")
    print(f"  {'Novel discoveries (deg>8 or name)':<35} {top_novel:>10} {bottom_novel:>12} {top_novel/max(bottom_novel,1):>8.1f}x")

    # BM degree distribution in top
    top_bm_degrees = [r["bm_degree"] for r in top_results if r["bm_verified"]]
    bottom_bm_degrees = [r["bm_degree"] for r in bottom_results if r["bm_verified"]]

    if top_bm_degrees:
        print(f"\n  Top group BM degree distribution: {Counter(top_bm_degrees).most_common()}")
    if bottom_bm_degrees:
        print(f"  Bottom group BM degree distribution: {Counter(bottom_bm_degrees).most_common()}")

    # Specific discoveries
    print(f"\n  Top group discoveries (BM verified):")
    for r in top_results:
        if r["bm_verified"]:
            print(f"    {r['seq_id']} deg={r['bm_degree']} score={r['enrichment_score']:.3f} — {r['name'][:80]}")

    print(f"\n  Top group discoveries (name match only):")
    for r in top_results:
        if r["name_match"] and not r["bm_verified"]:
            kws = ", ".join(r["name_keywords"])
            print(f"    {r['seq_id']} score={r['enrichment_score']:.3f} kw=[{kws}] — {r['name'][:80]}")

    # False positive rate
    # "True positive" = has hidden recurrence or algebraic description
    tp_top = top_either
    tp_bottom = bottom_either

    precision_top = tp_top / TOP_K if TOP_K > 0 else 0
    precision_bottom = tp_bottom / BOTTOM_K if BOTTOM_K > 0 else 0

    # Novel precision: only count deg 9-12 or name-only matches
    novel_prec_top = top_novel / TOP_K if TOP_K > 0 else 0
    novel_prec_bottom = bottom_novel / BOTTOM_K if BOTTOM_K > 0 else 0

    print(f"\n  Precision (all, top 100): {precision_top:.1%}")
    print(f"  Precision (all, bottom 100): {precision_bottom:.1%}")
    print(f"  Lift (all): {precision_top / max(precision_bottom, 0.001):.2f}x")
    print(f"  Precision (novel, top 100): {novel_prec_top:.1%}")
    print(f"  Precision (novel, bottom 100): {novel_prec_bottom:.1%}")
    print(f"  Lift (novel): {novel_prec_top / max(novel_prec_bottom, 0.001):.2f}x")

    # List hidden discoveries (deg 9-12)
    print(f"\n  HIDDEN recurrences (deg 9-12) in top group:")
    for r in top_results:
        if r["bm_was_missed"]:
            print(f"    {r['seq_id']} deg={r['bm_degree']} score={r['enrichment_score']:.3f} -- {r['name'][:80]}")

    # Step 8: Differential fingerprint — try first-differences mod p
    # This might detect higher-order recurrences that raw terms miss
    print(f"\n[8] Differential fingerprint analysis...")
    diff_fingerprints = {}
    for sid, terms in sampled.items():
        if len(terms) < FP_LEN + 1:
            continue
        diffs = [terms[i+1] - terms[i] for i in range(FP_LEN)]
        fp = multi_prime_fingerprint(diffs, PRIMES, FP_LEN)
        if fp is not None:
            diff_fingerprints[sid] = fp

    diff_scores = compute_enrichment_scores(diff_fingerprints, PRIMES)
    diff_ranked = sorted(diff_scores.items(), key=lambda x: x[1]["geo_mean_enrichment"], reverse=True)

    # Combined score: raw + differential
    combined = {}
    for sid in scores:
        raw = scores[sid]["geo_mean_enrichment"]
        diff = diff_scores.get(sid, {}).get("geo_mean_enrichment", 0)
        combined[sid] = raw + diff

    combined_ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)

    # Verify top 100 by combined score
    comb_top_ids = [sid for sid, _ in combined_ranked[:TOP_K]]
    comb_bottom_ids = [sid for sid, _ in combined_ranked[-BOTTOM_K:]]

    print(f"  Verifying combined-score top {TOP_K}...")
    comb_top_results = []
    for sid in comb_top_ids:
        terms = sampled[sid]
        result = verify_sequence(sid, terms, names_db, BM_MAX_DEGREE)
        result["combined_score"] = combined[sid]
        comb_top_results.append(result)

    comb_bottom_results = []
    for sid in comb_bottom_ids:
        terms = sampled[sid]
        result = verify_sequence(sid, terms, names_db, BM_MAX_DEGREE)
        result["combined_score"] = combined[sid]
        comb_bottom_results.append(result)

    ct_bm = sum(1 for r in comb_top_results if r["bm_verified"])
    ct_hidden = sum(1 for r in comb_top_results if r["bm_was_missed"])
    ct_name = sum(1 for r in comb_top_results if r["name_match"])
    cb_bm = sum(1 for r in comb_bottom_results if r["bm_verified"])
    cb_hidden = sum(1 for r in comb_bottom_results if r["bm_was_missed"])
    cb_name = sum(1 for r in comb_bottom_results if r["name_match"])

    print(f"  Combined score detection (top vs bottom 100):")
    print(f"    BM all:    {ct_bm} vs {cb_bm} ({ct_bm/max(cb_bm,1):.1f}x)")
    print(f"    BM hidden: {ct_hidden} vs {cb_hidden} ({ct_hidden/max(cb_hidden,1):.1f}x)")
    print(f"    Name:      {ct_name} vs {cb_name} ({ct_name/max(cb_name,1):.1f}x)")

    if ct_hidden > 0:
        print(f"\n  Combined-score HIDDEN discoveries:")
        for r in comb_top_results:
            if r["bm_was_missed"]:
                print(f"    {r['seq_id']} deg={r['bm_degree']} cscore={r['combined_score']:.3f} -- {r['name'][:80]}")

    # Step 9: Check if top 5% has consistently higher algebraic content
    # Do a broader sweep: check all with BM (just name-match since BM is slow)
    print(f"\n[9] Broad name-match sweep across full ranking...")
    decile_hits = defaultdict(int)
    decile_total = defaultdict(int)
    for i, (sid, score_data) in enumerate(ranked):
        decile = min(i * 10 // len(ranked), 9)
        name = names_db.get(sid, "")
        has_match, _ = check_name_for_algebraic(name)
        decile_hits[decile] += int(has_match)
        decile_total[decile] += 1

    print(f"\n  {'Decile':<10} {'Name hits':>12} {'Total':>8} {'Rate':>8}")
    print(f"  {'-'*10} {'-'*12} {'-'*8} {'-'*8}")
    for d in range(10):
        rate = decile_hits[d] / max(decile_total[d], 1)
        label = "TOP" if d == 0 else ("BOT" if d == 9 else f"  {d}")
        print(f"  {label:<10} {decile_hits[d]:>12} {decile_total[d]:>8} {rate:>8.1%}")

    elapsed = time.time() - t0

    # Build output
    output = {
        "challenge": "M6",
        "title": "Scaling Detector — Inverting the Scaling Law",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "parameters": {
            "n_sample": len(sampled),
            "primes": PRIMES,
            "fingerprint_length": FP_LEN,
            "bm_max_degree": BM_MAX_DEGREE,
            "top_k": TOP_K,
            "bottom_k": BOTTOM_K
        },
        "score_distribution": {
            "min": round(min(all_geo), 6),
            "median": round(float(np.median(all_geo)), 6),
            "mean": round(float(np.mean(all_geo)), 6),
            "max": round(max(all_geo), 6),
            "std": round(float(np.std(all_geo)), 6),
            "top_5pct_threshold": round(top_5pct_threshold, 6)
        },
        "detection_rates": {
            "top_100": {
                "bm_recurrence_all": top_bm_all,
                "bm_low_degree": top_bm_low,
                "bm_hidden_deg9_12": top_bm_missed,
                "name_match": top_name,
                "either": top_either,
                "novel": top_novel,
                "precision_all": round(precision_top, 4),
                "precision_novel": round(novel_prec_top, 4),
                "bm_degrees": dict(Counter(top_bm_degrees))
            },
            "bottom_100": {
                "bm_recurrence_all": bottom_bm_all,
                "bm_low_degree": bottom_bm_low,
                "bm_hidden_deg9_12": bottom_bm_missed,
                "name_match": bottom_name,
                "either": bottom_either,
                "novel": bottom_novel,
                "precision_all": round(precision_bottom, 4),
                "precision_novel": round(novel_prec_bottom, 4),
                "bm_degrees": dict(Counter(bottom_bm_degrees))
            },
            "lift_either": round(top_either / max(bottom_either, 1), 2),
            "lift_bm_all": round(top_bm_all / max(bottom_bm_all, 1), 2),
            "lift_bm_hidden": round(top_bm_missed / max(bottom_bm_missed, 1), 2),
            "lift_novel": round(top_novel / max(bottom_novel, 1), 2)
        },
        "decile_name_rates": {
            str(d): {
                "hits": decile_hits[d],
                "total": decile_total[d],
                "rate": round(decile_hits[d] / max(decile_total[d], 1), 4)
            } for d in range(10)
        },
        "top_100_details": top_results,
        "bottom_100_details": bottom_results,
        "top_discoveries_bm_all": [r for r in top_results if r["bm_verified"]],
        "top_discoveries_bm_hidden": [r for r in top_results if r["bm_was_missed"]],
        "top_discoveries_name": [r for r in top_results if r["name_match"] and not r["bm_verified"]],
        "combined_score_detection": {
            "top_100": {
                "bm_all": ct_bm, "bm_hidden": ct_hidden, "name_match": ct_name
            },
            "bottom_100": {
                "bm_all": cb_bm, "bm_hidden": cb_hidden, "name_match": cb_name
            },
            "top_hidden_discoveries": [r for r in comb_top_results if r["bm_was_missed"]]
        }
    }

    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\n  Results saved to {OUT_FILE.name}")
    print(f"  Elapsed: {elapsed:.1f}s")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Sampled {len(sampled):,} unlabeled OEIS sequences")
    print(f"  Enrichment score range: [{min(all_geo):.4f}, {max(all_geo):.4f}]")
    print(f"  Top 5% threshold: {top_5pct_threshold:.4f}")
    print(f"  Detection (top 100 vs bottom 100):")
    print(f"    BM (all):      {top_bm_all} vs {bottom_bm_all} ({top_bm_all/max(bottom_bm_all,1):.1f}x)")
    print(f"    BM (hidden):   {top_bm_missed} vs {bottom_bm_missed} ({top_bm_missed/max(bottom_bm_missed,1):.1f}x)")
    print(f"    Name match:    {top_name} vs {bottom_name} ({top_name/max(bottom_name,1):.1f}x)")
    print(f"    Novel:         {top_novel} vs {bottom_novel} ({top_novel/max(bottom_novel,1):.1f}x)")
    verdict = "WORKING" if top_novel > 2 * bottom_novel else "MARGINAL" if top_novel > bottom_novel else "FAILED"
    print(f"  Verdict: {verdict}")
    print("=" * 70)

    return output


if __name__ == "__main__":
    main()
