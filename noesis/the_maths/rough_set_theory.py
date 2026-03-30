"""
Rough Set Theory -- Lower/upper approximations, boundary regions, reducts, discernibility

Connects to: [lattice_theory, topological_data_analysis, paraconsistent_logic, partition_logic]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "rough_set_theory"
OPERATIONS = {}


def _build_information_system(x):
    """Build an information system from flat array.
    Returns decision table: objects x attributes, last column is decision."""
    n = len(x)
    n_attrs = min(3, n - 1)
    n_objects = n // (n_attrs + 1)
    if n_objects < 2:
        n_objects = 2
        n_attrs = max(1, n // n_objects - 1)
    total = n_objects * (n_attrs + 1)
    padded = np.zeros(total)
    padded[:min(n, total)] = x[:min(n, total)]
    table = padded.reshape(n_objects, n_attrs + 1)
    # Discretize to integer classes
    for col in range(n_attrs + 1):
        med = np.median(table[:, col])
        table[:, col] = (table[:, col] > med).astype(float)
    return table, n_objects, n_attrs


def _indiscernibility(table, attrs):
    """Compute equivalence classes for given attributes."""
    n_objects = table.shape[0]
    classes = {}
    for i in range(n_objects):
        key = tuple(table[i, attrs].astype(int))
        if key not in classes:
            classes[key] = set()
        classes[key].add(i)
    return list(classes.values())


def lower_approximation(x):
    """Lower approximation of decision classes by condition attributes.
    Input: array. Output: array (indicator of objects in lower approximation)."""
    table, n_obj, n_attrs = _build_information_system(x)
    cond_attrs = list(range(n_attrs))
    dec_col = n_attrs
    eq_classes = _indiscernibility(table, cond_attrs)
    # Decision classes
    dec_classes = {}
    for i in range(n_obj):
        d = int(table[i, dec_col])
        if d not in dec_classes:
            dec_classes[d] = set()
        dec_classes[d].add(i)
    # Lower approximation: union of eq classes fully contained in some decision class
    lower = set()
    for eq_class in eq_classes:
        for d, dec_class in dec_classes.items():
            if eq_class <= dec_class:
                lower |= eq_class
                break
    result = np.zeros(n_obj)
    for i in lower:
        result[i] = 1.0
    return result


OPERATIONS["lower_approximation"] = {
    "fn": lower_approximation,
    "input_type": "array",
    "output_type": "array",
    "description": "Lower approximation of decision classes"
}


def upper_approximation(x):
    """Upper approximation of decision classes.
    Input: array. Output: array (indicator)."""
    table, n_obj, n_attrs = _build_information_system(x)
    cond_attrs = list(range(n_attrs))
    dec_col = n_attrs
    eq_classes = _indiscernibility(table, cond_attrs)
    dec_classes = {}
    for i in range(n_obj):
        d = int(table[i, dec_col])
        if d not in dec_classes:
            dec_classes[d] = set()
        dec_classes[d].add(i)
    # Upper approximation: union of eq classes that intersect some decision class
    upper = set()
    for eq_class in eq_classes:
        for d, dec_class in dec_classes.items():
            if eq_class & dec_class:
                upper |= eq_class
                break
    result = np.zeros(n_obj)
    for i in upper:
        result[i] = 1.0
    return result


OPERATIONS["upper_approximation"] = {
    "fn": upper_approximation,
    "input_type": "array",
    "output_type": "array",
    "description": "Upper approximation of decision classes"
}


def boundary_region(x):
    """Boundary region = upper approximation - lower approximation.
    Input: array. Output: array."""
    lower = lower_approximation(x)
    upper = upper_approximation(x)
    mn = min(len(lower), len(upper))
    return upper[:mn] - lower[:mn]


OPERATIONS["boundary_region"] = {
    "fn": boundary_region,
    "input_type": "array",
    "output_type": "array",
    "description": "Boundary region (uncertain objects)"
}


def positive_region(x):
    """Positive region: objects definitely classifiable. Same as lower approximation union.
    Input: array. Output: scalar (fraction of objects in positive region)."""
    lower = lower_approximation(x)
    return float(np.mean(lower))


OPERATIONS["positive_region"] = {
    "fn": positive_region,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Fraction of objects in positive region"
}


def discernibility_matrix(x):
    """Compute discernibility matrix: M[i,j] = set of attributes distinguishing objects i,j.
    Returns flattened count matrix. Input: array. Output: array."""
    table, n_obj, n_attrs = _build_information_system(x)
    disc = np.zeros((n_obj, n_obj))
    for i in range(n_obj):
        for j in range(i + 1, n_obj):
            count = 0
            for a in range(n_attrs):
                if table[i, a] != table[j, a]:
                    count += 1
            disc[i, j] = count
            disc[j, i] = count
    return disc.ravel()


OPERATIONS["discernibility_matrix"] = {
    "fn": discernibility_matrix,
    "input_type": "array",
    "output_type": "array",
    "description": "Discernibility matrix (count of distinguishing attributes per pair)"
}


def reduct_find(x):
    """Find a reduct (minimal attribute subset preserving classification).
    Input: array. Output: array (indicator of attributes in reduct)."""
    table, n_obj, n_attrs = _build_information_system(x)
    dec_col = n_attrs
    # Full positive region
    all_attrs = list(range(n_attrs))
    full_classes = _indiscernibility(table, all_attrs)
    # Greedy forward selection
    selected = []
    remaining = list(range(n_attrs))
    for _ in range(n_attrs):
        best_attr = None
        best_score = -1
        for attr in remaining:
            test_attrs = selected + [attr]
            classes = _indiscernibility(table, test_attrs)
            # Score: number of singleton-like classes
            score = sum(1 for c in classes if len(c) == 1)
            if score > best_score:
                best_score = score
                best_attr = attr
        if best_attr is not None:
            selected.append(best_attr)
            remaining.remove(best_attr)
            # Check if we match full classification
            if _indiscernibility(table, selected) == full_classes:
                break
    result = np.zeros(n_attrs)
    for a in selected:
        result[a] = 1.0
    return result


OPERATIONS["reduct_find"] = {
    "fn": reduct_find,
    "input_type": "array",
    "output_type": "array",
    "description": "Find a reduct via greedy forward selection"
}


def rough_membership(x):
    """Rough membership function: degree to which each object belongs to its decision class.
    mu(x, X) = |[x]_R intersection X| / |[x]_R|. Input: array. Output: array."""
    table, n_obj, n_attrs = _build_information_system(x)
    cond_attrs = list(range(n_attrs))
    dec_col = n_attrs
    eq_classes = _indiscernibility(table, cond_attrs)
    dec_classes = {}
    for i in range(n_obj):
        d = int(table[i, dec_col])
        if d not in dec_classes:
            dec_classes[d] = set()
        dec_classes[d].add(i)
    membership = np.zeros(n_obj)
    for eq_class in eq_classes:
        for obj in eq_class:
            d = int(table[obj, dec_col])
            intersection = eq_class & dec_classes.get(d, set())
            membership[obj] = len(intersection) / len(eq_class) if len(eq_class) > 0 else 0
    return membership


OPERATIONS["rough_membership"] = {
    "fn": rough_membership,
    "input_type": "array",
    "output_type": "array",
    "description": "Rough membership degree for each object"
}


def rough_entropy(x):
    """Rough entropy of the partition induced by condition attributes.
    H = -sum p_i log p_i where p_i = |class_i|/|U|. Input: array. Output: scalar."""
    table, n_obj, n_attrs = _build_information_system(x)
    cond_attrs = list(range(n_attrs))
    eq_classes = _indiscernibility(table, cond_attrs)
    probs = np.array([len(c) / n_obj for c in eq_classes])
    probs = probs[probs > 0]
    entropy = -np.sum(probs * np.log2(probs + 1e-30))
    return float(entropy)


OPERATIONS["rough_entropy"] = {
    "fn": rough_entropy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Shannon entropy of the equivalence class partition"
}


def approximation_quality(x):
    """Quality of approximation gamma = |POS_R(D)| / |U|.
    Input: array. Output: scalar."""
    return positive_region(x)


OPERATIONS["approximation_quality"] = {
    "fn": approximation_quality,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Quality of rough approximation (gamma coefficient)"
}


def rough_inclusion_degree(x):
    """Rough inclusion degree: how well set A is included in set B.
    Uses first half as A, second half as B (thresholded). Input: array. Output: scalar."""
    n = len(x)
    half = n // 2
    med = np.median(x)
    A = set(i for i in range(half) if x[i] > med)
    B = set(i for i in range(half) if (half + i < n and x[half + i] > med))
    if len(A) == 0:
        return 1.0
    return float(len(A & B) / len(A))


OPERATIONS["rough_inclusion_degree"] = {
    "fn": rough_inclusion_degree,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Degree of rough inclusion of one set in another"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
