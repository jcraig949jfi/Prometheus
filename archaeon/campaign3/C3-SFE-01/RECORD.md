# C3-SFE-01 -- shelf-to-summit budget scan on W2_K2

## A. STARTUP (preregistration; sealed sha256:34a1eb7e5eca100a96e482772e2bd579c0ccefb2504202a7d626d5dcf2ed08c3)

- experiment ID: C3-SFE-01
- parents: C2-SFE-03, C2-SFE-07, SFE-10
- QUESTION: Does W2_K2 4-bit (N=200, E=16) have a reachable FULL solution (held-out >= 0.90) under the current organism/evaluator/search system within 300 generations, and on what timescale; and does starting on the half-credit shelf (preserved campaign-2 shelf organisms, dose 4 of 200) shorten the shelf-to-summit time?
- PARENT EVIDENCE: Campaign 2: 0/24 training-best >= 0.9 at G60 (L2-039); every foothold on the 0.50-0.56 shelf (L2-025); table at G60: 27 runs, 16 SHELF, 0 confirmed SUMMIT, 1 training-only candidate (0.9375 at 54, held-out 0.53).
- WHY THIS SLOT IS STILL WORTH SPENDING: Every economics and transfer question on K=2 cells measured time-to-shelf; whether a summit exists at all is the campaign's highest-value unresolved boundary and gates C3-SFE-02 and C3-SFE-08.
- ASSAY CAPABILITY REQUIREMENT: the fresh arm reaches the SHELF in >= 1 of 12 seeds (else TARGET_UNREACHABLE for the shelf, a table contradiction); a summit counts only when a 48-episode held-out probe of the candidate generation's elite reads >= 0.90
- POSITIVE CONTROL: fresh arm shelf arrival (table: 16/27 at G60); the SHELF organisms' held-out in [0.45, 0.90) checked before use
- REACHABILITY ESTIMATE:
    {"W2_K2": {"at_budget": {"band95": [0.3424, 1.0], "class": "REACHABLE", "class_summit": "UNESTABLISHED", "first_shelf_gens": [24, 49], "first_solved_gens": [35, 49], "first_summit_gens": [], "freq": 1.0, "freq_shelf": 1.0, "freq_summit": 0.0, "k": 2, "k_shelf": 2, "k_summit": 0, "k_summit_any": 0, "k_summit_candidate": 0, "levels": {"FLOOR": 0, "SHELF": 2, "SUMMIT": 0}, "n": 2, "n_censored_runs": 2, "shelf_hist": {"0.5": 2}}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"budgets": [[200, 30, 16], [200, 36, 16], [200, 40, 16], [200, 41, 16], [200, 42, 16], [200, 48, 16], [200, 55, 16], [200, 60, 16], [200, 70, 16]], "class": "REACHABLE", "class_summit": "OBSERVED_UNREACHABLE_AT_BUDGET", "freq": 0.3333, "k": 13, "k_summit": 0, "k_summit_any": 0, "n": 39}}}
- ARMS:
    - fresh
    - shelf
- COMMON-RANDOM-NUMBERS POLICY: default; identical generation 0 for both arms except the 4 substituted shelf organisms; one run per seed to G=300, ladder points read off the trace
- BUDGET:
    {"E": 16, "G": 300, "N": 200, "heldout_episodes": 48, "ladder": [60, 100, 150, 200, 300], "seeds": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "shelf_dose": 4, "shelf_min": 0.45, "stream_solved": 0.75, "summit_min": 0.9}
- PRIMARY OBSERVABLE: confirmed summit frequency per arm at G=300 (summit = 1/0 per run) and first_summit_gen; shelf residence (censored); secondary: shelf arrival, stream identity per generation and switches, regression from the shelf, candidates vs confirmations
- CLAIM CEILING: at n=12 per arm: 0 summits through G=300 is a CAPABLE NEGATIVE for summit reachability at this budget (upper band reported); k summits give a timescale, not a mechanism
- FALSIFICATION CONDITION: summit frequency (shelf arm) - (fresh arm) < 0.10 => shelf start does not shorten the transition; 0 confirmed summits in 24 runs => the summit is OBSERVED_UNREACHABLE at G=300 (band reported)
- KILL CONDITION: if the fresh arm reaches the shelf in < 1/12 seeds the table is wrong and the slot stops; if summits are confirmed in >= 6 of 12 fresh runs by G=100 the 'summit is hard' premise dies and C3-SFE-02 becomes an anatomy of the transition instead of the shelf
- TYPED FAILURE CONDITIONS:
    - TARGET_UNREACHABLE (fresh shelf 0/12)
    - UNDERPOWERED
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
    - IMMATURE_ARTIFACT is not applicable: the shelf organisms are deliberately partial (recorded, not gating)
