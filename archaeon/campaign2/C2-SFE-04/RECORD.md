# C2-SFE-04 -- falsify SFE-07's failed-genotype seeding (n=10, battery)

## A. STARTUP (preregistration; sealed sha256:25174391bd88213532edb3e43a4df4fbd09cef043f012b0dc6596a2e870235ac)

- experiment ID: C2-SFE-04
- parents: SFE-07, SFE-08
- QUESTION: Do genotypes that FAILED W1_d1 (SFE-01's floor organisms), used as the whole generation 0, raise held-out competence on W3_K2 4-bit over the cell's own generation 0 (SFE-07: 2/3 vs 0/3 at n=3), and if so what is the smallest description of the transported thing: instruction order, opcode composition, genome length, 'any evolved floor', or a solved related population?
- PARENT EVIDENCE: SFE-07 attempt 2: failed_A 2/3 footholds vs random 0/3 (N100 G40 E16); SFE-08: length-defined organs of the same lineages at floor. Campaign-1 fill for these sets was harness-seeded (L2-011). Table: W3_K2 4-bit N100 G40 E16 0/3 OBSERVED_UNREACHABLE_AT_BUDGET.
- ASSAY CAPABILITY REQUIREMENT: ANY arm reaches a foothold in >= 1 of 10 seeds (the baseline may be unreachable by premise); every set has >= 100 members
- POSITIVE CONTROL: none separate: the assay is capable iff some arm reaches (target baseline_arm '*'); the random arm measures the cell's own reach
- REACHABILITY ESTIMATE:
    {"W0": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "first_solved_gens": [], "freq": null, "k": 0, "n": 0}, "at_budget_any_foundry": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "foundries": [], "freq": null, "k": 0, "n": 0}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0, 1.0], "budgets": [], "class": "UNESTABLISHED", "freq": null, "k": 0, "n": 0}}, "W3_K2": {"at_budget": {"band95": [0.0, 0.5615], "class": "OBSERVED_UNREACHABLE_AT_BUDGET", "first_solved_gens": [], "freq": 0.0, "k": 0, "n": 3}, "at_budget_any_foundry": {"band95": [0.0, 0.5615], "class": "OBSERVED_UNREACHABLE_AT_BUDGET", "foundries": ["instr1-16:6528b9dc"], "freq": 0.0, "k": 0, "n": 3}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0, 0.5615], "budgets": [[100, 40, 16]], "class": "OBSERVED_UNREACHABLE_AT_BUDGET", "freq": 0.0, "k": 0, "n": 3}}, "W7_K2": {"at_budget": {"band95": [0.0, 0.3903], "class": "OBSERVED_UNREACHABLE_AT_BUDGET", "first_solved_gens": [], "freq": 0.0, "k": 0, "n": 6}, "at_budget_any_foundry": {"band95": [0.0, 0.3903], "class": "OBSERVED_UNREACHABLE_AT_BUDGET", "foundries": ["instr1-16:6528b9dc"], "freq": 0.0, "k": 0, "n": 6}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"band95": [0.0, 0.3903], "budgets": [[200, 60, 16]], "class": "OBSERVED_UNREACHABLE_AT_BUDGET", "freq": 0.0, "k": 0, "n": 6}}}
- ARMS:
    - random
    - failed_A
    - failed_shuffled
    - failed_opcodes
    - length_matched
    - evolved_unrelated
    - evolved_solved
