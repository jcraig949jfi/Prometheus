# C3-SFE-03 -- corridor ladder, powered

## A. STARTUP (preregistration; sealed sha256:3c2ada617855e9a73f3a78584a8ea7e603178911d5bad8fca76d7c431ebf6eec)

- experiment ID: C3-SFE-03
- parents: C2-SFE-06
- QUESTION: On the delay ladder W0 -> d1 -> d2 -> d4 (25 generations per rung, revisit share p=0.1), at which generation and on which rung does the elite first score >= 0.75 on every rung (delay generality), does it appear abruptly or gradually, does it survive later transitions, and do different seeds find the same corridor?
- PARENT EVIDENCE: C2-SFE-06 (n=6): delay-1 solutions were delay-invariant on arrival in 2 of 3 retained seeds (generation 30); the ladder reached W1_d4 competence 0.96-1.0 in 4/6 seeds by generation 99; p >= 0.1 removed the rung-boundary forgetting cliff. Table: W1_d4 4-bit direct search RARE (1/14 at G60).
- WHY THIS SLOT IS STILL WORTH SPENDING: Direct search rarely reaches W1_d4; if the ladder reaches it reliably and the generality's origin (rung, timing, genotype) is measurable, the route becomes an instrument for every later rare-cell question (C3-SFE-04) instead of a rediscovered accident.
- ASSAY CAPABILITY REQUIREMENT: the population reaches rung-0 competence >= 0.5 within the first rung in >= 6 of 12 seeds (else POSITIVE_CONTROL_FAILED: nothing to climb from)
- POSITIVE CONTROL: rung-0 (W0 4-bit) reached within 25 generations (table: W0 solved 11/21 by G30)
- REACHABILITY ESTIMATE:
    {"W0": {"at_budget": {"band95": [0.2834, 0.6763], "class": "REACHABLE", "class_summit": "REACHABLE", "first_shelf_gens": [0, 12, 16, 17, 17, 18, 18, 19, 19, 20], "first_solved_gens": [0, 12, 16, 17, 17, 18, 18, 19, 19, 20], "first_summit_gens": [], "freq": 0.4762, "freq_shelf": 0.4762, "freq_summit": 0.0, "k": 10, "k_shelf": 10, "k_summit": 0, "k_summit_any": 10, "k_summit_candidate": 10, "levels": {"FLOOR": 11, "SHELF": 10, "SUMMIT": 0}, "n": 21, "n_censored_runs": 21, "shelf_hist": {"0.1": 10, "0.2": 1, "1.0": 10}}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"budgets": [[200, 4, 16], [200, 16, 16], [200, 18, 16], [200, 19, 16], [200, 20, 16], [200, 21, 16], [200, 22, 16], [200, 23, 16], [200, 24, 16], [200, 30, 16], [200, 31, 16], [200, 35, 16], [200, 60, 16], [200, 100, 16]], "class": "REACHABLE", "class_summit": "REACHABLE", "freq": 0.619, "k": 13, "k_summit": 0, "k_summit_any": 13, "n": 21}}, "W1_d4": {"at_budget": {"band95": [0.0127, 0.3147], "class": "RARE", "class_summit": "RARE", "first_shelf_gens": [52], "first_solved_gens": [52], "first_summit_gens": [53], "freq": 0.0714, "freq_shelf": 0.0714, "freq_summit": 0.0714, "k": 1, "k_shelf": 1, "k_summit": 1, "k_summit_any": 1, "k_summit_candidate": 1, "levels": {"FLOOR": 13, "SHELF": 0, "SUMMIT": 1}, "n": 14, "n_censored_runs": 0, "shelf_hist": {"0.2": 9, "0.3": 4, "1.0": 1}}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"budgets": [[200, 60, 16]], "class": "RARE", "class_summit": "RARE", "freq": 0.0714, "k": 1, "k_summit": 1, "k_summit_any": 1, "n": 14}}}
- ARMS:
    - p0.1
