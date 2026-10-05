"""DEV-11 diagnostic: is endogenous derivation non-monotone in observation (T10 attack question 1)?

For seeds 1, 6, 12 and 13, re-run donor_g('g10') at O4 (T09 roles) and O10 (T10 roles). Record the derived schemas,
the composed candidates, and the g10 selection table (G, L, eligible). Every other input matches the T09/T10 rows, and
the reproduction of their selections is checked. This is a diagnostic over existing frozen inputs; it reads no new
transfer outcome. Output: beta01/runs/T10_OBS/D11_DERIVATION_DIAG.json.
"""
import os
os.environ.setdefault("V2B_T51_DIR", "T04_T51")
import json  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402

import r7e as R  # noqa: E402

SEEDS = [1, 6, 12, 13]
OUT = R.RUNS / "T10_OBS" / "D11_DERIVATION_DIAG.json"


def _job(a):
    R.T.init_worker()
    import a17
    import a18_c1
    import gtc
    a17.R_VAL = a18_c1.R_VAL_C1
    tag, d, s, fams, panel = a
    rec = []
    orig = gtc.T3D.derive_schemas

    def spy(x):
        out = orig(x)
        rec.append(list(out))
        return out
    gtc.T3D.derive_schemas = spy
    tabs = []
    osel = gtc._select_subset

    def spy_sel(c, st, cells):
        ch, tb, vc = osel(c, st, cells)
        tabs.append((ch, tb, {n: [e.get("schema") for e in ents[:1]] for n, ents in c.items()}))
        return ch, tb, vc
    gtc._select_subset = spy_sel
    fl = [dict(f, qualified_dev_size=f["Q2_size"]) for f in fams]
    specs = {f["name"]: (f["body"], f["final"], f["init"]) for f in fl}
    r = gtc.donor_g("g10", ("LIN%d" % s, "P", s, fl, specs, panel, True))
    gtc.T3D.derive_schemas = orig
    gtc._select_subset = osel
    ch, tb, heads = tabs[0]
    derived = [str(x.get("schema") if isinstance(x, dict) else x) for x in (rec[0] if rec else [])]
    return {"seed": s, "arm": tag, "derived": derived, "n_observed": r["n_observed"], "classes": r["classes"],
            "observed_families": r["observed_families"], "selected": r["selected"],
            "selected_schema": r["selected_schema"],
            "chosen": ch, "table": {k: {"G": v["G"], "L": v["L"], "eligible": v["eligible"], "size": v["size"],
                                        "head": heads.get(k)} for k, v in tb.items()}}


def main():
    r09 = {x["seed"]: x for x in json.loads((R.RUNS / "T09_SUBSET" / "T09_ROLES.json").read_text())}
    r10 = {x["seed"]: x for x in json.loads((R.RUNS / "T10_OBS" / "T10_ROLES.json").read_text())}
    panel = {s: p for _d, s, _f, p in R.seeds()}
    jobs = [(t, src[s]["src"], s, src[s]["families"], panel[s]) for s in SEEDS for t, src in (("O4", r09), ("O10", r10))]
    with ProcessPoolExecutor(max_workers=4, initializer=R.T.init_worker) as ex:
        rows = list(ex.map(_job, jobs))
    d09 = {x["seed"]: x for x in R.rdl(R.RUNS / "T09_SUBSET" / "T09_DONORS.jsonl") if x["genome"] == "g10"}
    d10 = {x["seed"]: x for x in R.rdl(R.RUNS / "T10_OBS" / "T10_DONORS.jsonl") if x["genome"] == "g10"}
    for r in rows:
        ref = (d09 if r["arm"] == "O4" else d10)[r["seed"]]
        r["reproduces"] = r["selected_schema"] == ref["selected_schema"] and r["n_observed"] == ref["n_observed"]
    out = []
    for s in SEEDS:
        a = next(r for r in rows if r["seed"] == s and r["arm"] == "O4")
        b = next(r for r in rows if r["seed"] == s and r["arm"] == "O10")
        out.append({"seed": s, "O4": a, "O10": b,
                    "lost": sorted(set(a["derived"]) - set(b["derived"])),
                    "gained": sorted(set(b["derived"]) - set(a["derived"])),
                    "O4_selected_still_derived_at_O10": (a["selected_schema"] in b["derived"])
                    if a["selected_schema"] else None})
    OUT.write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    for o in out:
        print(o["seed"], "chosen O4/O10", o["O4"]["chosen"], o["O10"]["chosen"], "lost", o["lost"], "gained", o["gained"], "O4sel_kept", o["O4_selected_still_derived_at_O10"],
              "repro", o["O4"]["reproduces"], o["O10"]["reproduces"])
        for arm in ("O4", "O10"):
            print("  ", arm, {k: (round(v["G"]), round(v["L"]), v["eligible"], v["head"]) for k, v in o[arm]["table"].items()})


if __name__ == "__main__":
    main()
    sys.exit(0)
