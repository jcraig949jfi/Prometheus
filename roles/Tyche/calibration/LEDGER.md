# Tyche calibration ledger

Currency: 2026-09-29. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. Empty at creation:
the seat has made no calls.

date | call made | what was true | corrected by | changed practice
2026-09-30 | v0 compute "< 1 core-hour" (PREREG s6) | stopped attempt used 13.0 core-hours by gen 34/40; BLAS oversubscription (16 workers x openblas threads) plus ecology growth the 2-epoch pilot never reached | seat's own measurement (PREREG_AMENDMENT_1.md) | pin BLAS to 1 thread per worker; pilot must reach the largest ecology size a campaign can reach; campaigns carry a compute guard
2026-09-30 | H1 PASS with P1, P3, P4, P5 solved (PREREG s4) | H1 INDETERMINATE: P3, P4, P6 VOID (random lenses had access), P1 never solved | v0 REPORT.json | measure initial access over the whole initial population before freezing controls; use only zero-marginal laws as "inaccessible" controls
2026-09-30 | H3 residual shift PASS | FAIL: err residual fell on negative worlds with no accuracy change (organism decorrelation) | v0 REPORT.md F1 | every residual definition ships with its own negative control (flat on TSD/PRF as the ecology grows)
2026-09-30 | H4 redundancy PASS | FAIL: tab attention budget displaced raw channels; lenses re-supplying them were admitted | v0 REPORT.md F2 | no organism input set may depend on ecology order; cheat control for manufactured residuals
2026-09-30 | ADV_decoy solved | not solved (best val 0.114 transient, admitted lens +0.039) | v0 REPORT.md | xor-type structure is a separate, harder class; do not predict it from the planted-control reasoning
