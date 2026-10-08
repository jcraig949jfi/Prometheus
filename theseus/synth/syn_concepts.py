"""THESEUS-13: compress repeatedly useful candidates into reusable SYNTHETIC CONCEPTS.

Charter ("RECURSIVE SYNTHETIC CONCEPT FORMATION"): a candidate that repeatedly produces useful
behaviour under several assays is compressed into SYN-###### with: executable definition,
behavioural fingerprint, lineage, lens dependencies, world dependencies, transfer results,
known failure modes. No human-readable name is required or given.

Selection (mechanical): solvers of the composition-necessary task in a task0-selected run
(theseus/runs/comp_task_2026-10-08/: J >= .9 on the task AND at least one essential rule that
is a collision-generated law), up to --max per run. Assays recorded per concept:
  J_ch0_k8_seed0   (the selecting task; from the 36 rows)
  J_ch0_k8_seed1   (replication on a fresh task seed)
  J_ch0_V8_k8      (transfer: larger alphabet)
  J_all_V8_k8      (transfer: full-state readout, the 31b setting)
  essential rules + their provenance (failure modes: which single removal breaks it)
A concept is admitted to the archive only if J_ch0_k8_seed1 >= .9 (replicates). Admitted
concepts are eligible tensor matter; re-injection into an ecology is a separate, later step.
"""

import argparse
import hashlib
import json
import os
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

from . import sel_eval as se  # noqa: E402
from . import substrate as sb  # noqa: E402
from . import task_system as ts  # noqa: E402


def assays(g):
    return {"J_ch0_k8_seed1": ts.task_J(g, V=4, k=8, seed=1, readout="ch0")["J"],
            "J_ch0_V8_k8": ts.task_J(g, V=8, k=8, seed=0, readout="ch0")["J"],
            "J_all_V8_k8": ts.task_J(g, V=8, k=8, seed=0)["J"]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="v0_2t0_2026-10-08")
    ap.add_argument("--evaldir", default="theseus/runs/comp_task_2026-10-08")
    ap.add_argument("--max", type=int, default=20)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    genomes = dict(se.sample(a.run))
    J = {json.loads(l)["id"]: json.loads(l)["v"] for l in open(f"{a.evaldir}/J_{a.run}.jsonl", encoding="utf-8")}
    KO = {json.loads(l)["id"]: json.loads(l)["v"] for l in open(f"{a.evaldir}/KO_{a.run}.jsonl", encoding="utf-8")}
    ents = {}
    for l in open(f"theseus/entities/{a.run}.jsonl", encoding="utf-8"):
        e = json.loads(l)
        ents[e["id"]] = e
    cand = []
    for i, ko in KO.items():
        g = genomes[i]
        law_ess = [x for x in ko["essential"] if "law:" in str(g["rules"][x].get("prov", ""))]
        if J[i] >= 0.9 and law_ess:
            cand.append(i)
    cand = sorted(cand, key=lambda i: (-J[i], i))[: a.max]
    with Pool(a.workers) as pool:
        res = pool.map(assays, [genomes[i] for i in cand])
    out, admitted = [], 0
    for i, r in zip(cand, res):
        g = genomes[i]
        e = ents.get(i, {})
        ko = KO[i]
        syn = "SYN-" + str(int(hashlib.sha256(sb.canonical(g).encode()).hexdigest(), 16) % 10**6).zfill(6)
        rec = {
            "syn_id": syn, "source_entity": i, "source_run": a.run,
            "admitted": r["J_ch0_k8_seed1"] >= 0.9,
            "executable_definition": g,
            "behavioral_fingerprint_ref": f"theseus/fingerprints/{a.run}.jsonl#{i}",
            "lineage": {"parentIds": e.get("parentIds"), "generation": e.get("generation"),
                        "genealogy": e.get("genealogy"), "n_ancestors": len(e.get("ancestry", []) or [])},
            "lens_dependencies": [str(x.get("prov", ""))[2:] for x in g["rules"] if x["op"] == "lensmap"],
            "world_dependencies": {"task": "prometheus.cosmos.c3.task cue recall via theseus.synth.task_system",
                                   "input": "channel 0 transient sensor (overwrite)", "N": ts.N_CELLS},
            "assays": {"J_ch0_k8_seed0": J[i], **r},
            "known_failure_modes": [{"remove_rule": x, "op": g["rules"][x]["op"],
                                     "prov": g["rules"][x].get("prov"), "J_drop": ko["drops"][x]}
                                    for x in ko["essential"]],
            "precise_language": {
                "no_direct_raw_human_parent": bool(e.get("genealogy", {}).get("has_direct_human_parent") is False),
                "min_ancestry_depth_to_g0": (e.get("genealogy") or {}).get("min_depth_to_g0"),
                "essential_step_is_collision_generated_law": True,
                "interpretation": "not attempted"},
        }
        admitted += rec["admitted"]
        out.append(rec)
    os.makedirs("theseus/archive", exist_ok=True)
    path = f"theseus/archive/syn_concepts_{a.run}.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for rec in out:
            f.write(json.dumps(rec, separators=(",", ":")) + "\n")
    print(json.dumps({"candidates": len(cand), "admitted": admitted, "path": path,
                      "assays": [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in x["assays"].items()} | {"syn": x["syn_id"]} for x in out]}, indent=1))


if __name__ == "__main__":
    main()
