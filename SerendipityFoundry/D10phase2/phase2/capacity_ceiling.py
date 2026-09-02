"""Phase 2: the offline capacity ceiling -- run on the DEV set ONLY.

The gate set is never touched here.

This asks a question that is logically PRIOR to "can a VM program express
it": IS THERE ANY TASK-CONDITIONAL RELEVANCE IN THIS CORPUS AT ALL?

PP1 (0.344) vs U (0.031) proves useful memories exist. It does NOT prove
that WHICH memory is useful depends on the query. If the same artifacts are
best for every task, then the whole PP1 advantage is UNCONDITIONAL, the
best possible strategy is "retrieve globally good material" -- which is
exactly what the R2 null already does -- and no KA/KQ pair, however
cleverly written, could beat R2. That would settle the capacity question
without writing a single key program.

Stage A measures exactly that.
  ORACLE_COND    per-task oracle retrieval            (PP1's ceiling)
  ORACLE_UNCOND  one fixed global top-k for all tasks (R2's ceiling)
  UNIFORM        uniform corpus sample                (U)
The quantity that matters is ORACLE_COND - ORACLE_UNCOND. That is the
entire budget any task-conditional keying could ever spend.
"""
import sys, json, random, time
import numpy as np
sys.path.insert(0, "d10")
from lib.acquire import acquire
from lib.objective import primary_objective
from foundry.tasks.base import ExactTask
from foundry.engines.gp.stackvm.adapter import StackVMAdapter
from foundry.engines.base import EngineLimits
from foundry.core.seeds import derive_seed

eng = StackVMAdapter()
LIM = EngineLimits(max_steps=200, timeout_s=5.0)
K, B_EVAL, N_EVAL_SEEDS = 4, 400, 4

D = json.load(open("d10/phase2/dataset.json"))
corpus = [bytes.fromhex(h) for h in D["corpus_hex"]]
dev = [(d["family"],
        ExactTask(train_cases=[(list(a), b) for a, b in d["train"]],
                  test_cases=[(list(a), b) for a, b in d["test"]]))
       for d in D["dev_tasks"]]
print(f"corpus={len(corpus)} dev_tasks={len(dev)}", flush=True)

t0 = time.perf_counter()
# ---------- oracle relevance matrix R[artifact, task] ----------
R = np.zeros((len(corpus), len(dev)))
for tj, (fi, task) in enumerate(dev):
    tv = task.machine_view()
    for ai, g in enumerate(corpus):
        r = eng.evaluate(g, tv, 0, LIM)
        R[ai, tj] = r.fitness or 0.0
    print(f"  relevance col {tj+1}/{len(dev)} [{time.perf_counter()-t0:.0f}s]",
          flush=True)
np.save("d10/phase2/relevance_dev.npy", R)

# ---------- variance decomposition ----------
grand = R.mean()
a_eff = R.mean(axis=1, keepdims=True) - grand      # artifact main effect
t_eff = R.mean(axis=0, keepdims=True) - grand      # task main effect
inter = R - grand - a_eff - t_eff
tot = float(((R - grand) ** 2).sum())
dec = {
    "total_ss": tot,
    "artifact_main_frac": float((a_eff ** 2).sum() * R.shape[1] / tot),
    "task_main_frac": float((t_eff ** 2).sum() * R.shape[0] / tot),
    "interaction_frac": float((inter ** 2).sum() / tot),
}

# ---------- is the best set task-specific? ----------
topk = [set(np.argsort(-R[:, j], kind="stable")[:K].tolist())
        for j in range(R.shape[1])]
pair = [len(topk[i] & topk[j]) / K
        for i in range(len(topk)) for j in range(i + 1, len(topk))]
global_rank = np.argsort(-R.mean(axis=1), kind="stable")
global_top = [corpus[i] for i in global_rank[:K]]
overlap_global = [len(topk[j] & set(global_rank[:K].tolist())) / K
                  for j in range(len(topk))]

# ---------- downstream anchors on DEV ----------
def run(cond_fn, tag):
    out = []
    for tj, (fi, task) in enumerate(dev):
        seeds_g = cond_fn(tj, task)
        for s in range(N_EVAL_SEEDS):
            sd = derive_seed(93, "devcap", f"{tj}", f"{s}")
            out.append(acquire(eng, task, sd, B_EVAL, seeds_g, LIM))
    rate = primary_objective(out)
    print(f"  {tag:16s} test_exact={rate:.4f} "
          f"[{time.perf_counter()-t0:.0f}s]", flush=True)
    return out, rate


def uniform(tj, task):
    rng = random.Random(derive_seed(94, "u", f"{tj}"))
    return [corpus[rng.randrange(len(corpus))] for _ in range(K)]


def cond_oracle(tj, task):
    return [corpus[i] for i in np.argsort(-R[:, tj], kind="stable")[:K]]


def uncond_oracle(tj, task):
    return global_top


_, r_u = run(uniform, "UNIFORM(U)")
_, r_un = run(uncond_oracle, "ORACLE_UNCOND")
_, r_c = run(cond_oracle, "ORACLE_COND(PP1)")

res = {
    "corpus": len(corpus), "dev_tasks": len(dev), "k": K, "B_EVAL": B_EVAL,
    "variance_decomposition": {k: round(v, 5) for k, v in dec.items()},
    "topk_pairwise_overlap_mean": round(float(np.mean(pair)), 4),
    "topk_overlap_with_global_mean": round(float(np.mean(overlap_global)), 4),
    "downstream": {"UNIFORM": round(r_u, 4),
                   "ORACLE_UNCOND": round(r_un, 4),
                   "ORACLE_COND": round(r_c, 4)},
    "conditional_headroom": round(r_c - r_un, 4),
    "total_memory_headroom": round(r_c - r_u, 4),
}
print(json.dumps(res, indent=1))
json.dump(res, open("d10/phase2/capacity_ceiling.json", "w"), indent=1)
