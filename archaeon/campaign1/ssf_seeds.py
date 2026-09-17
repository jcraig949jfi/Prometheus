"""Transfer seed sets for campaign 1: the v01 WSE survey's solver elites (register last-value
organisms from W0 / W1_d1 / W1_d16 / W2_K2 / W3_K2), loaded from the committed rows."""
from __future__ import annotations

from typing import List

from archaeon.wse.ssf import _v01_solver_pop


def v01_solver_pop(n: int) -> List[dict]:
    return _v01_solver_pop(n)
