# C2-SFE-02 -- representation: positive control first, operator mass matched

## A. STARTUP (preregistration; sealed sha256:33cdb9c9fbc6d809202b185a3d39257325ea5e6b326c4012ab280ff0a4f2f4d1)

- experiment ID: C2-SFE-02
- parents: SFE-09
- QUESTION: Gate: does the baseline representation (A_words) reach W1_d1 8-bit at N200 G100 E24 in >= 0 of 2 seeds? Science (only if the gate passes): with operator mass matched by construction, do representations whose opcode-field neighbourhood is uniform (B) or class-confined (C) reach the stuck cell W1_d4 8-bit that A does not, or reach the control cell faster?
- PARENT EVIDENCE: SFE-09: positive control (A on W1_d1 4-bit G60) 0/3, INCONCLUSIVE; L-029 operator mass unmatched. Table: W1_d1 8-bit N200 G100 E24 2/3 REACHABLE (49, 79); W1_d4 8-bit same budget 0/3 OBSERVED_UNREACHABLE_AT_BUDGET.
- ASSAY CAPABILITY REQUIREMENT: A_words/control reached in >= 0 of 2 seeds (else POSITIVE_CONTROL_FAILED and no comparison is run); B and C must have applied >= 1 opcode-field rewrite per row
- POSITIVE CONTROL: A_words on W1_d1 8-bit N200 G100 E24; expected 2/3 per seed
- REACHABILITY ESTIMATE:
    {"W1_d1": {"at_budget": {"band95": [0.0, 0.6576], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": 0.0, "k": 0, "n": 2}, "pooled_any_budget": {"band95": [0.1176, 0.7693], "budgets": [[20, 6, 4], [200, 100, 24]], "class": "REACHABLE", "freq": 0.4, "k": 2, "n": 5}}, "W1_d4": {"at_budget": {"band95": [0.0, 0.6576], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": 0.0, "k": 0, "n": 2}, "pooled_any_budget": {"band95": [0.0, 0.4345], "budgets": [[20, 6, 4], [200, 100, 24]], "class": "OBSERVED_UNREACHABLE_AT_BUDGET", "freq": 0.0, "k": 0, "n": 5}}}
- ARMS:
    - A_words/control
    - A_words/stuck
    - B_fields/control
    - B_fields/stuck
    - C_fields_class/control
    - C_fields_class/stuck
- COMMON-RANDOM-NUMBERS POLICY: default (rng_label=crn): identical generation 0 and identical selection/mutation random stream for every representation in a cell; the opcode redraw uses its own derived stream so A's stream is untouched
- BUDGET:
    {"E": 4, "G": 6, "N": 20, "gate_min": 0, "heldout_episodes": 48, "seeds": [1, 2]}
- PRIMARY OBSERVABLE: competence_heldout on the stuck cell (B_fields/stuck vs A_words/stuck); footholds and first_solved_gen on both cells secondary
- CLAIM CEILING: weak positive at best (n=2, one stuck cell); a capable negative = no unlock at this budget for these two neighbourhoods
- FALSIFICATION CONDITION: B_fields/stuck - A_words/stuck < 0.10 held-out (and C likewise) with the gate passed => CAPABLE_NEGATIVE for the unlock
- TYPED FAILURE CONDITIONS:
    - POSITIVE_CONTROL_FAILED (A_words/control < 0/2)
    - INTERVENTION_NOT_APPLIED (opfield_rewrites == 0 on a B/C arm)
    - UNDERPOWERED
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - op_mass_realized per row (the mass check)
    - opfield_rewrites per row
    - first_solved_gen
    - elite genome summary
    - reachability rows (A_words baseline; B/C treated)
- MACHINE CHANGES EXERCISED:
    - A
    - B (gate as a typed state)
    - C
    - D
    - G (descend_fn hook)
    - H (operator histograms)
    - I
- decl (machine-read by archaeon.wse.states): {"interventions": [{"arm": "B_fields/stuck", "counter": "opfield_rewrites"}, {"arm": "C_fields_class/stuck", "counter": "opfield_rewrites"}, {"arm": "B_fields/control", "counter": "opfield_rewrites"}, {"arm": "C_fields_class/control", "counter": "opfield_rewrites"}], "n_min": 2, "positive_control": {"arm": "A_words/control", "metric": "reached", "min": 1, "min_rows": 0}, "primary": {"control": "A_words/stuck", "metric": "competence_heldout", "min_effect": 0.1, "treatment": "B_fields/stuck"}, "representations": {"A_words": "grammar as is: operand_perturbation on an opcode word moves the opcode by +-delta mod 25 (index-adjacent neighbours)", "B_fields": "same grammar, same masses; when operand_perturbation lands on an opcode word the opcode is redrawn UNIFORMLY over 25", "C_fields_class": "as B, but the redraw stays inside the opcode's affordance class with p=0.75 (uniform otherwise)"}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a00); resumed_from: 1; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=INTERVENTION_NOT_APPLIED
    a02  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=CAPABLE_NEGATIVE
- engine: dry-run; worlds 0; artifacts 0; imports 0; records 0; errors 0
- timings (s): records_s=0.0, stage1_s=0.12, stage2_s=0.27, total_s=0.6
- decisions: D2-007: representations differ ONLY in the opcode-field neighbourhood under operand_perturbation; all twelve operator masses are the grammar's own (mass matched by construction, L-029)
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / competence_heldout      s1      s2    mean    n
    A_words/control          0.000   0.000   0.000    2
    A_words/stuck            0.000   0.000   0.000    2
    B_fields/control         0.000   0.000   0.000    2
    B_fields/stuck           0.000   0.000   0.000    2
    C_fields_class/control   0.000   0.000   0.000    2
    C_fields_class/stuck     0.000   0.000   0.000    2

    arm / train_last            s1      s2    mean    n
    A_words/control          0.000   0.000   0.000    2
    A_words/stuck            0.000   0.000   0.000    2
    B_fields/control         0.000   0.000   0.000    2
    B_fields/stuck           0.000   0.000   0.000    2
    C_fields_class/control   0.000   0.000   0.000    2
    C_fields_class/stuck     0.000   0.000   0.000    2

    arm / opfield_rewrites      s1      s2    mean    n
    A_words/control              0       0   0.000    2
    A_words/stuck                0       0   0.000    2
    B_fields/control             5       2   3.500    2
    B_fields/stuck               3       3   3.000    2
    C_fields_class/control       6       2   4.000    2
    C_fields_class/stuck         2       3   2.500    2

- footholds:
    arm                    footholds  first_solved_gen per row
    A_words/control        0/2        -,-
    A_words/stuck          0/2        -,-
    B_fields/control       0/2        -,-
    B_fields/stuck         0/2        -,-
    C_fields_class/control 0/2        -,-
    C_fields_class/stuck   0/2        -,-

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.0, "effect": 0.0, "min_effect": 0.1, "n_control": 2, "n_treatment": 2, "paired": 2, "paired_wins": 0, "treatment_mean": 0.0}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: weak positive at best (n=2, one stuck cell); a capable negative = no unlock at this budget for these two neighbourhoods

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: none (dry run)
- all TERMINATED: n/a

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-02

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). 
