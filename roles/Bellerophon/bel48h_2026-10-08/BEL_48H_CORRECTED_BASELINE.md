# BEL-48H Window 1 -- Corrected scientific baseline

Campaign BEL-48H-2026-10-08, Bellerophon[ubu005-0eb14d49]. Prereg s3 + amendment 1 (W1 v2 re-freeze after Review A's
repair) + amendment 2 (seed sharing across cells). Analysis tools/analyze_w1.py (committed c062cc55f before any W1 v2
result existed; clustered versions added under amendment 2 before W1 v2 results were read). Runs 3,240/3,240, 0 voids,
4.05 h active (6 workers), pinned code 7133438e5 (kernel = repaired dc1833bc2). Raw ~/bel48h_runs/w1v2; receipt
receipts/W1V2_ANALYSIS.json. Superseded first attempt (one-hop defect): 128 runs, ~/bel48h_runs/w1_SUPERSEDED_def008_onehop.

## 1. Which repair changes physics and which only changes measurement (lane A, same-seed end-state hashes)

| switch | condition | identical / pairs | reading |
|---|---|---|---|
| DEF-BEL-008 PROVENANCE | IMPLICIT pressure, 5 reproduction modes, WELL_MIXED | 100/100 | measurement only |
| DEF-BEL-008 PROVENANCE | MINIMAL_CRITERION (PARTIAL) | 0/20 | CHANGES PHYSICS (replication credit feeds survival) |
| DEF-BEL-008 PROVENANCE | QD (PARTIAL) | 20/20 | measurement only in these runs (the credit enters the QD cell index; why it never altered selection here was not investigated) |
| DEF-BEL-009 PAIRED | RANDOM init, no transplant, 5 modes | 100/100 | no-op by construction |
| DEF-BEL-009 PAIRED | replicator transplant | 0/20 | changes the realisation (which random tapes the majority gets), not its distribution |
| DEF-BEL-010 written | geometry on specimens | -- | measurement only by construction |

So the directive's five arms collapse: under IMPLICIT pressure "provenance only" and "written-byte only" are pure
re-measurements of the historical trajectory (computed in shadow on the same runs, lanes B), "paired init only" is the
historical physics unless a transplant is present (lane C), and "all three" equals "paired init" plus shadow rulers.
W1-P1, W1-P2, W1-P3: HOLD.

## 2. Frozen predictions (amendment-2 flags in brackets)

| id | result | verdict |
|---|---|---|
| W1-P4 SR robustness | 1,581,755 SR_res births; SR_res vs SR_prov count difference 347 (0.022%); SR_res births with a non-FUNC child 18,283 (1.16%); FUNC children not SR_res 14,863 | HOLDS |
| W1-P5 spontaneity survives [CLUSTER_DEPENDENT] | pooled B1: SPONT_res 45/1,800 runs, SPONT_TRB 47/1,800 [2.0, 3.5%]; per distinct seed 32/300 [7.7, 14.7%] vs 33/300; discordant runs 12 SR-only vs 14 TRB-only (p 0.85) | FAILS the frozen clause "TRB never without SR" (14 runs have a true replicative birth the historical classifier missed); the substantive claim -- spontaneous replication exists and its rate is unchanged -- HOLDS |
| W1-P5 per cell (G1a/G1b) | SPONT_TRB >= 1 in COPY 8/300, PARTIAL 16/300, PAIR 13/300, CONSTRUCTIVE 3/300, OVERWRITE 3/300, VM_COPY 4/150; BYTECODE32 0/150 (also 0 under the historical ruler) | G1 claims SURVIVE in 6/7 cells; BYTECODE32 NOT REPRODUCED at n = 150 (grounding: 2/200) |
| W1-P6 sustained [CLUSTER_DEPENDENT] | among 69 SPONT_TRB runs (45 distinct seeds): historical sustained 24, TRB-sustained 24 (34.8% both) | HOLDS (grounding G2: 39.4%) |
| W1-P7 G6a first TRB writer copy-born >= 90% [CLUSTER_DEPENDENT] | 43/69 runs; the 26 others are INITIAL organisms (17 at tick 0) concentrated in 7 distinct seeds: per population 38/45 = 84% copy-born | FALSIFIED as stated; see s3 |
| W1-P8 pairing value | PAIRED: init RNG equal 150/150 (HISTORICAL 0/150); RNG diverges at tick 1 in 150/150 pairs under BOTH; variance of the paired final_alive difference 1,289.5 vs 1,289.7 (ratio 0.9998); the bootstrap CI is uninformative ([0.001, 1.9e5]) because the difference is bimodal (transplant world survives, control dies: mean 250.8 of 256) | HOLDS (no variance reduction) |
| W1-P9 geometry v1 vs written | COPY specimens agree 30/32; all cells 3 disagreements in 245 specimens | FALSIFIED at the 95% bar (n small); disagreement is rare everywhere |
| Controls (B3) | positive 30/30 sustained; smear 0/30, capture 0/30; bare LDIR 2/30 with a TRB | bare-LDIR DIAGNOSED (s4): control expectation wrong, instrument correct |

