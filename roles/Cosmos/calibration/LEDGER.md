# Cosmos calibration ledger

Currency: 2026-09-23. Kept because it will be unflattering (base role s2).

One row per call this seat made that later proved wrong, with the
correction and what the seat now does differently. Empty at creation:
the seat has made no calls.

date | call made | what was true | corrected by | changed practice
2026-09-23 | Hour-1 CWE status stamped 2026-09-23T12:21Z, "elapsed 1h27m" | `date -u` at 11:39:11Z; campaign start 10:54:38Z, so the status was ~20-25 min in, and both fields were estimates | runtest receipt 20260923T113352Z | every status timestamp now comes from `date -u` in the same step
2026-09-23 | P4 (PREREG): active sampling beats random by >= 0.03 law-BA at budget 30 | active 0.790 vs random 0.788 (B=30), 0.807 vs 0.831 (B=60), 3 seeds; boundary bisection ties random; grid worst at 60 | c0_main_1d4465df9/sampler_eta.json | the active sampler is NOT earned complexity; treat random as the default until a sampler beats it on the oracle
2026-09-23 | P2 (PREREG): v1 dies in round 0 through the ca redundancy transform; v2 picked on first revision | round 0 died mostly through regs (no G term) and ring near-threshold worlds; first revision picked v1; redundancy killed round 1 instead | run2_f31339054/adversary.json | predict the failing mechanism AND the round separately; a right mechanism with a wrong path is still a lost call
2026-09-23 | own instrument: adversary coordinates | adversary evaluated a v2 law with v1 coordinates (defect I1) | RESULT_run2.md | coordinate map travels with the law object; test asserts it
2026-09-23 | own gate design: G6/G6b magnitude window |log2(f_obs/f*)| <= 1 and direction rule, preregistered without a chance floor | POST-HOC: a constant prescription f_hi = 2 scores magnitude 10/12 (gate needs 8); the law's precision (mean |log2 err| 0.155 hi / 0.183 lo vs best constant 0.83) is the discriminating statistic | c0b/run_21fd1b2cc/G6b_posthoc_baselines.json | every future gate ships with a naive-baseline score computed at PREREG time on the gate's own scale
2026-09-23 | own instrument: intervention prescription assumed a single (upper) flip | the law is a band; the engine returned the scan edge f=1/64 for 12/12 bases; G6 FAIL 0/12 is an engine defect | c0b PREREG amendment B1 | prescriptions report every flip of the law along the intervention axis (two_sided_flips + test)
