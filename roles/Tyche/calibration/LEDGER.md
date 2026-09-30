# Tyche calibration ledger

Currency: 2026-09-29. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. Empty at creation:
the seat has made no calls.

date | call made | what was true | corrected by | changed practice
2026-09-30 | v0 compute "< 1 core-hour" (PREREG s6) | stopped attempt used 13.0 core-hours by gen 34/40; BLAS oversubscription (16 workers x openblas threads) plus ecology growth the 2-epoch pilot never reached | seat's own measurement (PREREG_AMENDMENT_1.md) | pin BLAS to 1 thread per worker; pilot must reach the largest ecology size a campaign can reach; campaigns carry a compute guard
