"""P7: end-to-end feasibility of the real pipeline.

Runs a real history phase, forms a real corpus (every artifact created --
no curation), and measures on held-out eval tasks:
  cold    - k fresh random genotypes                       (arm N)
  uniform - k uniformly sampled corpus artifacts           (arm U)
  oracle  - the k corpus artifacts with the highest TRUE train fitness on
            this eval task                                 (planted positive
            PP1: an upper bound on what any retrieval could deliver)
This fixes the operating point AND the achievable effect size, which the
power calculation needs before anything is frozen.
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
K = 4
OUT_HI, MIN_DISTINCT = 255, 16
N_FAM = 6
N_HIST_MEM, N_EVAL_MEM = 3, 3
N_HIST_RESTARTS = 2
N_EVAL_SEEDS = 3


def bounded_ok(prog, ps):
    outs = []
    for ins in P._probe_inputs(ps, P.PROBE_N):
        r = P._run(prog, ins, P.MAX_REF_STEPS + 1)
        if r.halt != "end" or not (0 <= r.output <= OUT_HI):
            return None
        outs.append(r.output)
    return outs if len(set(outs)) >= MIN_DISTINCT else None


def root_b(seed, L, tries=4000):
    for i in range(tries):
        rng = random.Random(derive_seed(seed, "rb", f"#{i}"))
        p = bytes(rng.randrange(256) for _ in range(L))
        if bounded_ok(p, derive_seed(seed, "probe")) is not None:
            return p
    return None


def member_b(root, seed, n_mut, tries=400):
    ps = derive_seed(seed, "probe")
    ro = bounded_ok(root, ps)
    for i in range(tries):
        g = root
        for j in range(n_mut):
            g = eng.mutate(g, derive_seed(seed, "mb", f"#{i}", f"m{j}"))
        o = bounded_ok(g, ps)
        if o is not None and o != ro:
            return g
    return None


def make_families(L, n_mut, gseed, n_need, n_mem, cand=400):
    fams = []
    for f in range(cand):
        if len(fams) >= n_need:
            break
        root = root_b(derive_seed(gseed, "root", f"#{f}"), L)
        if root is None:
            continue
        tasks = []
        for m in range(n_mem * 25):
            if len(tasks) >= n_mem:
                break
            g = member_b(root, derive_seed(gseed, "mem", f"#{f}", f"#{m}"), n_mut)
            if g is None:
                continue
            t = P.task_from_program(g, derive_seed(gseed, "case", f"#{f}", f"#{m}"),
                                    6, 20, f"f{f}", m)
            if t is not None:
                tasks.append(t)
        if len(tasks) >= n_mem:
            fams.append(tasks)
    return fams


def train_fitness(genotype, task):
    r = eng.evaluate(genotype, task.machine_view(), 0, LIM)
    return r.fitness if r.fitness is not None else 0.0


out = {}
t0 = time.perf_counter()
for L, n_mut in ((10, 1), (12, 1)):
    hist_f = make_families(L, n_mut, 5150, N_FAM, N_HIST_MEM + N_EVAL_MEM)
    if len(hist_f) < N_FAM:
        out[f"L{L}/m{n_mut}"] = {"error": f"only {len(hist_f)} families"}
        print(out[f"L{L}/m{n_mut}"], flush=True)
        continue
    hist_tasks = [(fi, t) for fi, ts in enumerate(hist_f) for t in ts[:N_HIST_MEM]]
    eval_tasks = [(fi, t) for fi, ts in enumerate(hist_f) for t in ts[N_HIST_MEM:]]
    for B_HIST, B_EVAL in ((800, 400), (1500, 400)):
        # ---- history phase: corpus = every genotype evaluated -------------
        corpus, hist_solves = [], 0
        for hi, (fi, pt) in enumerate(hist_tasks):
            for rst in range(N_HIST_RESTARTS):
                seen = []
                r = acquire(eng, pt.task, derive_seed(61, "hist", f"{hi}", f"{rst}"),
                            B_HIST, [], LIM)
                hist_solves += r.solved_test
                if r.solver_genotype is not None:
                    seen.append(r.solver_genotype)
                corpus.extend(seen)
        # replay history to collect the FULL artifact set cheaply: rerun with
        # a collecting evaluate wrapper
        corpus = []
        class Collect:
            def __init__(s, e): s.e = e; s.seen = []
            def info(s): return s.e.info()
            def create_random(s, *a, **k): return s.e.create_random(*a, **k)
            def mutate(s, *a, **k): return s.e.mutate(*a, **k)
            def recombine(s, *a, **k): return s.e.recombine(*a, **k)
            def evaluate(s, g, tv, sd, lim):
                s.seen.append(bytes(g)); return s.e.evaluate(g, tv, sd, lim)
        col = Collect(eng)
        hist_solves = 0
        for hi, (fi, pt) in enumerate(hist_tasks):
            for rst in range(N_HIST_RESTARTS):
                r = acquire(col, pt.task, derive_seed(61, "hist", f"{hi}", f"{rst}"),
                            B_HIST, [], LIM)
                hist_solves += r.solved_test
        corpus = col.seen
        # ---- eval phase ---------------------------------------------------
        rng = random.Random(derive_seed(62, "unif"))
        acc = {"cold": [0, 0], "uniform": [0, 0], "oracle": [0, 0]}
        rank_pool_idx = list(range(len(corpus)))
        rng.shuffle(rank_pool_idx)
        rank_pool_idx = rank_pool_idx[:2500]
        for ei, (fi, pt) in enumerate(eval_tasks):
            scored = sorted(rank_pool_idx,
                            key=lambda i: -train_fitness(corpus[i], pt.task))
            oracle_seeds = [corpus[i] for i in scored[:K]]
            for s in range(N_EVAL_SEEDS):
                sd = derive_seed(63, "eval", f"{ei}", f"{s}")
                urng = random.Random(derive_seed(64, "u", f"{ei}", f"{s}"))
                unif = [corpus[urng.randrange(len(corpus))] for _ in range(K)]
                for cond, seeds in (("cold", []), ("uniform", unif),
                                    ("oracle", oracle_seeds)):
                    r = acquire(eng, pt.task, sd, B_EVAL, seeds, LIM)
                    acc[cond][0] += r.solved_test
                    acc[cond][1] += 1
        key = f"L{L}/m{n_mut}/Bh{B_HIST}/Be{B_EVAL}"
        out[key] = {c: round(v[0] / v[1], 3) for c, v in acc.items()}
        out[key].update({"corpus_size": len(corpus),
                         "history_trials": len(hist_tasks) * N_HIST_RESTARTS,
                         "history_solves": hist_solves,
                         "n_eval_tasks": len(eval_tasks),
                         "n_per_cond": acc["cold"][1],
                         "best_oracle_fitness_mean": None})
        print(f"{key}: {out[key]} [{time.perf_counter()-t0:.0f}s]", flush=True)
json.dump(out, open("d10/preflight/p7.json", "w"), indent=1)
print("DONE")
