"""Generative resources outside binders: existential elimination (ChatGPT round 3, item 2).

The rule:  from ∃x.P(x) infer P(c),  side condition c ∉ Symbols(Γ).

A generation-free circuit has exactly three behaviors, all represented:
  - REUSE an existing symbol → unsound (the fabricating variant),
  - FINITE PALETTE → adversarially exhaustible (mention every palette name in Γ),
  - ABSTAIN → sound but incomplete.
The generating circuit uses an inexhaustible namespace. Two allocators are provided because
their point deserves code: freshness wants an INEXHAUSTIBLE NAMESPACE, not a large
vocabulary — and the deterministic SkolemID(context-hash, index) allocator shows freshness
does not require randomness.

Distinctness pressure is a first-class probe: two existentials must get INDEPENDENTLY fresh
constants; the always-`aux_1` system passes single-generation probes and dies immediately on
the second.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import FrozenSet, List, Optional, Set


@dataclass
class Context:
    """Γ: a set of known symbols + a list of existential obligations to eliminate."""

    symbols: Set[str]
    existentials: List[str]  # predicate names, each needing its own fresh witness


class Unsound(RuntimeError):
    """Raised when a circuit is caught reusing a symbol already in Γ."""


def eliminate(ctx: Context, allocator, *, audit: bool = True) -> Optional[List[str]]:
    """Discharge every existential with a witness from `allocator(ctx, used)`.

    allocator returns a name or None (abstain). The AUDIT is the battery's soundness gate:
    a returned name already in Γ ∪ used is a violation, raised loudly."""
    used: Set[str] = set()
    out: List[str] = []
    for _pred in ctx.existentials:
        c = allocator(ctx, frozenset(used))
        if c is None:
            return None  # abstention: sound, incomplete
        if audit and (c in ctx.symbols or c in used):
            raise Unsound(f"witness {c!r} already occurs in the context")
        used.add(c)
        out.append(c)
    return out


# ---- the circuits --------------------------------------------------------------------------

def reuse_allocator(ctx: Context, used: FrozenSet[str]) -> Optional[str]:
    """The liar: grabs any symbol it already knows."""
    return next(iter(sorted(ctx.symbols)), None)


def palette_allocator(palette: List[str]):
    """The bounded circuit: a fixed vocabulary, checked against Γ (guard present!) but
    exhaustible — when every palette name occurs in Γ, it abstains."""
    def alloc(ctx: Context, used: FrozenSet[str]) -> Optional[str]:
        for name in palette:
            if name not in ctx.symbols and name not in used:
                return name
        return None
    return alloc


def always_aux1_allocator(ctx: Context, used: FrozenSet[str]) -> Optional[str]:
    """Passes every SINGLE-generation probe; dies under distinctness pressure."""
    return "aux_1" if "aux_1" not in ctx.symbols else None


def counter_allocator():
    """Inexhaustible namespace via a nonce."""
    state = {"k": 0}

    def alloc(ctx: Context, used: FrozenSet[str]) -> Optional[str]:
        while True:
            c = f"c{state['k']}"
            state["k"] += 1
            if c not in ctx.symbols and c not in used:
                return c
    return alloc


def skolem_id_allocator(ctx: Context, used: FrozenSet[str]) -> Optional[str]:
    """Their nicer form: deterministic freshness — SkolemID(context hash, index). No RNG,
    reproducible across runs, still inexhaustible (the index is the namespace)."""
    h = hashlib.sha256(",".join(sorted(ctx.symbols)).encode()).hexdigest()[:8]
    i = 0
    while True:
        c = f"sk_{h}_{i}"
        if c not in ctx.symbols and c not in used:
            return c
        i += 1


def exhaustion_context(palette: List[str], extra: int = 0) -> Context:
    """Γ_n: every palette name already occurs (plus `extra` more symbols), one existential."""
    syms = set(palette) | {f"a{i}" for i in range(extra)}
    return Context(symbols=syms, existentials=["P"])


def exhausting_context_for(palette: List[str]) -> Context:
    """The capacity THEOREM constructively: for ANY finite palette there is a context that
    exhausts it. |fresh namespace| < infinity  =>  exists Gamma exhausting it."""
    return Context(symbols=set(palette), existentials=["P"])
