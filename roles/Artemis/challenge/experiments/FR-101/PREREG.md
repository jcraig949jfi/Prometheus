# PREREG A-RUN FR-101 (reduced): does particle2 beat generic rules under the same encoding?

Artemis, 2026-09-28, committed BEFORE execution. Operator challenge s8
conditions: inputs committed (C3 @ cb9135104, herakles @ 5a0458fd6,
c3_sfe09 @ fe3c1647c); no GPU; confirmation sets already reused across
three campaigns (no hidden holdout); no seat holds a prereg on this (no
commits to herakles/ or archaeon/campaign3 on any ref since 09-17);
runtime minutes. Scored A-RUN in the prospective test. Courtesy note to
Archaeon and Herakles at report time.

Question: is particle2's delayed-recall margin (d=2, 31 cells, port 0,
Bernoulli-0.5 reset, horizon 8, ridge readout) produced by its evolved
dynamics, or would a generic rule table under the identical encoding
produce it?

Method (on a `git archive` copy; GIT_* unset):
- Script copies (does not import) ClampedCA / feats from
  archaeon/campaign3/c3_sfe09.py:45-71 @ fe3c1647c (importing c3_sfe09
  pulls proteus and the SFE client); uses herakles/ca_stream (core.py,
  reset_v2.py) and herakles/evca as committed.
- Seeds: C3-SFE-09 seeds 1..8, CAMPAIGN_SEED 20260920
  (archaeon/campaign3/c3base.py:18), the same train/confirmation
  partitions as base_acc.
- Rule set R: particle2; GKL; the 6 C2 named rules; identity; shift by
  1, 2, 3; and 64 random radius-3 rule tables drawn with
  numpy.random.default_rng(20260928) (uniform over the 2^128 tables).
  Metric per rule: mean confirmation accuracy over the 8 seeds.

Gate (harness validity, checked first): recomputed particle2 per-seed
accuracies match archaeon/campaign3/C3-SFE-09/rows.json within 0.01 in
>= 7 of 8 seeds. If not -> STOP; report a harness mismatch; no verdict.

Decision (fixed now):
- M(particle2) > 95th percentile of the 64 random rules' means AND >
  max over {identity, shift1, shift2, shift3} -> REOPEN as a narrow
  claim: evolved dynamics add beyond generic transport at d=2.
- M(particle2) <= 95th percentile of random rules -> CLOSE: the encoding
  and geometry explain the margin; the CA delayed-recall line closes and
  C4-10's retirement stands.
- M(particle2) > random 95th percentile but <= some transport rule ->
  CLOSE with note: plain transport explains it.
Diagnostic only (no decision): re-run the C2 reset-leakage probe with a
random (not index-order) split, so the record stops citing "below
chance" as a null.

Caps: 30 CPU-minutes expected; kill at 60 and report partial. Outputs:
rows.json (rule x seed accuracy), RESULT.md (gate, table, decision),
the script, all under this directory.
