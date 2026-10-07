"""PTE-C4 frozen module library (order s7): ONLY independently SOLVED one-stage machinery.
For each (cell, task in RELAY1H, HOLD): the lowest-idx library-stage search whose champion is competent on its held
worlds (deterministic; never chosen by inspection). Its LIVE lines (line ablation on 32 fresh worlds,
H(C4_NS, 0x11B, task id, cell_key)) form one module, kept in program order. No GATE/FLIP/XOR content can enter: the
library stage searched only RELAY1H and HOLD, and modules are copied verbatim from those champions.
usage: python build_library.py PLAN_L.json RUN_DIR OUT.json"""
import glob
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

plan = json.load(open(sys.argv[1])); run = sys.argv[2]; out = sys.argv[3]
cells = {c["cell_id"]: c for c in plan["cells"]}
rows = [json.loads(l) for p in glob.glob(os.path.join(run, "rows_w*.jsonl")) for l in open(p) if l.strip()]
mods, prov = [], []
for cid in sorted(cells):
    for task in ("RELAY1H", "HOLD"):
        cand = sorted([r for r in rows if r["cell_id"] == cid and r["task"] == task], key=lambda r: r["idx"])
        n_comp = sum(r["success"] for r in cand)
        win = next((r for r in cand if r["success"]), None)
        rec = {"cell_id": cid, "task": task, "n_searches": len(cand), "n_competent": n_comp,
               "source_job": win["job_id"] if win else None}
        if win:
            c = cells[cid]
            ph = R.rep_physics(C.Physics.from_dict(c["physics"]).validate(), win["rep"])
            env = RC.task_env(c, task)
            seeds = assays.world_seeds(C.H_int(RC.C4_NS, 0x11B, RC.TASK_ID[task], c["cell_key"]), 32)
            live, _ = K.live_lines(ph, env, np.asarray(win["champion"]), seeds, RC.ROLE[task])
            lines = [win["champion"][0][i] for i in live]
            rec.update(live_lines=live, n_lines=len(lines))
            if lines:
                mods.append({"id": len(mods) + 1, "task": task, "cell_id": cid, "source_job": win["job_id"],
                             "lines": lines})
        prov.append(rec)
        print(rec)
C.jdump(out, {"modules": mods, "provenance": prov})
print("modules", len(mods))
