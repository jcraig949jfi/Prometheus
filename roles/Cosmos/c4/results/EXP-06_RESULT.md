# EXP-06 RESULT -- surrogate underprediction on planted systems (INSTRUMENT QUALIFICATION; 2026-10-11)

Prereg: prereg/EXP-06_SURROGATE_UNDERPREDICTION.md (03521ea80, before data). Run 06:11Z-06:23:41Z under supervise
(DONE, 0 restarts), 22 planted systems x k {2,4,8} = 66 cells. Data EXP-06_planted.jsonl (sha256 4d9b200e97a99e26...).

| variant | median abs err | median signed err | qualifies (MAE <= .5 x V0 and abs SE <= .05) |
|---|---|---|---|
| V0 frozen | .054 | -.054 | -- |
| V1 noise 0 | .217 | +.066 | no |
| V2 no clip | .054 | -.054 | no (clip never binds) |
| V3 ridge 1e-4 | .051 | -.051 | no |
| V4 n 16384 | .068 | -.068 | no |

VERDICT (by rule): underprediction CONFIRMED on planted linear systems (SE -.054 < -.05); no variant identifies a
cause -> INSTRUMENT_DEFECT UNEXPLAINED. The surrogate stays UNQUALIFIED for cross-family use.

Failure shape (descriptive): the error is a function of MEMORY. Median signed error by reservoir gain a:
  a .50: V0 +.004 (V1 +.375) | a .70: -.029 (+.246) | a .85: -.095 (+.046) | a .95: -.263 (-.235).
At a .95, k 2 the truth is .71-.89 excess and the surrogate predicts .25; with the composition noise switched off
it still predicts .30. So the defect is in the learned DETERMINISTIC map (or its readout), not in the noise model,
clipping, regularisation or sample size: the composed surrogate forgets faster than the system. Plausible
mechanism (untested): one-step regression from stationary states recovers the contraction a poorly when the
stationary state is dominated by accumulated input variance, and a small per-step gain error compounds over k + 2
steps. A linear system with a = .95 is exactly where this matters most.

Consequence for EXP-04: its uniform underprediction is at least partly this defect, so EXP-04's family failures
(graph, phase) cannot be read as physics. Next: EXP-07 localises the defect by ORACLE substitution.
