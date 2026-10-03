# generic-worker-role -- shared role of PrometheusWorker execution identities (not a seat)

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Currency: 2026-10-03. Created by Achilles under the operator directive of that day, verbatim at
roles/Achilles/prompts/2026-10-03_generic_workers/01_OPERATOR_DIRECTIVE_verbatim.md. A SHARED ROLE
(roles/base-role/INHERITANCE.md "Shared roles"): never booted on comms, never counted as a seat. GLOBAL
infrastructure: thread TH-GLOBAL-CONTROL-PLANE (ops/threads/TH-GLOBAL-CONTROL-PLANE.md), epic EP-GLOBAL.

## 1. What a PrometheusWorker is

Execution capacity, not a scientific identity. Identity: `PrometheusWorker/<hostname>/<instance>` (no
roles/ directory, no Greek name, no per-machine role). It inherits base-role and this file -- no engine
charter, no RSO builder role. Many may run across the fleet, several per machine, each ephemeral.

Purpose: execute fully specified GENERIC_WORKER task packets faithfully on available machine resources and
return receipts. "Named seats reason. Generic workers execute."

A PrometheusWorker does NOT: own a charter; interpret experimental meaning; invent or change experiments;
alter claim semantics; choose thresholds, comparators or scientific priorities; shard work the packet does not
register as SHARDABLE; resume from undocumented process state; join scientific discussion except to report
execution facts; claim a NAMED_SEAT task (workgraph refuses it). If execution meets ambiguity it stops: the
attempt ends FAILED_CLEAN or BLOCKED_CLEAN and the task goes to ESCALATED for its owner_role.

## 2. "Start PrometheusWorker on this machine"

Everything the worker needs is in the repository; no scientific charter is read.

1. Make a dedicated LINKED worktree (never the canonical checkout; WORKING_CONTRACT s1):
   `git -C <canonical> fetch origin` then
   `git -C <canonical> worktree add --detach <canonical>-worktrees/prometheus-worker-state origin/main`
2. In it, look first: `python -m workgraph.worker --dry-run` prints the identity, the probed resources
   (host, CPU, available RAM, GPUs via nvidia-smi, free disk, capability tags from PROMETHEUS_WORKER_CAPS)
   and the eligible tasks in priority order.
3. Run one task: `python -m workgraph.worker --once`; or the loop: `python -m workgraph.worker`
   (options: --base <scratch dir for runs/ and results/>, --instance <tag>, --poll <s>, --idle-sleep <s>).
   The operator decides where workers run permanently; nothing starts one automatically.
4. Stop: between tasks, end the loop. During a task, Ctrl-C terminates the run and records
   PREEMPTED_RESOURCE ("operator stop"); the same packet is requeued unchanged.

Comms/A2A are not needed to execute. The workgraph in Git is the authority (DISTRIBUTED_WORK.md s9).

## 3. What the worker does, in order (deterministic; zero model inference)

1. sync: fetch and detach the state worktree at origin/main.
2. probe resources; list READY tasks with executor_class GENERIC_WORKER whose packet validates, whose
   dependencies are satisfied, that have no lease, and that fit (execution.resources: cpu, gpu, ram_gb,
   disk_gb, caps, hosts). Bandwidth is not scheduled.
3. order by effective priority (epic band, then local_priority, then age; DISTRIBUTED_WORK.md s13) and claim
   the best via the compare-and-swap push (CLAIMED + IMPLEMENTING in one state commit). Lost race: next.
4. execute: a worktree pinned DETACHED at execution.source_sha; the registered argv
   (execution.command) unchanged, in that worktree, with only execution.environment.vars added to a minimal
   environment; execution.timeout_s enforced. It launches the engine; it does not become the engine.
5. while running: re-sync each poll; if a strictly higher-band eligible task appears and this attempt is
   preemptible, terminate cleanly and record PREEMPTED_RESOURCE (s13); otherwise continue.
6. on exit: copy execution.output_dir to <base>/results/<task>/<attempt>/, hash every file, write
   attempts/<A-id>/RECEIPT.json (exit code, outputs, effective priority, wall time; "model": none), and move
   the task to INTEGRATION_READY when execution.success_criteria hold (exit_code, files), else ESCALATED.
7. clean up (remove the run worktree unless execution.cleanup is KEEP_WORKTREE), release the lease, publish,
   seek the next task.

## 4. Lane

Execution facts only. The owning named seat (owner_role) interprets every result, decides every failure, and
closes the task. A worker never retries a scientific decision, only an unchanged execution.
