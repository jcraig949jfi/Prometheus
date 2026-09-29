+==============================================================================+
| PROMETHEUS AGENT FABRIC / A2A v0 -- FINAL REPORT (review packet)             |
| Author: Odysseus (seat), ubu001 (Ubuntu 26.04.1, 4 cores, 7 GB, no GPU)      |
| Date: 2026-09-28                                                             |
| For: operator (HITL) and external reviewers                                  |
| Status: v0.1 on main; P2 cross-host pending (needs ubu002)                   |
| Self-contained: every load-bearing number is inline; no repo access needed.  |
+==============================================================================+

----- 0. Summary --------------------------------------------------------------

- **What was built.** A durable work fabric beside comms. Principals submit Tasks; workers pull them by
  capability; each try is an Attempt.
  - Tasks survive the Claude session that created them.
  - Leases, the single-live-attempt rule and idempotency are enforced by the database.
  - An isolated Claude Code worker has no seat memory and cannot write git.
  - The runtime, not Claude, deposits artifacts, content-addressed.
  - An A2A v1.0 JSON-RPC gateway fronts it.
- **Pilot.** P1, P2-local, P3, P4, P5, P6, P7, P7b and P8 PASS on ubu001. P9: the official a2a-tck on the JSON-RPC
  binding gives MUST 68 passed / 0 failed and SHOULD 8 passed / 0 failed / 0 xfail. P2 cross-host is NOT RUN (no
  worker on ubu002).
- **Science pilot: the operator-designated D2 firewall audit.**
  - Two isolated reviewers ran in parallel, and the self-tests ran as script tasks.
  - I adjudicated and reproduced every blocking finding myself.
  - Verdict FAIL: 4 blocking findings, posted to Nestor as #855. Per the brief, no record was committed.
  - Request to verdict took 14.6 minutes, against about 3h23m that the request waited in a seat queue.
- **Correction on the record.** An earlier line, "TCK MUST 65/65", counted tests. It hid skipped tests caused by
  five gateway bugs, which are now fixed. Section 2 has the accurate statement.

----- 1. Architecture -----------------------------------------------------------

```
principal --CLI/A2A--> [ fabric store: Postgres on M1, schema "fabric" ] <--claim/heartbeat/finish-- workers
                         tasks attempts leases artifacts+blobs events messages agents
```

- **The store is the only authority.** The gateway and CLI are stateless, and every invariant is a database
  constraint:
  - a partial unique index allows one running attempt per task;
  - a partial unique index allows one unreleased lease per resource;
  - `UNIQUE(principal, idempotency_key)`;
  - all expiry uses the database clock.
- **Thread != Task != Attempt.**
  - A comms thread is conversation.
  - A Task is a durable unit of requested work.
  - An Attempt is one worker's try at it.
- **Fail closed.** No store means no claim, no lease and no work.
- **Size.** Code: `fabric/` (store 549 lines, worker 213, executors 188, gateway 383, CLI 165), 17 tests.

----- 2. Protocol (A2A) --------------------------------------------------------

- **Binding:** A2A v1.0 JSON-RPC.
  - Methods: SendMessage, GetTask, ListTasks and CancelTask.
  - The Agent Card is built live from worker capabilities.
  - Requests need `A2A-Version: 1.0` (otherwise -32009) and `Content-Type: application/json` (otherwise -32005).
  - Prometheus fields go under the extension `https://prometheus.local/ext/fabric/v1`.
- **Not implemented** (declared false in the card): streaming, push notifications, the extended card, and the gRPC
  and HTTP+JSON bindings.
- **TCK** (a2a-tck 263b9cf, `--transport=jsonrpc`):
  - MUST: 68 passed, 0 failed, 167 skipped. By requirement: 56 PASS, 0 FAIL, 36 SKIPPED, 22 NOT TESTED.
  - SHOULD: 8 passed, 0 failed, 0 xfail. By requirement: 7 PASS, 4 NOT TESTED.
  - Every remaining JSON-RPC skip is for a feature we declare unsupported.
  - NOT TESTED covers signing, auth/TLS, version negotiation and cross-binding equivalence.
- **Claim:** no MUST or SHOULD requirement that the TCK exercises on JSON-RPC fails. We do NOT claim full A2A
  compliance.
- **Pilot-only deviations:**
  - no authentication (LAN only);
  - ListTasks is not scoped to the caller;
  - a blocking SendMessage is capped at 120 s.

----- 3. Data model -------------------------------------------------------------

| table | contents |
|---|---|
| tasks | tsk-, principal, thread/campaign/experiment ids, base_sha, instruction, executor claude/script/synthetic, params, required_caps[], resources[], host/target, priority, max_attempts, state (submitted, working, input-required, completed, canceled, failed, rejected), cancel_requested, idempotency key |
| attempts | att-, seq, agent/instance/host, model, status (running, succeeded, failed, abandoned, canceled), base_sha, worktree, lease_ids, env_receipt, heartbeat/expiry |
| leases | lse-, resource, attempt, holder, token, expiry, release reason |
| artifacts | art-, name, kind, media type, sha256; bytes in blobs (sha256 key, 16 MB limit, verified on read) |
| events | append-only history |
| messages | A2A history, in arrival order |
| agents, agent_instances | capabilities, executors, host, model, last_seen |

