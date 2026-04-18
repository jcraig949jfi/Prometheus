"""
Charon: OEIS Bridge Scan v2
Scan 394K OEIS sequences for cross-domain bridges to EC conductors and NF discriminants.

KEY INSIGHT from v1: EC conductors < 500K are ~60% of integers (squarefree density 6/pi^2).
Raw enrichment against conductors is meaningless -- it just tests "are terms squarefree?"

v2 approach:
  1. EXACT MATCH: find OEIS sequences whose terms are literally EC conductors or NF discriminants
     (e.g., A005117 = squarefree numbers, A014603 = imaginary quad field discriminants)
  2. STRUCTURAL ENRICHMENT: for sequences NOT about primes/squarefree, test whether their
     terms hit the GAPS in conductor/discriminant coverage at different rates than random.
     The ~40% of integers that are NOT conductors are the interesting signal.
  3. NF discriminant enrichment against FUNDAMENTAL discriminant baseline.
  4. EC conductor MULTIPLICITY: how many curves share each conductor? Match OEIS terms
     against high-multiplicity conductors (arithmetic significance).
"""

import json
import os
import sys
import time
import random
import math
import psycopg2
import numpy as np
from collections import defaultdict, Counter
from datetime import datetime

DB_SCI = dict(host="localhost", port=5432, user="postgres", password="prometheus", dbname="prometheus_sci")
DB_LMFDB = dict(host="localhost", port=5432, user="postgres", password="prometheus", dbname="lmfdb")

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "oeis_bridge_scan.json")

# Known trivial sequences
TRIVIAL_SEQS = {
    "A000040", "A000041", "A000079", "A000142", "A000290", "A000578",
    "A000010", "A002808", "A006530", "A001358", "A005117", "A000961",
    "A002110", "A005843", "A005408",  # squarefree, prime powers, primorial, even, odd
}


def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True


def is_squarefree(n):
    if n < 1: return False
    if n == 1: return True
    i = 2
    while i * i <= n:
        if n % (i * i) == 0: return False
        i += 1
    return True


def load_ec_conductor_multiplicities():
    """Load EC conductor -> number of curves (multiplicity), capped at 100K."""
    print("[1/7] Loading EC conductor multiplicities...")
    conn = psycopg2.connect(**DB_LMFDB)
    cur = conn.cursor()
    cur.execute("""
        SELECT CAST(conductor AS bigint) as cond, COUNT(*) as n_curves
        FROM ec_curvedata
        WHERE CAST(conductor AS bigint) < 100000
        GROUP BY cond
    """)
    mult = {row[0]: row[1] for row in cur.fetchall()}
    cur.close()
    conn.close()
    # High-multiplicity conductors (>=10 curves) -- these are arithmetically special
    high_mult = {c for c, m in mult.items() if m >= 10}
    print(f"  -> {len(mult)} distinct conductors, {len(high_mult)} high-multiplicity (>=10 curves)")
    return set(mult.keys()), high_mult, mult


def load_nf_discriminants_by_degree():
    """Load NF discriminants < 100K, grouped by degree."""
    print("[2/7] Loading NF discriminants by degree...")
    conn = psycopg2.connect(**DB_LMFDB)
    cur = conn.cursor()
    # Fundamental discriminants: degree-2 fields
    cur.execute("""
        SELECT DISTINCT CAST(disc_abs AS numeric)::bigint
        FROM nf_fields
        WHERE CAST(disc_abs AS numeric) < 100000 AND CAST(degree AS int) = 2
    """)
    fund_discs = set(row[0] for row in cur.fetchall())

    # All discriminants
    cur.execute("""
        SELECT DISTINCT CAST(disc_abs AS numeric)::bigint
        FROM nf_fields
        WHERE CAST(disc_abs AS numeric) < 100000
    """)
    all_discs = set(row[0] for row in cur.fetchall())

    # Higher-degree only (degree >= 3)
    cur.execute("""
        SELECT DISTINCT CAST(disc_abs AS numeric)::bigint
        FROM nf_fields
        WHERE CAST(disc_abs AS numeric) < 100000 AND CAST(degree AS int) >= 3
    """)
    high_deg_discs = set(row[0] for row in cur.fetchall())

    cur.close()
    conn.close()
    print(f"  -> {len(all_discs)} total, {len(fund_discs)} fundamental (deg-2), {len(high_deg_discs)} higher-degree (>=3)")
    return all_discs, fund_discs, high_deg_discs


