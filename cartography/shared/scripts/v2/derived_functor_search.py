"""
R4-3: Derived Sequence Functor Search
Find hidden cross-domain mappings by applying 6 functors to OEIS sequences
and matching derived fingerprints against EC a_p, other OEIS, and knot determinants.

Layer 3 functor search — most will fail; any success is significant.
"""

import json
import sys
import os
import time
import random
import math
from pathlib import Path
from collections import defaultdict
from functools import lru_cache

import numpy as np

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parents[4]  # F:/Prometheus
OEIS_FILE = REPO / "cartography" / "oeis" / "data" / "stripped_new.txt"
KNOTS_FILE = REPO / "cartography" / "knots" / "data" / "knots.json"
DUCKDB_FILE = REPO / "charon" / "data" / "charon.duckdb"
OUT_FILE = Path(__file__).resolve().parent / "derived_functor_results.json"

PRIMES_25 = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
FINGERPRINT_PRIMES = [2, 3, 5, 7, 11]
FINGERPRINT_LEN = 20
SAMPLE_SIZE = 1000
MIN_TERMS = 30

# ---------------------------------------------------------------------------
# Number theory helpers
# ---------------------------------------------------------------------------
def sieve_primes(n):
    """Sieve of Eratosthenes up to n."""
    if n < 2:
        return []
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j] = False
    return [i for i in range(2, n+1) if is_prime[i]]

def mobius_sieve(n):
    """Compute Mobius function for 1..n."""
    mu = [0] * (n + 1)
    mu[1] = 1
    is_prime = [True] * (n + 1)
    primes = []
    for i in range(2, n + 1):
        if is_prime[i]:
            primes.append(i)
            mu[i] = -1
        for p in primes:
            if i * p > n:
                break
            is_prime[i * p] = False
            if i % p == 0:
                mu[i * p] = 0
                break
            else:
                mu[i * p] = -mu[i]
    return mu

def divisors(n):
    """Return sorted list of divisors of n."""
    if n <= 0:
        return []
    divs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)

# Precompute
MAX_INDEX = 60  # max index we'll use for divisor-based functors
MU = mobius_sieve(MAX_INDEX)
DIVISOR_TABLE = {n: divisors(n) for n in range(1, MAX_INDEX + 1)}

# ---------------------------------------------------------------------------
# Functors
# ---------------------------------------------------------------------------
def F1_partial_sums(seq):
    """S(n) = sum_{k=0}^{n} a_k"""
    out = []
    s = 0
    for x in seq:
        s += x
        out.append(s)
    return out

def F2_first_differences(seq):
    """D(n) = a_{n+1} - a_n"""
    return [seq[i+1] - seq[i] for i in range(len(seq)-1)]

def F3_binomial_transform(seq):
    """B(n) = sum_{k=0}^{n} C(n,k) a_k"""
    n = len(seq)
    out = []
    for i in range(n):
        s = 0
        for k in range(i + 1):
            s += math.comb(i, k) * seq[k]
        out.append(s)
    return out

def F4_euler_transform(seq):
    """Euler transform via logarithmic derivative method.
    E(n) for n>=1 where a is 1-indexed (seq[0] = a_1).
    b(n) = (1/n) * sum_{d|n} a_d * d, then E via exponential."""
    N = min(len(seq), MAX_INDEX)
    if N < 2:
        return seq[:N]
    # a is 1-indexed: a[k] = seq[k-1]
    # Euler transform: if f(x) = prod_{k>=1} 1/(1-x^k)^{a_k}
    # then E(n) = coefficient of x^n in f(x)
    # Recurrence: E(0)=1, E(n) = (1/n)*sum_{k=1}^{n} b(k)*E(n-k)
    # where b(k) = sum_{d|k} d * a_d
    b = [0] * (N + 1)
    for k in range(1, N + 1):
        for d in DIVISOR_TABLE.get(k, []):
            if d <= len(seq):
                b[k] += d * seq[d - 1]
    E = [0] * (N + 1)
    E[0] = 1
    for n in range(1, N + 1):
        s = 0
        for k in range(1, n + 1):
            s += b[k] * E[n - k]
        E[n] = s // n if s % n == 0 else s / n
    # Return E[1..N] as integers (round if needed)
    return [int(round(E[i])) for i in range(1, N + 1)]

