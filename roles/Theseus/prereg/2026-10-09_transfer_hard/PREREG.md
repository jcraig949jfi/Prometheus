# THESEUS-43 preregistration -- do the selection and law effects transfer to a held-out harder task?

Currency: 2026-10-09. Committed before any variant scoring of the 9 runs below. The only
prior look is the exploratory headroom pilot (theseus/runs/task_headroom_2026-10-09/,
committed with this prereg). It scored the gate controls and 40 children each of
v0_2t0_s3 and v0_2tr_s3. Those 80 children are a subset of the samples scored here; this
is disclosed.
Code: theseus/synth/transfer_eval.py (new), task_comp.py, pooled.py, sel_eval.py; hashes in
CODE_HASHES.txt.

## Why

Every arm solves the selected task (V4 k8, sensor readout) at 59-91%. Ceiling compresses
every contrast, and the selected task is the one selection saw. A held-out, harder variant
of the same composition-necessary task does two things:
- it tests whether the capability that selection and generated laws produce generalises
  beyond the selected setting;
- it measures the contrasts away from the ceiling.

## Variant and gate

Cue recall at V 8, k 16, sensor-only readout, task seed 0, 400/400 episodes; chance is .125.

Pilot gate values:

| control | J |
|---|---|
| 1-part | .107-.128 |
| store+release pairs (all three) | 1.0 |
| k 24 (excluded) | breaks two pairs (.50 and .68) |

GATE: every 1-part control <= .25 and every 2-part control >= .80, re-scored inside.

## Runs (no new ecologies)

The same 100-child samples as the original evals (sel_eval.sample):

| seed | task0 | rep | no-law |
|---|---|---|---|
| 1 | v0_2t0_2026-10-08 | v0_2tr_2026-10-08 | v0_2t0nl_2026-10-08 |
| 2 | v0_2t0_s2_2026-10-08 | v0_2tr_s2_2026-10-08 | v0_2t0nl_s2_2026-10-08 |
| 3 | v0_2t0_s3_2026-10-09 | v0_2tr_s3_2026-10-09 | v0_2t0nl_s3_2026-10-09 |

Command: python -m theseus.synth.transfer_eval --tag transfer_hard_2026-10-09 --runs <all 9>
--workers 4.
Pooled: python -m theseus.synth.pooled over the 3 seed strata, with evaldir =
theseus/runs/transfer_hard_2026-10-09.

## Decision rules (SOLVER = J >= .6 at V 8 k 16)

H-SEL-TRANSFER (task0 > rep) and H-LAW-TRANSFER (task0 > no-law): each is SUPPORTED iff the
one-sided CMH p < .01 over the 3 strata AND the RD_MH 95% CI lower bound > 0. NOT
SUPPORTED iff RD_MH <= 0; else INDETERMINATE.

Descriptive:
- per-seed RDs with CIs;
- the transfer rate: the share of selected-task solvers that also solve the variant;
- the RD at the variant beside the selected-task RD_MH (.197 selection, .213 laws).

## Predictions

| id | prediction | p |
|---|---|---|
| X1 | the gate passes | 0.9 |
| X2 | H-SEL-TRANSFER SUPPORTED | 0.6 |
| X3 | H-LAW-TRANSFER SUPPORTED | 0.65 |
| X4 | the variant RD_MH for selection >= .197 (no shrink off the selected task) | 0.35 |
| X5 | transfer rate, task0 arm pooled >= .6 | 0.6 |

## Compute

900 genomes x ~4 s at V8 k16 = ~1 CPU-hour (MWO R2 cap 16).
