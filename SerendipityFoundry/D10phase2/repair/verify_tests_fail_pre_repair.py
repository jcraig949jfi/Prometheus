"""Charter 4.3: demonstrate each regression test FAILS against pre-repair D-10.

Loads the archived pre-repair modules under alias names and re-runs the same
predicates the regression suite asserts.
"""
import sys, importlib.util, random, inspect, hashlib
sys.path.insert(0, "d10")
from foundry.engines.gp.stackvm.adapter import StackVMAdapter
from foundry.engines.gp.stackvm import vm
from foundry.engines.base import EngineLimits
from foundry.core.seeds import derive_seed
from lib import progtasks as P

def load(alias, path):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[alias] = m
    spec.loader.exec_module(m)
    return m

old_og = load("old_og", "d10/repair/organizer_pre_repair.py")
old_A  = load("old_A",  "d10/repair/acquire_pre_repair.py")
eng = StackVMAdapter()
LIM = EngineLimits(max_steps=200, timeout_s=5.0)
res = []

def rec(name, predicate_holds_after_repair):
    res.append((name, predicate_holds_after_repair))
    verdict = "FAILS pre-repair (GOOD)" if not predicate_holds_after_repair \
        else "PASSES pre-repair (test is NOT discriminating)"
    print(f"{name:62s} {verdict}")

# D1
KA = bytes([vm.OP["LDR"], 0])
keys = [old_og.run_key(KA, old_og.artifact_words(bytes(n)))
        for n in (7,16,40,96,250)]
rec("D1 LDR R0 no longer returns genotype length",
    not all(n==k for n,k in zip((7,16,40,96,250), keys)))
rng = random.Random(0)
gs = [bytes(rng.randrange(256) for _ in range(rng.randint(4,200))) for _ in range(400)]
w0 = sum(1 for g in gs if old_og.artifact_words(g)[:1] == [len(g)])
rec("D1 word0 is not the length for a random genotype sample", w0 <= 2)

# D7
src = inspect.getsource(old_og.run_key)
rec("D7 key path uses the deterministic step meter, not a 5s wall",
    "timeout_s=5.0" not in src)
rec("D7 a wall halt raises instead of returning a key",
    hasattr(old_og, "NondeterministicKey"))

# D4
rec("D4 harness declares a hard genotype bound",
    hasattr(old_A, "MAX_GENOTYPE_BYTES"))
rec("D4 AcqResult carries a first-class VM-step meter",
    "vm_steps" in old_A.AcqResult.__dataclass_fields__)

# D2
rec("D2 tie-break token is a seeded hash of the genotype",
    hasattr(old_A, "_tiebreak"))
rec("D2 population sort no longer uses genotype bytes as the key",
    "(-m[1], m[0])" not in inspect.getsource(old_A.acquire))
rec("D2 tournament no longer breaks ties by list position",
    "items[i][2]" in inspect.getsource(old_A._tournament))

# D2 behavioural, in the real pre-repair loop
class W:
    def __init__(s,e): s.e=e; s.parents=[]
    def info(s): return s.e.info()
    def create_random(s,*a,**k): return s.e.create_random(*a,**k)
    def mutate(s,g,*a,**k): s.parents.append(bytes(g)); return s.e.mutate(g,*a,**k)
    def recombine(s,a_,b_,*a,**k):
        s.parents += [bytes(a_), bytes(b_)]; return s.e.recombine(a_,b_,*a,**k)
    def evaluate(s,*a,**k): return s.e.evaluate(*a,**k)

tasks=[]
for i in range(8000):
    if len(tasks)>=3: break
    r=random.Random(derive_seed(7,"d2t",f"#{i}"))
    p=bytes(r.randrange(256) for _ in range(8))
    ok=True; outs=[]
    for ins in P._probe_inputs(4242,P.PROBE_N):
        rr=P._run(p,ins,P.MAX_REF_STEPS+1)
        if rr.halt!="end" or not (0<=rr.output<=255): ok=False; break
        outs.append(rr.output)
    if not ok or len(set(outs))<16: continue
    t=P.task_from_program(p,derive_seed(7,"d2tc",f"#{i}"),10,20,"d2t",0)
    if t: tasks.append(t.task)

def share(lead,n=25,B=240):
    tot=inj=0
    for ti,t in enumerate(tasks):
        for s in range(n):
            rr=random.Random(derive_seed(3,"d2i",str(lead),f"{ti}",f"{s}"))
            seeds=[bytes([lead])+bytes(rr.randrange(256) for _ in range(39)) for _ in range(4)]
            ss=set(seeds); w=W(eng)
            old_A.acquire(w,t,derive_seed(4,"d2a",f"{ti}",f"{s}"),B,seeds,LIM)
            tot+=len(w.parents); inj+=sum(1 for g in w.parents if g in ss)
    return inj/tot
lo,hi=share(0x00),share(0xFF)
ratio=(lo/hi) if hi>0 else float("inf")
rec("D2 leading byte no longer swings injected parent share", 0.5<=ratio<=2.0)
print(f"\n   pre-repair real-loop share: 0x00={lo:.5f} 0xFF={hi:.5f} ratio={ratio:.2f}")

bad=[n for n,ok in res if ok]
print()
print(f"Discriminating tests: {len(res)-len(bad)}/{len(res)} fail against pre-repair code.")
if bad: print("NON-DISCRIMINATING (passed pre-repair):", bad)
