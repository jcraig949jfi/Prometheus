# EXP-07 RESULT -- surrogate START STATE (INSTRUMENT; 2026-10-11)

Prereg: prereg/EXP-07_SURROGATE_START_STATE.md (3fa5e628c, before data). Run 06:25:48Z-06:29:19Z under supervise
(DONE, 0 restarts). 38 planted systems x k {2,4,8}. Data EXP-07_planted.jsonl (sha256 09da99354cf444ba...).

| grid | cells | O0 (stationary start) MAE / SE | O1 (system.init start) MAE / SE | rule (MAE <= .5 x O0, abs SE <= .05) |
|---|---|---|---|---|
| G1 (EXP-06 systems) | 66 | .054 / -.054 | .027 / -.012 | PASS |
| G2 (fresh, wseed 3/4) | 48 | .089 / -.089 | .0453 / -.042 | FAIL (MAE .0453 > .0446) |

VERDICT (by rule): **H-START REJECTED** -- narrowly: on the fresh grid O1's MAE misses half of O0's by .0008.
The threshold is not revisited.

What the data say anyway (descriptive): the start-state mismatch is the DOMINANT part of the defect. Median signed
error by reservoir gain, O0 -> O1: a .50 -.000 -> -.002 | a .70 -.029 -> -.014 | a .85 -.110 -> -.037 |
a .95 -.290 -> -.043. A residual underprediction of ~-.04 remains at high memory on both grids and is not
explained (a candidate: the one-step fit's gain error, EXP-06's untested mechanism).

Consequences:
- EXP-04 used stationary starts: its family-level underprediction is substantially an instrument artefact. EXP-04's
  INCONCLUSIVE stands; no rescoring.
- A v2 surrogate (init start) is better but NOT qualified by its own rule. Any use needs a new prereg addressing the
  residual first, then requalification on fresh discovery worlds.
- Design lesson for C4: a "local physics" predictor must also know the TASK's start condition; the stationary
  distribution is not the task's initial distribution. Recorded for DESIGN v0.4.
