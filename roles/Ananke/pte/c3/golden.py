"""Old-genome compatibility golden digests (72h push, repair window; operator order s2).

Fixed specimens (C2 plants of record, the C2A control plant, and recorded champions) are evaluated on fixed worlds
(namespace GOLDEN_NS, 32 worlds) through BOTH evaluation paths:
  * assays.evaluate (the GA training path: per-world accuracy, sens_act, sens_any)
  * c2a_common.eval_programs (the held/ruler path: per-trial correctness)
and the sha256 of the integer arrays is stored. Any later engine/representation change must reproduce these digests
exactly for old (version-1) genomes. Float telemetry (sens_*) is digested after rounding to 1e-6 (CPU/GPU float
differences are documented at <= 6e-8).

usage: python golden.py write OUT.json      (CPU)
       python golden.py check GOLDEN.json   (exit 1 on any mismatch)
"""
import gzip
import hashlib
import json
import os
import sys

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "c2a"))
import numpy as np  # noqa: E402

import c2a_common as C  # noqa: E402
from prometheus.ananke import assays, envs  # noqa: E402

GOLDEN_NS = 0x60DE7001
PTE = os.path.join(HERE, "..")


def specimens():
    plan = json.load(open(os.path.join(PTE, "c2a", "PLAN_C2A.json")))
    cells = {c["cell_id"]: c for c in plan["cells"]}
    out = []
    for c in plan["cells"]:
        out.append((f"plant:{c['cell_id']}", c["physics"], c["env"], c["plant_genome"]))
    rows = [json.loads(l) for l in gzip.open(os.path.join(PTE, "c2a", "production", "rows_C2A.jsonl.gz"), "rt")]
    pick = [r for r in rows if r["success"] and r["arm"] == "BASE"][:1] + \
           [r for r in rows if r["arm"] == "PSEED" and r["cell_id"].startswith("FLIP")][:1] + \
           [r for r in rows if not r["success"] and r["arm"] == "M32"][:1]
    for r in pick:
        c = cells[r["cell_id"]]
        out.append((f"c2a:{r['job_id']}", c["physics"], c["env"], r["champion"]))
    rows = [json.loads(l) for l in gzip.open(os.path.join(PTE, "c2c", "production", "rows_C2C.jsonl.gz"), "rt")]
    pick = [r for r in rows if r.get("campaign") == "C2C" and r["success"]][:1] + \
           [r for r in rows if r.get("campaign") == "C2BX" and r["success_by"]["576"]][:1]
    for r in pick:
        c = cells[r["cell_id"]]
        g = r["champion"] if "champion" in r else r["checkpoint_champions"]["576"]
        out.append((f"c2c:{r['job_id']}", c["physics"], c["env"], g))
    c1 = [json.loads(l) for l in gzip.open(os.path.join(PTE, "c1_rows", "cells.jsonl.gz"), "rt")]
    r = next(x for x in c1 if x["cell_id"] == "6f82f9c7d51bcef1")
    out.append(("c1:6f82f9c7d51bcef1", r["physics"], r["env"], r["result"]["champion"]))
    return out


def digest(phd, envd, genome):
    ph = C.Physics.from_dict(phd).validate(); env = envs.EnvSpec(**envd)
    g = np.asarray(genome, dtype=np.int64)
    seeds = assays.world_seeds(C.H_int(GOLDEN_NS, int(ph.digest()[:8], 16)), 32)
    r = assays.evaluate(ph, g[None], env, seeds, device="cpu")
    pt, _ = C.eval_programs(ph, env, seeds, [g], device="cpu")
    h = hashlib.sha256()
    h.update(np.ascontiguousarray(r.acc).tobytes())
    h.update(np.round(r.sens_act, 6).tobytes()); h.update(np.round(r.sens_any, 6).tobytes())
    h.update(np.ascontiguousarray(pt).tobytes())
    return h.hexdigest(), float(r.acc.mean())


def main():
    mode, path = sys.argv[1], sys.argv[2]
    if mode == "write":
        res = {}
        for name, phd, envd, g in specimens():
            d, a = digest(phd, envd, g)
            res[name] = {"sha256": d, "acc": a, "physics": phd, "env": envd, "genome": g}
            print(name, d[:16], round(a, 4), flush=True)
        json.dump(res, open(path, "w"), indent=1)
    else:
        gold = json.load(open(path))
        bad = 0
        for name, v in gold.items():
            d, a = digest(v["physics"], v["env"], v["genome"])
            ok = d == v["sha256"]
            bad += not ok
            print(name, "OK" if ok else f"MISMATCH {d[:16]} vs {v['sha256'][:16]}", flush=True)
        print("golden mismatches", bad)
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
