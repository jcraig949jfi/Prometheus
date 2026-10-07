"""B08J -- the primitive ladder with the TIMING SHORTCUT removed (Phase 2-B Beta, instrument repair of B08)

B08b (2026-10-07): every evolved L1, L3 and L4 solver is a DELAY LINE (answer = the input from a fixed number of
ticks earlier); under 0-3 random NOISE ticks before each ask they collapse to .19-.38 while the hand slot solver
stays 1.0. Only L2 (write-once) produced genuine stored state (4/5 survive jitter at .83-.94). B08's ladder therefore
measured "is there a timing shortcut", not "is the memory primitive reachable".

Repair: every training AND held-out episode of every rung gets 0-3 NOISE ticks (independent draws) before each ask,
the B08b jitter. A delay line can no longer score; only state that persists across a variable gap can.
Same search as B08 (CMP3: N=200, E=16, E0, FOUNDRY_C2), fresh gen 0, G=300, 8 seeds per rung.

PREDICTION (before running): L1 >= 5/8 and L3 >= 5/8 (one register that persists is easy), L2 >= 3/8, L4 <= 2/8,
L5/L6 0/8. The reading that matters: whether L4 (TWO genuinely stored values) is reachable once timing cannot help.
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b08_primitive_ladder as B
from archaeon.beta.b08b_delay_line_check import jitter

OUT = Path(__file__).resolve().parent / "results"
_plain = B.eps_for


def jittered(rung, family, index, n):
    return jitter(_plain(rung, family, index, n), ("b08j", rung, family, index))


def cell(job):
    B.eps_for = jittered
    r = B.cell(job)
    r["jittered"] = True
    return r


def main(argv):
    OUT.mkdir(exist_ok=True)
    G_ = int(argv[0]) if argv else 300
    B.eps_for = jittered
    ctl = B.controls()
    print("controls (jittered)", json.dumps(ctl), flush=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 24) as ex:
        for f in as_completed([ex.submit(cell, {"rung": r, "seed": s, "G": G_}) for s in range(811, 819) for r in B.RUNGS]):
            r = f.result(); rows.append(r)
            print(json.dumps({k: r[k] for k in ("rung", "seed", "solved_gen", "final_heldout", "max_train", "wall_s")}), flush=True)
    summ = {r: {"solved": sum(x["rung"] == r and x["solved_gen"] is not None for x in rows),
                "gens": sorted(x["solved_gen"] for x in rows if x["rung"] == r and x["solved_gen"] is not None)} for r in B.RUNGS}
    print(json.dumps(summ), flush=True)
    (OUT / "B08J_result.json").write_text(json.dumps({"probe": "B08J", "G": G_, "controls": ctl, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
