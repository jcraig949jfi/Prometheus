"""
CANONICALIZER:poly_monomial_form@v1 — Type A (canonical identity).

First non-tensor instance of the canonicalizer primitive. Polynomials up
to variable relabeling and sign gauge.

Equivalence group G:
  - permutation(S_n) acting on variable indices
  - sign_gauge: p(x) ~ -p(x) iff -p(x) is the "canonical sign"

Declared limitations:
  - Does NOT handle affine change of variable (x -> ax + b).
  - Does NOT handle non-trivial GL actions on the polynomial ring (e.g.,
    SL(2) on binary forms).
  - Variable-signature tie-breaking falls back to lex index order on
    unordered variables; ties within degree can produce two inputs
    whose canonical forms differ only in variable labels when the
    signature is truly symmetric (e.g., x^2 + y^2). This is a known
    partial-quotienting gap called out in declared_limitations.

Procedure C:
  1. Represent polynomial as dict {monomial_tuple: coefficient}.
     monomial_tuple = sorted tuple of (var_index, exponent) pairs in
     v1's RAW (input) variable ordering.
  2. Compute variable signatures: for each variable i, signature_i =
     sum over monomials m of |coeff(m)| * total_degree(m) for m touching
     variable i.
  3. Sort variables by (signature, original_index) to get canonical
     variable ordering.
  4. Rewrite monomials with canonical variable indices.
  5. Apply sign gauge: if the leading coefficient (under the canonical
     monomial ordering below) is negative, multiply all coefficients
     by -1.
  6. Lex-sort monomials under the canonical variable ordering, where
     a monomial's key is (total_degree descending, per-var-exponent
     tuple descending in canonical var order).
  7. Return a tuple of (canonical_monomial, coefficient) pairs.

Hash: SHA-256 of deterministic JSON serialization of the canonical form,
with coefficients rounded to 8 decimal places.
"""

from __future__ import annotations
import hashlib
import json
from typing import Dict, List, Tuple


Monomial = Tuple[Tuple[int, int], ...]  # ((var_idx, exponent), ...) sorted
Polynomial = Dict[Monomial, float]


def _normalize_monomial(mono: Monomial) -> Monomial:
    """Sort (var_idx, exp) pairs by var_idx; drop zero-exp entries."""
    filtered = tuple((i, e) for i, e in mono if e != 0)
    return tuple(sorted(filtered))


def _total_degree(mono: Monomial) -> int:
    return sum(e for _, e in mono)


def _variable_signature(poly: Polynomial, var_idx: int) -> float:
    sig = 0.0
    for mono, coeff in poly.items():
        for i, e in mono:
            if i == var_idx and e != 0:
                sig += abs(coeff) * _total_degree(mono)
                break
    return sig


def _variables(poly: Polynomial) -> List[int]:
    vs = set()
    for mono in poly:
        for i, e in mono:
            if e != 0:
                vs.add(i)
    return sorted(vs)


def _relabel(poly: Polynomial, permutation: Dict[int, int]) -> Polynomial:
    """Apply var_idx permutation: var i becomes var permutation[i]."""
    out: Polynomial = {}
    for mono, coeff in poly.items():
        new_mono = _normalize_monomial(tuple((permutation[i], e) for i, e in mono))
        out[new_mono] = out.get(new_mono, 0.0) + coeff
    return {m: c for m, c in out.items() if abs(c) > 1e-12}


def _lex_key(mono: Monomial, n_vars: int) -> Tuple:
    """Sort key for monomials in canonical form.
    Ordering: total degree descending, then per-variable-exponent tuple
    (from var 0 to var n_vars-1) descending.
    """
    exp_vector = [0] * n_vars
    for i, e in mono:
        exp_vector[i] = e
    return (-_total_degree(mono), tuple(-e for e in exp_vector))


