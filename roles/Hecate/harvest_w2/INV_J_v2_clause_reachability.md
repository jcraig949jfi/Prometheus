# INV_J v2 -- clause reachability audit of the 16 Pass 3 v2 worlds

Date: 2026-09-30. Auditor: Claude agent, read-only; this file is the only write. Scope:
hecate/programs/HT-*/worlds/W5|W6 under roles/Hecate/prereg/2026-09-30_pass3_v2/PREREG.md, plus the
8 probed worlds (hecate/programs/PROBE_ROUND3_SELECTION.jsonl, probe/OUTCOME.json). Existing Pass 4
files are cited.

The freeze rule required that the positive control (PC) attain each success clause and the null twin
miss it. This audit asks five more questions:
- Q1: does any treatment implementing the mechanism pass by construction?
- Q2: does the clause reject the obvious simpler mechanism?
- Q3: did pre-freeze revisions move a threshold, statistic or the world toward the PC, and by how
  much?
- Q4: what does a parity clause prove?
- Q5: would a probe outcome change under a stricter, pre-freeze-justifiable reading?

Auditor runs: scratch copies of controls.py in the session scratchpad, never in place, each < 60 s.
Exploratory, not probes. [A1] and [A2] reuse frozen code paths with one arm added; in [A3]-[A5] the
auditor wrote the arm from spec text.
- [A1] 056d W5: per-component windowed NIS_j alarm, sparse reopening, h calibrated on seed 999 by
  the spec's rule, eval seeds 0-4.
- [A2] 5516 W6: FTLE readout at tau = 1 (not 8), and at eps_g = 0.10.
- [A3] ae38 W6: the spec's undamped-Newton labeller, seeds 0-1, frozen measure()/fit().
- [A4] e106 W6: the spec's persistent-residue treatment; 1 seed, 2000 burn-in + 30000 epochs (spec:
  100000), auditor RNG stream.
- [A5] 37e3 W6: vertical arm (twin loop minus the re-pairing line) and a vertical arm without
  selection, seeds 0-3.

Classes: SOUND (no material defect); PASSES_BY_CONSTRUCTION (the mechanism, implemented at all,
meets the success clauses); NON_DISCRIMINATING (a familiar simpler mechanism also meets them);
GOODHARTED (threshold, statistic or world moved toward the PC's reach); UNCLEAR (needs a run nobody
has done). Where two apply, the first is binding.

## 1. Classification table

| world | class | key evidence (detail in section 2) |
|---|---|---|
| 056d W5 | SOUND | per-component NIS_j alternative fails S1/S3 ([A1] 24 steps vs bar 10.8) |
| 056d W6 | NON_DISCRIMINATING | generic adaptive follow-up not excluded (self-declared) |
| 37e3 W5 | GOODHARTED | S1 statistic swapped after a PC knife-edge; new one does not test "abrupt" |
| 37e3 W6 | SOUND | [A5] plain vertical arm on the edge (D 0.093, ratio 0.47); drift D -0.01 |
| 5516 W5 | GOODHARTED | S1 0.15 -> 0.08, S3 0.15 -> 0.06 to fit under PC 0.103 |
| 5516 W6 | PASSES_BY_CONSTRUCTION, NON_DISCRIMINATING | [A2] tau = 1 gives ARI 1.0; Pass 4 ALT non-chaotic carriers ARI 1.0 |
| 8a87 W5 | PASSES_BY_CONSTRUCTION, NON_DISCRIMINATING | every MUS has size 2; channel reset ties exactly (Pass 4) |
| 8a87 W6 | NON_DISCRIMINATING, GOODHARTED | GREEDY_REF meets all 3 clauses; S1 relaxed from beat to parity |
| 9744 W5 | NON_DISCRIMINATING (S2), mild GOODHARTED | HIGH arm has no pressure by design, so S2 restates S1; lambda changed to rescue the PC |
| 9744 W6 | SOUND | S1 tightened 0.40 -> 0.60 (anti-Goodhart); S2, S3 follow from S1 |
| ae38 W5 | SOUND | threshold raised away from the twin; scope caveat (box safety vs verifier) |
| ae38 W6 | PASSES_BY_CONSTRUCTION (likely) | [A3] alpha 0.33/0.32 << 0.80; only F2 (R^2 0.946 vs 0.95) stands between it and SIGNAL |
| e106 W5 | UNCLEAR | clauses sound, but the PC is not censored like the decoder; 79% of blocks at the cap |
| e106 W6 | PASSES_BY_CONSTRUCTION (F2/F3 also forced) | [A4] F 28.5, 97% of epochs at s = 24, residue 11 -> 252 bits: NULL by construction |
| faa9 W5 | PASSES_BY_CONSTRUCTION | eta normalised to the PC's eps; analytic B ~0.22 vs bar 0.15 (self-declared) |
| faa9 W6 | GOODHARTED (harmless here) | lesion, noise and PC carving searched over 3 revisions to separate PC from FIXED |

