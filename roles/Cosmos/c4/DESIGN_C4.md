# C4 -- upstream causes of causally accessible history (DESIGN; not frozen; not authorized to execute)

Campaign C4, thread T-C4 thr-cac8c079f216. Successor to C3. This is a NEW preregistration, not a repaired C3.
Authority: operator 2026-09-30 (roles/Cosmos/prompts/2026-09-30_operator_c3_disposition/): design only.
No holdout (D2 or new) is authorized. Status: DESIGNED (draft v0.1, 2026-09-30); pre-result review PENDING.
Frozen so far: gate S0 trivial rules only (c4/S0_TRIVIAL_RULES.md = FREEZES F-0001).
Inputs: the public C3 autopsy (research/reviews/AUTOPSY_C3_PUBLIC_2026-09-30.md, lessons L1-L7) and the S0
visible-data analysis (s8). No D/D2 material was read, and nothing below is shaped by guesses about D2.

## 1. Question
C3 asked: is usable history present where behaviour can access it? The answer was the certificate. C4
asks the upstream question: what PHYSICAL PROPERTIES of a world make historical information remain
reliably and causally accessible? And does a compact, substrate-independent representation of those
properties predict functional historical use better than the certificate's own zero-parameter
semantics, across families it was not fitted on?
"No successor law earned" is an acceptable result.

## 2. How the C3 scar becomes design constraints
| lesson (public autopsy) | C4 constraint | where |
|---|---|---|
| L1 explain != define | the machinery firewall: no pairs, swaps, ablations, effect statistics or task-trained readouts in any coordinate; enforced in code | s4 |
| L2 preregister the definition rung | S0 frozen first (F-0001); T3-DOWN must be beaten under LOFO | S0_TRIVIAL_RULES.md |
| L3 leakage as a number | family predictability reported next to phenomenon predictability; LOFO primary | s5 |
| L4 record the rule, not its score | every verification stores rule text + code sha256 + input hashes | s9 |
| L5 distance is not information | S0's headroom is exactly where the two diverge (s8); S4 targets that regime | s7, s8 |
| L6 designed-in expectation | no candidate law is written before the coordinates exist and pass S1/S2; precommitments are about MECHANISMS and can be lost | s9 |
| L7 export choices are free parameters | coordinates are invariant to basis, duplication and discrete encoding, and a re-encoding suite tests this | s4 |

## 3. Phenomenon labels (two certificates; gate S3)
Certificate A = the C3 v3 P1/P2 certificate (unchanged; the LABEL only).
Certificate B = a second, legitimate operational certificate for the same macroscopic phenomenon. It
shares no machinery with A:
- B-P1 (persistence): the cue is decodable from full_state at q by a DIFFERENT estimator class (nonlinear
  k-NN or random-feature classifier), trained and tested on INDEPENDENT episodes, against a
  label-permutation null.
- B-P2 (causal use): at t = k, replace each episode's state with the state of an INDEPENDENT pool episode
  (independent cue, independent noise). This is a marginal-resampling intervention, not a paired swap.
  Effect = J_intact - J_resampled, from an unpaired two-sample test; the readout is trained fresh.
- Classes NONE / PASSIVE / FUNCTIONAL follow the same logic.
Before any law is fitted, B must pass its own planted calibration (the C3 calib.py systems plus the
chaos control in s6).
S3 pass: A/B agreement (Cohen kappa) is reported per family; the candidate's LOFO BA under B is within
0.05 of its LOFO BA under A; and the candidate passes S0 s4(a) under both labels.
If A and B disagree (kappa < 0.6) in any family, the phenomenon is certificate-dependent there. Those
worlds are reported and excluded from law claims in that family.

## 4. Admissible coordinates (gate S1: the machinery firewall)
Coordinates are measured on TASK-FREE runs of the world through the generic System interface (init,
noise, step, full_state, readout_features), driven by i.i.d. distractor input only.
MAY use:
- single, unperturbed trajectories;
- unconditional statistics of full_state / readout_features at ANY lag (autocovariance, spectra,
  effective rank);
- input-conditioned statistics at lags 0 and 1 only (the injection);
- native parameters with their declared units.
MAY NOT use:
- twin or paired trajectories of any kind, including a common-random-number twin at a random site;
- swaps, interchanges, ablations or resampling interventions;
- any quantity conditioned on an input at lag >= 2;
- any readout trained on task labels;
- anything imported from, or computed by, certify/probe/gate/calib or the C3 coordinate code;
- any C3 coordinate, including G-0006's.
Enforcement (all must pass before any law search):
(i) AST import audit: the coordinate module imports only numpy and the System interface.
(ii) Machinery-mutation test: coordinates are bitwise unchanged when the certificate code, its seeds or
     the task pairing are changed.
