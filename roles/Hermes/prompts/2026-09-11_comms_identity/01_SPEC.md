# SPEC -- a client must prove its connection reached the intended environment

Hermes, 2026-09-11. All numbers measured on this pass; every one names the
command that produced it.

## 1. The invariant

    A Prometheus client MUST NOT execute a statement against a resolved
    target until the target has PROVED it is the expected environment.
    Proof is read from the live connection. Absence of proof is refusal.

Three properties make it fail-closed rather than advisory:

  a. the expectation is COMMITTED and keyed by ENVIRONMENT, never by host.
     db_host is configuration, and the whole defect is that two machines
     ship the same value for it.
  b. an environment with no registered expectation REFUSES. An expectation
     that does not exist is not an expectation that is satisfied.
  c. an identity that cannot be READ refuses. An instrument that cannot see
     says so; it does not assume.

## 2. The failure path, reconstructed

    invocation        python -m comms <cmd>  /  any evidence_wiki caller
      |
    comms.api.connect()  ->  evidence_wiki.ew.db.connect()
      |
    ew.db.load_config()  reads evidence_wiki/config.json  (GIT-TRACKED)
      |                  db_host "localhost", db_name "prometheus_fire"
      |                  overrides: env EW_DB_HOST > config.local.json > this
      |                  (no config.local.json exists on M2: verified)
      |
    psycopg2.connect(host=..., dbname=..., user=..., password=...)
      |
    ACCEPTED unconditionally. No identity assertion anywhere on the path.

The committed default is correct on exactly one machine. On M1 "localhost"
IS the canonical store. Every other machine that has a local Postgres with
a database of that name gets its own.

## 3. What the resolver has, before and after connecting

BEFORE (all of it configuration, none of it identity):
    db_host, db_name, db_user, password, and whichever override won.
    Nothing here can distinguish two clusters that share a db_name.

AFTER (all of it free, one round trip, no privileges beyond connecting):
    pg_control_system().system_identifier   64-bit, assigned at initdb
    current_database()
    pg_is_in_recovery()                     standby vs primary
    pg_postmaster_start_time(), version()
    schema and table presence
    row contents

## 4. What each element can and cannot discriminate

Confusion classes the operator named, against the four elements, as
MEASURED in this fleet:

  class                          schema   db_name   db_system_id
  ---------------------------------------------------------------
  correct store (M1)             n/a      n/a       accepts
  stale copy / fork (M2, live)   NO       NO        YES
  unrelated db, similar tables   NO       NO        YES
  right schema, wrong machine    NO       NO        YES

The two NOs in the "stale copy" row are the point of this spec and both
are measurements, not arguments:

  * db_name cannot help: both stores are named prometheus_fire.
        select current_database()
        M1 -> prometheus_fire      M2 -> prometheus_fire

  * schema presence cannot help: `ew` exists in BOTH.
        select count(*) from information_schema.tables where table_schema='ew'
        M1 -> 41 tables            M2 -> 34 tables
    An Evidence Wiki call resolved to localhost on M2 finds ew.claims,
    finds ew.constraints, and succeeds. comms failed loudly on M2 only
    because the fork predates the comms schema; that was luck, not design.

  * db_system_id discriminates cleanly:
        select system_identifier::text from pg_control_system()
        M1 -> 7628127204585430828   M2 -> 7681719240261676752

## 5. The mechanism already exists; it records instead of refusing

evidence_wiki/ew/closure.py::service_attestation() already reads
system_identifier and already stamps it on rows, and its own docstring
calls it "non-spoofable proof of WHICH database persisted a row,
independent of the bearer token and the self-declared machine header".
That judgement is correct and this spec does not improve on it.

Observed on the M2 fork, in ew.constraints.attestation:
    {"db_host": "localhost", "db_name": "prometheus_fire",
     "db_system_id": "7681719240261676752", "service_name": ...}

The row knows it was written to the wrong store. Nothing compares the
value to an expectation, so nothing refuses. Two further properties stop
it doubling as a guard as written:

    * it caches per process (_ATTEST), which is right for a service pinned
      to one store and wrong for a guard answering for THIS connection;
    * its identity read is wrapped in `except Exception: pass`, so it can
      ship db_system_id=None. A field that may be null is not a gate.

So the marginal change is small: add the EXPECTED value, and the refusal.

## 6. Residual -- stated, not solved

A physical clone (pg_basebackup / streaming replica) inherits the
system_identifier. Promoted, it is writable and would pass. Catching it
needs a logical identity minted AFTER the split: a one-row table holding a
UUID, compared the same way.

That is deliberately NOT built, on evidence: M2's fork has a DIFFERENT
system_identifier from M1's, which proves it was made by dump/restore, not
by basebackup. No physical clone exists in this fleet, so the class is
currently unreachable and the cost is unjustified. The registry already
accepts an `expected_uuid` key and the guard already compares it when
present, so the upgrade is additive and needs no redesign. Build it when
the first basebackup clone exists.

A second residual, smaller: the guard proves WHICH store, not whether the
store is up to date. A canonical store restored from an old backup keeps
its system_identifier and passes. Freshness is a different instrument and
is not claimed here.

## 7. Controls (base role: positive, negative, cheat)

roles/Hermes/science/test_db_identity.py, 14 tests, green:

  POSITIVE  the real canonical store is accepted
  NEGATIVE  the real M2 fork -- the exact target five seats reached -- is
            rejected, and is ACCEPTED when a client names it deliberately
            (the guard is not a ban on local work)
  CHEAT     a database built for the test on the M2 cluster, given the real
            comms/schema.sql, with all four comms tables present and
            queryable, is rejected. The fixture is proved to be a cheat
            before the guard is run against it: comms's own predicate
            (select to_regclass('comms.messages')) returns non-null on it.
            Created and dropped by the fixture; cleanup verified.
  CLOSED    unknown environment refuses; unreadable identity refuses; an
            empty registry refuses everything.
