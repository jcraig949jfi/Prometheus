"""BEL-48H B1 analysis (rules: prereg s15; committed before the runs).   python3 analyze_b1.py RESULTS OUT"""
import json, sys, pathlib
from collections import Counter
from analyze_w2 import fisher_greater, wilson


def budget_class_b(tape_hex, shared, b):
    """as analyze_w6b3.budget_class, at the run's own budget b: a shared byte whose knockout kills competence at b but not 2b."""
    sys.path.insert(0, pathlib.Path(__file__).resolve().parents[4].as_posix())
    from prometheus.z80atlas.tasks import Task, verify_exact
    t = bytes.fromhex(tape_hex)
    if not shared:
        return "SEPARATED"
    comp = lambda x, bb: bool(verify_exact(x, 64, Task("ECHO"), "ABR", bb, "SHARED", False))
    kinds = set()
    for p in shared:
        u = bytearray(t); u[p] = 0
        kinds.add("BUDGET_COUPLED" if (not comp(bytes(u), b) and comp(bytes(u), 2 * b)) else "OTHER_SHARED")
    return "BUDGET_COUPLED" if "BUDGET_COUPLED" in kinds else "OTHER_SHARED"


def main(res, outp):
    R = [json.loads(l) for l in open(res)]
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    out = {"n": len(R) + len(voids), "voids": len(voids), "budgets": {}}
    for b in (192, 256, 384):
        rs = [r for r in R if r["arm"] == str(b)]
        m = [r for r in rs if r["comp"]["comp_func_alive"] > 0 and r["comp"].get("dominant")]
        c = Counter(budget_class_b(r["comp"]["dominant"]["tape"], r["comp"]["dominant"]["shared"], b) for r in m)
        out["budgets"][b] = {"runs": len(rs), "competent_machines": len(m), "classes": dict(c),
                             "budget_coupled_share": round(c.get("BUDGET_COUPLED", 0) / len(m), 3) if m else None,
                             "wilson": wilson(c.get("BUDGET_COUPLED", 0), len(m)), "acquisition_rate": wilson(len(m), len(rs))}
    lo, hi = out["budgets"][192], out["budgets"][384]
    a = lo["classes"].get("BUDGET_COUPLED", 0); n1 = lo["competent_machines"]; c_ = hi["classes"].get("BUDGET_COUPLED", 0); n2 = hi["competent_machines"]
    p = fisher_greater(a, n1 - a, c_, n2 - c_) if n1 and n2 else None
    sh = [out["budgets"][b]["budget_coupled_share"] for b in (192, 256, 384)]
    out["B-P1"] = {"share_192": sh[0], "share_384": sh[2], "p_one_sided": p, "holds": p is not None and p < 0.05}
    out["B-P2"] = {"shares": sh, "monotone_decreasing": all(x is not None for x in sh) and sh[0] >= sh[1] >= sh[2]}
    json.dump(out, open(outp, "w"), indent=1, default=str); print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
