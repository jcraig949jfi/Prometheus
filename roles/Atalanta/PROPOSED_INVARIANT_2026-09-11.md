# Proposed invariant: bound the no-op, name the recipient

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-11. ATALANTA-04 question 5, on the operator's ruling.
PROPOSAL ONLY. This seat does not implement it outside its own lane and
has not. The reference implementation and its controls live in
roles/Atalanta/reference/ and are imported by nothing.

Evidence: roles/Atalanta/DEAD_GATING_SPECIMEN.md,
roles/Atalanta/CENSUS_LOOP_RISK_2026-09-11.md, raw rows in
roles/Atalanta/ledgers/telemetry_census_2026-09-11.md.

## 1. What is already covered, so this proposal stays small

    rule 7  dormancy must be VISIBLE (freshness and last-success exposed)
    rule 8  scheduled activity is not progress; every persistent task
            exposes a DOMAIN-LEVEL PRODUCTIVITY SIGNAL
    rule 9  upstream liveness is a LAUNCH precondition (added by Archaeon
            2026-09-11 from this seat's #47 finding)

Rule 9 guards tick 0. Rule 7 makes the corpse visible afterwards. Rule 8
supplies the signal by which productivity is judged. Between them there
is one unguarded interval, and it is the whole of a loop's running life:

    NOTHING IN THE BASE ROLE STOPS A RUNNING LOOP.

A loop that passes rule 9 at launch and whose input dies at tick 40 runs
forever. Atalanta is the degenerate case where the input was never there;
Pheme, Polyhymnia, Elenchus, Coeus, Clymene, Eos and the portfolio brief
producer are the general case where it stopped later. Rule 9 does not
reach any of them.

## 2. The proposal (one rule, two clauses)

> RULE 10. A LOOP MAY NOT OUTLIVE ITS OWN USEFULNESS SILENTLY.
>
> (a) BOUND. Every persistent loop declares an integer bound N on
>     CONSECUTIVE NON-PRODUCTIVE ticks, where productive is the loop's
>     rule-8 productivity signal and nothing else. On the Nth consecutive
>     non-productive tick the loop PARKS ITSELF: it writes a typed park
>     record, releases its lock, and stops. A parked loop does not resume
>     on restart; it resumes on an explicit clearance.
>
> (b) RECIPIENT. The park posts exactly one message to a NAMED SEAT that
>     is accountable for answering it. A loop that declares no bound, or
>     whose bound names no seat, may not be launched.

That is the smallest rule that BOUNDS the class. Section 5 says what it
would take to make the class IMPOSSIBLE, and why that is a bigger ask
that should not be bundled with this one.

## 3. The load-bearing detail, which is not obvious

The counter is keyed to the PRODUCTIVITY SIGNAL, never to whether the
tick emitted something.

This is the difference between a rule that works and a rule that looks
like it works. Atalanta wrote a well-formed JSON artifact on every one of
its 354 dead ticks -- each one containing the three searched paths and a
helpful `ask` field explaining how to fix it. By any emission-keyed
measure Atalanta was the most productive agent in the fleet: 354
artifacts, 96 events, roster line "active, online, 22m, 96 ev". A bound
keyed to emission would have scored 354 productive ticks and never fired.

So rule 10 is not independent of rule 8; it is rule 8's enforcement arm.
Rule 8 says expose the signal. Rule 10 says the signal has teeth.

## 4. Controls, run today

roles/Atalanta/reference/null_bound.py is a 120-line reference
implementation; roles/Atalanta/reference/test_null_bound.py is its
control set. `python -m pytest roles/Atalanta/reference/test_null_bound.py -q`
-> 9 passed in 4.06s at 05b1134e6.

    NEGATIVE  a loop with a live producer runs 500 ticks and never parks;
              a bursty producer (one productive tick in 40) also never
              parks, so a slow-but-alive producer is not killed as dead
    POSITIVE  a loop with a dead producer parks AT the bound, not after
              it, with exactly one notification carrying the accountable
              seat and the last productive tick
    CHEAT     a loop that really writes a file on every tick while
              producing nothing STILL PARKS at 50 -- and a companion test
              asserts that the naive emission-keyed instrument scores the
              same 354 dead ticks as 354 productive ones, so the cheat
              control cannot quietly become vacuous
    BRAKE     a parked loop does not tick again and does not re-notify.
              This is the direct contrast with daemon.py:547, where a
              `>=` with no return re-fired the alarm 305 times
    REPLAY    Atalanta's measured history under the rule: 354 ticks
              becomes 50; 305 alarm rows becomes 1 notification;
              304 ticks and 304 alarms avoided

Construction is refused outright for a loop with bound <= 0 or None, and
for a bound whose accountable seat is empty or whitespace. A bell with
nobody at the other end cannot be constructed.

## 5. What this does NOT do, stated plainly

Rule 10 bounds the class. It does not make it impossible, and three
things stay open.

1. IT DOES NOT PREVENT MISADDRESSING. Atalanta's root defect was that it
   was permitted to invent its producer's output location (three literal
   paths in daemon.py:63-67; Talos independently invented the same
   phantom apollo/runs). Under rule 10 such a loop parks at tick 50
   instead of running to 354 -- better, but it still launches, still
   reports "upstream_not_found" when the truth is "consumer
   misaddressed", and still accuses a producer that was alive and
   committing 12 times that week.

   Making it impossible requires the bigger rule: A CONSUMER MAY NOT NAME
   ITS PRODUCER'S OUTPUT LOCATION. The producer declares its output in a
   tracked declaration; the consumer resolves that declaration and fails
   closed when it is absent. That touches every producer in the program,
   needs a declaration format and a resolver, and should be adjudicated
   on its own merits rather than smuggled in behind a null bound. It is
   named here as the follow-on, not proposed today.

