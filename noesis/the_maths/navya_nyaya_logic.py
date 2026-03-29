"""
Navya-Nyaya Logic — Indian logic with typed absence as first-class logical object

Connects to: [catuskoti_logic, jain_combinatorics, context_dependent_arithmetic]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.

In Navya-Nyaya, absence (abhava) is a structured entity with four types:
  - pragabhava (prior absence): absence before creation
  - pradhvamsabhava (posterior absence): absence after destruction
  - atyantabhava (absolute absence): absence at all times
  - anyonyabhava (mutual absence): A is not B (difference)

Values represent property-presence as continuous [0,1]. Absence is
modeled structurally, not as simple negation.
"""

import numpy as np

FIELD_NAME = "navya_nyaya_logic"
OPERATIONS = {}


def prior_absence(x):
    """Pragabhava: prior absence — max(0, threshold - x). Property absent before
    reaching threshold (mean). Input: array. Output: array."""
    threshold = np.mean(x)
    return np.maximum(0.0, threshold - x)


OPERATIONS["prior_absence"] = {
    "fn": prior_absence,
    "input_type": "array",
    "output_type": "array",
    "description": "Prior absence (pragabhava): deficit below mean threshold"
}


def posterior_absence(x):
    """Pradhvamsabhava: posterior absence — absence after a peak. For each element,
    measures decline from running maximum. Input: array. Output: array."""
    running_max = np.maximum.accumulate(x)
    return np.maximum(0.0, running_max - x)


OPERATIONS["posterior_absence"] = {
    "fn": posterior_absence,
    "input_type": "array",
    "output_type": "array",
    "description": "Posterior absence (pradhvamsabhava): decline from running maximum"
}


def absolute_absence(x):
    """Atyantabhava: absolute absence — property never present.
    Returns 1 where value is exactly 0, else 0. Input: array. Output: array."""
    return (np.abs(x) < 1e-12).astype(float)


OPERATIONS["absolute_absence"] = {
    "fn": absolute_absence,
    "input_type": "array",
    "output_type": "array",
    "description": "Absolute absence (atyantabhava): 1 where value is zero"
}


def mutual_absence(x):
    """Anyonyabhava: mutual absence (difference) — pairwise |x[i] - x[j]| for
    adjacent elements. A is not B when they differ. Input: array. Output: array."""
    if len(x) < 2:
        return np.array([0.0])
    return np.abs(np.diff(x))


OPERATIONS["mutual_absence"] = {
    "fn": mutual_absence,
    "input_type": "array",
    "output_type": "array",
    "description": "Mutual absence (anyonyabhava): absolute difference of adjacent pairs"
}


def absence_type_classify(x):
    """Classify each element's absence type:
    0=no absence (x > mean+std), 1=prior (x < mean-std),
    2=posterior (x declining from local max), 3=absolute (x ~ 0),
    4=mutual (flagged by high local variance).
    Input: array. Output: array."""
    mu = np.mean(x)
    std = np.std(x) + 1e-12
    result = np.zeros_like(x)
    # absolute absence
    result[np.abs(x) < 1e-10] = 3.0
    # prior absence
    mask_prior = (x < mu - std) & (np.abs(x) >= 1e-10)
    result[mask_prior] = 1.0
    # posterior absence: declining from running max
    running_max = np.maximum.accumulate(x)
    decline = running_max - x
    mask_post = (decline > std) & (result == 0) & (x < mu)
    result[mask_post] = 2.0
    return result


OPERATIONS["absence_type_classify"] = {
    "fn": absence_type_classify,
    "input_type": "array",
    "output_type": "array",
    "description": "Classifies each element's absence type (0-4)"
}


def qualifier_relation(x):
    """Viseshana (qualifier) relation: each element qualifies the next.
    Returns the ratio x[i]/x[i+1] representing qualification strength.
    Input: array. Output: array."""
    if len(x) < 2:
        return np.array([1.0])
    denom = np.where(np.abs(x[1:]) < 1e-12, 1e-12, x[1:])
    return x[:-1] / denom


