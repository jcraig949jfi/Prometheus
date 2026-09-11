# SFE engine backlog — H0-H5 and beyond

**Daedalus, 2026-09-10.** Schema 8 is live on M1
(`sha256:5380cb90…`, `eng_8a37a5d305969034d488c43e`).

Every item says what EXISTS today, what it would take, and who it blocks. An
item with no citation is a wish, not a backlog entry, so each carries one.
Ordered by rank within each band, not by discovery.

**Legend.** `NOTHING` — no code at all. `PARTIAL` — a mechanism exists and does
not reach this case. `EXISTS` — works, listed because something around it is
missing.

---

## Band A — costs the project is already paying

### A6. **TOP OF THE BACKLOG.** The engine cannot record its own unavailability, so a stall reads as data — `DESIGNED, not implemented`
**Found by Vivarium 2026-09-11, and it is the sharpest consequence of C9.**

When `BEGIN IMMEDIATE` exceeds its 30 s wait, `sqlite3.OperationalError`
propagates past the `FoundryError` handler (`sfe/api.py:514`, which only catches
`FoundryError`) as an unhandled 500. The only `except sqlite3.OperationalError`
in `sfe/` is `store.py:631` — the unrelated `initialize()` fast path.

**Nothing is written to the ledger. By construction it cannot be: recording the
failure needs the very lock that just failed.** So the hash chain is silent
exactly when the engine is the thing that broke, and a reader reconstructing
events from the ledger afterwards sees no trace at all.

**Why that is worse than losing rows.** The 13 rows the engine failed on
2026-09-11 were `cs-h5-1` arm `map`, rules **143–155 — thirteen CONSECUTIVE**.
Contiguous because they were consecutive in the producer's issue order and the
engine stalled for seventeen minutes; nothing about the rules. But the rule
number is the x-axis of what H5 plots, so a block-shaped hole is the shape most
likely to be read as a property of rule space. The map completes at 243 of 256,
and the difference between reporting *"243"* and *"243 with a named contiguous
gap at 143–155"* is the whole of whether a later reader can tell an instrument
failure from a finding.

**Do:** the record has to live somewhere the lock cannot block — that is the
design constraint, not an implementation detail. Options: a structured
unavailability log outside SQLite; a counter surfaced on `/v2/health` (**B3**)
so a consumer can ask "were you refusing writes during my window?"; or a
deliberate second connection reserved for incident records. Anything that writes
to the same ledger through the same lock is circular.
Blocks: nobody today, and it silently taxes every campaign that hits a stall.

**PROMOTED to the top by the operator, 2026-09-11.** Design and acceptance test
committed ahead of any implementation:

* `roles/Daedalus/DESIGN_A6_ATTESTATION_2026-09-11.md` — durable pre-attempt
  intent, reconciled against the ledger afterwards, with nine explicit failure
  modes and a stated scope boundary.
* `SerendipityFoundry/SerendipityFoundryEngine/tests/test_sfe_a6_attestation.py`
  — **4 passing** as live evidence the gap is real, **15 `xfail(strict=True)`**
  as the acceptance criteria, one per row of the incident.

**Why intent and not an incident log.** An incident channel records refusals,
which covers the 8 that died at `create_world` — and is silent for rule 146,
where nothing was refused and the caller still could not tell what happened.
Intent is written *before* the outcome is known, so the record exists whatever
the outcome turns out to be. It covers all 13; an incident channel is a strict
subset of it.

**The residual limit, stated rather than mitigated:** a request that never
reaches the engine is invisible to an engine-side journal. The producer's
register is the only witness there, which is why this corroborates the
register's failure classes and does not replace them.


### A0. The engine does not describe its own responses, so half the surface is unguardable — `NOTHING`
**Measured on the live spec: 0 of 67 GET/POST route-methods declare a 200
response schema.** Every one is `{}`, because `sfe/api.py` contains **zero**
`response_model` declarations — so FastAPI emits a request-shaped OpenAPI and
nothing about what comes back.

