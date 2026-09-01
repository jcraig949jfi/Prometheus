# Serendipity Foundry API — Apollo working notes (release 50b5c232, 2026-09-01)

Host `https://192.168.1.202:8799`. Canonical client `remote.py` (sha256 bdd6f0771f5c).
Credentials: kit `C:\ZeusD-var\d11\remote\{token.txt,m1.crt}`, loaded at runtime by
`foundry_creds.py` (token never logged/committed). **This file will need revision after
the next Foundry release — treat routes/schemas as version-pinned to 50b5c232.**

## Engines (systems)
- `stackvm-v1`   — register/stack machine, **deterministic**, bit-deterministic replay. Best for replay demos.
- `push-pyshgp`  — pyshgp donor, seeded_stochastic (re-seeds numpy/random per call → replay given seed).
- `treegp-deap`  — DEAP GP, seeded_stochastic.
All: create_random/mutate/recombine/evaluate/describe/trace/step_meter/behavior_trace.
`native_selection_available=false` — selection is a Foundry DRIVER, not the engine.

## Drivers (selection, part of the Q tuple)
`random` (control) · `objective` · `novelty` · `map_elites`. D-12/D-13 use objective+random
only → **novelty + map_elites are Apollo's lane.**

## Tasks (worlds)
Integer function-induction: `inputs:[int] → output:int` (default oracle affine_residual).
- `GET /v0/tasks` → content-addressed `sha256:` ids (thousands exist).
- `GET /v0/tasks/{id}/view` and `/evidence` → train_examples [{inputs,output}], value_kinds.
- `POST /v0/tasks` {train_cases:[[[in..],out],...], test_cases?, admin_metadata?, provenance?}
  → task_id. **Apollo authors its OWN task for isolation** (admin_metadata.client_id=apollo).
  Case format is NESTED `[[inputs], output]`; flat `[in,out]` 422s.

## Key endpoints
- `POST /v0/artifacts` {engine_id, op:create_random|mutate|recombine, seed, config?, parent_ids?} → artifact_id
- `GET  /v0/artifacts/{id}` · `/genotype` · `/lineage`  (fossil material)
- `POST /v0/search` {driver, engine_id, task_id?, seed, budget, config?} → driver report
        {best_fitness, evaluations_used, solved, solver_artifact_id, config_hash}
- `POST /v0/evaluate` {artifact_id, task_id?, seed, limits?}
- `POST /v0/replay` {event_seq}  (reproducibility — charter Job I)
- `GET  /v0/events` (provenance ledger; SELECTION carries candidate_ids + budget_before/after)
- `GET  /v0/operators/{engine_id}` (per-engine mutate/recombine operators + params)
- Search-Physics: POST displacement/heritability/improvement/locality/trace, checkpoint; GET compressors
- `POST /v0/index/build|query|ablate`, `GET /v0/index/{id}/provenance`  (archive/motif index)
- `POST /v0/court/nominate`, `GET /v0/court/cases[/{id}/verdict]`  (independent adjudication —
        the charter's "Apollo proposes, the ecology selects" made literal; do NOT self-promote)
- `GET  /v0/version` (source_tree_hash = the pin) · `/v0/health` (ledger_len, artifact_count)
- `GET  /admin/trace/{trace_id}` (reconcile; admin-scope) · `/admin/events` · `/admin/environment`

## Operating envelope (measured 2026-09-01)
- **/v0/search is SYNCHRONOUS and slow.** budget 1500 map_elites on stackvm did NOT return
  within a 60s client read timeout. Use a patient timeout (≥300s) AND modest budgets on a
  shared host. random driver is cheap; map_elites is the cost.
- **Transport doctrine works.** A client read-timeout raises TransportIndeterminate; the
  orphaned search trace reconciled to `found:false, committed:false` — no budget spent.
  NEVER treat a timeout as a result; reconcile `/admin/trace/{id}` before re-spending.
- Health at probe time: ledger_len ~87.5k, artifact_count ~17.9k (shared across all seats).

## Isolation obligations (charter S5)
Admin-scope token CAN touch other seats' worlds; discipline is Apollo's. Every call carries
client_id=apollo; Apollo only CREATES its own tasks/artifacts, never mutates/deletes another
seat's. Peers on M1: D-12/D-13 (ZeusE console), Harmonia A (genesis/harmonia_a/d14).
