#!/usr/bin/env python3
"""D001-07 re-derivation (NOT executed by the author; stdlib only).

Inputs (repo paths @ 0424c372a6bba88f50d31f3abbd8b1204871bba6):
  forge/verdicts/*_verdict.json          -- rebuilt forge ablation ledger (Lexis G1 population)
  aporia/iq/RESULT_IQ_NULL.json          -- IQ-NULL result ledger

Run from the repo root:  python3 analysis.py [REPO_ROOT]

Deciding readouts:
  A. Reproduce Lexis G1 raw census: n ablations with delta != None, fraction delta == 0,
     fraction |delta| >= 0.20. Lexis reports 2,103 / 89.73% / 5.94%. Mismatch => G1 citation wrong.
  B. Load-bearing rate among WINNERS: tools in top tercile of overall_score, and tools with
     verdict == PASS. If the top-tercile load-bearing rate (share of that tercile's ablations with
     |delta| >= 0.20) is >= 0.10, "winners' libraries are decoration" weakens for Forge; if < 0.10
     it is confirmed on winners specifically, not just on the whole population.
     (Dead-import vs decoration decomposition needs tool sources; see
     roles/Lexis/instruments/g1_ablation_decompose.py -- not reproduced here.)
  C. IQ-NULL: assert delta_E_null_noop == 0, delta_E_check_transitivity == 0,
     N3 true, verdict ADVANCE, and report whether any partition key exists (the reason
     FINDINGS_SCHEMA_FIX says G-BRANCH fires).
"""
import glob
import json
import os
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
BAR = 0.20


def forge():
    rows = []  # (tool_id, overall_score, verdict, [deltas])
    for p in sorted(glob.glob(os.path.join(ROOT, "forge/verdicts/*_verdict.json"))):
        d = json.load(open(p))
        abl = d.get("ablation")
        if not isinstance(abl, dict):
            continue
        deltas = [v.get("delta") for v in abl.values() if isinstance(v, dict)]
        rows.append((d.get("tool_id"), d.get("overall_score"), d.get("verdict"), deltas))
    allv = [x for r in rows for x in r[3] if x is not None]
    errs = sum(1 for r in rows for x in r[3] if x is None)
    print(f"[A] tools with ablation block: {len(rows)}; ablations: {len(allv)} (+{errs} errors)")
    if allv:
        print(f"    delta==0: {sum(1 for x in allv if x == 0)/len(allv):.4f}  "
              f"|delta|>={BAR}: {sum(1 for x in allv if abs(x) >= BAR)/len(allv):.4f}")
    allzero = sum(1 for r in rows if r[3] and all(x == 0 for x in r[3] if x is not None))
    print(f"    tools with every delta == 0: {allzero}/{len(rows)}")

    scored = sorted([r for r in rows if isinstance(r[1], (int, float))], key=lambda r: r[1])
    k = len(scored) // 3
    terciles = {"bottom": scored[:k], "middle": scored[k:2 * k], "top": scored[2 * k:]}
    for name, grp in terciles.items():
        v = [x for r in grp for x in r[3] if x is not None]
        lb = sum(1 for x in v if abs(x) >= BAR) / len(v) if v else float("nan")
        nz = sum(1 for x in v if x != 0) / len(v) if v else float("nan")
        print(f"[B] {name:6s} tercile: tools={len(grp)} ablations={len(v)} "
              f"load_bearing={lb:.4f} nonzero={nz:.4f}")
    for r in rows:
        if r[2] == "PASS":
            v = [x for x in r[3] if x is not None]
            print(f"[B] PASS {r[0]} score={r[1]} n_prim={len(v)} "
                  f"max|d|={max((abs(x) for x in v), default=0):.4f}")


def iq_null():
    d = json.load(open(os.path.join(ROOT, "aporia/iq/RESULT_IQ_NULL.json")))
    print("[C] delta_E_null_noop =", d.get("delta_E_null_noop"))
    print("[C] delta_E_check_transitivity =", d.get("delta_E_check_transitivity"))
    print("[C] N3 unlock =", d.get("N3_null_noop_changes_reachable_set"),
          " unlocked:", d.get("ops_unlocked_by_null_noop"))
    print("[C] region best =", (d.get("null_region_best") or {}).get("acc"), " E_C =", d.get("E_C"))
    print("[C] verdict =", d.get("verdict"))
    print("[C] partition-like keys:", [k for k in d if "partition" in k.lower()] or "NONE")


if __name__ == "__main__":
    forge()
    iq_null()
