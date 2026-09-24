# ENSORAIN D-SERIES "DIALS" -- Round 1 preregistration (exploratory search)

Currency: 2026-09-24. Seat Ensorain[m2-14baf7d5]. Authority: operator,
2026-09-24 ("create experiments that test this in the worlds you've been
playing with ... randomize dial adjustments, gather data and analyze for
subsequent rounds"), on top of the dials text in
roles/Ensorain/prompts/2026-09-24_dials_of_intelligence/. Committed BEFORE
any D-series code runs.

Round 1 is HYPOTHESIS-GENERATING. It issues no verdict. Its only outputs
are (a) the rows, (b) the analysis below run exactly as written, and (c) a
Round-2 preregistration that tests ONLY what Round 1 nominates by the
selection rule in s6. Nothing found in Round 1 is reported as a result
until Round 2 replicates it on fresh seeds.

## 1. The thesis under test

"Intelligence = phase behaviour of a coupled adaptive system": competence
is governed by COUPLINGS between opposing pressures more than by any dial
alone, with regimes where qualitatively new behaviour appears, and with
quantities that change BEFORE the competence rulers fire.
Three measurable claims, each with its null:
  T1 COUPLING   dial pairs interact (non-additively, including crossover
                interactions that no monotone rescaling of the ruler can
                remove). Null: additive.
  T2 PHASES     competence is bimodal/threshold-like in dial space and
                phase membership needs couplings to be predicted. Null:
                main effects predict membership as well.
  T3 PRECURSORS some internal quantities move consistently in a window
                before the ruler fires. Null: the same movement at randomly
                aligned times / in lives that never fire.
E0 evidence against T1 on one pair is on record (ensorain/DIALS_RETRO.md).

## 2. Worlds (E2's families, plus two world-side dials)

E2 lock worlds (4 modes x 8, held-out (A,C) region, L1/L2/L3 locks,
1,200 events, tau .15), family in {TT, MAT, CP, NONE} (NONE 10% of lives,
the no-structure null), hidden mode order random per instance. New world
dials: DRIFT d in [0, 0.6] -- at event 600 the generative parameters are
perturbed (x' from sqrt(1-d)*params + sqrt(d)*fresh params, same family
and structure; lock truths after 600 use x'); NOISE in [0.05, 0.5]
(observation sd). Economy as E1/E2; compute price multiplier in
[0.25, 4] (log-uniform). Different MECHANISM worlds (E0's navigation
world) are Round 2+ candidates, stated here, not built in Round 1.

## 3. Organism dials (operator's names -> the knob that implements them)

  plasticity<->stability        lam (proximal pull), log [0.3, 300]
  consolidation depth           sweeps, int [1, 20]
  timescale separation          scratch S (fast buffer between slow
                                consolidations), log-int [32, 512]
  constraint pressure           cap C, log-int [96, 512]
  replay (compression<->fid.)   replay_frac of cap for a raw-sample replay
                                store, [0, 0.5]; store mixed into every
                                consolidation
  internal generation           dream_ratio [0, 2]: pseudo-samples from the
                                organism's OWN predictions at random
                                addresses, per real sample
  prediction<->surprise         surprise_alpha [0, 2]: consolidation batch
                                resampled with weight |error|^alpha
  self-disturbance              disturb [0, 0.3]: relative noise injected
                                into parameters before each consolidation
  forgetting                    forget [0, 0.2]: magnitude shrink per
                                consolidation
  error persistence             err_frac of cap [0, 0.3] for a store of the
                                worst-residual samples, kept up to
                                persist [1, 20] consolidations or until
                                resolved
  representation fluidity /     p_restruct [0, 1] per consolidation: TT
  rewiring freedom              only -- re-express the memory in an
                                adjacent-swapped mode order (TT-SVD of its
                                own dense tensor), accept if batch
                                validation improves; charged
  representation family         family in {TT, CP, LR}; start structure in
                                {correct, random}
All stores count against the cap; the model gets what is left. Every
extra sample (replay, dreams, errors) is charged as consolidation compute.
NOT implemented in Round 1 (no honest knob in these worlds): causal
reach, information permeability, boundary softness, credit diffusion,
modularity pressure beyond family/rank allocation, counterfactual depth
beyond dreams. Stated so absence is not read as a null.

## 4. Sampling and rulers

Round 1: 2,400 lives, every dial drawn independently (uniform or
log-uniform as listed; categorical uniform), world instance seeds
60000-62399, organism seed = life index. Each life also runs a NOMEM
twin on the identical world for EFF.
Rulers (final): held-out R^2 against the CURRENT field; phase-2 L2
success; post-drift L2 success; EFF = (U - U_NOMEM) / max(P_used, 1);
survival. Trace every 4th consolidation: held-out R^2 on a fixed 512-cell
held-out sample, windowed L2 success, relative parameter change,
effective TT ranks, pre-update batch error (surprise), store fills.
FIRE time: first trace point with held-out R^2 >= 0.5.

## 5. Analysis (run exactly as written; ensorain/d1/analyze.py committed
## before the Round-1 rows exist)

Split: DISCOVERY = even life index, VALIDATION = odd.
A. Main effects: Spearman rho of each dial with each ruler, permutation
   p (2,000), BH-FDR q < .05 in discovery; replicated if same sign and
   p < .05 in validation.
B. Couplings: every pair of dials (continuous dials tercile-binned,
   categoricals as levels), OLS y ~ bins_i + bins_j + bins_i:bins_j,
   F test for the interaction block; BH-FDR across all pairs and the two
   primary rulers (held-out R^2, EFF). Nominated only if q < .05 in
   discovery AND the validation interaction pattern correlates with the
   discovery pattern (r > .5, p < .05). Reported separately on RANK-
   transformed rulers; a CROSSOVER (the sign of dial i's effect flips
   across bins of j, both CIs excluding 0) is flagged as the strongest
   form.
   Controls (must pass or B is void): ruler shuffled -> <= 5% of pairs
   nominated; planted interaction (ruler + 0.3 sd x z_i z_j for a random
   pair) -> that pair nominated.
C. Phases: fraction of lives with held-out R^2 >= .5; logistic model of
   membership with main effects only vs + all pairwise products; fit on
   discovery, compare log-loss on validation. T2-supportive only if the
   coupled model improves validation log-loss by > 5%.
D. Precursors: lives that FIRE at trace point >= 2; for each traced
   quantity, change over the two points before FIRE vs (i) the same
   quantity at random alignment times in non-firing lives, (ii) random
   alignment within firing lives before FIRE; sign-test and permutation
   p, BH-FDR; nominated if q < .05 in discovery and same sign, p < .05 in
   validation.

## 6. Round-2 selection rule (fixed now)

Round 2 tests at most 6 nominations: the replicated couplings with the
largest discovery effect (crossovers first), the replicated precursors,
and T2 if supportive. Each gets a replicated grid (>= 8 instances per
cell) on fresh seeds (70000+) with the same controls. Nothing else from
Round 1 is claimed.

## 7. Seat predictions (losable)

P1 Main effects dominate (lam, sweeps, cap, family-correctness, noise).
P2 At most 2 replicated couplings; the likeliest is replay x drift
   (replay helps stable worlds and hurts drifting ones -- a crossover) or
   lam x drift (stability good without drift, bad with it).
P3 Dreams (internal generation) help only with low noise and hurt with
   high noise (grounding coupling) -- p .3.
P4 Precursor: effective TT rank settles (stops changing) before FIRE;
   parameter change falls before FIRE -- p .4.