def load_all_oeis_sequences(min_terms=8):
    """Load ALL OEIS sequences (not just a sample) with enough terms."""
    print(f"[3/7] Loading ALL OEIS sequences (min_terms={min_terms})...")
    conn = psycopg2.connect(**DB_SCI)
    cur = conn.cursor()
    cur.execute("""
        SELECT oeis_id, name, first_terms
        FROM analysis.oeis
        WHERE array_length(first_terms, 1) >= %s
    """, (min_terms,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    print(f"  -> Loaded {len(rows)} sequences")
    return rows


def compute_prime_fraction(terms):
    eligible = [t for t in terms if 2 <= t <= 100000]
    if len(eligible) < 3:
        return 0.0, 0
    return sum(1 for t in eligible if is_prime(t)) / len(eligible), len(eligible)


def compute_squarefree_fraction(terms):
    eligible = [t for t in terms if 1 <= t <= 100000]
    if len(eligible) < 3:
        return 0.0, 0
    return sum(1 for t in eligible if is_squarefree(t)) / len(eligible), len(eligible)


def enrichment_vs_set(terms, target_set, range_max=100000):
    """Hit rate against a target set, with expected density from set size."""
    eligible = [t for t in terms if 2 <= t <= range_max]
    if len(eligible) < 5:
        return None
    hits = sum(1 for t in eligible if t in target_set)
    density = len(target_set) / range_max
    expected = density * len(eligible)
    enrich = hits / expected if expected > 0 else 0
    return {"hits": hits, "eligible": len(eligible), "enrichment": round(enrich, 4),
            "density": round(density, 4), "expected": round(expected, 2)}


def jaccard_similarity(terms_set, target_set):
    """Jaccard similarity between two sets."""
    inter = len(terms_set & target_set)
    union = len(terms_set | target_set)
    return inter / union if union > 0 else 0


def run_scan():
    t0 = time.time()

    # Load reference data
    ec_conductors, ec_high_mult, ec_mult_map = load_ec_conductor_multiplicities()
    all_discs, fund_discs, high_deg_discs = load_nf_discriminants_by_degree()

    # Build NON-conductor set (the 40% that are NOT squarefree)
    non_conductors = set(range(2, 100001)) - ec_conductors
    print(f"  Non-conductor integers [2,100K]: {len(non_conductors)} ({len(non_conductors)/99999*100:.1f}%)")

    # Build fundamental discriminant set for enrichment
    # Fundamental discriminants are: 1, or d where d is squarefree and d=1 mod 4, or 4d where d squarefree and d=2,3 mod 4
    # But we use the actual DB values instead
    fund_disc_only = fund_discs - high_deg_discs  # discriminants that appear ONLY as degree-2

    # Build squarefree reference for baseline
    squarefree_set = {n for n in range(1, 100001) if is_squarefree(n)}
    print(f"  Squarefree integers [1,100K]: {len(squarefree_set)} ({len(squarefree_set)/100000*100:.1f}%)")

    # Load OEIS
    sequences = load_all_oeis_sequences(min_terms=8)

    # ===== SCAN 1: High-multiplicity conductor enrichment =====
    print("\n[4/7] Scan 1: High-multiplicity conductor enrichment...")
    # High-mult conductors are ~5-10% of integers -- much more selective
    hm_density = len(ec_high_mult) / 100000
    print(f"  High-mult conductor density: {hm_density*100:.2f}%")

    results_hm = []
    prime_dominated = 0

    for oeis_id, name, terms in sequences:
        if oeis_id in TRIVIAL_SEQS:
            continue
        terms_int = [int(t) for t in terms if t is not None]
        prime_frac, n_elig = compute_prime_fraction(terms_int)
        is_pd = prime_frac > 0.6 and n_elig >= 5
        if is_pd:
            prime_dominated += 1

        r = enrichment_vs_set(terms_int, ec_high_mult)
        if r and r["enrichment"] > 1.5 and r["hits"] >= 3:
            results_hm.append({
                "oeis_id": oeis_id, "name": name[:120],
                "prime_dominated": is_pd, "prime_fraction": round(prime_frac, 3),
                **r
            })

    results_hm.sort(key=lambda x: x["enrichment"], reverse=True)
    hm_detrended = [r for r in results_hm if not r["prime_dominated"]]
    print(f"  Enriched >1.5x: {len(results_hm)} total, {len(hm_detrended)} after prime detrend")

    # ===== SCAN 2: Fundamental discriminant enrichment =====
    print("\n[5/7] Scan 2: Fundamental discriminant (deg-2 only) enrichment...")
    fd_density = len(fund_disc_only) / 100000
    print(f"  Fund disc density: {fd_density*100:.2f}%")

    results_fd = []
    for oeis_id, name, terms in sequences:
        if oeis_id in TRIVIAL_SEQS:
            continue
        terms_int = [int(t) for t in terms if t is not None]
        prime_frac, _ = compute_prime_fraction(terms_int)
        is_pd = prime_frac > 0.6

        r = enrichment_vs_set(terms_int, fund_disc_only)
        if r and r["enrichment"] > 1.5 and r["hits"] >= 3:
            results_fd.append({
                "oeis_id": oeis_id, "name": name[:120],
                "prime_dominated": is_pd, "prime_fraction": round(prime_frac, 3),
                **r
            })

    results_fd.sort(key=lambda x: x["enrichment"], reverse=True)
    fd_detrended = [r for r in results_fd if not r["prime_dominated"]]
    print(f"  Enriched >1.5x: {len(results_fd)} total, {len(fd_detrended)} after prime detrend")

    # ===== SCAN 3: Higher-degree discriminant enrichment =====
    print("\n[6/7] Scan 3: Higher-degree (>=3) discriminant enrichment...")
    hd_density = len(high_deg_discs) / 100000
    print(f"  High-deg disc density: {hd_density*100:.2f}%")

    results_hd = []
    for oeis_id, name, terms in sequences:
        if oeis_id in TRIVIAL_SEQS:
            continue
        terms_int = [int(t) for t in terms if t is not None]
        prime_frac, _ = compute_prime_fraction(terms_int)
        is_pd = prime_frac > 0.6

        r = enrichment_vs_set(terms_int, high_deg_discs)
        if r and r["enrichment"] > 1.5 and r["hits"] >= 3:
            results_hd.append({
                "oeis_id": oeis_id, "name": name[:120],
                "prime_dominated": is_pd, "prime_fraction": round(prime_frac, 3),
                **r
            })

    results_hd.sort(key=lambda x: x["enrichment"], reverse=True)
    hd_detrended = [r for r in results_hd if not r["prime_dominated"]]
    print(f"  Enriched >1.5x: {len(results_hd)} total, {len(hd_detrended)} after prime detrend")

    # ===== SCAN 4: Non-squarefree enrichment (anti-conductor signal) =====
    # Sequences whose terms preferentially AVOID conductors (= hit non-squarefree numbers)
    print("\n[6.5/7] Scan 4: Non-squarefree enrichment (anti-conductor)...")
    nonsqf_density = len(non_conductors) / 99999
    print(f"  Non-squarefree density: {nonsqf_density*100:.1f}%")

    results_anti = []
    for oeis_id, name, terms in sequences:
        if oeis_id in TRIVIAL_SEQS:
            continue
        terms_int = [int(t) for t in terms if t is not None]
        prime_frac, _ = compute_prime_fraction(terms_int)
        is_pd = prime_frac > 0.6

        r = enrichment_vs_set(terms_int, non_conductors)
        if r and r["enrichment"] > 1.5 and r["hits"] >= 3:
            results_anti.append({
                "oeis_id": oeis_id, "name": name[:120],
                "prime_dominated": is_pd, "prime_fraction": round(prime_frac, 3),
                **r
            })

    results_anti.sort(key=lambda x: x["enrichment"], reverse=True)
    anti_detrended = [r for r in results_anti if not r["prime_dominated"]]
    print(f"  Anti-conductor enriched >1.5x: {len(results_anti)} total, {len(anti_detrended)} after prime detrend")

    # ===== SCAN 5: Exact sequence matches =====
    # Check if any OEIS sequence names contain "conductor", "discriminant", "elliptic"
    print("\n[6.8/7] Scan 5: Name-based exact matches...")
    keywords = ["conductor", "discriminant", "elliptic curve", "number field",
                "modular form", "class number", "fundamental discriminant",
                "cremona", "isogeny", "L-function"]
    name_matches = defaultdict(list)
    for oeis_id, name, terms in sequences:
        name_lower = name.lower()
        for kw in keywords:
            if kw in name_lower:
                terms_int = [int(t) for t in terms if t is not None]
                name_matches[kw].append({
                    "oeis_id": oeis_id,
                    "name": name[:150],
                    "n_terms": len(terms_int),
                    "first_5": terms_int[:5],
                })

    for kw, matches in name_matches.items():
        print(f"  '{kw}': {len(matches)} sequences")

    # ===== NULL DISTRIBUTION for high-mult conductors =====
    print("\n  Computing null distribution for high-mult conductors...")
    null_hm_enrichments = []
    for _ in range(2000):
        rand_terms = [random.randint(2, 100000) for _ in range(15)]
        hits = sum(1 for t in rand_terms if t in ec_high_mult)
        expected = hm_density * 15
        null_hm_enrichments.append(hits / expected if expected > 0 else 0)
    null_hm_mean = np.mean(null_hm_enrichments)
    null_hm_std = np.std(null_hm_enrichments)
    print(f"  Null high-mult: mean={null_hm_mean:.3f}, std={null_hm_std:.3f}")

    # Add z-scores to high-mult results
    for r in results_hm:
        r["z_score"] = round((r["enrichment"] - null_hm_mean) / null_hm_std, 2) if null_hm_std > 0 else 0

    # ===== BUILD OUTPUT =====
    print("\n[7/7] Building output...")
    output = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "n_sequences_scanned": len(sequences),
            "reference_sets": {
                "ec_conductors_100k": len(ec_conductors),
                "ec_high_mult_conductors": len(ec_high_mult),
                "nf_disc_all": len(all_discs),
                "nf_disc_fundamental": len(fund_discs),
                "nf_disc_fund_only": len(fund_disc_only),
                "nf_disc_high_degree": len(high_deg_discs),
                "squarefree_100k": len(squarefree_set),
            },
            "densities_pct": {
                "ec_conductor": round(len(ec_conductors)/100000*100, 2),
                "ec_high_mult": round(hm_density*100, 2),
                "nf_fund_disc": round(fd_density*100, 2),
                "nf_high_deg_disc": round(hd_density*100, 2),
                "squarefree": round(len(squarefree_set)/100000*100, 2),
            },
            "prime_dominated_sequences": prime_dominated,
            "critical_finding": (
                "EC conductors <100K cover 62.6% of integers (= squarefree density 6/pi^2). "
                "Raw conductor enrichment is equivalent to testing squarefree-ness. "
                "v2 uses high-multiplicity conductors and fundamental discriminants for real signal."
            ),
            "runtime_seconds": round(time.time() - t0, 1),
        },
        "scan1_high_mult_conductors": {
            "description": "OEIS sequences enriched for high-multiplicity EC conductors (>=10 curves per conductor)",
            "total_enriched": len(results_hm),
            "after_prime_detrend": len(hm_detrended),
            "top_30_detrended": hm_detrended[:30],
        },
        "scan2_fundamental_discriminants": {
            "description": "OEIS sequences enriched for fundamental discriminants (degree-2 NF only)",
            "total_enriched": len(results_fd),
            "after_prime_detrend": len(fd_detrended),
            "top_30_detrended": fd_detrended[:30],
        },
        "scan3_higher_degree_discriminants": {
            "description": "OEIS sequences enriched for higher-degree (>=3) NF discriminants",
            "total_enriched": len(results_hd),
            "after_prime_detrend": len(hd_detrended),
            "top_30_detrended": hd_detrended[:30],
        },
        "scan4_anti_conductor": {
            "description": "OEIS sequences enriched for NON-squarefree numbers (anti-conductor signal)",
            "total_enriched": len(results_anti),
            "after_prime_detrend": len(anti_detrended),
            "top_30_detrended": anti_detrended[:30],
        },
        "scan5_name_matches": {k: v for k, v in name_matches.items()},
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {OUTPUT_PATH}")
    print(f"Total runtime: {time.time() - t0:.1f}s")

    # Print summaries
    print("\n" + "="*90)
    print("SCAN 1: HIGH-MULTIPLICITY CONDUCTOR BRIDGES (detrended)")
    print("="*90)
    for r in hm_detrended[:20]:
        print(f"  {r['oeis_id']:8s} | enrich={r['enrichment']:6.2f}x | z={r.get('z_score','?'):>6} | "
              f"hits={r['hits']:3d}/{r['eligible']:3d} | prime={r['prime_fraction']:.0%} | {r['name'][:55]}")

    print("\n" + "="*90)
    print("SCAN 2: FUNDAMENTAL DISCRIMINANT BRIDGES (detrended)")
    print("="*90)
    for r in fd_detrended[:20]:
        print(f"  {r['oeis_id']:8s} | enrich={r['enrichment']:6.2f}x | "
              f"hits={r['hits']:3d}/{r['eligible']:3d} | prime={r['prime_fraction']:.0%} | {r['name'][:55]}")

    print("\n" + "="*90)
    print("SCAN 3: HIGHER-DEGREE DISCRIMINANT BRIDGES (detrended)")
    print("="*90)
    for r in hd_detrended[:20]:
        print(f"  {r['oeis_id']:8s} | enrich={r['enrichment']:6.2f}x | "
              f"hits={r['hits']:3d}/{r['eligible']:3d} | prime={r['prime_fraction']:.0%} | {r['name'][:55]}")

    print("\n" + "="*90)
    print("SCAN 4: ANTI-CONDUCTOR (non-squarefree enriched) BRIDGES (detrended)")
    print("="*90)
    for r in anti_detrended[:20]:
        print(f"  {r['oeis_id']:8s} | enrich={r['enrichment']:6.2f}x | "
              f"hits={r['hits']:3d}/{r['eligible']:3d} | prime={r['prime_fraction']:.0%} | {r['name'][:55]}")

    print("\n" + "="*90)
    print("SCAN 5: NAME-BASED MATCHES")
    print("="*90)
    for kw, matches in name_matches.items():
        if matches:
            print(f"\n  --- {kw} ({len(matches)} matches) ---")
            for m in matches[:5]:
                print(f"    {m['oeis_id']:8s} | terms={m['n_terms']:3d} | first5={m['first_5']} | {m['name'][:60]}")

    return output


if __name__ == "__main__":
    run_scan()