Harmonia's conformance contract records exactly six per-route facts — `method`,
`path`, `path_params`, `required_body`, `required_query`,
`requires_session_key` — all request-side. That is not an omission on her part:
it is everything the spec gives her.

**The consequence is the one the gate exists to prevent.** A change that
REMOVED or RENAMED a response field reads **CONFORMANT**, because nothing in
the loop looks at responses; state 3 does not rescue it either, since
INCOMPLETE is computed from the route set and a response change moves no route.
The consumer then breaks at runtime against a green gate. Vivarium already
reads `indexed_artifacts` (C7) — that is exactly the class of field at risk.

**This is a TWO-PART dependency and neither half can start alone.** A0 (the
engine declares response models) must land before HARM-35 (the contract records
them and the gate checks them) is even possible — she cannot derive response
shapes from a spec that has none. The other half is **HARM-35** in
`roles/Harmonia/BACKLOG_H0H5.md`, cross-linked at **`42ca5030e`**; it had
previously recorded its blocker as "none", which implied she could begin.

Both entries now carry the other's SHA, so neither can drift back into looking
like one seat's item — and both name *two* commits rather than one, because a
pointer to where an item was FILED lands before the cross-link that makes it
findable. A0 filed `b24246097`, cross-linked `d618c0d22`.

Numbers measured independently on both sides and agreeing exactly: 67 GET/POST
route-methods, response codes `{'200': 67, '422': 66}`, **0 of 67** 200s
carrying a schema.

That `422: 66` is worth keeping beside the 0, because it is the number my first
count returned — I had asked "does a response schema appear anywhere in this
operation", which is a reasonable question and not the one the conclusion
needed. **Print the denominator next to the numerator** and a wrong denominator
cannot pass for agreement; I caught that one only because it happened to
contradict my argument, which is luck rather than method.

**Do:** declare response shapes the spec can carry. Cheapest honest version is
`response_model` on the routes whose responses other seats actually parse,
rather than all 67 at once. **Sequence: after step 5.** Building it before any
consumer holds the gate would be sharpening an instrument nobody is holding —
which is the whole lesson of this backlog's top item.


### A1. The client abandons a request ~3 s BEFORE the engine gives up — `PARTIAL`
Measured, `SerendipityFoundry/SerendipityFoundryEngine/deploy/WRITE_PATH_PROFILE_2026-09-10.json`: the client's socket
timeout fires at **30.01 s**; the engine's SQLite lock wait actually runs to
**33.11 s**, because SQLite's busy handler accumulates *sleep* time and
overshoots its configured 30 000 ms. Both are "30 s" in configuration and they
are not the same deadline. There is therefore a **3.1 s window in which the
caller has already reported failure while the engine may still commit** — which
is exactly the signature of the two rows that died on "The read operation timed
out" *after* their experiment was committed.
**Do:** make the client's timeout strictly exceed the engine's worst-case lock
wait, and derive one from the other rather than setting both to the same
number. Blocks: nobody, silently corrupts everybody's error accounting.

### A2. A timed-out write is not safely retryable — `PARTIAL`
`sfclient` sends `Idempotency-Key` on some routes, and `create_world` (and
several others) take no `idem_key` at all. A caller that times out on a
non-idempotent route cannot retry without risking a duplicate, and cannot
*not* retry without losing the work.
**Do:** audit every mutating route for an idempotency key; make the ones that
lack one accept it. Pairs with A1 — A1 makes the timeout happen, A2 makes it
unrecoverable.

**THE CANONICAL CASE IS RULE 146** (2026-09-11): the client timed out **on the
commit call itself**, and the commit **had landed**. The rule that follows, and
that any retry logic anywhere must obey:

> A timeout means the outcome is **UNKNOWN**. Reconcile before retry. Never
> assume the write failed.

Vivarium's policy of never requeueing a stranded row is the correct reading of
this, and it is stricter than anything the engine currently enforces.

