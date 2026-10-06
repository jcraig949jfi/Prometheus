"""B02 -- shelf -> summit: valley, plateau, or ramp? (Phase 2-B Beta)

B01-A showed a 20-instruction W2_K2 solver exists. This probe walks ONE explicit chain of single-instruction
edits (each a legal grammar-v0.4 replacement/insertion of one 4-word instruction) from the one-slot shelf program
to the solver and scores every intermediate on held-out episodes (48 x 5 seeds). It then estimates, for each
step, how often grammar v0.4 proposes THAT exact edit from the step's parent (20,000 sampled children per step).

PREDICTION (written before running): every intermediate scores within .05 of the shelf (a neutral plateau) and
only the last edit jumps to 1.0; the per-step proposal probability of the exact edit is < 1e-3, so the expected
waiting time on the plateau, not a valley, explains 0/60.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from proteus.foundry import generate as G
from proteus.foundry.lineage import descend

from archaeon.beta.b01_w2k2_existence import (EQ, HALT, IN, JNZ, JZ, LDC, MOV, NOP, OUT_, SOLVER, _prog, heldout,
                                              manifest)

OUT = Path(__file__).resolve().parent / "results"

def ladder():
    """Steps as complete programs, with the ASK block at a fixed tail so jump offsets stay simple."""
    progs = []
    # common head: kind test jumps to ASK block at index A
    def build(put, ask):
        a = 4 + len(put)
        return [(IN, 1, 0), (LDC, 2, 1), (EQ, 3, 1, 2), (JZ, 3, a - 3)] + put + ask
    # S0 shelf
    progs.append(("S0 shelf: store last value", build([(IN, 4, 0), (IN, 7, 0), (HALT,)], [(OUT_, 7, 0), (HALT,)])))
    # S1 also store last tag in r6 (neutral)
    progs.append(("S1 +tag->r6", build([(IN, 4, 0), (IN, 7, 0), (MOV, 6, 4), (HALT,)], [(OUT_, 7, 0), (HALT,)])))
    # S2 ASK reads the asked tag (neutral)
    progs.append(("S2 ASK reads tag", build([(IN, 4, 0), (IN, 7, 0), (MOV, 6, 4), (HALT,)],
                                           [(IN, 4, 0), (OUT_, 7, 0), (HALT,)])))
    # S3 PUT: remember the PREVIOUS slot in (r8,r9) before overwriting: MOV r9,r7 (neutral)
    progs.append(("S3 +MOV r9,r7 before store", build([(IN, 4, 0), (MOV, 9, 7), (IN, 7, 0), (MOV, 6, 4), (HALT,)],
                                                      [(IN, 4, 0), (OUT_, 7, 0), (HALT,)])))
    # S4 dead alternative output OUT r9 after the HALT (neutral)
    progs.append(("S4 +dead OUT r9", build([(IN, 4, 0), (MOV, 9, 7), (IN, 7, 0), (MOV, 6, 4), (HALT,)],
                                          [(IN, 4, 0), (OUT_, 7, 0), (HALT,), (OUT_, 9, 0), (HALT,)])))
    # S5 compare asked tag with last tag (neutral: result unused)
    progs.append(("S5 +EQ r3,r4,r6", build([(IN, 4, 0), (MOV, 9, 7), (IN, 7, 0), (MOV, 6, 4), (HALT,)],
                                          [(IN, 4, 0), (EQ, 3, 4, 6), (OUT_, 7, 0), (HALT,), (OUT_, 9, 0), (HALT,)])))
    # S6 branch: tag != last -> out r9 (the summit edit)
    progs.append(("S6 +JZ r3,+3 (summit)", build([(IN, 4, 0), (MOV, 9, 7), (IN, 7, 0), (MOV, 6, 4), (HALT,)],
                                                [(IN, 4, 0), (EQ, 3, 4, 6), (JZ, 3, 3), (OUT_, 7, 0), (HALT,),
                                                 (OUT_, 9, 0), (HALT,)])))
    return progs


def proposal_rate(parent_prog, child_prog, n=20000):
    parent = G.organism_record(manifest(_prog(parent_prog)), None, 0)
    target = _prog(child_prog)
    hit = 0
    for s in range(n):
        child, _ = descend(parent, 7_000_000 + s)
        if child["manifest"]["genome"] == target:
            hit += 1
    return hit / n


def main(argv):
    OUT.mkdir(exist_ok=True)
    progs = ladder()
    rows = []
    for i, (label, p) in enumerate(progs):
        m = manifest(_prog(p))
        hos = [round(heldout(m, seed=s)["reward"], 4) for s in range(5)]
        row = {"step": label, "n_instr": len(p), "heldout_5": hos, "mean": round(sum(hos) / 5, 4)}
        if i > 0:
            row["proposal_rate_from_prev"] = proposal_rate(progs[i - 1][1], p)
        rows.append(row)
        print(json.dumps(row), flush=True)
    last = progs[-1][1]
    rows.append({"check": "final step equals a full solver", "equals_B01_solver": _prog(last) == SOLVER})
    (OUT / "B02_result.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
