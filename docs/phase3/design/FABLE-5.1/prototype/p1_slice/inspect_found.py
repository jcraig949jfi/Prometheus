"""EXPLORATORY follow-up to reach.py. Not preregistered. Written after RECEIPT_reach.json existed.

reach.py showed that some lineages recovered a builder under the neutral and
strict acceptance rules, including one that started from an EMPTY program.
reach.py did not save the programs. The search is deterministic, so this script
replays the cells that had recoveries, prints what was found, and puts each
found organism through the same rulers the designed ones went through:

  BUILD class exclusion on sealed lives, interchange (does behaviour follow a
  swapped store?), lesion, reset equivalence, and whether it uses the designed
  mechanism (phase dispatch) or something else.

Everything here is a C0 observation in the design's terms: one substrate, one
world, one search seed, looked at after the fact.

    python inspect_found.py        # writes RECEIPT_found_exploratory.json
"""
import json
import pathlib
import sys
from datetime import datetime, timezone

import numpy as np

import organisms as org
import reach
import rulers as ru
import wm_mini as wm

HERE = pathlib.Path(__file__).resolve().parent
CELLS = [("neutral", 1, 8), ("neutral", 1, 3), ("neutral", 1, 1), ("strict", 2, 2), ("strict", 2, 1)]
BASE = ru.SEALED_BASE + 8_000_000        # sealed lives no other script has read


def main():
    P = ru.Params()
    target = org.builder_min()
    n = target.shape[0]
    st = org.empty_store(P.S)
    args = (P.K, P.R, P.E, P.T, P.F, P.cap, 0, reach.N_TRAIN)
    found = []
    for regime, regime_id, d in CELLS:
        evals, fit, progs = reach.search_cell(target, n, d, st, P.seed, reach.LINEAGES, reach.BUDGET, regime_id, *args)
        for j in range(reach.LINEAGES):
            if evals[j] < 0:
                continue
            sel, verdict, acc = reach.confirm(progs[j], P)
            if not (sel and verdict == ru.PASS):
                continue
            prog = progs[j].copy()
            ops = [wm.OPNAMES[int(w[0]) % wm.NOPS] for w in prog]
            same_as_designed = bool(np.array_equal(prog, target))
            uses_phase = "PH" in ops
            c = ru.evaluate(prog, st, P, BASE, 600)["counts"]
            build = ru.class_exclusion(int(c[wm.T_PROBE, 0]), int(c[wm.T_PROBE, 1]), P.R)
            novel = ru.novel_sanity(int(c[wm.T_NOVEL, 0]), int(c[wm.T_NOVEL, 1]), P.R)
            pairs = [(BASE + 100_000 + 2 * i, BASE + 100_001 + 2 * i) for i in range(500)]
            inter = ru.interchange(prog, st, P, pairs, 4)
            sham = ru.interchange(prog, st, P, pairs, 4, sham=True)
            les = ru.lesion(prog, st, P, range(BASE + 200_000, BASE + 201_000), 4, range(0, P.S))
            rst = ru.reset_equivalence(prog, st, P, range(BASE + 300_000, BASE + 300_100), 4)
            row = {
                "regime": regime, "d": d, "lineage": j, "evaluations_to_perfect_training_score": int(evals[j]),
                "program": [[int(v) for v in w] for w in prog], "listing": org.listing(prog),
                "identical_to_designed_builder": same_as_designed, "uses_phase_instruction": uses_phase,
                "sealed_probe_accuracy": int(c[wm.T_PROBE, 1]) / int(c[wm.T_PROBE, 0]),
                "build": build, "novel": novel,
                "interchange": inter, "interchange_sham": sham, "lesion_whole_store": les, "reset_equivalence": rst,
            }
            found.append(row)
            print("=== %s rule, d=%d, lineage %d, after %d proposals ===" % (regime, d, j, evals[j]))
            print(org.listing(prog))
            print("identical to the designed builder: %s; uses PH: %s" % (same_as_designed, uses_phase))
            print("sealed BUILD: %s (%d/%d = %.4f, certified >= %.3f); novel-trial check %s" % (
                build["verdict"], build["fired"], build["eligible"], row["sealed_probe_accuracy"],
                build.get("lower_bound", 0.0), novel["verdict"]))
            print("interchange: %s (%d of %d followed the donor); sham: %s (%d of %d)" % (
                inter["label"], inter["followed_donor"], inter["eligible"],
                sham["label"], sham["followed_donor"], sham["eligible"]))
            print("lesion of the whole store: still above bound %s (%d of %d); reset equivalence %s (%d mismatches of %d)" % (
                les["verdict"], les["fired"], les["eligible"], rst["verdict"], rst["fired"], rst["eligible"]))
    receipt = {
        "what": "EXPLORATORY inspection of organisms found by reach.py (not preregistered)",
        "written_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "claim_level": "C0", "params": P.as_dict(), "cells_replayed": CELLS, "found": found,
    }
    (HERE / "RECEIPT_found_exploratory.json").write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n",
                                                         encoding="utf-8", newline="\n")
    print("found organisms inspected: %d" % len(found))
    return 0


if __name__ == "__main__":
    sys.exit(main())
