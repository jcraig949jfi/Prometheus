#!/usr/bin/env python3
"""Reconcile producer cost receipts against engine cost events, BY DIGEST.

    python deploy/reconcile_costs.py [--json]

TRACKA-RECON-2's resolution, run on real data. The producer and the executor
name the same physical act differently -- Archaeon says `transfer`, Vivarium
and the engine say `retrieval` -- so a (attempt_id, stage) join reports one
byte movement as belonging to neither side. What all three DO share is the
bytes, so the join key is the artifact digest.

READ ONLY on the live ledger (`mode=ro`). Nothing is written to production.

IT RUNS A CONTROL. A join that has never matched anything is not known to be
capable of matching, so an empty result would be indistinguishable from a
broken join. The control replays a producer receipt onto a THROWAWAY engine,
settles it with the digest in refs, and reconciles that -- proving the join
works before the live result is interpreted.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sqlite3
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.dirname(HERE)
SF = os.path.dirname(ENG)
REPO = os.path.dirname(SF)
for p in (ENG, os.path.join(SF, "SerendipityFoundryClient"), REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

from sfe.runtime import Foundry                                   # noqa: E402
from archaeon.producer import costs as _costs                     # noqa: E402

LIVE_DB = r"F:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine\var\engine.db"


def producer_entries():
    """Every producer receipt under archaeon/docs/h0h5/ that carries a vector,
    projected into the engine's entry shape (which is where refs live)."""
    out = []
    for path in sorted(glob.glob(os.path.join(REPO, "archaeon", "docs", "h0h5",
                                              "ISSUE_RECEIPTS_*.json"))):
        try:
            doc = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        rel = os.path.relpath(path, REPO).replace(os.sep, "/")
        ents = doc.get("engine_entries")
        ce = doc.get("cost_event") or {}
        if not ents:
            continue
        for e in ents:
            out.append({"source": rel,
                        "candidate_set": doc.get("candidate_set_id"),
                        "producer_cost_event_id": ce.get("cost_event_id"),
                        "stage": ce.get("stage"),
                        "attempt_id": ce.get("attempt_id"),
                        "source_refs": ce.get("source_refs") or [],
                        "output_refs": ce.get("output_refs") or [],
                        **e})
    return out


def engine_entries_live():
    """Every engine cost-event resource entry, with its sealed refs."""
    if not os.path.exists(LIVE_DB):
        return None, "live ledger not found: %s" % LIVE_DB
    cx = sqlite3.connect("file:%s?mode=ro" % LIVE_DB.replace("\\", "/"),
                         uri=True, timeout=20)
    cx.row_factory = sqlite3.Row
    try:
        try:
            rows = cx.execute(
                "SELECT c.cost_event_id, c.world_id, c.stage, c.attempt_id, "
                "e.payload FROM cost_events c LEFT JOIN events e "
                "ON e.world_id=c.world_id AND e.event_seq=c.event_seq"
            ).fetchall()
        except sqlite3.OperationalError as exc:
            return None, ("no cost_events table on the live ledger (%s). That "
                          "table arrives with schema 8; anything that ran "
                          "before the migration has no engine-side cost events "
                          "to reconcile against, and never will." % exc)
        out = []
        for r in rows:
            try:
                p = json.loads(r["payload"] or "{}")
            except (TypeError, ValueError):
                continue
            for res in p.get("resources", []):
                out.append({"cost_event_id": r["cost_event_id"],
                            "world_id": r["world_id"], "stage": r["stage"],
                            "attempt_id": r["attempt_id"], **res})
        return out, None
    finally:
        cx.close()