- COMMON-RANDOM-NUMBERS POLICY: default; every set replaces the whole generation 0 through common_fill (tagged); the random arm is the untouched generation 0; derived sets (shuffled / opcodes / length) are deterministic functions of failed_A keyed on the seed
- BUDGET:
    {"E": 16, "G": 40, "G_source": 60, "N": 100, "heldout_episodes": 48, "margin": 0.1, "seeds": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
- PRIMARY OBSERVABLE: competence_heldout of the elite per arm x seed; primary comparison failed_A vs random; direct_best per set as telemetry
- CLAIM CEILING: SUPPORTED_POSITIVE only if failed_A - random >= 0.10 AND every kill attack survives by the same margin; otherwise WEAK_POSITIVE / CAPABLE_NEGATIVE
- FALSIFICATION CONDITION: failed_A - random < 0.10 => the SFE-07 effect does not replicate; a kill arm within 0.10 of failed_A => that description suffices
- TYPED FAILURE CONDITIONS:
    - TARGET_UNREACHABLE (no arm reaches)
    - UNDERPOWERED
    - IMMATURE_ARTIFACT recorded on failed_A (its source is immature by construction; telemetry, D2-011)
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - direct_best per set
    - set summaries (length, opcode categories)
    - import_share_final (share of the final population descending from the set)
    - source maturity per set
    - first_solved_gen
    - reachability rows (random arm baseline)
- MACHINE CHANGES EXERCISED:
    - B (target '*' + battery)
    - C (common_fill whole-population substitution)
    - D (cross-campaign fetch as keyed steps)
    - E (maturity on evolved sets)
    - F (canonical digests on campaign-1 artifacts)
    - G
    - H (origin shares)
    - I
- decl (machine-read by archaeon.wse.states): {"battery": [{"name": "failed_shuffled", "rule": "failed_A - failed_shuffled >= 0.10 mean held-out", "type": "kill"}, {"name": "failed_opcodes", "rule": "failed_A - failed_opcodes >= 0.10 mean held-out", "type": "kill"}, {"name": "length_matched", "rule": "failed_A - length_matched >= 0.10 mean held-out", "type": "kill"}, {"name": "evolved_unrelated", "rule": "failed_A - evolved_unrelated >= 0.10 mean held-out", "type": "kill"}], "n_min": 10, "primary": {"control": "random", "metric": "competence_heldout", "min_effect": 0.1, "treatment": "failed_A"}, "probes": ["evolved_solved"], "target": {"baseline_arm": "*", "reach_metric": "reached", "reach_min": 1, "reachability_class": "OBSERVED_UNREACHABLE_AT_BUDGET"}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a02); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=CAPABLE_NEGATIVE
    a02  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 3; artifacts 22; imports 21; records 70; errors 0
- import hash checks: 21/21 ok
- timings (s): exchange_s=6.69, fetch_s=0.14, records_s=19.57, sources_s=67.07, startup_s=0.18, targets_s=65.86, teardown_s=0.48, total_s=161.3
- decisions: D2-012: assay capability = ANY arm reaches (target baseline_arm '*'); the premise of a transport-unlocks-an-unreachable-cell design is that the baseline may not reach
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / competence_heldout      s1     s10      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    evolved_solved           0.542   0.438   0.625   0.458   0.604   0.062   0.500   0.542   0.062   0.438   0.427   10
    evolved_unrelated        0.062   0.083   0.021   0.042   0.604   0.062   0.583   0.062   0.479   0.062   0.206   10
    failed_A                 0.062   0.438   0.438   0.042   0.083   0.562   0.042   0.125   0.062   0.438   0.229   10
    failed_opcodes           0.542   0.021   0.021   0.458   0.604   0.521   0.042   0.542   0.479   0.083   0.331   10
    failed_shuffled          0.125   0.438   0.438   0.042   0.083   0.562   0.042   0.125   0.479   0.438   0.277   10
    length_matched           0.062   0.083   0.021   0.458   0.083   0.062   0.104   0.062   0.062   0.125   0.113   10
    random                   0.104   0.021   0.438   0.458   0.583   0.062   0.042   0.062   0.062   0.438   0.227   10

    arm / train_last            s1     s10      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    evolved_solved           0.688   0.688   0.500   0.625   0.562   0.062   0.562   0.562   0.188   0.562   0.500   10
    evolved_unrelated        0.062   0.062   0.125   0.250   0.562   0.062   0.500   0.000   0.375   0.062   0.206   10
    failed_A                 0.125   0.688   0.688   0.250   0.125   0.375   0.062   0.125   0.188   0.562   0.319   10
    failed_opcodes           0.688   0.062   0.125   0.625   0.562   0.750   0.062   0.562   0.375   0.062   0.388   10
    failed_shuffled          0.188   0.688   0.688   0.250   0.125   0.375   0.062   0.125   0.375   0.562   0.344   10
    length_matched           0.125   0.062   0.125   0.625   0.125   0.062   0.125   0.000   0.188   0.062   0.150   10
    random                   0.188   0.125   0.688   0.625   0.562   0.062   0.062   0.000   0.188   0.562   0.306   10

    arm / direct_best           s1     s10      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    evolved_solved           0.542   0.104   0.083   0.458   0.333   0.062   0.062   0.438   0.146   0.125   0.235   10
    evolved_unrelated        0.062   0.104   0.062   0.125   0.083   0.083   0.062   0.104   0.479   0.125   0.129   10
    failed_A                 0.062   0.604   0.062   0.125   0.083   0.062   0.062   0.104   0.062   0.438   0.167   10
    failed_opcodes           0.062   0.104   0.083   0.125   0.083   0.062   0.062   0.542   0.479   0.125   0.173   10
    failed_shuffled          0.062   0.104   0.083   0.042   0.083   0.062   0.062   0.104   0.146   0.125   0.087   10
    length_matched           0.062   0.021   0.062   0.042   0.083   0.062   0.062   0.104   0.062   0.083   0.065   10
    random                       -       -       -       -       -       -       -       -       -       -       -    0

- footholds:
    arm                    footholds  first_solved_gen per row
    evolved_solved         8/10       1,39,0,8,-,27,0,-,2,28
    evolved_unrelated      3/10       -,-,-,37,-,13,-,0,-,-
    failed_A               4/10       -,12,-,-,34,-,-,-,0,0
    failed_opcodes         6/10       38,-,14,17,38,-,1,0,-,-
    failed_shuffled        5/10       -,3,-,-,18,-,-,2,20,21
    length_matched         1/10       -,-,23,-,-,-,-,-,-,-
    random                 4/10       -,19,14,9,-,-,-,-,10,-

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.2271, "effect": 0.0021, "min_effect": 0.1, "n_control": 10, "n_treatment": 10, "paired": 10, "paired_wins": 3, "treatment_mean": 0.2292}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: SUPPORTED_POSITIVE only if failed_A - random >= 0.10 AND every kill attack survives by the same margin; otherwise WEAK_POSITIVE / CAPABLE_NEGATIVE

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

