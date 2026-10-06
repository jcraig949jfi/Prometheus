"""PTE-C2B plan builder (CPU). Same 8 cells as C2A (PLAN_C2A.json, production cell keys).

usage: python make_plan_c2b.py qual CELL_ID OUT.json        (per cell; run in parallel)
       python make_plan_c2b.py combine QUAL_DIR OUT_PLAN.json [--arms JSON]

qual (per cell, all before any C2B search):
  P0  the C2A plant of record is still TRUE on the C2B_BROKEN_QUAL worlds (known answer: exact plant competent).
  BRK for k in (1, 2), idx 0..7: first draw (rng(C2B_NS, BRK_EDIT_KEY, cell_key, k, idx, attempt)) with exactly
      k distinct GA-native field edits that reads FALSE on C2B_BROKEN_QUAL (TRUE/INDETERMINATE redrawn; cap 50).
  STEP RELAY-mh: relay_step must (a) read TRUE under the RELAY-1h ruler on the cell's one-hop variant (same
      physics, env d=1; every world exactly 1 hop) and (b) read FALSE (not INDETERMINATE) under the RELAY-mh ruler
      on the production env. FLIP: flip_step (RELAY_LATCH) must read FALSE under the B ruler with B hi99 < .75
      (not near the boundary) and have same-cue accuracy >= .75 (it performs the copy/latch subfunction).
      Both on STEP_QUAL worlds. A cell failing STEP qualification gets no STEP arm (STEP_UNAVAILABLE).
combine: job list (rounds by idx 0..7; cells interleaved R1 F1 R2 F2 ...; arm order BRK1, B4X, STEP, BRK2) and the
  disjointness assertion: qualification worlds vs C2A admission/held/train/final worlds and C2B train/final/held.
"""
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
sys.path.insert(0, HERE)
import c2b_common as B  # noqa: E402
C = B.C
from prometheus.ananke import assays, envs  # noqa: E402

C2A_PLAN = os.path.join(HERE, "..", "c2a", "PLAN_C2A.json")
ARMS = {"BRK1": 8, "B4X": 8, "STEP": 8, "BRK2": 8}
ARM_ORDER = ["BRK1", "B4X", "STEP", "BRK2"]


def core_cells():
    p = json.load(open(C2A_PLAN))
    return [c for c in p["cells"] if c["role"] in ("RELAY-mh", "FLIP")]


def hop_audit(ph, env, seeds):
    sys.path.insert(0, os.path.join(HERE, "..", "..", "research", "harvest", "wave2", "W2-AD"))
    from prometheus.ananke import topology as tp
    ep = envs.build(ph, env, seeds)
    s = ep.schedule.sense_idx.numpy()[:, 0]; a = ep.schedule.read_idx.numpy()[:, 0]
    h = [int(tp.graph_distances(ph, int(si))[int(ai)]) for si, ai in zip(s[::2], a[::2])]
    return min(h), max(h)


def step_qual(c, ph, env, plant):
    role = c["role"]
    ss = B.qual_seeds(c["cell_key"], B.STEP_QUAL_KEY)
    outl = []
    for fn in B.STEP_CANDIDATES[role]:
        st = fn(ph)
        if role == "RELAY-mh":
            env1 = B.onehop_env(env, ph)
            hmin, hmax = hop_audit(ph, env1, ss)
            p1, e1 = C.eval_programs(ph, env1, ss, [st, plant], device="cpu")
            one = C.competence("RELAY-1h", p1[0], e1)
            plant_one = C.competence("RELAY-1h", p1[1], e1)
            pm, em = C.eval_programs(ph, env, ss, [st], device="cpu")
            mh = C.competence("RELAY-mh", pm[0], em)
            ok = (hmin == hmax == 1) and one["status"] == "TRUE" and mh["status"] == "FALSE"
            outl.append({"name": fn.__name__, "genome": st.tolist(), "lines": C.nlines(st),
                         "onehop_hops": [hmin, hmax], "onehop_RELAY1h": C.slim(one), "plant_onehop": C.slim(plant_one),
                         "mh": C.slim(mh), "qualified": bool(ok)})
        else:
            pf, ef = C.eval_programs(ph, env, ss, [st], device="cpu")
            fl = C.competence("FLIP", pf[0], ef)
            b = fl["B"]
            ok = fl["status"] == "FALSE" and b["hi99"] < C.B_CUT and b["same"] >= 0.75
            outl.append({"name": fn.__name__ + "(RELAY_LATCH)", "genome": st.tolist(), "lines": C.nlines(st),
                         "FLIP": C.slim(fl), "qualified": bool(ok)})
    return outl


def stepqual(cell_id, path):
    import json as _j
    c = next(x for x in core_cells() if x["cell_id"] == cell_id)
    ph = C.Physics.from_dict(c["physics"]).validate(); env = envs.EnvSpec(**c["env"])
    rec = _j.load(open(path))
    rec["step_candidates"] = step_qual(c, ph, env, np.asarray(c["plant_genome"], dtype=np.int64))
    rec.pop("step", None)
    C.jdump(path, rec)
    print(cell_id, [(x["name"], x["qualified"]) for x in rec["step_candidates"]])


