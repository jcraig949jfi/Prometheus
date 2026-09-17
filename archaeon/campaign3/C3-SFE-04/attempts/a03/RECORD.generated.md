# C3-SFE-04 -- corridor map

## A. STARTUP (preregistration; sealed sha256:5fd458f38fd0bde2e5c294f03b3843c5a763843f6548a158bf39fc74799bd573)

- experiment ID: C3-SFE-04
- parents: C3-SFE-03, C3-SFE-01, C2-SFE-05
- QUESTION: Which mature solutions are stepping stones into which difficult cells? For sources ['W0_solver', 'delay_general'] and targets ['W1_d8', 'W1_d16', 'W2_K2', 'W3_K2', 'W7_K2']: what does a mature solution already contain (direct held-out competence), and where it does not solve the target, does initializing a search with dose 4 of it change time-to-foothold, time-to-shelf, time-to-full-solve or the final level against a matched fresh baseline and a permuted-control import?
- PARENT EVIDENCE: C3-SFE-03: 11 delay-general elites (held-out 1.0 on delays 0/1/2/4) and the corridor W0 -> d1 -> free; its comparator gap (direct W1_d4 measured at G60 only) is L3-013, closed here by the baseline arm at G100. C3-SFE-01: W2_K2 summit OBSERVED_UNREACHABLE through G300; its shelf material is NOT mature (shelf, not solved) and is therefore excluded as a source. Campaign-2 corridor rows: W0 -> W3_K2 direct 0.54 (n=10), W2_K2 -> W1_d4 direct 0.96 (n=6). Table: W1_d8/W1_d16 UNESTABLISHED, W2_K2 REACHABLE/summit OBSERVED_UNREACHABLE, W3_K2 REACHABLE (N=100 only), W7_K2 OBSERVED_UNREACHABLE (0/10 at G60). Direct-probe table measured before sealing: {'W0_solver->W0': {'n': 4, 'best': 1.0, 'median': 1.0, 'solved': 4}, 'W0_solver->W1_d16': {'n': 4, 'best': 0.0, 'median': 0.0, 'solved': 0}, 'W0_solver->W1_d8': {'n': 4, 'best': 0.0, 'median': 0.0, 'solved': 0}, 'W0_solver->W2_K2': {'n': 4, 'best': 0.2708, 'median': 0.2708, 'solved': 0}, 'W0_solver->W3_K2': {'n': 4, 'best': 0.5, 'median': 0.5, 'solved': 0}, 'W0_solver->W7_K2': {'n': 4, 'best': 0.0938, 'median': 0.0833, 'solved': 0}, 'delay_general->W0': {'n': 11, 'best': 1.0, 'median': 1.0, 'solved': 11}, 'delay_general->W1_d16': {'n': 11, 'best': 1.0, 'median': 1.0, 'solved': 11}, 'delay_general->W1_d8': {'n': 11, 'best': 1.0, 'median': 1.0, 'solved': 11}, 'delay_general->W2_K2': {'n': 11, 'best': 0.5417, 'median': 0.5417, 'solved': 0}, 'delay_general->W3_K2': {'n': 11, 'best': 0.5833, 'median': 0.5833, 'solved': 0}, 'delay_general->W7_K2': {'n': 11, 'best': 0.1458, 'median': 0.1354, 'solved': 0}}
- WHY THIS SLOT IS STILL WORTH SPENDING: the reachability table says which cells are hard; nothing says which hard cells are hard FROM WHERE. A sparse traversable graph turns every later rare-cell question into a route choice instead of a fresh search, and the same run supplies the matched-budget direct comparator C3-SFE-03 could not claim without.
- ASSAY CAPABILITY REQUIREMENT: at least 4 mature W0 solvers harvested (held-out >= 0.9 on W0) and >= 8 delay-general sources; the baseline arm must reach a foothold on at least one target (else the targets are all out of reach at this budget and only direct reuse is readable)
- POSITIVE CONTROL: the delay_general family solves W1_d8/W1_d16 directly, or the baseline arm reaches a foothold on W2_K2 (table: REACHABLE 24/51)
- REACHABILITY ESTIMATE:
    {"W1_d16": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "class_summit": "UNESTABLISHED", "first_shelf_gens": [], "first_solved_gens": [], "first_summit_gens": [], "freq": null, "freq_shelf": null, "freq_summit": null, "k": 0, "k_shelf": 0, "k_summit": 0, "k_summit_any": null, "k_summit_candidate": null, "levels": {"FLOOR": 0, "SHELF": 0, "SUMMIT": 0}, "n": 0, "n_censored_runs": null, "shelf_hist": {}}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"budgets": [], "class": "UNESTABLISHED", "class_summit": "UNESTABLISHED", "freq": null, "k": 0, "k_summit": 0, "k_summit_any": null, "n": 0}}, "W1_d8": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "class_summit": "UNESTABLISHED", "first_shelf_gens": [], "first_solved_gens": [], "first_summit_gens": [], "freq": null, "freq_shelf": null, "freq_summit": null, "k": 0, "k_shelf": 0, "k_summit": 0, "k_summit_any": null, "k_summit_candidate": null, "levels": {"FLOOR": 0, "SHELF": 0, "SUMMIT": 0}, "n": 0, "n_censored_runs": null, "shelf_hist": {}}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"budgets": [], "class": "UNESTABLISHED", "class_summit": "UNESTABLISHED", "freq": null, "k": 0, "k_summit": 0, "k_summit_any": null, "n": 0}}, "W2_K2": {"at_budget": {"band95": [0.3876, 0.8366], "class": "REACHABLE", "class_summit": "OBSERVED_UNREACHABLE_AT_BUDGET", "first_shelf_gens": [13, 19, 24, 27, 33, 49, 65, 84, 99], "first_solved_gens": [13, 19, 27, 35, 49, 65, 84, 95, 99], "first_summit_gens": [], "freq": 0.6429, "freq_shelf": 0.6429, "freq_summit": 0.0, "k": 9, "k_shelf": 9, "k_summit": 0, "k_summit_any": 0, "k_summit_candidate": 0, "levels": {"FLOOR": 5, "SHELF": 9, "SUMMIT": 0}, "n": 14, "n_censored_runs": 2, "shelf_hist": {"0.2": 3, "0.4": 2, "0.5": 7, "0.6": 1, "0.8": 1}}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"budgets": [[200, 30, 16], [200, 36, 16], [200, 40, 16], [200, 41, 16], [200, 42, 16], [200, 48, 16], [200, 55, 16], [200, 60, 16], [200, 70, 16], [200, 300, 16]], "class": "REACHABLE", "class_summit": "OBSERVED_UNREACHABLE_AT_BUDGET", "freq": 0.4706, "k": 24, "k_summit": 0, "k_summit_any": 0, "n": 51}}, "W3_K2": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "class_summit": "UNESTABLISHED", "first_shelf_gens": [], "first_solved_gens": [], "first_summit_gens": [], "freq": null, "freq_shelf": null, "freq_summit": null, "k": 0, "k_shelf": 0, "k_summit": 0, "k_summit_any": null, "k_summit_candidate": null, "levels": {"FLOOR": 0, "SHELF": 0, "SUMMIT": 0}, "n": 0, "n_censored_runs": null, "shelf_hist": {}}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"budgets": [[100, 40, 16]], "class": "REACHABLE", "class_summit": "OBSERVED_UNREACHABLE_AT_BUDGET", "freq": 0.3077, "k": 4, "k_summit": 0, "k_summit_any": 0, "n": 13}}, "W7_K2": {"at_budget": {"band95": [0.0, 1.0], "class": "UNESTABLISHED", "class_summit": "UNESTABLISHED", "first_shelf_gens": [], "first_solved_gens": [], "first_summit_gens": [], "freq": null, "freq_shelf": null, "freq_summit": null, "k": 0, "k_shelf": 0, "k_summit": 0, "k_summit_any": null, "k_summit_candidate": null, "levels": {"FLOOR": 0, "SHELF": 0, "SUMMIT": 0}, "n": 0, "n_censored_runs": null, "shelf_hist": {}}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"budgets": [[200, 60, 16]], "class": "OBSERVED_UNREACHABLE_AT_BUDGET", "class_summit": "OBSERVED_UNREACHABLE_AT_BUDGET", "freq": 0.0, "k": 0, "k_summit": 0, "k_summit_any": 0, "n": 10}}}