def canonicalize(poly: Polynomial) -> Tuple[Tuple[Monomial, float], ...]:
    """Type A canonical form for a polynomial.

    Input: dict mapping monomial tuples (sorted (var_idx, exp) pairs) to
    coefficients.

    Output: tuple of (canonical_monomial, coefficient) pairs, in canonical
    order. Rounds coefficients to 8 decimal places for hash stability.
    """
    if not poly:
        return tuple()

    variables = _variables(poly)
    if not variables:
        # constant polynomial
        c = sum(poly.values())
        if c < 0:
            c = -c
        return (((), round(c, 8)),) if c != 0 else tuple()

    # Step 2-3: compute signatures + canonical variable order
    sigs = [(_variable_signature(poly, v), v) for v in variables]
    # Sort by (signature, original_index) — low signatures first
    sigs.sort()
    canonical_order = [v for _, v in sigs]
    # Build permutation: original var v -> new index j
    permutation = {v: j for j, v in enumerate(canonical_order)}

    # Step 4: relabel
    relabeled = _relabel(poly, permutation)

    # Step 5: sign gauge
    n_vars = len(canonical_order)
    if relabeled:
        # Find leading monomial under lex order
        leading_mono = min(relabeled.keys(), key=lambda m: _lex_key(m, n_vars))
        if relabeled[leading_mono] < 0:
            relabeled = {m: -c for m, c in relabeled.items()}

    # Step 6: lex-sort
    sorted_items = sorted(relabeled.items(), key=lambda item: _lex_key(item[0], n_vars))

    # Step 7: build canonical representation with rounded coefficients
    return tuple((m, round(c, 8)) for m, c in sorted_items if abs(c) > 1e-12)


