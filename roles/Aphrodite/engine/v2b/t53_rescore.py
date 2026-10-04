"""TEST-2 (Beta-01): T53 -- D-stratified, tribunal-v1a re-score of A23 (E-011) capability. NEW EXPERIMENT on
preserved A23 data (donor selections, roles, families). It is correction/bridge-class evidence: A23's label is
never changed. Frozen spec: roles/Aphrodite/beta01/windows/T02_T53_SPEC.md.

Libraries per replicate r and held abstraction A (A in G1, SHAM_0, SHAM_1, SHAM_2), on A's TRANSFER families
(2 SAME = motif recurrence, 2 OTHER = a different composition of A), 4 cells each:
  PRISTINE                 FR.pristine()
  START_A                  a18.start_library(A, panel)
  SEL_<arm>                the donor's selected library, for each arm holding A (G1 -> G1 and G1_NC)
  SEL_P, SEL_OFF_0         LIVE controls: the P / OFF_0 donors' selected libraries on the SAME families. In A23
                           these arms could not score on REUSED/CAPABILITY_SAME by construction (no families
                           were assigned to them)
G1 families only (apparatus sensitivity inside the run):
  PC_MOTIF   [entry(m_G1)] + START_G1                 known answer: solves every family START cannot
  PC_ONE     [single-body entry: SAME family #1's witness body, inits H1, finals FINAL] + START_G1
             known answer: solves SAME #1 and NOT SAME #2 (unless SAME #2 is extensionally reachable from that body:
             recorded as a reason)
  NC_OTHER   [entry(o_G1)] + START_G1 on the SAME families    known answer: no SAME gain
Every walk: walk.first_qualified at CAP = 10,000,000 (the historical LADDER_CAP), tribunal T4 v1a (DIRECT path
with ARTIFACT confirmation of every positive), world W5, A23's cell seeds and dev sizes (Q2_size).
Stages: plan | run [workers] | report.
"""
import hashlib
import json
import math
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

import paths
import a17
import a18
from a18 import FR, G, T3D

import apparatus
import capability as CAP
import instruments as INS
import walk

A23 = paths.ENG / "A23_C3R2C"
OUTDIR = paths.ROOT / "beta01" / "runs" / __import__("os").environ.get("V2B_T53_DIR", "T02_T53")
CAP_T = int(__import__("os").environ.get("V2B_T53_CAP", 40 * a17.ESCROW))   # 10M frozen; env override = smoke only
CELLS = 4
TRIB = "v1a"
RULER = "v2.1"
ON = ["G1", "SHAM_0", "SHAM_1", "SHAM_2"]
LABEL = "A23-CON%d-rx"              # A23's transfer cell label pattern (a18_c1._transfer_job): '%s-%s-rx' % (TAG, cat)


def log(m):
    print("[T53 %s] %s" % (time.strftime("%H:%M:%S", time.gmtime()), m), flush=True)


def rdj(name):
    return json.loads((A23 / name).read_text(encoding="utf-8"))


def rdl(name):
    return [json.loads(x) for x in (A23 / name).read_text(encoding="utf-8").splitlines() if x.strip()]


def lib_key(entries):
    return hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()[:16]