def F5_dirichlet_conv_id(seq):
    """(a * id)(n) = sum_{d|n} a_d * (n/d), 1-indexed."""
    N = min(len(seq), MAX_INDEX)
    out = []
    for n in range(1, N + 1):
        s = 0
        for d in DIVISOR_TABLE.get(n, []):
            if d <= len(seq):
                s += seq[d - 1] * (n // d)
        out.append(s)
    return out

def F6_mobius_inversion(seq):
    """sum_{d|n} mu(n/d) a_d, 1-indexed."""
    N = min(len(seq), MAX_INDEX)
    out = []
    for n in range(1, N + 1):
        s = 0
        for d in DIVISOR_TABLE.get(n, []):
            if d <= len(seq):
                s += MU[n // d] * seq[d - 1]
        out.append(s)
    return out

FUNCTORS = {
    "F1_partial_sums": F1_partial_sums,
    "F2_first_differences": F2_first_differences,
    "F3_binomial_transform": F3_binomial_transform,
    "F4_euler_transform": F4_euler_transform,
    "F5_dirichlet_conv_id": F5_dirichlet_conv_id,
    "F6_mobius_inversion": F6_mobius_inversion,
}

# ---------------------------------------------------------------------------
# Fingerprinting
# ---------------------------------------------------------------------------
def mod_fingerprint(seq, length=FINGERPRINT_LEN):
    """Compute mod-p fingerprints for p in FINGERPRINT_PRIMES.
    Returns a dict {p: tuple of (a_i mod p) for first `length` terms}."""
    if len(seq) < length:
        return None
    fps = {}
    for p in FINGERPRINT_PRIMES:
        fp = tuple(int(x) % p for x in seq[:length])
        fps[p] = fp
    return fps

def multi_prime_key(fps):
    """Create a hashable key from all prime fingerprints."""
    if fps is None:
        return None
    return tuple(fps[p] for p in FINGERPRINT_PRIMES)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_oeis_sequences(min_terms=MIN_TERMS, sample_size=None):
    """Load OEIS sequences from stripped file. Returns dict {Axxxxxx: [int,...]}."""
    seqs = {}
    print(f"Loading OEIS from {OEIS_FILE}...")
    with open(OEIS_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            aid = parts[0]
            vals_str = parts[1].strip().strip(",")
            if not vals_str:
                continue
            try:
                vals = [int(x) for x in vals_str.split(",") if x.strip()]
            except ValueError:
                continue
            if len(vals) >= min_terms:
                seqs[aid] = vals
    print(f"  Loaded {len(seqs)} sequences with >= {min_terms} terms")
    if sample_size and len(seqs) > sample_size:
        keys = sorted(seqs.keys())
        random.seed(42)
        sampled = random.sample(keys, sample_size)
        seqs = {k: seqs[k] for k in sampled}
        print(f"  Sampled {sample_size} sequences")
    return seqs

def load_ec_aplist():
    """Load EC a_p sequences from DuckDB. Returns dict {label: [a_p,...]}."""
    import duckdb
    print(f"Loading EC aplist from {DUCKDB_FILE}...")
    con = duckdb.connect(str(DUCKDB_FILE), read_only=True)
    rows = con.sql("SELECT DISTINCT lmfdb_label, aplist FROM elliptic_curves").fetchall()
    con.close()
    ec_seqs = {}
    for label, aplist in rows:
        if aplist and len(aplist) >= FINGERPRINT_LEN:
            ec_seqs[label] = [int(x) for x in aplist]
    print(f"  Loaded {len(ec_seqs)} distinct EC a_p sequences")
    return ec_seqs

def load_knot_determinants():
    """Load knot determinants as a single sequence."""
    print(f"Loading knot determinants from {KNOTS_FILE}...")
    with open(KNOTS_FILE) as f:
        data = json.load(f)
    dets = data.get("determinants_list", [])
    print(f"  Loaded {len(dets)} knot determinants")
    return [int(x) for x in dets]

# ---------------------------------------------------------------------------
# Main search
# ---------------------------------------------------------------------------
def generate_random_sequences(n_seqs, length, value_range=(-100, 100)):
    """Generate random integer sequences for control."""
    random.seed(123)
    return {f"RAND_{i:04d}": [random.randint(*value_range) for _ in range(length)]
            for i in range(n_seqs)}

def build_fingerprint_index(seqs_dict, label_prefix=""):
    """Build {multi_prime_key: [(label, seq), ...]} index."""
    idx = defaultdict(list)
    for label, seq in seqs_dict.items():
        fps = mod_fingerprint(seq)
        if fps is None:
            continue
        key = multi_prime_key(fps)
        idx[key].append(label)
    return idx

def run_functor_search():
    t0 = time.time()
    results = {
        "metadata": {
            "task": "R4-3 Derived Sequence Functor Search",
            "sample_size": SAMPLE_SIZE,
            "fingerprint_length": FINGERPRINT_LEN,
            "fingerprint_primes": FINGERPRINT_PRIMES,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "functor_results": {},
        "top_bridges": [],
        "control": {},
        "summary": {},
    }

    # --- Load data ---
    oeis_all = load_oeis_sequences(min_terms=MIN_TERMS)
    oeis_sample = load_oeis_sequences(min_terms=MIN_TERMS, sample_size=SAMPLE_SIZE)
    ec_seqs = load_ec_aplist()
    knot_dets = load_knot_determinants()

    # --- Build raw fingerprint indices ---
    print("\nBuilding raw fingerprint indices...")
    # Raw OEIS index (all sequences, not just sample)
    oeis_raw_index = build_fingerprint_index(oeis_all, "OEIS_RAW")
    # Raw EC index
    ec_raw_index = build_fingerprint_index(ec_seqs, "EC")
    # Knot: treat as single sequence, also build sliding windows
    knot_fps = {}
    if len(knot_dets) >= FINGERPRINT_LEN:
        knot_fps_raw = mod_fingerprint(knot_dets)
        if knot_fps_raw:
            knot_fps["knot_dets_full"] = multi_prime_key(knot_fps_raw)

    # Also build raw OEIS sample index for baseline
    oeis_sample_raw_index = build_fingerprint_index(oeis_sample, "OEIS_SAMPLE")

    # --- Pre-compute raw matches (baseline) ---
    print("Computing raw match baseline...")
    raw_ec_matches = set()
    raw_oeis_matches = set()
    for aid, seq in oeis_sample.items():
        fps = mod_fingerprint(seq)
        if fps is None:
            continue
        key = multi_prime_key(fps)
        # Check EC
        if key in ec_raw_index:
            for ec_label in ec_raw_index[key]:
                raw_ec_matches.add((aid, ec_label))
        # Check OEIS (exclude self)
        if key in oeis_raw_index:
            for other_aid in oeis_raw_index[key]:
                if other_aid != aid:
                    raw_oeis_matches.add((aid, other_aid))

    print(f"  Raw EC matches: {len(raw_ec_matches)}")
    print(f"  Raw OEIS cross-matches: {len(raw_oeis_matches)}")

    results["baseline"] = {
        "raw_ec_matches": len(raw_ec_matches),
        "raw_oeis_cross_matches": len(raw_oeis_matches),
    }

    # --- Apply functors and search ---
    all_bridges = []

    for fname, func in FUNCTORS.items():
        print(f"\n{'='*60}")
        print(f"Functor: {fname}")
        print(f"{'='*60}")

        functor_ec_matches = set()
        functor_oeis_matches = set()
        functor_knot_matches = set()
        new_ec_bridges = []
        new_oeis_bridges = []
        errors = 0

        for i, (aid, seq) in enumerate(oeis_sample.items()):
            if i % 200 == 0:
                print(f"  Processing {i}/{len(oeis_sample)}...")
            try:
                derived = func(seq)
            except Exception:
                errors += 1
                continue

            fps = mod_fingerprint(derived)
            if fps is None:
                continue
            key = multi_prime_key(fps)

            # Match against EC
            if key in ec_raw_index:
                for ec_label in ec_raw_index[key]:
                    pair = (aid, ec_label)
                    functor_ec_matches.add(pair)
                    if pair not in raw_ec_matches:
                        new_ec_bridges.append({
                            "oeis_id": aid,
                            "ec_label": ec_label,
                            "functor": fname,
                            "derived_first_10": [int(x) for x in derived[:10]],
                            "ec_first_10": [int(x) for x in ec_seqs[ec_label][:10]],
                        })

            # Match against OEIS (raw, not transformed)
            if key in oeis_raw_index:
                for other_aid in oeis_raw_index[key]:
                    if other_aid != aid:
                        pair = (aid, other_aid)
                        functor_oeis_matches.add(pair)
                        if pair not in raw_oeis_matches:
                            new_oeis_bridges.append({
                                "source_oeis": aid,
                                "target_oeis": other_aid,
                                "functor": fname,
                            })

            # Match against knot determinants
            for klabel, kkey in knot_fps.items():
                if key == kkey:
                    functor_knot_matches.add((aid, klabel))

        n_new_ec = len(new_ec_bridges)
        n_new_oeis = len(new_oeis_bridges)
        print(f"  Total EC matches: {len(functor_ec_matches)} (new: {n_new_ec})")
        print(f"  Total OEIS cross-matches: {len(functor_oeis_matches)} (new: {n_new_oeis})")
        print(f"  Knot matches: {len(functor_knot_matches)}")
        print(f"  Errors: {errors}")

        results["functor_results"][fname] = {
            "total_ec_matches": len(functor_ec_matches),
            "new_ec_bridges": n_new_ec,
            "total_oeis_cross_matches": len(functor_oeis_matches),
            "new_oeis_bridges": n_new_oeis,
            "knot_matches": len(functor_knot_matches),
            "errors": errors,
            "ec_bridge_details": new_ec_bridges[:20],
            "oeis_bridge_details": new_oeis_bridges[:20],
        }
        all_bridges.extend(new_ec_bridges)

    # --- Control: random sequences ---
    print(f"\n{'='*60}")
    print("Control: Random sequences")
    print(f"{'='*60}")
    rand_seqs = generate_random_sequences(SAMPLE_SIZE, 60)
    control_results = {}

    for fname, func in FUNCTORS.items():
        rand_ec_matches = 0
        rand_oeis_matches = 0
        for rid, seq in rand_seqs.items():
            try:
                derived = func(seq)
            except Exception:
                continue
            fps = mod_fingerprint(derived)
            if fps is None:
                continue
            key = multi_prime_key(fps)
            if key in ec_raw_index:
                rand_ec_matches += len(ec_raw_index[key])
            if key in oeis_raw_index:
                rand_oeis_matches += len(oeis_raw_index[key])

        control_results[fname] = {
            "random_ec_matches": rand_ec_matches,
            "random_oeis_matches": rand_oeis_matches,
        }
        print(f"  {fname}: EC={rand_ec_matches}, OEIS={rand_oeis_matches}")

    results["control"] = control_results

    # --- Top 10 functorial bridges (EC matches are most valuable) ---
    # Sort by specificity: prefer bridges where derived matches but raw doesn't
    all_bridges.sort(key=lambda b: b["oeis_id"])
    results["top_bridges"] = all_bridges[:10]

    # --- Summary ---
    best_functor = None
    best_new = -1
    total_new_ec = 0
    total_new_oeis = 0
    for fname, fr in results["functor_results"].items():
        total_new_ec += fr["new_ec_bridges"]
        total_new_oeis += fr["new_oeis_bridges"]
        combined = fr["new_ec_bridges"] + fr["new_oeis_bridges"]
        if combined > best_new:
            best_new = combined
            best_functor = fname

    results["summary"] = {
        "total_new_ec_bridges": total_new_ec,
        "total_new_oeis_bridges": total_new_oeis,
        "best_functor": best_functor,
        "best_functor_new_bridges": best_new,
        "elapsed_seconds": round(time.time() - t0, 1),
    }

    # --- Enrichment ratio ---
    for fname in FUNCTORS:
        fr = results["functor_results"][fname]
        cr = results["control"][fname]
        real_ec = fr["total_ec_matches"]
        rand_ec = cr["random_ec_matches"]
        enrichment = real_ec / max(rand_ec, 1)
        fr["ec_enrichment_vs_random"] = round(enrichment, 2)

        real_oeis = fr["total_oeis_cross_matches"]
        rand_oeis = cr["random_oeis_matches"]
        oeis_enrichment = real_oeis / max(rand_oeis, 1)
        fr["oeis_enrichment_vs_random"] = round(oeis_enrichment, 2)

    # --- Save ---
    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")

    # --- Print report ---
    print(f"\n{'='*60}")
    print("REPORT: Derived Sequence Functor Search (R4-3)")
    print(f"{'='*60}")
    print(f"Sample: {SAMPLE_SIZE} OEIS sequences with >= {MIN_TERMS} terms")
    print(f"Fingerprint: mod-{FINGERPRINT_PRIMES} first {FINGERPRINT_LEN} terms")
    print(f"Baseline raw EC matches: {results['baseline']['raw_ec_matches']}")
    print(f"Baseline raw OEIS cross-matches: {results['baseline']['raw_oeis_cross_matches']}")
    print()
    print(f"{'Functor':<28} {'EC(new)':<12} {'OEIS(new)':<14} {'Knot':<8} {'EC enrich':<12} {'OEIS enrich'}")
    print("-" * 86)
    for fname in FUNCTORS:
        fr = results["functor_results"][fname]
        print(f"{fname:<28} {fr['new_ec_bridges']:<12} {fr['new_oeis_bridges']:<14} "
              f"{fr['knot_matches']:<8} {fr.get('ec_enrichment_vs_random','?'):<12} "
              f"{fr.get('oeis_enrichment_vs_random','?')}")
    print()
    print(f"Best functor: {results['summary']['best_functor']}")
    print(f"Total new EC bridges: {results['summary']['total_new_ec_bridges']}")
    print(f"Total new OEIS bridges: {results['summary']['total_new_oeis_bridges']}")
    print(f"Elapsed: {results['summary']['elapsed_seconds']}s")

    if all_bridges:
        print(f"\nTop functorial EC bridges:")
        for b in all_bridges[:10]:
            print(f"  {b['functor']}: {b['oeis_id']} -> {b['ec_label']}")
            print(f"    derived: {b['derived_first_10']}")
            print(f"    EC a_p:  {b['ec_first_10']}")

    return results


if __name__ == "__main__":
    run_functor_search()
