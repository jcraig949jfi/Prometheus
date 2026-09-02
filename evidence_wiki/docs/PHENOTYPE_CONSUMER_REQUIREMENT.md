# PEW Phenotype Consumer Requirement (for Daedalus / SFE)

Architectural decision (V3 closeout, charter s4):

- SFE owns phenotype emission semantics. Daedalus owns the schema.
- PEW consumes phenotype observations by reference and never retroactively
  redefines an authoritative emitted observation. PEW may layer versioned
  interpretations, associations, anomaly scores, candidate bumps, and
  falsification proposals on top; the emitted record itself is history.

## Minimum information PEW needs per observation

PEW can consume opaque/hash-stable identifiers throughout — no naming
scheme, serialization, or storage choice is being requested. What must be
recoverable from an emitted observation (field names are Daedalus's):

1. Organism identity        (stable id or content hash of the candidate)
2. World/environment id     (stable id or content hash)
3. Encounter identity       (unique per encounter; replay-safe)
4. Phenotype observation    (what behavior/output was observed)
5. Measurement definition   (id + version of the measure that produced 4/6)
6. Measurement value        (the number/label itself)
7. Cost/resource usage      (tokens, wall time, or whatever SFE meters)
8. Timestamp/order          (enough to order encounters)
9. Ledger/content hash      (the SFE hash-chain anchor, e.g. entry_hash)

Item 9 is the load-bearing one: it is what lets PEW reference immutable SFE
history instead of copying it.

## Why this is currently binding

Measured during V3 metabolization: only 2 of 6,006 candidate artifacts in
the SFE ledger carry phenotype scores in their metadata, so
discrimination-per-cost (fossil query q3) is unanswerable over the existing
record. Any future encounter that emits items 1-9 becomes immediately
minable; nothing else about SFE needs to change for PEW's purposes.

Contact surface: batch ingest at POST /api/v1/fossil/encounters/batch
(field `encounters`, per-row idempotency, ~3,600 ev/s measured pooled).
