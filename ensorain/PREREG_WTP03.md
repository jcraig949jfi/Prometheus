# PREREG WTP-03 — the substrate collider

Seat: Ensorain[m2-14baf7d5]. Date: 2026-09-24.
Authorization (verbatim): roles/Ensorain/prompts/2026-09-24_wtp03_authorization/.
Engine: ensorain/wtp3/ (world3, collider, preflight3, genome3, detect3, autopsy, controls, recipes, validate3, campaign3).
Rows: ensorain/runs/wtp03/.
WTP-02 is frozen as recorded: FROZEN SCORER EXPAND, OPERATOR SCIENTIFIC RULING PARK/REDESIGN
(ensorain/WTP02_OPERATOR_RULING.md).

This document is committed BEFORE any campaign row. Dev work used only seeds 9,100,000–9,999,999.
The dev findings that forced design choices are recorded in s13, so the design history is visible.

## 1. The question (auth s1)

Under necessity-bearing world physics, can any bounded substrate turn the SAME experience into
unseen-cell competence that the ladder of simpler nulls cannot explain?

## 2. Instrument: one stream, many substrates (auth s2, s10, s11)

EXPERIENCE STREAM. Each (world, seed, field) has one stream: the exact (step, cell, value) samples
that the world's CARRIER was told during its life. This includes the world's credit physics (delay,
noise, sign flips, radius). The carrier is a calibration-panel learner living under the world's own
physics (s5).

Every substrate and every null learns from that same stream. That gives same observations, same
actions, same world stochasticity, the same memory budget (cap = band x cells floats) and compute
counted in flops. A substrate that cannot fit the budget is recorded as INCOMPATIBLE and never
adapted to fit.

SUBSTRATES:
- simple:
  - constant (a running mean, 1 float);
  - table (dense lookup);
  - sketch (hashed/sparse);
  - additive (marginals);
  - mixture (table + marginals).
- structured:
  - lowrank (matrix);
  - cp;
  - tt;
  - dct (spectral);
  - hybrid_al (marginals + low-rank on the residual, one budget).
- not implemented, recorded:
  - symbolic rules (no such substrate exists in the engine);
  - graph/external memory (represented by N4 below).

RECIPES. Each structured substrate has one fixed training recipe (rule, lr, passes). It was chosen by
recipes.py on dev planted worlds (6 generators x 2 dev seeds) from one grid shared by every
substrate (runs/wtp03/recipes.json):
- lowrank, cp, tt: sgd .1 x 3;
- dct: nlms .1 x 1;
- hybrid_al: nlms .1 x 1.

Simple substrates:
- table: sgd 1;
- sketch: sgd .5;
- constant, additive, mixture: nlms .5.

TEST SETS. Only cells the training stream never touched:
- interp: unseen cells with a seen cell one coordinate away.
- novel: unseen cells with a coordinate value never seen.
- recomb (the s18 construction): choose value subsets H_m on every mode. Delete every stream sample
  with >= 2 coordinates in H. Test on the block H_1 x ... x H_D. Every H value is seen alone; no pair
  of H values ever is. p is tried in (.5, .4, .34, .25, .2); the block must have >= 64 cells, <= 60% of
  samples may be deleted, and every H value must survive. Otherwise recomb is not measurable.
- Each set: up to 512 cells; a set is scored only if >= 32 cells.

SCORE. AC = -log10(MSE/V0), where V0 is the birth variance (fixed), clipped to [-3, 6].

NULL LADDER. Batch fits (hindsight-favourable, so conservative) on the same stream:
- N0: zero.
- N1: optimal constant (stream mean and recent-25% mean).
- N2: marginal statistics (one-hot main effects, least squares).
- N3: tiny linear (index coordinates).
- N4: bounded lookup / graph-nearest-neighbour (cap/2 most recent distinct cells; predict the mean
  of the stored values at minimum Hamming distance).
- N5: strongest simple substrate within the budget: the online simple substrates above.

