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
import os
import pathlib

# C9-D06: the per-run files are gitignored and exist only in the checkout that ran the
# campaign; Z80A_FROZEN_OBS points at them from any other checkout.
PRED = pathlib.Path(os.environ.get("Z80A_FROZEN_OBS") or
                    (pathlib.Path(__file__).resolve().parent.parent / "z80atlas-2026-09-19" / "observatory"))
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


# ----------------------------------------------------------------------------- S4 / P-11
# The panel above samples the predecessor's 1,031 ADMISSIBLE runs. S1-C re-adjudicates
# every one of them through P-11, and the operator directive (2026-09-23, S4) requires the
# panel be REBUILT from P-11 survivors, not assumed. This rule was committed BEFORE any
# S1-C result was read; the source file it consumes is written by the forensic
# aggregator (z80atlas-forensics-2026-09-23/p11_reassay.py).
#
# THE RULE, in order:
#   0. eligible = REPLAY_MATCH (the replay reproduced the frozen run exactly), at least
#      one P-11-causal event, the donor genome of the FIRST P-11-causal event recorded
#      (earliest epoch, then pair index), and a cell valid under the Cycle-9 grammar;
#   1. coverage round-robin over (reproduction, structure, representation) strata,
#      exactly as the predecessor rule;
#   2. within a stratum: number of P-11-causal events desc, then that first event's
#      donor fidelity desc;
#   3. ties by ascending sha256(run_id).
# Arm B implants the donor genome of the first P-11-causal event - never the predecessor
# `first_replicator` genome, which for a pair event is the donor of the first event the
# predecessor criterion accepted, P-11-causal or not.
P11_SOURCE = (pathlib.Path(__file__).resolve().parent.parent / "z80atlas-forensics-2026-09-23"
              / "P11_REASSAY.jsonl")


def select_p11(panel_size=PANEL_SIZE, source=P11_SOURCE):
    import grammar as G
    cands = []
    skipped = collections.Counter()
    for line in pathlib.Path(source).read_text(encoding="ascii").splitlines():
        r = json.loads(line)
        if r.get("status") != "REPLAY_MATCH":
            skipped["replay_not_matched"] += 1
            continue
        if not r.get("n_p11_events"):
            skipped["no_p11_causal_event"] += 1
            continue
        fe = r.get("first_p11_event") or {}
        if not fe.get("donor_genome"):
            skipped["no_donor_genome"] += 1
            continue
        c = r["cell"]
        if not G.is_valid(c):
            skipped["invalid_under_cycle9_grammar"] += 1
            continue
        cands.append({
            "run_id": r["run_id"], "family": r["run_id"].split("-")[0], "cell": c,
            "stratum": (c.get("reproduction"), c.get("structure"), c.get("representation")),
            "n_p11_events": r["n_p11_events"], "fidelity": fe.get("fid_other", 0.0),
            "genome": fe["donor_genome"], "first_p11_epoch": fe.get("epoch"),
            "tie_hash": hashlib.sha256(r["run_id"].encode()).hexdigest()})
    by_stratum = collections.defaultdict(list)
    for c in cands:
        by_stratum[c["stratum"]].append(c)
    for k in by_stratum:
        by_stratum[k].sort(key=lambda c: (-c["n_p11_events"], -c["fidelity"], c["tie_hash"]))
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
    return picked, dict(skipped), len(cands)


def manifest_p11(panel_size=PANEL_SIZE, source=P11_SOURCE):
    picked, skipped, n_eligible = select_p11(panel_size, source)
    body = [{"run_id": p["run_id"], "family": p["family"], "stratum": list(p["stratum"]),
             "n_p11_events": p["n_p11_events"], "fidelity": p["fidelity"],
             "first_p11_epoch": p["first_p11_epoch"], "genome_hex": p["genome"],
             "genome_len": len(p["genome"]) // 2, "cell": p["cell"]} for p in picked]
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, ensure_ascii=True).encode()).hexdigest()
    return {"rule": "P-11 survivors only; coverage round-robin over (reproduction,structure,"
                    "representation); within stratum P-11-causal events desc, first P-11 "
                    "event donor fidelity desc; ties by ascending sha256(run_id)",
            "source": str(pathlib.Path(source).name),
            "source_sha256": hashlib.sha256(pathlib.Path(source).read_bytes()
                                            .replace(b"\r\n", b"\n")).hexdigest(),
            "n_eligible": n_eligible, "skipped": skipped,
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
