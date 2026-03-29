"""
Coxeter Groups -- Reflection groups, Cartan matrices, Dynkin diagrams, Weyl actions

Connects to: [lie_algebras, root_systems, representation_theory, lattices]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np
from itertools import combinations

FIELD_NAME = "coxeter_groups"
OPERATIONS = {}


def cartan_matrix_An(x):
    """Cartan matrix for type A_n. n = int(x[0]) or len(x).
    Input: array. Output: matrix(n, n)."""
    n = int(x[0]) if len(x) > 0 else 3
    n = max(1, min(n, 20))
    C = 2 * np.eye(n)
    for i in range(n - 1):
        C[i, i + 1] = -1
        C[i + 1, i] = -1
    return C

OPERATIONS["cartan_matrix_An"] = {
    "fn": cartan_matrix_An,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Cartan matrix for Lie algebra of type A_n"
}


def cartan_matrix_Bn(x):
    """Cartan matrix for type B_n. n = int(x[0]).
    Input: array. Output: matrix(n, n)."""
    n = int(x[0]) if len(x) > 0 else 3
    n = max(2, min(n, 20))
    C = 2 * np.eye(n)
    for i in range(n - 2):
        C[i, i + 1] = -1
        C[i + 1, i] = -1
    # B_n: last connection is asymmetric
    C[n - 2, n - 1] = -2
    C[n - 1, n - 2] = -1
    return C

OPERATIONS["cartan_matrix_Bn"] = {
    "fn": cartan_matrix_Bn,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Cartan matrix for Lie algebra of type B_n"
}


def cartan_matrix_Dn(x):
    """Cartan matrix for type D_n. n = int(x[0]).
    Input: array. Output: matrix(n, n)."""
    n = int(x[0]) if len(x) > 0 else 4
    n = max(3, min(n, 20))
    C = 2 * np.eye(n)
    for i in range(n - 2):
        C[i, i + 1] = -1
        C[i + 1, i] = -1
    # D_n: fork at the end -- node n-1 connects to n-3 instead of n-2
    # Standard: nodes 0..n-3 form a chain, node n-1 branches from node n-3
    C[n - 2, n - 1] = 0  # undo the chain connection
    C[n - 1, n - 2] = 0
    C[n - 3, n - 1] = -1
    C[n - 1, n - 3] = -1
    return C

OPERATIONS["cartan_matrix_Dn"] = {
    "fn": cartan_matrix_Dn,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Cartan matrix for Lie algebra of type D_n"
}


def coxeter_matrix_from_cartan(x):
    """Compute Coxeter matrix m_{ij} from Cartan matrix entries.
    m_{ij} is the order of s_i s_j. Uses: a_{ij}*a_{ji} determines m.
    Input: array (flattened square Cartan matrix). Output: matrix."""
    n = int(np.sqrt(len(x)))
    if n * n > len(x):
        n = max(1, n)
    C = x[:n*n].reshape(n, n)
    M = np.ones((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                M[i, j] = 1
            else:
                prod = C[i, j] * C[j, i]
                # Standard: prod=0->m=2, prod=1->m=3, prod=2->m=4, prod=3->m=6
                if prod <= 0:
                    M[i, j] = 2
                elif prod < 1.5:
                    M[i, j] = 3
                elif prod < 2.5:
                    M[i, j] = 4
                elif prod < 3.5:
                    M[i, j] = 6
                else:
                    M[i, j] = 0  # infinity
    return M

OPERATIONS["coxeter_matrix_from_cartan"] = {
    "fn": coxeter_matrix_from_cartan,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Coxeter matrix from Cartan matrix (order of pairwise products)"
}


def simple_reflection(x):
    """Simple reflection s_i acting on a weight vector.
    x[0] = index i (1-based), rest = weight vector in omega basis.
    Uses A_n Cartan matrix. s_i(lambda) = lambda - <lambda, alpha_i^v> alpha_i.
    Input: array. Output: array."""
    i = int(x[0]) - 1 if len(x) > 0 else 0
    lam = x[1:] if len(x) > 1 else np.array([1.0, 0.0, 0.0])
    n = len(lam)
    i = max(0, min(i, n - 1))
    C = cartan_matrix_An(np.array([float(n)]))
    # s_i(lambda) = lambda - (C[i,:] . lambda) * e_i
    inner = np.dot(C[i, :], lam)
    result = lam.copy()
    result[i] -= inner
    return result

OPERATIONS["simple_reflection"] = {
    "fn": simple_reflection,
    "input_type": "array",
    "output_type": "array",
    "description": "Simple reflection s_i on a weight vector (A_n root system)"
}


def weyl_group_orbit(x):
    """Compute the Weyl group orbit of a weight for A_n.
    Returns orbit as flattened array (unique weights found by BFS, limited).
    Input: array (weight vector). Output: array (flattened orbit)."""
    lam = x.copy()
    n = len(lam)
    C = cartan_matrix_An(np.array([float(n)]))
    orbit = set()
    queue = [tuple(lam)]
    orbit.add(tuple(np.round(lam, 8)))
    max_size = 120  # cap for performance
    while queue and len(orbit) < max_size:
        w = np.array(queue.pop(0))
        for i in range(n):
            inner = np.dot(C[i, :], w)
            new_w = w.copy()
            new_w[i] -= inner
            key = tuple(np.round(new_w, 8))
            if key not in orbit:
                orbit.add(key)
                queue.append(key)
    result = np.array(sorted(orbit))
    return result.flatten()

OPERATIONS["weyl_group_orbit"] = {
    "fn": weyl_group_orbit,
    "input_type": "array",
    "output_type": "array",
    "description": "Weyl group orbit of a weight vector under A_n reflections"
}


def root_system_positive_roots(x):
    """Positive roots of A_n root system. n = int(x[0]).
    Returns flattened array of n(n+1)/2 positive roots.
    Input: array. Output: array."""
    n = int(x[0]) if len(x) > 0 else 3
    n = max(1, min(n, 15))
    # Positive roots of A_n: e_i - e_j for 1<=i<j<=n+1
    # In simple root basis: alpha_{i} + alpha_{i+1} + ... + alpha_{j-1}
    roots = []
    for i in range(n):
        for j in range(i, n):
            root = np.zeros(n)
            for k in range(i, j + 1):
                root[k] = 1.0
            roots.append(root)
    return np.array(roots).flatten()

OPERATIONS["root_system_positive_roots"] = {
    "fn": root_system_positive_roots,
    "input_type": "array",
    "output_type": "array",
    "description": "Positive roots of A_n in simple root coordinates"
}


def dynkin_diagram_type(x):
    """Classify a Cartan matrix by its Dynkin diagram type.
    Returns encoded type: A=1, B=2, C=3, D=4, E=5, F=6, G=7, unknown=0.
    Plus rank as second element.
    Input: array (flattened Cartan matrix). Output: array(2)."""
    n = int(np.sqrt(len(x)))
    if n < 1:
        return np.array([0.0, 0.0])
    C = x[:n*n].reshape(n, n)
    # Check if it's A_n: tridiagonal, all off-diag = -1
    is_An = True
    for i in range(n):
        for j in range(n):
            if i == j and abs(C[i, j] - 2) > 0.01:
                is_An = False
            elif abs(i - j) == 1 and abs(C[i, j] + 1) > 0.01:
                is_An = False
            elif abs(i - j) > 1 and abs(C[i, j]) > 0.01:
                is_An = False
    if is_An:
        return np.array([1.0, float(n)])
    # Check B_n: like A_n but C[n-2,n-1]=-2, C[n-1,n-2]=-1
    if n >= 2:
        is_Bn = True
        for i in range(n):
            for j in range(n):
                expected = 0
                if i == j:
                    expected = 2
                elif abs(i - j) == 1:
                    if i == n-2 and j == n-1:
                        expected = -2
                    elif i == n-1 and j == n-2:
                        expected = -1
                    else:
                        expected = -1
                if abs(C[i, j] - expected) > 0.01:
                    is_Bn = False
                    break
            if not is_Bn:
                break
        if is_Bn:
            return np.array([2.0, float(n)])
    return np.array([0.0, float(n)])  # unknown type

OPERATIONS["dynkin_diagram_type"] = {
    "fn": dynkin_diagram_type,
    "input_type": "array",
    "output_type": "array",
    "description": "Classify Cartan matrix as Dynkin diagram type (A=1,B=2,C=3,D=4,...)"
}


def coxeter_number(x):
    """Coxeter number h for A_n: h = n+1. n = int(x[0]).
    Input: array. Output: scalar."""
    n = int(x[0]) if len(x) > 0 else 3
    n = max(1, n)
    # A_n: h = n+1
    return float(n + 1)

OPERATIONS["coxeter_number"] = {
    "fn": coxeter_number,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Coxeter number h for type A_n (h = n+1)"
}


def weyl_denominator_formula(x):
    """Weyl denominator product for A_n evaluated at a point.
    prod_{alpha>0} (1 - exp(-alpha . x)).
    Uses x as the vector in weight space.
    Input: array. Output: scalar."""
    n = len(x)
    if n < 1:
        return 1.0
    # Positive roots of A_n in standard basis: e_i - e_j for i<j
    # We work in the simple root basis; alpha = sum_{k=i}^{j-1} alpha_k
    product = 1.0
    for i in range(n):
        for j in range(i, n):
            # root = alpha_i + ... + alpha_j
            alpha_dot_x = np.sum(x[i:j+1])
            product *= (1.0 - np.exp(-alpha_dot_x))
    return float(product)

OPERATIONS["weyl_denominator_formula"] = {
    "fn": weyl_denominator_formula,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Weyl denominator product for A_n at given weight"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
