# Operator review of C3 autopsy / C4 v0.1, 2026-09-30 (verbatim)

Received in session Cosmos[m2-44f84976] (M2 SPECTREX5, claude-opus-5-5) on 2026-09-30, after the review
packet roles/Cosmos/research/reviews/REVIEW_PACKET_C3AUTOPSY_C4DESIGN_2026-09-30.txt. The text between
the markers is the operator's message exactly as received. Only Unicode dashes, quotes, arrows, the >=
sign and the section rule are transliterated to ASCII.

----- BEGIN VERBATIM -----
COSMOS -- OPERATOR REVIEW OF C3 AUTOPSY / C4 v0.1

Overall disposition

C3 remains:

CLOSED / KILLED BEFORE HOLDOUT

G-0006 remains dead.

The autopsy is accepted as a useful scientific result.

C4 is:

AUTHORIZED FOR DESIGN REVISION

but:

NOT YET AUTHORIZED TO FREEZE F-0002 OR BEGIN THE FULL BUILD

C4 appears worth building, but S0 v0.1 is mis-specified in one important respect.

----------

1. MAIN REVIEW FINDING: REVISE S0

T3-DOWN is not an ordinary predictive baseline.

It is a downstream, zero-parameter remeasurement of much of the target semantics.

Therefore requiring a new upstream physical representation to beat T3-DOWN by >= 0.05 balanced accuracy over the entire distribution is not the right scientific test.

Where T3-DOWN already reconstructs the certificate almost perfectly, an upstream explanatory model has little legitimate headroom.

The important scientific question is:

Can an upstream representation distinguish the worlds in which the certificate preconditions register but functional historical use nevertheless fails?

That is the unexplained region.

Revise S0 into at least two strata.

S0-A -- challenge-stratum superiority

Preregister a LABEL-BLIND procedure for generating/enriching worlds in the regime where:

* historical perturbation is physically registered;
* but reliable causal usability may or may not survive.

The candidate must materially outperform T3-DOWN in this challenge regime.

Use paired uncertainty/significance tests and family-held-out evaluation.

This is the primary explanatory gate.

S0-B -- ordinary-stratum non-inferiority

On an independently sampled, unenriched/natural world distribution, the upstream candidate must not buy challenge-stratum wins by breaking ordinary cases.

Require a preregistered non-inferiority margin rather than a large superiority margin.

Report both strata separately.

Do not hide the enriched sampling distribution inside a pooled score.

S0-C -- target-distribution estimate

Where possible, report a reweighted estimate for the intended natural distribution as well.

The enriched challenge set is an experimental instrument, not a claim about prevalence.

----------

2. KEEP T3-DOWN BINDING -- BUT ONLY FOR THE RIGHT QUESTION

Do not remove T3-DOWN.

It is valuable precisely because it exposes certificate restatements.

But its role should become:

A proposed physical explanation must add information where the certificate-derived shortcut is wrong.

It should not be:

A physical explanation must globally beat a near-label oracle on easy cases.

A candidate that merely duplicates T3-DOWN fails.

A candidate that fixes the challenge regime but introduces substantial ordinary-regime errors also fails.

A candidate that explains the challenge regime while remaining approximately non-inferior elsewhere earns further consideration.

----------

3. S1 FIREWALL -- RELAX ONE PART, STRENGTHEN THE PRINCIPLE

The underlying S1 principle is correct:

EXPLANATORY MEASUREMENT != CERTIFICATE MEASUREMENT

However, the current prohibition on essentially all lagged/task-related probing risks making the coordinate language artificially blind to the phenomenon it is meant to explain.

Do not permit:

* certificate twins;
* P2 swaps;
* certificate ablations;
* certificate seeds;
* certificate-trained readouts;
* reuse of label-producing statistics.

But allow preregistered, task-independent physical identification experiments when needed, for example:

* standardized impulse-response probes;
* intrinsic decay/mixing measurements;
* channel reliability measurements;
* perturbation propagation;
* spectral/mixing timescales;
* causal path length;
* redundancy;
* bottleneck measurements;
* perturbation amplification.

These probes must be independent of the certificate implementation and must not use the target label to choose their settings.

The goal is to move upstream, not to make the system observationally blind.

----------

4. S2 FAMILY LEAKAGE -- DO NOT USE KAPPA .30 AS A HARD SCIENTIFIC BOUNDARY

A universal coordinate may legitimately differ in distribution across substrate families.

Therefore family predictability from the coordinates is a warning signal, not by itself a falsification.

Keep family-ID prediction as a diagnostic.

The stronger gate should be:

After the candidate physical coordinates are known, does adding substrate identity materially improve prediction or explain residual errors?

Test:

* LOFO performance;
* per-family residual location;
* per-family calibration;
* whether explicit family terms materially improve held-out fit;
* conditional dependence of residual error on family identity.

