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
