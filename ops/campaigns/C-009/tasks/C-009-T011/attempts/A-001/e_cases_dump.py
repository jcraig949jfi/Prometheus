"""Dump the E01-E05 verdict fields (the expected table's columns) for every case and claim, on whatever code
tree is first on sys.path. Used for C-009-T011 'E01-E05 expectations unchanged'."""
import json, sys
sys.path.insert(0, sys.argv[1])
sys.dont_write_bytecode = True
from rso.slice001 import checker as C
from rso.slice001.fixtures import evidence_cases as F
recs = F.stage_records()
gv = {r["instrument"]: r["version"] for r in recs if r["instrument"] in C.GATES}
out = {}
for cid in sorted(F.CASES):
    case = F.CASES[cid]()
    cons = C.Consumer(case.bundle, case.anchors, case.store, case.config, gv, case.first_check)
    dec = cons.decide_all(case.claims)
    rows = {"custody": [cons.custody["status"], cons.custody.get("why")]}
    for k, d in sorted(dec.items()):
        lines = []
        for ln in d["prerequisites"]:
            if "verdict" in ln:
                v = ln["verdict"]; o = v["outcome"] or {}
                lines.append([ln["predicate"], ln["scope"], v["execution"]["status"], v["authority"]["status"],
                              o.get("value"), o.get("reason"), v["standing"]])
            else:
                lines.append([ln["predicate"], ln["scope"], ln["standing"]])
        rows[k] = {"eligibility": d["eligibility"], "standing": d["standing"], "not_satisfied": d["not_satisfied"],
                   "lines": lines}
    out[cid] = rows
json.dump(out, open(sys.argv[2], "w"), sort_keys=True, indent=1)
print(sys.argv[2], len(out))
