#!/usr/bin/env python3
"""
Berlekamp-Massey Recurrence Order Distribution Across OEIS
==========================================================
Measures the distribution of minimal linear recurrence orders across OEIS
sequences using the Berlekamp-Massey algorithm over a finite field (GF(p)).

Since BM works over fields, we reduce sequences mod a large prime and check
consistency across multiple primes to avoid false positives.

Method:
  1. Parse 10000 OEIS sequences (20+ terms) from stripped_new.txt
  2. For each sequence, run BM mod several primes; take consensus order
  3. Verify: check if detected recurrence actually predicts held-out terms
  4. Compute distribution statistics
  5. Compare algebraic-keyword families vs general OEIS
  6. Test correlation between BM order and growth rate
  7. Null model: random integer sequences of same lengths
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
import time
import random

DATA_FILE = Path(__file__).parent.parent / "oeis" / "data" / "stripped_new.txt"
KEYWORDS_FILE = Path(__file__).parent.parent / "oeis" / "data" / "oeis_keywords.json"
NAMES_FILE = Path(__file__).parent.parent / "oeis" / "data" / "oeis_names.json"
OUT_FILE = Path(__file__).parent / "oeis_bm_order_results.json"

MIN_TERMS = 20
N_SEQUENCES = 10000
VERIFY_HOLDOUT = 5  # hold out last 5 terms for verification
PRIMES = [10007, 10009, 10037]  # multiple primes for consensus


def berlekamp_massey_gf(seq, p):
    """
    Berlekamp-Massey algorithm over GF(p).
    Returns the minimal LFSR (list of coefficients) such that:
      s[i] = sum(c[j] * s[i-1-j] for j in range(len(c))) mod p
    Returns None if sequence is all zeros.
    """
    n = len(seq)
    s = [x % p for x in seq]

    # Check all zeros
    if all(v == 0 for v in s):
        return [0]  # order 0: constant zero

    C = [1]  # current polynomial
    B = [1]  # previous polynomial
    L = 0    # current LFSR length
    m = 1    # shift count
    b = 1    # previous discrepancy

    for i in range(n):
        # Compute discrepancy
        d = s[i]
        for j in range(1, len(C)):
            d = (d + C[j] * s[i - j]) % p

        if d == 0:
            m += 1
        elif 2 * L <= i:
            T = C[:]
            coeff = (d * pow(b, p - 2, p)) % p  # d / b mod p
            # C = C - coeff * x^m * B
            while len(C) < len(B) + m:
                C.append(0)
            for j in range(len(B)):
                C[j + m] = (C[j + m] - coeff * B[j]) % p
            L = i + 1 - L
            B = T
            b = d
            m = 1
        else:
            coeff = (d * pow(b, p - 2, p)) % p
            while len(C) < len(B) + m:
                C.append(0)
            for j in range(len(B)):
                C[j + m] = (C[j + m] - coeff * B[j]) % p
            m += 1

    return L  # return the order (LFSR length)


def bm_order_consensus(seq, primes=PRIMES):
    """
    Run BM over multiple primes and take consensus.
    Returns the order if consistent, else the minimum order found.
    """
    orders = []
    for p in primes:
        order = berlekamp_massey_gf(seq, p)
        if isinstance(order, list):
            orders.append(0)
        else:
            orders.append(order)

    # Consensus: if all agree, that's the order
    if len(set(orders)) == 1:
        return orders[0]
    # If two agree, use majority
    c = Counter(orders)
    most_common = c.most_common(1)[0]
    if most_common[1] >= 2:
        return most_common[0]
    # No consensus: return minimum (most conservative)
    return min(orders)


def verify_recurrence(seq, order, p=10007):
    """
    Verify that a recurrence of given order actually works by checking
    if it predicts the last VERIFY_HOLDOUT terms from the prefix.
    """
    if order == 0:
        # Constant sequence
        return len(set(seq)) == 1

    if order >= len(seq) // 2:
        return False  # order too high relative to data

    # Recompute the full LFSR coefficients
    n = len(seq)
    s = [x % p for x in seq]

    C = [1]
    B = [1]
    L = 0
    m = 1
    b = 1

    for i in range(n - VERIFY_HOLDOUT):
        d = s[i]
        for j in range(1, len(C)):
            d = (d + C[j] * s[i - j]) % p

        if d == 0:
            m += 1
        elif 2 * L <= i:
            T = C[:]
            coeff = (d * pow(b, p - 2, p)) % p
            while len(C) < len(B) + m:
                C.append(0)
            for j in range(len(B)):
                C[j + m] = (C[j + m] - coeff * B[j]) % p
            L = i + 1 - L
            B = T
            b = d
            m = 1
        else:
            coeff = (d * pow(b, p - 2, p)) % p
            while len(C) < len(B) + m:
                C.append(0)
            for j in range(len(B)):
                C[j + m] = (C[j + m] - coeff * B[j]) % p
            m += 1

    if L != order:
        return False

    # Now check: can we predict the held-out terms?
    # The recurrence is: s[i] = -sum(C[j]*s[i-j] for j=1..L) mod p
    for i in range(n - VERIFY_HOLDOUT, n):
        predicted = 0
        for j in range(1, len(C)):
            if i - j >= 0:
                predicted = (predicted - C[j] * s[i - j]) % p
        if predicted != s[i]:
            return False

    return True


def parse_oeis(path, min_terms=MIN_TERMS, max_seqs=N_SEQUENCES):
    """Parse OEIS stripped file, return dict of {A-number: [terms]}."""
    sequences = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) != 2:
                continue
            seq_id = parts[0]
            vals_str = parts[1].strip().strip(",")
            if not vals_str:
                continue
            try:
                vals = [int(v) for v in vals_str.split(",") if v.strip()]
            except ValueError:
                continue
            if len(vals) >= min_terms:
                sequences[seq_id] = vals
            if len(sequences) >= max_seqs:
                break
    return sequences


def estimate_growth_rate(seq):
    """Estimate growth rate as log of ratio of last to first nonzero abs value."""
    abs_vals = [abs(v) for v in seq if v != 0]
    if len(abs_vals) < 2:
        return 0.0
    first = abs_vals[0]
    last = abs_vals[-1]
    if first == 0 or last == 0:
        return 0.0
    n = len(abs_vals)
    try:
        rate = np.log(last / first) / n
    except (ValueError, OverflowError):
        rate = 0.0
    return float(rate)


def classify_sequence(seq_id, keywords, names):
    """Classify sequence into families based on keywords and name."""
    kw = keywords.get(seq_id, [])
    name = names.get(seq_id, "").lower()

    families = []

    # Algebraic indicators
    algebraic_words = ["polynomial", "chebyshev", "fibonacci", "lucas", "pell",
                       "catalan", "bernoulli", "euler number", "binomial",
                       "stirling", "bell number", "tribonacci", "padovan",
                       "recurrence", "linear recurrence"]
    for w in algebraic_words:
        if w in name:
            families.append("algebraic")
            break

    # Number-theoretic
    nt_words = ["prime", "divisor", "totient", "sigma", "mobius", "moebius",
                "partition", "class number"]
    for w in nt_words:
        if w in name:
            families.append("number_theoretic")
            break

    # Combinatorial
    combo_words = ["number of", "count", "ways", "permutation", "combination",
                   "graph", "tree", "lattice path"]
    for w in combo_words:
        if w in name:
            families.append("combinatorial")
            break

    # Base-dependent
    if "base" in kw:
        families.append("base_dependent")

    if "mult" in kw:
        families.append("multiplicative")

    if not families:
        families.append("unclassified")

    return families


def generate_random_sequences(n_seqs, lengths, value_range=(-1000, 1000)):
    """Generate random integer sequences as null model."""
    sequences = {}
    for i in range(n_seqs):
        length = random.choice(lengths)
        seq = [random.randint(value_range[0], value_range[1]) for _ in range(length)]
        sequences[f"RAND{i:06d}"] = seq
    return sequences


def main():
    t0 = time.time()
    print("Loading OEIS sequences...")
    sequences = parse_oeis(DATA_FILE)
    print(f"  Loaded {len(sequences)} sequences with {MIN_TERMS}+ terms")

    # Load keywords and names for classification
    print("Loading keywords and names...")
    with open(KEYWORDS_FILE, encoding="utf-8") as f:
        keywords = json.load(f)
    with open(NAMES_FILE, encoding="utf-8") as f:
        names = json.load(f)

    # === Phase 1: BM order for all OEIS sequences ===
    print("\nPhase 1: Computing BM orders for OEIS sequences...")
    results = {}
    order_counts = Counter()
    verified_order_counts = Counter()
    growth_rates = {}
    family_orders = defaultdict(list)

    for i, (seq_id, seq) in enumerate(sequences.items()):
        if (i + 1) % 1000 == 0:
            print(f"  Processed {i+1}/{len(sequences)}...")

        order = bm_order_consensus(seq)

        # Check if order is "real" (less than half the sequence length)
        # If BM returns order >= len/2, it's likely fitting noise
        is_trivial = order >= len(seq) // 2

        # Verify with holdout
        if not is_trivial and len(seq) >= order + VERIFY_HOLDOUT + 5:
            verified = verify_recurrence(seq, order)
        elif is_trivial:
            verified = False
        else:
            verified = None  # can't verify (not enough terms)

        effective_order = order if (not is_trivial and verified is not False) else float('inf')

        results[seq_id] = {
            "raw_order": order,
            "effective_order": effective_order if effective_order != float('inf') else "none",
            "verified": verified,
            "n_terms": len(seq),
            "is_trivial": is_trivial,
        }

        if effective_order == float('inf'):
            order_counts["none"] += 1
        else:
            order_counts[effective_order] += 1

        if verified is True:
            verified_order_counts[effective_order] += 1

        # Growth rate
        gr = estimate_growth_rate(seq)
        growth_rates[seq_id] = gr
        results[seq_id]["growth_rate"] = gr

        # Family classification
        families = classify_sequence(seq_id, keywords, names)
        results[seq_id]["families"] = families
        for fam in families:
            eo = effective_order if effective_order != float('inf') else "none"
            family_orders[fam].append(eo)

    # === Phase 2: Statistics ===
    print("\nPhase 2: Computing statistics...")
    numeric_orders = [r["effective_order"] for r in results.values()
                      if r["effective_order"] != "none"]
    no_recurrence_count = sum(1 for r in results.values() if r["effective_order"] == "none")
    total = len(results)

    stats = {
        "total_sequences": total,
        "with_recurrence": len(numeric_orders),
        "no_recurrence": no_recurrence_count,
        "fraction_with_recurrence": len(numeric_orders) / total,
        "fraction_no_recurrence": no_recurrence_count / total,
    }

    if numeric_orders:
        stats["mean_order"] = float(np.mean(numeric_orders))
        stats["median_order"] = float(np.median(numeric_orders))
        stats["std_order"] = float(np.std(numeric_orders))
        stats["max_order"] = int(max(numeric_orders))
        stats["fraction_order_le_1"] = sum(1 for o in numeric_orders if o <= 1) / total
        stats["fraction_order_le_2"] = sum(1 for o in numeric_orders if o <= 2) / total
        stats["fraction_order_le_5"] = sum(1 for o in numeric_orders if o <= 5) / total
        stats["fraction_order_le_10"] = sum(1 for o in numeric_orders if o <= 10) / total

    # Order distribution (top 20)
    order_dist = {}
    for k in sorted(order_counts.keys(), key=lambda x: (isinstance(x, str), x)):
        order_dist[str(k)] = order_counts[k]

    verified_dist = {}
    for k in sorted(verified_order_counts.keys()):
        verified_dist[str(k)] = verified_order_counts[k]

    # === Phase 3: Family comparison ===
    print("\nPhase 3: Family analysis...")
    family_stats = {}
    for fam, orders in family_orders.items():
        numeric = [o for o in orders if o != "none"]
        family_stats[fam] = {
            "count": len(orders),
            "with_recurrence": len(numeric),
            "fraction_with_recurrence": len(numeric) / len(orders) if orders else 0,
            "mean_order": float(np.mean(numeric)) if numeric else None,
            "median_order": float(np.median(numeric)) if numeric else None,
        }

    # === Phase 4: Growth rate correlation ===
    print("\nPhase 4: Growth rate vs BM order correlation...")
    growth_order_pairs = []
    for seq_id, r in results.items():
        if r["effective_order"] != "none":
            growth_order_pairs.append((r["growth_rate"], r["effective_order"]))

    if len(growth_order_pairs) > 10:
        gr_arr = np.array([p[0] for p in growth_order_pairs])
        or_arr = np.array([p[1] for p in growth_order_pairs])
        # Spearman rank correlation
        from scipy.stats import spearmanr, pearsonr
        spearman_r, spearman_p = spearmanr(gr_arr, or_arr)
        pearson_r, pearson_p = pearsonr(gr_arr, or_arr)
        correlation = {
            "spearman_r": float(spearman_r),
            "spearman_p": float(spearman_p),
            "pearson_r": float(pearson_r),
            "pearson_p": float(pearson_p),
            "n_pairs": len(growth_order_pairs),
        }
    else:
        correlation = {"error": "too few pairs"}

    # === Phase 5: Null model ===
    print("\nPhase 5: Random null model (5000 sequences)...")
    real_lengths = [len(seq) for seq in sequences.values()]
    random_seqs = generate_random_sequences(5000, real_lengths)

    null_orders = Counter()
    null_numeric = []
    for i, (sid, seq) in enumerate(random_seqs.items()):
        if (i + 1) % 1000 == 0:
            print(f"  Null: {i+1}/5000...")
        order = bm_order_consensus(seq)
        is_trivial = order >= len(seq) // 2
        if not is_trivial and len(seq) >= order + VERIFY_HOLDOUT + 5:
            verified = verify_recurrence(seq, order)
        else:
            verified = False

        if is_trivial or verified is False:
            null_orders["none"] += 1
        else:
            null_orders[order] += 1
            null_numeric.append(order)

    null_stats = {
        "total": 5000,
        "with_recurrence": len(null_numeric),
        "no_recurrence": 5000 - len(null_numeric),
        "fraction_with_recurrence": len(null_numeric) / 5000,
        "mean_order": float(np.mean(null_numeric)) if null_numeric else None,
        "median_order": float(np.median(null_numeric)) if null_numeric else None,
        "distribution": {str(k): v for k, v in sorted(null_orders.items(),
                         key=lambda x: (isinstance(x[0], str), x[0]))},
    }

    # === Phase 6: Notable sequences ===
    print("\nPhase 6: Notable examples...")
    # Sequences with verified low-order recurrences
    low_order_examples = []
    for seq_id, r in sorted(results.items()):
        if r["verified"] is True and isinstance(r["effective_order"], int) and r["effective_order"] <= 5:
            name = names.get(seq_id, "unknown")
            low_order_examples.append({
                "id": seq_id,
                "order": r["effective_order"],
                "name": name[:100],
            })
            if len(low_order_examples) >= 30:
                break

    elapsed = time.time() - t0

    # === Assemble output ===
    output = {
        "experiment": "Berlekamp-Massey Recurrence Order Distribution Across OEIS",
        "method": "BM over GF(p) with 3-prime consensus + holdout verification",
        "primes_used": PRIMES,
        "min_terms": MIN_TERMS,
        "holdout_terms": VERIFY_HOLDOUT,
        "n_sequences_analyzed": total,
        "statistics": stats,
        "order_distribution_raw": order_dist,
        "order_distribution_verified": verified_dist,
        "family_comparison": family_stats,
        "growth_rate_correlation": correlation,
        "null_model": null_stats,
        "notable_low_order_examples": low_order_examples,
        "elapsed_seconds": round(elapsed, 1),
    }

    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    # === Print summary ===
    print(f"\n{'='*60}")
    print(f"BERLEKAMP-MASSEY ORDER DISTRIBUTION -- OEIS")
    print(f"{'='*60}")
    print(f"Sequences analyzed: {total}")
    print(f"With detected recurrence: {stats['with_recurrence']} ({stats['fraction_with_recurrence']:.1%})")
    print(f"No recurrence detected:   {stats['no_recurrence']} ({stats['fraction_no_recurrence']:.1%})")
    if numeric_orders:
        print(f"\nAmong sequences WITH recurrence:")
        print(f"  Mean order:   {stats['mean_order']:.2f}")
        print(f"  Median order: {stats['median_order']:.1f}")
        print(f"  Fraction order <= 1: {stats['fraction_order_le_1']:.1%}")
        print(f"  Fraction order <= 2: {stats['fraction_order_le_2']:.1%}")
        print(f"  Fraction order <= 5: {stats['fraction_order_le_5']:.1%}")
        print(f"  Fraction order <= 10: {stats['fraction_order_le_10']:.1%}")

    print(f"\nOrder distribution (top entries):")
    for k, v in sorted(order_dist.items(), key=lambda x: -x[1])[:15]:
        print(f"  Order {k}: {v} ({v/total:.1%})")

    print(f"\nFamily comparison:")
    for fam, fs in sorted(family_stats.items(), key=lambda x: -x[1]["count"]):
        rec_frac = fs["fraction_with_recurrence"]
        mean_o = f"{fs['mean_order']:.1f}" if fs['mean_order'] is not None else "N/A"
        print(f"  {fam:20s}: n={fs['count']:5d}, recurrence={rec_frac:.1%}, mean_order={mean_o}")

    print(f"\nGrowth rate correlation:")
    if "error" not in correlation:
        print(f"  Spearman r = {correlation['spearman_r']:.4f} (p = {correlation['spearman_p']:.2e})")
        print(f"  Pearson  r = {correlation['pearson_r']:.4f} (p = {correlation['pearson_p']:.2e})")

    print(f"\nNull model (random sequences):")
    print(f"  With recurrence: {null_stats['with_recurrence']}/5000 ({null_stats['fraction_with_recurrence']:.1%})")
    if null_stats['mean_order'] is not None:
        print(f"  Mean order: {null_stats['mean_order']:.2f}")

    print(f"\nElapsed: {elapsed:.1f}s")
    print(f"Results saved to: {OUT_FILE}")


if __name__ == "__main__":
    main()
