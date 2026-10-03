================================================================================
PHASE 3 RSO -- CLOSURE REVIEW OF THE v0.4 SYNTHESIS
FABLE-5.1 (seat Dionysus) on the Enceladus (ASTRA-6.0) proposal
================================================================================
Prepared:    2026-10-03 (UTC)
Reviews:     docs/phase3/synthesis/ENCELADUS-DIONYSUS-v0.4/ at 3bd02f393
             (branch enceladus/rso-synthesis-2026-10-02; read with git
             show; not merged). Read: README, SYNTHESIS_AND_DECISIONS_v0.4,
             NEXT_ROUND_PLAN_v0.4, DIONYSUS_REVIEW_HANDOFF, VALIDATION.
             Not read: REVIEW_PACKET, SOURCE_INDEX, the ASTRA v0.2
             hardening directory (9af020b24), any design directory.
Context:     my hardening package, docs/phase3/hardening/FABLE-5.1/
             (3669bc7f2)
Directive:   roles/Dionysus/prompts/2026-10-03_closure_review/
Exposure:    I have read every current document of both packages, and my
             own code and tests. Nothing here is a first-sight score. My
             S3 and S4 attacks will be first-sight only relative to the
             new implementation and its frozen tests.

A. OVERALL VERDICT
--------------------------------------------------------------------------------
ACCEPT_WITH_MINOR_AMENDMENTS.

There is a coherent, bounded approach both designs can live with: a
shared evidence contract over native runtimes, one finite methods slice,
one native witness after it. No blocker. The chronological correction in
the synthesis is right: I reviewed f4d9e72d9 and had not seen the v0.3
updater or the complete-node binding. I find no claim attributed to me
that I do not make. The five amendments in C are contract fields and
wording, not design changes.

B. D01-D11
--------------------------------------------------------------------------------
ID   disposition  note / action
---  -----------  --------------------------------------------------------
D01  ACCEPT       Shared: registration, claims, evidence contract,
                  custody and exposure, resources, known-answer
                  qualification, invalidation, receipts. Native: state,
                  dynamics, search, interventions, execution. Both
                  harnesses stay as reference and adversarial corpora;
                  no gate is inherited as code. My reset fixtures are
                  offered as cases for T04 and T08 (C3).
D02  AMEND        Three fields, not one verdict (C1). INDETERMINATE is a
                  ruler outcome for a registered statistical decision;
                  it does not occur in the finite slice.
D03  ACCEPT       An exact bound is mandatory only where a claim excludes
                  a class. Comparator, intervention and replication
                  claims carry their own evidence and are rendered with
                  what they are relative to (C2). No L-numbers in the
                  slice. My disagreement is kept in D.
D04  ACCEPT       Measured caches are measurements, not class optima;
                  mediated updater, class exclusion and strong recursion
                  stay distinct. Evidence language: section 5 of the
                  directive, adopted as the only permitted forms.
D05  ACCEPT       The finite updater is a narrow behavioural positive
                  (8 of 8, tied with its flattened form and a sign-
                  gradient baseline): no advantage, no mediation, no
                  recursion shown. Answers per claim; no veto by
                  pedigree. Mediation is EMPIRICAL (D).
D06  AMEND        Author regression is not authority. Authority is a
                  stage recorded on the gate and inherited by the claim
                  (C4). Rounds are bounded to S3 and S4 per frozen
                  version.
D07  ACCEPT       Methods slice first, then one native witness, then one
                  science question (unseen pair, reach contrast or W1,
                  chosen then). The unseen-pair prerequisites in the
                  synthesis match my own list; nothing to add.
D08  ACCEPT       One realization earns local evidence. Two realizations
                  that share code, or are related by a reversible
                  encoding (E06), are one physics. Unlike is declared by
                  naming the differing state representation and
                  dynamics; the panel of three stays a target, not a
                  theorem.
D09  ACCEPT       Dependency gates and absolute caps; no 90-day plan; no
                  engine chosen by its author. Caps accepted as proposed
                  (six hours Enceladus, three hours Dionysus, 30 CPU
                  minutes, 12 launches, two working days, one repair).
                  My availability caveat is in F.
D10  ACCEPT       Hashes establish identity of bytes, binding of a
                  receipt to named inputs, and alteration against
                  anchors held elsewhere. They establish nothing about
                  execution, the truth of an observation, independence
                  of keys, or authorship. Anchor keeper named in S1
                  (C5); without one, custody is UNQUALIFIED.
D11  AMEND        The same change as D02 (C1). FAIL is a protocol
                  predicate that failed; a correct negative observation
                  is a ruler outcome, never FAIL. T02 is the test case.

C. MANDATORY AMENDMENTS (before S1 is frozen)
--------------------------------------------------------------------------------
C1  Verdict structure (D02, D11). A receipt carries three fields:
    execution {RAN; BLOCKED, with what was missing}; instrument authority
    {QUALIFIED at stage X; UNQUALIFIED, with why}; outcome. A gate's
    outcome is PASS or FAIL on a named protocol predicate, with its
    reason. A ruler's outcome is its registered scientific answer (for
    the slice POSITIVE, NEGATIVE or NOT_SHOWN; later INDETERMINATE for a
    statistical decision that meets neither threshold). Claim eligibility
    is the worst of the three; the report prints all three. Why: in the
    plan's T02 a world with no carry gives "retention-positive predicate
    FAIL", and a reader counts a correct negative as a defect.
    Replacement for T02: calibration gate PASS; retention ruler NEGATIVE
    (exact 1/2).
C2  Render rule (D03). A claim is rendered only with what it is relative
    to: the comparator set, the intervention set, or the class and its
    exact bound; and with its cell and registered setting. The words
    class, any, all and no organism appear only beside an exact bound.
    Why: this is how a comparator result drifts into an exclusion claim.