XC(substrate, set) = AC(substrate) - max over N0..N5 of AC(null). XC drives promotion; raw AC is kept.

## 3. Wave A gates (auth s4-s6, s20), in order

- G0 BUILD: legal field and graph; >= 64 cells.
- G1 BUDGET: cap >= sum(dims)+1 (marginals fit) and cap <= 0.25 x cells (memorisation impossible).
  Test cells are never in the stream in any case.
- G2 NONDEG: organism-free dry run, variance >= .1 V0, reach >= .3, rewards >= 1% (WTP-02 N5).
- G3 ECONOMY:
  - Rates are measured with metabolism 0 over min(T, 600) steps.
  - The trivial twins are random and frozen. A trivial life that traps itself in a sink counts at
    the rate it achieved.
  - The oracle reads the true field.
  - The CALIBRATION PANEL is additive, dct, lowrank, cp and tt, each with its recipe, replay
    consolidation (s6) and only if it fits the budget.
  - (i) INFORMATION VALUE at the cheapest price (kappa = .01): oracle_min > 0,
    oracle_min - trivial_max > .02 and > .2|trivial_max|. Else G3_INFO_VALUELESS.
  - (ii) the largest kappa in (1, .3, .1, .03, .01) (multiplying p_compute, p_read, p_write,
    p_probe, p_rollout; never 0, so information is never free) at which the best panel learner is
    FEASIBLE. Feasible means: with metabolism m := trivial_max + .25 gap (so the trivial twin loses
    and the oracle clearly wins), the learner's net rate is >= -.5 gap (not hopeless). Confirmed on
    2 seeds.
  - That learner becomes the world's CARRIER.
  - If the learner's net rate is negative, energy0 := max(energy0, 1.1 x .75 T x deficit + 10), so
    that it lives >= 75% of its lifetime.
  - Whether learning PAYS in life (learner - trivial >= max(.01, .1 gap)) is recorded, not gated.
- G4 EXPOSURE:
  - At the calibrated economy, trivial lives (300 steps, 2 seeds x random/frozen) end with U < 0,
    else G4_TRIVIAL_WINS.
  - Oracle (600 steps) U > 0, else G4_ORACLE_FAILS.
  - The carrier's full life reaches >= 75% of its lifetime, with >= 200 learning updates and
    >= 64 distinct cells in its stream, else G4_EXPOSURE.
  - Tracked: life fraction, updates, consolidations, conversions.
- G5 DEMAND: on the carrier's real stream, an UNBOUNDED batch planted mechanism (DCT least squares
  with <= min(n/4, 512) coefficients, low-rank ALS rank 4, CP-ALS rank 3) beats every batch null
  N0-N4 by >= .10 AC on interp or recomb. This covers "optimal constant insufficient" and
  "higher-order structure matters". The planted mechanism tests the INFORMATION in the stream, not
  a bounded substrate.
- G6 SURROGATE: the same excess on the marginal-preserving surrogate stream is <= max(.05, .5 x real).
  The surrogate keeps the mean, every per-mode marginal mean and the variance EXACTLY, and destroys
  interactions (the residual is permuted, re-centred on every mode and rescaled).
- Lineage cap: no founder lineage above 1.5% of the target (15 of 1,000). Mutants inherit their
  parent's root.

## 4. Search strata (auth s8, s19) and the physics changes, all declared

Candidate proposal:
- wild (45%): the WTP-02 grammar, all weirdness.
- clean_channel (25%): wild in every law except sensing and credit. Observation chain empty, noise
  <= .2, kind in {cell, fiber, masked}; credit delay 0, radius 0, sign_flip 0, noise <= .05.
- mutant (30%): mutation of an admitted world, or of one of the 50 best NEAR-MISSES, all under the
  lineage cap. A near-miss is a world rejected at G3-G6, ranked by learner margin (G3) or by
  .5 + demand (G4-G6).
- If there is no parent, the mutant share falls back to wild or clean.