A coordinate that identifies families but nevertheless supports a genuinely family-independent law may still be useful.

A coordinate whose apparent law requires family-specific corrections is not universal.

----------

5. S3 CERTIFICATE SWAP -- MAKE THE SECOND CERTIFICATE MORE INDEPENDENT

Certificate B should not merely implement the same internal-state swap with a different estimator.

Prefer changing the intervention level.

For example, consider a certificate based on source-level history randomization or another upstream causal intervention whose behavioral consequence is measured later while current observation is controlled.

The exact design is Cosmos's to develop.

The requirement is:

* different estimator;
* different randomization/intervention machinery;
* no shared certificate seeds;
* no shared internal swap implementation;
* same macroscopic phenomenon.

If the candidate relation only exists under Certificate A, it is not yet an earned physical relation.

----------

6. S4 INTERVENTION IS IMPORTANT -- KEEP IT

The intended intervention form is strong:

Change an upstream physical property while the cheap certificate precondition remains registered, and predict a transition in actual functional use.

Keep the matched opposite arm.

This is one of the best defenses against another definitional law.

The intervention must not directly manipulate the variable that defines the target label.

----------

7. ENRICHED SAMPLING IS ALLOWED, WITH DISCIPLINE

Yes, deliberately enriching worlds where T3-DOWN is likely to fail is scientifically legitimate.

Physics often probes phase boundaries and pathological regimes deliberately.

But three protections are required:

1. selection must be label-blind;
2. the challenge distribution and ordinary distribution must be reported separately;
3. no claim about natural prevalence may be made from the enriched sample without appropriate reweighting.

So R4 is a real concern, but it does not prohibit enrichment.

It requires explicit estimands.

----------

8. FOREIGN VISIBLE FAMILY -- YES

Commission one C4 visible family from a non-Cosmos author.

This is not a holdout.

After the family is written, it becomes fully visible and may participate in C4 development.

Its purpose is to break the single-author lineage before law discovery.

The foreign author should receive:

* the functional world/task contract;
* allowed native-observable interface;
* reproducibility requirements.

The author should NOT receive:

* Cosmos's preferred candidate coordinates;
* expected equations;
* expected challenge boundary;
* any request to reproduce a particular physical mechanism.

Because this is a visible family, strict repository secrecy is unnecessary.

Authorship independence is the goal.

Aim for at least:

* 4 visible families total;
* at least 2 mechanisms not present in C3;
* at least 1 family authored outside Cosmos.

----------

9. DESIGN REVIEW -- NOT HARMONIA

Keep Harmonia clean for D2 custody / compatibility / eventual audit.

Have the C4 design reviewed by reviewers who:

* did not author C4;
* do not control D2;
* are not the foreign visible-family author.

Prefer two independent lenses:

1. statistical / experimental-design review;
2. mechanistic / adversarial review.

They should specifically attack:

* S0 fairness;
* S1 firewall completeness;
* S3 independence;
* enriched-sampling bias;
* whether the candidate coordinate language can possibly express useful upstream physics;
* whether the planned interventions genuinely distinguish explanation from remeasurement.

C4 proceeds to F-0002 only after those reviews are reconciled.

----------

10. D2 INCIDENT I2

Do not let Cosmos adjudicate its own contact.

My provisional interpretation is:

CONTACT_WITH_PACKAGE_PATH / NO CONTENT REVEALED

not:

NO CONTACT.

A grep reporting only that a ciphertext file matched, with no bytes exposed and no decryption key on the machine, does not on its face reveal semantic holdout content.

However D2's custodian/auditor must make the formal ruling.

Until then:

D2 SEALED / UNREAD / UNSPENT / COMPATIBILITY PENDING

No C4 decision should depend on D2.

----------

11. C4 BUILD AUTHORIZATION GATE

Return with C4 v0.2 after independent review.

Authorize the build only if the revised protocol demonstrates that:

* S0 tests explanatory uplift specifically in the shortcut-failure regime;
* ordinary-distribution performance is protected separately;
* S1 prevents certificate reuse without banning legitimate upstream system identification;
* S2 tests residual family dependence rather than treating arbitrary family kappa as universality;
* Certificate B is genuinely machinery-independent;
* the world sampler is label-blind;
* at least one visible family will have independent authorship;
* the intervention changes an upstream physical property rather than the certificate itself.

If those conditions are met, proceed to F-0002 and instrument construction.

----------

12. SCIENTIFIC TARGET

C3 established that:

"usable history is present at the actor interface"

was too close to the operational certificate to count as an explanatory law.

C4 should ask:

What physical properties determine whether historical perturbations remain reliable, distinguishable, routable, and behaviorally usable over time?

That is the right move upstream.

Do not require C4 to find a law.

Require it to create an experiment capable of discovering that no compact substrate-independent law exists.

Return with v0.2 after review.
----- END VERBATIM -----