----- 4. CLI --------------------------------------------------------------------

```
python -m fabric init | agents | reap
python -m fabric submit --as P --cap C --base SHA --prompt-file F [--executor ...] [--resource R] [--host H] [--key K] [--wait N]
python -m fabric tasks | show | events | artifacts | get | cancel
python -m fabric lease acquire|renew|release|status
python -m fabric worker --agent A --caps ...
python -m fabric gateway
```

Set `EW_DB_HOST=192.168.1.202`.

----- 5. Worker -----------------------------------------------------------------

- One process runs one Attempt at a time: reap, then claim, then a pinned detached worktree, then the executor with
  a heartbeat thread (fencing and cancel), then the runtime uploads artifacts, then finish.
- **Worktree.** The canonical clone is only fetched and used to add worktrees, under a per-host flock. Any change
  a worker makes is captured as `changes.patch`, and the checkout is reset.
- **Claude executor:**
  - empty `CLAUDE_CONFIG_DIR`, and `HOME` set to the attempt directory;
  - explicit `--model`, with the model actually used recorded;
  - dontAsk permissions;
  - Read, Grep and Glob scoped to the worktree and `out/`; Write only to `out/`; `git log` and `git show` only;
  - denies for `~/.claude`, `~/.config`, `~/.ssh` and `~/.git-credentials`;
  - no Python, no shell, no sudo, no package installation.
- **Token handling.** The token is passed through the environment from the node's protected file. It is never
  printed, logged or stored.
- **Script executor.** Runs a pinned repository file or module, without a shell, with allow-listed environment
  variables only.

----- 6. Routing ----------------------------------------------------------------

- A worker claims a task when `required_caps` is a subset of its capabilities, the executor matches, and any
  host affinity or target matches. Tasks never name a machine unless locality requires it.
- P1: a lite worker advertising only `compute.cpu.light` only ever took the compute task.
- Science pilot: self-tests that required `python.numpy python.scipy` waited until a worker advertising those
  capabilities existed.

----- 7. Leases -----------------------------------------------------------------

- **One convention.** Leases are taken atomically with the claim. They are token-fenced, have a TTL on the
  database clock, are renewed by the heartbeat, and expire when stale.
- **Contention.** A busy resource sets `waiting_reason` and emits a `resource_busy` event; the worker then takes
  other work.
- **Manual leases.** `fabric lease` covers humans and scripts outside the fabric.
- **Open conflict (operator ruling needed).** Archaeon uses the ARC3 "host lease file + comms record" convention on
  ubu001. The fabric does not silently replace it (section 14).

----- 8. Recovery ---------------------------------------------------------------

- **Worker death.** The heartbeat stops and the reaper abandons the attempt, releases its leases and requeues the
  task (up to `max_attempts`). A zombie's late finish is rejected, and a killed attempt uploads nothing.
- **Principal death.** Irrelevant to the task.
- **Gateway restart.** Stateless, so nothing is lost.

----- 9. Artifacts --------------------------------------------------------------

- **Captured by the runtime:** `final_text.md`, stdout, stderr, `env_receipt.json`, every `out/` file, and the
  patch. All are content-addressed and verified by sha256.
- **Git.** Workers never commit or push. A patch is an artifact for a principal to review.
- **Rescue rate.** In the pilot and the science pilot, 100% of artifacts were retrieved without manual rescue. P6
  showed the report was captured even when Claude could not write it itself.

----- 10. Pilot (ubu001, 2026-09-28) --------------------------------------------

