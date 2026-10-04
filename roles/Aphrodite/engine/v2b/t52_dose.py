"""TEST-3 (Beta-01): T52 -- VALIDATION-MULTIPLICITY DOSE RESPONSE of A23-geometry selection (rung R3 SELECTABLE).
Frozen spec: roles/Aphrodite/beta01/windows/T03_T52_SPEC.md.

A23 (E-011) gave VALIDATE = 2 instances of the planted motif m_A. Its donors then selected a composition EQUAL
to m_A in most replicates (T02 readout, unreadable: 35 / 40 ON donors). Question: is selection driven by the
NUMBER of direct examples of the planted structure? Is it recovery of what was shown, rather than abstraction
that generalises beyond the examples?

Dose d in {0, 1, 2}: VALIDATE = the first d of A23's own VALIDATE motif families for replicate r and arm A, plus
(2 - d) SPARE instances of A's OTHER motif o_A. Spares are qualified A23 foundry rows of source
'r|A|OTHER', p_PRISTINE <= 0.75, never used by A23 as TRANSFER. Everything else is A23's frozen donor
unchanged: OBSERVE families, panel, composition move, paired selection, R_VAL, the escrow and TAG=A23 cell
labels.
Dose 2 is run for G1 only, as a CONTINUITY check. It is A23's own VALIDATE, so it must reproduce A23's
selected schema.
Arms: G1, SHAM_0, SHAM_1, SHAM_2 (composition on; held = arm). Replicates: A23's 10 fillable.
Stages: plan | run [workers] | report.
"""
import os
os.environ["A18_TAG"] = "A23"          # A23's cell labels/seeds; set before the engine imports
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402

import paths  # noqa: E402
import a17  # noqa: E402
import a18  # noqa: E402
import a18_c1 as C  # noqa: E402
from a18 import FR  # noqa: E402

import apparatus  # noqa: E402
import instruments as INS  # noqa: E402
import supply  # noqa: E402

A23 = paths.ENG / "A23_C3R2C"
OUTDIR = paths.ROOT / "beta01" / "runs" / os.environ.get("V2B_T52_DIR", "T03_T52")
ON = ["G1", "SHAM_0", "SHAM_1", "SHAM_2"]
DOSES = [0, 1]
RULER = "v2.1"


def log(m):
    print("[T52 %s] %s" % (time.strftime("%H:%M:%S", time.gmtime()), m), flush=True)


def rdj(n):
    return json.loads((A23 / n).read_text(encoding="utf-8"))


def rdl(n):
    return [json.loads(x) for x in (A23 / n).read_text(encoding="utf-8").splitlines() if x.strip()]


def stage_plan():
    a18.worker_init()
    a18.use_world("W5")
    plan_a23 = rdj("A20_PLAN_2026-09-28.json")
    panel, motifs = plan_a23["panel"], plan_a23["plan"]
    roles = rdj("A18_ROLES_2026-09-28.json")
    rows = rdl("A20_FOUNDRY_ROWS_2026-09-28.jsonl")
    donors = rdl("A18_DONORS_2026-09-28.jsonl")
    reps = sorted({d["replicate"] for d in donors})
    jobs, supply_rec = [], {}
    for r in reps:
        fams = roles["CON/%d" % r]["families"]
        used = {f["name"] for f in fams}
        for A in ON:
            val_m = [f for f in fams if f["role"] == "VALIDATE" and f["tclass"] == A + ":MOTIF"]
            spares = sorted([x for x in rows if x.get("T4_qualified") and x["source"] == "%d|%s|OTHER" % (r, A)
                             and x.get("p_PRISTINE", 0) <= 0.75 and x["name"] not in used], key=lambda x: x["name"])
            # distinctness: a spare must not be interchangeable with a used motif VALIDATE family
            sp = [dict(s, role="VALIDATE", tclass=A + ":OTHERVAL", qualified_dev_size=s["Q2_size"]) for s in spares]
            for d in DOSES + ([2] if A == "G1" else []):
                need = 2 - d
                if len(val_m) < d or len(sp) < need:
                    supply_rec["%d|%s|%d" % (r, A, d)] = "SUPPLY_LIMITED"
                    continue
                keep = val_m[:d]
                add = sp[:need]
                if need and d and supply.interchangeable(keep[0], add[0]):
                    supply_rec["%d|%s|%d" % (r, A, d)] = "NOT_DISTINCT"
                    continue
                supply_rec["%d|%s|%d" % (r, A, d)] = "OK"
                # A23's family list and order, with ONLY arm A's VALIDATE motif slots changed (single-factor dose)
                drop = [f["name"] for f in val_m[d:]]
                fl, ins = [], list(add)
                for f in fams:
                    if f["name"] in drop:
                        if ins:
                            fl.append(ins.pop(0))
                        continue
                    fl.append(dict(f, qualified_dev_size=f["Q2_size"]))
                specs = {f["name"]: (f["body"], f["final"], f["init"]) for f in fl}
                jobs.append({"rep": r, "arm": A, "dose": d, "fams": fl, "specs": specs,
                             "motif": motifs[str(r)][A]["motif"], "other": motifs[str(r)][A]["other"]})
    plan = {"panel": panel, "jobs": jobs, "supply": supply_rec, "reps": reps,
            "apparatus": apparatus.manifest("v1", RULER), "note": "donor tribunal/qualification = A23's frozen instruments"}
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "T52_PLAN.json").write_text(json.dumps(plan, sort_keys=True, default=str), encoding="utf-8")
    ok = sum(1 for v in supply_rec.values() if v == "OK")
    log("plan: %d donor jobs; supply %s" % (len(jobs), {k: sum(1 for v in supply_rec.values() if v == k)
                                                       for k in set(supply_rec.values())}))
    return plan


