# PREREG -- does Artemis's sharpening improve research yield?

Artemis, 2026-09-28, frozen BEFORE any thread in either cohort is
executed by anyone for this purpose (operator challenge s2). The commit
that adds this file is the freeze; any later edit is an amendment with
its own dated section below the END line. Pure ASCII.

## Question

Does a thread that went through Artemis's sharpening (question, evidence,
uncertainty, cheapest discriminator, prior art) produce consequential
epistemic outcomes more often, or more cheaply, than a comparable thread
taken from the raw backlog with the same execution budget?

## Cohorts (no hand selection)

- S (sharpened): all 19 threads that were SHARPENED or MATURE in
  backlog/INDEX.md at the pass-1 commit -- every one, none chosen.
- B (baseline): for each S thread, one RAW thread from the same cluster
  and host class, drawn without replacement by draw_cohorts.py, seeded
  with sha256 of the committed challenge directive
  (5bbd277ca664a5f5...). Output: COHORTS.json (19 pairs, all matched on
  cluster and host; no fallback needed). Excluded from B: BLOCKED,
  ANSWERED, SUPERSEDED, ops-owned rows.

## Outcome categories (one primary per executed thread)

  ID  reveals an instrument, ruler or harness defect
  FP  exposes a false premise (the thread's or a cited result's framing
      is wrong)
  ED  changes an engine's design, a seat's plan, or a program standard
      (a committed change or an explicit owner decision cites it)
  PR  a new positive result that survives its own controls
  NU  a clean null (discriminator worked; the effect is absent)
  KN  reproduces an already-known result
  UR  unresolved: the discriminator was inadequate, or the work could not
      be completed with the stated inputs

CONSEQUENTIAL = ID, FP, ED or PR; or NU when it changes a thread's state
or a seat's plan. KN and UR are not consequential.

## Execution protocol

1. Paired execution (primary). Pairs are executed by fresh workers (a new
   agent session or a seat not involved in writing the thread), one S
   and its B, with the SAME budget: 4 agent-hours and <= 1 CPU-hour on
   a Linux node, committed inputs only. S workers get the thread file
   (+ chop if any). B workers get the INDEX row and the raw harvest
   entries only -- NOT an Artemis-written brief. Each worker commits a
   short report: what was done, the result, cost.
2. Organic execution (secondary). Any execution by any seat during the
   window is also scored, flagged ORGANIC, and analysed separately
   (organic pickup is biased toward sharpened threads by visibility).
3. Artemis-run executions (flagged A-RUN). Artemis may run bounded
   experiments on cohort threads during this challenge (FR-011 now;
   possibly others). Those are scored but reported separately, because
   the predictor is also the executor.
4. Window: 30 days from the freeze. Threads not executed by then are
   recorded NOT_EXECUTED; the pickup rate per cohort is itself reported.

## Scoring

An independent scorer (a seat that did not write the thread, e.g.
Harmonia, or a fresh session given only the worker's report with the FR
id, the cohort label and all Artemis text removed) assigns the primary
category and CONSEQUENTIAL yes/no, using the definitions above. Artemis
does not score.

Primary metric: CONSEQUENTIAL rate per executed thread, S vs B (paired
executions only). Secondary: agent-hours per consequential outcome;
Artemis's prediction skill (category agreement, and Brier score on
p(consequential)) in S and in B separately -- this separates "sharpening
helps" from "Artemis can tell good questions apart".

## Decision rules (fixed now)

After >= 10 paired executions:
- S rate <= B rate + 0.10 -> sharpening does not add yield at this cost.
  Change the process: stop full sharpening; keep harvest + prior art +
  a one-line discriminator; spend the saved effort on executing.
- S rate >= B rate + 0.30 -> keep the process; continue to 19 pairs.
- Between -> continue to 19 pairs, then apply the same rules.
- If Artemis's Brier on B is no better than a constant 0.35 forecast,
  Artemis cannot rank raw questions; stop using its priority labels.
With 19 pairs the test can only detect large differences (about 0.3 in
rate); that limit is accepted and stated.

## Predictions (frozen)

p = Artemis's probability that the execution is CONSEQUENTIAL.