### A3. Producer and engine cannot actually be reconciled yet — `PARTIAL`
`SerendipityFoundry/SerendipityFoundryEngine/deploy/COST_RECONCILIATION_2026-09-10.json`, run on the live ledger: producer
entries carrying `refs.artifact_digest` = **0 of 8**; engine entries = **2 of
68**, and both of those are my own probe. The control proves the join works, so
the empty answer is a real gap and not a broken join. Two distinct causes:
`to_engine_entries` does not set the digest (Archaeon's), and the producer's
declared references are **experiment UUIDs, not content digests** — so even
once populated the two sides would be joining on different *kinds* of identity.
**Do:** agree which identity the join uses. Blocks: C4 reconciliation, and any
claim that per-artifact spend is visible.

### A4. Concurrent-writer errors are unexplained — `PARTIAL`
The profile shows `OperationalError`s at 2, 4 and 8 concurrent writers while
throughput still scales (1272 → 4897 writes/s). The harness shares one
`Foundry` across threads, which is **not** how the service runs, so this may be
an artefact of the harness rather than of the engine. It is listed because it
is unexplained, not because it is known to be a defect.
**Do:** re-run with one `Foundry` per thread and with real HTTP concurrency
before drawing any conclusion.
**2026-09-11, UNCHANGED AND VINDICATED.** Chasing a production stall I proposed
that the service shares one `Foundry` across the threadpool — which would have
made this entry's caveat wrong — and then refuted it: `sfe/api.py:491`
`get_foundry()` yields a new `Foundry` per request. Re-running the harness with
a shared `Foundry` reproduces 99 failures in 120 writes
(`cannot start a transaction within a transaction`), confirming the harness
artefact this entry described and NOT a service defect. The original framing
stands; the temptation was to rewrite it the moment a production symptom
appeared that it would have explained.

### A5. Rollback stops being an option tonight — `EXISTS`, by design
`SerendipityFoundry/SerendipityFoundryEngine/deploy/DEPLOY_SCHEMA8_2026-09-10.md` §4: rollback is code **and** data, and
costs every schema-8 cost event written since the deploy. Vivarium's point is
sharper than mine was — now that campaign rows are landing, that cost is
**rising by the minute** rather than fixed.
**Do:** decide, deliberately, the date after which rollback is off the table,
and say so rather than discovering it.

---

## Band B — the seeds the operator named

### B1. Engine-side cost events for producer stages (C4-3) — `PARTIAL`
`record_cost_event` exists and accepts every stage in `COST_STAGES`, including
`generation`, `transfer` and `retention`. What does *not* exist is any producer
writing them: Archaeon's costs live only in committed JSON receipts.
**Do:** nothing in the engine. This is a client-adoption item and should be
tracked as Archaeon's, not mine — recorded here so it is not lost.

### B2. Per-artifact ceilings and their READ policy — `PARTIAL`
v8 added `DEFAULT_MAX_ARTIFACT_BYTES` (16 MiB) enforced on write **and read**
(`sfe/runtime.py`, `get_artifact_content`). The deploy had to pass
`--max-artifact-bytes 33554432` because one stored artifact is 32 MiB and would
otherwise have become unreadable. That is a workaround, not a policy.
**Do:** decide what a ceiling means for data that predates it. Options: grandfather
by recording a per-artifact ceiling at creation; refuse only new writes and
always serve what was stored; or a documented migration that re-homes oversize
artifacts. Today the answer is "raise the flag and hope".

### B3. A status/health endpoint — `NOTHING`
`/v2/version` reports identity, not health. There is no endpoint that says
whether the engine is *serving well*: no queue depth, no lock-wait, no last
error. The runbook's own liveness section says reachability is answered by
`SerendipityFoundry/SerendipityFoundryEngine/deploy/sfengine.log` rather than by any API.
**Do:** `/v2/health` with queue depth, oldest open reservation, last-write age,
lock-wait p99. Blocks: every deploy gate that currently reads the SQLite file
directly, mine included.

### B4. Multi-world budget lineage — `PARTIAL`
`_budget_rows` already hits the local row **and** the lineage root, so a fork
cannot multiply an allowance. What is missing is any way to *see* that: no API
returns the lineage a budget is governed by, so a caller cannot tell which root
it is spending against.
**Do:** expose the governing root on `budget_status`. Small, and it makes an
existing guarantee checkable.

### B5. Runtime loader for H3 1.0 — `NOTHING` (engine side)
The loader is Vivarium's (`viv/preflight.py`) and now uses the engine's digest
gate. H3 1.0 needs it to resolve at *runtime* rather than at admission.
**Do:** identify what the engine must offer — probably a streaming or ranged
read, since today `get_artifact_content` returns the whole payload base64'd in
one response, which is also what makes the size ceiling load-bearing.

### B6. `encoding_search_v1` support — `NOTHING`
No such kind, executor or reference anywhere in `sfe/`.
**Do:** get the contract from Archaeon before estimating. Same shape as
`nk_landscape_v0`: engine owns semantics, Vivarium registers.

### B7. Temporal program interface — `NOTHING`
No temporal/program vocabulary in the engine at all.
**Do:** design packet first. Listed so it is ranked rather than assumed.

### B8. Replay harness: re-execute a sealed spec, compare a normalized projection — `NOTHING`
The design says "scientific replay compares a declared normalized result
projection". The engine has every input — `spec_hash`, sealed payloads,
`BIT_DETERMINISTIC` declarations — and nothing that re-runs one.
**Do:** take a sealed spec, execute it on a fresh engine, project both results
through a **declared** normalization, compare. The declaration is the hard part
and the reason it is worth building: it forces "what counts as the same
result?" to be written down instead of assumed. This is the single highest-value
item in Band B.

### B9. v8 reservation semantics under concurrent consumers — `PARTIAL`
`reserve_budget` is idempotent on `(world_id, idem_key)` and a settled
reservation is refused a second charge. Untested: two consumers reserving the
same resource concurrently, a reservation whose owner dies (there is no lease
or expiry on `budget_reservations` — an abandoned OPEN reservation holds its
allowance **forever**), and settle-vs-release racing.
**Do:** an expiry or reclaim path for OPEN reservations, and concurrency tests.
The forever-hold is the real defect here.

### B10. Schema-9 candidates, and what each would RETIRE — `NOTHING`
Nothing is scheduled. Candidates, each with what it would let us delete:
retire `consume_budget`'s direct-debit path in favour of reserve→settle only
(retires the two-mechanism ambiguity Vivarium's `allowance_mechanism` field
exists to record); give `budget_reservations` a lease (retires B9's forever-hold);
promote `refs.artifact_digest` to a real column (retires the JSON scan in
`cost_report.by_artifact`).
**Do:** nothing yet. A schema version should retire something, and none of these
is urgent enough alone.

---

## Band C — found while doing the above

### C1. `by_artifact` scans JSON on every call — `EXISTS`, slow later
`cost_report` parses every cost event's sealed payload to build the index. At
68 events that is free; at 68 000 it is not.
**Do:** index it when it hurts, not before. Cited so the decision is deliberate.

### C2. No engine-side proof that a ceiling change is safe — `NOTHING`
`SerendipityFoundry/SerendipityFoundryEngine/deploy/preflight_deploy.py` gained a gate that catches "an artifact readable
today becomes unreadable", but that lives in a deploy script, not the engine.
**Do:** refuse to *start* with a ceiling below the largest stored blob, or at
minimum log it loudly. The engine currently starts happily and fails per-read.

### C3. `source_commit` reports a tree that cannot reproduce the build — `EXISTS`
Live `/v2/version` says `afd3548db`, which is the shared checkout's HEAD on
another role's branch. `verify_deploy.py` correctly reports this as a `[note]`.
**Do:** either stop reporting `source_commit` or report it as
`source_commit_unverified`. A field that is usually wrong teaches readers to
ignore a field.

### C4. The conformance contract pins one exact hash — `EXISTS`, brittle
`roles/Harmonia/contracts/conformance_check.py` is fail-closed on exact
`engine_source_hash` equality, so every build change halts the automated seats
even when no route moved. It has been stale since the v7 deploy and is now two
schema versions behind.
**Do:** joint with Harmonia — see `roles/Harmonia/INBOX_DAEDALUS_CONFORMANCE_CONTRACT_2026-09-10.md`.

### C5. Archaeon has no engine read access — `NOTHING`
Decision B1, open since 09-08. Proposal in
`roles/Daedalus/PROPOSAL_ARCHAEON_READ_SCOPE_2026-09-10.md`; not issued.

### C6. No credential rotation — `NOTHING`
`POST /v2/clients` issues a token once and shows it once. There is no rotation,
no expiry, no revocation. A leaked token is permanent.
**Do:** revocation first (cheap, and the thing you need in an incident);
rotation second. Blocks: C5 — a read grant is easier to give when it can be
taken back.

### C7. A 200 does not tell a caller whether its join key landed — **LANDED ba0769ac7**
**The sharpest ergonomic defect found today, and it cost a day.** `refs` is
accepted at BOTH the cost-event level and the resource-entry level, and only the
entry-level one carries `artifact_digest` into `by_artifact`. Put it on the
event and the engine does exactly what it promises — seals it, echoes it, never
branches on it — and returns **200**. Nothing is indexed, nothing is refused,
and the response looks identical to success. Vivarium spent a day on it and
reported two engine defects that were one misplacement.

The information *is* in the response: entry-level `refs` comes back `{}`. But
"success" and "your join key silently went nowhere" are distinguished only by
an echo nobody thinks to compare.

**Do:** return `indexed_artifacts` on the cost-event response — the digests the
engine actually indexed, derived, not branched on. It converts an invisible
failure into a visible one without weakening the opacity promise, since it
reports what the engine DID with the input rather than interpreting it.
**DONE** in `ba0769ac7`; candidate build `sha256:62090a6d…`, **not deployed**
(production is still `5380cb90`, and the schema-8 authority was for that build).

**Adjudication status: NOT ADJUDICATED, and it cannot be yet.** I told Harmonia
her harness would confirm in one run whether this change is additive. It will
not, for two reasons she gave and I verified: production has not moved, so
nothing in the loop serves `62090a6d`; and more durably, **the gate is
structurally blind to responses** — see A0. Route-level additivity I expect and
can have checked the moment it is live. Response-level additivity is outside
what the contract describes, and a passing six-state run would have been a
green result standing in for a claim it does not address.

### C7b. `viv/resources.py:as_dict()` would 422 if it ever reached the wire — `PARTIAL`
It emits `{quantity, unit, method, enforcement_class, scope, additive}`: no
`resource` name, and two keys the engine's five-name allowlist refuses. **It is
not on the settle path today** — Vivarium confirmed it feeds the queue row and
the PEW fossil, and the settle path composes its entry inline. I had named it as
the likely cause of the empty index and was wrong about the object. Recorded
anyway because the reasoning holds: wire it to the wire and it 422s.
**Do:** Vivarium's, and only if they ever connect it.

### C8. The engine ships two executors and no kind registry — `EXISTS`
`kind` is a free-form string column on `work_items`; `result_schema` exists only
in Vivarium. `nk_landscape_v0` is now the third engine executor and the second
one Vivarium must register by hand.
**Do:** decide whether the engine should own a kind registry at all. It is a
real architectural fork and it is getting more expensive with each kind.

### C9. No test covers the engine under a real concurrent HTTP load — `NOTHING`
**PROMOTED 2026-09-11: this one has now cost production, not just time.** Under
light concurrent write load the live engine returned `GET /v2/version` in 9.68s,
then a 45s timeout, then 34.76s, and `POST /v2/clients` failed three times
(timeout / HTTP 500 / timeout). The 500 was
`sqlite3.OperationalError: database is locked` on `BEGIN IMMEDIATE` — the
engine's own 30s lock wait expiring. At rest, minutes later, the same endpoint
served in 0.00-0.22s with idle CPU and no leak; disk 153 MB/s, a direct sqlite
read 0.04s, and the write lock acquired externally in 0.00s.

**Cause NOT established**, and recorded that way on purpose. I formed a specific
hypothesis — one sqlite connection shared across the threadpool — and refuted it
at `sfe/api.py:491`, where `get_foundry()` builds a NEW Foundry per request.

The reason it is C9's evidence rather than anyone else's is that **nothing in
`deploy/WRITE_PATH_PROFILE_2026-09-10.json` could have caught it**: every
measurement there was in-process, on a temp disk, and found sub-millisecond
writes. None of it went through the HTTP service, which is exactly the gap C9
names. 416 tests, still all single-process.
**Do:** a load fixture that drives the real HTTP surface with N concurrent
clients, asserting latency and error class — and run it before the next deploy.

**Fixture spec, sharpened by Vivarium 2026-09-11 and worth following exactly:**
the concurrency that matters is *not* N clients hammering one route. It is N
clients whose writes **interleave across a transaction boundary**, with
**different transaction rhythms**. Their consumer does ~18 writes per row and
never stalled on its own load however long it ran — every stall coincided with a
*second writer*. N identical clients would reproduce throughput and miss the
bimodality entirely, and bimodality is the tell: `create_session` measured
23.46 s once and 0.28 s minutes later, with every other call 0.03–0.32 s in both
passes. A fixture that produces a smooth latency curve has not reproduced this.

### C10. `NKScanDidNotConverge` has no caller — `EXISTS`
Added because a mutant *hung* instead of failing. Nothing in the engine runs the
scan; it exists for tests and for whoever runs the kill precondition.
**Do:** nothing. Noted so it is not mistaken for dead code and deleted.

---

## Band D — smaller, and worth doing when nearby

| # | item | state | note |
|---|---|---|---|
| D1 | Expose the governing budget root on `budget_status` | `PARTIAL` | see B4 |
| D2 | `OPEN` reservation lease/expiry | `NOTHING` | see B9; the forever-hold |
| D3 | `/v2/health` queue depth | `NOTHING` | see B3 |
| D4 | Refuse startup when the ceiling is below the largest blob | `NOTHING` | see C2 |
| D5 | Idempotency key on `create_world` and peers | `PARTIAL` | see A2 |
| D6 | Derive client timeout from engine lock wait | `PARTIAL` | see A1 |
| D7 | `source_commit` → `source_commit_unverified` | `EXISTS` | see C3 |
| D8 | Token revocation endpoint | `NOTHING` | see C6 |
| D9 | Per-entry `refs` size cap is 4 KiB and unconfigurable | `EXISTS` | fine today; a constant, not a policy |
| D10 | `cost_report` has no time or stage filter | `EXISTS` | returns everything, always |
| D11 | No way to list a world's cost events without the report | `EXISTS` | `get_cost_event` needs an id you must already have |
| D12 | Migration rehearsal is manual | `PARTIAL` | I rehearse against a `VACUUM INTO` copy by hand each time |
| D13 | `SerendipityFoundry/SerendipityFoundryEngine/deploy/preflight_deploy.py` hardcodes M1 paths | `EXISTS` | fine for one host; wrong the day there are two |
| D14 | No structured engine log | `EXISTS` | `sfengine.log` is uvicorn text; the deploy gate reads SQLite instead |

---

## What I would do next, in order

1. **A6** — top of the list by the operator's instruction, and it is the only
   item here where *two* systems failed to record the same incident. Designed
   and acceptance-tested; implementation needs its own deploy authority.
2. **C7** — landed but held, deliberately, until A6 resolves or the operator
   batches the decision. Two builds' worth of change in one deploy beats two.
3. **A1** — one measured number, a small change, and it is currently
   miscounting every timeout the project sees.
4. **B9's forever-hold** — an abandoned OPEN reservation silently shrinks a
   world's budget with no way to notice or reclaim it.
5. **B8, the replay harness** — the highest-value thing in the list, because
   it forces a normalized projection to be *declared*.
6. **B3 / C2** — the engine cannot currently answer "are you healthy" or
   "will this ceiling hide data", and both of those are asked at deploy time.
