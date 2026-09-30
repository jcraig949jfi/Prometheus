"""W7 PKG-7: validate the ruler v2.1 draft.
  adv <W5|G4>   the W3 adversarial set (cases imported from w3_adversarial.py),
                v2 vs v2.1 verdicts and every flip; also the A19 panel and the
                C2 selected schemas (vs G1 and vs their held reference).
  base <W5|G4> <n>  random-schema base rate (W3's RB-1 junk generator, same
                seed) under v2 (frozen convention) and v2.1, with a Wilson CI.
Single core. Writes W7_RULER_ADV_<world>.json / W7_RULER_BASE_<world>_<n>.json.
"""
import json
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("A17_FASTEVAL", "1")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "science" / "arc3" / "w3_novelty_reuse"))
sys.path.insert(0, str(ROOT / "science" / "compounding" / "rb1"))
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT / "engine" / "accel"))
import ruler_v2 as R2          # noqa: E402
import ruler_v21 as R21        # noqa: E402
import tier3d as T3D           # noqa: E402

G1 = "(acc + {H})"


def world(w):
    if w == "W5":
        import a18
        a18.use_world("W5")


def wilson(k, n, z=1.96):
    if n == 0:
        return [0, 0]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 4), round(c + h, 4)]


def v2_full(s, sp, tsp, inst):
    v = R2.verdict_full(s, G1, sp, tsp, inst)
    return {k: v[k] for k in ("NEW_V2", "NEW_TRAJ", "NEW_FINAL", "EQUAL", "REFINES", "COMPOSES", "novel",
                              "novel_traj")}


def adv(w):
    world(w)
    import w3_adversarial as W3A
    sp = R2.span_of_schema(G1)
    tsp = R2.traj_span(R2.reexpression_bodies(G1))
    sp21, ri = R21.reference(G1)
    stored = {r["schema"]: r for r in json.loads((ROOT / ("science/arc3/w3_novelty_reuse/W3_ADVERSARIAL_%s.json" % w))
                                                  .read_text())}
    out = {"world": w, "ruler": R21.VERSION, "cases": [], "flips": []}
    for cls, s, exp_new, exp_rel, why in W3A.CASES:
        inst = T3D.instantiate(s)
        row = {"class": cls, "schema": s, "expected_NEW": exp_new, "expected_rel": exp_rel, "why": why,
               "instantiations": len(inst)}
        if inst:
            a = v2_full(s, sp, tsp, inst)
            b = R21.verdict_full(s, G1, sp21, ri, inst)
            row["v2"] = a
            row["v21"] = b
            row["v2_matches_W3_stored"] = stored.get(s, {}).get("NEW_FINAL") == a["NEW_FINAL"]
            row["v2_error"] = "OK" if a["NEW_FINAL"] == exp_new else ("FP" if a["NEW_FINAL"] else "FN")
            row["v21_error"] = "OK" if b["NEW_FINAL"] == exp_new else ("FP" if b["NEW_FINAL"] else "FN")
            diffs = []
            if a["NEW_FINAL"] != b["NEW_FINAL"]:
                diffs.append("NEW_FINAL %s->%s" % (a["NEW_FINAL"], b["NEW_FINAL"]))
            for k2, k21 in (("EQUAL", "EQUAL_ANY"), ("REFINES", "REFINES_ANY"), ("COMPOSES", "COMPOSES_ANY")):
                if bool(a[k2]) != bool(b[k21]):
                    diffs.append("%s %s->%s" % (k2, a[k2], b[k21]))
            if diffs:
                out["flips"].append({"class": cls, "schema": s, "expected_NEW": exp_new, "expected_rel": exp_rel,
                                     "changes": diffs, "v2_error": row["v2_error"], "v21_error": row["v21_error"]})
            print("%-14s %-44s v2=%-5s v21=%-5s exp=%-5s | g/t/both %d/%d/%d | EQ%d RF%d CO%d | %s" % (
                cls, s, a["NEW_FINAL"], b["NEW_FINAL"], exp_new, b["grid_novel"], b["traj_novel"],
                b["both_novel"], b["EQUAL_ANY"], b["REFINES_ANY"], b["COMPOSES_ANY"], "; ".join(diffs)), flush=True)
        out["cases"].append(row)
    tally = {}
    for r in out["cases"]:
        if "v2" not in r:
            continue
        t = tally.setdefault(r["class"], {"n": 0, "v2_err": 0, "v21_err": 0})
        t["n"] += 1
        t["v2_err"] += r["v2_error"] != "OK"
        t["v21_err"] += r["v21_error"] != "OK"
    out["tally"] = tally
    # panel + C2 selections
    panel = json.loads((ROOT / "engine/A19_C2/A18_PANEL_2026-09-28.json").read_text())["panel"]
    donors = [json.loads(x) for x in (ROOT / "engine/A19_C2/A18_DONORS_2026-09-28.jsonl").read_text().splitlines()]
    sel = {}
    for d in donors:
        if d.get("selected_schema"):
            sel.setdefault(d["selected_schema"], []).append("%s/%s" % (d["catalog"], d["arm"]))
    out["panel"], out["selections"] = {}, []
    for k, s in panel.items():
        inst = T3D.instantiate(s)
        out["panel"][k] = {"schema": s, "v2": v2_full(s, sp, tsp, inst),
                           "v21": R21.verdict_full(s, G1, sp21, ri, inst)}
    for s, where in sorted(sel.items()):
        inst = T3D.instantiate(s)
        a, b = v2_full(s, sp, tsp, inst), R21.verdict_full(s, G1, sp21, ri, inst)
        row = {"schema": s, "where": where, "v2_vs_G1": a, "v21_vs_G1": b}
        for k, ref in panel.items():
            if k != "G1":
                row["v21_rel_vs_" + k] = {x: R21.relations(s, ref)[x] for x in ("EQUAL_ANY", "REFINES_ANY",
                                                                                   "COMPOSES_ANY")}
        out["selections"].append(row)
        print("SEL %-44s %s v2 NEW=%s v21 NEW=%s CO=%s" % (s, where[0], a["NEW_FINAL"], b["NEW_FINAL"],
                                                            b["COMPOSES_ANY"]), flush=True)
    (HERE / ("W7_RULER_ADV_%s%s.json" % (w, "" if R21.NONE_TOL == 0.0 else "_tol%s" % R21.NONE_TOL))).write_text(json.dumps(out, indent=1, default=str))


