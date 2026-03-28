"""
Algebraic Number Theory organism.

Operations: gaussian_integers_norm, quadratic_residues, legendre_symbol,
            continued_fraction, pell_equation_solve
"""

from .base import MathematicalOrganism


class AlgebraicNumberTheory(MathematicalOrganism):
    name = "algebraic_number_theory"
    operations = {
        "gaussian_integers_norm": {
            "code": """
def gaussian_integers_norm(a, b):
    \"\"\"Compute the norm of a + bi in the Gaussian integers Z[i].
    N(a + bi) = a^2 + b^2.\"\"\"
    return int(a * a + b * b)
""",
            "input_type": "integer_pair",
            "output_type": "integer",
        },
        "quadratic_residues": {
            "code": """
def quadratic_residues(p):
    \"\"\"Return the set of quadratic residues modulo p (p should be an odd prime).
    QR(p) = {a^2 mod p : a in 1..p-1}.\"\"\"
    p = int(p)
    residues = set()
    for a in range(1, p):
        residues.add((a * a) % p)
    return sorted(residues)
""",
            "input_type": "integer",
            "output_type": "algebraic_structure",
        },
        "legendre_symbol": {
            "code": """
def legendre_symbol(a, p):
    \"\"\"Compute the Legendre symbol (a/p) using Euler's criterion.
    Returns 1 if a is a QR mod p, -1 if not, 0 if p divides a.
    p must be an odd prime.\"\"\"
    a = int(a) % int(p)
    p = int(p)
    if a == 0:
        return 0
    result = pow(a, (p - 1) // 2, p)
    if result == p - 1:
        return -1
    return int(result)
""",
            "input_type": "integer_pair",
            "output_type": "integer",
        },
        "continued_fraction": {
            "code": """
def continued_fraction(numerator, denominator=1):
    \"\"\"Compute the continued fraction expansion of numerator/denominator.
    Returns list of partial quotients [a0; a1, a2, ...].\"\"\"
    from math import gcd
    a = int(numerator)
    b = int(denominator)
    if b == 0:
        return []
    if b < 0:
        a, b = -a, -b
    quotients = []
    while b != 0:
        q = a // b
        quotients.append(q)
        a, b = b, a - q * b
    return quotients
""",
            "input_type": "rational",
            "output_type": "algebraic_structure",
        },
        "pell_equation_solve": {
            "code": """
def pell_equation_solve(d):
    \"\"\"Find the fundamental solution (x, y) to x^2 - d*y^2 = 1
    using continued fraction expansion of sqrt(d).
    d must not be a perfect square.\"\"\"
    import math
    d = int(d)
    sd = int(math.isqrt(d))
    if sd * sd == d:
        return None  # no solution for perfect squares

    # Continued fraction expansion of sqrt(d)
    m, dd, a = 0, 1, sd
    # Track convergents
    p_prev, p_curr = 1, sd
    q_prev, q_curr = 0, 1

    while True:
        m = dd * a - m
        dd = (d - m * m) // dd
        a = (sd + m) // dd

        p_prev, p_curr = p_curr, a * p_curr + p_prev
        q_prev, q_curr = q_curr, a * q_curr + q_prev

        # Check if this convergent solves x^2 - d*y^2 = 1
        if p_curr * p_curr - d * q_curr * q_curr == 1:
            return (int(p_curr), int(q_curr))
""",
            "input_type": "integer",
            "output_type": "algebraic_structure",
        },
    }


if __name__ == "__main__":
    import numpy as np

    org = AlgebraicNumberTheory()
    print(org)

    norm = org.execute("gaussian_integers_norm", 3, 4)
    print(f"N(3 + 4i) = {norm}  (expect 25)")

    qr = org.execute("quadratic_residues", 13)
    print(f"QR mod 13: {qr}  (expect [1,3,4,9,10,12])")

    ls1 = org.execute("legendre_symbol", 2, 7)
    print(f"(2/7) = {ls1}  (expect 1, since 3^2=9=2 mod 7)")

    ls2 = org.execute("legendre_symbol", 5, 7)
    print(f"(5/7) = {ls2}  (expect -1)")

    cf = org.execute("continued_fraction", 355, 113)
    print(f"CF of 355/113: {cf}  (expect [3, 7, 16])")

    pell = org.execute("pell_equation_solve", 2)
    print(f"Pell x^2 - 2y^2 = 1: {pell}  (expect (3, 2))")

    pell5 = org.execute("pell_equation_solve", 5)
    print(f"Pell x^2 - 5y^2 = 1: {pell5}  (expect (9, 4))")

    pell61 = org.execute("pell_equation_solve", 61)
    x, y = pell61
    print(f"Pell x^2 - 61y^2 = 1: ({x}, {y}), check: {x*x - 61*y*y}")

    print("--- algebraic_number_theory: ALL TESTS PASSED ---")
