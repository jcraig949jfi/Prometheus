"""BEL-RD-72 K2 analysis (rules: BEL_RD72_PREREG.md s3 amendment A1; committed before any run).
    python3 analyze_k2.py RESULTS PLAN OUT
Fixes from review: TWO_SOURCE on DISTINCTIVE positions only (content AND tag); extinction made explicit (INFORMATIVE run =
alive at tick 500; every Fisher test is reported on all runs AND on informative runs, and a prediction holds only if both
pass); K-P1 NOT_TESTABLE when a cell has < 30 informative runs; selection tested against RANDOM_REWARD; the competent
machine is re-checked on all 256 inputs."""
import json, sys, pathlib
from collections import defaultdict
_H = pathlib.Path(__file__).resolve()
for _p in (_H.parent, _H.parents[1].parent / "bel48h_2026-10-08" / "tools", _H.parents[4]):
    sys.path.insert(0, str(_p))
from analyze_k import fisher_greater, comp_any, comp_sr
from fixtures_k import fixtures
PAIRS = {"XY_AL": ("X_al", "Y_al"), "XY_SH": ("X_sh", "Y_sh"), "XY_NS": ("X_sh", "Y_ns"), "X_ONLY": ("X_al", "REP"), "Y_ONLY": ("Y_al", "REP")}


def anatomy(r):
    c = r["comp"]
    return (c.get("first_comp_sr") or {}).get("anatomy") or c.get("dominant")


def two_source_strict(r):
    """>= 1 competence-critical position where the two fixtures DIFFER whose byte equals fixture 0's byte and carries a
    transplant0 founder tag, AND >= 1 such position for fixture 1 / transplant1."""
    a = anatomy(r); fx = r["cell"].split("/")[0]
    if not a or fx not in PAIRS:
        return False
    F = fixtures(); f0, f1 = F[PAIRS[fx][0]], F[PAIRS[fx][1]]; tape = bytes.fromhex(a["tape"])
    hit = [False, False]
    for kind, _, mech, p in a["ccrit_origins"]:
        if f0[p] == f1[p] or kind != "F":
            continue
        if mech == "transplant0" and tape[p] == f0[p]:
            hit[0] = True
        if mech == "transplant1" and tape[p] == f1[p]:
            hit[1] = True
    return all(hit)


def informative(r):
    s = r["summary"]
    return (not s["extinct"]) or (s.get("extinct_tick") or 0) >= 500


def full256(r, cfgs):
    a = anatomy(r)
    if not a:
        return None
    from prometheus.z80atlas.world import Config
    from prometheus.z80atlas import vm
    from halves import _expected
    cfg = Config(**cfgs[r["id"]]); tape = bytes.fromhex(a["tape"]); L = cfg.L
    for x in range(256):
        mem = bytearray(256); mem[:L] = tape; mem[vm.IN_BASE] = x
        tr = vm.execute(mem, L, 0, cfg.budget, [x], allow_copyall=cfg.allow_copyall, strict_budget=cfg.physics != "v1", **cfg.chem)
        if not (tr.outputs and tr.outputs[0] == _expected(cfg.task, x)):
            return False
    return True


def main(res, plan, outp, check256=True):
    R = [json.loads(l) for l in open(res)]
    cfgs = {p["id"]: p["cfg"] for p in json.load(open(plan))}
    voids = [r for r in R if r.get("void")]; R = [r for r in R if not r.get("void")]
    by = defaultdict(list)
    for r in R:
        by["%s|%s" % (r["cell"], r["arm"])].append(r)
    out = {"n": len(R) + len(voids), "voids": len(voids), "cells": {}}
    for c, rs in sorted(by.items()):
        inf = [r for r in rs if informative(r)]
        out["cells"][c] = {"runs": len(rs), "informative": len(inf), "extinct": sum(r["summary"]["extinct"] for r in rs),
                           "comp_any": sum(map(comp_any, rs)), "comp_any_inf": sum(map(comp_any, inf)),
                           "comp_sr": sum(map(comp_sr, rs)), "comp_sr_inf": sum(map(comp_sr, inf)),
                           "comp_persist": sum(1 for r in rs if (r["comp"].get("comp_func_alive") or 0) > 0),
                           "comp_persist_inf": sum(1 for r in inf if (r["comp"].get("comp_func_alive") or 0) > 0),
                           "two_source_strict_of_comp_sr": sum(1 for r in rs if comp_sr(r) and two_source_strict(r)),
                           "full256_of_comp": [full256(r, cfgs) for r in rs if anatomy(r)] if check256 else None,
                           "exposure_median": sorted(r.get("exposure", 0) for r in rs)[len(rs) // 2] if rs else None}
    C = out["cells"]
    g = lambda c, k: C.get(c, {}).get(k, 0)

    def both(a, b, key):
        p_all = fisher_greater(g(a, key), g(a, "runs") - g(a, key), g(b, key), g(b, "runs") - g(b, key))
        p_inf = fisher_greater(g(a, key + "_inf"), g(a, "informative") - g(a, key + "_inf"), g(b, key + "_inf"), g(b, "informative") - g(b, key + "_inf"))
        return {"p_all": p_all, "p_inf": p_inf, "pass": p_all < 0.05 and p_inf < 0.05}
    p1 = {}
    for ops in ("COPY_BYTE", "COPY_STRUCT"):
        c = "XY_AL/%s|ON" % ops
        p1[ops] = {"comp_sr": g(c, "comp_sr"), "informative": g(c, "informative"),
                   "holds": (g(c, "comp_sr") <= 2) if g(c, "informative") >= 30 else "NOT_TESTABLE"}
    h1 = [v["holds"] for v in p1.values()]
    out["K-P1"] = {**p1, "holds": "NOT_TESTABLE" if "NOT_TESTABLE" in h1 else all(h1)}
    xy = "XY_AL/PARTIAL_BYTE|ON"
    t2 = {o: both(xy, o, "comp_any") for o in ("X_ONLY/PARTIAL_BYTE|ON", "Y_ONLY/PARTIAL_BYTE|ON", "XY_AL/COPY_BYTE|ON")}
    out["K-P2"] = {"tests": t2, "holds": all(t["pass"] for t in t2.values())}
    srs = g(xy, "comp_sr"); ts = g(xy, "two_source_strict_of_comp_sr")
    out["K-P3"] = {"two_source_strict": [ts, srs], "holds": (ts >= 0.8 * srs) if srs else "NOT_TESTABLE"}
    t4 = {"comp_any_vs_RR": both(xy, "XY_AL/PARTIAL_BYTE|RANDOM_REWARD", "comp_any"),
          "comp_persist_vs_RR": both(xy, "XY_AL/PARTIAL_BYTE|RANDOM_REWARD", "comp_persist")}
    out["K-P4"] = {"tests": t4, "holds": t4["comp_persist_vs_RR"]["pass"],
                   "descriptive_vs_OFF": both(xy, "XY_AL/PARTIAL_BYTE|OFF", "comp_any")}
    json.dump(out, open(outp, "w"), indent=1, default=str); print(json.dumps({k: out[k] for k in out if k.startswith("K-")}, indent=1, default=str))
    return out


if __name__ == "__main__":
    main(*sys.argv[1:4])
