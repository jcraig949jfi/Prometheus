#!/usr/bin/env python
"""
HARMONIA A GEN-2b -- frozen adjudication for the repaired candidate.
Implements HARMONIA_A_GEN2B_FREEZE.txt verbatim.
"""

import json
from collections import Counter, defaultdict

RULERS = ("R_HAM", "R_REL", "R_NMI", "R_VEC", "R_VEC2")
SCALARS = ("R_HAM", "R_REL", "R_NMI")


def main():
    cells = [json.loads(l) for l in open("results/cells_2b.jsonl")]
    viol = {r: [] for r in RULERS}
    for c in cells:
        req = c["required"]
        for r in RULERS:
            cls = c["classes"][r]
            if "must_be" in req and cls != req["must_be"]:
                viol[r].append((c["cell"], req["axiom"],
                                f"required {req['must_be']}, got {cls}"))
            if "must_not_be" in req and cls in req["must_not_be"]:
                viol[r].append((c["cell"], req["axiom"], f"forbidden {cls}"))
            if ("must_not_be_unless_equal" in req and c["d"] > 0
                    and cls in req["must_not_be_unless_equal"]):
                viol[r].append((c["cell"], req["axiom"],
                                f"forbidden {cls} (d>0)"))
    compliance = {}
    for r in RULERS:
        by_ax = defaultdict(int)
        for _, ax, _ in viol[r]:
            by_ax[ax] += 1
        compliance[r] = dict(n_violations=len(viol[r]),
                             by_axiom=dict(by_ax),
                             examples=viol[r][:4],
                             passes_all=len(viol[r]) == 0)

    gates = {}
    gates["G_TEETH"] = dict(
        verdict="PASS" if compliance["R_HAM"]["n_violations"] > 0
        else "HARNESS_SUSPECT")
    c13 = [c for c in cells if c["cell"].startswith("C13")]
    old_vec_fails_c13 = sum(1 for c in c13
                            if c["classes"]["R_VEC"] != "SMALL")
    gates["G_TEETH_C13"] = dict(
        n_c13=len(c13), old_R_VEC_failures=old_vec_fails_c13,
        verdict="PASS" if (len(c13) >= 5 and old_vec_fails_c13 > 0)
        else "HARNESS_SUSPECT",
        note="C13 must exist in force and must kill the Gen-2 R_VEC")

    if any(g["verdict"] != "PASS" for g in gates.values()):
        verdict = "HARNESS_SUSPECT"
    elif any(compliance[r]["passes_all"] for r in SCALARS):
        verdict = "SCALAR_RULER_SURVIVES"
    elif compliance["R_VEC2"]["passes_all"]:
        verdict = "VECTOR_RULER_REQUIRED"
    else:
        verdict = "CONSEQUENCE_LOCALITY_NOT_WELL_DEFINED"

    rs = [json.loads(l) for l in open("results/gen1_rescored_v2.jsonl")]
    old_local = [r for r in rs if r["old_band"] == "SMALL"]
    reclass = Counter(r["new_class"] for r in old_local)
    n = len(old_local)
    headline = dict(
        gen1_rows=len(rs), old_LOCAL_rows=n,
        frac_old_LOCAL_now_DESTRUCTION=round(
            reclass.get("DESTRUCTION", 0) / n, 4),
        frac_old_LOCAL_now_LARGE=round(reclass.get("LARGE", 0) / n, 4),
        frac_old_LOCAL_confirmed_SMALL=round(
            reclass.get("SMALL", 0) / n, 4),
        full_confusion={f"{a}->{b}": v for (a, b), v in sorted(
            Counter((r["old_band"], r["new_class"]) for r in rs).items())})

    report = dict(compliance=compliance, gates=gates, verdict=verdict,
                  gen1_rescore_v2=headline, ruler_version="R_VEC2_gen2b")
    json.dump(report, open("results/analysis_gen2b.json", "w"), indent=1)

    for r in RULERS:
        c = compliance[r]
        print(f"{r:7s} violations={c['n_violations']:3d} "
              f"by_axiom={c['by_axiom']} "
              f"{'SURVIVES' if c['passes_all'] else 'KILLED'}")
    for gname, gv in gates.items():
        print(f"{gname}: {gv['verdict']}")
    print("VERDICT:", verdict)
    print("RESCORE v2:", {k: v for k, v in headline.items()
                          if k.startswith("frac")})


if __name__ == "__main__":
    main()
