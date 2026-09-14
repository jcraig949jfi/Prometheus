# Metis Season 1 -- PREREGISTRATION

Frozen 2026-09-13, BEFORE any episode ledger was written and BEFORE a
line of the specimen exists. Committed in its own commit so the order is
in git history (base s2). Anything in this file that later turns out to
be wrong is annotated beside the original, never rewritten.

Authority: roles/Metis/prompts/2026-09-13_season1/SEASON1_PROMPT.md
(operator, verbatim, MANIFEST beside it).

## 1. The question, frozen

    When Prometheus has multiple pieces of evidence supporting a belief,
    which evidence is genuinely additive, which is redundant or
    contaminated, and what cheapest discriminating observation could most
    strongly change the belief?

Out of scope, explicitly: any confidence number. The specimen emits
structure and vetoes, never a scalar.

## 2. Episode usage and split, frozen

CONSTRUCTION (the mechanism may be shaped against these):

    E1  GREEDY-LORA      correlated evidence / base-rate confounding
    E2  APOLLO LIFT      instrument artifact as early evidence

WITHHELD (mechanism checks; their ledgers are NOT written until the
specimen is frozen and its hash recorded):

    E3  SAXL             stale internal authority vs available
                         external contradiction
    E4  GEOMETRY-1       cheaper discriminating experiment, delayed
    E5  EREBOS COMPOSITION  many generators, null science, one infra
                         success not to be read as scientific success

THE SPLIT IS 2/3, AND THE ORDER OF WORK IS THE GUARANTEE. The specimen
and the adversarial tests are committed and their hashes recorded BEFORE
roles/Metis/ledgers/episodes/E3, E4 and E5 exist. A later reader can
verify this from git history alone: if an E3/E4/E5 ledger commit precedes
the specimen-freeze commit, this preregistration was violated.

## 3. Blindness: what is honest and what is not

NO HONEST OUTCOME-BLINDNESS IS POSSIBLE, and I am not manufacturing any.
I wrote roles/Metis/ledgers/EPISODE_PRECONDITION_2026-09-11.md on
2026-09-11 and it already contains, for all five episodes, the outcome
and in several cases the mechanism. Specifically, before freezing this
document I already knew:

    E3 SAXL       the registry held the FALSE form ~3 months; the arXiv
                  withdrawal was public and dated 2025-12-20
    E4 GEOMETRY-1 retracted 2026-04-19; the missingness diagnostic was
                  run 2026-04-29, ten days LATE; ~52% of rank signal
                  attributable to marginals; pass_overall=FALSE
    E5 EREBOS     "0 signal passes survive nulls, 1 infra pass stands"

So the withheld episodes are withheld in a WEAKER sense, and the weaker
sense is stated here so nobody has to take my word later:

    WITHHELD MEANS: I have not reconstructed their pre-cutoff evidence
    sets, their decision points, their dependency structure, their
    instrument status, or their candidate discriminators. Those are the
    inputs the specimen consumes. I know the ANSWERS; I have not yet
    built the QUESTIONS.

This is a real but partial guarantee. It protects against shaping the
specimen's MECHANISM around three more evidence structures. It does NOT
protect against my choosing, when I build those ledgers, the evidence
items that make the specimen look good. That second risk is unmitigated
by the split and is listed in section 8 as the season's largest threat.
The mitigation I can offer is procedural, not structural: every E3/E4/E5
evidence item must cite a committed artifact and a timestamp, and the
ledger records items I expect to HURT the specimen as well as help it.

## 4. Historical cutoff rule, frozen

For each episode:

  a. The CONSEQUENTIAL DECISION is the point at which Prometheus chose
     what to do next and spent something non-trivial on it (compute,
     wall-clock, a promotion into a registry, a published claim).
  b. The CUTOFF is the instant immediately before that decision.
  c. An evidence item is PRE-CUTOFF only if its existence before the
     cutoff is established by one of:
       COMMIT   a commit timestamp in this repository at or before the
                cutoff, for a path that contains the item
       EXTERNAL a dated external artifact (arXiv withdrawal notice, a
                published paper) whose date precedes the cutoff
       INTERNAL a contemporaneous ledger, log line or preregistration
                carrying its own timestamp at or before the cutoff
     and its availability grade is recorded as one of those three.
  d. Any item whose pre-cutoff existence cannot be established that way
     is graded UNAVAILABLE_UNPROVEN and the specimen does not see it.
     It is NOT assumed post-cutoff; it is assumed unusable. This is
     deliberately conservative and will cost the specimen evidence it
     might legitimately have had.
  e. The existence of a document TODAY establishes nothing about its
     availability at the cutoff. Untracked files are the sharp case:
     Skopos demonstrated on 2026-09-11 that agents/skopos/reports/ was
     ignored by .gitignore twice over and its six reports were never
     committed, so they have NO provenance at all and cannot be dated
     from the repository.

