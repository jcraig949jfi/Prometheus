"""Phase 2 regression tests for the D-10-local repairs D1, D2, D4, D7.

Each test states the PRE-REPAIR behaviour it would have failed against.
    Run via the venv python; see PHASE2 report for the command.
"""
import sys, random, hashlib, inspect, statistics
sys.path.insert(0, ".")
sys.path.insert(0, "d10")

from lib import organizer as og
from lib import acquire as A
from lib import progtasks as P
from foundry.engines.gp.stackvm.adapter import StackVMAdapter
from foundry.engines.gp.stackvm import vm
from foundry.engines.base import EngineLimits
from foundry.core.seeds import derive_seed

eng = StackVMAdapter()
LIM = EngineLimits(max_steps=200, timeout_s=5.0)
fails = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        fails.append(name)


# ===================================================== D1
# PRE-REPAIR: LDR R0 returned len(g) exactly for every genotype.
KA_LEN = bytes([vm.OP["LDR"], 0])
keys = [og.run_key(KA_LEN, og.artifact_words(bytes(n)))
        for n in (7, 16, 40, 96, 250)]
check("D1 LDR R0 no longer returns genotype length",
      not all(n == k for n, k in zip((7, 16, 40, 96, 250), keys)),
      f"keys={keys}")

rng = random.Random(0)
gs = [bytes(rng.randrange(256) for _ in range(rng.randint(4, 200)))
      for _ in range(400)]
w0_is_len = sum(1 for g in gs if og.artifact_words(g)[:1] == [len(g)])
check("D1 word0 is not the length for a random genotype sample",
      w0_is_len <= 2, f"{w0_is_len}/400 coincidences")

check("D1 word0 is genuine genotype content",
      og.artifact_words(b"\x01\x02\x03")[0]
      == int.from_bytes(b"\x01\x02\x03".ljust(8, b"\x00"), "little"))

# ===================================================== D7
# PRE-REPAIR: run_key passed timeout_s=5.0, so keys were load-dependent.
src = inspect.getsource(og._run_key_vm)
check("D7 key path uses the deterministic step meter, not a 5s wall",
      "KEY_WALL_S" in src and "timeout_s=5.0" not in src)
check("D7 wall backstop cannot bind before the step cap",
      og.KEY_WALL_S > og.KEY_MAX_STEPS * 1.0,
      f"KEY_WALL_S={og.KEY_WALL_S} KEY_MAX_STEPS={og.KEY_MAX_STEPS}")
check("D7 a wall halt raises instead of returning a key",
      issubclass(og.NondeterministicKey, RuntimeError))
# determinism under repetition
prog = eng.create_random(4242)
ws = og.artifact_words(eng.create_random(99))
check("D7 identical inputs give identical keys over 200 repeats",
      len({og.run_key(prog, ws) for _ in range(200)}) == 1)

# ===================================================== D4
check("D4 harness declares a hard genotype bound",
      isinstance(A.MAX_GENOTYPE_BYTES, int) and A.MAX_GENOTYPE_BYTES > 0,
      f"MAX_GENOTYPE_BYTES={A.MAX_GENOTYPE_BYTES}")
check("D4 bound is far below the Foundry default it replaces",
      A.MAX_GENOTYPE_BYTES < LIM.max_genotype_bytes)
check("D4 AcqResult carries a first-class VM-step meter",
      "vm_steps" in A.AcqResult.__dataclass_fields__)


def _task(tag, n=1):
    out = []
    for i in range(8000):
        if len(out) >= n:
            break
        r = random.Random(derive_seed(7, tag, f"#{i}"))
        p = bytes(r.randrange(256) for _ in range(8))
        ok = True
        outs = []
        for ins in P._probe_inputs(4242, P.PROBE_N):
            rr = P._run(p, ins, P.MAX_REF_STEPS + 1)
            if rr.halt != "end" or not (0 <= rr.output <= 255):
                ok = False
                break
            outs.append(rr.output)
        if not ok or len(set(outs)) < 16:
            continue
        t = P.task_from_program(p, derive_seed(7, tag + "c", f"#{i}"),
                                10, 20, tag, 0)
        if t:
            out.append(t.task)
    return out


tk = _task("d4t", 1)[0]
r = A.acquire(eng, tk, 11, 3000, [], LIM)
check("D4 vm_steps is metered and positive", r.vm_steps > 0,
      f"vm_steps={r.vm_steps} steps/eval={r.vm_steps/max(r.evaluations,1):.1f}")
check("D4 no genotype exceeds the bound",
      all(len(g) <= A.MAX_GENOTYPE_BYTES for g in r.final_population),
      f"max_len={max((len(g) for g in r.final_population), default=0)}")

# ===================================================== D2
# PRE-REPAIR (measured in the real loop): injected genotypes occupied
# 6.137% of parent slots at leading byte 0x00 vs 0.217% at 0xFF -- 28.3x.
class ParentWatch:
    def __init__(s, e): s.e = e; s.parents = []
    def info(s): return s.e.info()
    def create_random(s, *a, **k): return s.e.create_random(*a, **k)
    def mutate(s, g, *a, **k): s.parents.append(bytes(g)); return s.e.mutate(g, *a, **k)
    def recombine(s, a_, b_, *a, **k):
        s.parents.append(bytes(a_)); s.parents.append(bytes(b_))
        return s.e.recombine(a_, b_, *a, **k)
    def evaluate(s, *a, **k): return s.e.evaluate(*a, **k)


tasks3 = _task("d2t", 3)


def share(lead, n_trials=25, B=240):
    tot = inj = 0
    for ti, t in enumerate(tasks3):
        for s in range(n_trials):
            rr = random.Random(derive_seed(3, "d2i", str(lead), f"{ti}", f"{s}"))
            seeds = [bytes([lead]) + bytes(rr.randrange(256) for _ in range(39))
                     for _ in range(4)]
            sset = set(seeds)
            w = ParentWatch(eng)
            A.acquire(w, t, derive_seed(4, "d2a", f"{ti}", f"{s}"), B, seeds, LIM)
            tot += len(w.parents)
            inj += sum(1 for g in w.parents if g in sset)
    return inj / tot


lo, hi = share(0x00), share(0xFF)
ratio = (lo / hi) if hi > 0 else float("inf")
check("D2 leading byte no longer swings injected-material parent share",
      0.5 <= ratio <= 2.0,
      f"0x00={lo:.5f} 0xFF={hi:.5f} ratio={ratio:.2f} (pre-repair 28.3)")

check("D2 tie-break token is a seeded hash of the genotype",
      A._tiebreak(5, b"abc") == hashlib.sha256(
          (5).to_bytes(8, "big") + b"\x00" + b"abc").digest())
check("D2 tie-break depends on the trial seed",
      A._tiebreak(5, b"abc") != A._tiebreak(6, b"abc"))
check("D2 population sort no longer uses genotype bytes as the key",
      "m[2]" in inspect.getsource(A.acquire)
      and "(-m[1], m[0])" not in inspect.getsource(A.acquire))
check("D2 tournament no longer breaks ties by list position",
      "items[i][2]" in inspect.getsource(A._tournament))

print()
print("RESULT:", "ALL PASS" if not fails else f"{len(fails)} FAILURES: {fails}")
sys.exit(1 if fails else 0)
