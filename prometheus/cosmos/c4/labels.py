"""C4 v0.3 labels with an effect-size floor (R-STAT A15) and the per-family class-count rule (R-STAT A14).

A15. FUNCTIONAL in C3 is a significance call (P2 effect > 3 SE). It certifies J .262 against chance .25. v0.3 keeps
the certificate unchanged and adds a SIZE floor, fixed from first principles (not tuned on data): a world is USABLE
only if the actor's held-out accuracy exceeds chance by at least MIN_EXCESS of the attainable range,
    excess = (acc - 1/V) / (1 - 1/V) >= MIN_EXCESS = 0.10
(one tenth of the way from chance to perfect recall). Three-way label:
    USABLE    certificate FUNCTIONAL and excess >= MIN_EXCESS
    MARGINAL  certificate FUNCTIONAL and excess <  MIN_EXCESS   (detected, practically negligible)
    NOT       certificate PASSIVE or NONE
The accuracy is the certificate's own J_intact for A and the held-out accuracy for B.

A14. A family enters a per-family statistic only with >= MIN_PER_CLASS rows of each class in that sample. A family that
cannot meet it is EXCLUDED and COUNTED; S0 needs >= MIN_FAMILIES informative families or it reports NOT_REACHED.
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List

MIN_EXCESS = 0.10
MIN_PER_CLASS = 10
MIN_FAMILIES = 4


def excess(acc: float, V: int) -> float:
    return (acc - 1.0 / V) / (1.0 - 1.0 / V)


def three_way(cert_class: str, acc: float, V: int) -> str:
    if cert_class == "FUNCTIONAL":
        return "USABLE" if excess(acc, V) >= MIN_EXCESS else "MARGINAL"
    if cert_class in ("PASSIVE", "NONE"):
        return "NOT"
    return cert_class            # INDETERMINATE / INCOHERENT pass through, excluded and counted


def informative_families(families: List[str], y: List[int]) -> Dict:
    """A14: which families have >= MIN_PER_CLASS of each class."""
    c = Counter(zip(families, y))
    fams = sorted(set(families))
    ok = [f for f in fams if c[(f, 0)] >= MIN_PER_CLASS and c[(f, 1)] >= MIN_PER_CLASS]
    return {"informative": ok, "excluded": [f for f in fams if f not in ok],
            "counts": {f: {"0": c[(f, 0)], "1": c[(f, 1)]} for f in fams},
            "reached": len(ok) >= MIN_FAMILIES}
