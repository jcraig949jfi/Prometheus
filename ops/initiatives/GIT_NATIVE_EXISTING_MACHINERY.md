# Existing Prometheus coordination machinery: mine, don't rewrite

> **STATUS: STRATEGIC INITIATIVE — PILOT / EVOLVING — NOT A UNIVERSAL OPERATING MANDATE**
>
> The presence of these files or commits does not authorize any seat to migrate its current workflow, stop current
> science, rewrite existing queues, or adopt this operating model on its own initiative. Existing scientific work
> continues under its current contracts unless the operator explicitly selects a seat or campaign for transition.

Companion to `GIT_NATIVE_LAB_CONTROL_PLANE.md`. Harmonia[m2-475d761f], 2026-09-27; every path was checked to exist at
origin/main 0d71dd200. **None of these systems is replaced, frozen or deprecated by the initiative.** They are listed so the
pilot learns from designs Prometheus has already built, run and, in several cases, forensically audited.

## 1. Vivarium canonical research queue (the closest existing Task/Attempt system)

- `Vivarium/migrations/001_vivarium_queue.sql`: `viv.research_experiment_queue`, status `queued → claimed → running →
  completed | failed | cancelled`, enforced by a transition trigger (terminal rows immutable); `claimed_by`/`claimed_at`;
  `research_experiment_events` log; `worker_heartbeat`.
- `Vivarium/viv/queue.py`: `claim_next()` with `FOR UPDATE SKIP LOCKED`; `stranded(stale_after_s=900)` and
  `release_stranded()`, which by default fails a stranded row and requeues only by the explicit `new_attempt` path.
- `Vivarium/migrations/006_execution_attempts_and_steps.sql` (DRAFT point release): `execution_attempt`,
  `execution_step`, `provenance_envelope`. **This is already an Attempt-level model** under an experiment row.
- `Vivarium/viv/deadman.py`: worker LIVE/BUSY/DEAD classification from heartbeats; bounded automatic
  `release_new_attempt()`.
- `roles/Vivarium/point_release/EXPERIMENT_TRANSACTION_MODEL.md`, `TERMINATION_ENVELOPE.md`: the transaction model
  and termination semantics. **Relevant to the cleanup contract (s12)**; read them before inventing terminal states.
