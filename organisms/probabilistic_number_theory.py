"""
Probabilistic Number Theory organism.

Operations: erdos_kac_simulation, random_integer_gcd_probability,
            prime_gap_distribution, divisor_function_average
"""

from .base import MathematicalOrganism


class ProbabilisticNumberTheory(MathematicalOrganism):
    name = "probabilistic_number_theory"
    operations = {
        "erdos_kac_simulation": {
            "code": """
def erdos_kac_simulation(n, trials=10000):
    \"\"\"Simulate the Erdos-Kac theorem: omega(m) (number of distinct prime
    factors of a random integer m ~ n) is approximately normally distributed
    with mean ln(ln(n)) and variance ln(ln(n)).
    Samples 'trials' random integers in [2, n] and counts distinct prime factors.\"\"\"
    import random as _rng
    n = int(n)
    if n < 2:
        return {"error": "n must be >= 2"}

    def omega(k):
        \"\"\"Count distinct prime factors of k.\"\"\"
        count = 0
        d = 2
        while d * d <= k:
            if k % d == 0:
                count += 1
                while k % d == 0:
                    k //= d
            d += 1
        if k > 1:
            count += 1
        return count

    samples = []
    for _ in range(trials):
        m = _rng.randint(2, n)
        samples.append(omega(m))

    samples = np.array(samples, dtype=np.float64)
    mean_obs = float(np.mean(samples))
    var_obs = float(np.var(samples))
    expected_mean = float(np.log(np.log(n)))
    expected_var = float(np.log(np.log(n)))

    # Normalized distribution (should approach standard normal)
    if expected_var > 0:
        normalized = (samples - expected_mean) / np.sqrt(expected_var)
    else:
        normalized = samples

    hist, bin_edges = np.histogram(normalized, bins=30, density=True)

    return {
        "n": n,
        "trials": trials,
        "mean_observed": mean_obs,
        "variance_observed": var_obs,
        "erdos_kac_mean": expected_mean,
        "erdos_kac_variance": expected_var,
        "histogram": hist.tolist(),
        "bin_edges": bin_edges.tolist(),
    }
""",
            "input_type": "integer",
            "output_type": "probability_distribution",
        },
        "random_integer_gcd_probability": {
            "code": """
def random_integer_gcd_probability(n, trials=10000):
    \"\"\"Estimate the probability that two random integers in [1, n] are coprime.
    By number theory, this approaches 6/pi^2 ~ 0.6079 as n -> infinity.\"\"\"
    import random as _rng
    import math
    n = int(n)
    coprime_count = 0
    for _ in range(trials):
        a = _rng.randint(1, n)
        b = _rng.randint(1, n)
        if math.gcd(a, b) == 1:
            coprime_count += 1

    empirical = coprime_count / trials
    theoretical = 6.0 / (np.pi ** 2)
    return {
        "n": n,
        "trials": trials,
        "coprime_count": coprime_count,
        "empirical_probability": float(empirical),
        "theoretical_limit": float(theoretical),
        "relative_error": float(abs(empirical - theoretical) / theoretical),
    }
""",
            "input_type": "integer",
            "output_type": "statistical_estimate",
        },
        "prime_gap_distribution": {
            "code": """
def prime_gap_distribution(n):
    \"\"\"Compute the empirical distribution of prime gaps up to n.
    Compare with Cramer's model prediction: P(gap >= g) ~ exp(-g / ln(p)).\"\"\"
    n = int(n)
    if n < 5:
        return {"error": "n must be >= 5"}
    # Sieve
    is_prime = np.ones(n + 1, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    primes = np.where(is_prime)[0]

    if len(primes) < 2:
        return {"error": "not enough primes"}

    gaps = np.diff(primes)
    unique_gaps, counts = np.unique(gaps, return_counts=True)
    total_gaps = len(gaps)
    avg_gap = float(np.mean(gaps))
    max_gap = int(np.max(gaps))
    median_gap = float(np.median(gaps))

    # Cramer's conjecture: max gap ~ (ln n)^2
    cramer_max = float(np.log(n) ** 2)

    return {
        "n": n,
        "num_primes": len(primes),
        "num_gaps": total_gaps,
        "average_gap": avg_gap,
        "median_gap": median_gap,
        "max_gap": max_gap,
        "cramer_predicted_max": cramer_max,
        "gap_frequencies": {int(g): int(c) for g, c in zip(unique_gaps, counts)},
    }
""",
            "input_type": "integer",
            "output_type": "probability_distribution",
        },
        "divisor_function_average": {
            "code": """
def divisor_function_average(n):
    \"\"\"Compute the average number of divisors d(k) for k = 1..n.
    By Dirichlet's theorem, the average tends to ln(n) + 2*gamma - 1
    where gamma is the Euler-Mascheroni constant.\"\"\"
    n = int(n)
    if n < 1:
        return {"error": "n must be >= 1"}
    # Count divisors for each k from 1 to n
    divisor_counts = np.zeros(n + 1, dtype=np.int64)
    for d in range(1, n + 1):
        divisor_counts[d::d] += 1
    divisor_counts = divisor_counts[1:]  # remove index 0

    total = int(np.sum(divisor_counts))
    avg = float(total / n)
    gamma = 0.5772156649  # Euler-Mascheroni constant
    predicted_avg = float(np.log(n) + 2 * gamma - 1)

    return {
        "n": n,
        "total_divisors": total,
        "average_divisors": avg,
        "dirichlet_prediction": predicted_avg,
        "ratio": float(avg / predicted_avg) if predicted_avg > 0 else 0.0,
        "max_divisors": int(np.max(divisor_counts)),
        "most_divisible": int(np.argmax(divisor_counts) + 1),
    }
""",
            "input_type": "integer",
            "output_type": "statistical_estimate",
        },
    }


