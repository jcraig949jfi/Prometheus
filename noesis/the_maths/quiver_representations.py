"""
Quiver Representations -- Path algebras, dimension vectors, Gabriel's theorem

Connects to: [representation_theory, homological_algebra, cluster_algebras, algebraic_geometry]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "quiver_representations"
OPERATIONS = {}


def quiver_adjacency(x):
    """Build adjacency matrix for a quiver from edge list encoding.
    x[0] = number of vertices n, then pairs (source, target).
    If too short, returns a type-A quiver (chain).
    Input: array. Output: matrix(n, n)."""
    n = int(x[0]) if len(x) > 0 else 3
    n = max(1, min(n, 20))
    adj = np.zeros((n, n))
    if len(x) >= 3:
        edges = x[1:]
        num_edges = len(edges) // 2
        for k in range(num_edges):
            src = int(edges[2 * k]) - 1
            tgt = int(edges[2 * k + 1]) - 1
            if 0 <= src < n and 0 <= tgt < n:
                adj[src, tgt] += 1
    else:
        # Default: type A chain 1->2->...->n
        for i in range(n - 1):
            adj[i, i + 1] = 1
    return adj

OPERATIONS["quiver_adjacency"] = {
    "fn": quiver_adjacency,
    "input_type": "array",
    "output_type": "matrix",
    "description": "Adjacency matrix for a quiver (directed graph)"
}


def path_algebra_dimension(x):
    """Dimension of path algebra for an acyclic quiver.
    Equals the number of paths of all lengths (including length 0).
    x is flattened adjacency matrix.
    Input: array. Output: scalar."""
    n = int(np.sqrt(len(x)))
    if n < 1:
        return 1.0
    A = x[:n*n].reshape(n, n)
    # Number of paths = sum over k of entries of A^k, for k=0,1,...,n-1
    # (acyclic quiver has no paths longer than n-1)
    total = float(n)  # k=0: n identity paths (one per vertex)
    power = np.eye(n)
    for k in range(1, n):
        power = power @ A
        total += np.sum(power)
        if np.sum(np.abs(power)) < 1e-12:
            break
    return total

OPERATIONS["path_algebra_dimension"] = {
    "fn": path_algebra_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Dimension of path algebra (number of all paths in acyclic quiver)"
}


def dimension_vector_euler_form(x):
    """Euler form <d, e> for two dimension vectors d, e of a quiver.
    Euler form: <d,e> = sum_i d_i*e_i - sum_{arrows i->j} d_i*e_j.
    x = [n, d_1..d_n, e_1..e_n, adj flattened].
    Simplified: if short, treat x as [d; e] with A_n quiver.
    Input: array. Output: scalar."""
    n = len(x) // 2
    if n < 1:
        return 0.0
    d = x[:n]
    e = x[n:2*n]
    # Default: A_n quiver (chain 1->2->...->n)
    result = np.dot(d, e)  # vertex contribution
    for i in range(n - 1):
        result -= d[i] * e[i + 1]  # arrow i -> i+1
    return float(result)

OPERATIONS["dimension_vector_euler_form"] = {
    "fn": dimension_vector_euler_form,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Euler form of two dimension vectors for a quiver"
}


def gabriel_type_classify(x):
    """Classify quiver as finite, tame, or wild type using Gabriel's theorem.
    Finite type iff underlying graph is Dynkin (A, D, E).
    x = flattened adjacency matrix.
    Returns: 1.0 (finite), 2.0 (tame/affine), 3.0 (wild).
    Input: array. Output: scalar."""
    n = int(np.sqrt(len(x)))
    if n < 1:
        return 1.0
    A = x[:n*n].reshape(n, n)
    # Underlying undirected graph: symmetric part
    G = A + A.T
    G = (G > 0).astype(float)
    np.fill_diagonal(G, 0)
    # Check number of edges
    num_edges = int(np.sum(G) / 2)
    # Finite type: underlying graph is ADE Dynkin
    # Necessary: num_edges = n-1 (tree) and max degree conditions
    if num_edges < n - 1:
        # Forest: always finite type
        return 1.0
    if num_edges == n - 1:
        # Tree: check if Dynkin (A, D, E)
        degrees = np.sum(G, axis=1)
        max_deg = np.max(degrees)
        branch_points = np.sum(degrees >= 3)
        if max_deg <= 2:
            return 1.0  # Type A
        if branch_points == 1 and max_deg == 3:
            # Could be D or E type
            if n <= 8:  # E6, E7, E8 or D_n
                return 1.0
            else:
                return 1.0  # D_n for any n
        return 3.0  # wild
    if num_edges == n:
        return 2.0  # tame (affine type)
    return 3.0  # wild

OPERATIONS["gabriel_type_classify"] = {
    "fn": gabriel_type_classify,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Gabriel classification: 1=finite, 2=tame, 3=wild"
}


def indecomposable_count_finite(x):
    """Number of indecomposable representations for finite type quiver.
    By Gabriel's theorem, equals number of positive roots.
    A_n: n(n+1)/2, D_n: n(n-1), E6=36, E7=63, E8=120.
    x[0] = type (1=A, 4=D, 5=E), x[1] = rank n.
    Input: array. Output: scalar."""
    typ = int(x[0]) if len(x) > 0 else 1
    n = int(x[1]) if len(x) > 1 else 3
    n = max(1, n)
    if typ == 1:  # A_n
        return float(n * (n + 1) // 2)
    elif typ == 4:  # D_n
        return float(n * (n - 1))
    elif typ == 5:  # E_n
        counts = {6: 36, 7: 63, 8: 120}
        return float(counts.get(n, 0))
    return 0.0

OPERATIONS["indecomposable_count_finite"] = {
    "fn": indecomposable_count_finite,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Number of indecomposables by Gabriel's theorem"
}


def quiver_mutation(x):
    """Fomin-Zelevinsky quiver mutation at vertex k.
    x[0] = k (1-based), rest = flattened adjacency matrix.
    Input: array. Output: array (flattened mutated adjacency)."""
    k_idx = int(x[0]) - 1 if len(x) > 0 else 0
    rest = x[1:]
    n = int(np.sqrt(len(rest)))
    if n < 1:
        return x
    B = rest[:n*n].reshape(n, n).copy()
    k = max(0, min(k_idx, n - 1))
    # Step 1: For each i->k->j, add arrow i->j (or cancel j->i)
    new_B = B.copy()
    for i in range(n):
        for j in range(n):
            if i == k or j == k:
                continue
            if B[i, k] > 0 and B[k, j] > 0:
                new_B[i, j] += B[i, k] * B[k, j]
            elif B[i, k] < 0 and B[k, j] < 0:
                new_B[i, j] += B[i, k] * B[k, j]
    # Step 2: Reverse all arrows incident to k
    for i in range(n):
        new_B[i, k], new_B[k, i] = -B[i, k], -B[k, i]
    # Step 3: Cancel 2-cycles (keep skew-symmetric part)
    for i in range(n):
        for j in range(i + 1, n):
            if new_B[i, j] > 0 and new_B[j, i] > 0:
                m = min(new_B[i, j], new_B[j, i])
                new_B[i, j] -= m
                new_B[j, i] -= m
    return new_B.flatten()

OPERATIONS["quiver_mutation"] = {
    "fn": quiver_mutation,
    "input_type": "array",
    "output_type": "array",
    "description": "Fomin-Zelevinsky quiver mutation at vertex k"
}


def ext_dimension(x):
    """Compute dim Ext^1(M, N) using the Euler form.
    For hereditary algebras: dim Ext^1 = -<d_M, d_N> + dim Hom(M,N).
    Approximation: max(0, -euler_form).
    Input: array (two dimension vectors). Output: scalar."""
    n = len(x) // 2
    if n < 1:
        return 0.0
    d = x[:n]
    e = x[n:2*n]
    euler = np.dot(d, e)
    for i in range(n - 1):
        euler -= d[i] * e[i + 1]
    # For indecomposables: dim Hom >= max(0, euler), dim Ext^1 >= max(0, -euler)
    return float(max(0, -euler))

OPERATIONS["ext_dimension"] = {
    "fn": ext_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Dimension of Ext^1 from Euler form (hereditary algebra)"
}


def auslander_reiten_translate(x):
    """Auslander-Reiten translation tau(d) for a dimension vector d on A_n quiver.
    tau shifts the dimension vector: tau(d)_i = d_{i+1} for type A_n linear orientation,
    with boundary adjustment. Simplified version.
    Input: array (dimension vector). Output: array."""
    d = x.copy()
    n = len(d)
    if n < 2:
        return np.zeros_like(d)
    # For type A_n with linear orientation:
    # The AR translate can be computed via the Coxeter transformation
    # C = -Phi where Phi is the Coxeter matrix
    # Simplified: use the formula tau(d) = max(0, Phi^{-1}(d)) component-wise
    # where Phi = product of reflections
    # For A_n: shift right and subtract
    result = np.zeros(n)
    for i in range(n):
        val = -d[i]
        if i > 0:
            val += d[i - 1]
        if i < n - 1:
            val += d[i + 1]
        result[i] = max(0, val)
    return result

OPERATIONS["auslander_reiten_translate"] = {
    "fn": auslander_reiten_translate,
    "input_type": "array",
    "output_type": "array",
    "description": "Auslander-Reiten translation of dimension vector (A_n quiver)"
}


def quiver_variety_dimension(x):
    """Dimension of Nakajima quiver variety M(v, w) for A_n.
    dim = 2 * sum_i v_i*w_i - sum_{edges i-j} v_i*v_j + sum_i v_i^2
    which simplifies to 2*<v,w> - <v,v> in Euler form terms.
    x = [v_1..v_n, w_1..w_n].
    Input: array. Output: scalar."""
    n = len(x) // 2
    if n < 1:
        return 0.0
    v = x[:n]
    w = x[n:2*n]
    # dim M(v,w) = 2 * sum v_i * w_i - (2*sum v_i^2 - 2*sum_{i~j} v_i*v_j)
    # = 2*v.w - v^T * C * v where C is Cartan matrix of A_n
    vw = 2 * np.dot(v, w)
    vCv = 2 * np.dot(v, v)
    for i in range(n - 1):
        vCv -= 2 * v[i] * v[i + 1]
    dim = vw - vCv
    return float(max(0, dim))

OPERATIONS["quiver_variety_dimension"] = {
    "fn": quiver_variety_dimension,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Dimension of Nakajima quiver variety M(v, w)"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
