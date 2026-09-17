# C3-SFE-06 -- basin share out-of-family test

## A. STARTUP (preregistration; sealed sha256:d2396af40c668b43f0a12a378a6f49a375ad0d94d703c3e0959f56149d838db2)

- experiment ID: C3-SFE-06
- parents: C2-SFE-08
- QUESTION: Over 4 opcode orderings (encodings) of two exhaustive 25^4 opcode spaces on a WSE cell (W0 4-bit, fixed battery) and two climbers unlike campaign 2's, does basin share rank-correlate with evaluations-to-threshold (expected negative, |rho| >= 0.5)?
- PARENT EVIDENCE: C2-SFE-08 (CA block-output evaluator, best-of-lambda climb, 52 rows): basin_share rho -0.59, deceptive_share +0.57, accessible variation -0.23.
- WHY THIS SLOT IS STILL WORTH SPENDING: A geometry that predicts search only on the evaluator/climber pair that produced it is a description of one landscape; the campaign needs to know whether basin share is a general instrument before C3-SFE-07 spends compute on manipulating it.
- ASSAY CAPABILITY REQUIREMENT: the identity encoding's climbers hit the table's threshold in >= 1 of 2 seeds on each table x climber (POSITIVE_CONTROL_FAILED otherwise); threshold_share must be identical across encodings of one table. a02 FAILED this with a fixed 0.875 threshold: only 9 of 390,625 genotypes (2.3e-05) reach it on skelA, so a 2,000-3,200 evaluation climb cannot find it and the primary observable was censored in 44 of 48 rows. a03 therefore sets the threshold PER TABLE by a rule fixed before the run: the HIGHEST battery level at least 0.001 of genotypes reach
- POSITIVE CONTROL: identity ordering, both climbers, both tables, at each table's adaptive threshold (climb budgets widened to 20 restarts x 400 steps and N=50 x G=80)
- REACHABILITY ESTIMATE:
    {"note": "exhaustive space; the reachability table does not apply; skeleton solvers found by reconnaissance (seeds 2 and 6, minimized to 4 instructions)"}
- ARMS:
    - class_grouped
    - identity
    - perm_1
    - perm_2
- COMMON-RANDOM-NUMBERS POLICY: one score table per skeleton shared by every encoding; climber seeds keyed on (search seed, encoding); neighbourhood moves keyed on the encoding
- BUDGET:
    {"climber_a": "first-improvement, 20 restarts x 400 steps", "climber_b": "(mu+lambda) N=50 G=80 elitism 4 tournament 4", "genotypes_per_table": 390625, "n_encodings": 4, "neighbours": 16, "search_seeds": [1, 2], "tables": ["skelA", "skelB"], "threshold_fixed_a02": 0.875, "threshold_rule": "highest level reached by >= 0.001 of genotypes, per table"}
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

- attempts: 4 (of record: a02); resumed_from: 3; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=CAPABLE_NEGATIVE
    a02  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=POSITIVE_CONTROL_FAILED
    a03  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=CAPABLE_NEGATIVE
    a04  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=CAPABLE_NEGATIVE
- engine: dry-run; worlds 0; artifacts 0; imports 0; records 0; errors 0
- timings (s): climbs_s=24.9, geometry_s=23.2, records_s=0.0, tables_s=0.0, total_s=168.2
- decisions: D3-021: the target level is chosen from the table's own score distribution (highest level reached by >= 0.1%% of genotypes) because a fixed 0.875 is reached by 9 of 390,625 genotypes and cannot be found at any affordable climb budget (a02 POSITIVE_CONTROL_FAILED); the level is fixed per table before any climbing and shared by every encoding, D3-011: basin share is the preregistered PRIMARY; the neighbourhood is +-1/+-2 in the encoding's opcode ordering (campaign 2's A_words geometry on the opcode word); two climbers unlike campaign 2's
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / median_first_hit sskelA/first_improvement sskelA/population sskelB/first_improvement sskelB/population    mean    n
    class_grouped             8021     301    8021     301  4161.000    4
    identity                  8021    4001    8021    4001  6011.000    4
    perm_1                    8021     651    8021     651  4336.000    4
    perm_2                    8021    3851    8021    3851  5936.000    4

    arm / basin_share      sskelA/first_improvement sskelA/population sskelB/first_improvement sskelB/population    mean    n
    class_grouped            0.038   0.038   0.038   0.038   0.038    4
    identity                 0.038   0.038   0.038   0.038   0.038    4
    perm_1                   0.036   0.036   0.036   0.036   0.036    4
    perm_2                   0.038   0.038   0.038   0.038   0.038    4

    arm / deceptive_share  sskelA/first_improvement sskelA/population sskelB/first_improvement sskelB/population    mean    n
    class_grouped            0.904   0.904   0.904   0.904   0.904    4
    identity                 0.905   0.905   0.905   0.905   0.905    4
    perm_1                   0.906   0.906   0.906   0.906   0.906    4
    perm_2                   0.904   0.904   0.904   0.904   0.904    4

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
    evidence: {"expected_sign": -1, "min_abs_rho": 0.5, "n": 16, "rho": 0.0}
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