- EXPECTED MACHINE TELEMETRY:
    - per-generation elite per-ask profile and population max per ask
    - summit candidates with held-out confirmations
    - shelf residence (censored)
    - regression from shelf
    - ancestry operator histograms (final elite; first summit elite)
    - ladder rows in the reachability table via the monotone lookup
    - corridor rows (shelf organisms -> W2_K2)
- MACHINE CHANGES EXERCISED:
    - A levels + candidates + confirmation
    - B monotone lookup at ladder points
    - C corridor rows
    - F common_fill dose
    - per_ask credit
- REPLACEMENT CONDITION: none: this slot is the campaign's first priority; its outcome replaces C3-SFE-08 if no summit regime exists
- ANCESTRY (original | replacement): original (queue slot 1)
- decl (machine-read by archaeon.wse.states): {"n_min": 12, "primary": {"control": "fresh", "metric": "summit", "min_effect": 0.1, "treatment": "shelf"}, "target": {"baseline_arm": "fresh", "reach_metric": "shelf_reached", "reach_min": 1, "reachability_class": "REACHABLE"}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a04); resumed_from: None; replayed steps on the attempt of record: 0
    a03  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=CAPABLE_NEGATIVE
    a04  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 24; errors 0
- timings (s): fetch_s=0.99, records_s=6.68, scan_s=1226.13, startup_s=0.09, teardown_s=0.2, total_s=1235.3
- decisions: D3-007: a summit is counted only when confirmed by a 48-episode held-out probe at the candidate generation (D3-006 applied); ladder points are read off one G=300 trace per seed
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / competence_heldout      s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    fresh                    0.542   0.531   0.604   0.073   0.510   0.500   0.542   0.542   0.531   0.573   0.500   0.552   0.500   12
    shelf                    0.542   0.542   0.531   0.510   0.510   0.542   0.542   0.542   0.531   0.573   0.500   0.552   0.535   12

    arm / first_shelf_gen       s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    fresh                      165      19      13       -      27      99     226      84      33     128      65     107  87.818   11
    shelf                        0       0       0       0       0       0       0       0       0       0       0       0   0.000   12

    arm / first_summit_gen      s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    fresh                        -       -       -       -       -       -       -       -       -       -       -       -       -    0
    shelf                        -       -       -       -       -       -       -       -       -       -       -       -       -    0

    arm / summit_candidates      s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    fresh                        0       0       0       0       0       0       0       0       0       0       0       0   0.000   12
    shelf                        0       0       0       0       0       0       0       0       0       0       0       0   0.000   12

    arm / shelf_residence       s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    fresh                      135     281     287       -     273     201      74     216     267     172     235     193  212.182   11
    shelf                      300     300     300     300     300     300     300     300     300     300     300     300  300.000   12

- footholds:
    arm                    footholds  first_solved_gen per row
    fresh                  11/12      165,27,99,226,84,95,128,65,114,19,13,-
    shelf                  12/12      0,0,0,0,0,0,0,0,0,0,0,0

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.0, "effect": 0.0, "min_effect": 0.1, "n_control": 12, "n_treatment": 12, "paired": 12, "paired_wins": 0, "treatment_mean": 0.0}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: at n=12 per arm: 0 summits through G=300 is a CAPABLE NEGATIVE for summit reachability at this budget (upper band reported); k summits give a timescale, not a mechanism

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

