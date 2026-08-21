"""Replicate the checkpoint pin's mutation score by an INDEPENDENT mechanism (soak P38).

P37 closed the contamination question but logged WITHHELD: re-running the same
script proves non-contamination, not correctness -- a probe carrying a logic error
reproduces that error faithfully.

The published method (P30/P31) edits run_zoo_matrix.py in place and runs pytest.
Its failure modes are: source-edit errors, stale bytecode, pytest collection, and
restore bugs. This method shares NONE of them: each mutation is a SUBCLASS whose
__init__ reimplements the loader variant, and the pin's assertions are evaluated
in-process. No file is touched.

Agreement between two mechanisms with disjoint failure modes is replication.
Disagreement means at least one is wrong.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "harmonia/experiments")
from run_zoo_matrix import Checkpoint  # noqa: E402

REQ = ("examinee", "probe_id")


def _loader(guard):
    """Build a Checkpoint variant whose load loop uses `guard(rec) -> bool` (skip?)."""
    class V(Checkpoint):
        def __init__(self, path):
            self.path = Path(path)
            self.done, self.records = set(), []
            self.n_skipped_malformed = 0
            for line in self.path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                skip, count = guard(rec)
                if skip:
                    if count:
                        self.n_skipped_malformed += 1
                    continue
                self.records.append(rec)
                self.done.add((rec["examinee"], rec["probe_id"]))
            self._fh = open(self.path, "a", encoding="utf-8")
    return V


VARIANTS = {
 "correct (guard intact)":
    lambda r: ((not isinstance(r, dict) or any(k not in r for k in REQ)), True),
 "M1 guard removed entirely":
    lambda r: (False, False),
 "M2 isinstance dropped":
    lambda r: ((any(k not in r for k in REQ)), True),
 "M3 probe_id check dropped":
    lambda r: ((not isinstance(r, dict) or "examinee" not in r), True),
 "M4 skips silently, no counter":
    lambda r: ((not isinstance(r, dict) or any(k not in r for k in REQ)), False),
}

# The ADOPTED pin's fixture and assertions, transcribed from
# harmonia/experiments/test_checkpoint_robustness.py (read, not imported, so the
# assertions are exercised against my variants rather than the real class).
LINES = [json.dumps({"examinee": "a", "probe_id": "p1"}),
         '{"truncat',
         json.dumps({"wrong": "shape"}),
         json.dumps({}),
         json.dumps({"unrelated": 1, "keys": 2}),
         json.dumps([1, 2, 3]),
         json.dumps("just a string"),
         json.dumps(["examinee", "probe_id"]),
         json.dumps({"examinee": "only-half"}),
         json.dumps({"examinee": "b", "probe_id": "p2"})]


def pin_assertions(ck):
    """Returns None if the pin PASSES, else the first assertion that failed."""
    if len(ck.records) != 2:
        return f"len(records)=={len(ck.records)} != 2"
    if ck.done != {("a", "p1"), ("b", "p2")}:
        return f"done=={ck.done}"
    n = getattr(ck, "n_skipped_malformed", 0)
    if n != 7:
        return f"n_skipped_malformed=={n} != 7"
    return None


d = Path(tempfile.mkdtemp()) / "ck.jsonl"
d.write_text("\n".join(LINES) + "\n", encoding="utf-8")

PUBLISHED = {"M1 guard removed entirely": "CAUGHT", "M2 isinstance dropped": "CAUGHT",
             "M3 probe_id check dropped": "CAUGHT", "M4 skips silently, no counter": "CAUGHT"}

print(f"{'variant':32s} {'pin verdict':>12s}  {'published':>10s}  agree?   first failure")
print("-" * 104)
agree = disagree = 0
for label, guard in VARIANTS.items():
    try:
        ck = _loader(guard)(d)
        fail = pin_assertions(ck)
        ck.close()
    except Exception as e:
        fail = f"RAISED {type(e).__name__}: {e}"
    verdict = "CAUGHT" if fail else "passes"
    if label in PUBLISHED:
        ok = verdict == PUBLISHED[label]
        agree += ok; disagree += not ok
        mark = "yes" if ok else "*** NO ***"
        print(f"{label:32s} {verdict:>12s}  {PUBLISHED[label]:>10s}  {mark:8s} {str(fail)[:36]}")
    else:
        print(f"{label:32s} {verdict:>12s}  {'(control)':>10s}  {'—':8s} {str(fail)[:36]}")

print("-" * 104)
print(f"agreements: {agree}/{len(PUBLISHED)}   disagreements: {disagree}")
print("no file was edited; no pytest was run; no bytecode was involved.")

# ---------------------------------------------------------------------------
# REFINEMENT the file-edit method cannot see: pytest reports "failed" whether the
# loader RAISED or an assertion discriminated. Here the two are distinguishable.
# So: how much of the 4/4 does a BARE construction (no assertions) already catch?
print("\nWhat catches each mutation — bare construction vs the pin's assertions?")
print(f"{'variant':32s} {'bare Checkpoint(path)':>22s}  {'pin assertions add':>19s}")
print("-" * 78)
bare_only = assertion_only = 0
for label, guard in VARIANTS.items():
    if label not in PUBLISHED:
        continue
    try:
        ck = _loader(guard)(d)
        bare = "loads fine"
        fail = pin_assertions(ck)
        ck.close()
    except Exception as e:
        bare, fail = f"RAISES {type(e).__name__}", None
    if bare.startswith("RAISES"):
        adds, bare_only = "nothing (already red)", bare_only + 1
    elif fail:
        adds, assertion_only = f"CATCHES: {fail[:22]}", assertion_only + 1
    else:
        adds = "nothing (escapes)"
    print(f"{label:32s} {bare:>22s}  {adds:>19s}")
print("-" * 78)
print(f"caught by merely LOADING the fixture : {bare_only}/4")
print(f"caught by the pin's ASSERTIONS       : {assertion_only}/4")
print("A 4/4 mutation score conflates 'the pin discriminates' with 'the code crashes'.")