WTP-03 physics that differs from WTP-02:
- (a) INFORMATION MARKET: every world has queries. A genome drawn with query_every = 0 has it
  redrawn from 3-40.
- (b) GRADED PAYOFF: a query pays query_reward x (1 - min(err^2/V0, 4)). The field mean earns about
  0, a learner earns in proportion to its R^2 on (mostly unseen) query cells, the oracle earns in
  full, and a worse-than-mean predictor loses. tol is unused. This replaces WTP-02's all-or-nothing
  tolerance.
- (c) REPLAY CONSOLIDATION for calibration-panel carriers: online learning plus, every 32 updates,
  2 sweeps over the last 256 samples.
- (d) information-cost scale kappa and the calibrated energy buffer (s3 G3).

## 5. Wave B — collision (auth s11, s13-s15)

For each admitted world at its admission seed:
- real, marg and shuf streams, each through the full panel and ladder at the native budget;
- on the real stream only:
  - the BUDGET LADDER: the panel at every band in (.01, .03, .10, .25) whose cap fits the marginals;
  - the EXPOSURE LADDER: stream prefixes of 25%, 50% and 100%.

Latent ratios recorded per world (s14):
- cap/cells;
- cap/DL, where DL = min(Fourier-90%-energy count, min over unfoldings of r90 x (rows+cols));
- updates per drift period;
- coverage;
- forgetting rate;
- n_org;
- door-close rate;
- kappa.

## 6. Detectors, each with a named null (auth s15-s18)

- X1 COMPLETION: a structured substrate with n_floats >= 8 has XC_interp >= .10, AND
  SD = XC_real - XC_marg >= .10.
  - Null: the marginal-preserving surrogate.
  - If the surrogate cannot be measured, there is NO claim.
- X6 RECOMBINATION: the same on the recomb block.
- X3 CROSSOVER: two panel substrates reverse order between ADJACENT budget (or exposure) levels,
  i.e. AC_A - AC_B >= .10 on one side and <= -.10 on the other, on interp or recomb.
  - Null: seed-split replication.
- X4 SUPERADDITIVE: hybrid_al AC >= max(additive, lowrank) + .10 at one budget, and that excess
  minus the surrogate's excess is >= .10.
- X7 CONVERSION (Wave G): converting the trained specimen into another structured kind (distillation
  that costs flops and workspace) gives XC_after >= XC_before + .10, AND it beats training the
  target kind directly by >= .10 (the conversion must be necessary).

Scalar and tiny substrates (constant, n_floats < 8) never fire X1, X6 or X4 (auth s3).

## 7. Waves C-G (survivors only)

- C REPLICATION: diverse selection of <= 48 flags (<= 12 per detector, <= 2 per lineage per
  detector, strongest first), 5 fresh seeds each (6,000,000+).
  - X1/X6/X4 statuses:
    - >= 3/5 hits, <= 1/5 surrogate hits, median SD >= .10: STRUCTURE-DEPENDENT;
    - >= 3/5 hits with >= 3 surrogate hits: STRUCTURE-INDEPENDENT;
    - 2/5: UNRESOLVED;
    - <= 1/5: FALSIFIED;
    - >= 3 units without a stream: DEGENERATE WORLD.
  - X3: REPLICATED if >= 3/5 seeds reverse, with >= 1 in each seed half.
  - Founder-level accounting throughout.
