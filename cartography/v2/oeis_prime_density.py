#!/usr/bin/env python3
"""
Prime Density in OEIS Sequences
================================
What fraction of OEIS sequence terms are prime? Does this correlate with
mathematical family, BM recurrence, or growth rate?

Method:
  1. Parse 5000 OEIS sequences with 20+ terms from stripped_new.txt
  2. For each: compute fraction of terms that are prime (sympy for < 10^15,
     trial division fallback)
  3. Distribution of prime density across OEIS
  4. Compare to theoretical 1/ln(n) density for random integers of same magnitude
  5. Group by keyword family (number-theoretic vs combinatorial etc.)
  6. Correlate with BM recurrence order (from prior analysis)
  7. Identify sequences with anomalously high prime density (> 50%)
"""

import json
import math
import numpy as np
from pathlib import Path
from collections import defaultdict
import time
import random

DATA_FILE = Path(__file__).parent.parent / "oeis" / "data" / "stripped_new.txt"
KEYWORDS_FILE = Path(__file__).parent.parent / "oeis" / "data" / "oeis_keywords.json"
NAMES_FILE = Path(__file__).parent.parent / "oeis" / "data" / "oeis_names.json"
BM_FILE = Path(__file__).parent / "oeis_bm_order_results.json"
OUT_FILE = Path(__file__).parent / "oeis_prime_density_results.json"

MIN_TERMS = 20
N_SEQUENCES = 5000


# ---------------------------------------------------------------------------
# Primality testing
# ---------------------------------------------------------------------------

# Small primes sieve for trial division
SMALL_PRIMES = []
def _build_small_primes(limit=10000):
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, limit + 1, i):
                sieve[j] = False
    return [i for i in range(2, limit + 1) if sieve[i]]

SMALL_PRIMES = _build_small_primes(10000)

def _miller_rabin(n, a):
    """Single Miller-Rabin witness test."""
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return True
    for _ in range(r - 1):
        x = pow(x, 2, n)
        if x == n - 1:
            return True
    return False

def is_prime(n):
    """
    Deterministic primality test for n < 3.317e24 using Miller-Rabin
    with specific witness sets. For practical OEIS terms (< 10^18) this
    is deterministic.
    """
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    # Trial division by small primes
    for p in SMALL_PRIMES:
        if p * p > n:
            return True
        if n % p == 0:
            return False
    # Deterministic MR witnesses for n < 3.317e24
    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    return all(_miller_rabin(n, a) for a in witnesses if a < n)


# ---------------------------------------------------------------------------
# Parse OEIS
# ---------------------------------------------------------------------------

def parse_sequences(path, n_seqs, min_terms):
    """Parse stripped_new.txt, return dict {seq_id: [terms]}."""
    seqs = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.strip().split(' ', 1)
            if len(parts) < 2:
                continue
            seq_id = parts[0]
            raw = parts[1].strip().strip(',')
            if not raw:
                continue
            try:
                terms = [int(x) for x in raw.split(',') if x.strip()]
            except ValueError:
                continue
            if len(terms) >= min_terms:
                seqs[seq_id] = terms
            if len(seqs) >= n_seqs:
                break
    return seqs


def compute_prime_density(terms):
    """Compute fraction of positive terms that are prime."""
    positive = [t for t in terms if t > 1]
    if not positive:
        return 0.0, 0, 0
    n_prime = sum(1 for t in positive if is_prime(t))
    return n_prime / len(positive), n_prime, len(positive)


def expected_prime_density(terms):
    """
    Expected prime density for random integers of the same magnitudes.
    Uses 1/ln(n) for n >= 2 (prime number theorem).
    """
    positive = [t for t in terms if t > 1]
    if not positive:
        return 0.0
    densities = [1.0 / math.log(t) if t >= 2 else 0.0 for t in positive]
    return float(np.mean(densities))


