"""
Abstract Rewriting — Confluence checking, termination orderings, Church-Rosser property, critical pairs

Connects to: [domain_theory, formal_logic_systems, proof_complexity]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "abstract_rewriting"
OPERATIONS = {}


def string_rewrite_step(x):
    """Apply one rewrite step: replace first occurrence of pattern [a, b] where a > b
    with [b, a] (bubble sort as rewriting). Input: array. Output: array."""
    result = x.copy()
    for i in range(len(result) - 1):
        if result[i] > result[i + 1]:
            result[i], result[i + 1] = result[i + 1], result[i]
            break
    return result


OPERATIONS["string_rewrite_step"] = {
    "fn": string_rewrite_step,
    "input_type": "array",
    "output_type": "array",
    "description": "One rewrite step: swap first adjacent pair where left > right (bubble sort rule)"
}


def normal_form_compute(x):
    """Compute normal form by exhaustively applying rewrite rules (sort = normal form
    of the bubble-swap rewriting system). Input: array. Output: array."""
    return np.sort(x)


OPERATIONS["normal_form_compute"] = {
    "fn": normal_form_compute,
    "input_type": "array",
    "output_type": "array",
    "description": "Compute normal form (sorted array) of the swap rewriting system"
}


def is_confluent_finite(x):
    """Check if a finite rewriting system is confluent by checking if all elements
    reduce to the same normal form regardless of reduction order.
    For our swap system, this is always 1 (sorting is confluent). Input: array. Output: scalar."""
    # The adjacent-swap rewriting system is confluent: any reduction order yields sorted array
    nf = np.sort(x)
    # Verify by doing multiple random-order reductions
    for _ in range(5):
        arr = x.copy()
        perm = np.random.permutation(len(arr) - 1)
        changed = True
        while changed:
            changed = False
            for i in perm:
                if arr[i] > arr[i + 1]:
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    changed = True
        if not np.allclose(arr, nf):
            return 0.0
    return 1.0


OPERATIONS["is_confluent_finite"] = {
    "fn": is_confluent_finite,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check confluence of swap rewriting by verifying unique normal form"
}


def church_rosser_check(x):
    """Check Church-Rosser property: if a ->* b and a ->* c, then b and c have common reduct.
    Equivalent to confluence for our system. Returns 1 if holds.
    Input: array. Output: scalar."""
    # For the sorting rewrite system, Church-Rosser = confluence = always true
    # We verify: take two different reduction paths, check they converge
    arr1 = x.copy()
    arr2 = x.copy()
    # Path 1: left-to-right passes
    for _ in range(len(x)):
        for i in range(len(arr1) - 1):
            if arr1[i] > arr1[i + 1]:
                arr1[i], arr1[i + 1] = arr1[i + 1], arr1[i]
    # Path 2: right-to-left passes
    for _ in range(len(x)):
        for i in range(len(arr2) - 2, -1, -1):
            if arr2[i] > arr2[i + 1]:
                arr2[i], arr2[i + 1] = arr2[i + 1], arr2[i]
    return float(np.allclose(arr1, arr2))


OPERATIONS["church_rosser_check"] = {
    "fn": church_rosser_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Verify Church-Rosser: two reduction strategies yield same normal form"
}


def critical_pair_count(x):
    """Count critical pairs in the rewriting system. For adjacent-swap rules on n symbols,
    critical pairs arise when rules overlap: (a,b) and (b,c) overlap at b.
    Count triples where x[i] > x[i+1] and x[i+1] > x[i+2]. Input: array. Output: scalar."""
    count = 0
    for i in range(len(x) - 2):
        if x[i] > x[i + 1] and x[i + 1] > x[i + 2]:
            count += 1
    return float(count)


OPERATIONS["critical_pair_count"] = {
    "fn": critical_pair_count,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Count overlapping critical pairs (descending triples) in rewrite system"
}


def termination_order_check(x):
    """Check if the rewriting system terminates using a well-founded ordering.
    For bubble-swap: the number of inversions strictly decreases. Returns inversion count
    (a termination measure). Input: array. Output: scalar."""
    n = len(x)
    inversions = 0
    for i in range(n):
        for j in range(i + 1, n):
            if x[i] > x[j]:
                inversions += 1
    return float(inversions)


OPERATIONS["termination_order_check"] = {
    "fn": termination_order_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Compute inversion count (termination measure for swap rewriting)"
}


def reduction_count_to_normal(x):
    """Count the number of rewrite steps to reach normal form (bubble sort steps).
    Input: array. Output: scalar."""
    arr = x.copy()
    steps = 0
    changed = True
    while changed:
        changed = False
        for i in range(len(arr) - 1):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                steps += 1
                changed = True
                break
    return float(steps)


OPERATIONS["reduction_count_to_normal"] = {
    "fn": reduction_count_to_normal,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Count single-swap rewrite steps to reach sorted normal form"
}


def rewrite_system_ambiguity(x):
    """Measure ambiguity: number of positions where a rewrite rule can be applied.
    (Number of adjacent pairs with left > right.) Input: array. Output: scalar."""
    count = 0
    for i in range(len(x) - 1):
        if x[i] > x[i + 1]:
            count += 1
    return float(count)


OPERATIONS["rewrite_system_ambiguity"] = {
    "fn": rewrite_system_ambiguity,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Count number of applicable rewrite positions (ambiguity measure)"
}


def knuth_bendix_completion_step(x):
    """One step of Knuth-Bendix completion: resolve a critical pair by adding a new rule.
    For our system, orient the first critical pair found (descending triple)
    and return the rewritten array. Input: array. Output: array."""
    result = x.copy()
    for i in range(len(result) - 2):
        if result[i] > result[i + 1] and result[i + 1] > result[i + 2]:
            # Critical pair: swap(i,i+1) vs swap(i+1,i+2) overlap
            # Resolve by sorting the triple (adding derived rule)
            triple = sorted([result[i], result[i + 1], result[i + 2]])
            result[i], result[i + 1], result[i + 2] = triple[0], triple[1], triple[2]
            break
    return result


OPERATIONS["knuth_bendix_completion_step"] = {
    "fn": knuth_bendix_completion_step,
    "input_type": "array",
    "output_type": "array",
    "description": "Knuth-Bendix: resolve first critical pair by sorting the overlapping triple"
}


def diamond_property_check(x):
    """Check diamond property: if a -> b and a -> c (one step), do b and c reduce to
    a common element in one step? For swap rewriting on non-overlapping positions, yes.
    Returns fraction of pairs satisfying diamond. Input: array. Output: scalar."""
    # Find all applicable rewrite positions
    positions = []
    for i in range(len(x) - 1):
        if x[i] > x[i + 1]:
            positions.append(i)
    if len(positions) < 2:
        return 1.0  # Trivially holds
    # Check all pairs of positions
    diamond_count = 0
    total = 0
    for pi in range(len(positions)):
        for pj in range(pi + 1, len(positions)):
            p1, p2 = positions[pi], positions[pj]
            total += 1
            # Apply p1 then p2, and p2 then p1
            arr1 = x.copy()
            arr1[p1], arr1[p1 + 1] = arr1[p1 + 1], arr1[p1]
            arr2 = x.copy()
            arr2[p2], arr2[p2 + 1] = arr2[p2 + 1], arr2[p2]
            # Now try to close the diamond
            arr1b = arr2.copy()
            if p1 < len(arr1b) - 1 and arr1b[p1] > arr1b[p1 + 1]:
                arr1b[p1], arr1b[p1 + 1] = arr1b[p1 + 1], arr1b[p1]
            arr2b = arr1.copy()
            if p2 < len(arr2b) - 1 and arr2b[p2] > arr2b[p2 + 1]:
                arr2b[p2], arr2b[p2 + 1] = arr2b[p2 + 1], arr2b[p2]
            if np.allclose(arr1b, arr2b):
                diamond_count += 1
    return float(diamond_count / total) if total > 0 else 1.0


OPERATIONS["diamond_property_check"] = {
    "fn": diamond_property_check,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Check diamond property: fraction of rewrite pairs that close in one step"
}


if __name__ == "__main__":
    print(f"Testing {FIELD_NAME}...")
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
