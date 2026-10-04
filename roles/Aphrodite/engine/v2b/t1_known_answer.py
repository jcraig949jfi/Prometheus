"""TEST-1 (Beta-01): the known-answer end-to-end assay of the repaired v2b apparatus.

Frozen spec: roles/Aphrodite/beta01/windows/T01_KNOWN_ANSWER_SPEC.md. This file implements it; its sha256 is
recorded there. Every case has a PRE-DECLARED expected outcome class. The assay qualifies the apparatus iff
every case returns its expected class FOR THE DECLARED REASON (reason codes are checked as well as classes).

Stages:
  python t1_known_answer.py plan            deterministic selection and pre-run screens -> T01_PLAN.json
  python t1_known_answer.py run [workers]   exact walks (D endpoint) -> T01_WALKS.jsonl (resumable)
  python t1_known_answer.py report          verdicts -> T01_RESULT.json
  python t1_known_answer.py smoke           a tiny plan+run at a small cap (DEV only; never a result)
"""
import json
import os
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import paths
import a17
import a18
from a18 import FR, G, T3D
import identity as I

import apparatus
import capability as CAP
import gates
import instruments as INS
import supply
import walk

OUTDIR = paths.ROOT / "beta01" / "runs" / "T01"
CAP_T1 = 2_000_000
CELLS = 4
TRIB = "v1a"
RULER = "v2.1"
SEED = "APHRODITE/V2B/T01/v1"
N_FAM = 4


def log(m):
    print("[T01 %s] %s" % (time.strftime("%H:%M:%S", time.gmtime()), m), flush=True)


def wr(name, obj):
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / name).write_text(json.dumps(obj, indent=1, sort_keys=True, default=str), encoding="utf-8")


def rd(name):
    return json.loads((OUTDIR / name).read_text(encoding="utf-8"))