def qual(cell_id, out):
    c = next(x for x in core_cells() if x["cell_id"] == cell_id)
    ph = C.Physics.from_dict(c["physics"]).validate()
    env = envs.EnvSpec(**c["env"])
    role = c["role"]
    plant = np.asarray(c["plant_genome"], dtype=np.int64)
    qs = B.qual_seeds(c["cell_key"])
    pt, ep = C.eval_programs(ph, env, qs, [plant], device="cpu")
    p0 = C.competence(role, pt[0], ep)
    rec = {"cell_id": cell_id, "P0_plant": C.slim(p0), "brk": {}, "brk_failures": []}
    for k in (1, 2):
        arm = f"BRK{k}"
        rec["brk"][arm] = {}
        for idx in range(8):
            g, att = B.broken_start(ph, env, role, plant, k, c["cell_key"], idx)
            if g is None:
                rec["brk_failures"].append([arm, idx, len(att)])
                continue
            rec["brk"][arm][str(idx)] = {"genome": g.tolist(), "edits": att[-1]["edits"], "attempts": att,
                                         "n_attempts": len(att)}
            print(cell_id, arm, idx, "attempts", len(att), [a["status"] for a in att], flush=True)
    rec["step_candidates"] = step_qual(c, ph, env, plant)
    print(cell_id, "STEP", [(x["name"], x["qualified"]) for x in rec["step_candidates"]], flush=True)
    C.jdump(out, rec)


def combine(qdir, out, arms=None):
    from prometheus.ananke.search import FINAL_NS, HELD_NS, TRAIN_NS
    arms = dict(ARMS, **(arms or {}))
    cells = []
    for c in core_cells():
        q = json.load(open(os.path.join(qdir, c["cell_id"] + ".json")))
        assert q["P0_plant"]["status"] == "TRUE", (c["cell_id"], "plant not competent on qual worlds")
        cc = dict(c)
        cc["brk"] = q["brk"]; cc["brk_failures"] = q["brk_failures"]; cc["P0_plant"] = q["P0_plant"]
        cc["step_candidates"] = q["step_candidates"]
        a = dict(arms)
        a["BRK1"] = min(a["BRK1"], len(q["brk"]["BRK1"])); a["BRK2"] = min(a["BRK2"], len(q["brk"]["BRK2"]))
        cc["arms"] = a
        cells.append(cc)
    # one family-wide stepping stone: the first declared candidate qualified at ALL four cells of the family;
    # if no candidate qualifies everywhere, each cell uses the first candidate qualified there, else no STEP arm.
    for role in ("RELAY-mh", "FLIP"):
        fam = [c for c in cells if c["role"] == role]
        names = [x["name"] for x in fam[0]["step_candidates"]]
        allq = [n for n in names if all(next(x for x in c["step_candidates"] if x["name"] == n)["qualified"] for c in fam)]
        for c in fam:
            pick = allq[0] if allq else next((x["name"] for x in c["step_candidates"] if x["qualified"]), None)
            c["step"] = next((x for x in c["step_candidates"] if x["name"] == pick), None)
            c["step_rule"] = "family-wide (qualified at all 4 cells)" if allq else "per-cell fallback"
            if c["step"] is None:
                c["arms"]["STEP"] = 0
    R = [c for c in cells if c["role"] == "RELAY-mh"]; F = [c for c in cells if c["role"] == "FLIP"]
    order = [x for pair in zip(R, F) for x in pair]
    jobs = []
    for rnd in range(8):
        for c in order:
            for arm in ARM_ORDER:
                if rnd < c["arms"].get(arm, 0) and (arm not in ("BRK1", "BRK2") or str(rnd) in c["brk"][arm]):
                    jobs.append({"job_id": f"{c['cell_id']}|{arm}|{rnd:02d}", "cell_id": c["cell_id"], "arm": arm, "idx": rnd})
    qual, prod, c2a_admit = set(), set(), set()
    for c in cells:
        qual.update(B.qual_seeds(c["cell_key"])); qual.update(B.qual_seeds(c["cell_key"], B.STEP_QUAL_KEY))
        c2a_admit.update(C.admit_seeds(c["family"], c["i"]))
        for idx in range(12):                                # every C2A seed index (BASE 12, W0/M32 8, ...)
            s = C.search_seed(c["cell_key"], idx)
            prod.update(assays.world_seeds(C.H_int(s, HELD_NS), C.M_HELD))
            prod.update(assays.world_seeds(C.H_int(s, FINAL_NS), 16))
            for gen in range(144):
                prod.update(assays.world_seeds(C.H_int(s, TRAIN_NS, gen), 32))
            for gi in B.B4X_CHECKPOINTS[1:]:
                prod.update(assays.world_seeds(C.H_int(s, FINAL_NS, B.FINAL_CKPT_KEY, gi + 1), 16))
    held = set()
    for c in cells:
        for idx in range(12):
            held.update(assays.world_seeds(C.H_int(C.search_seed(c["cell_key"], idx), HELD_NS), C.M_HELD))
    train = prod - held
    disj = {"qual_n": len(qual), "prod_n": len(prod), "qual_x_prod": len(qual & prod), "qual_x_c2a_admit": len(qual & c2a_admit),
            "held_x_train": len(held & train)}
    print("disjointness", disj)
    assert disj["qual_x_prod"] == 0 and disj["qual_x_c2a_admit"] == 0 and disj["held_x_train"] == 0, disj
    plan = {"schema": "pte_c2b.plan.v1", "c2a_plan": "roles/Ananke/pte/c2a/PLAN_C2A.json", "cells": cells,
            "jobs": jobs, "arms": arms, "arm_order": ARM_ORDER, "disjointness": disj}
    C.jdump(out, plan)
    print("jobs", len(jobs), {c["cell_id"]: c["arms"] for c in cells})


if __name__ == "__main__":
    if sys.argv[1] == "qual":
        qual(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "stepqual":
        stepqual(sys.argv[2], sys.argv[3])
    else:
        combine(sys.argv[2], sys.argv[3], json.loads(sys.argv[4]) if len(sys.argv) > 4 else None)
