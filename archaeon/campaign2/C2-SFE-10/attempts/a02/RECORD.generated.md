# C2-SFE-10 -- function-bearing organs

## A. STARTUP (preregistration; sealed sha256:def11d20cc90ebec6dd4a6a3795a0de7f70f906780a1f7b75ab3046073bb0286)

- experiment ID: C2-SFE-10
- parents: SFE-08, SFE-07, SFE-01
- QUESTION: Do organs defined by KNOCKOUT LOAD (instructions whose removal changes the organism's outputs on its own cell) transfer where SFE-08's length-defined organs did not: does a chimera of two functional organs from different failed lineages raise held-out competence on W2_K2 4-bit over a chimera of two length-defined organs?
- PARENT EVIDENCE: SFE-08: chimera = shuffled = random at floor; whole ancestors 1/3 each. C2-SFE-04: failed genotypes carry nothing that survives shuffling; the campaign-1 manifest rebuild was a per-seed treatment (fixed here). Table: W2_K2 4-bit N200 G60 E16 7/17 REACHABLE.
- ASSAY CAPABILITY REQUIREMENT: ANY arm reaches a foothold in >= 1 of 10 seeds; >= 1 functional organ found per lineage (else the functional arm falls back to length organs and the row says so)
- POSITIVE CONTROL: the random arm (own generation 0) on W2_K2 4-bit: expected 0.41 per seed; the whole_ancestors probe as the parent's reference
- REACHABILITY ESTIMATE:
    {"W2_K2": {"at_budget": {"band95": [0.2834, 0.6763], "class": "REACHABLE", "first_solved_gens": [13, 19, 32, 35, 39, 48, 49, 50, 54, 59], "freq": 0.4762, "k": 10, "n": 21}, "at_budget_any_foundry": {"band95": [0.2834, 0.6763], "class": "REACHABLE", "foundries": ["instr1-16:6528b9dc"], "freq": 0.4762, "k": 10, "n": 21}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.1975, 0.5039], "budgets": [[200, 30, 16], [200, 36, 16], [200, 40, 16], [200, 41, 16], [200, 42, 16], [200, 48, 16], [200, 60, 16]], "class": "REACHABLE", "freq": 0.3333, "k": 11, "n": 33}}}
- ARMS:
    - random
    - chimera_functional
    - chimera_length
    - shuffled_functional
    - whole_ancestors
- COMMON-RANDOM-NUMBERS POLICY: default; every set substitutes 100 organisms into the SAME generation 0 of 200 (common_fill, tagged) so the import share is informative; composition streams keyed on (seed, mode)
- BUDGET:
    {"E": 16, "G": 60, "N": 200, "heldout_episodes": 48, "margin": 0.1, "probe_episodes": 8, "recipe_seed": 0, "seeds": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "set_n": 100}
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
- decl (machine-read by archaeon.wse.states): {"battery": [{"name": "shuffled_functional", "rule": "chimera_functional - shuffled_functional >= 0.10 mean held-out", "type": "kill"}], "interventions": [{"arm": "chimera_functional", "counter": "functional_organs_used"}], "n_min": 10, "primary": {"control": "chimera_length", "metric": "competence_heldout", "min_effect": 0.1, "treatment": "chimera_functional"}, "probes": ["whole_ancestors", "random"], "target": {"baseline_arm": "*", "reach_metric": "reached", "reach_min": 1, "reachability_class": "REACHABLE"}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a02); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=TARGET_UNREACHABLE
    a02  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 2; artifacts 12; imports 10; records 50; errors 0
- import hash checks: 10/10 ok
- timings (s): exchange_s=3.06, fetch_s=0.17, load_maps_s=1.44, records_s=14.14, startup_s=0.2, targets_s=218.92, teardown_s=0.34, total_s=239.5
- decisions: D2-018: an organ is FUNCTIONAL iff its instructions are load-bearing under single-instruction knockout on the SOURCE cell's probe episodes; the target is never consulted
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / competence_heldout      s1     s10      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    chimera_functional       0.323   0.531   0.323   0.510   0.104   0.312   0.542   0.312   0.042   0.531   0.353   10
    chimera_length           0.104   0.062   0.531   0.031   0.104   0.531   0.052   0.531   0.531   0.083   0.256   10
    random                   0.323   0.292   0.292   0.344   0.104   0.333   0.542   0.271   0.531   0.531   0.356   10
    shuffled_functional      0.552   0.531   0.271   0.500   0.312   0.531   0.542   0.531   0.531   0.083   0.439   10
    whole_ancestors          0.521   0.062   0.083   0.510   0.542   0.052   0.542   0.052   0.531   0.312   0.321   10

    arm / train_last            s1     s10      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    chimera_functional       0.188   0.500   0.406   0.531   0.188   0.281   0.531   0.250   0.156   0.562   0.359   10
    chimera_length           0.062   0.125   0.531   0.125   0.188   0.500   0.156   0.562   0.562   0.125   0.294   10
    random                   0.188   0.188   0.344   0.344   0.188   0.250   0.531   0.281   0.562   0.562   0.344   10
    shuffled_functional      0.531   0.500   0.344   0.531   0.312   0.500   0.531   0.531   0.562   0.125   0.447   10
    whole_ancestors          0.688   0.125   0.156   0.531   0.500   0.062   0.531   0.094   0.562   0.281   0.353   10

    arm / direct_best           s1     s10      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    chimera_functional       0.094   0.073   0.115   0.104   0.104   0.094   0.062   0.052   0.073   0.104   0.087   10
    chimera_length           0.073   0.073   0.083   0.042   0.104   0.094   0.042   0.052   0.052   0.104   0.072   10
    random                       -       -       -       -       -       -       -       -       -       -       -    0
    shuffled_functional      0.094   0.073   0.083   0.042   0.104   0.094   0.062   0.052   0.052   0.125   0.078   10
    whole_ancestors          0.094   0.073   0.083   0.104   0.104   0.094   0.073   0.052   0.052   0.104   0.083   10

    arm / import_share_final      s1     s10      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    chimera_functional       1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   10
    chimera_length           1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   10
    random                       -       -       -       -       -       -       -       -       -       -       -    0
    shuffled_functional      1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   10
    whole_ancestors          1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   10

- footholds:
    arm                    footholds  first_solved_gen per row
    chimera_functional     4/10       -,-,32,-,-,36,-,-,11,23
    chimera_length         4/10       -,15,-,-,39,-,24,21,-,-
    random                 4/10       -,-,35,-,-,49,-,39,32,-
    shuffled_functional    7/10       26,-,58,-,39,23,48,55,-,45
    whole_ancestors        5/10       8,-,25,12,-,40,-,56,-,-

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.2562, "effect": 0.0969, "min_effect": 0.1, "n_control": 10, "n_treatment": 10, "paired": 10, "paired_wins": 5, "treatment_mean": 0.3531}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: SUPPORTED_POSITIVE only if the primary margin holds AND shuffled_functional falls below chimera_functional by the margin; else WEAK / CAPABLE_NEGATIVE

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"lineages": "TERMINATED", "target": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-10

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). 
