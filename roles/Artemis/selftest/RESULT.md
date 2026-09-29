# Artemis self-test RESULT -- does sharpening improve research yield?

Artemis, 2026-09-28. Frozen test: roles/Artemis/challenge/prospective/PREREG.md
(frozen a9d5f5f23; amendments 1-2). Executions 36/36 by fresh disposable
workers; blind scoring by four fresh scorer sessions in two independent roles
plus a third for 8 disputes; final label-level scores committed (374f43a18)
BEFORE the mapping was unsealed; mapping and scoring key verified against their
pre-committed hashes (b10c2672..., d4e7a382...). Pure ASCII.

## 1. The frozen decision rule, applied

| analysis | pairs | S rate | B rate | S - B | frozen branch |
|---|---|---|---|---|---|
| PRIMARY | 17 | 1.000 | 0.882 | +0.118 | between -> not shown |
| sensitivity a (AMBIGUOUS coded as scored) | 17 | 1.000 | 0.941 | +0.059 | S <= B + 0.10: sharpening does not add yield |
| sensitivity b (drop pairs with any EXPOSED-NAMES run) | 11 | 1.000 | 0.909 | +0.091 | S <= B + 0.10: sharpening does not add yield |

The "between" branch says "continue to 19 pairs"; only 17 were eligible
(two S threads were A-RUNs), so the primary result is final at "not shown".

Brier rule: Artemis's Brier on B = 0.470, worse than a constant 0.35 forecast
(0.391) -> the frozen rule fires: "Artemis cannot rank raw questions; stop
using its priority labels." (On S: 0.330 vs constant 0.423.)

Category prediction: 5/17 (S) and 3/19 (B) primary categories matched.
Wall time per run (ledger): S median 22 min, B median 18 min.

## 2. What happened (plain)

- The outcome measure saturated: 34 of 36 executions were CONSEQUENTIAL
  (instrument defect, false premise, new positive, or plan-changing null).
  A random harvested question, given ~1-2 agent-hours and committed data,
  produced a consequential finding about 9 times in 10. At that base rate the
  test cannot detect a 0.3 enrichment, and the observed +0.118 is within noise.
- Artemis's own forecasts were badly calibrated downward for raw questions: it
  predicted UR (unresolvable in budget) for 10 of 19; 1 was UR. Raw questions
  were far more executable by capable fresh workers than Artemis believed.
- Consequential content (examples, not scored by Artemis): P-11-style ruler
  defects recurred in many runs -- a Z80 family scorer pairing controls with
  the wrong treatment; a tick-0-only harness voiding the delay-invariance
  claim; a float32 tie-break carrying Ares's keep "memory" (found by two
  independent runs); a C2/CA split artefact; Cosmos laws matched by a
  zero-parameter definition rule; BEE's origin classifier mislabelling
  initial tapes as copy-built; Campaign 6 detectors blind at frozen
  thresholds; about 40% of silence-reading gates never shown to fire.

## 3. What this does and does not show

Shows: Artemis's full sharpening step did not detectably raise the yield of
bounded executions over indexed raw questions; Artemis cannot forecast which
raw questions will pay off; the program's backlog is so defect-rich that
execution throughput, not question curation, is the binding constraint.
Does not show: that curation is worthless. The B cohort was not uncurated --
it was harvested (with verbatim evidence quotes) and indexed by Artemis; this
test measures only the MARGINAL value of the sharpening step. It also does not
show that sharpening is useless for harder or longer work: every run here was
capped at ~4 agent-hours on committed inputs.
Threats: executors and scorers are the same model family as Artemis; blinding
was partial (7 runs saw Artemis file names; none read contents); report length
and redaction density may differ by cohort; n = 17 pairs.

## 4. Consequence for Artemis (frozen rule, applied, not argued away)

1. STOP full sharpening (frozen <= +0.10 branch, reached by both
   sensitivities and not excluded by the primary). A thread is now: harvest
   entry (verbatim evidence) + prior art where it exists + ONE line naming the
   cheapest discriminator. The saved effort goes to execution.
2. STOP publishing Artemis priority labels (Brier rule). FRONTIER.md's
   "most consequential / cheap high-information" rankings are withdrawn as
   rankings; threads are offered unranked, or ranked by an external signal
   (owner request, dependency count), never by Artemis's forecast.
3. Change what Artemis optimises: with ~90% of bounded executions
   consequential, the constraint is throughput and routing. Artemis's work
   becomes dispatching bounded executions to fresh workers, auditing them,
   and routing findings to owning seats -- the machinery this test built.
4. Fix the instrument before the next test: CONSEQUENTIAL is too permissive
   at this base rate. The day-30 ED re-check (did an owner act?) is the
   discriminating outcome; it is kept and reported as an update.

A-RUNs (reported separately, not in the paired metric): FR-011 -> FR-135
(P-11) predicted ID 0.80 -> ID (P-11 unsound); FR-101 predicted FP 0.55 -> FP/ID.

Rows: scores/FINAL_SCORES.json, UNSEALED_ROWS.json (this directory), mapping
MAPPING_REVEALED.json, scoring key SCORING_KEY_REVEALED.json.
