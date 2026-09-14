# Charon calibration ledger

Kept because it is unflattering (base role s2). One row per wrong call, with the
direction the error pushed and how it was caught. Seeded 2026-09-11 from the 09-01
journal; the 08-25 journal is NOT yet extracted (BACKLOG CHARON-05). Earlier sessions
(05-05 to 08-16) recorded "what I got wrong" in prose only.

Format: date | call | direction of the error | how caught | source

2026-09-01 | Keyed residue records by ledger_id#seq, the campaign's own key, which collides across blocks; first reading "23-27% of F-NULL controls are contaminated" | inflated severity | noticed 35 distinct fabricated records drawn from a pool of 6 (35 > 6); true figure 3.0% (A) and 24.1% (B), only for tasks whose treatment already carried it | charon/CHARON_SESSION_2026-09-01.md "What I got wrong" 1
2026-09-01 | Began writing that form (a) would retroactively rewrite already-collected P3 rows | inflated severity | checked the filesystem instead of asserting: no p2_*, p3_pilot.jsonl or p4_arms.jsonl existed; every harm was prospective | same, item 2
2026-09-01 | Began building toward "the corpus fabricates from nothing" | inflated severity | measured: 0 tasks in either block had only a transport-failed row | same, item 3
2026-09-01 | The seat's own standing pointer said the admissibility preflight "runs on every commit via pre-commit hook"; on M2 there was no hook | overstated own instrument | looked in .git/hooks on M2; the hook is installed per machine and recorded nowhere | same, CH-2026-09-01-B
2026-09-01 | ATK-013 printed "Defect ABSENT" over a live instance of its own class | own probe green for the wrong reason | its fire condition tests under-reading only and globs only block A | same, "Standing gates"

Pattern across the 09-01 rows: three of five errors pushed toward a BIGGER finding
(severity), not a more favourable one. The drift guard that audits the flattering
direction last must treat severity as a flattering direction for this seat.

2026-09-11 | Boot report (comms #149) said block B's residue pool "has moved again since the ruling": 534 rows now vs 275 in the ruling | inflated severity | 534 is every raw line, 275 is the rep-1 subset the ruling quoted; the ruling's own table (275/220/55) matches the file exactly; mtime 08-25, last commit d5e372cb9 (08-30). Withdrawn in charon/probe/RULINGS_2026-09-11.md section 0 | roles/Charon/comms_out/2026-09-11_boot_report.md "ONE FACT MEASURED"
2026-09-11 | First draft of check_c2 keyed on uid, not row; on block A (206 rep-1 rows, 200 uids: each failure retried under its uid) it would have fired on a loader that correctly dropped the failure and kept the retry | own instrument fires on the fixed case | the block A count (200 admitted uids vs 206 records) before the check shipped; re-keyed on (uid, seq), UNATTRIBUTABLE branch added, two tests | charon/probe/RULINGS_2026-09-11.md section 1, C2
