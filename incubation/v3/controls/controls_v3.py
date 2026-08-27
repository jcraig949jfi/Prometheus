"""controls_v3.py — the control arms for Lens Genesis (harness side).

  R0  old representation + fixed forward baseline
  R1  old representation + one mined v1-style macro edge (v2 MacroAdapter)
  R2  old representation + the granted v2 operator (also R3's own downstream)
  F1  old representation + the derived slot-match value as an ordering feature
      (best-first); state identity and decomposition unchanged
  R4  omniscient: the true lens + the same downstream — harness-side only
"""
from __future__ import annotations

import heapq
import os
import sys

_V3 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for sub in ("representations",):
    p = os.path.join(_V3, sub)
    if p not in sys.path:
        sys.path.insert(0, p)

from lens import Meter, run_program                                  # noqa: E402

_V2 = os.path.join(os.path.dirname(_V3), "v2")
if _V2 not in sys.path:
    sys.path.insert(0, _V2)
from runtime import MacroAdapter                                     # noqa: E402

R0 = ("STAGE", (("A", "S"),), ("ONLY", 0), "GOAL")
R2OP = ("STAGE", (("A", "S"), ("Z", "P")), ("IF", "FSIZE", "LE", "FSIZE"), "MEET")


def mine_macro(words):
    """v1-style miner: top contiguous n-gram by support * (len-1)."""
    support = {}
    for idx, w in enumerate(words):
        for n in range(2, 5):
            for i in range(len(w) - n + 1):
                support.setdefault(tuple(w[i:i + n]), set()).add(idx)
    scored = sorted(((len(t) * (len(g) - 1), len(g), g)
                     for g, t in support.items() if len(t) >= 2),
                    key=lambda x: (-x[0], x[1], x[2]))
    return list(scored[0][2]) if scored else None


def run_r1(domain, task, macro, budget):
    if not macro:
        return run_program(domain, task, R0, budget)
    meter = Meter(budget)
    ad = MacroAdapter(domain, task, meter, macro)
    return run_program(domain, task, R0, budget, meter=meter, adapter=ad)


def run_f1(domain, task, budget):
    meter = Meter(budget)
    s = tuple(domain.decode(task["start"]))
    t = tuple(domain.decode(task["target"]))

    def mism(x):
        return sum(1 for a, b in zip(x, t) if a != b)
    cnt = 0
    heap = [(mism(s), 0, s)]
    seen = {s}
    while heap:
        if meter.ops > meter.budget:
            return {"solved": False, "ops": meter.ops, "budget_exhausted": True}
        _m, _c, u = heapq.heappop(heap)
        r = domain.succ(u)
        meter.charge(len(r))
        for _pid, v in r:
            if v == t:
                return {"solved": True, "ops": meter.ops,
                        "budget_exhausted": False}
            if v not in seen:
                seen.add(v)
                cnt += 1
                heapq.heappush(heap, (mism(v), cnt, v))
    return {"solved": False, "ops": meter.ops, "budget_exhausted": False}
