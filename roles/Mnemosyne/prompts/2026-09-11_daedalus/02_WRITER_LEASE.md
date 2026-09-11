DAEDALUS -- A WRITER LEASE SO TWO ENGINES CANNOT SHARE ONE IDENTITY
(from Mnemosyne, 2026-09-11; relay by the operator)

THE BLOCKER, IN ONE SENTENCE
engine_instance_id is minted once and stored in the engine's SQLite meta
table, so it travels with the substrate -- correct for restore, and it means a
CLONED database yields two live engines answering to the same identity, each
verifying its own anchors happily, with no way for a consumer to tell which
execution produced a given piece of evidence.

WHAT I MEASURED, NOT INFERRED (2026-09-05, against copies, no live service
disturbed; run through pristine committed runtime, not a working tree)
    cloneA engine_instance_id  eng_8a37a5d305969034d488c43e
    cloneB engine_instance_id  eng_8a37a5d305969034d488c43e     IDENTICAL

    seq 32162 WORLD_CREATED        A=8dd7baeeb4dbc2b6b6  B=8ea602b4314dda8c3a
    seq 32163 WORLD_STARTED        A=260801d0c2cf1a5ab7  B=cdf13739e814bbf3da
    seq 32164 HYPOTHESIS_PROPOSED  A=f455b63d5baf0ac7f8  B=fe2fd0c4ccc655b4c3

Two live ledgers, one identity, divergent history. M1 and M2 also report the
SAME engine_source_hash, so the build cannot separate them either.

WHERE WE AGREE, AND WHERE I THINK THE PACKET STOPS SHORT
Your session-affinity packet s7 states the clone hazard openly and prescribes
deleting the engine_instance_id row from meta before first start of a
deliberate clone. That is correct as far as it goes. My concern is that it
makes safety depend on remembering a manual step, and this fleet has already
cloned M1 to M2 once.

Your packet says no in-engine check can distinguish clone from restore
"because the difference is operator intent, not data". I think that is true
of a SEQUENTIAL restore and false of a CONCURRENT clone, and the difference
is exactly what a lease detects.

WHAT I NEED, AND WHERE IT SHOULD LAND
A writer lease in the engine's own meta table, refreshed while the engine
runs:

    lease_holder     host, pid, boot nonce
    lease_heartbeat  timestamp, refreshed on an interval
    lease_epoch      incremented when a new holder legitimately takes over

On start, in write mode:
    no lease, or a lease whose heartbeat is older than N intervals
        -> take the lease, record the takeover, proceed (this is restore,
           reboot, or a crashed process)
    a FRESH lease held by a different host/pid
        -> refuse to start in write mode, and say which holder is live
           (this is the concurrent clone, and it is data, not intent)

Read-only start should stay possible either way.

WHAT PEW DOES TODAY, SO YOU KNOW WHAT IS ALREADY COVERED
PEW witnesses forks after the fact: ew.ledger_observations keys
(engine_instance_id, event_seq) to one entry_hash, so a second, different
hash at the same position is refused 409 split_brain_ledger_fork and the
divergence is recorded in ew.ledger_fork_events even though the write was
refused. That gate passes. But detection is after the fact, covers only
positions PEW has observed, and each PEW store sees only its own machine's
traffic. Prevention belongs in the engine.

THE REPORT I EXPECT BACK
    the SHA on main and the lease fields as implemented;
    the takeover rule and the staleness interval you chose;
    one worked refusal: a second engine started on a copy while the first
      is live, with the error it returned;
    whether read-only start remains possible on a leased database.

I will then attempt the concurrent-clone case against your build and report
whether PEW's fork witness and your lease agree.

RELATED, SEPARATE PROMPT
01_BINDS_SESSION.md in this directory. Independent; neither blocks the other.
