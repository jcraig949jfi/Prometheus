# C2-SFE-08 -- encoding geometry: what predicts search efficiency

## A. STARTUP (preregistration; sealed sha256:9d6e635e549f68d55a8ec67ebda78b717b1171588e11261d6a774df540881300)

- experiment ID: C2-SFE-08
- parents: SFE-06
- QUESTION: Over 3 encodings of one fixed evaluator (block-output score of the 256 elementary CA rules, 2 score tables), which preregistered neighbourhood statistic rank-correlates with evaluations-to-first-hit of a (1+4) hill climb? PRIMARY: does accessible variation (the parent's proxy) predict efficiency (expected NEGATIVE rho, |rho| >= 0.5)?
- PARENT EVIDENCE: SFE-06: direct first hit 13/53/53 evaluations, balanced 653/97/89 with ~50% more accessible variation, scrambled 971/-/190 (n=3); accessible variation decoupled from navigability (L-023).
- ASSAY CAPABILITY REQUIREMENT: the direct encoding reaches the threshold in >= 2 of 2 tables (else POSITIVE_CONTROL_FAILED: the evaluator has no reachable threshold region for the climb)
- POSITIVE CONTROL: direct encoding hill climb (hits >= 1 of 1 search seeds) on each table
- REACHABILITY ESTIMATE:
    {"note": "not a WSE cell; the CA rule space is enumerated exhaustively (4096 genotypes per encoding); the reachability table does not apply"}
- ARMS:
    - direct
    - balanced_1
    - scrambled_1
- COMMON-RANDOM-NUMBERS POLICY: one score table per table seed shared by every encoding; hill-climb parents and mutation streams keyed on (table seed, search seed) so every encoding climbs from the same genotypes with the same flip sequence
- BUDGET:
    {"encodings": 3, "lam": 4, "n_cells": 21, "n_ics": 64, "parents": 8, "search_seeds": [1], "steps": 40, "steps_ca": 11, "tables": [1, 2], "threshold": 0.9}
- PRIMARY OBSERVABLE: log10(median evaluations to first hit, censored at budget+1) per encoding x table; rank correlation with each statistic over all rows
- CLAIM CEILING: weak; one evaluator family, one climber; a capable negative for a statistic = it does not predict this climber's efficiency here
- FALSIFICATION CONDITION: rho(accessible_variation, log_first_hit) > -0.5 => the parent's proxy does not predict; every other statistic reported with its rho
- TYPED FAILURE CONDITIONS:
    - POSITIVE_CONTROL_FAILED (direct hits in < 2 tables)
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - six geometry statistics + threshold_share per row (threshold_share must be identical across encodings: a decoder-totality check)
    - first hits per search seed
    - rho table for every statistic
- MACHINE CHANGES EXERCISED:
    - B (rank_correlation primary in states)
    - I
- decl (machine-read by archaeon.wse.states): {"positive_control": {"arm": "direct", "metric": "hits", "min": 1, "min_rows": 2}, "primary": {"expected_sign": -1, "min_abs_rho": 0.5, "type": "rank_correlation", "x": "accessible_variation", "y": "log_first_hit"}, "statistics": ["accessible_variation", "useful_variation", "local_improvement_prob", "basin_share", "greedy_path_len", "deceptive_share", "mean_dist_to_threshold"]}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a00); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=CAPABLE_NEGATIVE
- engine: dry-run; worlds 0; artifacts 0; imports 0; records 0; errors 0
- timings (s): geometry_s=0.21, records_s=0.0, total_s=0.4
- decisions: D2-016: the primary is the PARENT'S proxy (accessible variation); the other six statistics are reported with their rho and none is promoted by the harness
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / median_first_hit      s1      s2    mean    n
    balanced_1                  21     552  286.500    2
    direct                      37      41  39.000    2
    scrambled_1                117     624  370.500    2

    arm / accessible_variation      s1      s2    mean    n
    balanced_1              11.761  11.761  11.761    2
    direct                   9.000   9.000   9.000    2
    scrambled_1              9.000   9.000   9.000    2

    arm / local_improvement_prob      s1      s2    mean    n
    balanced_1               0.438   0.434   0.436    2
    direct                   0.242   0.235   0.238    2
    scrambled_1              0.290   0.291   0.290    2

    arm / basin_share           s1      s2    mean    n
    balanced_1               0.175   0.173   0.174    2
    direct                   0.375   0.375   0.375    2
    scrambled_1              0.090   0.094   0.092    2

    arm / deceptive_share       s1      s2    mean    n
    balanced_1               0.684   0.690   0.687    2
    direct                   0.445   0.453   0.449    2
    scrambled_1              0.734   0.746   0.740    2

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- predictor does not rank-correlate at the declared strength/direction
    evidence: {"expected_sign": -1, "min_abs_rho": 0.5, "n": 6, "rho": -0.207}
- claim ceiling (machine): negative for this predictor on this evaluator; preregistered ceiling: weak; one evaluator family, one climber; a capable negative for a statistic = it does not predict this climber's efficiency here

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: none (dry run)
- all TERMINATED: n/a

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-08

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). 
