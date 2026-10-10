"""Verdict mapping for PREREG_D.md (DRAFT until FREEZE_D.json exists).

Usage: python -B -m chiasma.e1b.verdict_d <rows.jsonl>
"""
import json
import sys
from collections import defaultdict

WIN = 8
N_SEEDS = 10
DECIDING = (650, 700)
REPORTED = (800,)
UNCAPPED = 1000000
SECONDARY = [("O0F", "S0F"), ("SPFF", "O0F"), ("SRF", "S0F")]


def beats(cell, a, b, key="err_CDE"):
    A = {r["seed"]: r["endpoints"][key] for r in cell.get(a, [])}
    B = {r["seed"]: r["endpoints"][key] for r in cell.get(b, [])}
    seeds = sorted(set(A) & set(B))
    w = sum(1 for s in seeds if A[s] < B[s])
    if len(seeds) != N_SEEDS:
        return {"wins": w, "n": len(seeds), "beats": "NOT_VERIFIED"}
    return {"wins": w, "n": len(seeds), "beats": w >= WIN}


def claim(holds):
    if any(h == "NOT_VERIFIED" for h in holds):
        return "NOT_VERIFIED"
    n = sum(1 for h in holds if h is True)
    return "PASS" if n == len(holds) else "FAIL" if n == 0 else "MIXED"


def verdict(rows):
    cells = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r.get("world") == "D":
            cells[r["cap"]][r["arm"]].append(r)
    out = {"schema": "chiasma.e1b.verdict_d.v1", "cells": {}, "instrument": {}, "claims": {}}
    u = cells.get(UNCAPPED, {})
    A = {r["seed"]: r["endpoints"]["err_CDE"] for r in u.get("O0", [])}
    B = {r["seed"]: r["endpoints"]["err_CDE"] for r in u.get("O0F", [])}
    seeds = sorted(set(A) & set(B))
    i1 = len(seeds) == N_SEEDS and all(A[s] == B[s] for s in seeds)
    i2 = all(r["endpoints"]["bytes_peak"] <= r["cap"] for cap, arms_ in cells.items() if cap != UNCAPPED
             for rs in arms_.values() for r in rs)
    out["instrument"] = {"I1_lossless_uncapped": i1, "I1_pairs": len(seeds), "I2_cap_held": i2}
    d1, d2 = [], []
    for cap in DECIDING + REPORTED:
        c = cells.get(cap, {})
        v = {"O0F_vs_O0": beats(c, "O0F", "O0"), "O0F_vs_SRF": beats(c, "O0F", "SRF"),
             "O0F_vs_SXF": beats(c, "O0F", "SXF")}
        for a, b in SECONDARY:
            v["{}_vs_{}".format(a, b)] = beats(c, a, b)
        out["cells"][str(cap)] = v
        if cap in DECIDING:
            d1.append(v["O0F_vs_O0"]["beats"])
            s, x = v["O0F_vs_SRF"]["beats"], v["O0F_vs_SXF"]["beats"]
            d2.append("NOT_VERIFIED" if "NOT_VERIFIED" in (s, x) else (s is True and x is True))
    ok = i1 and i2
    out["claims"]["D1"] = claim(d1) if ok else "NOT_VERIFIED"
    out["claims"]["D2"] = claim(d2) if ok else "NOT_VERIFIED"
    return out


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    rows = [json.loads(l) for l in open(argv[0], encoding="utf-8")]
    print(json.dumps(verdict(rows), sort_keys=True, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
