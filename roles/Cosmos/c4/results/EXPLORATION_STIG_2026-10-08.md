# Exploration log: why do LOCAL laws fail on stig? (EXP-01 discovery data; EXPLORATORY, no claims)

Three explanations were tried on the SAME discovery data; all three are REFUTED. Tuning stops here (a fourth try on
these rows would be a forking path). Any future variant is preregistered and tested on unseen worlds.

| # | explanation | test | result |
|---|---|---|---|
| 1 | frame dependence (absolute vs agent frame) | EgoStig (exact relabelling, readout identical); L-0003 class at frozen theta | 1/30 class flips (< 10% prereg threshold) -> NOT frame-dependent at class level; scores shift by several log units; ego frame does NOT fix the 3 PASSIVE misses (ego log d2 1.0-1.4 vs theta -4.31) |
| 2 | no actor-resolution floor (ratio of two tiny numbers) | eps * I added to the readout covariance, eps in {1e-3, 1e-2, 1e-1} | best in-sample stig BA .52-.57 -> REFUTED |
| 3 | whitening amplifies near-zero-variance dimensions | eigenvalue floor rel {1e-4, 1e-2} | best in-sample stig BA .57-.63; 2 of 3 PASSIVE worlds still score above the FUNCTIONAL median -> REFUTED |

Status: UNEXPLAINED. Physics check: with v = 2 the trace is 3-9 cells from the sensor at the query, so a correct
linear composition must give ~0 signal; the local description assigns a large one. Working hypothesis for the
backlog (NOT an explanation): a stationary-averaged one-step description loses the CORRELATION between where the
cue was deposited and where the sensor will be (history-conditioned routing). If true, every stationary local
vocabulary has this blind spot, and a reachability coordinate needs event-conditioned (not stationary) local
statistics -- which must be designed so it cannot observe k-step propagation (G7).
rnn and graph: unaffected by all three variants (in-sample 1.00 / 1.00).
