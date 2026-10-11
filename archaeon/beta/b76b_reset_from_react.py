"""B76b -- CONTROL for B76: is the stepping stone the LATCH (write-once state) or just a compact competent start?

B76: from a LATCH gen 0, RESET-like genomes appear in 6/6 populations (from random gen 0, B75: 0/12). Here gen 0 is
100 x REACT_1 + 100 x REACT_2: the stateless forager, equally compact (13-14 instructions vs 15-16) and competent
(beats the best constant). Same world, search, seeds 7601-7606 and census as B76.
PREDICTION (committed before running), if the latch is the stepping stone: RESET-like in <= 2/6 populations.
If >= 5/6, the stepping stone is a compact competent start in general, and the latch is not specific.
"""
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from proteus.foundry import generate as G

import archaeon.beta.b76_reset_from_latch as B76
from archaeon.beta.b68_pulse_state_controls import man, react
import archaeon.beta.b75_reset_evolution as B75

OUT = Path(__file__).resolve().parent / "results" / "B76b_from_react"


def react_gen0():
    out = []
    for i in (1, 2):
        rec = G.organism_record(man(react(i), "none"), None, 0); rec["origins"] = ["gen0_react%d" % i]
        out += [copy.deepcopy(rec) for _ in range(100)]
    return out


def cell(job):
    B76.latch_gen0 = react_gen0; B76.OUT = OUT; return B76.cell(job)


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    refs = B75.refs_(); rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 6) as ex:
        futs = {ex.submit(cell, {"seed": 7601 + i, "G": int(argv[0]) if argv else 300, "refs": refs}): i for i in range(6)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                r = {"seed": 7601 + futs[f], "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B76b_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {"pops_with_reset_like": sum(r.get("reset_like_top10", 0) > 0 for r in rows)}
    print(json.dumps(summ))
    (OUT / "B76b_result.json").write_text(json.dumps({"probe": "B76b", "refs": refs, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
