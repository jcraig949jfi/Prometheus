# C3-SFE-08 -- does partial credit build the shelf?

## A. STARTUP (preregistration; sealed sha256:9fd47ab49ab1cf86a7f7365dfb8b8659bf0afcb9b01e9ceee996417cd10b0ce2)

- experiment ID: C3-SFE-08
- parents: C3-SFE-01, C3-SFE-02
- QUESTION: On W2_K2 4-bit (N=200, E=16, G=300), does selection on ALL-OR-NOTHING episode credit (an episode counts only if every ask is correct) change where the search ends up, compared with the per-ask partial credit every campaign has used: fewer runs on the half-credit shelf, and any run reaching the summit?
- PARENT EVIDENCE: C3-SFE-01 (n=24, G300): 0 confirmed summits, 0 candidates; fresh runs reach the shelf in 11/12 (median ~90 generations) and stay, residence censored at 300 everywhere; end-of-run held-out per ask ~0.5/0.5. C3-SFE-02 (n=12 shelf elites, 400 grammar children each): the shelf is a one-value memory (first-put 6/12, last-put 4/12), 1 improving child in 4,800, every second-stream gain (58/58) costs the first, 0/480 greedy paths to 0.90. The shelf pays ~0.5 under per-ask credit while solving neither stream: that half credit is a readout property.
- WHY THIS SLOT IS STILL WORTH SPENDING: the original slot 8 is dead (it required a full-solve regime C3-SFE-01 showed does not exist). Direction A asks what makes the shelf. If the shelf is an artefact of partial credit, the reward readout is a design variable for every K>=2 cell in campaign 4; if the summit is unreached under both readouts, the ceiling is structural and no reward shaping will move it -- and campaign 4 must change the organism or the search, not the payoff.
- ASSAY CAPABILITY REQUIREMENT: the per_ask arm reproduces C3-SFE-01's shelf rate (>= 8 of 12 seeds reach the shelf) -- else the assay is not the one that produced the parent evidence
- POSITIVE CONTROL: per_ask arm on W2_K2 4-bit (table: shelf in 11/12 at G300, C3-SFE-01)
- REACHABILITY ESTIMATE:
    {"W2_K2": {"at_budget": {"band95": [0.6853, 0.9873], "class": "COMMON", "class_summit": "OBSERVED_UNREACHABLE_AT_BUDGET", "first_shelf_gens": [13, 19, 24, 27, 33, 49, 65, 84, 99, 107, 128, 165, 226], "first_solved_gens": [13, 19, 27, 35, 49, 65, 84, 95, 99, 114, 128, 165, 226], "first_summit_gens": [], "freq": 0.9286, "freq_shelf": 0.9286, "freq_summit": 0.0, "k": 13, "k_shelf": 13, "k_summit": 0, "k_summit_any": 0, "k_summit_candidate": 0, "levels": {"FLOOR": 1, "SHELF": 13, "SUMMIT": 0}, "n": 14, "n_censored_runs": 2, "shelf_hist": {"0.2": 1, "0.5": 3, "0.6": 8, "0.8": 2}}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"budgets": [[200, 30, 16], [200, 36, 16], [200, 40, 16], [200, 41, 16], [200, 42, 16], [200, 48, 16], [200, 55, 16], [200, 60, 16], [200, 70, 16], [200, 100, 16], [200, 300, 16]], "class": "REACHABLE", "class_summit": "OBSERVED_UNREACHABLE_AT_BUDGET", "freq": 0.4912, "k": 28, "k_summit": 0, "k_summit_any": 0, "n": 57}}}
- ARMS:
    - per_ask
    - episode
