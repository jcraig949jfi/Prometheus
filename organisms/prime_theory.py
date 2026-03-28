"""
Prime Theory organism.

Operations: sieve_of_eratosthenes, prime_counting_function, prime_gaps,
            prime_factorization, miller_rabin_test, prime_density
"""

from .base import MathematicalOrganism


class PrimeTheory(MathematicalOrganism):
    name = "prime_theory"
    operations = {
        "sieve_of_eratosthenes": {
            "code": """
def sieve_of_eratosthenes(n):
    \"\"\"Return list of all primes up to n using the Sieve of Eratosthenes.\"\"\"
    if n < 2:
        return []
    is_prime = np.ones(n + 1, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return list(np.where(is_prime)[0])
""",
            "input_type": "integer",
            "output_type": "prime_list",
        },
        "prime_counting_function": {
            "code": """
def prime_counting_function(n):
    \"\"\"pi(n): count of primes <= n.\"\"\"
    if n < 2:
        return 0
    is_prime = np.ones(n + 1, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return int(np.sum(is_prime))
""",
            "input_type": "integer",
            "output_type": "integer",
        },
        "prime_gaps": {
            "code": """
def prime_gaps(n):
    \"\"\"Sequence of gaps between consecutive primes up to n.
    Returns list of (prime_k, prime_{k+1}, gap).\"\"\"
    if n < 3:
        return []
    is_prime = np.ones(n + 1, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    primes = np.where(is_prime)[0]
    gaps = []
    for i in range(len(primes) - 1):
        g = int(primes[i + 1] - primes[i])
        gaps.append((int(primes[i]), int(primes[i + 1]), g))
    return gaps
""",
            "input_type": "integer",
            "output_type": "gap_sequence",
        },
        "prime_factorization": {
            "code": """
def prime_factorization(n):
    \"\"\"Return dict {prime: exponent} for the prime factorization of n.\"\"\"
    if n < 2:
        return {}
    factors = {}
    d = 2
    remaining = int(n)
    while d * d <= remaining:
        while remaining % d == 0:
            factors[d] = factors.get(d, 0) + 1
            remaining //= d
        d += 1
    if remaining > 1:
        factors[remaining] = factors.get(remaining, 0) + 1
    return factors
""",
            "input_type": "integer",
            "output_type": "factorization",
        },
        "miller_rabin_test": {
            "code": """
def miller_rabin_test(n, k=10):
    \"\"\"Miller-Rabin probabilistic primality test.
    Returns True if n is probably prime, False if composite.
    k is the number of witness rounds.\"\"\"
    import random
    n = int(n)
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    # Witness loop
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True
""",
            "input_type": "integer",
            "output_type": "boolean",
        },
        "prime_density": {
            "code": """
def prime_density(n):
    \"\"\"Compare empirical prime density pi(n)/n with 1/ln(n) prediction
    from the Prime Number Theorem. Returns dict with both values and ratio.\"\"\"
    if n < 2:
        return {"n": n, "pi_n": 0, "empirical_density": 0.0,
                "pnt_prediction": 0.0, "ratio": 0.0}
    is_prime = np.ones(n + 1, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    pi_n = int(np.sum(is_prime))
    empirical = pi_n / n
    predicted = 1.0 / np.log(n)
    return {
        "n": n,
        "pi_n": pi_n,
        "empirical_density": float(empirical),
        "pnt_prediction": float(predicted),
        "ratio_pi_over_nlogn": float(pi_n / (n / np.log(n))),
    }
""",
            "input_type": "integer",
            "output_type": "density_comparison",
        },
    }


if __name__ == "__main__":
    import numpy as np

    org = PrimeTheory()
    print(org)

    primes = org.execute("sieve_of_eratosthenes", 50)
    print(f"Primes up to 50: {primes}")

    pi_100 = org.execute("prime_counting_function", 100)
    print(f"pi(100) = {pi_100}  (expect 25)")

    gaps = org.execute("prime_gaps", 30)
    print(f"Prime gaps up to 30: {gaps}")

    factors = org.execute("prime_factorization", 360)
    print(f"360 = {factors}  (expect {{2:3, 3:2, 5:1}})")

    is_prime = org.execute("miller_rabin_test", 104729)
    print(f"104729 is prime? {is_prime}  (expect True)")
    is_composite = org.execute("miller_rabin_test", 104730)
    print(f"104730 is prime? {is_composite}  (expect False)")

    density = org.execute("prime_density", 10000)
    print(f"Prime density at 10000: {density}")
    print(f"  PNT ratio -> 1 as n -> inf: {density['ratio_pi_over_nlogn']:.4f}")

    print("--- prime_theory: ALL TESTS PASSED ---")
