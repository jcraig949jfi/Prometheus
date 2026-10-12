"""THESEUS-39: build the injection sets for SYN re-injection.

Prereg: roles/Theseus/prereg/2026-10-09_syn_reinject/PREREG.md.

  S  the admitted SYN concepts (theseus/archive/syn_concepts_v0_2t0_2026-10-08.jsonl)
  M  matched control: for each SYN concept, in archive order, one viable DEEP/VERY_DEEP
     mechanism of the same source run that is NOT a solver of the composition-necessary task
     (J < .6, task_comp.J), not a SYN source, same generation (widened by 1 until found) and
     rule count within 1 of the SYN genome; candidates visited in a seeded order (20261009).
Output rows {"id", "genome", "generation", "meta"} -> theseus/archive/inject_<S|M>_<run>.jsonl,
read by run_v0 --inject.
"""

import argparse
import json

import numpy as np

from . import task_comp as tcm


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="v0_2t0_2026-10-08")
    a = ap.parse_args(argv)
    syn = [json.loads(l) for l in open(f"theseus/archive/syn_concepts_{a.run}.jsonl", encoding="utf-8")]
    syn = [s for s in syn if s["admitted"]]
    src = {s["source_entity"] for s in syn}
    pool = []
    for l in open(f"theseus/entities/{a.run}.jsonl", encoding="utf-8"):
        e = json.loads(l)
        if (e.get("viable") and e.get("kind") == "mechanism" and e.get("lane") in ("DEEP", "VERY_DEEP")
                and e["id"] not in src):
            pool.append(e)
    order = np.random.default_rng(20261009).permutation(len(pool))
    pool = [pool[i] for i in order]
    jcache, used = {}, set()
    S, M = [], []
    for s in syn:
        g = s["executable_definition"]
        gen, nr = s["lineage"]["generation"], len(g["rules"])
        S.append({"id": f"INJ-{s['syn_id']}", "genome": g, "generation": gen,
                  "meta": {"syn_id": s["syn_id"], "source_entity": s["source_entity"], "source_run": a.run}})
        pick = None
        for w in range(0, 21):
            for e in pool:
                if e["id"] in used or abs(e["generation"] - gen) > w:
                    continue
                if abs(len(e["executableRepresentation"]["rules"]) - nr) > 1:
                    continue
                if e["id"] not in jcache:
                    jcache[e["id"]] = tcm.J(e["executableRepresentation"])
                if jcache[e["id"]] < tcm.SOLVER:
                    pick = e
                    break
            if pick:
                break
        if pick is None:
            raise SystemExit(f"no matched control for {s['syn_id']}")
        used.add(pick["id"])
        M.append({"id": f"INJ-M-{pick['id']}", "genome": pick["executableRepresentation"],
                  "generation": pick["generation"],
                  "meta": {"matched_to": s["syn_id"], "source_entity": pick["id"], "source_run": a.run,
                           "J": jcache[pick["id"]]}})
    for name, rows in (("S", S), ("M", M)):
        with open(f"theseus/archive/inject_{name}_{a.run}.jsonl", "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, separators=(",", ":")) + "\n")
    print(json.dumps({"S": len(S), "M": len(M), "J_evaluated": len(jcache),
                      "M_gen_diff": [m["generation"] - s["generation"] for s, m in zip(S, M)],
                      "M_J": [round(m["meta"]["J"], 3) for m in M]}))


if __name__ == "__main__":
    main()
