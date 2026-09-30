# HT-79e904e13a / W1 -- implementation notes (written before any code ran)

Bound by roles/Hecate/prereg/2026-09-30_probe_round2/PREREG.md (control-first
pilot) and roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md.
Prompt: hecate/programs/_prompts/probe_impl_v2.md (sha256 2021ed66...185e).
Spec source: program.json experiment W1 (mechanisms M3, M10; lenses L3, L7).

## Spec field -> code

| spec field | code |
|---|---|
| mechanism: J = logm(C(tau) C(0)^{-1})/tau; r_k = -J^{-1} e_k | common.estimate_J, common.predict_responses |
| tau = 1.0 time units | common.TAU = 1.0 (= 100 steps at dt 0.01) |
| size: 12 species, Euler-Maruyama dt=0.01, 200,000 observational steps | common.N_SP=12, DT=0.01, N_OBS=200_000 |
| 12 presses x 4 distances x 30 seeds | common.DISTANCES = (-0.5,-0.2,-0.05,-0.01); SEEDS = 0..29 |
| observable: median over presses of Spearman(pred, actual) at 4 distances | common.press_spearmans + common.arm_summary |
| positive_control: linear OU, known J, same size, median Spearman >= 0.95 | pilot.py arm POSITIVE_CONTROL (common.simulate_ou) |
| null_twin / control: independent random circular shift per species | common.circular_shift; pilot arm NULL_TWIN (on OU series); phase-2 arm CONTROL (on gLV series) |
| cheat (round-1 PREREG): success injected into the observable | pilot arm CHEAT |
| intervention: press = immigration +0.02 x* on species k, to new equilibrium, true response = mean abundance shift | phase 2 world.py (gLV); OU: exact analytic mean shift |
| success_criterion | common.success() |
| failure_criterion | common.failure() |
| leading eigenvalue real part set to each distance | OU: diagonal shift of J0; gLV (phase 2): bisection on one mortality parameter |

## Ambiguities and the readings chosen

A1 "Median Spearman at eigenvalue d": per seed, median over the 12 presses of
   the 12-entry Spearman rank correlation (signed responses); then the median
   of those 30 per-seed values. The Wilcoxon test is paired over seeds on the
   per-seed medians at -0.5 vs -0.01, one-sided (-0.5 greater), p < 0.01.
A2 "null-twin median Spearman <= 0.2": the null twin's median (A1) must be
   <= 0.2 at BOTH -0.5 and -0.2 (the distances where success is claimed).
A3 Positive control "must reach median Spearman >= 0.95": at BOTH -0.5 and
   -0.2 (the same distances the success level is claimed at). The other two
   distances are reported, not judged.
A4 Pilot "null twin does NOT meet the success criterion": the arm-level parts
   of the criterion applied to the null twin as if it were the treatment:
   level >= 0.8 at -0.5 and -0.2 AND decline >= 0.3 with Wilcoxon p < 0.01.
   (The "null twin <= 0.2" clause has no meaning for a twin of the twin.)
   Its medians and whether it is <= 0.2 are reported in stats.
A5 Which series the pilot null twin shifts: the POSITIVE_CONTROL OU series
   (so no gLV / treatment code exists in phase 1, and the twin is tested on
   a series where the effect exists by construction). In phase 2 the spec's
   own control (circular shift of the gLV series) is arm CONTROL, and it is
   the one that decides CONFOUNDED; the OU twin is rerun as NULL_TWIN.
A6 CHEAT: the true response vectors are copied into the prediction at
   -0.5, -0.2, -0.05, and a random permutation of the truth at -0.01 (the
   full hypothesized success pattern injected into the observable), on the
   OU substrate. cheat_detected = common.success(CHEAT, NULL_TWIN) is True.
A7 OU "known J of same size": J0 = diag(x*) A with A the same trophic
   sign-structured 12-species community generator used for the gLV; J =
   J0 - (maxRe eig(J0) - d) I so the leading eigenvalue real part is exactly d.
   True OU press response is analytic: -J^{-1} (0.02 x*_k) e_k (exact mean
   shift of a linear OU under a constant press). Noise: isotropic,
   sigma = 0.05 (the estimator is invariant to the noise scale for a linear
   OU). The OU starts from its exact stationary distribution (Lyapunov solve),
   so all 200,000 steps are stationary observations.
A8 logm of a real matrix can be complex (e.g. negative eigenvalues in a
   shifted twin): the real part is used, and the max |imag| is recorded.
A9 "failure_criterion: null twin within 0.2 of real": |median(treat) -
   median(null)| < 0.2 at -0.5. "no decline": median(-0.5) - median(-0.01) < 0.1.
A10 Phase 2 gLV (declared now, before any code): dx_i = x_i (r_i - m_i +
   sum_j A_ij x_j) dt + sigma x_i dW_i, sigma = 0.02 (multiplicative
   environmental noise, keeps abundances positive; floor 1e-9); r chosen so
   the m=0 interior equilibrium is x0* ~ U(0.5,1.5); ONE mortality parameter
   m applied to the top predator (species 11) is bisected until the leading
   eigenvalue real part of J = diag(x*(m)) A equals d with x*(m) > 0. If a
   seed's community cannot reach d with x* > 0 by that route, the next
   generator draw for that seed is used (recorded).
   Press: constant immigration flux 0.02 x*_k added to dx_k/dt. True response
   = mean abundance shift, estimated from a stochastic pressed run driven by
   the SAME noise as the unpressed (observational) run (common random
   numbers), after the same burn-in, averaged over the 200,000 steps.
   Burn-in: 50,000 steps (500 time units = 5 relaxation times at d=-0.01).
   Deterministic equilibrium shift also recorded (not used for the verdict).