- COMMON-RANDOM-NUMBERS POLICY: default; one arm; seeds are the replicates; episode batteries keyed on (generation, seed)
- BUDGET:
    {"E": 16, "G": 100, "N": 200, "general_min": 0.75, "p": 0.1, "probe_dense": 5, "probe_episodes": 24, "probe_sparse": 5, "rung_gens": 25, "rungs": [{"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 0, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W0", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}, {"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 1, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W1_d1", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}, {"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 2, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W1_d2", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}, {"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 4, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W1_d4", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}], "seeds": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}
- PRIMARY OBSERVABLE: general_gen (first generation with elite competence >= 0.75 on all four rungs) per seed; rung_at_general; r3_rise_gens; general_survives; held-out per rung at the end
- CLAIM CEILING: an instrument reading at n=12: the ladder reaches W1_d4 competence in k/12 seeds with a measured timescale; no mechanism is claimed
- FALSIFICATION CONDITION: general_heldout in < 4 of 12 seeds => the ladder is not a reliable corridor at this budget (the C2 4/6 was luck or budget)
- KILL CONDITION: positive control fails (rung 0 unreached in > half the seeds); or the ladder's W1_d4 arrival rate is not above direct search's (1/14)
- TYPED FAILURE CONDITIONS:
    - POSITIVE_CONTROL_FAILED
    - UNDERPOWERED
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - rung x generation matrices with dense transition probes
    - appear/collapse/recover events per rung
    - adaptation speed per transition
    - revisit cost
    - elite genome summaries
    - corridor ladder rows
- MACHINE CHANGES EXERCISED:
    - D probe_plan + transition_events
    - C corridor ladder rows
    - G step API with per-step spec/episodes
    - I
- REPLACEMENT CONDITION: if C3-SFE-01 had shown W1_d4-like cells trivially reachable by direct search the ladder would be moot; it did not (W1_d4 RARE stands)
- ANCESTRY (original | replacement): original (queue slot 3)
- decl (machine-read by archaeon.wse.states): {"n_min": 12, "positive_control": {"arm": "p0.1", "metric": "reached_r0_by_rung_end", "min": 1, "min_rows": 6}, "primary": {"control": "p0.1", "metric": "general_heldout", "min_effect": 0.0, "treatment": "p0.1"}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a02); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=POSITIVE_CONTROL_FAILED
    a02  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=POSITIVE_CONTROL_FAILED
- engine: live; worlds 1; artifacts 2; imports 0; records 12; errors 0
- timings (s): ladder_s=109.0, records_s=3.49, startup_s=0.86, teardown_s=0.25, total_s=114.4
- decisions: D3-008: generality = elite >= 0.75 on all four rungs at a probe (24 eval episodes each), confirmed at the end by 48 held-out episodes per rung; the primary is descriptive (rate and timing), not a comparison
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / general_gen           s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    p0.1                         -      35      25      48      70       -      52       -      50      27       -       -  43.857    7

    arm / final_r3              s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    p0.1                     0.042   1.000   1.000   1.000   1.000   0.042   1.000   0.000   1.000   1.000   0.208   0.083   0.615   12

    arm / final_r0              s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    p0.1                     0.167   1.000   1.000   1.000   1.000   0.083   1.000   0.083   1.000   1.000   0.083   0.125   0.628   12

    arm / r3_rise_gens          s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    p0.1                         -       0       0       0      25       -       0       -      24       0       -       -   7.000    7

    arm / general_heldout       s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    p0.1                         0       1       1       1       1       0       1       0       1       1       0       0   0.583   12

- typed states fired: ['POSITIVE_CONTROL_FAILED']
    POSITIVE_CONTROL_FAILED  {"arm": "p0.1", "metric": "reached_r0_by_rung_end", "min": 1, "rows": 12, "rows_meeting": 5, "values": [0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0]}
- disposition candidate (machine): POSITIVE_CONTROL_FAILED -- assay precondition failed; the scientific question was not posed
- claim ceiling (machine): none; preregistered ceiling: an instrument reading at n=12: the ladder reaches W1_d4 competence in k/12 seeds with a measured timescale; no mechanism is claimed

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"ladder": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C3-SFE-03

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: POSITIVE_CONTROL_FAILED (machine candidate POSITIVE_CONTROL_FAILED). 
