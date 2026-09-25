# Ares TODO

Currency: 2026-09-25 (written before an operator reboot; seat PARKED).
Items are closed by deletion with the closing commit noted in the
journal. Nothing here is authorised to start: the seat is parked and
every science item waits on the operator's continue/close decision
(RESUME.md s7 Q1).

## Blocked on the operator (no work may start)
ARES-C2-Q1 | Continue to cycle 3 (test RESUME.md s6.1 only) or close
            and export | BLOCKED: operator decision
ARES-C2-Q2 | Nyx/Harmonia/Theophrastus have never replied to seven
            comms messages; decide relay / stop / different consumer |
            BLOCKED: operator decision
ARES-C2-Q3 | Evidence-wiki submission for a parked seat: do it or let
            the reports stand | BLOCKED: operator decision
ARES-C2-Q4 | Test the basin rule on another seat's substrate |
            BLOCKED: cross-lane, operator only

## Would run first if cycle 3 is authorised (spec in RESUME.md s6.1)
ARES-C3-1 | Arm A: decouple the leak trade-off (v = keep*v + f) and
            re-run c1_all on W4, 10 fresh seeds; prediction recorded
            BEFORE running: keep load-bearing >= 5/10 | ~10 runs
ARES-C3-2 | Arm B control: re-parameterise keep only (keep = 1-exp(-r),
            r in [0,8], step N(0,0.5)), same 10 seeds; prediction:
            keep does NOT take over | ~10 runs
ARES-C3-3 | Report both arms, disposition, then park again. No third
            arm, no new worlds.

## Instrument debt (do before ANY new campaign, cycle 3 or otherwise)
ARES-C2-1 | Fix D1 at source: search.run must not select the reported
            champion on the held-out set. Select on training, report
            held-out; keep the old field under a different name so old
            receipts stay readable | ares/search.py + a test that a
            shuffled control scores at the floor
ARES-C2-2 | Retire search.dissect's node-only ablation from any
            mechanism claim in favour of ares/carriers.py (D3), or
            make dissect call carriers and keep one path

## Carried, never done (honest backlog)
ARES-25   | Evidence-wiki submission (carried since cycle 0) |
            see ARES-C2-Q3
ARES-24   | Worlds Kernel (prometheus/toolbox/) adoption assessment
            and a note to Bellerophon | never started; only worth it
            if Ares continues