SFE-07's failed-genotype effect did not survive n=10 under common random numbers. Assay capable: 6 of 7 arms reached; the cell's own generation 0 reached 4/10 (generations 9-19), so W3_K2 4-bit N100 G40 E16 is REACHABLE (table now 4/13), not the OBSERVED_UNREACHABLE the campaign-1 'random' arm (a harness-seeded set of 135 random manifests, 0/3) had suggested. PRIMARY: failed_A - random = +0.002 held-out (paired wins 3/10), footholds 4/10 vs 4/10; CAPABLE_NEGATIVE accepted. Kill battery (moot for the claim, informative for the landscape): failed_shuffled 5/10 (0.28) and failed_opcodes 6/10 (0.33) BEAT the intact failed genomes (0.23): instruction order carries nothing and the genomes' opcode words with random operands do better than the originals; length_matched 1/10 (0.11): random words at the failed set's lengths (mean 20.8 instructions, max 52, against generation 0's 5.9) are worse than the cell's own short random organisms, so the long failed genomes were REPAIRING a length handicap, not adding capability; evolved_unrelated 3/10 (0.21): floor organisms of a W7_K2 search do about what the failed W1_d1 organisms do. Probe evolved_solved 8/10 (0.43, max 0.625): populations of W0 4-bit searches run to solution (7/10 sources solved by generation 27) seed footholds, with direct reuse up to 0.54 before any evolution; as in C2-SFE-03 this is a transported sub-solution (W0 answers the one asked stream of W3_K2 in the half of the episodes where the asked stream is the last one), and 4 of the 8 footholds sit in the half-credit band. A confound in the parent design surfaced: SFE-07 rebuilt manifests from genomes with a seeded random draw of n_regs/persist/tick_budget, so 'the same failed genotype' has a different manifest per seed, and its direct-reuse score swung from 0.06 to 0.60 across seeds with the genome fixed (failed_A direct_best per seed 0.06-0.60). What is transported by a failed W1_d1 population is therefore: nothing that survives shuffling, operand randomisation or replacement by an unrelated evolved floor; length that costs rather than pays; and, when a solved neighbour is used instead, a direct sub-solution. Must NOT be claimed: that failed genotypes carry reusable computation; that solved W0 populations improve search on W3_K2 beyond direct half-credit reuse.

## D. TEARDOWN (generated)

- worlds: {"source-solved": "TERMINATED", "source-unrelated": "TERMINATED", "world-B": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C2-SFE-04

Zero engine errors; 3 worlds; SFE-01's failure artifacts fetched from campaign 1's TERMINATED source world under campaign 1's own principal (3/3 hash ok, 135 genomes) through keyed steps; 21 artifacts (every evolved set with a maturity block; failed_A with a RECONSTRUCTED block from SFE-01's floor counts); 21/21 imports hash ok; 70 records; 90 reachability rows. Findings: (1) import_share_final is 1.0 by construction when a set replaces the whole generation 0 -- the telemetry is informative only for partial substitution (note for the funnel, not a defect); (2) SFE-07's manifest-rebuild recipe (random fields per seed) is a hidden treatment: recorded as a confound in the parent (L2); (3) the set summaries (instruction length per set) were what exposed the length handicap -- the L-027 telemetry paid for itself; (4) the mature W0 sources are again 'treated' rows for reachability because of the stop rule (L2-026 stands).

## F. LANDSCAPE / GRADIENT NOTES

W3_K2 4-bit N100 G40 E16: 4/13 baseline (first solved 9-19), a cell that reads REACHABLE once the baseline is the cell's own generation 0 rather than a harness-seeded set. Genome length is a cliff at this budget: 100 random genomes of the failed set's lengths (mean 20.8) reached 1/10 where the cell's own 5.9-instruction organisms reached 4/10. Solved W0 populations land on W3_K2 in 8/10 seeds within 0-39 generations (direct reuse 0.54 in the best case): the W0 -> K=2 gradient of SFE-10 and C2-SFE-03 holds for ask_mode=one as well. W0 4-bit N200: 7/10 solved by generation 27 (this run) beside 10/12 in C2-SFE-03: COMMON.

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). SFE-07's failed-genotype seeding does not replicate at n=10 (failed_A - random = +0.002; 4/10 vs 4/10); the campaign-1 weak positive is retired, and its control arm's 0/3 is explained by a harness-seeded random set on a cell whose own generation 0 reaches 4/10. Shuffled and operand-randomised versions of the failed genomes do as well or better; length-matched random genomes do worse: the smallest description of what the failed set transported is 'long genomes', which cost.
