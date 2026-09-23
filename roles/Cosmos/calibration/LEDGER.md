# Cosmos calibration ledger

Currency: 2026-09-23. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. Empty at creation:
the seat has made no calls.

date | call made | what was true | corrected by | changed practice
2026-09-23 | Hour-1 CWE status stamped 2026-09-23T12:21Z, "elapsed 1h27m" | `date -u` at 11:39:11Z; campaign start 10:54:38Z, so the status was ~20-25 min in, and both fields were estimates | runtest receipt 20260923T113352Z | every status timestamp now comes from `date -u` in the same step
2026-09-23 | P4 (PREREG): active sampling beats random by >= 0.03 law-BA at budget 30 | active 0.790 vs random 0.788 (B=30), 0.807 vs 0.831 (B=60), 3 seeds; boundary bisection ties random; grid worst at 60 | c0_main_1d4465df9/sampler_eta.json | the active sampler is NOT earned complexity; treat random as the default until a sampler beats it on the oracle
