"""W2-K Q2: the only C1 INTEGRATION_BEYOND_ONE_SENSOR call (MAJ lo99 > .70), 4781b0a172b6dc3c, recomputed by
W2-H's held_recompute method (recorded champion on world_seeds(H(search_seed, HELD_NS), M_held), CPU eager),
gated on exact reproduction of the recorded (acc, lo99, hi99); plus the same champion on the C1b held worlds
(0xC1B0, the S3 recheck 'normal' arm), an independent-world replicate of the statistic. Saves pair arrays.
"""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
import gzip  # noqa: E402
import json  # noqa: E402
import pathlib  # noqa: E402
import sys  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[5]
sys.path.insert(0, str(REPO))
os.chdir(REPO)
import numpy as np  # noqa: E402
import torch  # noqa: E402

torch.set_num_threads(2)
assert not torch.cuda.is_available()
from prometheus.ananke import assays, c1b, envs, search  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402

CID = "4781b0a172b6dc3c"
r = None
for l in gzip.open(REPO / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt"):
    x = json.loads(l)
    if x["cell_id"] == CID and x["kind"] == "evolve":
        r = x
        break
ph = Physics.from_dict(r["physics"])
env = envs.EnvSpec(**r["env"])
sp = search.SearchSpec(**r["search"])
hseeds = assays.world_seeds(H_int(r["search_seed"], search.HELD_NS), sp.M_held)
g = np.asarray(r["result"]["champion"])
ev = assays.evaluate(ph, g[None], env, hseeds, device="cpu")
held = ev.pair_acc()[0]
m, lo, hi = assays.pair_ci(held)
h = r["result"]["held"]
ok = abs(m - h["acc"]) < 1e-12 and abs(lo - h["lo99"]) < 1e-12 and abs(hi - h["hi99"]) < 1e-12
# independent worlds: C1b held namespace, c1b.evaluate (the S3 recheck path)
c1bw = c1b.evaluate(ph, g, env, c1b.assays.world_seeds(c1b.HELD_NS, c1b.H_WORLDS), device="cpu").pairs
np.savez(HERE / "out" / "pairs_c1_4781.npz", held=held, c1b_normal=c1bw)
out = {"cell": CID, "reproduced": bool(ok), "held_pct": [float(m), float(lo), float(hi)], "recorded": h,
       "c1b_normal_pct": list(map(float, assays.pair_ci(c1bw)))}
(HERE / "out" / "pairs_c1_4781.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out))
