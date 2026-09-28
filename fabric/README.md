# Prometheus Agent Fabric v0

A durable work queue for the Prometheus fleet, running as a sidecar to comms. It is built on the canonical Postgres
on M1 (schema `fabric`) and exposes an A2A v1.0 gateway. Its job is to keep work alive when a Claude session
ends. The rule is **threads queue, researchers don't**.

Owner: Odysseus (ubu001). Operator directive (verbatim):
`roles/Odysseus/prompts/2026-09-28_fabric/01_OPERATOR_DIRECTIVE_verbatim.md`.

## 1. Architecture

```
 principal (seat / operator / script)                A2A client (TCK, other agents)
        | python -m fabric submit ...                        | JSON-RPC  POST /a2a/jsonrpc
        v                                                    v
 +-------------------------- fabric.store (Postgres on M1, schema "fabric") ---------------------------+
 | tasks  attempts  leases  artifacts+blobs  events  messages  agents/agent_instances                  |
 | all invariants enforced IN THE DATABASE: one live attempt per task, one holder per resource,       |
 | idempotent submit, DB clock for every expiry                                                        |
 +------------------------------------^-----------------------------------^----------------------------+
                                      | claim / heartbeat / finish        | read-only view
                        fabric.worker (one process = one attempt)    fabric.gateway (stateless)
                          |- pinned detached worktree per base SHA
                          |- executor: claude | script | synthetic
                          '- the RUNTIME uploads artifacts (not Claude)
```

- **Thread != Task != Attempt.**
  - A comms thread (`thread_id`) is a conversation. It can own many Tasks.
  - A Task is one unit of requested work, with a durable state machine.
  - An Attempt is one worker's try at a Task. A Task may have several Attempts; at most one is live.
- **Pull, not push.** Workers advertise capabilities and executors, then claim compatible work. No scheduler
  assigns work to a machine. A Task names what it needs (`required_caps`, `resources`, and optionally
  `host_affinity` or `target_agent`), not who runs it.
- **The store is the only authority.** The gateway and the CLI hold no state. A gateway restart loses nothing (P8).
- **Fail closed.** No store means no claims, no leases and no work. There is no fallback lease convention.

## 2. Data model (`schema.sql`)

| table | key fields | invariant |
|---|---|---|
| `tasks` | `task_id tsk-`, principal, thread/campaign/experiment ids, `base_sha`, instruction, executor, params, `required_caps[]`, `resources[]`, host/target, priority, `max_attempts`, state, `cancel_requested` | `UNIQUE(principal, idempotency_key)`; terminal states are immutable |
| `attempts` | `attempt_id att-`, task, seq, agent/instance/host, model, status, base_sha, worktree, `lease_ids[]`, env_receipt, `expires_at` | partial unique index: one `running` attempt per task |
| `leases` | `lease_id lse-`, resource, attempt, holder, host, purpose, token, `expires_at`, `released_at` | partial unique index: one unreleased lease per resource |
| `artifacts` / `blobs` | name, kind, media type, `sha256`, size, metadata / content-addressed bytea | content verified by sha256 on read; 16 MB limit per artifact |
| `events` | append-only history: submitted, claimed, resource_busy, heartbeat, artifact_added, abandoned, requeued, late_finish_rejected, ... | never updated |
| `messages` | A2A user/agent messages per task | |
| `agents`, `agent_instances` | capabilities, executors, host, model, `last_seen_at` | the live Agent Card is built from these |

Task states are submitted, working, input-required, completed, canceled, failed and rejected. Attempt statuses are
running, succeeded, failed, abandoned and canceled.

## 3. CLI (principals)

