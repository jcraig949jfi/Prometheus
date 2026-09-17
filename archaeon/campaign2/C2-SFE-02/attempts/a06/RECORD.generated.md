# C2-SFE-02 -- representation: positive control first, operator mass matched

## A. STARTUP (preregistration; sealed sha256:1c47bafce25693e82dc2159c442168bdbf473798b7968e6ba03d1eb12ab23185)

- experiment ID: C2-SFE-02
- parents: SFE-09
- QUESTION: Gate: does the baseline representation (A_words) reach W2_K2 4-bit at N200 G60 E16 in >= 2 of 8 seeds? Science (only if the gate passes): with operator mass matched by construction, do representations whose opcode-field neighbourhood is uniform (B) or class-confined (C) reach the stuck cell W1_d4 4-bit that A does not, or reach the control cell faster?
- PARENT EVIDENCE: SFE-09: positive control (A on W1_d1 4-bit G60) 0/3, INCONCLUSIVE; L-029 operator mass unmatched. Table: W1_d1 8-bit N200 G100 E24 2/3 REACHABLE (49, 79); W1_d4 8-bit same budget 0/3 OBSERVED_UNREACHABLE_AT_BUDGET.
- ASSAY CAPABILITY REQUIREMENT: A_words/control reached in >= 2 of 8 seeds (else POSITIVE_CONTROL_FAILED and no comparison is run); B and C must have applied >= 1 opcode-field rewrite per row
- POSITIVE CONTROL: A_words on W2_K2 4-bit N200 G60 E16; table class REACHABLE (0.4118)
- REACHABILITY ESTIMATE:
    {"W1_d4": {"at_budget": {"band95": [0.0127, 0.3147], "class": "RARE", "first_solved_gens": [52], "freq": 0.0714, "k": 1, "n": 14}, "at_budget_any_foundry": {"band95": [0.0127, 0.3147], "class": "RARE", "foundries": ["instr1-16:6528b9dc"], "freq": 0.0714, "k": 1, "n": 14}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0127, 0.3147], "budgets": [[200, 60, 16]], "class": "RARE", "freq": 0.0714, "k": 1, "n": 14}}, "W2_K2": {"at_budget": {"band95": [0.2161, 0.6399], "class": "REACHABLE", "first_solved_gens": [35, 39, 48, 49, 50, 54, 59], "freq": 0.4118, "k": 7, "n": 17}, "at_budget_any_foundry": {"band95": [0.2161, 0.6399], "class": "REACHABLE", "foundries": ["instr1-16:6528b9dc"], "freq": 0.4118, "k": 7, "n": 17}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.156, 0.5087], "budgets": [[200, 36, 16], [200, 48, 16], [200, 60, 16]], "class": "REACHABLE", "freq": 0.3043, "k": 7, "n": 23}}}
- ARMS:
    - A_words/control
    - A_words/stuck
    - B_fields/control
    - B_fields/stuck
    - C_fields_class/control
    - C_fields_class/stuck
