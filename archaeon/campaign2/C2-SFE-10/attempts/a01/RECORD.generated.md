# C2-SFE-10 -- function-bearing organs

## A. STARTUP (preregistration; sealed sha256:a3db39aca45f430ab2055f2c26dfc5977ada036c5e43bf14b928707861956b84)

- experiment ID: C2-SFE-10
- parents: SFE-08, SFE-07, SFE-01
- QUESTION: Do organs defined by KNOCKOUT LOAD (instructions whose removal changes the organism's outputs on its own cell) transfer where SFE-08's length-defined organs did not: does a chimera of two functional organs from different failed lineages raise held-out competence on W2_K2 4-bit over a chimera of two length-defined organs?
- PARENT EVIDENCE: SFE-08: chimera = shuffled = random at floor; whole ancestors 1/3 each. C2-SFE-04: failed genotypes carry nothing that survives shuffling; the campaign-1 manifest rebuild was a per-seed treatment (fixed here). Table: W2_K2 4-bit N200 G60 E16 7/17 REACHABLE.
- ASSAY CAPABILITY REQUIREMENT: ANY arm reaches a foothold in >= 1 of 3 seeds; >= 1 functional organ found per lineage (else the functional arm falls back to length organs and the row says so)
- POSITIVE CONTROL: the random arm (own generation 0) on W2_K2 4-bit: expected 0.41 per seed; the whole_ancestors probe as the parent's reference
- REACHABILITY ESTIMATE:
    {"W2_K2": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.1975, 0.5039], "budgets": [[200, 30, 16], [200, 36, 16], [200, 40, 16], [200, 41, 16], [200, 42, 16], [200, 48, 16], [200, 60, 16]], "class": "REACHABLE", "freq": 0.3333, "k": 11, "n": 33}}}
- ARMS:
    - random
    - chimera_functional
    - chimera_length
    - shuffled_functional
    - whole_ancestors
- COMMON-RANDOM-NUMBERS POLICY: default; every set substitutes 100 organisms into the SAME generation 0 of 24 (common_fill, tagged) so the import share is informative; composition streams keyed on (seed, mode)
- BUDGET:
    {"E": 4, "G": 6, "N": 24, "heldout_episodes": 48, "margin": 0.1, "probe_episodes": 8, "recipe_seed": 0, "seeds": [1, 2, 3], "set_n": 100}
- PRIMARY OBSERVABLE: competence_heldout per arm x seed; chimera_functional vs chimera_length; direct_best and import_share_final as telemetry
- CLAIM CEILING: SUPPORTED_POSITIVE only if the primary margin holds AND shuffled_functional falls below chimera_functional by the margin; else WEAK / CAPABLE_NEGATIVE
- FALSIFICATION CONDITION: chimera_functional - chimera_length < 0.10 => function-defined organs transfer no better than length-defined ones
- TYPED FAILURE CONDITIONS:
    - TARGET_UNREACHABLE (no arm reaches)
    - UNDERPOWERED
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - load maps per genome (share load-bearing, organ count/length)
    - direct_best per set
    - import_share_final
    - set summaries
    - reachability rows
- MACHINE CHANGES EXERCISED:
    - B (battery, target '*')
    - C (partial substitution + origin share)
    - D (cross-campaign fetch)
    - E
    - H (load maps)
    - I
- decl (machine-read by archaeon.wse.states): {"battery": [{"name": "shuffled_functional", "rule": "chimera_functional - shuffled_functional >= 0.10 mean held-out", "type": "kill"}], "n_min": 3, "primary": {"control": "chimera_length", "metric": "competence_heldout", "min_effect": 0.1, "treatment": "chimera_functional"}, "probes": ["whole_ancestors", "random"], "target": {"baseline_arm": "*", "reach_metric": "reached", "reach_min": 1, "reachability_class": "UNESTABLISHED"}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a00); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=TARGET_UNREACHABLE
- engine: dry-run; worlds 0; artifacts 0; imports 0; records 0; errors 0
- timings (s): exchange_s=0.01, fetch_s=0.0, load_maps_s=0.25, records_s=0.0, targets_s=0.98, total_s=1.4
- decisions: D2-018: an organ is FUNCTIONAL iff its instructions are load-bearing under single-instruction knockout on the SOURCE cell's probe episodes; the target is never consulted
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / competence_heldout      s1      s2      s3    mean    n
    chimera_functional       0.042   0.083   0.042   0.056    3
    chimera_length           0.073   0.083   0.000   0.052    3
    random                   0.073   0.083   0.031   0.062    3
    shuffled_functional      0.000   0.083   0.042   0.042    3
    whole_ancestors          0.031   0.052   0.042   0.042    3

    arm / train_last            s1      s2      s3    mean    n
    chimera_functional       0.000   0.000   0.125   0.042    3
    chimera_length           0.000   0.000   0.000   0.000    3
    random                   0.000   0.000   0.125   0.042    3
    shuffled_functional      0.000   0.000   0.125   0.042    3
    whole_ancestors          0.000   0.125   0.125   0.083    3

    arm / direct_best           s1      s2      s3    mean    n
    chimera_functional       0.073   0.083   0.042   0.066    3
    chimera_length           0.073   0.083   0.042   0.066    3
    random                       -       -       -       -    0
    shuffled_functional      0.073   0.083   0.042   0.066    3
    whole_ancestors          0.073   0.083   0.042   0.066    3

    arm / import_share_final      s1      s2      s3    mean    n
    chimera_functional       1.000   1.000   1.000   1.000    3
    chimera_length           1.000   1.000   1.000   1.000    3
    random                       -       -       -       -    0
    shuffled_functional      1.000   1.000   1.000   1.000    3
    whole_ancestors          1.000   1.000   1.000   1.000    3

- footholds:
    arm                    footholds  first_solved_gen per row
    chimera_functional     0/3        -,-,-
    chimera_length         0/3        -,-,-
    random                 0/3        -,-,-
    shuffled_functional    0/3        -,-,-
    whole_ancestors        0/3        -,-,-

- typed states fired: ['TARGET_UNREACHABLE']
    TARGET_UNREACHABLE  {"band95_upper": 0.2039, "baseline_arm": "*", "reached": 0, "rows": 15, "table_class": "UNESTABLISHED"}
- disposition candidate (machine): TARGET_UNREACHABLE -- assay precondition failed; the scientific question was not posed
- claim ceiling (machine): none; preregistered ceiling: SUPPORTED_POSITIVE only if the primary margin holds AND shuffled_functional falls below chimera_functional by the margin; else WEAK / CAPABLE_NEGATIVE

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: none (dry run)
- all TERMINATED: n/a

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-10

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: TARGET_UNREACHABLE (machine candidate TARGET_UNREACHABLE). 
