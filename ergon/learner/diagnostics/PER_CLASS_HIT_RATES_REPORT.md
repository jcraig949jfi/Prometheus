# Per-Class Mutation Hit Rates

**Computed:** 2026-05-05  
**By:** Charon (outside auditor)  
**Corpus:** a149_real (4 ledgers, 12 seed-records, ~24K substrate-passes)  

---

## Definitions

- **promote**: (substrate-PASS records of class) / (actual scheduler attempts of class). Ergon a149: substrate-pass = lift >= 2.0 AND match_size >= 3.
- **archive_fill**: (distinct canonical_predicate_hash values of class) / (actual scheduler attempts of class). Predicate-novelty proxy for MAP-Elites cell-fill.
- **near_miss**: (substrate-PASS records of class with matched_kill_rate ∈ (0, 1)) / (actual scheduler attempts of class). Predicate captured a partial-kill cluster. Adaptation of KILL_VECTOR_SPEC near-miss semantics.

---

## Aggregate per class (12 seed-records, all configs pooled)

Bootstrap 95% CIs (2000 resamples). `n_seed_obs=12` for all classes.

| class | promote (mean [CI]) | archive_fill (mean [CI]) | near_miss (mean [CI]) | typical n_attempts/seed |
|---|---|---|---|---|
| structural | 0.3335 [0.3219, 0.3438] | 0.0968 [0.0808, 0.1132] | 0.2746 [0.2673, 0.2823] | ~4504.5 (range 1919-9474) |
| symbolic | 0.1215 [0.1054, 0.1369] | 0.0513 [0.0447, 0.0587] | 0.0895 [0.0765, 0.1038] | ~1419.0 (range 704-2205) |
| anti_prior | 0.0345 [0.0281, 0.0414] | 0.0214 [0.0182, 0.0251] | 0.0305 [0.0245, 0.0375] | ~1003.5 (range 481-1547) |
| uniform | 0.0485 [0.0469, 0.0500] | 0.0225 [0.0212, 0.0239] | 0.0409 [0.0397, 0.0422] | ~1238.0 (range 314-4489) |
| structured_null | 0.0240 [0.0205, 0.0272] | 0.0237 [0.0202, 0.0266] | 0.0216 [0.0172, 0.0255] | ~637.0 (range 312-974) |

## Per-config (regime-separated)

### trial_3_iter28_a149_u05_canonical

weights: `{"structural": 0.65, "symbolic": 0.15, "uniform": 0.05, "structured_null": 0.05, "anti_prior": 0.1}`  
n_episodes/seed: 5000, n_seeds: 3

| class | promote | archive_fill | near_miss | n_attempts/seed |
|---|---|---|---|---|
| structural | 0.3438 [0.3371, 0.3476] | 0.0673 [0.0621, 0.0712] | 0.2808 [0.2670, 0.2935] | ~3139 |
| symbolic | 0.1206 [0.0852, 0.1617] | 0.0424 [0.0394, 0.0481] | 0.0885 [0.0709, 0.1209] | ~736 |
| anti_prior | 0.0453 [0.0208, 0.0615] | 0.0267 [0.0146, 0.0330] | 0.0419 [0.0208, 0.0596] | ~485 |
| uniform | 0.0506 [0.0500, 0.0510] | 0.0258 [0.0250, 0.0269] | 0.0403 [0.0389, 0.0414] | ~320 |
| structured_null | 0.0241 [0.0191, 0.0277] | 0.0241 [0.0191, 0.0277] | 0.0210 [0.0096, 0.0277] | ~314 |

### trial_3_iter28_a149_u30_broad

weights: `{"structural": 0.4, "symbolic": 0.15, "uniform": 0.3, "structured_null": 0.05, "anti_prior": 0.1}`  
n_episodes/seed: 5000, n_seeds: 3

| class | promote | archive_fill | near_miss | n_attempts/seed |
|---|---|---|---|---|
| structural | 0.3064 [0.3007, 0.3173] | 0.0736 [0.0644, 0.0903] | 0.2607 [0.2600, 0.2612] | ~1956 |
| symbolic | 0.1437 [0.1247, 0.1591] | 0.0428 [0.0376, 0.0508] | 0.1107 [0.0900, 0.1364] | ~722 |
| anti_prior | 0.0263 [0.0200, 0.0322] | 0.0184 [0.0140, 0.0227] | 0.0223 [0.0180, 0.0284] | ~500 |
| uniform | 0.0503 [0.0456, 0.0532] | 0.0208 [0.0192, 0.0221] | 0.0437 [0.0416, 0.0458] | ~1505 |
| structured_null | 0.0178 [0.0095, 0.0248] | 0.0178 [0.0095, 0.0248] | 0.0147 [0.0063, 0.0217] | ~316 |

### trial_3_iter31_a149_u05_15k

weights: `{"structural": 0.65, "symbolic": 0.15, "uniform": 0.05, "structured_null": 0.05, "anti_prior": 0.1}`  
n_episodes/seed: 15000, n_seeds: 3

