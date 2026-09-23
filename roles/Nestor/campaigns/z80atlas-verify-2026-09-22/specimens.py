"""H2 specimen panel: a deterministic, committed selection from the FROZEN predecessor.

WHY THIS IS A SEPARATE, COMMITTED STEP. The predecessor has 1,031 admissible
replication-event runs spread over 35 (reproduction, structure, representation) strata.
"Three arms per cell" over that is not a bounded experiment, and choosing specimens after
seeing Cycle-9 results would be selection on the outcome. So the panel is chosen by a
rule that runs before any Cycle-9 result exists, written to a manifest, and hashed.

THE RULE, in order:
  1. maximize coverage over (reproduction, structure, representation) strata, taking one
     specimen per stratum in round-robin passes so no stratum contributes a second
     specimen until every stratum has contributed one;
  2. within a stratum rank by replication evidence: replication_events descending, then
     first_replicator.fidelity descending;
  3. break remaining ties by ascending sha256(run_id).

This file only READS the predecessor observatory. It never writes there.
"""
from __future__ import annotations

import collections
import hashlib
import json
import pathlib

PRED = pathlib.Path(__file__).resolve().parent.parent / "z80atlas-2026-09-19" / "observatory"
PANEL_SIZE = 16


def _admissible():
    adj = json.loads((PRED / "ADJUDICATION.json").read_text(encoding="ascii"))
    return [v for v in adj["verdicts"]
            if v["flag"] == "SPONTANEOUS_REPLICATOR_FROM_RANDOM_BYTES"
            and v["verdict"] == "ADMISSIBLE"]


def _evidence(v):
    p = PRED / "runs" / v["family"] / v["run_id"] / "RESULT.json"
    s = json.loads(p.read_text(encoding="ascii"))["summary"]
    fr = s.get("first_replicator") or {}
    return {"replication_events": s.get("replication_events", 0),
            "fidelity": fr.get("fidelity", 0.0),
            "genome": fr.get("genome"),
            "epoch": fr.get("epoch"),
            "births_similar_no_write": s.get("births_similar_no_write", 0)}


def select(panel_size=PANEL_SIZE):
    import grammar as G
    cands = []
    skipped = {"no_genome": 0, "invalid_under_cycle9_grammar": 0}
    for v in _admissible():
        c = v.get("cell") or {}
        ev = _evidence(v)
        if not ev["genome"]:
            skipped["no_genome"] += 1
            continue          # arm B implants the actual genome; without it there is no arm B
        # A specimen whose cell cannot be instantiated under the Cycle-9 grammar cannot
        # be an arm of a Cycle-9 experiment. P-10 removes ENV_MIG, and 177 of the 1,031
        # admissible predecessor cells use it, so they are dropped here rather than
        # silently repaired into some neighbouring cell - which would make the specimen
        # a different experiment from the one it was selected for.
        if not G.is_valid(c):
            skipped["invalid_under_cycle9_grammar"] += 1
            continue
        cands.append({
            "run_id": v["run_id"], "family": v["family"], "cell": c,
            "stratum": (c.get("reproduction"), c.get("structure"), c.get("representation")),
            "replication_events": ev["replication_events"], "fidelity": ev["fidelity"],
            "genome": ev["genome"], "first_replicator_epoch": ev["epoch"],
            "tie_hash": hashlib.sha256(v["run_id"].encode()).hexdigest(),
        })

    by_stratum = collections.defaultdict(list)
    for c in cands:
        by_stratum[c["stratum"]].append(c)
    for k in by_stratum:
        by_stratum[k].sort(key=lambda c: (-c["replication_events"], -c["fidelity"], c["tie_hash"]))

    # Strata visited in a deterministic order; round-robin so coverage is maximized
    # before any stratum is allowed a second specimen.
    order = sorted(by_stratum, key=lambda s: (-len(by_stratum[s]), tuple(str(x) for x in s)))
    picked, depth = [], 0
    while len(picked) < panel_size:
        added = False
        for s in order:
            if depth < len(by_stratum[s]):
                picked.append(by_stratum[s][depth])
                added = True
                if len(picked) == panel_size:
                    break
        if not added:
            break
        depth += 1
    return picked, skipped


def manifest(panel_size=PANEL_SIZE):
    picked, skipped = select(panel_size)
    body = [{"run_id": p["run_id"], "family": p["family"], "stratum": list(p["stratum"]),
             "replication_events": p["replication_events"], "fidelity": p["fidelity"],
             "genome_len": len(p["genome"]) // 2, "cell": p["cell"]} for p in picked]
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, ensure_ascii=True).encode()).hexdigest()
    repro = sorted({s["stratum"][0] for s in body})
    return {"rule": "coverage round-robin over (reproduction,structure,representation); "
                    "within stratum replication_events desc, fidelity desc; "
                    "ties by ascending sha256(run_id)",
            "source": "z80atlas-2026-09-19 ADJUDICATION.json, ADMISSIBLE spontaneity only",
            "skipped": skipped,
            # RECORDED, NOT REPAIRED. Every one of the predecessor's 1,031 admissible
            # spontaneous replicators is PAIR_EXECUTION. The panel therefore cannot be
            # diverse in reproduction physics, because the result it samples from is not.
            # H2 is consequently a test of pair-tape propagation specifically, and the
            # packet says so rather than letting "mechanism-diverse" imply otherwise.
            "reproduction_levels_present": repro,
            "reproduction_diversity_available": len(repro),
            "panel_size": len(body), "specimens": body, "panel_hash": digest}


if __name__ == "__main__":
    m = manifest()
    print(json.dumps({"panel_size": m["panel_size"], "panel_hash": m["panel_hash"]}, indent=1))
    seen = collections.Counter(tuple(s["stratum"]) for s in m["specimens"])
    print("distinct strata covered:", len(seen))
    print("skipped:", m["skipped"])
    print("reproduction levels available:", m["reproduction_levels_present"])
    for s in m["specimens"]:
        print("  %-30s %-46s ev=%-3d fid=%.3f" %
              (s["run_id"], "/".join(str(x) for x in s["stratum"]),
               s["replication_events"], s["fidelity"]))
