# C2-SFE-08 -- encoding geometry: what predicts search efficiency

## A. STARTUP (preregistration; sealed sha256:cb74e998f0989b28d8b95cc0238b39617da4858f64be5c685952ac4763a0aaf5)

- experiment ID: C2-SFE-08
- parents: SFE-06
- QUESTION: Over 13 encodings of one fixed evaluator (block-output score of the 256 elementary CA rules, 4 score tables), which preregistered neighbourhood statistic rank-correlates with evaluations-to-first-hit of a (1+4) hill climb? PRIMARY: does accessible variation (the parent's proxy) predict efficiency (expected NEGATIVE rho, |rho| >= 0.5)?
- PARENT EVIDENCE: SFE-06: direct first hit 13/53/53 evaluations, balanced 653/97/89 with ~50% more accessible variation, scrambled 971/-/190 (n=3); accessible variation decoupled from navigability (L-023).
- ASSAY CAPABILITY REQUIREMENT: the direct encoding reaches the threshold in >= 2 of 4 tables (else POSITIVE_CONTROL_FAILED: the evaluator has no reachable threshold region for the climb)
- POSITIVE CONTROL: direct encoding hill climb (hits >= 1 of 3 search seeds) on each table
- REACHABILITY ESTIMATE:
    {"note": "not a WSE cell; the CA rule space is enumerated exhaustively (4096 genotypes per encoding); the reachability table does not apply"}
- ARMS:
    - direct
    - balanced_1
    - balanced_2
    - balanced_3
    - balanced_4
    - balanced_5
    - balanced_6
    - scrambled_1
    - scrambled_2
    - scrambled_3
    - scrambled_4
    - scrambled_5
    - scrambled_6
- COMMON-RANDOM-NUMBERS POLICY: one score table per table seed shared by every encoding; hill-climb parents and mutation streams keyed on (table seed, search seed) so every encoding climbs from the same genotypes with the same flip sequence
- BUDGET:
    {"encodings": 13, "lam": 4, "n_cells": 21, "n_ics": 64, "parents": 8, "search_seeds": [1, 2, 3], "steps": 40, "steps_ca": 11, "tables": [1, 2, 3, 4], "threshold": 0.9}
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

- attempts: 2 (of record: a02); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=CAPABLE_NEGATIVE
    a02  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 52; errors 0
- timings (s): geometry_s=0.63, records_s=14.78, startup_s=0.08, teardown_s=0.22, total_s=16.5
- decisions: D2-016: the primary is the PARENT'S proxy (accessible variation); the other six statistics are reported with their rho and none is promoted by the harness
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / median_first_hit      s1      s2      s3      s4    mean    n
    balanced_1                 669     552      33     677  482.750    4
    balanced_2                 810     661     178     278  481.750    4
    balanced_3                 488     355     488     246  394.250    4
    balanced_4                 488     166     170     359  295.750    4
    balanced_5                 709     359     331     166  391.250    4
    balanced_6                 170     496     331     721  429.500    4
    direct                      37      41      41      61  45.000    4
    scrambled_1                649     624     544     540  589.250    4
    scrambled_2                500    1289     492    1184  866.250    4
    scrambled_3                343     331     182     971  456.750    4
    scrambled_4                327    1289     343     331  572.500    4
    scrambled_5               1289    1289    1289    1289  1289.000    4
    scrambled_6               1289    1289    1289     327  1048.500    4

    arm / accessible_variation      s1      s2      s3      s4    mean    n
    balanced_1              11.761  11.761  11.761  11.761  11.761    4
    balanced_2              11.754  11.754  11.754  11.754  11.754    4
    balanced_3              11.748  11.748  11.748  11.748  11.748    4
    balanced_4              11.755  11.755  11.755  11.755  11.755    4
    balanced_5              11.747  11.747  11.747  11.747  11.747    4
    balanced_6              11.734  11.734  11.734  11.734  11.734    4
    direct                   9.000   9.000   9.000   9.000   9.000    4
    scrambled_1              9.000   9.000   9.000   9.000   9.000    4
    scrambled_2              9.000   9.000   9.000   9.000   9.000    4
    scrambled_3              9.000   9.000   9.000   9.000   9.000    4
    scrambled_4              9.000   9.000   9.000   9.000   9.000    4
    scrambled_5              9.000   9.000   9.000   9.000   9.000    4
    scrambled_6              9.000   9.000   9.000   9.000   9.000    4

    arm / basin_share           s1      s2      s3      s4    mean    n
    balanced_1               0.175   0.173   0.180   0.181   0.177    4
    balanced_2               0.157   0.165   0.162   0.165   0.162    4
    balanced_3               0.167   0.159   0.172   0.161   0.165    4
    balanced_4               0.176   0.176   0.182   0.178   0.178    4
    balanced_5               0.187   0.186   0.180   0.181   0.183    4
    balanced_6               0.183   0.184   0.184   0.176   0.182    4
    direct                   0.375   0.375   0.410   0.344   0.376    4
    scrambled_1              0.090   0.094   0.090   0.094   0.092    4
    scrambled_2              0.121   0.133   0.121   0.129   0.126    4
    scrambled_3              0.117   0.129   0.113   0.082   0.110    4
    scrambled_4              0.113   0.109   0.109   0.105   0.109    4
    scrambled_5              0.078   0.090   0.074   0.074   0.079    4
    scrambled_6              0.074   0.066   0.066   0.070   0.069    4

    arm / deceptive_share       s1      s2      s3      s4    mean    n
    balanced_1               0.684   0.690   0.681   0.678   0.683    4
    balanced_2               0.708   0.703   0.704   0.701   0.704    4
    balanced_3               0.694   0.707   0.693   0.706   0.700    4
    balanced_4               0.682   0.688   0.679   0.682   0.682    4
    balanced_5               0.673   0.677   0.683   0.682   0.679    4
    balanced_6               0.677   0.683   0.679   0.685   0.681    4
    direct                   0.445   0.453   0.398   0.469   0.441    4
    scrambled_1              0.734   0.746   0.734   0.731   0.736    4
    scrambled_2              0.719   0.707   0.727   0.711   0.716    4
    scrambled_3              0.703   0.691   0.707   0.738   0.710    4
    scrambled_4              0.719   0.715   0.734   0.734   0.726    4
    scrambled_5              0.746   0.727   0.738   0.746   0.739    4
    scrambled_6              0.746   0.731   0.742   0.750   0.742    4

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- predictor does not rank-correlate at the declared strength/direction
    evidence: {"expected_sign": -1, "min_abs_rho": 0.5, "n": 52, "rho": -0.2272}
- claim ceiling (machine): negative for this predictor on this evaluator; preregistered ceiling: weak; one evaluator family, one climber; a capable negative for a statistic = it does not predict this climber's efficiency here

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

Assay capable: the direct encoding hit the threshold in 3/3 search seeds on all 4 tables (median first hit 37-61 evaluations). PRIMARY (the parent's proxy): rho(accessible_variation, log first-hit) = -0.23 over 52 encoding x table rows against the preregistered -0.5; the machine candidate CAPABLE_NEGATIVE is accepted: accessible variation does not predict this climber's efficiency on this evaluator. The exhaustive geometry says why, and it separates the parent's puzzle cleanly. Balanced encodings have MORE accessible variation than direct (11.75 vs 9.00 distinct neighbour rules), more useful variation (5.14 vs 2.89 improving distinct rules) and a higher local improvement probability (0.44 vs 0.24), yet search 9x slower (median 413 vs 45 evaluations): their greedy BASINS of the threshold set are half the size (basin_share 0.18 vs 0.38), their deceptive share is higher (0.69 vs 0.44: genotypes with an improving neighbour whose best-improvement path ends below threshold) and their greedy paths are shorter (1.47 vs 2.30 steps: the climb stalls early). Scrambled encodings keep direct's local statistics exactly (accessible 9.00: a rule permutation cannot change neighbourhood multiplicities) and are the slowest (median 804; 11 of 24 rows censored at the budget) with the smallest basins (0.10) and the most deception (0.73). Across all 52 rows the statistics that rank-correlate with efficiency at |rho| >= 0.5 are the GLOBAL ones -- basin_share (-0.59), greedy_path_len (-0.59, longer sustained climbs go with larger basins) and deceptive_share (+0.57) -- while every LOCAL variation statistic is below |0.25| (useful_variation -0.12, local_improvement_prob -0.13). Exploratory: within a kind the correlations weaken (balanced n=24: local_improvement_prob -0.30 is the largest; scrambled: mean_dist_to_threshold +0.53, basin -0.44), so the between-kind difference carries most of the signal, and 'basin share' is the best single description of what the parent called navigability. Must NOT be claimed: that basin share predicts efficiency for other climbers or evaluators (one climber, one evaluator family, 4 tables); that local improvement probability is irrelevant within an encoding family.

## D. TEARDOWN (generated)

- worlds: {"geometry": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-08

Zero engine errors; 1 world; 52 records; the geometry table published as one observation artifact; threshold_share was 0.0078 (2 of 256 rules) on every row: the decoder-totality check passed (every encoding maps 16 genotypes to each rule). The rank-correlation primary is a new machine capability (states.spearman + primary type rank_correlation) exercised for the first time. Bench notes: (1) the exhaustive geometry of 4096 genotypes x 12 neighbours per encoding took 0.63 s for all 52 rows -- the cheap measurement that should precede any search comparison on a finite genotype space; (2) the hill climb's censoring at budget+1 (1289) compresses the slow tail; a larger budget would separate the censored scrambled rows (MISSING_TELEMETRY, minor).

## F. LANDSCAPE / GRADIENT NOTES

On the block-output evaluator the threshold region is 2 of 256 rules (32 of 4096 genotypes under every total encoding). Direct: 38% of genotypes sit in a greedy basin of those 32 and the mean Hamming distance to the nearest threshold genotype is 3.25; balanced: 18% and 2.51 (closer on average, but the greedy paths are trapped: deception 0.69); scrambled: 10% and 3.42. Deceptive share is the landscape feature the parent's proxy missed: an encoding can hand the climber more distinct improving neighbours per step and still route most of them into local optima below threshold. Search efficiency followed the basin, not the neighbourhood.

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). Assay capable (direct 12/12 hits); over 13 encodings x 4 tables the parent's proxy (accessible variation) does not rank-correlate with efficiency (rho -0.23 vs -0.5 declared). Reported beside it, unpromoted: basin_share -0.59, greedy_path_len -0.59, deceptive_share +0.57 are the statistics that track this climber's efficiency.