def control(tmp):
    """Prove the join CAN match, on a throwaway engine, before believing an
    empty answer from the live one."""
    f = Foundry(os.path.join(tmp, "control.db"))
    c = f.create_client("recon-control")
    s = f.create_session(c, "recon-control")
    w = f.create_world(s, "recon-control", budget={
        "artifact_bytes": {"limit": 10_000, "enforcement": "measured"}})["world_id"]
    f.start_world(w, c)
    art = f.create_artifact(w, "blob", b"control bytes", client_id=c)
    digest = art["artifact_id"]

    ce = f.record_cost_event(
        w, stage="retrieval", attempt_id="control-attempt",
        source_artifacts=[digest],
        resources=[{"resource": "artifact_bytes", "quantity": 13,
                    "unit": "bytes", "method": "counter",
                    "refs": {"artifact_digest": digest}}],
        client_id=c)
    prod = [{"resource": "output_bytes", "quantity": 13, "unit": "bytes",
             "method": "counter", "scope": "campaign",
             "refs": {"artifact_digest": digest,
                      "producer_cost_event_id": "cost:control"}}]
    eng = [dict(e, cost_event_id=ce["cost_event_id"]) for e in ce["resources"]]
    rep = _costs.reconcile_by_digest(prod, eng)
    f.close()
    return {"digest": digest, "result": rep,
            "join_can_match": bool(rep.get("matched"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", default=os.path.join(
        HERE, "COST_RECONCILIATION_2026-09-10.json"))
    a = ap.parse_args()

    print("COST RECONCILIATION BY DIGEST -- live ledger, read only")
    print("=" * 74)

    prod = producer_entries()
    eng, why = engine_entries_live()
    R = {"_what_this_is":
         "Producer cost receipts reconciled against engine cost events on the "
         "artifact digest, per TRACKA-RECON-2. The live ledger was read "
         "read-only. A control runs first so an empty result cannot be "
         "confused with a broken join.",
         "join_key": "refs.artifact_digest",
         "producer_entries": len(prod),
         "producer_sources": sorted({p["source"] for p in prod}),
         "engine_entries": len(eng) if eng is not None else None,
         "engine_unavailable_reason": why}

    print("  producer entries : %d  from %d receipt(s)"
          % (len(prod), len(R["producer_sources"])))
    for s in R["producer_sources"]:
        print("      %s" % s)
    print("  engine entries   : %s%s"
          % (len(eng) if eng is not None else "UNAVAILABLE",
             "" if eng is not None else "  (%s)" % why))

    with tempfile.TemporaryDirectory(prefix="recon-") as tmp:
        R["control"] = control(tmp)
    print("  control          : join can match = %s  matched=%s"
          % (R["control"]["join_can_match"],
             R["control"]["result"].get("matched")))

    if eng is not None:
        rep = _costs.reconcile_by_digest(prod, eng)
        R["reconciliation"] = rep
        p_keyed = sum(1 for e in prod
                      if (e.get("refs") or {}).get("artifact_digest"))
        e_keyed = sum(1 for e in eng
                      if (e.get("refs") or {}).get("artifact_digest"))
        R["entries_carrying_the_join_key"] = {"producer": p_keyed,
                                              "engine": e_keyed}
        print()
        print("  entries carrying refs.artifact_digest:")
        print("      producer %d of %d" % (p_keyed, len(prod)))
        print("      engine   %d of %d" % (e_keyed, len(eng)))
        print()
        print("  matched       : %s" % (rep.get("matched") or []))
        print("  producer_only : %s" % (rep.get("producer_only") or []))
        print("  engine_only   : %d digest(s)"
              % len(rep.get("engine_only") or []))

        # WHAT AN EMPTY ANSWER MEANS. Stated by the tool, not left to a reader.
        notes = []
        if not p_keyed:
            notes.append(
                "NO PRODUCER ENTRY CARRIES refs.artifact_digest. "
                "costs.to_engine_entries puts provenance in refs but not the "
                "digest, so the producer side has nothing to join ON. This is "
                "the single blocking gap, and it is Archaeon's to close: set "
                "refs.artifact_digest to the same string the event declares "
                "in source_refs/output_refs.")
        if not e_keyed:
            notes.append(
                "NO ENGINE ENTRY CARRIES refs.artifact_digest either, so the "
                "executor is not yet sending it on the settle path.")
        if p_keyed and e_keyed and not rep.get("matched"):
            notes.append(
                "Both sides carry the key and nothing matched, which is a "
                "real disagreement about WHICH BYTES were paid for rather "
                "than a plumbing gap. Worth chasing.")
        prod_refs = {d for e in prod
                     for d in (e.get("source_refs") or []) + (e.get("output_refs") or [])}
        if prod_refs and not any(str(d).startswith("sha256:") for d in prod_refs):
            notes.append(
                "The producer's declared references are experiment UUIDs, not "
                "content digests (%s...). Even with refs populated, those "
                "identify a ROW rather than the BYTES, so the two sides would "
                "be naming different kinds of thing. A digest join needs both "
                "sides to agree on which identity they are joining on."
                % sorted(prod_refs)[0][:20])
        R["what_this_result_means"] = notes
        print()
        for n in notes:
            print("  [!] %s" % n)

    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(R, indent=2, default=str) + "\n")
    print()
    print("  written: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
