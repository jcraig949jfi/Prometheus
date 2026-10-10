"""E1b arms: the E1 organisms plus two controls named in REPORT_E1 s6.

  O3U   O3 with no byte cap: the ceiling, one variable away from O3 (E1's CEIL also
        dropped consolidation and inherited O0's keep-f bet; REPORT_E1 s3)
  O4LR  counterfeit provenance for O4L: at consolidation each pruned literal is
        recorded as a random literal from OUTSIDE the cell's anchor (never seen with
        the cell). Repair then runs O4L's rule on the wrong literal. Same entry count,
        so the same U bytes; tests whether O4L's gain needs the TRUE pruned literal.

Every E1 arm is chiasma.organisms.Organism unchanged.
"""
from typing import Optional

from ..organisms import Organism, make as make_e1
from ..world import bits


class E1bOrganism(Organism):
    ARMS = dict(Organism.ARMS,
                O3U=dict(neg="proj", consolidate=True, seams="none", uncapped=True),
                O4LR=dict(neg="proj", consolidate=True, seams="lazyrand"))

    def _maybe_consolidate(self, c) -> None:
        anchor = c.anchor
        was = c.consolidated
        super()._maybe_consolidate(c)
        if self.seams != "lazyrand" or was or not c.consolidated or anchor is None:
            return
        outside = [b for b in range(self.m) if not (anchor >> b) & 1]
        if outside:
            c.prov = [(1 << self.rng.choice(outside), j) for _l, j in c.prov]


E1B_ARMS = ["O1", "O2", "O3", "O0", "O4", "O4L", "O4LR", "O3U"]
UNCAPPED = {"O3U", "CEIL"}


def make(arm: str, m: int, cap: Optional[int], seed: int = 0):
    if arm in ("O3U", "O4LR"):
        return E1bOrganism(arm, m, cap, seed)
    return make_e1(arm, m, cap, seed)
