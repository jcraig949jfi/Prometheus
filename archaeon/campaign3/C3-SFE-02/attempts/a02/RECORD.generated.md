# C3-SFE-02 -- anatomy of the half-credit shelf

## A. STARTUP (preregistration; sealed sha256:f409f32f57a14f2269104578f54e1dd5a8e3f692d7a449302a951972c4b7c7bb)

- experiment ID: C3-SFE-02
- parents: C3-SFE-01
- QUESTION: What makes the W2_K2 half-credit shelf hard to leave: is the summit one or two ordinary mutations away but rarely sampled, does it require crossing a fitness valley, does solving stream 2 destroy stream 1, do complementary lineages exist that recombination cannot join, or is there no gradient?
- PARENT EVIDENCE: C3-SFE-01 (this campaign): 23 shelf elites and 0 confirmed summit elites at G300; campaign-2 L2-025/L2-039.
- WHY THIS SLOT IS STILL WORTH SPENDING: C3-SFE-01 gives the timescale; only the neighbourhood says why. Five explanations with preregistered rules, one cheap enumeration.
- ASSAY CAPABILITY REQUIREMENT: >= 3 shelf organisms with a solved stream (per-ask >= 0.75 on the battery) and >= 3 random controls; the battery must reproduce the shelf (parent_r in [0.45, 0.90) for shelf organisms) else INSTRUMENT_FAILURE
- POSITIVE CONTROL: random generation-0 organisms as the neighbourhood control (their fractions are the null for every class)
- REACHABILITY ESTIMATE:
    {"W2_K2": {"at_budget": {"band95": [0.6853, 0.9873], "class": "COMMON", "class_summit": "OBSERVED_UNREACHABLE_AT_BUDGET", "first_shelf_gens": [13, 19, 24, 27, 33, 49, 65, 84, 99, 107, 128, 165, 226], "first_solved_gens": [13, 19, 27, 35, 49, 65, 84, 95, 99, 114, 128, 165, 226], "first_summit_gens": [], "freq": 0.9286, "freq_shelf": 0.9286, "freq_summit": 0.0, "k": 13, "k_shelf": 13, "k_summit": 0, "k_summit_any": 0, "k_summit_candidate": 0, "levels": {"FLOOR": 1, "SHELF": 13, "SUMMIT": 0}, "n": 14, "n_censored_runs": 2, "shelf_hist": {"0.2": 1, "0.5": 3, "0.6": 8, "0.8": 2}}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"budgets": [[200, 30, 16], [200, 36, 16], [200, 40, 16], [200, 41, 16], [200, 42, 16], [200, 48, 16], [200, 55, 16], [200, 60, 16], [200, 70, 16], [200, 300, 16]], "class": "REACHABLE", "class_summit": "OBSERVED_UNREACHABLE_AT_BUDGET", "freq": 0.4706, "k": 24, "k_summit": 0, "k_summit_any": 0, "n": 51}}}
- ARMS:
    - shelf_org
    - summit_org
    - random_org
- COMMON-RANDOM-NUMBERS POLICY: one fixed 16-episode battery for every organism and child; child seeds keyed on the organism index
- BUDGET:
    {"basin_breadth": 30, "basin_samples": 3, "basin_steps": 3, "battery_episodes": 16, "children": 20, "max_orgs": 3, "recomb_tries": 10}
- PRIMARY OBSERVABLE: per organism: class fractions (useful, neutral, destructive, second_up, second_up_keep, first_down, tradeoff, deceptive, summit), basin share, valley; primary comparison shelf_org vs random_org on f_second_up_keep (a second-stream gradient that keeps the first stream)
- CLAIM CEILING: a topology map of <= 3 shelf organisms; explanations are flagged by rule, not asserted
- FALSIFICATION CONDITION: f_second_up_keep(shelf) - f_second_up_keep(random) < 0.01 => no usable second-stream gradient from the shelf (E5 or E2/E3 by their flags)
- KILL CONDITION: if the battery cannot reproduce the shelf for the shelf organisms the enumeration is meaningless (INSTRUMENT_FAILURE)
- TYPED FAILURE CONDITIONS:
    - INSTRUMENT_FAILURE (battery/shelf mismatch)
    - UNDERPOWERED (< 3 shelf organisms)
