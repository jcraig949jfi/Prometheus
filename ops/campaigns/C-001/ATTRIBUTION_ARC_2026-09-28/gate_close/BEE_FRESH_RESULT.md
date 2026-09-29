# E-003 BEE s4.3 fresh-set agreement: PASS (Archaeon, 2026-09-29)
**Set:** seed fefefe074; 500 interactions; pre sha256 937ffb58.
- All three outputs were sealed before any exchange (BEE_SEALED_HASHES.json @ ad2d65a11).
- Comparator bee_fresh.py (c28a74a97), unchanged since before the seed.
- Owner: tracer 823cbef1 (freeze cfb57f67a) via a declared relabelling driver agreement_export.py a320d94b (500/500
  value-checked).

**Gate** (raw per class, >= 0.995 on label/addr/ctrl/exec, owner vs BOTH): PASS.

| pair | self (14,389) | other (976) | perf_none (109) | unwritten (16,526) |
|---|---|---|---|---|
| owner ~ Archaeon (fully raw) | 1.0 | 1.0 | 1.0 | 1.0 |
| owner ~ reference, gated fields | label 14388/14389, rest 1.0 | 1.0 | 1.0 | 1.0 |
| reference ~ Archaeon | label 14388/14389, rest 1.0 | 1.0 | 1.0 | 1.0 |

- owner ~ Archaeon covers every field, performer included.
- The reference is the SAME outlier against both the owner and Archaeon.

**Every disagreement, classified** (records: bee_fresh_result/BEE_FRESH_DISCREPANCIES.jsonl; each carries (k, i); the pre-state
is in BEE_FRESH_PRE.jsonl):
- **B-P1, performer, 61 loci (self class; e.g. k=193 i=0): category (1), spec ambiguity.**
  * The store opcode byte's label is non-MOVE with a single entity base (e.g. COMPUTED{W13}).
  * Owner and Archaeon: performer entity = that base (W). Reference: no performer entity.
  * Nothing in the BEE text defines the performer ENTITY of a non-MOVE opcode label. v4 s2.2 defines the performer as the
    opcode byte's label; NPE C6 D1 (the reference's reading) is NPE-only.
  * Not gated. But it can move a locus between the self and none classes, and so class counts and class-keyed Qs.
  * RULING, which chooses nothing after exposure: BEE production reports class counts, per-class gates and class-keyed Qs
    under BOTH readings: (A) the entity base of a single-base non-MOVE opcode label; (B) no entity. Any verdict that differs
    between them is marked READING-DEPENDENT.
  * Recorded for the final reviewer and a future prereg version.
- **B-L1, data label, 1 locus (k=69, i=62): category (1).**
  * COMPUTED_FROM{W63} (owner, Archaeon) vs COMPUTED{W63} (reference). This is the flattening boundary between register INC
    and memory INC (reference SPEC_ISSUES B3; the same class as NPE S1).
  * Below the gate threshold. Recorded as a counterexample. No repair; no tracer is changed.

**No category (2), (3) or (4) disagreement.** Owner and Archaeon agree exactly on all 32,000 loci.
