"""Fossil metabolism S7 -- the gated composition, frozen.

    GATED_V2W(s) = S6 A_v2w_0(s)   if 5 <= N(s) <= 18      (N = feasible targets of the evidence state s)
                 = G(s)            otherwise

Nothing here is new: the gate bounds are the S6 eligible endgame frozen from S5 evidence (S6_PREREG), the inside branch
is the S6 rung A_v2w_0 exactly as implemented (archaeon.producer.s6_endgame.produce_refined with statistic "v2w",
window 0.0), the outside branch is the S4 incumbent G exactly as implemented (archaeon.producer.s4_producers.produce_G).
The gate reads N from the exact block solver (FI.infer(fossils).feasible_targets): observable before the decision,
target-free, deterministic. It depends on how MANY targets are feasible, never on which one is hidden.

Provenance on every proposal: extra["gate"] = {"N": N, "active": bool, "branch": "v2w" | "G", "gate_units": the work
the gate itself cost (one exact inference), "candidate_version": CANDIDATE_VERSION}. The production integration, if
licensed, counts proposals by extra["gate"]["active"].

CANDIDATE_VERSION binds the three frozen sources: this file, s6_endgame.py (A_v2w_0) and s4_producers.py (G).
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, Sequence

from . import fossil_inference as FI
from . import s4_producers as P
from . import s6_endgame as S6
from .work_budget import WorkBudget

GATE_LOW = 5
GATE_HIGH = 18
STATISTIC = "v2w"
WINDOW = 0.0

_HERE = Path(__file__).parent
CANDIDATE_VERSION = hashlib.sha256(b"".join(( _HERE / n).read_bytes() for n in ("s7_gated.py", "s6_endgame.py", "s4_producers.py"))).hexdigest()[:16]


def gate(fossils: Sequence[FI.Fossil]) -> Dict[str, object]:
    """The gate: N and whether the refinement is admitted. Charged separately (nested budget) as gate overhead."""
    with WorkBudget(10 ** 12) as b:
        N = FI.infer(fossils).feasible_targets
    return {"N": N, "active": GATE_LOW <= N <= GATE_HIGH, "gate_units": b.units}


def produce_gated_v2w(fossils: Sequence[FI.Fossil], seed_inputs: Dict[str, object], max_units: int = 2_000_000):
    g = gate(fossils)
    if g["active"]:
        p = S6.produce_refined(fossils, seed_inputs, STATISTIC, WINDOW, max_units=max_units); g["branch"] = "v2w"
    else:
        p = P.produce_G(fossils, seed_inputs, max_units=max_units); g["branch"] = "G"
    p.producer_id = "GATED_V2W"
    p.extra["gate"] = dict(g, candidate_version=CANDIDATE_VERSION)
    return p
