REPORT -- surprise-driven eviction vs random eviction: noise, recency or capacity?

1. WHAT I SET OUT TO TEST
A bounded low-rank learner (BufferALS: warm-started ALS over a buffer of B exact records) must choose which records to
evict. Two "surprise" rules (keep_worst = keep the highest current |residual|; residual_reservoir = residual-weighted
A-Res reservoir) were reported to lose to random reservoir eviction on a positive-control world where half the cells
carry extra noise. I asked: (a) is that loss a noise-retention effect (does it appear only as the extra noise grows),
(b) is surprise in the regime-switch family really a recency proxy, (c) is capacity or eviction order the bigger lever
in the committed dev rows, and (d) is the "random" control actually relevance-blind.

2. WHAT I DID
Code: ensorain/ (lm01 arms, families, fixture) exported from origin/main@6ff2b2f8a into work/R-16/src and run only there.
- Reproduction: work/R-16/dose.py re-implements the fixture's positive control (F2_latent L2, generator lowrank,
  rank 3, B = cells/4 = 432, dev seeds 9330000-9330003, corrupted half = mode-0 index < d0/2, test = never-seen cells of
  the clean half). A subclass of BufferALS ("Tracked") is identical for the declared rules (same RNG consumption) and
  also records each retained record's admission index. It reproduces the committed fixture JSON on main to all digits
  (random -0.126, oracle +0.506, keep_worst -0.182, residual_reservoir +0.023).
- Dose-response: extra-noise SD in {0, 0.3, 1, 3} (same normal draws, scaled), arms random, oracle, keep_worst,
  residual_reservoir, fifo, plus two labelled EXPLORATORY arms: lp (learning progress: key = drop in the record's own
  residual over up to its last 3 refits; new records protected until one refit; arrivals enter with key ~0) and
  keep_best (evict the worst-fitting record). 4 seeds x 4 SD x 7 arms. Then 8 more dev seeds (9330004-9330011) for
  random / keep_worst / residual_reservoir at SD 0 and 3 (12 seeds there). Logged per run: AC, fraction of the buffer
  in the corrupted half, mean retained-record age (fraction of stream).
- Recency probe: F3_switch L2 lowrank, B = c/4, seeds 9330000-003, arms random/fifo/keep_worst/residual_reservoir/lp,
  logging retained ages and the fraction of the buffer from the final (scored) episode.
- Re-analysis (step1.py): all OK rows of ensorain/lm01/dev/margins and dev/margins_f5real on main; self-signal minus
  random AC at equal B per family x B and per rule, bootstrap 95% CI of the median over worlds; dual B'/B ratio;
  |order| vs |doubling B| at c/4.
Commands: python3 dose.py f2|f3 <seeds> [<sds>] <arms> <out.jsonl> (2 workers, 1 BLAS thread); python3 reduce.py;
python3 step1.py. Outputs: work/R-16/out/{repro,dose,extra,f3}.jsonl, dose_table.txt, dose_summary.json, step1.json.
Seeds used: 9330000-9330011 (dev range, fixture block) and the committed margins rows; no campaign/sealed seeds.

3. RESULT
(a) The stated anomaly is stale. At the commit it was harvested from (6a48ff937) residual_reservoir scored -0.457 vs
random -0.335. The later ALS convergence-rule change re-ran the fixture; on current main the committed fixture says
residual_reservoir +0.023 BEATS random -0.126, and only keep_worst (-0.182) is below. The freeze-review text still says
"both rules lose to random" and quotes the old +0.91 oracle gap (current: +0.63). Also, the fixture compares medians of
arms over 4 seeds; paired per seed at SD 3 both rules beat random in 3/4 seeds.
Dose-response, paired (arm minus random) AC, median [bootstrap 95% CI], seeds won; buffer fraction in corrupted half:
  residual_reservoir  SD 0: +0.35 [+0.13,+0.58] 10/12, corrupt 0.51 | SD 0.3: +0.38 4/4, 0.60 | SD 1: +0.25 3/4, 0.69
                      SD 3: -0.16 [-0.43,+0.08] 5/12, corrupt 0.79
  keep_worst          SD 0: -0.22 [-0.27,+0.10] 4/12, corrupt 0.51 | SD 0.3: -0.23 0/4, 0.95 | SD 1: -0.02 2/4, 0.97
                      SD 3: +0.07 [-0.33,+0.18] 8/12, corrupt 0.99
  oracle              SD 0: -0.06 1/4 | 0.3: +0.12 4/4 | 1: +0.41 4/4 | 3: +0.66 4/4
  random median AC    SD 0 +0.59 (12 seeds), 0.3 +0.35, 1 -0.03, 3 -0.19 (12 seeds)
  fifo +0.01/+0.13/+0.24/+0.03; lp -0.16/+0.18/-0.16/+0.14; keep_best -0.53/-0.38/+0.07/+0.15 (4 seeds each).
