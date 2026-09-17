# C2-SFE-07 -- producer-consumer: maturity gating and wall-clock accounting

## A. STARTUP (preregistration; sealed sha256:ca2ab0088b16c2f835eb17521f6f8f00bd98eca7286d3de224b7d44b1b1e9970)

- experiment ID: C2-SFE-07
- parents: SFE-10
- QUESTION: Under a 8-generation envelope with explicit communication (ceil(bytes/4096) gens) and storage (0.5 gen/artifact) costs, does a producer on W0 4-bit that publishes ONLY once it has solved its cell (maturity gate) pay for itself when charged serially, and does it pay when it runs on its own clock and its elites are injected mid-run (wall-clock accounting)?
- PARENT EVIDENCE: SFE-10: mono 3/3 vs pc_0.4 1/3, pc_0.2 0/3 (CAPABLE_NEGATIVE); the one paying exchange came from a producer that solved W0 (1.0 at G12). C2-SFE-03/04: solved-W0 material lands on the K=2 half-credit shelf directly. Table: W2_K2 4-bit N200 G60 7/17; W0 4-bit COMMON by ~G35.
- ASSAY CAPABILITY REQUIREMENT: mono reaches a foothold in >= 1 of 3 seeds (TARGET_UNREACHABLE otherwise); >= 1 producer solves within the cap (else no gated exchange happens and the rows record the cost of closed gates)
- POSITIVE CONTROL: mono on W2_K2 4-bit (own generation 0): expected 0.41 per seed
- REACHABILITY ESTIMATE:
    {"W0": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0, 1.0], "budgets": [], "class": "UNESTABLISHED", "freq": null, "k": 0, "n": 0}}, "W2_K2": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.2153, 0.5577], "budgets": [[200, 36, 16], [200, 48, 16], [200, 60, 16]], "class": "REACHABLE", "freq": 0.3704, "k": 10, "n": 27}}}
- ARMS:
    - mono
    - gated_serial
    - gated_serial_noex
    - parallel
- COMMON-RANDOM-NUMBERS POLICY: default; the same producer run per seed feeds both exchange arms; consumers share generation 0 (gated_serial substitutes the fetched top-4 into it; parallel injects them at arrival)
- BUDGET:
    {"E": 4, "G": 8, "N": 24, "comm_bytes_per_gen": 4096, "full_solve": 0.9, "heldout_episodes": 48, "producer_cap": 6, "seeds": [1, 2, 3], "storage_gen_per_artifact": 0.5, "top_k": 4}
- PRIMARY OBSERVABLE: competence_heldout per arm x seed (parallel vs mono; gated_serial vs mono secondary); first_solved_gen, charged generation at foothold and full_solve_gen as the economics
- CLAIM CEILING: weak at best (n=3, one source/target pair); the break-even generation (producer solve time + comm + storage vs mono's exit) is the product
- FALSIFICATION CONDITION: parallel - mono < 0.10 held-out => wall-clock division of labour does not pay at this envelope; gated_serial - mono < 0.10 => serial gating does not pay
- TYPED FAILURE CONDITIONS:
    - TARGET_UNREACHABLE (mono 0/3)
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
- decl (machine-read by archaeon.wse.states): {"n_min": 3, "primary": {"control": "mono", "metric": "competence_heldout", "min_effect": 0.1, "treatment": "parallel"}, "target": {"baseline_arm": "mono", "reach_metric": "reached", "reach_min": 1, "reachability_class": "UNESTABLISHED"}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a00); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=TARGET_UNREACHABLE
- engine: dry-run; worlds 0; artifacts 0; imports 0; records 0; errors 0
- timings (s): consumers_s=0.26, exchange_s=0.0, producers_s=0.11, records_s=0.0, total_s=0.6
- decisions: D2-015: the maturity gate is the artifact's `solved` flag; an unsolved producer publishes nothing and the consumer still pays its cap (the cost of a closed gate is a measurement, not a failure)
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / competence_heldout      s1      s2      s3    mean    n
    gated_serial             0.073   0.083   0.021   0.059    3
    gated_serial_noex        0.073   0.083   0.021   0.059    3
    mono                     0.073   0.042   0.031   0.049    3
    parallel                 0.073   0.042   0.031   0.049    3

    arm / first_solved_gen      s1      s2      s3    mean    n
    gated_serial                 -       -       -       -    0
    gated_serial_noex            -       -       -       -    0
    mono                         -       -       -       -    0
    parallel                     -       -       -       -    0

    arm / charged_gen_at_foothold      s1      s2      s3    mean    n
    gated_serial                 -       -       -       -    0
    gated_serial_noex            -       -       -       -    0
    mono                         -       -       -       -    0
    parallel                     -       -       -       -    0

    arm / full_solve_gen        s1      s2      s3    mean    n
    gated_serial                 -       -       -       -    0
    gated_serial_noex            -       -       -       -    0
    mono                         -       -       -       -    0
    parallel                     -       -       -       -    0

- footholds:
    arm                    footholds  first_solved_gen per row
    gated_serial           0/3        -,-,-
    gated_serial_noex      0/3        -,-,-
    mono                   0/3        -,-,-
    parallel               0/3        -,-,-

- typed states fired: ['TARGET_UNREACHABLE']
    TARGET_UNREACHABLE  {"band95_upper": 0.5615, "baseline_arm": "mono", "reached": 0, "rows": 3, "table_class": "UNESTABLISHED"}
- disposition candidate (machine): TARGET_UNREACHABLE -- assay precondition failed; the scientific question was not posed
- claim ceiling (machine): none; preregistered ceiling: weak at best (n=3, one source/target pair); the break-even generation (producer solve time + comm + storage vs mono's exit) is the product

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: none (dry run)
- all TERMINATED: n/a

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-07

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: TARGET_UNREACHABLE (machine candidate TARGET_UNREACHABLE). 