```
export EW_DB_HOST=192.168.1.202          # the canonical Postgres on M1
python -m fabric init                     # create the schema (idempotent)
python -m fabric submit --as Odysseus --cap research.repo_readonly --base <sha> --prompt-file q.md \
       [--executor claude|script|synthetic] [--model M] [--wall-s N] [--tool web] [--resource gpu:m1] \
       [--host ubu002] [--target worker.x] [--thread thr-..] [--key <idempotency>] [--wait 600]
python -m fabric tasks [--state S] [--thread T] | show T | events T | artifacts T | get ART --out f | cancel T
python -m fabric lease acquire|renew|release|status <resource> --purpose ...   # manual leases for humans/scripts
python -m fabric worker --agent worker.ubu001 --caps repo.read research.repo_readonly ... [--executors claude script]
python -m fabric gateway --port 8710
python -m fabric agents | reap
```

A script task runs a repository file or module at the pinned SHA, for example
`--executor script --param module=pkg.mod --param 'env=["COSMOS_BROKER"]'`. It runs without a shell, and only
allow-listed environment variables are passed through.

## 4. Worker and executors (`worker.py`, `executors.py`)

1. The worker loop is reap, then touch, then claim. `claim` uses `FOR UPDATE SKIP LOCKED`:
   - it filters on `required_caps <@ worker caps`, executor, host and target;
   - it inserts the attempt and takes every resource lease in the same transaction;
   - a busy resource rolls back to a savepoint, records `waiting_reason` and a `resource_busy` event, and the
     worker moves on to other work.
2. The **worktree** is a detached checkout of `base_sha` for this worker only:
   - it is created from the canonical clone under a per-host flock;
   - the canonical clone is only fetched, never pulled;
   - after each attempt any change is captured as `changes.patch` (an artifact), then the checkout is reset.
3. A **heartbeat thread** runs every ttl/4 and extends the attempt and its leases:
   - `ok=false` means the attempt was fenced, and the executor is killed;
   - `cancel_requested` means the executor is killed and the attempt is canceled.
4. The **runtime uploads** `final_text.md`, `stdout`, `stderr`, `env_receipt.json`, every file in `out/`, and the
   patch. This happens whether or not the executor managed to write anything.
5. **Claude executor** (isolated and disposable):
   - `claude -p` with an empty `CLAUDE_CONFIG_DIR` and `HOME` set to the attempt directory, so there is no seat
     memory and no settings;
   - an explicit `--model` (an empty config directory silently changes the default model), with the model
     actually used recorded from `modelUsage`;
   - `--permission-mode dontAsk`;
   - Read, Grep and Glob scoped to the worktree and `out/`; Write and Edit to `out/` only;
   - `git log` and `git show` only;
   - explicit denies for `~/.claude`, `~/.config`, `~/.ssh` and `~/.git-credentials`.

   The token is read from `~/.config/prometheus/claude.env`, and only `CLAUDE_CODE_OAUTH_TOKEN` is passed on. It is
   never printed, logged or stored. The worker has no sudo, no package installation, no arbitrary shell and no
   python (see D3).

## 5. Leases

There is one convention: the `leases` table. Workers take leases with claims. Humans and scripts use
`fabric lease` for work outside the fabric.

- A lease is token-fenced, has a TTL on the DB clock, and is renewed by the heartbeat.
- A stale lease expires on the next acquire or reap.
- For substantial shared compute, fail closed if the store is unreachable.

## 6. Recovery

- **Worker death:** the heartbeat stops and `reap()` (any worker or `fabric reap`) marks the attempt abandoned. Its
  leases are released and the task is requeued if `attempts_made < max_attempts`; otherwise it fails.
- A late `finish_attempt` from a zombie is rejected (`late_finish_rejected`). A killed attempt uploads nothing, so
  it leaves no false artifacts (P4).
- **Principal death:** the task does not depend on the principal (P3).
- **Gateway restart:** stateless, so nothing is lost (P8).

## 7. Artifacts

Artifacts are content-addressed (sha256) in Postgres. The A2A view shows deliverables: output files, patches,
reports and bundles. Forensic artifacts (stdout, stderr, env receipt) are listed in task metadata and served at
`GET /artifacts/<id>`.

Workers never commit or push. A patch is an artifact for a principal to review (P6: `origin/main` unchanged and
the checkout clean after the worker tried to commit and push).

## 8. A2A gateway

