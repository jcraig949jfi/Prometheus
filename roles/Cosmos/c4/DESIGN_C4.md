# C4 -- upstream causes of causally accessible history (DESIGN v0.2; not frozen; build NOT authorized)

Campaign C4, thread T-C4 thr-cac8c079f216. Successor to C3; a NEW preregistration, not a repaired C3.
v0.2 of 2026-09-30 answers the operator review of v0.1
(roles/Cosmos/prompts/2026-09-30_operator_c4_review/). v0.1 is kept in git at c37e2c687.
Status: DESIGNED v0.2. It goes to two independent reviews (s12). F-0002 (the full preregistration) and
the instrument build wait for the operator's authorization after those reviews are reconciled.
Frozen so far: F-0001 (the v0.1 S0 rules). F-0001 is SUPERSEDED IN DESIGN by s3 below. The chain entry
changes to SUPERSEDED only when F-0002 is frozen (FREEZES rule: a repair appends, it never edits).
No D/D2 material was read. No choice below depends on D2 (s11).

## 1. Scientific target
C3 showed that "usable history is present at the actor interface" is too close to the operational
certificate to count as an explanatory law. C4 asks: what PHYSICAL PROPERTIES determine whether
historical perturbations remain reliable, distinguishable, routable and behaviourally usable over time?
C4 is not required to find a law. It is required to be an experiment CAPABLE OF DISCOVERING THAT NO
COMPACT SUBSTRATE-INDEPENDENT LAW EXISTS (s10). "No successor law earned" is an acceptable result.

## 2. Terms
- Certificate A: the C3 v3 P1/P2 certificate (the label; unchanged).
- Certificate B: the gate-S3 certificate (s6).
- T3-DOWN, the SHORTCUT: the zero-parameter certificate-precondition rule (definition in F-0001 s3).
  It is a downstream remeasurement of much of the target semantics, not an ordinary predictive
  baseline.
- REGISTERED world: a world where T3-DOWN predicts FUNCTIONAL, i.e. the historical perturbation is
  registered at the actor interface.
- LOFO: leave-one-family-out. BA: balanced accuracy (FUNCTIONAL vs not).

## 3. Gate S0 v0.2 -- explanatory uplift where the shortcut fails
T3-DOWN stays BINDING, but for the right question: a physical explanation must ADD information where the
shortcut is wrong, without breaking cases where the shortcut is right.
- A candidate that duplicates T3-DOWN FAILS.
- A candidate that fixes the challenge regime but breaks the ordinary one FAILS.
Two independently sampled world sets, reported SEPARATELY and never pooled into one score:

S0-A CHALLENGE STRATUM (the primary explanatory gate)
- Sampling (label-blind, s7): worlds drawn from an ENRICHED native proposal Q_A, keeping only REGISTERED
  worlds. So every world has the historical perturbation registered, and usability may or may not
  survive. Size: >= 160 determinate worlds, all families present.
- PASS requires ALL of:
  (a) pooled LOFO BA(candidate) - BA(T3-DOWN) >= DELTA_A = 0.10;
  (b) a paired sign-flip randomization test of that BA difference, one-sided p < 0.05. Each world
      contributes (1[cand right] - 1[T3 right]) / (2 n_class); 10000 flips;
  (c) the lower bound of a 95% family-stratified paired bootstrap CI > 0 (2000 resamples);
  (d) in every family, LOFO BA(candidate) >= BA(T3-DOWN).
  McNemar is reported DESCRIPTIVELY only. It tests accuracy, not BA, and on class-imbalanced strata it
  rejects good candidates (v0.1 power finding, s9).
- T3-DOWN's BA in this stratum is ~.5 by construction, so DELTA_A = .10 asks for real
  discrimination, not perfection.

S0-B ORDINARY STRATUM (non-inferiority)
- Sampling: an INDEPENDENT sample from the NATURAL distribution P (s7), not enriched, not filtered.
  Size: >= 240 determinate worlds.
- PASS requires:
  (a) the lower bound of a one-sided 95% family-stratified paired bootstrap CI of BA(cand) - BA(T3-DOWN)
      > -EPS_B, with EPS_B = 0.03;
  (b) LOFO BA(candidate) >= max(T0, T1a, T2a) + 0.05 (the trivial baselines of F-0001 s3).

