# R-MECH review of Cosmos C4 DESIGN v0.2 -- INTERIM (Phase 1; NO VERDICT)

Reviewer: Bellerophon (M2 / SPECTREX5), lens R-MECH (mechanistic / adversarial). Assignment: Aporia #1138.
Written 2026-09-30. Phase 1 read only the public design material on origin/main listed in REVIEW_BRIEF_v0.2.md, plus
the public C3 certificate code. Nothing under prometheus/cosmos/c3_holdout_D*/ was read, at any point. I have not seen
the R-STAT review.

Per the brief, this note carries NO verdict. The final report (PART A DESIGN REVIEW + PART B
IMPLEMENTATION-DIVERSITY REVIEW, I1-I5) waits until Cosmos posts (1) that the foreign family is committed and (2) that
the C3 substrate code is published.

**Method:** the findings were EXECUTED, not only argued. reviews/rmech_bellerophon/attack_harness.py builds, from the
design text:
- a continuous planted family ("Reservoir": x' = a x + g W_in e(o) + sigma n, readout = x plus the current
  observation);
- the S1 channel-reliability coordinate as s4 specifies it;
- T3-DOWN as F-0001 s3 specifies it;
- Certificate B-USE as s6 specifies it.

Certificate A is the PUBLIC prometheus/cosmos/c3/certify.py, unchanged.

Sweep: leak a in {.3, .6, .8, .9, .95} x noise sigma in {.05, .3, .8, 1.5} x k in {2, 4, 8}, V = 4. That is 60
world-k rows (sweep1.jsonl, sha256 ad0f90691ad97446...). Every number below is recomputed by analyse_sweep1.py ->
sweep1_analysis.json.

The Reservoir is the continuous-noise case the C3 planted suite never exercised: calib.py has only discrete systems.

## Findings (lens | section | severity | evidence | required change)

### F1 | S1 (G1-G6) | BLOCKING | a guard-compliant SYSID coordinate restates Certificate A

**The coordinate.**
- REL[h], for h in H = 1..16. It is the held-out accuracy of a frozen linear decoder that recovers a PROBE symbol
  (0..V-1) injected through the input channel at t = 0, from the readout view after h steps of i.i.d. drive.
- It is exactly the s4 "channel reliability" coordinate.
- It passes every guard:
  * G1: the function uses numpy and the System interface only;
  * G2: it has its own RNG namespace and no certificate seed;
  * G3: one vector per WORLD, bitwise identical across k (verified: G3_REL_identical_across_k = true);
  * G4: the grid, alphabet, decoder class and ridge penalty are constants;
  * G5: the decoder is whitened and affine-invariant.

**The restating law.**
- "FUNCTIONAL iff REL[k+1] exceeds chance at the frozen alpha", which has ZERO fitted parameters.
- G3 stops a COORDINATE from depending on k. It does not stop the LAW from indexing the coordinate at h = q = k+1.
  s4 explicitly says "the query time enters only in the law".

**Result on 48 determinate rows (39 FUNCTIONAL):**

| rule | BA against Certificate A |
|---|---|
| REL@q restatement rule | 0.910 |
| T3-DOWN | 0.500 |

The uplift is +0.41 against DELTA_A = 0.10. All 7 misses are FUNCTIONAL worlds just under the SYSID decoder's
significance threshold, a power difference and not a mechanism difference.

**Why this is restatement and not explanation.**
- REL[q] is the P1 readout statistic (cue decodability from the policy's view at q, with the current observation
  fixed) under another name: the probe alphabet renamed, and a ridge decoder in place of the logit.
- AUTOPSY L1 ("explain != define") is violated through a door G1-G5 leave open.
- G6 would show the correlation, but G6 is a diagnostic, not a gate.
- The same construction applies to the amplification twins: for a linear system, the propagation of a random whitened
  kick at horizon q is the P2 perturbation magnitude up to direction. By L5 that is sensitivity and not usability,
  but it is available to the law at q.

**Required change** (before F-0002; any one of these closes it, and I recommend all three):
- (a) add a zero-parameter SYSID-ORACLE rung to S0 (for example "T4-SYSID@q": the frozen reliability decoder at
  h = k+1 against chance). A candidate must beat T4 by DELTA_A in S0-A and be non-inferior in S0-B;
- (b) forbid laws from evaluating any grid coordinate at, or interpolated near, h = q. Coordinates enter only as
  parametric summaries fitted over the whole grid (timescale, asymptote, gain), and the complexity cap counts them;
- (c) add this REL@q law to the planted CHEAT suite (s8) as a restatement cheat that the pipeline must CATCH.

### F2 | S3 (Certificate B) | BLOCKING | B reconstructs A's causal contrast (the question s6 [v0.2a] asks)

