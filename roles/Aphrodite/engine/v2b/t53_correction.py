"""T53-C (CORRECTION class, post-exposure): T53's frozen walks, re-read with the control logic repaired in DEV-3.
The T02 readouts were SEEN before this repair, so this is NOT a frozen test. It is a corrected analysis whose
evidential weight is below T02's would-have-been result. Writes beta01/runs/T02_T53/T53_CORRECTION.json.

Repairs:
  C1  PC_ONE is START-relative: good iff SAME#1 is solved in >= 3/4 cells AND PC_ONE gains no family-capability on
      SAME#2 beyond START. Evaluated ONLY on extensionally DISTINCT pairs (supply.interchangeable). A duplicate pair
      is excluded from the control, not counted as a failure.
  C2  CAP_D_SAME requires >= 2 extensionally DISTINCT SAME classes (supply.distinct_classes). In a duplicate pair, a
      solved pair counts as one class.
The measurement gate and readouts are otherwise exactly T02 spec s4.
"""
import json
import math
from collections import defaultdict

import paths
import a18
import supply
import t53_rescore as T


def main():
    a18.worker_init()
    plan = json.loads((T.OUTDIR / "T53_PLAN.json").read_text(encoding="utf-8"))
    walks = {(w["lib"], w["family"], w["cell"]): w for w in
             map(json.loads, (T.OUTDIR / "T53_WALKS.jsonl").read_text(encoding="utf-8").splitlines())}
    cells = defaultdict(dict)
    for j in plan["jobs"]:
        w = walks.get((j["lib"], j["family"], j["cell"]))
        if w and w["status"] == "OK":
            cells[(j["rep"], j["held"], j["cls"], j["family"], j["arm"])][j["cell"]] = w["result"]
    meta = plan["meta"]["families"]
    reps = plan["meta"]["reps"]

    def solved(x):
        return x is not None and not x.get("censored", True)

    def fam_cap(rep, held, cls, fam, arm):
        a = cells.get((rep, held, cls, fam, arm), {})
        s = cells.get((rep, held, cls, fam, "START"), {})
        return sum(1 for i in range(4) if solved(a.get(i)) and (s.get(i) or {}).get("censored")) >= 2

    fams_by = defaultdict(lambda: {"SAME": [], "OTHER": []})
    for n, f in meta.items():
        fams_by[(f["rep"], f["held"])][f["cls"]].append(n)
    classes = {}
    for key, d in fams_by.items():
        for cls in ("SAME", "OTHER"):
            fl = [dict(meta[n], name=n) for n in sorted(d[cls])]
            classes[(key, cls)] = [[f["name"] for f in c] for c in supply.distinct_classes(fl)]
    arms_for = {"G1": ["SEL_G1", "SEL_G1_NC", "SEL_P", "SEL_OFF_0", "PC_MOTIF", "NC_OTHER"],
                "SHAM_0": ["SEL_SHAM_0", "SEL_P", "SEL_OFF_0"], "SHAM_1": ["SEL_SHAM_1", "SEL_P", "SEL_OFF_0"],
                "SHAM_2": ["SEL_SHAM_2", "SEL_P", "SEL_OFF_0"]}
    capD = defaultdict(dict)
    for held, arms in arms_for.items():
        for arm in arms:
            for r in reps:
                cl = classes.get(((r, held), "SAME"), [])
                k = sum(1 for c in cl if any(fam_cap(r, held, "SAME", f, arm) for f in c))
                capD[(held, arm)][r] = {"CAP_D_SAME": k >= 2, "classes_solved": k, "n_classes": len(cl)}
    counts = {"%s|%s" % k: sum(x["CAP_D_SAME"] for x in v.values()) for k, v in capD.items()}
    # C1 PC_ONE
    pc1 = []
    for r in reps:
        same = sorted(fams_by[(r, "G1")]["SAME"])
        if len(same) < 2:
            continue
        f1, f2 = same
        dup = len(classes[((r, "G1"), "SAME")]) == 1
        if dup:
            pc1.append([r, "EXCLUDED_DUPLICATE_PAIR"])
            continue
        a = cells.get((r, "G1", "SAME", f1, "PC_ONE"), {})
        s1 = sum(solved(a.get(i)) for i in range(4))
        gain2 = fam_cap(r, "G1", "SAME", f2, "PC_ONE")
        pc1.append([r, "GOOD" if (s1 >= 3 and not gain2) else "BAD", s1, gain2])
    evaluated = [x for x in pc1 if x[1] != "EXCLUDED_DUPLICATE_PAIR"]
    pc1_ok = sum(1 for x in evaluated if x[1] == "GOOD")
    pcm = T.json.loads((T.OUTDIR / "T53_RESULT.json").read_text())["apparatus_controls"]
    n = len(reps)
    measured = (pcm["PC_MOTIF"]["reps_ok"] >= n - 1 and pcm["NC_OTHER"]["reps_ok"] >= n - 1
                and pc1_ok >= len(evaluated) - 2)
    k = math.ceil(0.58 * n)
    g1 = counts.get("G1|SEL_G1", 0)
    shams = {s: counts.get("%s|SEL_%s" % (s, s), 0) for s in ("SHAM_0", "SHAM_1", "SHAM_2")}
    out = {"class": "CORRECTION (post-exposure; T02 readouts were seen before the repair)",
           "PC_ONE_repaired": {"evaluated": len(evaluated), "good": pc1_ok, "rows": pc1},
           "disposition": "MEASURED_CORRECTION" if measured else "MEASUREMENT_FAILED",
           "distinct_class_counts": counts, "threshold_k": k,
           "readouts": {"R_SURVIVES": "YES" if g1 >= k else "NO", "G1": g1, "shams": shams,
                        "R_G1_SPECIFIC": "NO" if g1 - max(shams.values()) <= 0 else "YES"},
           "duplicate_classes": {"%s|%s" % (kk[0][0], kk[0][1]): v for kk, v in classes.items()
                                 if kk[1] == "SAME" and len(v) < 2}}
    (T.OUTDIR / "T53_CORRECTION.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("disposition", "PC_ONE_repaired", "readouts", "duplicate_classes")}, default=str))


if __name__ == "__main__":
    main()
