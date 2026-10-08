# THESEUS-35 verdict (prereg roles/Theseus/prereg/2026-10-08_distributed_replication/, d4245e870)

Fresh-seed run: PYTHONHASHSEED=0 python -m theseus.synth.run_v0 --tag v0_1s2_2026-10-08
--master-seed 20261009 --workers 4 (v0_1 configuration). Stages: python -m
theseus.synth.task_replicate --tag replicate_s2_2026-10-08 --ref v0_1s2_2026-10-08
(checkpointed; killed once at the 2 h limit during S3 and resumed). Arms D, R, P, B, C.

GATE: noop J .119 (<= .175); relay .972 / memcomp 1.000 (>= .30); redundant_relay degenerate
20/20; single_relay one-point 20/20. PASSES.

SECONDARY H-TASK-HARD (V 8, k 8, mean J over task seeds 0, 1; 100 per arm):
  D .807 (median 1.0) | R .606 (.798) | P .496 | B .510 | C .459
  D > pooled one-shot Mann-Whitney one-sided p 1.1e-12; D > R p 2.1e-5. REPLICATED.
  (The task advantage now holds in 31a, 31b and on a fresh master seed.)

PRIMARY H-DIST (share of the arm's capable knockout set that is DISTRIBUTED):
  D 7/40 | R 2/40 | one-shot 7/119 (P 2/40, B 4/40, C 1/39)
  D > R one-sided Fisher p .077; D > one-shot p .033. VERDICT: INDETERMINATE -- not
  replicated by the preregistered rule (needs both comparisons at p < .05).
Full carrier table (one-point / degenerate / distributed): D 24/9/7, R 36/2/2, P 31/7/2,
  B 31/5/4, C 34/4/1.
Descriptive across both seeds (not a test): distributed D 21/80 vs R 4/80; no single point of
failure D 16/40 here vs R 4/40 (33 found 24/40 vs 16/40).
Reading: the direction of 33's post-hoc pattern recurs on a fresh seed but at half the size
and below the preregistered bar against random; the robust result of this line is the TASK
advantage (D carries the cue better than one-shot and random), not its distributed form.

Predictions: R1 gate RIGHT; R2 H-DIST replicated WRONG; R3 H-TASK-HARD replicated RIGHT.
