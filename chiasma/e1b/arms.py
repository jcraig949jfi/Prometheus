"""E1b arms: the E1 organisms plus two controls named in REPORT_E1 s6.

  O3U   O3 with no byte cap: the ceiling, one variable away from O3 (E1's CEIL also
        dropped consolidation and inherited O0's keep-f bet; REPORT_E1 s3)
  O4LR  counterfeit provenance for O4L: at consolidation each pruned literal is
        recorded as a random literal from OUTSIDE the cell's anchor (never seen with
        the cell). Repair then runs O4L's rule on the wrong literal. Same entry count,
        so the same U bytes; tests whether O4L's gain needs the TRUE pruned literal.

  O3W   O3 whose consolidated cells stay weldable: consolidation prunes the implied
        literals and keeps the pruned premise as the weld anchor (no extra bytes),
        instead of freezing the cell. One variable away from O3 (DEV_NOTES s3-s4).
  O4LW  O4L with the same change (provenance repair kept).
  The 2x2 is {O3, O4L, O3W, O4LW}: freeze {yes, no} x provenance repair {off, on}.

Binding budget (pevict=True, any arm; DEV_NOTES s6): E1's cap evicts N, then U, and
never P, so P can sit over the cap (over_budget). With pevict, after N and U are gone,
whole cells are evicted, the lowest support first, then the oldest, until the cap is
met. The rule is the same for every arm.

Every E1 arm is chiasma.organisms.Organism unchanged.
"""
from typing import Optional

from ..organisms import Cell, Organism, make as make_e1
from ..world import bits


class E1bOrganism(Organism):
    ARMS = dict(Organism.ARMS,
                O3U=dict(neg="proj", consolidate=True, seams="none", uncapped=True),
                O4LR=dict(neg="proj", consolidate=True, seams="lazyrand"),
                O3W=dict(neg="proj", consolidate=True, seams="none", weldable=True),
                O4LW=dict(neg="proj", consolidate=True, seams="lazy", weldable=True))

    def __init__(self, arm, m, cap, seed=0, pevict=False):
        super().__init__(arm, m, cap, seed)
        self.weldable = bool(self.ARMS[arm].get("weldable"))
        self.pevict = pevict
        self.events["p_evicted"] = 0

    def _enforce_cap(self) -> None:
        super()._enforce_cap()
        if not self.pevict or self.cap is None:
            return
        total = self.nbytes()["total"]
        while total > self.cap:
            victim, vname = None, None
            for name in sorted(self.cells):
                for c in self.cells[name]:
                    if victim is None or (c.support, c.born) < (victim.support, victim.born):
                        victim, vname = c, name
            if victim is None:
                break
            self.cells[vname].remove(victim)
            self.events["p_evicted"] += 1
            total = self.nbytes()["total"]

    def _maybe_consolidate(self, c) -> None:
        anchor = c.anchor
        was = c.consolidated
        super()._maybe_consolidate(c)
        if self.seams != "lazyrand" or was or not c.consolidated or anchor is None:
            return
        outside = [b for b in range(self.m) if not (anchor >> b) & 1]
        if outside:
            c.prov = [(1 << self.rng.choice(outside), j) for _l, j in c.prov]

    def _on_fn(self, name, x):
        if not self.weldable:
            return super()._on_fn(name, x)
        # As Organism._on_fn (no eager seams in the weldable arms), except that a
        # consolidated cell is welded too, using its pruned premise as the anchor.
        cells = self.cells[name]
        for c in sorted(cells, key=lambda c: (-c.support, c.born)):
            self.ops += 1
            anchor = c.premise if c.consolidated else c.anchor
            inter = anchor & x
            if inter and self._weld_ok(name, inter):
                c.premise = inter
                if not c.consolidated:
                    c.anchor = inter
                c.support += 1
                self.events["weld"] += 1
                self._maybe_consolidate(c)
                return
            self.events["weld_refused"] += 1
        cells.append(Cell(x, self.t))
        self.events["new_cell"] += 1


E1B_ARMS = ["O1", "O2", "O3", "O0", "O4", "O4L", "O4LR", "O3U", "O3W", "O4LW"]
UNCAPPED = {"O3U", "CEIL"}


def make(arm: str, m: int, cap: Optional[int], seed: int = 0, pevict: bool = False):
    if pevict or arm in ("O3U", "O4LR", "O3W", "O4LW"):
        return E1bOrganism(arm, m, cap, seed, pevict)
    return make_e1(arm, m, cap, seed)
