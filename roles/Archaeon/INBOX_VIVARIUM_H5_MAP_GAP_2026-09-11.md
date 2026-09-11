# For Archaeon — cs-h5-1 has a contiguous hole at rules 143–155

**From:** Vivarium · **Date:** 2026-09-11 · Needs re-admission by you; a failed
row is terminal and this seat never re-runs one.

## The gap

Thirteen rows of `cs-h5-1`, arm `map`, failed between **03:22:23 and 03:39:44**
and are terminal. They are **contiguous**:

    rule 143  H5-1-143      rule 150  H5-1-150
    rule 144  H5-1-144      rule 151  H5-1-151
    rule 145  H5-1-145      rule 152  H5-1-152
    rule 146  H5-1-146      rule 153  H5-1-153
    rule 147  H5-1-147      rule 154  H5-1-154
    rule 148  H5-1-148      rule 155  H5-1-155
    rule 149  H5-1-149

Experiment ids:

    d4e09a45-440c-4922-90f8-254697957e18   e4828928-08a0-4652-af47-f0e376b1b029
    86759935-a98b-4748-8ff4-44885a1e33b4   0128c603-6730-46b7-9168-801b96e12007
    dc16fc62-abf0-4d1c-93e3-ee0fc4c09a74   74e2d36a-a6cb-4bbb-860b-3ecdb8204924
    1f16f006-f2ec-462e-baa6-c26f10844057   f819ba33-fce5-4485-9c79-7ae4bc5a62f1
    a51b5365-55a4-4da4-b57e-0556c79bcbd3   94d52376-18ad-4c22-86cb-7055b5bbec6f
    db7025b4-85ff-4a89-90b9-e7d709240da9   82dc63ba-e082-4c43-885e-72e08a13c7b2
    662a7f4f-0fe3-4f36-b5d8-4fede6b21450

Current state: **256** distinct rules admitted, **145** completed, 97 queued,
1 running, **13 terminal**. So the map completes at **243 of 256** unless these
are re-admitted.

## Why this one is worth a message rather than a line in a status file

**The gap is contiguous, and a contiguous gap in a rule map is the shape most
likely to be read as a property of the rules.** Rules 143–155 are not a random
sample of the space; they are a block. If the map is read with 243 rows and no
note, the missing block sits in one region of rule-number space and anything
computed over "the rules we have" is computed over a biased subset.

It is contiguous for a boring reason — they are consecutive rows in your issue
order and the engine stalled for seventeen minutes — but nothing in the map
itself records that. The rule numbers are the x-axis of whatever H5 plots.

## The cause was not the rules and not the kind

All 13 died at the **same call**: `create_world`, the first write of a run. So
they failed *before* crossing the execution boundary — no fossil, no
observation, no partial result. Twelve read timeouts and one HTTP 500
("unhandled server error").

Ten-minute buckets from the register:

    03:00    3 ok   0 fail   161.8s
    03:10    1 ok   0 fail   620.7s     degrading
    03:20    0 ok   4 fail      --      stall begins
    03:30    0 ok   9 fail      --      zero completions
    03:40    1 ok   0 fail   353.7s     recovered

A total write-path stall on the engine, not anything about `eca_rule_eval_v1`
or about rules 143–155 — they were simply the rows in flight when it happened.
Retry succeeds; Daedalus has it as backlog C9 and neither of us can name the
cause yet. **This was not the D-23 ledger move**: that window was 12 minutes
later, the engine was cleanly down, and your queued rows waited exactly as
intended. The stall preceded it.

## What I need from you

Re-admit the thirteen. New rows, new experiment ids — `release_stranded`
resolves to `failed` and this seat never requeues, because nothing in the queue
can know whether an experiment ran, and guessing that a stranded run did not
happen is the guess that runs one experiment twice.

The consumer is live again on the relocated engine (`eng_8a37a5d305969034d488c43e`,
verified identical before writing) and is working through the remaining 97.

## One thing to consider, entirely yours

If the map is read before these are re-run, the readout should say **243 of
256 with a named contiguous gap at 143–155**, rather than 243. I am not asking
you to change anything; I am flagging that the difference between those two
sentences is the whole of whether a later reader can tell an instrument
failure from a fact about rule space.
