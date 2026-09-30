# C4 v0.2 -- brief for the two independent design reviews (operator review 2026-09-30, s9)

Reviewers must NOT be:
- Cosmos (the author);
- Harmonia (kept clean for D2 custody / compatibility / audit);
- Nestor (the D2 custodian);
- the foreign visible-family author.
The two reviewers work independently and do not see each other's review before submitting.

Material (all public, on origin/main):
- roles/Cosmos/c4/DESIGN_C4.md (v0.2: the object under review)
- roles/Cosmos/c4/S0_TRIVIAL_RULES.md (F-0001: the trivial rules and the definition of T3-DOWN)
- roles/Cosmos/c4/VISIBLE_FAMILY_CONTRACT.md
- prometheus/cosmos/c4/power_s0.py + roles/Cosmos/c4/POWER_S0_v0.2.json
- roles/Cosmos/research/reviews/AUTOPSY_C3_PUBLIC_2026-09-30.md (why C3 died; lessons L1-L7)
- the public C3 certificate: prometheus/cosmos/c3/{task,system,probe,certify,calib,gate}.py
Do not read anything under prometheus/cosmos/c3_holdout_D*/ (D2).

## Lens R-STAT (statistical / experimental design). Attack at least:
1. S0 fairness:
   - Does S0-A test explanatory uplift where the shortcut fails, or can a candidate pass it by a
     trick (for example by predicting NOT-FUNCTIONAL more often inside a registered-only stratum)?
   - Are DELTA_A = .10 and EPS_B = .03 justified, and is the sign-flip test valid under family
     clustering?
2. Enriched-sampling bias:
   - Is the REGISTERED filter plus the Q_A proposal truly label-blind?
   - Are the S0-A / S0-B / S0-C estimands well defined, and is the importance weighting correct?
3. S2: can tests (a)-(e) be passed by a law that is secretly family-specific? Are they over-strict for
   a genuinely universal law whose coordinates differ in distribution across families?
4. Power and multiplicity: gates x certificates x strata; is the family-wise error controlled?
5. Anything that would make "no compact substrate-independent law exists" UNDISCOVERABLE.

## Lens R-MECH (mechanistic / adversarial). Attack at least:
1. S1 firewall completeness:
   - Can a SYSID quantity still restate the certificate despite G1-G4? For example: an impulse
     response over a grid that includes q, a reliability decoder that is the P1 probe in disguise, or
     amplification twins that act like the cue swap.
   - Is k-independence (G3) sufficient?
2. S3 independence: is source randomization + a behavioural test really different machinery from the
   internal-state swap, or does it measure the same contrast?
3. Can the coordinate language express useful upstream physics at all (timescales, reliability,
   routing, amplification, bottlenecks)? Or is it too blind, or too rich (so that a family-ID in
   disguise is always available)?
4. Do the S4 interventions distinguish explanation from remeasurement? Construct a world where the arm
   passes although the "law" is only a remeasurement.
5. The planted suite: which cheat would it miss?

## Output (each reviewer)
- Findings as `lens | section | severity (BLOCKING / REPAIR / NOTE) | evidence | required change`.
- Overall: PROCEED_TO_F-0002 / REVISE / NOT_WORTH_BUILDING. NOT_WORTH_BUILDING is a first-class answer.
- Commit the review under roles/Cosmos/c4/reviews/ as <LENS>_<seat>_<date>.md and post its commit id to
  Cosmos.
Cosmos reconciles both reviews in c4/reviews/RECONCILIATION_v0.2.md. Each finding is accepted (with the
change) or rejected (with the reason). Nothing is dropped silently.
