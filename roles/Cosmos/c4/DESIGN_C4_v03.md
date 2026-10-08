# C4 DESIGN v0.3 -- repairs to v0.2 driven by executed reviewer attacks (NOT frozen; F-0002 NOT made)

Campaign 48H_2026-10-08 (operator directive roles/Cosmos/prompts/2026-10-08_operator_48h_campaign/, s VI).
v0.2 (DESIGN_C4.md) stays the text under independent review; this file lists what v0.3 CHANGES and why. Each
change cites the finding it answers and the executable evidence. Branch cosmos/c4-v03; merges to main only after
both final reviews (operator ruling 2026-10-01 on R-MECH independence).

## 0. Status of every BLOCKING finding
| finding | v0.3 change | executable evidence | status |
|---|---|---|---|
| A1 family-constant cheat passes S0-A | primary statistic = mean WITHIN-family BA uplift, equal family weights; within-family sign-flip; family-floor (d') | stats.py; tests/test_c4_stats.py (cheat FAILS 10/10 seeds; v0.2 statistic kept as red reference) | REPAIRED (pending R-STAT final) |
| A4 multiplicity in S2 | one omnibus LRT per criterion (offset, slope) + one CMH-type permutation test, Holm at FWER .05 | stats.py, calib_s2.py; planted universal passes .93 (n 240, 60 sims), FAM_OFFSET / FAM_SLOPE pass 0/60 | REPAIRED; DEFECT FOUND on the way (below) |
| A5 selection leakage | DISCOVERY / CONFIRMATION / EXTERNAL seed namespaces; confirmation vault: freeze-first, spend-once, every scoring ledgered | firewall.py; tests/test_c4_firewall.py (incl. a winner's-curse demonstration) | REPAIRED |
| F1 SYSID restatement | coordinates restricted to LOCAL (one controlled step from a stationary state, decoder-free) behind LocalProbe; G7 LOCALITY enforced in code | sysid_local.py; tests/test_c4_sysid_local.py (the REL@q cheat raises HorizonError; G1 AST import audit; G3; G5 re-encoding) | REPAIRED BY REDESIGN of the vocabulary |
| F2 B reconstructs A | S3 RE-SCOPED (option b) + machinery declared; shared-failure matrix on planted systems; decoder class made explicit | cert_b.py; tests/test_c4_cert_b.py | RE-SCOPED; see s3 |

## 1. S0 (A1, A2, A10)
- Primary S0-A statistic U = mean over families of [BA_f(candidate) - BA_f(baseline)], equal family weights.
  Justification: the claim is cross-substrate, so each family is one unit of evidence; world-count weighting
  lets the largest family carry the claim; pooled BA lets between-family base rates masquerade as explanation.
- (a) U >= DELTA_A = .10; (b) within-family sign-flip p < .05 (10000 flips); (c) family-stratified bootstrap LB of
  U > 0 (2000); (d') per-family uplift > 0 in all but at most one family and >= -.05 in every family.
- Families with one class present are dropped from U and COUNTED.
- A2: the S0 claim is CONDITIONAL ON THE VISIBLE FAMILIES. The exact family-level sign-flip p (floor 2^-F) is
  reported next to it as descriptive cross-family support. Substrate independence is never argued from S0.

## 2. S1 vocabulary (F1, F3, F5)
- Coordinates may observe the dynamics for AT MOST ONE controlled step from a stationary state (G7). Burn-in
  inputs are never exposed. Coordinates are decoder-free and whitened.
- Current LOCAL vocabulary: lam (spectral radius of the regressed one-step response to resample perturbations;
  works for float and integer states), eta (one-step noise injection), gamma (one-step input injection), vis
  (readout visibility of a state perturbation). rho (median kick ratio) is RETIRED: it is undefined for integer
  state (graph: 225 / 0).
- Why this closes F1 for the right reason: nothing in the vocabulary has observed k-step input propagation, so a
  law must PREDICT k-step usability by composing one-step physics. That is a falsifiable physical claim; it fails
  wherever local physics does not compose (thresholds, non-Markov views, clumped transport).
- T4-SYSID@q (probe decodability at q) is kept as an ORACLE REFERENCE, not a must-beat rung: it remeasures the
  phenomenon, so requiring a law to beat it by DELTA would make S0 unpassable by any honest law. Reported always.
- F3: an S4 arm counts only if the law's frozen prediction differs from T4's on that arm, or the law uses LOCAL
  coordinates only (it then cannot have measured the post-intervention propagation).
- F5: planted continuous families (planted.Reservoir, RotReservoir) are in the calibration suite.

## 3. S3 re-scoped (F2, A12)
- In passive families (an externally trained readout is the actor) every behavioural certificate tests the same
  causal contrast. "Certificate independence" of the contrast is not available there, and v0.3 does not claim it.
- S3 becomes MACHINERY ROBUSTNESS: a law must pass under A and under B, where B differs from A in intervention
  (source randomization vs state-dict interchange), statistic, seeds, code and decoder implementation. B imports
  nothing from A (AST test).
- Shared-failure matrix (planted): HiddenCarrier (carrier outside the state dict): A PASSIVE 5/5 seeds, B
  FUNCTIONAL -> A's interchange depends on state-dict completeness, B does not. XorCue (V = 2): B-linear .49,
  B-rf 1.00 -> usability is RELATIVE TO THE ACTOR'S READOUT CLASS; A and B-linear share the linear-actor
  definition by design. Reservoir: all agree (same contrast, legitimate agreement).
- Every C4 claim states its actor class ("linear-actor usability"). B-rf is reported as an actor-class
  sensitivity, not as a second certificate.
- A12: A/B kappa per family is reported BEFORE any law is scored.

## 4. S2 (A4)
- (b) offset: y ~ 1 + s vs y ~ fam + s (df F-1); (c) slope: y ~ fam + s vs y ~ fam + fam:s (df F-1);
  (e) CMH-type permutation of family labels within predicted-probability bins. Holm across the three, FWER .05.
- DEFECT FOUND AND FIXED (2026-10-08): the first (c), a family recalibration LRT on LOFO predictions, falsely
  rejected 30% of planted universal laws, because each held-out family's predictions come from a different fold
  model (family structure planted in p by construction). (c) now tests slope heterogeneity on the law's own
  score; LOFO calibration is reported, not gated.

## 5. Discovery / confirmation (A5)
- Law search, coordinate selection and complexity choice see DISCOVERY only. A candidate is frozen in the vault
  BEFORE any CONFIRMATION batch exists. A confirmation batch is spent by its first scoring. A revised law gets
  a new id and a fresh batch.

## 6. Instrument findings that change how labels are read
- Certificate A is SEED-UNSTABLE where linear usability is knife-edge (XorCue V = 2: F/P/I/P/F over 5 seed x
  size settings; a linear actor can reach .75 on XOR by sacrificing one pattern). A label is a property of world
  x actor training procedure x sample. v0.3 requires, per world, A at two seeds; disagreement -> INDETERMINATE.
- F4: T3-DOWN registers every continuous-noise world (60/60 on the R-MECH grid). The per-family REGISTERED rate
  under P is reported before F-0002; S0-A's challenge meaning holds only in families with non-trivial
  registration.

## 7. Not yet repaired (REPAIR-class findings; before F-0002)
A3 power re-run with family-varying accuracy and base rates; A6 equivalence bounds ("no law" only when the
bound excludes the minimum effect of interest); A7 Z_A estimation for S0-C; A9 best/worst-case BA bounds for
excluded rows and a Newcombe CI on the differential-exclusion flag; A13 one headline statistic per gate.
