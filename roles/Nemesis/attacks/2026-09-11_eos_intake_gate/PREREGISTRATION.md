# NEMESIS-01 -- preregistration: attack on the Eos intake gate

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. Written BEFORE any attack code was executed and
committed in its own commit so the order is in git history (base
doctrine s2). Nothing in this directory besides this file exists at the
commit that carries it.

Built from 742a6c8b3 in D:\Prometheus-worktrees\nemesis-adopt on branch
nemesis/eos-scorer-attack-2026-09-11.

## Honest statement of what I already know

I have READ agents/eos/src/intake.py (449 lines) and
agents/eos/tests/test_intake.py in full. I have RUN nothing. These
predictions are therefore informed by the source, not blind, and that
weakens them exactly as much as it sounds like it does. They are written
down anyway because a prediction made after reading the source and
before running the code can still be wrong, and the ones below are
constructed so that each can fail in the direction that costs me.

## The target, and the question that is mine rather than Eos's

Target: `agents/eos/src/intake.py`, the Eos intake gate. Owner: Eos.
Not modified by this attack; not a byte of it is edited (base rule 6).

Eos has ALREADY done the honest thing and shipped cheat controls. Eos's
own docstring names a hole -- the gate verifies that a referent EXISTS,
not that it is the RIGHT one -- and `test_cheat_a_real_but_unrelated_
referent_still_passes` locks that hole in deliberately so that closing it
breaks the test. Credit where it is due: this instrument was built by a
seat that went looking for its own failure and wrote it down.

So "can a fraud pass?" is already answered, by Eos, in the affirmative.
That is not my question. Mine, as the operator posed it, is the harder
one:

> WHAT IS THE CHEAPEST INCAPABLE POPULATION THAT CAN NEVERTHELESS CROSS?

An instrument with one known hand-built counterexample and an instrument
whose passing-fraud population is mechanically enumerable at near-zero
cost per member are in very different conditions, and the difference is
not visible from the counterexample. Density and cost are the
measurements Eos has not taken.

## The rule this attack enforces (operator, 2026-09-11)

> No instrument earns trust merely because it rejects negatives. Nemesis
> must attempt to make it ACCEPT A FRAUD.

## Populations to be constructed

A FRAUD here means: an item and claim pair carrying ZERO of the
capability the gate's terminal state asserts -- no relationship between
the item and the referent, no real measurement, no absorbed knowledge --
assembled mechanically without reading or understanding anything.

  POP-NULL   empty / missing claim fields. The POSITIVE control on my own
             harness: the gate MUST refuse these. If it does not, the gate
             is inert and every other number here is meaningless.
  POP-A      ANCHOR frauds: a real tracked file, plus a token drawn
             mechanically from that file's own bytes, plus 20+ characters
             of filler falsifier, plus a rationale avoiding the banned
             word list. The item text is unrelated to the referent by
             construction.
  POP-B      ACQUIRE frauds: a capability marker that is a fresh random
             string (so `git grep` is guaranteed 0 hits), a destination
             whose parent exists, a consumer path that exists.
  POP-C      RESOURCE frauds: an observation block with every required
             key present and fabricated, declaring
             observed_by = "eos-intake". No measurement is taken.
  POP-MIN    the shrink of whichever fraud crosses, reduced toward the
             cheapest member that still crosses.

## Predictions, each able to lose

P1  POP-A crosses (reaches PENDING_ADMISSION) at a rate >= 0.90.
    LOSES IF < 0.90, which would mean the gate carries a semantic
    defence I did not find by reading it.

P2  The cheapest crossing ANCHOR fraud has a referent token of length 1
    and a falsifier of exactly 20 filler characters.
    LOSES IF a length-1 token or a content-free 20-char falsifier is
    refused.

P3  POP-B crosses at a rate >= 0.90 using random-string capability
    markers.
    LOSES IF < 0.90.

P4  POP-C reaches the TERMINAL state RESOURCE -- settled by the gate
    with no human admission step -- on a wholly fabricated observation
    that merely asserts observed_by = "eos-intake".
    LOSES IF the gate refuses, i.e. if some authenticity check exists
    that I did not find.
    This is the prediction I most want to be wrong about, because
    RESOURCE is the one state the gate settles on its own.

P5  POP-NULL crosses at rate 0.00 (my positive control: the gate CAN
    refuse).
    LOSES IF anything in POP-NULL crosses, which would invalidate this
    whole attack rather than condemn the gate.

P6  The passing-fraud population for ANCHOR is mechanically enumerable
    at a scale of at least 10,000 distinct members from the tracked tree
    alone, at a construction cost of no reading and no model call.
    LOSES IF construction requires any semantic step.

## What each outcome licenses me to write

  DEATH CERTIFICATE   only if POP-NULL is refused (P5 holds) AND the
                      fraud populations cross on all three paths at high
                      rate AND the crossing requires no capability. Then
                      the statement is: this gate does not distinguish
                      capability from typing.

  BOUNDED STATEMENT   the expected outcome. The gate verifies real
                      properties (a path exists; a token occurs; a grep
                      returns zero; a directory exists; a timestamp is
                      fresh). The statement then names EXACTLY which
                      property each check verifies and which property a
                      reader might wrongly assume it verifies. A bounded
                      statement is not a lesser result; it is the
                      instrument's actual specification, written by an
                      adversary instead of by its author.

  ATTACK FAILED       if P5 fails, or if my harness cannot execute the
                      gate's real scoring path. An instrument-error
                      result is reported as instrument error and NOT as
                      a fact about the gate.

## Constraints I am holding myself to

- The gate is executed, never reimplemented. If I cannot execute it, the
  result is NOT_EXAMINED, not SURVIVES.
- Not one byte of agents/eos/** is modified.
- Chance floor and eligible count are computed and published beside every
  rate. "Nothing crossed" and "nothing could have crossed" are different
  facts.
- A crossing rate is a statement about a POPULATION I built. It is not a
  statement that Eos's real first-season items were frauds; they were
  not, and 6 of them reached PENDING_ADMISSION on the seat's own pass.
- I am a conflicted party: this is my seat's first specimen and a
  dramatic result flatters my lane. A bounded statement is the outcome I
  expect and it is written up with the same energy as a kill would be.
- Eos is notified through comms with this preregistration and the result,
  whichever way it goes. The operator directed this attack, which settles
  NEM-XL-2 for this instance in the direction of notification; the
  general rule is still an open decision.

## What would make me wrong in a way that matters

If the gate refuses POP-A and POP-B at any appreciable rate, then
referent-existence and grep-absence are doing far more work than they
look like they are doing, and I will have learned that a cheap
existence check is a stronger filter than an adversary expects. That is
a result worth having and it is the one that costs me.
