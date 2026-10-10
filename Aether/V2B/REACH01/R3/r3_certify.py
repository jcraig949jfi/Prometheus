"""REACH01 R3 certifier (run on COMBINE candidates only; outside the search loop). Two lattice batches per patch.

For a patch whose output table depends strictly on both inputs (COMBINE):
  REFERENCE  batch 1: the unmodified patch at tile positions 0..P-1 (P = patch cells). Arbitration is keyed to
             coordinates, so each position gets its own reference table.
  ABLATION   batch 2: variant i (cell i made inert: opcode 9, energy 0) at tile position i. Cell i is a-NECESSARY iff
             the reference at position i depends on a (some slice) and variant i does not; b likewise.
             Na, Nb = the a- and b-necessary cell sets. COMPOSE iff Na\\Nb and Nb\\Na are both non-empty: two causally
             necessary substructures, one per input path, meeting in a combination neither performs alone.
  AUTONOMY   the unmodified patch, with no archive and no search, keeps COMBINE at every reference position
             (position_combine_frac) AND under 2 other physics seeds at position 0. AUTONOMOUS iff
             position_combine_frac >= 0.9 and both seeds hold.
"""

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r3_frontier as F  # noqa: E402


def any_dep(out16, which):
    t = out16.reshape(4, 4)
    if which == "a":
        return any(len(set(t[:, j])) > 1 for j in range(4))
    return any(len(set(t[i, :])) > 1 for i in range(4))


def certify(patch, op="XOR", backend="gpu", side=32):
    ph, pw = patch.shape[1:]
    cells = [(y, x) for y in range(ph) for x in range(pw)]
    P = len(cells)
    ev = F.Evaluator(op, side=side, backend=backend)
    ref = ev.run_batch(np.stack([patch] * P))
    var = []
    for (y, x) in cells:
        q = patch.copy()
        q[:, y, x] = (9, 0, 0, 0, 0)
        var.append(q)
    vo = ev.run_batch(np.stack(var))
    na, nb = set(), set()
    for i, c in enumerate(cells):
        if any_dep(ref[i], "a") and not any_dep(vo[i], "a"):
            na.add(c)
        if any_dep(ref[i], "b") and not any_dep(vo[i], "b"):
            nb.add(c)
    pos_combine = float(np.mean([F.descriptor(r)[1] == 2 for r in ref]))
    seeds_ok = []
    for sd in (0xBEEF, 0xCAFE):
        ev2 = F.Evaluator(op, side=side, backend=backend, seed=sd)
        seeds_ok.append(F.descriptor(ev2.run_batch(np.stack([patch]))[0])[1] == 2)
    return {"Na": sorted(na), "Nb": sorted(nb), "a_only": len(na - nb), "b_only": len(nb - na), "shared": len(na & nb),
            "COMPOSE": bool(na - nb) and bool(nb - na), "position_combine_frac": pos_combine,
            "other_seeds_combine": seeds_ok, "AUTONOMOUS": pos_combine >= 0.9 and all(seeds_ok)}
