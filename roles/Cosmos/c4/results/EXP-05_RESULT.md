# EXP-05 RESULT -- stig: ring RETURN vs ACCUMULATION (EXPLORATORY; DISCOVERY batch 3; 2026-10-11)

Prereg: prereg/EXP-05_STIG_RETURN_VS_ACCUM.md (fdd6097f0, before data). Run 06:10:02Z-07:15:05Z under supervise
(DONE, 0 restarts, 160/160). Data EXP-05_stig_ksweep.jsonl (sha256 37674eff6e30b5d8...). 60 stig worlds (48 moving, v >= 1;
12 with v = 0), k 1..40, L 16 and L 24 (intervention); controls 20 rnn + 20 phase.

## Preregistered decision
| statistic | value | H-RETURN needs | H-ACCUM needs |
|---|---|---|---|
| median r16 (excess vs R at L16) | .225 | >= .50 | -- |
| median r24 | .309 | >= .50 | -- |
| ring change moves the pattern toward R24 | 44/48 worlds (.917) | >= .70 | -- |
| median Spearman(k, excess) | .545 | -- | >= .50 |
| median abs(excess L24 - excess L16) | .262 | -- | < .05 |
VERDICT (by rule): **INCONCLUSIVE** (neither hypothesis meets all its clauses).

What the clauses say separately:
- H-ACCUM in its stated form is contradicted: usability depends strongly on ring length (median change .26
  excess), which a pure accumulation account forbids.
- H-RETURN's geometry is right in direction (the intervention moves the pattern as predicted in 92% of worlds), but
  the noise-free predictor R explains little of the variance.
- v = 0 (sensor never leaves the cue): median excess .998 at every k (Spearman with k -.02): the cue is never lost
  when the sensor stays put, consistent with geometric reachability.
- Controls: rnn and phase usability FALLS with k (median Spearman -.31, -.67), as expected for decaying memory.

## Failure shape (descriptive, post hoc; NO evidential weight -- several looks at batch 3)
Median r16 / r24 / Spearman(k) by diffusion D: D < .1: .53 / .55 / .41 | .1-.2: .20 / .24 / .58 |
.2-.3: .20 / .26 / .72. Jitter and decay strata show no comparable gradient (r16 .19-.34; .21-.24).
Reading: where the trace does not diffuse, the return predictor works; diffusion spreads the cue trace along the
ring into the moving sensor's reach, and the spread grows with elapsed time -- hence "rise with k".
New hypothesis H-SPREAD (for a fresh-data prereg, EXP-09): usability = reachability of a decaying, diffusing trace
by a moving, jittering sensor; zero-parameter predictor = expected cue-trace mass inside the sensor window at query
time, computed from the declared knobs.

## Consequence
stig's k-dependence is geometric (trace transport + sensor motion), not a memory property a stationary local
probe can see. This supports DESIGN v0.4 note 3 (a separate geometric-reachability stratum). EXP-04's "rise with k"
was not accumulation.
