"""Phase 2: rebuild the FROZEN Phase-1 operating point with the repaired
harness, and split evaluation material into a DEV set (for PP2 construction)
and a held-out GATE set (never touched until the frozen final evaluation).

Operating point is Phase 1's provisioned cell, unchanged:
  L_REF=8  N_MUT=1  N_TRAIN=10  N_TEST=20  outputs in [0,255]  >=16 distinct
  F_SEEN=8 families  N_HIST_MEM=4  N_RESTART=3  B_HIST=12800
  corpus = final populations + solvers + uniform subsample (N_SUB=2000), deduped
  k=4  B_EVAL=400  POP_SIZE=24  N_EVAL_SEEDS=4
The ONLY addition is that eval members are split DEV / GATE (charter 11).
"""
import sys, json, random, time
sys.path.insert(0, "d10")
from lib import progtasks as P
from lib.acquire import acquire, MAX_GENOTYPE_BYTES
from foundry.engines.gp.stackvm.adapter import StackVMAdapter
from foundry.engines.base import EngineLimits
from foundry.core.seeds import derive_seed

eng = StackVMAdapter()
LIM = EngineLimits(max_steps=200, timeout_s=5.0)
L_REF, N_MUT = 8, 1
OUT_HI, MIN_DISTINCT = 255, 16
N_TRAIN, N_TEST = 10, 20
F_SEEN = 8
N_HIST_MEM, N_DEV_MEM, N_GATE_MEM = 4, 3, 3
N_RESTART, B_HIST, N_SUB = 3, 12800, 2000
GEN_SEED = 8181                     # same family-generation seed as Phase 1


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
                                    N_TRAIN, N_TEST, f"f{f}", m)
            if t is not None:
                tasks.append(t)
        if len(tasks) >= n_mem:
            fams.append({"root": root, "tasks": tasks})
    return fams


t0 = time.perf_counter()
NM = N_HIST_MEM + N_DEV_MEM + N_GATE_MEM
fams = make_families(GEN_SEED, F_SEEN, NM)
print(f"families={len(fams)} members_each={NM} [{time.perf_counter()-t0:.0f}s]",
      flush=True)
assert len(fams) == F_SEEN, f"only {len(fams)} families"

hist, dev, gate = [], [], []
for fi, fam in enumerate(fams):
    ts = fam["tasks"]
    for t in ts[:N_HIST_MEM]:
        hist.append((fi, t))
    for t in ts[N_HIST_MEM:N_HIST_MEM + N_DEV_MEM]:
        dev.append((fi, t))
    for t in ts[N_HIST_MEM + N_DEV_MEM:NM]:
        gate.append((fi, t))
print(f"history_tasks={len(hist)} dev_tasks={len(dev)} gate_tasks={len(gate)}",
      flush=True)


class Collect:
    def __init__(s, e): s.e = e; s.seen = []
    def info(s): return s.e.info()
    def create_random(s, *a, **k): return s.e.create_random(*a, **k)
    def mutate(s, *a, **k): return s.e.mutate(*a, **k)
    def recombine(s, *a, **k): return s.e.recombine(*a, **k)
    def evaluate(s, g, tv, sd, lim):
        s.seen.append(bytes(g)); return s.e.evaluate(g, tv, sd, lim)


col = Collect(eng)
finals, solvers = [], []
hist_solves = 0
hist_evals = hist_steps = hist_trunc = 0
prov = []                     # per corpus-admission provenance, oracle-side
for hi, (fi, pt) in enumerate(hist):
    for r_i in range(N_RESTART):
        before = len(col.seen)
        r = acquire(col, pt.task, derive_seed(91, "hist", f"{hi}", f"{r_i}"),
                    B_HIST, [], LIM)
        hist_solves += r.solved_test
        hist_evals += r.evaluations
        hist_steps += r.vm_steps
        hist_trunc += r.n_truncated
        for g in r.final_population:
            finals.append((g, fi, hi, r_i, "final_population"))
        if r.solver_genotype is not None:
            solvers.append((r.solver_genotype, fi, hi, r_i, "solver"))
    print(f"  history {hi+1}/{len(hist)} [{time.perf_counter()-t0:.0f}s]",
          flush=True)

all_art = col.seen
rng = random.Random(derive_seed(92, "sub"))
sub_idx = [rng.randrange(len(all_art)) for _ in range(N_SUB)]
sub = [(all_art[i], -1, -1, -1, "subsample") for i in sub_idx]

seen_bytes, corpus, corpus_prov = set(), [], []
for g, fi, hi, ri, src in solvers + finals + sub:
    if g in seen_bytes:
        continue
    seen_bytes.add(g)
    corpus.append(g)
    corpus_prov.append({"family": fi, "hist_task": hi, "restart": ri,
                        "source": src, "len": len(g)})

out = {
    "operating_point": {
        "L_REF": L_REF, "N_MUT": N_MUT, "N_TRAIN": N_TRAIN, "N_TEST": N_TEST,
        "OUT_HI": OUT_HI, "MIN_DISTINCT": MIN_DISTINCT, "F_SEEN": F_SEEN,
        "N_HIST_MEM": N_HIST_MEM, "N_DEV_MEM": N_DEV_MEM,
        "N_GATE_MEM": N_GATE_MEM, "N_RESTART": N_RESTART, "B_HIST": B_HIST,
        "N_SUB": N_SUB, "GEN_SEED": GEN_SEED,
        "MAX_GENOTYPE_BYTES": MAX_GENOTYPE_BYTES},
    "history": {"trials": len(hist) * N_RESTART, "test_solves": hist_solves,
                "solver_genotypes": len(solvers),
                "all_artifacts": len(all_art), "evaluations": hist_evals,
                "vm_steps": hist_steps, "truncations": hist_trunc},
    "corpus_size": len(corpus),
    "corpus_hex": [g.hex() for g in corpus],
    "corpus_prov": corpus_prov,
    "dev_tasks": [{"family": fi, "ref": pt.reference.hex(),
                   "train": pt.task.train_cases, "test": pt.task.test_cases}
                  for fi, pt in dev],
    "gate_tasks": [{"family": fi, "ref": pt.reference.hex(),
                    "train": pt.task.train_cases, "test": pt.task.test_cases}
                   for fi, pt in gate],
}
json.dump(out, open("d10/phase2/dataset.json", "w"))
print(json.dumps({k: v for k, v in out.items()
                  if k not in ("corpus_hex", "corpus_prov", "dev_tasks",
                               "gate_tasks")}, indent=1))
print(f"DONE [{time.perf_counter()-t0:.0f}s]")
