"""THESEUS-24: re-run the preregistered H1 decision rule with a larger LLM arm.

Prereg: roles/Theseus/prereg/2026-10-08_h1_large_A/PREREG.md.

Arms D, B, C, R (and P) are the committed rows of run v0_1_2026-09-30 (genomes, fingerprints and
viability from theseus/controls/arms_<REF>.jsonl and theseus/entities|fingerprints/<REF>.jsonl).
Arm A = the 60 v0 LLM genomes (already in the arms file) + the 250 v1 LLM genomes
(theseus/controls/llm_arm_v1/GENOMES_part*.jsonl), evaluated here under the FROZEN v0_1
calibration. The H1 rule itself is theseus.synth.analysis.hard_test, unchanged.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import time
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

from . import analysis as an  # noqa: E402
from . import battery as bt  # noqa: E402
from . import rulers as ru  # noqa: E402
from . import substrate as sb  # noqa: E402

REF = "v0_1_2026-09-30"
_CAL = None


def _init(cald):
    global _CAL
    _CAL = ru.Cal(cald)


def _job(g):
    t0 = time.process_time()
    r = bt.evaluate(g, _CAL.desc_scales, _CAL.tau_rep, _CAL.sd)
    r["cpu_s"] = time.process_time() - t0
    return r


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--d-ref", default=REF, help="run tag whose DEEP/VERY_DEEP children form arm D")
    ap.add_argument("--a-v1-rows", default=None, help="reuse evaluated A v1 rows (A_V1_ROWS.jsonl) instead of re-evaluating")
    a = ap.parse_args(argv)
    out = f"theseus/runs/{a.tag}"
    os.makedirs(out, exist_ok=True)
    cald = json.load(open(f"theseus/runs/{REF}/CAL.json", encoding="utf-8"))
    cal = ru.Cal(cald)
    table = {k: [] for k in ("D", "A", "B", "C", "R", "P")}
    fps = {}
    for l in open(f"theseus/fingerprints/{a.d_ref}.jsonl", encoding="utf-8"):
        x = json.loads(l)
        fps[x["id"]] = x["fp"]
    for l in open(f"theseus/entities/{a.d_ref}.jsonl", encoding="utf-8"):
        e = json.loads(l)
        if e.get("kind") == "mechanism" and e.get("lane") in ("DEEP", "VERY_DEEP"):
            table["D"].append({"id": e["id"], "fp": fps[e["id"]], "viable": bool(e["viable"])})
    for l in open(f"theseus/controls/arms_{REF}.jsonl", encoding="utf-8"):
        r = json.loads(l)
        if r["arm"] in ("A", "B", "C", "R", "P"):
            table[r["arm"]].append({"id": r["id"], "fp": r["fp"], "viable": bool(r["viable"]), "src": "v0"})
    new, rejected = [], []
    for f in sorted(glob.glob("theseus/controls/llm_arm_v1/GENOMES_part*.jsonl")):
        for l in open(f, encoding="utf-8"):
            d = json.loads(l)
            g = d["genome"]
            for r_ in g.get("rules", []):
                r_["prov"] = "llm_v1"
            errs = sb.validate(g)
            (rejected if errs else new).append({"tid": d["tid"], "genome": g, "errors": errs})
    t0 = time.time()
    rows = []
    if a.a_v1_rows:
        for l in open(a.a_v1_rows, encoding="utf-8"):
            r = json.loads(l)
            table["A"].append({k: r[k] for k in ("id", "fp", "viable", "viability", "src")})
            rows.append(r)
    else:
        with Pool(a.workers, initializer=_init, initargs=(cald,)) as pool:
            res = pool.map(_job, [x["genome"] for x in new])
        for x, r in zip(new, res):
            row = {"id": f"A1-{x['tid']}", "fp": r["fp"], "viable": r["viable"], "viability": r["viability"], "src": "v1"}
            table["A"].append(row)
            rows.append({**row, "genome": x["genome"], "cpu_s": r["cpu_s"]})
    with open(f"{out}/A_V1_ROWS.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
    rng = np.random.default_rng(20261008)
    ht = an.hard_test(table, cal, rng)
    ht_v0A = an.hard_test({**table, "A": [r for r in table["A"] if r.get("src") == "v0"]}, cal,
                          np.random.default_rng(20261008))
    # secondary (prereg): H1 without A, comparing D against B, C, R only
    saved = an.CMP
    an.CMP = ("B", "C", "R")
    try:
        ht_noA = an.hard_test({k: v for k, v in table.items() if k != "A"}, cal, np.random.default_rng(20261008))
    finally:
        an.CMP = saved
    summary = {"ref": REF, "d_ref": a.d_ref, "a_v1_rows": a.a_v1_rows, "A_v1_valid": len(new), "A_v1_rejected": rejected, "A_v1_viable": sum(r["viable"] for r in rows),
               "wall_s": round(time.time() - t0, 1), "cpu_s": round(sum(r.get("cpu_s", 0) for r in rows), 1),
               "H1_large_A": ht, "H1_v0_A_reproduced": {"verdict": ht_v0A["verdict"], "n_equal": ht_v0A["n_equal"]},
               "H1_without_A": ht_noA}
    with open(f"{out}/SUMMARY.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, default=float)
    print(json.dumps({k: summary[k] for k in ("A_v1_valid", "A_v1_viable", "wall_s")}, indent=1))
    print("H1_large_A", ht["verdict"], ht["n_equal"], "| v0-A reproduced", ht_v0A["verdict"], "| without A", ht_noA["verdict"])


if __name__ == "__main__":
    main()
