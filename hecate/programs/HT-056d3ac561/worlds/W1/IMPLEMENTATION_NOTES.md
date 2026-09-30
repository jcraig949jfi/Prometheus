# HT-056d3ac561 / W1 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v1.md (sha256 cf4bd374...a2).
Bound by roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.

## World (substrate "causal toy", linear-Gaussian)

True system: x_{t+1} = A x_t + w_t, y_t = C x_t + v_t, t = 0..499 (size.steps = 500),
state_dim 4 (size.state_dim).

Fixed parameters (chosen from the spec's words, not from results):
- A: one fixed stable 4x4 matrix ("a stable 4x4 A"): M = normal(4,4) from
  numpy default_rng(20260929), A = 0.9 * M / spectral_radius(M). Spectral
  radius 0.9 = stable with a memory long enough for the stride relation to
  matter; the value is not tuned.
- C = I4 (spec names no observation model; full-state observation is the
  simplest reading and keeps all 16 entries of A identifiable).
- Q = I4, R = I4 (spec names no noise levels; unit, equal noise is the
  neutral choice).
- x_0 ~ N(0, Sigma_true) with Sigma_true the stationary covariance of A.
- Filter init: x_hat = 0, P_0 = stationary covariance of the filter's own
  model A' (if A' is not stable, P_0 = 10 I).

## Spec field -> code

- hypothesis / mechanism (M8): `run_filters` runs a Kalman filter with model
  A' at stride 1 on y_0..y_499 and a Kalman filter with model A'^2,
  Q2 = A' Q A'^T + Q, at stride 2 on y_0, y_2, ..., y_498. At each even t the
  disagreement is d_t = xhat1_t - xhat2_t (both filtered, i.e. posterior at t).
  Normalization ("by its predicted covariance"): under the filter's model,
  xhat2 is the conditional mean given a subset of the data used by xhat1, so
  by orthogonality Cov(d_t) = P2_t - P1_t exactly (model-predicted). The
  normalized disagreement is D_t = d_t^T (P2_t - P1_t)^{-1} d_t, expected
  value 4 under a matched model. Observable D = mean of D_t over even
  t in [50, 498] (burn-in 50 steps = 10% of the run, fixed a priori; at t=0
  both filters are identical so P2-P1 = 0).
- NIS baseline (lens L1): stride-1 innovations e_t, S_t; NIS = mean over
  t in [50, 499] of e_t^T S_t^{-1} e_t.
- Lasso (M8 sparse attribution): AMBIGUITY. "Lasso of mean disagreement on
  per-entry sensitivity vectors". A literal time-mean of the 4-vector d_t is
  ~0 for a zero-mean stationary process and gives 4 equations for 16
  unknowns. Reading chosen: the response is the stacked whitened disagreement
  series z = [(P2_t-P1_t)^{-1/2} d_t] over the evaluated even t (length
  4 x 225 = 900) -- i.e. the disagreement whose conditional mean is
  model-error-driven -- and the 16 regressors are the per-entry sensitivity
  vectors dz/dA'_ij computed by central finite differences (eps = 1e-5) on
  the same data, rerunning both filters with A' +/- eps E_ij (A'^2 and Q2
  recomputed). Lasso: sklearn Lasso(fit_intercept=False), alpha =
  0.1 * alpha_max where alpha_max = max|X^T z| / n (a fixed data-scaled rule,
  not tuned), max_iter 20000. Top-1 entry = argmax |coef|; if all coefs are
  0, argmax |X^T z|. As a declared secondary diagnostic only (not used in any
  criterion) the literal reading is also recorded: Lasso of the time-mean
  4-vector of z on the time-mean 4-vectors of the sensitivities, same alpha
  rule.
- intervention: filter model A' = A + delta * E_ij, true system untouched.
  AMBIGUITY: sign of delta not stated; reading: +delta. Entry (i,j) is drawn
  uniformly from the 16 per mismatched seed (so chance top-1 = 1/16 = 0.0625,
  matching the spec). delta in {0.05, 0.1, 0.2}; the criteria use delta = 0.1
  only; 0.05 and 0.2 are reported as secondary.
- control: matched model, delta = 0, A' = A.
- positive_control: oracle detector = true-state RMSE of the stride-1
  filtered estimate over t in [50, 499] (uses hidden truth, lens L3 style);
  AUC mismatched(delta=0.1) vs matched.
- null_twin: same runs; the stride-2 estimate at t is compared with the
  stride-1 estimate at t' = pi(t), pi a random permutation (seeded) of the
  evaluated even times, normalized by the same (P2_t - P1_t)^{-1}; D_null =
  mean. Equal marginals, relation destroyed.
