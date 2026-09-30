# HT-55162c0ac0 / W3 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v1.md
(sha256 cf4bd374bce1b817a12d3607063278183ce0a8b7c4a7b771061dc8ce133bcea2).
Bound by roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Sources read: PREREG, program.json experiment W3, mechanisms M4 and M2,
lenses L3 and L2. Nothing else.

## Spec field -> code

- **hypothesis / mechanism (M4, M2)**: `world.py::step_logistic`. Globally
  coupled logistic maps, N = 100, eps = 0.1:
  `x_i' = (1 - eps) f_a(x_i) + eps * mean_j f_a(x_j) + b_i`, with
  `f_a(x) = a x (1 - x)`.
- **forcing patterns b**: a pattern with k levels is a balanced random
  assignment of the N sites to k labels (`label_i = perm(arange(N) % k)`),
  seeded. Level values are `b_i = 0.02 * label_i / (k - 1)`, i.e. evenly
  spaced in [0, 0.02] ("amplitude 0.02" read as the peak-to-peak span of
  the levels). Choice reason: b >= 0 and max f_a = a/4 <= 0.975 keep
  x in [0, 1) with no clipping, so the map is exactly the one written.
  The three patterns in a seed (k = 2, 4, 8) are drawn independently.
- **modulator a ramps with k**: during the forced block for k = 2, 4, 8
  the modulator is 3.7, 3.8, 3.9 respectively (held constant within the
  500-step block; stepped between blocks as the intervention states).
- **intervention (TREATMENT arm)**: two orders per seed, same initial
  state x0 ~ U(0,1)^N and same patterns:
  easy->hard = blocks (k2, a3.7), (k4, a3.8), (k8, a3.9);
  hard->easy = (k8, a3.9), (k4, a3.8), (k2, a3.7);
  500 forced steps per block, then 1000 unforced steps (b = 0).
  AMBIGUITY: a during the unforced phase is not stated. Reading chosen:
  the modulator stays at its last value (3.9 for easy->hard, 3.7 for
  hard->easy), because nothing in the spec resets it. This is a real
  confound (the two orders are read out at different a) and is recorded
  as such; the fixed-a CONTROL arm is the arm that removes it.
- **control (CONTROL arm)**: identical to TREATMENT with a = 3.8 in every
  block and in the unforced phase.
- **positive_control (POSITIVE_CONTROL arm)**: one pattern k = 2, forced
  500 steps at a = 3.7, then 1000 unforced steps at a = 3.7; observable =
  ARI(final partition, that pattern). DETECTED iff the mean ARI over the
  30 seeds >= 0.8 (the threshold the spec gives).
- **null_twin (NULL_TWIN arm)**: f_a replaced by the contracting affine
  map `g_a(x) = mu_a + rho (x - mu_a) + s_a xi`, xi ~ N(0,1) iid per site
  per step, rho = 0.5, inside the same coupling and forcing. AMBIGUITY:
  a deterministic contracting affine map has zero temporal variance at
  its fixed point, so "per-site variance matches the chaotic run" can
  only be met with an additive noise term; I read the spec that way.
  rho = 0.5 is a fixed a-priori choice (clearly contracting, not near 1).
  mu_a, sigma_a^2 = mean over sites of the per-site temporal mean and
  variance of an unforced coupled logistic run at the same a (1200
  steps, first 200 discarded, same seed), calibrated per seed per a in
  {3.7, 3.8, 3.9}. s_a is set so the site-deviation variance of the
  coupled linear system matches: sigma^2 = (1-eps)^2 s^2 / (1 - (1-eps)^2 rho^2).
  The realized per-site variance (last 500 unforced steps) is written to
  the rows so the match can be checked. Same orders, same a schedule,
  same patterns as TREATMENT. Monostable by construction.
- **CHEAT arm**: runs the real hard->easy order; for easy->hard the
  final partition is replaced, pattern by pattern, with that pattern's
  own partition before the ARI is computed (so retention(easy->hard) = 1
  is injected into the observable through the same ARI code, bypassing
  the dynamics). DETECTED iff the CHEAT rows pass the difference +
  Wilcoxon part of the success criterion.
