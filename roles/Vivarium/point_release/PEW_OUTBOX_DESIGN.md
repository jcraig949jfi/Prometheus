# PEW outbox design -- durable, asynchronous, idempotent (point release, MUST SHIP)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-09-17 (Vivarium m2-fce3fe0b). Stage 1 design (operator s8; Amendment 1 s6.D, s6.H, s7.D). PostgreSQL only; no Redis.

## 0. Today, and the defect

loop stage 6 (FOSSILIZE) calls viv.pew.write_encounter synchronously: world
anchor POST then encounter POST. `pew.required` on the spec decides whether a
PEW failure fails the row; when not required the failure is an event row
(pew_write_failed) and nothing is ever re-delivered. So: a PEW outage during
a completed execution either fails good science (required) or silently
loses its fossil (not required). Both are wrong; the second is invisible.

## 1. Properties (operator s8), and how each is met

    execution never waits on PEW           stage 6 becomes: write outbox rows in the SAME transaction as the row's terminal update;
                                           return. A separate deliverer process drains. The consumer never opens a PEW connection
                                           in the tick path.
    delivery repeatable                    the deliverer is idempotent per event_id; it may run any number of times
    duplicate delivery != duplicate evidence
                                           event_id is content-derived and PEW's ingestion keys on it (Mnemosyne s7.D: duplicate ->
                                           no-op). Until PEW exposes an idempotent route, the deliverer uses the existing
                                           (encounter_id, run_id) uniqueness (PEW returns 409 on a repeat) and records 409 as DELIVERED
    gaps visible                           per (producer, stream) a dense sequence; PEW records the highest contiguous sequence seen;
                                           a missing sequence is a GAP on PEW's side and a not-DELIVERED row on mine; neither heals it
    failed delivery inspectable            attempts, last_error, last_http on the row; `viv.cli outbox` lists by state
    provenance never lost                  the outbox row is written before the attempt is COMPLETED (same transaction); a crash after
                                           commit leaves it PENDING; a crash before leaves the attempt OPEN and the row absent, which
                                           the NEW ATTEMPT rule handles

## 2. Table (viv.pew_outbox)

    event_id            text PK                         "sha256:" + sha256(producer || stream || source_attempt || source_step || event_kind || payload_digest)
                                                        -- content-derived, so the same fact re-enqueued by a replayed step has the SAME id
    producer            text NOT NULL                   "vivarium@<host>" (the worker id)
    stream              text NOT NULL                   "viv.fossil.v1" for WORLD_ANCHORED / ENCOUNTER_RECORDED (the routes PEW has
                                                        today) and "viv.execution.v1" for the provenance events (the ingest route
                                                        Mnemosyne adds); ordered independently, so a fossil never waits behind an
                                                        event PEW cannot ingest yet (implementation finding, 2026-09-17)
    sequence            bigint NOT NULL                 per (producer, stream), dense, assigned at insert (UNIQUE (producer, stream, sequence))
    event_kind          text NOT NULL                   CLOSED set v1: WORLD_ANCHORED | ENCOUNTER_RECORDED | ATTEMPT_OPENED | STEP_COMPLETED |
                                                        INTERVENTION_RECEIPTED | GATE_EVALUATED | ATTEMPT_TERMINATED | ATTEMPT_REPLAYED
                                                        (raw events only, Amendment s7.B; no projection names)
    source_attempt      uuid NOT NULL
    source_step         uuid NULL
    source_experiment   uuid NOT NULL
    payload             jsonb NOT NULL                  the body PEW receives (encounter body, receipt, envelope); identities verbatim
    payload_digest      text NOT NULL
    created_at          timestamptz NOT NULL DEFAULT now()
    state               text NOT NULL DEFAULT 'PENDING'  PENDING | DELIVERED | REJECTED | PARKED
    attempts            integer NOT NULL DEFAULT 0
    last_attempt_at     timestamptz NULL
    last_http           integer NULL
    last_error          text NULL
    delivered_at        timestamptz NULL
    pew_reference       text NULL                       what PEW returned (encounter reference), verbatim. The QUEUE ROW's
                                                        pew_reference stays NULL on this path: a terminal row is frozen by the
                                                        transition trigger and that invariant outranks the convenience column;
                                                        `viv.cli trace` reads the reference from here (implementation finding)

