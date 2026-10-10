# Long-duration execution architecture (C-013-T020, Workstream C)

Eupalamus[harry1-68c6ba4c], claude-opus-5-5 (Q2), host harry1 (M4), 2026-10-10. Branch eupalamus/c-013-t020 from
base 9b1893d6f, worktree C:/Prometheus-worktrees/eupalamus-c013-t020. Authority: operator Strategic Expansion
Directive s9, s10, s13-C and OPERATOR RULING s5-s7 (roles/Palamedes/prompts/2026-10-10_strategic_expansion/01_..., 02_...).

Paths are repo-relative and line numbers are at base 9b1893d6f. "CHECK nn" points to a raw output that this seat
captured with a read-only command on 2026-10-10 between 08:04Z and 08:06Z. The outputs are in
rso/scale/evidence/T020_checks_20261010T080419Z/ (files 00-12). The measured numbers in s7 come from
`python -B -m rso.scale.ledger_numbers` (rso/scale/ledger_numbers.py, with a known-answer test in rso/scale/tests/),
which cross-checks itself against `rso.slice001.ledger` usage().

Nothing was restarted or reconfigured, and nothing was spent. No RunPod API was called (s6.0).

---------------------------------------------------------------------------------------------------------------------

## 0. Answers first

**Directive s17 Q5. How would we run a seven-day experiment without depending on an agent session staying alive?**

The answer is not available today as a working path. It is available as a design built from parts that already
exist, and most of the missing coordination layer is already being built by Themis in C-012. The rule is that the
job, not the conversation, owns four things:
- an immutable manifest;
- a chain of checkpoint records published to PostgreSQL on M1, with expected-parent compare-and-set;
- an append-only event and attempt ledger;
- checkpoint bytes in a retained store, verified by sha256.

Workers are interchangeable processes that hold canonical Fabric leases. Any worker or seat can resume the chain from
its last PUBLISHED checkpoint, after first verifying the bytes and a short resume-equivalence replay. An agent
session appears in exactly two places: freezing the manifest at the start, and reading the final account at the end.
Everything else is mechanical (s3).

Three things are missing before this works:
- **A live worker plane.** Today there are zero live Fabric workers (CHECK 01). The PrometheusWorker fleet has run
  one packet ever (CHECK 07).
- **A retained artifact store reachable from the Ubuntu nodes.** None exists. Fabric blobs are capped at 16 MB
  (fabric/store.py:34), and Pan's lake is M2-local (pan/config.json:10-21).
- **A save_state/load_state pair in the engine being run.** Only Aether's kernel, prometheus z80atlas (via pickle)
  and Proteus can checkpoint today without engine edits (rso/scale/CHECKPOINT_REPLAY_SURVEY.md s2.1, Cadmus).

**Directive s17 Q6. When would renting computation improve our chance of discovering a new mechanism?**

Only when all three of these hold:
- the workload is measured locally as GPU-shaped (batched, vectorised, little transfer);
- the experiment has earned a 4x/16x budget under a registered rule (directive s12);
- the local fleet cannot deliver that budget within the scientific deadline.

None of the C-004, C-009 or C-010 workloads meets the first condition. Together they ledgered 111.2 CPU-minutes and
0 GPU-seconds (s7). The cloud path is therefore a capability to qualify cheaply now (s6), not a throughput lever to
pull. The binding costs are qualification and coordination, not compute. Palamedes reaches the same conclusion
independently in rso/scale/RSO_SCALING_ASSESSMENT.md s0.

**What the ruling's five states show, in one line each (full table in s1):**
- Leases, custody and the Fabric store are verified operational now.
- The Fabric queue is degraded: implemented and tested historically, with 0 live workers.
- PrometheusWorker is implemented and tested once, but its current operation could not be verified from harry1.
- The RunPod controller is implemented and tested historically (43 receipts, every created pod observed absent).
  Its pod-side termination and billing hard cap are designed but unimplemented.
- A general checkpoint/resume facility, a large-object store and a dollar ledger are designed but unimplemented.

---------------------------------------------------------------------------------------------------------------------

## 1. Five-state inventory

The column headings are the five states from the ruling (OPERATOR RULING s5).
- **IMPL** means the code exists.
- **HIST** means there is a record that it ran successfully before today.
- **NOW** means a read-only check this seat ran today shows it operating. "n/c" means not checked, and the reason is
  given.
- **DEGR** means it exists but is impaired today.
- **DESIGN** means it is described in a document but not implemented.

The ruling says stale worker presence is not evidence of a working queue. It is not counted as NOW anywhere below.

### 1.1 Fabric (owner Odysseus, fabric/README.md:7; frozen at v0.2, fabric/FREEZE.md:9-21)

