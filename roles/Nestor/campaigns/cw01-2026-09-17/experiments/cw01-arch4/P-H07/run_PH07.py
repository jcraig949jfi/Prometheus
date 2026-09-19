"""P-H07 [T-X12, anti-gravity]: ARE THE GEOMETRIES RESOURCE ARTEFACTS? Representatives of every geometry
re-read with tick_budget halved / doubled and tape_words halved / doubled (within bounds), behaviour
identity on the base episodes recorded; curve distance and reward change per knob. Computational scope:
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
import manifold as MF          # noqa: E402
A, L = CM.A, CM.L

PID, TID = "P-H07", "T-X12"
SHAPES = {0: "start_anchored", 4: "periodic", 5: "ask_time", 1: "schedule", 3: "immune"}
KNOBS = ("tick_budget_x0.5", "tick_budget_x2", "tape_words_x0.5", "tape_words_x2")


def knob(m, k):
    c = json.loads(json.dumps(m))
    if k.startswith("tick_budget"):
        v = c["tick_budget"] * (0.5 if k.endswith("0.5") else 2)
        c["tick_budget"] = int(min(65536, max(8, v)))
    else:
        v = c["tape_words"] * (0.5 if k.endswith("0.5") else 2)
        v = int(min(4096, max(16, v)))
        v = (v // 4) * 4
        if v < len(c["genome"]):
            return None
        c["tape_words"] = v
    return c


def job(j):
    m = A.canonical(j["manifest"])
    eps = A.episodes(j["env"])
    v0 = MF.curve(m)[0]
    a0 = A.C1.answers(m, eps)
    r0 = A.evaluate(m, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
    out = {"pid": j["pid"], "shape": j["shape"], "knobs": {}}
    for k in KNOBS:
        c = knob(m, k)
        if c is None:
            out["knobs"][k] = {"feasible": False}
            continue
        try:
            v = MF.curve(c)[0]
            ident = A.C1.answers(c, eps) == a0
            r = A.evaluate(c, eps, rng_seed=0, reward_mode="per_ask")["reward_per_ask"]
        except Exception as e:      # noqa: BLE001
            out["knobs"][k] = {"feasible": False, "err": str(e)[:60]}
            continue
        out["knobs"][k] = {"feasible": True, "identical": ident, "d_curve": MF.dist(v, v0), "dreward": r - r0, "changed": bool(MF.dist(v, v0) > 0.3)}
    return out


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "requires": ["P-G11"], "scope": CM.SCOPE, "claim_type": "anti-gravity", "shapes": SHAPES, "representatives": 8, "knobs": KNOBS,
                         "reading": "ARTEFACT for a shape if a knob changes its geometry (curve distance > .3) in more than a third of its representatives WHILE behaviour on the base episodes is unchanged; ENTANGLED if the geometry changes only where behaviour changes; ROBUST otherwise",
                         "material_rule": "any shape reads ARTEFACT", "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    jobs = [{"pid": r["organism_id"], "shape": SHAPES[c], "manifest": r["manifest"], "env": r["env"]} for c in SHAPES for r in MF.representatives(c, 8)]
    with A.pool(8) as ex:
        rows = list(ex.map(job, jobs))
    table = {}
    for sh in SHAPES.values():
        rs = [r for r in rows if r["shape"] == sh]
        table[sh] = {}
        for k in KNOBS:
            xs = [r["knobs"][k] for r in rs if r["knobs"][k].get("feasible")]
            table[sh][k] = {"n": len(xs), "changed": float(np.mean([x["changed"] for x in xs])) if xs else None, "changed_with_identity": float(np.mean([x["changed"] and x["identical"] for x in xs])) if xs else None,
                            "identity": float(np.mean([x["identical"] for x in xs])) if xs else None, "d_curve": float(np.mean([x["d_curve"] for x in xs])) if xs else None, "dreward": float(np.mean([x["dreward"] for x in xs])) if xs else None}
    readings = {}
    for sh, v in table.items():
        art = any(x["changed_with_identity"] is not None and x["changed_with_identity"] > 1 / 3 for x in v.values())
        ent = any(x["changed"] is not None and x["changed"] > 1 / 3 for x in v.values()) and not art
        readings[sh] = "ARTEFACT" if art else "ENTANGLED" if ent else "ROBUST"
    material = any(r == "ARTEFACT" for r in readings.values())
    out = {"perturbation_id": PID, "parent": TID, "readings": readings, "table": table, "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps(rows, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence(TID, PID, "resource-knob test: readings %s; %s" % (readings, {sh: {k: (x["changed"], x["identity"]) for k, x in v.items()} for sh, v in table.items()}), material, detail=table)
    L.append_evidence("T-X17", PID, "cross: resource-artefact readings %s" % readings, material)
    print("DONE material=%s %s (%.0f s)" % (material, readings, time.time() - t0))


if __name__ == "__main__":
    main()