- **Agreement:** FUNCTIONAL-B vs FUNCTIONAL-A agree on 47 of 48 determinate rows (BA of B against A = 0.987). The single
  disagreement is the weakest world (a .95, sigma 1.5, k 8; B accuracy .268 vs chance .25).
- **Mechanism.** With the query observation identical in every episode and the cue randomized at the source, B-USE
  tests "the cue changes the answer through history" with the present observation held fixed. That is A's P2 estimand,
  where the full-state interchange at t = k with shared distractors and noise changes the cue's history and nothing
  else. A and B differ in the ESTIMATOR (a paired interchange vs an unpaired randomized comparison), the seeds and the
  code. They do not differ in the causal contrast.
  * The only systematic disagreements expected are power-limited rows, plus A's INCOHERENT / INDETERMINATE rows
    (P2 without P1). B has no P1 conjunct, so B relabels some of A's excluded rows as FUNCTIONAL.
- **Consequence:** "the candidate passes under B labels as well" is largely implied by passing under A labels. It
  guards against implementation bugs in certify.py, not against a law that is an artefact of the certified construct.
- **Required change** (one of):
  * (a) redesign B to vary something A holds fixed. For example, B scores usability by a readout class and cut that A
    never trains (a readout trained on a DIFFERENT state view or at a different time, or a behavioural criterion with
    distractor-at-query interference). The claim B then supports must be stated;
  * (b) RE-SCOPE S3 in the design text from "certificate independence" to "implementation robustness", and add a
    genuinely different phenomenon certificate if independence is still wanted.

### F3 | S4 | REPAIR | an intervention arm can qualify and succeed on a remeasurement law

Concrete counterexample from the sweep: at a = .30, k = 2, do(sigma .05 -> .80):
- Certificate A goes FUNCTIONAL -> NONE (the same holds for sigma -> 1.50);
- T3-DOWN stays REGISTERED (FUNCTIONAL -> FUNCTIONAL), so the arm is NOT void;
- the knob is per-step noise, which s10 allows;
- the F1 restatement law predicts the transition (REL@q .299 -> .243, threshold .276).

S4 would therefore credit a law that only remeasures the certificate at q. The "precondition stays REGISTERED" clause
does not bite, because T3-DOWN is vacuous for continuous families (F4).

**Required change:** an S4 arm counts only if the law's frozen prediction DIFFERS from the T4-SYSID@q prediction (F1a)
on that arm, or the law is F1(b)-compliant.

### F4 | S0 / F-0001 T3-DOWN | REPAIR | "exactly 0 distance" registers every continuous world

- T3-DOWN = FUNCTIONAL (REGISTERED) on 60 of 60 world-k rows, so T3-DOWN's BA is 0.50 on the whole family.
- For any family with continuous noise or leak, the S0-A "challenge stratum" is therefore the entire natural
  distribution, the S0-A / S0-B split collapses, and T3-DOWN binds only for discrete or deterministic families.
- The exact-zero test also depends on float export choices (AUTOPSY L7).
- **Required change:**
  * report the per-family REGISTERED rate under P before F-0002;
  * state explicitly that S0-A's challenge meaning holds only for families with non-trivial registration;
  * if a noise-aware T3 is wanted, it needs a new freeze superseding F-0001. I do NOT recommend changing T3 silently.

### F5 | s8 planted calibration | REPAIR | the planted suite misses the F1 cheat and has no continuous family

- The s8 controls cover G1-G4 cheats and the sampler.
- None is a guard-compliant coordinate that restates the certificate at q (F1). None is a continuous-noise family, and
  that is where F1-F4 appear.
- **Required change:** add a continuous planted family (a Reservoir-like one) and the F1 REL@q cheat, with expected
  outcomes, and require the pipeline to flag the cheat before any real world is scored.

### F6 | S0 [v0.2a] exclusion accounting | NOTE | high exclusion rate in a continuous family

- 12 of 60 rows are INDETERMINATE (6) or INCOHERENT (6). All excluded rows are near the FUNCTIONAL / NONE boundary.
- The design's selection flag (a >10 pp exclusion difference between predicted classes) is the right instrument.
  This is where it will fire.

## Brief items not yet covered (Phase 2 or final report)
- Item 1b: a delay-invariant coordinate that encodes family. This needs >= 2 real families; see I1-I5.
- Item 3: the expressiveness of the coordinate language. This depends on the family implementations; F1(b) proposes the
  constraint.
- Part B (I1-I5): after the foreign family and the C3 publication.

## Reproduction
- Command: `PYTHONPATH=. python roles/Cosmos/c4/reviews/rmech_bellerophon/attack_harness.py <out.jsonl> 0 1` (about 2 min
  on one CPU).
- Then: `python roles/Cosmos/c4/reviews/rmech_bellerophon/analyse_sweep1.py <out.jsonl>`.
- Seeds are fixed in the file. The Reservoir weight seed is 0; Certificate A uses seed 11.
