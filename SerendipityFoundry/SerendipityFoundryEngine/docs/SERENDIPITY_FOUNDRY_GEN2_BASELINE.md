# Serendipity Foundry Gen-2 - Forensic Baseline

Empirical audit of the EXISTING Foundry (`F:\SerendipityD`, release `50b5c232`,
git `ac57cf8`) against the Gen-2 multi-world-runtime requirements. Every
classification below is backed by a read-only probe (in-process `TestClient` on a
throwaway temp dir) or a cited code path. The live D-13 service and its data
(`var/`) were NOT touched during the audit.

## Method

Seven capability clusters were probed in parallel, read-only. Probes imported
`foundry`, exercised the ledger / store / API against temp directories, and
inspected code; none contacted the running service on `192.168.1.202:8799` and
none wrote to `var/`. A capability is `VERIFIED` only if a probe demonstrated it,
`BROKEN` only if a probe showed it failing, `ABSENT` if the concept does not exist
in the codebase, `PARTIAL` if some of it exists (with the gap stated), `UNKNOWN`
if read-only constraints prevented a determination.

## Terminology hazard (recorded so it cannot mislead)

In the existing code, **"world" means `CausalWorld`** (`foundry/worlds/`) -- a
sequential transition system a candidate drives. That is NOT the Gen-2 research
**WORLD** (a durable experimental unit owning hypotheses / experiments / failures
/ budget / ledger / checkpoints). Wherever a Gen-2 capability is assessed, it is
assessed against the Gen-2 meaning; the collision is a naming coincidence, not a
capability.

## Capability ledger

Legend: classification | Gen-2 reuse verdict.

### Multi-tenancy (Client / Session / World hierarchy)
| Capability | Class | Verdict |
|---|---|---|
| Per-client identity / client hierarchy | ABSENT | BUILD_NEW |
| Session concept (simultaneous sessions) | ABSENT | BUILD_NEW |
| Multiple research WORLDs (durable experimental units) | ABSENT | BUILD_NEW |
| AppState is a process-local singleton (not multi-tenant) | VERIFIED | MIGRATE |
| Ownership binding on objects | ABSENT | BUILD_NEW |
| Identifier scheme (flat global namespace, no tenant prefix) | PARTIAL | MIGRATE |
| Auth scopes usable as ownership control | PARTIAL | WRAP |
| Simultaneous clients WITH isolation | PARTIAL | MIGRATE |

Evidence: two `TestClient`s resolve to `app.state.foundry is st == True`; both
callers' events land in ONE ledger chain. `client_id`/`session_id`/`owner`/
`tenant` appear nowhere in `foundry/` except one prose comment in `security.py`.
Auth (`security.py:113`) maps a token to a capability scope
(experiment<=observer<=admin), never to a client identity; any valid token sees
all data within its scope.

### Durability & recovery
| Capability | Class | Verdict |
|---|---|---|
| Durable storage substrate survives full process restart | VERIFIED | MIGRATE |
| Crash recovery (torn-tail repair, fsync, cross-process append lock) | VERIFIED | KEEP |
| Genuine immutable ledger + transactional row store (NOT JSONL-as-queue) | VERIFIED | KEEP |
| ALL server-side registries survive restart | PARTIAL | MIGRATE |
| Cross-store transactional atomicity (ledger+blob+SQLite as one commit) | ABSENT | BUILD_NEW |
| Durable per-client SESSION state | ABSENT | BUILD_NEW |
| Durable multi-WORLD isolation (independent persistent worlds) | ABSENT | BUILD_NEW |

Evidence: dispose+reopen on a temp `var_root` recovered the ledger
(`verify()` pass, identical head hash), the blob, the artifact row, and the task;
a simulated torn tail was tolerated and truncated before the next append. But the
**idempotency store and live index objects are in-memory only and were lost**
across restart. The three durable stores (JSONL ledger, CAS blobs, SQLite) are
each independently fsync-durable with careful ordering -- there is **no single
transaction** spanning them. This is the load-bearing finding for Gen-2.

