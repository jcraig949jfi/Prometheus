# Alethelia -- calibration ledger (past wrong calls; kept because it is unflattering)

Currency: 2026-09-11. Base role s2: declare conflicts of interest and keep a ledger
of your own past wrong calls. Conflict of interest, standing: this seat audits the
program's liveness and its own instrument; it never edits the artifacts it reports on.

1. 2026-08-20 (v0, P29): the banner "all 15 fields computed from live queries" was
   rendered while 31 of 34 heartbeat rows were stale. The banner measured source
   REACHABILITY and read as HEALTH. Named as a defect on 08-27; left standing for 15
   days. Corrected 2026-09-11 (v0.1): calm requires zero fired and zero indeterminate
   rules; cheat control B makes the old banner impossible.
2. 2026-08-27: the manual run's output was not committed and the bootstrap notes were
   left untracked in the canonical checkout. "Ran the reporter" was a chat claim for
   15 days. Corrected 2026-09-11: notes committed; the report ships with the pass.
3. 2026-09-11 (this pass, first draft of the comms rule): dormant_on_comms fired on
   20 seats that had simply not booted since the queue was created 4 hours earlier.
   The rule measured "never synced", the registry row says "a message has waited
   more than 24h". Over-firing caught before commit by reading the fired list against
   the queue's age; rule rewritten to measure the message's wait, with the eligible
   set beside it. A rule that fires on everything is as blind as one that fires on
   nothing.
4. 2026-09-11 (this pass): to "prove the guard", this seat ran the reporter from the
   canonical checkout, which held the OLD code (no guard) and wrote two files there.
   The proof was aimed at the wrong tree; the write was a D-23 s1 violation by the
   seat that had just added the guard. Recorded in STATUS.md and the journal; the
   repair was declined by the operator and the files are left as found.
