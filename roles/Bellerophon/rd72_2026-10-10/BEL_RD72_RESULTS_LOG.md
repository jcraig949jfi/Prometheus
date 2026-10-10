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
