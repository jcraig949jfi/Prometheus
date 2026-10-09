"""THESEUS-46: redundant (no single essential rule) vs one-point solvers -- generalisation.

Prereg: roles/Theseus/prereg/2026-10-09_redundancy_generalise/PREREG.md.

  PYTHONPATH=. python theseus/synth/redund_score.py
"""
import json

from theseus.synth import pooled as P

rows = [json.loads(l) for l in open("theseus/runs/generalise_2026-10-09/TABLE.jsonl", encoding="utf-8")]
STRATA = [(a, s) for a in ("law", "nolaw") for s in (1, 2, 3)]


def test(pred, strata):
    tabs = []
    for a, s in strata:
        R = [r for r in rows if r["arm"] == a and r["stratum"] == s and r["n_essential"] == 0]
        O = [r for r in rows if r["arm"] == a and r["stratum"] == s and r["n_essential"] >= 1]
        tabs.append((sum(pred(r) for r in R), len(R), sum(pred(r) for r in O), len(O)))
    z, p = P.cmh(tabs)
    rd, lo, hi = P.rd_mh(tabs)
    return {"tables": tabs, "CMH_z": z, "p_one_sided": p, "RD_MH": rd, "ci95": [lo, hi]}


alpha = lambda r: r["J_V8k8"] >= 0.6  # noqa: E731
delay = lambda r: r["J_delay"][4] >= 0.6  # noqa: E731
out = {"H_REDUND_ALPHA": test(alpha, STRATA), "H_REDUND_DELAY": test(delay, STRATA),
       "by_arm": {a: {"alpha": test(alpha, [x for x in STRATA if x[0] == a]),
                      "delay": test(delay, [x for x in STRATA if x[0] == a])} for a in ("law", "nolaw")}}
json.dump(out, open("theseus/runs/generalise_2026-10-09/REDUND_SUMMARY.json", "w"), indent=1)
print(json.dumps({k: (v if k != "by_arm" else {a: {t: {kk: vv for kk, vv in x.items() if kk != "tables"} for t, x in d.items()} for a, d in v.items()}) for k, v in out.items()}, indent=1))
