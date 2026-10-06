"""C2BX + PTE-C2C plan builder (CPU).

usage: python make_plan_c2c.py stones CELL_ID OUT.json [cuda]   (per FLIP cell; graded stones for idx 0..7;
       CPU and GPU evaluation are bit-identical, C2A gate G7)
       python make_plan_c2c.py combine STONE_DIR OUT_PLAN.json

Cells: the C2A/C2B cells (PLAN_C2A.json). C2BX uses the 4 RELAY-mh cells, idx 0..7 (the 32 C2B B4X searches).
C2C uses the 4 FLIP cells, idx 0..7, arms OP0_BASE, OPB_BASE, OP0_STEP, OPB_STEP; a STEP arm exists at (cell, idx)
only if a graded stone qualified there (c2c_common.graded_stone); unavailable stays unavailable.
Job order: all 32 C2BX jobs first (rounds by idx, RELAY cells interleaved; they are 16x-long), then C2C rounds by
idx 0..7, FLIP cells interleaved, arms in the order OP0_BASE, OPB_BASE, OP0_STEP, OPB_STEP.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DEV = "cuda" if (len(sys.argv) > 4 and sys.argv[1] == "stones" and sys.argv[4] == "cuda") else "cpu"
if DEV == "cpu":
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
sys.path.insert(0, HERE)
import c2c_common as X  # noqa: E402
B = X.B
C = X.C
from prometheus.ananke import assays, envs  # noqa: E402

C2A_PLAN = os.path.join(HERE, "..", "c2a", "PLAN_C2A.json")
C2C_ARMS = ["OP0_BASE", "OPB_BASE", "OP0_STEP", "OPB_STEP"]


def core_cells():
    return [c for c in json.load(open(C2A_PLAN))["cells"] if c["role"] in ("RELAY-mh", "FLIP")]


def stones(cell_id, out):
    c = next(x for x in core_cells() if x["cell_id"] == cell_id)
    ph = C.Physics.from_dict(c["physics"]).validate(); env = envs.EnvSpec(**c["env"])
    plant = np.asarray(c["plant_genome"], dtype=np.int64)
    qs = X.stone_qual_seeds(c["cell_key"])
    pt, ep = C.eval_programs(ph, env, qs, [plant], device=DEV)
    rec = {"cell_id": cell_id, "P0_plant": C.slim(C.competence("FLIP", pt[0], ep)), "stones": {}, "unavailable": []}
    for idx in range(8):
        g, att = X.graded_stone(ph, env, plant, c["cell_key"], idx, device=DEV)
        if g is None:
            rec["unavailable"].append(idx)
        else:
            rec["stones"][str(idx)] = {"genome": g.tolist(), "attempt": att[-1], "n_attempts": len(att),
                                       "attempt_statuses": [[a["status"], round(a["B"], 3)] for a in att]}
        print(cell_id, idx, "stone" if g is not None else "UNAVAILABLE", len(att),
              att[-1]["B"] if g is not None else None, flush=True)
    C.jdump(out, rec)


def combine(sdir, out):
    from prometheus.ananke.search import FINAL_NS, HELD_NS, TRAIN_NS
    cells = []
    for c in core_cells():
        cc = dict(c)
        if c["role"] == "FLIP":
            s = json.load(open(os.path.join(sdir, c["cell_id"] + ".json")))
            # sanity (declared pre-freeze): the plant must not read FALSE on the stone-qualification worlds.
            # FLIP-0004 reads INDETERMINATE there (B .874, lo99 .804, d_se 2.35 < 2.605) while TRUE on every C2A/C2B
            # held set and C2B qualification set: a near-margin plant, recorded as a threat, not a failure.
            assert s["P0_plant"]["status"] != "FALSE", c["cell_id"]
            cc["stones"] = s["stones"]; cc["stones_unavailable"] = s["unavailable"]; cc["P0_plant_stonequal"] = s["P0_plant"]
        cells.append(cc)
    R = [c for c in cells if c["role"] == "RELAY-mh"]; F = [c for c in cells if c["role"] == "FLIP"]
    jobs = []
    for idx in range(8):
        for c in R:
            jobs.append({"job_id": f"{c['cell_id']}|C2BX|{idx:02d}", "cell_id": c["cell_id"], "campaign": "C2BX",
                         "arm": "B16X", "idx": idx})
    for idx in range(8):
        for c in F:
            for arm in C2C_ARMS:
                if arm.endswith("STEP") and str(idx) not in c["stones"]:
                    continue
                jobs.append({"job_id": f"{c['cell_id']}|{arm}|{idx:02d}", "cell_id": c["cell_id"], "campaign": "C2C",
                             "arm": arm, "idx": idx})
    # disjointness: C2C stone-qualification worlds vs every C2A/C2B/C2BX/C2C production world and the C2B qual worlds
    qual, prod, held = set(), set(), set()
    for c in F:
        qual.update(X.stone_qual_seeds(c["cell_key"]))
    for c in cells:
        qb = set(B.qual_seeds(c["cell_key"])) | set(B.qual_seeds(c["cell_key"], B.STEP_QUAL_KEY))
        prod |= qb | set(C.admit_seeds(c["family"], c["i"]))
        seeds = [C.search_seed(c["cell_key"], i) for i in range(12)]
        if c["role"] == "FLIP":
            seeds += [X.search_seed(c["cell_key"], i) for i in range(8)]
        for s in seeds:
            h = assays.world_seeds(C.H_int(s, HELD_NS), C.M_HELD); held.update(h); prod.update(h)
            prod.update(assays.world_seeds(C.H_int(s, FINAL_NS), 16))
            for gen in range(576 if c["role"] == "RELAY-mh" else 144):
                prod.update(assays.world_seeds(C.H_int(s, TRAIN_NS, gen), 32))
            for gi in range(71, 576, 36):
                prod.update(assays.world_seeds(C.H_int(s, FINAL_NS, B.FINAL_CKPT_KEY, gi + 1), 16))
    train = prod - held
    disj = {"stone_qual_n": len(qual), "prod_n": len(prod), "qual_x_prod": len(qual & prod), "held_x_train": len(held & train)}
    print("disjointness", disj)
    assert disj["qual_x_prod"] == 0 and disj["held_x_train"] == 0, disj
    plan = {"schema": "pte_c2c.plan.v1", "cells": cells, "jobs": jobs, "c2c_arms": C2C_ARMS, "disjointness": disj}
    C.jdump(out, plan)
    from collections import Counter
    print("jobs", len(jobs), Counter(j["arm"] for j in jobs), {c["cell_id"]: c.get("stones_unavailable") for c in F})


if __name__ == "__main__":
    if sys.argv[1] == "stones":
        stones(sys.argv[2], sys.argv[3])
    else:
        combine(sys.argv[2], sys.argv[3])