| test | result |
|---|---|
| P1 capability routing | PASS |
| P2-local atomic claim race | PASS: 20 tasks, 3 workers, 20 claims, split 7/7/6, 0 duplicates |
| P2 cross-host | NOT RUN: needs one worker on ubu002 (#854; Artemis offline since 15:40Z) |
| P3 principal exits | PASS: completed, retrieved by a new process |
| P4 SIGKILL mid-attempt | PASS: abandoned, 0 artifacts from the killed attempt, rescued in 37.3 s |
| P5 resource contention | PASS: research completed while the heavy task waited; heavy ran 5.1 s after release |
| P6 no git write | PASS: `origin/main` unchanged, checkout clean, report captured |
| P7 isolation | PASS: no seat identity; claude-opus-5-5 requested and used |
| P7b secret canaries | PASS: `~/.claude` and `~/.config` canaries denied, no leak |
| P8 gateway restart | PASS: identical GetTask, list total 28 = 28 |
| P9 TCK | PASS as stated in section 2 |

----- 11. Science pilot: D2 firewall audit ----------------------------------------

- **Why this task.** It is real, operator-designated work (Nestor #827). It was read-only and fully prepared, and
  it was the only gate blocking Cosmos C3.
- **Shape:**
  - two independent Claude reviewers with the same adversarial brief, no Python, and no knowledge of each other
    (about 10-11 minutes each, run in parallel);
  - both self-tests as script tasks;
  - Odysseus adjudicated and reproduced the findings.
- **Result: FAIL.**
  - F1: Cosmos-authored modules run unbound in the key-holding process, and `protocol/__init__.py` can shadow the
    gate module.
  - F2: the predictor can read secrets from disk, and the AST audit can be bypassed with `np.fromfile`, an aliased
    `open`, or a sourceless `.pyc`.
  - F3: a tag can shadow `origin/main`.
  - F4: a record can be swapped through a merge.
- **Convergence.** Both reviewers found F1 and F2 independently. I had derived F1 before reading either report.
- **Self-tests.** Both PASS (34+3 checks and 10+13 checks). None of them exercises these attacks.
- **Where it is.** Posted to Nestor as #855. Evidence: `roles/Odysseus/fabric_pilot/d2_audit/`. Nothing was
  written under `prometheus/cosmos/`.

----- 12. Before / after (measured where possible) ---------------------------------

| metric | before (seat-bound) | fabric (this pilot) |
|---|---|---|
| request to result, D2 audit | #827 waited 3h23m in the seat queue before work began | 14.6 min from submit to posted verdict |
| operator interventions | ubu002 worker (P2) still needs the operator or Artemis | 0 for all ubu001 work |
| relay steps per task | a comms message to a live seat, then a human or seat acts | 0: a worker pulls it |
| tasks lost | #854 cannot progress while its seat is offline | 0 lost. Live schema: 39 tasks; 35 completed, 4 failed (all 4 are the self-test mis-routing, D7); 0 stranded; 0 tasks with two successful attempts |
| duplicate executions | n/a | 0 (enforced by the database) |
| worker start latency | minutes to hours (seat boot) | claim within 6 s of submit; first worktree about 30 s; Claude attempt 40 s to 11 min |
| contention wait | ad-hoc lease files | measured: 5.1 s after release (P5) |
| recoveries | manual | 1 automatic (P4, 37.3 s) |
| artifacts needing manual rescue | frequent (files on one node) | 0% |

Caveat: the "before" column comes from two concrete cases today (#827, #854), not a controlled comparison.

----- 13. Defects (found, fixed, open) --------------------------------------------

Fixed:
- **D1** Workers could see seat memory and the token path: tools scoped, denies added, `HOME` redirected
  (checked by P7b).
- **D2** Claude permission rules need `//abs` for absolute paths.
- **D3** The `--tool python` option allowed arbitrary code; removed.
- **D4** An empty `CLAUDE_CONFIG_DIR` changes the default model; the model is now explicit and recorded.
- **D5** Concurrent `git worktree add` collided; serialised with a flock.
- **D6** TCK skips hid five gateway bugs, and the compliance line overstated coverage. The bugs were fixed and
  the claim corrected.

Open:
- **D7** Capabilities are declared, not probed. A principal mis-declared `python.stdlib` for code needing numpy:
  2 fast, evidenced failures, then a correct resubmit.
- **D8** No gateway authentication.
- **D9** The reaper only runs inside worker loops.
- **D10** Workers are Linux-only.

----- 14. What NOT to migrate ------------------------------------------------------

- Comms itself: threads, rulings, prompts, acks. The fabric sits beside it and never mutates it.
- Seat identity, boot and memory.
- Anything touching holdout keys, custody or reveal. That stays with the key holder, never an unattended worker.
- Anything needing sudo, package installation or host changes.
- Frozen campaigns (Expedition 1, S7).
- Atlas scheduling or any global optimiser.
- Archaeon's ARC3 host-lease-file jobs, until the operator rules on one lease convention.

----- 15. Next migration ------------------------------------------------------------

1. **Thread-to-Task bridge.**
   - A comms `delegation` whose body carries a fenced `fabric:` block (caps, base, executor, prompt path)
     becomes a Task with `thread_id` = that comms thread. The id comes from the message, so the bridge is
     idempotent.
   - When the Task reaches a terminal state, a comms `report` is posted back with `--reply-to`, carrying the
     state, the artifact ids and the verdict line.
   - Comms stays the conversation, and the fabric does the work.
2. **Worker on ubu002, then P2 cross-host** (one command, no install).
3. **Worker on M1** with the at-draw numpy 2.2.6 environment, for Cosmos and Nestor script tasks.
4. **Attestation and recert requests** (TH-006-style hash checks, Archaeon #813) as script tasks with host
   affinity.
5. **One lease convention** (operator ruling). Then add capability probing at worker start (D7).

----- Questions for the reviewer ---------------------------------------------------

1. Is a database-enforced queue beside comms the right boundary, or should comms threads become Tasks outright?
2. Is "runtime deposits artifacts, workers never write git" too restrictive for code-producing work?
3. Did the D2 audit show that the fabric helped, or only that two parallel reviewers are faster than a queued seat?
   Those are different claims.
4. Should the fabric be retired in favour of plain comms plus discipline?

+==============================================================================+
| END. "Not worth continuing" is a legitimate answer; say so if it is.         |
+==============================================================================+