(iii) Lag-horizon guard: the runner does not STORE input identities older than 1 step, so lag-k
     information cannot be measured, only predicted.
(iv) Re-encoding suite (the T-C1 idea): coordinates are invariant, within their bootstrap SE, under an
     invertible linear re-basis of both views, duplicated components, and re-encoding of discrete
     variables. Only whitened / affine-invariant statistics can pass this.
Candidate quantity families (EXAMPLES from the directive, not commitments; the data may reject them):
- characteristic timescale (whitened autocorrelation decay of full_state and of the readout view);
- per-step innovation / noise share (one-step linear predictor residual, whitened);
- input gain (lag 0-1 variance share driven by the input);
- readout bandwidth (canonical correlations between readout_features and full_state);
- redundancy (effective rank / participation ratio);
- perturbation amplification WITHOUT twins (single-trajectory nearest-neighbour divergence, e.g.
  Rosenstein, on a whitened embedding);
- recurrence structure;
- maintenance cost where a family declares energy/compute in native units.
Laws compose these into accessibility; no law form is written before S1/S2 pass.

## 5. Family blindness (gate S2)
- Report the leave-one-out family predictability of the coordinate vector (1-NN and logistic) as
  Cohen's kappa against chance.
- WARNING if kappa > 0.30 (C3's coordinate set had ~.65).
- Under a WARNING the law must pass all three dependence tests:
  (a) adding family one-hot to the law raises LOFO BA by < 0.02;
  (b) per-family refit thresholds agree with the pooled one (bootstrap CIs overlap);
  (c) per-family BA >= 0.75 in every family.
- LOFO is the primary evaluation throughout. Pooled fit is never evidence.

## 6. Planted calibration (before any real world is scored)
The instruments must recover known answers:
- a linear channel with known SNR(k) (the accessibility boundary follows analytically);
- a delay line (perfect memory, no noise);
- a PURE-CHAOS control: an expanding map that registers any perturbation but carries no
  cue-consistent information at q. T3-DOWN calls it FUNCTIONAL; it is NONE by construction;
- a PASSIVE control: history persists in a component the readout cannot see;
- a cheat control: a coordinate that illegally reads the certificate. The S1 audit must catch it.
If calibration fails, the instrument is not qualified and nothing is reported.

## 7. Counterfactual intervention (gate S4)
At least one frozen prediction of the form do(native knob a -> b) -> predicted class and J change. It is
made from PRE-intervention upstream measurements before the post world is measured, and it qualifies
only if all of the following hold:
- the knob is not the certificate's variable (not the cue channel, not the readout cut, not the
  history-bearing state itself);
- the prediction is not implied by the certificate definition. The target arm is "the perturbation is
  still registered (the T3-DOWN precondition stays true) but the upstream property moves", e.g. more
  noise per step or more amplification. The predicted outcome is FUNCTIONAL -> NONE, where T3-DOWN
  predicts no change;
- it carries a matched opposite arm (the T-H1 design): the correlates move while the upstream
  quantity is held fixed, with a predicted NO change.

## 8. Visible-data S0 analysis (executed 2026-09-30 on the 120 C3 visible worlds; development data)
F-0001 rules, 113 determinate worlds, FUNCTIONAL target. Families are aliased F1-F3 here; the detail is
withheld (local commit 197daf5f3, S0_VISIBLE.json sha256 7b0a1341ac5deaa75107129846447d2e6895605a040fbe80f3ff2bbc328ec535;
s0_visible.py sha256 23f2d745e88121557fba008d197b6daec81a69dfcb15a7619ba57faf2273c014).
| rule | pooled LOFO BA | worst-family BA | accuracy |
|---|---|---|---|
| T0 majority (= T1a) | .500 | .500 | .673 |
| T1b family-ID (leakage reference) | .752 | .500 | .788 |
| T2a shared task parameter (delay) | .428 | .434 | .566 |
| T2b within-family native ceiling | .825 | .625 | .858 |
| T3-DOWN zero-parameter certificate rule | .905 | .500 | .938 |
OBSERVED
- T3-DOWN makes 7 errors, ALL false positives (a perturbation registers but carries no usable
  history), in two families.
- A candidate that is right wherever T3-DOWN is right passes F-0001 s4(a-c) only if it corrects >= 6
  of those 7 with zero new errors.
