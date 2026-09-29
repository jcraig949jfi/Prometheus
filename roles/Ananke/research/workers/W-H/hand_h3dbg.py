"""W-H H3 debug iterations (PLAN: <= 3). Role-faithful forwarder variants on S3."""
import sys, json, pathlib, dataclasses
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import numpy as np, torch
torch.set_num_threads(2)
from harness import run, acc
from prometheus.ananke import c1b_run, lens, plants
OUT = pathlib.Path(__file__).parent / "out"
cid = "95649e2c29e72d45"
ph, env, g, row = c1b_run.load(cid)
ph1 = dataclasses.replace(ph, rules=1, setrule=0)
# iter1: no refractory (forward every packet) ; readout S0 := CNT0
it1 = [("MOV", "EMIT", "S1", 0, 0), ("CONST", "PAY0", 0, 7, 1), ("MAX", "T0", "SENSE", "ZERO", 0),
       ("GT", "T1", "CNT0", "ZERO", 0), ("ADD", "S1", "T0", "T1", 0), ("MOV", "S0", "CNT0", 0, 0)]
# iter2: forwarder + hop budget carried in payload: PAY0 := IN0_0 - 16 (sensor starts at 256)
it2 = [("MOV", "EMIT", "S1", 0, 0), ("ADDI", "PAY0", "S1", 0, -16), ("MAX", "T0", "SENSE", "ZERO", 0),
       ("MAX", "T1", "IN0_0", "ZERO", 0), ("MAX", "S1", "T0", "T1", 0), ("MOV", "S0", "CNT0", 0, 0)]
res = {}
for name, lines in (("iter1_no_refractory", it1), ("iter2_payload_ttl", it2)):
    tr = run(ph1, plants.assemble(ph1, lines)[None], env)
    res[name] = lens.ci(acc(tr))
    ym = tr.ep.y == -1
    res[name + "_neg_trials"] = lens.ci(acc(tr, mask=ym)); res[name + "_pos_trials"] = lens.ci(acc(tr, mask=~ym))
    print(name, {k: [round(x, 3) for x in v] for k, v in res.items() if k.startswith(name)}, flush=True)
(OUT / "hand_h3dbg.json").write_text(json.dumps(res, indent=1, default=float))
