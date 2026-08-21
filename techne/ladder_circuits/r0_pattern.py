"""R0 straw-man circuits: retrieval keyed on (canonicalized) sympy ASTs.

Purpose is DIAGNOSTIC, not capability (rung notes: techne/loop/rung_notes/R0_pattern_response.md).

- R0PatternCircuit: exact-AST retrieval — the mechanically precise definition of "pattern
  response". It answers only problems whose surface structure is IDENTICAL to something seen,
  and abstains otherwise. It is the null model every claimed R1+ circuit must beat, and the
  reference implementation of R0's failure signature (answers clean, abstains on isomorphs).
- CanonicalizingCircuit: identical retrieval after alpha-renaming variables to positional
  indices. Deliberately one notch above R0: it survives the rename kill test while still being
  pure retrieval. The R0→R1 boundary IS the choice of AST canonicalization.

Abstention is a first-class output: `answer()` returns None rather than guessing. A retrieval
circuit that guesses is not a weaker reasoner, it is a differently-shaped liar.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import sympy as sp


def ast_key(expr: sp.Expr) -> str:
    """Exact structural key: sympy's canonical srepr, literals and variable NAMES preserved.

    Two problems share a key iff their ASTs are identical — the identity congruence.
    """
    return sp.srepr(expr)


def canonical_key(expr: sp.Expr) -> str:
    """Alpha-invariant key: variables renamed to v0, v1, ... in first-occurrence order of
    sympy's deterministic sorted traversal. Quotients the identity congruence by renaming —
    the smallest step up the AST-congruence lattice."""
    symbols = sorted(expr.free_symbols, key=lambda s: sp.default_sort_key(s))
    ren = {s: sp.Symbol(f"v{i}") for i, s in enumerate(symbols)}
    return sp.srepr(expr.xreplace(ren))


@dataclass
class R0PatternCircuit:
    """Exact-AST retrieval. Holds R0 and nothing above it, by construction."""

    keyer: Any = ast_key
    store: Dict[str, Any] = field(default_factory=dict)

    def train(self, expr: sp.Expr, answer: Any) -> None:
        self.store[self.keyer(expr)] = answer

    def answer(self, expr: sp.Expr) -> Optional[Any]:
        """The trained answer for a structurally identical problem, else None (abstain)."""
        return self.store.get(self.keyer(expr))


def CanonicalizingCircuit() -> R0PatternCircuit:
    """Retrieval that survives variable renaming — NOT an R0 circuit, and that is the point."""
    return R0PatternCircuit(keyer=canonical_key)
