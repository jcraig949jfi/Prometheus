"""RB-5 census builder: EC_ANALYSIS.json + EC_SEARCH_*.json + OEIS_SEARCH.jsonl ->
RB5_CENSUS.json (forensic, not a disposition).

CANONICAL tallies use only the FIRST verified witness class in enumeration order
(no choice among extensions); the default tallies are LENIENT (any class).
VIABLE (the supply criterion of the RB-5 brief, step 3), per family, lenient
(best verified witness class): expressible AND T4-admissible AND Q2-qualified
AND fclass != ADDITIVE AND not extensionally G1 (K7 test). A world is a viable
compounding supply iff its VIABLE families include >= 2 families sharing a
single-hole schema (tier3d.derive_schemas over their witness bodies, distinct
families as distinct classes) that is not G1's own schema (acc + {H})."""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rb5_common as C      # noqa: E402
import rb5_ec as EC         # noqa: E402

G1_FORMS = {"(acc + {H})", "({H} + acc)"}


def viable(s):
    return (s["expressible"] and s["t4_admissible"] and s["q2_qualified"]
            and s["best_fclass"] != "ADDITIVE" and not s["best_g1_equivalent"])


def tally(summaries):
    n = len(summaries)
    ex = [s for s in summaries if s["expressible"]]
    adm = [s for s in ex if s["t4_admissible"]]
    q = [s for s in adm if s["q2_qualified"]]
    return {
        "n": n, "expressible": len(ex),
        "expressible_frac": round(len(ex) / n, 4) if n else None,
        "t4_admissible": len(adm), "q2_qualified": len(q),
        "viable": sum(1 for s in summaries if viable(s)),
        "fclass_expressible_best": dict(Counter(s["best_fclass"] for s in ex)),
        "fclass_admissible_qualified_best": dict(Counter(s["best_fclass"] for s in q)),
        "g1_equivalent_best": sum(1 for s in ex if s["best_g1_equivalent"]),
        "perm_invariant_best": sum(1 for s in ex if s["best_perm_invariant"]),
        "t4_rejection_reasons_best": dict(Counter(r for s in ex if not s["t4_admissible"]
                                                  for r in (s["best_t4_reasons"] or []))),
    }


def schemas(families):
    """families: {name: [witness body, ...]} -> shared single-hole schemas."""
    T3D = C.a17.T3D
    names = sorted(families)
    ds = T3D.derive_schemas([families[n] for n in names])
    out = []
    for d in ds:
        fams = sorted({names[ci] for ci, cj, a, b in d["witness_pairs"]}
                      | {names[cj] for ci, cj, a, b in d["witness_pairs"]})
        out.append({"schema": d["schema"], "n_pairs": d["n_pairs"],
                    "example_families": fams[:8], "is_G1": d["schema"] in G1_FORMS})
    return sorted(out, key=lambda x: -x["n_pairs"])