| class | promote | archive_fill | near_miss | n_attempts/seed |
|---|---|---|---|---|
| structural | 0.3521 [0.3389, 0.3600] | 0.1152 [0.1020, 0.1223] | 0.2845 [0.2593, 0.3009] | ~9445 |
| symbolic | 0.0949 [0.0746, 0.1203] | 0.0494 [0.0416, 0.0572] | 0.0685 [0.0550, 0.0873] | ~2162 |
| anti_prior | 0.0355 [0.0291, 0.0393] | 0.0193 [0.0157, 0.0227] | 0.0321 [0.0250, 0.0373] | ~1496 |
| uniform | 0.0461 [0.0448, 0.0478] | 0.0229 [0.0213, 0.0254] | 0.0389 [0.0375, 0.0396] | ~959 |
| structured_null | 0.0276 [0.0198, 0.0327] | 0.0265 [0.0198, 0.0306] | 0.0258 [0.0167, 0.0306] | ~959 |

### trial_3_iter31_a149_u30_15k

weights: `{"structural": 0.4, "symbolic": 0.15, "uniform": 0.3, "structured_null": 0.05, "anti_prior": 0.1}`  
n_episodes/seed: 15000, n_seeds: 3

| class | promote | archive_fill | near_miss | n_attempts/seed |
|---|---|---|---|---|
| structural | 0.3316 [0.3190, 0.3475] | 0.1309 [0.1213, 0.1461] | 0.2723 [0.2689, 0.2751] | ~5904 |
| symbolic | 0.1269 [0.1102, 0.1383] | 0.0705 [0.0656, 0.0748] | 0.0904 [0.0707, 0.1016] | ~2197 |
| anti_prior | 0.0309 [0.0291, 0.0341] | 0.0213 [0.0190, 0.0241] | 0.0256 [0.0246, 0.0268] | ~1524 |
| uniform | 0.0468 [0.0454, 0.0481] | 0.0207 [0.0201, 0.0212] | 0.0406 [0.0386, 0.0428] | ~4430 |
| structured_null | 0.0267 [0.0236, 0.0301] | 0.0263 [0.0236, 0.0291] | 0.0249 [0.0226, 0.0270] | ~963 |

## Honesty notes

- Denominators come from deterministic scheduler simulation (OperatorScheduler replay with seed + weights), not from persisted attempt counts. The engine's operator_call_counts is computed at runtime but not persisted in the ledger or trial_results.json. Replay agrees with weights × n_episodes within multinomial variance for the warm-up period; min-share enforcement adjusts shares for post-warm-up episodes (see scheduler.py).
- PROMOTE rate uses Ergon's substrate-pass criterion (lift >= 2.0 AND match_size >= 3). Strict kernel PROMOTE (F1+F6+F9+F11 all CLEAR) is not applicable to predicate search: predicates aren't tested by the battery; corpus records are. Per engine.py docstring, strict kernel PROMOTE at Path B is empirically 0/30000 — different metric, different pipeline.
- Archive cell-fill rate is approximated by distinct canonical_predicate_hash per class. The MAP-Elites archive's true cell-fill (cell-coordinate-based) is computed at archive.submit() time but not persisted. The proxy may undercount classes that explore many cells with the same predicate or overcount classes that produce predicate variants without exploring new cells. Trial 2's archive_n_cells (per-seed total) is consistent with these numbers in aggregate but cannot be broken down per-class without re-running.
- Near-miss rate adapts KILL_VECTOR_SPEC's 'cleared k of 4 falsifiers, k>=3' to predicate-search. The adaptation: predicate captured a partial-kill cluster (matched_kill_rate strictly in (0, 1)). This is qualitatively similar — a substrate-PASS event whose match-set isn't unanimous. Don't compare numerically across the Lehmer/Mahler kill_vector pipeline; the semantics of 'falsifier' differ.
- Cross-seed CIs are 95% percentile bootstrap (2000 resamples) over per-seed rates. With 12 seed-records (3 seeds × 4 configs) the CIs are wide; treat any single-config metric (n_seed_observations=3) as exploratory only. n_seed_observations=1 means single-seed; flagged below.
- Aggregate-level CIs pool across configs. This treats u05_canonical and u30_broad as the same regime, which is partly defensible (same corpus, same evaluator, same scheduler module — only weights differ) but also partly conflated (different weight regimes induce different exploration dynamics). The per-config table preserves regime separation; consult both.
- Synthetic-corpus ledgers (iter15, iter18, iter27_uniform30) are excluded. Different corpus, different lift threshold, different baseline kill rate. Mixing would conflate regimes.
- Iter28 had 1/3-seed cluster discovery flagged in CALIBRATION post; treat any class-specific metric where one seed dominates as suspect. Per-seed raw_values are reported in the JSON for verification.
- The scheduler's deterministic replay reconstructs attempts exactly only if trial_3_iter28_a149_real.py used the same min_shares (DEFAULT_MIN_SHARES) and lookback_window (100) as the scheduler module. These are the defaults and the trial code does not override; verified by code-read 2026-05-05.

---

## Substrate use

Numbers above are **internal fuel for the scheduler**, not external claims. Compare classes within the same metric and same config — cross-pipeline comparisons (Ergon vs Lehmer/Mahler) are not supported by the data. Wide CIs (n=12 seed-records) mean any per-class ranking of small effect sizes is unreliable; consider larger n_seeds or longer runs before shifting compute on borderline numbers.

— Charon, outside auditor, 2026-05-05