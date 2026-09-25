"""P-I06 [T-ARCH5 x T-X21, serendipity]: GRAMMAR-B EVOLUTION in world B (remembered regime), 120 generations,
2 seeds; held-out reward vs threshold and vs grammar v0.4; tops' geometry census. Computational scope:
integer programs on a bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from collections import Counter

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import manifold as MF          # noqa: E402
import ctxevo as CE            # noqa: E402
A, L = CM.A, CM.L
try:
    from archaeon.campaign5.repb import grammar_b as GB
    GB_OK = True
except Exception:      # noqa: BLE001
    GB, GB_OK = None, False

PID, TID = "P-I06", "T-ARCH5"


def mutator(m, rng):
    return GB.mutate_b(m, rng, None, None)


def job(j):
    r = CE.run_world("B", j["seed"], G=120, label="nestor.pi06", mutator=mutator)
    shapes = Counter()
    for t in r["tops"][:8]:
        v = MF.curve(t["m"])[0]
        shapes["silent" if not all(x == x for x in v) else ("NEW" if MF.nearest(v)[1] > 0.3 else MF.SHAPE[MF.nearest(v)[0]])] += 1
    return {"seed": j["seed"], "top4_held": float(np.mean([t["held"] for t in r["tops"][:4]])), "best": r["tops"][0]["held"], "crossed": CE.crossed(r), "shapes": dict(shapes), "len": r["len_final"], "pw": r["pw_final"], "tops": r["tops"][:4]}


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "co_parents": ["T-X21"], "scope": CM.SCOPE, "claim_type": "serendipity-representation", "grammar_b_available": GB_OK, "world": "B", "G": 120, "seeds": (1, 2), "threshold": CE.THRESH["B"],
                         "readouts": "held-out reward, crossing, tops' shapes, vs P-I01's grammar-v0.4 B runs", "material_rule": "grammar B crosses B, or its crossing differs from v0.4's", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    if not GB_OK:
        out = {"perturbation_id": PID, "parent": TID, "reading": "NOT_RUNNABLE", "material": False, "elapsed_s": 0.0}
        L.result(HERE, out, ph)
        L.append_evidence(TID, PID, "grammar B not importable: NOT_RUNNABLE", False)
        return
    with A.pool(2) as ex:
        runs = list(ex.map(job, [{"seed": s} for s in (1, 2)]))
    p1 = HERE.parent / "P-I01" / "RESULT.json"
    v04 = None
    if p1.exists():
        t = json.loads(p1.read_text(encoding="utf-8"))["table"]
        v04 = {k: v["top4_held"] for k, v in t.items() if k.startswith("B|plain")}
    material = bool(any(r["crossed"] for r in runs) or (v04 and (any(r["crossed"] for r in runs) != any(v >= CE.THRESH["B"] for v in v04.values()))))
    out = {"perturbation_id": PID, "parent": TID, "runs": [{k: v for k, v in r.items() if k != "tops"} for r in runs], "v04_B_top4_held": v04, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "tops.json").write_text(json.dumps([{"seed": r["seed"], "tops": r["tops"]} for r in runs], ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "grammar B in world B: %s; v0.4 B runs %s" % ([(r["seed"], round(r["top4_held"], 3), r["crossed"], r["shapes"]) for r in runs], v04), material, detail={"runs": out["runs"]})
    L.append_evidence("T-X21", PID, "cross: grammar-B crossing of world B %s" % [r["crossed"] for r in runs], material)
    print("DONE material=%s (%.0f s) %s" % (material, time.time() - t0, [(r["seed"], round(r["top4_held"], 3), r["crossed"]) for r in runs]))


if __name__ == "__main__":
    main()