- `archaeon/vivqueue.py` (Archaeon's writer; cadence caps per lane per UTC day), `archaeon/docs/QUEUE_RELATION_CONTRACT.md`.

**Lesson to carry:** a stranded claim defaults to *failed*, not silently re-queued. A retry is an explicit new Attempt.
This is the Task/Attempt distinction, already practised.

## 2. Other claim / lease / requeue patterns

- **comms** (`comms/schema.sql`, `comms/api.py` `claim()`): `task_queue` with an atomic `UPDATE … WHERE status='queued'`
  returning CLAIMED / LOST(held_by) / NOT_QUEUED. **No lease expiry, no requeue**: a claim held by a dead instance
  stays held. Useful as a counter-example for s5 (lease expiry is an open question).
- **SFE** (`SerendipityFoundry/SerendipityFoundryEngine/sfe/store.py` `work_items`; `sfe/runtime.py` `_reclaim_expired`):
  `claim_id` **fencing token**, `lease_expires`, `heartbeat_ts`. **The most complete lease design in the repo.** A Git
  lease should consider a fencing token, so a worker that lost its lease can't commit results as if it still held it.
- `engine/driver/backlog_gen.py`: backlog item INFRA-QCLIENT "PG queue client: SKIP LOCKED + fencing tokens + DLQ"
  (a proposed dead-letter queue, cf. DIRTY → CLEANUP).
- `scripts/agora_persist.py`: `agora.research_queue`, `agora.agent_heartbeats`, `agora.gpu_reservations`.

## 3. GPU / resource reservation (prior art for resource leases, s6)

- `pivot/gpu_reservation_system_2026-05-23.md`: Postgres per-GPU lock with TTL; partial unique index
  `(machine, gpu_id) WHERE status='active'`.
- `scripts/gpu_reservation.py` (CLI: acquire / renew / release / force-release / sweep) over the `agora_persist.py`
  functions `acquire_gpu`, `renew_gpu`, `release_gpu`, `sweep_expired_gpu_reservations`.
- `primordial/bus/bus.py`: Redis lease `pm:gpu:lease` with `gpu_lease()` renewing at ttl/3 and a `lost` flag on failed
  renewal (**lease-loss detection in the worker**). `primordial/nv/gpuq.py`: GPU arbiter, requeue ≤ 3 attempts,
  records VRAM before/peak.
- RunPod: `Aether/runpod/prometheus_gpu/launch.py` (+ `provider.py`); `Aether/runpod/aeth01_canary/independent_reaper.py`
  and `terminate_and_verify()` in the Aether orchestration scripts. **"Terminated and absence verified" (s12) already exists
  here.**

**Lesson to carry:** GPU leases in Prometheus were built on runtime stores with TTL renewal, not on Git. A Git resource
lease is a *declaration and record*; whether live enforcement stays in Postgres/Redis is open question Q6.

## 4. Archaeon / Vivarium queue history

- `archaeon/docs/QUEUE_RELATION_CONTRACT.md` and the migration that retired Archaeon's own `archaeon.experiment_queue`
  in favour of Vivarium's canonical queue: **Prometheus has already consolidated queues once.** Read this before proposing
  a new one.
- `archaeon/frontier/DEEP_FRONTIER_CHARTER.md` (2026-09-18): lineage registry
  (`archaeon/frontier/registry/{LINEAGES,EVENTS}.jsonl`), **file-based** queues
  (`archaeon/frontier/queues/{EXPLORATION,EXPLOITATION,AUDIT}.jsonl`, code `archaeon/frontier/queues.py`; states PENDING /
  CLAIMED / DONE / DROPPED), frozen allocation (`archaeon/frontier/ALLOCATION_RULES_frozen.json`: AUDIT ≥ 0.15,
  EXPLORATION ≥ 0.2, EXPLOITATION ≤ 0.6), and `archaeon/frontier/scheduler.py` with `GLOBAL_HALT.json`.
  **The nearest existing file-in-repo queue, with the pilot seat's own conventions.**

## 5. Orchestration forensics (why the fleet stalls)

- `charon/ORCHESTRATION_FORENSIC_MAP_2026-08-31.md` (+ `.json`): a reporting engine without an execution engine; a backlog
  with no dependency edges; review gates hardened into hard gates. **The CWO's explicit dependencies and the Task
  `depends_on` field answer the second finding directly.** The pilot should check it doesn't recreate the third.
- `roles/Vivarium/INVESTIGATIVE_REPORT_2026-09-11.md`, `roles/Vivarium/NOTES_POSTMORTEM_2026-09-08_to_09-11.md`,
  `roles/Vivarium/INBOX_ARCHAEON_CONSUMER_DEAD_SINCE_REBOOT_2026-09-16.md`: a consumer dead since reboot while the queue
  looked healthy. **"Silence is not health"** applies to Git leases too: a LEASE.yaml can outlive its worker.
- D-23 workspace invariant (one worktree per seat; never mutate the canonical checkout), recorded in
  `archaeon/docs/expansion/DECISIONS.md`: the branch strategy in s5 must fit D-23, not fight it.
- Topology ruling 2026-09-16 (Postgres + Redis shared on M1; every other service on exactly one host), recorded in
  `roles/Vivarium/STATUS.md` and `SerendipityFoundry/SerendipityFoundryEngine/docs/RUNNING_M1_VS_M2.md`: **existing
  placements stay unchanged during the pilot.**

## 6. Fleet inventory (Odysseus)

- `roles/Odysseus/RESPONSIBILITIES.md` s4 "Host and fleet": a Markdown table of M1 SKULLPORT (comms/Postgres),
  M2 SPECTREX5, M3 GANDALF (Hephaestus), M4 HARRY1 (Aphrodite), BUCKKEEP (Aether), UBU002 (Linux, Artemis),
  UBU001 (Linux, Odysseus), DESKTOP-RUAPVAI (no known seat). Supporting: `roles/Odysseus/journal/`,
  `roles/Odysseus/receipts/`.
- `infra/ubuntu_nodes/ubuntu_server_machines.md` (Harmonia, 2026-09-25): hardware facts for ubu001/ubu002 (X1 Carbon 5th gen, 4 threads,
  8 GB RAM, 238 GB NVMe, Wi-Fi, battery health).
- **Proposal only:** Odysseus's table seeds `ops/resources/FLEET.yaml`. Odysseus's charter is **not** changed here.

## 7. Atlas

- `roles/Atlas/RESPONSIBILITIES.md` s0: Atlas is "Prometheus's memory AND its research-policy layer … while never
  running, commanding or adjudicating anyone's science". **This already matches the initiative's Atlas boundary (s9);**
  the initiative restates it and doesn't change it.

## 8. Not found

- No root `ops/` directory existed before this commit.
- No prior "Combined Work Order" / `CWO-` artifact in the repo (the one grep hit is an unrelated research dossier).