| Component | IMPL | HIST | NOW | DEGR | DESIGN | Evidence |
|---|---|---|---|---|---|---|
| Store (Postgres schema `fabric` on M1) | Y | Y | **Y** | | | CHECK 01-03 and 10 read the store from harry1 |
| Task queue: claim with SKIP LOCKED, attempts, retries, wall limits | Y | Y: pilot P1-P9 PASS 2026-09-28 (fabric/README.md:170-184; fabric/pilot/evidence/P2-*.json: 50 tasks, 0 duplicate claims) | **N** | **Y** | | `claim()` is at fabric/store.py:356-402. CHECK 02 shows 375 lifetime tasks (302 completed, 45 canceled, 28 failed); the newest update is 2026-10-04 16:01Z; nothing is queued or working |
| Worker presence (`agent_instances`) | Y | Y | **N** | **Y** | | CHECK 01 lists 53 agents, 0 live. Three report status `online` but were last seen 2026-10-02 14:37Z (worker.ubu001.a/.b/.sci). Only `reap()` flips a worker offline (fabric/store.py:546-547), and "With zero workers alive, nothing reaps" (fabric/README.md:222). Known defect DEF-ODY-017 (roles/Odysseus/fabric_pilot/DEFECTS.md:25) |
| Reaper (abandon expired attempts, requeue) | Y | Y: P4, 37.4 s from kill to completion | **N** | **Y** | | `reap()` is at fabric/store.py:528-549. It runs only inside a worker loop (fabric/worker.py:271) or as a manual `fabric reap` |
| Resource leases (`<host>:<res>`, token-fenced, TTL) | Y | Y | **Y** | partial | | CHECK 03 shows 82 leases since 2026-09-28 from 12 holders, 30 of them since 10-08; the newest is Pan, 2026-10-10 07:26Z. One expired lease was never released: `skullport:gpu0`, Ananke, expired 2026-10-07 21:39Z. Expiry is lazy (fabric/store.py:266); this blocks nothing but misleads a reader |
| Blobs (sha256 content-addressed, 16 MB cap) | Y | Y | **Y** | | | CHECK 11 fetched art-8509eb89c369 and re-hashed it: sha256 3a362c3f... and 1884 bytes both match. The cap is at fabric/store.py:34. `artifacts.uri` for external content is in the schema, with no external store (fabric/schema.sql:93-113) |
| Events (append-only by convention, no trigger) | Y | Y | Y (read) | | | fabric/schema.sql:133-145; `_event()` only inserts (fabric/store.py:124) |
| Cancellation | Y | Y | n/c (would mutate) | | | fabric/store.py:241-262 |
| Checkpoint/resume | N | | | | partial | Every retry starts from scratch. No schema field. The `input-required` continuation is A2A multi-turn, not a checkpoint (fabric/store.py:567-586) |
| A2A gateway | Y | Y: TCK MUST 68/0 (fabric/README.md:184) | n/c (not started) | | | fabric/gateway.py |
| promexec broker | Y | positive control only | N | | | "EXPERIMENTAL / UNVERIFIED / NOT ENABLED" (fabric/promexec/STATUS_EXPERIMENTAL.md:1-3). MWO-0004 G4 keeps it off |

### 1.2 Workers

| Component | IMPL | HIST | NOW | DEGR | DESIGN | Evidence |
|---|---|---|---|---|---|---|
| ubu001-006 hosts (2C-4C, 8-22 GB, no GPU; infra/FLEET_HOSTS.md:36-41) | Y | Y | **Y (network only)** | | | CHECK 05: all six answer ICMP from harry1. SSH from harry1 is not authorised (publickey), so service state was not read. This check also added the six host keys to harry1's known_hosts |
| Fabric v0.2 workers on ubu nodes | Y | Y (pilot) | **N** | **Y** | | CHECK 01; no systemd unit; started by hand (fabric/FREEZE.md:35-41). ops/fleet/M1_DRAIN_2026-10-03/P2B_INTAKE.md:112-119 records 28 Aether tasks cancelled unclaimed |
| PrometheusWorker (workgraph push-claim; systemd user unit with Restart=on-failure) | Y | Y, once: C-005-T001 DONE_CLEAN on ubu002, 15.4 s (ops/campaigns/C-005/tasks/C-005-T001/attempts/A-20261003T102428Z-ubu002-svc-9513e7/RECEIPT.json) | **n/c** | unknown | | It was installed "enabled, active" on ubu001-006 on 2026-10-03 (infra/ubuntu_nodes/ubuntu_server_machines.md:183-190). It registers no presence anywhere this seat can read. Comms `who` shows only interactive seats on ubu nodes (CHECK 06). It is a git CAS worker; its lease is a LEASE.json with no TTL (workgraph/core.py:482-506) and its preemption replays from the start (workgraph/worker.py:249-253). Exactly 1 GENERIC_WORKER packet has ever been issued (CHECK 07). Minimum check: `journalctl --user -u prometheus-worker -n 5` on any ubu node, run by an account with access |
| Windows hosts as Fabric workers | N | | | | | "No Windows host runs a Fabric worker (DEF-ODY-012)" (infra/FLEET_HOSTS.md:27). Host-affine work runs natively under MWO-0004 R3 |

### 1.3 Ledgers, custody, accounting

| Component | IMPL | HIST | NOW | DEGR | DESIGN | Evidence |
|---|---|---|---|---|---|---|
| RSO attempted-run ledger (START/END/REFUSED JSONL, fsync, charges failures and children, INTERRUPTED is unmetered, never zero) | Y | Y: C-004, C-009, C-010 | **Y** (all three stores parse; usage matches; s7) | | | rso/slice001/ledger.py:7-30, 133-137, 201-203. It is single-writer with no lock ("Concurrent top-level launches ... could both pass the check", :35-36), has no hash chain, and re-reads O(N) per `begin()` (:243, :248). It is not a multi-host ledger |
| Run-bundle driver (MANIFEST written last as the commit point; CAS artifacts verified before write; seed refusals before any ledger row) | Y | Y: C-010 | n/c (would launch) | | | rso/witness/run_witness.py:9-14, 189-259, 287-320, 348-406 |
| Custody registry (hash-chained, trigger-computed, UPDATE/DELETE refused) | Y | Y | **Y** | | | CHECK 04: `verify` returns chain_ok, 67 rows, head 65fb3a97..., rc 0. Tampering is detected, not prevented, because every seat is a shared superuser (ops/custody/schema.sql:11-13) |
| Moonshot attempt receipts (every attempt charged, including discarded retries) | Y (C-008, git transport) | Y (C-008 T001/T002/T005) | | | Y (PG transport, C-012) | moonshot/epoch/CONTRACT.md:151-158 |
| Dollar ledger (fleet-wide) | **N** | | | | Y (fragments) | The RSO contracts declare `cloud_usd: 0` and `gpu_hours`, and the ledger never enforces them (rso/slice001/ledger.py:88-93; rso/witness/contract.json:11-17). RunPod receipts carry estimates only. archaeon cost events record physical units, not USD (archaeon/producer/costs.py:1-21) |
| Postgres backups of M1 (whole-database pg_dump daily to M2, weekly restore-verify) | Y | Y | n/c | | | evidence_wiki/docs/BACKUP_AND_RESTORE.md:18-51. The M1-side jobs are "UNOBSERVABLE from M2" (:52-56). RPO is about 24 h for all coordination state |

