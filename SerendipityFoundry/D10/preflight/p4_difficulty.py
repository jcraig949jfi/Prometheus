"""P4: no-memory (cold-start) acquisition solve rate vs budget, per family x difficulty.

Finds the operating point where the no-memory baseline is neither at floor
nor ceiling, i.e. where an organization COULD show an effect at all.
"""
import json, sys, time
sys.path.insert(0, "d10")
from lib.acquire import acquire
from foundry.engines.gp.stackvm.adapter import StackVMAdapter
from foundry.engines.base import EngineLimits
from foundry.tasks.synthetic import sample_task, FAMILY_NAMES
from foundry.core.seeds import derive_seed

eng = StackVMAdapter()
LIM = EngineLimits(max_steps=200, timeout_s=5.0)
N_TASKS = 6
N_SEEDS = 4
BUDGETS = [int(b) for b in sys.argv[1].split(",")] if len(sys.argv) > 1 else [500, 2000]
DIFFS = [1, 2, 3]

out = {}
t_start = time.perf_counter()
for family in FAMILY_NAMES:
    for d in DIFFS:
        tasks = [sample_task(family, seed=derive_seed(99, "cal", family, f"#{i}"),
                             difficulty=d) for i in range(N_TASKS)]
        for B in BUDGETS:
            ntr = nte = tot = 0
            evs = 0
            for ti, t in enumerate(tasks):
                for s in range(N_SEEDS):
                    r = acquire(eng, t, derive_seed(7, "cal", f"{ti}", f"{s}"),
                                B, [], LIM)
                    ntr += r.solved_train; nte += r.solved_test
                    evs += r.evaluations; tot += 1
            out[f"{family}/d{d}/B{B}"] = {
                "solve_train": round(ntr/tot, 3), "solve_test": round(nte/tot, 3),
                "n": tot, "mean_evals": round(evs/tot, 1)}
            print(f"{family}/d{d}/B{B}: train={ntr/tot:.3f} test={nte/tot:.3f} "
                  f"evals={evs/tot:.0f}  [{time.perf_counter()-t_start:.0f}s]", flush=True)
json.dump(out, open("d10/preflight/p4_difficulty.json", "w"), indent=1)
