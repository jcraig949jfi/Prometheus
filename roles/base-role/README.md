# roles/base-role

The responsibilities and the repository working contract every Prometheus
seat inherits. Adopted by the operator 2026-09-11.

- NORTH_STAR.md -- the operator's north star, verbatim; read before any charter.
- RESPONSIBILITIES.md -- north star, boot sequence, doctrine, journaling, communication
  (ASCII paste blocks; write-a-prompt-when-blocked; suggest work at boot),
  Claude Code rules, session close.
- WORKING_CONTRACT.md -- the git/workspace invariant (D-23): worktree per
  seat, task branches from a recorded base SHA, no `git pull`, receipts
  carry base_sha/branch/worktree_path, fast-forward integration, pinned
  worktrees for long-running processes, destroy-not-nurse, conformance as
  provenance.
- INHERITANCE.md -- the list of roles and the banner each carries.

A seat's own documents ADD to these files and may not contradict them.
Where a seat file predates this directory and disagrees, this directory
wins and the seat file is annotated, never silently rewritten.
