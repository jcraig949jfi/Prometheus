# PREREG -- Hecate Pass 3 generator v2 and probe round 3 (HECATE-05 repaired)

Frozen: 2026-09-30Z, before any v2 spec exists. Author: Hecate[m1-dd0c3882].

## Why (the evidence)

Probe rounds 1-2: 12 of 29 built worlds were unattainable or unbuildable
as specified (hecate/programs/PROBE_ROUND{1,2}_REPORT.json): positive
controls that could not reach the spec's own threshold, clauses that
contradict each other, null twins that already succeed, a spec that
deferred to another world. The v1 generator never ran anything, so no
threshold was ever checked. This is a defect of the instrument, not
evidence about the triplicates.

## Which programs (8)

- SPECULATIVE with one valid NULL: HT-056d3ac561, HT-974471f045,
  HT-ae38c641b1, HT-e106e1603b.
- PARK whose recorded reason is "Pass 3 produced no testable world in
  two tries": HT-37e311ce05, HT-55162c0ac0, HT-8a87057933, HT-faa9277e02.
  PARK is revivable; the reason for these four PARKs is exactly the
  defect repaired here, so they are revived. Programs PARKed on two
  valid NULL readings, or by Pass 4, are NOT revived.

## Generator v2 (one fresh instance per program; prompt pass3_v2.md)

Writes TWO new worlds (W5, W6) for its program, from mechanisms and
lenses already in program.json (it may target mechanisms already tested,
with a different world). For each world, before the spec is final:
  1. spec.json with the v1 world fields, fully self-contained (no
     reference to any other world), success and failure criteria as
     separate numbered clauses;
  2. controls.py implementing POSITIVE_CONTROL (the effect present by
     construction), CHEAT (success injected into the observable) and
     NULL_TWIN, run for >= 5 seeds, writing control_rows.jsonl;
  3. ATTAINABILITY.json: for every success clause, the value under the
     positive control and under the null twin, and whether the clause is
     attainable (positive meets it) and discriminating (twin does not);
     for any clause that compares treatment against twin or control, the
     range the treatment would have to reach, stated as a number.
A world is FROZEN only if every clause is attainable and discriminating
on the control rows. The generator may revise a spec any number of times
BEFORE freezing (no treatment exists yet); each revision is recorded.
It must not write treatment code. A program where neither world freezes
records NO_FREEZABLE_WORLD.

## Probe round 3

For each frozen world (at most one per program: the lower-cost of W5/W6,
ties by id), a fresh implementer (prompt probe_impl_v3.md) builds ONLY the
treatment and control arms against the frozen spec and frozen controls,
reruns controls in the same code path, and classifies with the round-1
classes. It may not modify spec.json, controls.py or thresholds. If the
rerun controls disagree with ATTAINABILITY.json, the outcome is
INSTRUMENT_FAIL (reproducibility), never a repair.

Consequences: as round 2's table, counting only valid readings. A
revived PARK program that reads NULL goes back to PARK with two reasons.

## Budget

Generator: <= 5 core-min of control runs per world. Probe: <= 10 core-min
per world. <= 8 x (10 + 10) = 160 core-min. MWO-0004 R2.

## What would falsify the repair

If round 3 still has >= 3 of 8 worlds unattainable, INSTRUMENT_FAIL or
NO_FREEZABLE_WORLD, the generator is not repaired and Pass 3 needs a
different design (e.g. worlds proposed by one instance and adversarially
pre-tested by another). That is recorded as the outcome of this
preregistration.
