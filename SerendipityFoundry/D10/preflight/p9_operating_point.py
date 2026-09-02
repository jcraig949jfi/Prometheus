"""P9: the operating point and the PP1 ceiling that the power calculation needs.

Runs the real pipeline at L_REF=8 with the declared corpus rule
  C = union(final populations) + all history solvers + uniform subsample
and measures, on held-out members of the SAME families:
  N       cold, k fresh random genotypes
  U       k uniformly sampled corpus artifacts
  PP1     the k corpus artifacts with the highest TRUE train fitness (oracle)
Also reports the train/test generalisation gap at two train-set sizes.
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
L_REF, N_MUT = 8, 1
F_SEEN = 8
N_HIST_MEM, N_EVAL_MEM = 3, 3
N_RESTART = 2
B_HIST = 3200
N_SUB = 2000
K = 4
N_EVAL_SEEDS = 4
N_TRAIN = int(sys.argv[1]) if len(sys.argv) > 1 else 6
B_EVAL = int(sys.argv[2]) if len(sys.argv) > 2 else 400
if len(sys.argv) > 3: B_HIST = int(sys.argv[3])
if len(sys.argv) > 4: N_HIST_MEM = int(sys.argv[4])
if len(sys.argv) > 5: N_RESTART = int(sys.argv[5])
TAG = sys.argv[6] if len(sys.argv) > 6 else f"n{N_TRAIN}_B{B_EVAL}"


def bounded_ok(prog, ps):
    outs = []
    for ins in P._probe_inputs(ps, P.PROBE_N):
        r = P._run(prog, ins, P.MAX_REF_STEPS + 1)
        if r.halt != "end" or not (0 <= r.output <= OUT_HI):
            return None
        outs.append(r.output)
    return outs if len(set(outs)) >= MIN_DISTINCT else None


def make_families(gseed, n_need, n_mem):
    fams = []
    for f in range(3000):
        if len(fams) >= n_need:
            break
        root = None
        for i in range(4000):
            rng = random.Random(derive_seed(gseed, "root", f"#{f}", f"#{i}"))
            p = bytes(rng.randrange(256) for _ in range(L_REF))
            if bounded_ok(p, derive_seed(gseed, "probe")) is not None:
                root = p
                break
        if root is None:
            continue
        ro = bounded_ok(root, derive_seed(gseed, "probe"))
        tasks = []
        for m in range(n_mem * 30):
            if len(tasks) >= n_mem:
                break
            g = eng.mutate(root, derive_seed(gseed, "mut", f"#{f}", f"#{m}"))
            o = bounded_ok(g, derive_seed(gseed, "probe"))
            if o is None or o == ro:
                continue
            t = P.task_from_program(g, derive_seed(gseed, "case", f"#{f}", f"#{m}"),
                                    N_TRAIN, 20, f"f{f}", m)
            if t is not None:
                tasks.append(t)
        if len(tasks) >= n_mem:
            fams.append(tasks)
    return fams


t0 = time.perf_counter()
fams = make_families(8181, F_SEEN, N_HIST_MEM + N_EVAL_MEM)
print(f"families={len(fams)} [{time.perf_counter()-t0:.0f}s]", flush=True)
if len(fams) < F_SEEN:
    print(json.dumps({"error": f"only {len(fams)} families"}))
    sys.exit(0)

hist = [(fi, t) for fi, ts in enumerate(fams) for t in ts[:N_HIST_MEM]]
evals = [(fi, t) for fi, ts in enumerate(fams) for t in ts[N_HIST_MEM:]]


class Collect:
    def __init__(s, e): s.e = e; s.seen = []
    def info(s): return s.e.info()
    def create_random(s, *a, **k): return s.e.create_random(*a, **k)
    def mutate(s, *a, **k): return s.e.mutate(*a, **k)
    def recombine(s, *a, **k): return s.e.recombine(*a, **k)
    def evaluate(s, g, tv, sd, lim):
        s.seen.append(bytes(g)); return s.e.evaluate(g, tv, sd, lim)


col = Collect(eng)
finals, solvers, hist_solves = [], [], 0
for hi, (fi, pt) in enumerate(hist):
    for r_i in range(N_RESTART):
        r = acquire(col, pt.task, derive_seed(91, "hist", f"{hi}", f"{r_i}"),
                    B_HIST, [], LIM)
        hist_solves += r.solved_test
        finals.extend(r.final_population)
        if r.solver_genotype is not None:
            solvers.append(r.solver_genotype)
all_art = col.seen
rng = random.Random(derive_seed(92, "sub"))
sub = [all_art[rng.randrange(len(all_art))] for _ in range(N_SUB)]
corpus = list(dict.fromkeys(finals + solvers + sub))
print(f"history_trials={len(hist)*N_RESTART} history_test_solves={hist_solves} "
      f"n_solver_genotypes={len(solvers)} all_artifacts={len(all_art)} "
      f"corpus={len(corpus)} [{time.perf_counter()-t0:.0f}s]", flush=True)


def train_fit(g, task):
    r = eng.evaluate(g, task.machine_view(), 0, LIM)
    return r.fitness or 0.0


acc = {"N": [0, 0], "U": [0, 0], "PP1": [0, 0]}
tr = {"N": 0, "U": 0, "PP1": 0}
for ei, (fi, pt) in enumerate(evals):
    order = sorted(range(len(corpus)), key=lambda i: -train_fit(corpus[i], pt.task))
    oracle = [corpus[i] for i in order[:K]]
    for s in range(N_EVAL_SEEDS):
        sd = derive_seed(93, "eval", f"{ei}", f"{s}")
        urng = random.Random(derive_seed(94, "u", f"{ei}", f"{s}"))
        unif = [corpus[urng.randrange(len(corpus))] for _ in range(K)]
        for cond, seeds in (("N", []), ("U", unif), ("PP1", oracle)):
            r = acquire(eng, pt.task, sd, B_EVAL, seeds, LIM)
            acc[cond][0] += r.solved_test
            tr[cond] += r.solved_train
            acc[cond][1] += 1

out = {"N_TRAIN": N_TRAIN, "B_EVAL": B_EVAL, "B_HIST": B_HIST,
       "L_REF": L_REF, "n_families": len(fams),
       "history_trials": len(hist) * N_RESTART,
       "history_test_solves": hist_solves,
       "n_solver_genotypes": len(solvers),
       "all_history_artifacts": len(all_art), "corpus_size": len(corpus),
       "n_eval_tasks": len(evals), "n_per_cond": acc["N"][1],
       "test": {c: round(v[0] / v[1], 4) for c, v in acc.items()},
       "train": {c: round(tr[c] / acc[c][1], 4) for c in tr}}
print(json.dumps(out, indent=1))
json.dump(out, open(f"d10/preflight/p9_{TAG}.json", "w"), indent=1)
print("DONE")