Counts: 4 SOUND, 5 PASSES_BY_CONSTRUCTION (one "likely"), 3 NON_DISCRIMINATING, 3 GOODHARTED, 1
UNCLEAR. Both round-3 SIGNALs (5516 W6, 8a87 W5) are PASSES_BY_CONSTRUCTION worlds.

## 2. Per world, per clause

### HT-056d3ac561 W5 (M3+M8, stride-MR reopening). Probed: NULL.
- **S1 (median latency <= 12).** Not by construction (treatment 75). Redundant: S3 needs <= 10.8
  given NIS 18.
- **S2 (FA <= 0.10).** NO_REOPEN meets it (FA 0.00): a guard, not a discriminator.
- **S3 (ratio to isotropic NIS <= 0.60).** Q2: the spec's named alternative (per-component NIS,
  sparse reopening) was run as [A1]: median 24, FA 0.045, ratio 1.33. It fails S1 and S3 (the max
  over 8 components raises its threshold), so S3 rejects the obvious sparse alternative. Rough
  reach: a per-component CUSUM at J = 1.5, R = 1 detects in about 2 ln(ARL)/(J^2/R), 9-10 steps,
  plus recovery. The 10.8 bar is attainable only by a near-optimal detector.
- **Q3.** No clause moved (rev 1: wording, secondary observable). J was chosen pre-treatment so NIS
  = 18 leaves room both ways.
- **Q5.** NULL stands under any reading (75 vs 10.8).

### HT-056d3ac561 W6 (M9, SBL-guided test selection). Unprobed.
- **Q1.** Not by construction: fixed-Gaussian greedy is data-independent (Riccati) and scores 0.28.
- **Q2.** Clauses compare only with random and fixed-Gaussian greedy. A "follow up on large
  residuals" rule without Kalman machinery would very likely reach 0.43-0.60; the notes concede a
  pass cannot separate M9 from adaptive group testing.
- **Q3.** Budget 12 -> 24 (oracle 0.86 at 12) before any threshold existed. It raised random (0.05
  -> 0.23) as well as the oracle: neutral.

### HT-37e311ce05 W5 (M5, coset cheating). Probed: NULL.
- **S1.** Rev 0: sharpness (gbar(m*-8) - gbar(m*+8))/drop >= 0.6, PC 0.659 (margin 0.06), twin
  0.459. Rev 1: completion (gbar(12) - gbar(36))/ (gbar(12) - gbar(60)) >= 0.8, PC 0.931, twin
  0.627. Q2/Q3: swapped after the PC values were seen, and it drops the hypothesis's word "abrupt":
  a gap falling linearly from m = 12 to 0 at m = 36 scores completion 1.00. Completion tests
  "finished by m*+8", not "collapses at m*". GOODHARTED: the PC margin doubled (0.06 -> 0.13) for a
  weaker claim.
- **S2 (mean gap at m >= 40 <= 0.05).** Gaps can be negative, so any reward deficit passes
  (treatment high-m gaps -0.01 to -0.045). It cannot separate "coset closes" from "population
  stopped earning the reward".
- **Q5.** Completion 0.732: neither S1 nor F1 (0.65). Stricter rev-0 sharpness 0.487 < 0.6: still
  NULL. Only a looser reading (>= 0.7) flips it.

