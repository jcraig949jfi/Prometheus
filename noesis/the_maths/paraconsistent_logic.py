"""
Paraconsistent Logic — logic that tolerates contradictions

Connects to: [fuzzy_logic, many_valued_logic, lattice_theory, relevance_logic]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "paraconsistent_logic"
OPERATIONS = {}

# Belnap's four-valued logic: values encoded as (told_true, told_false)
# We represent them as 2D: col0 = told_true degree, col1 = told_false degree
# For 1D input, we interpret pairs: [t1, f1, t2, f2, ...] or just treat
# values as truth degrees and derive contradiction from complementary info.

def _to_belnap(x):
    """Convert array to Belnap pairs. Even indices = told_true, odd = told_false."""
    x = np.asarray(x, dtype=float)
    if x.ndim == 1 and len(x) % 2 == 0:
        return x.reshape(-1, 2)
    # If odd length, pad with 0
    x = np.concatenate([x, [0.0]]) if len(x) % 2 != 0 else x
    return x.reshape(-1, 2)


def belnapian_and(x):
    """Belnap's four-valued AND: min on told_true, max on told_false.
    Input: array (pairs). Output: array (single pair)."""
    pairs = _to_belnap(x)
    t = np.min(pairs[:, 0])
    f = np.max(pairs[:, 1])
    return np.array([t, f])

OPERATIONS["belnapian_and"] = {
    "fn": belnapian_and,
    "input_type": "array",
    "output_type": "array",
    "description": "Belnap four-valued AND: min of true supports, max of false supports"
}


def belnapian_or(x):
    """Belnap's four-valued OR: max on told_true, min on told_false.
    Input: array (pairs). Output: array (single pair)."""
    pairs = _to_belnap(x)
    t = np.max(pairs[:, 0])
    f = np.min(pairs[:, 1])
    return np.array([t, f])

OPERATIONS["belnapian_or"] = {
    "fn": belnapian_or,
    "input_type": "array",
    "output_type": "array",
    "description": "Belnap four-valued OR: max of true supports, min of false supports"
}


def belnapian_not(x):
    """Belnap's negation: swap told_true and told_false.
    Input: array (pairs). Output: array (swapped pairs)."""
    pairs = _to_belnap(x)
    return pairs[:, ::-1].flatten()

OPERATIONS["belnapian_not"] = {
    "fn": belnapian_not,
    "input_type": "array",
    "output_type": "array",
    "description": "Belnap negation: swap true and false support values"
}


def four_valued_entailment(x):
    """Check entailment in Belnap logic: A entails B iff A_true <= B_true and B_false <= A_false.
    Takes [A_true, A_false, B_true, B_false]. Returns 1.0 if entails, 0.0 otherwise.
    Input: array. Output: scalar."""
    x = np.asarray(x, dtype=float)
    if len(x) < 4:
        return 0.0
    a_t, a_f, b_t, b_f = x[0], x[1], x[2], x[3]
    # Information ordering: a <= b iff a_t <= b_t and a_f <= b_f
    entails = float(a_t <= b_t + 1e-12 and b_f <= a_f + 1e-12)
    return entails

OPERATIONS["four_valued_entailment"] = {
    "fn": four_valued_entailment,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Belnap entailment check on the truth ordering"
}


def degree_of_inconsistency(x):
    """Measure contradiction: min(told_true, told_false) for each pair.
    Returns mean inconsistency across all propositions.
    Input: array (pairs). Output: scalar."""
    pairs = _to_belnap(x)
    inconsistencies = np.minimum(pairs[:, 0], pairs[:, 1])
    return float(np.mean(inconsistencies))

OPERATIONS["degree_of_inconsistency"] = {
    "fn": degree_of_inconsistency,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Mean degree of inconsistency: average of min(true_support, false_support)"
}


def paraconsistent_inference(x):
    """LP (Logic of Paradox) inference: truth value in {0, 0.5, 1} where 0.5 = both.
    Maps continuous inputs to three-valued: >0.66 -> 1 (true), <0.33 -> 0 (false),
    else -> 0.5 (both true and false). Returns the designated values (>=0.5 count as accepted).
    Input: array. Output: array."""
    x = np.asarray(x, dtype=float)
    # Map to LP three values
    lp = np.where(x > 0.66, 1.0, np.where(x < 0.33, 0.0, 0.5))
    return lp

OPERATIONS["paraconsistent_inference"] = {
    "fn": paraconsistent_inference,
    "input_type": "array",
    "output_type": "array",
    "description": "LP three-valued logic: map to {0, 0.5, 1} where 0.5 means both T and F"
}


def dialetheia_degree(x):
    """Degree to which each value is a dialetheia (true contradiction).
    Uses the product of truth and falsity degrees. For a single array,
    treats consecutive pairs as (truth, falsity) evidence.
    Input: array (pairs). Output: scalar."""
    pairs = _to_belnap(x)
    # Dialetheia strength = product of positive evidence for both
    strengths = pairs[:, 0] * pairs[:, 1]
    return float(np.max(strengths))

OPERATIONS["dialetheia_degree"] = {
    "fn": dialetheia_degree,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Maximum dialetheia (true contradiction) strength across propositions"
}


def truth_value_lattice(x):
    """Compute the lattice join/meet structure of Belnap's FOUR.
    Returns the knowledge-ordering lattice distances between consecutive pairs.
    Knowledge order: None < {T,F} < Both, with T and F incomparable.
    Input: array (pairs). Output: array."""
    pairs = _to_belnap(x)
    # Encode each pair as a knowledge level: k = t + f (0=none, 1=one, 2=both)
    knowledge = pairs[:, 0] + pairs[:, 1]
    # Lattice distances between consecutive elements
    if len(knowledge) < 2:
        return np.array([0.0])
    dists = np.abs(np.diff(knowledge))
    return dists

OPERATIONS["truth_value_lattice"] = {
    "fn": truth_value_lattice,
    "input_type": "array",
    "output_type": "array",
    "description": "Knowledge-ordering distances in Belnap's FOUR lattice"
}


def relevance_logic_check(x):
    """Check variable sharing (relevance condition): A->B is relevant only if
    A and B share a propositional variable. We approximate: given truth vectors,
    check if the support sets overlap. Returns overlap ratio.
    Input: array. Output: scalar."""
    x = np.asarray(x, dtype=float)
    n = len(x) // 2
    if n == 0:
        return 0.0
    a = x[:n]
    b = x[n:2*n]
    # "Variables" are indices where value is non-negligible
    a_support = np.abs(a) > 0.1
    b_support = np.abs(b) > 0.1
    shared = np.sum(a_support & b_support)
    total = np.sum(a_support | b_support)
    if total == 0:
        return 0.0
    return float(shared / total)

OPERATIONS["relevance_logic_check"] = {
    "fn": relevance_logic_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Relevance condition: variable-sharing ratio between antecedent and consequent"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
