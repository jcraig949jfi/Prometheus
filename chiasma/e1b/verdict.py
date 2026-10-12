"""E1b verdict mapping (DRAFT until frozen with PREREG_E1b.md).

Usage: python -B -m chiasma.e1b.verdict <rows.jsonl>

Cell = (world, cap). "A beats B" in a cell = A's endpoint strictly lower on at least
WIN of N_SEEDS paired seeds (ties do not count). Uncapped arms (O3U) are paired with
every cell of their world.

Primary, per family (PW-H: 9 cells; PW-H3: 3 cells):
  O4L beats O1 AND O2 AND O3 on err_CDE.
  PASS = every cell; FAIL = fewer than half the cells; MIXED otherwise;
  NOT_VERIFIED = any contrast lacks N_SEEDS paired seeds.
Attribution: in each cell where the primary holds, O4L also beats O4LR (counterfeit
provenance). MECHANISM_ATTRIBUTED only if the family PASSes and every cell attributes.
"""
import json
import sys
from collections import defaultdict

WIN = 8
N_SEEDS = 10
BIG = 10 ** 12

PRIMARY = ("O1", "O2", "O3")
SECONDARY = [("O4L", "O0", "err_CDE"), ("O4L", "O3U", "err_CDE"), ("O2", "O4L", "collateral_CDE"),
             ("O4", "O1", "err_CDE"), ("O4", "O2", "err_CDE"), ("O4LR", "O3", "err_CDE"),
             ("O3", "O2", "err_CDE")]


def _v(x):
    return x if isinstance(x, int) else BIG


def beats(cell, a, b, key="err_CDE"):
    A = {r["seed"]: r["endpoints"][key] for r in cell.get(a, [])}
    B = {r["seed"]: r["endpoints"][key] for r in cell.get(b, [])}
    seeds = sorted(set(A) & set(B))
    w = sum(1 for s in seeds if _v(A[s]) < _v(B[s]))
    if len(seeds) != N_SEEDS:
        return {"wins": w, "n": len(seeds), "beats": "NOT_VERIFIED"}
    return {"wins": w, "n": len(seeds), "beats": w >= WIN}


def family(world):
    return "PW-H3" if world == "H3" else "PW-H"


def verdict(rows):
    cells = defaultdict(lambda: defaultdict(list))
    uncapped = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["cap"] == "NONE":
            uncapped[r["world"]][r["arm"]].append(r)
        else:
            cells[(r["world"], r["cap"])][r["arm"]].append(r)
    out = {"schema": "chiasma.e1b.verdict.v1", "cells": {}, "primary": {}}
    fam = defaultdict(lambda: {"cells": 0, "pass": 0, "attr": 0, "nv": 0})
    for (world, cap) in sorted(cells):
        c = dict(cells[(world, cap)])
        for arm, rs in uncapped[world].items():
            c[arm] = rs
        v = {"O4L_vs_" + b: beats(c, "O4L", b) for b in PRIMARY}
        v["O4L_vs_O4LR"] = beats(c, "O4L", "O4LR")
        for a, b, key in SECONDARY:
            v["{}_vs_{}:{}".format(a, b, key)] = beats(c, a, b, key)
        prim = [v["O4L_vs_" + b]["beats"] for b in PRIMARY]
        holds = all(p is True for p in prim)
        v["primary_holds"] = holds
        f = fam[family(world)]
        f["cells"] += 1
        f["pass"] += int(holds)
        f["attr"] += int(holds and v["O4L_vs_O4LR"]["beats"] is True)
        f["nv"] += int("NOT_VERIFIED" in prim)
        out["cells"]["{}|{}".format(world, cap)] = v
    for name, f in sorted(fam.items()):
        if f["nv"]:
            verdict_ = "NOT_VERIFIED"
        elif f["pass"] == f["cells"]:
            verdict_ = "PASS"
        elif 2 * f["pass"] < f["cells"]:
            verdict_ = "FAIL"
        else:
            verdict_ = "MIXED"
        out["primary"][name] = {
            "verdict": verdict_,
            "cells_primary_holds": "{}/{}".format(f["pass"], f["cells"]),
            "cells_also_beating_O4LR": "{}/{}".format(f["attr"], f["cells"]),
            "attribution": ("MECHANISM_ATTRIBUTED" if verdict_ == "PASS" and f["attr"] == f["cells"]
                            else "NOT_ATTRIBUTED")}
    return out


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    rows = [json.loads(l) for l in open(argv[0], encoding="utf-8")]
    print(json.dumps(verdict(rows), sort_keys=True, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
