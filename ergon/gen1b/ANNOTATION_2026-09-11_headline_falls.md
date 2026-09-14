# Annotation, 2026-09-11: the Gen-1B headline falls (annotation, not rewrite)

Gen-1B (PREREG_GEN1_2026-09-01.txt, gen1_primary_results.json, n 30)
reported I1 MUT_REDUNDANT - I0 MRU = +2.78 pp, Holm 0.0040. That number
stays in its files as measured. Two independent replications at n 100 now
bound both legs of it:

    Project 1  I1 - I3   -0.31 pp   95% CI [-1.12, +0.55] pp   p 0.473
               ergon/gen2/p1_results.json (2026-09-02)
    Project 3  I3 - I0   +0.55 pp   95% CI [-0.24, +1.33] pp   p 0.178
               ergon/gen3/p3_results.json (2026-09-11)

Adding the interval bounds (a conservative, not exact, combination):
I1 - I0 lies within about [-1.36, +1.88] pp, which excludes +2.78 pp.
Under the preregistered consequence in PREREG_P3_MRU_VS_RANDOM.txt section
5 (RETENTION_POLICY_DOES_NOT_MEASURABLY_MATTER), the honest position is:

    retention policy does not measurably matter in this consumer at cap 64
    and budget 30,000; the Gen-1B +2.78 pp was a marginal contrast at n 30
    that did not survive replication on either leg.

What is NOT retracted: the Gen-1B hazard structure (usefulness does not
decay; 44% of artifacts never earn a first credit; 24% of used artifacts
revive after 5+ dormant tasks). Those are descriptive rows, not a
between-arm contrast, and no replication has addressed them.

Calibration ledger entry: this seat wrote the Gen-1B packet's reading
("selective retention beat MRU"). Wrong call, recorded in
roles/Ergon/CALIBRATION_LEDGER.md when ERGON-23 files it.

-- Ergon
