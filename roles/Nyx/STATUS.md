# Nyx status

Currency: 2026-09-11 (seat creation and base-role adoption pass).

seat state: ACTIVE for the adoption pass (operator, 2026-09-11); charter
  PENDING. Standing state after this pass: BLOCKED on the charter, with
  the blocker named (the operator holds it; no prompt to write, the
  operator said it follows).
what it asserts: PRESENT (booted in comms 2026-09-11 14:31 UTC),
  ACTIVE (this pass ran), NOT PRODUCTIVE (no domain output; artifacts are
  the roles/Nyx/ directory only), VALID not applicable.
workspace: F:\Prometheus-worktrees\nyx-base-role, branch
  nyx/base-role-adopt-2026-09-11, base 56125e9e4 (origin/main at
  creation), dirty: only roles/Nyx/ additions.
guard: git-dir F:/Prometheus/.git/worktrees/nyx-base-role differs from
  git-common-dir F:/Prometheus/.git (linked worktree; not canonical).
comms: booted (host SKULLPORT, model claude-opus-5[1m], tier heavy,
  capabilities any); synced 2026-09-11 14:31 UTC: 1 new (Archaeon
  broadcast #1, sha256 402c3445443d1be5), queue length 0.
monitors owned or fed: none. No row in roles/base-role/MONITORS.md.
lane: none until the charter lands. No code or document outside
  roles/Nyx/ is touched by this seat.
blockers: the charter (operator).
next executable action: receive the charter; commit it verbatim under
  roles/Nyx/prompts/2026-09-11_charter/ with a MANIFEST
  (python -m comms.manifest write <dir>); rewrite RESPONSIBILITIES.md;
  file a 20-60 item BACKLOG_H0H5.md; register any monitor the charter
  creates; suggest the first five items and start the first.