### 1.4 RunPod (Aether/runpod/; zero-spend ruling s7)

| Component | IMPL | HIST | NOW | DEGR | DESIGN | Evidence |
|---|---|---|---|---|---|---|
| Controller: `flight.py --go`, inventory refusal, create-with-reconcile | Y | Y: 43 run receipts 2026-09-24..10-05; 35 pods created (CHECK 12) | n/c (no API call; s6.0) | | | Aether/runpod/prometheus_gpu/launch.py:532-549 (refuses if any pod exists or the listing fails), :552-646; provider.py:392-501 |
| Termination in `finally` plus an independent absence check (LIST omits and GET empty) | Y | Y: 35 of 35 created pods `observed_absent` (CHECK 12) | n/c | | | launch.py:24-25, 644-646, 1403-1487 |
| Pod-side self-termination / max-lifetime / idle kill | **N** | | | | Y | Bootstrap holds the pod open: "The controller's teardown ends it" (prometheus_gpu/dryrun.py:371-373). A SIGKILLed controller leaves the pod billing (flight.py:337-341). aeth01_canary/README.md:281-282 says "The pod continues billing until externally terminated" |
| Independent cleanup-only reaper | Y | local tests only | N | | | aeth01_canary/independent_reaper.py:1-30; never deployed |
| Resume (re-attach to a live pod named in the ledger; never creates) | Y | Y: used twice, controller absent 47.6 s and 122.5 s (CHECK 12) | n/c | | | launch.py:668-767 |
| Checkpoint off the pod (network volume / object store) | **N** | | | | | Artifacts return over HTTP before terminate and are sha-checked against the pod manifest (launch.py:1296-1372). Some workloads wrote `ckpt.bin` as an artifact (CHECK 12), so the checkpoint is lost with the pod if retrieval fails (several FAILED or ABORTED receipts list `ckpt.bin` missing) |
| Budget control | Y (client-side estimate) | Y: BUDGET_CEILING fired once (CHECK 12) | | **Y as a guarantee** | | `spend = elapsed/3600*hourly` (launch.py:1148-1154). The ruling says this "does not constitute a hard spending guarantee" (s7) |
| Billing readback and reconciliation | Y (manual, separate) | Y, twice on 2026-09-27 | n/c | **Y** | | Aether/runpod/prometheus_gpu/billing.py:4-7, 45-71. 0 of 43 receipts are `billing_reconciled` (CHECK 12). The i5 reconciliation shows **$5.025 billed to pods with no receipt**, against $1.017 matched (Aether/runpod/receipts/i5_billing_reconciliation_2026-09-27.json, `totals`); nobody has explained it |
| Account cap | | | **unverified** | | | `spendLimit: 80` and clientBalance $13.14-13.89 are readings from 2026-09-27 (same files, `account`). The ruling says to treat both as unverified (s7) |

Historical totals from CHECK 12: 5.87 GPU-hours of wall clock, $2.07 estimated. GPUs used: L4 10, A5000 8, RTX 4090 5,
A4000 4, A40 4, 4000 Ada 2, A6000 1, 2000 Ada 1.

**Correction to source digest 3** (roles/Palamedes/notes/2026-10-10_strategic_sources/03_PHASE3_AND_INFRA_DIGEST.md:37):
- There are 43 run receipts from 2026-09-24, not ">60" from 09-22.
- "billed ~1.004x estimate" holds for individual L4 pods only. The fleet-level reconciliations disagree:
  - block file: $0.560 billed and matched, against $1.590 in receipt estimates;
  - i5 file: $1.017 matched against $0.844 estimated, plus $5.025 unmatched.

### 1.5 GPUs

| Host | GPU | NOW | Evidence |
|---|---|---|---|
| M1 SKULLPORT | RTX 5060 Ti 16 GB (infra/FLEET_HOSTS.md:17) | n/c directly | Lease `skullport:gpu0` was used through 2026-10-07 (CHECK 03), and one stale lease is still unreleased |
| M2 SPECTREX5 | RTX 5060 Ti 16 GB (:18) | n/c directly | `spectrex5:gpu0` was leased 11 times; the latest is Pan, 2026-10-09 22:15Z, gemma3:12b (CHECK 03) |
| M3 GANDALF | GTX 1070 8 GB, no AVX (:19) | n/c | seats only |
| M4 harry1 | Quadro P500 2 GB | **Y** (CHECK 08: nvidia-smi, 0% util, 53 C) | Not a compute GPU. harry1 is thermally limited (ruling s1) |
| ubu001-006 | none | | infra/FLEET_HOSTS.md:36-41 |

### 1.6 Artifact stores

| Store | IMPL | HIST | NOW | Limit | Fit for long runs |
|---|---|---|---|---|---|
| Git (manifests, hashes, receipts, small bundles) | Y | Y | Y | Repo size, not bytes | Authoritative small records only (directive s9) |
| Fabric blobs (Postgres BYTEA) | Y | Y | **Y** (CHECK 11) | 16 MB per object | Small checkpoints only, and it competes with the shared M1 database |
| RunPod out-of-repo dir `Prometheus-data/runpod_artifacts/` (Aether/runpod/flight.py:72-77, 248-261) | Y | Y | n/c (absent on harry1) | host-local | Not shared |
| Pan Parquet/Iceberg lake (catalog in M1 `pan_iceberg`, data on M2 NVMe; pan/iceberg.py:1-47, pan/config.json:10-21) | Y | Y | **Y** (CHECK 09: Pan jobs OK through 2026-10-10 07:23Z) | Pan self-caps 10 GB on M1 (roles/Pan/docs/DATA_ARCHITECTURE.md:194-198). Lake location is an open question, Q-003 (:193) | Analytics, not authority (OP-NF2 :117-123: "Do not assume M2-local Iceberg files are available to the Ubuntu nodes") |
| Large retained object store (MinIO, NAS, S3) | **N** | | | | **The gap**: the directive asks for this (s9) and nothing provides it |