Reading: residual_reservoir shows the predicted noise-retention pattern: a clear win at SD 0 that shrinks and crosses
below random at SD 3 while its corrupted-half share climbs 0.51 -> 0.79 (CI at SD 3 still spans 0). keep_worst is NOT a
noise-dose story: it is already at or below random with no corruption (SD 0, a younger buffer: age 0.41 vs 0.50),
fills its buffer 95-99% with corrupted records from SD 0.3 on, yet is not worse than random at SD 1-3, because at
SD >= 1 random itself is below AC 0 (worse than predicting zero): a floor effect, not a ranking signal. Only the oracle
is well above floor at SD 3. The lp arm as implemented degenerated into a near-FIFO (retained age 0.045 vs FIFO 0.034;
corrupt share 0.60 at SD 3), so it is not evidence for a learning-progress repair.
(b) F3 switch (B = c/4, 4 seeds): AC random -0.36, fifo +0.84, lp +0.76, keep_worst +0.16, residual_reservoir -0.47.
Final-episode share of the buffer: random 0.33 (= its share of the stream), keep_worst 0.50, fifo/lp 1.00; mean age
random 0.50, keep_worst 0.38. keep_worst's F3 win over random is consistent with a partial recency proxy, and a plain
FIFO beats it by ~0.7 AC; residual_reservoir (not the frozen F3 choice) loses to random there.
(c) Committed dev rows (1,056 OK; reproduces the package's numbers): self-signal minus random at c/4 +0.074
[+0.055,+0.098], 63% > 0; F2 +0.37 [+0.32,+0.44] (all residual_reservoir); F3 +0.30 [+0.28,+0.32] 97% (all keep_worst);
F4 -0.054 [-0.068,-0.040]; F5 (old scale) keep_worst -0.32 [-0.37,-0.21] 17% > 0 while residual_reservoir +0.04; F5
real-cells rows: residual_reservoir +0.30 at c/4, keep_worst -0.04 (and -0.32 at c). Where the self-signal loses it
is mostly keep_worst. At c/4 median |order effect| 0.167 vs |doubling B| 0.160, order larger in 49% of rows (real-cell
F5: 0.26 vs 0.44, 35%). Dual B'/B at c/4 median 1.19 (F2 1.80, F3 1.57, F4 0.86).
(d) "random" here is Algorithm-R reservoir sampling: content-blind and age-neutral (mean retained age exactly 0.50,
per-segment shares equal stream shares), i.e. distribution matching. It is relevance-blind only when the test
distribution equals the stream distribution; in F3 (test = last episode) it is systematically mis-weighted, and FIFO is
the relevant relevance-free recency control.

4. DID IT RESOLVE THE QUESTION
Partly. Resolved: the harvested anomaly as quoted is stale on current code; the two surprise rules must be separated
(residual_reservoir: noise-retention crossing, consistent with the literature; keep_worst: loses without any
corruption and acts as a partial recency buffer); the SD >= 1 fixture regime is at the performance floor for all
non-oracle arms, so it cannot rank eviction rules; capacity and order are comparable levers at c/4 in the dev rows;
random is distribution matching. Not resolved: 4-12 seeds on one generator give wide CIs (residual_reservoir at SD 3
spans 0); the learning-progress key tested here collapsed to recency, so whether a proper learning-progress or
noise-floor key repairs residual_reservoir at high noise remains open; F4/F5 losses were not probed with new runs.

5. CONSEQUENCES
- Documentation/harness defect (Ensorain / LM01 prereg owners): the freeze-review note ("both self-signal rules lose to
  random", oracle gap +.91) describes the pre-convergence-fix fixture; the current committed fixture says otherwise.
  The fixture also compares per-arm medians over 4 seeds instead of paired differences; and at SD 3 (B = c/4) every
  non-oracle arm is below AC 0, so the fixture validates the oracle but says little about the self-signal rules. A
  lower-noise level (SD 0.3) separates the rules cleanly.
- False premise, partial: "surprise retains noise" is true for residual_reservoir (a clean, modest dose-response), but
  keep_worst's weakness is not noise retention; it is present with homoscedastic noise.
- F3: keep_worst's win over random is partly recency; FIFO dominates. Any F3 claim of "relevance selection" by
  surprise should be read against FIFO, which v0.3.2 already added as a reference arm -- this confirms that choice.
- Controls: calling reservoir-random "relevance-blind" is fine for content, but it is distribution matching; in
  non-stationary worlds it is not a neutral baseline. Programs using it as the blind control (SI, Ergon) should say so.
- "Order is second-order to capacity" does not hold at c/4 in these rows; an Ergon-style null on another consumer should
  not be generalised.
- Designers of learning-progress keys: a naive "residual drop" key with neutral admission becomes a recency buffer;
  it needs an admission test or a noise-floor term to be a genuine alternative.
Who should know: Ensorain (LM01 fixture/review text), whoever owns the engine-wide forgetting-rule primitive, SI and
Ergon control-labelling owners.

6. COST
About 1.5 hours of my time. CPU about 2,430 s (~41 CPU-minutes) of BufferALS fits (216 fits, 2 workers, 1 BLAS thread
each) plus a few seconds of re-analysis; RAM well under 1 GB. Not done: more generators/seeds for the dose curve, a
proper learning-progress/noise-floor key, F4/F5 new runs, retained-age logging across the full F3 dev set, and
committing step 1 (read-only clone).
