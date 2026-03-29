"""
Catuskoti Logic — Buddhist four-valued logic (true/false/both/neither) as algebraic lattice

Connects to: [navya_nyaya_logic, jain_combinatorics, bambara_divination]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.

Encoding: 0=false, 1=true, 2=both, 3=neither
This forms a Belnap bilattice with two orderings:
  - truth order: false < neither < true, false < both < true
  - knowledge order: neither < false < both, neither < true < both
"""

import numpy as np

FIELD_NAME = "catuskoti_logic"
OPERATIONS = {}

# Truth table indices: F=0, T=1, B=2, N=3
# Belnap bilattice AND (truth-meet): conjunction in knowledge lattice
_AND_TABLE = np.array([
    [0, 0, 0, 0],  # F & {F,T,B,N}
    [0, 1, 2, 3],  # T & {F,T,B,N}
    [0, 2, 2, 0],  # B & {F,T,B,N}
    [0, 3, 0, 3],  # N & {F,T,B,N}
], dtype=float)

_OR_TABLE = np.array([
    [0, 1, 2, 3],  # F | {F,T,B,N}
    [1, 1, 1, 1],  # T | {F,T,B,N}
    [2, 1, 2, 1],  # B | {F,T,B,N}
    [3, 1, 1, 3],  # N | {F,T,B,N}
], dtype=float)

_NOT_TABLE = np.array([1.0, 0.0, 2.0, 3.0])  # ~F=T, ~T=F, ~B=B, ~N=N

# Knowledge-meet (consensus): what both sources agree on
_K_MEET = np.array([
    [0, 3, 0, 3],
    [3, 1, 1, 3],
    [0, 1, 2, 3],
    [3, 3, 3, 3],
], dtype=float)

# Knowledge-join (gullibility): accept everything from both
_K_JOIN = np.array([
    [0, 2, 2, 0],
    [2, 1, 2, 1],
    [2, 2, 2, 2],
    [0, 1, 2, 3],
], dtype=float)


def _to_idx(x):
    return np.clip(np.round(x).astype(int), 0, 3)


def catuskoti_and(x):
    """Four-valued AND: pairwise AND of adjacent elements. Input: array. Output: array."""
    idx = _to_idx(x)
    result = []
    for i in range(len(idx) - 1):
        result.append(_AND_TABLE[idx[i], idx[i + 1]])
    if len(result) == 0:
        return x.copy()
    return np.array(result)


OPERATIONS["catuskoti_and"] = {
    "fn": catuskoti_and,
    "input_type": "array",
    "output_type": "array",
    "description": "Pairwise four-valued AND of adjacent elements"
}


def catuskoti_or(x):
    """Four-valued OR: pairwise OR of adjacent elements. Input: array. Output: array."""
    idx = _to_idx(x)
    result = []
    for i in range(len(idx) - 1):
        result.append(_OR_TABLE[idx[i], idx[i + 1]])
    if len(result) == 0:
        return x.copy()
    return np.array(result)


OPERATIONS["catuskoti_or"] = {
    "fn": catuskoti_or,
    "input_type": "array",
    "output_type": "array",
    "description": "Pairwise four-valued OR of adjacent elements"
}


def catuskoti_not(x):
    """Four-valued negation: ~T=F, ~F=T, ~B=B, ~N=N. Input: array. Output: array."""
    idx = _to_idx(x)
    return _NOT_TABLE[idx]


OPERATIONS["catuskoti_not"] = {
    "fn": catuskoti_not,
    "input_type": "array",
    "output_type": "array",
    "description": "Four-valued negation"
}


def catuskoti_implies(x):
    """Four-valued implication: a->b = ~a OR b, pairwise. Input: array. Output: array."""
    idx = _to_idx(x)
    result = []
    for i in range(len(idx) - 1):
        neg_a = int(_NOT_TABLE[idx[i]])
        result.append(_OR_TABLE[neg_a, idx[i + 1]])
    if len(result) == 0:
        return x.copy()
    return np.array(result)


