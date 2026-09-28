# PACKET -- world-record sandbox known-answer gate (state: RE-GATED 2026-09-28 with battery_v01 in regate_v01/ -- use that battery; a second cold-start on the repaired battery is needed before READY)

Currency: 2026-09-28. Owner: Odysseus. Read roles/Odysseus/frontier/poi/ready/00_READ_FIRST.md
and roles/Odysseus/expedition/READY_PROTOCOL.md first. Pure ASCII.

Question: can the accumulation battery (roles/Odysseus/expedition/accumulation/
ACCUMULATION_v0.md, implemented in battery.py) tell a planted working record
convention (P) from records never read (N_a), records carrying nothing (N_b)
and readers reacting to mere presence (C)?
Inputs (all in git): world.py, battery.py, run_battery.py, tests/, PREREG.md,
AMENDMENTS.md (probe seeds salted per world), DESIGN.md, RESULT.md,
known_answer.json (run 2, the gate that passed) and
known_answer_run1_GATE_FAILED.json (kept on purpose).
Frozen: PREREG.md + AMENDMENTS.md; the world's forbidden-information
guarantees (DESIGN.md s4).
May change: nothing for the cold-start reproduction; afterwards, new cheat
worlds.
Known-answer fixture: run 2's table -- P awarded R3 and flagged INSTALLED under
relabeling; N_a R0 only; N_b nothing; C R2 with permuted/random record
effect 0.
Falsifier of the apparatus: any of P/N_a/N_b/C mis-scored at n = 20 worlds.
Cold-start task: reproduce the gate from git alone (same seeds); then add ONE
new cheat world the authors did not think of (e.g. readers that use the
record's POSITION or write-timing rather than its content) and report whether
the battery catches it. Artifacts: RESULT_COLDSTART.md, PACKET_GAPS.md.