## Parameters (from the spec or fixed here, before any run)

N_SP 12; DT 0.01; N_OBS 200000; TAU 1.0; distances -0.5,-0.2,-0.05,-0.01;
press 0.02 x*; seeds 0..29 (30, spec); OU sigma 0.05; gLV sigma 0.02;
gLV burn-in 50000 steps. Community generator: 12 species = 6 basal,
4 herbivores, 2 predators; self-regulation A_ii = -U(0.5,1.0); each consumer
eats each species in the level below with prob 0.5 (at least one): prey
effect -U(0.2,1.0), consumer gain 0.5 x that; basal competition with prob 0.3,
-U(0,0.2); x0* ~ U(0.5,1.5).
RNG: community = default_rng([seed, 101]); OU noise = default_rng([seed, d_idx,
202]); shifts = default_rng([seed, d_idx, 303]); cheat perm = default_rng([seed,
404]); gLV noise = default_rng([seed, d_idx, 505]).

## Outcome logic (phase 2, in evaluate.py code)

INSTRUMENT_FAIL if positive control (A3) or cheat (A6) not detected;
else CONFOUNDED if CONTROL meets the arm-level success parts (A4);
else SIGNAL if success(TREATMENT, CONTROL); else NULL.

## CPU accounting

All scripts pin BLAS/OpenMP to 1 thread; each appends its process CPU time to
cpu_ledger.jsonl; core_minutes = sum.

## Pilot log

Attempt 1 (pilot_rows.jsonl, PILOT.json attempt 1 overwritten by attempt 2;
numbers kept here): FAIL. POSITIVE_CONTROL medians 0.955/0.951/0.960/0.969
(meets >= 0.95 at -0.5 and -0.2). NULL_TWIN medians 0.250/0.219/0.196/0.124
(does not meet arm-level success; but is NOT <= 0.2 at -0.5 or -0.2).
CHEAT medians 1/1/1/-0.002, decline 1.0, p 9e-10, yet cheat_detected = False
because A6 paired the cheat with the real NULL_TWIN, whose 0.25 > 0.2 blocks
the success() clause. The cheat was therefore testing the null twin, not the
evaluator's ability to see success.

Repair (the one allowed; controls only, no threshold touched): the CHEAT
now injects the WHOLE success pattern into the observable, including its own
null-twin observable: CHEAT_NULL = Spearman(truth[perm], truth) per press
(random permutation per press, default_rng([seed, d_idx, 405])), i.e. an injected
at-chance null. cheat_detected = success(CHEAT, CHEAT_NULL). The real
NULL_TWIN arm is unchanged and still judged by A4. Rerun = attempt 2 with the
same seeds (pilot_rows_attempt2.jsonl).

Recorded finding from attempt 1 (not a repair target): the spec's own null
twin (per-species circular shift) stays at median ~0.22-0.25 on an OU system
whose J is known, i.e. above the success criterion's "null <= 0.2" clause.
Circular shifts preserve each species' autocorrelation, hence the diagonal
of J, and -J^{-1} e_k from a diagonal-dominant estimate still ranks the
pressed species' own response first (stupid explanation 2). Unless the gLV
null twin is lower, the treatment cannot reach SIGNAL through that clause.

Attempt 2 (pilot_rows_attempt2.jsonl, PILOT.json): PASS. positive 0.955 /
0.951 (>= 0.95 at -0.5, -0.2); cheat detected (1/1/1/0.00 vs injected null
~0); null twin 0.250/0.219/0.196/0.124 does not meet arm-level success.
Pilot CPU ~38 s.

## Phase 2 construction clarification (written before any treatment run)

A10 precision (world construction, no treatment statistic exists): the
leading-eigenvalue curve lambda(m) over the interval of m where x*(m) > 0
is not monotone. The fold path is: from m_min = argmin lambda(m) (grid of
4001 points over [-20, 20], restricted to x* > 0) toward INCREASING m
(more top-predator mortality), where lambda rises toward 0 at the boundary
where a species' x* -> 0. For each d, m_d is the first grid crossing of d on
that path, refined by 60 bisection steps. A draw is rejected (next draw for
that seed, recorded as glv_draw) if lambda(m_min) > -0.5 or any d is not
crossed. A exploration of lambda ranges for 8 seeds x 3 draws (1 s CPU) was
done to confirm roughly half the draws reach -0.5; no simulation was run.
Stats-only extras (do not enter the outcome): ORACLE = -J_true^{-1} vs the
stochastic truth (separates estimation from nonlinearity), deterministic
exact shift vs stochastic truth, abundance-rank predictor (SE1),
off-diagonal-zeroed J-hat predictor (SE2), min x/x* in the observational run
(SE3), Spearman(linear true-J prediction, deterministic exact shift) (SE4).

## Phase 2 result (rows.jsonl, OUTCOME.json)

Outcome NULL (decided in evaluate.py). TREATMENT medians 0.956/0.951/0.944/
0.932 (decline 0.024, failure clause "decline < 0.1" met; p 2e-5 but the
0.3 magnitude clause fails). CONTROL (gLV circular shift) 0.220/0.206/0.245/
0.201: above 0.2, so the null clause would also have failed. ORACLE (true J)
and deterministic exact shift both 1.0 at every distance: at sigma 0.02 the
gLV stays in its linear-response regime even at -0.01, so there is no
degradation to find. sigma was a NOTES choice (spec gives none); the
no-decline result is conditional on it. 8/30 seeds needed a community
redraw. CONTROL logm had complex parts (real part used).
