# Gen-2 Invariants -> Evidence

Each non-negotiable invariant, how it is enforced, and the adversarial test that
proves it. "PASS" means a test provokes the failure mode and the invariant holds
(or the system fails closed). Run: `.venv/Scripts/python -m pytest gen2/tests -q`.

| # | Invariant | Enforcement | Test(s) | Status |
|---|---|---|---|---|
| I1 | Clients are disposable | World state is DB rows, not process memory; a client is just a token | T4 client death, T6 restart | PASS |
| I2 | Worlds are durable | SQLite (fsync, WAL) survives dispose+reopen; recovery verified | T4, T6 | PASS |
| I3 | Workers are interchangeable | Atomic claim + lease + heartbeat; expired lease reclaimed | T5, T6, T7 | PASS |
| I4 | Evidence is immutable | Append-only hash chain in one txn with state; corrections = new events/errata; verify() rejects edits | T15 tamper + delete | PASS |
| I5 | Worlds isolated by default | Ownership checked on every op; sharing only via policy-gated provenance import | T1, T8 (HTTP), T9, T14 | PASS |
| I6 | Predictions precede observations | Prediction seals hash + event_seq at registration; observation ordering enforced | T11 | PASS |
| I7 | Failures are first-class objects | `failures` table with typed schema, queryable by type/consumed, on the lineage DAG | T13; query_failures | PASS |
| I8 | Resource limits belong to the world | Per-world budget with enforcement class; BUDGET_EXHAUSTED transition | T12 | PASS (enforceable); PARTIAL auto-metering |
| I9 | The Foundry records what happened | Every mutation appends an event atomically; agents cannot write history | all mutating tests; T15 | PASS |
| I10 | No LLM is the authority | State = SQLite + hashes + CHECK constraints + tests; accounting is COUNTs | epistemic_accounting; whole battery | PASS |

## Lifecycle & structural guarantees (section 4/5/6/11)

| Guarantee | Test | Status |
|---|---|---|
| Invalid world transition fails closed | smoke + `_WORLD_TRANSITIONS` CHECK | PASS |
| Paused world consumes no work | claim skips non-RUNNING worlds | PASS |
| Fork: identical frozen prefix + independent divergence | T9 | PASS |
| Duplicate completion -> exactly one authoritative result | T7 | PASS |
| Concurrent claim is exclusive | T7 concurrent, T18 | PASS |
| Ledger corruption detected | T15 | PASS |
| Deterministic replay equality (executor) | T16 | PASS |
| Nondeterminism NOT falsely labelled deterministic | T17 | PASS |
| Sharing topology is an enforced, provenance-visible variable | T14 + canary | PASS |
| Load ceiling reported honestly, not hidden | T18 | PASS (~387 units/s) |

## Honest gaps (marked, not stubbed)

- **Resource auto-metering (I8):** enforceable budgets are enforced, but wall/
  cpu/mem/token consumption is only recorded when a caller reports it; executors
  do not auto-measure it yet. Classified `measured`/`estimated`/`unavailable`
  rather than fabricated as enforced.
- **Full replay/restore (section 17):** checkpoints capture chain position +
  state hash + counts; there is no engine to RE-RUN a world from a checkpoint.
  Fork inherits evidence by reference; it does not re-execute. Reproducibility of
  an executor pass is classified honestly (T16/T17), but a whole-world replay is
  not implemented.
- **Executor isolation:** reference executors run in-process; subprocess/remote
  isolation is future work.
- **DELAYED_SHARING:** named but delivered as immediate policy-gated import; no
  background scheduler.