def stage_plan():
    a18.worker_init()
    a18.use_world("W5")
    panel = rdj("A20_PLAN_2026-09-28.json")["panel"]
    plan_m = rdj("A20_PLAN_2026-09-28.json")["plan"]
    roles = rdj("A18_ROLES_2026-09-28.json")
    donors = rdl("A18_DONORS_2026-09-28.jsonl")
    by = {(d["replicate"], d["arm"]): d for d in donors}
    reps = sorted({d["replicate"] for d in donors})
    libs, jobs, meta = {}, [], {"reps": reps, "families": {}, "recovery": {}}

    def add_lib(entries):
        k = lib_key(entries)
        libs.setdefault(k, entries)
        return k

    P = add_lib(FR.pristine().entries)
    for r in reps:
        fams = {f["name"]: f for f in roles["CON/%d" % r]["families"]}
        for A in ON:
            same = sorted(n for n, f in fams.items() if f["tclass"] == A + ":SAME")
            other = sorted(n for n, f in fams.items() if f["tclass"] == A + ":OTHER")
            start = a18.start_library(A, panel)[0]
            arms = {"PRISTINE": P, "START": add_lib(start)}
            holders = ["G1", "G1_NC"] if A == "G1" else [A]
            for arm in holders + ["P", "OFF_0"]:
                d = by.get((r, arm))
                if d:
                    arms["SEL_" + arm] = add_lib(d["selected_entries"])
                    if arm in holders:
                        m = plan_m[str(r)][A]["motif"]
                        s = d["selected_schema"]
                        meta["recovery"]["%d|%s" % (r, arm)] = (
                            "NONE" if not s else ("RECOVERED" if INS.equal_extensional(s, m, RULER)
                                                  else ("COMPOSES_HELD" if d.get("COMPOSES_held") else "OTHER")))
            fam_sets = {"SAME": same, "OTHER": other}
            if A == "G1" and same:
                m, o = plan_m[str(r)]["G1"]["motif"], plan_m[str(r)]["G1"]["other"]
                w1 = fams[same[0]]["body"]
                arms["PC_MOTIF"] = add_lib([a17.schema_entry("pc_motif", m)] + start)
                arms["PC_ONE"] = add_lib([{"name": "pc_one", "inits": list(G.H1_SPACE), "bodies": [w1],
                                           "finals": list(G.FINAL_SPACE), "schema": None}] + start)
                arms["NC_OTHER"] = add_lib([a17.schema_entry("nc_other", o)] + start)
            for cls, names in fam_sets.items():
                for n in names:
                    f = fams[n]
                    meta["families"][n] = {"rep": r, "held": A, "cls": cls, "body": f["body"], "init": f["init"],
                                           "final": f["final"], "size": f["Q2_size"]}
                    for arm, k in arms.items():
                        if arm in ("PC_MOTIF", "PC_ONE", "NC_OTHER") and cls != "SAME":
                            continue
                        for i in range(CELLS):
                            jobs.append({"rep": r, "held": A, "cls": cls, "family": n, "arm": arm, "lib": k,
                                         "cell": i})
    uniq = {}
    for j in jobs:
        uniq.setdefault((j["lib"], j["family"], j["cell"]), j)
    plan = {"cap": CAP_T, "cells": CELLS, "tribunal": TRIB, "ruler": RULER, "jobs": jobs,
            "unique_walks": len(uniq), "libs": libs, "meta": meta, "apparatus": apparatus.manifest(TRIB, RULER)}
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "T53_PLAN.json").write_text(json.dumps(plan, sort_keys=True, default=str), encoding="utf-8")
    log("plan: reps %s jobs %d unique walks %d libs %d" % (reps, len(jobs), len(uniq), len(libs)))
    return plan


def _walk(args):
    libk, fam, cell_i, entries, spec, size = args
    a18.worker_init()
    a18.use_world("W5")
    name = fam
    prov = a17.Prov({name: (spec["body"], spec["final"], spec["init"])})
    a17.M.use_provider(prov)
    c = FR.Cell(prov, name, cell_i, size, label=LABEL % spec["rep"])
    conf = []
    q = INS.qualifier(prov, name, TRIB, "BOTH", log=conf)
    t0 = time.time()
    try:
        r = walk.first_qualified(FR.KLib(entries), c, CAP_T, q)
        st = "OK"
    except INS.EvaluatorDisagreement as e:
        r, st = {"error": str(e)}, "EVALUATOR_DISAGREEMENT"
    return {"lib": libk, "family": fam, "cell": cell_i, "status": st, "result": r,
            "artifact_confirmations": len(conf), "seconds": round(time.time() - t0, 1)}


