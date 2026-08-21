"""R2 straw man: multi-step execution along a SUPPLIED order (Canon Band E, R2).

Rung notes: techne/loop/rung_notes/R2_multi_step.md. The circuit executes a given program
(ordered list of rule names) by threading the intermediate EXPRESSION through guarded rules.
No planning, no search: the order is supplied — that is what separates R2 from R4/R7.

The falsification payload for claim v2 lives in the STATE TYPE: what flows between steps is
an unbounded expression, not fixed-arity slot bindings — see the rung notes for the v2→v3
amendment this forced.

Honesty features:
- `run()` returns the full TRACE (every intermediate expression), never just the answer —
  an R2 claim without a checkable trace is indistinguishable from end-to-end retrieval
  (gaming trap 8).
- Any step failing (no match, guard, exception) aborts to None. Partial credit is a
  different rung's business.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import sympy as sp


@dataclass(frozen=True)
class TransformRule:
    """A guarded expression->expression step. `apply` returns None to signal no-match."""

    name: str
    apply: Callable[[sp.Expr], Optional[sp.Expr]]


def rule_together() -> TransformRule:
    """Combine a sum of fractions over a common denominator: 3/(x+1) + 4/(x-1) ->
    (7x+1)/((x+1)(x-1)). Guarded to fire only when it changes something. (First draft used
    expand/collect, but sympy AUTO-expands integer*(sum) at construction, making those steps
    no-ops — a real lesson about picking rule granularity above the CAS's automatic layer.)"""
    def _apply(e: sp.Expr) -> Optional[sp.Expr]:
        out = sp.together(e)
        return out if out != e else None
    return TransformRule("together", _apply)


def rule_numer() -> TransformRule:
    """Pass to the numerator (solving f = 0 for a rational f). Guard: the denominator must
    actually involve a variable — numer of a non-fraction is a no-match, not identity."""
    def _apply(e: sp.Expr) -> Optional[sp.Expr]:
        n, d = sp.fraction(e)
        if not d.free_symbols:
            return None
        return n
    return TransformRule("numer", _apply)


def rule_linear_root() -> TransformRule:
    """Terminal step: a*x+b -> its root as a Rational expression (guard: numeric a != 0)."""
    def _apply(e: sp.Expr) -> Optional[sp.Expr]:
        syms = sorted(e.free_symbols, key=sp.default_sort_key)
        if len(syms) != 1:
            return None
        x = syms[0]
        poly = sp.Poly(e, x)
        if poly.degree() != 1:
            return None
        a, b = poly.all_coeffs()
        if a == 0 or a.free_symbols or b.free_symbols:
            return None
        return -sp.Rational(b) / sp.Rational(a) if a.is_rational and b.is_rational else -b / a
    return TransformRule("linear_root", _apply)


def rule_noop_annotate() -> TransformRule:
    """A distractor: does nothing, legally. R2 must complete THROUGH it (v0.1 probe table:
    'insert one irrelevant distractor step; R2 should still complete')."""
    return TransformRule("annotate", lambda e: e)


def rule_succ_elim() -> TransformRule:
    """One succ-elimination step: innermost succ(k) with integer k -> k+1. Exists to make the
    iteration argument executable: succ-towers of arbitrary depth need arbitrarily many
    firings, so no fixed program handles the whole family."""
    succ = sp.Function("succ")

    def _apply(e: sp.Expr) -> Optional[sp.Expr]:
        for node in sp.preorder_traversal(e):
            if node.func == succ and node.args and node.args[0].is_Integer:
                return e.xreplace({node: node.args[0] + 1})
        return None
    return TransformRule("succ_elim", _apply)


REGISTRY: Dict[str, Callable[[], TransformRule]] = {
    r().name: (lambda rr=r: rr()) for r in (rule_together, rule_numer, rule_linear_root,
                                            rule_noop_annotate, rule_succ_elim)
}


@dataclass
class R2PipelineCircuit:
    """Executes a supplied program of known rules, threading one expression through."""

    registry: Dict[str, TransformRule] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.registry is None:
            self.registry = {name: make() for name, make in REGISTRY.items()}

    def run(
        self, expr: sp.Expr, program: List[str]
    ) -> Tuple[Optional[Any], List[sp.Expr]]:
        """(answer, trace). trace[k] is the expression AFTER step k; on abort, the trace up
        to the failure is still returned — failures are data (F-axis doctrine)."""
        trace: List[sp.Expr] = []
        cur = expr
        if not program:
            return None, trace
        for name in program:
            rule = self.registry.get(name)
            if rule is None:
                return None, trace
            try:
                nxt = rule.apply(cur)
            except Exception:
                return None, trace
            if nxt is None:
                return None, trace
            cur = nxt
            trace.append(cur)
        return cur, trace

    def answer(self, expr: sp.Expr, program: List[str]) -> Optional[Any]:
        return self.run(expr, program)[0]

    def run_until_fixpoint(
        self, expr: sp.Expr, name: str, max_steps: int = 1000
    ) -> Tuple[Optional[sp.Expr], List[sp.Expr]]:
        """The ITERATION ingredient (ChatGPT critique, 2026-08-21): variable-length execution
        is not expressible as any fixed R1 pipeline — 'apply rule until no match' is a new
        combinator, not a longer program. Kept explicit and bounded (max_steps) so runaway
        rules fail loudly instead of spinning."""
        trace: List[sp.Expr] = []
        rule = self.registry.get(name)
        if rule is None:
            return None, trace
        cur = expr
        for _ in range(max_steps):
            try:
                nxt = rule.apply(cur)
            except Exception:
                return None, trace
            if nxt is None:
                return cur, trace          # fixpoint reached: no match left
            cur = nxt
            trace.append(cur)
        return None, trace                  # budget exhausted = failure, never silent
