"""atlas_feed -- emit the pilot's lineage as harvester-ready records + a schema-extension proposal (directive Phase 7).

Atlas is READ-ONLY for this seat: this module WRITES NOTHING to the atlas schema or code. It reads the packet's
frozen preregs and results and emits, into roles/Bellerophon/atlas_bee/:
  ATLAS_FEED.jsonl              one record per adaptation: SOURCE_EXPERIMENT -> ADAPTATION -> ECOSYSTEM_ATTEMPT -> EVIDENCE
  ATLAS_EXTENSION_PROPOSAL.md   the SMALLEST extension that lets Atlas index a cross-ecosystem ADAPTATION

Each ADAPTATION has its own immutable identity (its frozen prereg sha256); the record never overwrites the source
experiment -- it points at it with a TRANSPLANT_OF edge / reason CROSS_SUBSTRATE_TRANSPLANT (vocabulary Atlas already
has). Run:  python -m prometheus.atlas_bee.atlas_feed
"""
from __future__ import annotations

import json
import pathlib

from prometheus.toolbox import receipt as RC
from prometheus.atlas_bee.harness import PACKET
from prometheus.atlas_bee.freeze import verify

IDS = ["a1", "a2", "a3", "a4", "a5", "a6"]


def _engine_instance() -> str:
    b = RC.build_block()
    h = RC.host_block() or {}
    host = h.get("host") or h.get("machine") or "unknown"
    return "bee@%s:%s" % (host, b["kernel_hash"][:12])


def _record(aid: str) -> dict:
    prereg = json.loads((PACKET / ("PREREG_%s.json" % aid)).read_text(encoding="utf-8"))
    result = json.loads((PACKET / ("RESULT_%s.json" % aid)).read_text(encoding="utf-8"))
    assert verify(prereg), "prereg %s does not recompute" % aid
    body = prereg["prereg"]; sha = prereg["freeze"]["sha256"]
    comp = result["comparison"]
    native = "atlas_bee/%s@%s" % (aid, sha[:12])
    return {
        "adaptation": {"id": aid, "native_id": native, "prereg_sha256": sha, "immutable": True,
                       "question": body.get("question"), "manifest_counts": body["manifest"]["counts"]},
        "source_experiment": {"atlas_key": result["source"]["atlas_key"], "disposition": result["source"].get("disposition")},
        "edge": {"relation": "TRANSPLANT_OF", "reason": "CROSS_SUBSTRATE_TRANSPLANT", "basis": "DECLARED",
                 "from": native, "to": result["source"]["atlas_key"],
                 "note": "the source question moved to another ecosystem (BEE); the source experiment is not modified"},
        "ecosystem_attempt": {"engine": "bee", "engine_instance": _engine_instance(),
                              "utc": result.get("utc"), "wall_s": result.get("wall_s"), "replay_ok": result.get("replay_ok")},
        "manifest_refusals": [e for e in body["manifest"]["entries"] if e["relation"] in ("OMITTED", "UNREPRESENTABLE")],
        "evidence": {"verdict": comp["verdict"], "summary": comp.get("summary"),
                     "new_phenomena": comp.get("new_phenomena", []),
                     "differences": comp.get("differences", {})},
    }


def write_feed() -> pathlib.Path:
    recs = [_record(a) for a in IDS if (PACKET / ("RESULT_%s.json" % a)).exists()]
    out = PACKET / "ATLAS_FEED.jsonl"
    out.write_text("\n".join(json.dumps(r, sort_keys=True) for r in recs) + "\n", encoding="utf-8", newline="\n")
    return out


PROPOSAL = """# Atlas extension proposal -- indexing a cross-ecosystem ADAPTATION (Bellerophon atlas-bee pilot)

STATUS: PROPOSAL ONLY. Atlas is read-only for the Bellerophon seat; nothing here is applied to the atlas schema or
code. This documents the SMALLEST extension that would let Atlas index the pilot's records (ATLAS_FEED.jsonl).

## What already exists (no change needed)

- engine / engine_instance: BEE is a new `engine` row `bee`; its instance id is synthetic, `bee@<host>:<kernel_hash12>`
  (kernel_hash + host from the BEE receipt), exactly as SOURCES.md prescribes for an engine that mints no instance id.
- edge vocabulary: relation TRANSPLANT_OF ("the parent's question moved to another world/substrate/engine") with
  reason CROSS_SUBSTRATE_TRANSPLANT and basis DECLARED already expresses ADAPTATION -> SOURCE_EXPERIMENT. No new
  relation is required.
- source visibility, validity_state (INSTRUMENT_FAILURE / PARTIAL_EVIDENCE), and the RAN/OBSERVED/CONCLUDED layering
  all carry over unchanged.

## The one concept Atlas does not yet name: the ADAPTATION

An ADAPTATION is not an experiment (it did not run in the source engine) and not merely an attempt (it carries a
translation manifest and a frozen design). The smallest addition is a single node kind with its own immutable
identity, linked to both the source and the BEE run:

  SOURCE_EXPERIMENT --(TRANSPLANT_OF, CROSS_SUBSTRATE_TRANSPLANT)--> ADAPTATION --(REALISED_BY)--> ECOSYSTEM_ATTEMPT --(EVIDENCE)--> fact/conclusion

- ADAPTATION identity = its frozen prereg sha256 (immutable; a repair is a new descendant ADAPTATION via DESCENDANT_OF,
  never an overwrite). Fields: source_experiment key, question, manifest counts, manifest refusals.
- ECOSYSTEM_ATTEMPT = an ordinary BEE attempt row (engine `bee`, the synthetic instance, its receipts), reusing the
  existing attempt table; the only new column is a nullable `adaptation_id` foreign key.
- REALISED_BY / EVIDENCE reuse the existing edge and fact_evidence machinery.

Concretely, two additive changes and no rewrites:
  1. a small `adaptation` table (id = prereg sha256, source_experiment, question, manifest_counts JSON, refusals JSON);
  2. a nullable `adaptation_id` on `attempt` (an attempt that realises an adaptation names it; every other attempt
     leaves it null).

The manifest's relation vocabulary (IDENTICAL / ANALOGOUS / MODIFIED / OMITTED / UNREPRESENTABLE) is data on the
adaptation row, not a schema change; the OMITTED/UNREPRESENTABLE entries are exactly the honest record of what the
transplant could not carry.

## Records

The harvester-ready records are in ATLAS_FEED.jsonl (one JSON object per line). Each carries the ADAPTATION identity,
the TRANSPLANT_OF edge to the source, the BEE ecosystem attempt, the manifest refusals, and the evidence (verdict,
summary, new phenomena). A harvester with the two additive changes above can ingest them without touching any source
experiment.
"""


def write_proposal() -> pathlib.Path:
    out = PACKET / "ATLAS_EXTENSION_PROPOSAL.md"
    out.write_text(PROPOSAL, encoding="utf-8", newline="\n")
    return out


def main() -> int:
    f = write_feed(); p = write_proposal()
    print(json.dumps({"feed": str(f.name), "proposal": str(p.name), "records": sum(1 for _ in f.read_text(encoding="utf-8").splitlines() if _.strip())}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
