TASK_ID: NEW
BLOCKER: No packet exists for the smallest next Workstream C investment. A seven-day run still depends on an agent session staying alive: no session-independent runner, no shared checkpoint store, 0 live Fabric workers.
EVIDENCE: rso/scale/LONG_DURATION_EXECUTION_ARCHITECTURE.md s0, s2, s4 (branch eupalamus/c-013-t020, C-013-T020 INTEGRATION_READY); rso/scale/CHECKPOINT_REPLAY_SURVEY.md s4 rank 1 (Aether kernel, adapter cost S, split-run equality verified); RSO_SCALING_ASSESSMENT.md s7 B2.
OPTIONS:
  1. P-1: a session-independent local runner for the Aether kernel. It covers manifest, partitions under a canonical lease, epoch checkpoints to a sha-addressed directory, sharded ledger, verified resume (s3.8) and final account. Acceptance is a fire test: kill the worker, the supervisor and the session, and get the same final digest as the control, with wasted work accounted. Under 1 core-hour (R2). Formats aligned with C-012 so the runner moves to Fabric/NF transport without change.
  2. Wait for C-012-T002/T003 and build directly on PG publication. This is lower duplication risk, but it is gated on Themis's schedule.
  3. P-2 first (enforce gpu_hours/cloud_usd caps in rso/slice001/ledger.py Caps, with fire tests): Q1, small, independent.
RECOMMENDATION: Option 1, with option 3 alongside it. Option 1 removes the B2 dependency now, and its formats stay compatible with option 2.
CAPABILITY_NEEDED: Q2
