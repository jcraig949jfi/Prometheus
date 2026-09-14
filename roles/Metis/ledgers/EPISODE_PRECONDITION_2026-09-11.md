# Season 1 upstream-liveness precondition: the five named episodes

Currency: 2026-09-11. Run BEFORE the season prompt exists, under base
rule 9 (UPSTREAM LIVENESS IS A LAUNCH PRECONDITION, not a per-tick
observation; the owner shows the upstream is live NOW, dated, before a
loop is launched). The season's upstream is five already-dead episodes
named by the operator. If their evidence does not survive, the season
does not exist, and that is cheaper to learn now than in week two.

Verdict in one line: ALL FIVE ARE RECOVERABLE. One is misnamed in a way
that changes the season, one is ambiguous between two distinct threads,
and one is not the kind of episode the directive assumed.

Provenance grades: COMMIT / MEASURED / DOC / RECALL. Nothing below is
RECALL.

## 0. An instrument error of this seat's own, recorded first

The first pass of this survey reported greedy-LoRA NOT LOCATABLE. That
was WRONG, and it was wrong for a reason this seat is supposed to catch.

    git ls-files | grep -iE "...|greedy.?lora|lora" | head -40

The pattern matched. `roles/Ergon/GREEDY_LORA_RESULT_2026-06-03.md`
sorts below the fortieth line of an alphabetical listing, and `head -40`
cut it. A second attempt with `git grep` over file CONTENTS also missed
it, because git grep does not search filenames.

Base role s2: "Sampling is analysis: enumerate the inventory first,
NEVER READ A PREFIX." This seat read a prefix, twice, and would have
told the operator that a real episode with 179 lines of committed
evidence did not exist. Had that reached the season prompt, the best
case in the set would have been dropped.

A third error in the same survey: `grep -i "lora"` matched "expLORAtion"
across hundreds of Coeus enrichment files. A substring is not a token.

Recorded as C-05 in calibration/CALIBRATION.md. The counts below are
from full enumerations with no head, and the negative claim "no other
episode exists under this name" is the one claim in this document that
is graded as a REPORTING CLAIM WITH A DATE, not a fact.

## 1. Geometry-1 -- RECOVERABLE, STRONG

    anchor    harmonia/memory/retraction_registry.md, entry
              "2026-04-19 -- Geometry 1 (tensor latent-rank claims)"
    was       tensor specimen-manifold effective dimension <= 5; SVT
              completion gave rank 12-16; 3D core 48-74% of variance
    status    RETRACTED (strong form falsified; amended weak form
              unsupported by the method)
    mechanism SVT assumes continuous real entries, missing-at-random,
              low-rank + Gaussian noise. The tensor is sparse ordinal
              {-2..+2} with 0 = unobserved and MNAR (cells tested by
              researcher attention). Most-loaded SVD columns (P020,
              P023) are also the most-tested.

