"""E3 (PLAN.md): operator transfer matrix of existing matched C1 champions."""
import json, pathlib, sys, time
import numpy as np, torch
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import e2_evolve as E
from prometheus.ananke import assays, c1b_run, lens
from prometheus.ananke.rng import H_int
torch.set_num_threads(2)
CELLS = {"SUM": ["57650798bada0219", "8ccf6c723ec57b3d", "7e2affed17ce5db1", "08d8f0c51f1cad2f",
                 "48dbe2a190030f09", "8e1caf6bcc7897fb", "308d6488ba1291f8", "839b39c79ec65b56",
                 "1448cd7d2eba30a8", "0f1969774985a933"],
         "ALOHA2": ["057941f350d54c75", "6b602a1943146426", "8c5eba065b9853bc"],
         "SAT2": ["f6b623cdb23afd2c", "083fde9f3fbbeddb", "84c8c1d19358a25c", "15e58864edb122bc",
                  "1a86071f8e62e6ae"]}
dev = sys.argv[1] if len(sys.argv) > 1 else "cpu"
out_f = E.OUT / "e3.json"
res = json.loads(out_f.read_text()) if out_f.exists() else {}
seeds = assays.world_seeds(H_int(E.NS, 0xE3), 64)
for arm, cells in CELLS.items():
    for cid in cells:
        if cid in res:
            continue
        t0 = time.time()
        ph, env, g, row = c1b_run.load(cid)
        base = ph
        xfer = {a2: E.held_eval(base, a2, env, g, seeds, dev)[0] for a2 in E.ARMS}
        pr = E.probes(base, arm, env, g, dev)
        res[cid] = {"arm": arm, "c1_held": row["result"]["held"], "transfer": xfer, "probes": pr}
        out_f.write_text(json.dumps(res, indent=1, default=float))
        print(arm, cid, {a: round(v[0], 3) for a, v in xfer.items()},
              {n: v["verdict"] for n, v in pr.items() if n != "normal"}, round(time.time() - t0), flush=True)
