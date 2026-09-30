# W6 Pass 4 round 2 -- implementation notes (HT-55162c0ac0)

Written BEFORE any run. Prompt: hecate/programs/_prompts/pass4_impl_v2.md
(sha256 e55576b2abf79aca49dd5b740bfd6a0d9a6d8ce4060652fc13aded01fb0e2d8c).
Bound by roles/Hecate/prereg/2026-09-30_pass4_round2/PREREG.md (section
HT-55162c0ac0 W6), ../2026-09-30_pass4_round1/PREREG.md (common rules) and
../2026-09-29_probe_round1/PREREG.md (faithfulness guard). Frozen files
outside pass4/ (spec.json, controls.py, ATTAINABILITY.json, probe/) are
read and imported, never modified. controls.main is never called.

## Files and order

1. NOTES.md (this file), before any run.
2. alt_world.py: the generalised carrier (map scale r, additive noise
   sigma) and the Lyapunov measurement. Generic, like controls.run_arm; no
   treatment arm is invoked in it.
3. alt_controls.py: ALT positive control, cheat, null twin, carrier LLE
   per level -> alt_control_rows.jsonl and ALT_ATTAINABILITY.json.
   Also an exactness check: alt_world.run with r = 1, sigma = 0 must equal
   controls.run_arm bit for bit on the POSITIVE_CONTROL arm.
4. attack.py: written only AFTER ALT_ATTAINABILITY.json exists. Runs R,
   ORIG and (if ALT eligible) ALT, each with positive + cheat controls and
   a null twin -> rows.jsonl (one row per attack x variant x arm x seed,
   all parameters, flushed per row). Prints no treatment statistic.
5. evaluate.py: prints/writes control status FIRST; treatment statistics
   only if all controls needed for a reading are detected. Writes
   PASS4_OUTCOME.json; predicate computed in code.

Seeds: 100..109 for every attack (fresh, disjoint from round-3 seeds
0..9). v0 ~ U(-1,1)^12 from numpy default_rng(seed) (spec). Null-twin
partners from default_rng(500 + seed) (spec). Noise stream (only where
sigma > 0) from default_rng(10000 + seed), the SAME realisation at every
level of a sweep (matched noise).

Frozen round-1 parameters reused unchanged everywhere: N 12, G 4,
KAPPA 0.10, eps_g 0.05 (treatment/twin), 0 (positive control),
DELTA 1e-9, TAU 8, K 100, SPACING 20, BURN 500, L 5000, readouts
(FTLE grouping, correlation grouping), average linkage, ARI.

## R (replication)

Original world exactly (controls.run_arm, sigma 0, r 1), seeds 100..109.
Arms: TREATMENT (group partners, eps_g 0.05), POSITIVE_CONTROL (eps_g 0),
CHEAT (PC rows, FTLE partition := nominal), NULL_TWIN (random partners,
eps_g 0.05).
Rule (PREREG): ari_ftle >= 0.8 on >= 9/10 seeds AND correlation grouping
"stays at chance".
Ambiguity "at chance": reading chosen = |mean over seeds of ari_corr|
<= 0.1 (chance ARI is 0; round-3 twins' 10-seed means were within
+-0.06). R reproduced iff treatment meets both AND the null twin does
not meet the grouping rule.
PC detected (R) = PC meets the same rule (grouping 9/10 and corr at
chance). Cheat detected = CHEAT rows meet it.

## ORIG (non-chaotic carrier)

Carrier: v_i' = (1-kappa-eps_g) r T(v_i) + kappa v_p v_q + eps_g mean_j r T(v_j)
+ sigma xi_i, then clipped to [-1, 1] (clip applied only when sigma > 0,
so r = 1, sigma = 0 is exactly the original world). Same coupling graph
(group partners), same kappa, same eps_g. ORIG carrier: r = 0.2 (slope
at the origin 0.85 x 0.2 x 3 = 0.51 < 1: contracting). Its LLE is
MEASURED (tangent-vector method, analytic Jacobian, 2000 post-burn-in
steps) and must be < 0 on every seed for the variant to count.

