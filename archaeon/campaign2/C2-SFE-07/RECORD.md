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

Assay capable (mono 2/6 footholds at 35 and 49; the same rows as C2-SFE-01's fresh arm and C2-SFE-02's control, by common random numbers). Producers solved W0 4-bit within the 30-generation cap in 3 of 6 seeds (first solved 17, 18, 19; elites 1.0) and the maturity gate closed the other three (elites 0.06-0.19: nothing published, the cap still charged). PRIMARY: parallel - mono = +0.109 held-out (paired wins 3/6; footholds 3/6 vs 2/6); the machine candidate WEAK_POSITIVE is accepted at exactly the preregistered margin and at n=6, i.e. as weak as a positive gets. The economics, read per seed: where the producer solved, the injected elites (arrival = solve generation + 1 comm generation) produced a foothold within 6-7 generations of arrival (seeds 3, 4: foothold at 25 against mono's 35 and never), and in seed 1 they did not (held-out 0.375 vs mono 0.323, no foothold); where the producer did not solve, parallel equals mono (nothing arrived). Serial gating did NOT pay on average: gated_serial 2/6 footholds (charged generation 24.5 and 25.5 at foothold, 10 generations before mono's 35) and mean held-out 0.29 against mono's 0.32, because the three closed gates cost their cap (consumer budget 30 of 60) for nothing (held-out 0.05-0.06 vs mono 0.33-0.54 in seeds 5 and 6); the noex control confirms the loss is the budget (gated_serial_noex 1/6). Break-even as measured: a producer that solves by generation ~19 and ships in 1 generation beats the consumer's own exit (35-49) by 10-24 generations; a producer that does not solve costs its whole cap. Wall-clock accounting removes the closed-gate cost from the consumer and keeps the gain, which is why parallel is the only arm above mono. Two further observations: (i) import_share_final = 1.0 in every imported seed: the four injected W0 elites (half-credit solutions on W2_K2) displaced the entire population within the remaining generations -- the exchange is a takeover, not a seeding; (ii) 0 of 24 rows reached a FULL solve (training best >= 0.9): every foothold, imported or not, is the half-credit shelf, and neither the head start nor 60 generations converted it. Must NOT be claimed: that division of labour pays in general (n=6, one pair of cells, effect at the margin); that gating is useless (it paid in 2 of 3 open gates; the closed gates are the cost).

## D. TEARDOWN (generated)

- worlds: {"consumer": "TERMINATED", "producer": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-07

Zero engine errors; 2 worlds; 3 producer-elite artifacts (the gate published nothing for the three unsolved producers, by construction of publish() + maturity.solved); 3/3 imports hash ok; 24 records; 30 reachability rows. The mid-run injection went through the step API (inject() replaces the worst four of the current scored generation and re-sorts; elitism and tournament see the imports at once). Bench notes: (1) the takeover (import share 1.0 within ~10 generations) says injected elites need a fitness handicap or a cap on their offspring if seeding rather than replacement is the intent -- a KEEP_POLICY question for C3; (2) the full-solve observable (>= 0.9) was 0/24: the reachability table needs the per-cell full-solve threshold (L2-025) before a C3 economics run is worth its budget; (3) charged_gen_at_foothold is the right economic observable and is now a row field.

## F. LANDSCAPE / GRADIENT NOTES

W2_K2 4-bit N200 G60 E16 from the half-credit shelf upward: 0 full solves in 24 runs (60 generations), including runs that sat on the shelf from generation 25. The shelf is a plateau in its own right. Producer W0 4-bit N200: solve times 17-19 in the three seeds that solved by 30 (C2-SFE-03: 0-31, one at 99): the W0 solve-time distribution has a long tail; a cap of 30 closes the gate on about half the seeds. Injected half-credit solvers take the population over in ~10 generations: the shelf organism dominates fitness so completely that the search's diversity collapses around it -- one candidate explanation for why the second stream is never found after the first is imported.

DISPOSITION: WEAK_POSITIVE (machine candidate WEAK_POSITIVE). Assay capable; n=6; parallel (wall-clock) exchange beats mono by exactly the preregistered margin (+0.109 held-out, 3/6 vs 2/6 footholds, 3/6 paired wins) because it keeps the gain of open gates without the cost of closed ones; serial gating does not pay on average (closed gates cost their cap). Break-even: producer solve + 1 comm generation < mono's exit (35-49). No full solves anywhere.