C3  Registered finite model for reset (T04, T08). S1 states the delay
    horizon in episodes and the number of repeated resets the model
    covers, and lists which known escapes of both harnesses fall inside
    it and must now be caught, and which fall outside and stay listed.
    Two of mine to place: a carry hidden from the reported state and
    used two episodes later; a reset that leaks on every third call (my
    G6.reset escapes). Why: closure is relative to a stated model;
    without the horizon, "no unresolved applicable survivor" has no
    denominator.
C4  Authority stage (D06). Each gate record carries one of: author-
    tested; first-sight challenged (date, cases and edits with
    denominators, first-sight score); closed after repair (closure
    score). A claim's receipt inherits the lowest stage among its gates,
    and the stage is printed with the claim. No further rounds are
    required for the slice. Why: whether someone else has tried to break
    a gate must be answerable from the receipt; my six first-sight
    figures (12 of 26 to 22 of 25 unnoticed) say author-tested gates are
    not tested.
C5  Anchor keeper (D10). S1 names who holds the evidence-node anchors
    and the attempted-run inventory outside the producer (the operator
    or the reviewer), and in what form. If nobody does, E01-E05 are run
    and reported with custody UNQUALIFIED, as the plan already allows.

Nothing else is required before S1. The mutation probe is not rerun; the
existing receipts stay as they are.

D. AGREE TO DISAGREE / EMPIRICAL
--------------------------------------------------------------------------------
1. Exact null as a level requirement (mine) versus claim-specific
   evidence (ASTRA). Use ASTRA's for the slice. Evidence: after the
   native witness, audit every rendered claim for a comparator result
   read as exclusion. If one is found, the level rule returns.
2. One five-valued verdict (mine) versus separated axes (ASTRA). Use the
   three-field receipt (C1). Evidence: whether the S5 report needs a
   collapsed verdict anywhere a reader acts on it.
3. Whether a gate may feed a claim before any first-sight challenge. I
   said UNQUALIFIED until attacked; ASTRA keeps distinct records. Use
   the labelled stage (C4). Evidence: the S3 first-sight score. If it
   is as bad as my six figures, no claim is rendered on an author-
   tested gate thereafter.
4. The finite updater's mediated effect under an intervention set.
   Empirical: the native witness, with clamp and swap, decides whether
   any mediated effect exists. No promotion before it.
5. The next science question after the witness (unseen pair, a reach
   contrast, or one W1 comparison). Decided then, by what the witness
   shows to limit, not before.
6. Field decisions, as in section 9 of the directive: R3 versus R4;
   reset semantics per physics; exact bounds beyond W1; which state
   channels matter natively; an external-cognition lane; which gates
   earn their keep (one that returns only PASS on real work is
   removed). Each recorded as uncertainty, choice, reversibility,
   trigger.
7. Whether information crossing a boundary with fresh keys can ever be
   read as more than retention. Mine says not from behaviour alone.
   Left open; the unseen-pair experiment is the first test, if it is
   ever run.

E. OUT OF SCOPE
--------------------------------------------------------------------------------
The directive's list is confirmed as stated. Added from my package, all
backlog and none rejected: my 21-gate harness as a runtime (corpus
only); the generalised report checker (G13); the boundary 2x2 pilot; the
W1 keyed family with exact class values; a second author's isomers; the
world-selection rule as a gate; stochastic, asynchronous and continuous
observer contracts; the 90-day allocation of my design.

F. FIRST IMPLEMENTATION SLICE
--------------------------------------------------------------------------------
Build ASTRA S1-S5 as written, with C1-C5 folded into S1. I cannot remove
a load-bearing test: T01-T08 and E01-E05 each catch a mistake one of our
harnesses has made. One trim: E06 (encoding and flattened twins) is run
and reported but is not an exit criterion of this slice; it belongs to
the native witness, where there is a second realization.

Enceladus builds: one versioned contract (claim: a retained bit across a
named boundary with an allowed channel; finite organism state plus a
modelled pending-message channel and any counter or schedule state;
reset and restart as separate predicates; the receipt schema; the
three-field verdict; the anchor keeper; the delay horizon and repeat
count; the approved caps); one finite transition fixture with a producer
and consumer receipt boundary and a small adapter; the independently
derived expected-answer table; sound and broken cases for T01-T08 and
E01-E06.

I take the reviewer role as proposed: at S1, an independent expected-
answer table derived from the contract before I see the implementation;
at S3, five fresh sound cases, five fresh broken cases and ten semantic
source edits, committed with their intended faults before any outcome is
observed and before the frozen test bodies are opened; at S4, two, two
and three for the closure set. First sight means first sight of the new
code; my exposure to both packages is recorded above. Three review hours
accepted. Caveat: my model budget is the operator's to spend. If I
cannot be run when S3 is ready, the operator names another reviewer, of
another model family where possible; a subagent of Enceladus does not
count.

Exit of the slice: zero unresolved false admissions or rejections in the
registered finite model; every outcome typed with its reason; no
unresolved applicable survivor on a claim-critical path; authority stages
printed. Then the native witness, not another methods round.

G. EXIT FROM DESIGN REVIEW
--------------------------------------------------------------------------------
NO. After C1-C5 are written into the S1 contract, no further broad
architecture or harness design review is needed before implementation.
The remaining conditions are the operator's: authorize the caps and name
the anchor keeper. The next thing I should be asked to read is a frozen
contract and a frozen implementation, not a design.

Bottom line: build it, let me try to break it once, repair once, then put
a real architecture through it.
================================================================================
END OF CLOSURE REVIEW
================================================================================
