# ARCHAEON — charter

**Seat opened** 2026-09-05. **Layer of operation:** the read side of the
experiment loop. Archaeon is the only seat whose output is a *question*.

## What Archaeon is

An experimental-archaeology service. It reads the fossil record left by SFE and
PEW, looks for places where the record is *unsettled*, and proposes the next
experiment. That is the whole job:

    READ FOSSILS -> FIND A POSSIBLE WEAK STRUCTURE -> PROPOSE A PROBE

and when it finds no weak structure:

    EXPLORE

## The loop Archaeon closes

    PEW / SFE fossils -> Archaeon -> PostgreSQL experiment queue -> Vivarium
      -> SFE / worlds / players -> PEW -> Archaeon

Archaeon owns exactly one arrow: fossils -> queue. It does not run experiments,
does not execute worlds, and does not write to PEW's evidence tables.

## What Archaeon is NOT

Archaeon is **not a claim judge.** It holds no scientific authority whatsoever.
It may not:

- promote, support, or retire a scientific conclusion;
- declare a lineage dead, exhausted, or uninteresting;
- reject an observation because it conflicts with prior expectation;
- assert that a hypothesis is disproven;
- recommend that experimentation stop.

A detector firing means one thing only:

> "This region may be worth interrogating again."

It never means "a phenomenon has been discovered."

Absence of a detector firing means one thing only:

> "Use the exploration fallback."

There is no third reading. **Archaeon has no negative authority.** This is
enforced mechanically, not by convention — see `archaeon/queue.py`
(`assert_no_negative_authority`) and `archaeon/tests/test_negative_authority.py`,
which fail the build if a forbidden claim reaches a queue record.

## Standing constraints

1. **No LLM in the decision path.** Nothing in `archaeon/` may call a model to
   decide what is interesting, which experiment to run, or which combination
   "makes sense". Detectors are arithmetic with thresholds in a config file.
2. **No human scientific priors.** Exploration draws from the *measured*
   coverage of the world/player space, never from literature or semantics.
3. **Deterministic and inspectable.** Same corpus + same seed -> same proposal.
   Every threshold is a named constant in `archaeon/config.py`.
4. **Cadence is a database invariant,** not a policy note: at most SIX
   autonomous proposals per UTC day and at least FOUR HOURS between them,
   enforced so two concurrent Archaeon instances cannot evade it.
5. **Provenance is mandatory.** A proposal that cannot answer "which fossils,
   which detector, which values, which alternatives, why this one, what seed"
   is not written.
6. **Eligibility is reported separately from firing.** "Zero detectors fired"
   and "zero rows were eligible to fire" are different facts and Archaeon must
   never let the second be read as the first.

## Posture on its own output

Archaeon is designed to be easy to prove wrong. Its detectors are crude on
purpose. If a detector's null firing rate is bad, that is a measurable property
of the detector and it should be measured (`archaeon/calibrate.py`), not argued
about. Sophistication comes later; a v0 nobody can audit is worth nothing.
