# C3-SFE-02 -- anatomy of the half-credit shelf

## A. STARTUP (preregistration; sealed sha256:141d4e760f10479083772efe3d51913eb0bbb662880b508e78fd984f8cc87304)

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
    {"basin_breadth": 30, "basin_samples": 40, "basin_steps": 3, "battery_episodes": 16, "children": 400, "max_orgs": 12, "recomb_tries": 200}
- PRIMARY OBSERVABLE: per organism: class fractions (useful, neutral, destructive, second_up, second_up_keep, first_down, tradeoff, deceptive, summit), basin share, valley; primary comparison shelf_org vs random_org on f_second_up_keep (a second-stream gradient that keeps the first stream)
- CLAIM CEILING: a topology map of <= 12 shelf organisms; explanations are flagged by rule, not asserted
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

- attempts: 3 (of record: a03); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=INSTRUMENT_FAILURE
    a02  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=INSTRUMENT_FAILURE
    a03  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 1; artifacts 1; imports 0; records 18; errors 0
- timings (s): anatomy_s=16.16, records_s=4.91, startup_s=0.23, teardown_s=0.18, total_s=22.2
- decisions: D3-010: explanation flags E1-E5 are rules on class fractions (E1 summit adjacent but < 1%%; E2 second-stream gains only below the parent; E3 tradeoff >= 80%% of second-stream gains; E4 complementary profiles with 0 joins; E5 second_up < 0.5%% and basin 0)
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / parent_r              s0      s1     s10     s11      s2    s200    s201    s202    s203    s204    s205      s3      s4      s5      s6      s7      s8      s9    mean    n
    random_org                   -       -       -       -       -   0.000   0.000   0.031   0.000   0.000   0.000       -       -       -       -       -       -       -   0.005    6
    shelf_org                0.531   0.531   0.438   0.531   0.438       -       -       -       -       -       -   0.531   0.531   0.531   0.562   0.531   0.531   0.562   0.521   12

    arm / f_useful              s0      s1     s10     s11      s2    s200    s201    s202    s203    s204    s205      s3      s4      s5      s6      s7      s8      s9    mean    n
    random_org                   -       -       -       -       -   0.015   0.000   0.007   0.010   0.005   0.005       -       -       -       -       -       -       -   0.007    6
    shelf_org                0.000   0.000   0.003   0.000   0.000       -       -       -       -       -       -   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12

    arm / f_second_up           s0      s1     s10     s11      s2    s200    s201    s202    s203    s204    s205      s3      s4      s5      s6      s7      s8      s9    mean    n
    random_org                   -       -       -       -       -   0.000   0.000   0.007   0.000   0.000   0.000       -       -       -       -       -       -       -   0.001    6
    shelf_org                0.000   0.000   0.003   0.020   0.000       -       -       -       -       -       -   0.005   0.098   0.010   0.000   0.000   0.022   0.005   0.014   12

    arm / f_second_up_keep      s0      s1     s10     s11      s2    s200    s201    s202    s203    s204    s205      s3      s4      s5      s6      s7      s8      s9    mean    n
    random_org                   -       -       -       -       -   0.000   0.000   0.000   0.000   0.000   0.000       -       -       -       -       -       -       -   0.000    6
    shelf_org                0.000   0.000   0.000   0.000   0.000       -       -       -       -       -       -   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12

    arm / f_tradeoff            s0      s1     s10     s11      s2    s200    s201    s202    s203    s204    s205      s3      s4      s5      s6      s7      s8      s9    mean    n
    random_org                   -       -       -       -       -   0.000   0.000   0.000   0.000   0.000   0.000       -       -       -       -       -       -       -   0.000    6
    shelf_org                0.000   0.000   0.000   0.005   0.000       -       -       -       -       -       -   0.005   0.098   0.010   0.000   0.000   0.022   0.005   0.012   12

    arm / f_deceptive           s0      s1     s10     s11      s2    s200    s201    s202    s203    s204    s205      s3      s4      s5      s6      s7      s8      s9    mean    n
    random_org                   -       -       -       -       -   0.015   0.000   0.000   0.010   0.005   0.005       -       -       -       -       -       -       -   0.006    6
    shelf_org                0.000   0.000   0.000   0.000   0.000       -       -       -       -       -       -   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12

    arm / f_summit              s0      s1     s10     s11      s2    s200    s201    s202    s203    s204    s205      s3      s4      s5      s6      s7      s8      s9    mean    n
    random_org                   -       -       -       -       -   0.000   0.000   0.000   0.000   0.000   0.000       -       -       -       -       -       -       -   0.000    6
    shelf_org                0.000   0.000   0.000   0.000   0.000       -       -       -       -       -       -   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12

    arm / basin_share           s0      s1     s10     s11      s2    s200    s201    s202    s203    s204    s205      s3      s4      s5      s6      s7      s8      s9    mean    n
    random_org                   -       -       -       -       -   0.000   0.000   0.000   0.000   0.000   0.000       -       -       -       -       -       -       -   0.000    6
    shelf_org                0.000   0.000   0.000   0.000   0.000       -       -       -       -       -       -   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.0, "effect": 0.0, "min_effect": 0.01, "n_control": 6, "n_treatment": 12, "paired": 0, "paired_wins": 0, "treatment_mean": 0.0}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: a topology map of <= 12 shelf organisms; explanations are flagged by rule, not asserted

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

