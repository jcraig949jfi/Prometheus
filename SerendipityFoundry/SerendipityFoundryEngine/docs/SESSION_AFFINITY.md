# Session affinity (schema v5)

**An experiment must not wander between engines.**

M1 and M2 run byte-identical builds over separate databases. Before v5 a client
could register on one and send otherwise-valid requests to the other: best case
a confusing 404, worst case a write into the wrong engine. World ids and tokens
were always engine-local — nothing *said so on the wire*.

---

## The invariant

> A session key is minted by exactly one engine instance, and any request
> carrying it that reaches a different instance fails closed with
> `421 WRONG_SESSION` **before any resource is read or mutated**.

## Protocol

**Transport:** one header, everywhere — `X-SFE-Session`. Covers every
experiment-scoped route INCLUDING the collection routes `POST /v2/worlds`
and `GET /v2/worlds` (see the coverage note below). No endpoint takes it
differently. `sfclient` adopts the key at `create_session()` and sends it on
every later call; a caller never appends it per-callsite.

**Key format:** `sfes_<engine-instance-hex>_<random>`

The engine instance id is carried **in the key, in the clear, on purpose**. It
is what makes a wrong-engine request distinguishable from noise: the receiving
engine reads the claimed instance out of the key itself and answers
`WRONG_SESSION` *without any lookup*. If the binding lived only in the database,
a foreign key and a random string would produce the same event — an absent row —
and the engine could not tell "you are talking to the wrong machine" from "that
session never existed". That confusion is the entire defect.

The instance id is not a secret; `verify_anchor` and the audit envelope already
publish it. The entropy is the random tail. Only the SHA-256 of the whole key is
stored, and logs carry a `sfp_…` fingerprint, never the key.

**Binding:** `sessions.key_hash`, `sessions.engine_instance_id`,
`sessions.affinity_mode`, plus the existing `created_ts` and `state`.

`engine_instance_id` is minted once per **database** and stored in `meta`, so it
travels with the substrate rather than the host — restoring a backup elsewhere
keeps the identity of the ledger it contains. Nothing hardcodes M1 or M2;
M1…M50, ephemeral VMs and containers work unchanged.

## HTTP semantics

| Code | Status | Meaning | Client action |
|---|---|---|---|
| `WRONG_SESSION` | **421** Misdirected Request | Key minted by a different engine instance | Re-send to the owning engine |
| `SESSION_REQUIRED` | **428** Precondition Required | No key on a bound session (strict mode) | Send the key |
| `SESSION_MALFORMED` | **422** | Header present, not a session key | Fix the value |
| `SESSION_UNKNOWN` | **401** | Well-formed, names this engine, never issued here | Re-open a session |
| `SESSION_CLOSED` | **409** | Session exists here but is CLOSED | Open a new one |
| `SESSION_MISMATCH` | **403** | Valid session, but not this world's | Use the right session |

421 is chosen deliberately over 404 (which sends an operator hunting for missing
data when the truth is a wrong machine) and over 500 (nothing failed — the
engine answered correctly). The body names both the claimed and the serving
instance id, and nothing else about the infrastructure.

**A genuine missing resource inside a valid session is still `404 not_found`.**
That discrimination is tested.

## Enforcement modes

`serve.py --session-enforcement {advisory|strict}` (default **advisory**).

| | advisory | strict |
|---|---|---|
| key from another engine | **421** | **421** |
| malformed key | **422** | **422** |
| missing key, ANY session-scoped route | allowed, **counted** | **428** |

**"Strict" means every session-scoped route, including the collection routes
and the four `/v2/work` routes.** It briefly meant "strict on `{wid}`-scoped
routes only", which had two consequences Harmonia measured on 2026-09-05: an
unkeyed `POST /v2/worlds` returned **200 and created a world the caller could
never touch again** — an orphan at birth, in a system with no GC — and an
unkeyed worker could still claim and complete work. Both now refuse at the
point of the mistake.

**The cross-engine defect is closed in both modes.** What the mode phases is
only the *requirement to send* a key — because 106 pre-existing sessions and
every already-written client would otherwise break the hour this shipped.

## Migration

Pre-v5 sessions become `affinity_mode='LEGACY'` with **NULL** `key_hash` and
**NULL** `engine_instance_id`. That is deliberate: no key was ever issued for
them and no binding was ever recorded, so back-filling this engine's id would
manufacture a provenance claim that was never made — true on M1 today, false the
moment the database is restored elsewhere. NULL says *unknown*, which is what we
actually know.

