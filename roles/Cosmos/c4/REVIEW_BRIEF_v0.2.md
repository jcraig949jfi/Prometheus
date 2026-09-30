# C4 v0.2 -- brief for the two independent design reviews
(operator reviews 2026-09-30: s9 of prompts/2026-09-30_operator_c4_review/ and prompts/2026-09-30_operator_c4_review2_publication/)

Reviewers must NOT be:
- Cosmos (the author);
- Harmonia (kept clean for D2);
- Nestor (the D2 custodian);
- the foreign visible-family author.
The two reviewers work independently and do not see each other's review before submitting.
Do not read anything under prometheus/cosmos/c3_holdout_D*/ (D2), at any phase.

## Phasing
PHASE 1 -- START NOW (design material, all public on origin/main):
- roles/Cosmos/c4/DESIGN_C4.md (v0.2 + the [v0.2a] additions)
- roles/Cosmos/c4/S0_TRIVIAL_RULES.md (F-0001: the trivial rules; defines T3-DOWN)
- prometheus/cosmos/c4/power_s0.py + roles/Cosmos/c4/POWER_S0_v0.2.json
- roles/Cosmos/c4/VISIBLE_FAMILY_CONTRACT.md
- roles/Cosmos/research/reviews/AUTOPSY_C3_PUBLIC_2026-09-30.md (lessons L1-L7)
- the public C3 certificate: prometheus/cosmos/c3/{task,system,probe,certify,calib,gate}.py
PHASE 2 -- FINAL VERDICT ONLY AFTER BOTH hold (Cosmos will post on comms when they do):
(1) the foreign family is committed;
(2) the C3 substrate implementations are public (c3/PUBLICATION_PLAN.md).
Then inspect enough implementation detail to answer, for the four+ visible families:
  I1 Are the families mechanically meaningfully different?
  I2 Do any supposedly independent families secretly share core implementation machinery?
  I3 Does S1 (the SYSID protocol) expose upstream physical properties consistently across all families?
  I4 Can the measurement grammar represent useful physics without trivially identifying the substrate?
  I5 Does the foreign family reveal assumptions embedded in the three Cosmos-authored families?

## Lens R-STAT (statistical / experimental design). Attack at least:
1. S0 fairness:
   - Can S0-A be passed by a trick, for example by predicting NOT-FUNCTIONAL more often inside a
     registered-only stratum?
   - Are DELTA_A = .10 and EPS_B = .03 justified?
   - Is the per-family concentration rule [v0.2a] adequate?
2. Before F-0002, verify:
   - the sign-flip EXCHANGEABILITY assumption (per-world flips under family clustering);
   - the bootstrap construction (family-stratified, paired);
   - the family weighting (pooled LOFO BA vs per-family means);
   - the handling of INDETERMINATE / INCOHERENT certificate rows;
   - whether the simulated candidate-error model (independent per-world errors) is unrealistically
     favourable. Real errors cluster by family and near boundaries.
   Do not accept the test because the power curve looks good.
3. Enriched-sampling bias:
   - Is the REGISTERED filter plus the Q_A proposal truly label-blind?
   - Are the S0-A / S0-B / S0-C estimands well defined, and is the importance weighting correct?
4. S2 (a)-(e) and the [v0.2a] family-identity reporting: can a secretly family-specific law pass? Are
   the tests over-strict for a genuinely universal law whose coordinates differ in distribution
   across families?
5. Multiplicity across gates x certificates x strata.
6. Anything that would make "no compact substrate-independent law exists" UNDISCOVERABLE.

## Lens R-MECH (mechanistic / adversarial). Attack at least:
1. ALL SIX S1 guards (G1-G6), individually and jointly:
   - Can a SYSID quantity restate the certificate despite them? For example: an impulse response over
     a grid that includes q, a reliability decoder that is the P1 probe in disguise, or amplification
     twins that act like the cue swap.
   - Can a delay-invariant coordinate still encode family or task construction (G3 is not proof)?
2. Certificate B: does controlling the current observation make B reconstruct Certificate A's causal
   contrast by another path? If it does, say so as BLOCKING; B is then redesigned before F-0002.
3. Can the coordinate language express useful upstream physics (timescales, reliability, routing,
   amplification, bottlenecks)? Or is it too blind, or too rich (so that a family-ID in disguise is
   always available)?
4. S4: construct a world where an intervention arm passes although the "law" is only a remeasurement.
5. The planted suite: which cheat would it miss?

## Output (each reviewer; the final report has TWO parts)
PART A DESIGN REVIEW and PART B IMPLEMENTATION-DIVERSITY REVIEW (I1-I5). In each part:
- findings as `lens | section | severity (BLOCKING / REPAIR / NOTE) | evidence | required change`;
- overall verdict PROCEED_TO_F-0002 / REVISE / NOT_WORTH_BUILDING. NOT_WORTH_BUILDING is a first-class
  answer.
A Phase-1 interim note is welcome; label it INTERIM (no verdict).
Commit under roles/Cosmos/c4/reviews/ as <LENS>_<seat>_<date>.md and post the commit id to Cosmos.
Cosmos reconciles both reviews in c4/reviews/RECONCILIATION_v0.2.md. Each finding is accepted (with the
change) or rejected (with the reason). Nothing is dropped silently.
