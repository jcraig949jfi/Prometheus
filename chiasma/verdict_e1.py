"""E1 verdict mapping, frozen with PREREG_E1.md (its sha256 is in FREEZE_E1.json).

Usage: python -B -m chiasma.verdict_e1 <rows.jsonl>
Reads evaluation rows and prints the preregistered verdicts as canonical JSON.
"""
import json
import sys
from collections import defaultdict

WIN = 8          # wins out of 10 paired seeds needed for "beats" in one cell
N_SEEDS = 10


def wins(rows_a, rows_b, key):
    A = {r["seed"]: r["endpoints"][key] for r in rows_a}
    B = {r["seed"]: r["endpoints"][key] for r in rows_b}
    seeds = sorted(set(A) & set(B))
    big = 10 ** 12
    w = sum(1 for s in seeds if (A[s] if isinstance(A[s], int) else big) < (B[s] if isinstance(B[s], int) else big))
    return w, len(seeds)


def beats(cell, a, b, key="err_CDE"):
    w, n = wins(cell.get(a, []), cell.get(b, []), key)
    if n != N_SEEDS:
        return {"wins": w, "n": n, "beats": "NOT_VERIFIED"}
    return {"wins": w, "n": n, "beats": w >= WIN}


def verdict(rows):
    cells = defaultdict(lambda: defaultdict(list))
    ceil = defaultdict(list)
    for r in rows:
        if r["arm"] == "CEIL":
            ceil[r["ratio"]].append(r)
        else:
            cells[(r["ratio"], r["cap"])][r["arm"]].append(r)
    out = {"schema": "chiasma.e1.verdict.v1", "cells": {}}
    n_both, n_cells, not_verified = 0, 0, 0
    attributed = 0
    for (ratio, cap) in sorted(cells):
        c = cells[(ratio, cap)]
        v = {
            "O4_vs_O1": beats(c, "O4", "O1"),
            "O4_vs_O2": beats(c, "O4", "O2"),
            "O4_vs_O4R": beats(c, "O4", "O4R"),
            "O4_collateral_le_O2": beats(c, "O2", "O4", "collateral_CDE"),
            # secondary (never decide the primary verdict)
            "O4L_vs_O1": beats(c, "O4L", "O1"),
            "O4L_vs_O2": beats(c, "O4L", "O2"),
            "O4L_vs_O3": beats(c, "O4L", "O3"),
            "O4L_vs_O0": beats(c, "O4L", "O0"),
            "O4_vs_O0": beats(c, "O4", "O0"),
            "O3_vs_O2": beats(c, "O3", "O2"),
            "O3_vs_O3R": beats(c, "O3", "O3R"),
        }
        both = v["O4_vs_O1"]["beats"] is True and v["O4_vs_O2"]["beats"] is True
        if "NOT_VERIFIED" in (v["O4_vs_O1"]["beats"], v["O4_vs_O2"]["beats"]):
            not_verified += 1
        v["O4_beats_O1_and_O2"] = both
        n_cells += 1
        n_both += int(both)
        attributed += int(both and v["O4_vs_O4R"]["beats"] is True)
        out["cells"]["{}|{}".format(ratio, cap)] = v
    if not_verified:
        primary = "NOT_VERIFIED"
    elif n_both == n_cells:
        primary = "PASS"
    elif 2 * n_both < n_cells:
        primary = "FAIL"
    else:
        primary = "MIXED"
    out["primary"] = {"verdict": primary, "cells_O4_beats_O1_and_O2": "{}/{}".format(n_both, n_cells),
                      "cells_also_beating_O4R": "{}/{}".format(attributed, n_cells),
                      "attribution": ("MECHANISM_ATTRIBUTED" if primary == "PASS" and attributed == n_cells
                                      else "NOT_ATTRIBUTED")}
    out["charter_mapping"] = {"PASS": "O4 survives E1; next step is G3 challenge, then operator decides evolution",
                              "MIXED": "REVISE: name the cells where O4 fails",
                              "FAIL": "KILL or radically REVISE O4 as designed (charter s7)",
                              "NOT_VERIFIED": "missing rows; no verdict"}[primary]
    return out


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    rows = [json.loads(l) for l in open(argv[0], encoding="utf-8")]
    print(json.dumps(verdict(rows), sort_keys=True, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
