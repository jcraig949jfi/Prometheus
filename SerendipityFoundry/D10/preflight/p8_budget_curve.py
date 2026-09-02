"""P8: cold-start test-exact solve rate vs evaluation budget, by reference
program length.

The pipeline needs TWO operating points on the same task distribution: a
history budget large enough that the history phase actually deposits useful
material in the hoard, and an evaluation budget small enough that the
no-memory baseline leaves headroom. That is only possible if the curve is
steep. This measures it.
"""
import json, sys, time, random
sys.path.insert(0, "d10")
from lib import progtasks as P
from lib.acquire import acquire
from foundry.engines.gp.stackvm.adapter import StackVMAdapter
from foundry.engines.base import EngineLimits
from foundry.core.seeds import derive_seed

eng = StackVMAdapter()
LIM = EngineLimits(max_steps=200, timeout_s=5.0)
OUT_HI, MIN_DISTINCT = 255, 16
BUDGETS = [200, 800, 3200, 12800]
N_TASK, N_SEED = 8, 3


def bounded_ok(prog, ps):
    outs = []
    for ins in P._probe_inputs(ps, P.PROBE_N):
        r = P._run(prog, ins, P.MAX_REF_STEPS + 1)
        if r.halt != "end" or not (0 <= r.output <= OUT_HI):
            return None
        outs.append(r.output)
    return outs if len(set(outs)) >= MIN_DISTINCT else None


def gen_tasks(L, n, gseed):
    tasks = []
    for i in range(6000):
        if len(tasks) >= n:
            break
        rng = random.Random(derive_seed(gseed, "p8", f"L{L}", f"#{i}"))
        p = bytes(rng.randrange(256) for _ in range(L))
        if bounded_ok(p, derive_seed(gseed, "probe")) is None:
            continue
        t = P.task_from_program(p, derive_seed(gseed, "case", f"#{i}"),
                                6, 20, f"g{i}", 0)
        if t is not None:
            tasks.append(t)
    return tasks


out = {}
t0 = time.perf_counter()
for L in (8, 10, 12):
    tasks = gen_tasks(L, N_TASK, 3030)
    if len(tasks) < N_TASK:
        out[f"L{L}"] = {"error": f"only {len(tasks)} tasks"}
        print(out[f"L{L}"], flush=True)
        continue
    for B in BUDGETS:
        ok = tot = 0
        okt = 0
        for ti, pt in enumerate(tasks):
            for s in range(N_SEED):
                r = acquire(eng, pt.task, derive_seed(41, "p8", f"{ti}", f"{s}"),
                            B, [], LIM)
                ok += r.solved_test
                okt += r.solved_train
                tot += 1
        out[f"L{L}/B{B}"] = {"test": round(ok / tot, 3),
                             "train": round(okt / tot, 3), "n": tot}
        print(f"L{L}/B{B}: test={ok/tot:.3f} train={okt/tot:.3f} "
              f"[{time.perf_counter()-t0:.0f}s]", flush=True)
json.dump(out, open("d10/preflight/p8.json", "w"), indent=1)
print("DONE")
