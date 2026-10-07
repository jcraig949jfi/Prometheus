"""PTE-C4 ladder admission (CPU): for every FLIP cell x task, the task's hand plant (positive control only) at the C4
representation must pass the task ruler on 128 fresh worlds (H(C4_NS, 0xAD4, task id, cell_key)); the null program and
the cross-task adversaries must not.
  RELAY1H: plant relay_flood;  HOLD: hold_latch;  GATE: gate_plant (adversary: relay_flood = cue without context);
  FLIP: P_FLIP (adversary: RELAY_LATCH copy policy).
usage: python c4_admission.py REP OUT.json"""
import json
import os
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

import c4_common as K  # noqa: E402
import run_c4 as RC  # noqa: E402
C = K.C; R = K.R
from prometheus.ananke import assays  # noqa: E402

rep, out = sys.argv[1], sys.argv[2]
P = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "c2c", "PLAN_C2C.json")))
res = {}
for c in [x for x in P["cells"] if x["role"] == "FLIP"]:
    ph = R.rep_physics(C.Physics.from_dict(c["physics"]).validate(), rep)
    for task in ("RELAY1H", "HOLD", "GATE", "FLIP"):
        env = RC.task_env(c, task)
        plant = {"RELAY1H": K.relay_plant, "HOLD": K.hold_plant, "GATE": K.gate_plant, "FLIP": R.rep_plant}[task](ph)
        adv = {"GATE": [("relay_flood", K.relay_plant(ph))], "FLIP": [("relay_latch", C.canonical(C.relay_latch(ph)))]}.get(task, [])
        seeds = assays.world_seeds(C.H_int(RC.C4_NS, 0xAD4, RC.TASK_ID[task], c["cell_key"]), 128)
        progs = [plant, C.null(ph)] + [a for _, a in adv]
        pt, ep = C.eval_programs(ph, env, seeds, progs, device="cpu")
        role = RC.ROLE[task]
        rd = [C.competence(role, pt[i], ep) for i in range(len(progs))]
        ok = rd[0]["status"] == "TRUE" and all(x["status"] == "FALSE" for x in rd[1:])
        res[f"{c['cell_id']}|{task}"] = {"admitted": ok, "plant": C.slim(rd[0]), "null": C.slim(rd[1]),
                                         "adversaries": {n: C.slim(rd[2 + i]) for i, (n, _) in enumerate(adv)},
                                         "plant_genome": plant.tolist()}
        print(c["cell_id"], task, "ADMITTED" if ok else "NOT", rd[0]["status"], round(rd[0]["all"]["mean"], 3),
              [x["status"] for x in rd[1:]], flush=True)
C.jdump(out, res)
