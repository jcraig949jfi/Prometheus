"""R1 straw man: guarded template-rule circuit — applies ONE known operation correctly.

Rung notes: techne/loop/rung_notes/R1_local_operation.md. The R1 object is a *fibration with
a guard*, not a bare congruence (cycle-002 amendment to the cycle-001 claim): a rule maps a
template equivalence class plus literal witnesses to an answer, restricted by a legality
guard. "One known operation" = exactly one rule firing exactly once.

Abstention is first-class: no matching rule, guard failure, or a problem that would need the
rule twice all return None. An R1 circuit that chains rules is mislabeled R2.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import sympy as sp


@dataclass(frozen=True)
class Rule:
    """One known operation: template with Wild slots, legality guard, answer function."""

    name: str
    template: sp.Expr                     # e.g. a*x + b with a,b Wild, x concrete-slot
    guard: Callable[[Dict[str, Any]], bool]
    answer: Callable[[Dict[str, Any]], Any]


def linear_root_rule() -> Rule:
    """The canonical R1 rule: root of a*x + b (a != 0) is -b/a. Guard IS the operation's
    legality domain — 0*x + 7 matches the template but has no root."""
    a, b = sp.Wild("a", exclude=[0]), sp.Wild("b")
    x = sp.Wild("x", properties=[lambda e: e.is_Symbol])
    return Rule(
        name="linear_root",
        template=a * x + b,
        guard=lambda m: m["a"] != 0 and getattr(m["a"], "free_symbols", set()) == set()
        and getattr(m["b"], "free_symbols", set()) == set(),
        answer=lambda m: -m["b"] / m["a"],
    )


@dataclass
class R1LocalOpCircuit:
    """Holds R1: applies each SUPPLIED rule at the root of the expression, at most once."""

    rules: List[Rule] = field(default_factory=list)

    def give_rule(self, rule: Rule) -> None:
        self.rules.append(rule)

    def answer(self, expr: sp.Expr) -> Optional[Any]:
        """One rule, one application, guard-checked. None on no match / guard fail /
        anything that would need more than one firing."""
        for rule in self.rules:
            a, b, xw = sorted(rule.template.atoms(sp.Wild), key=lambda w: w.name)
            m = expr.match(rule.template)
            if m is None:
                continue
            bind = {w.name: v for w, v in m.items()}
            # Reject matches where a slot swallowed structure the template did not intend:
            # every non-variable slot must bind a CONSTANT (that is what "local" means here).
            try:
                if not rule.guard(bind):
                    continue
            except Exception:
                continue
            try:
                return rule.answer(bind)
            except Exception:
                return None
        return None