def base(w, n):
    world(w)
    import w3_baserate as W3B
    sp = R2.span_of_schema(G1)
    tsp = R2.traj_span(R2.reexpression_bodies(G1))
    sp21, ri = R21.reference(G1)
    schemas = W3B.junk(n)
    rows = []
    for j, s in enumerate(schemas):
        inst = T3D.instantiate(s)
        a = v2_full(s, sp, tsp, inst)
        b = R21.verdict_full(s, G1, sp21, ri, inst)
        # ablations of v2.1 (one repair at a time on top of v2)
        rel_c = b["EQUAL_ANY"] or b["REFINES_ANY"]
        acc = b["accumulating"]
        ok = lambda c: c >= 2 and c >= 0.10 * max(1, acc)   # noqa: E731
        rows.append({"schema": s, "v2": a["NEW_FINAL"], "v21": b["NEW_FINAL"],
                     "abl_rel_only": a["NEW_V2"] and a["NEW_TRAJ"] and not rel_c,
                     "abl_traj_only": a["NEW_V2"] and b["NEW_TRAJ"] and not (a["EQUAL"] or a["REFINES"]),
                     "abl_same_witness_only": ok(b["both_novel"]) and not (a["EQUAL"] or a["REFINES"]),
                     "accumulating": acc, "COMPOSES_v21": b["COMPOSES_ANY"]})
        if j % 25 == 0:
            print(w, j, s, a["NEW_FINAL"], b["NEW_FINAL"], flush=True)
    N = len(rows)
    summ = {"world": w, "n": N}
    for k in ("v2", "v21", "abl_rel_only", "abl_traj_only", "abl_same_witness_only"):
        c = sum(r[k] for r in rows)
        summ[k] = {"NEW": c, "rate": round(c / N, 4), "wilson95": wilson(c, N)}
    summ["flips_v2_to_v21"] = [{"schema": r["schema"], "v2": r["v2"], "v21": r["v21"]} for r in rows
                               if r["v2"] != r["v21"]]
    (HERE / ("W7_RULER_BASE_%s_%d%s.json" % (w, n, "" if R21.NONE_TOL == 0.0 else "_tol%s" % R21.NONE_TOL))).write_text(json.dumps({"summary": summ, "rows": rows},
                                                                          indent=1))
    print(json.dumps({k: v for k, v in summ.items() if k != "flips_v2_to_v21"}), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "adv":
        adv(sys.argv[2])
    else:
        base(sys.argv[2], int(sys.argv[3]))
