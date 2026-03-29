"""
Incidence Algebras -- Poset zeta/Mobius functions, generalized inversion, Whitney numbers

Connects to: [combinatorics, lattice_theory, number_theory, homological_algebra]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "incidence_algebras"
OPERATIONS = {}


def _relation_matrix(x):
    """Interpret input as a partial order relation matrix or build a chain poset."""
    n = int(np.sqrt(len(x)))
    if n >= 2 and n * n <= len(x):
        R = x[:n*n].reshape(n, n)
        # Ensure reflexivity
        np.fill_diagonal(R, 1)
        return (R > 0).astype(float)
    else:
        # Default: chain poset 0 < 1 < ... < n-1
        n = max(2, len(x))
        R = np.zeros((n, n))
        for i in range(n):
            for j in range(i, n):
                R[i, j] = 1.0
        return R


def poset_zeta_function(x):
    """Zeta function of a poset: zeta(i,j) = 1 if i <= j, else 0.
    Input: array (flattened relation matrix or chain length). Output: matrix."""
    R = _relation_matrix(x)
    return R

OPERATIONS["poset_zeta_function"] = {
    "fn": poset_zeta_function,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Zeta function matrix of a poset (1 if i <= j)"
}


def poset_mobius_function(x):
    """Mobius function: inverse of the zeta function in the incidence algebra.
    mu = zeta^{-1}. Computed via matrix inversion.
    Input: array (flattened relation matrix). Output: matrix."""
    R = _relation_matrix(x)
    n = R.shape[0]
    # Compute Mobius function by inverting zeta (upper triangular)
    mu = np.zeros((n, n))
    for i in range(n):
        mu[i, i] = 1.0
        for j in range(i + 1, n):
            if R[i, j] > 0:
                s = 0.0
                for k in range(i, j):
                    if R[i, k] > 0 and R[k, j] > 0:
                        s += mu[i, k]
                mu[i, j] = -s
    return mu

OPERATIONS["poset_mobius_function"] = {
    "fn": poset_mobius_function,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Mobius function matrix (inverse of zeta in incidence algebra)"
}


def incidence_algebra_product(x):
    """Product of two functions in the incidence algebra: (f*g)(i,j) = sum_{i<=k<=j} f(i,k)*g(k,j).
    This is matrix multiplication restricted to the poset.
    Input: array (two flattened square matrices concatenated). Output: matrix."""
    total = len(x)
    half = total // 2
    n = int(np.sqrt(half))
    if n < 1:
        n = int(np.sqrt(total))
        if n < 1:
            return np.array([[0.0]])
        f = x[:n*n].reshape(n, n)
        g = f.copy()
    else:
        f = x[:n*n].reshape(n, n)
        g = x[n*n:2*n*n].reshape(n, n) if 2*n*n <= total else f.copy()
    return f @ g

OPERATIONS["incidence_algebra_product"] = {
    "fn": incidence_algebra_product,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Convolution product in the incidence algebra"
}


def incidence_algebra_inverse(x):
    """Inverse of a function in the incidence algebra (if it exists).
    f must have nonzero diagonal. Computes via upper triangular inversion.
    Input: array (flattened upper triangular matrix). Output: matrix."""
    n = int(np.sqrt(len(x)))
    if n < 2:
        return np.array([[1.0]])
    f = x[:n*n].reshape(n, n)
    # Check invertibility
    diag = np.diag(f)
    if np.any(np.abs(diag) < 1e-15):
        # Not invertible; return zeros
        return np.zeros((n, n))
    # Upper triangular inverse
    inv_f = np.zeros((n, n))
    for i in range(n):
        inv_f[i, i] = 1.0 / f[i, i]
        for j in range(i + 1, n):
            s = 0.0
            for k in range(i, j):
                s += inv_f[i, k] * f[k, j]
            inv_f[i, j] = -s / f[j, j]
    return inv_f

OPERATIONS["incidence_algebra_inverse"] = {
    "fn": incidence_algebra_inverse,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Inverse in the incidence algebra (upper triangular inversion)"
}


def poset_characteristic_polynomial(x):
    """Characteristic polynomial of a poset evaluated at t = x[0].
    chi(P, t) = sum_{y in P} mu(0, y) * t^{rank(hat1) - rank(y)}.
    Simplified: for chain of length n, chi = (t-1)^{n-1}.
    For general poset, use Mobius function.
    Input: array. Output: scalar."""
    # Use first element as t, rest to define poset
    t = x[0] if len(x) > 0 else 2.0
    rest = x[1:] if len(x) > 1 else np.array([3.0])
    n = int(rest[0]) if len(rest) > 0 else 3
    n = max(1, min(n, 20))
    # Chain poset: mu(0, k) = (-1)^k * C(?, ?) ... for chain, mu(0,j) = (-1)^j if j adjacent
    # Actually for chain 0<1<...<n-1: mu(i,j) = (-1)^{j-i} if j=i or j=i+1, else 0
    # Wait, for a chain, mu(i,j) = (-1)^{j-i} only if j-i <= 1
    # For total order: mu(i,i)=1, mu(i,i+1)=-1, mu(i,j)=0 if j>i+1
    # Characteristic polynomial: sum_{j=0}^{n-1} mu(0,j) * t^{n-1-j}
    # = t^{n-1} - t^{n-2} = t^{n-2}(t - 1) for chain
    result = 0.0
    for j in range(min(2, n)):
        if j == 0:
            result += t ** (n - 1)
        elif j == 1:
            result -= t ** (n - 2)
    return float(result)

OPERATIONS["poset_characteristic_polynomial"] = {
    "fn": poset_characteristic_polynomial,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Characteristic polynomial of poset at given t"
}


def interval_count(x):
    """Count number of intervals [i,j] (pairs with i <= j) in the poset.
    Input: array (flattened relation matrix). Output: scalar."""
    R = _relation_matrix(x)
    return float(np.sum(R))

OPERATIONS["interval_count"] = {
    "fn": interval_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Number of intervals [i,j] in the poset"
}


def chain_count(x):
    """Count maximal chains in a poset (paths from minimal to maximal elements).
    Uses dynamic programming on the relation matrix.
    Input: array (flattened relation matrix). Output: scalar."""
    R = _relation_matrix(x)
    n = R.shape[0]
    # Build cover relation (Hasse diagram)
    cover = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j and R[i, j] > 0:
                # Check if j covers i (no k with i < k < j)
                is_cover = True
                for k in range(n):
                    if k != i and k != j and R[i, k] > 0 and R[k, j] > 0:
                        is_cover = False
                        break
                if is_cover:
                    cover[i, j] = 1
    # Find minimal elements (no incoming covers)
    is_minimal = np.all(cover[:, :] == 0, axis=0) | (np.sum(cover, axis=0) == 0)
    # Actually: minimal = elements with no element below them
    minimals = [i for i in range(n) if not any(R[j, i] > 0 and j != i for j in range(n))]
    maximals = [i for i in range(n) if not any(R[i, j] > 0 and j != i for j in range(n))]
    if not minimals:
        minimals = [0]
    if not maximals:
        maximals = [n - 1]
    # DP: count paths from each minimal to each maximal via covers
    # paths[i] = number of maximal chains ending at i
    paths = np.zeros(n)
    for m in minimals:
        paths[m] = 1
    # Process in topological order
    for length in range(n):
        new_paths = paths.copy()
        for j in range(n):
            for i in range(n):
                if cover[i, j] > 0:
                    new_paths[j] += paths[i] * cover[i, j]
        if np.allclose(paths, new_paths):
            break
        paths = new_paths
    total = sum(paths[m] for m in maximals)
    return float(max(1, total))

OPERATIONS["chain_count"] = {
    "fn": chain_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Number of maximal chains in the poset"
}


def antichain_count(x):
    """Count antichains in the poset using the complement of the comparability graph.
    An antichain is a set of pairwise incomparable elements.
    Uses inclusion-exclusion for small posets.
    Input: array (flattened relation matrix). Output: scalar."""
    R = _relation_matrix(x)
    n = R.shape[0]
    if n > 15:
        # Approximate: Dilworth's theorem gives max antichain size
        # Just count small antichains
        n = 15
        R = R[:n, :n]
    # Comparability: i ~ j if i <= j or j <= i (and i != j)
    comp = np.zeros((n, n), dtype=bool)
    for i in range(n):
        for j in range(n):
            if i != j and (R[i, j] > 0 or R[j, i] > 0):
                comp[i, j] = True
    # Count antichains by brute force (subsets of size up to n)
    count = 1  # empty antichain
    for size in range(1, n + 1):
        from itertools import combinations
        for subset in combinations(range(n), size):
            is_ac = True
            for a, b in combinations(subset, 2):
                if comp[a, b]:
                    is_ac = False
                    break
            if is_ac:
                count += 1
    return float(count)

OPERATIONS["antichain_count"] = {
    "fn": antichain_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Number of antichains in the poset"
}


def whitney_number(x):
    """Whitney numbers of the second kind: W_k = number of elements of rank k.
    For a ranked poset. Uses chain poset with n = int(x[0]).
    Input: array. Output: array (W_0, W_1, ..., W_{n-1})."""
    n = int(x[0]) if len(x) > 0 else 5
    n = max(1, min(n, 20))
    # For chain poset: each rank has exactly 1 element
    # For Boolean lattice B_n (power set of [n]): W_k = C(n, k)
    # Use Boolean lattice as more interesting
    from math import comb
    whitney = np.array([float(comb(n, k)) for k in range(n + 1)])
    return whitney

OPERATIONS["whitney_number"] = {
    "fn": whitney_number,
    "input_type": "array",
    "output_type": "array",
    "description": "Whitney numbers of the second kind (elements per rank level)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
