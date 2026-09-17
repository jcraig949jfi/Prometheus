# C2-SFE-06 -- retention economics on a rung ladder

## A. STARTUP (preregistration; sealed sha256:d08ad16428043955fb3b302075b6aee1676e262da9ea74f2e7e15b14eccfbd3a)

- experiment ID: C2-SFE-06
- parents: SFE-05
- QUESTION: When the selective pressure climbs a delay ladder (W0 -> d1 -> d2 -> d4, 25 generations per rung), at what revisit share p of earlier rungs in the training battery is rung-0 competence retained to the end, and what does retention cost on the top rung?
- PARENT EVIDENCE: SFE-05: adaptive +0.155, transfer +0.113 (n=3); fixed/on lost Kd-0 competence entirely (forgetting shelf hidden by the battery mean, L-022). Table: W0 4-bit COMMON by ~G35 (10/12 C2-SFE-03, 7/10 C2-SFE-04); W1_d4 4-bit RARE (1/14 at G60).
- ASSAY CAPABILITY REQUIREMENT: the ladder is climbable at its bottom: the p0.0 arm reaches rung-0 competence >= 0.5 (peak_r0) in >= 3 of 6 seeds; otherwise POSITIVE_CONTROL_FAILED (nothing to retain)
- POSITIVE CONTROL: p0.0 on rung 0 during the first 25 generations (W0 4-bit): expected ~0.7 per seed
- REACHABILITY ESTIMATE:
    {"W0": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0, 1.0], "budgets": [], "class": "UNESTABLISHED", "freq": null, "k": 0, "n": 0}}, "W1_d4": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0127, 0.3147], "budgets": [[200, 60, 16]], "class": "RARE", "freq": 0.0714, "k": 1, "n": 14}}}
- ARMS:
    - p0.0
    - p0.1
    - p0.25
    - p0.5
- COMMON-RANDOM-NUMBERS POLICY: default; identical generation 0 and selection stream for every p (the RNG is keyed on rung 0's world id); episodes per generation keyed on (generation, seed) so arms share the current-rung episodes and differ only in the revisit share
- BUDGET:
    {"E": 16, "G": 100, "N": 200, "probe_episodes": 24, "probe_every": 5, "rung_gens": 25, "rungs": [{"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 0, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W0", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}, {"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 1, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W1_d1", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}, {"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 2, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W1_d2", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}, {"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 4, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W1_d4", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}], "seeds": [1, 2, 3, 4, 5, 6], "shares": [0.0, 0.1, 0.25, 0.5]}
- PRIMARY OBSERVABLE: final_r0 (rung-0 competence of the elite at the end, 24 eval episodes) per arm x seed; rung x generation matrix; shelf report
- CLAIM CEILING: weak at best (n=6, one ladder); a capable negative = revisits at p<=0.5 do not retain rung-0 competence
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
- decl (machine-read by archaeon.wse.states): {"n_min": 6, "positive_control": {"arm": "p0.0", "metric": "peak_r0", "min": 0.5, "min_rows": 3}, "primary": {"control": "p0.0", "metric": "final_r0", "min_effect": 0.15, "treatment": "p0.25"}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a02); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=POSITIVE_CONTROL_FAILED
    a02  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=WEAK_POSITIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 24; errors 0
- timings (s): ladder_s=295.6, records_s=6.53, startup_s=0.97, teardown_s=0.19, total_s=304.3
- decisions: D2-014: revisit share p is the only difference between arms; it is an ecological pressure (old conditions recur), never a reward for retaining anything
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / final_r0              s1      s2      s3      s4      s5      s6    mean    n
    p0.0                     0.042   0.125   1.000   0.000   0.083   0.083   0.222    6
    p0.1                     1.000   0.125   1.000   1.000   0.083   0.833   0.674    6
    p0.25                    1.000   0.125   1.000   1.000   1.000   0.083   0.701    6
    p0.5                     1.000   1.000   1.000   1.000   1.000   1.000   1.000    6

    arm / final_r3              s1      s2      s3      s4      s5      s6    mean    n
    p0.0                     0.042   0.083   1.000   1.000   0.000   0.042   0.361    6
    p0.1                     1.000   0.083   1.000   1.000   0.000   0.583   0.611    6
    p0.25                    1.000   0.083   1.000   1.000   1.000   0.042   0.688    6
    p0.5                     1.000   0.083   1.000   1.000   1.000   0.000   0.681    6

    arm / peak_r0               s1      s2      s3      s4      s5      s6    mean    n
    p0.0                     1.000   0.167   1.000   1.000   0.167   0.167   0.583    6
    p0.1                     1.000   0.167   1.000   1.000   0.083   0.833   0.681    6
    p0.25                    1.000   0.167   1.000   1.000   1.000   0.083   0.708    6
    p0.5                     1.000   1.000   1.000   1.000   1.000   1.000   1.000    6

    arm / retention_r0          s1      s2      s3      s4      s5      s6    mean    n
    p0.0                     0.042   0.750   1.000   0.000   0.500   0.500   0.465    6
    p0.1                     1.000   0.750   1.000   1.000   1.000   1.000   0.958    6
    p0.25                    1.000   0.750   1.000   1.000   1.000   1.000   0.958    6
    p0.5                     1.000   1.000   1.000   1.000   1.000   1.000   1.000    6

    arm / fell_r0_at            s1      s2      s3      s4      s5      s6    mean    n
    p0.0                        25       -      25      25       -       -  25.000    3
    p0.1                        30       -       -      25       -       -  27.500    2
    p0.25                       45       -       -       -       -       -  45.000    1
    p0.5                         -       -       -       -       -       -       -    0

- footholds:
    arm                    footholds  first_solved_gen per row
    p0.0                   3/6        18,-,17,19,-,-
    p0.1                   4/6        18,-,17,19,-,91
    p0.25                  4/6        18,-,17,19,88,-
    p0.5                   4/6        18,-,17,19,82,-

- typed states fired: none
- disposition candidate (machine): WEAK_POSITIVE -- effect >= min_effect but n < 10 or a declared falsification attack failed or was not run
    evidence: {"control_mean": 0.2222, "effect": 0.4792, "min_effect": 0.15, "n_control": 6, "n_treatment": 6, "paired": 6, "paired_wins": 3, "treatment_mean": 0.7014}
    battery: {"attacked": 0, "declared": 0, "survived": 0}
- claim ceiling (machine): weak; not for propagation; preregistered ceiling: weak at best (n=6, one ladder); a capable negative = revisits at p<=0.5 do not retain rung-0 competence

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"ladder": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-06

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: WEAK_POSITIVE (machine candidate WEAK_POSITIVE). 
