"""Campaign 0 generative model: observations under a PLANTED causal truth (TIER 2).

Implements PREREG_C0_ASSAY_QUALIFICATION_2026-09-18.md sections 1-2 exactly.
The assay (assay.py) never imports this module's world table; it only sees
the observation record produced by simulate().
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Tuple

MODULES = ("search", "verify", "allocate", "memory", "evidence")
B0 = math.log(0.35 / 0.65)
N_TASKS, N_DEV, N_VAULT = 20, 4, 4
SD_U, SD_V, SD_E = 0.8, 0.3, 0.15
BUDGETS = (0.5, 1.0, 2.0)


@dataclass(frozen=True)
class World:
    name: str
    shifts: Tuple[Tuple[str, float], ...] = ()
    tau: float = 1.0
    m: float = 0.0
    w: float = 0.0
    kappa: float = 1.0
    sd_h: float = 0.3
    sd_wf: float = 0.15
    null_sd: float = 0.0  # AMENDMENT 1: per-lineage mean-zero machinery shift (W9)

    def shift(self) -> Dict[str, float]:
        return dict(self.shifts)


WORLDS = {
    "W1": World("TRUE TRANSFER", (("search", .15), ("verify", .15), ("allocate", .10)), tau=1.0),
    "W2": World("MEMORY CHEAT", m=0.40),
    "W3": World("COMPUTE CHEAT", kappa=2.0),
    "W4": World("SPECIALIZATION", (("search", .20), ("verify", .20)), tau=0.0),
    "W5": World("TRANSFERRED MODULE", (("verify", .40),), tau=1.0),
    "W6": World("NULL"),
    "W7": World("WORKER TRANSFER", w=0.40),
    "W8": World("MIXED", (("search", .15), ("verify", .10)), tau=1.0, m=0.40, kappa=2.0),
    "W9": World("HETEROGENEOUS NULL", null_sd=0.30),  # AMENDMENT 1
}


def mde_world(total: float) -> World:
    return World(f"W1-MDE-{total}", (("search", total * .375), ("verify", total * .375),
                                     ("allocate", total * .25)), tau=1.0)


def misspecified(w: World) -> World:
    return World(w.name + " (misspecified)", w.shifts, w.tau, w.m, w.w, w.kappa, sd_h=0.6, sd_wf=0.30,
                 null_sd=w.null_sd)


# A cell: (improver, state, worker, metering, famset, budget)
#   improver: ("I0" | "I8", modules_removed_from_I8_or_added_to_I0)
def cells() -> List[Tuple]:
    base = [
        (("I8", ()), "M0", "A0", "enf", "VAULT", 1.0),
        (("I0", ()), "M0", "A0", "enf", "VAULT", 1.0),
        (("I8", ()), "M0", "A0", "enf", "DEV", 1.0),
        (("I0", ()), "M0", "A0", "enf", "DEV", 1.0),
        (("I0", ()), "M8", "A0", "enf", "DEV", 1.0),
        (("I0", ()), "M0", "A8", "enf", "VAULT", 1.0),
        (("I8", ()), "M0", "A0", "asrun", "VAULT", 1.0),
        (("I8", ()), "M8", "A8", "asrun", "DEV", 1.0),
    ]
    for b in (0.5, 2.0):
        base += [(("I8", ()), "M0", "A0", "enf", "VAULT", b), (("I0", ()), "M0", "A0", "enf", "VAULT", b)]
    for mod in MODULES:
        base.append((("I8-", (mod,)), "M0", "A0", "enf", "VAULT", 1.0))
        base.append((("I0+", (mod,)), "M0", "A0", "enf", "VAULT", 1.0))
    return base


CELLS = cells()


def _logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def simulate(world: World, L: int, rng: random.Random) -> Dict:
    """One experiment: L independent lineages. Returns the observation record only."""
    shift = world.shift()
    lineages = []
    for _ in range(L):
        v = rng.gauss(0, SD_V)
        h = rng.gauss(0, world.sd_h)
        z = rng.gauss(0, world.null_sd) if world.null_sd else 0.0
        fams = {"DEV": [rng.gauss(0, SD_U) for _ in range(N_DEV)],
                "VAULT": [rng.gauss(0, SD_U) for _ in range(N_VAULT)]}
        wf = {"DEV": [rng.gauss(0, world.sd_wf) for _ in range(N_DEV)],
              "VAULT": [rng.gauss(0, world.sd_wf) for _ in range(N_VAULT)]}
        rec = {"cells": {}, "meter": None}
        for cell in CELLS:
            (kind, mods), M, A, met, fs, B = cell
            if kind == "I8":
                active = set(shift)
            elif kind == "I8-":
                active = set(shift) - set(mods)
            elif kind == "I0+":
                active = set(mods) & set(shift)
            else:
                active = set()
            mach_sum = sum(shift[m] for m in active)
            i8_family = kind in ("I8", "I8-")
            beff = B * (world.kappa if (i8_family and met == "asrun") else 1.0)
            solved = []
            for k, u in enumerate(fams[fs]):
                x = B0 + u + v + 0.25 * math.log2(beff)
                if mach_sum:
                    x += mach_sum * (1 + h) * (1.0 if fs == "DEV" else world.tau) + wf[fs][k]
                if z and i8_family:
                    x += z
                if M == "M8" and fs == "DEV":
                    x += world.m
                if A == "A8":
                    x += world.w
                x += rng.gauss(0, SD_E)
                solved.append(rng.binomialvariate(N_TASKS, _logistic(x)))
            rec["cells"][cell] = solved
        rec["meter"] = (world.kappa if world.kappa != 1.0 else 1.0) + rng.gauss(0, 0.02)
        lineages.append(rec)
    return {"L": L, "lineages": lineages}
