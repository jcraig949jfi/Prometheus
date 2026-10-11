# THESEUS-36 preregistration -- a composition-NECESSARY task: does task selection build it?

Currency: 2026-10-08. Committed before the task0-selected run.

## Why

31c (a8c236231): selection on cue recall raised capability but not compositions -- the task
is solvable by a 1-part relay. 36 uses a variant no 1-part mechanism can solve: the readout
sees ONLY the sensor channel after the query step (task_system readout="ch0", V 4, k 8); the
sensor is overwritten every step, so the cue must be stored elsewhere and released back at
query time. Validation before this prereg (controls only, theseus/runs/comp_task_2026-10-08/
CONTROLS.json): every 1-part control at chance (k 8: .29-.31, chance .25); every
store+release 2-part control 1.0 (relay out+back, remember+inject, remember+recall).
Hence every SOLVER is a functional composition of parts each worth nothing alone for this task.

## Design

TASK0-SEL: PYTHONHASHSEED=0 python -m theseus.synth.run_v0 --tag v0_2t0_2026-10-08
--quality task0 --g0-readers --cond-ops --aligned-binding --ecology-only --elite-grids pca
--pop-cap 300 --dark-protect-gens 3 --elite-protect-k 150 --seed-select 1.5 --workers 4
CONTROL: the 31c TASKSEL-REP run v0_2tr_2026-10-08 (identical config except --quality rep;
code paths it uses are unchanged since it ran -- verified default-preserving).
Eval: python -m theseus.synth.task_comp --tag comp_task_2026-10-08 --a v0_2t0_2026-10-08
--b v0_2tr_2026-10-08 (controls re-run inside as the gate; 100 viable D per run; solver =
J >= .6; single-rule knockouts on solvers).

## Decision rule

GATE (re-run inside): every 1p control J <= .40 AND every 2p control J >= .80.
PRIMARY H-SEL-SOLVE: solver share among D, TASK0-SEL > CONTROL, one-sided Fisher p < .05 ->
SUPPORTED (task selection makes recursion build a composition-necessary mechanism);
TASK0-SEL share <= CONTROL share -> NOT SUPPORTED; else INDETERMINATE.
Descriptive: solver essential-rule counts and essential ops (which parts the solvers use);
accounting row per Hestia #1896 (organism = the program; developmental = none; search =
ecology + task selection; certifier = the frozen task + controls).

## Predictions

V1 gate passes.                                         p = 0.85
V2 H-SEL-SOLVE SUPPORTED.                               p = 0.5
V3 CONTROL run has <= 5% solvers.                       p = 0.6

Compute: one ecology-only run with task0 J per child (~45 min) + eval (~30-60 min).
