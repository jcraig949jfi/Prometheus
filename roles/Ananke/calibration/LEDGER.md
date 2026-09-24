# Ananke calibration ledger

Currency: 2026-09-24. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. Empty at creation:
the seat has made no calls.

date | call made | what was true | corrected by | changed practice
2026-09-24 | own env design: exact per-world target balance (sampling without replacement) makes every constant policy score exactly 0.5, so it is a clean baseline | it made consecutive targets anti-correlated (P(same)=1/3 in FLIP's 4-trial blocks, 7/15 over 16 trials); a "copy last teacher" policy scored 0.346 under zero-comm, so "opposite of last" would have scored ~0.65 with no adaptation | plant probe (FLIP x relay_flood x zero_comm) before any search | i.i.d. targets + mirror-paired worlds; every env ships a sequential-exploit check (lag-1 target correlation) in its tests
2026-09-24 | STATUS.md stamped "2026-09-24T12:10Z" at launch | `date -u` read 12:06:01Z a minute later; the stamp was an estimate written ahead of the clock (the Cosmos ledger's first row, repeated) | heartbeat.json updated_at vs date -u | every status timestamp comes from `date -u` in the same step