### Work execution (claims / leases / heartbeats)
| Capability | Class | Verdict |
|---|---|---|
| Asynchronous work queue | ABSENT | BUILD_NEW |
| Atomic claiming by workers | ABSENT | BUILD_NEW |
| Leases (time-bounded ownership) | ABSENT | BUILD_NEW |
| Heartbeats (liveness / lease renewal) | ABSENT | BUILD_NEW |
| Lease expiry & reclaim / worker-death recovery | ABSENT | BUILD_NEW |
| Retry of failed work | ABSENT | BUILD_NEW |
| Idempotent completion | PARTIAL | MIGRATE |
| Concurrent workers on distinct units | ABSENT | BUILD_NEW |

Evidence: `/v0/search` executes SYNCHRONOUSLY in the request thread
(`routes/search.py`); there is no queue, no lease table, no worker/claim/heartbeat
symbol anywhere in `foundry/`. The only asynchrony-adjacent feature is an
in-memory Idempotency-Key cache. This is the exact "backlog vs execution" hazard
Gen-2 must not repeat, and it is entirely unbuilt.

### Evidence ledger & provenance
| Capability | Class | Verdict |
|---|---|---|
| Append-only immutable event history | VERIFIED | KEEP |
| Hash-chaining of events | VERIFIED | KEEP |
| Tamper detection (`verify()`) | VERIFIED | KEEP |
| Crash durability / locking / segment rotation / torn-tail | VERIFIED | KEEP |
| Structured failures as first-class QUERYABLE objects | PARTIAL | MIGRATE |
| Artifact-ancestry lineage DAG | VERIFIED | KEEP |
| Research-WORLD lineage (hypotheses/experiments/budget) | ABSENT | BUILD_NEW |
| Provenance / scientific identity | VERIFIED | MIGRATE |
| Per-world / per-session ledger partitioning | ABSENT | BUILD_NEW |

Evidence: probe appended events and `verify()` passed; tampering a segment byte
made `verify()` fail (tamper-evident). `FailureVector`/`EvaluationResult` capture
failure DATA but it is embedded in an evaluation result, not a queryable
first-class object with its own id, type, falsifier, lineage, or consumption
edges. Lineage today is `parent_ids` on artifacts only.

### Determinism / checkpoints / replay / fork
| Capability | Class | Verdict |
|---|---|---|
| Deterministic named seed streams | VERIFIED | KEEP |
| Semantic (hash-equality) replay of a run | VERIFIED | MIGRATE |
| Bit-deterministic replay through external/nondeterministic calls | PARTIAL | MIGRATE |
| Replay of a mutation event (re-derive from recorded operator config) | VERIFIED | MIGRATE |
| A "checkpoint" that can restore/fork a research world | ABSENT | BUILD_NEW |
| Research-world checkpoint (budget/hypotheses/ledger-cursor/RNG) | ABSENT | BUILD_NEW |
| World FORK (frozen shared history + independent divergence) | ABSENT | BUILD_NEW |

Evidence: `SeedStream`/`derive_seed_at` are deterministic and reused across the
codebase; D-13 mutation replay re-derives the artifact from the recorded
effective operator config. But the searchphysics `/checkpoint` returns a
measurement STATE VECTOR, not a restorable world snapshot; there is no fork
operation of any kind.

### Resource budgets / isolation / sharing topology / auth
| Capability | Class | Verdict |
|---|---|---|
| Per-world resource budget accounting + enforcement | ABSENT | BUILD_NEW |
| Per-evaluation resource METERING vector | PARTIAL | MIGRATE |
| Enforceable per-operation execution limits (steps/timeout/size) | VERIFIED | MIGRATE |
| World-vs-world data isolation | ABSENT | BUILD_NEW |
| Observer/semantic firewall (measurement !-> selection) | VERIFIED | KEEP |
| Cross-world sharing policy / information topology | ABSENT | BUILD_NEW |
| Artifact import/export with provenance | PARTIAL | MIGRATE |
| Authorization boundary (does knowing an id grant access?) | PARTIAL | MIGRATE |

Evidence: `EngineLimits` (steps/timeout/size) are enforced per operation and
`ResourceVector` meters per evaluation, but there is NO per-world budget with an
exhaustion transition. The existing firewall isolates MEASUREMENT from SELECTION,
not WORLD from WORLD. Today, a valid token + an object id grants access (no
ownership check), so "knowing an id grants access" is effectively TRUE within a
scope -- a Gen-2 isolation gap.

