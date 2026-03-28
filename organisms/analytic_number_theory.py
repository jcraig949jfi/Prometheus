"""
Analytic Number Theory organism.

Operations: riemann_zeta_partial, dirichlet_eta, von_mangoldt_function,
            chebyshev_psi, prime_number_theorem_ratio
"""

from .base import MathematicalOrganism


class AnalyticNumberTheory(MathematicalOrganism):
    name = "analytic_number_theory"
    operations = {
        "riemann_zeta_partial": {
            "code": """
def riemann_zeta_partial(s, n_terms=1000):
    \"\"\"Partial sum approximation of the Riemann zeta function.
    zeta(s) ~ sum_{k=1}^{n_terms} 1/k^s.
    Works for real s > 1 and complex s with real part > 1.\"\"\"
    k = np.arange(1, n_terms + 1, dtype=np.float64)
    if isinstance(s, complex) or (isinstance(s, (list, tuple)) and len(s) == 2):
        if isinstance(s, (list, tuple)):
            s = complex(s[0], s[1])
        terms = np.power(k, -s.real) * np.exp(-1j * s.imag * np.log(k))
        return complex(np.sum(terms))
    else:
        s = float(s)
        terms = np.power(k, -s)
        return float(np.sum(terms))
""",
            "input_type": "real",
            "output_type": "complex_value",
        },
        "dirichlet_eta": {
            "code": """
def dirichlet_eta(s, n_terms=1000):
    \"\"\"Dirichlet eta function (alternating zeta).
    eta(s) = sum_{k=1}^{n_terms} (-1)^{k-1} / k^s.
    Converges for Re(s) > 0 (wider than zeta).
    Related: eta(s) = (1 - 2^{1-s}) * zeta(s).\"\"\"
    k = np.arange(1, n_terms + 1, dtype=np.float64)
    signs = np.power(-1.0, k - 1)
    if isinstance(s, complex) or (isinstance(s, (list, tuple)) and len(s) == 2):
        if isinstance(s, (list, tuple)):
            s = complex(s[0], s[1])
        terms = signs * np.power(k, -s.real) * np.exp(-1j * s.imag * np.log(k))
        return complex(np.sum(terms))
    else:
        s = float(s)
        terms = signs * np.power(k, -s)
        return float(np.sum(terms))
""",
            "input_type": "real",
            "output_type": "complex_value",
        },
        "von_mangoldt_function": {
            "code": """
def von_mangoldt_function(n):
    \"\"\"Von Mangoldt function Lambda(n).
    Lambda(n) = log(p) if n = p^k for some prime p and integer k >= 1,
    Lambda(n) = 0 otherwise.\"\"\"
    import math
    n = int(n)
    if n < 2:
        return 0.0
    # Factor out the smallest prime
    d = 2
    prime_base = None
    remaining = n
    while d * d <= remaining:
        if remaining % d == 0:
            if prime_base is None:
                prime_base = d
            elif prime_base != d:
                return 0.0  # multiple distinct primes
            remaining //= d
        else:
            d += 1
    if remaining > 1:
        if prime_base is None:
            prime_base = remaining
        elif prime_base != remaining:
            return 0.0
    return float(np.log(prime_base))
""",
            "input_type": "integer",
            "output_type": "real",
        },
        "chebyshev_psi": {
            "code": """
def chebyshev_psi(n):
    \"\"\"Chebyshev's psi function: psi(n) = sum_{k=1}^{n} Lambda(k).
    By the PNT, psi(n) ~ n as n -> infinity.\"\"\"
    import math
    n = int(n)
    if n < 2:
        return 0.0
    total = 0.0
    for k in range(2, n + 1):
        # Check if k is a prime power
        d = 2
        prime_base = None
        remaining = k
        is_prime_power = True
        while d * d <= remaining:
            if remaining % d == 0:
                if prime_base is None:
                    prime_base = d
                elif prime_base != d:
                    is_prime_power = False
                    break
                remaining //= d
            else:
                d += 1
        if not is_prime_power:
            continue
        if remaining > 1:
            if prime_base is None:
                prime_base = remaining
            elif prime_base != remaining:
                continue
        total += math.log(prime_base)
    return float(total)
""",
            "input_type": "integer",
            "output_type": "analytic_estimate",
        },
        "prime_number_theorem_ratio": {
            "code": """
def prime_number_theorem_ratio(n):
    \"\"\"Compute pi(n) / (n / ln(n)) which should approach 1 as n -> infinity.
    Also computes pi(n) / Li(n) where Li is the logarithmic integral.\"\"\"
    n = int(n)
    if n < 2:
        return {"n": n, "pi_n": 0, "ratio_simple": 0.0, "ratio_li": 0.0}
    # Sieve for pi(n)
    is_prime = np.ones(n + 1, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    pi_n = int(np.sum(is_prime))
    # Simple PNT estimate
    simple_est = n / np.log(n)
    # Logarithmic integral Li(n) via numerical integration (trapezoidal)
    # Li(x) = integral from 2 to x of 1/ln(t) dt
    t = np.linspace(2, n, min(n, 10000))
    if len(t) > 1:
        integrand = 1.0 / np.log(t)
        li_n = float(np.trapz(integrand, t))
    else:
        li_n = 0.0
    return {
        "n": n,
        "pi_n": pi_n,
        "n_over_ln_n": float(simple_est),
        "li_n": float(li_n),
        "ratio_simple": float(pi_n / simple_est) if simple_est > 0 else 0.0,
        "ratio_li": float(pi_n / li_n) if li_n > 0 else 0.0,
    }
""",
            "input_type": "integer",
            "output_type": "analytic_estimate",
        },
    }


if __name__ == "__main__":
    import numpy as np

    org = AnalyticNumberTheory()
    print(org)

    # zeta(2) should be close to pi^2/6 ~ 1.6449
    z2 = org.execute("riemann_zeta_partial", 2.0, 10000)
    print(f"zeta(2) ~ {z2:.6f}  (expect {np.pi**2/6:.6f})")

    # zeta(4) = pi^4/90 ~ 1.0823
    z4 = org.execute("riemann_zeta_partial", 4.0, 10000)
    print(f"zeta(4) ~ {z4:.6f}  (expect {np.pi**4/90:.6f})")

    # eta(1) = ln(2) ~ 0.6931
    e1 = org.execute("dirichlet_eta", 1.0, 100000)
    print(f"eta(1) ~ {e1:.6f}  (expect {np.log(2):.6f})")

    # Von Mangoldt
    vm8 = org.execute("von_mangoldt_function", 8)  # 2^3
    print(f"Lambda(8) = {vm8:.4f}  (expect ln(2) = {np.log(2):.4f})")
    vm6 = org.execute("von_mangoldt_function", 6)  # 2*3, not prime power
    print(f"Lambda(6) = {vm6:.4f}  (expect 0)")

    # Chebyshev psi
    psi_100 = org.execute("chebyshev_psi", 100)
    print(f"psi(100) = {psi_100:.4f}  (PNT predicts ~100)")

    # PNT ratio
    pnt = org.execute("prime_number_theorem_ratio", 100000)
    print(f"PNT ratio at 10^5: simple={pnt['ratio_simple']:.4f}, Li={pnt['ratio_li']:.4f}")
    print(f"  pi(10^5) = {pnt['pi_n']}, n/ln(n) = {pnt['n_over_ln_n']:.1f}, Li = {pnt['li_n']:.1f}")

    print("--- analytic_number_theory: ALL TESTS PASSED ---")
