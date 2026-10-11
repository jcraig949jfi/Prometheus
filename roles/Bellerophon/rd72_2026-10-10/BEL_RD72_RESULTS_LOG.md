# BEL-RD-72 RESULTS LOG (block results in completion order; each with its frozen analysis receipt)

## D1 -- uptake economics: the functional loss/gain ratio as a frozen prediction (prereg s2; completed 2026-10-10 ~15:06Z)
1,900 runs, 0 voids, pin 3996962c5, active 5.2 h; receipt receipts/D1_analysis.json (analyze_d1.py as frozen).
| substrate | FUNC_LOSS / FUNC_GAIN (UF arm, 150 worlds) | R | frozen prediction | origins normal / blocked (400 pairs) | discordant pairs blocked-only / normal-only | one-sided p | observed |
|---|---|---|---|---|---|---|---|
| S_LOCAL (PARTIAL, GRID LOCAL, budget 256) | 246 / 365 | 0.674 | NO_INCREASE | 16 / 28 | 21 / 9 | 0.021 | INCREASE |
| S_PAIR320 (PAIR_EXECUTION, WELL_MIXED, budget 320) | 1,640 / 1,338 | 1.226 | NO_PREDICTION | 71 / 98 | 68 / 41 | 0.006 | INCREASE |
**D1-P1 FALSIFIED** (1 testable substrate, 0 matches). The ratio rule that fitted BEL-48H post hoc (UF2) does NOT predict the
uptake-block effect in a new substrate: the effect appeared where the rule said it would not. The suppression effect itself
GENERALISED beyond the BEL-48H reference (GRID WELL_MIXED budget 256) to two new substrates (local spatial structure;
pair execution at budget 320) -- adding to the BEL-48H boundary (no effect in SOUP or at budget 384). Disposition:
mechanism account "imports destroy more functional replicators than they create" is NOT sufficient (here imports create
more FUNC than they destroy, yet blocking them still raises origination); the origin effect must act through something
other than net damage to existing replicators (e.g. damage to PRECURSORS before they are FUNC, which FUNC_LOSS/GAIN cannot
see). That is a new hypothesis, not a finding.

## Q4 -- budget coupling split into its components, manipulated separately (reviewer Q4; EXPLORATORY, static, deterministic)
Tool tools/budget_split.py; receipt receipts/Q4_budget_split_summary.json. Every copy length c = 0..255 (0 = 256-byte copy,
the NOP-knockout value) x budget 192 / 256 / 384 / 512 / 1,024 / 4,096; competence on the 16-input panel.
| specimen | input read | competence failures, c 1..160 | c 161..255 (copy reaches the I/O area 0xE0) | c = 0 |
|---|---|---|---|---|
| COPY_FIRST (copier; IN; INC; OUT) | after copy | 0 at all budgets | 95/95 at EVERY budget (192..4,096) | fails at every budget |
| IN_FIRST_OUT_LAST (IN; copier; INC; OUT) | before copy | 0 | 70 (192), 6 (256), 0 (>= 384) | fails <= 256, competent >= 384 |
| EVOLVED w4_00735 (BEL-48H M6; ECHO) | before copy | 0 | 73 (192), 9 (256), 0 (>= 384) | fails <= 256, competent >= 384 |
| COMPUTE_FIRST (IN; INC; OUT; copier) | before copy, output before copy | 0 | 0 | competent at every budget |
Reading: copy-length criticality has two SEPARABLE components. EXHAUSTION (the copy consumes the shared step budget before
the output instruction) is budget-dependent and vanishes at >= 384 -- this is what the M6 specimen has. DAMAGE (an
overlong copy overwrites the input slot before it is read) is budget-INDEPENDENT; it exists only when the input is read
after the copy. Output-before-copy removes both. Consequence for BEL-48H M6 / B1: "the coupling vanishes when the budget
exceeds the copy cost" is true of the exhaustion component only; an input-after-copy architecture stays coupled at any
budget. The position of ONE instruction (IN) relative to the copy decides which physics couples computation to heredity.

