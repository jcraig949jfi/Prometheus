# Setup receipt -- generic workers, epic priority, operator priority queue (Achilles, 2026-10-03)

Directive: roles/Achilles/prompts/2026-10-03_generic_workers/ (verbatim, MANIFEST). Built from 59dcf0325 on
achilles/generic-workers-2026-10-03 (worktree Prometheus-worktrees/achilles-gw, ELSA, claude-opus-5-5); one
commit fast-forwarded to main (the commit carrying this file). Achilles is not a scheduler or coordinator of this.

## Delivered (s32)
1. roles/generic-worker-role/ (shared role; inherits base-role; registered under INHERITANCE.md Shared roles;
   excluded from the roster by the *-role rule).
2. PrometheusWorker identity `PrometheusWorker/<host>/<instance>` (workgraph.core.is_worker); bootstrap in
   generic-worker-role s2; README pointer "Start PrometheusWorker on this machine".
3. executor_class NAMED_SEAT (default) | GENERIC_WORKER, enforced in `ready` (seats never see generic tasks)
   and `transition CLAIMED` (wrong class refused both ways; claimant must be owner/eligible for named tasks).
4. execution_mode ATOMIC (default) | NATIVE_PARALLEL | SHARDABLE (registered shards/unit/aggregation/
   restart/merge required); generic `execution` block validated (exact SHA, argv, env, inputs, resources,
   timeout, output dir, success criteria, cleanup, preemption policy; NATIVE_CHECKPOINT needs `checkpoint`).
5. Epic bands in EPIC.json: EP-PHASE3 HIGH 300, EP-GLOBAL MEDIUM 200, EP-PHASE2B LOW 100 (SAFETY 400 only for
   EP-GLOBAL safety_critical); effective priority (band, local 0..99, age); local never crosses a band.
6. Overrides only from operator-decided, unexpired PRQ records (task / experiment / campaign target);
   descendants inherit; the rest of the seat does not.
7-8. preemptible/restartable (LOW preemptible by default); strictly-higher-band preemption only;
   workgraph.core.preempt writes PREEMPTED_RESOURCE and requeues the same packet unchanged.
9. ops/operator_queue/ (priority/PRQ-*.json, README, generated PRIORITY_REQUESTS.md); `workgraph prq
   validate|render|decide|notify|template`.
10. Notification events PRIORITY_ELEVATION_REQUESTED / _APPROVED / _DENIED / _EXPIRED as comms posts after the
    durable record (`prq notify` prints the command); a message never elevates.
11. Deterministic Markdown view (`prq render`).
12. Census email: "Operator Priority Requests -- N open" at the top, with decisions since the last digest
    (achilles/census/build.py _operator_queue, render.operator_queue_block). Goes live when the census pinned
    worktree advances to this commit.
13. workgraph/worker.py: deterministic PrometheusWorker (dry-run / once / loop), resource probe, fit,
    priority order, CAS claim, pinned exec worktree, registered argv unchanged, timeout, mid-run
    preemption check, receipt with output hashes, lease release, cleanup; refuses a main worktree.
14. Tests: workgraph/tests/test_generic_workers.py (14, incl. simulations A-D) + amended workgraph tests;
    with shared-role, base-role, census and comms tests: 119 passed, 8 skipped. Real-git smoke test against a
    throwaway local bare repo: claim and result pushed as two commits, INTEGRATION_READY with receipt, lease
    released, run worktree removed, main worktree refused. It found two defects (scratch dir not created;
    lease not released at completion), both fixed and covered.
15. ops/epics/EP-PHASE2B/CADENCE.md (48-hour CWO cycle, close categories, inference economy, protection
    requests); `workgraph cwo-inputs <epic>`; DISTRIBUTED_WORK.md s12-s15; TH-GLOBAL-CONTROL-PLANE under
    EP-GLOBAL (s25).
16. This receipt.

## Completion simulation (s33), run as tests through the real worker code
- A: Nestor's generic ATOMIC LOW run is preempted when a Phase 3 generic task appears -> PREEMPTED_RESOURCE
  receipt, task READY, execution block and experiment unchanged, no verdict; the HIGH task runs next; the
  Nestor packet replays unchanged to DONE_CLEAN; cwo-inputs lists it under replay_unchanged.
- B: Aether's PREEMPTION_PROTECTION request appears in the digest; while REQUESTED (and when forged as
  APPROVED without the operator) the experiment stays LOW; after the operator's decision that experiment's
  tasks are MEDIUM (MEDIUM GLOBAL work can no longer displace it, HIGH still can); Aether's other experiment
  stays LOW; after expiry it is LOW again.
- C: an Argus-owned generic HIGH task runs on a PrometheusWorker to INTEGRATION_READY; owner_role stays Argus;
  receipt says model none, band HIGH, output hashes.
- D: Nestor and Palamedes cannot claim a generic task; a PrometheusWorker cannot claim a named-seat task.

## Compatibility
Additive. Existing packets default to NAMED_SEAT/ATOMIC; C-004 untouched and valid (HIGH band); the five
builders remain EP-PHASE3-only; `priority_class` still accepted, superseded for ordering (s10 note).

## For the operator
- Choose where PrometheusWorkers run (none was started); each needs a linked state worktree (role s2).
- Decide priority requests with `python -m workgraph prq decide <id> APPROVED|DENIED --note ".."`, then commit.
- Census email section goes live when Achilles advances its pinned census worktree (logged, after tests).