Census on M1 at deploy: **117 sessions — 11 STRICT, 106 LEGACY, 346 worlds on
legacy sessions.**

### When STRICT becomes mandatory

A checkable condition, not an intention:

> Flip to `--session-enforcement strict` when
> `affinity_census()["sessions_legacy_open"] == 0`, **or** on **2026-10-01**,
> whichever comes first.

Until then every unkeyed request is logged as `SESSION_ABSENT_ALLOWED` with its
client, world and session mode, so the tail is measured rather than guessed. A
legacy session cannot be created — `open_session` only ever writes `STRICT` — so
the count is monotonically non-increasing.

## Restart, backup, restore

- **Restart** (same substrate): identity and every key survive. Verified.
- **Restore elsewhere**: identity follows the data, so keys issued before the
  backup still work. Verified.
- **Clone hazard, stated openly:** copying a database copies its engine
  identity, so two engines would both answer to the same instance id and
  affinity would stop distinguishing them. This is the *correct* behaviour for
  restore and the *wrong* behaviour for cloning, and no in-engine check can tell
  the two apart — the difference is operator intent. **If you clone a substrate
  to stand up a genuinely new engine, delete the `engine_instance_id` row from
  `meta` before first start**; it is re-minted lazily. M1 and M2 today hold
  independently minted ids (`eng_8a37a5d3…` / `eng_abc7e695…` for the test
  instance), verified distinct.

## Instrumentation

`sfe.affinity` logs one line per decision: code, engine instance, client id,
world, key fingerprint, and for rejections the claimed engine. Never the key.
`affinity_census()` gives session totals by mode plus worlds on legacy sessions
— the signals a future allocator needs.

---

## FUTURE — fleet allocator / front-door router

**Not built, deliberately.** A capacity-aware allocator will select an SFE
instance, create or route the session there, and maintain affinity afterwards
using the session identity.

The architectural boundary this release establishes:

> **The allocator chooses the engine once. Session affinity prevents the
> experiment from wandering afterwards.**

The session is already the durable answer to *"which SFE instance owns this
experiment?"* — readable from the key itself, without consulting any registry.

---

## Coverage note — two holes found after the first implementation

Both were found by widening a test, not by review, and both are recorded
because the *shape* of the mistake is the interesting part.

1. **`start` / `pause` / `resume` / `terminate`** are registered in a `for`
   loop rather than with decorators, so a decorator-matching wiring pass
   skipped them. `terminate` answered a foreign session with **404** — a
   missing-resource diagnosis for a wrong-machine problem, the exact confusion
   this feature removes.

2. **`POST /v2/worlds` and `GET /v2/worlds`** were outside the first
   route-coverage probe, which was scoped to `/v2/worlds/{wid}`. `POST` gave
   **403 access_denied** (a permissions diagnosis for a wrong-machine problem)
   and `GET` gave **200** — a foreign session key silently enumerating the
   engine. A silent 200 is precisely the defect class being closed.

The coverage test now enumerates the **live route table** and probes every
`/v2/worlds*` and `/v2/work/*` route, so a route added tomorrow is either
covered or the test fails. A hand-maintained list would have reproduced both
holes.

`POST /v2/worlds` additionally binds the presented key to the `session_id` in
the body: holding session A's key while creating a world under session B is
`403 SESSION_MISMATCH`, because that would break the affinity chain at its root
and every later call on that world would look consistent.

---

## Ending a session

`POST /v2/sessions/{sid}/close` — idempotent, **owner-gated (bearer token), not
key-gated**.

That choice is load-bearing. The 106 LEGACY sessions never had a key, so a
key-gated close would leave exactly the sessions that need draining
permanently undrainable.

Closing does **not** terminate or delete worlds and does not touch their
events. It ends the session: the key stops authenticating (`409
SESSION_CLOSED`) and no new world can be created under it.

It exists because Harmonia's pass found the same gap from two sides:
`SESSION_CLOSED` was in the taxonomy but **unreachable** — a documented
failure no client could trigger or test — and the strict-cutover drain
condition (`sessions_legacy_open == 0`) could never move, because nothing in
the system closed a session. The cutover was date-driven by accident rather
than by decision. Both are now addressable, though **nothing is auto-closed**:
draining is a deliberate operator act on sessions known to be finished.