### Measurement registry / executor adapter / orchestration
| Capability | Class | Verdict |
|---|---|---|
| Versioned OPERATOR registry (interventions as research objects) | VERIFIED | KEEP |
| Operator `validation_status` + `implementation_hash` fields | ABSENT | BUILD_NEW |
| Versioned METRIC/ORACLE registry | ABSENT | BUILD_NEW |
| Executor adapter contract (pluggable execution) | VERIFIED | KEEP |
| Executor isolation / subprocess / remote | PARTIAL | MIGRATE |
| Executor leases / concurrency / per-worker budgets | ABSENT | BUILD_NEW |
| Frozen probe batteries as content-addressed objects | VERIFIED | KEEP |
| In-repo orchestration / backlog / status-generator | ABSENT | N/A |
| Consolidation verdict | VERIFIED | KEEP |

Evidence: `foundry.operators` (D-13) IS a versioned registry of interventions
with typed/ranged params + config hashing -- a good model for the measurement
registry, which does not yet exist. `EngineAdapter` is a clean pluggable
execution contract. There is NO backlog/status-generator/scheduler inside
`F:\SerendipityD` that could be mistaken for an executor.

**Orchestration scope note:** section 27 asks to inspect "existing Prometheus
orchestration machinery." The broader `F:\Prometheus` repository is OUT OF SCOPE
for this expedition under this project's firm directory rules and was NOT
inspected. Within `F:\SerendipityD` the only execution machinery is the
synchronous REST API + in-process engines; there is no separate orchestrator to
consolidate here. If Prometheus-repo orchestration exists, its consolidation is a
follow-up that must be run where those directories are in scope.

## Verdict: what Gen-2 keeps, migrates, and builds

- **KEEP the ideas, not the files, of the immutable ledger.** The JSONL
  hash-chain is durable and tamper-evident but is a single global chain and
  cannot participate in a cross-store transaction. Gen-2 re-expresses the same
  discipline (append-only, `prev_hash` chain, `verify()`) as a table inside one
  SQLite database, so an event append, a state change, and a work claim commit
  as ONE transaction -- closing the two biggest ABSENT durability gaps
  (cross-store atomicity, per-world partitioning).
- **KEEP** deterministic seed streams, content-addressed hashing, the versioned-
  operator pattern, and the executor-contract idea -- reused or mirrored in
  `gen2/`.
- **BUILD_NEW** (absent today, the bulk of Gen-2): client/session/world
  hierarchy + ownership; the async work queue with atomic claim / lease /
  heartbeat / expiry / reclaim / retry; per-world budgets + exhaustion; world-vs-
  world isolation; sharing topology + artifact-import provenance; first-class
  queryable failures + metabolization edges; the hypothesis/prediction/experiment
  epistemic state machine with prediction-ordering enforcement; the lineage DAG;
  the versioned measurement registry; research-world checkpoint + fork.

## Storage decision (grounded in the above)

SQLite in WAL mode with foreign keys ON is the Gen-2 authoritative substrate.
Rationale from evidence, not preference:
1. cross-store atomic commit is ABSENT and SQLite gives it for free (one
   transaction over events + state + work);
2. atomic work claiming (ABSENT) is a single `UPDATE ... WHERE status='QUEUED'`;
3. per-world partitioning (ABSENT) is a `world_id` column + index;
4. referential integrity + queryability (needed for lineage/failure queries) are
   native;
5. it is boring, single-machine, concurrent-reader friendly, and recoverable --
   exactly section 23's constraints. Blobs remain content-addressed on disk
   (the existing CAS pattern), referenced by hash from SQLite rows.

## Safety posture for the Gen-2 build

Gen-2 is implemented under a NEW top-level `gen2/` package, which is OUTSIDE the
release allowlist (`foundry`, `tests`, `third_party`, `scripts`). Therefore
adding Gen-2 code does not change `source_tree_hash`, `release_match` stays
`True`, and the running D-13 service + M2's release pin are unaffected. Gen-2
runs as a SEPARATE process on a DIFFERENT port with its OWN database. The live
service is never restarted or modified by this work.
