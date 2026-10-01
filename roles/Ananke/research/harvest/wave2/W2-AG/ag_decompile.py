"""W2-AG: static decompile only (no engine run) of 4781b0a1 and its D replicate 8743da7f,
plus the anti-copy champion 964053bb, to see whether sensors gate emission on inbox traffic."""
import os, sys, json
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "H-PLANT"))
import torch; torch.set_num_threads(2); assert not torch.cuda.is_available()
import numpy as np
from hp_common import rows, decompile
from prometheus.ananke.physics import Physics
out = {}
for cid in (sys.argv[1:] or ["4781b0a1", "8743da7f", "964053bb", "613162a3"]):
    r = [x for x in rows() if x["cell_id"].startswith(cid) and x["kind"] == "evolve"][0]
    ph = Physics.from_dict(r["physics"]); g = np.asarray(r["result"]["champion"])
    out[cid] = {"rules": ph.rules, "setrule": r["physics"].get("setrule"),
                "programs": [decompile(ph, g[k]) for k in range(g.shape[0])]}
json.dump(out, open(os.path.join(os.path.dirname(__file__), ("decompiled.json" if len(sys.argv) < 2 else "decompiled_hopscan.json")), "w"), indent=1)
for k, v in out.items():
    print("==", k, "rules", v["rules"], "setrule", v["setrule"])
    for j, p in enumerate(v["programs"]):
        print(" rule", j); print("\n".join("   " + s for s in p))
