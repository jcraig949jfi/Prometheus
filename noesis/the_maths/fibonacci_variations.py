"""
Fibonacci Variations — Lucas, tribonacci, Fibonacci words, Zeckendorf representation

Connects to: [number_theory, recurrence_relations, golden_ratio]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "fibonacci_variations"
OPERATIONS = {}


def fibonacci_sequence(x):
    """Generate first n Fibonacci numbers. n=int(x[0]). Input: array. Output: array."""
    n = int(abs(x[0]))
    n = min(max(n, 1), 1000)
    fibs = np.zeros(n, dtype=np.float64)
    if n >= 1:
        fibs[0] = 0
    if n >= 2:
        fibs[1] = 1
    for i in range(2, n):
        fibs[i] = fibs[i - 1] + fibs[i - 2]
    return fibs


OPERATIONS["fibonacci_sequence"] = {
    "fn": fibonacci_sequence,
    "input_type": "array",
    "output_type": "array",
    "description": "First n Fibonacci numbers starting from F(0)=0"
}


def lucas_sequence(x):
    """Generate first n Lucas numbers. n=int(x[0]). Input: array. Output: array."""
    n = int(abs(x[0]))
    n = min(max(n, 1), 1000)
    luc = np.zeros(n, dtype=np.float64)
    if n >= 1:
        luc[0] = 2
    if n >= 2:
        luc[1] = 1
    for i in range(2, n):
        luc[i] = luc[i - 1] + luc[i - 2]
    return luc


OPERATIONS["lucas_sequence"] = {
    "fn": lucas_sequence,
    "input_type": "array",
    "output_type": "array",
    "description": "First n Lucas numbers starting from L(0)=2"
}


def tribonacci_sequence(x):
    """Generate first n tribonacci numbers. n=int(x[0]). Input: array. Output: array."""
    n = int(abs(x[0]))
    n = min(max(n, 1), 500)
    tri = np.zeros(n, dtype=np.float64)
    if n >= 3:
        tri[2] = 1
    for i in range(3, n):
        tri[i] = tri[i - 1] + tri[i - 2] + tri[i - 3]
    return tri


OPERATIONS["tribonacci_sequence"] = {
    "fn": tribonacci_sequence,
    "input_type": "array",
    "output_type": "array",
    "description": "First n tribonacci numbers (0,0,1,1,2,4,7,...)"
}


def fibonacci_word_density(x):
    """Density of 0s in first n characters of Fibonacci word. n=int(x[0]). Input: array. Output: scalar."""
    n = int(abs(x[0]))
    n = min(max(n, 1), 100000)
    # Fibonacci word: start with "0", apply 0->01, 1->0
    # Build iteratively
    a, b = "0", "01"
    while len(a) < n:
        a, b = b, b + a
    word = a[:n]
    count_0 = word.count('0')
    return float(count_0 / n)


OPERATIONS["fibonacci_word_density"] = {
    "fn": fibonacci_word_density,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Density of 0s in Fibonacci word (approaches 1/phi)"
}


def zeckendorf_representation(x):
    """Zeckendorf representation of n as sum of non-consecutive Fibonacci numbers. Input: array. Output: array."""
    n = int(abs(x[0]))
    if n == 0:
        return np.array([0])
    # Generate Fibonacci numbers up to n
    fibs = [1, 2]
    while fibs[-1] < n:
        fibs.append(fibs[-1] + fibs[-2])
    # Greedy algorithm
    components = []
    remaining = n
    for f in reversed(fibs):
        if f <= remaining:
            components.append(f)
            remaining -= f
            if remaining == 0:
                break
    return np.array(sorted(components), dtype=np.int64)


OPERATIONS["zeckendorf_representation"] = {
    "fn": zeckendorf_representation,
    "input_type": "array",
    "output_type": "array",
    "description": "Zeckendorf representation as non-consecutive Fibonacci numbers"
}


def pisano_period(x):
    """Compute Pisano period pi(m) = period of Fibonacci mod m. m=int(x[0]). Input: array. Output: integer."""
    m = int(abs(x[0]))
    if m <= 1:
        return 1
    # Fibonacci mod m is periodic; find the period
    prev, curr = 0, 1
    for i in range(1, 6 * m + 1):  # pi(m) <= 6m
        prev, curr = curr, (prev + curr) % m
        if prev == 0 and curr == 1:
            return int(i)
    return int(6 * m)  # fallback upper bound


OPERATIONS["pisano_period"] = {
    "fn": pisano_period,
    "input_type": "array",
    "output_type": "integer",
    "description": "Pisano period (period of Fibonacci sequence mod m)"
}


def fibonacci_golden_ratio_approx(x):
    """Compute F(n+1)/F(n) ratios approaching golden ratio. n=int(x[0]). Input: array. Output: array."""
    n = int(abs(x[0]))
    n = min(max(n, 2), 80)
    ratios = np.zeros(n - 1, dtype=np.float64)
    a, b = 1.0, 1.0
    for i in range(n - 1):
        a, b = b, a + b
        ratios[i] = b / a
    return ratios


OPERATIONS["fibonacci_golden_ratio_approx"] = {
    "fn": fibonacci_golden_ratio_approx,
    "input_type": "array",
    "output_type": "array",
    "description": "Successive F(n+1)/F(n) ratios converging to golden ratio"
}


def binet_formula(x):
    """Compute F(n) via Binet's formula. Input: array. Output: array."""
    n = np.asarray(np.abs(x), dtype=np.float64)
    phi = (1 + np.sqrt(5)) / 2
    psi = (1 - np.sqrt(5)) / 2
    result = (phi ** n - psi ** n) / np.sqrt(5)
    return np.round(result)


OPERATIONS["binet_formula"] = {
    "fn": binet_formula,
    "input_type": "array",
    "output_type": "array",
    "description": "Fibonacci F(n) via Binet's closed form"
}


def fibonacci_divisibility_order(x):
    """Find smallest k such that F(k) is divisible by n. n=int(x[0]). Input: array. Output: integer."""
    n = int(abs(x[0]))
    if n <= 1:
        return int(n)
    # alpha(n) = rank of apparition / entry point
    a, b = 0, 1
    for k in range(1, 10000):
        a, b = b, (a + b)
        if a % n == 0:
            return int(k)
    return -1  # not found within limit


OPERATIONS["fibonacci_divisibility_order"] = {
    "fn": fibonacci_divisibility_order,
    "input_type": "array",
    "output_type": "integer",
    "description": "Rank of apparition: smallest k with n | F(k)"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
