# A6 — attesting what the ledger cannot record

**Daedalus, 2026-09-11. DESIGN ONLY — nothing implemented.**
Acceptance test committed first: `tests/test_sfe_a6_attestation.py`
(4 passing as live evidence of the gap, 15 `xfail(strict=True)` as the criteria).

## The failure this closes

On 2026-09-11 a seventeen-minute stall cost 13 rows of `cs-h5-1` arm `map`,
rules **143–155**. Two systems each saw part of it and **neither could attest
what happened**:

- the **engine** could not record its own lock failure, because recording needs
  the lock that just failed; and
- the **register** recorded 13 failed rows with **no failure class**, because
  the failure landed inside a thirteen-line window where the class had not been
  decided yet.

The truth was recovered only by a human joining two records by hand — and the
first attempt was wrong, reporting all 13 as `create_world` because a
frame-matching pattern also matched Python's own `http/client.py`.

**Three shapes, verified against the live ledger:**

| rules | died at | effect in the ledger |
|---|---|---|
| 147–154 (8) | `create_world` | **no** |
| 146 (1) | the commit call **timed out** | **yes — it landed** |
| 143–145, 155 (4) | `audit_envelope`, post-commit | **yes** |

## Rule 146 is the canonical write-timeout case

The client timed out **on the commit itself**, and the commit had landed.

> **A timeout means the outcome is UNKNOWN. Reconcile before retry. Never
> assume the write failed.**

Any mechanism that reports "failed" because the caller saw an error is wrong in
precisely the case it exists for. `UNKNOWN` is a permitted verdict; `failed`
without evidence is not. This is now the reference case for backlog **A2**
(timed-out writes are not safely retryable) as well.

## The constraint

The mechanism **must not require the lock that failed.** Every durable record
the engine keeps today is an `events.append` inside `store.write()` — so any
"record the incident in the ledger" is circular. A test asserts this
(`test_the_engine_has_no_channel_that_survives_a_failed_lock`) and will fail
if a non-ledger sink ever appears, which would mean A6 had a home already.

## The mechanism: durable pre-attempt intent, reconciled afterwards

An **append-only intent journal**, outside SQLite, written at three points:

```
intent(request_id, ts, route, client, idem_key)      BEFORE the lock is touched
effected(request_id, kind, ref)                      after the effect
refused(request_id, reason)                          on a refusal
```

A **reconciler** joins journal → ledger, per `request_id`, and yields exactly
one of four verdicts:

| verdict | means |
|---|---|
| `CONFIRMED_EFFECT` | intent + effect, agreed by journal and ledger |
| `CONFIRMED_NO_EFFECT` | intent + refusal, and the ledger confirms nothing landed |
| `UNKNOWN_RECONCILABLE` | intent, no outcome — **the ledger can still settle it** |
| `UNKNOWN_UNRECONCILABLE` | intent, no outcome, and the ledger cannot settle it |

**Why intent rather than an incident log.** An incident channel records
refusals, which covers the 8 — but it is silent for rule 146, where nothing
was refused and the caller still could not tell what happened. Intent covers
all 13 because it is written *before* the outcome is known, so the record
exists whatever the outcome turns out to be. An incident channel is a strict
subset and I am not proposing one separately.

## Explicit failure modes

1. **The journal cannot be written.** *Fail open.* The request proceeds; the
   journal sets `degraded` and says so. A mechanism that can take the engine
   down in exchange for evidence has made availability worse.
2. **Process dies between `intent` and the effect.** → `UNKNOWN_RECONCILABLE`;
   the ledger settles it. This is the 8.
3. **Process dies between the effect and `effected`.** → `UNKNOWN_RECONCILABLE`;
   the ledger settles it. **This is rule 146** and the reason the ledger, not
   the journal, is the tie-breaker.
4. **Journal and ledger on the same disk.** Correlated loss — a disk failure
   takes both. The path is configurable so they can be separated; today they
   would not be, and that is stated rather than mitigated.
5. **Unbounded growth.** Rotation by size, and rotation must never drop a
   record whose `request_id` has no outcome yet.
6. **Concurrent appends.** One line per record, `O_APPEND`, flushed per write.
   No interleaving guarantees beyond line atomicity are assumed.
7. **The request never reaches the engine.** Invisible here, by construction.
   The client's register is the only witness, which is exactly why this does
   **not** replace the register's failure classes — it corroborates them.
8. **Clock skew.** Join on `request_id`, never on timestamps.
9. **Misreading it as provenance.** The journal is **not sealed** and is **not
   in the hash chain**. It is operational evidence about requests, never a
   scientific record about results. Nothing may derive a finding from it.

## Scope boundary — what this is NOT

- Not a second ledger, not a second source of truth, not sealed.
- Not a retry mechanism. It makes retry *decidable*; it does not retry.
- Not a health endpoint (**B3**) and not a load test (**C9**) — both remain
  separate items.
- Not a fix for the stall itself. The cause of the stall is **still not
  established**, and A6 deliberately does not depend on knowing it.

## What must be true before implementation

The acceptance test exists and is strict. Before writing `sfe/attestation.py`:

1. All 13 rows must map to a case in it (they do).
2. The four verdicts must be sufficient for all 13 (they are: 8 →
   `CONFIRMED_NO_EFFECT`, 5 → `CONFIRMED_EFFECT`, with
   `UNKNOWN_RECONCILABLE` the transient state each passes through).
3. It must add **no** route, **no** schema change, and **no** dependency.

Implementation would move `engine_source_hash`, so it needs its own deploy
authority. **C7 is held pending this**, per the operator, so the two would
batch into one build rather than two.
