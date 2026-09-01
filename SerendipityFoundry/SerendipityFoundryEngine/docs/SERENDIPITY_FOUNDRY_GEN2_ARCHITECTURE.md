# Gen-2 Architecture

The smallest system that satisfies the invariants. One SQLite database is the
authoritative substrate; everything else is a thin layer over it.

## Layers

```
  gen2/api.py          FastAPI /v2   (auth token -> client; ownership passed down)
        |
  gen2/runtime.py      Foundry facade: one write-transaction per mutating op,
        |              state change + event appended atomically
   +----+----+-------------------------------+
   |         |               |               |
 events.py  store.py     executors.py    canary.py
 (per-world (SQLite WAL   (executor       (a driver/agent that
  hash chain, + FK + CAS   contract +      USES the runtime; not
  verify)    blobs)        worker loop)    part of the runtime)
```

- `store.py` -- the schema and connection. WAL for concurrent readers, `BEGIN
  IMMEDIATE` write transactions so a read-then-write (claim a work item) is
  atomic against other writers. Foreign keys and `CHECK` enumerations make an
  illegal transition or dangling reference a database error. Blobs are
  content-addressed on disk, verified on read.
- `events.py` -- the per-world append-only hash chain. `append()` runs inside
  the caller's transaction, so evidence and state commit together or not at all
  (the cross-store atomicity the baseline found ABSENT). `verify_world()`
  recomputes the chain and rejects any edit.
- `runtime.py` -- `Foundry`, the only object that writes authoritative state.
  Every mutating method: open one write transaction, check ownership, mutate
  the relevant table, append the matching event, commit. Reads never write.
- `executors.py` -- the pluggable execution contract (`Executor.execute(
  WorkPackage) -> ExecutorResult`) and a `WorkerLoop` (claim -> heartbeat ->
  execute -> commit). Reference executors: a deterministic bitstring scorer and
  a deliberately nondeterministic one (for the replay-honesty test).
- `api.py` -- HTTP surface. A bearer token resolves to a client id; that id is
  passed into every runtime call, so isolation is enforced by the runtime, not
  by the API.

## Object model

```
CLIENT --< SESSION --< WORLD --< { events (hash chain), work_items,
                                   hypotheses, predictions, experiments,
                                   observations, failures, artifacts,
                                   lineage_edges, budget, checkpoints }
MEASUREMENT (foundry-global, versioned)
```

A WORLD is the primary experimental unit and the isolation boundary. Its id
survives client disconnect, worker death, and Foundry restart because all of its
state is rows in the database, not process memory.

## Key mechanisms

**Atomic work claim.** `claim_work` runs `BEGIN IMMEDIATE`, reclaims any expired
leases, selects the highest-priority claimable item for a RUNNING world, and
`UPDATE`s it to CLAIMED with a lease -- all under the write lock, so two workers
never claim the same unit. Completion is idempotent and exactly-once: a second
distinct worker is rejected; the original worker's replay returns the stored
result.

**Lease recovery.** A claim carries a lease deadline and a heartbeat. A dead
worker stops heartbeating; the next claim reclaims the expired lease to RETRYABLE
(or EXPIRED past max attempts) and records `WORK_EXPIRED`. No background sweeper
is required.

**Per-world hash chain + fork by reference.** Each world's events chain by
`prev_hash`. A fork child is created with `next_index` and `head_hash` seeded
from the parent's fork-point event, so the child's first event chains onto the
parent's immutable prefix WITHOUT copying a row. The shared prefix is the
parent's rows; neither parent nor child can write the other's rows, so they
cannot mutate one another. `world_history()` resolves the inherited prefix by
walking ancestors; `verify_world()` checks a child links to the correct fork
point.

**Prediction ordering.** A prediction seals its content hash and stamps the
`event_seq` at registration. An observation that references a prediction is
rejected unless the prediction's seq strictly precedes the observation's --
post-hoc laundering is exposed by the honest sequence, not trusted narration.

**Sharing topology.** A world's `sharing_policy` names the information KINDS that
may cross into it; `import_artifact` gates a cross-world transfer by that policy
(and by matching `topology_group`) and records permanent provenance
(`origin=IMPORTED`, source world/artifact/hash). An imported object can never be
mistaken for an independent discovery.

**Budgets.** A world carries limits with an enforcement class (enforceable /
measured / estimated / unavailable -- precision is never fabricated). Consuming
past an ENFORCEABLE limit records `BUDGET_EXHAUSTED`, marks the world exhausted
(committed), then raises.

## What is deliberately NOT here

No distributed infrastructure (one SQLite file). No agent framework, no
LLM-authored state transitions, no process-local authoritative state, no
JSONL-as-a-queue. Intelligence (mutation, selection, interpretation) lives in
drivers/executors, never in the runtime (section 26).
