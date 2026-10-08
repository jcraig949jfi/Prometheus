"""C3R representation admissibility (order s4: a representation whose plant cannot pass is inadmissible).
For every FLIP cell x representation: the re-encoded P_FLIP (c3r_common.rep_plant) and the original C2 plant of record
are evaluated on 128 fresh REP_QUAL worlds (H(C3_NS, 0x3AD, cell_key)). Admissible iff the re-encoded plant does not
read FALSE, has the SAME ruler status as the R0 plant there, and |B - B_R0| <= .02. (First version required IDENTICAL
per-trial outputs; at FLIP-0004 (mut_site .001) prog_len 24 changes which program lines the in-world site mutation
targets (line index mod prog_len), so outputs differ slightly (B .877 vs .881, same status). Rule declared before any
C3R search; the capacity x site-mutation interaction is recorded as a confound.)
usage: python rep_admission.py OUT.json"""
import json, os, sys
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import c3r_common as R
C = R.C
from prometheus.ananke import assays, envs
P = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "c2c", "PLAN_C2C.json")))
out = {}
for c in [x for x in P["cells"] if x["role"] == "FLIP"]:
    ph0 = C.Physics.from_dict(c["physics"]).validate(); env = envs.EnvSpec(**c["env"])
    seeds = assays.world_seeds(C.H_int(R.K.C3_NS, 0x3AD, c["cell_key"]), 128)
    pt0, ep = C.eval_programs(ph0, env, seeds, [np.asarray(c["plant_genome"])], device="cpu")
    base = C.competence("FLIP", pt0[0], ep)
    for rep in R.REPS:
        ph = R.rep_physics(ph0, rep); g = R.rep_plant(ph)
        pt, ep2 = C.eval_programs(ph, env, seeds, [g], device="cpu")
        same = bool(np.array_equal(pt[0], pt0[0]))
        comp = C.competence("FLIP", pt[0], ep2)
        out[f"{c['cell_id']}|{rep}"] = {"identical_to_R0_plant": same, "status": comp["status"], "B": comp["B"]["mean"],
                                        "R0_status": base["status"], "R0_B": base["B"]["mean"],
                                        "admissible": comp["status"] != "FALSE" and comp["status"] == base["status"]
                                        and abs(comp["B"]["mean"] - base["B"]["mean"]) <= .02, "lines": C.nlines(g),
                                        "plant_genome": g.tolist()}
        print(c["cell_id"], rep, same, comp["status"], round(comp["B"]["mean"], 3), flush=True)
C.jdump(sys.argv[1], out)
