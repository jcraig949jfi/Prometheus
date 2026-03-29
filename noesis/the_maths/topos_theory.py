"""
Topos Theory — subobject classifiers, presheaves on finite categories (toy models)

Connects to: [category_theory, logic, sheaf_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "topos_theory"
OPERATIONS = {}


def subobject_classifier_truth_values(x):
    """Truth values in the subobject classifier for a presheaf topos on a poset.
    x=[n] where n is size of poset (linear order). Returns number of truth values = n+1.
    Input: array. Output: integer."""
    n = int(abs(x[0]))
    # For presheaves on a linear order 0 < 1 < ... < n-1,
    # the subobject classifier Omega has truth values = sieves on each object
    # For a total order of length n, Omega has n+1 global truth values
    # (the downward-closed sets: empty, {0}, {0,1}, ..., {0,...,n-1})
    return int(n + 1)


OPERATIONS["subobject_classifier_truth_values"] = {
    "fn": subobject_classifier_truth_values,
    "input_type": "array",
    "output_type": "integer",
    "description": "Number of truth values in Omega for presheaves on linear order"
}


def presheaf_on_poset(x):
    """Evaluate a presheaf F on a poset. x encodes: [n_objects, then F(0), F(1), ...].
    Returns dimension vector of presheaf. Input: array. Output: array."""
    n = int(abs(x[0]))
    n = min(max(n, 1), 50)
    # Assign set sizes from input or default
    dims = np.zeros(n, dtype=np.int64)
    for i in range(n):
        if i + 1 < len(x):
            dims[i] = max(1, int(abs(x[i + 1])))
        else:
            dims[i] = 1
    # For a presheaf on a linear order, restriction maps must be order-preserving
    # Ensure dimensions are non-increasing (for contravariant functor on total order)
    for i in range(1, n):
        if dims[i] > dims[i - 1]:
            dims[i] = dims[i - 1]
    return dims


OPERATIONS["presheaf_on_poset"] = {
    "fn": presheaf_on_poset,
    "input_type": "array",
    "output_type": "array",
    "description": "Dimension vector of a presheaf on a linear poset"
}


def natural_transformation_check(x):
    """Check naturality condition for maps between presheaves on a linear order.
    x = [n, f0, f1, ..., g0, g1, ...] where fi are source dims, gi are target dims.
    Returns 1 if compatible, 0 otherwise. Input: array. Output: integer."""
    n = int(abs(x[0]))
    n = min(max(n, 1), 20)
    if len(x) < 2 * n + 1:
        # Not enough data, default to compatible
        return 1
    f_dims = [int(abs(x[1 + i])) for i in range(n)]
    g_dims = [int(abs(x[1 + n + i])) for i in range(n)]
    # Naturality: for each morphism i->j in poset, the square commutes
    # In a linear order, for i < j: g(i->j) o eta_i = eta_j o f(i->j)
    # This holds iff eta components are compatible with restriction
    # Necessary condition: if f(i) > 0 and g(i) > 0, then eta_i can be defined
    # Simple check: g_dims[i] >= f_dims[i] for all i (enough room for embedding)
    # This is a sufficient but not necessary condition for existence
    for i in range(n):
        if g_dims[i] < f_dims[i]:
            return 0
    return 1


OPERATIONS["natural_transformation_check"] = {
    "fn": natural_transformation_check,
    "input_type": "array",
    "output_type": "integer",
    "description": "Check if natural transformation exists between presheaves (simplified)"
}


def yoneda_embedding_finite(x):
    """Yoneda embedding of object c in finite category into presheaf.
    For poset {0<1<...<n-1}, y(c)(d) = |Hom(d,c)| = 1 if d<=c, else 0.
    x=[n, c]. Input: array. Output: array."""
    n = int(abs(x[0]))
    c = int(abs(x[1])) if len(x) > 1 else 0
    n = min(max(n, 1), 100)
    c = min(c, n - 1)
    # Representable presheaf: y(c)(d) = Hom(d, c) in poset = {1 if d<=c, 0 otherwise}
    result = np.zeros(n, dtype=np.int64)
    for d in range(n):
        result[d] = 1 if d <= c else 0
    return result


OPERATIONS["yoneda_embedding_finite"] = {
    "fn": yoneda_embedding_finite,
    "input_type": "array",
    "output_type": "array",
    "description": "Yoneda embedding y(c) for object c in a finite linear poset"
}


def pullback_in_set(x):
    """Compute pullback (fiber product) of sets via functions.
    x = [n_A, n_B, n_C, f_values..., g_values...] where f: A->C, g: B->C.
    Returns size of pullback. Input: array. Output: integer."""
    idx = 0
    n_A = int(abs(x[idx])); idx += 1
    n_B = int(abs(x[idx])) if idx < len(x) else 1; idx += 1
    n_C = int(abs(x[idx])) if idx < len(x) else 1; idx += 1
    n_A = min(max(n_A, 1), 50)
    n_B = min(max(n_B, 1), 50)
    n_C = min(max(n_C, 1), 50)
    # Read f: A -> C
    f = []
    for i in range(n_A):
        val = int(abs(x[idx])) % n_C if idx < len(x) else i % n_C
        f.append(val)
        idx += 1
    # Read g: B -> C
    g = []
    for i in range(n_B):
        val = int(abs(x[idx])) % n_C if idx < len(x) else i % n_C
        g.append(val)
        idx += 1
    # Pullback = {(a, b) : f(a) = g(b)}
    count = 0
    for a in range(n_A):
        for b in range(n_B):
            if f[a] == g[b]:
                count += 1
    return int(count)


OPERATIONS["pullback_in_set"] = {
    "fn": pullback_in_set,
    "input_type": "array",
    "output_type": "integer",
    "description": "Size of pullback (fiber product) A x_C B in Set"
}


def pushout_in_set(x):
    """Compute pushout (amalgamated sum) of sets.
    x = [n_A, n_B, n_C, f_values..., g_values...] where f: C->A, g: C->B.
    Returns size of pushout. Input: array. Output: integer."""
    idx = 0
    n_A = int(abs(x[idx])); idx += 1
    n_B = int(abs(x[idx])) if idx < len(x) else 1; idx += 1
    n_C = int(abs(x[idx])) if idx < len(x) else 1; idx += 1
    n_A = min(max(n_A, 1), 50)
    n_B = min(max(n_B, 1), 50)
    n_C = min(max(n_C, 1), 50)
    # Read f: C -> A
    f = []
    for i in range(n_C):
        val = int(abs(x[idx])) % n_A if idx < len(x) else i % n_A
        f.append(val)
        idx += 1
    # Read g: C -> B
    g = []
    for i in range(n_C):
        val = int(abs(x[idx])) % n_B if idx < len(x) else i % n_B
        g.append(val)
        idx += 1
    # Pushout = (A + B) / ~ where f(c) ~ g(c) for each c in C
    # Use union-find
    total = n_A + n_B
    parent = list(range(total))

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    def union(u, v):
        u, v = find(u), find(v)
        if u != v:
            parent[u] = v

    for c in range(n_C):
        a_idx = f[c]
        b_idx = n_A + g[c]
        union(a_idx, b_idx)

    # Count distinct components
    roots = set(find(i) for i in range(total))
    return int(len(roots))


OPERATIONS["pushout_in_set"] = {
    "fn": pushout_in_set,
    "input_type": "array",
    "output_type": "integer",
    "description": "Size of pushout (amalgamated sum) A +_C B in Set"
}


def exponential_object_finite(x):
    """Size of exponential object B^A in Set = |B|^|A|. x=[|A|, |B|]. Input: array. Output: integer."""
    n_A = int(abs(x[0]))
    n_B = int(abs(x[1])) if len(x) > 1 else 2
    n_A = min(max(n_A, 0), 20)
    n_B = min(max(n_B, 0), 20)
    # |B^A| = |B|^|A| = number of functions from A to B
    return int(n_B ** n_A)


OPERATIONS["exponential_object_finite"] = {
    "fn": exponential_object_finite,
    "input_type": "array",
    "output_type": "integer",
    "description": "Size of exponential object B^A = |B|^|A| in FinSet"
}


def nerve_of_category(x):
    """Compute nerve dimensions for a finite category (poset).
    x=[n] for linear poset of size n. Returns [N_0, N_1, N_2, ...] simplex counts.
    Input: array. Output: array."""
    n = int(abs(x[0]))
    n = min(max(n, 1), 50)
    # For a linear poset 0 < 1 < ... < n-1:
    # k-simplices = chains of length k+1 = C(n, k+1)
    from math import comb
    max_dim = min(n, 10)
    nerve = np.array([comb(n, k + 1) for k in range(max_dim)], dtype=np.int64)
    # N_0 = n objects, N_1 = C(n,2) morphisms (non-identity), N_2 = C(n,3) composable pairs, etc.
    # Actually N_0 = n, N_k = C(n, k+1) for k >= 0
    return nerve


OPERATIONS["nerve_of_category"] = {
    "fn": nerve_of_category,
    "input_type": "array",
    "output_type": "array",
    "description": "Simplex counts [N_0, N_1, ...] in nerve of a linear poset"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
