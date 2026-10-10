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
