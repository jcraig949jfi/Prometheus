"""MINT-0001 vacuous_truth -- semantic specification (re-run under the typed / verified protocol).

Semantic state: q (route key) in {universal, negative_universal, existential}; d = domain size;
s = satisfier count with 0 <= s <= d. Target: truth value (bool).
SEARCH points: the operator's table instantiated at n in {1,2,3,5}. VERIFY points: exhaustive
0 <= s <= d <= 12 -- disjoint from and much larger than the search points (Q8 requirement).
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "agents" / "hephaestus" / "src"))
import forge_primitives as fp  # noqa: E402

NOTES = "vacuous_truth kernel; typed membership + counterfactual verification (Addendum 3)."
REPRESENTATION_DEBT = ("Large: extracting (quantifier, domain noun phrase, predicate, domain_size, satisfier_count) "
                       "from text with domain EQUALITY as the acceptance rule; measured adapter v3 covers 0.9125 of "
                       "author-adversarial dev v2 and 0.20 of out-of-template phrasings, conditional correctness 1.0.")
ROUTE_KEYS = ["universal", "negative_universal", "existential"]
TARGET_TYPE = "bool"

SEARCH_POINTS = [(0, 0)] + [(n, s) for n in (1, 2, 3, 5) for s in range(0, n + 1)]
# VERIFY_EXHAUSTIVE_SMALL: every (d, s) with 0 <= s <= d <= 12, minus the search points.
VERIFY_POINTS = [(d, s) for d in range(0, 13) for s in range(0, d + 1) if (d, s) not in set(SEARCH_POINTS)]
# VERIFY_STRUCTURAL_SHIFT (Addendum 4, Q5): a different regime -- large domains far from the search
# sizes, including the boundary rows s = d, s = d-1, s = 0, s = 1 at every size 40..60. An alias that
# exploits small-number arithmetic (e.g. a probability that underflows, a modulus coincidence) fails here.
VERIFY_SHIFT_DESCRIPTION = "domain sizes 40..60 with boundary rows s in {0, 1, d-1, d} and a mid row"
VERIFY_SHIFT_POINTS = [(d, s) for d in range(40, 61) for s in sorted({0, 1, d // 2, d - 1, d})]


def target(q, pt):
    d, s = pt
    if d == 0:
        return q != "existential"
    return {"universal": s == d, "negative_universal": s == 0, "existential": s >= 1}[q]


TERMINALS = {
    "d": ("int", lambda pt: pt[0]),
    "s": ("int", lambda pt: pt[1]),
    "0": ("int", lambda pt: 0),
    "1": ("int", lambda pt: 1),
}

# Frozen primitives with STATIC return types as declared/observed. Only integer-typed ones apply.
FROZEN_OPS = {
    "all_but_n":              (("int", "int"), "int",   lambda a, b: fp.all_but_n(a, b)),
    "pigeonhole_check":       (("int", "int"), "bool",  lambda a, b: fp.pigeonhole_check(a, b)),
    "fencepost_count_T":      (("int",), "int",         lambda a: fp.fencepost_count(a, True)),
    "fencepost_count_F":      (("int",), "int",         lambda a: fp.fencepost_count(a, False)),
    "modular_arithmetic":     (("int", "int", "int"), "int", lambda a, b, m: fp.modular_arithmetic(a, b, m) if m else 0),
    "coin_flip_independence": (("int", "int"), "float", lambda n, k: fp.coin_flip_independence(n, k) if 0 <= k <= n else 0.0),
    "information_sufficiency": (("int", "int"), "str",  lambda a, b: fp.information_sufficiency(a, b)),
    "parity_check_pair":      (("int", "int"), "str",   lambda a, b: fp.parity_check([a, b])),
}
# A2 uses the FROZEN global basis (closure_specs/generic_basis.py); per-spec generic ops are forbidden.
# B: small generic language (the control)
B_OPS = {
    "eq":  (("int", "int"), "bool", lambda a, b: a == b),
    "lt":  (("int", "int"), "bool", lambda a, b: a < b),
    "le":  (("int", "int"), "bool", lambda a, b: a <= b),
    "gt":  (("int", "int"), "bool", lambda a, b: a > b),
    "ge":  (("int", "int"), "bool", lambda a, b: a >= b),
    "not": (("bool",), "bool", lambda a: not a),
    "and": (("bool", "bool"), "bool", lambda a, b: a and b),
    "or":  (("bool", "bool"), "bool", lambda a, b: a or b),
    "add": (("int", "int"), "int", lambda a, b: a + b),
    "sub": (("int", "int"), "int", lambda a, b: a - b),
}
