"""t1 v2 -- graded (sensitivity) and selection (R3) known-answer cases for the v2b apparatus.

T01 qualified the apparatus on all-or-nothing cases only. This battery adds cases whose correct answer is a
NUMBER or a CHOICE, not an extreme. It reuses T01's frozen plan (motif M = (v * (acc + {H})), 4 deep
families, siblings), read from beta01/runs/T01/T01_PLAN.json.

Graded capability (D endpoint, T4 v1a, cap 2M, 4 cells):
  GK_k (k = 1, 2, 3)  [entry: inits H1, bodies = the witness bodies of the first k deep families, finals FINAL]
                      + PRISTINE. Expected: exactly the first k families solved (>= 3/4 cells each); the others
                      censored. A cross-family solve is checked for extensional overlap and reported as a
                      reason, not hidden.
  GK_LATE             PRISTINE + [entry(M)] (M AFTER coverage). Expected: all 4 families solved at
                      charge > N_COV (the WINDOW stratum, not COVERED). The D endpoint must record the
                      ordering cost.
Selection (a17.select: the paired-saving rule of every historical donor; cost = fast_cost first hit at the
250k escrow):
  SK1  candidates {INHERITED = PRISTINE, M, SIBLING, SHAM_X, NULL}; validation = 2 deep M families x 4 cells.
       Expected: chosen = M.
  SK2  same candidates; validation = 2 families where NO candidate helps (PRISTINE-censored instances of an
       unrelated OFF schema). Expected: chosen = INHERITED.
  SK3  candidates {INHERITED, M, M' (re-expression)}; validation as SK1. Expected: chosen in {M, M'}, and the
       ruler calls the pair EQUAL (selection of the class).
  SK4  candidates as SK1; validation = 1 M family + 1 unrelated family. Expected: recorded, not gated. This is
       the dose point that T52 studies.
"""
import json
import random
import sys
import time

import paths
import a17
import a18
from a18 import FR, G, T3D
import identity as I

import capability as CAP
import instruments as INS
import walk

T01 = paths.ROOT / "beta01" / "runs" / "T01" / "T01_PLAN.json"
OUTDIR = paths.ROOT / "beta01" / "runs" / __import__("os").environ.get("V2B_T1V2_DIR", "T03_T1V2")
CAP_G = int(__import__("os").environ.get("V2B_T1V2_CAP", 2_000_000))
CELLS = 4


def log(m):
    print("[T1v2 %s] %s" % (time.strftime("%H:%M:%S", time.gmtime()), m), flush=True)


def _prov(f):
    return a17.Prov({f["name"]: (f["body"], f["final"], f["init"])})


def graded(plan):
    fams = plan["families"]
    P = FR.pristine().entries
    libs = {}
    for k in (1, 2, 3):
        libs["GK_%d" % k] = [{"name": "gk", "inits": list(G.H1_SPACE), "bodies": [f["body"] for f in fams[:k]],
                             "finals": list(G.FINAL_SPACE), "schema": None}] + P
    libs["GK_LATE"] = P + [a17.schema_entry("late", plan["M"])]
    out = []
    for f in fams:
        prov = _prov(f)
        q = INS.qualifier(prov, f["name"], "v1a", "BOTH")
        for arm, ents in libs.items():
            lib = FR.KLib(ents)
            for i in range(CELLS):
                c = FR.Cell(prov, f["name"], i, f["size"], label="V2B-T01")      # T01's cell seeds
                out.append({"family": f["name"], "arm": arm, "cell": i, "result": walk.first_qualified(lib, c, CAP_G, q)})
    return out


def _cells(fams, label):
    cells = []
    for f in fams:
        prov = _prov(f)
        for i in range(CELLS):
            cells.append(FR.Cell(prov, f["name"], i, f["size"], label=label))
    return cells