WHY IT FITS THE SEASON. The predicting signal is nameable in advance
(most-tested == most-loaded is a confound, not a rank), and the
deterministic test that would have caught it EXISTS AND WAS RUN TEN DAYS
LATE: harmonia/memory/diagnostics/missingness_confound_v01.py,
2026-04-29, which measured that ~52 percent of any rank-flavoured signal
is attributable to row/column density marginals alone, pass_overall=
FALSE. Question 4 ("could a deterministic composition rule have selected
a cheaper, more discriminating next experiment") has a literal answer
here: the cheaper experiment was written down, by the same programme,
after the claim had already been promoted and retracted.

## 2. Saxl -- RECOVERABLE, STRONG, AND IT IS AN INVERSION

    anchor    techne/registry/anti_anchors.jsonl rows AA-004, AA-011,
              AA-031 (MEASURED: read this pass)
    shape     AA-004's own verification_source says it was "INVERTED
              from prior 2026-05-10 entry which incorrectly claimed
              Saxl was solved"

The registry asserted the FALSE form for roughly three months while the
falsifying evidence was public the entire time: arXiv:2512.15035 (Lee)
was withdrawn by its author on 2025-12-20, three days after posting,
with the verbatim comment "The claim of a complete proof is not
justified in its current form." AA-031 names the mechanism as DATA
CONTAMINATION rather than hallucination -- models reproduce verbatim
phrases from the flawed paper -- and flags a second trap axis: the
tensor CUBE version IS proven (Harman-Ryba, arXiv:2206.13769), the
SQUARE is not.

WHY IT FITS THE SEASON. This is question 3 in its purest form: a signal
that was AVAILABLE AND IGNORED, where "available" is not a judgement
call because the withdrawal notice is a dated public artifact. It also
supplies a second, harder case: a seat consuming the registry between
May and August would have been correct to trust it and wrong in fact.
Composition over a corrupted channel is not a solved problem by having
more channels.

## 3. Erebos -- RECOVERABLE, BUT THE NAME IS AMBIGUOUS

The directive says "Erebos transport." Two distinct threads carry the
name and only one of them is about transport.

  (a) EREBOS COMPOSITION. aporia/docs/STATUS_2026-06-15_reset.md line
      103 (MEASURED): "OFF until they have a consumer: ... Erebos
      composition (paused; reframe Phase-3 docs honestly -- 0 signal
      passes survive nulls, 1 infra pass stands)."
      Twenty-plus generator designs exist under
      aporia/docs/erebos_v2_designs/ and
      aporia/docs/deep_research_reports/erebos_v2_2026-05-27/ (g01
      intersection, g03 failure-neighbourhood, g06 null-space, g16
      anti-anchor, g20 instrument-disagreement, ...), each with a
      design audit, plus three v3 synthesis batches.

  (b) EREBOS PHASE-0 TRANSPORT. A decentralised communication protocol:
      Blake2-addressed object storage, plaintext 4-way handshake,
      WebSocket tunnelling, local-storage lock contention. Documented
      through the Moros cross-pollination retrospective
      (aporia/docs/deep_research_reports/2026-05-28/00390_...).

RECOMMENDATION, NOT A RULING. (b) matches the word "transport"; (a) is
the one that belongs in a season about composition, and its recorded
death -- ZERO signal passes surviving nulls against ONE surviving infra
pass, across twenty-plus generators -- is the single most on-topic
failure in the whole set. If the operator meant (b), the season loses
its best structural case and should be told so. This is the one item
where a wrong guess would change the deliverable, so it is not guessed.

## 4. greedy-LoRA -- RECOVERABLE, STRONG, AND IT IS NOT A FAILURE

    anchor    roles/Ergon/GREEDY_LORA_RESULT_2026-06-03.md, 179 lines,
              with an addendum dated 2026-06-04 (MEASURED)
    headline  "The needle moved, hard -- and the gain survives the
              content control."

The directive lists this among "already-dead episodes." The surviving
record does not read as dead. It reads as a HEADLINE COLLAPSE, which is
a different and considerably more useful shape:

    raw delta base -> trained                        +0.678
    real LoRA 0.907 vs shuffled-label control 0.681  +0.226 content
    --- then the entity-disjoint addendum, 2026-06-04 ---
    relation base-rate oracle (no objects, no values) 0.669  <- FLOOR
    E-hidden  (entity-disjoint, values withheld)      0.744
    E-shown   (entity-disjoint, values given)         0.841
    value memorization        E-hidden vs v1          +0.116
    genuine relational reasoning  E-shown - E-hidden  +0.097

Ergon's own verdict: "the 'mathematical reasoning' share is the smallest
component. Ordered by size: format-following > relation base-rate priors
(~0.67) > value memorization (~0.12) > genuine reasoning (~0.10)."

WHY IT FITS THE SEASON, AND WHY IT IS THE BEST CASE IN THE SET. Four
evidence channels all pointed the same way -- a large raw delta, a
passed shuffled-label control, OOD generalisation on CounterMath,
per-source scores of 1.00/1.00/0.86 -- and they were CORRELATED, because
all four are downstream of the same format-following gain. One
orthogonal control, a base-rate oracle that knows only which relation
types usually hold, collapsed the headline from +0.68 to about +0.10.
That is operator question 5 exactly: where composition manufactures
false confidence from correlated evidence. A composition rule that
counted agreeing channels would have scored this episode MORE confident
the more wrong it was.

Note also that the episode self-corrected in ONE DAY, unprompted, by its
own author. Whatever rule the season proposes has to explain why Ergon
caught this and the other four episodes were not caught.

## 5. Apollo's failed lift -- RECOVERABLE, STRONGEST PROVENANCE

    anchor    roles/Apollo/STARTUP.md lines 95-118 (MEASURED);
              apollo/cycles/type_bridge/PREREGISTRATION.md;
              apollo/pivot/dispatch_arc_writeup_2026-06-27.md and
              seven more under apollo/pivot/
    run       run_branch_c_dispatch_llm2, gen 800, 86156 s (~24 h),
              finished 2026-06-28 10:28
    verdict   max_acc 0.833, max_routable_acc 1.000, coverage 0.833 --
              "exactly the deterministic numbers. Zero lift from
              Granite." 2152 LLM mutations bought nothing.
    shape     0.317 (g1) -> 0.833 at gen 131, then 669 generations of
              archive padding

This is the only episode in the set with a PRE-REGISTERED KILL
CONDITION, which makes question 1 ("what evidence existed before the
next experiment was chosen") answerable exactly rather than
reconstructively.

THE TRAP IN IT. An archive report dated 2026-04-06 (MEASURED:
apollo/archive/reports/evolution_report_2026-04-06_0723.md) already
said "No LLM-generated mutations are surviving" and "All llm_alive
counts are 0, indicating adaptive operator selection has disabled LLM
mutations entirely." That looks like the failure being visible almost
three months early. IT WAS NOT. That signal was an INSTRUMENT ARTIFACT:
drift() was wiping LLM lineage, and the one-line fix on 2026-05-22 took
llm_alive from 0 to 24/50. The early signal was measuring the
instrument, not the world -- and the eventual conclusion was right
anyway, for a different reason.

Any composition rule that treats the April row as an early true positive
is right by accident. This is the sharpest available test of whether a
proposed rule distinguishes evidence from instrument error, and it is
the reason this episode should be in the set even though its outcome is
the least surprising.

## 6. Prior art the season should know exists

    aporia/docs/deep_research_batch_2026-08-17/
      16_expected_information_gain_experiment_selection_in_practice.md
      16_..._answer.md
    aporia/docs/deep_research_batch_2026-08-17/
      05_verifier_in_the_loop_discovery_systems_canon_band_g.md

Deep research this programme already commissioned, on experiment
selection and expected information gain, which is the literature this
season sits in. Per the north star these are REFERENCE ARMS AND
ACQUISITION CANDIDATES, never the target: the season is not to
reimplement EIG. It is named here so the season cannot later claim
novelty it has not earned, and so the seat is not the channel through
which "the standard approach is" enters (this seat's constraint 7 and
Eos's constraint 8).

## 7. What this survey does NOT establish

- Not that four or five episodes is the right N. Five decision points is
  a very small replay set, and any rule fitted on five and evaluated on
  the same five is fitted, not tested. The season needs a declared
  train/test split over episodes, or it needs to be honest that its
  first output is a HYPOTHESIS about composition and not a validated
  rule. This is the single largest design risk and it belongs in the
  prompt, not in a later caveat.
- Not that the surviving evidence is the evidence that existed AT the
  decision. Every one of these records was written with the outcome
  known. Reconstructing "what was available before" from documents
  authored after is the core methodological hazard of the whole season,
  and it biases every episode in the SAME direction: toward the signal
  that turned out to matter being more legible than it was. Git history
  gives a partial fix (what was committed before the decision date) and
  the season should use commit dates, not document contents, wherever
  the two can disagree.
- Not that these five are representative. They are five episodes the
  operator remembered, which is a sample selected on memorability, and
  memorable failures are not average failures.
