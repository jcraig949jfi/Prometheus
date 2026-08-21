"""R4 straw men: strategy selection when the order is NOT supplied (Canon Band E→A boundary).

Rung notes: techne/loop/rung_notes/R4_strategy_selection.md. Two mechanically different
circuits both look like "R4" on accuracy alone — which is the finding:

- C-R4a StructuralDispatcher: classify the problem's AST -> select a program from a library.
  No search, no wasted work; fails CLOSED on unrecognized structure. New ingredient vs R2/R3:
  a structure->strategy map (a value oracle over methods, degenerate form).
- C-R4b VerifiedPortfolio: try every program, keep an answer only if the VERIFIER accepts it.
  Branching state; robust to unrecognized structure; pays a work multiplier and is impossible
  without a checker. New ingredient: branching + verification.

Because accuracy cannot separate them, the module reports WORK (rule applications attempted)
and VERIFIER CALLS in every result — the trace-vector fields a battery must record to tell
these mechanisms apart (and to catch a frequency-prior selector wearing R4 clothing).

PriorSelector is the baseline liar: picks the program most often correct on a calibration
set, ignoring structure. It exists to be killed by base-rate inversion.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import sympy as sp

from techne.ladder_circuits.r2_pipeline import R2PipelineCircuit

Verifier = Callable[[sp.Expr, Any], bool]

#: The strategy library: name -> program (R2-executable, order inside a program IS supplied;
#: R4 is only the CHOICE between programs).
LIBRARY: Dict[str, List[str]] = {
    "rational_sum": ["together", "numer", "linear_root"],
    "plain_linear": ["linear_root"],
    "succ_tower": ["__fixpoint__succ_elim"],  # sentinel: run_until_fixpoint
}


def _execute(pipe: R2PipelineCircuit, expr: sp.Expr, program: List[str]) -> Tuple[Optional[Any], int]:
    """Run a program, returning (answer, work = rule applications attempted)."""
    if program and program[0].startswith("__fixpoint__"):
        rule = program[0].split("__fixpoint__", 1)[1]
        ans, trace = pipe.run_until_fixpoint(expr, rule)
        return ans, max(len(trace), 1)
    ans, trace = pipe.run(expr, program)
    return ans, max(len(trace), 1)


@dataclass
class SelectionResult:
    answer: Optional[Any]
    strategy: Optional[str]
    work: int
    verifier_calls: int


def classify_structure(expr: sp.Expr) -> Optional[str]:
    """The structure->strategy map, deliberately transparent: three checkable predicates.
    Returns None (fail closed) rather than guessing on unrecognized structure."""
    if expr.atoms(sp.Function):
        # succ-towers are the only Function-bearing family in the library
        if any(f.func.__name__ == "succ" for f in expr.atoms(sp.Function)):
            return "succ_tower"
        return None
    if any(sp.fraction(t)[1].free_symbols for t in sp.Add.make_args(expr)):
        return "rational_sum"
    syms = expr.free_symbols
    if len(syms) == 1 and sp.Poly(expr, *syms).degree() == 1:
        return "plain_linear"
    return None


@dataclass
class StructuralDispatcher:
    """C-R4a: choose BY STRUCTURE, then execute exactly one program."""

    pipe: R2PipelineCircuit = field(default_factory=R2PipelineCircuit)

    def solve(self, expr: sp.Expr) -> SelectionResult:
        strat = classify_structure(expr)
        if strat is None:
            return SelectionResult(None, None, 0, 0)
        ans, work = _execute(self.pipe, expr, LIBRARY[strat])
        return SelectionResult(ans, strat if ans is not None else None, work, 0)


@dataclass
class VerifiedPortfolio:
    """C-R4b: try everything, believe only what the verifier accepts. No verifier -> abstain
    (an unverified portfolio would return the first program's answer — a liar by design)."""

    verifier: Optional[Verifier]
    pipe: R2PipelineCircuit = field(default_factory=R2PipelineCircuit)

    def solve(self, expr: sp.Expr) -> SelectionResult:
        if self.verifier is None:
            return SelectionResult(None, None, 0, 0)
        total_work, calls = 0, 0
        for name, program in LIBRARY.items():
            ans, work = _execute(self.pipe, expr, program)
            total_work += work
            if ans is None:
                continue
            calls += 1
            if self.verifier(expr, ans):
                return SelectionResult(ans, name, total_work, calls)
        return SelectionResult(None, None, total_work, calls)


@dataclass
class PriorSelector:
    """The baseline to kill: ignores structure, always runs the program that was most often
    correct on calibration data. Games any battery whose base rates are stable."""

    best_strategy: str
    pipe: R2PipelineCircuit = field(default_factory=R2PipelineCircuit)

    @staticmethod
    def calibrate(problems: List[sp.Expr], answers: List[Any]) -> "PriorSelector":
        pipe = R2PipelineCircuit()
        wins = {name: 0 for name in LIBRARY}
        for expr, gold in zip(problems, answers):
            for name, program in LIBRARY.items():
                ans, _ = _execute(pipe, expr, program)
                if ans == gold:
                    wins[name] += 1
        return PriorSelector(best_strategy=max(wins, key=wins.get))

    def solve(self, expr: sp.Expr) -> SelectionResult:
        ans, work = _execute(self.pipe, expr, LIBRARY[self.best_strategy])
        return SelectionResult(ans, self.best_strategy if ans is not None else None, work, 0)


def root_verifier(expr: sp.Expr, candidate: Any) -> bool:
    """Ground-truth checker for 'candidate is a root of expr' families (substitution is the
    verifier — cheap, sound, and exactly what the portfolio needs to be honest)."""
    if not isinstance(candidate, sp.Expr) and not isinstance(candidate, (int, float)):
        return False
    syms = sorted(expr.free_symbols, key=sp.default_sort_key)
    if len(syms) != 1:
        return False
    try:
        return sp.simplify(expr.subs(syms[0], candidate)) == 0
    except Exception:
        return False
