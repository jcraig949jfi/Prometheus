# HT-79e904e13a / W4 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v1.md (sha256 cf4bd374...a2).
Bound by roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Spec read: program.json experiment W4, mechanism M15, lens L5. Nothing else.

## Spec field -> code

- hypothesis: backtracking counterfactuals lose identifiability at a rate
  set by net phase-space contraction; forward ones do not. Tested by the
  TREATMENT arm (backward posterior entropy growth rate vs measured net
  contraction across 8 dissipation levels) plus CONTROL (forward spread).
- mechanism (M15): three coupled Ricker-type maps with a dissipation
  parameter d. Implemented as
      x_i' = (1-d) * x_i * exp(rho_i * (1 - x_i - alpha * sum_{j!=i} x_j)) + d
  i.e. a Ricker community update relaxed toward carrying capacity 1 with
  weight d. The (1-d) factor multiplies every Jacobian row, so d adds
  about 3*log(1/(1-d)) nats/step of contraction directly (plus whatever
  the change of dynamics adds); it keeps all states strictly positive.
- intervention: d over 8 levels; for each (level, seed) a reference
  initial grid point x0 is mapped T steps; the final state is perturbed
  by delta in a random unit direction; the backward query collects every
  initial grid point whose T-step image lies within radius r of the
  perturbed final state.
- observable (L5): backward posterior entropy H(T) for T = 1..30. With a
  uniform prior over the grid and a hard radius-r likelihood, the
  posterior is uniform over the N_match(T) matched grid points, so
  H(T) = log N_match(T) + log(cell volume) (nats). Growth rate = OLS
  slope of H(T) on T over T = 1..30 (the additive cell-volume constant
  does not affect the slope). Computed by evaluate.py from the stored
  series.
- measured net contraction rate: -(sum of Lyapunov exponents) =
  -mean log|det J| along an orbit on the attractor (500 transient,
  4000 steps, per seed, seed-dependent start in (0.2, 2)^3). lambda_max
  from the same orbit by QR re-orthonormalisation.
- control: forward query on the same map/level/seed: 64 initial states
  x0 + delta*u_k (random unit u_k) mapped forward; spread(T) = log RMS
  distance of the cloud from the reference trajectory; forward growth
  rate = OLS slope over T = 1..30. Reported; not part of the decision
  (the success criterion does not mention it).
- positive_control: linear contracting map x' = A x, A = 0.95 * R (R a
  seed-random rotation), singular values all 0.95, so
  -sum log sv = -3 log 0.95 = 0.15388 nats/step (known). Same backward
  estimator, same grid size, same relative r and delta. Detected iff the
  seed-mean fitted growth rate is within 10% of 0.15388.
