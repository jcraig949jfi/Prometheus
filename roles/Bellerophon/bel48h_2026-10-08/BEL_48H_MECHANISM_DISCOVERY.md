# BEL-48H Window 5 -- Mechanism discovery

Campaign BEL-48H-2026-10-08, Bellerophon[ubu005-0eb14d49]. This report collects the mechanisms that survived the first
four windows, the Window-5 interventions run on them (prereg s7, s8, s10), and their confirmations (W6, prereg s9, s11).
Every mechanism record follows the directive's 10 fields. Classes: CAUSALLY_CONFIRMED / REPRODUCED / PROVISIONAL.
Status of pending blocks is stated where they are cited; the final numbers are in BEL_48H_FINAL_REPORT.md.

## W5 block 1 -- complementation repair and its ablation (prereg s7; 240 runs, 0 voids, 2 workers)

| id | result | verdict |
|---|---|---|
| W5-P1 target material makes function MORE persistent at HIGH mutation | seeded copiers, PARTIAL, 40 seed-pairs: FUNC at the end preserve 28 vs zero 34; discordant 4 vs 10, McNemar p 0.18 (reversed sign) | FALSIFIED |
| W5-P2 more 'repair births' (functional child of a non-functional writer) with target material | MED 39/40 pairs higher (median 288 vs 92 per run); HIGH 36/40 (910 vs 269); sign tests p < 1e-6 | HOLDS |
| W5-P3 the target-material ablation abolishes W2's fragment complementation | E5b: causal assembly 39/40 preserve vs 1/40 zero; FUNC at the end 39 vs 24, McNemar 16 vs 1, p 0.0003 | HOLDS |

Reading. Target material is a real repair channel (P2) and is NECESSARY for fragment complementation (P3), but its
net effect on persistence depends on the mutation regime: at MED it helps (8 vs 1 discordant pairs, p 0.039 -- not the
frozen test level), at HIGH it hurts (4 vs 10) and preserve worlds hold fewer functional organisms (median 96 vs 155):
the same channel that completes broken copiers also overwrites working ones with chimeras. PROVISIONAL (one block).

## Mechanism records

### M1. Two-fragment complementation (heritable replicator from two non-replicating sources)
1. Minimal mechanism: a non-replicating writer lays down part of a copy routine (LD T,n) in a partner whose own bytes
   supply the rest (LDIR); the composite child is a self-copier and propagates by copying.
2. Conditions: unwritten target bytes survive into the child (ENDOGENOUS_PARTIAL, target_fill preserve).
3. Causal dependencies: both byte sets individually necessary (knockout); single-source reconstructions non-FUNC.
4. Failure boundaries: ENDOGENOUS_COPY (97/100 none); target_fill zero (39/40 -> 1/40).
5. Smallest specimen: writer 07 14 08 40 03 02 15 ff (+ 08 40 @20-21); carrier 01 01 15; child 08 40 15 ...
6. Independent origins: 194 worlds (W2) + 40 (E5b); generality on 3 confound-free variants: W6 block 2.
7. Ablation: remove A -> FUNC in 6/100 (B) and 8/100 (none) worlds; remove target material -> 1/40.
8. Transplant: W6 block 2 tests the mechanism transplanted to new operands/offsets with a writer that holds no LDIR.
9. Generalisation limits: GRID WELL_MIXED, 300 ticks, physics v2, one task-free setting.
10. Other engines: 'complementation of partial programs across individuals' -- measure single-source reconstructions
    against the composite in any engine with partial writes or crossover-like construction (NPE, SFE).
Class: CAUSALLY_CONFIRMED.

### M2. Single-step activation of a copy-assembled cryptic precursor (how replicators first arise)
1. Mechanism: imperfect copying by non-replicating writers builds tapes that carry most of a copy routine but copy
   nothing; one change (mutation, uptake or self-move) switches the routine on.
2. Conditions: random worlds, any endogenous physics; LDIR + permissive NOP filler (17/27 depend on zero filler).
3. Causal dependencies: the completing change is individually necessary (reversion kills FUNC) in 54/75 in-place
   origins; LDIR writes the window in 85/85.
4. Failure boundaries: LDIR off or undefined -> HALT abolishes replication (grounding P8); BYTECODE32 0/150.
5. Smallest specimen: LD T,0x40 + LDIR (3 bytes) with zero entry registers (S = 0, C = 0 -> 256-byte sweep).
6. Independent origins: 21 (W3a discovery) + 85 (W6 confirmation, distinct seeds).
7. Ablation: per-byte reversion of the completing change.
8. Transplant: cores implanted into 20 random backgrounds at the same positions: mean portability 0.1-0.54 per cell
   (W2 reach) -- the machine is background-dependent.
9. Limits: single-execution FUNC criterion; knockout misses redundant elements (2/85 carry two LDIRs).
10. Other engines: 'activation of cryptic, copy-assembled precursors' predicts that reachability is governed by the
    density of near-complete inert machinery that copying produces, not by graded fitness ramps.
Class: REPRODUCED (85 independent unseen populations).

### M3. Uptake: horizontal assembly of a replicator from partner material
1. Mechanism: an organism's own code copies partner bytes into its own tape; the imported bytes, inert in the partner,
   complete a copy routine in the importer.
2. Conditions: any endogenous physics (the partner is in the window either way).
3. Causal dependencies: each taken-up byte individually necessary (reversion) in 13/13 W6 uptake origins.
4. Failure boundaries: not yet tested by blocking uptake (next experiments).
5. Specimen: w2_00345 -- 08 a0 .. 15 imported into positions 4, 5, 10 in one execution, each byte originally made by a
   different mutation in a different organism.
6. Independent origins: 5 runs / 5 seeds (W3a), 13/85 (W6).
7-8. Ablation: per-byte reversion; transplant not measured.
9. Limits: one-record-per-byte history across executions.
10. Other engines: horizontal transfer as a route to the FIRST instance of a capability, not only its spread.
Class: CAUSALLY_CONFIRMED per specimen; REPRODUCED as a route (15% of origins).

### M4. Distributed persistence (function without lineage continuity)
Function persists in ~98-100% of fragment worlds while the first assembled lineage survives in only 32-38%; in 42/100
fresh worlds no assembly lineage is alive at all. Persistence runs through recurrent re-assembly and capture. Ablating
target material lowers persistence (39 -> 24 of 40). Class: REPRODUCED (W6 C2); causal role of re-making: CAUSALLY
CONFIRMED by E5b. Other engines: measure capability persistence separately from lineage persistence; they diverge.

### M5. Rearrangement accessibility (epistemic fault-line for reachability rulers)
Fragment A: 0/16,320 single substitutions but 8/50,512 single segment moves reach FUNC; random tapes 0/1,515,360 moves.
Under copy physics, COPY_AB origins are built from A's bytes in 60/60. Class: CAUSALLY_CONFIRMED for the specimen.
Other engines: any reachability/mutational-robustness ruler must use the physics' own variation operators.

### M6. Entangled computation and reproduction
16/20 evolved ECHO replicators share competence- and copy-critical bytes; traced specimens produce the answer after
the copy, through the child in the window. Selection test (entangled vs separated, ON/OFF x MED/HIGH): W5 block 3.
Class: PROVISIONAL.

### M7. Payment-driven conflict repair
Contingent payment yields competent self-replicators from a damaging hybrid (10/300 vs 0/300) by in-place repair of the
damaging lineage (8/10). Class: CAUSALLY_CONFIRMED (frequency), PROVISIONAL (in-place route).
