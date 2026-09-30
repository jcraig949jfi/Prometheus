# HT-056d3ac561 / W4 -- implementation notes (written before any run)

Prompt: hecate/programs/_prompts/probe_impl_v2.md (sha256 2021ed66...185e).
Bound by roles/Hecate/prereg/2026-09-30_probe_round2/PREREG.md and
2026-09-29_probe_round1/PREREG.md. Read: W4, M14, M1, L3 only.

## Spec field -> code

| spec field | code |
|---|---|
| 20-dim linear system | `core.make_world`: x_{t+1} = A x_t + w, A = 0.9 I + 0.05 (T + T^T), Q = q I; z = x + b + v, R = r I (20 sensors, one per state) |
| T, relation kernel dim 8 | T = U diag(I_8, R(th_1..th_6)) U^T, U random orthogonal, th_i ~ U(pi/3, pi). Relation kernel = fixed space of T (dim 8): a bias there is invisible to the MR (M14 collusion) |
| mirror filters (M14) | filter A (steady-state KF) on z_A = x + b + v_A; filter B (same KF) on z_B = T x + b + v_B (same faulty sensors see the transformed input). A, Q, R commute with T so the MR "T xhatA = xhatB" holds exactly without faults |
| MR residual (M1) | r_t = T xhatA_t - xhatB_t (x cancels exactly: oracle-free) |
| 40-atom sensor-fault dictionary | D: 20x40 Gaussian, unit-norm columns; fault bias b = D f, f in R^40 |
| accumulated whitened residual y = P f + noise | ybar = mean_t r_t over 200 steps (simulated, batched over trials); whitened by W = Sigma^{-1/2}, Sigma = exact analytic covariance of ybar under noise; P = W Gbar (T - I) D computed exactly from the linear recursion (C_s coefficients). P is 20x40, rank 12, ker(P) dim 28 |
| Lasso recovery | sklearn Lasso(fit_intercept=False), alpha FIXED BY RULE (not tuned): alpha = max_j ||P_j|| * sqrt(2 ln(2*40)) / 20 (universal threshold for unit whitened noise) |
| min-norm LS (spec "control") | f_mn = pinv(P, rank 12) y |
| sparsity k in {1,2,3,6,10} | k atoms, uniform support, coefficients sign * U(1, 2) |
| trials 200 | 200 trials per k per seed |
| observable 1 | rel_err = ||f_hat - f|| / ||f|| |
| observable 2 (L3) | recovered kernel-energy fraction = <f_hat_ker, f_ker> / ||f_ker||^2, ker = ker(P) in coefficient space; also visibility ratio = ||f_row||^2/||f||^2 |
| null twin | per trial: draw the paired sparse f_s (same stream), draw g ~ N(0, I_40), rescale its ker(P) and row(P) parts separately to ||f_s,ker|| and ||f_s,row|| (same total energy, same kernel-energy fraction); recover by Lasso and min-norm |
| positive control (spec) | "faults entirely outside the kernel": f_pc = row(P)-projection of the paired sparse f_s, rescaled to ||f_s||; recover by Lasso and min-norm |
| cheat | null-twin data, but the Lasso observable is overwritten with f_hat = f (rel_err 0); min-norm computed honestly |

Noise (chosen a priori from design, not results): q = 0.1, r = 0.1, 200 steps.
Seeds 0..4; each seed builds its own (U, T, D) world. RNG streams keyed
(seed, arm-family, k) so treatment / null twin / positive control are paired
on the same sparse draw f_s.

## Ambiguities and chosen readings

1. "kernel_dim 8" = dim of the relation kernel in sensor space (fixed space
   of T). In fault-coefficient space ker(P) is 40 - 12 = 28. "Kernel-energy
   fraction" (null twin matching, L3) uses ker(P) in coefficient space.
2. "For k <= 3 over 200 trials": each k in {1,2,3} separately, 200 trials,
   per seed. An arm meets the criterion iff every k <= 3 meets it in every
   one of the 5 seeds. Pooled rates are also reported.
3. Full success criterion for an arm X = (Lasso err <= 0.20 in >= 80%) AND
   (min-norm err >= 0.50 in >= 80%) on X's trials AND (null-twin Lasso
   err <= 0.20 in <= 20%) on the null-twin trials of the same seed and k.
   For TREATMENT, the Lasso clause comes from TREATMENT and the min-norm
   clause from CONTROL (same trials).
   null_twin_meets_success = null twin's own two arm clauses met (the
   third clause is about the null twin itself).
4. Failure criterion (phase 2): pooled-over-seeds Lasso success rate < 50%
   at any k <= 3, OR |null-twin Lasso success - treatment Lasso success|
   <= 15 pp at any k <= 3.
5. Cheat detected iff the full criterion evaluates true on cheat rows.

## Predicted pilot problem, declared in advance

The spec's positive control ("both methods should recover") CANNOT meet
the spec's success criterion: a fault in row(P) is recovered by min-norm to
noise level, so the clause "min-norm err >= 0.50 in >= 80%" fails by
construction. Attempt 1 runs it exactly as specified anyway.

Pre-declared repair (used only if attempt 1 fails; thresholds unchanged):
positive control := ORACLE-SUPPORT least squares on the paired sparse
faults f_s (LS restricted to the true support: a sparse prior that has the
effect by design), with min-norm on the same trials. This is a control
repair, not a treatment: no Lasso on sparse faults is run.

## Stupid explanations (spec)

- projection rank high enough that no recovery is needed: rank(P) = 12 < 40,
  visibility ratio reported per trial.
- Lasso lambda tuned on the test trials: alpha fixed by formula above,
  written before any run, recorded in rows.
- incoherent dictionary makes any method work: mutual coherence of D and of
  P's columns recorded; NOT varied in this run (cannot be ruled out here).

## Pilot attempt 1 (spec_rowspace) -- FAILED, as predicted above

positive_meets_success = false: min-norm error median ~0.02 on row(P)
faults (min-norm clause needs >= 0.50), and Lasso error ~0.9-1.5 on these
dense-in-coefficient faults. cheat_detected = true; null_twin_meets_success
= false (NT Lasso success 0%). Instrument checks: simulated mean residual
matches P f to ~0.2% relative; whitened noise covariance diag ~1.0.
Saved as PILOT_attempt1.json; rows attempt=1 kept in pilot_rows.jsonl.

## Repair (the one allowed; declared before attempt 1 ran)

positive control := oracle-support LS on the paired sparse faults f_s, with
min-norm on the same trials (pc_mode = oracle_support). Nothing else
changed: same thresholds, noise, alpha rule, seeds, worlds, null twin, cheat.

## Pilot attempt 2 (oracle_support) -- PASSED

## Phase 2 (world.py, evaluate.py) -- outcome NULL

Treatment Lasso success (err <= 0.20), pooled over 5 seeds: k=1 0.975,
k=2 0.876, k=3 0.618 (below 0.80 in all 5 seeds). Control min-norm err
>= 0.50 in 100% at every k (median 0.84 = sqrt of kernel-energy fraction).
Null twin Lasso success 0%. No failure-criterion clause was met: Lasso
success is >= 50% at every k <= 3, and the gap to the null twin is > 15 pp.
The class is NULL because the k=3 cells fail reading 2 (every k <= 3).
Reading sensitivity (reported, not applied): if the success rate is
pooled over k in {1,2,3}, it is 0.823 >= 0.80 and the class would be
SIGNAL. Reading 2 was fixed in this file before any run.
Core-minutes total: 0.465.
