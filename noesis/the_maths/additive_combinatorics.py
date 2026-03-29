"""
Additive Combinatorics — sumset bounds, Freiman's theorem, Roth's theorem

Connects to: [number_theory, combinatorics, harmonic_analysis, ergodic_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "additive_combinatorics"
OPERATIONS = {}


def sumset_size(x):
    """Size of the sumset A + A = {a + b : a, b in A}.
    Input: array A (treated as a set of integers). Output: integer.
    """
    A = np.unique(np.round(x)).astype(int)
    sumset = set()
    for a in A:
        for b in A:
            sumset.add(a + b)
    return np.int64(len(sumset))


OPERATIONS["sumset_size"] = {
    "fn": sumset_size,
    "input_type": "array",
    "output_type": "integer",
    "description": "Size of the sumset A+A"
}


def doubling_constant(x):
    """Doubling constant sigma(A) = |A+A| / |A|.
    Input: array A. Output: scalar.
    Small doubling constant indicates additive structure.
    """
    A = np.unique(np.round(x)).astype(int)
    n = len(A)
    if n == 0:
        return np.float64(0.0)
    sumset = set()
    for a in A:
        for b in A:
            sumset.add(a + b)
    return np.float64(len(sumset) / n)


OPERATIONS["doubling_constant"] = {
    "fn": doubling_constant,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Doubling constant |A+A|/|A| measuring additive structure"
}


def ruzsa_distance(x):
    """Ruzsa distance d(A, B) = log(|A - B|) - log(|A|)/2 - log(|B|)/2.
    Input: array of length 2n, first half A, second half B. Output: scalar.
    """
    n = len(x) // 2
    if n < 1:
        return np.float64(0.0)
    A = np.unique(np.round(x[:n])).astype(int)
    B = np.unique(np.round(x[n:2*n])).astype(int)
    if len(A) == 0 or len(B) == 0:
        return np.float64(0.0)
    # A - B = {a - b : a in A, b in B}
    diff_set = set()
    for a in A:
        for b in B:
            diff_set.add(a - b)
    d = np.log(len(diff_set)) - np.log(len(A)) / 2.0 - np.log(len(B)) / 2.0
    return np.float64(d)


OPERATIONS["ruzsa_distance"] = {
    "fn": ruzsa_distance,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Ruzsa distance between two sets A and B"
}


def plunnecke_ruzsa_bound(x):
    """Plunnecke-Ruzsa inequality: if |A+A| <= K|A|, then |nA - mA| <= K^{n+m}|A|.
    Input: array [K, n, m, |A|]. Output: scalar (upper bound on |nA - mA|).
    """
    if len(x) < 4:
        return np.float64(0.0)
    K = max(x[0], 1.0)
    n_val = max(int(round(x[1])), 0)
    m_val = max(int(round(x[2])), 0)
    size_A = max(x[3], 1.0)
    bound = K**(n_val + m_val) * size_A
    return np.float64(bound)


OPERATIONS["plunnecke_ruzsa_bound"] = {
    "fn": plunnecke_ruzsa_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Plunnecke-Ruzsa upper bound on |nA - mA| given doubling constant K"
}


def arithmetic_progression_count(x):
    """Count 3-term arithmetic progressions in a set A.
    A 3-AP is a triple (a, a+d, a+2d) with d > 0, all in A.
    Input: array A. Output: integer.
    """
    A = set(np.unique(np.round(x)).astype(int).tolist())
    count = 0
    A_sorted = sorted(A)
    for i, a in enumerate(A_sorted):
        for j in range(i + 1, len(A_sorted)):
            b = A_sorted[j]
            d = b - a
            c = b + d
            if c in A:
                count += 1
    return np.int64(count)


OPERATIONS["arithmetic_progression_count"] = {
    "fn": arithmetic_progression_count,
    "input_type": "array",
    "output_type": "integer",
    "description": "Count of 3-term arithmetic progressions in set A"
}


def roth_density_bound(x):
    """Roth's theorem bound: maximum density of a 3-AP-free subset of {1,...,N}.
    delta(N) <= C / log(log(N)) (Roth's original bound).
    Better bounds exist but this is the classic one.
    Input: array [N]. Output: scalar (density bound).
    """
    N = max(int(round(np.abs(x[0]))), 3)
    # Roth's bound: roughly C / log(log(N))
    # Use the Bloom-Sisask improvement-style constant for reasonable values
    llN = np.log(np.log(N + 2) + 1) + 1
    density = 1.0 / llN
    return np.float64(min(density, 1.0))


OPERATIONS["roth_density_bound"] = {
    "fn": roth_density_bound,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Roth's theorem density bound for 3-AP-free subsets of {1,...,N}"
}


def freiman_dimension_bound(x):
    """Freiman dimension: if |A+A| <= K|A|, then A is contained in a
    generalized arithmetic progression of dimension d <= K - 1 (roughly).
    Input: array A. Output: integer (estimated Freiman dimension).
    """
    A = np.unique(np.round(x)).astype(int)
    n = len(A)
    if n <= 1:
        return np.int64(0)
    sumset = set()
    for a in A:
        for b in A:
            sumset.add(a + b)
    K = len(sumset) / n
    # Freiman's theorem: d <= floor(K - 1) roughly, but more precisely
    # A lies in a GAP of dimension d <= C * K for some constant
    # For 1D integer sets: if K < 2, d=1 (it's essentially an AP)
    if K < 2.0:
        return np.int64(1)
    d = int(np.ceil(K - 1))
    return np.int64(max(d, 1))


OPERATIONS["freiman_dimension_bound"] = {
    "fn": freiman_dimension_bound,
    "input_type": "array",
    "output_type": "integer",
    "description": "Estimated Freiman dimension from the doubling constant"
}


def additive_energy(x):
    """Additive energy E(A) = |{(a,b,c,d) in A^4 : a+b = c+d}|.
    Input: array A. Output: integer.
    Computed as sum of squares of representation counts r_{A+A}(s)^2.
    """
    A = np.unique(np.round(x)).astype(int)
    # Count representations: for each sum s = a+b, count how many pairs give s
    from collections import Counter
    rep_counts = Counter()
    for a in A:
        for b in A:
            rep_counts[a + b] += 1
    energy = sum(c**2 for c in rep_counts.values())
    return np.int64(energy)


OPERATIONS["additive_energy"] = {
    "fn": additive_energy,
    "input_type": "array",
    "output_type": "integer",
    "description": "Additive energy E(A) = |{(a,b,c,d): a+b=c+d}|"
}


def sum_product_estimate(x):
    """Sum-product estimate: max(|A+A|, |A*A|) >= |A|^{1+epsilon}.
    Computes both |A+A| and |A*A| and returns them.
    Input: array A. Output: array [|A+A|, |A*A|, |A|].
    """
    A = np.unique(np.round(x)).astype(int)
    n = len(A)
    sumset = set()
    prodset = set()
    for a in A:
        for b in A:
            sumset.add(a + b)
            prodset.add(a * b)
    return np.array([len(sumset), len(prodset), n], dtype=float)


OPERATIONS["sum_product_estimate"] = {
    "fn": sum_product_estimate,
    "input_type": "array",
    "output_type": "array",
    "description": "Sum-product sizes [|A+A|, |A*A|, |A|] for the Erdos-Szemeredi conjecture"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