- COMMON-RANDOM-NUMBERS POLICY: default (rng_label=crn): identical generation 0 and identical selection/mutation random stream for every representation in a cell; the opcode redraw uses its own derived stream so A's stream is untouched
- BUDGET:
    {"E": 16, "G": 60, "N": 200, "control": {"D": 1, "K": 2, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 0, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W2_K2", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}, "foundry": "c2", "foundry_id": "instr1-16:6528b9dc", "gate_min": 2, "heldout_episodes": 48, "seeds": [1, 2, 3, 4, 5, 6, 7, 8], "stuck": {"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 4, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W1_d4", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}}
- PRIMARY OBSERVABLE: competence_heldout on the stuck cell (B_fields/stuck vs A_words/stuck); footholds and first_solved_gen on both cells secondary
- CLAIM CEILING: weak positive at best (n=8, one stuck cell); a capable negative = no unlock at this budget for these two neighbourhoods
- FALSIFICATION CONDITION: B_fields/stuck - A_words/stuck < 0.10 held-out (and C likewise) with the gate passed => CAPABLE_NEGATIVE for the unlock
- TYPED FAILURE CONDITIONS:
    - POSITIVE_CONTROL_FAILED (A_words/control < 2/8)
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
- decl (machine-read by archaeon.wse.states): {"interventions": [{"arm": "B_fields/stuck", "counter": "opfield_rewrites"}, {"arm": "C_fields_class/stuck", "counter": "opfield_rewrites"}, {"arm": "B_fields/control", "counter": "opfield_rewrites"}, {"arm": "C_fields_class/control", "counter": "opfield_rewrites"}], "n_min": 8, "positive_control": {"arm": "A_words/control", "metric": "reached", "min": 1, "min_rows": 2}, "primary": {"control": "A_words/stuck", "metric": "competence_heldout", "min_effect": 0.1, "treatment": "B_fields/stuck"}, "representations": {"A_words": "grammar as is: operand_perturbation on an opcode word moves the opcode by +-delta mod 25 (index-adjacent neighbours)", "B_fields": "same grammar, same masses; when operand_perturbation lands on an opcode word the opcode is redrawn UNIFORMLY over 25", "C_fields_class": "as B, but the redraw stays inside the opcode's affordance class with p=0.75 (uniform otherwise)"}}

## B. EXECUTION (generated from receipts)

- attempts: 6 (of record: a06); resumed_from: 5; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=INTERVENTION_NOT_APPLIED
    a02  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=CAPABLE_NEGATIVE
    a03  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=POSITIVE_CONTROL_FAILED
    a04  errors=0 replayed=11 engine=True purpose=foundry=v01 disposition_candidate=POSITIVE_CONTROL_FAILED
    a05  errors=0 replayed=11 engine=True purpose=foundry=c2 control=W2_K2 stuck=W1_d4 bits=4 G=60 disposition_candidate=CAPABLE_NEGATIVE
    a06  errors=0 replayed=0 engine=True purpose=foundry=c2 control=W2_K2 stuck=W1_d4 bits=4 G=60 disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 48; errors 0
- timings (s): records_s=23.42, stage1_s=45.43, stage2_s=156.75, startup_s=0.08, teardown_s=0.2, total_s=226.8
- decisions: D2-007: representations differ ONLY in the opcode-field neighbourhood under operand_perturbation; all twelve operator masses are the grammar's own (mass matched by construction, L-029)
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / competence_heldout      s1      s2      s3      s4      s5      s6      s7      s8    mean    n
    A_words/control          0.323   0.292   0.344   0.104   0.333   0.542   0.271   0.531   0.342    8
    A_words/stuck            0.042   0.104   0.021   0.083   0.062   0.083   0.021   0.042   0.057    8
    B_fields/control         0.062   0.083   0.031   0.542   0.531   0.323   0.042   0.521   0.267    8
    B_fields/stuck           0.021   0.104   0.083   0.083   0.062   0.083   0.062   0.042   0.068    8
    C_fields_class/control   0.552   0.531   0.302   0.312   0.031   0.323   0.042   0.531   0.328    8
    C_fields_class/stuck     0.042   0.104   0.021   0.083   1.000   0.083   0.042   0.042   0.177    8

    arm / train_last            s1      s2      s3      s4      s5      s6      s7      s8    mean    n
    A_words/control          0.188   0.344   0.344   0.188   0.250   0.531   0.281   0.562   0.336    8
    A_words/stuck            0.125   0.125   0.062   0.062   0.125   0.188   0.125   0.125   0.117    8
    B_fields/control         0.062   0.156   0.125   0.375   0.500   0.219   0.062   0.750   0.281    8
    B_fields/stuck           0.125   0.125   0.062   0.062   0.125   0.188   0.125   0.125   0.117    8
    C_fields_class/control   0.531   0.531   0.312   0.312   0.125   0.219   0.062   0.562   0.332    8
    C_fields_class/stuck     0.125   0.125   0.062   0.125   1.000   0.188   0.188   0.125   0.242    8

    arm / opfield_rewrites      s1      s2      s3      s4      s5      s6      s7      s8    mean    n
    A_words/control              0       0       0       0       0       0       0       0   0.000    8
    A_words/stuck                0       0       0       0       0       0       0       0   0.000    8
    B_fields/control           560     593     576     576     585     553     543     585  571.375    8
    B_fields/stuck             595     558     530     612     558     559     614     545  571.375    8
    C_fields_class/control     604     595     595     554     609     576     602     596  591.375    8
    C_fields_class/stuck       525     574     563     600     562     615     505     561  563.125    8

- footholds:
    arm                    footholds  first_solved_gen per row
    A_words/control        3/8        -,-,35,-,-,49,-,39
    A_words/stuck          0/8        -,-,-,-,-,-,-,-
    B_fields/control       3/8        -,-,-,7,8,-,-,36
    B_fields/stuck         0/8        -,-,-,-,-,-,-,-
    C_fields_class/control 4/8        45,50,35,-,-,-,-,32
    C_fields_class/stuck   1/8        -,-,-,-,41,-,-,-

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.0573, "effect": 0.0104, "min_effect": 0.1, "n_control": 8, "n_treatment": 8, "paired": 8, "paired_wins": 2, "treatment_mean": 0.0677}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: weak positive at best (n=8, one stuck cell); a capable negative = no unlock at this budget for these two neighbourhoods

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

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). 