- null_twin: volume-preserving 3-torus map of three sequential shears
      x1 += k sin(2 pi x2); x2 += k sin(2 pi x3); x3 += k sin(2 pi x1')  (mod 1)
  det J = 1 exactly, invertible. For each dissipation level k is chosen
  from a precomputed k-grid (0.02..1.5, 150 values) to minimise
  |lambda_max_twin(k) - lambda_max_treatment(level mean)|; this tuning is
  mandated by the spec ("tuned to the same lambda_max (+/-10%)") and uses
  only lambda_max, never the entropy observable. The achieved match is
  recorded per level and checked against +/-10%.
- CHEAT: rows with entropy series constructed as H(T) = H0 + C_level*T
  (C_level = the treatment level's measured contraction, per seed) and a
  flat twin series; bypasses every map. Detected iff the full success
  criterion evaluates true on the CHEAT rows.
- success_criterion, as applied: Spearman(level-mean backward growth rate,
  level-mean measured net contraction), n = 8 levels, 10 seeds each,
  >= 0.8, AND the null twin growth rate <= 0.1 nats/step at every level
  (max over levels of the seed-mean twin growth rate <= 0.1).
- failure_criterion, as applied: Spearman < 0.5, OR the twin growth rate
  within 50% of the treatment's at matched lambda_max, meaning
  |g_twin - g_treat| <= 0.5 * |g_treat| (level means) at a majority
  (>= 5 of 8) of levels.

## Ambiguities and the readings chosen

1. "Ricker-type with a dissipation parameter controlling net contraction":
   the relaxation form above (see mechanism). Chosen because it keeps the
   Ricker update and positivity while the parameter enters every Jacobian
   row; the net contraction is still MEASURED, not assumed.
2. rho = (3.3, 2.2, 1.8), alpha = 0.05, d in linspace(0, 0.21, 8).
   Reasoning (a priori, no pilot): species 1 at rho 3.3 is in the chaotic
   Ricker range so lambda_max > 0 is plausible over the range (the twin
   can only match a positive lambda_max, since a volume-preserving map
   has lambda_max >= 0); species 2 and 3 are in the period-2 / stable
   ranges so the baseline sum of exponents is near zero or negative
   ("dissipative community"), and d up to 0.21 adds up to ~0.7 nats/step.
   Weak coupling (0.05) keeps it a coupled community without driving
   extinction. If lambda_max <= 0 at some level, the twin match fails
   there and that is recorded, not repaired.
3. "100,000-point initial grid": regular 47^3 = 103,823 grid (smallest
   cube >= 100,000); per-seed sub-cell offset. Domains: treatment
   (0, 3]^3 (covers the Ricker range, max image ~3.03 for rho 3.3);
   positive control (-1, 1]^3; twin: unit 3-torus with periodic distance.
4. r and delta: r = side/30 in every arm (treatment 0.1, PC 0.0667, twin
   0.0333), giving ~15 grid points inside a radius-r ball at T = 0 in
   every arm; delta = r/2 so the reference initial point is always
   matched (posterior never empty). Single r only; r-scaling is NOT
   tested (see stupid explanations).
5. "entropy of their distribution": uniform posterior over matched grid
   points -> log count (see observable). A Gaussian-fit entropy is NOT
   used for decisions.
6. Growth rate "over T = 1..30": OLS slope over all 30 points.
7. Spearman "across 8 levels (10 seeds each)": on the 8 level means.
8. "null twin meets the success criterion": the twin's level-mean growth
   rate has Spearman >= 0.8 with the treatment's level-mean measured
   contraction (the twin is matched level-by-level in lambda_max, so this
   asks whether chaotic stretching alone reproduces the trend). The
   twin's own measured contraction is identically 0 and cannot carry a
   rank correlation.
9. Outcome mapping (PREREG), in code: controls not both detected ->
   INSTRUMENT_FAIL; else treatment meets success and twin meets success
   -> CONFOUNDED; else treatment meets success (and twin does not) ->
   SIGNAL; else NULL (treatment fails success, whether or not the failure
   criterion is also met; the flags are recorded).
10. Positive control reference point: a grid point with all |x| < 0.3,
   so the preimage ellipsoid (axis growth 0.95^-30 = 4.65 -> 0.31) stays
   inside the domain; chosen from geometry, not results.

## Seeds and sizes

Seeds 0..9 for every arm (10 >= 5; spec says 10 seeds). rng per row =
default_rng([arm_code, level, seed]). T = 1..30. 8 levels. Forward cloud
K = 64. Lyapunov orbit 500 + 4000 steps. Twin k-grid 150 values x 8
starts x 3000 steps. BLAS threads pinned to 1; CPU time measured with
process_time and written cumulatively into every row.

## Budget

Estimated well under 1 core-minute (vectorised numpy over the grid).
Hard limit 10 core-minutes.

## Attempt log (appended after runs)

- Attempt 1 (55.6 CPU s): completed, but 3 of 80 CONTROL rows (level/seed
  1/8, 2/8, 5/2) had inf/NaN forward spreads. Cause (bug): the reference
  initial point had a coordinate below delta (0.017, 0.0078, 0.00023), so
  some x0 + delta*u started at a negative population; the Ricker map
  diverges from negative states. Diagnosed from CONTROL rows only, before
  any TREATMENT statistic was computed or viewed. Fix: resample forward
  perturbation directions that would start at a coordinate <= 0
  (rejection sampling; CONTROL arm only; no parameter changed). Attempt 1
  rows kept as rows_attempt1_control_bug.jsonl. All arms rerun (seeded,
  so non-CONTROL rows are reproduced identically).
- Attempt 2 (59.3 CPU s; total 1.91 core-minutes): no NaN; non-CONTROL
  rows byte-identical to attempt 1. evaluate.py -> NULL. Unanticipated:
  the a-priori parameter choice left lambda_max <= 0 at levels 2-7
  (d >= 0.06), so the twin (lambda_max >= 0 by construction) matched only
  at levels 0-1. Recorded as anomalies, not repaired (no tuning after a
  treatment result).
