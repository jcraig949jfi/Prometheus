# Themis status

Currency: 2026-10-04T15:39Z (from the creation tool's clock, UTC).

seat state: ACTIVE (creation pass). Charter PENDING the operator.
  WORK_STATE.json: HOLD (no READY work without a charter; base role
  2a F), MWO-0004 @ 25a486d44; fleet order CWO-2026-09-30C.
what it asserts: PRESENT (comms boot Themis[m2-7151a6d4] on the M1 store, heavy
  tier, claude-opus-5-5; booted by hand 2026-10-04 after the creation tool's
  boot failed -- see blockers), ACTIVE (this pass), NOT PRODUCTIVE (no
  domain output), VALID not applicable.
host: SPECTREX5; worktree themis-base-role-adopt-2026-10-04, branch themis/base-role-adopt-2026-10-04,
  base d93d3d8c6, dirty False at start.
monitors owned or fed: none.
fleet queue: no Themis row in ops/fleet/QUEUE.json.
blockers: none. The creation tool's comms boot failed (sparse cone lacks
  evidence_wiki; no EW_DB_HOST off M1); fixed in this worktree by
  `git sparse-checkout add evidence_wiki roles/Hestia` and EW_DB_HOST=192.168.1.202.
  Reported to Hestia as comms message 1451 (operator request).
next executable action: commit the operator's charter verbatim when it
  arrives, rewrite RESPONSIBILITIES.md around it, file the first backlog.
