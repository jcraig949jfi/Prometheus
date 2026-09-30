# PREREG -- Hecate probe round 1: Pass 3 -> cheap probe -> Pass 4 (HECATE-08)

Frozen: 2026-09-30Z, while the 16 Pass 0-3 generators were still
running, BEFORE the author had read any world spec. Author:
Hecate[m1-dd0c3882].

## Which world is probed (one per triplicate, breadth first)

For each of the 16 frozen programs, a world W in program.json
"experiments" is ELIGIBLE iff, checked by code (hecate/probe_select.py):

  E1  the program validates (hecate.schema.validate_program == []);
  E2  W.cost_estimate parses to <= 10 CPU core-minutes;
  E3  W has non-empty null_twin, positive_control, control;
  E4  W.success_criterion contains a digit AND a comparator
      (<, >, <=, >=, =, "at least", "at most", "exceeds", "below",
      "above", "less than", "more than", "fewer than");
  E5  W.stupid_explanations has >= 3 entries.

The probed world is the eligible world with the lowest parsed
cost_estimate; ties broken by id order. A triplicate with no eligible
world is recorded NO_ELIGIBLE_WORLD (a fact about its Pass 3, not a
kill of the triplicate) and gets no probe this round.

## How it is probed

The spec is frozen by the commit that holds program.json before any
implementation exists. An implementer (a fresh generator instance) builds
the world, its null twin, its positive control, and a CHEAT control
(success injected directly into the observable, to show the evaluator
can see success) under hecate/programs/<id>/worlds/<W>/, with >= 5
seeds per arm, and writes rows (one JSON line per seed x arm) plus an
evaluator that applies the spec's success and failure criteria as
written. Where the spec's criterion is ambiguous, the implementer
records the reading it chose in the world's IMPLEMENTATION_NOTES.md
before running anything; it may not change the threshold.

Faithfulness guard: the implementer may not tune any parameter after
seeing a treatment-arm result. Every run's parameters are written to
the rows. A second attempt after a crash or a bug is allowed and
recorded; a second attempt because the result was unwelcome is not.

## Outcome classes (decided by the evaluator's output, not by prose)

  SIGNAL           treatment meets success_criterion; null twin does not;
                   positive control and cheat control both detected
  NULL             treatment fails the criterion (or meets failure_criterion);
                   positive control AND cheat control detected -- the
                   instrument could have seen it
  CONFOUNDED       the null twin also meets the success criterion
  INSTRUMENT_FAIL  positive or cheat control not detected; no reading of
                   the treatment is made
  NOT_BUILT        the spec could not be faithfully implemented within
                   10 core-minutes or without inventing the mechanism;
                   the reason is recorded

## Consequences (allocation states; base role: no LLM adjudicates)

  SIGNAL           program -> PROBING; world goes to Pass 4 (first
                   falsification: the spec's stupid_explanations are
                   each tested before any escalation)
  NULL             the world's claim at this configuration is killed,
                   with rows; the triplicate stays SPECULATIVE and may
                   probe its next eligible world in round 2; two NULL
                   worlds -> PARK
  CONFOUNDED       counts as NULL for the world, and the confound is a
                   recorded finding about the spec
  INSTRUMENT_FAIL  one instrument repair allowed, then rerun; a second
                   INSTRUMENT_FAIL -> NOT_BUILT
  NOT_BUILT        next eligible world in round 2

No program reaches PROMISING in round 1: that needs a Pass 4 survival
under its own preregistered predicate.

## Eligibility and attainable range, stated in advance

At most 16 probes, <= 10 core-minutes each, <= 160 core-minutes total
(well inside MWO-0004 R2). A round in which every probe is NULL or
CONFOUNDED is a legitimate and reportable result about the first
selection and about Pass 0-3 as a generator of worlds; it is also data
for the meta-experiment v2 (usefulness). "Nothing fired" and "nothing
could have fired" are separated by the positive and cheat controls.
