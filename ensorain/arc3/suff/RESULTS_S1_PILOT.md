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

## Addendum: learned compression (hmm_learner.py; results/hmm_pilot.json; 8 seeds, T = 4000)

Excess vs Bayes (whole stream / 2nd half):

| world | HMM2 full | HMM3 | HMM4 | HMM2 W256 | HMM2 W1024 | STAT_k6 |
|---|---|---|---|---|---|---|
| W3 Even process | .025 / .000 | .027 / .001 | .028 / .001 | .026 / .001 | .025 / .001 | .060 / .040 |
| W4 SNS | .021 / .000 | .021 / .001 | .021 / .001 | .023 / .003 | .021 / .001 | .020 / .005 |
| W2 order-2 Markov | .171 / .096 | .055 / .016 | .044 / .004 | .200 / .190 | .228 / .206 | .016 / .008 |

- A learned bounded state that CAN represent the causal-state compression reaches Bayes. It needs only a short window
  of exact history (256 symbols) to discover it, and it beats the best window statistic, which retains ~1,500 bits.
- With too few states it fails (order-2 Markov with 2 states): model-class mismatch, not retention.

## Three-loci decomposition (loci.py; results/loci.json; analytic resource profiles x measured excess)

Per world, the best learner of each compression locus: excess (bits/symbol) | stored raw bits | persistent hypothesis
bits | transient readout-state bits | readout ops per query.
- W2 order 3:
  - storage-statistic STAT_k3: .000 | 3 | 191 | 0 | 3
  - verbatim + readout-summary VERB_SUM_B4096_k3: .000 | 4096 | 0 | 192 | 12288
  - verbatim + nonparametric NEAREST: .075 | 4096 | 0 | 0 | 49152
- W3 Even process:
  - learned hypothesis HMM2_EM: .025 (2nd half .000) | 4000 | 320 | 0 | 4
  - storage-statistic STAT_k6: .060 | 6 | 1532 | 0 | 6
  - verbatim + summary: .060 | 4096 | 0 | 1536 | 24576
- W4 SNS: storage-statistic STAT_k2 .006 = verbatim + summary .006. HMM2 .021 over the whole stream (2nd half ~.000).

Readings (answer-keyed; calibration of concepts):
1. When the SAME statistic is computed, compression at STORAGE and compression at READOUT give IDENTICAL accuracy. The
   locus decides only the resource profile: storage costs ~100 hypothesis bits and O(k) ops; readout costs a 4096-bit
   store and ~10^4 ops per query. Here "where compression happens" is a memory-for-compute trade, not an accuracy
   question.
2. Removing compression from the readout (nonparametric suffix readout over the same verbatim store) COSTS accuracy
   (.04-.17 excess): a readout must contract to generalize. "Lossless storage is not absence of compression"
   (directive baseline), with numbers.
3. The HYPOTHESIS locus pays only where fixed statistics cannot represent the needed compression (Even process): a
   320-bit learned state beats a 1,532-bit window statistic. This is the answer-keyed version of "discovering what can
   be discarded".