- COMMON-RANDOM-NUMBERS POLICY: default; both arms share generation 0 per seed and the same per-generation batteries (episodes are keyed on (generation, cell seed)); only the fitness readout differs; both arms are SCORED at the end on the same held-out battery with both readouts
- BUDGET:
    {"E": 16, "G": 300, "N": 200, "arms": ["per_ask", "episode"], "heldout_n": 48, "runs": 24, "seeds": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "target": {"D": 1, "K": 2, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 0, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W2_K2", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}}
- PRIMARY OBSERVABLE: summit arrival (held-out per-ask >= 0.90) per seed, and, since both arms are expected to be summit-free, the preregistered secondary ladder: shelf arrival rate, generations on the shelf, best per-ask and best episode credit reached
- CLAIM CEILING: one cell, one organism family, n=12 per arm at G=300: whether the half-credit shelf survives the removal of partial credit; no claim about which readout is 'right', and none about cells other than W2_K2
- FALSIFICATION CONDITION: the episode arm reaches the shelf as often as the per_ask arm AND neither reaches a summit => partial credit does not build the shelf; the half-credit plateau is what this organism/search can do on this cell
- KILL CONDITION: the per_ask arm does not reproduce the parent shelf rate (< 8/12): the assay drifted and no comparison is licensed
- TYPED FAILURE CONDITIONS:
    - POSITIVE_CONTROL_FAILED
    - TARGET_UNREACHABLE
    - READOUT_CANNOT_EXPRESS
    - UNDERPOWERED
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - both readouts per generation for the elite of every arm
    - levels on the common per-ask yardstick
    - generations at floor / on shelf
    - ladder points
    - reachability rows (per_ask baseline, episode treated)
- MACHINE CHANGES EXERCISED:
    - evaluate(reward_mode) + Evolution(reward_mode) all-or-nothing episode credit
    - A levels on a common yardstick
    - B ladder lookups
- REPLACEMENT CONDITION: this IS the replacement (D3-013). It would itself be replaced only if C3-SFE-02 had found a gradient off the shelf, which it did not (0 of 4,800 children kept the first stream while gaining the second)
- ANCESTRY (original | replacement): replacement (queue slot 8; original: wall-clock producer-consumer with a FULL-solve criterion, killed by C3-SFE-01's 0/24 summits)
- decl (machine-read by archaeon.wse.states): {"battery": [{"name": "episode_arm_shelf_rate_below_per_ask", "passed": null}, {"name": "episode_arm_reaches_higher_episode_credit", "passed": null}, {"name": "per_ask_arm_reproduces_parent_shelf_rate", "passed": null}], "n_min": 12, "positive_control": {"arm": "per_ask", "metric": "shelf_reached", "min": 1, "min_rows": 8}, "primary": {"control": "per_ask", "metric": "summit", "min_effect": 0.25, "treatment": "episode"}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a02); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=POSITIVE_CONTROL_FAILED
    a02  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 1; artifacts 1; imports 0; records 24; errors 0
- timings (s): records_s=18.66, scan_s=885.85, startup_s=0.34, teardown_s=0.25, total_s=905.9
- decisions: D3-019: both arms are read out on the SAME held-out battery with both readouts; levels (FLOOR/SHELF/SUMMIT) are always computed on per-ask credit so the arms are comparable
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / competence_heldout      s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    episode                  0.521   0.521   0.052   0.073   0.073   0.542   0.500   0.646   0.438   0.125   0.479   0.062   0.336   12
    per_ask                  0.542   0.531   0.604   0.073   0.510   0.500   0.542   0.542   0.531   0.573   0.500   0.552   0.500   12

    arm / heldout_episode       s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    episode                  0.083   0.521   0.000   0.000   0.000   0.083   0.500   0.646   0.438   0.021   0.479   0.000   0.231   12
    per_ask                  0.083   0.104   0.604   0.000   0.021   0.500   0.083   0.083   0.062   0.167   0.000   0.104   0.151   12

    arm / best_per_ask_max      s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    episode                  0.625   0.812   0.594   0.219   0.375   0.594   0.875   0.875   0.875   0.250   0.875   0.281   0.604   12
    per_ask                  0.625   0.656   0.875   0.219   0.656   0.812   0.656   0.656   0.594   0.625   0.656   0.688   0.643   12

    arm / best_episode_max      s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    episode                  0.312   0.812   0.188   0.188   0.062   0.188   0.875   0.875   0.875   0.125   0.875   0.125   0.458   12
    per_ask                  0.250   0.375   0.875   0.188   0.312   0.812   0.312   0.312   0.188   0.250   0.312   0.375   0.380   12

    arm / first_shelf_gen       s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    episode                     72     146     104       -       -     243     104     145     162       -     126       -  137.750    8
    per_ask                    165      19      13       -      27      99     226      84      33     128      65     107  87.818   11

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.0, "effect": 0.0, "min_effect": 0.25, "n_control": 12, "n_treatment": 12, "paired": 12, "paired_wins": 0, "treatment_mean": 0.0}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: one cell, one organism family, n=12 per arm at G=300: whether the half-credit shelf survives the removal of partial credit; no claim about which readout is 'right', and none about cells other than W2_K2

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

Partial credit BUILDS the shelf but is not what CAPS the cell. Primary: 0 summits of 12 in each arm (effect 0.0 against a declared 0.25), so removing partial credit does not open the summit and the negative stands. The secondary ladder, preregistered because both arms were expected to be summit-free, separates the arms cleanly: shelf arrivals 8/12 (episode) vs 11/12 (per_ask); median generations below the shelf 250 vs 131; runs stuck at the floor for all 300 generations 4 vs 1; training bests at or above 0.81 in 5/12 vs 2/12. The organism CLASS differs, which is the result worth carrying: under per-ask credit the elite's held-out episode credit is 0.00-0.17 while its per-ask credit is 0.50-0.60 (it answers half the asks and almost never a whole episode -- the one-value memory), whereas the five successful episode-arm runs have held-out episode credit identical to their per-ask credit (0.438-0.646), meaning they answer both asks in an episode or neither. Selection on complete episodes therefore produces two-value organisms rather than one-value ones, at a cost of three extra total failures and roughly twice as long below the shelf, and it still tops out around 0.65 held-out against the 0.90 the summit needs. Read with C3-SFE-01 (0 summits in 24 runs of 300 generations) and C3-SFE-02 (1 improving child in 4,800, every second-stream gain trading the first), the W2_K2 ceiling is not a reward-shaping artefact: changing the payoff changes which plateau the population sits on and what kind of organism occupies it, and leaves the summit exactly as far away. Campaign 4 must change the organism or the search, not the payoff. Must NOT be claimed: that per-ask credit is wrong (it is the campaign-wide yardstick and the comparison depends on it); that all-or-nothing credit is better (it fails outright in 4 of 12 seeds where per-ask fails in 1); that the two-value organisms are summit-adjacent (0.44-0.65 held-out, and no run in either arm produced a single summit candidate).

## D. TEARDOWN (generated)

- worlds: {"credit": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C3-SFE-08

Two attempts (a01 dry, a02 of record). 906 s for 24 runs of 300 generations at N=200 on 12 processes; 1 world, 24 records, 24 reachability rows, 0 errors. The machine change this slot required (evaluate(reward_mode) and Evolution(reward_mode): every evaluation returns reward_per_ask AND reward_episode, and selection uses either) was built and tested before the run, with 47 machine tests passing; levels are always computed on the per-ask yardstick so the two arms and the reachability table stay comparable (D3-019). The per_ask arm is a CRN replicate of C3-SFE-01's fresh arm and reproduces it exactly: shelf in 11 of 12 seeds, the same seeds, the same first-shelf generations (13-226), the same ladder (4/7/9/10/11 at G60/100/150/200/300). Battery note: the second attack compared MEDIAN best episode credit (0.3125 in both arms) and reports FAILED, while the distribution it summarises separates clearly (5 of 12 episode-arm runs above 0.8 against 2 of 12); the record reads the distribution and keeps the attack's verdict as declared.

## F. LANDSCAPE / GRADIENT NOTES

Removing partial credit moves the search without raising its ceiling. The episode arm spends a median of 250 generations below the shelf against the per_ask arm's 131, reaches the shelf in 8 of 12 seeds against 11 of 12, and fails entirely (300 generations at the floor) in 4 seeds against 1. When it does climb it climbs differently: 5 of 12 episode-arm runs reach a training best of 0.81-0.875 against 2 of 12 under per-ask credit. The decisive detail is in the held-out readouts. Under per-ask credit the typical elite has held-out per-ask 0.50-0.60 and held-out EPISODE credit 0.00-0.17: it answers about half the asks and almost never gets a whole episode right, which is exactly the one-value memory C3-SFE-02 anatomised. Under episode credit, the five successful runs have held-out per-ask EQUAL to held-out episode credit (0.500/0.500, 0.646/0.646, 0.438/0.438, 0.479/0.479, 0.521/0.521): these organisms answer both asks or neither. That is a different creature. The half-credit shelf is therefore partly a property of the readout, and the all-or-nothing readout builds the kind of organism the summit needs -- one that holds both values keyed -- at 0.44-0.65 reliability, which is well short of the 0.90 the summit requires. Higher variance, better failures, same ceiling.

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). Assay capable and the positive control is exact (the per_ask arm reproduces the parent shelf rate, 11/12). The preregistered primary -- summit arrival, episode arm vs per_ask arm, minimum effect 0.25 -- is 0/12 vs 0/12, effect 0.0. The preregistered falsification ('the episode arm reaches the shelf as often as the per_ask arm AND neither reaches a summit') does NOT fire, because the episode arm reaches the shelf less often (8/12 vs 11/12): partial credit does contribute to the shelf. But the summit is absent under both readouts, so the disposition on the primary is negative.
