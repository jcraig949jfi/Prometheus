"""Phase 2, step 1: independently reproduce the D-10-local defects.

Charter requirement: do NOT preserve Phase 1's explanations as fact. Every
measurement here runs against the CURRENT d10/lib code, and D2 is measured
INSIDE the real acquire() loop (by observing which genotypes the loop
actually passes to the variation operators), not against a simulated sort.
"""
import sys, json, random, statistics, time
sys.path.insert(0, "d10")
from lib import organizer as og
from lib import progtasks as P
from lib.acquire import acquire
from foundry.engines.gp.stackvm.adapter import StackVMAdapter
from foundry.engines.gp.stackvm import vm
from foundry.engines.base import EngineLimits
from foundry.core.seeds import derive_seed

eng = StackVMAdapter()
LIM = EngineLimits(max_steps=200, timeout_s=5.0)
OUT = {}

# ---------------------------------------------------------------- D1
# Is genotype length directly readable from the supplied encoding?
KA_LEN = bytes([vm.OP["LDR"], 0])          # LDR R0
probe = [(n, og.run_key(KA_LEN, og.artifact_words(bytes(n))))
         for n in (7, 16, 40, 96, 250)]
OUT["D1_LDR_R0_returns_length"] = {
    "pairs": probe, "exact": all(n == k for n, k in probe)}
# how much of the key space does word 0 occupy across a realistic corpus?
genos = [eng.create_random(derive_seed(1, "d1", f"#{i}")) for i in range(400)]
w0 = [og.artifact_words(g)[0] for g in genos]
OUT["D1_word0_equals_len_fraction"] = sum(
    1 for g, w in zip(genos, w0) if w == len(g)) / len(genos)

# ---------------------------------------------------------------- D2
# Measured INSIDE the real acquire loop: which genotypes does the loop
# actually hand to mutate/recombine as parents?
def bounded_ok(p, ps, hi=255, md=16):
    outs = []
    for ins in P._probe_inputs(ps, P.PROBE_N):
        r = P._run(p, ins, P.MAX_REF_STEPS + 1)
        if r.halt != "end" or not (0 <= r.output <= hi):
            return None
        outs.append(r.output)
    return outs if len(set(outs)) >= md else None

tasks = []
for i in range(8000):
    if len(tasks) >= 3:
        break
    rng = random.Random(derive_seed(2, "d2t", f"#{i}"))
    p = bytes(rng.randrange(256) for _ in range(8))
    if bounded_ok(p, 4242) is None:
        continue
    t = P.task_from_program(p, derive_seed(2, "d2c", f"#{i}"), 10, 20, "d2", 0)
    if t:
        tasks.append(t.task)

class ParentWatch:
    """Non-invasive observer: records every genotype the REAL acquire loop
    passes to a variation operator as a parent."""
    def __init__(s, e): s.e = e; s.parents = []; s.steps = 0; s.maxlen = 0
    def info(s): return s.e.info()
    def create_random(s, *a, **k): return s.e.create_random(*a, **k)
    def mutate(s, g, *a, **k):
        s.parents.append(bytes(g)); return s.e.mutate(g, *a, **k)
    def recombine(s, a_, b_, *a, **k):
        s.parents.append(bytes(a_)); s.parents.append(bytes(b_))
        return s.e.recombine(a_, b_, *a, **k)
    def evaluate(s, g, tv, sd, lim):
        s.maxlen = max(s.maxlen, len(g))
        r = s.e.evaluate(g, tv, sd, lim); s.steps += r.resources.steps; return r

def parent_share(lead, n_trials=25, B=240):
    tot = inj = 0
    for ti, t in enumerate(tasks):
        for s in range(n_trials):
            rng = random.Random(derive_seed(3, "d2i", str(lead), f"{ti}", f"{s}"))
            seeds = [bytes([lead]) + bytes(rng.randrange(256) for _ in range(39))
                     for _ in range(4)]
            sset = set(seeds)
            w = ParentWatch(eng)
            acquire(w, t, derive_seed(4, "d2a", f"{ti}", f"{s}"), B, seeds, LIM)
            tot += len(w.parents)
            inj += sum(1 for g in w.parents if g in sset)
    return inj / tot, tot

lo, n_lo = parent_share(0x00)
hi, n_hi = parent_share(0xFF)
OUT["D2_real_loop_parent_share"] = {
    "lead_0x00": round(lo, 5), "lead_0xFF": round(hi, 5),
    "parent_draws_each": n_lo,
    "ratio": (round(lo / hi, 2) if hi > 0 else "inf(hi==0)")}

# ---------------------------------------------------------------- D4
w = ParentWatch(eng)
r = acquire(w, tasks[0], 11, 6400, [], LIM)
OUT["D4_unbounded_growth"] = {
    "max_genotype_bytes_limit": LIM.max_genotype_bytes,
    "observed_max_genotype_len": w.maxlen,
    "vm_steps_total": w.steps,
    "steps_per_eval": round(w.steps / max(r.evaluations, 1), 1),
    "harness_bounds_length": False}

# ---------------------------------------------------------------- D7
import inspect
src = inspect.getsource(og.run_key)
OUT["D7_walltime_in_key_path"] = {
    "run_key_passes_timeout_s": "timeout_s=" in src,
    "vm_can_halt_on_wall": '"wall"' in inspect.getsource(vm.run_program),
    "key_semantics_load_dependent": "timeout_s=" in src}

print(json.dumps(OUT, indent=1))
json.dump(OUT, open("d10/repair/before_repair.json", "w"), indent=1)