### HT-37e311ce05 W6 (M2+M9, partner-specific complementarity). Unprobed.
- **Analytic range.** With R_own = 0, D = R_other is about P(a symbiont class is among a random
  host's 5 of 24) = 0.208 (PC 0.211). The bar 0.10 is about half of D_max. Coalescence also lowers
  R_other, so D needs diversity across pairs as well as complementarity.
- **Q1.** Not by construction: [A5] vertical selection gives D 0.093 (bar 0.10) and R_own ratio 0.47
  (bar 0.5), both on the edge.
- **Q2.** [A5] vertical without selection gives D -0.011 and R_own 0.216, so the clonal-family
  explanation fails. "Any additive complementarity" cannot be separated: here class-avoidance is
  complementarity (disclosed).
- **Q3.** No revisions.

### HT-55162c0ac0 W5 (M10, chaos causes item loss). Unprobed.
- **Q3.** S1 and S3 started at 0.15. The PC reached 0.103 and no absorbing threshold in {0.02, 0.03,
  0.05, 0.08} reached 0.15. S1 was moved to 0.08 (-47%), S3 to 0.06 (-60%): GOODHARTED, set just
  under the PC.
- **Margin.** S1 margin 0.023 is about 1.0 null SE (0.022). On fresh draws the PC would miss S1 ~15%
  of the time (normal approx.). The treatment uses seeds 100-104; attainability was shown on seeds
  0-4 only.
- **Q2.** S3 adjusts for mean off-diagonal strength, not for "which entries were perturbed" (named
  in the alternative).

### HT-55162c0ac0 W6 (M12, FTLE grouping under XOR coupling). Probed: SIGNAL.
- **Analytic.** First-order per-pair transfer: structured kappa*E|v| = 0.1*(2/pi) = 0.064; leak
  (eps_g/N)*E|T'(v)| = (0.05/12)*4.31 = 0.018 (arcsine density). Ratio ~3.6 (0.55 log10; probe
  within-minus-between 0.77). Correlation ~0 by construction (odd map, symmetric density, product
  coupling). S1 (ARI >= 0.8) and S2 (gap >= 0.5) follow from the coupling coefficients for any
  perturbation readout.
- **[A2].** tau = 1 (a one-step finite difference, no finite-time divergence) gives ARI 1.0 on all
  10 seeds; eps_g = 0.10 also gives 1.0, so the rev-1 leak halving did not create the pass. Pass 4
  ALT: carriers classed non-chaotic reach ARI 0.73-1.0 (levels 0.5-0.8); predicate PARK.
- **Q2.** The NULL_TWIN (random partners) destroys the target, not the mechanism, so discrimination
  is automatic. The spec's own alternative ("intervention beats observation, not chaos") is exactly
  what passes.
