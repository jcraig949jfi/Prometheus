# Gen-2 Migration & Consolidation

## Guiding constraint

The Gen-1 / D-13 Foundry is LIVE and in use (release `50b5c232` on
`192.168.1.202:8799`, with a real client, M2). Gen-2 was built to leave it
completely undisturbed:

- Gen-2 lives under the new top-level `gen2/` package, which is OUTSIDE the
  release allowlist (`foundry`, `tests`, `third_party`, `scripts`). Adding it
  does NOT change `source_tree_hash`; `release_match` stays True; M2's release
  pin keeps working.
- Gen-2 runs as a SEPARATE process, on a SEPARATE port, with its OWN SQLite
  database. It shares no state and no code path with the running service.
- The live service was never quiesced, restarted, or modified during this work.

## Component disposition (from the forensic baseline)

| Existing component | Verdict | Rationale |
|---|---|---|
| JSONL hash-chained EventLedger | KEEP (idea), BUILD_NEW (impl) | Durable + tamper-evident, but a single global chain that cannot join a cross-store transaction. Gen-2 re-expresses the same discipline as a SQLite table so events + state + work claim commit atomically, and partitions per world. |
| Content-addressed blob store | MIGRATE | Atomic publish + verify-on-read is the right pattern; Gen-2 reuses it (`store.put_blob`/`get_blob`). |
| Deterministic seed streams | KEEP | Reused conceptually by executors/reproducibility. |
| Versioned operator registry (D-13 `foundry.operators`) | KEEP | Good model for the Gen-2 measurement registry. |
| Executor contract (`EngineAdapter`) | KEEP (idea) | Informs the Gen-2 `Executor` contract (broader: not engine-specific). |
| Observer/semantic firewall | KEEP | Solves a DIFFERENT problem (measurement != selection); Gen-2 adds world-vs-world isolation on top. |
| Synchronous `/v0/search` request path | WRAP (future) | Could become a Gen-2 executor kind (`Executor` that calls the D-13 engine), so Gen-2 owns the lifecycle while the D-13 engines do the science. Not built this pass. |
| Auth scopes (experiment/observer/admin) | WRAP | Capability firewall, not ownership; Gen-2 adds client-ownership beside it. |
| Any backlog / status-generator / scheduler in `F:\SerendipityD` | N/A (none exists) | There is no separate orchestrator to consolidate here. |

Nothing was DELETED or DEPRECATED: the live release is frozen and preserved.

## Orchestration consolidation (section 27)

The section-27 goal -- one authoritative execution lifecycle, no status-generator
mistaken for an executor -- is satisfied WITHIN Gen-2: `work emitted -> QUEUED ->
CLAIMED -> RUNNING -> COMPLETED/FAILED -> evidence committed` is the only path,
and a `world_status` view is explicitly a VIEW derived from authoritative rows,
never a source of truth.

The broader `F:\Prometheus` orchestration machinery referenced by section 27 is
OUT OF SCOPE for this expedition under this project's firm directory rules and
was not inspected. If it exists, folding it onto the Gen-2 work queue (emit its
units as `work_items`, run them through claims/leases) is the recommended
follow-up, to be done where those directories are in scope. The mechanism is
ready: any producer can `enqueue_work` and any worker can `claim_work`.

## Adopting Gen-2 incrementally

1. Stand up the Gen-2 service on a spare port with its own DB (see the API doc).
2. Point new multi-world experiments at `/v2`; leave existing D-13 clients on
   `/v0`.
3. To run D-13 science THROUGH Gen-2 later, add an `Executor` whose `execute()`
   drives the D-13 engine/terrain and returns a structured result -- Gen-2 then
   owns scheduling, budgets, provenance, and isolation while D-13 owns the
   science. (Contract is defined; adapter not built this pass -- marked
   incomplete rather than stubbed.)
