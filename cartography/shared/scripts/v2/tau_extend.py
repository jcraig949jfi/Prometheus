"""
Ramanujan tau function computation + Lehmer's Conjecture analysis
==================================================================
Extends tau(n) from 30 OEIS terms to ~100K values using:
1. Direct q-expansion of Delta = q * prod_{n>=1} (1-q^n)^24
2. Multiplicativity: tau(mn) = tau(m)*tau(n) for gcd(m,n)=1
3. Prime power recurrence: tau(p^{k+1}) = tau(p)*tau(p^k) - p^11*tau(p^{k-2})

Then runs:
- Ramanujan congruence verification (mod 691, mod 23, etc.)
- Mod-p residue class distribution
- Weight-12 Sato-Tate distribution check
- Impossibility scan (simultaneous vanishing mod many primes)

Usage:
    python tau_extend.py
    python tau_extend.py --max-n 1000000
"""

import time
import json
import argparse
from collections import Counter, defaultdict
from pathlib import Path
from math import sqrt, pi, log, gcd


def sieve_primes(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]


def compute_tau_qexpansion(N):
    """
    Compute tau(n) for n=1..N via the q-expansion of Delta.

    Delta(q) = q * prod_{n>=1} (1-q^n)^24 = sum_{n>=1} tau(n) * q^n

    We compute prod (1-q^n)^24 as a power series mod q^{N+1}.
    The key: (1-q^n)^24 = sum_k C(24,k)*(-1)^k * q^{nk}
    But it's faster to use Euler's pentagonal trick iteratively.

    Actually, the fastest approach for moderate N: compute eta(q)^24 directly.
    eta(q) = q^{1/24} * prod (1-q^n), so Delta = eta^24 = q * prod(1-q^n)^24.

    We compute the coefficients of prod_{n=1}^{N} (1-q^n)^24 as a polynomial mod q^{N+1}.
    """
    # Initialize: coefficient array for prod (1-q^n)^24
    # Start with [1, 0, 0, ...] and multiply by (1-q^n)^24 for each n

    # More efficient: compute prod(1-q^n) first, then raise to 24th power
    # But raising a polynomial to 24th power is expensive.
    # Better: compute prod(1-q^n)^24 by repeated multiplication.

    # Actually, use the recurrence for Dedekind eta:
    # prod(1-q^n) has a known expansion via pentagonal theorem:
    # prod(1-q^n) = sum_{k=-inf}^{inf} (-1)^k * q^{k(3k-1)/2}

    # But we need the 24th power. Let's just do it iteratively.
    # For each n, multiply current series by (1 - q^n)^24.

    # (1-x)^24 = sum_{k=0}^{24} C(24,k) * (-1)^k * x^k
    binom24 = [1]
    for k in range(1, 25):
        binom24.append(binom24[-1] * (24 - k + 1) // k)
    # binom24[k] = C(24, k)
    signs = [(-1)**k * binom24[k] for k in range(25)]

    # coeffs[j] = coefficient of q^j in the product so far
    coeffs = [0] * (N + 1)
    coeffs[0] = 1

    for n in range(1, N + 1):
        # Multiply by (1 - q^n)^24 = sum_{k=0}^{24} signs[k] * q^{n*k}
        # Process from high to low to avoid overwriting
        # For each existing coeff[j], add signs[k] * coeffs[j] at position j + n*k
        # But this is O(N * 24) per n, total O(24 * N^2) — too slow for large N

        # Better: multiply by (1 - q^n)^24 in-place, processing from high degree down
        new_coeffs = list(coeffs)
        for k in range(1, 25):
            offset = n * k
            if offset > N:
                break
            for j in range(N, offset - 1, -1):
                new_coeffs[j] += signs[k] * coeffs[j - offset]
        coeffs = new_coeffs

        if n % 1000 == 0:
            print(f"  q-expansion: processed n={n}/{N}", flush=True)

    # Delta = q * prod(1-q^n)^24, so tau(m) = coeffs[m-1]
    tau = {}
    for m in range(1, N + 1):
        tau[m] = coeffs[m - 1]

    return tau


def compute_tau_sieve(N, tau_primes):
    """
    Compute tau(n) for n=1..N using known tau(p) values and multiplicativity.

    tau_primes: dict {p: tau(p)} for primes p
    """
    tau = {1: 1}

    # Compute tau(p^k) for all prime powers
    primes = sorted(tau_primes.keys())
    for p in primes:
        tau[p] = tau_primes[p]
        pk = p * p
        while pk <= N:
            # tau(p^{k+1}) = tau(p)*tau(p^k) - p^11*tau(p^{k-1})
            tau[pk] = tau[p] * tau[pk // p] - p**11 * tau[pk // (p * p)]
            pk *= p

    # Extend by multiplicativity using sieve
    # For each n, find its factorization and compute tau(n) = prod tau(p^k)
    for n in range(2, N + 1):
        if n in tau:
            continue
        m = n
        result = 1
        computable = True
        for p in primes:
            if p * p > m:
                break
            if m % p == 0:
                pk = 1
                while m % p == 0:
                    pk *= p
                    m //= p
                if pk not in tau:
                    computable = False
                    break
                result *= tau[pk]
        if not computable:
            continue
        if m > 1:
            # m is a remaining prime factor
            if m in tau_primes:
                result *= tau_primes[m]
            else:
                continue  # Can't compute
        tau[n] = result

    return tau


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=10000,
                        help="Compute tau(n) up to this value")
    parser.add_argument("--method", choices=["qexp", "sieve", "auto"], default="auto",
                        help="Computation method")
    args = parser.parse_args()

    N = args.max_n
    method = args.method

    print("RAMANUJAN TAU FUNCTION + LEHMER'S CONJECTURE ANALYSIS")
    print("=" * 72)
    print(f"Computing tau(n) for n = 1..{N}")
    print()

    # Step 1: Get tau(p) for primes
    # For small N (<=5000), q-expansion is fast and gives ALL values
    # For large N, use sieve with known tau(p)

    if method == "auto":
        method = "qexp" if N <= 5000 else "sieve"

    t0 = time.time()

    if method == "qexp":
        print("Method: q-expansion of Delta = q * prod(1-q^n)^24")
        tau = compute_tau_qexpansion(N)
        print(f"Computed {len(tau)} values in {time.time()-t0:.1f}s")
    else:
        # Need tau(p) for primes up to N
        # First compute via q-expansion up to a reasonable bound
        prime_bound = min(N, 5000)
        print(f"Method: sieve (q-expansion to {prime_bound}, then multiplicativity)")
        print(f"Step 1: q-expansion to {prime_bound}...")
        tau_small = compute_tau_qexpansion(prime_bound)
        primes = sieve_primes(prime_bound)
        tau_primes = {p: tau_small[p] for p in primes if p in tau_small}
        print(f"  Got tau(p) for {len(tau_primes)} primes (up to p={max(tau_primes.keys())})")

        print(f"Step 2: Sieve extension to {N}...")
        tau = compute_tau_sieve(N, tau_primes)
        print(f"Computed {len(tau)} values in {time.time()-t0:.1f}s")

    coverage = len(tau) / N * 100
    print(f"Coverage: {len(tau)}/{N} ({coverage:.1f}%)")
    print()

    # ─── Verification: OEIS A000594 ───
    print("=" * 72)
    print("VERIFICATION: OEIS A000594")
    print("=" * 72)
    oeis_path = Path(__file__).resolve().parents[3] / "oeis" / "data" / "stripped_new.txt"
    oeis_tau = []
    with open(oeis_path, 'r', errors='ignore') as f:
        for line in f:
            if line.startswith('A000594'):
                for t in line.strip().split(','):
                    t = t.strip()
                    if t and not t.startswith('A'):
                        try:
                            oeis_tau.append(int(t))
                        except:
                            pass
                break

    match = 0
    mismatch = 0
    for i, expected in enumerate(oeis_tau):
        n = i + 1
        if n in tau:
            if tau[n] == expected:
                match += 1
            else:
                mismatch += 1
                if mismatch <= 5:
                    print(f"  MISMATCH at n={n}: computed={tau[n]}, OEIS={expected}")

    print(f"OEIS match: {match}/{len(oeis_tau)} ({mismatch} mismatches)")
    print()

    # ─── Ramanujan Congruences ───
    print("=" * 72)
    print("RAMANUJAN CONGRUENCES")
    print("=" * 72)

    def sigma_k(n, k):
        """Sum of k-th powers of divisors of n."""
        s = 0
        for d in range(1, int(n**0.5) + 1):
            if n % d == 0:
                s += d**k
                if d != n // d:
                    s += (n // d)**k
        return s

    # tau(n) = sigma_11(n) (mod 691) — Ramanujan
    # tau(n) = sigma_11(n) (mod 2^11 = 2048) — Kolberg?
    # tau(n) = n^2 * sigma_7(n) (mod 3^3 = 27) — related
    # tau(n) = sigma_11(n) (mod 7)
    congruences = [
        (691, lambda n: sigma_k(n, 11), "sigma_11(n)"),
        (7, lambda n: sigma_k(n, 11), "sigma_11(n)"),
        (5, lambda n: sigma_k(n, 11), "sigma_11(n)"),
        (3, lambda n: sigma_k(n, 11), "sigma_11(n)"),
        (2, lambda n: sigma_k(n, 11), "sigma_11(n)"),
        (23, lambda n: sigma_k(n, 11), "sigma_11(n)"),
    ]

    test_range = min(200, N)
    for mod, func, label in congruences:
        passes = 0
        fails = 0
        for n in range(1, test_range + 1):
            if n not in tau:
                continue
            expected = func(n) % mod
            actual = tau[n] % mod
            if actual == expected:
                passes += 1
            else:
                fails += 1

        total = passes + fails
        status = "PASS" if fails == 0 else f"{fails} FAIL"
        print(f"  tau(n) = {label} (mod {mod:>3}): {passes}/{total} {status}")

    print()

    # ─── Mod-p Distribution ───
    print("=" * 72)
    print("MOD-p RESIDUE CLASS DISTRIBUTION")
    print("=" * 72)

    test_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 691]
    tau_values = sorted(tau.items())

    for p in test_primes:
        residues = Counter(v % p for _, v in tau_values)
        n_classes = len(residues)
        zero_count = residues.get(0, 0)
        zero_frac = zero_count / len(tau_values) if tau_values else 0
        expected_frac = 1 / p

        print(f"  mod {p:>3}: {n_classes:>3}/{p} classes, "
              f"zero-class: {zero_count}/{len(tau_values)} "
              f"({100*zero_frac:.1f}%, expected {100*expected_frac:.1f}%)")

    print()

    # ─── Weight-12 Sato-Tate ───
    print("=" * 72)
    print("WEIGHT-12 SATO-TATE DISTRIBUTION")
    print("=" * 72)
    print("For weight k=12: a_p should follow the Sato-Tate distribution")
    print("scaled by p^{(k-1)/2} = p^{11/2}.")
    print("Normalized: x_p = a_p / (2 * p^{11/2}) should lie in [-1, 1]")
    print("with density (2/pi) * sqrt(1 - x^2).")
    print()

    primes_list = sieve_primes(min(N, 5000))
    x_values = []
    for p in primes_list:
        if p in tau:
            x = tau[p] / (2 * p ** 5.5)
            x_values.append(x)

    if x_values:
        # Histogram in 10 bins from -1 to 1
        bins = 10
        hist = [0] * bins
        for x in x_values:
            b = int((x + 1) / 2 * bins)
            b = max(0, min(bins - 1, b))
            hist[b] += 1

        # Expected: (2/pi) * sqrt(1 - x^2) integrated over each bin
        print(f"Sato-Tate histogram ({len(x_values)} primes):")
        for i in range(bins):
            x_lo = -1 + 2 * i / bins
            x_hi = -1 + 2 * (i + 1) / bins
            x_mid = (x_lo + x_hi) / 2
            expected_density = 2 / pi * sqrt(max(0, 1 - x_mid**2))
            expected_count = expected_density * (2 / bins) * len(x_values)
            bar = "#" * int(hist[i] / max(hist) * 40) if max(hist) > 0 else ""
            print(f"  [{x_lo:+.1f},{x_hi:+.1f}]: {hist[i]:>4} (exp {expected_count:>5.1f}) {bar}")

        # Moments
        mean = sum(x_values) / len(x_values)
        var = sum((x - mean)**2 for x in x_values) / len(x_values)
        m4 = sum((x - mean)**4 for x in x_values) / len(x_values)
        print(f"\n  Mean: {mean:.6f} (expected: 0)")
        print(f"  Variance: {var:.6f} (expected: 1/4 = 0.2500)")
        print(f"  4th moment: {m4:.6f} (expected: 2/16 = 0.1250)")
        print(f"  |x| > 1 count: {sum(1 for x in x_values if abs(x) > 1)} "
              f"(should be 0 by Ramanujan-Petersson)")

    print()

    # ─── Impossibility Scan ───
    print("=" * 72)
    print("IMPOSSIBILITY SCAN (Lehmer)")
    print("=" * 72)
    print("If tau(n)=0, then tau(n)=0 mod p for ALL primes p.")
    print("Checking: how many n have tau(n)=0 mod p for MANY primes simultaneously.")
    print()

    scan_primes = sieve_primes(100)
    max_simultaneous = 0
    best_n = 0

    for n, v in tau.items():
        if n <= 1:
            continue
        count = sum(1 for p in scan_primes if v % p == 0)
        if count > max_simultaneous:
            max_simultaneous = count
            best_n = n

    print(f"Max simultaneous vanishing: n={best_n} vanishes mod {max_simultaneous}/{len(scan_primes)} primes")
    if best_n > 0 and best_n in tau:
        # Show which primes
        vanishing_primes = [p for p in scan_primes if tau[best_n] % p == 0]
        print(f"  tau({best_n}) = {tau[best_n]}")
        print(f"  Vanishes mod: {vanishing_primes}")

    # Distribution of simultaneous vanishing counts
    vanish_dist = Counter()
    for n, v in tau.items():
        if n <= 1:
            continue
        count = sum(1 for p in scan_primes if v % p == 0)
        vanish_dist[count] += 1

    print(f"\nDistribution of simultaneous vanishing count:")
    for k in sorted(vanish_dist.keys(), reverse=True)[:10]:
        print(f"  vanishes mod {k:>2} primes: {vanish_dist[k]:>5} values of n")

    # ─── Save results ───
    out = {
        "N": N,
        "n_computed": len(tau),
        "coverage_pct": round(coverage, 1),
        "oeis_match": match,
        "oeis_mismatch": mismatch,
        "zeros_found": sum(1 for n, v in tau.items() if v == 0 and n > 1),
        "max_simultaneous_vanishing": max_simultaneous,
        "best_n": best_n,
    }

    out_path = Path(__file__).parent / "tau_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults saved to {out_path}")

    # Also save tau(p) for primes (useful for other scripts)
    primes_out = {}
    for p in sieve_primes(min(N, 5000)):
        if p in tau:
            primes_out[str(p)] = tau[p]

    tau_primes_path = Path(__file__).parent / "tau_primes.json"
    with open(tau_primes_path, "w") as f:
        json.dump(primes_out, f)
    print(f"tau(p) for {len(primes_out)} primes saved to {tau_primes_path}")


if __name__ == "__main__":
    main()
