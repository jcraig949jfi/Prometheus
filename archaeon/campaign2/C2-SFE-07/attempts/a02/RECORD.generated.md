# C2-SFE-07 -- producer-consumer: maturity gating and wall-clock accounting

## A. STARTUP (preregistration; sealed sha256:23e8616ee2a00746d439d32bb08245bb0f278b6efd296cdb3ae01ff37aaf8f3e)

- experiment ID: C2-SFE-07
- parents: SFE-10
- QUESTION: Under a 60-generation envelope with explicit communication (ceil(bytes/4096) gens) and storage (0.5 gen/artifact) costs, does a producer on W0 4-bit that publishes ONLY once it has solved its cell (maturity gate) pay for itself when charged serially, and does it pay when it runs on its own clock and its elites are injected mid-run (wall-clock accounting)?
- PARENT EVIDENCE: SFE-10: mono 3/3 vs pc_0.4 1/3, pc_0.2 0/3 (CAPABLE_NEGATIVE); the one paying exchange came from a producer that solved W0 (1.0 at G12). C2-SFE-03/04: solved-W0 material lands on the K=2 half-credit shelf directly. Table: W2_K2 4-bit N200 G60 7/17; W0 4-bit COMMON by ~G35.
- ASSAY CAPABILITY REQUIREMENT: mono reaches a foothold in >= 1 of 6 seeds (TARGET_UNREACHABLE otherwise); >= 1 producer solves within the cap (else no gated exchange happens and the rows record the cost of closed gates)
- POSITIVE CONTROL: mono on W2_K2 4-bit (own generation 0): expected 0.41 per seed
- REACHABILITY ESTIMATE:
    {"W0": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0, 1.0], "budgets": [], "class": "UNESTABLISHED", "freq": null, "k": 0, "n": 0}}, "W2_K2": {"at_budget": {"band95": [0.2834, 0.6763], "class": "REACHABLE", "first_solved_gens": [13, 19, 32, 35, 39, 48, 49, 50, 54, 59], "freq": 0.4762, "k": 10, "n": 21}, "at_budget_any_foundry": {"band95": [0.2834, 0.6763], "class": "REACHABLE", "foundries": ["instr1-16:6528b9dc"], "freq": 0.4762, "k": 10, "n": 21}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.2153, 0.5577], "budgets": [[200, 36, 16], [200, 48, 16], [200, 60, 16]], "class": "REACHABLE", "freq": 0.3704, "k": 10, "n": 27}}}
- ARMS:
    - mono
    - gated_serial
    - gated_serial_noex
    - parallel
- COMMON-RANDOM-NUMBERS POLICY: default; the same producer run per seed feeds both exchange arms; consumers share generation 0 (gated_serial substitutes the fetched top-4 into it; parallel injects them at arrival)
- BUDGET:
    {"E": 16, "G": 60, "N": 200, "comm_bytes_per_gen": 4096, "full_solve": 0.9, "heldout_episodes": 48, "producer_cap": 30, "seeds": [1, 2, 3, 4, 5, 6], "storage_gen_per_artifact": 0.5, "top_k": 4}