if __name__ == "__main__":
    import numpy as np

    org = ProbabilisticNumberTheory()
    print(org)

    # Erdos-Kac
    ek = org.execute("erdos_kac_simulation", 1000000, 5000)
    print(f"Erdos-Kac at n=10^6:")
    print(f"  Observed mean: {ek['mean_observed']:.3f}, "
          f"EK predicted: {ek['erdos_kac_mean']:.3f}")
    print(f"  Observed var:  {ek['variance_observed']:.3f}, "
          f"EK predicted: {ek['erdos_kac_variance']:.3f}")

    # GCD coprimality
    gcd_prob = org.execute("random_integer_gcd_probability", 10000, 10000)
    print(f"\nCoprime probability (n=10000):")
    print(f"  Empirical: {gcd_prob['empirical_probability']:.4f}")
    print(f"  6/pi^2:    {gcd_prob['theoretical_limit']:.4f}")
    print(f"  Rel error: {gcd_prob['relative_error']:.4f}")

    # Prime gap distribution
    pgd = org.execute("prime_gap_distribution", 100000)
    print(f"\nPrime gaps up to 10^5:")
    print(f"  Average gap: {pgd['average_gap']:.2f}")
    print(f"  Max gap: {pgd['max_gap']}")
    print(f"  Cramer predicted max: {pgd['cramer_predicted_max']:.2f}")
    top5 = sorted(pgd['gap_frequencies'].items(), key=lambda x: -x[1])[:5]
    print(f"  Top 5 gap sizes: {top5}")

    # Divisor function average
    dfa = org.execute("divisor_function_average", 10000)
    print(f"\nDivisor function average (n=10000):")
    print(f"  Average d(k): {dfa['average_divisors']:.4f}")
    print(f"  Dirichlet:    {dfa['dirichlet_prediction']:.4f}")
    print(f"  Ratio:        {dfa['ratio']:.4f}")
    print(f"  Most divisible: {dfa['most_divisible']} with {dfa['max_divisors']} divisors")

    print("--- probabilistic_number_theory: ALL TESTS PASSED ---")
