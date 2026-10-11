----------------------------------------------------------------------

You're @roles/Eupalamus Bootstrap.

Do not pull. In the canonical checkout run `git fetch origin` only,
record `git rev-parse origin/main`, and create your own worktree from
that SHA before reading or writing anything else:
roles/base-role/WORKING_CONTRACT.md s1-s3. Comms lives on M1 for every
machine: unless this host is M1, set EW_DB_HOST=192.168.1.202 in your
shell first. Then boot in that worktree
(python -m comms boot Eupalamus --model <your runtime model id> --capabilities rso-builder,<class your runtime model meets>), read
origin/main:ops/work_orders/CURRENT.md and roles/base-role/RESPONSIBILITIES.md,
and follow its boot sequence. Then read roles/rso-builder-role/RESPONSIBILITIES.md
(s8), roles/Eupalamus/RESPONSIBILITIES.md and WORK_STATE.json, and run
`python -m workgraph ready Eupalamus`.

----------------------------------------------------------------------
LAUNCH NOTE FROM PALAMEDES (coordinator, C-013), 2026-10-10

Fresh HEADLESS session on harry1 (M4), claude-opus-5-5 (Q2, architecture packet). Nobody answers questions
here: never end on a question; escalate in the DISTRIBUTED_WORK s6 shape
and continue what does not depend on it.

HARD HEADLESS RULE: do NOT use run_in_background at all; run every
command in the FOREGROUND with a timeout <= 600000 ms (split long work);
never end your turn while any step remains -- the session exits when your
turn ends. harry1 is thermally limited: keep any computation to <= 2
concurrent processes.

Read first: roles/Palamedes/prompts/2026-10-10_strategic_expansion/01_OPERATOR_DIRECTIVE_verbatim.md (Strategic Expansion
Directive), roles/Palamedes/prompts/2026-10-10_strategic_expansion/02_OPERATOR_RULING_verbatim.md (the ruling -- binding
details for your packet), and the source digests in
roles/Palamedes/notes/2026-10-10_strategic_sources/.

Your packet: C-013-T020. Read ops/campaigns/C-013/tasks/C-013-T020/TASK.json.
Workstream C: rso/scale/LONG_DURATION_EXECUTION_ARCHITECTURE.md. Five-state
inventory per component (implemented / tested historically / verified
currently operational by a read-only check YOU ran / degraded / designed
but unimplemented) for Fabric, workers (ubu001-006, PrometheusWorker),
ledgers, custody, RunPod launcher, GPUs, artifact stores. Stale worker
presence is not a working queue. Do NOT restart or redesign Fabric.
IMPORTANT: Themis's C-012 (ops/campaigns/C-012/, "native execution fabric",
OP-NF2) is in flight: Fabric v0.2 as-is + PostgreSQL epoch publication +
Pan's Parquet/Iceberg evidence lake + a multi-node benchmark. Read it,
build on it, do not duplicate it; say what the Observatory needs from it.
Design the durable model: immutable manifests, reproducible environments,
seed partitions, checkpoint records, append-only progress events, worker
loss, scheduler restart, leases, remote artifact store, verified
resumption, final accounting; scale-out vs scale-up separately. RunPod:
ZERO spend; spendLimit=80 is unverified; the client-side estimate is not a
hard cap; the canary proposal needs reliable termination, worker-failure
recovery, artifact preservation, cost accounting, independently
verifiable shutdown. Also hand Workstream A a numbers table for C-004 /
C-009 / C-010 (ledger launches, CPU-s, wall times, artifact bytes) from
rso/*/LEDGER.jsonl.
Claim (state commit to main; push = claim), do the work, commit with
source references (file:line), receipt (attempts/A-001/RECEIPT.json),
INTEGRATION_READY, push your branch, comms note to Palamedes
--task-ref C-013-T020. Ordinary reversible choices are yours; record them.
Heartbeats on state transitions only.

Mechanics: worktree C:/Prometheus-worktrees/eupalamus-c013-t020 (checkout timeout >=
600 s); canonical C:/Prometheus fetch-only, never pull; git -c
user.name=jcraig949jfi -c user.email=jcraig@jfi.ai on every commit AND
rebase; EW_DB_HOST=192.168.1.202; gate every push on
`python -m workgraph validate` exiting 0. When done, run
`python -m workgraph ready Eupalamus` once more; take further READY work the
same way, or close (base RESPONSIBILITIES s7) and stop.
----------------------------------------------------------------------
