"""THESEUS-48 scoring (preregistered rules) -> theseus/runs/store_release_2026-10-10/SUMMARY.json.

  PYTHONPATH=. python theseus/synth/store_release_score.py
"""
import json
from collections import Counter

from theseus.synth import pooled as P

D = "theseus/runs/store_release_2026-10-10"
rows = [json.loads(l) for l in open(f"{D}/TABLE.jsonl", encoding="utf-8")]
st_ok = lambda r: r["J_store"] >= 0.6  # noqa: E731
rel = lambda r: r["J_release"] >= 0.6  # noqa: E731


def cmh(pred, pop):
    tabs = []
    for s in (1, 2, 3, 4):
        L = [r for r in rows if r["stratum"] == s and r["arm"] == "law" and pop(r)]
        N = [r for r in rows if r["stratum"] == s and r["arm"] == "nolaw" and pop(r)]
        tabs.append((sum(pred(r) for r in L), len(L), sum(pred(r) for r in N), len(N)))
    z, p = P.cmh(tabs)
    rd, lo, hi = P.rd_mh(tabs)
    return {"tables": tabs, "CMH_z": z, "p_one_sided": p, "RD_MH": rd, "ci95": [lo, hi]}


out = {"n": len(rows),
       "H_RELEASE": cmh(rel, st_ok),
       "H_STORE": cmh(st_ok, lambda r: True),
       "failure_locus": {}, "best_source_kind": {}, "store_ok_share": {}}
for a in ("law", "nolaw"):
    A = [r for r in rows if r["arm"] == a]
    F = [r for r in A if not rel(r)]
    out["failure_locus"][a] = {"failing": len(F), "STORE_FAIL": sum(not st_ok(r) for r in F),
                               "RELEASE_FAIL": sum(st_ok(r) for r in F)}
    out["best_source_kind"][a] = dict(Counter((r["best_source"] or "none")[0] for r in A))
    out["store_ok_share"][a] = [sum(st_ok(r) for r in A), len(A)]
json.dump(out, open(f"{D}/SUMMARY.json", "w"), indent=1)
print(json.dumps({k: ({kk: vv for kk, vv in v.items() if kk != "tables"} if k.startswith("H_") else v) for k, v in out.items()}, indent=1))
print("tables", out["H_RELEASE"]["tables"], out["H_STORE"]["tables"])
