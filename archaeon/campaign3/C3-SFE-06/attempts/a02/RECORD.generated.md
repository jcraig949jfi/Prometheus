# C3-SFE-06 -- basin share out-of-family test

## A. STARTUP (preregistration; sealed sha256:fdeef8d7797396f4bcb613307307c486982a5b2a0fef18cf799a936d227f071b)

- experiment ID: C3-SFE-06
- parents: C2-SFE-08
- QUESTION: Over 12 opcode orderings (encodings) of two exhaustive 25^4 opcode spaces on a WSE cell (W0 4-bit, fixed battery) and two climbers unlike campaign 2's, does basin share rank-correlate with evaluations-to-threshold (expected negative, |rho| >= 0.5)?
- PARENT EVIDENCE: C2-SFE-08 (CA block-output evaluator, best-of-lambda climb, 52 rows): basin_share rho -0.59, deceptive_share +0.57, accessible variation -0.23.
- WHY THIS SLOT IS STILL WORTH SPENDING: A geometry that predicts search only on the evaluator/climber pair that produced it is a description of one landscape; the campaign needs to know whether basin share is a general instrument before C3-SFE-07 spends compute on manipulating it.
- ASSAY CAPABILITY REQUIREMENT: each score table contains threshold genotypes (threshold_share > 0) and the identity encoding's climbers hit the threshold in >= 1 of 3 seeds on each table (POSITIVE_CONTROL_FAILED otherwise); threshold_share must be identical across encodings of one table
- POSITIVE CONTROL: identity ordering, both climbers, both tables
- REACHABILITY ESTIMATE:
    {"note": "exhaustive space; the reachability table does not apply; skeleton solvers found by reconnaissance (seeds 2 and 6, minimized to 4 instructions)"}
- ARMS:
    - class_grouped
    - identity
    - perm_1
    - perm_10
    - perm_2
    - perm_3
    - perm_4
    - perm_5
    - perm_6
    - perm_7
    - perm_8
    - perm_9
- COMMON-RANDOM-NUMBERS POLICY: one score table per skeleton shared by every encoding; climber seeds keyed on (search seed, encoding); neighbourhood moves keyed on the encoding
- BUDGET:
    {"climber_a": "first-improvement, 8 restarts x 400 steps", "climber_b": "(mu+lambda) N=50 G=40 elitism 4 tournament 4", "genotypes_per_table": 390625, "n_encodings": 12, "neighbours": 16, "search_seeds": [1, 2, 3], "tables": ["skelA", "skelB"], "threshold": 0.875}
- PRIMARY OBSERVABLE: log10(median evaluations to threshold, censored) per encoding x table x climber; Spearman rho of basin_share with it
- CLAIM CEILING: weak: two skeleton spaces, one cell, two climbers; a negative kills basin share as a general predictor for this substrate
- FALSIFICATION CONDITION: rho(basin_share, log_first_hit) > -0.5 over all rows => basin share does not generalize; per-climber rho reported
- KILL CONDITION: positive control fails on either table; or every encoding has identical geometry (the neighbourhood definition would then be inert)
- TYPED FAILURE CONDITIONS:
    - POSITIVE_CONTROL_FAILED
    - INSTRUMENT_FAILURE (threshold_share differs across encodings of one table)
- EXPECTED MACHINE TELEMETRY:
    - seven geometry statistics per encoding x table
    - first hits per seed per climber
    - rho table (all rows; per climber)
- MACHINE CHANGES EXERCISED:
    - B rank_correlation primary
    - I
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (queue slot 6)
- decl (machine-read by archaeon.wse.states): {"positive_control": {"arm": "identity", "metric": "hits", "min": 1, "min_rows": 2}, "primary": {"expected_sign": -1, "min_abs_rho": 0.5, "type": "rank_correlation", "x": "basin_share", "y": "log_first_hit"}, "statistics": ["accessible_variation", "useful_variation", "local_improvement_prob", "basin_share", "greedy_path_len", "deceptive_share", "mean_dist_to_threshold"]}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a02); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=CAPABLE_NEGATIVE
    a02  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=POSITIVE_CONTROL_FAILED
