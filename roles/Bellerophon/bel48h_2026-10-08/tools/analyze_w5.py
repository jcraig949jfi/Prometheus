"""BEL-48H Window 5 block 1 analysis (rules: BEL_48H_PREREG.md s7; committed before W5 results).

    python3 analyze_w5.py RESULTS.jsonl OUT.json"""
import json
import math
import sys
from collections import defaultdict

from analyze_w1 import mcnemar_exact


def sign_one_sided(pos, neg):
    n = pos + neg
    return round(sum(math.comb(n, i) for i in range(pos, n + 1)) / 2 ** n, 6) if n else 1.0


def rb(r):
    H = r["heredity"]["H"]
    return H.get("func_birth_ASSEMBLY", 0) + H.get("func_birth_CAPTURE", 0) + H.get("func_birth_CONSTRUCT", 0)


def main(res, outp):
    R = [json.loads(l) for l in open(res)]
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    pairs = defaultdict(dict)
    for r in R:
        pairs[(r["lane"], r["cell"], r["pair"])][r["arm"]] = r
    out = {"n": len(R) + len(voids), "voids": len(voids), "cells": {}}
    for cell in sorted({(k[0], k[1]) for k in pairs}):
        ps = [v for k, v in pairs.items() if (k[0], k[1]) == cell and len(v) == 2]
        fe = lambda r: r["heredity"]["func_alive"] > 0
        po = sum(1 for v in ps if fe(v["preserve"]) and not fe(v["zero"])); zo = sum(1 for v in ps if fe(v["zero"]) and not fe(v["preserve"]))
        rp = sum(1 for v in ps if rb(v["preserve"]) > rb(v["zero"])); rn = sum(1 for v in ps if rb(v["preserve"]) < rb(v["zero"]))
        ca = lambda r: r["heredity"]["H"].get("causal_assembly", 0) > 0
        out["cells"]["%s/%s" % cell] = {
            "pairs": len(ps), "func_end": {"preserve": sum(fe(v["preserve"]) for v in ps), "zero": sum(fe(v["zero"]) for v in ps)},
            "mcnemar": {"preserve_only": po, "zero_only": zo, "p": mcnemar_exact(po, zo)},
            "repair_births_median": {a: sorted(rb(v[a]) for v in ps)[len(ps) // 2] for a in ("preserve", "zero")} if ps else None,
            "repair_sign": {"preserve_higher": rp, "zero_higher": rn, "p_one_sided": sign_one_sided(rp, rn)},
            "causal_assembly_runs": {a: sum(ca(v[a]) for v in ps) for a in ("preserve", "zero")},
            "func_alive_median": {a: sorted(v[a]["heredity"]["func_alive"] for v in ps)[len(ps) // 2] for a in ("preserve", "zero")} if ps else None}
    c = out["cells"]
    hi = c.get("E5a/SEEDED/PARTIAL/HIGH")
    out["W5-P1"] = {"holds": bool(hi and hi["mcnemar"]["p"] < 0.05 and hi["mcnemar"]["preserve_only"] > hi["mcnemar"]["zero_only"]), **(hi or {}).get("mcnemar", {})}
    out["W5-P2"] = {lv: c.get("E5a/SEEDED/PARTIAL/%s" % lv, {}).get("repair_sign") for lv in ("MED", "HIGH")}
    out["W5-P2"]["holds"] = all((out["W5-P2"][lv] or {}).get("p_one_sided", 1) < 0.05 for lv in ("MED", "HIGH"))
    b = c.get("E5b/A/PARTIAL")
    out["W5-P3"] = {"causal_assembly_runs": (b or {}).get("causal_assembly_runs"), "pairs": (b or {}).get("pairs"),
                    "holds": bool(b and b["causal_assembly_runs"]["preserve"] >= 0.9 * b["pairs"] and b["causal_assembly_runs"]["zero"] <= 0.05 * b["pairs"])}
    json.dump(out, open(outp, "w"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
