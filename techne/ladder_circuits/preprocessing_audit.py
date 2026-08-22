"""PREPROCESSING AUDIT — which layer delivers which invariance? (Cycle 034.)

Round 8 named this the most interesting cycle-022 finding: R0 advertises an *identity congruence
over ASTs*, and what it implements is `srepr ∘ sympy-normalisation`. Cycle 032 measured seven of
eight source-level distinctions erased before the circuit runs. The instruction for this cycle
was to build a RAW-SYNTAX control and separate what sympy did from what the circuit did.

**Applying HITL #129 to the control first changed the question.** Before using it for anything I
constructed the inputs on which it must give the answer I did not want — and it gave them, 6 of
6. `ast.parse` merges redundant parentheses, whitespace, comments, numeric literal spelling
(`1000` / `1_000`), radix (`0x10` / `16`), and string quoting. So:

> **There is no raw. Every keyer is a preprocessing map.** The question is never "circuit or CAS"
> but *which invariances each layer delivers*, and the answer has to be an attribution across
> layers rather than a fraction.

So this module measures a LADDER of keyers, each strictly coarser than the last, and attributes
every invariance to the layer that first introduces it:

    L0  source text        no normalisation at all — the only true floor
    L1  Python ast         lexical: parens, whitespace, comments, literal spelling, radix
    L2  sympy srepr        algebraic: commutativity, associativity, constant folding, powers,
                           rational normalisation, evaluation, cancellation
    L3  circuit key        whatever the circuit itself adds on top of L2

For R0 that last step is variable renaming, and **it is the only invariance R0 contributes.**
Everything else it appears to know was delivered before it ran.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import sympy as sp

__all__ = ["LAYERS", "PAIRS", "raw_source_key", "python_ast_key", "sympy_srepr_key",
           "circuit_canonical_key", "attribute", "Attribution", "audit_pairs",
           "control_is_itself_a_normaliser"]


# --------------------------------------------------------------------------------------------
# The layers, coarsest last.

def raw_source_key(src: str) -> str:
    """L0 — the only genuine floor: the source text itself, unnormalised."""
    return src


def python_ast_key(src: str) -> str:
    """L1 — Python's own parser. Lexical normalisation and nothing algebraic.

    **Not a raw control**, and the docstring says so because I nearly used it as one. See
    `control_is_itself_a_normaliser`.
    """
    return ast.dump(ast.parse(src.strip(), mode="eval"), annotate_fields=False)


def sympy_srepr_key(src: str) -> str:
    """L2 — what R0 actually uses. Algebraic normalisation, applied at construction."""
    return sp.srepr(sp.sympify(src))


def circuit_canonical_key(src: str) -> str:
    """L3 — R0's `canonical_key`: L2 plus a variable-renaming quotient."""
    from techne.ladder_circuits.r0_pattern import canonical_key
    return canonical_key(sp.sympify(src))


LAYERS: Tuple[Tuple[str, Callable[[str], str]], ...] = (
    ("L0 source", raw_source_key),
    ("L1 python-ast", python_ast_key),
    ("L2 sympy-srepr", sympy_srepr_key),
    ("L3 circuit-key", circuit_canonical_key),
)


# --------------------------------------------------------------------------------------------
# The battery: pairs that differ at L0, chosen to separate at each layer.

PAIRS: Tuple[Tuple[str, str, str], ...] = (
    # expected first-merging layer, a, b
    ("L1", "(x)+y", "x+y"),
    ("L1", "1000", "1_000"),
    ("L1", "x  +  y", "x+y"),
    ("L1", "0x10", "16"),
    ("L2", "x+y", "y+x"),
    ("L2", "2*x", "x*2"),
    ("L2", "x**2", "x*x"),
    ("L2", "x/2", "Rational(1,2)*x"),
    ("L2", "(x+1)+2", "x+3"),
    ("L2", "sqrt(4)*x", "2*x"),
    ("L2", "x-x", "0"),
    ("L3", "x+y", "a+b"),
    ("L3", "x*y", "a*b"),
    ("--", "x*(y+1)", "x*y+x"),        # nobody merges: a genuine algebraic identity
    ("--", "x+y", "x+z"),              # nobody merges: genuinely different
)


@dataclass(frozen=True)
class Attribution:
    """Which layer first merged a pair that differs at the source."""

    a: str
    b: str
    first_merging_layer: Optional[str]
    expected: str

    @property
    def as_expected(self) -> bool:
        want = None if self.expected == "--" else self.expected
        got = None if self.first_merging_layer is None else self.first_merging_layer.split()[0]
        return want == got


def attribute(a: str, b: str, expected: str = "--") -> Attribution:
    """Find the coarsest-first layer at which two differing sources become one key."""
    for name, keyer in LAYERS:
        try:
            if keyer(a) == keyer(b):
                return Attribution(a, b, name, expected)
        except Exception:
            continue
    return Attribution(a, b, None, expected)


def audit_pairs(pairs: Sequence[Tuple[str, str, str]] = PAIRS) -> List[Attribution]:
    return [attribute(a, b, expected) for expected, a, b in pairs]


def control_is_itself_a_normaliser() -> Tuple[int, int]:
    """HITL #129 applied to this module's own control, BEFORE it was used for anything.

    Returns `(merged, total)` over inputs the control must merge if it is a normaliser. Measured
    6/6: parentheses, literal spelling, whitespace, comments, radix and string quoting all fall
    to `ast.parse`. That is why this module reports an ATTRIBUTION ACROSS LAYERS rather than a
    circuit-versus-CAS fraction — the fraction would have been computed against a baseline that
    was quietly doing work of its own.
    """
    must_merge = [("(x)+y", "x+y"), ("1000", "1_000"), ("x  +  y", "x+y"),
                  ("x+y", "x+y  # note"), ("0x10", "16"), ("'''a'''", "'a'")]
    merged = 0
    for a, b in must_merge:
        try:
            if python_ast_key(a) == python_ast_key(b):
                merged += 1
        except Exception:
            continue
    return merged, len(must_merge)