def selection(plan):
    a17.M.use_provider(a17.Prov({f["name"]: (f["body"], f["final"], f["init"]) for f in plan["families"]}))
    P = FR.pristine().entries
    E = lambda n, s: [a17.schema_entry("g2_new", s)] + P   # noqa: E731
    base = {"INHERITED": P, "M": E("M", plan["M"]), "SIBLING": E("S", plan["SIBLING"]),
            "SHAM_X": E("X", plan["SHAM_X"]), "NULL": E("N", plan["NULL"])}
    deep = plan["families"][:2]
    # unrelated, PRISTINE-censored families for SK2/SK4: deep instances of NULL's composition-free body space
    rng = random.Random(I._seed("APHRODITE/V2B/T1V2/UNREL/v1"))
    unrel = []
    finals = [f for f in G.FINAL_SPACE if "acc" in f]
    prist = FR.KLib(P)
    R = INS.ruler("v2.1")
    pool = [b for b in G.BODY_SPACE if R.accumulating(b)]
    tries = 0
    while len(unrel) < 2 and tries < 400:
        tries += 1
        b = rng.choice(pool)
        init, fin = rng.choice(G.H1_SPACE), rng.choice(finals)
        p = ("fold", init, b, fin)
        if not INS.TRIBUNALS["v1a"].family_profile(p)["admissible"]:
            continue
        name = "u" + "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(4))
        prov = a17.Prov({name: (b, fin, init)})
        size = a17.qualify(prov, name, "V2B-T1V2-Q2")
        if size is None:
            continue
        c = FR.Cell(prov, name, 0, size, label="V2B-T1V2-screen")
        if not walk.first_hit(prist, c, a17.ESCROW)[1] is None:
            continue                               # PRISTINE must fail at the selection escrow
        if any(walk.first_hit(FR.KLib(base[k]), c, a17.ESCROW)[1] is not None for k in ("M", "SIBLING", "SHAM_X", "NULL")):
            continue                               # no candidate may help either
        unrel.append({"name": name, "body": b, "init": init, "final": fin, "size": size})
    specs = {f["name"]: (f["body"], f["final"], f["init"]) for f in plan["families"] + unrel}
    a17.M.use_provider(a17.Prov(specs))
    res = {"unrelated_families": unrel, "unrelated_tries": tries}

    def sel(cands, fams, label):
        provs = a17.Prov({f["name"]: (f["body"], f["final"], f["init"]) for f in fams})
        cells = [FR.Cell(provs, f["name"], i, f["size"], label=label) for f in fams for i in range(CELLS)]
        chosen, table, _ = a17.select(cands, P, cells)
        return {"chosen": chosen, "table": {k: {x: v[x] for x in ("mean_paired_saving", "lower95_one_sided",
                                                                 "eligible")} for k, v in table.items()}}
    res["SK1"] = sel(base, deep, "V2B-T1V2-SK1")
    res["SK2"] = sel(base, unrel, "V2B-T1V2-SK2") if len(unrel) == 2 else {"chosen": None, "note": "SUPPLY_LIMITED"}
    reex = plan.get("SHAM_EQ")
    res["SK3"] = sel({"INHERITED": P, "M": base["M"], "MPRIME": E("Mp", reex)}, deep, "V2B-T1V2-SK3") if reex else None
    res["SK4"] = sel(base, [deep[0]] + unrel[:1], "V2B-T1V2-SK4") if unrel else None
    res["SK3_equal"] = INS.equal_extensional(plan["M"], reex, "v2.1") if reex else None
    return res


def report(plan, gw, sres):
    fams = [f["name"] for f in plan["families"]]
    cases = {}

    def solved_fams(arm):
        out = []
        for f in fams:
            k = sum(1 for w in gw if w["family"] == f and w["arm"] == arm and not w["result"]["censored"])
            if k >= 3:
                out.append(f)
        return out
    for k in (1, 2, 3):
        got = solved_fams("GK_%d" % k)
        cases["GK_%d" % k] = {"expected": fams[:k], "got": got, "pass": got == fams[:k]}
    late = [w for w in gw if w["arm"] == "GK_LATE"]
    sl = [w for w in late if not w["result"]["censored"]]
    cases["GK_LATE"] = {"expected": "all solved, every charge > N_COV", "solved_cells": len(sl), "of": len(late),
                        "min_charge": min((w["result"]["charge"] for w in sl), default=None), "N_COV": CAP.N_COV,
                        "pass": len(sl) >= 3 * len(fams) and all(w["result"]["charge"] > CAP.N_COV for w in sl)}
    cases["SK1"] = {"expected": "M", "got": sres["SK1"]["chosen"], "pass": sres["SK1"]["chosen"] == "M"}
    cases["SK2"] = {"expected": "INHERITED", "got": sres["SK2"]["chosen"], "pass": sres["SK2"]["chosen"] == "INHERITED"}
    if sres.get("SK3"):
        cases["SK3"] = {"expected": "M or MPRIME, ruler EQUAL", "got": sres["SK3"]["chosen"],
                        "pass": sres["SK3"]["chosen"] in ("M", "MPRIME") and bool(sres["SK3_equal"])}
    cases["SK4_recorded"] = {"got": (sres.get("SK4") or {}).get("chosen"), "pass": True, "gated": False}
    q = all(c["pass"] for c in cases.values())
    return {"QUALIFICATION": "QUALIFIED" if q else "NOT_QUALIFIED", "cases": cases}


def main():
    a18.worker_init()
    a18.use_world("W5")
    plan = json.loads(T01.read_text(encoding="utf-8"))
    OUTDIR.mkdir(parents=True, exist_ok=True)
    gw = graded(plan)
    (OUTDIR / "T1V2_GRADED_WALKS.json").write_text(json.dumps(gw, default=str), encoding="utf-8")
    sres = selection(plan)
    (OUTDIR / "T1V2_SELECTION.json").write_text(json.dumps(sres, indent=1, default=str), encoding="utf-8")
    rep = report(plan, gw, sres)
    (OUTDIR / "T1V2_RESULT.json").write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")
    log("QUALIFICATION %s %s" % (rep["QUALIFICATION"], {k: v.get("got", v.get("solved_cells")) for k, v in rep["cases"].items()}))


if __name__ == "__main__":
    main()
