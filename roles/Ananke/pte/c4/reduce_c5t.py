"""PTE-C5T reducer (frozen rules; PREREG_PTE_C5T s4). usage: python reduce_c5t.py RUN_DIR ASSAY.json REDUCE_C4.json OUT.json
ASSAY.json = assay_c4.py output over the competent C5T rows (may be [] when none is competent).
Assay-confirmed competent = ruler TRUE on held AND fresh_held TRUE (256 fresh worlds) AND zero_comm != TRUE AND
  at least one non-readout state register (S1 or S2) zeroed every tick loses competence (operational form of
  "the context carrier (GATE) / the mapping carrier (FLIP) is causally used"; S0 is the readout register)
Labels per task: COMPOSITION_REACHED_UNDER_REUSE (>= 4 confirmed across >= 2 cells), SPARSE_COMPOSITION (1-3, or one
cell), NO_COMPOSITION (0).
Kill: PTE_SEARCH_ARCHITECTURE_EXHAUSTED_FOR_COMPOSITION iff total confirmed <= 1 among n >= 40 completed searches AND the
C4-T arm-C MODULE_PRESENT fraction >= .5 for both tasks; if MODULE_PRESENT < .5 -> LIBRARY_NOT_TAKEN_UP (no kill);
if n < 40 -> UNDERPOWERED (no kill)."""
import glob
import json
import os
import sys

from scipy.stats import beta


def cp95(k, n):
    if n == 0:
        return [0.0, 1.0]
    return [0.0 if k == 0 else float(beta.ppf(.025, k, n - k + 1)), 1.0 if k == n else float(beta.ppf(.975, k + 1, n - k))]


def confirmed(a):
    if a["fresh_held"]["status"] != "TRUE" or a["zero_comm"]["status"] == "TRUE":
        return False
    rz = a.get("reg_zero", {})
    return any(rz.get(s) not in (None, "TRUE") for s in ("S1", "S2"))


def main(run_dir, assay_p, c4_p, out_p):
    rows = [json.loads(l) for p in glob.glob(os.path.join(run_dir, "rows_w*.jsonl")) for l in open(p) if l.strip()]
    flags = [["OVERLAP", r["job_id"]] for r in rows if r["held_train_overlap"]]
    rows = [r for r in rows if not r["held_train_overlap"]]
    assays = {a["name"]: a for a in json.load(open(assay_p))}
    c4 = json.load(open(c4_p))
    res = {"n": len(rows), "flags": flags, "tasks": {}}
    tot = 0
    for task in ("GATE", "FLIP"):
        rr = [r for r in rows if r["task"] == task]
        comp = [r for r in rr if r["success"]]
        conf = [r for r in comp if r["job_id"] in assays and confirmed(assays[r["job_id"]])]
        cells = sorted({r["cell_id"] for r in conf})
        k = len(conf); tot += k
        lab = ("COMPOSITION_REACHED_UNDER_REUSE" if k >= 4 and len(cells) >= 2 else
               "SPARSE_COMPOSITION" if k >= 1 else "NO_COMPOSITION")
        res["tasks"][task] = {"n": len(rr), "competent": len(comp), "confirmed": k, "CP95_confirmed": cp95(k, len(rr)),
                              "cells_confirmed": cells, "label": lab,
                              "unassayed_competent": [r["job_id"] for r in comp if r["job_id"] not in assays]}
    mp = {t: c4["tasks"][t]["arms"]["C"]["module_present"] for t in ("GATE", "FLIP")}
    mp_ok = all(v[1] and v[0] / v[1] >= .5 for v in mp.values())
    if not mp_ok:
        kill = "LIBRARY_NOT_TAKEN_UP"
    elif len(rows) < 40:
        kill = "UNDERPOWERED"
    elif tot <= 1:
        kill = "PTE_SEARCH_ARCHITECTURE_EXHAUSTED_FOR_COMPOSITION"
    else:
        kill = "NOT_ISSUED"
    res.update({"confirmed_total": tot, "CP95_total": cp95(tot, len(rows)), "c4_module_present": mp, "kill": kill})
    json.dump(res, open(out_p, "w"), indent=1)
    print(json.dumps({"n": res["n"], "kill": kill, "confirmed_total": tot,
                      **{t: (v["confirmed"], v["competent"], v["n"], v["label"]) for t, v in res["tasks"].items()}}))


if __name__ == "__main__":
    main(*sys.argv[1:5])
