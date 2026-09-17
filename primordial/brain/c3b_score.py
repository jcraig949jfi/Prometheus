"""Score the C3b record run against its pre-run hypothesis (bus 1789391944739-0).

usage: python -m primordial.brain.c3b_score <record.jsonl>
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys

ROWS = pathlib.Path(__file__).resolve().parents[1] / "ledger" / "rows" / "C"
EXP_ID = "C3b-ecology-from-samples"
STRUCT = ("tt_rank2", "separable_decay", "program_out")


def main(argv):
    src = pathlib.Path(argv[0])
    rows = [json.loads(line) for line in open(src, encoding="utf-8")]
    win = {(r["seed"], r["target"], r["N"]): r for r in rows if r["kind"] == "winner"}
    pts = [r for r in rows if r["kind"] == "point"]
    seeds = sorted({k[0] for k in win})
    Ns = sorted({k[2] for k in win})

    h2 = [(s, N, win[(s, "program_in", N)]["rep"], win[(s, "program_in", N)]["heldout_rel_mse"]) for s in seeds for N in Ns]
    h2_held = all(rep == "program" and err is not None and err <= 1e-3 for _, _, rep, err in h2)
    h3 = [(s, t, N, win[(s, t, N)]["rep"]) for s in seeds for t in STRUCT + ("noise",) for N in Ns if N <= 512]
    h3_held = all(rep is None for *_, rep in h3)
    h5 = [(s, N, win[(s, "noise", N)]["rep"]) for s in seeds for N in Ns]
    h5_held = all(rep is None for *_, rep in h5)
    h1 = []
    for s in seeds:
        for t in STRUCT:
            learned = [N for N in Ns if win[(s, t, N)]["rep"] is not None]
            if not learned:
                h1.append({"seed": s, "target": t, "held": False, "note": "never learned"})
                continue
            first, last = win[(s, t, learned[0])], win[(s, t, Ns[-1])]
            h1.append({"seed": s, "target": t, "first_N": learned[0], "first": [first["rep"], first["bytes"]],
                       "last": [last["rep"], last["bytes"]],
                       "held": last["rep"] is not None and last["bytes"] > first["bytes"]})
    h1_held = all(x["held"] for x in h1)
    h4_dense_wins = [k for k, w in win.items() if w["rep"] == "dense"]
    probes = [r for r in pts if "probe" in r]
    leak = [r for r in probes if r["rep"] == "dense_leak"]
    honest = [r for r in probes if r["rep"] != "dense_leak"]
    controls = {"dense_leak_flagged": f"{sum(r['probe'] == 'LEAK' for r in leak)}/{len(leak)}",
                "honest_clean": f"{sum(r['probe'] == 'CLEAN' for r in honest)}/{len(honest)}"}
    controls_ok = all(r["probe"] == "LEAK" for r in leak) and all(r["probe"] == "CLEAN" for r in honest) and leak
    status = "KILL" if not (h2_held and h3_held) else ("PASS" if (h5_held and controls_ok) else "FAIL")
    table = {f"s{s}/{t}": {N: (win[(s, t, N)]["rep"], win[(s, t, N)]["bytes"], win[(s, t, N)]["heldout_rel_mse"])
                           for N in Ns} for s in seeds for t in ("tt_rank2", "separable_decay", "program_in", "program_out", "noise")}
    out = {"exp_id": EXP_ID, "source": src.name, "git": rows[0]["git"], "seeds": seeds, "Ns": Ns,
           "H2_program_in": {"held": h2_held, "cells": h2}, "H3_small_N": {"held": h3_held, "cells": h3},
           "H5_noise": {"held": h5_held}, "H1_growth": {"held": h1_held, "per": h1},
           "H4_dense_wins": {"held": not h4_dense_wins, "cells": h4_dense_wins},
           "controls": controls, "controls_ok": bool(controls_ok), "status_by_posted_rule": status,
           "winner_table": table}
    ROWS.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, ROWS / f"{EXP_ID}.jsonl")
    with open(ROWS / f"{EXP_ID}.summary.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    print(json.dumps({k: v for k, v in out.items() if k != "winner_table"}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