S0-C TARGET-DISTRIBUTION ESTIMATE (reported, not a gate)
- A self-normalised importance-weighted BA for the natural distribution P, combining both samples
  with the balance heuristic over the two known proposal densities (P and Q_A are Cosmos-specified,
  so the weights are exact).
- Reported with a bootstrap CI and the effective sample size.
- No prevalence claim is ever made from S0-A alone.

Also reported in both strata: T0, T1a, T1b (leakage reference), T2a, T2b (within-family ceiling), T3-DOWN.

## 4. Gate S1 v0.2 -- explanatory measurement != certificate measurement
PROHIBITED in any candidate coordinate:
- certificate twins;
- P2 swaps or interchanges;
- certificate ablations;
- certificate seeds or RNG streams;
- certificate-trained readouts;
- any label-producing statistic (P1 cross-entropies, P2 effects, their nulls);
- T3-DOWN outputs;
- any C3 coordinate, including G-0006's (dead; not revived).

ALLOWED: preregistered, TASK-INDEPENDENT physical identification experiments (the SYSID protocol), run
through the generic System interface by a separate module with its own RNG namespace:
- standardized impulse-response probes: probe symbols injected through the input channel, responses
  recorded over a FIXED horizon grid H = 1..16;
- intrinsic decay and mixing: whitened autocorrelation and spectral timescales of full_state and of
  the readout view under i.i.d. drive;
- channel reliability: a fixed-class decoder (linear, frozen hyper-parameters) recovers PROBE symbols
  over the grid H. Probe symbols, not the task cue, and never the certificate's probe;
- perturbation propagation and amplification: probe-owned twins with a standardized random
  whitened-state kick, at probe-chosen times, over the grid H. Never a cue swap, and never at a task
  time;
- causal path length, redundancy and bottlenecks: from the propagation map and from the effective rank
  or canonical correlations between the input, state and readout views;
- where a family declares them, energetic or computational maintenance costs in native units.

Guards (all must pass before any law search; each has a planted cheat control that must be CAUGHT):
G1 IMPORT AUDIT: the SYSID module imports numpy and the System interface only. No certify, probe, gate,
   calib, task pairing or C3 coordinate code.
G2 MUTATION: coordinates are bitwise unchanged when the certificate code, its seeds or the task
   pairing change.
G3 K-INDEPENDENCE: coordinates are WORLD properties (rates, timescales, gains, capacities) and are
   BITWISE IDENTICAL across the k-variants of a world. The query time enters only in the law, never in
   a coordinate. This is the structural guard against remeasuring the certificate at q.
G4 LABEL-BLIND SETTINGS: every probe setting (horizons, probe alphabet, kick size, decoder class) is a
   constant of the frozen protocol. None is chosen by, or after, any label.
G5 RE-ENCODING INVARIANCE: coordinates are invariant, within bootstrap SE, under an invertible linear
   re-basis of either view, duplicated components and re-encoded discrete variables (whitened /
   affine-invariant statistics only).
G6 RESTATEMENT DIAGNOSTIC: report each coordinate's rank correlation with the P2 effect and with the
   T3-DOWN inputs. This is a diagnostic, not a gate: a good upstream coordinate SHOULD predict
   usability. Restatement is prevented structurally by G1-G4.

## 5. Gate S2 v0.2 -- residual family dependence
Family-ID prediction from the coordinates (1-NN / logistic LOO, kappa) is REPORTED as a DIAGNOSTIC and
is not a boundary: a universal coordinate may differ in distribution across families. The gate asks
whether substrate identity, once the physical coordinates are known, still explains prediction or
residuals. A law FAILS S2 (it is not universal; it is recorded as RESTRICTED or killed) if any of the
following holds:
(a) LOFO collapse: S0-A or S0-B passes on within-family cross-validation but fails under LOFO;
(b) residual location: a per-family boundary offset whose bootstrap CI excludes 0 by more than the
    attainable resolution (resolution computed before the freeze, from replicate noise);
(c) calibration: a per-family calibration intercept or slope whose CI excludes the pooled values
    (logistic recalibration on held-out predictions);