OPERATIONS["qualifier_relation"] = {
    "fn": qualifier_relation,
    "input_type": "array",
    "output_type": "array",
    "description": "Qualifier-qualified ratio for adjacent elements"
}


def qualified_relation(x):
    """Viseshya (qualified) relation: property-bearer strength.
    Returns element-wise product with positional weight (later = more qualified).
    Input: array. Output: array."""
    weights = np.linspace(0.5, 1.0, len(x))
    return x * weights


OPERATIONS["qualified_relation"] = {
    "fn": qualified_relation,
    "input_type": "array",
    "output_type": "array",
    "description": "Positionally-weighted qualified relation"
}


def navya_negation(x):
    """Navya-Nyaya negation: structurally different from classical/intuitionistic.
    Classical: ~p = 1-p. Intuitionistic: ~p requires proof of impossibility.
    Navya: absence is typed — negation returns (absence_type, degree) encoded as
    type*10 + degree. Uses prior_absence model. Input: array. Output: array."""
    mu = np.mean(x)
    std = np.std(x) + 1e-12
    # Degree of absence: how far below the mean, normalized
    degree = np.clip((mu - x) / (3 * std), 0, 1)
    # Type: 0 if present, 1 prior, 3 absolute
    atype = np.zeros_like(x)
    atype[np.abs(x) < 1e-10] = 3.0
    atype[(x < mu - std) & (np.abs(x) >= 1e-10)] = 1.0
    # Encode: type * 10 + degree (so 10.8 = prior absence degree 0.8)
    return atype * 10.0 + degree


OPERATIONS["navya_negation"] = {
    "fn": navya_negation,
    "input_type": "array",
    "output_type": "array",
    "description": "Structured Navya-Nyaya negation encoding (type*10 + degree)"
}


def property_locus_check(x):
    """Check if property is present in locus: returns 1 where x > mean (property
    present at locus), 0 otherwise. In Navya-Nyaya, a property (dharma) resides
    in a locus (dharmin). Input: array. Output: array."""
    mu = np.mean(x)
    return (x > mu).astype(float)


OPERATIONS["property_locus_check"] = {
    "fn": property_locus_check,
    "input_type": "array",
    "output_type": "array",
    "description": "Checks property presence at each locus (above mean)"
}


def absence_compose(x):
    """Compose absences: if both prior and posterior absence exist, yields absolute
    absence. Returns composed absence measure per element. Input: array. Output: array."""
    pa = prior_absence(x)
    post = posterior_absence(x)
    # Where both types of absence are nonzero, we get absolute absence
    composed = np.minimum(pa, post)
    # Scale to [0,1]
    mx = np.max(composed) if np.max(composed) > 0 else 1.0
    return composed / mx


OPERATIONS["absence_compose"] = {
    "fn": absence_compose,
    "input_type": "array",
    "output_type": "array",
    "description": "Composes prior and posterior absence into absolute absence"
}


def relational_abstract(x):
    """Relational abstract (sambandha): extracts the abstract relational structure.
    Computes normalized covariance-like structure from running pairs.
    Input: array. Output: array."""
    if len(x) < 2:
        return np.array([0.0])
    pairs_product = x[:-1] * x[1:]
    mu_product = np.mean(pairs_product)
    mu_x = np.mean(x[:-1]) * np.mean(x[1:])
    # Relational strength per pair
    relation = pairs_product - mu_x
    # Normalize
    mx = np.max(np.abs(relation)) if np.max(np.abs(relation)) > 0 else 1.0
    return relation / mx


OPERATIONS["relational_abstract"] = {
    "fn": relational_abstract,
    "input_type": "array",
    "output_type": "array",
    "description": "Extracts abstract relational structure from adjacent pairs"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