- ARMS:
    - baseline
    - init_mature
    - init_control
- COMMON-RANDOM-NUMBERS POLICY: default; per (target, seed) the three arms share generation 0 (common fill: the import REPLACES the first 4 organisms of the same base population) and every per-generation battery; the permuted control uses the SAME manifests as init_mature. Targets a mature family already solves directly get the baseline arm ONLY, to fill their direct-search class in the reachability table (W1_d8/W1_d16 are UNESTABLISHED)
- BUDGET:
    {"E": 16, "G": 100, "N": 200, "direct_probes": 90, "dose": 4, "harvest_G": 60, "heldout_n": 48, "informative_targets": ["W2_K2", "W3_K2", "W7_K2"], "runs": 66, "seeds": [1, 2, 3, 4, 5, 6], "table_fill_baselines": ["W1_d8", "W1_d16"], "targets": [{"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 8, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W1_d8", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}, {"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 16, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W1_d16", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}, {"D": 1, "K": 2, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 0, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W2_K2", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}, {"D": 1, "K": 2, "Kd": 0, "ask_kind": "ASK", "ask_mode": "one", "ask_timing": "end", "delay": 0, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W3_K2", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}, {"D": 1, "K": 2, "Kd": 0, "ask_kind": "ASK2", "ask_mode": "all", "ask_timing": "end", "delay": 0, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W7_K2", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}]}
- PRIMARY OBSERVABLE: per informative edge: first_foothold_gen, first_shelf_gen, first_summit_gen and final held-out competence, init_mature vs baseline (paired by seed); the machine primary is the pooled foothold rate init_mature vs baseline
- CLAIM CEILING: a sparse map at n=6 per edge and G=100: which edges show a measurable initialization advantage over a matched baseline, with the permuted control as the capability test; no claim that the advantage transfers structure rather than search time
- FALSIFICATION CONDITION: init_mature does not beat baseline on foothold rate by >= 0.25 pooled over informative edges => no measurable corridor at this budget beyond direct competence
- KILL CONDITION: fewer than 4 mature W0 solvers or fewer than 8 delay-general sources (no mature source set); or every target is solved directly (no search question left)
- TYPED FAILURE CONDITIONS:
    - IMMATURE_ARTIFACT
    - TARGET_UNREACHABLE
    - POSITIVE_CONTROL_FAILED
    - UNDERPOWERED
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - direct-reuse matrix (family x target)
    - levels and transition generations per run
    - import share
    - corridor rows (direct and init)
    - reachability rows for every target incl. the UNESTABLISHED delay cells
- MACHINE CHANGES EXERCISED:
    - C corridor table (direct + init rows)
    - A levels
    - B reachability rows for UNESTABLISHED cells
    - F common_fill dose
- REPLACEMENT CONDITION: if C3-SFE-03 had found no reliable corridor the map would have no mature multi-cell source; it did (11/12 delay-general)
- ANCESTRY (original | replacement): replacement (queue slot 4; the retired campaign 1/2 transfer lane). This is NOT 'does transferred residue help': every source is mature and the question is which subsequent searches its capability makes reachable
- decl (machine-read by archaeon.wse.states): {"battery": [{"name": "permuted_control_gives_no_advantage", "passed": null}, {"name": "advantage_survives_excluding_directly_solved_edges", "passed": null}, {"name": "advantage_is_not_only_generation_0", "passed": null}], "n_min": 18, "primary": {"control": "baseline", "metric": "foothold", "min_effect": 0.25, "treatment": "init_mature"}}

## B. EXECUTION (generated from receipts)

- attempts: 3 (of record: a03); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=WEAK_POSITIVE
    a02  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=WEAK_POSITIVE
    a03  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=WEAK_POSITIVE
- engine: live; worlds 1; artifacts 3; imports 0; records 66; errors 0
- timings (s): direct_s=0.32, harvest_s=17.62, phase1_s=17.95, records_s=19.33, search_s=880.51, startup_s=0.08, teardown_s=0.29, total_s=919.2
- decisions: D3-016: mature sources only -- W0 solvers harvested here (held-out >= 0.9) and C3-SFE-03 delay-general elites; the W2_K2 shelf material is excluded (not solved), D3-017: edge selection is preregistered and cheap-first: a target is informative unless a mature family already solves it directly (>= 0.90 held-out)
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / competence_heldout      s1      s2      s3      s4      s5      s6    mean    n
    baseline                 0.062   1.000   0.062   0.062   0.062   0.062   0.219    6
    init_control             0.344   0.490   0.031   0.167   0.104   0.042   0.196    6
    init_mature              0.365   0.490   0.542   0.417   0.438   0.229   0.413    6

    arm / first_foothold_gen      s1      s2      s3      s4      s5      s6    mean    n
    baseline                     -      52       -       -       -       -  52.000    1
    init_control                95      38       -       -       -       -  66.500    2
    init_mature                 24      11      20      25       7       -  17.400    5

    arm / first_shelf_gen       s1      s2      s3      s4      s5      s6    mean    n
    baseline                     -      52       -       -       -       -  52.000    1
    init_control                95      36       -       -       -       -  65.500    2
    init_mature                 24      11      20      25       7      15  17.000    6

    arm / first_summit_gen      s1      s2      s3      s4      s5      s6    mean    n
    baseline                     -      55       -       -       -       -  55.000    1
    init_control                 -       -       -       -       -       -       -    0
    init_mature                  -       -       -       -       -       -       -    0

    arm / summit                s1      s2      s3      s4      s5      s6    mean    n
    baseline                     0       1       0       0       0       0   0.167    6
    init_control                 0       0       0       0       0       0   0.000    6
    init_mature                  0       0       0       0       0       0   0.000    6

- typed states fired: none
- disposition candidate (machine): WEAK_POSITIVE -- effect >= min_effect but n < 10 or a declared falsification attack failed or was not run
    evidence: {"control_mean": 0.4333, "effect": 0.5111, "min_effect": 0.25, "n_control": 30, "n_treatment": 18, "paired": 6, "paired_wins": 4, "treatment_mean": 0.9444}
    battery: {"attacked": 3, "declared": 3, "survived": 2}
- claim ceiling (machine): weak; not for propagation; preregistered ceiling: a sparse map at n=6 per edge and G=100: which edges show a measurable initialization advantage over a matched baseline, with the permuted control as the capability test; no claim that the advantage transfers structure rather than search time

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"map": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C3-SFE-04

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: WEAK_POSITIVE (machine candidate WEAK_POSITIVE). 