def _job(j_panel):
    j, panel = j_panel
    a18.worker_init()
    a18.use_world("W5")
    t0 = time.time()
    cat = "CON%d" % j["rep"]
    d = C._donor_job((cat, j["arm"], j["rep"], j["fams"], j["specs"], panel, True, j["arm"]))
    # is the planted motif even a candidate here (exact screen against these validation cells)?
    prov = a17.Prov(j["specs"])
    size = {f["name"]: f["qualified_dev_size"] for f in j["fams"]}
    val = [f["name"] for f in j["fams"] if f["role"] == "VALIDATE"]
    cells = [FR.Cell(prov, f, j["rep"] * a17.R_VAL + k, size[f], label="%s-%s-val/r%d" % (a18.TAG, cat, j["rep"]))
             for f in val for k in range(a17.R_VAL)]
    m_reach = a18.hits_any_cell(j["motif"], cells)
    o_reach = a18.hits_any_cell(j["other"], cells)
    sel = d["selected_schema"]
    return {"rep": j["rep"], "arm": j["arm"], "dose": j["dose"], "selected_schema": sel,
            "selected_origin": d["selected_origin"], "COMPOSES_held": d["COMPOSES_held"],
            "n_composed_candidates": d["n_composed_candidates"], "motif_candidate": m_reach,
            "other_candidate": o_reach,
            "RECOVERED_MOTIF": bool(sel) and INS.equal_extensional(sel, j["motif"], RULER),
            "RECOVERED_OTHER": bool(sel) and INS.equal_extensional(sel, j["other"], RULER),
            "seconds": round(time.time() - t0, 1)}


def stage_run(workers=4):
    plan = json.loads((OUTDIR / "T52_PLAN.json").read_text(encoding="utf-8"))
    out = OUTDIR / "T52_DONORS.jsonl"
    done = set()
    if out.exists():
        done = {(x["rep"], x["arm"], x["dose"]) for x in map(json.loads, out.read_text(encoding="utf-8").splitlines())}
    todo = [j for j in plan["jobs"] if (j["rep"], j["arm"], j["dose"]) not in done]
    # continuity jobs first (dose 2), so a mismatch is seen early
    todo.sort(key=lambda j: (-j["dose"], j["arm"], j["rep"]))
    log("donor jobs todo %d workers %d" % (len(todo), workers))
    with open(out, "a", encoding="utf-8") as fh, ProcessPoolExecutor(max_workers=workers,
                                                                    initializer=a18.worker_init) as ex:
        for r in ex.map(_job, [(j, plan["panel"]) for j in todo]):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            log("r%d %-6s dose %d sel=%s rec_m=%s rec_o=%s cand_m=%s %ss" % (
                r["rep"], r["arm"], r["dose"], r["selected_schema"], r["RECOVERED_MOTIF"], r["RECOVERED_OTHER"],
                r["motif_candidate"], r["seconds"]))
    log("run done")