- D LOCAL PHYSICS (STRUCTURE-DEPENDENT specimens and REPLICATED crossovers):
  - Budget sweep over 7 geometric levels from sum(dims)+1 to .25 cells, x 4 seeds (offline, on
    each seed's own stream).
  - PHASE/CROSSOVER BOUNDARY: adjacent levels whose means differ by > 3 x pooled sd, same sign in
    both seed halves, with the phenomenon present on one side and absent on the other (for X3, the
    sign of the ordering flips).
- E CAUSAL AUTOPSY (3 seeds): ablate_half, shuffle_modes, reset, freeze (the never-trained
  substrate).
  - Each intervention records attempted / changed (parameter digest AND predictions) / magnitude.
    No change means NOT_APPLICABLE.
  - CARRIER: reset and freeze keep <= 20% of XC; each of ablate/shuffle is REMOVES (<= 50% kept) or
    NOT_APPLICABLE; at least one is REMOVES; holds on >= 2 of 3 seeds.
  - RESKIN NEGATIVE CONTROL: the trained substrate evaluated on the axis-permuted field must LOSE
    >= .10 AC on >= 2 of 3 seeds. A reskin-invariant "specimen" is scalar-like and fails.
- F TRANSFER / RECOMBINATION (3 seeds):
  - RECOMBINES: 3 fresh recomb blocks per seed, median XC >= .10.
  - TRANSFERS: the learned artifact, with no retraining, on a RELATED world with the same field
    (observation noise doubled + .05, policy changed) beats the related world's best null by >= .10
    on >= 2 seeds.
- G CONVERSION / HYBRID: s6 X7.

## 8. Promotion bar and verdict (auth s21, s22)

A specimen family is PROMOTED only if all of the following hold on the same flag:
1. STRUCTURE-DEPENDENT X1/X6/X4 (XC > .10, SD, replicated, beats N0-N5);
2. Wave E CARRIER + RESKIN LOSES;
3. at least one of {RECOMBINES, TRANSFERS, PHASE BOUNDARY on the budget sweep, X7 CONVERSION}.

Verdict:
- CANDIDATE PHYSICS FOUND -- DEEPEN: >= 1 promoted family (the founder lineage is the unit).
- SUBSTRATE PHASE STRUCTURE FOUND -- MAP: no promoted specimen, but >= 1 REPLICATED crossover whose
  boundary Wave D brackets.
- INSTRUMENT CLEAN, NO SIGNAL -- BROADEN: validation ALL_PASS and nothing survives.
- STILL EASY TO FOOL -- REDESIGN: validation fails, OR (seat adjudication, reported beside the rule
  and never in place of it) a trivial mechanism explains a promoted specimen.

Also reported:
- the admission rate and gate funnel per stratum;
- the fraction of admitted LINEAGES with a STRUCTURE-DEPENDENT X1/X6 (operator prior < .5%);
- per-world and per-founder statistics;
- whether XC winners track the world's carrier kind (the carrier-bias check);
- whether crossover locations collapse better on cap/DL than on cap/cells (CV of the boundary
  across worlds).

## 9. Wave sizes and budget

- Wave A: target 1,000 admitted, at most 200,000 candidates, at most 10 h wall, batches of 2,000,
  20 workers.
- If the target is not reached, the campaign proceeds with what was admitted; zero is allowed.

## 10. Instrument validation (validate3.py, fixed, run first; seeds 9,500,000+)

- V1 teeth: X1 fires in >= 2 of 3 planted worlds.
- V2 no false positive: on an additive field, max structured XC < .10.
- V3 scalar kill: on the WTP-02 #10 genome (lifetime 300, an unkillable carrier), the constant's XC
  <= 0 on >= 1 measured set. Vacuous fails.
- V4 determinism.
- V5 surrogate exactness plus structure destroyed.
- V6 intervention support: NOT_APPLICABLE on a constant; changed on a trained CP.
- V7 recombination teeth: X6 fires in the planted spectral world.

Dev run of this suite: ALL_PASS (runs/wtp03/validation.json is overwritten by the campaign run).

## 11. Seat predictions (losable)

- P1 (written AFTER the dev funnel in s13.6, which admitted 0 of 2,000):
  - Wave A admits <= 0.5% of candidates, and fewer than 150 worlds in 10 h.
  - The majority of admitted worlds are MUTANTS, of near-misses or of admitted worlds.
  - The first founder appears after more than 5,000 candidates.
- P2: the fraction of admitted lineages with a STRUCTURE-DEPENDENT X1 is 1-10%. The carriers are
  dominated by lowrank/cp/tt in lowrank/cp/tt/pairwise-generator worlds, i.e. matrix/tensor
  completion (KNOWN physics).
- P3: X6 (strict pair-block recombination) is rarer, < 2% of lineages, dominated by dct in spectral
  worlds.
- P4: replicated X3 crossovers exist in >= 3 lineages; the most common pair is a structured
  substrate against the N-class winner as the budget changes.
- P5: X4 superadditive < 1% of lineages.
- P6: verdict probabilities: DEEPEN .25 (a completion specimen passing the whole chain), MAP .30,
  BROADEN .35, REDESIGN .10.
- P7: at least one promoted or STRUCTURE-DEPENDENT flag carries a new counterfeit that the ladder
  misses (the seat's standing prior after WTP-01 and WTP-02). It will be searched for in the
  report.

## 12. What is NOT claimed in advance

- A completion specimen (lowrank/cp/tt/dct predicting unseen cells of a low-rank or smooth field) is
  KNOWN PHYSICS: matrix/tensor completion.
- If one is promoted, the report says so plainly. It is a positive control that the collider can
  see real structure, NOT a discovery.
- "Extraordinary" is reserved for something the known completion account does not predict: a
  crossover whose location collapses on a latent ratio, a necessary conversion, superadditivity,
  or recombination where completion theory says the block is unidentifiable.

## 13. Dev history that forced the design (dev seeds only)

1. The strict "no seen neighbour within Hamming 1" recombination set was EMPTY once coverage was
   high. It was replaced by the pair-block holdout (s2).
2. CP and TT diverged under the default NLMS recipe (AC -3). The recipe grid was run on planted dev
   worlds (s2).
3. Economy:
   - Random WTP genomes: learners earned no more than trivial walkers. With the WTP-02 all-or-nothing
     query tolerance, only oracle-grade predictions paid.
   - Information costs were often fatal (up to -186 energy per step for a DCT learner).
   - Trivial walkers trapped in sinks were rejected as degenerate worlds.
   These led to the kappa search, the graded market, the query market for every world, replay
   consolidation, and counting trapped trivial walkers as losing.
4. Even then, 0 of ~1,000 dev candidates passed a "learning must PAY" gate: in-life learners mostly
   lose to the zero predictor.
   - Offline, on clean-channel worlds with an unkillable carrier, 7 of 89 worlds (8%) had a
     structured substrate with XC_interp >= .10. Recomb was measurable in only 9 of 89.
   - The gate was reset to the authorization's literal conditions (trivial loses, a feasible
     learner survives, the oracle clearly wins), and in-life payoff was made a recorded property.
6. The final dev funnel with this exact preflight (seeds 9,900,000-9,901,999; 2,000 candidates with
   the wild and clean strata, no mutants) admitted 0.
   - Kill counts on the last 1,400: G1 561, G2 349, G3_ECONOMY 328, G3_INFO_VALUELESS 108, G0 39,
     G5 7, G4_EXPOSURE 4, G4_TRIVIAL_WINS 3, CRASH 1.
   - Every world that reached G5 failed it. The unbounded planted mechanism did not beat the nulls
     (excess -0.02 to -0.29), and several of those worlds came from the pure-noise generator.
   - The rarity is therefore expected, and it is itself a primary result of Wave A.
7. Pipeline smoke on a planted CP world (dev seed 9,990,101): X1 fired for cp and tt with SD around
   2.9, and replicated as STRUCTURE-DEPENDENT on 3 of 3 fresh dev seeds. That is known tensor
   completion, the positive control of s12. X6 (tt) did not replicate (1 of 3).
5. V5 first failed (approximate marginals); the surrogate was made exact.
   V3 first passed VACUOUSLY (no test cells); vacuous now fails.
   The completion detector counted a missing surrogate measurement as SD = XC; a missing null now
   means no claim.
