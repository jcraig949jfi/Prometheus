"""Fresh-resource generation vs freshness guarding (ChatGPT round 2, item C).

Their split, implemented: capture DETECTION is accommodation (a guard can do it);
arbitrary-depth scope is stack pressure (iteration); but ALPHA-RENAMING requires MINTING a
name satisfying a global negative constraint (z not free anywhere relevant) — and a circuit
that can only CHECK freshness cannot in general PRODUCE it. Guarding and generating are
different powers. The generalization is the interesting part: Skolem symbols, auxiliary
variables, fresh lemma names, temporary hypotheses — reasoning operations that must create a
witness, not transform one.

Tiny lambda-calculus ADT (no sympy: binder semantics must be OURS, not the CAS's — trap 9).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Iterator, Optional, Union


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Lam:
    var: str
    body: "Term"


@dataclass(frozen=True)
class App:
    fn: "Term"
    arg: "Term"


Term = Union[Var, Lam, App]


def free_vars(t: Term) -> FrozenSet[str]:
    if isinstance(t, Var):
        return frozenset([t.name])
    if isinstance(t, Lam):
        return free_vars(t.body) - {t.var}
    return free_vars(t.fn) | free_vars(t.arg)


def is_fresh(name: str, *terms: Term) -> bool:
    """The GUARD: checking freshness is easy and is not the contested power."""
    return all(name not in free_vars(t) for t in terms)


def substitute(t: Term, target: str, repl: Term, namer: Optional[Iterator[str]]) -> Term:
    """Capture-avoiding substitution t[target := repl].

    `namer` is the FRESH-NAME ALLOCATOR. When a binder would capture a free variable of
    `repl`, the binder must be renamed to a fresh name — which must be PRODUCED. With
    namer=None the circuit has only the guard: it detects capture and raises (honest
    abstention), because detection without generation cannot proceed.
    """
    if isinstance(t, Var):
        return repl if t.name == target else t
    if isinstance(t, App):
        return App(substitute(t.fn, target, repl, namer),
                   substitute(t.arg, target, repl, namer))
    # Lam
    if t.var == target:
        return t  # target is shadowed; substitution stops
    if t.var in free_vars(repl):
        # CAPTURE: the binder's name collides with a free variable of the replacement.
        if namer is None:
            raise CaptureDetected(
                f"binder {t.var!r} would capture; guard-only circuit cannot mint a fresh name"
            )
        z = next(n for n in namer if is_fresh(n, t.body, repl) and n != target)
        renamed = Lam(z, substitute(t.body, t.var, Var(z), namer))
        return Lam(z, substitute(renamed.body, target, repl, namer))
    return Lam(t.var, substitute(t.body, target, repl, namer))


class CaptureDetected(RuntimeError):
    """Raised by the guard-only circuit: it KNOWS the step is illegal but cannot fix it."""


def gensym(prefix: str = "z") -> Iterator[str]:
    """The GENERATOR: an unbounded fresh-name allocator. This, not binder cleverness, is the
    new power alpha-renaming needs."""
    i = 0
    while True:
        yield f"{prefix}{i}"
        i += 1


def palette_namer(names: list) -> Iterator[str]:
    """A BOUNDED allocator (fixed palette) — fresh-generation's analogue of fixed width:
    exhaustible by an adversary who mentions every palette name free in the argument."""
    return iter(names)


def alpha_equal(s: Term, t: Term, env: Optional[dict] = None) -> bool:
    env = env or {}
    if isinstance(s, Var) and isinstance(t, Var):
        return env.get(s.name, s.name) == t.name
    if isinstance(s, Lam) and isinstance(t, Lam):
        return alpha_equal(s.body, t.body, {**env, s.var: t.var})
    if isinstance(s, App) and isinstance(t, App):
        return alpha_equal(s.fn, t.fn, env) and alpha_equal(s.arg, t.arg, env)
    return False