MAJOR RESULT, RECORDED WITH ITS CENSORING: zero confirmed summits and zero training-only candidates in 24 runs of 300 generations on W2_K2 4-bit (N=200, E=16). Assay capable: the fresh arm reached the SHELF in 11 of 12 seeds (first shelf at generations 13-226, median ~90; at the ladder points 4/12 by G60, 7/12 by G100, 9/12 by G150, 10/12 by G200, 11/12 by G300), so the population climbs onto the shelf routinely and then stays: shelf residence 74-287 generations, every one censored at G=300. Best training reward over 300 generations was 0.59-0.69 in 10 of 11 shelf runs and 0.81 / 0.875 in two (seeds 3 and 11; 26 and 28 of 32 asks in one battery), never 0.90; end-of-run held-out 0.50-0.60. The SHELF arm (four preserved campaign-2 shelf organisms substituted into generation 0) sat on the shelf from generation 0 in 12/12 seeds and produced no summit either (best 0.625-0.81; the imports took the population over, import share 1.0 in every seed, D3-005's cap deliberately off). The machine candidate CAPABLE_NEGATIVE for the primary (shelf-start vs fresh on summit frequency: 0/12 vs 0/12) is accepted, and the reachability table now reads W2_K2 4-bit N200 summit OBSERVED_UNREACHABLE_AT_BUDGET at every ladder point with 14 baseline runs at G300 (95% band < 0.22; < 0.13 including the shelf arm's 12 treated runs). Timescale: none measurable; the shelf-to-summit transition did not occur within 300 generations under this organism/evaluator/search system. Exploratory shape (the anatomy is C3-SFE-02's job): (i) end-of-run held-out per ask position is ~0.5 / ~0.5 for almost every elite (e.g. 0.56/0.52, 0.42/0.60, 0.50/0.50), not 1.0 / 0.0 -- the shelf elite does not solve ONE stream; it answers each ask correctly about half the time, which is what an organism that outputs the LAST PUT value does when the asked stream is the last-written one half the time; (ii) the training-battery 'stream profile' of the elite flips between 01 and 10 across generations (0-6 flips per run) and briefly shows 11 in 4 runs (seed 11: 18 generations, best 0.875 at 294, held-out 0.60), so the 'switching' is mostly battery luck on a last-value strategy, with two runs showing real two-stream progress that never reached 0.9; (iii) the shelf is not absorbing: after first reaching it, elites spent 42, 61 and 105 generations back below 0.45 in three seeds (regression), i.e. the training best fluctuates across the shelf boundary. Must NOT be claimed: that a summit is impossible (band < 0.22 at G300; N and E were fixed); that the shelf is 'one stream solved' (the per-ask data say last-value); anything about mechanism before C3-SFE-02.

## D. TEARDOWN (generated)

- worlds: {"scan": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C3-SFE-01

Zero engine errors; 1 world; the campaign-2 shelf archives fetched under campaign 2's principal (8 organisms kept, held-out 0.5625, per-ask 0.65/0.48); 24 records; 24 reachability rows with per-ask held-out; 12 corridor rows (shelf organisms -> W2_K2, dose 4: 12 SHELF, 0 SUMMIT). Bench notes: (1) the run took 1226 s for 24 x 300 generations on 12 processes (about 4x the campaign-2 rate per generation: the per-ask credit, the 300-generation traces and 12 concurrent processes on a 12-core box); a 24-run G300 scan is the largest single job of three campaigns and still under half an hour; (2) 'stream profile' from a 16-episode training battery is not a lineage property when the strategy is last-value; the anatomy needs a per-episode probe against the last PUT value (added to C3-SFE-02 before it runs); (3) the ladder points were read off one trace per seed through the monotone lookup, as designed: no rerun per budget.

## F. LANDSCAPE / GRADIENT NOTES

W2_K2 4-bit N200 E16: FLOOR -> SHELF in 11/12 seeds by G300 (median ~90 generations; the campaign-2 'plateau with a late exit' is the same shape stretched: 4/12 by G60); SHELF -> SUMMIT never in 24 x 300 generations (0/14 baseline at G300). The shelf's best training reward saturates at 0.59-0.69 (19-22 of 32 asks) with rare excursions to 0.81-0.875; end-of-run held-out 0.50-0.60 with per-ask ~0.5/0.5. Two runs reached a both-streams profile on the training battery (0.875 = 28/32 at generation 294 in seed 11) without a held-out above 0.61: whatever partial two-stream competence appears, it is not the keyed recall the summit needs. The reachability table's summit level for W2_K2 is now OBSERVED_UNREACHABLE_AT_BUDGET through G300.

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). Assay capable (fresh 11/12 on the shelf); 0/24 confirmed summits and 0 candidates through G300, both arms; shelf residence censored at 300 in every shelf run. The summit of W2_K2 is OBSERVED_UNREACHABLE at every ladder point up to G300 under the current system (95% upper band 0.22 at n=14). C3-SFE-08's premise (a meaningful full-solve regime) is dead: replaced (D3-013).