Assay capable: 10 of 12 C3-SFE-01 shelf elites reproduce the shelf on the fixed battery (parent reward 0.44-0.56); 6 random generation-0 organisms are the null (0.00-0.03). The machine candidate CAPABLE_NEGATIVE (shelf vs random on second-stream gains that keep the first stream: 0.000 vs 0.000) is accepted; the topology is the result. STRATEGY: the strategy-signature probe (output per ask vs the correct value, the FIRST put value and the LAST put value) names the shelf without ambiguity: 6 of 12 shelf organisms answer every ask with the FIRST put value of the episode (correct 0.53 + first 0.47 = 1.00), 4 with the LAST put value (correct 0.53-0.56 + last 0.44-0.47), 2 mixed (0.44 correct, 0.28 first, 0.28 last). The shelf is 'remember one PUT and answer with it': correct exactly when the asked stream is the remembered one, half the time. No shelf organism keys its answer on the asked tag. NEIGHBOURHOOD (400 grammar children each): useful children 1 in 4,800 (one organism, one insertion, +1/32); neutral 0.64; destructive 0.36 (deletion, replacement and movement lead); second-stream gains 0-10% of children and EVERY one of them (58 of 58) came with a first-stream loss (second_up_keep = 0.000 for all 12); summit children 0; the 3-step best-of-30 greedy probe from 40 children per organism reached 0.90 in 0 of 480 paths (best endpoint = the parent's own reward in 11 of 12). Explanations by the preregistered rules: E5 no gradient fires in 6/12, E2 valley (second-stream gains only below the parent) in 7/12, E3 trade-off (>= 80% of second-stream gains cost the first) in 5/12, E1 summit-adjacent in 0/12, E4 complementary-but-unjoinable not applicable (no organism has a solved stream: every profile is 00 at the 0.75 criterion, because the strategy solves NEITHER stream; it solves the remembered-put case). Read together: the summit is not a small edit from the shelf; the shelf organism has no register keyed by tag, and any single change that raises the other ask's credit does so by switching WHICH put it remembers (first <-> last), which loses the credit it had. The half-credit shelf is a one-value memory, and the summit needs a two-value keyed memory that the neighbourhood does not contain. Must NOT be claimed: that the summit is unreachable in principle (a 3-step greedy probe is not an evolutionary run; C3-SFE-01 already bounded the run); that recombination cannot join complements (there are no complementary solvers to join).

## D. TEARDOWN (generated)

- worlds: {"anatomy": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C3-SFE-02

Zero engine errors; 1 world; 18 records; 22 s. The strategy-signature probe (added after C3-SFE-01, L3-004) is the instrument that turned '01/10 profile flips' into a named strategy; it belongs in telemetry for every K>=2 cell (TO_MACHINERY). The per-ask 'solved stream' classification assumed a stream was solved; with a one-value memory neither is, so E4's premise was empty -- recorded, not a defect. Two of 12 shelf elites read 0.44 on the fixed battery (below the 0.45 band): the fixed 16-episode battery's resolution (1/32) straddles the shelf boundary (KEEP_POLICY: the band is fine; the battery is the campaign standard).

## F. LANDSCAPE / GRADIENT NOTES

The W2_K2 shelf is a one-value memory (first-put in 6/12, last-put in 4/12); its neighbourhood under the grammar is 64% neutral, 36% destructive and 0.02% improving; second-stream credit is available only by trading the first (58/58); greedy basins to 0.90 are empty (0/480). Deletion, replacement and movement are the destructive operators (order 260/253/231 of 1,750 destructive children); the one improving child was an insertion. The summit (keyed two-value recall) is outside the one-step and three-greedy-step horizon of every shelf organism examined.

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). Assay capable (10/12 shelf reproduced, random null at the floor). No second-stream gradient from the shelf that keeps the first stream (0/4,800 children; 0/480 greedy paths to 0.90); every shelf organism is a first-value or last-value one-slot memory. The shelf is hard to leave because leaving it requires keying, and no single grammar step supplies keying.