def stage_report():
    """Frozen rules: T03_T52_SPEC.md s4."""
    plan = json.loads((OUTDIR / "T52_PLAN.json").read_text(encoding="utf-8"))
    rows = [json.loads(x) for x in (OUTDIR / "T52_DONORS.jsonl").read_text(encoding="utf-8").splitlines()]
    a23 = {(d["replicate"], d["arm"]): d for d in rdl("A18_DONORS_2026-09-28.jsonl")}
    a23_plan = rdj("A20_PLAN_2026-09-28.json")["plan"]
    # continuity: dose-2 G1 re-run reproduces A23's selected schema
    cont = [(x["rep"], x["selected_schema"], a23[(x["rep"], "G1")]["selected_schema"]) for x in rows
            if x["dose"] == 2 and x["arm"] == "G1"]
    cont_ok = sum(a == b for _r, a, b in cont)
    # dose-2 readout for every arm comes from A23's own donors (identical inputs; continuity-checked on G1)
    d2 = []
    for (r, arm), d in a23.items():
        if arm in ON:
            m, o = a23_plan[str(r)][arm]["motif"], a23_plan[str(r)][arm]["other"]
            s = d["selected_schema"]
            d2.append({"rep": r, "arm": arm, "dose": 2, "selected_schema": s, "COMPOSES_held": d["COMPOSES_held"],
                       "RECOVERED_MOTIF": bool(s) and INS.equal_extensional(s, m, RULER),
                       "RECOVERED_OTHER": bool(s) and INS.equal_extensional(s, o, RULER),
                       "n_composed_candidates": d["n_composed_candidates"]})
    allr = [x for x in rows if x["dose"] in DOSES] + d2
    tab = {}
    for arm in ON + ["ALL"]:
        for dose in (0, 1, 2):
            xs = [x for x in allr if x["dose"] == dose and (arm == "ALL" or x["arm"] == arm)]
            if not xs:
                continue
            tab["%s|%d" % (arm, dose)] = {
                "n": len(xs), "SELECTED_COMPOSITION": sum(bool(x["COMPOSES_held"]) for x in xs),
                "RECOVERED_MOTIF": sum(x["RECOVERED_MOTIF"] for x in xs),
                "RECOVERED_OTHER": sum(x["RECOVERED_OTHER"] for x in xs),
                "motif_was_candidate": sum(bool(x.get("motif_candidate", True)) for x in xs),
                "chance_recovery": round(sum(1.0 / max(1, x["n_composed_candidates"]) for x in xs), 3)}
    n_cont = len(cont)
    measured = n_cont >= 9 and cont_ok >= n_cont - 1
    sup_ok = {d: sum(1 for k, v in plan["supply"].items() if k.endswith("|%d" % d) and v == "OK") for d in DOSES}
    res = {"continuity_dose2_G1": {"n": n_cont, "identical_selection": cont_ok, "rows": cont},
           "supply": sup_ok, "table": tab,
           "disposition": ("MEASURED" if measured and all(v >= 32 for v in sup_ok.values()) else
                           ("MEASUREMENT_FAILED" if not measured else "SUPPLY_LIMITED"))}
    A = lambda d: tab.get("ALL|%d" % d, {})      # noqa: E731
    res["readouts"] = {
        "R_RECOVERY_DOSE": [A(d).get("RECOVERED_MOTIF", 0) / max(1, A(d).get("n", 1)) for d in (0, 1, 2)],
        "R_FOLLOWS_SHOWN_STRUCTURE": (A(0).get("RECOVERED_OTHER", 0) / max(1, A(0).get("n", 1))),
        "R_ONE_EXAMPLE_SUFFICES": (A(1).get("RECOVERED_MOTIF", 0) / max(1, A(1).get("n", 1))) >=
                                  0.8 * (A(2).get("RECOVERED_MOTIF", 0) / max(1, A(2).get("n", 1)))}
    (OUTDIR / "T52_RESULT.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str), encoding="utf-8")
    log("disposition %s readouts %s" % (res["disposition"], res["readouts"]))
    return res


if __name__ == "__main__":
    st = sys.argv[1]
    {"plan": stage_plan, "run": lambda: stage_run(int(sys.argv[2]) if len(sys.argv) > 2 else 4),
     "report": stage_report}[st]()
