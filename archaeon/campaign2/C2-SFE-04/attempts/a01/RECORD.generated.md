# C2-SFE-04 -- falsify SFE-07's failed-genotype seeding (n=10, battery)

## A. STARTUP (preregistration; sealed sha256:6a9f20570ed2bb68c6ad1024a18c60ac1a8810d1afa9c99d004a1987e8a6f833)

- experiment ID: C2-SFE-04
- parents: SFE-07, SFE-08
- QUESTION: Do genotypes that FAILED W1_d1 (SFE-01's floor organisms), used as the whole generation 0, raise held-out competence on W3_K2 4-bit over the cell's own generation 0 (SFE-07: 2/3 vs 0/3 at n=3), and if so what is the smallest description of the transported thing: instruction order, opcode composition, genome length, 'any evolved floor', or a solved related population?
- PARENT EVIDENCE: SFE-07 attempt 2: failed_A 2/3 footholds vs random 0/3 (N100 G40 E16); SFE-08: length-defined organs of the same lineages at floor. Campaign-1 fill for these sets was harness-seeded (L2-011). Table: W3_K2 4-bit N100 G40 E16 0/3 OBSERVED_UNREACHABLE_AT_BUDGET.
- ASSAY CAPABILITY REQUIREMENT: ANY arm reaches a foothold in >= 1 of 3 seeds (the baseline may be unreachable by premise); every set has >= 24 members
- POSITIVE CONTROL: none separate: the assay is capable iff some arm reaches (target baseline_arm '*'); the random arm measures the cell's own reach
- REACHABILITY ESTIMATE:
    {"W0": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0, 1.0], "budgets": [], "class": "UNESTABLISHED", "freq": null, "k": 0, "n": 0}}, "W3_K2": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0, 0.5615], "budgets": [[100, 40, 16]], "class": "OBSERVED_UNREACHABLE_AT_BUDGET", "freq": 0.0, "k": 0, "n": 3}}, "W7_K2": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0, 0.3903], "budgets": [[200, 60, 16]], "class": "OBSERVED_UNREACHABLE_AT_BUDGET", "freq": 0.0, "k": 0, "n": 6}}}
- ARMS:
    - random
    - failed_A
    - failed_shuffled
    - failed_opcodes
    - length_matched
    - evolved_unrelated
    - evolved_solved
- COMMON-RANDOM-NUMBERS POLICY: default; every set replaces the whole generation 0 through common_fill (tagged); the random arm is the untouched generation 0; derived sets (shuffled / opcodes / length) are deterministic functions of failed_A keyed on the seed
- BUDGET:
    {"E": 4, "G": 6, "G_source": 8, "N": 24, "heldout_episodes": 48, "margin": 0.1, "seeds": [1, 2, 3]}
- PRIMARY OBSERVABLE: competence_heldout of the elite per arm x seed; primary comparison failed_A vs random; direct_best per set as telemetry
- CLAIM CEILING: SUPPORTED_POSITIVE only if failed_A - random >= 0.10 AND every kill attack survives by the same margin; otherwise WEAK_POSITIVE / CAPABLE_NEGATIVE
- FALSIFICATION CONDITION: failed_A - random < 0.10 => the SFE-07 effect does not replicate; a kill arm within 0.10 of failed_A => that description suffices
- TYPED FAILURE CONDITIONS:
    - TARGET_UNREACHABLE (no arm reaches)
    - UNDERPOWERED
    - IMMATURE_ARTIFACT recorded on failed_A (its source is immature by construction; telemetry, D2-011)
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - direct_best per set
    - set summaries (length, opcode categories)
    - import_share_final (share of the final population descending from the set)
    - source maturity per set
    - first_solved_gen
    - reachability rows (random arm baseline)
- MACHINE CHANGES EXERCISED:
    - B (target '*' + battery)
    - C (common_fill whole-population substitution)
    - D (cross-campaign fetch as keyed steps)
    - E (maturity on evolved sets)
    - F (canonical digests on campaign-1 artifacts)
    - G
    - H (origin shares)
    - I
- decl (machine-read by archaeon.wse.states): {"battery": [{"name": "failed_shuffled", "rule": "failed_A - failed_shuffled >= 0.10 mean held-out", "type": "kill"}, {"name": "failed_opcodes", "rule": "failed_A - failed_opcodes >= 0.10 mean held-out", "type": "kill"}, {"name": "length_matched", "rule": "failed_A - length_matched >= 0.10 mean held-out", "type": "kill"}, {"name": "evolved_unrelated", "rule": "failed_A - evolved_unrelated >= 0.10 mean held-out", "type": "kill"}], "n_min": 3, "primary": {"control": "random", "metric": "competence_heldout", "min_effect": 0.1, "treatment": "failed_A"}, "probes": ["evolved_solved"], "target": {"baseline_arm": "*", "reach_metric": "reached", "reach_min": 1, "reachability_class": "UNESTABLISHED"}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a00); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=CAPABLE_NEGATIVE
- engine: dry-run; worlds 0; artifacts 0; imports 0; records 0; errors 0
- timings (s): exchange_s=0.0, fetch_s=0.0, records_s=0.0, sources_s=1.2, targets_s=0.52, total_s=1.9
- decisions: D2-012: assay capability = ANY arm reaches (target baseline_arm '*'); the premise of a transport-unlocks-an-unreachable-cell design is that the baseline may not reach
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / competence_heldout      s1      s2      s3    mean    n
    evolved_solved           0.062   0.062   0.042   0.056    3
    evolved_unrelated        0.062   0.062   0.125   0.083    3
    failed_A                 0.062   0.000   0.042   0.035    3
    failed_opcodes           0.062   0.000   0.125   0.062    3
    failed_shuffled          0.062   0.021   0.042   0.042    3
    length_matched           0.062   0.000   0.042   0.035    3
    random                   0.062   0.021   0.000   0.028    3

    arm / train_last            s1      s2      s3    mean    n
    evolved_solved           0.000   0.000   0.000   0.000    3
    evolved_unrelated        0.000   0.000   0.000   0.000    3
    failed_A                 0.000   0.000   0.000   0.000    3
    failed_opcodes           0.000   0.000   0.000   0.000    3
    failed_shuffled          0.000   0.250   0.000   0.083    3
    length_matched           0.000   0.000   0.000   0.000    3
    random                   0.000   0.250   0.000   0.083    3

    arm / direct_best           s1      s2      s3    mean    n
    evolved_solved           0.062   0.062   0.125   0.083    3
    evolved_unrelated        0.062   0.062   0.042   0.056    3
    failed_A                 0.062   0.062   0.042   0.056    3
    failed_opcodes           0.062   0.062   0.125   0.083    3
    failed_shuffled          0.062   0.083   0.125   0.090    3
    length_matched           0.062   0.062   0.042   0.056    3
    random                       -       -       -       -    0

- footholds:
    arm                    footholds  first_solved_gen per row
    evolved_solved         0/3        -,-,-
    evolved_unrelated      0/3        -,-,-
    failed_A               0/3        -,-,-
    failed_opcodes         1/3        -,-,1
    failed_shuffled        0/3        -,-,-
    length_matched         0/3        -,-,-
    random                 0/3        -,-,-

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.0278, "effect": 0.0069, "min_effect": 0.1, "n_control": 3, "n_treatment": 3, "paired": 3, "paired_wins": 1, "treatment_mean": 0.0347}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: SUPPORTED_POSITIVE only if failed_A - random >= 0.10 AND every kill attack survives by the same margin; otherwise WEAK_POSITIVE / CAPABLE_NEGATIVE

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: none (dry run)
- all TERMINATED: n/a

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-04

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). 
