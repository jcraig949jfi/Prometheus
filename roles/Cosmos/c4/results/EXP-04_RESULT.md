# EXP-04 RESULT -- LOCAL SUFFICIENCY (EXPLORATORY; discovery worlds only; labels previously seen)

Prereg: prereg/EXP-04_LOCAL_SUFFICIENCY.md (f0d1fd689, 2026-10-08, before any surrogate was run on any world).
Instrument: sysid_surrogate.py (859e18741, unchanged). Driver: c4/exp04.py under prometheus.cosmos.supervise.
Run: 2026-10-11T05:43:50Z-05:58:50Z, COSMOS_HOME/c4_exp04; 300/300 worlds, 0 job failures, 1 watchdog restart
(stall of the runner itself, not of the science: see campaigns/48H_2026-10-08/INCIDENT_2026-10-08_EXP04_STALL.md).
Data: EXP-04_surrogate.jsonl (sha256 8711caf2b6cb1c99...), EXP-04_verdict.json, EXP-04_run_EVENTS.jsonl.
No confirmation data created or spent. D2 untouched.

## Preregistered per-family decisions (USABLE-B = B excess >= .10; HOLDS iff Spearman >= .70 and BA >= .75)
| family | n | usable/not | Spearman(pred, actual) | USABLE BA | pred usable rate | verdict |
|---|---|---|---|---|---|---|
| rnn | 60 | 33/27 | .951 | .939 | .48 | HOLDS |
| sediment | 60 | 45/15 | .784 | .878 | .63 | HOLDS |
| graph | 60 | 11/49 | .479 | .591 | .03 | FAILS |
| phase | 60 | 17/43 | -.079 | .500 | .00 | FAILS |
| stig | 60 | 53/7 | .088 | -- | .33 | NOT_REACHED (7 < 10 per class) |

OVERALL (by the prereg rules): **INCONCLUSIVE**. The rules cover (a) controls fail -> INSTRUMENT_DEFECT,
(b) holds on phase or stig -> LINEARIZATION, (c) fails on stig AND phase, holds elsewhere -> LOCALITY
INSUFFICIENT. Observed: two controls hold, one control (graph) fails, phase fails, stig is not reachable. None of
(a)-(c) applies. No physics conclusion is drawn and the surrogate is not tuned post hoc.

## Failure shape (descriptive, not a verdict)
Mean excess by k, predicted vs actual:
| family | k=2 | k=4 | k=8 |
|---|---|---|---|
| rnn | .39 / .57 | .15 / .25 | .02 / .12 |
| graph | .04 / .14 | .01 / .04 | .00 / .01 |
| sediment | .28 / .67 | .15 / .56 | .05 / .34 |
| stig | .23 / .42 | .13 / .67 | .04 / .82 |
| phase | .00 / .15 | .00 / .11 | .00 / .05 |

1. The surrogate UNDERPREDICTS in every family and every k (as its planted check already showed for high-memory
   reservoirs). Where actual excess sits near the .10 floor (graph), underprediction alone flips the labels: graph's
   failure is at least partly calibration (Spearman .48: the ranking is partly right).
2. stig: actual usability RISES with k (.42 -> .67 -> .82); every composed local model (linear L-0003 and this
   nonlinear surrogate) predicts DECAY. A sign error, not a calibration error. This is the clearest evidence so far
   that stig's usability is history-accumulative (the trace builds up over the episode) and not visible from a
   stationary one-step response. It is NOT a verdict: stig is uninformative under A14.
3. phase: the surrogate predicts ~0 excess even at k=2, where 15% excess is real. The one-step model does not carry
   the cue at all. Likely instrument (random ReLU features of whitened phases do not represent circular state, or
   the fitted residual noise swamps a small phase offset); untested.

## What this does and does not establish
- Establishes: the nonlinear surrogate composes usefully on rnn and sediment (exploratory, labels seen).
- Does NOT establish locality insufficiency for stig or phase, and does NOT rescue G-0007/G-0008.
- New hypothesis (H-ACCUM, untested, for a future prereg): on stig-like substrates, usability grows with episode
  length because the substrate integrates the cue-conditioned drive; a stationary local probe cannot see this.
  A test needs a k-sweep beyond 8 and a probe started from cue-conditioned (non-stationary) states, which the G7
  locality guard forbids; that tension is itself a design question for C4.
