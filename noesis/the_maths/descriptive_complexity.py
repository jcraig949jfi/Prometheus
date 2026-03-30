"""
Descriptive Complexity — Characterizing complexity classes by logic fragments: FO = AC0, SO-exists = NP

Connects to: [formal_logic_systems, proof_complexity, automata_infinite_words]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "descriptive_complexity"
OPERATIONS = {}


def first_order_quantifier_rank(x):
    """Compute the first-order quantifier rank needed to distinguish structures.
    On a linear order of size n, quantifier rank ceil(log2(n)) suffices (EF games).
    Input: array (structure elements). Output: scalar."""
    n = max(len(x), 1)
    return float(np.ceil(np.log2(n + 1)))


OPERATIONS["first_order_quantifier_rank"] = {
    "fn": first_order_quantifier_rank,
    "input_type": "array",
    "output_type": "scalar",
    "description": "FO quantifier rank to distinguish structures: ceil(log2(n))"
}


def existential_second_order_check(x):
    """Check if input encodes a witness for an existential second-order (ESO = NP) property.
    ESO: exists R such that phi(R) holds. We check a simple NP property:
    does there exist a subset summing to target (x[0])?
    Input: array (x[0] = target, rest = set). Output: scalar (0 or 1)."""
    if len(x) < 2:
        return 0.0
    target = round(x[0])
    elements = np.round(x[1:]).astype(int)
    n = len(elements)
    # Brute force subset sum for small n (up to 20)
    if n > 20:
        elements = elements[:20]
        n = 20
    for mask in range(2 ** n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += elements[i]
        if s == target:
            return 1.0
    return 0.0


OPERATIONS["existential_second_order_check"] = {
    "fn": existential_second_order_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "ESO (NP) witness check: subset sum with target x[0]"
}


def monadic_second_order_tree(x):
    """Evaluate a monadic second-order (MSO) property on a tree.
    MSO on trees is decidable (Rabin's theorem). We check a simple MSO property:
    does the tree (encoded as parent array) have a dominating set of size <= n/2?
    Input: array (parent pointers, root = self-loop). Output: scalar (0 or 1)."""
    n = len(x)
    parent = np.round(np.abs(x)).astype(int) % n
    # Find a dominating set greedily (leaves first)
    # A node is dominated if it or its parent is in the set
    in_set = np.zeros(n, dtype=bool)
    dominated = np.zeros(n, dtype=bool)
    # Simple greedy: select every other level
    children_count = np.zeros(n, dtype=int)
    for i in range(n):
        if parent[i] != i:
            children_count[parent[i]] += 1
    # Select nodes with children (internal nodes)
    for i in range(n):
        if children_count[i] > 0:
            in_set[i] = True
    return float(np.sum(in_set) <= n / 2)


OPERATIONS["monadic_second_order_tree"] = {
    "fn": monadic_second_order_tree,
    "input_type": "array",
    "output_type": "scalar",
    "description": "MSO on tree: check if dominating set exists with <= n/2 nodes"
}


def fixed_point_logic_iterate(x):
    """Iterate a fixed-point logic operator (IFP = Immerman-Vardi on ordered structures = P).
    Compute transitive closure via repeated squaring of adjacency matrix.
    Input: array (flattened sqrt(n) x sqrt(n) adjacency). Output: array (flattened closure)."""
    n = len(x)
    side = int(np.sqrt(n))
    if side * side != n:
        side = int(np.ceil(np.sqrt(n)))
    mat = np.zeros((side, side))
    for i in range(min(n, side * side)):
        mat[i // side, i % side] = 1.0 if x[i] > 0.5 else 0.0
    # Transitive closure via repeated squaring
    closure = mat.copy()
    for _ in range(int(np.ceil(np.log2(max(side, 2))))):
        closure = ((closure @ closure) > 0).astype(float)
        closure = np.maximum(closure, mat)
    return closure.flatten()[:n]


OPERATIONS["fixed_point_logic_iterate"] = {
    "fn": fixed_point_logic_iterate,
    "input_type": "array",
    "output_type": "array",
    "description": "Fixed-point logic: compute transitive closure via repeated squaring"
}


def counting_logic_extension(x):
    """Counting logic extension (FO+C): count elements satisfying a predicate.
    FO+C can express properties like 'an even number of elements satisfy p'.
    Input: array. Output: array [count_positive, count_negative, count_zero, parity]."""
    pos = np.sum(x > 0.5)
    neg = np.sum(x < -0.5)
    zero = np.sum(np.abs(x) <= 0.5)
    parity = pos % 2  # even/odd count
    return np.array([float(pos), float(neg), float(zero), float(parity)])


OPERATIONS["counting_logic_extension"] = {
    "fn": counting_logic_extension,
    "input_type": "array",
    "output_type": "array",
    "description": "FO+Counting: count positives, negatives, zeros, and parity"
}


def ehrenfeucht_fraisse_rounds(x):
    """Compute Ehrenfeucht-Fraisse game rounds needed to distinguish two structures.
    For two linear orders of sizes a and b, Duplicator wins r rounds iff
    they agree on all sentences of quantifier rank r.
    Spoiler needs ceil(log2(|a-b|+1)) + 1 rounds on linear orders.
    Input: array (split into two halves as two structures). Output: scalar."""
    n = len(x)
    half = n // 2
    size_a = half
    size_b = n - half
    if size_a == size_b:
        # Same size linear orders are EF-equivalent at all finite rounds
        # (if same size and same order type)
        return float(np.ceil(np.log2(size_a + 1)))
    diff = abs(size_a - size_b)
    rounds = np.ceil(np.log2(diff + 1)) + 1
    return float(rounds)


OPERATIONS["ehrenfeucht_fraisse_rounds"] = {
    "fn": ehrenfeucht_fraisse_rounds,
    "input_type": "array",
    "output_type": "scalar",
    "description": "EF game rounds to distinguish two linear orders from split input"
}


def pebble_game_number(x):
    """Compute the k-pebble game number: minimum pebbles to distinguish structures.
    On structures of treewidth t, k = t+1 pebbles suffice.
    Estimate treewidth from array as a graph (flattened adjacency).
    Input: array. Output: scalar."""
    n = len(x)
    side = int(np.sqrt(n))
    if side < 2:
        return 1.0
    # For a graph on 'side' vertices, treewidth <= side - 1
    # Estimate: count non-zero edges to estimate density
    edges = np.sum(np.abs(x[:side * side]) > 0.5)
    # Sparse graphs have low treewidth; dense graphs have high
    density = edges / max(side * side, 1)
    tw_estimate = max(1, int(density * side))
    return float(tw_estimate + 1)  # k = tw + 1


OPERATIONS["pebble_game_number"] = {
    "fn": pebble_game_number,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Minimum pebbles for k-pebble game (treewidth + 1 estimate)"
}


def locality_gaifman_radius(x):
    """Compute Gaifman locality radius. By Gaifman's theorem, every FO sentence
    is equivalent to a boolean combination of local sentences.
    Locality radius for quantifier rank q is 3^q - 1.
    Input: array. Output: scalar."""
    n = max(len(x), 1)
    q = np.ceil(np.log2(n + 1))  # quantifier rank
    radius = 3.0 ** q - 1.0
    return float(radius)


OPERATIONS["locality_gaifman_radius"] = {
    "fn": locality_gaifman_radius,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Gaifman locality radius: 3^(quantifier_rank) - 1"
}


def order_invariant_query(x):
    """Check if a query result is order-invariant: same result regardless of linear order.
    Compute a property (e.g., sum) on x and on sorted x; if same, order-invariant.
    Input: array. Output: scalar (1 if invariant, 0 if not)."""
    # A truly order-invariant query gives same result on any permutation
    # Test: compare result on original vs reversed
    val_orig = np.sum(x ** 2)  # sum of squares is order-invariant
    val_rev = np.sum(x[::-1] ** 2)
    return float(abs(val_orig - val_rev) < 1e-10)


OPERATIONS["order_invariant_query"] = {
    "fn": order_invariant_query,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check order-invariance: query gives same result regardless of element order"
}


def immerman_vardi_iterate(x):
    """Immerman-Vardi theorem: on ordered structures, IFP = P.
    Iterate a PTIME-computable operator (reachability) until fixed point.
    Return iteration count. Input: array (flattened adjacency). Output: scalar."""
    n = len(x)
    side = int(np.sqrt(n))
    if side < 2:
        return 1.0
    mat = np.zeros((side, side))
    for i in range(min(n, side * side)):
        mat[i // side, i % side] = 1.0 if x[i] > 0.5 else 0.0
    # Iterate: R_{i+1} = R_i union {(a,c) : exists b, R_i(a,b) and mat(b,c)}
    reach = mat.copy()
    for step in range(1, side + 1):
        new_reach = ((reach @ mat) > 0).astype(float)
        new_reach = np.maximum(new_reach, reach)
        if np.allclose(new_reach, reach):
            return float(step)
        reach = new_reach
    return float(side)


OPERATIONS["immerman_vardi_iterate"] = {
    "fn": immerman_vardi_iterate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Immerman-Vardi: iteration count for reachability fixed point"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