def stage_run(workers=3):
    plan = json.loads((OUTDIR / "T53_PLAN.json").read_text(encoding="utf-8"))
    out = OUTDIR / "T53_WALKS.jsonl"
    done = set()
    if out.exists():
        done = {(x["lib"], x["family"], x["cell"]) for x in map(json.loads, out.read_text(encoding="utf-8").splitlines())}
    uniq = {}
    for j in plan["jobs"]:
        uniq.setdefault((j["lib"], j["family"], j["cell"]), j)
    todo = [k for k in uniq if k not in done]
    # order: cheap libraries first is not needed; deterministic order by key
    todo.sort()
    log("unique walks %d, todo %d, workers %d" % (len(uniq), len(todo), workers))
    meta = plan["meta"]["families"]
    args = [(k[0], k[1], k[2], plan["libs"][k[0]], meta[k[1]], meta[k[1]]["size"]) for k in todo]
    with open(out, "a", encoding="utf-8") as fh, ProcessPoolExecutor(max_workers=workers,
                                                                    initializer=a18.worker_init) as ex:
        n = 0
        for r in ex.map(_walk, args, chunksize=2):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            n += 1
            if n % 50 == 0:
                log("%d/%d" % (n, len(args)))
    log("run done")


def _sign_p(a, b):
    n = a + b
    return sum(math.comb(n, k) for k in range(a, n + 1)) / 2 ** n if n else 1.0