(d) explicit family terms: in cross-validation held out WITHIN the training families, law + family
    fixed effects improve BA by >= 0.02, or log-loss by a paired-test p < 0.01;
(e) conditional dependence: a stratified permutation (CMH-type) test of error independent of family,
    given predicted-probability bins, gives p < 0.01.
A law whose apparent success needs a family-specific correction term is NOT universal.

## 6. Gate S3 v0.2 -- Certificate B changes the intervention level
- B-USE (causal use; source-level randomization):
  - the cue is randomized at the SOURCE, independently per episode, from B's own seed namespace;
  - distractors are independent of it, and the query observation is identical in every episode, so
    the current observation is controlled;
  - a readout is trained on B's own training episodes and tested on held-out episodes;
  - FUNCTIONAL-B iff held-out answer accuracy beats chance, by an exact binomial test on V-way
    accuracy with a pre-frozen alpha and a minimum effect.
  Because the cue is randomized at the source and the present observation carries nothing, any
  dependence of the answer on the cue is causal and must travel through the world's history.
- B-STORE (persistence, for the PASSIVE split): the cue is decodable from full_state at q by a
  DIFFERENT estimator class (k-NN / random-feature classifier) on independent episodes, against a
  label-permutation null.
- Classes: FUNCTIONAL-B = B-USE; PASSIVE-B = B-STORE and not B-USE; NONE-B = otherwise.
- Independence from A:
  | machinery | Certificate A | Certificate B |
  |---|---|---|
  | intervention | internal-state swap at t = k | source randomization at t = 0 |
  | test | paired effect | behavioural held-out test |
  | pairing | common-random-number pairs | none |
  | seeds | A's | own namespace |
  | code | certify.py | separate module |
  They share only the task definition, the System interface and the macroscopic phenomenon.
- B is calibrated on the planted suite (s8) before use.
- S3 PASS: A/B agreement is reported per family (kappa). The candidate passes S0-A and S0-B under B
  labels as well as A labels. A relation that exists only under Certificate A is NOT earned.

## 7. World sampling (label-blind, with explicit estimands)
- Families: >= 4 visible families; >= 2 mechanisms not present in C3; >= 1 authored outside Cosmos
  (commission: c4/VISIBLE_FAMILY_CONTRACT.md).
  - Plan: the C3 visible families (FRESH worlds only; the C3 visible worlds are burned for scoring) +
    >= 1 new Cosmos-authored mechanism + >= 1 foreign family.
  - If the foreign author independently builds a C3-like mechanism, Cosmos authors a second new one.
- NATURAL distribution P (S0-B): per family, uniform over the family's DECLARED native ranges or
  lattice, k uniform on {2, 4, 8}, V as declared.
- CHALLENGE proposal Q_A (S0-A):
  - per family, a density over native knobs that up-weights ranges whose DECLARED physical meaning is
    noise, gain, coupling or proximity to a stability limit;
  - written from the native declarations BEFORE any C4 certificate label exists;
  - followed by the REGISTERED filter (T3-DOWN predicts FUNCTIONAL).
  T3-DOWN is computed without any certificate label, so the filter is label-blind.
- Label-blindness is enforced in code. The sampler never imports the certifier, and its output is
  bitwise identical when labels are permuted or absent (test with a planted label-peeking sampler that
  must be caught).
- Estimands: S0-A = BA on (Q_A restricted to REGISTERED worlds); S0-B = BA on P; S0-C = BA on P, by
  importance weighting.

## 8. Planted calibration (before any real world is scored)
The instruments (SYSID, Certificate B, the sampler) must recover known answers:
- a linear channel with known SNR(k);
- a noiseless delay line;
- a PURE-CHAOS control: T3-DOWN = FUNCTIONAL, truth = NONE;
- a PASSIVE control;
- a slow-leak control whose usability dies between k = 4 and k = 8 at a known rate;
- cheat controls for G1-G4 and for the sampler.
Any failure means the instrument is not qualified and nothing is reported.

