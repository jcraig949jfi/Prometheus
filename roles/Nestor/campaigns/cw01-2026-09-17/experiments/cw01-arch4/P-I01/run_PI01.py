"""P-I01 [T-X21, deformation W]: CONTEXT WORLDS A / B / C - the regime changes the correct answer.
Formal ceilings of invariant policies on 200 episode sets are written to PREREG before execution.
Evolution: 3 seeds per world, 120 generations; controls: B-destroyed and C-destroyed evolved (2 seeds);
B tops evaluated on shuffled / no-cue / destroyed controls. Thresholds A .90, B .80, C .80 on held-out
sets. Tops saved with genomes. Computational scope: integer programs on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import ctxworlds as CW         # noqa: E402
import ctxevo as CE            # noqa: E402
A, L = CM.A, CM.L

PID, TID = "P-I01", "T-X21"
SEEDS, G = (1, 2, 3), 120


def formal_ceilings():
    out = {}
    for w in "ABC":
        keys = ("ignore_cue_best", "cue_follow", "oracle") + (("tracker",) if w == "C" else ())
        acc = {k: [] for k in keys}
        for i in range(200):
            c = CW.ceilings(CW.make(w, 7, i), w)
            for k in keys:
                acc[k].append(c[k])
        out[w] = {k: {"mean": float(np.mean(v)), "p95": float(np.percentile(v, 95))} for k, v in acc.items()}
        out[w]["threshold"] = CE.THRESH[w]
        out[w]["invariant_cannot_reach_threshold"] = bool(out[w]["ignore_cue_best"]["p95"] < CE.THRESH[w] and (w == "A" or out[w]["cue_follow"]["p95"] < CE.THRESH[w]))
    return out


def job(j):
    return CE.run_world(j["world"], j["seed"], G=G, control=j.get("control"), label="nestor.pi01")


def main():
    t0 = time.time()
    ceil = formal_ceilings()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "W", "scope": CM.SCOPE, "claim_type": "world-construction",
                         "worlds": {"A": "observable regime word in the ask tick", "B": "cue tick, then PUT, then bare ASK", "C": "lifetime of 16 trials, block 4, cue reliability .7"},
                         "formal_ceilings_200_sets": ceil, "no_privileged_signal": "no phase variable, mode bit, clock or memory operation; the cue is an ordinary input word",
                         "evolution": {"N": 96, "G": G, "tournament": 3, "births": "mutation only", "seeds": SEEDS, "episodes": "fresh every generation"},
                         "controls": {"evolved": ["B destroyed cue (2 seeds)", "C destroyed cue (2 seeds)"], "evaluated_on_B_tops": ["shuffled history", "no cue", "destroyed cue"]},
                         "held_out": "4 fresh sets (indices 10000+); a world is CROSSED if the mean held-out reward of the top-4 is >= threshold in >= 2/3 seeds; a control that crosses is a LOOPHOLE (world invalid)",
                         "material_rule": "always material: the crossing table is the result", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    jobs = [{"world": w, "seed": s} for w in "ABC" for s in SEEDS] + [{"world": w, "seed": s, "control": "destroyed"} for w in "BC" for s in (1, 2)]
    with A.pool(8) as ex:
        runs = list(ex.map(job, jobs))
    table = {}
    for r in runs:
        key = "%s|%s|s%d" % (r["world"], r["control"] or "plain", r["seed"])
        table[key] = {"top4_held": float(np.mean([t["held"] for t in r["tops"][:4]])), "best_held": r["tops"][0]["held"], "pop_held": r["pop_held_mean"], "train_final": r["history"][-1], "len": r["len_final"], "pw": r["pw_final"], "persist": r["persist_final"], "crossed": CE.crossed(r)}
    # B controls on B tops
    ctl = {}
    for r in runs:
        if r["world"] == "B" and r["control"] is None:
            for c in ("shuffled", "nocue", "destroyed"):
                sets = CE.held_sets("B", r["seed"], control=c)
                ctl["B|s%d|%s" % (r["seed"], c)] = float(np.mean([CE.held_reward(t["m"], sets) for t in r["tops"][:4]]))
    crossing = {w: sum(1 for r in runs if r["world"] == w and r["control"] is None and CE.crossed(r)) for w in "ABC"}
    loophole = {w: any(CE.crossed(r, w) for r in runs if r["world"] == w and r["control"] == "destroyed") for w in "BC"}
    disposition = {w: ("LOOPHOLE" if loophole.get(w) else "CROSSED" if crossing[w] >= 2 else "PARTIAL" if crossing[w] == 1 else "NOT_CROSSED") for w in "ABC"}
    out = {"perturbation_id": PID, "parent": TID, "ceilings": ceil, "thresholds": CE.THRESH, "table": table, "B_controls_on_tops": ctl, "crossing_seeds": crossing, "loophole": loophole, "disposition": disposition,
           "material": True, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "tops.json").write_text(json.dumps([{k: v for k, v in r.items() if k != "history"} for r in runs], ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "context worlds: disposition %s; top-4 held-out %s; B tops under controls %s; ceilings (mean) %s"
                      % (disposition, {k: round(v["top4_held"], 3) for k, v in table.items()}, {k: round(v, 3) for k, v in ctl.items()}, {w: {k: round(v["mean"], 3) for k, v in c.items() if isinstance(v, dict)} for w, c in ceil.items()}), True, detail={"disposition": disposition, "table": table, "controls": ctl})
    print("DONE %s (%.0f s) %s | controls %s" % (disposition, time.time() - t0, {k: round(v["top4_held"], 3) for k, v in table.items()}, {k: round(v, 3) for k, v in ctl.items()}))


if __name__ == "__main__":
    main()
