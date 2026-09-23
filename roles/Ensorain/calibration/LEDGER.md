# Ensorain calibration ledger

Currency: 2026-09-23. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. Empty at creation:
the seat has made no calls.

date | call made | what was true | corrected by | changed practice
2026-09-23 | H2 harvest margin would FAIL (PREREG s7) | TT_EVOLVED beat TT_TUNED +33.5% at C=168 (CI lo > 0) | confirm_M1 / score_E0.json | underrated how much a GA on constants gains over a 20-point grid; the gain was generic (cross-class), so the harvest margin alone says little
2026-09-23 | H3 would PASS as a meaningful dose-response | TT advantage negative at every lambda; rho = -9/10 exact, float -0.8999999 failed a <= -0.9 gate | score_E0.json | never write a rank-correlation gate at an attainable exact value; state the tie rule, and require the advantage to be positive somewhere
2026-09-23 | Negative-control wording "R^2 within .05 of 0" | miscalibrated learners have R^2 << 0 without false signal | dev_r2; A6 | write controls on the property (no false signal), not on a symmetric band
