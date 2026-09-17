# C3-SFE-08 -- does partial credit build the shelf?

## A. STARTUP (preregistration; sealed sha256:cfb1da2bb2eea587908d775cccf51765b9de561e63c3b7d4adcce40bdb2d998c)

- experiment ID: C3-SFE-08
- parents: C3-SFE-01, C3-SFE-02
- QUESTION: On W2_K2 4-bit (N=60, E=16, G=12), does selection on ALL-OR-NOTHING episode credit (an episode counts only if every ask is correct) change where the search ends up, compared with the per-ask partial credit every campaign has used: fewer runs on the half-credit shelf, and any run reaching the summit?
- PARENT EVIDENCE: C3-SFE-01 (n=24, G300): 0 confirmed summits, 0 candidates; fresh runs reach the shelf in 11/12 (median ~90 generations) and stay, residence censored at 300 everywhere; end-of-run held-out per ask ~0.5/0.5. C3-SFE-02 (n=12 shelf elites, 400 grammar children each): the shelf is a one-value memory (first-put 6/12, last-put 4/12), 1 improving child in 4,800, every second-stream gain (58/58) costs the first, 0/480 greedy paths to 0.90. The shelf pays ~0.5 under per-ask credit while solving neither stream: that half credit is a readout property.
- WHY THIS SLOT IS STILL WORTH SPENDING: the original slot 8 is dead (it required a full-solve regime C3-SFE-01 showed does not exist). Direction A asks what makes the shelf. If the shelf is an artefact of partial credit, the reward readout is a design variable for every K>=2 cell in campaign 4; if the summit is unreached under both readouts, the ceiling is structural and no reward shaping will move it -- and campaign 4 must change the organism or the search, not the payoff.
- ASSAY CAPABILITY REQUIREMENT: the per_ask arm reproduces C3-SFE-01's shelf rate (>= 8 of 2 seeds reach the shelf) -- else the assay is not the one that produced the parent evidence
- POSITIVE CONTROL: per_ask arm on W2_K2 4-bit (table: shelf in 11/12 at G300, C3-SFE-01)
- REACHABILITY ESTIMATE:
    {"W2_K2": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "class_summit": "UNESTABLISHED", "first_shelf_gens": [], "first_solved_gens": [], "first_summit_gens": [], "freq": null, "freq_shelf": null, "freq_summit": null, "k": 0, "k_shelf": 0, "k_summit": 0, "k_summit_any": null, "k_summit_candidate": null, "levels": {"FLOOR": 0, "SHELF": 0, "SUMMIT": 0}, "n": 0, "n_censored_runs": null, "shelf_hist": {}}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"budgets": [[200, 30, 16], [200, 36, 16], [200, 40, 16], [200, 41, 16], [200, 42, 16], [200, 48, 16], [200, 55, 16], [200, 60, 16], [200, 70, 16], [200, 300, 16]], "class": "REACHABLE", "class_summit": "OBSERVED_UNREACHABLE_AT_BUDGET", "freq": 0.4706, "k": 24, "k_summit": 0, "k_summit_any": 0, "n": 51}}}
- ARMS:
    - per_ask
    - episode
- COMMON-RANDOM-NUMBERS POLICY: default; both arms share generation 0 per seed and the same per-generation batteries (episodes are keyed on (generation, cell seed)); only the fitness readout differs; both arms are SCORED at the end on the same held-out battery with both readouts
- BUDGET:
    {"E": 16, "G": 12, "N": 60, "arms": ["per_ask", "episode"], "heldout_n": 48, "runs": 4, "seeds": [1, 2], "target": {"D": 1, "K": 2, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 0, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W2_K2", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}}
- PRIMARY OBSERVABLE: summit arrival (held-out per-ask >= 0.90) per seed, and, since both arms are expected to be summit-free, the preregistered secondary ladder: shelf arrival rate, generations on the shelf, best per-ask and best episode credit reached
- CLAIM CEILING: one cell, one organism family, n=2 per arm at G=12: whether the half-credit shelf survives the removal of partial credit; no claim about which readout is 'right', and none about cells other than W2_K2
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
- decl (machine-read by archaeon.wse.states): {"battery": [{"name": "episode_arm_shelf_rate_below_per_ask", "passed": null}, {"name": "episode_arm_reaches_higher_episode_credit", "passed": null}, {"name": "per_ask_arm_reproduces_parent_shelf_rate", "passed": null}], "n_min": 2, "positive_control": {"arm": "per_ask", "metric": "shelf_reached", "min": 1, "min_rows": 8}, "primary": {"control": "per_ask", "metric": "summit", "min_effect": 0.25, "treatment": "episode"}}

## B. EXECUTION (generated from receipts)

- attempts: 1 (of record: a00); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=POSITIVE_CONTROL_FAILED
- engine: dry-run; worlds 0; artifacts 0; imports 0; records 0; errors 0
- timings (s): records_s=0.0, scan_s=2.51, total_s=3.0
- decisions: D3-019: both arms are read out on the SAME held-out battery with both readouts; levels (FLOOR/SHELF/SUMMIT) are always computed on per-ask credit so the arms are comparable
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / competence_heldout      s1      s2    mean    n
    episode                  0.083   0.052   0.068    2
    per_ask                  0.042   0.010   0.026    2

    arm / best_per_ask_max      s1      s2    mean    n
    episode                  0.156   0.156   0.156    2
    per_ask                  0.125   0.188   0.156    2

    arm / best_episode_max      s1      s2    mean    n
    episode                  0.062   0.062   0.062    2
    per_ask                  0.000   0.000   0.000    2

    arm / first_shelf_gen       s1      s2    mean    n
    episode                      -       -       -    0
    per_ask                      -       -       -    0

    arm / first_summit_gen      s1      s2    mean    n
    episode                      -       -       -    0
    per_ask                      -       -       -    0

- typed states fired: ['POSITIVE_CONTROL_FAILED']
    POSITIVE_CONTROL_FAILED  {"arm": "per_ask", "metric": "shelf_reached", "min": 1, "rows": 2, "rows_meeting": 0, "values": [0, 0]}
- disposition candidate (machine): POSITIVE_CONTROL_FAILED -- assay precondition failed; the scientific question was not posed
- claim ceiling (machine): none; preregistered ceiling: one cell, one organism family, n=2 per arm at G=12: whether the half-credit shelf survives the removal of partial credit; no claim about which readout is 'right', and none about cells other than W2_K2

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: none (dry run)
- all TERMINATED: n/a

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C3-SFE-08

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: POSITIVE_CONTROL_FAILED (machine candidate POSITIVE_CONTROL_FAILED). 
