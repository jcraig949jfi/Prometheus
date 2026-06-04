"""Landscape adapters. Each exposes:
    name: str
    available() -> bool
    seeds(rng, k) -> list[str]                       # namespaced node ids
    expand(node, rng, ruleset) -> list[(dst, op, null_p)]

Edges are operator-typed (the verb) with a null_p in [0,1] (high => a random
crawler would make this edge just as easily => cheap/generic).
"""
from __future__ import annotations


def build_landscapes() -> dict:
    """Instantiate every adapter that can reach its data. Returns name->adapter
    for the available ones only."""
    from agents.arachne.landscapes.mathlib import MathlibLandscape
    from agents.arachne.landscapes.lmfdb import LmfdbLandscape
    from agents.arachne.landscapes.algolib import AlgolibLandscape
    from agents.arachne.landscapes.oeis import OeisLandscape
    from agents.arachne.landscapes.pgtable import KnotsLandscape, GroupsLandscape

    out = {}
    for cls in (MathlibLandscape, LmfdbLandscape, AlgolibLandscape, OeisLandscape,
                KnotsLandscape, GroupsLandscape):
        try:
            inst = cls()
            if inst.available():
                out[inst.name] = inst
        except Exception:
            continue
    return out