S cohort
| FR | predicted primary | p | one-line reason |
|---|---|---|---|
| FR-001 | FP | 0.50 | "payoff vs landscape" likely collapses into arrival-of-the-frequent once payoff is defined as finished-mechanism payoff |
| FR-002 | FP | 0.60 | basin and peak are confounded in Ares's own basin.json; the headline claim is unsupported |
| FR-010 | FP | 0.70 | most Block D recurrences will turn out design-bound (shared published ancestor) |
| FR-011 | ID | 0.80 | P-11 certifies self-painting; an information criterion will remove the copy-op-free "replicators" (A-RUN now) |
| FR-035 | ID | 0.50 | the linear P1 probe likely cannot see in-flight packet state (B1 INCOHERENT) |
| FR-038 | KN | 0.30 | surprise eviction retaining noise is a known effect |
| FR-043 | UR | 0.30 | needs an operator amendment and a heavy design; likely not completed in budget |
| FR-044 | NU | 0.45 | PRISTINE at 10x likely reaches the families: S4 was speed, no ceiling moved |
| FR-049 | KN | 0.25 | IQ-PORT-1 already provides the template; a rerun reproduces it |
| FR-051 | NU | 0.35 | failure-conditioned proposer shows no advantage on the z80 index |
| FR-057 | ID | 0.60 | ruler/instrument loci dominate the reversals |
| FR-058 | ID | 0.55 | at least one current verdict flips between 0.5x and 2x its threshold |
| FR-059 | ID | 0.50 | many current gates have no demonstrated firing case |
| FR-067 | UR | 0.25 | closure growth likely does not converge within caps / RAM |
| FR-070 | UR | 0.30 | Avida arms need a toolchain; census alone is thin |
| FR-094 | ED | 0.50 | <= 5/12 headlines recomputable from git -> evidence packs become a standard |
| FR-101 | FP | 0.55 | reset/encoding arms reproduce most of particle2's margin; CA line closes |
| FR-118 | FP | 0.50 | W16 solvers are neither of Nyx's architectures (plastic storage or a float artefact) |
| FR-132 | UR | 0.35 | splice results likely ambiguous between primitive and operator |

B cohort (predicted from the index row and raw harvest entries only)
| FR | predicted primary | p | one-line reason |
|---|---|---|---|
| FR-004 | UR | 0.25 | neutral-network re-encoding of Crius is a design task, not a 4-hour test |
| FR-006 | FP | 0.40 | task supply, not the improver, is the recursion blocker |
| FR-015 | KN | 0.30 | cargo erosion follows known error-threshold theory |
| FR-018 | UR | 0.25 | RIE-01's precondition failed; heavy to restage |
| FR-041 | UR | 0.20 | no label-free criterion ready to apply |
| FR-039 | UR | 0.20 | instrument build, not a test, within budget |
| FR-050 | UR | 0.20 | Engine Five rungs not implemented |
| FR-048 | KN | 0.25 | leverage-without-recursion restates A17 |
| FR-045 | FP | 0.45 | inherited machinery may not beat a generic enumerator at matched budget |
| FR-052 | UR | 0.20 | closing the loop needs infrastructure beyond budget |
| FR-061 | ID | 0.45 | a metric/tautology audit usually finds at least one defect |
| FR-063 | ID | 0.40 | a preflight on an existing grammar finds an unsupported comparison |
| FR-064 | UR | 0.25 | fingerprint labeller is a build |
| FR-068 | FP | 0.45 | capability numbers drop on tasks by another author |
| FR-071 | UR | 0.20 | monoculture is hard to operationalize in budget |
| FR-100 | ED | 0.35 | a lens-field proposal adopted by Atlas |
| FR-104 | FP | 0.40 | the delay knob was never hard |
| FR-117 | UR | 0.20 | Ludus line is dormant; data interpretation heavy |
| FR-009 | UR | 0.20 | horizon/myopia needs a new world |

Mean p: S 0.49, B 0.29. Artemis predicts S is enriched by about 0.2 --
below the 0.3 the test can reliably detect. If the truth is as predicted,
the likely outcome of this test is "between", and the honest reading will
be "not shown", not "shown".

END (frozen)

## AMENDMENT 1 (2026-09-28, after the freeze, before any cohort execution)

Cause: an adversarial review of the seven MATURE threads
(../MATURE_REVIEW.md) downgraded all seven, split FR-011 and FR-035, and
marked FR-010, FR-057, FR-101 and FR-118 answered-in-part. Cohort
membership, categories, predictions and decision rules are UNCHANGED.
Rules added:
- A split S thread is scored on its parent id: the first child executed
  under the protocol stands for the parent (FR-011 -> FR-135 or FR-136;
  FR-035 -> FR-137 or FR-138). Children are not added to either cohort.
- A thread found answered-in-part before execution keeps its frozen
  prediction; if the executed discriminator only re-confirms the part
  already answered, the scorer codes KN, which counts against S. This is
  deliberate: a sharpening process that cannot see prior answers should
  be penalised.
- Planned A-RUN executions by Artemis in this challenge: FR-135 (P-11
  soundness, from S/FR-011) and FR-101 (reduced). They leave the paired
  sample (15 pairs remain eligible) and are reported separately. FR-118
  and FR-057 are deliberately NOT run by Artemis, to keep their pairs
  (with FR-117 and FR-061) available for paired execution by fresh
  workers.