State rules: PENDING -> DELIVERED (2xx, or 409 duplicate); PENDING ->
REJECTED (4xx other than 409/429: the payload is wrong; never retried
automatically; visible; a NEW event with a corrected payload is a new
event_id); PENDING stays PENDING on 5xx / connection errors (retried with
backoff); PENDING -> PARKED after the deliverer's rule-10 bound.

## 3. The deliverer (viv.deliver; a second scheduler one-shot, like the dead-man)

    - every N minutes: select PENDING ordered by (producer, stream, sequence) FOR UPDATE SKIP LOCKED, limit batch
    - deliver in sequence order per stream; stop the stream at the first non-2xx/409 (ordering preserved; a gap is never
      created by delivering ahead)
    - rule 10: bound on consecutive ticks that delivered nothing while PENDING rows exist -> park, one comms report to
      Mnemosyne (accountable for PEW availability), state file every tick (registry row VivariumOutboxDeliverer)
    - no delivery from the consumer process; no delivery from a test run (namespace test is refused by the deliverer unless
      VIV_PEW_NAMESPACE=test is set for it explicitly, the existing conftest rule)

## 4. Growth bound (Stage 2 question: "can the outbox grow without bound?")

Yes, by design, up to the queue's own rate: one attempt produces ~4 + steps
events (~20 rows, ~10-50 KB). At C3's rate (10 slots, 6.1 h compute) that is
under 1 MB per campaign per day of outage. The bound is the disk; the
policy is: never drop, never compact, PARK and report when the backlog
exceeds a declared count (default 10,000 rows = weeks of outage), and let
the operator decide. A dropped event is a lost fossil; a parked deliverer is
a visible one.

## 5. Coordination with Mnemosyne (s7.C/D)

    my event_id derivation           sha256 over (producer, stream, source ids, kind, payload_digest) -- proposed to Mnemosyne #330
    my sequence                      dense per (producer, stream); PEW stores the last contiguous sequence per producer/stream
    UNKNOWN vs NULL                  in payloads: "UNKNOWN" (string) = the owner exists and I could not know; null = NOT_APPLICABLE
    idempotent route                 requested: POST /fossil/events accepting event_id, returning 200 on first and 200-with-
                                     duplicate:true on repeat; until then 409 on (encounter_id, run_id) is my duplicate signal

## 6. Migration of today's path

    stage 6 today: write_encounter(...) synchronous   -> stage 6 new: outbox.enqueue(WORLD_ANCHORED, ENCOUNTER_RECORDED, ATTEMPT_TERMINATED, ...)
    pew.required == true                              -> means "the row is not COMPLETED until DELIVERED"? NO: it means the outbox row is
                                                         REQUIRED (always true now). The flag becomes a no-op and is deprecated in the
                                                         spec contract with a note; old specs validate unchanged
    pew_reference column on the row                   -> filled by the deliverer when DELIVERED (was filled synchronously)
    tests/test_live_pew.py                            -> becomes tests of the deliverer against a fake PEW: outage, duplicate, gap, 4xx

## 7. Acceptance (Stage 4)

    positive   an attempt completes with PEW down; the row is COMPLETED; 4 outbox rows PENDING; deliverer parks after its bound
    positive   PEW returns; the deliverer drains in sequence; rows DELIVERED; pew_reference set on the row
    negative   the same events delivered twice (deliverer run twice, or PEW answered but the ack was lost) -> the second pass sees
               409/duplicate and marks DELIVERED without a second fossil (asserted against a fake PEW counting bodies)
    negative   a 422 payload -> REJECTED, never retried, listed by `viv.cli outbox --state REJECTED`
    cheat      a deliverer that delivers sequence 7 while 6 is PENDING is refused by the ordering rule (test forces 6 to 5xx)
    cheat      a consumer process that imports the PEW client in its tick path fails a static test (the tick path may not import
               viv.pew's HTTP client; only the deliverer may)
