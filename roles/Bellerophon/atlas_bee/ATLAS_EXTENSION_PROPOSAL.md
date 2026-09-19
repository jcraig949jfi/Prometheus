# Atlas extension proposal -- indexing a cross-ecosystem ADAPTATION (Bellerophon atlas-bee pilot)

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
