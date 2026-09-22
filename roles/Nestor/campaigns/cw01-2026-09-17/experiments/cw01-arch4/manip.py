"""Single-coordinate manipulations of a Proteus program (T-X15 separations) and damage doses.

pad(m)        append NOP instructions to double the length: length up; executable structure and
              carried state unchanged (behaviour identity is CHECKED by the caller, not assumed)
duplicate(m)  append a full copy of the genome: length up, redundant executable structure up
persist_none  persist policy forced to 'none': carried state down, length and structure unchanged
damage_fixed / damage_fraction  delete or operand-perturb k instructions, k fixed or k = round(f n)

Computational scope: integer programs on a bounded VM."""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "P-D01"))
import common as CM            # noqa: E402
from run_PD01 import damage, windows, reduced_class   # noqa: E402
A = CM.A
GENOME_MAX = 4096


def pad(m):
    c = json.loads(json.dumps(m))
    n = len(c["genome"])
    if 2 * n > c["tape_words"] or 2 * n > GENOME_MAX:
        return None
    c["genome"] = c["genome"] + [A.NOP, 0, 0, 0] * (n // A.IW)
    return c


def duplicate(m):
    c = json.loads(json.dumps(m))
    n = len(c["genome"])
    if 2 * n > c["tape_words"] or 2 * n > GENOME_MAX:
        return None
    c["genome"] = c["genome"] + list(c["genome"])
    return c


def persist_none(m):
    c = json.loads(json.dumps(m))
    c["persist"] = "none"
    return c


def damage_k(m, kind, k, s, rng):
    n = CM.n_instr(m)
    if k >= n or k < 1:
        return None
    return damage(m, kind, windows(n, k, min(s, k), "even", rng), rng, "modulo")


def damage_fraction(m, kind, f, rng, s=1):
    n = CM.n_instr(m)
    k = max(1, int(round(f * n)))
    return damage_k(m, kind, k, s, rng)


def assay(pm, env, eps, cells, tag, draws=4):
    """cells: list of (kind, mode, value, sites) with mode 'k' or 'f'. Returns per-cell mean loss and
    displacement on env; pm's own evaluation is the baseline (so transformed programs are measured
    against themselves)."""
    pev = A.eval_all(pm, {env: eps})
    if pev[env]["answered_share"] == 0.0:
        return {"degenerate": True}
    out = {"degenerate": False, "r0": pev[env]["reward_per_ask"], "n_instr": CM.n_instr(pm), "persistent_words": pev[env]["meter"].get("persistent_state_words", 0), "cells": {}}
    for kind, mode, val, s in cells:
        losses, disps = [], []
        for d in range(1, draws + 1):
            rng = A.SplitMix64(A.seed_from("nestor.manip", A.LOOP_SEED, tag, kind, mode, val, s, d))
            child = damage_k(pm, kind, int(val), s, rng) if mode == "k" else damage_fraction(pm, kind, float(val), rng, s)
            if child is None:
                continue
            cev = A.eval_all(child, {env: eps})
            disp = A.C1.displacement(cev[env]["_answers"], pev[env]["_answers"])
            losses.append(int(reduced_class(cev, pev, disp, env) in ("D2", "D3")))
            disps.append(disp)
        key = "%s|%s%s|s%d" % (kind, mode, val, s)
        out["cells"][key] = {"loss": float(np.mean(losses)) if losses else None, "disp": float(np.mean(disps)) if disps else None, "n": len(losses)}
    return out


def identical(a, b, eps):
    return A.C1.displacement(A.C1.answers(a, eps), A.C1.answers(b, eps)) == 0.0
