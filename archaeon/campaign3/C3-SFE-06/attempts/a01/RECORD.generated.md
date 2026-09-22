# C3-SFE-06 -- basin share out-of-family test

## A. STARTUP (preregistration; sealed sha256:67e06826e6bb56c621db2eebecd197906c9ff0e4276f3673ab1ba092f3dc1dc3)

- experiment ID: C3-SFE-06
- parents: C2-SFE-08
- QUESTION: Over 4 opcode orderings (encodings) of two exhaustive 25^4 opcode spaces on a WSE cell (W0 4-bit, fixed battery) and two climbers unlike campaign 2's, does basin share rank-correlate with evaluations-to-threshold (expected negative, |rho| >= 0.5)?
- PARENT EVIDENCE: C2-SFE-08 (CA block-output evaluator, best-of-lambda climb, 52 rows): basin_share rho -0.59, deceptive_share +0.57, accessible variation -0.23.
- WHY THIS SLOT IS STILL WORTH SPENDING: A geometry that predicts search only on the evaluator/climber pair that produced it is a description of one landscape; the campaign needs to know whether basin share is a general instrument before C3-SFE-07 spends compute on manipulating it.
- ASSAY CAPABILITY REQUIREMENT: each score table contains threshold genotypes (threshold_share > 0) and the identity encoding's climbers hit the threshold in >= 1 of 1 seeds on each table (POSITIVE_CONTROL_FAILED otherwise); threshold_share must be identical across encodings of one table
- POSITIVE CONTROL: identity ordering, both climbers, both tables
- REACHABILITY ESTIMATE:
    {"note": "exhaustive space; the reachability table does not apply; skeleton solvers found by reconnaissance (seeds 2 and 6, minimized to 4 instructions)"}
- ARMS:
    - class_grouped
    - identity
    - perm_1
    - perm_2
- COMMON-RANDOM-NUMBERS POLICY: one score table per skeleton shared by every encoding; climber seeds keyed on (search seed, encoding); neighbourhood moves keyed on the encoding
- BUDGET:
    {"climber_a": "first-improvement, 8 restarts x 400 steps", "climber_b": "(mu+lambda) N=50 G=40 elitism 4 tournament 4", "genotypes_per_table": 390625, "n_encodings": 4, "neighbours": 16, "search_seeds": [1], "tables": ["skelA", "skelB"], "threshold": 0.875}
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

- attempts: 1 (of record: a00); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=CAPABLE_NEGATIVE
- engine: dry-run; worlds 0; artifacts 0; imports 0; records 0; errors 0
- timings (s): climbs_s=26.81, geometry_s=25.26, records_s=0.0, tables_s=0.0, total_s=27.0
- decisions: D3-011: basin share is the preregistered PRIMARY; the neighbourhood is +-1/+-2 in the encoding's opcode ordering (campaign 2's A_words geometry on the opcode word); two climbers unlike campaign 2's
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / median_first_hit sskelA/first_improvement sskelA/population sskelB/first_improvement sskelB/population    mean    n
    class_grouped               13       7      13       7  10.000    4
    identity                    13       5      13       5   9.000    4
    perm_1                      54       3      54       3  28.500    4
    perm_2                      23      14      23      14  18.500    4

    arm / basin_share      sskelA/first_improvement sskelA/population sskelB/first_improvement sskelB/population    mean    n
    class_grouped            0.985   0.985   0.985   0.985   0.985    4
    identity                 0.984   0.984   0.984   0.984   0.984    4
    perm_1                   0.985   0.985   0.985   0.985   0.985    4
    perm_2                   0.984   0.984   0.984   0.984   0.984    4

    arm / deceptive_share  sskelA/first_improvement sskelA/population sskelB/first_improvement sskelB/population    mean    n
    class_grouped            0.010   0.010   0.010   0.010   0.010    4
    identity                 0.010   0.010   0.010   0.010   0.010    4
    perm_1                   0.009   0.009   0.009   0.009   0.009    4
    perm_2                   0.010   0.010   0.010   0.010   0.010    4

    arm / accessible_variation sskelA/first_improvement sskelA/population sskelB/first_improvement sskelB/population    mean    n
    class_grouped           15.988  15.988  15.988  15.988  15.988    4
    identity                15.988  15.988  15.988  15.988  15.988    4
    perm_1                  15.989  15.989  15.989  15.989  15.989    4
    perm_2                  15.988  15.988  15.988  15.988  15.988    4

    arm / local_improvement_prob sskelA/first_improvement sskelA/population sskelB/first_improvement sskelB/population    mean    n
    class_grouped            0.500   0.500   0.500   0.500   0.500    4
    identity                 0.500   0.500   0.500   0.500   0.500    4
    perm_1                   0.500   0.500   0.500   0.500   0.500    4
    perm_2                   0.500   0.500   0.500   0.500   0.500    4

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- predictor does not rank-correlate at the declared strength/direction
    evidence: {"expected_sign": -1, "min_abs_rho": 0.5, "n": 16, "rho": 0.0491}
- claim ceiling (machine): negative for this predictor on this evaluator; preregistered ceiling: weak: two skeleton spaces, one cell, two climbers; a negative kills basin share as a general predictor for this substrate

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: none (dry run)
- all TERMINATED: n/a

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C3-SFE-06

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). 
