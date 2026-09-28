# PKG-S1 pilot result: sufficiency ladder with exact oracles (2026-09-28)

Status: PILOT (answer-keyed calibration of concepts; not a preregistered campaign). Data: results/ladder.json.
- Code: worlds.py (oracles verified by tests: the Even/golden-mean Bayes log-loss hits h_mu = 2/3; the Even process has
  no finite window; W1 beats plug-in; SNS beats iid; W5 lookup exact; STAT(k) = Bayes at the true order).
- Setup: 16 seeds, T = 4000 (binary) / 20000 (key-value). One process at BELOW_NORMAL, 93 s on M2 (not contended:
  < 1 core).
- Metric: excess log-loss vs the EXACT Bayes predictor (bits/symbol). Tolerance declared .02.

## Findings (numbers are means over 16 seeds)

1. LOCUS OF COMPRESSION IS IRRELEVANT WHEN THE STATISTIC IS RIGHT. In W0, W1, W2 (orders 2, 3), golden mean and W4, the
   storage learner (STAT(k), keeps only counts) and the verbatim-store learner with a query-time summary (VERB_SUM(B, k)
   at B = 4096) have IDENTICAL excess. It is 0.000 at the true order in W2, and the two coincide by construction once
   B >= T. What matters is WHICH statistic is computed (k), not whether the compression happens at storage or at
   readout.

2. KEEPING EXTRA DISTINCTIONS COSTS ONLY VIA FINITE-SAMPLE ESTIMATION.
   - Over-order statistics lose monotonically, e.g. W2 order 3: excess .004 / .017 / .039 at k = 4 / 6 / 8, vs 0 at
     k = 3.
   - A short verbatim window (B = 256) loses vs B = 4096 at every k.
   - This is the Shamir-Sabato-Tishby / Still-Crutchfield regime: discarding is a variance-control device whose value
     vanishes as data grow. It is NOT a sign that the extra information is harmful in itself.

3. NO WINDOW STATISTIC REACHES BAYES ON THE EVEN PROCESS (finite causal state, infinite Markov order).
   - STAT excess by k = 0, 1, 2, 3, 4, 6, 8: .252 .211 .131 .110 .075 .060 .075. An INTERIOR optimum at k = 6
     (truncation error vs estimation error).
   - The 1-bit causal-state tracker (not in the learner family) would reach 0.
   - So the useful compression here is the RIGHT sufficient statistic (2 states), not "less information". Window
     learners store MORE bits (1,537 at k = 6) and still lose.

4. NONPARAMETRIC READOUT OVER VERBATIM HISTORY PAYS VARIANCE. NEAREST (PPM-style longest-context readout) is worse than
   the right-order statistic everywhere except the Even process, where it is also worse than STAT k = 6:
   - W2 order 3: NEAREST .075-.129 vs STAT_k3 .000;
   - W4: NEAREST .129-.225 vs STAT_k2 .006.

5. EXACT HISTORY IS NECESSARY IN THE KEY-VALUE LONG TAIL, AND SELECTION AT MATCHED CAPACITY MATTERS.
   - LOG (full verbatim) = Bayes (0.000).
   - Bounded stores lose steeply below ~1,000 slots: 64 / 256 / 1,024 slots give TABLE (random eviction)
     1.512 / .728 / .040, and WINDOW (recency) 1.288 / .553 / .019.
   - At EQUAL capacity, recency selection beats random eviction. In Zipf-keyed streams recency correlates with the
     query distribution. A case where SELECTIVE retention beats random retention at matched capacity (cf. T05); the
     reason (the recency-query correlation) is a property of the world.

## What this does and does not establish

- DOES: in answer-keyed worlds, "discarding helps" appears only as (a) finite-sample variance control and (b) choosing a
  sufficient statistic. Neither is "extra information is harmful to an optimal predictor", consistent with Good 1967 /
  Blackwell 1953. Exact history is strictly necessary exactly where the theory says (long-tail recall).
- Does NOT: anything about continuous-field generalization (LM01's regime); learned statistics (all statistics here are
  hand-specified families).
- The learned causal-state tracker (the missing arm) is the next build step. It is the case where a learner must
  DISCOVER the right compression.

## Implications for ARC3

- For LM01, EXACT_RETENTION_PAYS or BOUNDED_SUFFICES should be read as statements about estimation variance and
  statistic choice, not about information being harmful.
- T03 (availability vs accessibility): in these worlds, excess history hurt only by estimation variance (over-order
  statistics, short windows), never at fixed statistic with more data. The accessibility case needs a world where
  computation, not data, limits (lit T18 PRG / rotated nuisance; T19 streaming parity).