- **Q5.** SIGNAL is valid under the frozen clauses. A stricter reading fixable pre-freeze ("chaotic
  carrier" must be load-bearing: tau = 1 or contracting knockout) gives CONFOUNDED for M12.

### HT-8a87057933 W5 (M1, core-guided forgetting). Probed: SIGNAL.
- **Q1.** Point clauses on one channel make every MUS a same-channel pair (probe mus_size_range
  [2,2]), so the treatment equals "keep the newest observation of the conflicting channel". The
  design notes estimated that rule at ~0.3 of drop-oldest BEFORE freezing; the treatment got 0.322
  (bar 0.50).
- **Q2.** Pass 4 ORIG: CHANNEL_RESET 1278 errors = core-guided 1278 (ratio 1.000, identical per
  seed).
- **Q3.** S1 0.70 -> 0.50 (stricter); S2 redefined stricter; S3 0.25 -> 0.50 (2x looser, not needed
  by the PC at 0.0, no reach rationale; treatment 0.147 passes either way).
- **Q5.** The spec's own alternative_explanation ("reset the channel that just mismatched") gives
  CONFOUNDED. Pass 4 recorded the kill later; the information existed before the freeze.

### HT-8a87057933 W6 (M4, hitting-set probing). Unprobed. See also section 3.
- **Analytic.** Any non-oracle needs >= log2 64 = 6.0 probes on average. The S1 bar 1.05 x 6.019 =
  6.32 leaves a success band [6.0, 6.32].
- **Q2.** GREEDY_REF, the named alternative, meets S1 (1.00), S2 (6.02 <= 9.0) and S3 (p95 6 <= 8).
- **Q3.** S1 0.95 (beat greedy) -> 1.05 (parity): +0.10 ratio, +0.60 probes. Correct (0.95 was
  oracle-only), but the clause can no longer favour M4.
- **Q1.** Not by construction: "lowest-index member of a minimum separating family that splits V"
  can pick unbalanced probes, so F1 (>= 1.15) is reachable. The world can fail M4 but cannot favour
  it.

### HT-974471f045 W5 (M2, bracketed inheritance). Unprobed.
- **S2.** The pre-freeze diagnostic gives the constructed reservoir an advantage of 0.825 at n = 8
  and 0.008 at n = 200. The HIGH arm is effectively drift, so S2 = G_LOW - G_HIGH is about S4. Any
  selection that deposits at n = 8 passes S2: the budget interaction, M2's distinctive claim, is not
  separated from "selection acts only where error is high" (stupid explanation 3).
- **Q3.** Rev 1 changed the instrument (ridge lambda 1e-6 -> 1e-2) and the PC (chain gain 2 -> 1)
  after PC G = -0.68, moving the ruler until the PC read 0.83 (justified: exact interpolation at n =
  8). Rev 2 (30 -> 60 generations, mutation 0.02 -> 0.05) eases the treatment. No threshold moved.
- **S3** (off-task channel) is a genuine content check.

### HT-974471f045 W6 (M14, eidetic variation). Probed: NULL.
- **Analytic.** corr^2(u1, u1 - u2) = 1/2 caps single-channel decoding at 0.5.
- **Q3.** S1 0.40 -> 0.60 on that ceiling, a stricter move that decided the outcome: at 0.40 the
  treatment (I_perp 0.4505, S2 0.400, S3 0.413) meets every success clause and no F clause, so it
  would read SIGNAL.
- **S2, S3.** With I_ones <= ~0.1 and twin I_perp 0.04, both follow from S1 >= 0.40: effectively one
  clause.
- **Q5.** NULL stands. Caveat: 0.45 < 0.5 does not show single-channel decoding; 0.6 is sufficient,
  not necessary. Template collapse is not in play (template-to-noise 1.79 vs twin 1.99).

### HT-ae38c641b1 W5 (M2+M14, box-verifier imprint). Probed: NULL.
- **Q1.** Not by construction (the generator expected 8-fold or no imprint).
- **Q2.** The clauses do not separate "a budgeted verifier imprints" from "any square safety region
  imprints"; a concrete box-safety gate was never an arm.
- **Q3.** Rev 0 -> 1 (affine -> linear) removed an unselected observable. The threshold went 0.30 ->
  0.40, away from the twin (3.1 null SD).
- **Q5.** S1 0.334 and S2 0.277 sit in the spec's INCONCLUSIVE band [0.15, 0.40), recorded as NULL
  (round-1 class). At 0.30, S2 still fails: NULL. Per seed values are bimodal (~+0.95 or negative:
  clonal drift; SD of the mean 0.15). No stricter reading changes it; the recorded NULL is harsher
  than the spec's own reading.

### HT-ae38c641b1 W6 (M8, fractal sign boundary of undamped Newton). Unprobed.
- **Q1.** [A3], the spec's labeller through frozen measure()/fit(): seed 0 alpha 0.329, R^2 0.946,
  coarse/fine slope 0.50/0.21, label 0 ~6%; seed 1 alpha 0.316, R^2 0.946. S1 (<= 0.80) and S2 (twin
  0.99 - 0.33 >= 0.15) pass by a wide margin. Sign-only disagreement still gives alpha 0.65.
  Undamped Newton on a score with psi' = 0 points has chaotic orbits, so a small alpha follows from
  implementing the estimator at all.
- **Guard.** The success clauses cannot separate a fractal boundary from non-convergence speckle
  (fine 0.21 vs coarse 0.50 is the speckle signature). The only guard is F2 (R^2 < 0.95), and [A3]
  sits at 0.946.
- **Q3.** Data tuned for the twin's label balance only; no threshold moved.

### HT-e106e1603b W5 (M8, iteration count informs on w). Probed: NULL.
- **Q1/Q2.** Not by construction. G >= 0.20 / min >= 0.10 is met by any t that is a less noisy
  function of w than s is, including a monotone count with no criticality; "near-threshold slowing"
  is only a premise check (F2).
- **Attainability evidence.** The PC's t is an uncensored formula peaking at w/n = 0.07, but the
  decoder saturates: 79% of blocks at the 60 cap (99.5% for p 0.06-0.09; 17% even for p 0.02-0.04).
  With p ~ U[0.02, 0.12] mostly above the min-sum threshold at n = 504, a censored t was nearly
  forced; the NULL is partly a world artefact.
- **Q3.** The PC was weakened (jitter 0.10 -> 0.40): anti-Goodhart.
- **Q5.** NULL stands (G 0.027, F1 fires).

### HT-e106e1603b W6 (M2, redundancy thermostat with residue). Unprobed.
- **Q1.** With "failure = e nonzero after scrub" and e persistent, one quiescent residue fails every
  epoch until new flips dislodge it (~0.02 flips/epoch at s = 24). [A4]: failure rate 0.965; s = 24
  on 97% of epochs; F = Fano(1000)/Fano(10) = 28.5 (bar 2.0); failure runs median 255, max 26892;
  residue 11 -> 252 bits from first to last quarter.
- **Reading.** S1-S3 pass by construction, and F2 (saturation > 0.5) and F3 (residue growth > 2
  bits) fire by construction: a faithful treatment reads NULL whatever M2 is, because the world
  counts one defect many times.
- **Q3.** Rev 1 extended the world (S_MAX 15 -> 24, p = 0.04*0.75^s) after the PC failed S1 (1.72 <
  2.0), then weakened the PC (F 32 -> 7). The world moved toward the PC; thresholds did not. S3 (>=
  0.34) follows from S1.

### HT-faa9277e02 W5 (M9, STDP tissue arrow). Unprobed.
- **Q1.** By construction (design notes agree). eta makes the jitter-free equilibrium eps = 0.2, the
  PC mean. After one decay time eps = 0.198*e^-1 = 0.073; interpolating CALIBRATION (0.05 -> 0.153,
  0.1 -> 0.301) gives B ~0.22 vs the S2 bar 0.15. Jitter (~8% reversed edges) lowers it a little.
  S1: P = sum g*eps / sum g|eps| ~0.8-0.9 for mostly positive eps. S3, S4 follow from S2 (scrambled
  twin B ~0).
- **Q3.** The bar (0.15, eps ~0.05) and the forecast (0.22) appear together in the notes; the record
  does not show which came first. Either way eta, a treatment parameter, was normalised to the PC.
- **Q2.** Any antisymmetric timing rule under one-way waves writes the same arrow; the reversed-wave
  F4 only checks code orientation.

### HT-faa9277e02 W6 (M6+M1, Hebbian repair memory). Probed: NULL.
- **Q3.** Three revisions: lesion 16 -> 24, lesion noise 0.01 -> 0.3 (FIXED r 0.86 at rev 0; RIF
  0.145 after), and PC carving picked from 4 variants by best separation from FIXED (boundary-only
  cut, RIF 0.381). Thresholds were then placed between them: world and PC tuned toward PC
  separation.
- **Q1/Q2.** Not by construction; the Hebbian rule does not produce boundary carving (predicted in
  the notes).
- **Q5.** Treatment RIF 0.009 (below FIXED 0.145 and twin 0.018): NULL under any reading; the tuning
  did not matter.

## 3. Q4: parity and twin-relative clauses -- what passing proves

- **8a87 W6 S1 (ratio to greedy <= 1.05).** Passing proves only "at most 5% worse than greedy
  information gain", and GREEDY_REF passes S1-S3 itself. A SIGNAL would say M4 is at most equivalent
  to its own simpler alternative (the notes: "adds a name, not a mechanism"). A parity clause can
  falsify (F1) but cannot support; under burden symmetry a parity pass is not support.
- **Implied clauses.** These "beats the twin by X" clauses follow from an absolute clause because
  the twin sits near 0: 9744 W5 S2/S4; 9744 W6 S2/S3; e106 W6 S3; faa9 W5 S3/S4; 056d W5 S1 (from
  S3). They add no discrimination; the effective number of independent clauses is about half the
  count on paper.
- **Target-destroying twins.** 5516 W6 (random partners vs nominal partition) and 8a87 W5 (random
  drop) remove the target, not the mechanism, so discrimination against them is free.

## 4. Q5 summary for the 8 probed worlds

| world | recorded | stricter pre-freeze-justifiable reading | changes? |
|---|---|---|---|
| 056d W5 | NULL | any | no |
| 37e3 W5 | NULL | rev-0 sharpness >= 0.6 (0.487) | no |
| 5516 W6 | SIGNAL | chaos must be load-bearing (tau = 1 knockout, [A2] ARI 1.0) | YES -> CONFOUNDED for M12 |
| 8a87 W5 | SIGNAL | must beat the spec's named alternative (channel reset, ratio 1.000) | YES -> CONFOUNDED |
| 9744 W6 | NULL | any (already strict) | no (a looser 0.40 would give SIGNAL) |
| ae38 W5 | NULL | any | no (spec: INCONCLUSIVE band) |
| e106 W5 | NULL | any | no (partly a cap artefact) |
| faa9 W6 | NULL | any | no |

Under the stricter readings round 3 has 0 SIGNALs, not 2. The PREREG falsification count
(unattainable, INSTRUMENT_FAIL or NO_FREEZABLE_WORLD >= 3 of 8) is unaffected: every world froze and
every control reproduced. But the repair produced attainable worlds, not discriminating ones, and
both positive readings were decided by construction.

## 5. Cross-cutting findings

1. **Attainability was checked against the PC, never against the named simpler alternative.** In 4
   worlds the spec's own alternative_explanation or stupid_explanations names a mechanism that meets
   the success clauses: 8a87 W5 (channel reset), 8a87 W6 (greedy), 5516 W6 (any perturbation
   readout), 056d W6 (adaptive group testing). This supports LEDGER Q6's rule: build the
   self-declared alternative as an arm before freezing, and freeze only if it fails at least one
   success clause.
2. **Threshold moves were mostly toward strictness** (8a87 W5 S1, ae38 W5, 9744 W6). Toward the PC:
   5516 W5, 8a87 W6 S1, 8a87 W5 S3, 37e3 W5 (the statistic swap). The commoner Goodhart form moved
   the world, instrument or PC: 9744 W5 lambda, e106 W6 S_MAX, faa9 W6 lesion/carving, 056d W6
   budget. The PREREG records revisions but does not require each to state which way it moved the PC
   margin or the treatment's expected reach.
3. **Two worlds were decided by the world, not the mechanism**: e106 W6 (success and failure both
   forced: NULL by construction) and e106 W5 (79% censoring: NULL nearly forced). Requiring the PC
   to pass through the same censoring/saturation path as the treatment would have caught both.
4. **One world hangs on a fit-quality guard at a knife-edge**: ae38 W6, F2 R^2 0.946 vs 0.95 in
   [A3].

## Summary (<= 120 words)

All 16 worlds froze correctly, but the freeze never tested the simpler mechanism each spec itself
named. Classes: 4 SOUND (056d W5, 37e3 W6, 9744 W6, ae38 W5); 5 PASSES_BY_CONSTRUCTION (5516 W6,
8a87 W5, ae38 W6 likely, e106 W6, faa9 W5); 3 NON_DISCRIMINATING (056d W6, 8a87 W6 parity, 9744 W5
S2); 3 GOODHARTED (37e3 W5 statistic swap, 5516 W5 0.15 -> 0.08/0.06, faa9 W6 world tuning); 1
UNCLEAR (e106 W5). Both round-3 SIGNALs fall to a stricter pre-freeze reading: 8a87 W5 equals
channel reset (ratio 1.000), and 5516 W6 reaches ARI 1.0 with a one-step perturbation. That leaves
zero SIGNALs. No recorded NULL changes. e106 W6 reads NULL by construction.