## 9. Power (synthetic; prometheus/cosmos/c4/power_s0.py; output c4/POWER_S0_v0.2.json)
- S0-A with the sign-flip test, 5 families, P(pass):
  | challenge worlds | candidate right .62 | right .70 | right .80 |
  |---|---|---|---|
  | 80 | .35-.40 | .86-.93 | 1.00 |
  | 160 | .67 | .99-1.00 | 1.00 |
  Stable across FUNCTIONAL shares .4-.6. The v0.1 McNemar version gave .20-.40 at share .6: a test
  defect, now removed.
- S0-B (the shortcut is wrong on 6% of natural worlds; the candidate fixes half of those; P(pass)):
  | new-error rate | n 120 | n 240 |
  |---|---|---|
  | 0 | 1.00 | 1.00 |
  | .02 | .77 | .91 |
  | .04 | .35 | .53 |
  | .06 | .15 | .12 |
  So EPS_B = .03 tolerates about 2% new errors and rejects 4-6%.
- Sizes adopted: S0-A >= 160, S0-B >= 240 determinate worlds, >= 4 families.
- The C3 visible analysis that motivated v0.2: T3-DOWN BA .905, and all 7 of its errors are false
  positives. The detail is withheld (local 197daf5f3, S0_VISIBLE.json 7b0a1341...).

## 10. Gate S4 -- counterfactual intervention (kept)
- At least one frozen prediction of the form do(native knob a -> b) -> predicted class and J change.
- It is made from PRE-intervention SYSID coordinates, before the post world is measured.
- The target arm changes an upstream physical property (noise per step, amplification, coupling,
  bottleneck) while the cheap certificate precondition STAYS REGISTERED. The arm is VOID if T3-DOWN is
  not REGISTERED on the post world, and that check is preregistered. The prediction is a transition
  in functional use, e.g. FUNCTIONAL -> NONE, where the shortcut predicts no change.
- A MATCHED OPPOSITE ARM moves the correlates while holding the upstream quantity fixed, and predicts
  NO change.
- The knob may not be the cue channel, the readout cut or the history-bearing state itself.

## 11. Stop conditions (each mapped to a check) and D2
| stop condition | check |
|---|---|
| zero-parameter semantics still explain almost everything | S0-A fails (no uplift where the shortcut fails) |
| the law buys challenge wins by breaking ordinary cases | S0-B fails |
| the law needs family-specific corrections | S2 (b)-(e) fails |
| performance collapses under LOFO | S2 (a) |
| the law depends on one certificate implementation | S3 fails under B |
| the only successful intervention moves the label-defining quantity | no S4 arm qualifies |
| no compact representation | a law above the preregistered complexity cap (fixed in F-0002), or a per-family exception needed |
All gates are the ways "no compact substrate-independent law exists" gets DISCOVERED. Each failure is
reported as a failure SHAPE: which stratum, which family, which certificate.
D2: SEALED / UNREAD / UNSPENT / COMPATIBILITY PENDING.
- Harmonia ruled the 2026-09-30 ciphertext-grep incident NO_INFORMATION (Addendum R, ca7d354f4). The
  operator's provisional reading is CONTACT_WITH_PACKAGE_PATH / NO CONTENT REVEALED.
- No C4 decision depends on D2.
- D2's compatibility is determined separately, after the visible gates, by a seat other than Cosmos.

## 12. Reviews before F-0002 (operator s9)
Two independent reviewers. Neither may be Cosmos, Harmonia (kept clean for D2), Nestor (the D2
custodian) or the foreign visible-family author:
- R-STAT, statistical / experimental design;
- R-MECH, mechanistic / adversarial.
Brief: c4/REVIEW_BRIEF_v0.2.md. Seats are assigned by Aporia. C4 proceeds to F-0002 only after both
reviews are reconciled, the reconciliation is recorded, and the operator authorizes the build.

## 13. Open for the operator
Q-A C3 FAMILY CODE is on the withheld branch.
- Using those families in C4 means C4 results expose them. Publication now needs only the operator's
  trigger: the original seal and D2 are on main, D2 is sealed, and Harmonia ruled the incident
  NO_INFORMATION.
- Lean: trigger publication of the C3 withheld branch AFTER the foreign family is committed (so its
  author works without the C3 material in view) and before the reviews close.
- Otherwise C4 uses only new families.
Q-B BUILD authorization after the reviews (operator s11 gate).
