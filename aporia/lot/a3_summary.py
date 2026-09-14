"""a3_summary.py -- print the tables FINDINGS_A3 quotes, straight from RESULT_A3.json.

    python aporia/lot/a3_summary.py

Every number in the findings document is produced here, so a reviewer can regenerate them
without trusting the prose. Read-only.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARMS = ("FLAT", "REIFIED", "ORACLE", "CONTROL", "RANDOM", "FREQ", "MEMO")


def med(xs):
    return statistics.median(xs) if xs else None


def main(path=HERE / "RESULT_A3.json"):
    r = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = r["rows"]
    print("verdict", r["verdict"], "kills", r["kill_criteria_fired"])
    print("seeds", r["seeds"], "episodes", len(rows), "dropped_records", r["dropped_records"])
    print()
    print("RULES")
    print(json.dumps(r["rules"], indent=1)[:6000])
    print()
    print("MINT DECISIONS BY CLASS (episodes minted / eligible; c_max median; precision)")
    for cls in ("REUSE", "NO_REUSE", "DECOY_REUSE", "LATE_REUSE", "CONTROL"):
        eps = [x for x in rows if x["class"] == cls]
        m = [x for x in eps if x["minted"]]
        prec = [x["s_max_is_shared"] for x in m if x["s_max_is_shared"] is not None]
        miss = sum(x["witnesses_missing"] for x in eps)
        print(f"  {cls:12s} {len(m):3d}/{len(eps):3d}  c_max median {med([x['c_max'] for x in eps])}  "
              f"s_max==shared {sum(prec)}/{len(prec)}  witnesses_missing {miss}")
    print()
    print("LATE MEDIAN C_SEARCH BY CLASS AND ARM (median over episodes of per-episode medians)")
    print("  class        " + "".join(f"{a:>10s}" for a in ARMS))
    for cls in ("REUSE", "NO_REUSE", "DECOY_REUSE", "LATE_REUSE", "CONTROL"):
        eps = [x for x in rows if x["class"] == cls]
        line = f"  {cls:12s} "
        for a in ARMS:
            v = med([x["arms"][a]["median_c_search"] for x in eps if x["arms"][a]["median_c_search"] is not None])
            line += f"{v:10.0f}" if v is not None else f"{'-':>10s}"
        print(line)
    print()
    print("LATE MEDIAN C_EXECUTION BY CLASS AND ARM")
    print("  class        " + "".join(f"{a:>10s}" for a in ARMS))
    for cls in ("REUSE", "NO_REUSE", "DECOY_REUSE", "LATE_REUSE", "CONTROL"):
        eps = [x for x in rows if x["class"] == cls]
        line = f"  {cls:12s} "
        for a in ARMS:
            v = med([x["arms"][a]["median_c_execution"] for x in eps if x["arms"][a]["median_c_execution"] is not None])
            line += f"{v:10.0f}" if v is not None else f"{'-':>10s}"
        print(line)
    print()
    print("DROPPED LATE TASKS BY ARM (sum over all episodes) and closures that exhausted the budget")
    for a in ARMS:
        d = sum(x["arms"][a]["late_dropped"] for x in rows)
        ex = sum(1 for x in rows if x["arms"][a]["closure_exhausted"])
        print(f"  {a:8s} dropped {d:4d}   exhausted closures {ex:3d}/{len(rows)}")
    print()
    print("ORACLE/FLAT late C_search ratio by class (the ceiling, all episodes)")
    for cls in ("REUSE", "NO_REUSE", "DECOY_REUSE", "LATE_REUSE", "CONTROL"):
        xs = []
        for x in rows:
            if x["class"] != cls:
                continue
            a, b = x["arms"]["ORACLE"]["median_c_search"], x["arms"]["FLAT"]["median_c_search"]
            if a is not None and b:
                xs.append(a / b)
        print(f"  {cls:12s} median {med(xs):.3f}  n {len(xs)}" if xs else f"  {cls:12s} -")
    print()
    print("REIFIED/FLAT late C_search ratio on MINTED episodes by class")
    for cls in ("REUSE", "DECOY_REUSE", "CONTROL"):
        xs = []
        for x in rows:
            if x["class"] != cls or not x["minted"]:
                continue
            a, b = x["arms"]["REIFIED"]["median_c_search"], x["arms"]["FLAT"]["median_c_search"]
            if a is not None and b:
                xs.append(a / b)
        print(f"  {cls:12s} median {med(xs):.3f}  n {len(xs)}  values {[round(v,3) for v in sorted(xs)]}" if xs else f"  {cls:12s} -")


if __name__ == "__main__":
    main(*(sys.argv[1:2]))
