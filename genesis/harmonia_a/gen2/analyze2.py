#!/usr/bin/env python
"""
HARMONIA A GEN-2 -- frozen adjudication. Implements the axioms, gates and
verdict rule of HARMONIA_A_GEN2_FREEZE.txt verbatim. Run after bench2.py.
"""

import json
from collections import Counter, defaultdict

RULERS = ("R_HAM", "R_REL", "R_NMI", "R_VEC")
SCALARS = ("R_HAM", "R_REL", "R_NMI")   # banded-scalar candidates


def main():
    cells = [json.loads(l) for l in open("results/cells.jsonl")]

    # ---- axiom compliance per ruler
    viol = {r: [] for r in RULERS}
    for c in cells:
        req = c["required"]
        for r in RULERS:
            cls = c["classes"][r]
            if "must_be" in req and cls != req["must_be"]:
                viol[r].append((c["cell"], req["axiom"],
                                f"required {req['must_be']}, got {cls}"))
            if "must_not_be" in req and cls in req["must_not_be"]:
                viol[r].append((c["cell"], req["axiom"],
                                f"forbidden {cls}"))
            if ("must_not_be_unless_equal" in req and c["d"] > 0
                    and cls in req["must_not_be_unless_equal"]):
                viol[r].append((c["cell"], req["axiom"],
                                f"forbidden {cls} (d>0)"))

    compliance = {}
    for r in RULERS:
        by_ax = defaultdict(int)
        for _, ax, _ in viol[r]:
            by_ax[ax] += 1
        compliance[r] = dict(
            n_cells=len(cells), n_violations=len(viol[r]),
            violations_by_axiom=dict(by_ax),
            examples=viol[r][:5],
            passes_all=len(viol[r]) == 0)

    # ---- gates
    gates = {}
    gates["G_TEETH"] = dict(
        r_ham_violations=compliance["R_HAM"]["n_violations"],
        verdict="PASS" if compliance["R_HAM"]["n_violations"] > 0
        else "HARNESS_SUSPECT",
        note="battery must kill the known-defective incumbent")
    # Gen-1 pathology severity flag: any collapse cell classified SMALL
    ax4 = {r: sum(1 for c in cells
                  if c["required"].get("axiom", "").startswith("AX2")
                  and c["classes"][r] == "SMALL") for r in RULERS}
    gates["G_AX4_SEVERITY"] = dict(collapse_classified_SMALL=ax4)

    # ---- verdict (frozen rule)
    if gates["G_TEETH"]["verdict"] != "PASS":
        verdict = "HARNESS_SUSPECT"
    elif any(compliance[r]["passes_all"] for r in SCALARS):
        verdict = "SCALAR_RULER_SURVIVES"
    elif compliance["R_VEC"]["passes_all"]:
        verdict = "VECTOR_RULER_REQUIRED"
    else:
        verdict = "CONSEQUENCE_LOCALITY_NOT_WELL_DEFINED"

    # ---- Gen-1 re-score headline (descriptive, gate-free, frozen stat)
    rs = [json.loads(l) for l in open("results/gen1_rescored.jsonl")]
    old_local = [r for r in rs if r["old_band"] == "SMALL"]
    reclass = Counter(r["new_class"] for r in old_local)
    n = len(old_local)
    headline = dict(
        gen1_rows=len(rs), old_LOCAL_rows=n,
        reclassified=dict(reclass),
        frac_old_LOCAL_now_DESTRUCTION=round(
            reclass.get("DESTRUCTION", 0) / n, 4) if n else None,
        frac_old_LOCAL_now_LARGE=round(
            reclass.get("LARGE", 0) / n, 4) if n else None,
        frac_old_LOCAL_confirmed_SMALL=round(
            reclass.get("SMALL", 0) / n, 4) if n else None)
    full = Counter((r["old_band"], r["new_class"]) for r in rs)
    headline["full_confusion"] = {f"{a}->{b}": v
                                  for (a, b), v in sorted(full.items())}
    nov = sorted(r["novelty_min_sib_d"] for r in rs)
    headline["novelty_component_reportonly"] = dict(
        median=nov[len(nov) // 2], p90=nov[int(0.9 * len(nov))])

    report = dict(compliance=compliance, gates=gates, verdict=verdict,
                  gen1_rescore=headline)
    json.dump(report, open("results/analysis_gen2.json", "w"), indent=1)

    for r in RULERS:
        c = compliance[r]
        print(f"{r:6s} violations={c['n_violations']:3d} "
              f"by_axiom={c['violations_by_axiom']} "
              f"{'SURVIVES' if c['passes_all'] else 'KILLED'}")
    print("G_TEETH:", gates["G_TEETH"]["verdict"],
          "| AX4 severity:", ax4)
    print("VERDICT:", verdict)
    print("GEN1 RESCORE:", {k: v for k, v in headline.items()
                            if k.startswith("frac")})


if __name__ == "__main__":
    main()
