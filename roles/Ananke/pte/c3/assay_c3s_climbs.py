"""C3S: causal check of every competence climb (class D). DESCRIPTIVE. usage: python assay_c3s_climbs.py ROWS_DIR PLAN OUT.json
For each D search: the climbing genome (BL if TRUE, else the champion); competence on 256 fresh worlds
(H(0xC35C1, job hash)); teacher_off (teacher only on trial 0) and zero_comm controls; swap_v2 FLIP/NO_EFFECT/PARTIAL/
EMPTY for S0, S1 and Msum on 64 fresh worlds at offset delta//2 over the scored trials among 3..10; line distance to
the canonical plant of record and to the injected stone."""
import glob
import hashlib
import json
import os
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
os.environ.setdefault("OMP_NUM_THREADS", "2")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import torch  # noqa: E402

torch.set_num_threads(2)
import swap_v2 as SW  # noqa: E402
C = SW.C
from prometheus.ananke import assays, envs, lens  # noqa: E402
from prometheus.ananke.engine import Controls  # noqa: E402

rows = [json.loads(l) for p in glob.glob(os.path.join(sys.argv[1], "rows_w*.jsonl")) for l in open(p)]
plan = json.load(open(sys.argv[2])); cells = {c["cell_id"]: c for c in plan["cells"]}
out = []
for r in rows:
    d = (r["bl_held"] and r["bl_held"]["status"] == "TRUE") or (r["champ_held"]["status"] == "TRUE" and r["champ_share"] >= .5)
    if not d:
        continue
    c = cells[r["cell_id"]]
    ph = C.Physics.from_dict(c["physics"]).validate(); env = envs.EnvSpec(**c["env"])
    g = np.asarray(r["bl_genome"] if r["bl_held"] and r["bl_held"]["status"] == "TRUE" else r["champion"], dtype=np.int64)
    plant = np.asarray(c["plant_genome"]); stone = np.asarray(c["stones"][str(r["idx"])]["genome"])
    h = int(hashlib.sha256(r["job_id"].encode()).hexdigest()[:8], 16)
    seeds = assays.world_seeds(C.H_int(0xC35C1, h), 256)
    pt, ep = C.eval_programs(ph, env, seeds, [g], device="cpu")
    rec = {"job_id": r["job_id"], "fresh_held": C.slim(C.competence("FLIP", pt[0], ep)),
           "lines_from_plant": int((g != plant).any(-1).sum()), "lines_from_stone": int((g != stone).any(-1).sum())}
    ep2 = envs.build(ph, env, seeds); sv = ep2.schedule.sense_val.numpy().copy(); C.teacher_off(sv, ep2)
    sch = type(ep2.schedule)(ep2.schedule.sense_idx, torch.as_tensor(sv), ep2.schedule.read_idx)
    tr = lens.run(ph, g, env, seeds, device="cpu", schedule=sch, ep=ep2)
    rec["teacher_off"] = C.slim(C.competence("FLIP", tr.per_trial, ep2))
    trz = lens.run(ph, g, env, seeds, device="cpu", ctrl=Controls(zero_comm=True))
    rec["zero_comm"] = C.slim(C.competence("FLIP", trz.per_trial, trz.ep))
    rec["swaps"] = {}
    for nm, cc in (("S0", [("S", 0)]), ("S1", [("S", 1)]), ("Msum", [("Msum", None)])):
        rec["swaps"][nm] = SW.carrier_swap(ph, g, env, seeds[:64], cc, trials=list(range(3, 11)),
                                           offset=max(1, env.delta // 2))["verdict"]
    print(rec["job_id"], rec["fresh_held"]["status"], round(rec["fresh_held"]["B"]["mean"], 3), "teacher_off",
          rec["teacher_off"]["status"], "zero_comm", rec["zero_comm"]["status"], rec["swaps"],
          "d_plant", rec["lines_from_plant"], "d_stone", rec["lines_from_stone"], flush=True)
    out.append(rec)
C.jdump(sys.argv[3], out)
