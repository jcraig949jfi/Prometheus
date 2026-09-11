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
