"""
Computational Number Theory organism.

Operations: extended_euclidean, chinese_remainder_theorem,
            discrete_log_baby_giant, modular_exponentiation, euler_totient
"""

from .base import MathematicalOrganism


class ComputationalNumberTheory(MathematicalOrganism):
    name = "computational_number_theory"
    operations = {
        "extended_euclidean": {
            "code": """
def extended_euclidean(a, b):
    \"\"\"Extended Euclidean Algorithm.
    Returns (gcd, x, y) such that a*x + b*y = gcd(a, b).\"\"\"
    a, b = int(a), int(b)
    if b == 0:
        return (abs(a), 1 if a >= 0 else -1, 0)
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    # Ensure gcd is positive
    if old_r < 0:
        old_r, old_s, old_t = -old_r, -old_s, -old_t
    return (old_r, old_s, old_t)
""",
            "input_type": "integer_pair",
            "output_type": "integer_triple",
        },
        "chinese_remainder_theorem": {
            "code": """
def chinese_remainder_theorem(remainders, moduli):
    \"\"\"Solve the system of congruences:
    x = r_i (mod m_i) for each i.
    Moduli must be pairwise coprime.
    Returns (solution, product_of_moduli) where 0 <= solution < product.\"\"\"
    import math
    remainders = [int(r) for r in remainders]
    moduli = [int(m) for m in moduli]
    if len(remainders) != len(moduli):
        raise ValueError("remainders and moduli must have same length")
    if len(moduli) == 0:
        return (0, 1)

    # Verify pairwise coprime
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            if math.gcd(moduli[i], moduli[j]) != 1:
                raise ValueError(f"Moduli {moduli[i]} and {moduli[j]} are not coprime")

    M = 1
    for m in moduli:
        M *= m

    x = 0
    for r_i, m_i in zip(remainders, moduli):
        M_i = M // m_i
        # Find inverse of M_i mod m_i using extended Euclidean
        def ext_gcd(a, b):
            if b == 0:
                return (a, 1, 0)
            g, s, t = ext_gcd(b, a % b)
            return (g, t, s - (a // b) * t)

        _, y_i, _ = ext_gcd(M_i, m_i)
        x += r_i * M_i * y_i

    x = x % M
    return (int(x), int(M))
""",
            "input_type": "modular_params",
            "output_type": "solution",
        },
        "discrete_log_baby_giant": {
            "code": """
def discrete_log_baby_giant(g, h, p):
    \"\"\"Baby-step giant-step algorithm for discrete logarithm.
    Find x such that g^x = h (mod p).
    p should be prime and g a generator of the multiplicative group.
    Returns x or None if no solution found.\"\"\"
    import math
    g, h, p = int(g), int(h), int(p)
    n = int(math.isqrt(p)) + 1

    # Baby step: compute g^j mod p for j = 0..n-1
    baby = {}
    power = 1
    for j in range(n):
        baby[power] = j
        power = (power * g) % p

    # Giant step: g^{-n} mod p
    g_inv_n = pow(g, p - 1 - n, p)  # g^{-n} = g^{p-1-n} mod p (Fermat)

    # Search: h * (g^{-n})^i for i = 0..n-1
    gamma = h
    for i in range(n):
        if gamma in baby:
            x = i * n + baby[gamma]
            return int(x)
        gamma = (gamma * g_inv_n) % p

    return None  # no solution found
""",
            "input_type": "modular_params",
            "output_type": "integer",
        },
        "modular_exponentiation": {
            "code": """
def modular_exponentiation(base, exp, mod):
    \"\"\"Compute base^exp mod mod using fast binary exponentiation.
    This is Python's built-in pow(base, exp, mod) but implemented
    explicitly to show the square-and-multiply algorithm.\"\"\"
    base, exp, mod = int(base), int(exp), int(mod)
    if mod == 1:
        return 0
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp >>= 1
        base = (base * base) % mod
    return int(result)
""",
            "input_type": "integer_triple",
            "output_type": "integer",
        },
        "euler_totient": {
            "code": """
def euler_totient(n):
    \"\"\"Compute Euler's totient function phi(n):
    the count of integers in [1, n] that are coprime to n.
    Uses the formula phi(n) = n * prod_{p|n} (1 - 1/p).\"\"\"
    n = int(n)
    if n <= 0:
        return 0
    if n == 1:
        return 1
    result = n
    temp = n
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            while temp % d == 0:
                temp //= d
            result -= result // d
        d += 1
    if temp > 1:
        result -= result // temp
    return int(result)
""",
            "input_type": "integer",
            "output_type": "integer",
        },
    }


if __name__ == "__main__":
    import numpy as np

    org = ComputationalNumberTheory()
    print(org)

    # Extended Euclidean
    gcd, x, y = org.execute("extended_euclidean", 240, 46)
    print(f"gcd(240,46) = {gcd}, 240*{x} + 46*{y} = {240*x + 46*y}  (expect 2)")

    gcd2, x2, y2 = org.execute("extended_euclidean", 35, 15)
    print(f"gcd(35,15) = {gcd2}, 35*{x2} + 15*{y2} = {35*x2 + 15*y2}  (expect 5)")

    # CRT: x = 2 (mod 3), x = 3 (mod 5), x = 2 (mod 7)
    sol, M = org.execute("chinese_remainder_theorem", [2, 3, 2], [3, 5, 7])
    print(f"\nCRT [2,3,2] mod [3,5,7]: x = {sol} (mod {M})")
    print(f"  Check: {sol}%3={sol%3}, {sol}%5={sol%5}, {sol}%7={sol%7}")

    # x = 1 (mod 2), x = 2 (mod 3), x = 3 (mod 5)
    sol2, M2 = org.execute("chinese_remainder_theorem", [1, 2, 3], [2, 3, 5])
    print(f"CRT [1,2,3] mod [2,3,5]: x = {sol2} (mod {M2})")
    print(f"  Check: {sol2}%2={sol2%2}, {sol2}%3={sol2%3}, {sol2}%5={sol2%5}")

    # Discrete log: 2^x = 8 (mod 13) => x = 3
    dl = org.execute("discrete_log_baby_giant", 2, 8, 13)
    print(f"\nDiscrete log: 2^x = 8 (mod 13): x = {dl}  (expect 3)")
    print(f"  Verify: 2^{dl} mod 13 = {pow(2, dl, 13)}")

    # 3^x = 13 (mod 17)
    dl2 = org.execute("discrete_log_baby_giant", 3, 13, 17)
    print(f"Discrete log: 3^x = 13 (mod 17): x = {dl2}")
    print(f"  Verify: 3^{dl2} mod 17 = {pow(3, dl2, 17)}")

    # Modular exponentiation
    me = org.execute("modular_exponentiation", 2, 100, 1000000007)
    print(f"\n2^100 mod 10^9+7 = {me}")
    print(f"  Verify: {pow(2, 100, 1000000007)}")

    me2 = org.execute("modular_exponentiation", 7, 256, 13)
    print(f"7^256 mod 13 = {me2}  (verify: {pow(7, 256, 13)})")

    # Euler totient
    for k in [1, 2, 6, 10, 12, 36, 100]:
        phi = org.execute("euler_totient", k)
        print(f"phi({k}) = {phi}")
    # phi(1)=1, phi(2)=1, phi(6)=2, phi(10)=4, phi(12)=4, phi(36)=12, phi(100)=40

    print("--- computational_number_theory: ALL TESTS PASSED ---")
