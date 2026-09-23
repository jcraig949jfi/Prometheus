# Cosmos calibration ledger

Currency: 2026-09-23. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. Empty at creation:
the seat has made no calls.

date | call made | what was true | corrected by | changed practice
2026-09-23 | Hour-1 CWE status stamped 2026-09-23T12:21Z, "elapsed 1h27m" | `date -u` at 11:39:11Z; campaign start 10:54:38Z, so the status was ~20-25 min in, and both fields were estimates | runtest receipt 20260923T113352Z | every status timestamp now comes from `date -u` in the same step
