# BEL-48H -- Failure boundaries and epistemic fault-lines

Sparse by design (directive s8): only the conditions under which a supported claim or ruler STOPS being true. Every row
points to the rows that show it. Classes as in the prereg.

## A. Rulers

| ruler | holds when | fails when | evidence |
|---|---|---|---|
| PROVENANCE label (DEF-BEL-008) | counting the material origin of child bytes, multi-hop within one execution | parentage is meant: inert-majority writers, prefix replicators under PARTIAL, partner-authored code (PAIR_EXECUTION), children built across several ticks by different writers | Review B S1a/S1d/S1e/Q2; first version also failed for window-staged copies (Review A, fixed dc1833bc2) |
| RESEMBLANCE label (historical) | the child is a whole-tape copy of one parent | children are constructed or chimeric: disagreement with material origin 8-94% of births per cell; 22-26% of living organisms change genetic root in WELL_MIXED mixing worlds | W1v2 s3/s5 |
| SR classifier (historical) | counting own-code copy events | -- (robust: 0.02% vs PROVENANCE, 1.2% non-FUNC children); misses copies made through registers / staging (14 runs with a TRB and no SR) | W1v2 W1-P4/P5 |
| 'written' replicates (DEF-BEL-010) | rejecting zero-padding and zero-sweep artefacts | sterile near-copies pass; prefix and shifted replicators fail; on evolved tapes it agrees with v1 on 242/245 | Review B Q4; W1v2 W1-P9 |
| FUNC (campaign) | one-generation own-position self-copy | prefix / shifted replicators (rejected); sterility of the child (caught only by TRB chaining or FUNCK) | Review B; funck.py |
| PAIRED init (DEF-BEL-009) | aligning the world RNG at tick 0 | any treatment that changes births, deaths or tapes: divergence at tick 1 (150/150); paired variance = unpaired variance | W1v2 C1; Review B Q3 |
| byte-substitution neighbourhood (geometry.scan, G4) | counting point-mutation accessibility | the physics' own operator is segment copying with offsets: fragment A is 0/16,320 substitutions but 8/50,512 segment moves from a replicator | W3b addendum |
| historical G6 classifier | -- | initial organisms carry mechanism None: every initial writer defaults to BUILT_BY_COPY (ERRATA E1, reproduced: 62/62 on W1v2) | W1v2 s3 |
| seed = base + lane*1e9 + k | independence WITHIN a cell | pooled ACROSS cells: one initial population counted up to 4x (H1: 550 runs / 150 seeds; grounding G1: 2,400 / 400) | amendment 2 |

## B. Mechanisms

| claim | holds when | stops when | evidence |
|---|---|---|---|
| two-fragment complementation (CL-04) | ENDOGENOUS_PARTIAL with target material preserved | ENDOGENOUS_COPY (97/100 none); target_fill zero (39/40 -> 1/40) | W2 H2, W5 E5b |
| complementation repair raises persistence (CL-12) | MED mutation (8 vs 1) | HIGH mutation: reverses (4 vs 10), fewer functional organisms (96 vs 155 median) | W5 E5a |
| first assembly lineage carries the function | -- | it does not: 32-38% of first assemblies leave living TRB descendants while function persists in ~100% of worlds | W2 H2 (post-hoc; W6 C2 pending) |
| incremental ramp to replication (grounding G6b reading) | 5/27 origins | the typical precursor copies nothing (21/27): activation, not a graded ramp | W3a W3-P2 |
| competence from new bytes (W4-P5) | 19/20 (corrected reading) | -- | W4 |
| cross-lineage repair of a damaging machine | never observed (0/10) | -- | W4 W4-P3 |
| spontaneous replication | 6/7 LOCAL cells | BYTECODE32 0/150 under both rulers (historical 2/200) | W1v2 |

## C. Process faults of this campaign (recorded so they are not repeated)

Instrument defects found and fixed before the affected analysis was read: DEF-008 one-hop (Review A); FUNC zero-sweep;
short-tape slice shrink in Func; `comp` name collision with World.comp. Analysis defect found after the results were
read: W4-P5 tag-case (reported both ways). Prediction defects: W1-P7 written from a withdrawn figure; W2-P3 from a 3-run
pilot. Hand-written future timestamps in the prereg (three errata). Calibration ledger: roles/Bellerophon/calibration/LEDGER.md.
