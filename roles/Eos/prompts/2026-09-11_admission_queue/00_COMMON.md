# Eos admission queue -- what this is and what it is not (2026-09-11)

Authority: operator ruling 2026-09-11, EOS-01 ACTIVE. Eos's job is to
prevent outside novelty from entering Prometheus without earning a reason
to exist. Every item terminates as ANCHOR, ACQUIRE, RESOURCE or REFUSED.

THE GATE CAN ONLY REFUSE. It does not assign ANCHOR or ACQUIRE, because
admission is a human act (base role s2). An item that survives every
check leaves the gate as PENDING_ADMISSION and is sent to the seat that
owns the object it names. That is what you are receiving.

WHAT IS BEING ASKED: one of two answers, in your own time and at your own
priority.

    ADMIT   the item bears on the named object and you want it typed
            ANCHOR. Say what you would do with it.
    REFUSE  it does not. Say why in one line. A refusal is a result and
            is the expected answer most of the time -- 51 of 59 items in
            this season were refused and the seat reports that as the
            normal case, not a failure.

WHAT IS NOT BEING ASKED: not that you read the paper, not that you act
this week, not that you agree the item is good. Nobody at Eos has read
these beyond title and abstract, and under the operator's ruling titles
and abstracts support TRIAGE ONLY -- no description of an artifact this
seat has not inspected appears anywhere in this queue.

HOW IT WAS SELECTED: a bounded arXiv probe (2 requests, both HTTP 200,
24 items, no filtering) typed through
agents/eos/src/intake.py. An item reaches you only if a claim naming
YOUR file and a token really in it survived every check.

THE KNOWN HOLE, stated up front so you weigh this correctly: the gate
verifies that a referent EXISTS, not that it is the RIGHT one. A
preregistered attack (Test 4) confirmed that a deliberately irrelevant
item paired with a real file and a real token passes. You are the check
that catches that. If an item below looks unrelated to the object it
names, say so -- that is the single most useful answer you can give, and
it goes straight into roles/Eos/CALIBRATION.md.

Full results, rows and refusal corpus:
roles/Eos/intake/FIRST_SEASON_2026-09-11.md
roles/Eos/intake/ledger_2026-09-11.json
roles/Eos/intake/REFUSALS_2026-09-11.md
