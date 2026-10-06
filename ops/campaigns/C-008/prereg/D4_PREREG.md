# C-008 D4 preregistration -- the git compare-and-swap transport study

Task C-008-T002. Owner: Themis. Authority: OP-LC1 (roles/Themis/prompts/2026-10-06_op_lc1/).
Written and frozen BEFORE any D4 baseline data exists (OP-LC1: "Freeze the D4 bounds before observing the
baseline"). The commit that adds this file, with its MANIFEST, is the freeze; every D4 run receipt must
come after it in git history. A change after any D4 data exists is a NEW preregistration with its own
manifest, never an edit of this one.

## 1. Question

Is git compare-and-swap, on a dedicated remote, an adequate transport for R-EP shard epochs on this
fleet? How do the single-ref layout (workgraph's claim-is-a-push, emulated) and the per-chain-ref layout
compare? Below what epoch duration does each stop being adequate?

The protocol's CORRECTNESS is not in question here: D3 (moonshot/epoch/tests) established it. D4 measures
COST, and checks that correctness survives real hosts and a real network (P4).

## 2. Rig

R1 (primary; reachable at freeze):
- Remote: a disposable bare repository on ubu001 (192.168.1.218; ThinkPad X1 Carbon 5th, i5 7th gen,
  2C/4T, 8 GB, NVMe; Wi-Fi only -- its Ethernet port is down), served by `git daemon
  --enable=receive-pack` on the LAN (git://, unauthenticated, started for each run and stopped after).
  A fresh bare repository per sweep point. ubu001 runs no workers.
- Workers: N = 8 -- SPECTREX5/M2 x6 (Windows 11, i7-14700F, wired) and ubu002 x2 (Ubuntu 26.04, i5 7th
  gen 2C/4T, Wi-Fi). Python 3.14.4 and git 2.53.0 on every host.
- Code: the T001 SHA integrated on main, recorded in each run manifest; remote workers run a `git
  archive` of exactly that SHA; every chain's approved_code_sha is that SHA.
- Coordinator (chain creation, validation, report): M2.

R2 (extension, only if ubu003-006 become reachable from M2 before the run): add ubu003 x2, ubu004 x2,
ubu005 x4, ubu006 x2 (N = 18) as one more operating point under the same bounds, reported separately.
R1 is the primary baseline either way; R2 neither replaces nor rescues it.

## 3. Arms

- A-PC: PER_CHAIN layout (one ref per slot), leases on.
- A-SR: SINGLE_REF layout (one index ref for every slot), leases on.
- At the operating point only: A-PC-NL and A-SR-NL (leases disabled).

## 4. Workload (synthetic.v1; no organisms, no science)

- Chains: C = 2N per run, each with 100000 epochs (never completes; runs are time-bounded), in a fresh
  namespace and a fresh bare repository per sweep point.
- Epoch size: work_iterations = round(D x r), where r = the median synthetic.v1 throughput (iterations
  per second) over the worker hosts, measured once at launch by the calibration command and recorded in
  the run manifest BEFORE the sweep; trace_every = max(1, work_iterations // 16); checkpoint_bytes = 4096.
  D is the nominal epoch duration; measured durations differ by host and are reported.
- Sweep: D in {60, 30, 10, 3, 1} s for A-PC and A-SR. OPERATING POINT: D = 30 s.
- Each point: W = 6 min wall. At the deadline workers start no new attempt and finish the one in flight.
  Receipts are flushed every 10 attempts and at exit; each worker also flushes one WORKER_SUMMARY record
  (its polls and idle coordination, which no attempt receipt carries). Then a validation pass on every
  chain: every epoch byte-verified; every epoch with epoch_index divisible by 10 replay-verified.
- Worker loop: sticky round-robin over the chain list from the worker's own offset; it stays on a chain
  while it publishes and moves on at BUSY, COMPLETE or HALTED; it sleeps 0.5 s after a full round without
  progress.

## 5. Metrics

Computed only from the remote's receipts, the worker summaries and measurements of the point's bare
repository, by the frozen report command. Per (arm, point), with P = PUBLISHED epochs on the lineages at
the end of the run and V = epochs VALIDATED by the validation pass:

- M1 coordination wall fraction = sum(coordination_wall_s) / (sum(coordination_wall_s) + sum(execute_s)),
  over every attempt receipt and worker summary (polls included).
- M2 non-duplicate CAS retries per published epoch = (sum over attempts of max(0, push_attempts_cas - 1)
  + sum of contention_retries) / P. A CAS rejected because the epoch was already published identically
  is a DUPLICATE, not a retry.
- M3 claim latency ratio = p95(claim_s over attempts that executed) / median(execute_s).
- M4 abandonment rate = (attempts ending ABANDONED_RECOVERED or STALE, plus attempts still AMBIGUOUS or
  REMOTE_UNAVAILABLE at the end, plus contention-exhausted attempts) / attempts that executed.
- M5 bytes transferred per published epoch = (sum(bytes_pushed) + sum(bytes_fetched) over receipts and
  summaries) / P; also / V.
- M6 repository growth per published epoch = the point's bare-repository object bytes after the run
  (`git count-objects -v`: size + size-pack, in bytes) / P; also / V; the ref count is reported.
- M7 tripwire projection = M6 x (P / W) x 30 days.
- Descriptive: wasted executions (DUPLICATE share of executed attempts), DISAGREEMENT count, validation
  states, epoch-duration distribution per host, CPU (Linux hosts only).

Limitation, stated now: M5 counts the pack payload git reports in its progress output, not protocol
overhead (ref advertisement, negotiation). M1's coordination time is wall time of git operations.

## 6. Frozen bounds (OP-LC1: retained from the proposal)

At each (arm, point):

| Bound | Metric | Threshold |
|---|---|---|
| B1 | M1 coordination wall fraction | <= 0.05 |
| B2 | M2 non-duplicate CAS retries per published epoch | <= 0.05 (1 per 20) |
| B3 | M3 p95 claim latency / median epoch duration | <= 0.10 |
| B4 | M4 abandonment rate | <= 0.01 |
| B5 | rate-limit responses | = 0 |

Tripwire T1 (operational, not a scientific bound): M7 <= 1 GB per 30 days at the operating point.

Verdict per (arm, point): ADEQUATE iff B1-B5 all hold, else RECONSIDER naming the failed bounds.
Envelope per arm: T* = the smallest swept D at which the arm is ADEQUATE and every larger swept D is
too ("none" if D = 60 s fails).

THE RECONSIDER-TRANSPORT THRESHOLD: git CAS is adequate for the Moonshot work plane iff A-PC is ADEQUATE
at the operating point (D = 30 s) on R1. If it is not, the transport is reconsidered (sharding, a broker,
or another design) before any epoch-distributed science, whatever the other arms show.

## 7. Predictions (precommitted; each can be lost)

- P1: A-PC is ADEQUATE at D = 30 s.
- P2: A-SR is RECONSIDER at D = 30 s, failing B2.
- P3: T*(A-PC) <= 10 s, and T*(A-SR) > T*(A-PC).
- P4: zero DISAGREEMENT and every epoch VALIDATED, in every arm and point.
- P5: at D = 30 s, A-PC-NL wastes more executions than A-PC, and both chains validate.

## 8. Budget and stop rules

- Local, unpaid. Estimate: 12 runs x 6 min x 8 workers = 9.6 CPU core-hours, under MWO-0004 R2 (<= 16 per
  item, <= 48 per seat per rolling 24 h).
- A point stops early, recorded as a DEVIATION and never as a result to tune: a worker host unreachable for
  more than 60 s; free RAM under 10% on any host; or an unrelated task starting on a worker host (noted,
  point finished, flagged).
- A failed bound is a result. A rerun happens only for an execution failure (BLOCKED/INVALID, e.g. a host
  died), with the reason recorded; never because a number looked wrong.

## 9. Not baseline data

Instrument smoke runs that check the report command (temporary local remotes, at most 2 workers, at most 2
minutes) are not D4 data and are excluded. They are journaled.

## 10. The GitHub WAN-semantics arm (task C-008-T004; OP-LC1 #3)

- Remote: a dedicated, disposable, private repository created for this arm under the operator's GitHub
  account. Never the Prometheus repository or its ref namespace (the code's denylist refuses it).
- Credential: a repository-scoped SSH deploy key with write access, created for this arm only, used only
  by processes on M2, with `IdentitiesOnly=yes` and no agent.
- Caps: at most 2 concurrent workers; at most 250 write attempts in total, counted in code (every push
  attempt, failed or not) with a hard stop at 250.
- Stop at once, recording the evidence verbatim, on:
  - throttling: HTTP 429, secondary rate limit or abuse-detection text;
  - authentication spillover: `ssh -T` with the deploy key must greet the dedicated repository, never a
    user account; otherwise stop before any write;
  - interference with unrelated Prometheus work: a push failure or incident reported by any seat during
    the arm, or the arm's process touching any remote other than the dedicated repository.
- Purpose: semantics, not stress. Checks, each PASS/FAIL:
  - G1: refs under refs/moonshot/ are accepted;
  - G2: force-with-lease rejects a stale expectation;
  - G3: two racing workers give exactly one PUBLISHED and one DUPLICATE;
  - G4: an ambiguous push that applied resolves to PUBLISHED, counted once;
  - G5: an ambiguous push that did not apply is resent and publishes;
  - G6: delete-with-lease works (staging cleanup);
  - G7: a 2-worker run of at least 20 epochs validates (every epoch VALIDATED).
  Per-operation latency, bytes per published epoch and write attempts used are reported. B1-B4 are
  reported DESCRIPTIVELY for this arm, not as verdicts: GitHub validates semantics; the LAN carries the
  scaling question.

## 11. Analysis code

`python -m moonshot.epoch report` at the SHA recorded in each run manifest. These definitions govern
where the code disagrees: a disagreement is a defect to fix and report, never a reason to move a bound.