def classify_growth(terms):
    """Classify growth rate of a sequence."""
    if len(terms) < 5:
        return "unknown"
    pos = [abs(t) for t in terms if t != 0]
    if len(pos) < 5:
        return "zero-heavy"
    # Check last vs first magnitude
    last_5 = np.mean(pos[-5:])
    first_5 = np.mean(pos[:5])
    if first_5 == 0:
        return "from-zero"
    ratio = last_5 / first_5 if first_5 > 0 else 0
    n = len(pos)
    if ratio < 2:
        return "bounded"
    elif ratio < n:
        return "sublinear"
    elif ratio < n * n:
        return "linear-quadratic"
    elif ratio < n ** 4:
        return "polynomial"
    else:
        return "exponential"


# ---------------------------------------------------------------------------
# Keyword families
# ---------------------------------------------------------------------------

FAMILY_KEYWORDS = {
    "number_theoretic": {"nonn"},  # We'll refine below with names
    "combinatorial": {"walk", "comb"},
    "core": {"core"},
    "nice": {"nice"},
    "easy": {"easy"},
    "hard": {"hard"},
}

def keyword_families(seq_id, keywords_db):
    """Return set of family tags for a sequence."""
    kws = set(keywords_db.get(seq_id, []))
    families = set()
    for fam, target_kws in FAMILY_KEYWORDS.items():
        if kws & target_kws:
            families.add(fam)
    return families