## 5. Vocabulary v0, frozen (7 concepts, every one on probation)

    DEPENDENT              two items share a load-bearing upstream token
    ORTHOGONAL             two items discriminate different live
                           explanations
    STALE                  admissible once; contrary information was
                           available and is unincorporated
    INSTRUMENT_SUSPECT     the observation is producible by measurement
                           failure as well as by the phenomenon
    BASE_RATE_CONFOUNDED   an easier background mechanism explains the
                           bulk of the result
    CHEAP_KILL_AVAILABLE   a materially cheaper cutoff-available test
                           discriminates live explanations
    VETO                   confidence must not be compounded until a
                           named thing is resolved

PROBATION RULE, frozen: a concept that is not load-bearing in at least
one CONSTRUCTION episode by the time the specimen freezes is DELETED, not
carried. I expect to delete at least one. If all seven survive I should
be suspected of building an ontology rather than a mechanism.

## 6. Success criteria, frozen

The specimen SURVIVES the retrospective only if ALL of the following hold
on the replay, each with committed rows:

  S1  On E1 it emits AGREEMENT_NOT_ADDITIVE naming the shared upstream,
      and a VETO naming the base-rate explanation as live, from
      PRE-CUTOFF evidence only.
  S2  On E2 it does NOT credit the April llm_alive=0 observation as
      valid evidence for the eventual (correct) conclusion; it marks it
      INSTRUMENT_SUSPECT from cutoff-available information.
  S3  On adversarial test C (true independence) it emits NO veto.
  S4  On adversarial test F (veto flood) it emits no veto on the major
      conclusion.
  S5  On adversarial test E it returns UNKNOWN, never ABSENT.
  6.  It names at least one cutoff-available discriminator that is both
      cheaper (on a declared ordinal scale) and discriminating (its
      outcomes partition the live explanation set) than the experiment
      actually run, in at least two episodes.

VETO RATE BOUND, frozen now so it cannot be moved later: across the six
adversarial tests A-F, the specimen must emit vetoes on at most 4 of 6.
A specimen that vetoes 5 or 6 of 6 has degenerated into permanent
skepticism and FAILS regardless of its episode performance. I am naming
the number before I know what it will do.

## 7. Failure criteria, frozen

The specimen FAILS if any of:

  F1  It requires an LLM to produce any veto, dependency or ranking.
  F2  The dependency structure for a construction episode cannot be
      written without consulting post-cutoff evidence.
  F3  Vetoes exceed the bound in section 6.
  F4  ORTHOGONAL cannot be operationalized without a subjective call,
      i.e. two reasonable analysts reading the same pre-cutoff record
      would assign different discriminates-against sets and the
      specimen's output flips.
  F5  It scores well on all five only after post-hoc adjustment made
      once the episode outcome was visible.

INSTRUMENT_INADEQUATE is the ruling if the historical record cannot
support the reconstruction at all -- not a fallback for a mechanism that
worked badly.

## 8. Known contamination risks, frozen

  R1  HINDSIGHT IN THE RECORD. Every surviving postmortem was authored
      with the outcome known, so the signal that mattered is more
      legible in the document than it was in the moment. Partial
      mitigation: commit timestamps over document contents wherever the
      two can disagree.
  R2  HINDSIGHT IN ME. I know all five outcomes (section 3). The split
      does not fix this. Largest threat: evidence-item SELECTION in the
      withheld ledgers.
  R3  SELECTION OF THE EPISODE SET. Five episodes the operator
      remembered. Memorable failures are not average failures, and four
      of the five are failures of a kind that got written up, which is
      itself a filter.
  R4  AUTHOR-SCORES-OWN-MECHANISM. I propose the rule, build the
      specimen, choose its inputs, and grade it. Declared as a conflict
      of interest in calibration/CALIBRATION.md. An independent attacker
      (Kairos, Charon, Nemesis or Elenchus) is named in the receipt; the
      season does not claim validation without one.
  R5  N=5. No statistical claim is licensed. The withheld episodes test
      COHERENCE, not performance, and will be reported as such.
  R6  MY OWN TOOLING. Three instrument errors on 2026-09-11 (stalled
      progress meter believed over file count; a CR grep that counted
      lines; a prefix read that produced a false negative-existence
      claim). The specimen must be executable and replayable precisely
      because my reading of evidence is demonstrably unreliable.

## 9. P-5, restated and standing

    A deterministic composition rule fitted on these five episodes will
    NOT beat the best single evidence channel out of sample. The season's
    honest output is more likely a negative result plus a named veto
    primitive than a working selector.

P-6 also stands: the VETO list will outlive the ranking.

I am not to optimize against these. If the specimen does beat the best
single channel, that is a result I must attack rather than report.

## 10. What this season may NOT claim, whatever happens

Not that Metis improves Prometheus decisions. Not that composition beats
single-channel selection. Not that five episodes generalize. The
strongest licensed claim is exactly:

    COMPOSITION-VETO MECHANISM SURVIVES RETROSPECTIVE SPECIMENS

and the weakest honest one is that it does not.