- **observable**: final cluster partition = connected components of the
  graph linking sites i, j when max over the last 20 unforced steps of
  |x_i - x_j| < 1e-5 (single linkage; synchronized clusters in a GCM are
  identical to float precision, so 1e-5 is loose for true clusters and
  tight versus chaotic divergence). retention = mean over the three
  patterns of sklearn adjusted_rand_score(final partition, pattern
  labels). Number of clusters is recorded (stupid explanation 2).
- **success_criterion** as applied (evaluate.py):
  (S1) mean over 30 seeds of d = retention(easy->hard) - retention(hard->easy) >= 0.15;
  (S2) Wilcoxon signed-rank on the 30 paired d, one-sided (greater),
       p < 0.01 (one-sided because the hypothesis is directional);
       if all d == 0, p = 1;
  (S3) mean NULL_TWIN d < 0.05;
  (S4) L3 loop area > 0 across a in [3.7, 3.9] -- see below.
  Success iff S1 and S2 and S3 and S4.
- **failure_criterion**: mean d < 0.05, or mean NULL_TWIN d >= 0.1.
  Reported; per the PREREG, NULL is "treatment fails the criterion (or
  meets failure_criterion)", so any non-success with detected controls
  and non-confounded null twin is NULL.
- **null twin meets success** (for CONFOUNDED): NULL_TWIN passes S1 and
  S2 on its own paired d.
- **L3 loop area** (LOOP arm, unforced treatment map, 30 seeds): sweep a
  over 21 evenly spaced values 3.7 -> 3.9, then 3.9 -> 3.7 (state carried
  over), 200 steps per a value, then read q(a) = number of clusters / N
  (L2 "number of attractors" proxy, same clustering rule). Per-seed signed
  loop area A = trapezoid integral over a of (q_up(a) - q_down(a)).
  AMBIGUITY: any chaotic run gives a nonzero |A|, so "> 0" is read with
  L3's null expectation ("zero loop area within seed noise"): S4 holds iff
  a two-sided Wilcoxon signed-rank test of the 30 per-seed A against 0
  gives p < 0.01 (two-sided because the loop direction is not specified).
- **stupid explanations**: (1) recency -- addressed by the NULL_TWIN arm
  (recency without hysteresis) and by recording per-pattern ARIs, so it
  can be seen whether the last-presented pattern dominates; (2) ARI
  biased by cluster count -- ARI is chance-adjusted; cluster counts are
  recorded per row; (3) transients -- a TRANSIENT_CHECK arm reruns the
  treatment with 5000 unforced steps and the difference is reported.

## Parameters (all fixed here, before any run)

N = 100; eps = 0.1; amplitude 0.02; forced steps 500/block; unforced
1000 (5000 in TRANSIENT_CHECK); seeds 0..29 (30, as the spec says);
clustering tolerance 1e-5 over last 20 steps; rho = 0.5; calibration
1200 steps / 200 burn-in; loop sweep 21 values x 200 steps; alpha 0.01.
Per-seed RNG: numpy default_rng(seed) for x0 and patterns; the null-twin
noise uses default_rng(10_000 + seed). All arms of a seed share x0 and
patterns.

## Feasibility

About 2500 vectorized steps of a 100-vector per run, ~10 runs per seed
plus the sweep: well under 1 CPU core-minute. Buildable without
inventing the mechanism; the only invented pieces are the noise term in
the null twin (forced by the variance-matching requirement) and the
clustering tolerance, both stated above.

## Post-run record (appended after attempt 1; nothing above was changed)

Attempt 1 ran without crash (12.6 CPU s). evaluate.py: INSTRUMENT_FAIL --
POSITIVE_CONTROL mean ARI 0.024 (< 0.8; ~3.7 final clusters), CHEAT
detected. The one permitted instrument repair was NOT used: the readout
(clustering + ARI) behaves as specified (CHEAT detected; cluster counts
are plausible: ~100 in the turbulent a=3.8/3.9 runs, ~4 at a=3.7). The
failure is in the specified dynamics (weak forcing does not imprint at
a=3.7 with eps=0.1), and changing amplitude, eps or step counts would be
tuning the mechanism after a treatment result, which the rules forbid.
