"""BEL-48H UF analysis (rules: prereg s17).   python3 analyze_uf.py RESULTS OUT"""
import json, sys
from collections import Counter
from analyze_w5 import sign_one_sided


def main(res, outp):
    R = [json.loads(l) for l in open(res)]
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    tot = Counter()
    for r in R:
        tot.update(r["UF"])
    rb = sum(1 for r in R if r["UF"].get("BREAK", 0) > r["UF"].get("MAKE", 0)); rm = sum(1 for r in R if r["UF"].get("MAKE", 0) > r["UF"].get("BREAK", 0))
    fl = sum(1 for r in R if r["UF"].get("FUNC_LOSS", 0) > r["UF"].get("FUNC_GAIN", 0)); fg = sum(1 for r in R if r["UF"].get("FUNC_GAIN", 0) > r["UF"].get("FUNC_LOSS", 0))
    out = {"n": len(R) + len(voids), "voids": len(voids), "pooled": dict(tot),
           "runs_break_gt_make": rb, "runs_make_gt_break": rm, "p_break": sign_one_sided(rb, rm),
           "runs_funcloss_gt_gain": fl, "runs_gain_gt_loss": fg, "p_funcloss": sign_one_sided(fl, fg),
           "per_cell": {c: dict(sum((Counter(r["UF"]) for r in R if r["cell"] == c), Counter())) for c in sorted({r["cell"] for r in R})}}
    out["UF-P1"] = {"holds": tot["BREAK"] > tot["MAKE"] and out["p_break"] < 0.05}
    out["UF-P2"] = {"holds": tot["FUNC_LOSS"] > tot["FUNC_GAIN"] and out["p_funcloss"] < 0.05}
    json.dump(out, open(outp, "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
