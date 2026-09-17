# C3-SFE-06 -- basin share out-of-family test

## A. STARTUP (preregistration; sealed sha256:f8465b338ee5178548b9eaffcc780d4eeeebdf18c613ba65ea8c5c92162fd515)

- experiment ID: C3-SFE-06
- parents: C2-SFE-08
- QUESTION: Over 12 opcode orderings (encodings) of two exhaustive 25^4 opcode spaces on a WSE cell (W0 4-bit, fixed battery) and two climbers unlike campaign 2's, does basin share rank-correlate with evaluations-to-threshold (expected negative, |rho| >= 0.5)?
- PARENT EVIDENCE: C2-SFE-08 (CA block-output evaluator, best-of-lambda climb, 52 rows): basin_share rho -0.59, deceptive_share +0.57, accessible variation -0.23.
- WHY THIS SLOT IS STILL WORTH SPENDING: A geometry that predicts search only on the evaluator/climber pair that produced it is a description of one landscape; the campaign needs to know whether basin share is a general instrument before C3-SFE-07 spends compute on manipulating it.
- ASSAY CAPABILITY REQUIREMENT: the identity encoding's climbers hit the table's threshold in >= 1 of 3 seeds on each table x climber (POSITIVE_CONTROL_FAILED otherwise); threshold_share must be identical across encodings of one table. a02 FAILED this with a fixed 0.875 threshold: only 9 of 390,625 genotypes (2.3e-05) reach it on skelA, so a 2,000-3,200 evaluation climb cannot find it and the primary observable was censored in 44 of 48 rows. a03 therefore sets the threshold PER TABLE by a rule fixed before the run: the HIGHEST battery level at least 0.001 of genotypes reach
- POSITIVE CONTROL: identity ordering, both climbers, both tables, at each table's adaptive threshold (climb budgets widened to 20 restarts x 400 steps and N=50 x G=80)
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
    {"climber_a": "first-improvement, 20 restarts x 400 steps", "climber_b": "(mu+lambda) N=50 G=80 elitism 4 tournament 4", "genotypes_per_table": 390625, "n_encodings": 12, "neighbours": 16, "search_seeds": [1, 2, 3], "tables": ["skelA", "skelB"], "threshold_fixed_a02": 0.875, "threshold_rule": "highest level reached by >= 0.001 of genotypes, per table"}
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
    - adaptive per-table threshold (a03)
- REPLACEMENT CONDITION: none
- ANCESTRY (original | replacement): original (queue slot 6); a03 = a02 with a data-derived threshold after POSITIVE_CONTROL_FAILED
- decl (machine-read by archaeon.wse.states): {"positive_control": {"arm": "identity", "metric": "hits", "min": 1, "min_rows": 2}, "primary": {"expected_sign": -1, "min_abs_rho": 0.5, "type": "rank_correlation", "x": "basin_share", "y": "log_first_hit"}, "statistics": ["accessible_variation", "useful_variation", "local_improvement_prob", "basin_share", "greedy_path_len", "deceptive_share", "mean_dist_to_threshold"]}

## B. EXECUTION (generated from receipts)

- attempts: 5 (of record: a05); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=CAPABLE_NEGATIVE
    a02  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=POSITIVE_CONTROL_FAILED
    a03  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=CAPABLE_NEGATIVE
    a04  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=CAPABLE_NEGATIVE
    a05  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=WEAK_POSITIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 48; errors 0
- timings (s): climbs_s=56.84, geometry_s=51.92, records_s=13.79, startup_s=1.17, tables_s=349.26, teardown_s=0.19, total_s=422.1
- decisions: D3-021: the target level is chosen from the table's own score distribution (highest level reached by >= 0.1%% of genotypes) because a fixed 0.875 is reached by 9 of 390,625 genotypes and cannot be found at any affordable climb budget (a02 POSITIVE_CONTROL_FAILED); the level is fixed per table before any climbing and shared by every encoding, D3-011: basin share is the preregistered PRIMARY; the neighbourhood is +-1/+-2 in the encoding's opcode ordering (campaign 2's A_words geometry on the opcode word); two climbers unlike campaign 2's
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / median_first_hit sskelA/first_improvement sskelA/population sskelB/first_improvement sskelB/population    mean    n
    class_grouped             8021     401    1210       1  2408.250    4
    identity                  8021     201    1231       1  2363.500    4
    perm_1                    5224     351       4       1  1395.000    4
    perm_10                   8021     551    1214       1  2446.750    4
    perm_2                    3232     151      11       1  848.750    4
    perm_3                    3638     451     403       1  1123.250    4
    perm_4                    8021     501    2022       1  2636.250    4
    perm_5                    8021    4001     406       1  3107.250    4
    perm_6                    8021     701      47       1  2192.500    4
    perm_7                    4826     501     431       1  1439.750    4
    perm_8                    8021     151     405       1  2144.500    4
    perm_9                    8021     201     409       1  2158.000    4

    arm / basin_share      sskelA/first_improvement sskelA/population sskelB/first_improvement sskelB/population    mean    n
    class_grouped            0.027   0.027   0.435   0.435   0.231    4
    identity                 0.026   0.026   0.425   0.425   0.225    4
    perm_1                   0.030   0.030   0.427   0.427   0.228    4
    perm_10                  0.028   0.028   0.414   0.414   0.221    4
    perm_2                   0.030   0.030   0.425   0.425   0.228    4
    perm_3                   0.030   0.030   0.414   0.414   0.222    4
    perm_4                   0.031   0.031   0.416   0.416   0.223    4
    perm_5                   0.028   0.028   0.413   0.413   0.220    4
    perm_6                   0.030   0.030   0.410   0.410   0.220    4
    perm_7                   0.034   0.034   0.420   0.420   0.227    4
    perm_8                   0.029   0.029   0.416   0.416   0.222    4
    perm_9                   0.030   0.030   0.420   0.420   0.225    4

    arm / deceptive_share  sskelA/first_improvement sskelA/population sskelB/first_improvement sskelB/population    mean    n
    class_grouped            0.331   0.331   0.000   0.000   0.165    4
    identity                 0.320   0.320   0.000   0.000   0.160    4
    perm_1                   0.326   0.326   0.000   0.000   0.163    4
    perm_10                  0.317   0.317   0.000   0.000   0.158    4
    perm_2                   0.326   0.326   0.000   0.000   0.163    4
    perm_3                   0.313   0.313   0.000   0.000   0.157    4
    perm_4                   0.314   0.314   0.000   0.000   0.157    4
    perm_5                   0.317   0.317   0.000   0.000   0.159    4
    perm_6                   0.308   0.308   0.000   0.000   0.154    4
    perm_7                   0.318   0.318   0.000   0.000   0.159    4
    perm_8                   0.307   0.307   0.000   0.000   0.154    4
    perm_9                   0.321   0.321   0.000   0.000   0.160    4

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

- typed states fired: none
- disposition candidate (machine): WEAK_POSITIVE -- predictor rank-correlates in the declared direction at |rho| >= min
    evidence: {"expected_sign": -1, "min_abs_rho": 0.5, "n": 48, "rho": -0.5678}
- claim ceiling (machine): weak; one evaluator family; preregistered ceiling: weak: two skeleton spaces, one cell, two climbers; a negative kills basin share as a general predictor for this substrate

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

DISPOSITION: WEAK_POSITIVE (machine candidate WEAK_POSITIVE). 