def name_based_family(seq_id, names_db):
    """Classify by sequence name keywords."""
    name = names_db.get(seq_id, "").lower()
    families = set()
    nt_signals = ["prime", "divisor", "totient", "moebius", "sigma", "gcd",
                  "lcm", "factor", "square-free", "squarefree", "coprime",
                  "arithmetic", "euler phi"]
    comb_signals = ["catalan", "fibonacci", "partition", "binomial", "bell",
                    "stirling", "walk", "lattice", "path", "permutation",
                    "combination", "tree", "graph"]
    poly_signals = ["polynomial", "bernoulli", "legendre", "chebyshev",
                    "hermite", "laguerre"]
    for s in nt_signals:
        if s in name:
            families.add("number_theoretic")
            break
    for s in comb_signals:
        if s in name:
            families.add("combinatorial")
            break
    for s in poly_signals:
        if s in name:
            families.add("polynomial")
            break
    return families


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    print("Loading OEIS data...")
    seqs = parse_sequences(DATA_FILE, N_SEQUENCES, MIN_TERMS)
    print(f"  Loaded {len(seqs)} sequences with {MIN_TERMS}+ terms")

    # Load keywords
    keywords_db = {}
    if KEYWORDS_FILE.exists():
        with open(KEYWORDS_FILE) as f:
            keywords_db = json.load(f)
        print(f"  Keywords: {len(keywords_db)} entries")

    # Load names
    names_db = {}
    if NAMES_FILE.exists():
        with open(NAMES_FILE, encoding='utf-8') as f:
            names_db = json.load(f)
        print(f"  Names: {len(names_db)} entries")

    # Load BM order results if available
    bm_orders = {}
    if BM_FILE.exists():
        with open(BM_FILE) as f:
            bm_data = json.load(f)
        for entry in bm_data.get("per_sequence", []):
            bm_orders[entry["seq_id"]] = entry.get("bm_order")
        print(f"  BM orders: {len(bm_orders)} entries")

    # Compute prime density for each sequence
    print("Computing prime densities...")
    results = []
    densities = []
    expected_densities = []

    for i, (seq_id, terms) in enumerate(seqs.items()):
        if (i + 1) % 500 == 0:
            print(f"  {i+1}/{len(seqs)}...")

        density, n_prime, n_positive = compute_prime_density(terms)
        expected = expected_prime_density(terms)
        growth = classify_growth(terms)

        # Family classification
        families = keyword_families(seq_id, keywords_db)
        families |= name_based_family(seq_id, names_db)

        bm_order = bm_orders.get(seq_id)

        entry = {
            "seq_id": seq_id,
            "n_terms": len(terms),
            "n_positive_gt1": n_positive,
            "n_prime": n_prime,
            "prime_density": round(density, 6),
            "expected_density_pnt": round(expected, 6),
            "density_ratio": round(density / expected, 4) if expected > 0 else None,
            "growth_class": growth,
            "families": sorted(families),
            "bm_order": bm_order,
        }
        results.append(entry)
        densities.append(density)
        expected_densities.append(expected)

    densities = np.array(densities)
    expected_densities = np.array(expected_densities)

    # ---------------------------------------------------------------------------
    # Distribution statistics
    # ---------------------------------------------------------------------------
    print("\nComputing distribution statistics...")
    percentiles = [0, 5, 10, 25, 50, 75, 90, 95, 100]
    dist_stats = {
        "mean": round(float(np.mean(densities)), 6),
        "median": round(float(np.median(densities)), 6),
        "std": round(float(np.std(densities)), 6),
        "percentiles": {str(p): round(float(np.percentile(densities, p)), 6)
                        for p in percentiles},
        "zero_density_count": int(np.sum(densities == 0)),
        "above_50pct": int(np.sum(densities > 0.5)),
        "above_90pct": int(np.sum(densities > 0.9)),
    }

    # Expected vs actual comparison
    valid = expected_densities > 0
    if valid.sum() > 0:
        ratios = densities[valid] / expected_densities[valid]
        dist_stats["mean_density_ratio"] = round(float(np.mean(ratios)), 4)
        dist_stats["median_density_ratio"] = round(float(np.median(ratios)), 4)

    # Histogram bins
    bins = np.linspace(0, 1, 21)
    hist_counts, _ = np.histogram(densities, bins=bins)
    dist_stats["histogram"] = {
        f"{bins[i]:.2f}-{bins[i+1]:.2f}": int(hist_counts[i])
        for i in range(len(hist_counts))
    }

    # ---------------------------------------------------------------------------
    # Family comparison
    # ---------------------------------------------------------------------------
    print("Analyzing family comparisons...")
    family_stats = defaultdict(list)
    for r in results:
        for fam in r["families"]:
            family_stats[fam].append(r["prime_density"])
        if not r["families"]:
            family_stats["unclassified"].append(r["prime_density"])

    family_comparison = {}
    for fam, vals in sorted(family_stats.items()):
        arr = np.array(vals)
        family_comparison[fam] = {
            "count": len(vals),
            "mean_density": round(float(np.mean(arr)), 6),
            "median_density": round(float(np.median(arr)), 6),
            "std_density": round(float(np.std(arr)), 6),
            "above_50pct": int(np.sum(arr > 0.5)),
        }

    # ---------------------------------------------------------------------------
    # Growth class comparison
    # ---------------------------------------------------------------------------
    print("Analyzing growth class comparisons...")
    growth_stats = defaultdict(list)
    for r in results:
        growth_stats[r["growth_class"]].append(r["prime_density"])

    growth_comparison = {}
    for gc, vals in sorted(growth_stats.items()):
        arr = np.array(vals)
        growth_comparison[gc] = {
            "count": len(vals),
            "mean_density": round(float(np.mean(arr)), 6),
            "median_density": round(float(np.median(arr)), 6),
        }

    # ---------------------------------------------------------------------------
    # BM recurrence correlation
    # ---------------------------------------------------------------------------
    print("Analyzing BM correlation...")
    bm_corr = {}
    bm_pairs = [(r["bm_order"], r["prime_density"])
                for r in results if r["bm_order"] is not None]
    if len(bm_pairs) >= 10:
        bm_arr = np.array(bm_pairs)
        corr = float(np.corrcoef(bm_arr[:, 0], bm_arr[:, 1])[0, 1])
        bm_corr["n_with_bm_order"] = len(bm_pairs)
        bm_corr["pearson_r"] = round(corr, 4)

        # Group by BM order category
        bm_groups = defaultdict(list)
        for bm_ord, density in bm_pairs:
            if bm_ord <= 2:
                bm_groups["order_1-2"].append(density)
            elif bm_ord <= 5:
                bm_groups["order_3-5"].append(density)
            elif bm_ord <= 10:
                bm_groups["order_6-10"].append(density)
            else:
                bm_groups["order_11+"].append(density)

        bm_corr["by_order_group"] = {
            k: {"count": len(v), "mean_density": round(float(np.mean(v)), 6)}
            for k, v in sorted(bm_groups.items())
        }
    else:
        bm_corr["n_with_bm_order"] = len(bm_pairs)
        bm_corr["note"] = "Too few sequences with BM orders for correlation"

    # ---------------------------------------------------------------------------
    # Anomalous sequences (> 50% prime density)
    # ---------------------------------------------------------------------------
    print("Identifying anomalous sequences...")
    anomalous = sorted(
        [r for r in results if r["prime_density"] > 0.5],
        key=lambda x: -x["prime_density"]
    )
    # Add names
    for a in anomalous:
        a["name"] = names_db.get(a["seq_id"], "")

    # Top-10 highest density
    top10 = sorted(results, key=lambda x: -x["prime_density"])[:10]
    for t in top10:
        t["name"] = names_db.get(t["seq_id"], "")

    # Also find highest density_ratio (most enriched relative to PNT)
    enriched = sorted(
        [r for r in results if r["density_ratio"] is not None and r["density_ratio"] > 0],
        key=lambda x: -x["density_ratio"]
    )[:10]
    for e in enriched:
        e["name"] = names_db.get(e["seq_id"], "")

    # ---------------------------------------------------------------------------
    # Output
    # ---------------------------------------------------------------------------
    elapsed = time.time() - t0
    output = {
        "metadata": {
            "n_sequences": len(seqs),
            "min_terms": MIN_TERMS,
            "elapsed_seconds": round(elapsed, 1),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "distribution": dist_stats,
        "family_comparison": family_comparison,
        "growth_comparison": growth_comparison,
        "bm_correlation": bm_corr,
        "anomalous_high_density": [{
            "seq_id": a["seq_id"],
            "name": a["name"],
            "prime_density": a["prime_density"],
            "n_terms": a["n_terms"],
            "n_prime": a["n_prime"],
            "families": a["families"],
            "growth_class": a["growth_class"],
        } for a in anomalous[:50]],
        "top10_highest_density": [{
            "seq_id": t["seq_id"],
            "name": t["name"],
            "prime_density": t["prime_density"],
            "expected_density_pnt": t["expected_density_pnt"],
            "density_ratio": t["density_ratio"],
        } for t in top10],
        "top10_most_enriched_vs_pnt": [{
            "seq_id": e["seq_id"],
            "name": e["name"],
            "prime_density": e["prime_density"],
            "expected_density_pnt": e["expected_density_pnt"],
            "density_ratio": e["density_ratio"],
        } for e in enriched],
    }

    with open(OUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"PRIME DENSITY IN OEIS — SUMMARY")
    print(f"{'='*60}")
    print(f"Sequences analyzed: {len(seqs)}")
    print(f"Mean prime density:   {dist_stats['mean']:.4f}")
    print(f"Median prime density: {dist_stats['median']:.4f}")
    print(f"Std dev:              {dist_stats['std']:.4f}")
    print(f"Zero-density seqs:    {dist_stats['zero_density_count']}")
    print(f"Above 50% density:    {dist_stats['above_50pct']}")
    print(f"Above 90% density:    {dist_stats['above_90pct']}")
    if "mean_density_ratio" in dist_stats:
        print(f"Mean density/PNT:     {dist_stats['mean_density_ratio']:.4f}")
        print(f"Median density/PNT:   {dist_stats['median_density_ratio']:.4f}")

    print(f"\n--- Family Comparison ---")
    for fam, stats in sorted(family_comparison.items(), key=lambda x: -x[1]["mean_density"]):
        print(f"  {fam:25s} n={stats['count']:5d}  mean={stats['mean_density']:.4f}  median={stats['median_density']:.4f}")

    print(f"\n--- Growth Class Comparison ---")
    for gc, stats in sorted(growth_comparison.items(), key=lambda x: -x[1]["mean_density"]):
        print(f"  {gc:25s} n={stats['count']:5d}  mean={stats['mean_density']:.4f}  median={stats['median_density']:.4f}")

    print(f"\n--- Top 10 Highest Prime Density ---")
    for t in top10:
        print(f"  {t['seq_id']}  density={t['prime_density']:.4f}  ratio={t['density_ratio']}  {t['name'][:60]}")

    print(f"\n--- Top 10 Most Enriched vs PNT ---")
    for e in enriched:
        print(f"  {e['seq_id']}  density={e['prime_density']:.4f}  ratio={e['density_ratio']}  {e['name'][:60]}")

    print(f"\nElapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
