"""W2-O: attribute guard alarms to an arm. Runs the held normal arm and the zero_comm arm in SEPARATE
guarded() contexts (exact W2-C guard code), so an alarm raised only by the zero_comm World is visible.
G6/G7/G0 need both arms in one context and are not meaningful here; read G1-G5, G9-G12 only."""
import os, sys, json, pathlib
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["PTE_MUT_THREADS"] = "2"
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import null_audit as NA  # noqa: E402
import numpy as np  # noqa: E402
from prometheus.ananke import assays, envs, search  # noqa: E402
from prometheus.ananke.engine import Controls  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402
from prometheus.ananke.search import HELD_NS  # noqa: E402
from pte_mut.guards import guarded  # noqa: E402

with open(HERE / "out/per_arm_guards.jsonl", "a") as f:
    for cid in sys.argv[1:]:
        r = NA.ROWS[cid]
        ph = Physics.from_dict(r["physics"]).validate()
        env = envs.EnvSpec(**r["env"])
        sp = search.SearchSpec(**r["search"])
        champ = np.asarray(r["result"]["champion"])
        hs = assays.world_seeds(H_int(r["search_seed"], HELD_NS), sp.M_held)
        out = {"cell": cid, "signal": bool(r["labels"].get("SIGNAL"))}
        for arm, ctrl in (("normal", None), ("zero_comm", Controls(zero_comm=True))):
            with guarded() as g:
                g.champion = champ
                assays.evaluate(ph, champ[None], env, hs, ctrl=ctrl, device="cpu", graph=False)
                out[arm] = g.check()
        print(json.dumps(out), flush=True)
        f.write(json.dumps(out) + "\n")