### 1.7 C-012 (Themis, OP-NF2): designed, in flight, not duplicated here

As of origin/main 3ba021d5f, nothing in C-012 is implemented: `moonshot/nf/` does not exist. T001 (interface
contract) and T002 (PG publication) are CLAIMED by Themis[m2-0e9b1ed2]. T003-T006 are READY
(ops/campaigns/C-012/tasks/*/TASK.json). The semantics carried over from C-008 are implemented, with a git
transport, in moonshot/epoch/:
- `work_id = H(input_ckpt, spec, runtime)` and `epoch_digest = H(work_id, trace, output_ckpt)` (CONTRACT.md:28-31);
- PUBLISHED is not VALIDATED (:115-124);
- "The first writer never wins silently" (:126-141);
- every attempt is charged (:151-158).

---------------------------------------------------------------------------------------------------------------------

## 2. The five target workloads, assessed (directive s13-C)

| Workload | Works today | What breaks first | Smallest step that fixes it |
|---|---|---|---|
| **72-hour experiment** | Natively on one host, with a canonical lease (MWO-0004 R3) and an engine that resumes per job (Ares sweep, Ananke campaign cell, z80atlas scheduler; CHECKPOINT_REPLAY_SURVEY.md s1). This is how Ananke's 72 h push ran on M1 (lease, CHECK 03) | The session that launched it. Nothing restarts a dead process, and a lease with no renewer expires silently and stays unreleased (the stale `skullport:gpu0`). The RSO ledger's INTERRUPTED rows make lost work visible but not recoverable | A host-local supervisor outside any agent session (Windows Task Scheduler or a systemd user unit) that runs the s3 runner loop. Checkpoints go to a retained path. The lease is renewed by the runner, not by the seat |
| **Week-long checkpointed** | No | No shared checkpoint store; seven days spans machine reboots and seat turnover; a 24 h backup RPO on M1 | s3 in full: epoch chain via C-012, artifact store (s3.6), engine save/load (Cadmus tier C) |
| **Interrupted cloud execution** | Partly: the controller's resume re-attaches to a *live* pod (launch.py:668) | Pod loss loses its state (no off-pod checkpoint). Controller death leaves the pod billing | Ship checkpoints off-pod at every epoch; pod-side deadline self-termination; an independent reaper on another host (s6) |
| **Many concurrent cheap searches** | Locally: per-host process pools under a lease (Pan and Archaeon run 4-12 processes on M2, CHECK 03) | The fleet queue: 0 live Fabric workers. PrometheusWorker is git-CAS, polls every 15 s to 5 min, and has a TTL-less lease. The RSO ledger is single-writer with an O(N) begin | Run seed partitions as Fabric tasks once workers are live (owner: Odysseus; C-012-T004 benchmarks it). Each partition writes its own ledger shard, merged at final accounting (s3.7) |
| **Selective GPU acceleration** | Local M1/M2 GPUs through leases. RunPod is qualified as a controller, but paid runs are not allowed (MWO-0004 G4) | No RSO workload is GPU-shaped yet (s7). The cloud termination guarantee is client-side only | Stage 2 of the escalation ladder (directive s4) on M1/M2 first. The cloud canary in s6 qualifies termination and recovery, not throughput |

---------------------------------------------------------------------------------------------------------------------

## 3. The durable execution model (design; builds on C-012, does not replace Fabric)

### 3.0 Division of authority

Each layer reuses something that already exists. No new queue, no new lease authority and no new transport are
introduced; OP-NF2 forbids all three (roles/Themis/prompts/2026-10-10_op_nf2/01_OPERATOR_OP-NF2_verbatim.md:22-26, :106).

    Git                    immutable RunManifest + EnvironmentSpec + final account + result hashes   (authoritative, small)
    PostgreSQL on M1       Fabric: tasks, attempts, leases, heartbeats, retries        (Odysseus; frozen v0.2)
                           Moonshot NF: epoch identity, chain publication, outcomes   (Themis; C-012-T001/T002)
                           Observatory: progress events + run ledger rows            (this design; thin)
    Retained object store  checkpoint and raw-evidence bytes, addressed by sha256    (MISSING; s3.6)
    Pan lake               analytical copies only; never gates publication          (C-012-T005)

The Observatory contributes three things:
- a manifest layer above Moonshot epochs;
- an accounting layer that carries RSO ledger semantics across many workers;
- the resume-verification rule.

Everything else it consumes.

### 3.1 Immutable RunManifest (frozen before the first attempt; lives in Git)

    run_manifest/1 {
      question_ref        path@sha of the preregistration (frozen scientific question; directive s4 Stage 5)
      engine              {repo_path, code_sha, entry, adapter_tier: R|C}        (s3.4)
      environment         EnvironmentSpec (s3.2)
      partitions          [SeedPartition] (s3.3)
      epoch_budget        counter-denominated (ticks/generations/evaluations), never wall clock
                          (CHECKPOINT_REPLAY_SURVEY.md finding 5)
      checkpoint_every    counter interval; sets the maximum work lost per failure
      stop_rules          registered plateau / failure / escalation criteria (directive s12)
      caps                cpu_core_h, gpu_h, artifact_bytes, cloud_usd (all enforced; s3.7)
      canonical_digest    the declared canonical subset hashed for replay equality (survey finding 6)
    }
    manifest_id = sha256(canonical JSON)

A change to anything listed here produces a new manifest_id. A new manifest is a new run, never an edit to the old
one. This is the scientific freeze. The execution layer may change where and when an epoch runs, never what it
computes.

### 3.2 EnvironmentSpec (reproducible environments)

`{code_sha, interpreter + version, lockfile sha256 (or container image digest for cloud), required capability probe}`.

Workers resolve dependencies by capability, not by name (base RESPONSIBILITIES, "Verify the property"). Before it
claims anything, a worker runs the manifest's capability probe; `fabric worker --probe` is the existing hook
(fabric/__main__.py:90-91). For example, Cadmus could not run Ananke, Tyche or wm_mini on harry1 because torch,
sklearn and numba were absent (survey, header). A probe makes such a host ineligible instead of letting it fail
mid-run.

### 3.3 SeedPartition (independent seed partitions)

A partition is `{partition_id, seed list or range, epoch count}`. Partitions share no mutable state, so they are the
unit of scale-out. Seed hygiene is the run driver's existing pre-ledger refusal (rso/witness/run_witness.py:189-259),
applied per partition: no duplicate seeds, no seeds below the floor, none from evaluation sets. Each partition is a
separate checkpoint chain.

### 3.4 Engine adapter tiers (from Cadmus's survey, s2 finding 4)

- **Tier R, replay-from-seed.** Allowed only when one epoch runs shorter than the checkpoint interval. A
  "checkpoint" is then `(seed, counter)`, and resuming means re-running from the seed.
- **Tier C, save_state/load_state.** The engine owner owns this pair, never the adapter (native runtimes keep their
  own state; rso-builder-role s2.1). The returned bytes must include every RNG state (survey finding 3). This tier is
  required for any run whose epoch is longer than about one hour, or whose manifest asks for Stage 4/5.

Engines that are tier C today without edits: the Aether kernel, prometheus z80atlas (pickle), Proteus (if the caller
saves its rng), and Ananke World (in memory; it needs a file wrapper).

### 3.5 CheckpointRecord = a Moonshot epoch (do not duplicate)

A checkpoint segment is exactly C-008/C-012's epoch: `work_id = H(input_ckpt, spec, runtime)`, output `output_ckpt`
and `epoch_digest`. The Observatory adds no second record type. It needs the following from the C-012 contract (s5
lists these as asks):
- **expected-parent plus chain-generation CAS.** A stale or zombie worker cannot advance the chain. This is already
  OP-NF2 :90-100.
- **output_ckpt carried by reference.** `{store_uri, sha256, bytes}`, so checkpoints larger than 16 MB never pass
  through Postgres.
- **Outcomes PUBLISHED / DUPLICATE / CONTESTED / STALE / INVALID kept separate from VALIDATED.** A resumed chain
  counts as scientific evidence only after the verification in s3.8.

### 3.6 Remote retained artifact store (missing; the one new component)

Requirements:
- content-addressed by sha256;
- write-once;
- readable from the ubu nodes, M1, M2 and (over a tunnel) a cloud pod;
- survives the loss of any single worker;
- has a retention policy and a byte cap per run;
- verified on read.

Today nothing meets all of these. Fabric blobs meet everything except size and placement: they are 16 MB and live
inside the shared database.

Recommendation, recorded as a reversible field choice (FD-2 in s9): a plain sha256-addressed directory tree on M1's
data disk, served read-only over HTTP on the LAN, with writes through an append-only upload endpoint that refuses an
existing key with different bytes. It sits beside, not inside, Postgres. The `artifacts.uri` column already exists
for this (fabric/schema.sql:93-113).

The owner should be the infrastructure owner, not this seat. The placement question is the same open question as
Pan's Q-003. It goes to Palamedes as a NEW-packet proposal and is not built here (rso-builder-role s8.7).

### 3.7 Append-only progress events and final accounting

- **Progress events.** Each epoch attempt writes START and END (or nothing, which then reads as INTERRUPTED) with
  the RSO ledger's semantics (rso/slice001/ledger.py:7-30):
  - every attempt is charged, including failures, retries, discarded duplicates and mutation children;
  - INTERRUPTED is unmetered and never counted as zero.

  The current file ledger is single-writer and unlocked (:35-36), so for many workers there are two options:
  - (a) each partition writes its own JSONL shard, and they are merged at accounting time;
  - (b) the rows go into the C-012 attempt-receipt table, which is "durable and separate from canonical scientific
    traces" (OP-NF2 :90-100).

  (b) is preferred once T002 lands. (a) works today (FD-3).
- **Caps enforced, not declared.** `gpu_hours` and `cloud_usd` must become enforced caps. Today `Caps.from_dict`
  reads only launches, CPU and bytes (ledger.py:88-93).
- **Final account** (Git, written once):
  - per resource: CPU core-s, GPU-s, peak/avg RSS, artifact bytes retained, network bytes, cloud $ estimated, cloud
    $ billed-reconciled (two fields that are never merged);
  - per outcome class: productive epochs, retried, duplicate, contested, interrupted;
  - **wasted work**: compute on epochs that never published, which is the price of worker loss.

  This is the directive s10 cost model in machine form. The discovery/proof split comes from tagging each launch by
  ladder stage (directive s8).

### 3.8 Verified resumption

Resuming from checkpoint k is accepted only if all four of these pass:
- (1) The checkpoint bytes re-hash to the published sha256.
- (2) The engine's `load_state` followed by `save_state` round-trips to identical bytes.
- (3) On a sampled fraction of resumptions, which is a manifest parameter (default 1 in 10 plus the first), the
  worker also restores checkpoint k-1, replays one epoch, and requires the `epoch_digest` to match checkpoint k's
  published digest. This is the split-run equality Cadmus verified for Aether and z80atlas (survey s3).
- (4) The worker's EnvironmentSpec probe matches.

A failure of (1), (2) or (4) is INVALID. A failure of (3) is CONTESTED and halts the chain, because disagreements
fail closed (CONTRACT.md:126-141). Tier R engines satisfy (3) automatically by replaying from the seed.

### 3.9 Failure semantics

| Event | What happens | Work lost |
|---|---|---|
| Worker loss (process, host, Wi-Fi) | Attempt heartbeat stops. The lease expires at its TTL (default 90 s, fabric/__main__.py:81). Any live worker's reaper requeues the task (fabric/store.py:528-549). The next worker resumes from the last PUBLISHED checkpoint | At most one checkpoint interval, charged as wasted |
| Zombie worker returns late | Its finish is fenced (`late_finish_rejected`, fabric/store.py:511-517). Its publication fails the expected-parent CAS and is classified STALE (OP-NF2 :90-100) | none |
| Scheduler restart | Fabric has no central scheduler process. State lives entirely in Postgres, and workers are stateless loops, so a restart is a no-op. **Defect**: reaping happens only inside live workers, so a fleet with zero workers never reaps or corrects presence (fabric/README.md:222; CHECK 01). Reported to the owner, not redesigned (s8) | none, but lost visibility |
| M1 Postgres down | Every worker stalls: no claims, no publication. Running epochs finish but cannot publish, and they retry publication. If M1 is lost, coordination state rolls back to the last daily dump (evidence_wiki/docs/BACKUP_AND_RESTORE.md:43-51), and work published since then must be re-verified from Git manifests plus store hashes | up to about 24 h of publication records; the checkpoint bytes survive if the store is not on M1's same disk |
| Agent session ends | Nothing. No execution state lives in a conversation | none |
| Cloud pod lost | Treated as worker loss. The checkpoint is off-pod (s6), so nothing is lost beyond the interval | interval plus $ |

### 3.10 Scale-out and scale-up, evaluated separately (directive s9)

- **Scale-out** means many independent partitions on cheap CPUs: ubu001-006 have 14 cores in total (2C, 2C, 2C, 2C,
  4C, 2C), plus M2's 20C under leases. Its costs are coordination (claim latency, publication round trips) and
  storage growth, and C-012-T004 measures exactly those. The measure to ask for is useful evaluations per hour per
  core and the coordination share. Until T004 reports, scale-out gains are not asserted.
- **Scale-up** means few, intensive accelerator jobs: M1/M2 RTX 5060 Ti, then rented. Its costs are batch shape,
  host-device transfer and checkpoint size. Survey: Aether is 5*H*W bytes, about 20 MiB at 2048^2. The measure is
  throughput per GPU-hour against the same work on M2's CPU, measured on M1/M2 before any rental (directive s4
  Stage 2).
- The two share the manifest, the checkpoint chain and the accounting. They differ only in the worker capability
  string and the partition size.

---------------------------------------------------------------------------------------------------------------------

## 4. Smallest next investment (Workstream C's recommendation to Workstream D)

One packet: **a session-independent local runner for one tier-C engine.** The Aether kernel is the first choice
because Cadmus ranks it first with adapter cost S, and its split-run equality is already verified. The runner covers
s3.1-s3.8 on one host:
- manifest;
- partitions as subprocesses under a canonical lease;
- epoch checkpoints to a sha-addressed local directory (the s3.6 layout, without the network part);
- sharded ledger;
- resume with the s3.8 checks;
- a final account.

It is driven by a host supervisor, not a seat. Acceptance is a fire test:
- kill the worker mid-epoch;
- kill the supervisor;
- end the launching session;
- show that the run completes with an identical final canonical digest to an uninterrupted control;
- show that the wasted work is accounted for.

The runner moves to Fabric/C-012 transport when T002/T003 land, with no change to the manifest or checkpoint
formats. That is the reason to keep the formats aligned with C-012 now.

Estimated cost: well inside MWO-0004 R2 (under 1 core-hour of execution) plus Q2 engineering. It removes the
dependency the scaling assessment names as B2 ("the job owns its state", RSO_SCALING_ASSESSMENT.md s7).

---------------------------------------------------------------------------------------------------------------------

## 5. What the Observatory needs from C-012 (to Themis, through Palamedes; not a demand on its schedule)

- N1. The checkpoint reference fields `{uri, sha256, bytes}` on the epoch output, so checkpoints never have to fit
  in Postgres (s3.5).
- N2. Attempt receipts with the RSO ledger's charging semantics: failures, retries and discarded duplicates are
  charged, and an unfinished attempt is "unmetered", never zero. CONTRACT.md:151-158 already says so for C-008; ask
  that the PG schema keep it.
- N3. A read path that lets an Observatory final account sum attempts by run/manifest_id, which means a manifest_id
  (or an opaque tag) column on the attempt or epoch.
- N4. In the T004 benchmark, report the coordination share separately from execution (OP-NF2 :156-162 already
  requires this), plus the wasted-work fraction under induced worker loss. Those are the two numbers s3.10 and the
  cost model need.
- N5. Confirmation that VALIDATED can be granted by a replay policy that includes the s3.8(3) sampled
  resume-equivalence check.

---------------------------------------------------------------------------------------------------------------------

## 6. Zero-spend GPU canary proposal (RunPod)

### 6.0 Authority and what this section is not

The OPERATOR RULING s7 authorises zero spend. MWO-0004 G4 says "No RunPod or other paid compute"
(ops/work_orders/CURRENT.md:199-201). This section is a proposal only. During this window this seat did not call
the RunPod API at all, not even read-only. The ruling authorises inspecting "existing code, receipts, and historical
cost records", and an account query is outside that list (FD-1).

Executing the paid phase (6.3) needs all of the following:
- an explicit operator approval naming a dollar cap;
- an MWO that lifts G4 for this item;
- the hard-cap precondition in 6.2(e) verified.

### 6.1 What the canary qualifies

The canary qualifies the five properties the ruling names: reliable termination, recovery from worker failure,
artifact preservation, cost accounting, and independently verifiable shutdown. Plus one property this architecture
needs: off-pod checkpoint resumption.

It does **not** qualify throughput or scientific value. Neither is a reason to rent until s0 Q6 holds.

### 6.2 Design

- **Workload.** The Aether kernel (`Aether/test/reference/gpu_aeth01.py`). Its state is 5 uint8 fields plus seed
  plus tick, it has resume parameters (`Aether/observatory/aeth01_run.py:118`, `start_tick`), and Cadmus verified
  split-run digest equality on CPU (survey s3). One small grid, a counter budget of N ticks, and a checkpoint every
  N/4 ticks. The CuPy/GPU path is unchecked (survey s4 rank 1), so step 6.3-0 checks it locally first.
- **(a) Termination, three independent layers.** Any single layer must suffice.
  - 1. The controller's existing `finally` terminate, followed by the LIST+GET absence check (launch.py:644-646,
    1403-1487).
  - 2. **New: pod-side deadline.** The bootstrap wraps the module in `timeout <T_max>`, and after it (or on any
    exit) the pod deletes itself through the provider API using a pod-scoped credential. This replaces the
    current "hold the pod open" (dryrun.py:371-373). UNVERIFIED: whether RunPod's stock image exposes the pod id
    and a usable CLI. This must be shown in a $0 dry-run of the bootstrap text and then, at the first paid minute,
    observed.
  - 3. **The independent reaper** (aeth01_canary/independent_reaper.py) runs on a *different host* from the
    controller (M1). It holds only list and terminate permissions, and it terminates any pod whose name matches the
    run prefix and has passed `T_max + grace`.
- **(b) Worker-failure recovery.** Fault injection is part of the protocol. At checkpoint 2 the controller kills the
  module process inside the pod, then terminates the pod. A *new* pod resumes from the off-pod checkpoint 2. The
  acceptance condition is that the final digest equals the uninterrupted CPU control's digest (s3.8(3)).
- **(c) Artifact preservation.** Every checkpoint and the result are pulled through the existing sha-verified
  artifact path (launch.py:1296-1372) at each checkpoint, not only at the end. This works because the controller
  already polls during the run (launch.py:1261-1277). The kept copies go to the s3.6 store, or to the existing
  `Prometheus-data/runpod_artifacts/` until that store exists. A pod lost after checkpoint k loses nothing before k.
- **(d) Cost accounting.** The receipt's estimate stays as it is. The new requirement is `cli.py billing`
  readback for the run window, written as a reconciliation that must show **billed_unmatched = $0** and
  billed_matched within 1.25x of the estimate. Any unmatched billing fails the canary, given the unexplained $5.025
  in the i5 reconciliation. Both numbers go to the s3.7 final account as separate fields.
- **(e) Hard cap precondition, checked by the operator, not by code.** The client-side budget is not a cap (ruling
  s7). The operator verifies, in the RunPod console, an account-level limit at or below the canary cap, or a
  prepaid balance at or below it. The operator records the observed value and time in the approval. The repository
  value `spendLimit: 80` does not satisfy this.
- **(f) Independently verifiable shutdown.** After `T_end` a different host from the controller (M1, through the
  reaper's read path) records three readings:
  - LIST shows no pod with the run prefix;
  - GraphQL `currentSpendPerHr == 0`;
  - 15 minutes later, the billing endpoint shows no charge accruing after T_end.

  All three go into the receipt as `absence_evidence_independent`.

### 6.3 Phases and caps

| Phase | Cost | What | Exit |
|---|---|---|---|
| 6.3-0 local | $0 | Run the Aether kernel's GPU path on M1 or M2 under a lease (Stage 2). Measure ticks/s against M2's CPU and the checkpoint size | GPU digest equals CPU digest; throughput recorded |
| 6.3-1 rehearse | $0 | `prometheus_gpu/cli.py rehearse` (fake provider; cli.py:147-188), extended with the three fault injections (module kill, controller SIGKILL, pod vanish) and the three termination layers | All six behaviours observed in the fake-provider receipt |
| 6.3-2 paid canary | **cap $1.00; T_max 20 min; one pod; cheapest available GPU from the history (L4 or A4000)** | 6.2 end to end, with exactly one induced failure and one resume onto a second pod | All of 6.2(a)-(f) pass; otherwise STOP, keep the receipts, no retry without a new approval |

The cap of $1.00 is under the existing Aether canary sub-cap of $3 (Aether/AETHER_RUNPOD.md:8-11; aeth01_canary/README.md:233).
Historical canary-class runs cost cents (CHECK 12: $2.07 over 43 receipts), so $1 is ample. It is a cap, not a
forecast.

### 6.4 What would justify renting after the canary

Rental is justified only when both of these hold:
- an experiment that has earned a 4x budget under its registered rule shows, in 6.3-0-style measurement, GPU
  throughput at least 10x per dollar over M2 CPU for that workload;
- local GPU queue time would breach its deadline.

Until then the canary only buys the ability to use RunPod safely. That is what directive s10 asks for ("become able
to use RunPod intelligently").

---------------------------------------------------------------------------------------------------------------------

## 7. Numbers for Workstream A (MEASURED; reproducible)

Command:

    python -B -m rso.scale.ledger_numbers rso/slice001/s2/LEDGER.jsonl rso/binding/LEDGER.jsonl rso/witness/LEDGER.jsonl --json

The C-004 store is rso/slice001/s2/LEDGER.jsonl. It covers S2/S3, S4 and R2 (rso/slice001/S5_FINAL_DISPOSITION.md:97).
Every total matches `rso.slice001.ledger` usage() (crosscheck MATCH on all three).

| | C-004 (slice001/s2) | C-009 (binding) | C-010 (witness) | all three |
|---|---|---|---|---|
| ledger rows | 714 | 318 | 70 | 1,102 |
| top-level launches | 17 | 10 | 8 | 35 |
| receipt-node launches | 312 | 133 | 16 | 461 |
| mutation-child launches | 28 | 17 | 11 | 56 |
| END status | 357 COMPLETED | 158 COMPLETED, **2 INTERRUPTED (unmetered)** | 35 COMPLETED | |
| REFUSED (cap) | 0 | 0 | 0 | 0 |
| CPU-s total | 3,187.2 (53.1 min) | 1,910.2 (31.8 min) | 1,573.7 (26.2 min) | 6,671.1 (111.2 min) |
| of which mutation children (adversarial challenge) | 2,508.0 (**79%**) | 1,728.0 (**90%**) | 849.0 (**54%**) | 5,085.0 (**76%**) |
| of which receipt nodes | 393.5 | 137.2 | 158.5 | 689.2 |
| of which top-level own | 285.7 | 45.0 | 566.1 | 896.8 |
| artifact bytes | 31,780,730 | 13,381,360 | 10,304,724 | 55,466,814 |
| top-level wall time, sum / median / max (s) | 3,231 / 45 / 1,794 | 1,917 / 32.5 / 1,196 | 1,464 / 56.5 / 691 | 6,612 / - / 1,794 |
| ledger span (UTC) | 10-04 17:39 to 10-06 23:38 | 10-07 02:27 to 07:43 | 10-07 11:11 to 14:33 | |
| GPU-s / cloud $ | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

Readings for Workstream A. These are facts from the table, and the interpretation stays Palamedes's.
- They agree with RSO_SCALING_ASSESSMENT.md s1 on launches, CPU and bytes, with no differences to record.
- New: **76% of all ledgered CPU is adversarial mutation testing**, the qualification stage, not the experiments.
  This supports B1 in compute terms as well: the scarce stage is also the CPU-dominant one.
- Top-level wall time (110 min in total) is about equal to CPU time (111 min). Execution is serial and
  single-process, so even these campaigns' compute ran at roughly one core. Wall-clock for whole campaigns (days and
  hours) is therefore almost entirely coordination, which is consistent with assessment s2.
- C-009's 2 INTERRUPTED rows are unmetered attempts. Their CPU is unknown and is not zero (ledger.py:14-15).
- Two other figures for the assessment's resource line: Fabric has 375 tasks in its lifetime (302 completed, 45
  canceled, 28 failed; CHECK 02), and none came from C-004, C-009 or C-010. The defect packet's "completed 12,
  canceled 38" counts were taken with the CLI's default list limit of 50 (CHECK 02b), so they are not lifetime
  totals. The packet's conclusion (0 live workers) is unaffected.

---------------------------------------------------------------------------------------------------------------------

## 8. Defects and observations routed (not fixed here; Fabric is frozen and not this seat's)

- O-1 (to Odysseus, through Palamedes's existing defect packet, roles/Palamedes/comms/2026-10-10_fabric_defect_packet.md).
  CHECK 01 confirms it at 08:04Z: 0 live, 3 stale `online`. An additional point for the owner: reaping exists only
  inside live workers, so a zero-worker fleet cannot self-correct presence. This is also the scheduler-restart gap in
  s3.9.
- O-2 (to Ananke / lease holders, informational). `skullport:gpu0` lease lse-7d61e3584398 held by Ananke expired 2026-10-07
  21:39Z and was never released. Lazy expiry makes it harmless to the next acquirer, but `lease status` readers see
  a holder that is not there.
- O-3 (to Aether, informational). $5.025 billed to pods with no receipt (i5 reconciliation, 2026-09-27) is
  unexplained. It is a precondition item for any future paid canary (s6.2(d)).
- O-4 (to Palamedes). The digest-3 figures ">60 receipts" and "1.004x" are corrected in s1.4.
- O-5 (to Achilles, informational). PrometheusWorker liveness is not observable from any seat without SSH to the
  nodes. It writes no presence row and no heartbeat. Stale or absent presence is not a working queue in either
  direction.
- O-6 (harry1). The CHECK 05 ssh probe added six host keys to harry1's ~/.ssh/known_hosts. This is harmless, and
  recorded for completeness.

---------------------------------------------------------------------------------------------------------------------

## 9. Field decisions (rso-builder-role s2.7)

| # | Uncertainty | Choice | Why reversible | Revisit when |
|---|---|---|---|---|
| FD-1 | Whether a read-only RunPod API query (list pods, balance) is inside "inspect existing code, receipts, and historical cost records" | Not done. Account state is marked unverified | A later query changes nothing already written | The operator authorises account inspection, or approves 6.3-2 |
| FD-2 | Retained-store technology | Sha-addressed directory on M1, LAN HTTP, write-once, via `artifacts.uri` | It is behind a URI, so it can be swapped for MinIO or S3 without changing records | The infra owner or Pan's Q-003 decides placement |
| FD-3 | Multi-writer ledger | Per-partition JSONL shards merged at accounting, until C-012 attempt receipts exist | A shard is a valid single-writer ledger.py store | C-012-T002 lands |
| FD-4 | Resume-verification sampling rate | 1 in 10 plus the first, as a manifest parameter | It is a manifest parameter | Measured cost of the replay check |
| FD-5 | Added files outside the packet's `owns` (rso/scale/ledger_numbers.py, tests, evidence dir) | Added, because a script is the reproducible form of the numbers table (DISTRIBUTED_WORK s2b: leave code, not prose) | They are deletable, and nothing imports them | Palamedes objects at integration |
| FD-6 | Canary cap | $1.00, 20 min, one pod | Proposal only | The operator sets a cap |

---------------------------------------------------------------------------------------------------------------------

## 10. Proposed next dependency-safe packets (for Palamedes to accept, edit or drop)

- P-1 (Q2, Eupalamus or Cadmus). Session-independent local runner for the Aether kernel with the s4 fire test. It
  depends on nothing.
- P-2 (Q1, Eupalamus). Enforce `gpu_hours` and `cloud_usd` caps in rso/slice001/ledger.py `Caps`, with fire tests.
  This is the accounting half of s3.7.
- P-3 (to the infra owner; NEW escalation). The s3.6 retained store: placement decision plus a minimal
  write-once/read-verify service.
- P-4 (Aether lane, $0). Steps 6.3-0 and 6.3-1: the local GPU-path digest check, and rehearse with fault injection
  plus a pod-side deadline in the bootstrap text.
- P-5 (operator). Decide whether to lift MWO-0004 G4 for 6.3-2 only, with a named cap and a verified account limit.
  This is a hard gate (paid spend). It is listed, not requested, here.

Sources not re-derived here: rso/scale/RSO_SCALING_ASSESSMENT.md (Palamedes, Workstream A),
rso/scale/CHECKPOINT_REPLAY_SURVEY.md (Cadmus, C-013-T021), ops/campaigns/C-012/ and
roles/Themis/prompts/2026-10-10_op_nf2/ (Themis, OP-NF2).
