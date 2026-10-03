# roles/base-role

The responsibilities and the repository working contract every Prometheus
seat inherits. Adopted by the operator 2026-09-11.

- NORTH_STAR.md -- the operator's north star, verbatim; read before any charter.
  Its 2026-09-29 addendum makes the North Star the default work selector.
- RESPONSIBILITIES.md -- north star, boot sequence, doctrine, journaling, communication
  (ASCII paste blocks; write-a-prompt-when-blocked; suggest work at boot),
  Claude Code rules, session close. Section 2a is the work-conserving research
  loop: local North-Star selection, options become sequences, a blocked item
  is not a blocked seat, frontier replenishment, no coordination-induced idle.
- WORKING_CONTRACT.md -- the git/workspace invariant (D-23): worktree per
  seat, task branches from a recorded base SHA, no `git pull`, receipts
  carry base_sha/branch/worktree_path, fast-forward integration, pinned
  worktrees for long-running processes, destroy-not-nurse, conformance as
  provenance.
- WAKE_DIRECTIVE.md -- the conformant wake wording the operator pastes
  (fetch, record the SHA, worktree; never pull).
- INHERITANCE.md -- the list of roles and the banner each carries.
- comms/ (repository root) -- the inter-agent inbox, broadcast and task queue every seat syncs before and after each prompt; python -m comms sync <Seat>.
- MONITORS.md -- the registry of standing loops, watchdogs and shadows: input, freshness source, dormancy threshold, alarm, state.
- DISTRIBUTED_WORK.md -- (2026-10-03) executable work graphs: task packets, lifecycle, capability
  classes, inference economy, structured escalation, receipts, low-coordination rules; tool
  `python -m workgraph` (workgraph/), files under ops/campaigns/<C-id>/.

Shared roles (2026-10-03): a directory roles/<name>-role/ is an inherited role layer, not a seat. A seat
inherits base-role and may also inherit one shared role; the chain is declared on the seat's entry file
and listed in INHERITANCE.md "Shared roles". comms roster, the census and the self-tests skip *-role
directories.

A seat's own documents ADD to these files and may not contradict them.
Where a seat file predates this directory and disagrees, this directory
wins and the seat file is annotated, never silently rewritten.

The base role tests its own claims: archaeon/tests/test_base_role.py (mandatory
artifact paths not ignored; every role stamped; base files pure ASCII; issued
manifests verify; the harness's linked worktrees pass the canonical guard), and
archaeon/tests/test_shared_roles.py (shared-role chains resolve; every seat is discoverable) with
workgraph/tests/ (packet, lifecycle, capability class, receipt and escalation shapes).