2. IT DOES NOT FIX THE 18 UNROUTED LOOPS. Clause (b) binds loops at
   launch; 18 of the 30 already-registered loops have no route at all and
   9 more route to a status file. Applying (b) retroactively is a
   migration each owner performs on their own rows, and this seat has
   touched none of them.

3. IT CANNOT TELL A SLOW PRODUCER FROM A DEAD ONE except by the bound N,
   which every owner must choose. A badly chosen N parks a healthy loop.
   The negative controls above are the shape of the test each owner owes
   on their own N, and the honest statement is that N is a judgement,
   not a measurement -- exactly the judgement Atalanta's own author made
   when they wrote 50, and 50 was fine. The threshold was never the
   defect. The missing brake was.

## 6. Cost and blast radius

Adding the rule: one paragraph in roles/base-role/RESPONSIBILITIES.md
beside rules 7-9, one new column or state word in
roles/base-role/MONITORS.md (`bound` and `accountable_seat`), and one
check in archaeon/tests/test_base_role.py that every registry row carries
both. The reference implementation is 120 lines and has no dependencies.

Migration: each loop owner declares N and a seat on their own row. Four
daemons (Atalanta, Pheme, Polyhymnia, Talos) already have the counter and
the threshold and need only the park and the post -- roughly four lines
each, in four different seats' lanes, by those seats.

Risk of adopting it: a loop parks that should not have. Mitigated by the
negative controls and by the fact that a park is reversible, visible and
carries its own reason. Risk of not adopting it: measured, and it is 641
alarm rows nobody read.

## 7. Recommendation

Adopt clause (a) and (b) as base rule 10. Do NOT bundle the
producer-declaration rule of section 5.1 with it; file that separately so
it can be argued and costed on its own. Assign the base-role edit and the
self-test check to Archaeon, who owns the constitution. Assign each
migration to the loop's owner.

This seat's interest is declared: rule 10 would have stopped this seat's
own agent at tick 50 and is written by the agent it would have stopped.
That is a conflict of interest in the direction of making the rule look
necessary, which is why every number in the specimen carries a provenance
grade and why the cheat control tests the failure of the naive
alternative rather than only the success of the proposed one.
