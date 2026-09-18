"""Campaign 0B generator: the Campaign 0 worlds under three pathologies (PREREG_C0B). TIER 2.

worlds.py is left byte-identical so Campaign 0 stays reproducible; this
module re-implements simulate() with the pathology hooks and nothing else
changed. The assay is imported unchanged elsewhere.
"""
from __future__ import annotations

import math
import random
from typing import Dict

from worlds import B0, CELLS, N_DEV, N_TASKS, N_VAULT, SD_E, SD_U, SD_V, World, _logistic

PATHOLOGIES = ("P1_heavy_tails", "P2_sign_changing_families", "P3_jackpot_lineages")
FAMILY_MULT = (4.0, 4.0 / 3.0, 0.0, -4.0 / 3.0)  # mean 1.0
JACKPOT_P, JACKPOT_X = 0.10, 10.0
NU = 2.5


def student_t(rng: random.Random, nu: float = NU) -> float:
    """Standard Student-t draw (scale 1)."""
    z = rng.gauss(0, 1)
    chi2 = rng.gammavariate(nu / 2.0, 2.0)
    return z / math.sqrt(chi2 / nu)


def simulate_0b(world: World, L: int, rng: random.Random, pathology: str) -> Dict:
    shift = world.shift()
    lineages = []
    for _ in range(L):
        if pathology == "P1_heavy_tails":
            v = SD_V * student_t(rng)
            h = world.sd_h * student_t(rng)
            z = world.null_sd * student_t(rng) if world.null_sd else 0.0
        else:
            v = rng.gauss(0, SD_V)
            h = rng.gauss(0, world.sd_h)
            z = rng.gauss(0, world.null_sd) if world.null_sd else 0.0
        lineage_mult = 1.0
        if pathology == "P3_jackpot_lineages":
            jackpot = rng.random() < JACKPOT_P
            lineage_mult = JACKPOT_X if jackpot else 0.0
            if world.null_sd:
                z = 1.0 if jackpot else -1.0 / 9.0
        fams = {"DEV": [rng.gauss(0, SD_U) for _ in range(N_DEV)],
                "VAULT": [rng.gauss(0, SD_U) for _ in range(N_VAULT)]}
        wf = {"DEV": [rng.gauss(0, world.sd_wf) for _ in range(N_DEV)],
              "VAULT": [rng.gauss(0, world.sd_wf) for _ in range(N_VAULT)]}
        fmult = {fs: [rng.choice(FAMILY_MULT) if pathology == "P2_sign_changing_families" else 1.0
                      for _ in range(n)] for fs, n in (("DEV", N_DEV), ("VAULT", N_VAULT))}
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
                    x += (mach_sum * (1 + h) * (1.0 if fs == "DEV" else world.tau)
                          * lineage_mult * fmult[fs][k]) + wf[fs][k]
                if z and i8_family:
                    x += z * fmult[fs][k]
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
