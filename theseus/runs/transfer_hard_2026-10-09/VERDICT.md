# THESEUS-43 verdict: the 36/37 effects on a held-out harder task (prereg roles/Theseus/prereg/2026-10-09_transfer_hard/, d3f5e6796)

Command: python -m theseus.synth.transfer_eval --tag transfer_hard_2026-10-09 --runs <9 runs> --workers 2.
Variant: cue recall V 8, k 16, sensor-only readout, task seed 0, 400/400 episodes. Selection
in every run used V 4, k 8. Samples: the same 100 children per run as the original evals.

GATE: 1-part controls .107-.128 (chance .125, <= .25); 2-part controls 1.0 (>= .80). PASSES.

## Solvers at V8 k16 (J >= .6), per 100

| seed | task0 | rep | no-law |
|---|---|---|---|
| 1 | 63 | 41 | 32 |
| 2 | 51 | 32 | 22 |
| 3 | 41 | 38 | 22 |

## H-SEL-TRANSFER (task0 vs rep)

| seed | RD [95% CI] |
|---|---|
| 1 | .22 [.082, .347] |
| 2 | .19 [.053, .317] |
| 3 | .03 [-.104, .162] |

CMH z 3.63, one-sided p 1.4e-4; RD_MH .147 [.065, .229]. SUPPORTED.

## H-LAW-TRANSFER (task0 vs no-law)

| seed | RD [95% CI] |
|---|---|
| 1 | .31 [.173, .431] |
| 2 | .29 [.158, .409] |
| 3 | .19 [.061, .310] |

CMH z 6.67, one-sided p 1.2e-11; RD_MH .263 [.178, .349]. SUPPORTED.

## Descriptive

Transfer rate (selected-task solvers that also solve V8 k16):

| arm | seed 1 | seed 2 | seed 3 | pooled |
|---|---|---|---|---|
| task0 | 63/91 (.69) | 51/78 (.65) | 41/75 (.55) | 155/244 (.635) |
| rep | 41/59 (.69) | 32/63 (.51) | 38/63 (.60) | 111/185 (.60) |
| no-law | 32/52 (.62) | 22/66 (.33) | 22/62 (.35) | 76/180 (.42) |

No child that fails the selected task solves the harder variant (0 in all 9 runs).

Variant RD_MH beside the selected-task RD_MH (40):

| effect | selected task | V8 k16 |
|---|---|---|
| selection | .197 | .147 (shrinks off the selected setting; seed 3 is near zero) |
| laws | .213 | .263 (grows) |

## Reading

Both capability effects generalise to a harder, unselected variant of the same task.

The law effect is the more robust one. Solvers built without collision-generated laws mostly
fail to generalise (.42 pooled, .33-.35 on seeds 2-3), while law-built solvers generalise at
.60-.64. The generated k-ary laws yield store/release implementations that survive a longer
delay and a larger alphabet. The human-derived and mutation-edited rules that the no-law
ecology falls back on mostly do not.

The selection effect is real but partly specific to the selected setting.

This rests on 3 seeds and one held-out variant; no claim beyond this task family.

## Predictions

| id | prediction | outcome |
|---|---|---|
| X1 | gate | RIGHT |
| X2 | H-SEL-TRANSFER | RIGHT |
| X3 | H-LAW-TRANSFER | RIGHT |
| X4 | selection RD >= .197, p .35 | did not occur (.147), in line with the stated probability |
| X5 | task0 transfer rate >= .6 | .635, RIGHT |