## 3. Which historical claims survive corrected measurement

- SPONTANEOUS SELF-REPLICATION (grounding G1): survives; same rates under both rulers (TRB uses an independent
  functional test, multi-hop provenance and the written-own-position rule).
- SUSTAINED fraction (G2): survives (34.8% vs historical 39.4%).
- SR-level statistics (self_rep_births, sr_max_depth): robust to the lineage repair (0.02% difference).
- LINEAGE-LEVEL statistics are NOT robust: res and prov labels disagree in 8-94% of births per cell (CONSTRUCTIVE
  78-94%: computed bytes the resemblance rule called 'writer'); among living organisms the genetic root differs between
  rulers for 22-26% in WELL_MIXED PARTIAL/PAIR/COPY cells (0-2% in LOCAL). Historical seed_lineage_share,
  genetic_lineages_final and 'captures' in mixing worlds are ruler-dependent and should not be cited without a ruler.
- G6a: the published "160/160 BUILT_BY_COPY / no initial random tape became the first self-replicator" was ALREADY
  WITHDRAWN on 2026-09-29 (forensics_2026-09-23/ERRATA_2026-09-29.md E1, DEF-BEL-001: the classifier tested
  mechanism == "init" but initial organisms carry mechanism None, so every initial writer defaulted to BUILT_BY_COPY;
  corrected 103/160 copy-born, 57 initial writers, 26 with their unmodified random tape). W1-P7 was written from the
  withdrawn figure -- my error (calibration ledger, 2026-10-08): the seat's own errata were not re-read before the
  prediction. On fresh seeds W1 v2 REPRODUCES THE CORRECTED PICTURE independently: first TRB writer copy-born in 43/69
  runs / 38 of 45 independent populations (84%); initial organisms in 7 populations, 17 runs at tick 0 (an unmodified
  random founder tape that already self-copies). Running the grounding's own g6_class on these runs returns 62/62
  BUILT_BY_COPY -- the defect reproduces exactly (init writers: genealogy length 1, mechanism None). Classification of
  G6a under corrected measurement: REPRODUCED in its corrected (errata) form; FALSIFIED in its published form.
- DEF-BEL-009: old same-seed transplant-vs-control contrasts are NOT retrospectively corrected; and PAIRED would not
  have helped them (s2 W1-P8).

## 4. Control diagnosis (bare-LDIR transplant, 2/30 runs with a TRB)

w1_02873: a spontaneous replicator unrelated to the transplant (its first TRB writer's tape does not contain the
transplant; the matching B1 cell's background rate is 8/300, so ~0.8 of 30 expected). w1_02897: the transplanted
LDIR-HALT tape acquired 08 40 (LD T,64) in place and became a real, short-lived replicator (1 TRB birth, depth 1) -- the
'cheat' specimen is half a replicator, i.e. a cryptic precursor of exactly the kind W3 finds at real origins. The
frozen expectation (0/30) ignored both; the instrument reported a real event correctly. Not an INSTRUMENT_FAILURE.

## 5. Descriptive (per cell; receipt)

Ruler disagreement per birth: LOCAL 8.5-78% (COPY 8.5, PARTIAL 9.9, PAIR 9.0, OVERWRITE 40, VM_COPY 30, BYTECODE32 73,
CONSTRUCTIVE 78); WELL_MIXED 9.5-94%. Mixed-origin births (>= L/8 bytes from each): <= 5.7% (PARTIAL LOCAL). Constructed
births: 2-94%. TRB mechanism signatures (DETECTOR level): 5-28 per cell. Geometry v1 vs written: 3/245 disagreements.
