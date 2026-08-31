#!/usr/bin/env python
"""
HARMONIA A GEN-2b -- repaired ruler candidate under a fresh freeze.

R_VEC2 replaces the tie-ruled minority-support survival with a SYMMETRIC,
boundary-continuous survival: surv_sym = min(J(ones,ones'), J(zeros,zeros')).
Battery = the frozen Gen-2 cells (same streams, byte-identical) PLUS C13
boundary-crossing cells (the class that killed R_VEC, now first-class).
All five rulers classified on every cell. Gen-1 re-scored under R_VEC2.
"""

import json
import sys

import numpy as np

import bench2 as b2                     # frozen Gen-2 machinery, unchanged

DOM = b2.DOM
EPS_TRIV = b2.EPS_TRIV
LOCAL_BAND = b2.LOCAL_BAND


def jaccard(a, b):
    u = np.count_nonzero(a | b)
    return float(np.count_nonzero(a & b)) / u if u else 1.0


def surv_sym(f, g):
    return min(jaccard(f, g), jaccard(~f, ~g))


def r_vec2(f, g):
    if np.array_equal(f, g):
        return "NEUTRAL"
    if b2.minmass(g) <= EPS_TRIV:
        return "DESTRUCTION"
    d = b2.d_of(f, g)
    return "SMALL" if (d <= LOCAL_BAND and surv_sym(f, g) >= 0.5) else "LARGE"


RULERS5 = dict(b2.RULERS, R_VEC2=r_vec2)


def build_cells_2b():
    # identical Gen-2 cells (same seeds), reclassified under all 5 rulers
    cells = b2.build_cells()
    for c in cells:
        pass  # classes for the original 4 already present; add R_VEC2 below
    # rebuild classifications including R_VEC2 requires the raw pair; easiest:
    # regenerate with a hook -- instead, patch b2.RULERS and rebuild.
    b2.RULERS = RULERS5
    cells = b2.build_cells()            # same streams -> byte-identical cells
    # C13: guaranteed boundary-crossing flips (the R_VEC killer class)
    balanced, _, _, _ = b2.build_pools()
    rng = b2.rng_for(888, 1)
    extra = []
    for i, o in enumerate(balanced[:10]):
        ones = int(o["f"].sum())
        if ones > 512:                  # need mean <= 0.5 parent
            continue
        zeros_idx = np.flatnonzero(~o["f"])
        for k in (1, 4, 8):
            need = (512 - ones) + 1     # flips (0->1) forcing mean past 0.5
            kk = max(k, need)
            if kk > len(zeros_idx) or kk > 64:
                continue
            g = o["f"].copy()
            g[rng.choice(zeros_idx, size=kk, replace=False)] = True
            extra.append(dict(cell=f"C13_k{kk}_{i}",
                              type="boundary_crossing_flip", obj=o["id"],
                              parent_bal=round(o["bal"], 4),
                              mm_child=round(b2.minmass(g), 4),
                              d=round(b2.d_of(o["f"], g), 5),
                              surv=round(surv_sym(o["f"], g), 4),
                              required={"must_be": "SMALL",
                                        "axiom": "AX3/C13"},
                              classes={n: fn(o["f"], g)
                                       for n, fn in RULERS5.items()}))
    return cells + extra


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    cells = build_cells_2b()
    with open("results/cells_2b.jsonl", "w") as fh:
        for c in cells:
            fh.write(json.dumps(c) + "\n")
    n13 = sum(1 for c in cells if c["cell"].startswith("C13"))
    print(f"BATTERY 2b: {len(cells)} cells ({n13} boundary-crossing)")
    if mode == "cells":
        return
    # Gen-1 re-score under R_VEC2 (deterministic regeneration, as Gen-2)
    rows_out = []
    for line in open(b2.GEN1):
        o = json.loads(line)
        gates = [tuple(g) for g in o["gates"]]
        f = b2.eval_wires(gates)[-1].copy()
        edits = b2.circuit_edit_space(gates)
        rng = b2.rng_for(o["seed"], 102, o["level"], o["obj"])
        for k in range(128):
            e = edits[int(rng.integers(len(edits)))]
            g = b2.eval_wires(b2.apply_edit(gates, e))[-1]
            d = b2.d_of(f, g)
            old = ("NEUTRAL" if d == 0.0
                   else "SMALL" if d <= LOCAL_BAND else "LARGE")
            rows_out.append(dict(seed=o["seed"], level=o["level"],
                                 obj=o["obj"], edit=k, d=round(d, 5),
                                 old_band=old, new_class=r_vec2(f, g),
                                 mm_child=round(b2.minmass(g), 4),
                                 surv_sym=round(surv_sym(f, g), 4),
                                 ruler="R_VEC2_gen2b"))
    with open("results/gen1_rescored_v2.jsonl", "w") as fh:
        for r in rows_out:
            fh.write(json.dumps(r) + "\n")
    print(f"RESCORE v2: {len(rows_out)} rows")


if __name__ == "__main__":
    main()
