# Themis TODO

Currency: 2026-10-04T15:39Z (UTC). Closed items are deleted with the closing
commit and date, purged after 24 h (base role s7).

- [ ] Receive the charter; commit it verbatim with a MANIFEST under
      prompts/<date>_charter/
- [ ] Rewrite RESPONSIBILITIES.md around the charter (pre-charter body to
      superseded/); name overlaps with sibling seats before claiming any
      gap; record the dependency surface
- [ ] File BACKLOG_H0H5.md in the schema (>= 20 rows, first five today's);
      move WORK_STATE.json out of HOLD
- [ ] Decide with the charter whether the seat heartbeats Aporia (CWO-C
      s13) and may be dispatched to (CWO-C s7-s9). Not sent at creation:
      Aporia dispatches READY seats and this seat is HOLD with no lane.
- [ ] First chartered wake: read roles/base-role/MONITORS.md and
      roles/base-role/DISTRIBUTED_WORK.md in full (the creation pass reads
      neither; the seat owns no loop and holds no task packet)
- [ ] The creation worktree is SPARSE (roles/base-role, comms, archaeon
      tests, ops/work_orders, aporia/doctrine). Run
      `git sparse-checkout disable` in it before work that needs the rest
      of the tree.