def canonical_hash(poly: Polynomial) -> str:
    canonical = canonicalize(poly)
    payload = json.dumps(
        [[list(m), c] for m, c in canonical],
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


# ---------- instance metadata (added v0.3 stratification 2026-04-25) ----------

INSTANCE_METADATA = {
    "name": "poly_monomial_form",
    "version": 1,
    "type": "A",
    "subclass": "group_quotient",
    "equivalence_E": "polynomial up to variable permutation S_n + sign gauge",
    "declared_limitations": [
        {
            "name": "no_affine_change_of_variable",
            "severity": "total",
            "workaround": "Instance does not handle x -> ax + b. Consumers needing affine equivalence require a separate instance.",
        },
        {
            "name": "no_GL_action_on_polynomial_ring",
            "severity": "total",
            "workaround": "Instance does not handle non-trivial GL actions (e.g., SL(2) on binary forms). Consumers requiring such must use a separate instance.",
        },
        {
            "name": "symmetric_polynomial_signature_ties",
            "severity": "partial",
            "workaround": "Variable-signature tie-breaking falls back to lex on unordered variables; for fully symmetric polynomials (e.g., x^2 + y^2) the canonical form is determined by the original index ordering. Practical workaround: use a smaller toy instance for symmetric forms specifically.",
        },
    ],
    "calibration_anchors": {
        "variable_relabel_equivalence": {"description": "x^2 - 1 == y^2 - 1 (under S_2)", "passed": True},
        "sign_gauge_equivalence": {"description": "x^2 - 1 == -(x^2 - 1)", "passed": True},
        "constant_sign_discrimination": {"description": "x^2 - 1 != x^2 + 1", "passed": True},
        "var_swap_equivalence": {"description": "x^2 + y == x + y^2 (under x<->y)", "passed": True},
        "coefficient_discrimination": {"description": "x + y != x + 2y", "passed": True},
        "trivial_reorder_equivalence": {"description": "x^2 + y^2 == y^2 + x^2 (insertion order)", "passed": True},
    },
    "implementation_path": "agora/canonicalizer/poly_monomial_form_v1.py::canonical_hash",
    "first_shipped": "2026-04-23",
}


# ---------- calibration anchors ----------

def _poly(*terms) -> Polynomial:
    """Convenience: build a polynomial from (coefficient, monomial) pairs.
    Monomial is a dict {var_idx: exp} or a tuple of (var_idx, exp) pairs.
    """
    out: Polynomial = {}
    for coeff, mono in terms:
        if isinstance(mono, dict):
            mono_tuple = tuple(sorted((i, e) for i, e in mono.items() if e != 0))
        else:
            mono_tuple = _normalize_monomial(mono)
        out[mono_tuple] = out.get(mono_tuple, 0.0) + coeff
    return {m: c for m, c in out.items() if abs(c) > 1e-12}


def run_calibration():
    print("=== CANONICALIZER:poly_monomial_form@v1 — calibration anchors ===\n")

    anchors = []

    # Anchor 1: x^2 - 1 and y^2 - 1 should hash identically (variable relabel)
    p1 = _poly((1, {0: 2}), (-1, {}))      # x^2 - 1 (var 0)
    p2 = _poly((1, {1: 2}), (-1, {}))      # y^2 - 1 (var 1)
    h1, h2 = canonical_hash(p1), canonical_hash(p2)
    same_class_1 = (h1 == h2)
    print(f"Anchor 1 (same-class, variable relabel):")
    print(f"  x^2 - 1 hash: {h1}")
    print(f"  y^2 - 1 hash: {h2}")
    print(f"  Expected: same. Result: {'SAME (pass)' if same_class_1 else 'DIFFERENT (fail)'}\n")
    anchors.append(("same-class variable-relabel", same_class_1, True))

    # Anchor 2: x^2 - 1 and -(x^2 - 1) = -x^2 + 1 should hash identically (sign gauge)
    p3 = _poly((-1, {0: 2}), (1, {}))      # -x^2 + 1
    h3 = canonical_hash(p3)
    same_class_2 = (h1 == h3)
    print(f"Anchor 2 (same-class, sign gauge):")
    print(f"  x^2 - 1   hash: {h1}")
    print(f"  -x^2 + 1  hash: {h3}")
    print(f"  Expected: same. Result: {'SAME (pass)' if same_class_2 else 'DIFFERENT (fail)'}\n")
    anchors.append(("same-class sign-gauge", same_class_2, True))

    # Anchor 3: x^2 - 1 and x^2 + 1 should hash DIFFERENTLY (not equivalent)
    p4 = _poly((1, {0: 2}), (1, {}))       # x^2 + 1
    h4 = canonical_hash(p4)
    diff_class_1 = (h1 != h4)
    print(f"Anchor 3 (different-class, +1 vs -1 constant term):")
    print(f"  x^2 - 1 hash: {h1}")
    print(f"  x^2 + 1 hash: {h4}")
    print(f"  Expected: different. Result: {'DIFFERENT (pass)' if diff_class_1 else 'SAME (fail)'}\n")
    anchors.append(("different-class constant-sign", diff_class_1, True))

    # Anchor 4: x^2 + y and x + y^2 should hash DIFFERENTLY (non-symmetric var usage)
    p5 = _poly((1, {0: 2}), (1, {1: 1}))   # x^2 + y
    p6 = _poly((1, {0: 1}), (1, {1: 2}))   # x + y^2
    h5, h6 = canonical_hash(p5), canonical_hash(p6)
    # Under variable permutation x <-> y: x^2+y becomes y^2+x = x+y^2 — ARE equivalent!
    same_class_3 = (h5 == h6)
    print(f"Anchor 4 (same-class via S_2 relabel):")
    print(f"  x^2 + y hash: {h5}")
    print(f"  x + y^2 hash: {h6}")
    print(f"  Under x<->y swap, x^2+y -> y^2+x = x+y^2. Expected: same.")
    print(f"  Result: {'SAME (pass)' if same_class_3 else 'DIFFERENT (fail)'}\n")
    anchors.append(("same-class var swap", same_class_3, True))

    # Anchor 5: x + y and x + 2y should hash DIFFERENTLY (coefficients distinguish)
    p7 = _poly((1, {0: 1}), (1, {1: 1}))   # x + y
    p8 = _poly((1, {0: 1}), (2, {1: 1}))   # x + 2y
    h7, h8 = canonical_hash(p7), canonical_hash(p8)
    diff_class_2 = (h7 != h8)
    print(f"Anchor 5 (different-class, different coefficients):")
    print(f"  x + y  hash: {h7}")
    print(f"  x + 2y hash: {h8}")
    print(f"  Expected: different. Result: {'DIFFERENT (pass)' if diff_class_2 else 'SAME (fail)'}\n")
    anchors.append(("different-class coefficient", diff_class_2, True))

    # Anchor 6: known partial-limit — symmetric polynomial edge case
    # x^2 + y^2 and y^2 + x^2 are trivially same (just reordering)
    p9 = _poly((1, {0: 2}), (1, {1: 2}))   # x^2 + y^2
    p10 = _poly((1, {1: 2}), (1, {0: 2}))  # y^2 + x^2 (same polynomial, different insertion order)
    h9, h10 = canonical_hash(p9), canonical_hash(p10)
    print(f"Anchor 6 (same-class, trivial reorder):")
    print(f"  x^2 + y^2 (inserted x first) hash: {h9}")
    print(f"  y^2 + x^2 (inserted y first) hash: {h10}")
    print(f"  Expected: same. Result: {'SAME (pass)' if h9 == h10 else 'DIFFERENT (fail)'}\n")
    anchors.append(("same-class trivial reorder", h9 == h10, True))

    # Summary
    print("=== VERDICT ===")
    passed = sum(1 for _, actual, expected in anchors if actual == expected)
    for name, actual, expected in anchors:
        status = "PASS" if actual == expected else "FAIL"
        print(f"  {status}: {name}")
    print(f"\n{passed}/{len(anchors)} calibration anchors pass.")
    if passed == len(anchors):
        print("poly_monomial_form@v1 VALIDATED on first non-tensor Type A instance.")
    else:
        print("poly_monomial_form@v1 PARTIAL — document failures as declared_limitations.")
    return passed == len(anchors)


if __name__ == "__main__":
    run_calibration()
