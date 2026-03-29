"""
Cardinal Arithmetic — transfinite arithmetic approximations via finite representations

Connects to: [set theory, model theory, ordinal arithmetic, combinatorics, logic]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "cardinal_arithmetic"
OPERATIONS = {}


def aleph_sequence(x):
    """Generate the first n aleph numbers represented as beth-style tower heights.
    aleph_0 = countable infinity ~ len, aleph_n approximated by iterated power set sizes.
    Input: array. Output: array of log-scale aleph representations."""
    n = len(x)
    # Represent aleph_i as i (ordinal index), but scale by a base
    # In ZFC, aleph_n is the nth infinite cardinal; we represent log-scale
    alephs = np.zeros(n)
    alephs[0] = np.log2(max(np.sum(np.abs(x)), 1.0))  # aleph_0 base
    for i in range(1, n):
        # Each successor cardinal is strictly larger
        alephs[i] = alephs[i - 1] + np.log2(i + 2)
    return alephs


OPERATIONS["aleph_sequence"] = {
    "fn": aleph_sequence,
    "input_type": "array",
    "output_type": "array",
    "description": "Generates log-scale representation of the aleph cardinal sequence"
}


def beth_sequence(x):
    """Generate beth numbers: beth_0 = aleph_0, beth_{n+1} = 2^{beth_n}.
    In log scale: log(beth_{n+1}) = beth_n. Input: array. Output: array."""
    n = len(x)
    beths = np.zeros(n)
    beths[0] = np.log2(max(float(np.sum(np.abs(x))), 2.0))
    for i in range(1, n):
        # beth_{i+1} = 2^{beth_i}, so log_2(beth_{i+1}) = beth_i
        # We cap to avoid overflow
        beths[i] = min(beths[i - 1] ** 2, 1e15)
    return beths


OPERATIONS["beth_sequence"] = {
    "fn": beth_sequence,
    "input_type": "array",
    "output_type": "array",
    "description": "Generates log-scale beth number sequence (iterated power sets)"
}


def cardinal_exponentiation(x):
    """Compute cardinal exponentiation approximation: kappa^lambda for finite cardinals
    derived from x. Input: array (pairs: base, exponent). Output: array."""
    n = len(x)
    pairs = n // 2
    results = np.zeros(max(pairs, 1))
    for i in range(pairs):
        base = max(int(np.abs(x[2 * i])), 1)
        exp = min(int(np.abs(x[2 * i + 1])), 20)  # Cap exponent
        results[i] = float(base ** exp)
    if pairs == 0:
        results[0] = float(max(int(np.abs(x[0])), 1))
    return results


OPERATIONS["cardinal_exponentiation"] = {
    "fn": cardinal_exponentiation,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes cardinal exponentiation for finite cardinal pairs"
}


def cofinality_estimate(x):
    """Estimate cofinality of a limit ordinal/cardinal by finding the smallest cofinal
    subsequence. Input: array (treated as an ordinal sequence). Output: scalar."""
    sorted_x = np.sort(np.abs(x))
    n = len(sorted_x)
    if n <= 1:
        return float(n)
    target = sorted_x[-1]
    # Find minimal cofinal subsequence: smallest subset whose sup = target
    # For a monotone sequence, cofinality = omega (countable) if the sequence is
    # unbounded. For finite sets, cofinality = 1.
    # We approximate: find minimal step size that still reaches the max
    for step in range(1, n + 1):
        subseq = sorted_x[::step]
        if len(subseq) > 0 and subseq[-1] == target:
            return float(len(subseq))
    return float(n)


OPERATIONS["cofinality_estimate"] = {
    "fn": cofinality_estimate,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Estimates cofinality by finding minimal cofinal subsequence length"
}


def konig_theorem_check(x):
    """Verify Konig's theorem: cf(kappa^lambda) > lambda for infinite cardinals.
    Approximated for finite values. Input: array [kappa, lambda]. Output: scalar (1=holds, 0=fails)."""
    if len(x) < 2:
        return 1.0
    kappa = max(int(np.abs(x[0])), 2)
    lam = max(int(np.abs(x[1])), 1)
    lam = min(lam, 15)
    kappa = min(kappa, 100)
    # kappa^lambda
    result = kappa ** lam
    # For finite cardinals, cf(n) = 1 for all finite n > 0
    # Konig's theorem is trivially true for finite cardinals
    # But we check the finite analog: sum_i(a_i) < prod_i(b_i) when a_i < b_i
    n = min(len(x), 10)
    a = np.sort(np.abs(x[:n]))
    b = a + 1  # Ensure a_i < b_i
    holds = float(np.sum(a)) < float(np.prod(np.minimum(b, 1e10)))
    return 1.0 if holds else 0.0


OPERATIONS["konig_theorem_check"] = {
    "fn": konig_theorem_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Checks Konig's theorem inequality for finite cardinal approximations"
}


def cardinal_successor(x):
    """Compute the cardinal successor for each element. For finite n, successor is n+1.
    For transfinite approximation, we jump to the next 'level'. Input: array. Output: array."""
    vals = np.abs(x)
    successors = np.zeros_like(vals)
    for i, v in enumerate(vals):
        if v < 100:
            successors[i] = v + 1  # Finite successor
        else:
            # "Transfinite" jump: next power of 2 (Hartogs number flavor)
            successors[i] = 2 ** np.ceil(np.log2(v + 1))
    return successors


OPERATIONS["cardinal_successor"] = {
    "fn": cardinal_successor,
    "input_type": "array",
    "output_type": "array",
    "description": "Computes cardinal successor (finite: n+1, large: next power-of-2 level)"
}


def continuum_hypothesis_ratio(x):
    """Compute the ratio 2^aleph_0 / aleph_1 in a finite model.
    Under CH this should be 1. We approximate using power set sizes.
    Input: array. Output: scalar."""
    n = len(x)
    # |P(n)| = 2^n, next cardinal after n is n+1 in finite world
    power_set_size = 2.0 ** n
    next_cardinal = n + 1.0
    # Ratio: in finite models, this is far from 1, demonstrating
    # that CH is about the gap in infinite cardinals
    ratio = power_set_size / next_cardinal
    return float(ratio)


OPERATIONS["continuum_hypothesis_ratio"] = {
    "fn": continuum_hypothesis_ratio,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Computes 2^n / (n+1) ratio illustrating the continuum hypothesis gap"
}


def inaccessible_test(x):
    """Test if a value is 'inaccessible-like': regular and a strong limit.
    A cardinal kappa is inaccessible if it's uncountable, regular, and for all
    lambda < kappa, 2^lambda < kappa. Finite approximation.
    Input: array. Output: array (1=inaccessible-like, 0=not)."""
    results = np.zeros(len(x))
    for i, v in enumerate(x):
        v = int(np.abs(v))
        if v < 2:
            results[i] = 0.0
            continue
        # 'Regular': not a sum of fewer than v values less than v
        # For primes, this loosely holds; composite = sum of smaller parts
        is_prime = v > 1 and all(v % d != 0 for d in range(2, min(int(np.sqrt(v)) + 1, v)))
        # 'Strong limit': 2^lambda < v for all lambda < v
        # Only holds trivially for small v
        is_strong_limit = (2 ** max(0, v - 1)) > v  # This is always true for v >= 2, flip logic
        # Actually: strong limit means for all lambda < kappa, 2^lambda < kappa
        # For finite: 2^(v-1) < v is only true for v <= 1. So no finite number is a strong limit.
        # We relax: check if v is a power of 2 (analogous)
        is_power_of_2 = (v & (v - 1)) == 0 and v > 0
        results[i] = 1.0 if (is_prime and is_power_of_2) else 0.0
    return results


OPERATIONS["inaccessible_test"] = {
    "fn": inaccessible_test,
    "input_type": "array",
    "output_type": "array",
    "description": "Tests if values are inaccessible-like (prime and power of 2 = only 2)"
}


def large_cardinal_hierarchy(x):
    """Map input values to positions in the large cardinal hierarchy.
    Higher = stronger consistency strength. Input: array. Output: array."""
    # Hierarchy levels (by consistency strength):
    # 0: inaccessible, 1: Mahlo, 2: weakly compact, 3: indescribable,
    # 4: measurable, 5: strong, 6: Woodin, 7: supercompact,
    # 8: extendible, 9: huge, 10: rank-into-rank, 11: 0=1 (inconsistent)
    hierarchy_names = [
        "inaccessible", "Mahlo", "weakly_compact", "indescribable",
        "measurable", "strong", "Woodin", "supercompact",
        "extendible", "huge", "rank_into_rank"
    ]
    n_levels = len(hierarchy_names)
    # Map x values to hierarchy levels based on their relative rank
    if len(x) == 0:
        return np.array([])
    ranks = np.argsort(np.argsort(np.abs(x)))  # Rank of each element
    levels = (ranks / max(len(x) - 1, 1) * (n_levels - 1)).astype(float)
    return levels


OPERATIONS["large_cardinal_hierarchy"] = {
    "fn": large_cardinal_hierarchy,
    "input_type": "array",
    "output_type": "array",
    "description": "Maps values to positions in the large cardinal consistency hierarchy"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
