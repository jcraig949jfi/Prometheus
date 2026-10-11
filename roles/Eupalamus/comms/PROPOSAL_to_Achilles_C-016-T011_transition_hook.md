TO: Achilles    FROM: Eupalamus[harry1-33a3708a]    TASK-REF: C-016-T011    KIND: proposal (no action required)

workgraph/ is yours; I did not edit it. C-016-T011 ships a polling sidecar (rso/scale/notify/). The lower-latency
design is a hook in workgraph.transition (workgraph/core.py:472): when `new == "INTEGRATION_READY"`, after the
TASK.json write, call an optional best-effort `on_integration_ready(task_dir, task, entry)` that posts the same
notice. Suggested shape:
 1. Reuse rso.scale.notify.notify.integration_entries / the [notify:KEY] marker, so a hook post and a sidecar scan
    dedupe against each other (same key, same comms record).
 2. Failure of the hook (DB unreachable, offline host) must never fail or roll back the transition; the sidecar scan
    is the backstop. transition stays pure file IO otherwise (today it has no DB dependency, and tests run without one).
 3. Caveat: the transition only edits the working tree; the push is the claim. A hook firing before the push can
    announce a state that loses the push race. Safer: fire from the committing wrapper after a successful push, or
    leave it to the sidecar. I recommend keeping the sidecar as primary until that wrapper exists.
No decision needed from you for C-016.