## E1b -- long-horizon accumulation inside a composite task (prereg s6 / s6-A; DISCOVERY; completed 2026-10-10T17:06:36Z)
150 runs, 0 voids, plan sha256 11c59eb3..., pin 6570ec568, frozen analysis tools/analyze_e1.py; receipt receipts/E1b_analysis.json.
| cell | runs | FUNC alive at end | established (FUNC at t500) | LO acquired | HI acquired | BOTH |
|---|---|---|---|---|---|---|
| C1_ON (COND_ONE, paid) | 80 | 15 | 16 | 15 | 13 | 0 |
| C1_OFF (COND_ONE, unpaid) | 30 | 9 | 11 | 6 | 0 | 0 |
| CM_ON (COND_MULTI, paid) | 40 | 13 | 14 | 13 | 0 | 0 |
- E1-a (LO, C1_ON > C1_OFF, all runs, frozen): 15/80 vs 6/30, Fisher one-sided p 0.67 -- NOT SUPPORTED. The frozen test is
  dominated by survival (~80% of worlds lose their replicators before t500 in every cell).
- E1-b (BOTH): 0 vs 0, p 1.0 -- NOT SUPPORTED. No world in any cell ever held an organism solving both halves.
- E1-c: no BOTH event; nothing to order, no replay queued (plan_replay has 0 inputs). The cumulative-vs-at-once question is
  UNANSWERED by E1b, not answered negatively.
- Descriptive (prereg s6-A "established" restriction, not a test): LO 15/16 vs 6/11 (Fisher p 0.027); HI 13/16 vs 0/11
  (p 2.8e-5). LO retention (fraction of post-acquisition censuses still holding a FUNC LO solver): median 0.97 paid vs 0.06
  unpaid.
- The composition DESERT, observed: in 13 paid COND_ONE worlds a FUNC LO solver (ECHO-like) and a FUNC HI solver (x+1-like)
  COEXISTED in the same census, many for > 2,000 ticks, LO carriers in the 50-180 range, HI carriers 1-14 -- and no
  organism ever carried both halves. Both partial capabilities are reachable and payable; their composite is not reached
  within 3,000 ticks of coexistence. In COND_MULTI the transform half ((x^0x55)+3) was never reached (0/14 established).
- Consequence for s7: C3-P1 / C3-P2 need >= 5 BOTH events; they are expected to be NOT_TESTABLE. They run anyway as
  frozen (no outcome-dependent cancellation); C2 (source removal of LO) is unaffected.

## C2 / C3 -- source removal and mechanism dependency on E1b worlds (prereg s7; CONFIRMATORY; completed 2026-10-10 ~19:25Z)
101 runs, 0 voids; plan generated from E1b by the frozen plan_c23.py (sha256 93bf6136...), pin 6570ec568; analysis
tools/analyze_c23.py; receipt receipts/C23_analysis.json.
| arm | n | LO-or-BOTH FUNC at end | BOTH | FUNC alive at end |
|---|---|---|---|---|
| C2 NONE | 16 | 13 | 0 | 16 |
| C2 SHAM (median 74 NONE organisms removed) | 16 | 13 | 0 | 15 |
| C2 REMOVE (median 99 LO carriers removed) | 16 | 11 | 0 | 16 |
| C3 A_PRESENT | 11 | 9 | 0 | 11 |
| C3 SHAM | 11 | 10 | 0 | 11 |
| C3 ABLATE | 11 | 7 | 0 | 11 |
| C3F IMPLANT (16 foreign LO FUNC) | 10 | 6 | 0 | 8 |
| C3F IMPLANT_SHAM (16 own NONE FUNC) | 10 | 4 | 0 | 5 |
- C2-a (SHAM > REMOVE at the end): 13/16 vs 11/16, p 0.34 -- not supported; it was reported, not a claim by itself.
- C2-b (regeneration, frozen sign test): LO came back in 12 of the 16 REMOVE worlds. In 8 the re-acquisition delay was
  shorter than the world's original t_LO, in 1 it was longer, and 3 were ties at the 100-tick census grain. One-sided
  sign test on the decided pairs: p 0.0195. HOLDS.
  Reading, under the confound disclosed in the prereg: removing every carrier of the capability does not remove it from
  the world. It returns faster than it first arose, so the route is held by the world (non-carrier material, or a copier
  population poised to re-make it), not only by the lineage that carried it. The light instrument does not resolve
  where the route is held.
- C3-P1 and C3-P2: NOT_TESTABLE (0 BOTH events in every arm; threshold 5). Whether A makes B reachable is unanswered,
  because B (the composite) is never reached with or without A. See E1b and the desert probe.
