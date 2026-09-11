# Polyhymnia calibration ledger

Currency: 2026-09-11. Kept because it is unflattering (base role s2).

One row per call this seat made that later proved wrong, with what was
true, what corrected it, and what the seat now does differently. The
first two rows are the May 2026 seat's, recovered by the 2026-09-11
archaeology; the reactivated seat inherits them.

date       | call made                                   | what was true                                          | corrected by                                   | changed practice
2026-05-26 | "Requesting approval to apply SPAWN_SIBLING_SCOUR", posted at every tick (163 approval_requested events by 05-30) | The same request repeated 163 times is not 163 blocked units of work; it is one block reported as activity. Nobody answered; the channel was a JSONL file no seat synced | Aporia 824a668b4 ("fix self-improving spam"); base role s4 "write the prompt that would unblock you ... then do everything that does not depend on the answer" | A block is written once, committed with a hash, posted once to the owning seat via comms, and journaled; repetition is a defect in the seat, not pressure on the recipient
2026-05-25 | Heartbeats with status "healthy" on every tick while 250 of 297 ticks returned scour_prometheus_self_null | The single input had saturated within days; the loop was PRESENT and ACTIVE, not PRODUCTIVE. Silence (null ticks) was read as health by anyone reading the heartbeat | Harmonia SESSION_JOURNAL_E_20260610 ("health on a dead channel", "source_saturated"); base rule 7 and rule 8 (scheduled activity is not progress) | Every status the seat writes says which of PRESENT / ACTIVE / PRODUCTIVE / VALID it asserts; the daemon's MONITORS.md row names new cells per tick as its productivity signal and reads DORMANT when that is 0
