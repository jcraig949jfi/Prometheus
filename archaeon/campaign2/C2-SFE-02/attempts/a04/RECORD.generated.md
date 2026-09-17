# C2-SFE-02 -- representation: positive control first, operator mass matched

## A. STARTUP (preregistration; sealed sha256:672392bed1c23af1658acf25ae75b9f6f28c7419a7397c425da17b8ca8733da4)

- experiment ID: C2-SFE-02
- parents: SFE-09
- QUESTION: Gate: does the baseline representation (A_words) reach W1_d1 8-bit at N200 G100 E24 in >= 2 of 6 seeds? Science (only if the gate passes): with operator mass matched by construction, do representations whose opcode-field neighbourhood is uniform (B) or class-confined (C) reach the stuck cell W1_d4 8-bit that A does not, or reach the control cell faster?
- PARENT EVIDENCE: SFE-09: positive control (A on W1_d1 4-bit G60) 0/3, INCONCLUSIVE; L-029 operator mass unmatched. Table: W1_d1 8-bit N200 G100 E24 2/3 REACHABLE (49, 79); W1_d4 8-bit same budget 0/3 OBSERVED_UNREACHABLE_AT_BUDGET.
- ASSAY CAPABILITY REQUIREMENT: A_words/control reached in >= 2 of 6 seeds (else POSITIVE_CONTROL_FAILED and no comparison is run); B and C must have applied >= 1 opcode-field rewrite per row
- POSITIVE CONTROL: A_words on W1_d1 8-bit N200 G100 E24; expected 2/3 per seed
- REACHABILITY ESTIMATE:
    {"W1_d1": {"at_budget": {"band95": [0.2077, 0.9385], "class": "REACHABLE", "first_solved_gens": [49, 79], "freq": 0.6667, "k": 2, "n": 3}, "at_budget_any_foundry": {"band95": [0.1206, 0.6458], "class": "REACHABLE", "foundries": ["instr1-16:6528b9dc", "instr1-32:199105b4"], "freq": 0.3333, "k": 3, "n": 9}, "foundry": "instr1-32:199105b4", "pooled_any_budget": {"band95": [0.2077, 0.9385], "budgets": [[200, 100, 24]], "class": "REACHABLE", "freq": 0.6667, "k": 2, "n": 3}}, "W1_d4": {"at_budget": {"band95": [0.0, 0.5615], "class": "OBSERVED_UNREACHABLE_AT_BUDGET", "first_solved_gens": [], "freq": 0.0, "k": 0, "n": 3}, "at_budget_any_foundry": {"band95": [0.0, 0.5615], "class": "OBSERVED_UNREACHABLE_AT_BUDGET", "foundries": ["instr1-32:199105b4"], "freq": 0.0, "k": 0, "n": 3}, "foundry": "instr1-32:199105b4", "pooled_any_budget": {"band95": [0.0, 0.5615], "budgets": [[200, 100, 24]], "class": "OBSERVED_UNREACHABLE_AT_BUDGET", "freq": 0.0, "k": 0, "n": 3}}}
- ARMS:
    - A_words/control
    - A_words/stuck
    - B_fields/control
    - B_fields/stuck
    - C_fields_class/control
    - C_fields_class/stuck
- COMMON-RANDOM-NUMBERS POLICY: default (rng_label=crn): identical generation 0 and identical selection/mutation random stream for every representation in a cell; the opcode redraw uses its own derived stream so A's stream is untouched
- BUDGET:
    {"E": 24, "G": 100, "N": 200, "foundry": "v01", "foundry_id": "instr1-32:199105b4", "gate_min": 2, "heldout_episodes": 48, "seeds": [1, 2, 3, 4, 5, 6]}
- PRIMARY OBSERVABLE: competence_heldout on the stuck cell (B_fields/stuck vs A_words/stuck); footholds and first_solved_gen on both cells secondary
- CLAIM CEILING: weak positive at best (n=6, one stuck cell); a capable negative = no unlock at this budget for these two neighbourhoods
- FALSIFICATION CONDITION: B_fields/stuck - A_words/stuck < 0.10 held-out (and C likewise) with the gate passed => CAPABLE_NEGATIVE for the unlock
- TYPED FAILURE CONDITIONS:
    - POSITIVE_CONTROL_FAILED (A_words/control < 2/6)
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
- decl (machine-read by archaeon.wse.states): {"interventions": [{"arm": "B_fields/stuck", "counter": "opfield_rewrites"}, {"arm": "C_fields_class/stuck", "counter": "opfield_rewrites"}, {"arm": "B_fields/control", "counter": "opfield_rewrites"}, {"arm": "C_fields_class/control", "counter": "opfield_rewrites"}], "n_min": 6, "positive_control": {"arm": "A_words/control", "metric": "reached", "min": 1, "min_rows": 2}, "primary": {"control": "A_words/stuck", "metric": "competence_heldout", "min_effect": 0.1, "treatment": "B_fields/stuck"}, "representations": {"A_words": "grammar as is: operand_perturbation on an opcode word moves the opcode by +-delta mod 25 (index-adjacent neighbours)", "B_fields": "same grammar, same masses; when operand_perturbation lands on an opcode word the opcode is redrawn UNIFORMLY over 25", "C_fields_class": "as B, but the redraw stays inside the opcode's affordance class with p=0.75 (uniform otherwise)"}}

## B. EXECUTION (generated from receipts)

- attempts: 4 (of record: a04); resumed_from: 3; replayed steps on the attempt of record: 11
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=INTERVENTION_NOT_APPLIED
    a02  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=CAPABLE_NEGATIVE
    a03  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=POSITIVE_CONTROL_FAILED
    a04  errors=0 replayed=11 engine=True purpose=foundry=v01 disposition_candidate=POSITIVE_CONTROL_FAILED
- engine: live; worlds 1; artifacts 2; imports 0; records 6; errors 0
- timings (s): records_s=0.0, stage1_s=74.1, startup_s=0.0, teardown_s=0.14, total_s=74.7
- decisions: D2-007: representations differ ONLY in the opcode-field neighbourhood under operand_perturbation; all twelve operator masses are the grammar's own (mass matched by construction, L-029), gate failed (1/6): stage 2 not run; POSITIVE_CONTROL_FAILED is the row of record
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / competence_heldout      s1      s2      s3      s4      s5      s6    mean    n
    A_words/control          0.000   0.000   0.042   1.000   0.000   0.000   0.174    6

    arm / train_last            s1      s2      s3      s4      s5      s6    mean    n
    A_words/control          0.000   0.000   0.125   1.000   0.000   0.000   0.188    6

    arm / opfield_rewrites      s1      s2      s3      s4      s5      s6    mean    n
    A_words/control              0       0       0       0       0       0   0.000    6

- footholds:
    arm                    footholds  first_solved_gen per row
    A_words/control        1/6        -,-,-,46,-,-

- typed states fired: ['POSITIVE_CONTROL_FAILED']
    POSITIVE_CONTROL_FAILED  {"arm": "A_words/control", "metric": "reached", "min": 1, "rows": 6, "rows_meeting": 1, "values": [0, 0, 0, 1, 0, 0]}
- disposition candidate (machine): POSITIVE_CONTROL_FAILED -- assay precondition failed; the scientific question was not posed
- claim ceiling (machine): none; preregistered ceiling: weak positive at best (n=6, one stuck cell); a capable negative = no unlock at this budget for these two neighbourhoods

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"rep": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-02

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: POSITIVE_CONTROL_FAILED (machine candidate POSITIVE_CONTROL_FAILED). 
