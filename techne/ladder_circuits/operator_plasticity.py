"""Operator plasticity — the proposed SIXTH coordinate (ChatGPT round 3, item 3).

Their argument, adopted as claim v6-candidate: coordinates 1-5 describe state MECHANICS of a
fixed transition algebra R = {r_1..r_m}. Bands S/G demand constructing NEW operators from
experience — R_t -> R_{t+1}: the machine modifies the language its later reasoning runs in.
(Independently, this is Prometheus's gen-30-wall doctrine: menus must GROW; and it is the
Hephaestus forge stated as a rung axis. External convergence noted — and per doctrine,
convergence is a warning to test, not proof. Hence the kill test, built here.)

Their brutal fake-synthesis kill, implemented: same low-level traces in training, but only a
REUSABLE subprogram survives held-out substitutions.

- TraceCache: memorizes concrete two-step trajectories a->?->c. Perfect on seen inputs,
  dead on unseen ones. (A cached macro without abstraction: "cached macros" rung of their
  plasticity scale, lower half.)
- OperatorSynthesizer: observes that the two-step pattern is f∘f, INSTALLS g := f∘f into
  its rule set, and applies g to inputs never seen in training. The vocabulary changed:
  len(rules) grows, and the new rule is INTENSIONAL (a composition), not a lookup table.

Plasticity scale (theirs): fixed -> composable -> macro-able -> inducible -> REVISABLE.

Cycle 009 additions from the restated round 3:
- SYMBOLIC held-out abstraction (stronger than held-out integers): train on 2a->2a+1,
  2b->2b+1, 2c->2c+1 and test on a novel SYMBOL z. A cache over ground terms cannot answer;
  a synthesized rule 2X -> 2X+1 is a pattern over an unbound variable and does.
- REVISABILITY (negative plasticity): mutate the environment so an installed macro becomes
  harmful. invent -> evaluate -> revise/delete. An add-only system provably degrades; the
  test measures that degradation rather than asserting it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

Rule = Callable[[int], int]


@dataclass
class TraceCache:
    """Memorizes endpoint pairs of observed two-step chunks. No abstraction anywhere."""

    table: Dict[int, int] = field(default_factory=dict)

    def observe_chunk(self, x: int, fx2: int) -> None:
        self.table[x] = fx2

    def answer_two_step(self, x: int) -> Optional[int]:
        return self.table.get(x)


@dataclass
class OperatorSynthesizer:
    """Starts with rules = {f}. From repeated two-step usage it INDUCES g = f∘f and installs
    it — the transition system itself changes. Held-out substitutions then come free."""

    f: Rule
    rules: Dict[str, Rule] = field(default_factory=dict)
    chunk_observations: int = 0
    install_threshold: int = 3

    def __post_init__(self) -> None:
        self.rules["f"] = self.f

    def observe_chunk(self, x: int, fx2: int) -> None:
        # audit the observation against its own primitive (no blind trust in traces),
        # then count it as evidence for the chunk's reusability
        if self.f(self.f(x)) == fx2:
            self.chunk_observations += 1
        if self.chunk_observations >= self.install_threshold and "g" not in self.rules:
            f = self.f
            self.rules["g"] = lambda v: f(f(v))  # the induced operator: intensional, total

    def answer_two_step(self, x: int) -> Optional[int]:
        g = self.rules.get("g")
        return g(x) if g is not None else None

    def vocabulary(self) -> List[str]:
        return sorted(self.rules)


# --------------------------------------------------------------------------- cycle 009

import sympy as _sp


@dataclass
class SymbolicRuleSynthesizer:
    """Induces a PATTERN over an unbound variable from ground instances: 2t -> 2t+1.

    The distinction from TraceCache is the object learned: a substitution rule (lhs/rhs with
    a free pattern variable) versus a table of ground pairs. Only the former applies to a
    symbol never seen."""

    pattern_var: _sp.Symbol = field(default_factory=lambda: _sp.Wild("t"))
    lhs: Optional[_sp.Expr] = None
    rhs: Optional[_sp.Expr] = None
    support: int = 0
    install_threshold: int = 3

    def observe(self, before: _sp.Expr, after: _sp.Expr) -> None:
        """Anti-unify the ground pair against the hypothesised shape (2t, 2t+1).

        NOTE (learned RED->GREEN): sympy's Wild SOLVES rather than matches — `(3*a).match(2*t)`
        succeeds with t = 3a/2. Structural anti-unification must therefore split the leading
        coefficient explicitly; a bare .match() would have installed a rule from evidence that
        does not support it, which is the fake-synthesis failure this module exists to catch."""
        coeff, rest = before.as_coeff_Mul()
        if coeff != 2:
            return
        if after != 2 * rest + 1:
            return
        self.support += 1
        if self.support >= self.install_threshold and self.lhs is None:
            t = self.pattern_var
            self.lhs, self.rhs = 2 * t, 2 * t + 1

    def apply(self, expr: _sp.Expr) -> Optional[_sp.Expr]:
        if self.lhs is None:
            return None
        m = expr.match(self.lhs)
        return None if m is None else self.rhs.subs(m)


@dataclass
class RevisableOperators:
    """invent -> evaluate -> revise/delete. Tracks each installed operator's live utility and
    RETRACTS it when the environment turns it harmful. `add_only=True` reproduces the
    degradation of a system that can install but never retract."""

    rules: Dict[str, Rule] = field(default_factory=dict)
    utility: Dict[str, int] = field(default_factory=dict)
    add_only: bool = False
    retract_threshold: int = -2
    retracted: List[str] = field(default_factory=list)

    def install(self, name: str, rule: Rule) -> None:
        self.rules[name] = rule
        self.utility[name] = 0

    def evaluate(self, name: str, helped: bool) -> None:
        """One outcome observation for an installed operator."""
        if name not in self.rules:
            return
        self.utility[name] += 1 if helped else -1
        if not self.add_only and self.utility[name] <= self.retract_threshold:
            del self.rules[name]
            self.retracted.append(name)

    def available(self) -> List[str]:
        return sorted(self.rules)


# --------------------------------------------------------------------------- cycle 010

@dataclass
class Domain:
    """A carrier plus its OWN realizations of the primitives. Same operator names, different
    code — this is what separates an abstraction from a cached macro."""

    name: str
    double: Rule
    succ: Rule


@dataclass
class CachedMacro:
    """Caches the macro as a CONCRETE FUNCTION captured from the training domain. Correct
    forever on that domain; silently WRONG on another whose primitives differ, because it
    kept the realization rather than the schema."""

    concrete: Optional[Rule] = None

    def learn(self, dom: "Domain") -> None:
        d, s = dom.double, dom.succ
        self.concrete = lambda x: s(d(x))

    def apply(self, dom: "Domain", x):
        return None if self.concrete is None else self.concrete(x)


@dataclass
class AbstractOperator:
    """Stores the SCHEMA — an ordered list of primitive NAMES — and instantiates it against
    whatever domain it is handed. Same higher-level operator, different internal realization.

    ChatGPT round 3 (restated): 'kill mere macro caching by changing the domain so the useful
    abstraction requires different internal realizations but the same higher-level operator.'
    """

    schema: Optional[Tuple[str, ...]] = None

    def learn(self, schema: Tuple[str, ...]) -> None:
        self.schema = schema

    def apply(self, dom: "Domain", x):
        if self.schema is None:
            return None
        prims = {"double": dom.double, "succ": dom.succ}
        for step in self.schema:
            x = prims[step](x)
        return x


@dataclass
class BudgetedSelector:
    """Round 4, item 2: add-only plasticity PROVABLY poisons selection.

    Construction: installed operators are considered BEFORE primitives, and only B candidates
    may be evaluated per task. Let stale macros accumulate (each was useful once, all now
    invalid). Once n_stale >= B, the useful primitive is never reached and accuracy -> 0.

    This settles the guard question: adding a guarded replacement while the unguarded macro
    REMAINS ACTIVE does not fix poisoning -- it is still selected first and still consumes
    budget. The real power is modifying the ACTIVE SET: R_next SUBSET R_now must be possible,
    not merely R_next SUPERSET R_now.
    """

    budget: int
    macros: List[Tuple[str, Rule]] = field(default_factory=list)
    primitive: Optional[Rule] = None
    can_retract: bool = False

    def install_macro(self, name: str, rule: Rule) -> None:
        self.macros.append((name, rule))

    def retract(self, name: str) -> bool:
        """Remove from the ACTIVE set. Only a system with negative plasticity can do this."""
        if not self.can_retract:
            return False
        before = len(self.macros)
        self.macros = [(n, r) for n, r in self.macros if n != name]
        return len(self.macros) != before

    def solve(self, x: int, gold: int) -> Tuple[bool, int]:
        """(solved, candidates_evaluated). Macros first, then the primitive, until budget."""
        evaluated = 0
        for _name, rule in self.macros:
            if evaluated >= self.budget:
                return False, evaluated
            evaluated += 1
            try:
                if rule(x) == gold:
                    return True, evaluated
            except Exception:
                pass
        if evaluated < self.budget and self.primitive is not None:
            evaluated += 1
            if self.primitive(x) == gold:
                return True, evaluated
        return False, evaluated
