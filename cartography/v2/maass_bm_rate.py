"""
Maass form Berlekamp-Massey recurrence rate analysis.

For each Maass form with 50+ coefficients, extract c_p at the first 50 prime
indices, run Berlekamp-Massey over GF(10^9+7), and classify as recurrent
(BM order < 25) vs non-recurrent.

EC was 0.1%, OEIS was 19.8%. Where do Maass forms land?
"""

import json
import random
import sys
from pathlib import Path
from collections import Counter

# ---------------------------------------------------------------------------
# Primes
# ---------------------------------------------------------------------------

def sieve_primes(n):
    """Return list of primes up to n."""
    is_prime = [False, False] + [True] * (n - 1)
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

PRIMES_50 = sieve_primes(500)[:50]  # first 50 primes: 2,3,5,...,229
assert len(PRIMES_50) == 50

# ---------------------------------------------------------------------------
# Berlekamp-Massey over GF(p)
# ---------------------------------------------------------------------------

MOD = 10**9 + 7

def modinv(a, m=MOD):
    """Modular inverse via extended Euclidean algorithm."""
    g, x, _ = _extended_gcd(a % m, m)
    if g != 1:
        return None
    return x % m

def _extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x, y = _extended_gcd(b % a, a)
    return g, y - (b // a) * x, x

def berlekamp_massey(seq, mod=MOD):
    """
    Berlekamp-Massey algorithm over GF(mod).
    Returns the LFSR length (recurrence order).
    seq: list of integers in [0, mod).
    """
    n = len(seq)
    C = [1]  # current connection polynomial
    B = [1]  # previous connection polynomial
    L = 0    # current LFSR length
    m = 1    # shift counter
    b = 1    # previous discrepancy

    for i in range(n):
        # compute discrepancy
        d = 0
        for j in range(L + 1):
            d = (d + C[j] * seq[i - j]) % mod
        if d == 0:
            m += 1
        elif 2 * L <= i:
            T = C[:]
            coeff = (mod - d * modinv(b, mod)) % mod
            # C = C - coeff * x^m * B
            while len(C) < len(B) + m:
                C.append(0)
            for j in range(len(B)):
                C[j + m] = (C[j + m] + coeff * B[j]) % mod
            L = i + 1 - L
            B = T
            b = d
            m = 1
        else:
            coeff = (mod - d * modinv(b, mod)) % mod
            while len(C) < len(B) + m:
                C.append(0)
            for j in range(len(B)):
                C[j + m] = (C[j + m] + coeff * B[j]) % mod
            m += 1

    return L

# ---------------------------------------------------------------------------
# Float to GF(p) discretization
# ---------------------------------------------------------------------------

def float_to_gf(x, mod=MOD, scale=10**6):
    """
    Map a float coefficient to GF(mod) by rounding to integer at given scale.
    """
    val = int(round(x * scale)) % mod
    return val

# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def main():
    data_path = Path(__file__).parent.parent / "maass" / "data" / "maass_with_coefficients.json"
    out_path = Path(__file__).parent / "maass_bm_rate_results.json"

    print(f"Loading {data_path} ...")
    with open(data_path) as f:
        data = json.load(f)
    print(f"  {len(data)} forms loaded")

    # Filter: need at least max(PRIMES_50) coefficients (229th index means 229 coeffs)
    min_coeffs = PRIMES_50[-1]  # 229
    eligible = [d for d in data if len(d.get("coefficients", [])) >= min_coeffs]
    print(f"  {len(eligible)} forms with >= {min_coeffs} coefficients")

    # Sample 2000 for speed
    SAMPLE_SIZE = 2000
    if len(eligible) > SAMPLE_SIZE:
        random.seed(42)
        sample = random.sample(eligible, SAMPLE_SIZE)
        print(f"  Sampled {SAMPLE_SIZE} forms")
    else:
        sample = eligible
        print(f"  Using all {len(sample)} eligible forms")

    # Analyze each form
    bm_orders = []
    recurrent_count = 0
    non_recurrent_count = 0
    results_detail = []

    for i, form in enumerate(sample):
        coeffs = form["coefficients"]
        # Extract c_p for first 50 primes (1-indexed: c_p is coeffs[p-1])
        seq_float = [coeffs[p - 1] for p in PRIMES_50]
        seq_gf = [float_to_gf(x) for x in seq_float]

        order = berlekamp_massey(seq_gf)
        bm_orders.append(order)

        is_recurrent = order < 25
        if is_recurrent:
            recurrent_count += 1
        else:
            non_recurrent_count += 1

        results_detail.append({
            "maass_id": form["maass_id"],
            "level": form.get("level"),
            "spectral_parameter": form.get("spectral_parameter"),
            "bm_order": order,
            "recurrent": is_recurrent,
        })

        if (i + 1) % 500 == 0:
            print(f"  Processed {i+1}/{len(sample)} ...")

    total = recurrent_count + non_recurrent_count
    rate = recurrent_count / total if total > 0 else 0.0

    # BM order distribution
    order_dist = dict(sorted(Counter(bm_orders).items()))

    print(f"\n{'='*60}")
    print(f"RESULTS: Maass form BM recurrence rate")
    print(f"{'='*60}")
    print(f"  Sample size:       {total}")
    print(f"  Recurrent (BM<25): {recurrent_count} ({rate*100:.1f}%)")
    print(f"  Non-recurrent:     {non_recurrent_count} ({(1-rate)*100:.1f}%)")
    print(f"\n  Context:")
    print(f"    EC rate:    0.1%")
    print(f"    OEIS rate: 19.8%")
    print(f"    Maass rate: {rate*100:.1f}%")
    print(f"\n  BM order distribution (top 10):")
    for order, count in sorted(order_dist.items(), key=lambda x: -x[1])[:10]:
        print(f"    order {order:3d}: {count:5d} ({count/total*100:.1f}%)")

    # Summary stats
    import statistics
    print(f"\n  BM order stats:")
    print(f"    mean:   {statistics.mean(bm_orders):.1f}")
    print(f"    median: {statistics.median(bm_orders):.1f}")
    print(f"    stdev:  {statistics.stdev(bm_orders):.1f}")
    print(f"    min:    {min(bm_orders)}")
    print(f"    max:    {max(bm_orders)}")

    # Save results
    output = {
        "experiment": "maass_bm_recurrence_rate",
        "date": "2026-04-10",
        "description": "Berlekamp-Massey recurrence rate for Maass form prime-indexed coefficients",
        "method": {
            "sequence": "c_p at first 50 primes (p=2,3,5,...,229)",
            "discretization": "round(coeff * 10^6) mod 10^9+7",
            "bm_field": "GF(10^9+7)",
            "recurrence_threshold": "BM order < 25 (half sequence length)",
            "sample_size": total,
            "total_eligible": len(eligible),
            "total_forms": len(data),
        },
        "results": {
            "recurrence_rate": round(rate, 4),
            "recurrent_count": recurrent_count,
            "non_recurrent_count": non_recurrent_count,
            "context": {
                "ec_rate": 0.001,
                "oeis_rate": 0.198,
                "maass_rate": round(rate, 4),
            },
            "bm_order_distribution": {str(k): v for k, v in order_dist.items()},
            "bm_order_stats": {
                "mean": round(statistics.mean(bm_orders), 2),
                "median": statistics.median(bm_orders),
                "stdev": round(statistics.stdev(bm_orders), 2),
                "min": min(bm_orders),
                "max": max(bm_orders),
            },
        },
        "sample_details": results_detail,
    }

    with open(out_path, "w") as f:
        json.dump(output, f, indent=1)
    print(f"\nSaved to {out_path}")

if __name__ == "__main__":
    main()