See `PROTOCOL.md` for compliance and deviations. It supports the A2A v1.0 JSON-RPC binding only, checked with
the official a2a-tck:
- MUST: 68 tests passed, 0 failed (56 requirements pass, 0 fail);
- SHOULD: 8 tests passed, 0 failed, 0 xfail;
- every remaining JSON-RPC skip is a feature declared unsupported.

Evidence is in `validation/`. Streaming, push notifications and the extended card are **not** implemented and are
declared false in the card. This is not a claim of full A2A compliance.

## 9. Pilot evidence (`pilot/evidence/*.json`, 2026-09-28, ubu001)

| test | result |
|---|---|
| P1 routing by capability | PASS: no task named a machine; the lite worker only ever took the compute task |
| P2-local atomic claim race | PASS: 20 tasks, 3 workers, 20 claims, split 7/7/6, 0 duplicates. P2 **cross-host** (ubu001 vs ubu002) PENDING: needs a worker on ubu002 (#854) |
| P3 principal disappears | PASS: submitted, principal exits, completed, retrieved by a new process |
| P4 worker SIGKILL mid-attempt | PASS: attempt abandoned, 0 artifacts from it, rescued by a second worker 37.3 s after the kill |
| P5 resource contention | PASS: heavy task waits ("resource pilot:cpu8 busy") while the same worker completes research; heavy runs 5.1 s after release |
| P6 artifact deposition without git write | PASS: report captured by the runtime, commit and push denied, `origin/main` unchanged, checkout clean |
| P7 context isolation | PASS: no seat identity, model `claude-opus-5-5` requested and used |
| P7b secret-path canary | PASS: repo read OK; `~/.claude` and `~/.config` canaries DENIED; no leak |
| P8 gateway restart | PASS: GetTask identical before and after; ListTasks total 28 = 28 |
| P9 A2A TCK | PASS (v0.1 rerun): MUST 68 passed / 0 failed; SHOULD 8 passed / 0 failed / 0 xfail (JSON-RPC). The first report ("65/65") overstated coverage; see D6 |

Canary files for the P7b regression are left in place deliberately: `~/.claude/fabric_canary.txt` and
`~/.config/fabric_canary.txt` (non-secret marker strings).

## 10. Defects found and fixed during the pilot

- **D1 (P7): seat memory was visible to workers.** Unscoped Read plus path-free shell readers (`head`, `ls`)
  could see `~/.claude/projects` and the token file. Fixed with scoped tools, explicit denies, `HOME` set to the
  attempt directory, and those readers removed. Regression test: P7b.
- **D2: Claude permission rules need `//abs` for absolute paths.** Before the fix, writes to `out/` were denied.
  The runtime still captured the report, which is why the runtime (not Claude) does the uploading.
- **D3: the `--tool python` option was arbitrary code** as the node account and bypassed every Read deny. It was
  removed. Code now runs through the `script` executor (pinned file or module, no shell, allow-listed env).
- **D4: an empty `CLAUDE_CONFIG_DIR` changes the default model** (Archaeon lesson). `--model` is always explicit,
  and the model used is recorded.
- **D5: concurrent `git worktree add` on one clone collides.** Serialised with a per-host flock.
- **D6: TCK skips hid gateway bugs, and the first compliance line overstated coverage.** The bugs were:
  - `messageId` used as an idempotency key;
  - snake_case keys ignored;
  - continuation kept the old behaviour;
  - wrong Content-Type accepted;
  - history deduplicated by messageId.

  All were fixed. Lesson: read the skip reasons and xfails, not just the pass line.

## 11. Known limits (v0)

- There is no auth on the gateway: bind it to the LAN only. ListTasks is not scoped to the caller.
- Blocking SendMessage is capped at `FABRIC_BLOCK_CAP_S` (120 s by default), after which the non-terminal task is
  returned.
- A worker runs one attempt at a time; run N processes for N slots.
- The reaper runs inside worker loops. With zero workers alive, nothing reaps (`fabric reap` does it by hand).
- Workers are Linux-only (process groups, flock). Windows workers are not in v0.
