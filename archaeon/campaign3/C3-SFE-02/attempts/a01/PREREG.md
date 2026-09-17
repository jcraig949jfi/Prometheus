## A. STARTUP (preregistration; sealed sha256:41bd26f829145558c5b7eaf90f5b744900cdb15509f57ebe158f3513bfa60772)

- experiment ID: C3-SFE-02
- parents: C3-SFE-01
- QUESTION: What makes the W2_K2 half-credit shelf hard to leave: is the summit one or two ordinary mutations away but rarely sampled, does it require crossing a fitness valley, does solving stream 2 destroy stream 1, do complementary lineages exist that recombination cannot join, or is there no gradient?
- PARENT EVIDENCE: C3-SFE-01 (this campaign): 3 shelf elites and 0 confirmed summit elites at G300; campaign-2 L2-025/L2-039.
- WHY THIS SLOT IS STILL WORTH SPENDING: C3-SFE-01 gives the timescale; only the neighbourhood says why. Five explanations with preregistered rules, one cheap enumeration.
- ASSAY CAPABILITY REQUIREMENT: >= 3 shelf organisms with a solved stream (per-ask >= 0.75 on the battery) and >= 3 random controls; the battery must reproduce the shelf (parent_r in [0.45, 0.90) for shelf organisms) else INSTRUMENT_FAILURE
- POSITIVE CONTROL: random generation-0 organisms as the neighbourhood control (their fractions are the null for every class)
- REACHABILITY ESTIMATE:
    {"W2_K2": {"at_budget": {"band95": [0.3424, 1.0], "class": "REACHABLE", "class_summit": "UNESTABLISHED", "first_shelf_gens": [24, 49], "first_solved_gens": [35, 49], "first_summit_gens": [], "freq": 1.0, "freq_shelf": 1.0, "freq_summit": 0.0, "k": 2, "k_shelf": 2, "k_summit": 0, "k_summit_any": 0, "k_summit_candidate": 0, "levels": {"FLOOR": 0, "SHELF": 2, "SUMMIT": 0}, "n": 2, "n_censored_runs": 2, "shelf_hist": {"0.5": 2}}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"budgets": [[200, 30, 16], [200, 36, 16], [200, 40, 16], [200, 41, 16], [200, 42, 16], [200, 48, 16], [200, 55, 16], [200, 60, 16], [200, 70, 16]], "class": "REACHABLE", "class_summit": "OBSERVED_UNREACHABLE_AT_BUDGET", "freq": 0.3333, "k": 13, "k_summit": 0, "k_summit_any": 0, "n": 39}}}
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
