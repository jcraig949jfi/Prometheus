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

## W5 block 2 -- does target material raise the rate of replicator ORIGIN? (prereg s8; 400 runs, 0 voids, 3.03 h)

200 seed-pairs, RANDOM PARTIAL WELL_MIXED, preserve vs zero, OriginWorld. First FUNC event: preserve 9/200 [2.4, 8.3%],
zero 7/200 [1.7, 7.1%]; discordant 8 vs 6, McNemar p 0.79. W5-P4 FALSIFIED (no detectable effect; low base rate gives
little power -- recorded as 'no effect detected at n = 200', not as absence). Causes: preserve UPTAKE 4, MUTATION 3,
BORN_ASSEMBLY 1, SELF_CONSTRUCT 1; zero MUTATION 4, UPTAKE 1, BORN_ASSEMBLY 1, SELF_MOVE 1. Reading: target material is
necessary for designed fragment complementation (E5b) and raises repair births (E5a), but it is not a measurable driver
of de novo origin; the origin routes (mutation, uptake) do not need preserved target bytes.

## W5 block 3 -- budget-coupled ('E', copy-then-compute) vs separated ('S', compute-then-copy) (prereg s10; 192 runs, 0 voids)

| id | result | verdict |
|---|---|---|
| W5-P6 E favoured under ON + HIGH | E share > 0.5 in 15 seeds, < 0.5 in 1 (8 undecided: no attributable FUNC organism); mean E share 0.91; sign p 0.0003 | HOLDS |
| W5-P7 E's advantage depends on payment (ON > OFF) | MED: ON < OFF in 23 of 24 seeds (E share ON 0.45 vs OFF 0.87); HIGH: no seed with both arms decided (OFF loses all attributable FUNC in most HIGH worlds; 10/24 extinct per order) | FALSIFIED (reversed at MED) |
Reading (POST-HOC): without payment the budget-coupled copier E out-replicates S (0.87 at MED); paying for the computation at
MED brings S to parity (0.45); under HIGH mutation only payment keeps replicators at all, and then E dominates. Which
architecture payment favours flips with the mutation regime. PROVISIONAL (one specimen pair; attribution by founder tags
degrades at HIGH mutation).

## N1 -- operator-matched completion, PREDICTIVE test (prereg s14; 440 runs, 0 voids, 2.30 h)

The 55 W6 precursors re-placed in new worlds at mutation VLOW vs HIGH (4 paired seeds each, 100 ticks):
NEEDLE (39; completed by mutation, 0 move routes): completion 0.14 at VLOW -> 0.78 at HIGH (+0.64); MOVE_RICH (16;
completed by uptake / self-move, >= 100 move routes): 0.98 -> 1.00 (+0.02). N-P1 HOLDS (+0.64 >= 0.20); N-P2 HOLDS
(difference of differences 0.62, bootstrap 95% CI [0.50, 0.73]); N-P3 HOLDS (move-rich completions at VLOW: SELF_MOVE 33,
UPTAKE 27, BORN_ASSEMBLY 3, MUTATION 0). CL-17 PROVISIONAL (post-hoc) -> CAUSALLY_CONFIRMED by a mutation-rate
intervention: whether a precursor needs point mutation or is completed by the copy dynamics themselves is a property of
its neighbourhood, measurable beforehand.

## B1 -- budget coupling versus the execution budget (prereg s15; 600 runs, 0 voids, 2.22 h)

Competent dominant machines and BUDGET_COUPLED share: budget 192: 31 machines, 0.52; 256: 28, 0.50; 384: 41, 0.00.
B-P1 HOLDS (Fisher p < 0.001), B-P2 HOLDS (monotone). When the budget exceeds what an unbounded copy costs, budget-
dependent criticality vanishes -- the COST component of coupling is a consequence of the shared step budget. Shared
critical bytes persist at 384 (OTHER_SHARED 31/41): the DAMAGE component (an unbounded copy wrapping over the
organism's own code) is budget-independent, as noted before freezing. Acquisition is higher at the larger budget (41 vs
28-31 of 200). CL-11 refined: budget coupling = CAUSALLY_CONFIRMED as a budget phenomenon.

## W6 block 4 U -- is uptake necessary? (prereg s13; 1,600 runs, 0 voids, 4.95 h)

800 seed-pairs (PARTIAL 400, PAIR 400), normal vs UPTAKE BLOCKED (partner bytes cannot be imported into the own tape;
the ablation acted in 800/800 blocked runs, median 905 bytes reverted per run). U-P1 HOLDS (0 uptake origins blocked; 9
normal). U-P2 HOLDS and overshoots: origins blocked 84 vs normal 61 (+38%); discordant pairs 55 blocked-only vs 32
normal-only, McNemar p = 0.018; both physics (PARTIAL 49 vs 37, PAIR 35 vs 24). Not a survival artefact: blocked worlds
go extinct MORE (531 vs 488 of 800) with fewer births (median 846 vs 920); origin timing unchanged (median tick 63 vs 64).
Causes, blocked vs normal: MUTATION 47 vs 32, BORN_ASSEMBLY 19 vs 8, SELF_MOVE 15 vs 11.
READING: uptake is a real route to the first replicator (9/61 here, 13/85 in W6 C1) but on balance it SUPPRESSES
origination -- removing it raises the origin rate. Hypothesis (untested): importing partner bytes mostly overwrites the
importer's own cryptic precursor. Class: CAUSALLY_CONFIRMED (net suppressive effect; paired intervention, 800 pairs, two
physics); mechanism of suppression PROVISIONAL.

