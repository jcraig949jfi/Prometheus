# Gen-2 Test Report

`gen2/tests` -- 30 passed, 0 failed, 0 skipped. Every test provokes a real
mechanism (threads, DB restart, lease expiry, direct DB tampering); nothing is
mocked; SQLite is the source of truth throughout.

Reproduce:
```
.venv/Scripts/python -m pytest gen2/tests -q
```

## Adversarial battery (section 24)

| T | Requirement | Test function | Result |
|---|---|---|---|
| T1 | Two clients, no leakage | `test_t1_two_clients_no_leakage` | PASS |
| T2 | >=25 worlds across sessions | `test_t2_many_worlds` (27) | PASS |
| T3 | Concurrent mutation of several worlds | `test_t3_concurrent_mutation` (6 worlds, threads) | PASS |
| T4 | Client death, world survives | `test_t4_client_death_world_survives` | PASS |
| T5 | Worker death, work reclaimable | `test_t5_worker_death_reclaim` | PASS |
| T6 | Foundry restart recovery | `test_t6_foundry_restart_recovery` | PASS |
| T7 | Duplicate completion -> one authoritative | `test_t7_duplicate_completion`, `test_t7_concurrent_claim_is_exclusive` | PASS |
| T8 | Isolation attack fails closed | `test_t8_isolation_attack_fails_closed`, `test_http_isolation_attack` | PASS |
| T9 | Fork isolation | `test_t9_fork_isolation` | PASS |
| T10 | Artifact import provenance | `test_t10_artifact_import_provenance` | PASS |
| T11 | Prediction ordering / laundering | `test_t11_prediction_must_precede_observation`, `test_t11_cannot_attach_future_prediction` | PASS |
| T12 | Budget exhaustion | `test_t12_budget_exhaustion`, `test_t12_measured_budget_is_not_enforced` | PASS |
| T13 | Failure lineage chain | `test_t13_failure_lineage_chain` | PASS |
| T14 | Sharing topology | `test_t14_sharing_topology`, `test_t14_topology_group_barrier` | PASS |
| T15 | Ledger corruption detected | `test_t15_tamper_is_detected`, `test_t15_deleting_an_event_breaks_chain` | PASS |
| T16 | Deterministic replay | `test_t16_deterministic_replay` | PASS |
| T17 | Nondeterministic NOT falsely deterministic | `test_t17_nondeterministic_not_falsely_deterministic` | PASS |
| T18 | Load / ceiling reported | `test_t18_load_ceiling` | PASS |

## REST API (`test_gen2_api.py`)

- full flow over HTTP (session -> world -> hypothesis -> prediction ->
  experiment -> observation -> status): PASS
- unauthenticated request -> 401: PASS
- **HTTP isolation attack** (valid token B + known world id of A -> 403 on every
  op, and B cannot create a world in A's session): PASS
- work lifecycle over HTTP (enqueue -> claim -> heartbeat -> complete): PASS
- unknown request field -> 422 (scientific requests fail closed): PASS
- OpenAPI document generated at `/v2/openapi.json`: PASS

## Canary (`test_gen2_canary.py`)

Structural guarantees locked: identical initial conditions, topology enforced +
provenance-visible (W1 imports 0, sharing worlds import >0), all five ledgers
verify, first-class failures + hypotheses recorded per world. The scientific
outcome (whether a topology helps) is left free and recorded separately -- see
`SERENDIPITY_FOUNDRY_GEN2_CANARY.md`.

## Load ceiling (T18, this machine)

300 work-units / 10 workers / 20 worlds in ~0.78s -> ~387 units/s, with every
unit completed exactly once (zero double-commits under contention). This is a
reported basement-hardware ceiling for the current claim protocol, not a hidden
number; it will change with lease durations, work granularity, and disk.