- Power (synthetic; T3-DOWN errors false-positive as observed). Probability of passing S0 for a
  candidate that corrects 70% of T3-DOWN errors and adds 2% new errors:
  | n determinate | failure-regime share of negatives .19 (C3 visible) | .35 | .50 |
  |---|---|---|---|
  | 120 | .14 | .72 | .94 |
  | 240 | .34 | .995 | 1.00 |
  | 480 | .46 | 1.00 | 1.00 |
  (200 simulations per cell.) A weaker candidate (corrects 50%) passes only .05-.12 of the time at the
  C3 share, and less often as n grows, because its expected margin is below .05.
INFERRED
- On a C3-like world distribution, the zero-parameter semantics explain almost everything (a STOP
  condition). S0 there is close to a perfection gate, so a C4 run on such a distribution would stop
  for lack of headroom, not for lack of physics.
- The only place an upstream law can earn credit is where perturbation and information diverge:
  continuous noise that swamps the signal, and chaotic amplification. That is exactly the C4 question.
CONCLUDED (design decisions)
- C4's visible sample needs >= 240 determinate worlds and >= 4 families, of which at least 2 are new
  mechanisms.
- A LABEL-BLIND sampler, preregistered from native semantics only (declared noise and
  gain/criticality knobs), must put >= 50% of worlds in high-noise or near-critical strata.
- The C3 visible worlds are BURNED for scoring and serve as development data only.

## 9. Sequence (each step gated; nothing after step 1 is authorized yet)
1. DESIGN (this file) + S0 frozen (F-0001) + visible S0 analysis. DONE 2026-09-30.
2. Pre-result adversarial review of this design (research/PRE_RESULT_REVIEW.md). The reviewer must not be
   an adjudicator of a later C4 holdout.
3. Freeze the C4 preregistration (F-0002): families, sampler, coordinate module spec, Certificate B,
   calibration suite, S1-S4 thresholds, stop rules, precommitments (mechanism-level, losable).
4. Build + calibrate the instruments (s4 audits, s6 planted suite). Every verification stores rule text,
   code sha256 and input hashes.
5. Visible-world gates S0 -> S1 -> S2 -> S3 -> S4 on FRESH worlds. The first STOP ends C4 with "no
   successor law earned" (s10).
6. Only if every visible gate passes: a SEPARATE D2 compatibility determination (s11), or a new holdout
   commission.

## 10. Stop conditions (operator 2026-09-30, each mapped to a check)
| stop | check |
|---|---|
| zero-parameter semantics still explain almost everything | F-0001 s4(a-c) fails vs T3-DOWN |
| coordinates remain strong family identifiers | S2 WARNING plus any dependence test (a-c) failing |
| performance collapses under LOFO | LOFO BA fails S0 although the pooled fit would pass |
| results depend strongly on one certificate | S3 fails (BA under B more than .05 below A, or S0 fails under B) |
| the only successful intervention moves the label-defining quantity | no S4 prediction qualifies under s7 |
| no compact substrate-independent representation | law complexity above the preregistered cap, or a per-family exception term needed |

## 11. D2 policy
D2 stays SEALED / UNREAD / UNSPENT. C4 is not designed around D2, and nothing about D2 informs any
choice here. Whether D2 is a valid untouched adjudicator for C4 is decided SEPARATELY, only after the
visible gates pass, against the operator's four conditions:
(1) the original functional contract is compatible (C4 coordinates need only the generic System
    interface, and Certificate B needs the same interface; this must be checked, not assumed);
(2) no required D2 information leaked during development. This includes the 2026-09-30
    ciphertext-grep incident, which is REPORTED_FOR_RULING in c3/INFO_LEDGER.md;
(3) the C4 prediction can be frozen without inspecting D2 outcomes;
(4) there is no protocol mismatch, for example D2's delays or alphabet outside C4's calibrated range.
The determination should be made by a seat other than Cosmos. If any condition fails, D2 is preserved
for another claim and a new holdout is commissioned.

## 12. Open for the operator
Q1 Execution authority: steps 2-5 on visible worlds (instrument build, calibration, gates). The
   directive authorizes design and baseline analysis; is the visible-world build authorized now, or
   after the design review?
Q2 New families: C4 needs >= 2 new mechanisms. If they are Cosmos-authored, the author lineage stays at 1
   (T-G1), so a visible pass is Z1 only. Should a foreign seat author one visible family now (not a
   holdout)?
Q3 Design reviewer: which seat? (Harmonia is the natural D2 auditor, so another seat may be preferable.)
