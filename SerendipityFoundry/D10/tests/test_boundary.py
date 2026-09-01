"""Structural tests of the D-10 information boundary. These must pass before
the preregistration may be frozen."""
import sys, random
sys.path.insert(0, ".")
sys.path.insert(0, "d10")

from lib import organizer as org
from lib import audit
from lib import progtasks as P
from foundry.tasks.base import ExactTask
from foundry.engines.gp.stackvm.adapter import StackVMAdapter
from foundry.core.seeds import derive_seed

eng = StackVMAdapter()
fails = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        fails.append(name)


# --- E3: task_id must not influence a query key --------------------------
train = [([1, 2], 7), ([3, 4], 11), ([5, 6], 15),
         ([7, 8], 19), ([9, 10], 23), ([11, 12], 27)]
a = ExactTask(train_cases=list(train), test_cases=[([100, 1], 201)])
b = ExactTask(train_cases=list(train), test_cases=[([200, 1], 401)])
check("task_ids differ for identical train splits", a.task_id != b.task_id)
n_id, n_tot = 0, 0
for s in range(200):
    g = eng.create_random(derive_seed(5, "diff", f"#{s}"))
    ka = org.query_key(g, a.evidence())
    kb = org.query_key(g, b.evidence())
    n_tot += 1
    n_id += int(ka == kb)
check("query keys identical across differing task_ids", n_id == n_tot,
      f"{n_id}/{n_tot}")

# --- artifact_words must not depend on execution history -----------------
w1 = org.artifact_words(b"\x01\x02\x03")
w2 = org.artifact_words(b"\x01\x02\x03")
check("artifact_words is a pure function of bytes", w1 == w2)

# --- source audit ---------------------------------------------------------
try:
    hits = audit.organizer_source_audit(".")
except Exception as e:                                   # noqa: BLE001
    hits = [{"error": str(e)}]
check("no forbidden identifier in the organizer input path", hits == [], str(hits))

# --- total decode: every byte string is a legal organizer ----------------
bad = 0
rng = random.Random(0)
for _ in range(2000):
    n = rng.randrange(0, 40)
    g = bytes(rng.randrange(256) for _ in range(n))
    try:
        ka, kq = org.decode(g)
        org.run_key(ka, org.artifact_words(b"\x00\x01"))
    except Exception:                                    # noqa: BLE001
        bad += 1
check("every byte string decodes and runs as an organizer", bad == 0, f"{bad} failures")

# --- scramble preserves the key multiset ---------------------------------
ids = [f"a{i}" for i in range(100)]
genos = [eng.create_random(i) for i in range(100)]
o = org.build_organization(eng.create_random(1004), ids, genos)
sc = o.scrambled(7)
check("scramble preserves the key multiset", sorted(o.keys) == sorted(sc.keys))
check("scramble preserves granularity",
      o.stats()["n_distinct_keys"] == sc.stats()["n_distinct_keys"])
check("scramble preserves key entropy",
      abs(o.stats()["key_entropy_bits"] - sc.stats()["key_entropy_bits"]) < 1e-9)

# --- retrieval determinism -------------------------------------------------
r1 = org.retrieve(o, 12345, 4, 99)
r2 = org.retrieve(o, 12345, 4, 99)
check("retrieval is deterministic", r1 == r2)

print()
print("RESULT:", "ALL PASS" if not fails else f"{len(fails)} FAILURES: {fails}")
sys.exit(1 if fails else 0)