Ambiguity "same ... noise": the original world has no noise term. A
noiseless contracting carrier collapses to its fixed point (here v = 0,
where the product coupling has zero linear response), so "noise" in the
PREREG text implies a noise-driven stable system. Reading chosen: ORIG is
an existence test ("chaos is not needed" is refuted by ANY non-chaotic
carrier that groups), run at a pre-declared noise grid
sigma in {0 (literal), 0.01, 0.05}. The perturbation experiment uses
COMMON noise: reference and perturbed copies receive the same noise
realisation (the one that drove the trajectory), so dv is pure response.
ORIG fires iff, in at least one READABLE variant, TREATMENT ari_ftle >= 0.8
on >= 9/10 seeds (same rule as R). A variant is readable iff its LLE < 0
on all seeds, its PC (eps_g 0) meets the grouping rule, its CHEAT meets
it, and its NULL_TWIN does not. Unreadable variants are recorded, not
read. If no variant is readable, ORIG is not assessable (fired = false,
recorded as anomaly, and controls.positive_detected = false).
Also reported (not used for firing): mean ari_ftle per variant.

## ALT (carrier sweep, control-first)

Levels r in {0.2, 0.35, 0.5, 0.65, 0.8, 0.9, 1.0} (7 >= 5), kappa 0.10,
eps_g 0.05, sigma 0.05 at every level (matched coupling and noise; sigma
0.05 is the largest point of the ORIG grid, small against the state range
[-1,1] and far above DELTA; chosen here before any run).
Level classification (chaotic iff mean LLE > 0, non-chaotic iff < 0) is
frozen in the control phase from the NULL_TWIN carrier (random partners,
same kappa, eps_g, sigma, r), which has matched nuisance statistics and no
treatment. Treatment-world LLE is also measured; a sign disagreement with
the frozen class is an anomaly (the frozen class is still used).
Clauses (PREREG, thresholds unchanged):
  A1 min over chaotic levels of mean ari_ftle - max over non-chaotic levels
     of mean ari_ftle >= 0.2.
  A2 Spearman(LLE, ari_ftle) >= 0.6.
Ambiguity for A2: reading chosen = pooled over (level, seed) pairs
(70 points, per-(level, seed) LLE of that arm's world, per-seed score),
average ranks for ties. Level-mean Spearman (7 points) is reported as a
secondary statistic only. Reason: 7 points give chance Spearman often
>= 0.6, so a level-mean clause could not be discriminating.
Eligibility (ALT_ATTAINABILITY.json, before any treatment code exists):
  E0 >= 5 levels, >= 1 frozen chaotic and >= 1 frozen non-chaotic level;
  positive control: group partners with eps_g 0 at chaotic levels and
     random partners (rng 500+seed) with eps_g 0.05 at non-chaotic levels
     (grouping gated on chaos by construction); must meet A1 and A2;
  cheat: NULL_TWIN rows with the FTLE partition replaced by the nominal
     partition at chaotic levels; must meet A1 and A2;
  null twin: random partners, eps_g 0.05, at every level; must meet
     NEITHER A1 NOR A2 (each clause individually discriminating).
If any fails: ALT NOT_ELIGIBLE, no ALT treatment code is written.
ALT PASS iff A1 AND A2 on the treatment (group partners, eps_g 0.05,
sigma 0.05), seeds 100..109. Otherwise FAIL.

## Predicate (in code)

controls_ok = R controls detected AND ALT controls (attainability) all
detected AND >= 1 readable ORIG variant.
- if not controls_ok or ALT != PASS -> PARK
- elif ORIG fired -> ORIG_FOSSIL_ALT_PASS
- elif R reproduced -> SURVIVES
- else -> PARK (R not reproduced; recorded).

## Budget and faithfulness

OMP/MKL threads = 1. CPU seconds from time.process_time, summed over
alt_controls.py and attack.py (and evaluate.py) -> core_minutes. Cap 10.
No parameter or threshold changes after a treatment statistic is printed.
A rerun after a crash/bug is recorded in attempts.
