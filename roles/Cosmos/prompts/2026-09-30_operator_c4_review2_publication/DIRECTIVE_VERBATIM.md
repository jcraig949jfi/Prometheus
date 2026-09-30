# Operator direction 2026-09-30 (second C4 review; Q-A publication ruling) -- verbatim

Received in session Cosmos[m2-44f84976] (M2 SPECTREX5, claude-opus-5-5) on 2026-09-30, after C4 v0.2
(5f5051e66). The text between the markers is the operator's message exactly as received. Only Unicode
dashes, quotes, the arrow and the section rule are transliterated to ASCII; the LaTeX display block is
kept as written.

----- BEGIN VERBATIM -----
COSMOS -- OPERATOR DIRECTION

C4 v0.2 is accepted for independent review.

No build authorization yet.

Q-A ruling: withheld C3 publication

Your proposed sequence is approved.

Do not publish the withheld C3 branch yet.

First require the foreign visible-family author to complete and commit its family under VISIBLE_FAMILY_CONTRACT.md without access to the C3 substrate implementations.

Once that foreign family is committed and its authorship/provenance receipt is immutable:

AUTHORIZE publication of the previously withheld C3 branch.

This publication is for C4 visible-development use only.

Before publication, verify:

* no D2 content is present;
* no foreign-family hidden material is present;
* the published head is descended from the previously committed withheld hash;
* the publication does not alter historical C3 receipts;
* the three original substrate implementations are exactly the versions whose results were audited.

Record the publication event in the C3/C4 information ledger.

----------

Why this ordering matters

The foreign visible family is intended to break the single-author lineage.

If its author sees the existing C3 mechanisms first, they may unintentionally construct another implementation occupying the same design space.

Therefore:

[
\text{foreign family authored independently}
\rightarrow
\text{family committed}
\rightarrow
\text{C3 substrates published}
]

After that point the foreign family is visible development data, not a holdout, so secrecy is no longer scientifically useful.

----------

Review ordering

Do not wait for publication to begin the two independent design reviews.

The reviewers may start immediately from:

* DESIGN_C4.md v0.2;
* REVIEW_BRIEF_v0.2.md;
* public C3 autopsy;
* S0 power analysis;
* foreign-family contract.

However, they should not issue their final review verdicts until the foreign family is committed and the C3 substrate implementations are public.

At final review they should inspect enough implementation detail to answer:

1. Are the four visible families mechanically meaningfully different?
2. Do any supposedly independent families secretly share core implementation machinery?
3. Does S1 expose upstream physical properties consistently across all families?
4. Can the proposed measurement grammar represent useful physics without trivially identifying substrate?
5. Does the foreign family reveal assumptions embedded in the three Cosmos-authored families?

Their final reports should distinguish:

DESIGN REVIEW

from

IMPLEMENTATION-DIVERSITY REVIEW.

----------

S0 v0.2

The revised two-stratum formulation is directionally approved.

Keep:

* S0-A challenge-stratum superiority;
* S0-B ordinary-stratum non-inferiority;
* S0-C reweighted ordinary-distribution estimate.

Do not pool A and B into one headline score.

One additional requirement:

Report the absolute number and rate of T3-DOWN failures in every challenge family.

A candidate cannot claim strong explanatory uplift because one small family contributes nearly all of the shortcut failures.

Where sample sizes permit, report candidate-only corrections and candidate-introduced errors separately by family.

----------

Power simulation

The replacement of McNemar with a paired family-stratified test on balanced-accuracy difference is approved in principle.

Before F-0002, the independent statistical reviewer should verify:

* the sign-flip exchangeability assumption;
* bootstrap construction;
* family weighting;
* handling of INDETERMINATE certificate rows;
* whether the simulated candidate-error model is unrealistically favorable.

Do not freeze the test merely because the power curve looks good.

----------

S1

The revised S1 direction is much better.

The delay-invariance guard is valuable, but do not treat:

coordinate unchanged across delay variants

as proof of independence by itself.

A coordinate can remain delay-invariant while still encoding family or task construction.

The independent reviewers should attack all six guards.

----------

S2

Approved conceptually.

Residual family dependence is the key test.

Family-ID predictability remains diagnostic, not automatically fatal.

Require explicit reporting of whether adding family identity improves:

* held-out discrimination;
* calibration;
* boundary location;
* intervention prediction.

----------

Certificate B

The source-randomization design is substantially more independent than the previous proposal.

Keep it subject to review.

The reviewer should specifically determine whether controlling current observation inadvertently reconstructs the same causal contrast as Certificate A through another path.

If so, redesign before F-0002.

----------

Foreign visible family

Yes: commission one now.

Aporia may assign the author under the constraints already sent.

The foreign author must not see the withheld C3 substrate code before committing its implementation.

After commit, publish everything needed for ordinary C4 visible development.

The foreign family is not a holdout and may thereafter be inspected, instrumented, attacked, and modified according to C4's visible-world protocol.

Preserve its original pre-exposure commit as provenance.

----------

Harmonia / D2

Harmonia's NO_INFORMATION ruling on I2 is accepted for the incident record.

D2 remains:

SEALED / UNREAD / UNSPENT

Do not involve Harmonia in C4 design review.

Do not assess D2 compatibility yet.

That happens only after C4 passes visible gates and has an earned claim worth adjudicating.

----------

Authorization state

Current authorization:

C4 v0.2 -- DESIGN REVIEW AUTHORIZED

FOREIGN VISIBLE FAMILY -- AUTHORING AUTHORIZED

WITHHELD C3 PUBLICATION -- AUTHORIZED AFTER FOREIGN FAMILY COMMIT

F-0002 FREEZE -- NOT YET AUTHORIZED

C4 FULL BUILD -- NOT YET AUTHORIZED

D2 ACCESS -- NOT AUTHORIZED

Once:

1. the foreign family is committed;
2. the C3 branch is published and provenance verified;
3. both independent reviews are complete;
4. Cosmos writes RECONCILIATION_v0.2.md;

return for the C4 build decision.

Do not preempt that gate.
----- END VERBATIM -----
