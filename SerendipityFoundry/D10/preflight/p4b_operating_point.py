"""P4b: find a cold-start operating point with usable variance.

Sweeps (family x difficulty x n_train x budget). We need a cell where the
no-memory arm's TEST-exact solve rate sits strictly between floor and
ceiling; otherwise no organization of any kind could show an effect.
"""
import json, sys, time
sys.path.insert(0, "d10")
from lib.acquire import acquire
from lib.tasks import task_pool
from foundry.engines.gp.stackvm.adapter import StackVMAdapter
from foundry.engines.base import EngineLimits
from foundry.tasks.synthetic import FAMILY_NAMES
from foundry.core.seeds import derive_seed

eng = StackVMAdapter()
LIM = EngineLimits(max_steps=200, timeout_s=5.0)
N_TASKS, N_SEEDS = 5, 4
out = {}
t0 = time.perf_counter()
for family in FAMILY_NAMES:
    for d in (1,):
        for n_train in (3, 6):
            tasks = task_pool(family, d, n_train, N_TASKS, 4242, "p4b")
            for B in (400, 1500):
                ntr = nte = tot = 0
                for ti, t in enumerate(tasks):
                    for s in range(N_SEEDS):
                        r = acquire(eng, t, derive_seed(11, "p4b", f"{ti}", f"{s}"),
                                    B, [], LIM)
                        ntr += r.solved_train; nte += r.solved_test; tot += 1
                key = f"{family}/d{d}/n{n_train}/B{B}"
                out[key] = {"train": round(ntr/tot,3), "test": round(nte/tot,3), "n": tot}
                print(f"{key}: train={ntr/tot:.3f} test={nte/tot:.3f} [{time.perf_counter()-t0:.0f}s]", flush=True)
json.dump(out, open("d10/preflight/p4b.json","w"), indent=1)
