"""Phase 2 charter section 6: query-side firewall recheck after repairs.

Each check is mechanical. The point is not "is the forbidden field absent"
but "does the forbidden quantity change the KQ input".
"""
import sys, random
sys.path.insert(0, ".")
sys.path.insert(0, "d10")
from lib import organizer as og
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


TRAIN = [([i, i + 1], (i * 7 + 3) % 256) for i in range(10)]

base = ExactTask(train_cases=[(list(a), b) for a, b in TRAIN],
                 test_cases=[([100, 1], 55)],
                 admin_metadata={"family_id": "fA", "name": "alpha"},
                 provenance={"family_id": "fA", "reference_len": 8,
                             "seed": 1, "member_index": 0, "difficulty": 3})
# same TRAIN, everything oracle-side different
other = ExactTask(train_cases=[(list(a), b) for a, b in TRAIN],
                  test_cases=[([200, 9], 77), ([201, 9], 78)],
                  admin_metadata={"family_id": "fZ", "name": "omega"},
                  provenance={"family_id": "fZ", "reference_len": 40,
                              "seed": 999, "member_index": 7, "difficulty": 1})

w1 = og.evidence_words(base.evidence())
w2 = og.evidence_words(other.evidence())
check("identical train evidence -> identical KQ input, "
      "despite different oracle identity", w1 == w2)
check("task_id genuinely differs between the two", base.task_id != other.task_id)

# task_id inaccessible: 300 random KQ programs must agree
n_id = sum(1 for s in range(300)
           if og.run_key(eng.create_random(derive_seed(21, "qf", f"#{s}")), w1)
           == og.run_key(eng.create_random(derive_seed(21, "qf", f"#{s}")), w2))
check("task_id is inaccessible to 300 random KQ programs", n_id == 300,
      f"{n_id}/300")

# test examples inaccessible: vary ONLY the test split
n_words = len(w1)
check("test examples do not appear in the KQ input at all",
      w1 == og.evidence_words(other.evidence()) and n_words == 2 + 8 * 5,
      f"n_words={n_words}")

# family / generator params / difficulty inaccessible
check("family identity is not in the KQ input",
      "fA" not in str(w1) and "fZ" not in str(w1))
check("generator parameters / difficulty are not in the KQ input",
      og.evidence_words(base.evidence()) == og.evidence_words(other.evidence()))

# chronology: TaskEvidence has no temporal field at all
ev = base.evidence()
check("TaskEvidence exposes no chronology field",
      set(ev.model_dump().keys()) == {"schema_version", "task_id",
                                      "train_examples", "value_kinds"},
      str(sorted(ev.model_dump().keys())))

# structural: evidence_words reads only train_examples
import inspect
src = inspect.getsource(og.evidence_words)
body = src.split('"""')[-1]
for forbidden in ("task_id", "test", "value_kinds", "admin", "provenance"):
    check(f"evidence_words body never references '{forbidden}'",
          forbidden not in body)

# extra="forbid" still holds on the learner surface
from foundry.core.schemas import TaskEvidence
try:
    TaskEvidence(task_id="x", train_examples=[], value_kinds=[],
                 oracle_distance=0.5)
    ok = False
except Exception:
    ok = True
check("TaskEvidence still rejects injected oracle fields", ok)

print()
print("RESULT:", "ALL PASS" if not fails else f"{len(fails)} FAILURES: {fails}")
sys.exit(1 if fails else 0)
