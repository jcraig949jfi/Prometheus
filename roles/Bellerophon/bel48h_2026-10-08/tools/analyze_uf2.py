"""BEL-48H UF2 analysis (rules: prereg s21).   python3 analyze_uf2.py RESULTS OUT"""
import json, sys
from collections import Counter
from analyze_w5 import sign_one_sided


def main(res, outp):
    R = [json.loads(l) for l in open(res)]
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    out = {"n": len(R) + len(voids), "voids": len(voids), "cells": {}}
    for c in sorted({r["cell"] for r in R}):
        rs = [r for r in R if r["cell"] == c]
        t = sum((Counter(r["UF"]) for r in rs), Counter())
        rb = sum(1 for r in rs if r["UF"].get("BREAK", 0) > r["UF"].get("MAKE", 0)); rm = sum(1 for r in rs if r["UF"].get("MAKE", 0) > r["UF"].get("BREAK", 0))
        fl = sum(1 for r in rs if r["UF"].get("FUNC_LOSS", 0) > r["UF"].get("FUNC_GAIN", 0)); fg = sum(1 for r in rs if r["UF"].get("FUNC_GAIN", 0) > r["UF"].get("FUNC_LOSS", 0))
        out["cells"][c] = {"runs": len(rs), "uptake_events": t["uptake_events"], "BREAK": t["BREAK"], "MAKE": t["MAKE"],
                           "break_over_make": round(t["BREAK"] / max(1, t["MAKE"]), 3), "runs_break_gt_make": rb, "runs_make_gt_break": rm,
                           "p_break": sign_one_sided(rb, rm), "FUNC_LOSS": t["FUNC_LOSS"], "FUNC_GAIN": t["FUNC_GAIN"],
                           "loss_over_gain": round(t["FUNC_LOSS"] / max(1, t["FUNC_GAIN"]), 3), "runs_loss_gt_gain": fl, "runs_gain_gt_loss": fg}
    ref = out["cells"].get("GRID_WM_budget256_reference", {}).get("break_over_make")
    out["UF2-P1"] = {"reference_break_over_make": ref, "holds": bool(ref) and all(v["break_over_make"] < ref for k, v in out["cells"].items() if k != "GRID_WM_budget256_reference")}
    json.dump(out, open(outp, "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