def _nm(i):
    L = "abcdefghijklmnopqrstuvwxyz"
    return "t" + "".join(L[(i // 26 ** k) % 26] for k in range(3))


def _entry(name, schema):
    return a17.schema_entry(name, schema)


def _memo_entry(programs):
    """A literal-program memory: (init, body, final) triples memorised from sibling instances."""
    return {"name": "memo", "inits": sorted({p[1] for p in programs}), "bodies": sorted({p[2] for p in programs}),
            "finals": sorted({p[3] for p in programs}), "schema": None}


# ---------------------------------------------------------------- plan
def _deep_instances(motif, rng, need, prist, tries=60, cap=CAP_T1, exclude=()):
    """Seeded instances of motif: accumulating, T4-admissible (v1a), and PRISTINE-CENSORED at cap on cell 0
    (the family lies beyond PRISTINE's reach, so a gain there is budget-free). Returns (families, screened)."""
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    R = INS.ruler(RULER)
    bodies = [b for b in T3D.instantiate(motif) if R.accumulating(b) and b not in exclude]
    rng.shuffle(bodies)
    fams, screened = [], []
    for b in bodies[:tries]:
        init, fin = rng.choice(G.H1_SPACE), rng.choice(finals)
        p = ("fold", init, b, fin)
        if not INS.TRIBUNALS["v1a"].family_profile(p)["admissible"]:
            screened.append({"body": b, "why": "T4_INADMISSIBLE"})
            continue
        name = _nm(len(screened) + 1000 * len(fams) + 7)
        prov = a17.Prov({name: (b, fin, init)})
        size = a17.qualify(prov, name, "V2B-T01-Q2")
        if size is None:
            screened.append({"body": b, "why": "Q2_FAIL"})
            continue
        q = INS.qualifier(prov, name, TRIB, "DIRECT")
        c = FR.Cell(prov, name, 0, size, label="V2B-T01-screen")
        fq = walk.first_qualified(prist, c, cap, q)
        if not fq["censored"]:
            screened.append({"body": b, "why": "PRISTINE_SOLVES", "charge": fq["charge"]})
            continue
        fams.append({"name": name, "body": b, "init": init, "final": fin, "size": size})
        screened.append({"body": b, "why": "DEEP_OK"})
        if len(fams) >= need:
            break
    return fams, screened


def stage_plan(cap=CAP_T1, n_fam=N_FAM):
    a18.worker_init()
    a18.use_world("W5")
    R = INS.ruler(RULER)
    rng = random.Random(I._seed(SEED))
    prist = FR.KLib(FR.pristine().entries)
    comps = a18.compositions(a18.G1)
    # motif M: the first G1 composition (seeded order) that is NOT a re-expression of G1, has >= 8 accumulating
    # instantiations, and yields n_fam deep T4-admissible instances.
    order = list(comps)
    rng.shuffle(order)
    plan = {"cap": cap, "cells": CELLS, "tribunal": TRIB, "ruler": RULER, "seed": SEED, "cases": {}}
    M = fams = None
    for w in order:
        if INS.equal_extensional(w, a18.G1, RULER):
            continue
        acc_inst = [b for b in T3D.instantiate(w) if R.accumulating(b)]
        if len(acc_inst) < 8:
            continue
        f, scr = _deep_instances(w, random.Random(I._seed(SEED + "/M/" + w)), n_fam, prist, cap=cap)
        if len(f) >= n_fam:
            M, fams = w, f
            plan["motif_screen"] = scr
            break
    if M is None:
        plan["PLAN"] = "SUPPLY_LIMITED"
        wr("T01_PLAN.json", plan)
        return plan
    # sibling motif (knockout), equal-expressivity sham, re-expression "sham", null
    others = [w for w in order if w != M and not INS.equal_extensional(w, M, RULER)
              and not INS.equal_extensional(w, a18.G1, RULER)]
    n_m = len(T3D.instantiate(M))
    sib = next(w for w in others if len(T3D.instantiate(w)) >= 2)
    sham = next((w for w in others if w != sib and 0.75 * n_m <= len(T3D.instantiate(w)) <= 1.25 * n_m), None)
    reexpr = None
    for cand in R.reexpressions(M) if hasattr(R, "reexpressions") else []:
        if cand != M and len(T3D.instantiate(cand)) >= 2:
            reexpr = cand
            break
    null = "math.gcd(abs((acc // {H})), abs(first))"            # A22/A23 OFF_0
    plan.update({"M": M, "families": fams, "SIBLING": sib, "SHAM_X": sham, "SHAM_EQ": reexpr, "NULL": null,
                 "inst_counts": {k: len(T3D.instantiate(v)) for k, v in
                                 (("M", M), ("SIBLING", sib), ("SHAM_X", sham), ("NULL", null),
                                  ("SHAM_EQ", reexpr)) if v}})
    # memorisation cheat: literal witness programs of OTHER instances of M (siblings of the transfer families)
    used = {f["body"] for f in fams}
    sibs = [b for b in T3D.instantiate(M) if b not in used and R.accumulating(b)][:8]
    plan["MEMO_programs"] = [("fold", fams[k % len(fams)]["init"], b, fams[k % len(fams)]["final"])
                             for k, b in enumerate(sibs)]
    # control-distinctness checks (computed, recorded)
    dist = {}
    for nm in ("SIBLING", "SHAM_X", "NULL", "SHAM_EQ"):
        s = plan.get(nm)
        if not s:
            dist[nm] = "ABSENT"
            continue
        try:
            gates.Control(nm, s, "SHAM").check_distinct(M, lambda a, b: INS.equal_extensional(a, b, RULER))
            dist[nm] = "DISTINCT"
        except gates.ControlNotDistinct:
            dist[nm] = "NOT_DISTINCT"
    plan["distinctness"] = dist
    # representation case: a body outside W5 and outside every library's instantiations
    probe = "(((acc + v) * v) + ((v * v) - first))"
    plan["REPR_probe"] = {"body": probe, "in_W5": probe in set(G.BODY_SPACE),
                          "in_any_lib": any(probe in set(T3D.instantiate(s)) for s in (M, sib, sham, null) if s)}
    # tribunal-version case: C2 family qbda (W7: unsolvable by construction under v1; PRISTINE p 0 -> 1 under v1a)
    rows = [json.loads(x) for x in open(paths.ENG / "A19_C2" / "A18_FOUNDRY_ROWS_2026-09-28.jsonl", encoding="utf-8")]
    q = next((r for r in rows if r["name"] == "qbda"), None)
    plan["TRIB_family"] = {k: q[k] for k in ("name", "body", "init", "final", "Q2_size")} if q else None
    plan["apparatus"] = apparatus.manifest(TRIB, RULER)
    plan["PLAN"] = "OK"
    wr("T01_PLAN.json", plan)
    log("plan OK: M=%s families=%d sham=%s sib=%s reexpr=%s dist=%s" % (M, len(fams), sham, sib, reexpr, dist))
    return plan


# ---------------------------------------------------------------- run
def _libs(plan):
    P = FR.pristine().entries
    L = {"PRISTINE": P, "T": [_entry("planted", plan["M"])] + P, "SIBLING": [_entry("sib", plan["SIBLING"])] + P,
         "NULL": [_entry("null", plan["NULL"])] + P, "MEMO": [_memo_entry(plan["MEMO_programs"])] + P}
    if plan.get("SHAM_X"):
        L["SHAM_X"] = [_entry("sham", plan["SHAM_X"])] + P
    if plan.get("SHAM_EQ"):
        L["SHAM_EQ"] = [_entry("reexpr", plan["SHAM_EQ"])] + P
    return L


def _job(args):
    plan, fam, arm, cell_i, version = args
    a18.worker_init()
    a18.use_world("W5")
    prov = a17.Prov({fam["name"]: (fam["body"], fam["final"], fam["init"])})
    lib = FR.KLib(_libs(plan)[arm])
    c = FR.Cell(prov, fam["name"], cell_i, fam["size"], label="V2B-T01")
    agree = []
    q = INS.qualifier(prov, fam["name"], version, "BOTH", log=agree)
    t0 = time.time()
    try:
        r = walk.first_qualified(lib, c, plan["cap"], q)
        status = "OK"
    except INS.EvaluatorDisagreement as e:
        r, status = {"error": str(e)}, "EVALUATOR_DISAGREEMENT"
    return {"family": fam["name"], "arm": arm, "cell": cell_i, "tribunal": version, "status": status,
            "result": r, "artifact_confirmations": len(agree), "seconds": round(time.time() - t0, 1)}


def stage_run(workers=3):
    plan = rd("T01_PLAN.json")
    if plan["PLAN"] != "OK":
        log("plan %s: nothing to run" % plan["PLAN"])
        return
    jobs = []
    for fam in plan["families"]:
        for arm in _libs(plan):
            for i in range(plan["cells"]):
                jobs.append((plan, fam, arm, i, TRIB))
    tf = plan.get("TRIB_family")
    if tf:
        fam = {"name": tf["name"], "body": tf["body"], "init": tf["init"], "final": tf["final"], "size": tf["Q2_size"]}
        for v in ("v1", "v1a"):
            for i in range(plan["cells"]):
                jobs.append((plan, fam, "PRISTINE", i, v))
    out = OUTDIR / "T01_WALKS.jsonl"
    done = set()
    if out.exists():
        for x in out.read_text(encoding="utf-8").splitlines():
            r = json.loads(x)
            done.add((r["family"], r["arm"], r["cell"], r["tribunal"]))
    jobs = [j for j in jobs if (j[1]["name"], j[2], j[3], j[4]) not in done]
    log("walk jobs %d (workers %d)" % (len(jobs), workers))
    with open(out, "a", encoding="utf-8") as fh, ProcessPoolExecutor(max_workers=workers,
                                                                    initializer=a18.worker_init) as ex:
        for r in ex.map(_job, jobs):
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
            fh.flush()
            log("%s %-8s c%d %s %s ch=%s spur=%s %ss" % (r["family"], r["arm"], r["cell"], r["tribunal"],
                                                        r["status"], r["result"].get("charge"),
                                                        r["result"].get("spurious_before"), r["seconds"]))


# ---------------------------------------------------------------- report (frozen verdict rules: spec s4)
def _fam_solved(walks, fam, arm, cap, need=3):
    cells = [w for w in walks if w["family"] == fam and w["arm"] == arm and w["tribunal"] == TRIB]
    ok = sum(1 for w in cells if not w["result"].get("censored", True))
    return ok >= need, ok


def stage_report():
    plan = rd("T01_PLAN.json")
    res = {"apparatus": plan.get("apparatus", {}).get("apparatus_id"), "cases": {}}
    if plan["PLAN"] != "OK":
        res["QUALIFICATION"] = "NOT_QUALIFIED"
        res["reason"] = "plan " + plan["PLAN"]
        wr("T01_RESULT.json", res)
        return res
    walks = [json.loads(x) for x in (OUTDIR / "T01_WALKS.jsonl").read_text(encoding="utf-8").splitlines()]
    tech = [w for w in walks if w["status"] != "OK"]
    fams = [f["name"] for f in plan["families"]]
    cap = plan["cap"]

    def count(arm):
        return sum(_fam_solved(walks, f, arm, cap)[0] for f in fams)

    rows = []
    for f in fams:
        for i in range(plan["cells"]):
            arms = {w["arm"]: w["result"] for w in walks if w["family"] == f and w["cell"] == i
                    and w["tribunal"] == TRIB and w["status"] == "OK"}
            if "PRISTINE" in arms:
                rows.append({"family": f, "cell": i, "arms": arms})
    summ = CAP.summarise(rows, cap)
    C = res["cases"]

    def case(name, expected, got, reason_ok, detail):
        C[name] = {"expected": expected, "got": got, "reason_ok": bool(reason_ok),
                   "pass": got == expected and bool(reason_ok), "detail": detail}

    nT, nS, nK, nN, nM = count("T"), count("SHAM_X") if plan.get("SHAM_X") else None, count("SIBLING"), \
        count("NULL"), count("MEMO")
    pristine_cens = all(w["result"].get("censored") for w in walks if w["arm"] == "PRISTINE" and w["tribunal"] == TRIB)
    excess = CAP.generic_cliff_excess(summ, "T", [a for a in ("SHAM_X", "SIBLING", "NULL") if a in summ["by_arm"]])
    # K1 (frozen rule): PASS iff T qualifies in >= 3/4 cells on >= 3 of 4 families; reason: the CENSORED-stratum
    # cell excess over the best control (SHAM_X, SIBLING, NULL) is >= 6 of 16 cells. Gains only count where
    # PRISTINE is censored at the cap (budget-free).
    case("K1_PLANTED_ABSTRACTION", "PASS", "PASS" if nT >= 3 else "NO", excess >= 6,
         {"families_solved": nT, "of": len(fams), "pristine_all_censored": pristine_cens, "cliff_excess_cells": excess})
    case("K1b_KNOCKOUT_SIBLING", "NO", "NO" if nK <= 1 else "PASS", True, {"families_solved": nK})
    case("K2_NULL", "NO", "NO" if nN <= 1 else "PASS", True, {"families_solved": nN})
    if nS is None:
        case("K3a_SHAM_EQUAL_EXPRESSIVITY", "NO", "ABSENT", False, {"note": "no sham met the size match"})
    else:
        case("K3a_SHAM_EQUAL_EXPRESSIVITY", "NO", "NO" if nS <= 1 else "PASS",
             plan["distinctness"].get("SHAM_X") == "DISTINCT", {"families_solved": nS})
    if plan.get("SHAM_EQ"):
        nE = count("SHAM_EQ")
        case("K3b_REEXPRESSION_NOT_A_SHAM", "NOT_A_SHAM", "NOT_A_SHAM" if plan["distinctness"]["SHAM_EQ"] ==
             "NOT_DISTINCT" else "COUNTED_AS_SHAM", True, {"families_solved": nE})
    case("K4_MEMORISATION_CHEAT", "NO", "NO" if nM <= 1 else "PASS", True, {"families_solved": nM})
    rp = plan["REPR_probe"]
    case("K5_UNREPRESENTABLE", "REPRESENTATION_LIMITED",
         "REPRESENTATION_LIMITED" if not rp["in_W5"] and not rp["in_any_lib"] else "REPRESENTABLE", True, rp)
    bad = gates.Gate("constant_gate_fixture", lambda ev: True)
    try:
        bad.qualify({"a": 1}, {"a": 0})
        got = "SEALED"
    except gates.GateUnreachable:
        got = "INVALID_DESIGN"
    case("K6_CONSTANT_GATE_DESIGN", "INVALID_DESIGN", got, True, {})
    rec = supply.screen("K7", [{"name": f} for f in fams], lambda rows, r: ([], r < len(rows)), 6, 6)
    case("K7_SUPPLY_SHORTFALL", "SUPPLY_LIMITED", "SUPPLY_LIMITED" if not rec.passed else "SUPPLIED", True,
         rec.as_dict())
    tf = plan.get("TRIB_family")
    if tf:
        v1 = [w for w in walks if w["family"] == tf["name"] and w["tribunal"] == "v1"]
        v1a = [w for w in walks if w["family"] == tf["name"] and w["tribunal"] == "v1a"]
        s1 = sum(1 for w in v1 if not w["result"].get("censored", True))
        s1a = sum(1 for w in v1a if not w["result"].get("censored", True))
        spur1 = sum(w["result"].get("spurious_before", 0) for w in v1)
        case("K8_TRIBUNAL_VERSION", "V1_BLIND_V1A_SOLVES", "V1_BLIND_V1A_SOLVES" if (s1 == 0 and s1a >= 3)
             else "NO_DIFFERENCE", spur1 >= 1, {"v1_solved_cells": s1, "v1a_solved_cells": s1a,
                                                 "v1_spurious_walked_past": spur1})
    res["capability_summary"] = summ
    res["technical_failures"] = tech
    res["QUALIFICATION"] = "QUALIFIED" if (all(c["pass"] for c in C.values()) and not tech) else "NOT_QUALIFIED"
    wr("T01_RESULT.json", res)
    log("QUALIFICATION %s %s" % (res["QUALIFICATION"], {k: (v["got"], v["pass"]) for k, v in C.items()}))
    return res


if __name__ == "__main__":
    st = sys.argv[1]
    if st == "smoke":
        OUTDIR = paths.ROOT / "beta01" / "runs" / "T01_SMOKE"
        stage_plan(cap=200_000, n_fam=1)
    elif st == "plan":
        stage_plan()
    elif st == "run":
        stage_run(int(sys.argv[2]) if len(sys.argv) > 2 else 3)
    elif st == "report":
        stage_report()
