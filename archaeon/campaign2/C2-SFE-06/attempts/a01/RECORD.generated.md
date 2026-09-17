# C2-SFE-06 -- retention economics on a rung ladder

## A. STARTUP (preregistration; sealed sha256:b097cb3fd7e1ddf5446ec636bef64c6ce65ee926ae1703846431d4978cbbebe1)

- experiment ID: C2-SFE-06
- parents: SFE-05
- QUESTION: When the selective pressure climbs a delay ladder (W0 -> d1 -> d2 -> d4, 3 generations per rung), at what revisit share p of earlier rungs in the training battery is rung-0 competence retained to the end, and what does retention cost on the top rung?
- PARENT EVIDENCE: SFE-05: adaptive +0.155, transfer +0.113 (n=3); fixed/on lost Kd-0 competence entirely (forgetting shelf hidden by the battery mean, L-022). Table: W0 4-bit COMMON by ~G35 (10/12 C2-SFE-03, 7/10 C2-SFE-04); W1_d4 4-bit RARE (1/14 at G60).
- ASSAY CAPABILITY REQUIREMENT: the ladder is climbable at its bottom: the p0.0 arm reaches rung-0 competence >= 0.5 (peak_r0) in >= 3 of 3 seeds; otherwise POSITIVE_CONTROL_FAILED (nothing to retain)
- POSITIVE CONTROL: p0.0 on rung 0 during the first 3 generations (W0 4-bit): expected ~0.7 per seed
- REACHABILITY ESTIMATE:
    {"W0": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0, 1.0], "budgets": [], "class": "UNESTABLISHED", "freq": null, "k": 0, "n": 0}}, "W1_d4": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0127, 0.3147], "budgets": [[200, 60, 16]], "class": "RARE", "freq": 0.0714, "k": 1, "n": 14}}}
- ARMS:
    - p0.0
    - p0.1
    - p0.25
    - p0.5
- COMMON-RANDOM-NUMBERS POLICY: default; identical generation 0 and selection stream for every p (the RNG is keyed on rung 0's world id); episodes per generation keyed on (generation, seed) so arms share the current-rung episodes and differ only in the revisit share
- BUDGET:
    {"E": 4, "G": 12, "N": 24, "probe_episodes": 24, "probe_every": 5, "rung_gens": 3, "rungs": [{"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 0, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W0", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}, {"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 1, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W1_d1", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}, {"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 2, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W1_d2", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}, {"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 4, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W1_d4", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}], "seeds": [1, 2, 3], "shares": [0.0, 0.1, 0.25, 0.5]}
- PRIMARY OBSERVABLE: final_r0 (rung-0 competence of the elite at the end, 24 eval episodes) per arm x seed; rung x generation matrix; shelf report
- CLAIM CEILING: weak at best (n=3, one ladder); a capable negative = revisits at p<=0.5 do not retain rung-0 competence
- FALSIFICATION CONDITION: final_r0(p0.25) - final_r0(p0.0) < 0.15 => revisiting does not retain; cost = final_r3(p0.25) - final_r3(p0.0) reported
- TYPED FAILURE CONDITIONS:
    - POSITIVE_CONTROL_FAILED (p0.0 peak_r0 >= 0.5 in < 3 seeds)
    - UNDERPOWERED
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - rung x generation matrix per row
    - shelf report per rung
    - peak/final per rung
    - schedule (rung, best, mean per generation)
    - elite genome summary
    - gen0 provenance
- MACHINE CHANGES EXERCISED:
    - G (spec and episodes change per step)
    - H (rung_matrix_row, shelf_report)
    - B
    - C
    - I
- decl (machine-read by archaeon.wse.states): {"n_min": 3, "positive_control": {"arm": "p0.0", "metric": "peak_r0", "min": 0.5, "min_rows": 3}, "primary": {"control": "p0.0", "metric": "final_r0", "min_effect": 0.15, "treatment": "p0.25"}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a00); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=POSITIVE_CONTROL_FAILED
- engine: dry-run; worlds 0; artifacts 0; imports 0; records 0; errors 0
- timings (s): ladder_s=0.45, records_s=0.0, total_s=0.7
- decisions: D2-014: revisit share p is the only difference between arms; it is an ecological pressure (old conditions recur), never a reward for retaining anything
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / final_r0              s1      s2      s3    mean    n
    p0.0                     0.042   0.125   0.000   0.056    3
    p0.1                     0.042   0.125   0.000   0.056    3
    p0.25                    0.042   0.125   0.000   0.056    3
    p0.5                     0.042   0.000   0.000   0.014    3

    arm / final_r3              s1      s2      s3    mean    n
    p0.0                     0.042   0.083   0.000   0.042    3
    p0.1                     0.042   0.083   0.000   0.042    3
    p0.25                    0.042   0.083   0.000   0.042    3
    p0.5                     0.042   0.042   0.000   0.028    3

    arm / peak_r0               s1      s2      s3    mean    n
    p0.0                     0.042   0.125   0.000   0.056    3
    p0.1                     0.042   0.125   0.000   0.056    3
    p0.25                    0.042   0.125   0.000   0.056    3
    p0.5                     0.042   0.000   0.000   0.014    3

    arm / retention_r0          s1      s2      s3    mean    n
    p0.0                     1.000   1.000       -   1.000    2
    p0.1                     1.000   1.000       -   1.000    2
    p0.25                    1.000   1.000       -   1.000    2
    p0.5                     1.000       -       -   1.000    1

    arm / fell_r0_at            s1      s2      s3    mean    n
    p0.0                         -       -       -       -    0
    p0.1                         -       -       -       -    0
    p0.25                        -       -       -       -    0
    p0.5                         -       -       -       -    0

- footholds:
    arm                    footholds  first_solved_gen per row
    p0.0                   0/3        -,-,-
    p0.1                   0/3        -,-,-
    p0.25                  0/3        -,-,-
    p0.5                   0/3        -,-,-

- typed states fired: ['POSITIVE_CONTROL_FAILED']
    POSITIVE_CONTROL_FAILED  {"arm": "p0.0", "metric": "peak_r0", "min": 0.5, "rows": 3, "rows_meeting": 0, "values": [0.0417, 0.125, 0.0]}
- disposition candidate (machine): POSITIVE_CONTROL_FAILED -- assay precondition failed; the scientific question was not posed
- claim ceiling (machine): none; preregistered ceiling: weak at best (n=3, one ladder); a capable negative = revisits at p<=0.5 do not retain rung-0 competence

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: none (dry run)
- all TERMINATED: n/a

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-06

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: POSITIVE_CONTROL_FAILED (machine candidate POSITIVE_CONTROL_FAILED). 
