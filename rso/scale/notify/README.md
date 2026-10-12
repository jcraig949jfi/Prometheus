# rso.scale.notify -- INTEGRATION_READY notices (C-016-T011)

Cuts integration latency (operator directive s7): when a task enters INTEGRATION_READY, one durable comms notice
reaches the integrator, and the queue is visible. A sidecar: it READS `ops/campaigns/*/tasks/*/TASK.json` and
WRITES comms messages only. It never merges, never changes task state, never bypasses tests.

    python -m rso.scale.notify scan  --coordinator Palamedes [--to Palamedes] [--from Eupalamus] [--dry-run]
    python -m rso.scale.notify scan  --campaign C-016
    python -m rso.scale.notify queue --coordinator Palamedes [--no-db] [--json]

On a host that is not M1 set `EW_DB_HOST=192.168.1.202` first. Run it from a checkout/worktree at `origin/main`
(`git fetch origin`, never pull): it reads the task files of the tree it runs in.

## Idempotency (the core property)

- Key: `(task_id, attempt)` where attempt = the 40-hex branch head sha in the INTEGRATION_READY history note, else
  the `end_sha` of the newest `attempts/*/RECEIPT.json`, else `ts:<transition timestamp>`.
- Record: the notice itself, a `comms.messages` row with `task_ref=<task_id>` and `[notify:<key>]` in the subject.
  Before posting, `scan` looks for that row; a postgres session advisory lock (`pg_advisory_lock`) covers
  find+post so two scanners racing do not both post. The record is in the one shared database, not a temp file.
- A retry, a second scanner, or another host posts nothing new. A new head sha (a new attempt) posts a new notice.
- Disposition: when a notified entry is followed by INTEGRATED/CLOSED (or IMPLEMENTING = SENT_BACK) in the task
  history, the next scan posts one `DISPOSITION ... [notify-disp:<key>]` message. Entries never notified are not
  retro-notified.

## Wake command (documented, nothing installed; no OS scheduler task)

A one-shot headless launch for the coordinator, e.g. from whatever already runs the fleet:

    cd <worktree at origin/main> && EW_DB_HOST=192.168.1.202 python -m rso.scale.notify scan --coordinator Palamedes \
      && python -m rso.scale.notify queue --coordinator Palamedes

The notice lands in the coordinator's comms inbox (`python -m comms sync Palamedes`). To wake the coordinator
itself, the existing launch path can be invoked when `scan` reports `posted` non-empty; that wiring is the
coordinator's choice and is not part of this sidecar.

## Limits (honest)

- Polling, not an event: latency = scan interval. The event-driven form is a hook in `workgraph.transition`; see
  `roles/Eupalamus/comms/PROPOSAL_to_Achilles_C-016-T011_transition_hook.md` (routed, workgraph/ not edited).
- Sees only what is pushed to the tree it runs in; a builder's INTEGRATION_READY state commit must be on main.
- A head sha absent from the note and from any receipt falls back to the transition timestamp: still once per
  transition, but a re-sent-back-and-redone attempt with no sha is distinguished only by its new timestamp.

Tests: `python -m unittest rso.scale.notify.tests.test_notify` (RED first: evidence/RED.txt, GREEN.txt).
