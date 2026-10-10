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
