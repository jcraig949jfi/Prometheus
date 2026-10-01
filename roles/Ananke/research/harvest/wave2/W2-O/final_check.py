"""W2-O: the search side of a NULL. Re-evaluate each sampled champion on its recorded FINAL (selection-ranking)
seeds under W2-C's guards: champ_train_final must reproduce exactly, and no break-indicating guard may fire
on the world set the search used to choose the champion."""
import os, sys, json, pathlib
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["PTE_MUT_THREADS"] = "2"
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import null_audit as NA  # noqa: E402  (imports W2-C guards, CPU)
import time  # noqa: E402
import numpy as np  # noqa: E402
from prometheus.ananke import assays, envs, search  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402
from prometheus.ananke.search import FINAL_NS  # noqa: E402
from pte_mut.guards import guarded  # noqa: E402

t0 = time.process_time()
out = []
for s in json.load(open(HERE / "out/sample.json")):
    r = NA.ROWS[s["cell"]]
    ph = Physics.from_dict(r["physics"]).validate()
    env = envs.EnvSpec(**r["env"])
    sp = search.SearchSpec(**r["search"])
    champ = np.asarray(r["result"]["champion"])
    fs = assays.world_seeds(H_int(r["search_seed"], FINAL_NS), sp.M_final)
    with guarded() as g:
        g.champion = champ
        res = assays.evaluate(ph, champ[None], env, fs, device="cpu", graph=False)
        al = g.check()
    v = float(res.mean()[0])
    o = {"cell": s["cell"], "final_recorded": r["result"]["champ_train_final"], "final_cpu": v,
         "exact": abs(v - r["result"]["champ_train_final"]) < 1e-12, "alarms": al}
    print(o, flush=True)
    out.append(o)
(HERE / "out/final_check.json").write_text(json.dumps({"rows": out, "cpu_s": round(time.process_time() - t0, 1)}, indent=1))
