"""P-I09 [T-ARCH4/W1 x T-X21, anti-gravity]: IS THE PREDICTIVE WORLD ESCAPED BY CUE-FOLLOWING? World C at cue
reliability p in {.55, .7, .9} (block 4) and block 8 (p .7), 120 generations, 2 seeds each; held-out
reward vs the cue-follow ceiling (p) and the tracker ceiling at each dose. Computational scope:
integer programs on a bounded VM.
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

PID, TID = "P-I09", "T-ARCH4/W1"
DOSES = [{"p_cue": 0.55, "block": 4}, {"p_cue": 0.7, "block": 4}, {"p_cue": 0.9, "block": 4}, {"p_cue": 0.7, "block": 8}]


def job(j):
    kw = dict(j["dose"])
    r = CE.run_world("C", j["seed"], G=120, label="nestor.pi09|p%.2f|b%d" % (kw["p_cue"], kw["block"]), **kw)
    sets = CE.held_sets("C", j["seed"], **kw)
    ceil = {k: float(np.mean([CW.ceilings(s, "C")[k] for s in sets])) for k in ("ignore_cue_best", "cue_follow", "tracker")}
    return {"dose": kw, "seed": j["seed"], "top4_held": float(np.mean([t["held"] for t in r["tops"][:4]])), "best": r["tops"][0]["held"], "ceilings": ceil, "pw": r["pw_final"], "tops": r["tops"][:2]}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-X21"], "scope": CM.SCOPE, "claim_type": "anti-gravity", "doses": DOSES, "G": 120, "seeds": (1, 2),
                         "reading": "TRACKS_CUE if |top4 held - cue_follow| <= .05 at every dose and top4 < tracker - .05; EXCEEDS_CUE if top4 >= cue_follow + .10 in >= 2 doses; BELOW_CUE if top4 < cue_follow - .10 in >= 2 doses; MIXED otherwise",
                         "material_rule": "the reading is not MIXED", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    with A.pool(8) as ex:
        runs = list(ex.map(job, [{"dose": d, "seed": s} for d in DOSES for s in (1, 2)]))
    table = {}
    for d in DOSES:
        rs = [r for r in runs if r["dose"] == d]
        table["p%.2f|b%d" % (d["p_cue"], d["block"])] = {"top4_held": float(np.mean([r["top4_held"] for r in rs])), "best": max(r["best"] for r in rs), "cue_follow": float(np.mean([r["ceilings"]["cue_follow"] for r in rs])), "tracker": float(np.mean([r["ceilings"]["tracker"] for r in rs])), "pw": float(np.mean([r["pw"] for r in rs]))}
    tracks = all(abs(v["top4_held"] - v["cue_follow"]) <= 0.05 and v["top4_held"] < v["tracker"] - 0.05 for v in table.values())
    exceeds = sum(1 for v in table.values() if v["top4_held"] >= v["cue_follow"] + 0.10) >= 2
    below = sum(1 for v in table.values() if v["top4_held"] < v["cue_follow"] - 0.10) >= 2
    reading = "TRACKS_CUE" if tracks else "EXCEEDS_CUE" if exceeds else "BELOW_CUE" if below else "MIXED"
    material = reading != "MIXED"
    out = {"perturbation_id": PID, "parent": TID, "reading": reading, "table": table, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "tops.json").write_text(json.dumps([{"dose": r["dose"], "seed": r["seed"], "tops": r["tops"]} for r in runs], ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "cue-reliability / block dose in world C: reading %s; %s" % (reading, {k: (round(v["top4_held"], 3), round(v["cue_follow"], 3), round(v["tracker"], 3)) for k, v in table.items()}), material, detail=table)
    L.append_evidence("T-X21", PID, "cross: world C reward vs cue-follow ceiling: %s" % reading, material)
    print("DONE material=%s %s (%.0f s) %s" % (material, reading, time.time() - t0, {k: (round(v["top4_held"], 3), round(v["cue_follow"], 2), round(v["tracker"], 2)) for k, v in table.items()}))


if __name__ == "__main__":
    main()