def stage_report():
    """Frozen rules: T02_T53_SPEC.md s4."""
    plan = json.loads((OUTDIR / "T53_PLAN.json").read_text(encoding="utf-8"))
    walks = {(w["lib"], w["family"], w["cell"]): w for w in
             map(json.loads, (OUTDIR / "T53_WALKS.jsonl").read_text(encoding="utf-8").splitlines())}
    tech = [k for k, w in walks.items() if w["status"] != "OK"]
    cap = plan["cap"]
    # per (rep, held, family, arm): cells
    cells = defaultdict(dict)
    for j in plan["jobs"]:
        w = walks.get((j["lib"], j["family"], j["cell"]))
        if w and w["status"] == "OK":
            cells[(j["rep"], j["held"], j["cls"], j["family"], j["arm"])][j["cell"]] = w["result"]

    def solved(res):
        return res is not None and not res.get("censored", True)

    def fam_cap(rep, held, fam, arm):
        """family counts for `arm` iff in >= 2 of 4 cells arm qualifies <= cap AND START is censored at cap."""
        a = cells.get((rep, held, "SAME", fam, arm)) or cells.get((rep, held, "OTHER", fam, arm)) or {}
        cls = "SAME" if (rep, held, "SAME", fam, arm) in cells else "OTHER"
        s = cells.get((rep, held, cls, fam, "START"), {})
        k = sum(1 for i in range(plan["cells"]) if solved(a.get(i)) and s.get(i) and s[i].get("censored"))
        return k >= 2

    fams_by = defaultdict(lambda: {"SAME": [], "OTHER": []})
    for n, f in plan["meta"]["families"].items():
        fams_by[(f["rep"], f["held"])][f["cls"]].append(n)
    reps = plan["meta"]["reps"]
    arms_for = {"G1": ["SEL_G1", "SEL_G1_NC", "SEL_P", "SEL_OFF_0", "PC_MOTIF", "PC_ONE", "NC_OTHER"],
                "SHAM_0": ["SEL_SHAM_0", "SEL_P", "SEL_OFF_0"], "SHAM_1": ["SEL_SHAM_1", "SEL_P", "SEL_OFF_0"],
                "SHAM_2": ["SEL_SHAM_2", "SEL_P", "SEL_OFF_0"]}
    capD = defaultdict(dict)        # (held, arm) -> rep -> {"SAME": bool, "OTHER": bool, "n_same": k}
    for held, arms in arms_for.items():
        for arm in arms:
            for r in reps:
                fs = fams_by[(r, held)]
                if not fs["SAME"]:
                    continue
                ks = sum(fam_cap(r, held, f, arm) for f in fs["SAME"])
                ko = sum(fam_cap(r, held, f, arm) for f in fs["OTHER"])
                capD[(held, arm)][r] = {"CAP_D_SAME": ks >= 2, "n_same": ks, "CAP_D_OTHER": ko >= 2, "n_other": ko}
    counts = {"%s|%s" % k: {"n": len(v), "CAP_D_SAME": sum(x["CAP_D_SAME"] for x in v.values()),
                            "CAP_D_OTHER": sum(x["CAP_D_OTHER"] for x in v.values())} for k, v in capD.items()}
    # historical bridge
    hist = json.loads((A23 / "A23_C3R2C_RESULT_2026-09-28.json").read_text(encoding="utf-8"))["ladders"]
    bridge = {}
    for held in ON:
        for arm in ([held] if held != "G1" else ["G1", "G1_NC"]):
            agree = dis = []
            rows = []
            for r in reps:
                h = hist.get(arm, {}).get("CON%d" % r)
                n = capD.get((held, "SEL_" + arm), {}).get(r)
                if h is not None and n is not None:
                    rows.append((r, bool(h["CAPABILITY_SAME"]), n["CAP_D_SAME"]))
            bridge[arm] = {"rows": rows, "agree": sum(a == b for _r, a, b in rows),
                           "hist_only": sum(a and not b for _r, a, b in rows),
                           "new_only": sum(b and not a for _r, a, b in rows)}
    # live-control sign tests on G1 families
    def sgn(a_arm, c_arm, held="G1"):
        A, Cc = capD[(held, a_arm)], capD[(held, c_arm)]
        a = sum(1 for r in A if A[r]["CAP_D_SAME"] and not Cc.get(r, {}).get("CAP_D_SAME"))
        b = sum(1 for r in Cc if Cc[r]["CAP_D_SAME"] and not A.get(r, {}).get("CAP_D_SAME"))
        return {"a": a, "b": b, "p": round(_sign_p(a, b), 5)}
    live = {c: sgn("SEL_G1", c) for c in ("SEL_G1_NC", "SEL_P", "SEL_OFF_0")}
    g1 = counts.get("G1|SEL_G1", {}).get("CAP_D_SAME", 0)
    shams = {s: counts.get("%s|SEL_%s" % (s, s), {}).get("CAP_D_SAME", 0) for s in ("SHAM_0", "SHAM_1", "SHAM_2")}
    # motif recovery split
    rec = plan["meta"]["recovery"]
    split = defaultdict(lambda: {"n": 0, "CAP_D_SAME": 0})
    for held in ON:
        arm = held
        for r in reps:
            x = capD.get((held, "SEL_" + arm), {}).get(r)
            if x is None:
                continue
            k = rec.get("%d|%s" % (r, arm), "NA")
            split[k]["n"] += 1
            split[k]["CAP_D_SAME"] += int(x["CAP_D_SAME"])
    # apparatus controls (G1 families)
    def pc(arm):
        ok = 0
        detail = []
        for r in reps:
            fs = fams_by[(r, "G1")]["SAME"]
            if not fs:
                continue
            if arm == "PC_ONE":
                f1, f2 = fs[0], fs[1] if len(fs) > 1 else None
                a = cells.get((r, "G1", "SAME", f1, arm), {})
                b = cells.get((r, "G1", "SAME", f2, arm), {}) if f2 else {}
                s1 = sum(solved(a.get(i)) for i in range(plan["cells"]))
                s2 = sum(solved(b.get(i)) for i in range(plan["cells"]))
                good = s1 >= 3 and s2 <= 1
            elif arm == "PC_MOTIF":
                need = [f for f in fs if any((cells.get((r, "G1", "SAME", f, "START"), {}).get(i) or {}).get("censored")
                                             for i in range(plan["cells"]))]
                good = all(sum(solved(cells.get((r, "G1", "SAME", f, arm), {}).get(i)) for i in range(plan["cells"]))
                           >= 3 for f in need)
                s1, s2 = len(need), None
            else:   # NC_OTHER
                g = sum(fam_cap(r, "G1", f, arm) for f in fs)
                good, s1, s2 = g == 0, g, None
            ok += int(good)
            detail.append([r, good, s1, s2])
        return {"reps_ok": ok, "n": len(detail), "detail": detail}
    pcs = {a: pc(a) for a in ("PC_MOTIF", "PC_ONE", "NC_OTHER")}
    n = len(reps)
    k = math.ceil(0.58 * n)
    measurement_ok = (pcs["PC_MOTIF"]["reps_ok"] >= n - 1 and pcs["PC_ONE"]["reps_ok"] >= n - 2
                      and pcs["NC_OTHER"]["reps_ok"] >= n - 1)
    if tech:
        disp = "TECHNICAL_FAILURE"
    elif not measurement_ok:
        disp = "MEASUREMENT_FAILED"
    else:
        disp = "MEASURED"
    res = {"apparatus": plan["apparatus"]["apparatus_id"], "cap": cap, "n_reps": n, "threshold_k": k,
           "technical_failures": tech[:20], "n_technical": len(tech), "disposition": disp,
           "apparatus_controls": pcs, "counts": counts, "bridge_A23_CAPABILITY_SAME": bridge,
           "live_control_sign_tests_G1": live, "generic_cliff_excess_G1_over_shams": g1 - max(shams.values()),
           "motif_recovery_split": dict(split),
           "readouts": {
               "R_SURVIVES": "YES" if g1 >= k else "NO",
               "R_G1_SPECIFIC": "NO" if g1 - max(shams.values()) <= 0 else "YES",
               "R_LIVE_CONTROLS_BEATEN": all(v["p"] < 0.05 for v in live.values()),
               "R_RECOVERY_ONLY": (dict(split).get("RECOVERED", {}).get("CAP_D_SAME", 0) > 0 and
                                   sum(v["CAP_D_SAME"] for kk, v in split.items() if kk != "RECOVERED") == 0)}}
    # D stratification summary for G1 SAME families: SEL_G1 vs START reference
    rows = []
    for (r, held, cls, fam, arm), cc in cells.items():
        if held == "G1" and cls == "SAME" and arm in ("SEL_G1", "START", "SEL_P", "SEL_OFF_0", "SEL_G1_NC"):
            for i, v in cc.items():
                rows.append(((r, fam, i), arm, v))
    by_cell = defaultdict(dict)
    for key, arm, v in rows:
        by_cell[key][arm] = v
    summ = CAP.summarise([{"family": k[1], "cell": k[2], "arms": v} for k, v in by_cell.items() if "START" in v],
                         cap, ref="START")
    res["D_stratified_G1_SAME_vs_START"] = summ
    # continuity: A23 transfer cells where A23's SELECTED first hit qualified (v1) at <= 250k must reproduce the same
    # charge here whenever that program is also v1a-qualified (first qualified == first hit).
    trans = rdl("A18_TRANSFER_2026-09-28.jsonl")
    arm2lib = {}
    for j in plan["jobs"]:
        if j["arm"].startswith("SEL_"):
            arm2lib[(j["rep"], j["arm"][4:], j["family"])] = j["lib"]
    rep_n = rep_eq = 0
    for t in trans:
        r = int(t["catalog"][3:])
        lk = arm2lib.get((r, t["arm"], t["family"]))
        if not lk:
            continue
        for i, c in enumerate(t["cells"]):
            if c["SELECTED"]["qualified"] and c["SELECTED"]["charge"] <= a17.ESCROW:
                w = walks.get((lk, t["family"], i))
                if w and w["status"] == "OK" and not w["result"]["censored"] and w["result"]["spurious_before"] == 0:
                    rep_n += 1
                    rep_eq += int(w["result"]["charge"] == c["SELECTED"]["charge"])
    res["continuity_A23_selected_charges"] = {"comparable_cells": rep_n, "identical": rep_eq}
    (OUTDIR / "T53_RESULT.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str), encoding="utf-8")
    log("disposition %s readouts %s" % (disp, res["readouts"]))
    return res


if __name__ == "__main__":
    st = sys.argv[1]
    if st == "plan":
        stage_plan()
    elif st == "run":
        stage_run(int(sys.argv[2]) if len(sys.argv) > 2 else 3)
    elif st == "report":
        stage_report()
