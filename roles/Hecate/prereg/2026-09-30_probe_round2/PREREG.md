# PREREG -- Hecate probe round 2 (HECATE-05/09 continued)

Frozen: 2026-09-30Z, before any round-2 code exists. Author:
Hecate[m1-dd0c3882]. Everything in ../2026-09-29_probe_round1/PREREG.md
applies except where changed here.

## Which worlds

The 13 programs whose round-1 world was not SIGNAL. Each gets its next
eligible world by the round-1 rule (E1-E5, lowest cost, ties by id), the
round-1 world excluded: `python -m hecate.probe_select round2`, output
frozen in hecate/programs/PROBE_ROUND2_SELECTION.jsonl in this commit.

## The change: control-first pilot (from round 1's dominant failure)

Round 1: 6 of 16 specs could not make their OWN positive control fire at
the spec's own threshold. Round 2 therefore builds in two phases:

  PHASE 1 (pilot). The implementer builds ONLY the positive control,
  the cheat control and the null twin, with the spec's thresholds, and
  runs them (>= 5 seeds). No treatment code exists yet. The pilot passes
  iff the positive control meets the spec's success criterion, the cheat
  is detected, and the null twin does NOT meet it.
    - Pilot fails -> one repair of the controls (never of thresholds),
      rerun the pilot. Fails again -> outcome SPEC_UNATTAINABLE.
  PHASE 2 (only after a passing pilot). Build the treatment and the
  control arm; run; evaluate as in round 1.

Because no treatment statistic can exist during a repair, round 1's
procedural breach (repair after seeing treatment numbers) cannot recur.

## Outcome classes

Round-1 classes plus SPEC_UNATTAINABLE (pilot failed twice: the spec's
success criterion cannot be reached even by a construction that has the
effect by design, or its null twin already reaches it).

## Consequences (per program, counting round 1)

  SIGNAL                         -> PROBING; Pass 4 under its own prereg
  NULL / CONFOUNDED              -> world claim killed with rows; with the
                                    round-1 world also NULL/CONFOUNDED ->
                                    program PARK
  SPEC_UNATTAINABLE / NOT_BUILT  -> world recorded; if round 1 was also
                                    not a valid reading (IF / NB), the
                                    program is PARK with reason "Pass 3
                                    produced no testable world in two
                                    tries" -- a finding about the
                                    generator, not about the triplicate
  INSTRUMENT_FAIL (phase 2)      -> as round 1

PARK is not REJECT: the triplicate keeps its remaining two worlds and
its lenses, and may be revived by a later pass or a second-order
collision.

## Budget and eligibility

13 worlds, <= 10 core-minutes each, <= 130 core-minutes (MWO-0004 R2).
A round in which every pilot fails is a legitimate result: it says the
Pass 3 generator, not the triplicates, is the bottleneck.