- engine: live; worlds 1; artifacts 2; imports 0; records 48; errors 0
- timings (s): climbs_s=57.75, geometry_s=52.31, records_s=45.42, startup_s=0.1, tables_s=348.54, teardown_s=0.16, total_s=453.4
- decisions: D3-011: basin share is the preregistered PRIMARY; the neighbourhood is +-1/+-2 in the encoding's opcode ordering (campaign 2's A_words geometry on the opcode word); two climbers unlike campaign 2's
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / median_first_hit sskelA/first_improvement sskelA/population sskelB/first_improvement sskelB/population    mean    n
    class_grouped             3209    2001    3209    2001  2605.000    4
    identity                  3209    2001    3209    2001  2605.000    4
    perm_1                    3209    2001    3209    2001  2605.000    4
    perm_10                   3209    2001    3209    2001  2605.000    4
    perm_2                    3209    2001    3209    2001  2605.000    4
    perm_3                    3209    2001    3209    2001  2605.000    4
    perm_4                    3209    2001    3209    1331  2437.500    4
    perm_5                    3209    2001    3209    2001  2605.000    4
    perm_6                    3209    2001    3209    2001  2605.000    4
    perm_7                    3209    2001    3209    2001  2605.000    4
    perm_8                    3209    2001    3209    2001  2605.000    4
    perm_9                    3209    2001    3209    2001  2605.000    4

    arm / basin_share      sskelA/first_improvement sskelA/population sskelB/first_improvement sskelB/population    mean    n
    class_grouped            0.001   0.001   0.003   0.003   0.002    4
    identity                 0.001   0.001   0.002   0.002   0.002    4
    perm_1                   0.001   0.001   0.003   0.003   0.002    4
    perm_10                  0.001   0.001   0.003   0.003   0.002    4
    perm_2                   0.001   0.001   0.003   0.003   0.002    4
    perm_3                   0.001   0.001   0.002   0.002   0.002    4
    perm_4                   0.001   0.001   0.003   0.003   0.002    4
    perm_5                   0.001   0.001   0.002   0.002   0.002    4
    perm_6                   0.001   0.001   0.002   0.002   0.002    4
    perm_7                   0.001   0.001   0.003   0.003   0.002    4
    perm_8                   0.001   0.001   0.002   0.002   0.002    4
    perm_9                   0.001   0.001   0.002   0.002   0.002    4

    arm / deceptive_share  sskelA/first_improvement sskelA/population sskelB/first_improvement sskelB/population    mean    n
    class_grouped            0.356   0.356   0.348   0.348   0.352    4
    identity                 0.344   0.344   0.339   0.339   0.342    4
    perm_1                   0.353   0.353   0.341   0.341   0.347    4
    perm_10                  0.343   0.343   0.328   0.328   0.335    4
    perm_2                   0.354   0.354   0.339   0.339   0.347    4
    perm_3                   0.342   0.342   0.328   0.328   0.335    4
    perm_4                   0.343   0.343   0.330   0.330   0.337    4
    perm_5                   0.343   0.343   0.328   0.328   0.335    4
    perm_6                   0.336   0.336   0.325   0.325   0.331    4
    perm_7                   0.350   0.350   0.335   0.335   0.342    4
    perm_8                   0.334   0.334   0.331   0.331   0.332    4
    perm_9                   0.348   0.348   0.335   0.335   0.341    4

    arm / accessible_variation sskelA/first_improvement sskelA/population sskelB/first_improvement sskelB/population    mean    n
    class_grouped            1.451   1.451   1.439   1.439   1.445    4
    identity                 1.440   1.440   1.429   1.429   1.434    4
    perm_1                   1.449   1.449   1.431   1.431   1.440    4
    perm_10                  1.439   1.439   1.418   1.418   1.429    4
    perm_2                   1.449   1.449   1.429   1.429   1.439    4
    perm_3                   1.437   1.437   1.418   1.418   1.428    4
    perm_4                   1.438   1.438   1.420   1.420   1.429    4
    perm_5                   1.439   1.439   1.418   1.418   1.428    4
    perm_6                   1.432   1.432   1.415   1.415   1.423    4
    perm_7                   1.445   1.445   1.425   1.425   1.435    4
    perm_8                   1.430   1.430   1.420   1.420   1.425    4
    perm_9                   1.444   1.444   1.424   1.424   1.434    4

    arm / local_improvement_prob sskelA/first_improvement sskelA/population sskelB/first_improvement sskelB/population    mean    n
    class_grouped            0.034   0.034   0.034   0.034   0.034    4
    identity                 0.034   0.034   0.034   0.034   0.034    4
    perm_1                   0.035   0.035   0.035   0.035   0.035    4
    perm_10                  0.035   0.035   0.035   0.035   0.035    4
    perm_2                   0.034   0.034   0.034   0.034   0.034    4
    perm_3                   0.035   0.035   0.035   0.035   0.035    4
    perm_4                   0.035   0.035   0.035   0.035   0.035    4
    perm_5                   0.035   0.035   0.034   0.034   0.035    4
    perm_6                   0.036   0.036   0.036   0.036   0.036    4
    perm_7                   0.036   0.036   0.036   0.036   0.036    4
    perm_8                   0.035   0.035   0.035   0.035   0.035    4
    perm_9                   0.035   0.035   0.034   0.034   0.034    4

- typed states fired: ['POSITIVE_CONTROL_FAILED']
    POSITIVE_CONTROL_FAILED  {"arm": "identity", "metric": "hits", "min": 1, "rows": 4, "rows_meeting": 1, "values": [0, 0, 0, 1]}
- disposition candidate (machine): POSITIVE_CONTROL_FAILED -- assay precondition failed; the scientific question was not posed
- claim ceiling (machine): none; preregistered ceiling: weak: two skeleton spaces, one cell, two climbers; a negative kills basin share as a general predictor for this substrate

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"basin": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C3-SFE-06

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: POSITIVE_CONTROL_FAILED (machine candidate POSITIVE_CONTROL_FAILED). 
