"""Read-only probe (bake-off design evidence). Imports TFS-1 unmodified. Measures how much of the syntactic
enumeration class is semantically redundant on a probe input set, and shows that the existing OE prune log already
emits (redundant term -> representative) pairs, i.e. candidate equations. Bounded to small sizes."""
import sys, time, random, json, collections
sys.path.insert(0, sys.argv[1])            # .../roles/Aphrodite/beta04
from tfs1 import core as C
from tfs1.enum import Enumerator

MAXN = int(sys.argv[2]) if len(sys.argv) > 2 else 6
rng = random.Random("bakeoff-probe-v1")
inputs = [[rng.randrange(-9, 10) for _ in range(rng.randrange(3, 9))] for _ in range(8)]
out = {"inputs": inputs, "max_size": MAXN, "rows": []}

t0 = time.process_time()
E0 = Enumerator(None, comm_canon=False)
E1 = Enumerator(None, comm_canon=True)
E2 = Enumerator(None, comm_canon=True, oe=True, oe_inputs=inputs)
log = []
E2.oe_pruned_log = log
for T in ("Int", "List", "Bool"):
    for n in range(1, MAXN + 1):
        raw = len(E0.terms(T, (), n)); comm = len(E1.terms(T, (), n)); oe = len(E2.terms(T, (), n))
        out["rows"].append({"type": T, "size": n, "syntactic": raw, "comm_canon": comm, "oe_kept": oe})
        print(T, n, raw, comm, oe, flush=True)
out["oe_stats"] = dict(E2.oe_stats)
out["cpu_s"] = round(time.process_time() - t0, 2)
closed = [r for r in log if r[1] == ()]
out["pruned_pairs_total"] = len(log)
out["pruned_pairs_closed_ctx"] = len(closed)
bysize = collections.Counter(r[2] for r in closed)
out["pruned_closed_by_size"] = dict(sorted(bysize.items()))
out["examples_closed"] = [(r[3], r[4]) for r in closed if r[2] <= 3][:40]
lam = [r for r in log if r[1] != ()]
out["examples_binder_ctx"] = [(r[1], r[3], r[4]) for r in lam if r[2] <= 3][:25]
print(json.dumps({k: v for k, v in out.items() if k not in ("rows", "inputs")}, indent=1))
json.dump(out, open(sys.argv[3], "w"), indent=1)
