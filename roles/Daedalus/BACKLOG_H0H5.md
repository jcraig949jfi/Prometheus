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

### A1. The client abandons a request ~3 s BEFORE the engine gives up — `PARTIAL`
Measured, `deploy/WRITE_PATH_PROFILE_2026-09-10.json`: the client's socket
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

### A3. Producer and engine cannot actually be reconciled yet — `PARTIAL`
`deploy/COST_RECONCILIATION_2026-09-10.json`, run on the live ledger: producer
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

### A5. Rollback stops being an option tonight — `EXISTS`, by design
`deploy/DEPLOY_SCHEMA8_2026-09-10.md` §4: rollback is code **and** data, and
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
`deploy/sfengine.log` rather than by any API.
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
`deploy/preflight_deploy.py` gained a gate that catches "an artifact readable
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

### C7. `viv/resources.py` cannot produce a postable entry — `PARTIAL`
`Resource.as_dict()` emits `{quantity, unit, method, enforcement_class, scope,
additive}`: no `resource` name, no `refs`, and two keys the engine's five-name
allowlist refuses. Anything composed from it would 422.
**Do:** Vivarium's, flagged in their inbox. Recorded because it is the most
likely explanation for their empty `by_artifact`.

### C8. The engine ships two executors and no kind registry — `EXISTS`
`kind` is a free-form string column on `work_items`; `result_schema` exists only
in Vivarium. `nk_landscape_v0` is now the third engine executor and the second
one Vivarium must register by hand.
**Do:** decide whether the engine should own a kind registry at all. It is a
real architectural fork and it is getting more expensive with each kind.

### C9. No test covers the engine under a real concurrent HTTP load — `NOTHING`
411 tests, all single-process. The two failure modes that have actually cost us
time — the write stall and the read timeout — are both concurrency-shaped.
**Do:** a load fixture that drives the real HTTP surface with N clients.

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
| D13 | `deploy/preflight_deploy.py` hardcodes M1 paths | `EXISTS` | fine for one host; wrong the day there are two |
| D14 | No structured engine log | `EXISTS` | `sfengine.log` is uvicorn text; the deploy gate reads SQLite instead |

---

## What I would do next, in order

1. **A1** — one measured number, a small change, and it is currently
   miscounting every timeout the project sees.
2. **B9's forever-hold** — an abandoned OPEN reservation silently shrinks a
   world's budget with no way to notice or reclaim it.
3. **B8, the replay harness** — the highest-value thing in the list, because
   it forces a normalized projection to be *declared*.
4. **B3 / C2** — the engine cannot currently answer "are you healthy" or
   "will this ceiling hide data", and both of those are asked at deploy time.