## W6 block 4 X -- the same competition with an INDEPENDENT specimen pair (prereg s13; 192 runs, 0 voids)

E = w6b3_00001 (BUDGET_COUPLED), S = w6b3_00020 (SEPARATED), fresh seeds. MED: E share ON 0.07 vs OFF 0.60; ON < OFF in
24/24 seeds -- X-P7 HOLDS (the W5 block 3 MED reversal reproduces). HIGH + ON: S majority in 4/4 decided seeds -- X-P6
FALSIFIED (W5-P6's 'E dominates at HIGH' was pair-specific). Generalisable part: paying for the computation favours the
compute-first architecture (at least at MED mutation) across two independently evolved pairs.

## W6 block 2 -- GENERALITY of two-fragment complementation (prereg s11; 720 runs, 0 voids, 2.0 h)

Three confound-free variants (writer holds NO LDIR and writes LD T,n by constructed writes; carrier holds only LDIR; each
fragment non-FUNC with 0 single-substitution routes, asserted): V0 LD T,0x40@13 + LDIR@34; V1 LD T,0xA0@4 + LDIR@10;
V2 LD T,0x40@30 + LDIR@45. 40 seed-pairs x 6 arms each.

| variant | FUNC in AB / A / B / none | AB vs target-material ablation (AB-only vs zero-only) | AB vs COPY physics | first event two-source |
|---|---|---|---|---|
| V0 | 40 / 40 / 1 / 2 | 6 vs 0, p 0.031 (zero arm 34/40) | 32 vs 0 | 40/40 |
| V1 | 40 / 39 / 0 / 2 | 15 vs 0, p 6e-5 (25/40) | 38 vs 0 | 40/40 |
| V2 | 40 / 40 / 2 / 2 | 12 vs 0, p 0.0005 (28/40) | 31 vs 0 | 40/40 |
G-P1..G-P4 HOLD in every variant. M1 is general across operands, offsets and construction mode (copied OR computed
writer bytes); the writer alone completes against random background (A arm 39-40/40, as in W2). Unlike the W2 fragment,
the target-material ablation here REDUCES but does not abolish FUNC (25-34/40 remain): with a writer that carries no
copy routine, other completion routes exist in these worlds (not dissected).

## POST-HOC -- rearrangement accessibility of the 75 W6 origin precursors (one-off; receipts/MOVE_ACCESS_POSTHOC.json)

Single-substitution and single segment-move routes to FUNC from each precursor (pre-event tape): completed by MUTATION
(53): median 4 substitution routes, 0 move routes (39/53 have no move route); by UPTAKE (13): 74 / 870; by SELF_MOVE (7):
121 / 2,067. The completing operator matches the neighbourhood: narrow 'needle' precursors are completed by a point
mutation, move-rich precursors by moving bytes. Not preregistered (labelled); a predictive test is in NEXT_EXPERIMENTS.

## Mechanism records

### M1. Two-fragment complementation (heritable replicator from two non-replicating sources)
1. Minimal mechanism: a non-replicating writer lays down part of a copy routine (LD T,n) in a partner whose own bytes
   supply the rest (LDIR); the composite child is a self-copier and propagates by copying.
2. Conditions: unwritten target bytes survive into the child (ENDOGENOUS_PARTIAL, target_fill preserve).
3. Causal dependencies: both byte sets individually necessary (knockout); single-source reconstructions non-FUNC.
4. Failure boundaries: ENDOGENOUS_COPY (97/100 none); target_fill zero (39/40 -> 1/40).
5. Smallest specimen: writer 07 14 08 40 03 02 15 ff (+ 08 40 @20-21); carrier 01 01 15; child 08 40 15 ...
6. Independent origins: 194 worlds (W2) + 40 (E5b) + 3 x 40 (W6 block 2, three confound-free variants, all G-P1..P4 hold).
7. Ablation: remove A -> FUNC in 6/100 (B) and 8/100 (none) worlds; remove target material -> 1/40.
8. Transplant: transplanted to new operands (0x40, 0xA0), offsets (13/34, 4/10, 30/45) and a writer that holds no LDIR
   and writes by computation: two-source assembly in 120/120 first events (W6 block 2).
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
4. Failure boundaries: blocking uptake removes this route (0 origins) yet RAISES total origination by 38% (W6 block 4 U):
   uptake is a creative route and a net suppressor at once.
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

### M6. Budget coupling of computation and reproduction (CORRECTED; the 'through the child' reading is retracted)
Evolved ECHO replicators that run their task code AFTER the copy depend on the copy routine's length operand: an
unbounded copy (C = 0, 256 bytes) exhausts the 256-step budget before the task code runs; doubling the budget restores
competence (w4_00735, causal). Prevalence 10/20 (post-hoc), OUT never executed from the child copy (0/20). Confirmation
of prevalence on fresh seeds: W6 block 3 (E-P2). Selection test (budget-coupled 'copy-then-compute' E vs 'compute-then-
copy' S, ON/OFF x MED/HIGH): W5 block 3 -- its frozen labels 'entangled/separated' refer to these two specimens.
Class: CAUSALLY_CONFIRMED (specimen), PROVISIONAL (prevalence).

### M7. Payment-driven conflict repair
Contingent payment yields competent self-replicators from a damaging hybrid (10/300 vs 0/300) by in-place repair of the
damaging lineage (8/10). Class: CAUSALLY_CONFIRMED (frequency), PROVISIONAL (in-place route).