def main():
    EMPTY = C.family_summary([])
    # ---------------- EC
    ea = json.loads((HERE / "EC_ANALYSIS.json").read_text(encoding="utf-8"))["families"]
    s4 = json.loads((HERE / "EC_SEARCH_G4.json").read_text(encoding="utf-8"))
    s5 = json.loads((HERE / "EC_SEARCH_G5.json").read_text(encoding="utf-8"))
    ec = {}
    ec_rows = {}
    ec_viable = {}
    for mp in EC.MAPPINGS:
        ec[mp] = {}
        for tier in ("ALL", "CONST", "LINEAR", "QUAD", "QUAD_COMPLEX", "QUAD_COEF_GT1"):
            fams = [fm for fm in EC.families() if fm[0] == mp
                    and (tier == "ALL" or tier in EC.tiers(*fm[1:]))]
            ec[mp][tier] = {}
            for gr in ("g4", "g5"):
                sums = [ea.get(EC.fid(fm), {}).get(gr, {}).get("summary", EMPTY) for fm in fams]
                ec[mp][tier][gr] = tally(sums)
                strict = [C.family_summary(ea.get(EC.fid(fm), {}).get(gr, {}).get("classes", [])[:1])
                          for fm in fams]
                ec[mp][tier][gr + "_canonical"] = tally(strict)
        for fm in EC.families():
            if fm[0] != mp:
                continue
            f = EC.fid(fm)
            if f in ea:
                ec_rows[f] = {gr: ea[f][gr]["summary"] for gr in ea[f]}
                ec_rows[f]["tiers"] = EC.tiers(*fm[1:])
                for gr in ea[f]:
                    s = ea[f][gr]["summary"]
                    if viable(s):
                        cls = [c for c in ea[f][gr]["classes"] if c["t4_admissible"]
                               and c["Q2_size"] is not None and c["prog"][0] == "fold"]
                        ec_viable.setdefault(gr, {})[f.replace("|", "_")] = [c["prog"][2] for c in cls]
    # ---------------- OEIS
    rows = [json.loads(l) for l in (HERE / "OEIS_SEARCH.jsonl").read_text(encoding="utf-8").splitlines()
            if l.strip()]
    oe = {}
    oe_viable = {}
    for st in ("ALL", "CORE", "CLASSIC", "LINREC", "NONLIN"):
        rs = [r for r in rows if st == "ALL" or st in r["strata"]]
        oe[st] = {}
        for gr in ("g4", "g5"):
            sums = []
            if gr == "g5":      # G5 tallies only over rows where G5 was searched (or G4 qualified)
                rs = [r for r in rs if r.get("g5_searched", True) or r["g4"]["summary"]["q2_qualified"]]
            for r in rs:
                if gr == "g4":
                    sums.append(r["g4"]["summary"])
                else:   # G5 = G4 when G4 already qualified, else the G5 extras run (or G4)
                    s5r = r.get("g5", {}).get("summary")
                    sums.append(r["g4"]["summary"] if (s5r is None or not s5r["expressible"]) else s5r)
            oe[st][gr] = tally(sums)
            strict = []
            for r in rs:
                cl = r["g4"]["classes"][:1]
                if gr == "g5" and not cl and r.get("g5"):
                    cl = r["g5"]["classes"][:1]
                strict.append(C.family_summary(cl))
            oe[st][gr + "_canonical"] = tally(strict)
    for r in rows:
        for gr in ("g4", "g5"):
            if gr in r and viable(r[gr]["summary"]):
                cls = [c for c in r[gr]["classes"] if c["t4_admissible"]
                       and c["Q2_size"] is not None and c["prog"][0] == "fold"]
                oe_viable.setdefault(gr, {})[r["A"]] = [c["prog"][2] for c in cls]
    oe_viable_all = dict(oe_viable.get("g4", {}))
    oe_viable_all.update(oe_viable.get("g5", {}))
    ec_viable_all = dict(ec_viable.get("g4", {}))
    for k, v in ec_viable.get("g5", {}).items():
        ec_viable_all.setdefault(k, v)
    census = {
        "block": "RB-5", "forensic": "forensic, not a disposition", "label": C.LABEL,
        "grammar": {"G4_inits": len(C.G.INIT_SPACE), "G4_bodies": len(C.G.BODY_SPACE),
                    "G4_finals": len(C.G.FINAL_SPACE),
                    "G5_bodies": len(C.a17.g5_bodies()), "G5_inits_searched": list(C.G.H1_SPACE)},
        "search_seconds": {"ec_g4": s4["search_seconds"], "ec_g5_extras": s5["search_seconds"]},
        "ec": {"mappings": EC.__doc__, "tallies": ec, "expressible_families": ec_rows,
               "viable_families": ec_viable_all,
               "viable_schemas": schemas(ec_viable_all) if len(ec_viable_all) > 1 else []},
        "oeis": {"mapping": "list = a(0..k-1), query m = k, answer a(k); dev k=4..9, holdout k=10..19",
                 "selection": json.loads((HERE / "cache" / "oeis_selection_rb5.json").read_text(
                     encoding="utf-8"))["counts"],
                 "n_searched": len(rows), "tallies": oe,
                 "rows": [{"A": r["A"], "strata": r["strata"], "recurrence": r["recurrence"],
                           "g4": r["g4"]["summary"], "g5": r.get("g5", {}).get("summary"),
                           "g5_searched": r.get("g5_searched", True),
                           "seconds": r["seconds"]} for r in rows],
                 "viable_families": oe_viable_all,
                 "viable_schemas": schemas(oe_viable_all) if len(oe_viable_all) > 1 else []},
    }
    # canonical (first verified class only) viable families and their schemas
    can = {}
    for f, v in ea.items():
        for gr in ("g4", "g5"):
            cl = v.get(gr, {}).get("classes", [])[:1]
            if cl and viable(C.family_summary(cl)):
                can.setdefault("ec", {}).setdefault(f.replace("|", "_"), [cl[0]["prog"][2]])
    for r in rows:
        cl = r["g4"]["classes"][:1] or (r.get("g5") or {}).get("classes", [])[:1]
        if cl and viable(C.family_summary(cl)):
            can.setdefault("oeis", {})[r["A"]] = [cl[0]["prog"][2]]
    for w in ("ec", "oeis"):
        fams = can.get(w, {})
        census[w]["viable_families_canonical"] = fams
        census[w]["viable_schemas_canonical"] = schemas(fams) if len(fams) > 1 else []
    q2c = HERE / "Q2_SPOTCHECK.json"
    if q2c.exists():
        census["q2_spotcheck"] = json.loads(q2c.read_text(encoding="utf-8"))
    (HERE / "RB5_CENSUS.json").write_text(json.dumps(census, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"ec": {mp: {t: {g: (v[g]["expressible"], v[g]["t4_admissible"], v[g]["q2_qualified"], v[g]["viable"])
                                    for g in v} for t, v in ec[mp].items()} for mp in ec},
                      "oeis": {st: {g: (v[g]["n"], v[g]["expressible"], v[g]["t4_admissible"],
                                        v[g]["q2_qualified"], v[g]["viable"]) for g in v}
                               for st, v in oe.items()}}, indent=1))


if __name__ == "__main__":
    main()