OPERATIONS["catuskoti_implies"] = {
    "fn": catuskoti_implies,
    "input_type": "array",
    "output_type": "array",
    "description": "Four-valued material implication a->b for adjacent pairs"
}


def four_value_lattice_meet(x):
    """Knowledge-lattice meet (consensus) of adjacent pairs. Input: array. Output: array."""
    idx = _to_idx(x)
    result = []
    for i in range(len(idx) - 1):
        result.append(_K_MEET[idx[i], idx[i + 1]])
    if len(result) == 0:
        return x.copy()
    return np.array(result)


OPERATIONS["four_value_lattice_meet"] = {
    "fn": four_value_lattice_meet,
    "input_type": "array",
    "output_type": "array",
    "description": "Knowledge-lattice meet (consensus) of adjacent pairs"
}


def four_value_lattice_join(x):
    """Knowledge-lattice join (gullibility) of adjacent pairs. Input: array. Output: array."""
    idx = _to_idx(x)
    result = []
    for i in range(len(idx) - 1):
        result.append(_K_JOIN[idx[i], idx[i + 1]])
    if len(result) == 0:
        return x.copy()
    return np.array(result)


OPERATIONS["four_value_lattice_join"] = {
    "fn": four_value_lattice_join,
    "input_type": "array",
    "output_type": "array",
    "description": "Knowledge-lattice join (gullibility) of adjacent pairs"
}


def belnap_bilattice_construct(x):
    """Construct full Belnap bilattice product for each value:
    returns [truth_component, knowledge_component] flattened.
    truth: F=0,T=1,B=0.5,N=0.5; knowledge: F=0.5,T=0.5,B=1,N=0.
    Input: array. Output: array."""
    idx = _to_idx(x)
    truth = np.array([0.0, 1.0, 0.5, 0.5])
    knowledge = np.array([0.5, 0.5, 1.0, 0.0])
    t_vals = truth[idx]
    k_vals = knowledge[idx]
    return np.concatenate([t_vals, k_vals])


OPERATIONS["belnap_bilattice_construct"] = {
    "fn": belnap_bilattice_construct,
    "input_type": "array",
    "output_type": "array",
    "description": "Maps each 4-value to its (truth, knowledge) bilattice coordinates"
}


def knowledge_state_evaluate(x):
    """Evaluate overall knowledge state: ratio of informative values (T,F,B) vs uninformative (N).
    Input: array. Output: scalar."""
    idx = _to_idx(x)
    informative = np.sum(idx != 3)
    return float(informative / max(len(idx), 1))


OPERATIONS["knowledge_state_evaluate"] = {
    "fn": knowledge_state_evaluate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Ratio of informative values to total (knowledge completeness)"
}


def catuskoti_entailment(x):
    """Check entailment chain: does x[0]->x[1]->...->x[n] hold?
    Returns degree of entailment (fraction of valid implications).
    Input: array. Output: scalar."""
    idx = _to_idx(x)
    if len(idx) < 2:
        return 1.0
    valid = 0
    for i in range(len(idx) - 1):
        neg_a = int(_NOT_TABLE[idx[i]])
        imp = _OR_TABLE[neg_a, idx[i + 1]]
        if imp == 1.0 or imp == 2.0:  # true or both => entailment holds
            valid += 1
    return float(valid / (len(idx) - 1))


OPERATIONS["catuskoti_entailment"] = {
    "fn": catuskoti_entailment,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Degree of entailment along the chain of values"
}


def catuskoti_contradiction_degree(x):
    """Measure contradiction: fraction of elements that are 'both' (value 2).
    Input: array. Output: scalar."""
    idx = _to_idx(x)
    return float(np.sum(idx == 2) / max(len(idx), 1))


OPERATIONS["catuskoti_contradiction_degree"] = {
    "fn": catuskoti_contradiction_degree,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Fraction of elements in the 'both' (contradictory) state"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
