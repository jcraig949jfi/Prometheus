# HANDOVER to Archaeon -- two rulings, deliberately separate

From: Atalanta (retiring)
To: Archaeon
Kind: ruling request
Base: origin/main at the commit carrying roles/Atalanta/RETIREMENT_2026-09-11.md,
worktree D:\Prometheus-worktrees\atalanta-base-role, host SPECTREX5 (M2).

The operator accepted this seat's recommendation on 2026-09-11: clean
retirement, no replacement mission. This is a handover, not a proposal
this seat will follow up on. Nothing below is Atalanta's to enforce or to
chase, and Atalanta will not answer on any of it after this message.

## Ruling 1: base rule 10, as already filed

roles/Atalanta/PROPOSED_INVARIANT_2026-09-11.md, reported in comms #86.
Unchanged. Bound consecutive NON-PRODUCTIVE ticks, park at N, post once to
a NAMED accountable seat; no bound or no seat, no launch. Reference
implementation and 9 controls in roles/Atalanta/reference/, 9 passed.

The operator's reading, which should travel with it:

    "Rule 10 is worth adopting, but it is containment rather than
    prevention. It turns '354 perfectly punctual useless ticks' into at
    most N useless ticks."

And on the dependency, which is the part most likely to be optimised away
by a later editor who finds it fussy:

    "I also like the distinction between emission and productivity. It is
    exactly the kind of anti-cheat Prometheus needs. A heartbeat,
    artifact, database row, or successful process exit is evidence that
    machinery operated; none is evidence that useful work occurred. Rule
    10 depending on Rule 8's productivity predicate preserves that
    distinction."

If rule 10 is ever rewritten to key on emission instead, it becomes
decorative: Atalanta emitted a well-formed artifact on all 354 dead ticks
and scores 354/354 productive under any emission-keyed bound. The
companion control in reference/test_null_bound.py asserts exactly that
failure, so the regression is testable rather than merely warned about.

## Ruling 2: the producer-declaration invariant, as its own ruling

The operator's formulation of the root defect, verbatim:

    "A consumer was allowed to invent the producer's interface, and then
    mistake failure of that invented interface for failure of the
    producer."

    "The stronger follow-on is the producer-declaration invariant: a
    consumer cannot launch against an output location/interface that the
    producer has not explicitly declared. That belongs above Atalanta and
    should probably become its own Archaeon ruling rather than being
    smuggled into Rule 10."

This seat agrees and had already declined to bundle it, for the same
reason stated from the other direction: prevention and containment are
different claims, they cost different amounts, and a rule that carries
both can be adopted for the cheap half and credited with the expensive
one.

Evidence this seat can hand you for the ruling:

- daemon.py:63-67. Three literal paths, chosen by the consumer's author,
  as an inference about where Apollo ought to write. Apollo never agreed
  to them, was never asked, and never wrote to any of them.
- daemon.py:222-226. The liveness test is `root.exists() and
  root.is_dir()`. It answers "is there a directory at this string", not
  "is my producer alive and emitting". Same return type, different
  question. Base rule 2 one layer below Techne's `which("gcc")`.
- The consequence that makes it a program defect rather than a bug: the
  consumer CANNOT DISTINGUISH its own misconfiguration from its producer's
  death, so it reports the second while suffering the first. 354 artifacts
  accuse Apollo of being absent. Apollo committed 12 times during that
  exact window.
- Talos independently named the same phantom apollo/runs in the same week
  and marked it "never existed". Two authors, no contact, one invented
  address. That is evidence about a system that permits guessing, not
  about two people making one mistake. Filed as a NULL with its search
  scope: no common source for the path was found.
- Base rule 9, which you added from this seat's #47, does not close it. A
  launch-time liveness check phrased as "does my configured input exist"
  can pass against an address that exists, is empty, and belongs to
  someone else. The gate then reads legitimate and the silence looks
  earned.

What a ruling would have to settle, in this seat's view and not binding on
yours: where a declaration lives and what it contains; who is refused at
launch when it is absent (the consumer, necessarily, since the producer
may be dormant for good reasons); and whether an existing producer without
a declaration blocks its consumers immediately or after a migration
window. The blast radius is every producer in the program, which is
precisely why it should be costed on its own.

## Not asked, and deliberately so

Nothing else. This seat is retired. It is not requesting a role in either
ruling, not offering to draft the declaration format, and not asking to be
told the outcome. The residue is committed and navigable; a later search
can reach it without Atalanta.
