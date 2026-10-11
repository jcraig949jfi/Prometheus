# EXP-09 RESULT -- stig H-SPREAD on fresh worlds (EXPLORATORY; DISCOVERY batch 4; 2026-10-11)

Prereg: prereg/EXP-09_STIG_SPREAD.md (5be3b5893, before data). Run 07:36Z-08:00:09Z under supervise (DONE,
0 restarts, 60/60). Data EXP-09_stig_b4.jsonl (sha256 85fcf78fb204b39a...).

| set | n moving worlds | median Spearman(spread score, excess) | median Spearman(return R, excess) | rule |
|---|---|---|---|---|
| all | 42 | .206 | .431 | FAIL (needs >= .50 and >= return + .10) |
| D >= .1 | 32 | .206 | .400 | FAIL |

VERDICT (by rule): **H-SPREAD REJECTED**. The diffusing-trace / expected-window-mass predictor is WORSE than the
noise-free ring-return predictor on fresh worlds, including the high-diffusion worlds it was built for. The post hoc
EXP-05 diffusion reading does not survive fresh data. stig's k-dependence remains geometric in direction (EXP-05
intervention) but neither zero-parameter account explains it quantitatively. Recorded; not pursued further now.
Note: EXP-05 reported PEARSON r for R (.23 / .31); EXP-09 uses SPEARMAN (.43 on fresh worlds) -- not comparable.
