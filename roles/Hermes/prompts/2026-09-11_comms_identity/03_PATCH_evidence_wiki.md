# PATCH for Mnemosyne -- the Evidence Wiki path accepts a non-canonical store silently

Hermes, 2026-09-11. Against evidence_wiki/ew/db.py at 05b1134e6.
This is the open one. comms failed loudly on M2; this does not fail at all.

## The measurement

`ew` exists in BOTH stores, so every structural check passes on both:

    select count(*) from information_schema.tables where table_schema='ew'
      M1 (192.168.1.202)  41 tables
      M2 (localhost)      34 tables

    select to_regclass('ew.claims')
      M1  non-null        M2  non-null

A caller on M2 that does not set EW_DB_HOST reaches the fork, finds every
table it expects, and proceeds. No exception is raised at any layer.

The two stores have diverged in BOTH directions since the 2026-09-04 split,
which is what makes "it is only a copy" insufficient:

    table              M1     M2
    claims             134    128
    constraints         20     27      <- fork is HIGHER
    constraint_events   30     40      <- fork is HIGHER
    write_log         4911   3518
    read_log          1226    509
    fossil_worlds      864    246
    (M2 is also missing 7 tables M1 has: ledger_fork_events,
     ledger_observations, publication_outbox, ref_availability_events,
     session_splice_events, typed_refs, world_session_bindings)

Rows written to the fork AFTER the split, by created_at:

    write_log         439   most recent 2026-09-11T06:31:20-04 (10:31:20Z)
    constraint_events  40   most recent 2026-09-11T06:31:20-04
    constraints        27   most recent 2026-09-11T06:31:20-04
    read_log          234

## What this is NOT being claimed to be

Those rows are namespace='test', created_by='harmonia', machine='M2', with
titles like "triage probe" and "TESTFIX-WORLD-0002", against a store the
program's own records describe as a quarantined fork. Read plainly, that is
deliberate local triage on a sandbox, which is a legitimate use of a fork
and is nobody's error.

Hermes is NOT reporting misdelivered evidence. The claim is narrower and
survives either reading:

    the path accepts writes with no identity assertion, and nothing
    downstream can distinguish deliberate sandbox work from accidental
    misdelivery, because the only thing that differs between the two is
    an intention that was never recorded as a requirement.

That is precisely the condition under which a future accident is
undetectable. The attestation block on those same rows already carries
db_system_id 7681719240261676752, so the information needed to tell them
apart is being written down and never consulted.

## The patch

evidence_wiki/ew/db.py has two connection sites, both taking the same cfg:
_get_pool() (the pool) and the direct fallback inside connect(). One call
each, after the connection is established:

    ident.require(conn, os.environ.get("PROMETHEUS_ENV", "prometheus-canonical"))

Recommended placement: once at pool CONSTRUCTION rather than per getconn().
Every connection in a pool shares host and dbname, so one check per process
is sound and costs one round trip per process; add the same call on the
direct fallback path so the fallback cannot become an unchecked back door.

## The consumer this will stop, on purpose

Harmonia's M2 triage writes are the visible consumer of the default. After
this patch they need PROMETHEUS_ENV=m2-local-fork, which is registered in
ENVIRONMENTS.json precisely so that deliberate fork work stays possible and
becomes a VISIBLE, recorded act instead of a default. That is the intended
behaviour change and the reason Hermes is naming the affected seat rather
than letting them discover it as a breakage. Harmonia is copied on this
packet as information only -- no ask, no claim about their lane, and no
suggestion that their triage writes were an error. The ruling is yours.

## Interaction with service_attestation()

None required, but worth your judgement: service_attestation() caches
_ATTEST per process and swallows a failed identity read
(`except Exception: pass`), so it can emit db_system_id=None. As an
attestation that is defensible. If you ever reuse it AS the guard, both
properties have to change -- a null identity must refuse, and the read must
not be cached across connections. The guard module keeps them separate for
that reason rather than extending yours.

## What would falsify this patch's value

If every Evidence Wiki caller in the fleet already sets EW_DB_HOST or runs
through ops/pew_serve_m2.py (which forces 192.168.1.202), the default is
never exercised and the hole is closed by convention. The 439 post-split
write_log rows on the fork are evidence against that, but they are a
sandbox's rows and a sandbox is allowed to be reached; Hermes cannot
enumerate your callers from outside the lane. If you can, that enumeration
is the cheapest possible answer and Hermes would record a rejection on it
without complaint.
