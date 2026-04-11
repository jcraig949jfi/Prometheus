#!/usr/bin/env python3
"""
OEIS First Differences — Do They Reveal Hidden Recurrence?
===========================================================
Many OEIS sequences that aren't linearly recurrent become recurrent after
taking first differences (Δa_n = a_{n+1} - a_n). This measures the
recurrence recovery rate under differencing.

Method:
  1. Load 5000 OEIS sequences with 25+ terms
  2. Run BM on raw sequence: classify recurrent/non-recurrent
  3. For non-recurrent: compute first differences Δa_n, run BM again
  4. For still non-recurrent: compute second differences Δ²a_n
  5. Continue up to depth 5
  6. Build "differencing depth" distribution
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
OUT_FILE = Path(__file__).parent / "oeis_differencing_results.json"

MIN_TERMS = 25
N_SEQUENCES = 5000
VERIFY_HOLDOUT = 5
PRIMES = [10007, 10009, 10037]
MAX_DIFF_DEPTH = 5  # try up to 5th differences


def berlekamp_massey_gf(seq, p):
    """BM algorithm over GF(p). Returns LFSR length (order)."""
    n = len(seq)
    s = [x % p for x in seq]

    if all(v == 0 for v in s):
        return 0

    C = [1]
    B = [1]
    L = 0
    m = 1
    b = 1

    for i in range(n):
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

    return L


def bm_order_consensus(seq, primes=PRIMES):
    """Run BM over multiple primes, take consensus."""
    orders = []
    for p in primes:
        order = berlekamp_massey_gf(seq, p)
        orders.append(order)

    if len(set(orders)) == 1:
        return orders[0]
    c = Counter(orders)
    most_common = c.most_common(1)[0]
    if most_common[1] >= 2:
        return most_common[0]
    return min(orders)


def verify_recurrence(seq, order, p=10007):
    """Verify recurrence predicts held-out terms."""
    if order == 0:
        return len(set(v % p for v in seq)) == 1

    if order >= len(seq) // 2:
        return False

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

    for i in range(n - VERIFY_HOLDOUT, n):
        predicted = 0
        for j in range(1, len(C)):
            if i - j >= 0:
                predicted = (predicted - C[j] * s[i - j]) % p
        if predicted != s[i]:
            return False

    return True


def is_recurrent(seq):
    """Check if sequence is recurrent: BM order < n/2 AND holdout passes."""
    if len(seq) < VERIFY_HOLDOUT + 5:
        return False, None

    order = bm_order_consensus(seq)
    is_trivial = order >= len(seq) // 2

    if is_trivial:
        return False, order

    if len(seq) >= order + VERIFY_HOLDOUT + 5:
        verified = verify_recurrence(seq, order)
    else:
        verified = False

    return verified, order


def first_differences(seq):
    """Compute Δa_n = a_{n+1} - a_n."""
    return [seq[i + 1] - seq[i] for i in range(len(seq) - 1)]


def parse_oeis(path, min_terms=MIN_TERMS, max_seqs=N_SEQUENCES):
    """Parse OEIS stripped file."""
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


def classify_sequence(seq_id, keywords, names):
    """Classify sequence into families."""
    name = names.get(seq_id, "").lower()
    families = []

    algebraic_words = ["polynomial", "chebyshev", "fibonacci", "lucas", "pell",
                       "catalan", "bernoulli", "euler number", "binomial",
                       "stirling", "bell number", "tribonacci", "padovan",
                       "recurrence", "linear recurrence"]
    for w in algebraic_words:
        if w in name:
            families.append("algebraic")
            break

    nt_words = ["prime", "divisor", "totient", "sigma", "mobius", "moebius",
                "partition", "class number"]
    for w in nt_words:
        if w in name:
            families.append("number_theoretic")
            break

    combo_words = ["number of", "count", "ways", "permutation", "combination",
                   "graph", "tree", "lattice path"]
    for w in combo_words:
        if w in name:
            families.append("combinatorial")
            break

    kw = keywords.get(seq_id, [])
    if "base" in kw:
        families.append("base_dependent")
    if "mult" in kw:
        families.append("multiplicative")

    if not families:
        families.append("unclassified")
    return families


def main():
    t0 = time.time()
    print("Loading OEIS sequences...")
    sequences = parse_oeis(DATA_FILE)
    print(f"  Loaded {len(sequences)} sequences with {MIN_TERMS}+ terms")

    print("Loading keywords and names...")
    with open(KEYWORDS_FILE, encoding="utf-8") as f:
        keywords = json.load(f)
    with open(NAMES_FILE, encoding="utf-8") as f:
        names = json.load(f)

    # =========================================================
    # Phase 1: Classify raw sequences
    # =========================================================
    print("\nPhase 1: BM on raw sequences...")
    raw_recurrent = {}     # seq_id -> order
    raw_non_recurrent = {} # seq_id -> raw_order (failed)
    raw_orders = []

    for i, (seq_id, seq) in enumerate(sequences.items()):
        if (i + 1) % 1000 == 0:
            print(f"  {i+1}/{len(sequences)}...")

        rec, order = is_recurrent(seq)
        if rec:
            raw_recurrent[seq_id] = order
            raw_orders.append(order)
        else:
            raw_non_recurrent[seq_id] = order

    n_total = len(sequences)
    n_raw_rec = len(raw_recurrent)
    n_raw_nonrec = len(raw_non_recurrent)
    raw_rate = n_raw_rec / n_total

    print(f"  Raw recurrent: {n_raw_rec}/{n_total} ({raw_rate:.1%})")
    print(f"  Raw non-recurrent: {n_raw_nonrec}/{n_total} ({1 - raw_rate:.1%})")

    # =========================================================
    # Phase 2: Differencing cascade on non-recurrent sequences
    # =========================================================
    print(f"\nPhase 2: Differencing cascade (up to depth {MAX_DIFF_DEPTH})...")
    # For each non-recurrent sequence, try differences up to MAX_DIFF_DEPTH
    # depth 0 = raw (already non-recurrent)
    # depth 1 = first differences
    # depth 2 = second differences, etc.

    diff_results = {}  # seq_id -> {depth, order, recovered}
    depth_counts = Counter()  # depth -> count of sequences that became recurrent
    depth_orders = defaultdict(list)  # depth -> list of BM orders
    never_recurrent = 0

    for i, seq_id in enumerate(raw_non_recurrent):
        if (i + 1) % 1000 == 0:
            print(f"  {i+1}/{n_raw_nonrec}...")

        seq = sequences[seq_id]
        recovered = False

        for depth in range(1, MAX_DIFF_DEPTH + 1):
            # Compute differences
            seq = first_differences(seq)

            # Need enough terms for BM + holdout
            if len(seq) < VERIFY_HOLDOUT + 10:
                break

            rec, order = is_recurrent(seq)
            if rec:
                diff_results[seq_id] = {
                    "depth": depth,
                    "order": order,
                    "recovered": True
                }
                depth_counts[depth] += 1
                depth_orders[depth].append(order)
                recovered = True
                break

        if not recovered:
            diff_results[seq_id] = {
                "depth": None,
                "order": None,
                "recovered": False
            }
            never_recurrent += 1

    total_recovered = sum(depth_counts.values())
    recovery_rate = total_recovered / n_raw_nonrec if n_raw_nonrec > 0 else 0

    print(f"\n  Non-recurrent analyzed: {n_raw_nonrec}")
    print(f"  Recovered via differencing: {total_recovered} ({recovery_rate:.1%})")
    print(f"  Never recurrent (depth 1-{MAX_DIFF_DEPTH}): {never_recurrent}")

    for d in range(1, MAX_DIFF_DEPTH + 1):
        c = depth_counts.get(d, 0)
        r = c / n_raw_nonrec if n_raw_nonrec > 0 else 0
        print(f"    Depth {d}: {c} recovered ({r:.1%})")

    # =========================================================
    # Phase 3: Family breakdown of recovery
    # =========================================================
    print("\nPhase 3: Family breakdown...")
    family_recovery = defaultdict(lambda: {"total_nonrec": 0, "recovered": 0, "depths": []})

    for seq_id in raw_non_recurrent:
        families = classify_sequence(seq_id, keywords, names)
        dr = diff_results[seq_id]
        for fam in families:
            family_recovery[fam]["total_nonrec"] += 1
            if dr["recovered"]:
                family_recovery[fam]["recovered"] += 1
                family_recovery[fam]["depths"].append(dr["depth"])

    family_recovery_stats = {}
    for fam, data in sorted(family_recovery.items(), key=lambda x: -x[1]["total_nonrec"]):
        rate = data["recovered"] / data["total_nonrec"] if data["total_nonrec"] > 0 else 0
        mean_depth = float(np.mean(data["depths"])) if data["depths"] else None
        family_recovery_stats[fam] = {
            "total_nonrec": data["total_nonrec"],
            "recovered": data["recovered"],
            "recovery_rate": round(rate, 4),
            "mean_depth": round(mean_depth, 2) if mean_depth else None,
        }
        print(f"  {fam:20s}: {data['recovered']}/{data['total_nonrec']} recovered ({rate:.1%})")

    # =========================================================
    # Phase 4: Order distribution after differencing
    # =========================================================
    print("\nPhase 4: Order distribution of recovered sequences...")
    all_recovered_orders = []
    for d in range(1, MAX_DIFF_DEPTH + 1):
        all_recovered_orders.extend(depth_orders.get(d, []))

    if all_recovered_orders:
        rec_order_counter = Counter(all_recovered_orders)
        order_dist = {str(k): v for k, v in sorted(rec_order_counter.items())}
        mean_recovered_order = float(np.mean(all_recovered_orders))
        median_recovered_order = float(np.median(all_recovered_orders))
        print(f"  Mean order after differencing: {mean_recovered_order:.2f}")
        print(f"  Median order after differencing: {median_recovered_order:.1f}")
        print(f"  Order distribution (top 10):")
        for k, v in sorted(rec_order_counter.items(), key=lambda x: -x[1])[:10]:
            print(f"    Order {k}: {v}")
    else:
        order_dist = {}
        mean_recovered_order = None
        median_recovered_order = None

    # =========================================================
    # Phase 5: Null model — random sequences under differencing
    # =========================================================
    print("\nPhase 5: Null model (1000 random sequences)...")
    real_lengths = [len(seq) for seq in sequences.values()]
    null_recovered = 0
    null_total = 1000
    null_depth_counts = Counter()

    for i in range(null_total):
        if (i + 1) % 200 == 0:
            print(f"  Null: {i+1}/{null_total}...")
        length = random.choice(real_lengths)
        seq = [random.randint(-1000, 1000) for _ in range(length)]

        # First check raw
        rec, _ = is_recurrent(seq)
        if rec:
            continue  # skip sequences that are already recurrent in the null

        for depth in range(1, MAX_DIFF_DEPTH + 1):
            seq = first_differences(seq)
            if len(seq) < VERIFY_HOLDOUT + 10:
                break
            rec, order = is_recurrent(seq)
            if rec:
                null_recovered += 1
                null_depth_counts[depth] += 1
                break

    null_recovery_rate = null_recovered / null_total
    print(f"  Null recovery rate: {null_recovered}/{null_total} ({null_recovery_rate:.1%})")

    # =========================================================
    # Phase 6: Notable examples
    # =========================================================
    print("\nPhase 6: Notable examples...")
    examples_by_depth = defaultdict(list)
    for seq_id, dr in diff_results.items():
        if dr["recovered"] and len(examples_by_depth[dr["depth"]]) < 5:
            name = names.get(seq_id, "unknown")
            examples_by_depth[dr["depth"]].append({
                "id": seq_id,
                "name": name[:120],
                "depth": dr["depth"],
                "order_after_diff": dr["order"],
                "n_terms": len(sequences[seq_id]),
            })

    notable_examples = []
    for d in sorted(examples_by_depth.keys()):
        notable_examples.extend(examples_by_depth[d])

    # =========================================================
    # Phase 7: Cumulative recurrence rate
    # =========================================================
    # After differencing, what's the total fraction of sequences that are
    # recurrent (raw + recovered)?
    total_recurrent_after_diff = n_raw_rec + total_recovered
    cumulative_rate = total_recurrent_after_diff / n_total

    # Build depth distribution
    depth_distribution = {}
    depth_distribution["depth_0_raw"] = {
        "count": n_raw_rec,
        "fraction_of_total": round(n_raw_rec / n_total, 4),
    }
    for d in range(1, MAX_DIFF_DEPTH + 1):
        c = depth_counts.get(d, 0)
        depth_distribution[f"depth_{d}"] = {
            "count": c,
            "fraction_of_total": round(c / n_total, 4),
            "fraction_of_nonrec": round(c / n_raw_nonrec, 4) if n_raw_nonrec > 0 else 0,
            "mean_order": round(float(np.mean(depth_orders[d])), 2) if depth_orders.get(d) else None,
            "median_order": round(float(np.median(depth_orders[d])), 1) if depth_orders.get(d) else None,
        }
    depth_distribution["never_recurrent"] = {
        "count": never_recurrent,
        "fraction_of_total": round(never_recurrent / n_total, 4),
    }

    elapsed = time.time() - t0

    # =========================================================
    # Assemble output
    # =========================================================
    output = {
        "experiment": "OEIS First Differences — Hidden Recurrence Recovery",
        "method": "BM over GF(p) with 3-prime consensus + holdout verification, "
                  f"differencing cascade up to depth {MAX_DIFF_DEPTH}",
        "parameters": {
            "min_terms": MIN_TERMS,
            "n_sequences": n_total,
            "holdout_terms": VERIFY_HOLDOUT,
            "primes": PRIMES,
            "max_differencing_depth": MAX_DIFF_DEPTH,
        },
        "raw_classification": {
            "total": n_total,
            "raw_recurrent": n_raw_rec,
            "raw_non_recurrent": n_raw_nonrec,
            "raw_recurrence_rate": round(raw_rate, 4),
            "mean_raw_order": round(float(np.mean(raw_orders)), 2) if raw_orders else None,
            "median_raw_order": round(float(np.median(raw_orders)), 1) if raw_orders else None,
        },
        "differencing_recovery": {
            "non_recurrent_tested": n_raw_nonrec,
            "total_recovered": total_recovered,
            "recovery_rate": round(recovery_rate, 4),
            "never_recurrent": never_recurrent,
            "cumulative_recurrent_after_diff": total_recurrent_after_diff,
            "cumulative_recurrence_rate": round(cumulative_rate, 4),
        },
        "depth_distribution": depth_distribution,
        "recovered_order_stats": {
            "mean_order": round(mean_recovered_order, 2) if mean_recovered_order else None,
            "median_order": round(median_recovered_order, 1) if median_recovered_order else None,
            "order_distribution": order_dist,
        },
        "family_recovery": family_recovery_stats,
        "null_model": {
            "n_sequences": null_total,
            "recovered": null_recovered,
            "recovery_rate": round(null_recovery_rate, 4),
            "depth_distribution": {str(k): v for k, v in sorted(null_depth_counts.items())},
        },
        "notable_examples": notable_examples,
        "comparison_to_baseline": {
            "baseline_raw_rate_22pct": 0.22,
            "this_experiment_raw_rate": round(raw_rate, 4),
            "recovery_rate_via_differencing": round(recovery_rate, 4),
            "new_cumulative_rate": round(cumulative_rate, 4),
            "net_gain_pct_points": round((cumulative_rate - raw_rate) * 100, 2),
        },
        "elapsed_seconds": round(elapsed, 1),
    }

    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    # =========================================================
    # Print summary
    # =========================================================
    print(f"\n{'='*65}")
    print(f"OEIS DIFFERENCING — HIDDEN RECURRENCE RECOVERY")
    print(f"{'='*65}")
    print(f"Total sequences:       {n_total}")
    print(f"Raw recurrent:         {n_raw_rec} ({raw_rate:.1%})")
    print(f"Raw non-recurrent:     {n_raw_nonrec} ({1-raw_rate:.1%})")
    print(f"")
    print(f"DIFFERENCING RECOVERY (among non-recurrent):")
    print(f"  Recovered:           {total_recovered}/{n_raw_nonrec} ({recovery_rate:.1%})")
    for d in range(1, MAX_DIFF_DEPTH + 1):
        c = depth_counts.get(d, 0)
        mo = f"(mean order {float(np.mean(depth_orders[d])):.1f})" if depth_orders.get(d) else ""
        print(f"    Depth {d}: {c:5d} {mo}")
    print(f"  Never recurrent:     {never_recurrent}")
    print(f"")
    print(f"CUMULATIVE RECURRENCE RATE:")
    print(f"  Raw only:            {raw_rate:.1%}")
    print(f"  Raw + differencing:  {cumulative_rate:.1%}")
    print(f"  Net gain:            +{(cumulative_rate - raw_rate)*100:.1f} pp")
    print(f"")
    print(f"Null model recovery:   {null_recovered}/{null_total} ({null_recovery_rate:.1%})")
    print(f"")
    print(f"Elapsed: {elapsed:.1f}s")
    print(f"Results saved to: {OUT_FILE}")


if __name__ == "__main__":
    main()
