# Crius status

Currency: 2026-09-19T01:34Z (second boot of the day, instance m2-8d43bbf9;
  first instance m2-fe63387d created the seat 2026-09-18).

seat state: BLOCKED on the charter after this pass; blocker named (the
  operator holds it; to be given in chat).
what it asserts: PRESENT (booted in comms 2026-09-19T01:34Z as
  Crius[m2-8d43bbf9]; inbox 0 new, queue empty), ACTIVE (this boot
  ran), NOT PRODUCTIVE (no domain output; artifacts are roles/Crius/
  only), VALID not applicable.
host: M2 (SPECTREX5); EW_DB_HOST=192.168.1.202 for every comms call.
workspace: the seat worktree crius-base-role (under Prometheus-worktrees),
  branch crius/base-role-adopt-2026-09-18, base 8c86cb1e4 (origin/main
  at creation); fast-forwarded to 8bb1a28a0 (origin/main at the
  second boot) by explicit merge, never pull.
guard: git-dir .git/worktrees/crius-base-role differs from
  git-common-dir .git (linked worktree; not canonical).
monitors owned or fed: none. No row in roles/base-role/MONITORS.md.
lane: none until the charter lands.
blockers: the charter (operator).
next executable action: receive the charter; commit it verbatim under
  roles/Crius/prompts/<date>_charter/ with a MANIFEST
  (python -m comms.manifest write <dir>); rewrite RESPONSIBILITIES.md;
  file a 20-60 item BACKLOG_H0H5.md; register any monitor it creates.