- observable: D, NIS, top-1 entry per run (all written to rows).
- success_criterion (as applied, threshold unchanged): 50 mismatched seeds
  at delta 0.1 vs 50 matched seeds: AUC(D) >= 0.80 AND AUC(D) >= AUC(NIS) +
  0.05 AND localization accuracy (top-1 == true entry, over the 50 mismatched
  seeds) >= 0.60 AND AUC(D_null) <= 0.60. AUC = P(stat_mismatched >
  stat_matched) + 0.5 P(tie) (one-sided, larger = flag mismatch), via
  sklearn roc_auc_score.
- failure_criterion: AUC(D) < 0.70 or AUC(D) <= AUC(NIS) or loc < 0.25 or
  AUC(D_null) > 0.60.

## Seeds

Matched (CONTROL) seeds 0..49; mismatched seeds 1000..1049 (same seeds and
same true entry for each delta, so deltas differ only in delta). Total runs
50 + 3 x 50 = 200 (spec size.seeds = 100 = 50 + 50 at the criterion delta).
Null-twin permutation rng: default_rng(seed + 777).

## Arms (one row per arm x seed [x delta])

- TREATMENT: mismatched runs; fields D, NIS, top1, true entry, delta.
- CONTROL: matched runs; D, NIS, top1 (no true entry).
- NULL_TWIN: D_null for every run (matched and mismatched).
- POSITIVE_CONTROL: oracle RMSE for every run.
- CHEAT: for every run, D_cheat = D + 100 if mismatched else D, and
  top1_cheat = true entry: success injected straight into the observable.

## Decisions in evaluate.py (a priori)

- positive_control_detected: oracle AUC at delta 0.1 >= 0.80 (the success
  detection threshold; spec says "expected near 1").
- cheat_detected: the full success criterion is met when D and top1 are
  replaced by the CHEAT values (NIS and D_null from the same runs).
- null_twin_meets_success: the detection part of the success criterion holds
  with D_null in place of D: AUC(D_null) >= 0.80 AND AUC(D_null) >=
  AUC(NIS) + 0.05 (the null twin has no localization of its own).
- Outcome order (PREREG): INSTRUMENT_FAIL if PC or CHEAT not detected;
  else CONFOUNDED if null_twin_meets_success; else SIGNAL if success met;
  else NULL.
- Stupid explanations checked: (1) AUC(D) vs AUC(NIS) and null twin;
  (2) matched-run mean D and mean NIS vs 4 (normalization sanity; anomaly if
  outside [3.5, 4.5]); (3) data-free baseline: top-1 = argmax sensitivity
  column norm, and the top-1 distribution on matched runs.

Compute: time.process_time per run in rows; budget 10 core-minutes; single
process.

## Addendum (still before any run)

- Sensitivity columns are whitened with the base model's W_t =
  (P2_t - P1_t)^{-1/2} (held fixed across the +/- eps reruns), so only the
  disagreement d_t is differentiated, not the normalizer.
- Filter gains are data-independent and are cached per model; the cache is
  cleared whenever the (entry, delta) group changes.

## Post-run record (attempt 1; written after the run)

- world.py ran once (46.6 CPU s), with no crash and no rerun. evaluate.py was
  rerun twice with no world rerun. The first edit only added anomaly strings:
  an oracle AUC below 0.60 at any delta, and a Lasso top-1 accuracy below the
  data-free baseline. No criterion, threshold or parameter changed.
- Outcome INSTRUMENT_FAIL. The positive control (oracle true-state RMSE)
  had AUC 0.490 at delta=0.1 (0.476 at 0.05, 0.558 at 0.2), which is chance.
  The CHEAT arm was detected (AUC 1.0, loc 1.0).
- Instrument repair: NONE made (the prompt allows one but does not require
  it). Diagnosis: the evaluator is not blind, because CHEAT is seen. What
  happens is that with Q = R = C = I and T = 500, a +0.1 entry error in the
  filter model changes the true-state error by much less than its
  seed-to-seed spread, so even ground truth cannot separate the arms between
  seeds. Only two repairs would make the positive control fire:
  (a) change the world (Q, R, T, spectral radius), or (b) switch to a
  paired oracle that also runs the correct model on the same data. Both
  would be chosen after seeing TREATMENT (AUC(D) = 0.493), and (a) is
  parameter tuning, which the faithfulness guard forbids. Neither is a
  repair of a broken evaluator. So the INSTRUMENT_FAIL stands as recorded.
  This fits "nothing could have fired": the TREATMENT reading (AUC(D) 0.493,
  AUC(NIS) 0.490, loc 0.00, null-twin AUC 0.417) is NOT interpreted.
- Unexpected in the controls: on matched runs the Lasso top-1 was entry 13
  in 49 of 50 runs. On mismatched runs the localization accuracy was 0.00,
  below the data-free sensitivity-norm baseline of 0.16. This fits the spec's
  stupid explanation 3 (localization driven by the sensitivity structure, not
  the data) at this world's signal level. Matched mean D = 4.03 (expected 4),
  so the normalization is right (stupid explanation 2 is addressed).