- EXPECTED MACHINE TELEMETRY:
    - class fractions and operator histograms per class
    - basin probe end rewards
    - recombination joins
    - edit distances shelf<->summit
- MACHINE CHANGES EXERCISED:
    - per_ask credit
    - I
- REPLACEMENT CONDITION: if C3-SFE-01 had produced no shelf organisms at all (impossible per the table) this slot would be replaced by a finer C3-SFE-01 scan
- ANCESTRY (original | replacement): original (queue slot 2)
- decl (machine-read by archaeon.wse.states): {"n_min": 3, "primary": {"control": "random_org", "metric": "f_second_up_keep", "min_effect": 0.01, "treatment": "shelf_org"}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a00); resumed_from: 1; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=INSTRUMENT_FAILURE
    a02  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=INSTRUMENT_FAILURE
- engine: dry-run; worlds 0; artifacts 0; imports 0; records 0; errors 0
- timings (s): anatomy_s=1.34, records_s=0.0, total_s=1.5
- decisions: D3-010: explanation flags E1-E5 are rules on class fractions (E1 summit adjacent but < 1%%; E2 second-stream gains only below the parent; E3 tradeoff >= 80%% of second-stream gains; E4 complementary profiles with 0 joins; E5 second_up < 0.5%% and basin 0)
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / parent_r              s0      s1      s2    s200    s201    s202    mean    n
    random_org                   -       -       -   0.000   0.000   0.031   0.010    3
    shelf_org                0.531   0.531   0.438       -       -       -   0.500    3

    arm / f_useful              s0      s1      s2    s200    s201    s202    mean    n
    random_org                   -       -       -   0.050   0.000   0.000   0.017    3
    shelf_org                0.000   0.000   0.000       -       -       -   0.000    3

    arm / f_second_up           s0      s1      s2    s200    s201    s202    mean    n
    random_org                   -       -       -   0.000   0.000   0.000   0.000    3
    shelf_org                0.000   0.000   0.000       -       -       -   0.000    3

    arm / f_second_up_keep      s0      s1      s2    s200    s201    s202    mean    n
    random_org                   -       -       -   0.000   0.000   0.000   0.000    3
    shelf_org                0.000   0.000   0.000       -       -       -   0.000    3

    arm / f_tradeoff            s0      s1      s2    s200    s201    s202    mean    n
    random_org                   -       -       -   0.000   0.000   0.000   0.000    3
    shelf_org                0.000   0.000   0.000       -       -       -   0.000    3

    arm / f_deceptive           s0      s1      s2    s200    s201    s202    mean    n
    random_org                   -       -       -   0.050   0.000   0.000   0.017    3
    shelf_org                0.000   0.000   0.000       -       -       -   0.000    3

    arm / f_summit              s0      s1      s2    s200    s201    s202    mean    n
    random_org                   -       -       -   0.000   0.000   0.000   0.000    3
    shelf_org                0.000   0.000   0.000       -       -       -   0.000    3

    arm / basin_share           s0      s1      s2    s200    s201    s202    mean    n
    random_org                   -       -       -   0.000   0.000   0.000   0.000    3
    shelf_org                0.000   0.000   0.000       -       -       -   0.000    3

- typed states fired: ['INSTRUMENT_FAILURE']
    INSTRUMENT_FAILURE  {"first": {"error": "shelf organisms not in band on the battery", "step": "battery"}, "n_errors": 1}
- disposition candidate (machine): INSTRUMENT_FAILURE -- execution state fired
- claim ceiling (machine): none; preregistered ceiling: a topology map of <= 3 shelf organisms; explanations are flagged by rule, not asserted

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: none (dry run)
- all TERMINATED: n/a

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C3-SFE-02

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: INSTRUMENT_FAILURE (machine candidate INSTRUMENT_FAILURE). 
