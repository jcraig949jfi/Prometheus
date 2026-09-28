"""Saturated-ruler guard (directive item 9; deep-block B7).

When two DISTINCT entities both sit at a ruler's maximum, the ruler cannot compare their mechanisms. Report
MECHANISM COMPARISON UNINFORMATIVE AT SATURATED RULER unless a secondary ruler still separates them. A shared maximum is never
evidence of shared mechanism.
"""
from __future__ import annotations

UNINFORMATIVE = "MECHANISM COMPARISON UNINFORMATIVE AT SATURATED RULER"


def compare(scores: dict, max_score: float, distinct: bool, secondary: dict = None, tol: float = 1e-9, sec_tol: float = 1e-9) -> dict:
    """scores: entity -> primary ruler score. distinct: the entities are materially distinct (different genomes / lineages)."""
    at_max = sorted(k for k, v in scores.items() if abs(v - max_score) <= tol)
    if len(set(scores.values())) > 1 and len(at_max) < 2:
        return {"verdict": "SEPARATED", "at_max": at_max}
    if len(at_max) < 2:                                                # equal but not at ceiling: an ordinary tie
        return {"verdict": "TIED_BELOW_CEILING", "at_max": at_max}
    if not distinct:
        return {"verdict": "SAME_ENTITY", "at_max": at_max}
    if secondary:
        vals = [secondary.get(k) for k in at_max]
        if None not in vals and max(vals) - min(vals) > sec_tol:
            return {"verdict": "SEPARATED_BY_SECONDARY", "at_max": at_max, "secondary": {k: secondary[k] for k in at_max}}
    return {"verdict": UNINFORMATIVE, "at_max": at_max,
            "note": "shared maximum score is not evidence of shared mechanism; add a non-saturating secondary ruler"}
