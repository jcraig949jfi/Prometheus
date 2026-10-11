# THESEUS-31c preregistration -- does selection on a task make recursion assemble compositions?

Currency: 2026-10-08. Committed before either run.

## Why

30c-34: with inert-alone parts available (30e) and aligned (34), writer/reader compositions
appear at low, roughly co-occurrence rates in every arm; recursion does not enrich them.
Nothing selects for them (Hestia #1897: REWARD). The cue-recall task rewards memory, and a
writer + inject pair solves it (memcomp control J 1.0). If selection on the task makes the
recursive ecology assemble such pairs, deep descendants should contain more compositions
than under the same ecology selected on reproducibility.

## Design (two ecology-only runs, identical except the elite quality)

Common: PYTHONHASHSEED=0, master seed 20260930, --g0-readers --cond-ops --aligned-binding
--ecology-only --elite-grids pca --pop-cap 300 --dark-protect-gens 3 --elite-protect-k 150
--seed-select 1.5 --workers 4.
  TASKSEL-J:   --quality task  (quality = cue-recall J at V 4, k 4, 200/200 episodes)
               tag v0_2t_2026-10-08
  TASKSEL-REP: --quality rep   tag v0_2tr_2026-10-08
Scans: composition_v3 --ref <tag> (gate inside; D/E/S/G arms only -- ecology-only runs have
no one-shot/random arms) and sel_eval (J at V 4, k 4, 400/400, 100 viable D per run).

## Decision rule

GATE as 30c (both scans).
MANIPULATION CHECK: D J under TASKSEL-J > TASKSEL-REP, one-sided Mann-Whitney p < .05;
else selection did not take and the composition result is descriptive only.
PRIMARY H-SEL-COMP: D composition share (v3, 120 viable D) TASKSEL-J > TASKSEL-REP,
one-sided Fisher p < .05 -> SUPPORTED; TASKSEL-J share <= TASKSEL-REP share -> NOT SUPPORTED;
else INDETERMINATE.
Accounting (Hestia #1896) filled for every found pair: organism (the pair) / developmental
(none) / search (ecology + task selection) / certifier (v3 detector).

## Predictions

U1 manipulation check passes.                     p = 0.8
U2 H-SEL-COMP SUPPORTED.                          p = 0.35
U3 TASKSEL-J D composition share >= 5%.           p = 0.3

Compute: two ecology-only runs (~35 min each incl. task J) + scans (~15 min each) + J eval.
