"""W7 PKG-6 (2): downstream consequences of fix (a) (T4 v1a) for the frozen C2
(A19) and C3 (A20) assays.
  1. Role draws: re-run the frozen role assignment (a18_c1.assign_roles for C2,
     a20_c3.assign for C3) with the foundry p_PRISTINE values that v1a implies
     (from W7_T4DEV_ROWS.jsonl) and diff the family lists per replicate.
  2. C2 transfer cells of every flipped family that served as TRANSFER: re-walk
     SELECTED / START / PRISTINE (same labels, same libraries, 250k) and score
     the first hit with v1 and v1a (direct). Reports SOLVED-relevant flips.
Single core. Writes W7_DOWNSTREAM_FIXA.json.
"""
import json

from w7_common import *              # noqa: F401,F403
import tribunal_t4 as T4             # noqa: E402
import tribunal_t4_v1a as T4A        # noqa: E402

A19 = ENG / "A19_C2"


def main():
    a18.worker_init()
    dev = {(x["tag"], x["name"]): x for x in map(json.loads, open(HERE / "W7_T4DEV_ROWS.jsonl"))}
    out = {"roles": {}, "transfer": []}
    # ---- C2 roles
    rows19 = rows("A19", t4=False)
    mod = []
    flipped19 = []
    for r in rows19:
        r2 = dict(r)
        d = dev.get(("A19", r["name"]))
        if d and "p_PRISTINE_v1a" in d and d["p_PRISTINE_v1a"] != r.get("p_PRISTINE"):
            r2["p_PRISTINE"] = d["p_PRISTINE_v1a"]
            r2["p_L1"] = d.get("p_L1_v1a", r.get("p_L1"))
            flipped19.append(r["name"])
        mod.append(r2)
    frozen_roles = json.loads((A19 / "A18_ROLES_2026-09-28.json").read_text())
    ch = {}
    for supply, n in C.NREP.items():
        for rep in range(n):
            a, _ = C.assign_roles(rows19, supply, rep)
            b, okb = C.assign_roles(mod, supply, rep)
            key = "%s/%d" % (supply, rep)
            fa = sorted((f["name"], f["role"]) for f in a)
            fb = sorted((f["name"], f["role"]) for f in b)
            fr = sorted((f["name"], f["role"]) for f in frozen_roles[key]["families"])
            ch[key] = {"reproduces_frozen": fa == fr, "changed": fa != fb, "ok_v1a": okb,
                       "n_families": len(fa), "n_same": len(set(fa) & set(fb)),
                       "removed": sorted(set(fa) - set(fb)), "added": sorted(set(fb) - set(fa))}
    out["roles"]["C2"] = {"flipped_families": flipped19, "replicates": ch}
    # ---- C3 roles
    import a20_c3 as C3
    rows20 = rows("A20", t4=False)
    mod20, flipped20 = [], []
    for r in rows20:
        r2 = dict(r)
        d = dev.get(("A20", r["name"]))
        if d and "p_PRISTINE_v1a" in d and d["p_PRISTINE_v1a"] != r.get("p_PRISTINE"):
            r2["p_PRISTINE"] = d["p_PRISTINE_v1a"]
            flipped20.append(r["name"])
        mod20.append(r2)
    ch3 = {}
    for rep in range(8):
        a, _ = C3.assign(rows20, rep)
        b, _ = C3.assign(mod20, rep)
        fa = sorted((f["name"], f["role"]) for f in a)
        fb = sorted((f["name"], f["role"]) for f in b)
        ch3[str(rep)] = {"changed": fa != fb, "removed": sorted(set(fa) - set(fb)),
                         "added": sorted(set(fb) - set(fa))}
    out["roles"]["C3"] = {"flipped_families": flipped20, "replicates": ch3}
    # ---- C2 transfer cells of flipped TRANSFER families
    panel = json.loads((A19 / "A18_PANEL_2026-09-28.json").read_text())["panel"]
    donors = [json.loads(x) for x in open(A19 / "A18_DONORS_2026-09-28.jsonl")]
    trows = [json.loads(x) for x in open(A19 / "A18_TRANSFER_2026-09-28.jsonl")]
    byname = {r["name"]: r for r in rows19}
    for t in trows:
        if t["family"] not in flipped19:
            continue
        d = [x for x in donors if x["catalog"] == t["catalog"] and x["arm"] == t["arm"]][0]
        r = byname[t["family"]]
        prov = prov_of(r)
        T4.use_provider(prov)
        w = ("fold", r["init"], r["body"], r["final"])
        libs_ = {"SELECTED": FR.KLib(d["selected_entries"]),
                 "START": FR.KLib(a18.start_library(C.HELD[d["arm"]], panel)[0]),
                 "PRISTINE": FR.KLib(FR.pristine().entries)}
        cells_ = []
        for i, c0 in enumerate(t["cells"]):
            c = FR.Cell(prov, r["name"], i, r["Q2_size"], label="A19-%s-rx" % t["catalog"])
            row = {}
            for k, lib in libs_.items():
                chg, prog = a18.fast_cost(lib, c, FR.ESCROW)
                v1 = bool(prog) and T4A.direct_score(tuple(prog), r["name"], w, "v1")["qualified"]
                va = bool(prog) and T4A.direct_score(tuple(prog), r["name"], w, "v1a")["qualified"]
                row[k] = {"charge": chg, "repro": chg == c0[k]["charge"] and v1 == c0[k]["qualified"],
                          "v1": v1, "v1a": va}
            cells_.append(row)
        solved_v1 = any(c["SELECTED"]["v1"] and not c["START"]["v1"] for c in cells_)
        solved_va = any(c["SELECTED"]["v1a"] and not c["START"]["v1a"] for c in cells_)
        out["transfer"].append({"catalog": t["catalog"], "arm": t["arm"], "family": t["family"], "cells": cells_,
                                "SOLVED_cell_v1": solved_v1, "SOLVED_cell_v1a": solved_va,
                                "qualified_v1": sum(c[k]["v1"] for c in cells_ for k in c),
                                "qualified_v1a": sum(c[k]["v1a"] for c in cells_ for k in c)})
        print(t["catalog"], t["arm"], t["family"], solved_v1, solved_va,
              out["transfer"][-1]["qualified_v1"], out["transfer"][-1]["qualified_v1a"],
              all(c[k]["repro"] for c in cells_ for k in c), flush=True)
    (HERE / "W7_DOWNSTREAM_FIXA.json").write_text(json.dumps(out, indent=1))
    for k, v in out["roles"].items():
        print(k, v["flipped_families"], {r: (x["changed"], x.get("reproduces_frozen")) for r, x in v["replicates"].items()})


if __name__ == "__main__":
    main()
