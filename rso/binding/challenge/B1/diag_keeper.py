# Diagnostic (unledgered, disclosed; consumer-only on already-observed outcomes): why does FAILED_RETRY_KEEPER
# differ from the KEEPER control on every claim? Walks every claim field by field on the r1 base. First run by
# harry1-b97f1fc4 walked CL-CAL(STANDARD) only; the resumed instance harry1-2697f39e extended it to all six claims.
import json, sys, os, importlib
sys.dont_write_bytecode = True
ROOT = os.getcwd(); sys.path.insert(0, ROOT)
from rso.slice001 import checker as C
from rso.slice001 import s2_run as SR
from rso.slice001.fixtures import evidence_cases as F
RC = importlib.import_module("rso.binding.challenge.B1.run_cases")
CS = importlib.import_module("rso.binding.challenge.B1.cases")
recs, blobs = SR.stage_records()
g1 = RC.load_r1_g0()
base = F.real_base(g1, stage_records=recs, blobs=blobs)
gv = RC.gate_versions_for("r1", recs)
ref, cref = RC.decide(F.keeper(base), gv)
dec, cust = RC.decide(CS.sound_failed_retry_keeper(base), gv)


def strip(d):
    d = json.loads(C.decision_bytes(d))
    d["prerequisites"] = [ln for ln in d["prerequisites"] if ln.get("predicate") != "custody"]
    return json.dumps(d, sort_keys=True)


for k in sorted(ref):
    same_full = C.decision_bytes(ref[k]) == C.decision_bytes(dec[k])
    same_nocust = strip(ref[k]) == strip(dec[k])
    print("%-18s identical_full=%s identical_without_custody_line=%s" % (k, same_full, same_nocust))
print("control custody rows:", cref.get("rows"))
print("case    custody rows:", cust.get("rows"))


def walk(x, y, path="$"):
    if isinstance(x, dict) and isinstance(y, dict):
        for k in sorted(set(x) | set(y)):
            if k not in x or k not in y:
                print(path + "." + k, "only in", "control" if k in x else "case")
                continue
            walk(x[k], y[k], path + "." + k)
    elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
        for i, (p, q) in enumerate(zip(x, y)):
            walk(p, q, "%s[%d]" % (path, i))
    elif x != y:
        print(path, ":", json.dumps(x)[:160], "->", json.dumps(y)[:160])


for k in sorted(ref):
    print("\n--- field-level diff, %s ---" % k)
    walk(json.loads(C.decision_bytes(ref[k])), json.loads(C.decision_bytes(dec[k])))