- C3F, descriptive: implanting a foreign LO solver left LO present at the end in 6/10 worlds vs 4/10 for the sham, and
  FUNC alive in 8/10 vs 5/10. Not tested (n is small).

## DP -- composition-desert geometry probe (EXPLORATORY, post hoc after E1b, static; tool tools/desert_probe.py, commit 62e1609e2)
In each of the 13 E1b worlds where FUNC LO and FUNC HI solvers coexisted, I took the most common LO and HI FUNC tapes at
the first coexistence census and counted one-step routes to a FUNC BOTH tape from each.
- Operators: SUB 16,320, MOVE 50,512, INS 16,384, DEL 64, and DONOR 51,416 neighbours (DONOR = segments of the partner
  tape, i.e. uptake from the coexisting solver).
- Paths: 2,000 random 3-step paths over all five operators, with the partner as donor.
Result: 0 routes from either side in all 13 worlds (26 tapes, ~3.9M one-step neighbours) and 0 of 52,000 three-step paths.
The LO and HI tapes are unrelated programs (Hamming distance 27-64 of 64 bytes). They are not two variants of one machine.
Positive control (receipt in this section; same predicate, world e1b_00011's config):
- The hand-built composite (copier + COND_ONE witness, 8 bytes) is BOTH and FUNC.
- 13 of its single-byte zero knockouts break it, and the probe finds the way back (SUB 1 route each, MOVE 2 in one case).
So the instrument sees routes where they exist.
Reading: the composite is not one or a few operator steps from the partial solvers the dynamics actually produces. Nor
is it a donor splice away from the coexisting partner. COND_ONE needs a compare-and-branch structure that neither half
contains, and payment for each half does not build it. This is a reachability desert in the directive's sense, located
by geometry: the obstacle is the missing control-flow element, not the distance between the two halves.
Limit: geometric only (no selection, no rates); 3-step paths are sampled, not exhaustive.

## RU-E1b -- the anti-triviality ruler applied to the evolved E1b solvers (EXPLORATORY, static; tools/apply_ruler_e1b.py)
Receipt receipts/RULER_E1b.json. For each world, I profiled the most common FUNC LO tape and HI tape at the last census
that held one (47 tapes from 34 worlds). Each was checked against the composite task's halves and against the whole-panel
single task it might really be solving.
| tapes | solves the whole single task | competence-critical bytes (min / median / max) | crit. bytes shared with replication | hidden redundant pairs | FUNC + competent 3 generations |
|---|---|---|---|---|---|
| 34 LO solvers (C1_ON, C1_OFF, CM_ON) | ECHO on all 16 inputs: 34/34 | 1 / 3 / 7 | 24/34 | 2/34 | 33/34 |
| 13 HI solvers (C1_ON) | INC on all 16 inputs: 13/13 | 3 / 5 / 6 | 12/13 | 0/13 | 13/13 |
Reading (triviality, Workstream B):
- None of the "half-composite" solvers is partial progress toward COND_ONE. Each is the simplest single-task machine, ECHO
  or INC, and coincides with the target on one half of the inputs.
- "Acquiring LO" in E1b is the acquisition of ECHO, which BEL-48H already showed is payable and reachable. "Acquiring HI"
  is the acquisition of INC.
- The composite needs a compare-and-branch that neither machine contains. This matches the desert probe (DP) and E1b's 0
  composites.
- The positive content is narrower than the E1-a/E1-b framing: payment raises ECHO and INC acquisition in established
  worlds (descriptive). Both are heritable through 3 copy generations (multi-generation ruler, the reviewer's request;
  33/34 and 13/13). In most of them the computation and the replication share critical bytes, which is coupled
  architecture.
- One CM_ON tape (e1b_00116) loses FUNC at generation 2, a delayed failure of heredity that a one-generation test would
  not see.

## A3 stage 2 -- operator-aware prediction of completion in unseen worlds (prereg s5 + erratum s5-E1; CONFIRMATORY; completed 2026-10-11 ~03:20Z)
1,374 runs, 0 voids, plan sha256 d3ebea24..., pin 30410747f; analysis tools/analyze_a3.py at 3e91c7b03 (the erratum's
fix: precursor joined from the plan by id); receipt receipts/A3_stage2_analysis.json.
- Tapes: 597 replanted (2 worlds each); 46 completed (a FUNC origin within 100 ticks in >= 1 of 2 worlds).
- Background: 1/60 (PARTIAL), 6/60 (PAIR), 2/60 (COPY) worlds originate with no transplant.
| AUC | pooled | COPY | PARTIAL | PAIR |
|---|---|---|---|---|
| S_op (operator-aware) | 0.592 | 0.552 | 0.577 | 0.626 |
| S_sub (substitution) | 0.586 | 0.497 | 0.579 | 0.632 |
| S_nz (non-zero bytes) | 0.606 | 0.458 | 0.580 | 0.702 |
- A3-P1 (S_op beats S_sub): 95% CI of the difference [-0.008, +0.031]. FAILS.
- A3-P2 (S_op beats S_nz): [-0.094, +0.058]. FAILS.
- A3-P3 (S_op > S_sub in >= 2 physics): 1 of 3. FAILS.
- The operator-aware ruler does not predict better than substitution or byte content on this harvest.
Why (descriptive, post hoc; the route classes are from the frozen stage-1 scan):
| route class | tapes | completed |
|---|---|---|
| >= 1 one-step SUB route | 9 | 8 |
| INS / DEL routes only (none had MOVE-only routes) | 7 | 1 |
| no one-step route under any operator | 581 | 37 |
- Fisher, SUB-route vs no-route: p 5e-9. Where geometry says "one substitution away", completion is near-certain.
- 581 of 597 harvested non-FUNC tapes (97%) have no one-step route. Their completion rate (6.4%) is at or below the
  background expected for 2 worlds (~10%). Those "completions" are other organisms' origins, not the tape's.
- The AUC test is therefore decided by noise in the zero-route mass, and the operator-aware score has nothing to add:
  - in this harvest, no tape is reachable by a move that substitution does not also reach;
  - the BEL-48H move-rich precursors (N1) came from a different source, the founding assembly products of complementation
    worlds, not random non-FUNC survivors at tick 100.
Answer to directive Q1: NO. Operator-aware reachability did not predict transitions better than the simpler ruler in
unseen worlds.
Answer to Q2: in this harvest, no apparent desert was an artifact of the operator model (0 MOVE-only routes in 600
scanned tapes).
Limit: one-step geometry only. Multi-step accessibility was not part of the frozen scores.

## C2R -- where is the regenerated capability held? (prereg s9; CONFIRMATORY; completed 2026-10-11 ~04:30Z)
48 runs, 0 voids, plan sha256 e6ecc430..., pin 3e21631fe; receipt receipts/C2R_analysis.json. Validity: in all 16 worlds the
re-run REMOVE census equals the C2 run at every common (100-tick) census (0 invalid), a deterministic-replay receipt.
| arm (removed, median) | re-acquired (first FUNC LO appearance, 20-tick census) | median delay |
|---|---|---|
| REMOVE (99 carriers) | 16/16 | 60 |
| NEAR (145: carriers + within Hamming 16) | 12/16 | 80 |
| RESET (all 254, replaced by fresh copiers) | 9/16 | 140 |
- C2R-P1 (REMOVE faster than RESET): 13 of 15 decided worlds, sign p 0.0037. HOLDS.
- C2R-P2 (REMOVE faster than NEAR): 10 of 12 decided, p 0.019. HOLDS.
Reading:
- The regeneration seen in C2-b is NOT only copier abundance. A world that keeps its non-carrier material regains the
  capability faster and more often than an equally large, copier-rich population with no material.
- Part of the route sits in near-carriers (variants within 16 bytes of an ECHO solver).
- A material-free copier population still re-invents ECHO in 9/16 worlds within 1,000 ticks, as expected for the cheap
  ECHO (triviality audit s1).
- In the directive's terms: ENVIRONMENTAL REGENERATION from stored, near-functional material, plus fresh re-invention.
  It is not lineage continuity.
Disclosures:
1. The re-acquisition count of 16/16 here vs 12/16 in C2 is consistent, because their censuses agree at every 100-tick
   tick. The extra 4 are appearances between 100-tick censuses that did not last to a 100-tick census. "Re-acquisition"
   here is FIRST APPEARANCE, not durable return.
2. NEAR removes more organisms than REMOVE (median 145 vs 99) with no size-matched sham. Part of P2 may be removal size.
3. RESET replaces the population; it does not shrink it.
4. The capability is ECHO (ruler RU-E1b), the cheapest computation in the family. This shows lineage-independent
   persistence of a MINIMAL capability, not of a complex one; directive C2's "beyond minimal copiers" holds only in that
   narrow sense.

## K2 -- composing two computational blocks across a verified desert (prereg s3 + amendment 3-A1; CONFIRMATORY; completed 2026-10-11T06:30Z)
1,320 runs, 0 voids, plan sha256 727cea06..., pin cbc7a1eb6; analysis tools/analyze_k2.py; receipt receipts/K2_analysis.json.
Target: COND_MULTI by a FUNC replicator, from fixtures X (copier + transform block) and Y (copier + branch block).
- Desert verification (review R1): >= 4 substitutions from X and >= 5 from Y; 0 competent in ~3e9 two-step neighbours.
  The aligned pair has exactly one assembly route (a prefix transfer).
- 22 cells x 60 seeds, 1,000 ticks, three operator regimes (COPY_BYTE, COPY_STRUCT, PARTIAL_BYTE), payment ON vs
  RANDOM_REWARD (and OFF under PARTIAL_BYTE).
Outcome:
- COMP_SR (a competent replicator born): 0 in 1,320 runs.
- COMP_PERSIST: 0.
- COMP_ANY (a competent non-replicating child of a non-competent writer): 1 run, k2_00856 (XY_AL, PARTIAL_BYTE, ON): 4
  such children among 70,032 births, none alive at the end.
- Extinction: 822 / 1,320 runs (62%) extinct by tick 1,000; 555 informative (alive at, or extinct after, tick 500). That
  leaves 765 runs (58%) dead before tick 500. Informative runs per cell: 5 - 37.
Frozen tests:
- K-P1 (desert holds under historical operators, XY_AL COMP_SR <= 2/60): NOT_TESTABLE by its own rule (29 and 24
  informative runs, rule needs >= 30). The raw count, 0/60 in both cells, is in the predicted direction.
- K-P2 (PARTIAL_BYTE crossing exceeds the controls): FAILS (1/60 vs 0/60 each; all p >= 0.5).
- K-P3 (two-source): NOT_TESTABLE (no COMP_SR).
- K-P4 (selection, COMP_PERSIST ON > RANDOM_REWARD): FAILS (0 vs 0).
Reading: a verified 4-5-step desert between two working half-blocks is NOT crossed in 1,000 ticks, under any of the three
copy operators, with or without payment, even with the single aligned assembly route present in 60 worlds. The partial-
overwrite operator produced the only competent product (4 non-replicating machines in one world). Assembly happened at
the rate the geometry allows, and the product was not heritable.
Failure classification (directive F list):
- extinction before exploration: a large share (58% of runs dead before tick 500);
- reachable but improbable: the one-route aligned case;
- insufficient search duration: 1,000 ticks; LADDER2 ran 20,000 ticks and got 0/240 for COND_ONE.
- Not instrument blindness: competence is checked on every birth.
- Not inaccessible: an assembly route exists and was used once.

## F1 -- COND_ONE desert stress test with a distance ladder (prereg s10; CONFIRMATORY; completed 2026-10-11T08:09Z)
240 runs, 0 voids, plan sha256 d57a6102..., pin 8bc7f5384 (resumed once with more workers at 06:30Z, no plan change);
analysis tools/analyze_f1.py; receipts receipts/F1_analysis.json, receipts/F1_baseline_geometry.json.
| founder | paid: crossed / FUNC at end / established | unpaid: crossed / FUNC at end / established | one-step routes to target |
|---|---|---|---|
| W0 (the composite itself) | BOTH kept to the end 1/14 | BOTH lost before the first census in 20/20 | (is the target) |
| KO1 (1 knockout) | 0 / 10 / 13 | 0 / 5 / 6 | SUB 1-103 |
| KO2 | 0 / 3 / 4 | 0 / 3 / 5 | 0 |
| KO4 | 0 / 6 / 8 | 0 / 4 / 5 | not scanned |
| ECHOH (copier + ECHO) | 0 / 7 / 10 | 0 / 3 / 5 | 0 |
| REP (bare copier) | 0 / 3 / 4 | 0 / 1 / 5 | 0 |
- F1-P0 (the setting keeps a composite): 1 of 14 surviving paid W0 worlds holds a FUNC BOTH at the end. FAILS.
- F1-P1 (KO1 > REP) and F1-P2 (KO1 paid > unpaid): 0 vs 0. FAIL.
FROZEN INTERPRETATION (s10): the setting DESTROYS composites. The E1b null and the C3 NOT_TESTABLE are reclassified as
DESTRUCTIVE SELECTION / INSTABILITY, not as inaccessibility. Even founders one substitution from the composite never
produced one in 2,000 ticks.
Trajectories (descriptive, from the census): in paid W0 worlds the composite persists 100-1,800 ticks and decays DOWNHILL.
- The survivors at the end are the same ECHO (LO) and INC (HI) replicators E1b evolved, in 12 of the 13 that lost it.
- One world (f1_00011) still held 47 BOTH carriers at tick 2,000, next to 100 HI and 34 LO.
- Unpaid W0 worlds lose it before tick 100.
Mechanism hypothesis (POST HOC, from reading the kernel after the outcome):
- Payment is per interaction, on ONE uniform random input (world.py: task.inputs(rng); coupling.py: correct -> BONUS).
  ECHO and INC are each paid on about 50% of interactions, the composite on 100%.
- The composite earns at most twice a half-solver's bonus but carries 10 competence-critical bytes against 2-6, so most
  of its mutations land on a half-solver.
- Under this payment rule, the half-solvers are a mutation-selection attractor next to the composite. The composite is
  downhill-unstable, and the step back up (one substitution) is not taken because a half-solver's one-step mutants
  toward the composite are rare (KO1 SUB routes: 1-2 for most) and selected only 2:1.
- Untested here. The decisive test is the same ladder with ALL-OR-NOTHING payment (a bonus only for a full-panel
  correct answer), which removes the half-credit attractor; or a payment on both halves per interaction.
  -> NEXT_CAMPAIGN #1.

## F2 -- the F1 ladder under PAIRED-HALVES payment (prereg s11 + erratum s11-E1; CONFIRMATORY; completed 2026-10-11T09:18Z)
80 runs, 0 voids, plan sha256 62a92bd0..., pin f3cd80c86; analysis tools/analyze_f2.py at fc93ca78d (bool-cast erratum);
receipt receipts/F2_analysis.json. Same seeds and founders as F1 (payment ON), payment rule changed only.
| founder | paired rule: BOTH at end / crossed / FUNC end / established | kernel rule (F1, matched): same |
|---|---|---|
| W0 | 2 / (18) / 11 / 14 | 1 / (16) / 14 / 19 |
| KO1 | 1 / 1 / 7 / 8 | 0 / 0 / 10 / 13 |
| ECHOH | 0 / 0 / 2 / 3 | 0 / 0 / 7 / 10 |
| REP | 0 / 0 / 2 / 3 | 0 / 0 / 3 / 4 |
- Second-check denials: ECHOH 25,109 / 25,123 and REP 5,533 / 5,535; W0 worlds ~15% of correct events. The instrument did
  what it was meant to: half-solvers earn nothing.
- F2-P0 (maintenance, paired > kernel): 2/20 vs 1/20, p 0.5. FAILS. By the frozen rule the half-credit hypothesis is
  REJECTED: the planted composite is still not maintained when half-solvers earn no bonus.
- F2-P1 (KO1 crossing): 1/20 vs 0/20, p 0.5. FAILS.
Descriptive:
- Under the paired rule the composite lasts longer. The last census with a FUNC BOTH is >= 1,700 in 6/20 worlds, against
  2/20 under the kernel rule.
- Unpaid half-solvers still take over: one world ends with 193 INC replicators, and the composite's descendants decay to
  them anyway. The decay does not need the half-solvers to be paid. It is a VARIATION effect (mutation breaking the
  composite downhill), not a SELECTION-for-halves effect.
- Paired payment lowers survival of worlds founded by non-composites (ECHOH FUNC at end 2/20 vs 7/20): they lose their
  bonus.
- ONE CROSSING, the first evolved composite of the campaign: f2_00022 (founder KO1 position 9, the CP operand set to 0, an
  INC-like HI solver).
  - A FUNC BOTH appears at tick 1,100 and is held to tick 2,000 (47 carriers at the end, next to 99 HI and 33 LO).
  - The matched kernel-rule world (f1_00042) never crossed.
  - The founder has 1 SUB route (restore the operand); the intermediate (the founder) is functional (HI).
  - Single event: not a rate, not tested.

## XR -- forensics of the one crossing (f2_00022; EXPLORATORY, post hoc; tools/replay_crossing.py, commit 45832c827)
Receipt receipts/F2_crossing_replay.json. Replay: HalvesWorld (byte-origin tags) + the identical paired-payment code path,
deterministic, to tick 1,100. VALID: alive and FUNC-halves counts equal the original at all 11 common censuses.
The directive's crossing questions:
- Which operator: a single point change. Of the composite's 8 competence-critical bytes, 7 are founder material
  (transplant0, tick 0). The eighth, position 9 (the compare operand the KO1 founder lacked), is NEW material written at
  the birth of tick 652.
- Intermediate states functional: yes. The founder is an INC-like HI solver and FUNC.
- Inherited: yes. Composite carriers were present at tick 1,100 and 47 at tick 2,000.
- Timing: the first FUNC composite was BORN at tick 652, but the light census first saw one at tick 1,100. It existed
  below census detection or flickered for ~450 ticks before establishing.
- Temporal depth 652 ticks, 2 epochs (founder material + one later change), so CUMULATIVE in the E1-c sense: composed
  across time from an earlier capability plus a later change.
- Repeated independently: NO (1 of 40 KO1 worlds across F1 + F2).
- Changes future reachability: not measured.
Triviality: this is the geometrically predicted distance-1 repair of a knockout (the founder had 1 SUB route). It shows
that the dynamics CAN take a one-step route to the composite and keep it, at ~1/20 per 2,000 ticks under paired
payment. It is NOT an evolved innovation.

## F3 -- is composite maintenance limited by mutation? (prereg s12; CONFIRMATORY; completed 2026-10-11 ~12:10Z)
60 runs, 0 voids, plan sha256 c9998d12..., pin e662f8944; analysis tools/analyze_f3.py; receipt receipts/F3_analysis.json.
Same 20 W0 worlds (the planted COND_ONE composite) as F1; only the mutation rate (and, in one arm, payment) changes.
| mutation (per byte per tick) | payment | composite kept to tick 2,000 | FUNC at end | median last census with a FUNC composite |
|---|---|---|---|---|
| MED 0.008 (F1, matched) | ON | 1/20 | 14 | 100 |
| LOW 0.002 | ON | 13/20 | 15 | 2,000 |
| VLOW 0.0005 | ON | 17/20 | 18 | 2,000 |
| VLOW 0.0005 | OFF | 8/20 | 10 | 1,300 |
- F3-P0 (VLOW > MED): 17/20 vs 1/20, Fisher one-sided p 2.0e-7. HOLDS.
- F3-P1 (LOW > MED): 13/20 vs 1/20, p 6.8e-5. HOLDS.
- Dose-response, monotone: 1 -> 13 -> 17 (VLOW > LOW p 0.14, not tested).
FROZEN INTERPRETATION (s12): composite maintenance is limited by DESTRUCTIVE VARIATION, an error threshold. The E1b / F1
composition null is a MUTATION-LOAD boundary: at the mutation rate where minimal capabilities (ECHO, INC: 2-6 critical
bytes) are acquired and kept, a 10-critical-byte composite cannot be kept even when planted.
Reported:
- At VLOW, payment still matters: 17/20 paid vs 8/20 unpaid (Fisher p 0.004). Selection for the computation is
  necessary but not sufficient.
- With F2: payment structure is not the limiting factor (F2-P0 failed), mutation rate is.
Consequence for the campaign's central question:
- Search needs variation and maintenance needs its absence. In this substrate, the rate that lets populations FIND
  ECHO / INC destroys anything with ~10 critical bytes. So "composition" fails here before reachability is even tested.
- The next step is variable or self-regulated mutation (e.g. a high-mutation search phase then a low-mutation phase, or
  heritable copy fidelity), or redundancy: NEXT_CAMPAIGN.
Limit: the planted composite is the hand-built witness. Whether an evolved composite with redundant critical bytes would
sit above the threshold is unknown.
