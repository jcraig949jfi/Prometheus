# C3-3 design (built 2026-09-10 from Harmonia 57c259656 item 3; NOT issued)

Code archaeon/producer/campaign_c3_3.py; preflight archaeon/docs/h0h5/C3_3_PREFLIGHT.json
(seed 0, one IC sample per rule, 60 random tables + six genomes + constants + centre rules,
through Vivarium's registered executor).

## What changes from C3-2
- success_criterion = cellwise_majority_match (Herakles 7b8f364cb; Vivarium 30e97ed94):
  accuracy is a per-cell MEAN, and the row carries cellwise_sd_across_ics.
- Two PRIMARIES (3a): location = per-rule mean; dispersion = per-rule sd across ICs.
  Bonferroni across the two.
- Everything else is C3-2's: seed_root 930001 (the same four IC samples), n_ic 100,
  149 cells, 320 steps, six genomes, six baselines, 18 exact-symmetry nulls, and the
  same first 120 random tables -- so every organism is PAIRED across the two criteria.

## Printed before any gate (3f), from the preflight
- random tables: location mean 0.4998, range [0.4893, 0.5126], sd 0.0049;
  dispersion mean 0.072; support size 58 of 60; p_mode 0.033 (R-C3-1 satisfied);
  f = 1.0 (every table non-degenerate: dispersion > 0); granularity 1/14,900
  (348 granules across the random range -- Harmonia's 1/149 caution does not apply).
- corpus = ceil(120 / 1.0) = 120 random tables; expected 12 non-degenerate rules per
  region (popcount deciles of Binomial(128, 1/2), declared analytically); 10 of 10
  regions expected >= 8; expected neighbourhood 108 >= 16.
- 3e: one generating distribution for every random table => the TRUE between-region
  variance ratio is 1.0, inside [0.3333, 3.0]. H2's instrument for C3-3 is the X1
  variance-ratio test across descriptor regions (unit = region); D3 runs as a LEAD
  GENERATOR only, reported with its geometry, denominator, eligible count and
  exchangeability class. The observed per-region ratios on ~6 tables each are F noise
  and are reported, not gated on.
- Named organisms at seed 0: maj 0.597 (measurable here; 0.0 under both masks);
  constants location ~0.5 with dispersion at the 0.5 CEILING (per-IC match is 0 or 1);
  the null under the third criterion is IDENTICAL on maj x three transforms.

## One correction filed to Harmonia (3b)
The constants' dispersion is a structural BOUNDARY, but at the ceiling (0.5), not
zero; random tables sit near 0.10. Substance unchanged (a boundary comparison,
labelled); direction inverted. roles/Harmonia/INBOX_ARCHAEON_C3_3_PREFLIGHT_2026-09-10.md.

## Plan
150 rows: C3-hist 6, C3-base 6, C3-null 18, C3-acq 120; 600 observations; executor
preflight one row per arm: ok_to_issue true. Issue on the operator's word after
Harmonia's go on the preflight numbers.
