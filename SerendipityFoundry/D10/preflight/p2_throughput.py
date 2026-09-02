"""P2: raw StackVM evaluation throughput vs max_steps, and ledgered-path cost."""
import time, statistics, json, sys
from foundry.engines.gp.stackvm.adapter import StackVMAdapter
from foundry.engines.base import EngineLimits
from foundry.tasks.synthetic import sample_task, FAMILY_NAMES

eng = StackVMAdapter()
out = {}
for family in FAMILY_NAMES:
    for d in (1, 2, 3):
        t = sample_task(family, seed=1234, difficulty=d)
        tv = t.machine_view()
        for ms in (200, 1000, 5000):
            lim = EngineLimits(max_steps=ms, timeout_s=5.0)
            genos = [eng.create_random(i) for i in range(300)]
            t0 = time.perf_counter()
            n = 0
            steps = 0
            for g in genos:
                r = eng.evaluate(g, tv, 0, lim)
                steps += r.resources.steps
                n += 1
            dt = time.perf_counter() - t0
            out[f"{family}/d{d}/ms{ms}"] = {
                "evals_per_s": round(n/dt, 1),
                "mean_steps_per_eval": round(steps/n, 1),
                "n_train_cases": len(tv.train_examples),
            }
print(json.dumps(out, indent=1))
