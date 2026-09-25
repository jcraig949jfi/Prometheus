"""P-I07 [T-X12 x T-X21, anti-gravity]: PERSIST-CHANNEL KNOCKOUTS - world B evolution with the persist
policy locked to none / regs / tape / all, or inherited (no config mutation of the policy), 120
generations, 2 seeds each. Which channels allow the threshold to be crossed. Computational scope:
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
import ctxevo as CE            # noqa: E402
A, L = CM.A, CM.L

PID, TID = "P-I07", "T-X12"
LOCKS = ("none", "regs", "tape", "all", "inherit")


def job(j):
    r = CE.run_world("B", j["seed"], G=120, label="nestor.pi07|" + j["lock"], persist_lock=j["lock"])
    return {"lock": j["lock"], "seed": j["seed"], "top4_held": float(np.mean([t["held"] for t in r["tops"][:4]])), "best": r["tops"][0]["held"], "crossed": CE.crossed(r), "persist_final": r["persist_final"], "pw": r["pw_final"], "len": r["len_final"], "tops": r["tops"][:2]}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-X21"], "scope": CM.SCOPE, "claim_type": "anti-gravity", "world": "B", "locks": LOCKS, "G": 120, "seeds": (1, 2), "threshold": CE.THRESH["B"],
                         "reading": "channels that cross; LOOPHOLE if persist=none crosses (remembered context carried outside the documented state channels); CHANNEL_SEAT if a subset of channels crosses", "material_rule": "persist=none crosses, or the crossing set is a strict subset of the locks", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    with A.pool(8) as ex:
        runs = list(ex.map(job, [{"lock": k, "seed": s} for k in LOCKS for s in (1, 2)]))
    table = {k: {"top4_held": [round(r["top4_held"], 3) for r in runs if r["lock"] == k], "crossed": [r["crossed"] for r in runs if r["lock"] == k], "pw": [round(r["pw"], 0) for r in runs if r["lock"] == k], "persist_final": [r["persist_final"] for r in runs if r["lock"] == k]} for k in LOCKS}
    crosses = {k: any(v["crossed"]) for k, v in table.items()}
    reading = "LOOPHOLE_NONE_CROSSES" if crosses["none"] else ("CHANNEL_SEAT: " + ",".join(k for k, v in crosses.items() if v)) if any(crosses.values()) and not all(crosses.values()) else ("ALL_CROSS" if all(crosses.values()) else "NONE_CROSS")
    material = bool(crosses["none"] or (any(crosses.values()) and not all(crosses.values())))
    out = {"perturbation_id": PID, "parent": TID, "reading": reading, "table": table, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "tops.json").write_text(json.dumps([{"lock": r["lock"], "seed": r["seed"], "tops": r["tops"]} for r in runs], ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "persist-channel knockouts in world B: %s; %s" % (reading, {k: (v["top4_held"], v["crossed"]) for k, v in table.items()}), material, detail=table)
    L.append_evidence("T-X21", PID, "cross: which state channel carries remembered context: %s" % reading, material)
    print("DONE material=%s %s (%.0f s) %s" % (material, reading, time.time() - t0, {k: v["top4_held"] for k, v in table.items()}))


if __name__ == "__main__":
    main()
