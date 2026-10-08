# Diagnostic (unledgered, disclosed; Pallas[harry1-2697f39e]): which suite killed E1 and E5? EXPOSURE.md says a kill
# by the binding unit suite (read by the set's author) would be a reviewer error, a kill by the slice suite (not
# read) a first-sight result. Runs the runner's own in-process child on each killed edit against the 13-test binding
# suite alone, and against each slice module alone, and prints failures per module. No ledger row: ~1-2 CPU-min.
import json, os, sys
sys.dont_write_bytecode = True
ROOT = os.getcwd(); sys.path.insert(0, ROOT)
from rso.slice001 import mutation as M
edits, _ = M.load_edits(os.path.join(ROOT, "rso/binding/challenge/B1/edits.json"))
by = {e["edit_id"]: e for e in edits}
MODS = ["rso.binding.tests.test_binding", "rso.slice001.tests.test_evidence", "rso.slice001.tests.test_checker_render",
        "rso.slice001.tests.test_stages_evidence", "rso.slice001.tests.test_ledger"]
for eid in ("E1-parent-default", "E5-runjson-trusted"):
    e = by[eid]
    src = open(os.path.join(ROOT, e["path"]), "rb").read().decode("utf-8")
    for mod in MODS:
        job = {"sys_path": [ROOT], "module": e["module"], "source": M.apply_edit(src, e),
               "filename": os.path.join(ROOT, e["path"]), "suite": [mod], "witness": [], "mark": M._MARK}
        res, wall = M._run_child(job, 600)
        print("%-22s %-45s %-7s run=%s fail=%s err=%s wall=%.1f" % (eid, mod, M._classify(res), res.get("tests_run"),
              res.get("failures"), res.get("errors"), wall))
        if res.get("failures") or res.get("errors"):
            print("    ", json.dumps(res.get("detail"))[:900])