- PRIMARY OBSERVABLE: competence_heldout per arm x seed (parallel vs mono; gated_serial vs mono secondary); first_solved_gen, charged generation at foothold and full_solve_gen as the economics
- CLAIM CEILING: weak at best (n=6, one source/target pair); the break-even generation (producer solve time + comm + storage vs mono's exit) is the product
- FALSIFICATION CONDITION: parallel - mono < 0.10 held-out => wall-clock division of labour does not pay at this envelope; gated_serial - mono < 0.10 => serial gating does not pay
- TYPED FAILURE CONDITIONS:
    - TARGET_UNREACHABLE (mono 0/6)
    - IMMATURE_ARTIFACT cannot occur by construction (gate); a closed gate is a row with imported=false
    - UNDERPOWERED
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - producer solve time and maturity
    - costs charged per row
    - arrival generation
    - import lineage share at the end
    - first foothold and first full solve generations
    - reachability rows (mono baseline)
- MACHINE CHANGES EXERCISED:
    - E (gate = maturity.solved; publish requires it)
    - G (mid-run injection through the step API)
    - C (common_fill substitution)
    - D
    - F (costs from canonical bytes)
    - H (origin shares)
    - I
- decl (machine-read by archaeon.wse.states): {"n_min": 6, "primary": {"control": "mono", "metric": "competence_heldout", "min_effect": 0.1, "treatment": "parallel"}, "target": {"baseline_arm": "mono", "reach_metric": "reached", "reach_min": 1, "reachability_class": "REACHABLE"}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a02); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=TARGET_UNREACHABLE
    a02  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=WEAK_POSITIVE
- engine: live; worlds 2; artifacts 4; imports 3; records 24; errors 0
- import hash checks: 3/3 ok
- timings (s): consumers_s=85.47, exchange_s=0.85, producers_s=5.84, records_s=6.57, startup_s=0.2, teardown_s=0.37, total_s=100.4
- decisions: D2-015: the maturity gate is the artifact's `solved` flag; an unsolved producer publishes nothing and the consumer still pays its cap (the cost of a closed gate is a measurement, not a failure)
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / competence_heldout      s1      s2      s3      s4      s5      s6    mean    n
    gated_serial             0.333   0.240   0.510   0.542   0.052   0.062   0.290    6
    gated_serial_noex        0.031   0.240   0.260   0.073   0.052   0.062   0.120    6
    mono                     0.323   0.292   0.344   0.104   0.333   0.542   0.323    6
    parallel                 0.375   0.292   0.510   0.542   0.333   0.542   0.432    6

    arm / first_solved_gen      s1      s2      s3      s4      s5      s6    mean    n
    gated_serial                 -       -       5       4       -       -   4.500    2
    gated_serial_noex            -       -      35       -       -       -  35.000    1
    mono                         -       -      35       -       -      49  42.000    2
    parallel                     -       -      25      25       -      49  33.000    3

    arm / charged_gen_at_foothold      s1      s2      s3      s4      s5      s6    mean    n
    gated_serial                 -       -  24.500  25.500       -       -  25.000    2
    gated_serial_noex            -       -  53.000       -       -       -  53.000    1
    mono                         -       -  35.000       -       -  49.000  42.000    2
    parallel                     -       -  25.500  25.500       -  49.000  33.333    3

    arm / full_solve_gen        s1      s2      s3      s4      s5      s6    mean    n
    gated_serial                 -       -       -       -       -       -       -    0
    gated_serial_noex            -       -       -       -       -       -       -    0
    mono                         -       -       -       -       -       -       -    0
    parallel                     -       -       -       -       -       -       -    0

- footholds:
    arm                    footholds  first_solved_gen per row
    gated_serial           2/6        -,-,5,4,-,-
    gated_serial_noex      1/6        -,-,35,-,-,-
    mono                   2/6        -,-,35,-,-,49
    parallel               3/6        -,-,25,25,-,49

- typed states fired: none
- disposition candidate (machine): WEAK_POSITIVE -- effect >= min_effect but n < 10 or a declared falsification attack failed or was not run
    evidence: {"control_mean": 0.3229, "effect": 0.1094, "min_effect": 0.1, "n_control": 6, "n_treatment": 6, "paired": 6, "paired_wins": 3, "treatment_mean": 0.4323}
    battery: {"attacked": 0, "declared": 0, "survived": 0}
- claim ceiling (machine): weak; not for propagation; preregistered ceiling: weak at best (n=6, one source/target pair); the break-even generation (producer solve time + comm + storage vs mono's exit) is the product

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"consumer": "TERMINATED", "producer": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-07

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: WEAK_POSITIVE (machine candidate WEAK_POSITIVE). 
