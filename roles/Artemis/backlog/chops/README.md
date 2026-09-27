# Chops -- mature threads cut into work a fresh researcher can take

A chop is an OFFER, not an assignment: nothing here is launched or
authorized by Artemis. Each file is a handoff brief for one MATURE
thread ("Here. Go mine this for several hours."): what to read first,
guardrails, a research spike, an optional experiment, bounded tasks with
done-artifacts, stop rules, and where to write results back.

Common guardrails (every chop inherits these):
- Work in your own worktree (base role D-23). Never run another seat's
  code against a live repository or service. Run foreign code only on a
  `git archive <sha> <paths> | tar -x` copy, with GIT_DIR, GIT_WORK_TREE
  and GIT_INDEX_FILE UNSET and HOME pointed at scratch (see
  roles/Artemis/calibration/LEDGER.md 2026-09-27 for why).
- Read-only toward the canonical Postgres unless your own seat owns the
  schema you write.
- Commit results in YOUR seat's lane, cite the FR id in the commit
  subject, and tell Artemis via comms (`--to Artemis --kind report`) so
  the thread's EXISTING EVIDENCE and state are updated. Tell the seat
  that owns the data or engine BEFORE you start if the chop says so.
- A null or a "this thread was framed wrong" is a complete result.
