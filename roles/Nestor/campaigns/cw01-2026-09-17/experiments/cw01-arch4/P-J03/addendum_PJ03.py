"""P-J03 ADDENDUM (post hoc, labelled): (a) the preregistered removal retest used the xor-15 sets, which the
lineage never crossed; the scaffold's own transform is xor 1, so persistence / decay is re-measured here on
the xor-1 held-out sets for the populations after the xor-15 stage (S2) and after removal (R). (b) the
one-edit structured census (P-J02's instrument) of the XOR-1 witness itself toward xor 3, xor 5, xor 15 and
add 1: which transforms are ONE edit from the scaffold, and whether they need a literal constant.
Computational scope: integer programs on a bounded VM."""
from __future__ import annotations

import gzip
import json
import pathlib
import sys
import time
from collections import Counter

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "P-J02"))
import common as CM            # noqa: E402
import ctxevo as CE            # noqa: E402
from run_PJ02 import insert, structured_census, reached_out, fit   # noqa: E402
from run_PJ03 import witness_genome                                 # noqa: E402
A, L = CM.A, CM.L


def main():
    t0 = time.time()
    with gzip.open(HERE / "populations.json.gz", "rt", encoding="utf-8") as fh:
        pops = json.load(fh)
    persist = {}
    for p in pops:
        if p["chain"] != "scaffolded":
            continue
        s1 = CE.held_sets("A", p["seed"], xor=1)
        for k in ("S2", "R"):
            h = sorted([CE.held_reward(x["m"], s1) for x in p["pops"][k]], reverse=True)
            persist["%s|s%d" % (k, p["seed"])] = {"top4_xor1": float(np.mean(h[:4])), "pop_mean_xor1": float(np.mean(h)), "share_ge_.9": float(np.mean([v >= 0.9 for v in h]))}
    wm, w = witness_genome()
    sets = {"xor1": CE.held_sets("A", 1, xor=1), "xor3": CE.held_sets("A", 1, xor=3), "xor5": CE.held_sets("A", 1, xor=5), "xor15": CE.held_sets("A", 1, xor=15), "add1": CE.held_sets("A", 1, transform="add:1")}
    f0 = {k: fit(wm, s[:2]) for k, s in sets.items()}
    f0_4 = {k: fit(wm, s) for k, s in sets.items()}
    pos, a, ch = reached_out(wm, sets["xor1"][0])
    census = structured_census(wm, a, sets, f0, CE.THRESH["A"])
    out_c = {}
    for k in sets:
        hits = [r for r in census if r[k + "_class"] == "hit"]
        conf = [r for r in hits if fit(insert(wm, r["pos"], [[{"XOR": 12, "ADD": 7, "SUB": 8, "OR": 11, "AND": 10, "MUL": 9, "MOV": 4, "IN": 21}[r["op"]], a, a, r["j"]] if r["op"] != "IN" else [21, a, r["j"], 0]]) if r["mode"] == "insert" else
                                     __import__("run_PJ02").replace(wm, r["pos"], [{"XOR": 12, "ADD": 7, "SUB": 8, "OR": 11, "AND": 10, "MUL": 9, "MOV": 4, "IN": 21}[r["op"]], a, a, r["j"]]), sets[k]) >= CE.THRESH["A"]]
        out_c[k] = {"f0_witness_4set": f0_4[k], "hits_confirmed": len(conf), "hit_ops": dict(Counter(r["op"] for r in conf)), "hit_modes": dict(Counter(r["mode"] for r in conf)), "classes": dict(Counter(r[k + "_class"] for r in census)), "examples": conf[:3]}
    out = {"perturbation_id": "P-J03", "addendum": "post hoc, labelled", "witness": {"seed": w["seed"], "rank": w["rank"], "n_instr": w["xor1"]["n_instr"], "out_index": pos, "out_reg": a},
           "xor1_persistence": persist, "one_edit_from_witness": out_c, "reading": "transforms whose regime-1 answer is a register-to-register operation on the read regime word (add 1: ADD out,out,t) can be one edit from the scaffold; transforms needing a literal constant (xor 3 / 5 / 15) need an LDC whose 32-bit word must equal the constant, which the grammar's uniform word draws cannot supply",
           "elapsed_s": round(time.time() - t0, 1)}
    (HERE / "ADDENDUM.json").write_text(json.dumps(out, indent=1, ensure_ascii=True, default=CM.js), encoding="utf-8")
    L.append_evidence("T-X17", "P-J03", "ADDENDUM (post hoc): xor-1 persistence of the scaffolded populations after the xor-15 stage and after removal %s; one-edit census of the XOR-1 witness toward other transforms: %s" % (
        {k: {kk: round(vv, 3) for kk, vv in v.items()} for k, v in persist.items()}, {k: (v["hits_confirmed"], v["hit_ops"], round(v["f0_witness_4set"], 3)) for k, v in out_c.items()}), True, detail=out)
    print("DONE", json.dumps({"persist": persist, "census": {k: (v["hits_confirmed"], v["hit_ops"], round(v["f0_witness_4set"], 3)) for k, v in out_c.items()}}, default=CM.js))


if __name__ == "__main__":
    main()
