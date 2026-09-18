# Campaign 6 -- observatory qualification, Harmonia's lane (v0.1)

Author: Harmonia[m2-ca1148a0]. Date: 2026-09-18. Source: the operator's
Campaign 6 charter, verbatim at roles/Harmonia/prompts/2026-09-18_campaign6/
(MANIFEST). Executable form: qualification/campaign6/c6_observatory.py
(OQ-1.0.0, tests 11/11). Campaign lead: Archaeon. This seat builds no world,
organism, pressure schedule or detector; it decides what the observatory's
output may be quoted as, holds the planted fixtures blind, and calibrates
recall. Base rule 6: nothing this seat audits is edited by it.

## 0. The one sentence this lane exists for

"Do not interpret absence of detection as absence of phenomena until
observatory recall has been independently calibrated." Calibrating that
recall INDEPENDENTLY is this seat's job, and it is the campaign's own
success criterion ("It fails if increasing generative complexity makes SFE
scientifically blind"). Everything below serves the last question: how much
stranger can SFE become before we stop being able to tell what happened --
answered as a measured curve, recall against complexity, never as a mood.

## 1. What this seat delivers, and when

    item                                  before the campaign opens   during        at close
    ------------------------------------  --------------------------  ------------  ------------------------------
    F  fixture registry (sealed)          commitments committed;      no contact    reveal verified against the
                                          private registry held by     with the      commitments; VOID for any
                                          this seat only               operating     tampered fixture
                                                                       seats
    D  detector admission (11)            per detector: chance floor,  frozen        firing table + the two event
                                          positive / negative / cheat  thresholds    classes (DISAGREEMENT,
                                          controls, geometry, null     never moved   NONE_OF_THE_ABOVE) counted
                                          family (charter s6)
    E  escalation gate                    preservation-before-         every         packet digests on file
                                          explanation as a check       escalation
    R  recall calibration                 metric definitions frozen    --            detection / preservation /
                                          with their denominators                    false escalation / replay /
                                                                                     causal recovery /
                                                                                     classification / unknown
                                                                                     retention, each with eligible
                                                                                     count + Wilson 95
    C  classification admission           UNKNOWN_MECHANISM default;   every         UNKNOWN_MECHANISM catalogue
                                          named mechanism needs a       classifi-     (return item 8)
                                          reproducing replay + a        cation
                                          moving causal probe
    S  success-class rulers               six predicates frozen        --            six independent verdicts;
                                                                                     PASS/FAIL refused
    P  provenance / LLM-free floor        label vocabulary fixed       census        eligibility for
                                                                       per tranche   SEARCH_DIVERSITY
    K  the complexity curve               complexity bins declared     --            recall by bin (the answer to
                                          from Axis W/O features                     the last question)

## 2. Fixture custody (BLIND SPOTS / ANTI-GRAVITY)

The charter: "The seats operating the main campaign must not know fixture
locations." Custody therefore sits with a seat that does not operate the
campaign. Protocol:

    1  fixture authors (this seat, with Nemesis for cheat-shaped fixtures and
       any seat the operator names) write each fixture as {fixture_id,
       phenomenon_class, location, expected observatory behaviour, spec}
    2  seal_fixtures() commits sha256 over each fixture; the PUBLIC registry
       (ids + commitments + sealed_at) is committed to main; the PRIVATE
       registry is written to a path the operating seats cannot read (this
       seat's worktree, not pushed until reveal) and its digest is in the
       public one
    3  the campaign runs; no fixture is discussed in comms; a planted
       location that a seat asks about is answered "sealed"
    4  the firing table is frozen (Archaeon posts its digest); only THEN is
       the private registry pushed and verify_reveal() run; any fixture whose
       commitment fails is VOID and counted as such, never silently dropped
    5  recall_metrics() runs on the verified reveal against the frozen table

The eight phenomenon classes the charter lists are the minimum; each gets
>= 3 plantings across >= 2 complexity bins so per-class detection has a
denominator. A class with fewer than 3 plantings is reported
NOTHING_COULD_FIRE for that class, not as 100% or 0%.

The cheat control of the whole stack: a stack that fires on everything has
detection 1.0 and is labelled VACUOUS_FIRES_ON_EVERYTHING by its
false-escalation rate. A silent stack is MEASURED at 0.0, not excused.

## 3. Detector admission (the eleven)

Each detector is admitted per condition (charter s6; CALIBRATION_CORPUS_
POLICY.md is the precedent): a declared null family, a chance floor
measured on it at the campaign's geometry, a positive control that fires,
a negative that does not, a cheat that shows the channel can see what it
claims. Thresholds are FROZEN before the first tranche and never moved
(charter: "frozen threshold"). Two consequences the rulers enforce:

- "detector disagreement is itself an event class": at a location where
  some detectors fire and others with a score are silent, the location is
  counted under DETECTOR_DISAGREEMENT and escalated like any firing.
- "a classifier returning none of the above is an event class": a
  classifier_failure firing is preserved, never treated as a miss.

No global interestingness score exists anywhere in the pipeline; a
MULTI_RULER count is reported beside single firings and never replaces them.

## 4. Escalation as an instrument

check_escalation_order(): the nine freezes complete and timestamped, the
replay packet digested, BEFORE a classification exists. A classification
timestamped earlier than preserved_at is refused. Replays A-C and probes D-G
are recorded per escalation as booleans with their receipts; recall_metrics
reads them.

## 5. Classification admission

UNKNOWN_MECHANISM is admissible always and is the default. A named
mechanism needs >= 1 replay that reproduced the event AND >= 1 causal probe
that moved it. "evidence_kind: RESEMBLANCE" is refused outright (charter:
'mechanism X occurred' because a trajectory resembles X). The
UNKNOWN_MECHANISM catalogue (return item 8) is the set of escalations that
stayed UNKNOWN after the probes ran, with their packets -- a first-class
result, not a backlog.

## 6. Success classes and forbidden conclusions

campaign_return() takes six SuccessClassVerdict rows (SUPPORTED /
UNSUPPORTED / INCONCLUSIVE / INELIGIBLE), each with its eligible count and
evidence paths; a missing class, a verdict without paths, or an eligible
count of 0 under a non-INELIGIBLE verdict is refused; refuse_collapse()
refuses PASS/FAIL. refuse_forbidden_conclusion() refuses the charter's five
sentences when offered on the insufficient evidence the charter names.

## 7. The complexity curve (return item 13, and the last question)

Complexity bins are declared BEFORE the campaign from Axis W and Axis O
feature counts (e.g. number of world primitives active x organism structural
mutation kinds enabled), and every fixture is planted in a declared bin.
recall_by_complexity() gives detection per bin with its eligible count. The
"recommended next complexity ceiling" is the highest bin at which planted
detection's Wilson lower bound stays above a threshold the operator fixes
BEFORE the reveal (SIZING_RULE.md: the meaningful effect comes first). A bin
with no fixture is NOTHING_COULD_FIRE, never "safe".

## 8. What this seat asks of the others (posted with this file)

    Archaeon     the tranche plan with complexity bins and provenance labels
                 per run; the detector specs for admission; the frozen firing
                 table digest at close; escalation receipts in the shape
                 c6_observatory reads (freezes / replays / causal_probes /
                 classification / preserved_at / classified_at)
    Daedalus     T0-T3 telemetry tiers as ledger content with cost receipts
                 (return item 4); the replay packet format
    Proteus      organism ancestry metadata sufficient to "reconstruct
                 exactly what changed" -- the unit the lineage detectors read
    Herakles     world generative provenance on every world (Axis W)
    Nemesis      cheat-shaped fixtures and the chance floors for the eleven
    Mnemosyne    where escalation packets live (Postgres, per the 09-18
                 ledger ruling), and their backup
    operator     the recall threshold for the complexity ceiling (s7), fixed
                 before the reveal; who besides this seat may author fixtures

## 9. Conflicts, falsifiers, what to stop

Conflict: this seat authors fixtures AND scores recall on them. Mitigation:
fixture authorship is shared (Nemesis; the operator's nominees), the
commitments are public before the campaign, and the reveal is verified by
anyone against them.
Falsifier of the lane: a natural anomaly caught by no detector but found by
a human reading a trace would show the eleven are the wrong eleven; that is
recorded under return item 11, not smoothed.
Stop: any interestingness score; any threshold moved after a firing; any
classification written before preservation; any fixture location in comms.
