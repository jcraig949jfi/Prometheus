# C3-SFE-07 -- basin geometry as a causal target

## A. STARTUP (preregistration; sealed sha256:edb916865cac4e5ec678dc8bdbbc8802e6584515f66bb4750e0a29b37076dd17)

- experiment ID: C3-SFE-07
- parents: C3-SFE-06, C2-SFE-08
- QUESTION: Holding the task (W0 4-bit), the operator masses, the evaluation budget (N=200, G=60, E=16) and generation 0 fixed, does rewriting the OPCODE-FIELD neighbourhood to the ordering with the higher measured basin share (perm_7: basin 0.0338) make the search reach W0 competence sooner or more often than the ordering with the lower basin share (identity: basin 0.0256), matched on gross accessible variation within 15%?
- PARENT EVIDENCE: C3-SFE-06 measured basin share, deceptive share and accessible variation exhaustively over 25^4 opcode genotypes of two minimal W0 solver skeletons, under 12 orderings, with two climbers. Its pooled rank correlation was CONFOUNDED by table difficulty (INCONCLUSIVE, L3-029); within the one informative table ['skelA'] the first-improvement climber gives rho = -0.527 and the population climber +0.187, and the other table's target fell at the chance level (L3-030) so it is excluded here. The pair selected by the preregistered rule from the informative table(s): {'high': {'encoding': 'perm_7', 'basin_share': 0.0338, 'accessible_variation': 1.445, 'deceptive_share': 0.3183}, 'low': {'encoding': 'identity', 'basin_share': 0.0256, 'accessible_variation': 1.4399, 'deceptive_share': 0.3201}, 'gap': 0.0082}. Random-ordering scale pair: {'a': {'encoding': 'perm_3', 'basin_share': 0.0305, 'accessible_variation': 1.4371, 'deceptive_share': 0.3134}, 'b': {'encoding': 'perm_6', 'basin_share': 0.0305, 'accessible_variation': 1.4321, 'deceptive_share': 0.308}} (gap 0.0). C2-SFE-08: basin share -0.59 / deceptive +0.57 with the CA evaluator and one climber -- correlational, in-family.
- WHY THIS SLOT IS STILL WORTH SPENDING: every geometry number campaigns 2 and 3 produced is correlational: measured on the same space whose search it predicts. If a geometry knob moves a real evolutionary run, geometry becomes a design variable; if it does not, the measurements are descriptive and the line dies here.
- ASSAY CAPABILITY REQUIREMENT: the grammar arm reaches W0 competence (held-out >= 0.9) in >= 6 of 12 seeds (the table: W0 REACHABLE, 13/21 pooled) -- else there is no search to speed up and the result is POSITIVE_CONTROL_FAILED
- POSITIVE CONTROL: arm 'grammar' (the unmodified neighbourhood) on W0 4-bit at N=200, G=60
- REACHABILITY ESTIMATE:
    {"W0": {"at_budget": {"band95": [0.4375, 0.8372], "class": "REACHABLE", "class_summit": "REACHABLE", "first_shelf_gens": [0, 12, 16, 17, 17, 18, 18, 19, 19, 20, 27, 31], "first_solved_gens": [0, 12, 16, 17, 17, 18, 18, 19, 19, 20, 27, 31], "first_summit_gens": [], "freq": 0.6667, "freq_shelf": 0.6667, "freq_summit": 0.0, "k": 12, "k_shelf": 12, "k_summit": 0, "k_summit_any": 12, "k_summit_candidate": 12, "levels": {"FLOOR": 6, "SHELF": 12, "SUMMIT": 0}, "n": 18, "n_censored_runs": 18, "shelf_hist": {"0.2": 6, "1.0": 12}}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"budgets": [[200, 4, 16], [200, 16, 16], [200, 18, 16], [200, 19, 16], [200, 20, 16], [200, 21, 16], [200, 22, 16], [200, 23, 16], [200, 24, 16], [200, 30, 16], [200, 31, 16], [200, 35, 16], [200, 60, 16], [200, 100, 16]], "class": "REACHABLE", "class_summit": "REACHABLE", "freq": 0.619, "k": 13, "k_summit": 0, "k_summit_any": 13, "n": 21}}}
- ARMS:
    - grammar
    - high_basin
    - low_basin
    - rand_a
    - rand_b
- COMMON-RANDOM-NUMBERS POLICY: default; every arm shares generation 0 per seed (same campaign seed and cell seed, no substitution) and the same per-generation batteries; only the opcode-field neighbourhood differs; the same 12 seeds run in every arm (paired)
- BUDGET:
    {"E": 16, "G": 60, "N": 200, "acc_tolerance": 0.15, "arms": ["grammar", "high_basin", "low_basin", "rand_a", "rand_b"], "moves": [1, -1, 2, -2], "seeds": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "selected": {"high": {"accessible_variation": 1.445, "basin_share": 0.0338, "deceptive_share": 0.3183, "encoding": "perm_7"}, "low": {"accessible_variation": 1.4399, "basin_share": 0.0256, "deceptive_share": 0.3201, "encoding": "identity"}, "rand_a": {"accessible_variation": 1.4371, "basin_share": 0.0305, "deceptive_share": 0.3134, "encoding": "perm_3"}, "rand_b": {"accessible_variation": 1.4321, "basin_share": 0.0305, "deceptive_share": 0.308, "encoding": "perm_6"}}}
- PRIMARY OBSERVABLE: confirmed (held-out-confirmed W0 competence within G) and confirmed_gen per seed; high_basin vs low_basin, paired by seed
- CLAIM CEILING: one task, one genotype-space slice (the opcode field), n=12 paired seeds, and a SMALL geometric difference (the informative table's encodings span a 32% relative range in basin share): whether a preregistered geometric difference moves realized search efficiency in the predicted direction; no claim that basin share is THE explanatory variable, and a null here does not separate 'geometry is inert' from 'this gap is too small'
- FALSIFICATION CONDITION: high_basin does not beat low_basin by >= 0.25 in confirmed rate (or by >= 5 generations in median confirmed_gen) => basin share does not act causally on this search at this budget
- KILL CONDITION: the two random orderings (matched basin share) differ by as much as high vs low => the contrast is ordering noise, not geometry; the line is killed early as the directive allows
- TYPED FAILURE CONDITIONS:
    - POSITIVE_CONTROL_FAILED
    - INTERVENTION_NOT_APPLIED (opfield_rewrites = 0)
    - UNDERPOWERED
    - READOUT_CANNOT_EXPRESS
- EXPECTED MACHINE TELEMETRY:
    - opcode-field rewrite counts per run
    - realized operator masses per arm (the match check)
    - levels + first solved / confirmed generations
    - best-by-generation traces
    - reachability rows (treated)
- MACHINE CHANGES EXERCISED:
    - descend_fn geometry intervention
    - A levels
    - B reachability rows
- REPLACEMENT CONDITION: if C3-SFE-06 had found no encoding pair matched on accessible variation with a basin gap, this slot would have had no intervention to make and would be replaced by a retention or import-ecology question
- ANCESTRY (original | replacement): replacement (queue slot 7; a dead representation-unlock lane)
- decl (machine-read by archaeon.wse.states): {"battery": [{"name": "random_pair_gap_smaller_than_treatment_gap", "passed": null}, {"name": "operator_masses_matched_across_arms", "passed": null}, {"name": "intervention_applied_every_arm", "passed": null}], "n_min": 12, "positive_control": {"arm": "grammar", "metric": "confirmed", "min": 1, "min_rows": 6}, "primary": {"control": "low_basin", "metric": "confirmed", "min_effect": 0.25, "treatment": "high_basin"}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a02); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=POSITIVE_CONTROL_FAILED
    a02  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 60; errors 0
- timings (s): records_s=17.7, search_s=102.15, startup_s=0.09, teardown_s=0.2, total_s=121.1
- decisions: D3-022: only C3-SFE-06 tables whose threshold is ABOVE CHANCE are used to choose the encodings (L3-030); skelB's target fell at 1/16 and its rows carry no search information, D3-018: the encodings are chosen by the preregistered rule (largest basin gap among pairs matched on accessible variation within 15%), from geometry measured by C3-SFE-06 BEFORE this run; no ordering was chosen on a known search time
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / confirmed             s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    grammar                      0       1       1       1       1       0       1       0       1       1       0       1   0.667   12
    high_basin                   1       1       1       0       1       1       0       0       1       1       0       1   0.667   12
    low_basin                    1       1       0       1       0       1       1       1       1       1       0       1   0.750   12
    rand_a                       1       1       0       1       0       1       1       1       0       0       1       0   0.583   12
    rand_b                       0       1       1       1       0       0       1       0       1       1       1       1   0.667   12

    arm / confirmed_gen         s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    grammar                      -      13      13      34      38       -      51       -      11      21       -      13  24.250    8
    high_basin                  46       9       8       -       9      57       -       -       5      24       -      49  25.875    8
    low_basin                   54      12       -       8       -      38      49      25       8      43       -      10  27.444    9
    rand_a                      42       6       -      10       -      15      18      38       -       -      14       -  20.429    7
    rand_b                       -       9      34       8       -       -      11       -       8      36      13      24  17.875    8

    arm / solved_gen            s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    grammar                     58      11      13      34      30       -      50       -      11      21       -      13  26.778    9
    high_basin                  46       9       8       -       9      57       -       -       5      24       -      49  25.875    8
    low_basin                   53      11       -       8       -      38      49      25       8      43       -      10  27.222    9
    rand_a                      42       6       -      10       -      15      18      38       -       -      14       -  20.429    7
    rand_b                       -       8      34       8       -       -      11       -       8      33      13      24  17.375    8

    arm / best_g20              s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    grammar                  0.312   1.000   1.000   0.250   0.312   0.312   0.188   0.188   1.000   0.250   0.188   1.000   0.500   12
    high_basin               0.125   1.000   1.000   0.375   1.000   0.312   0.188   0.188   1.000   0.188   0.250   0.250   0.490   12
    low_basin                0.188   1.000   0.250   1.000   0.312   0.312   0.188   0.312   1.000   0.250   0.250   1.000   0.505   12
    rand_a                   0.125   1.000   0.250   1.000   0.312   1.000   1.000   0.188   0.250   0.188   1.000   0.250   0.547   12
    rand_b                   0.312   1.000   0.250   1.000   0.312   0.312   1.000   0.188   1.000   0.250   1.000   0.312   0.578   12

    arm / competence_heldout      s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    grammar                  0.896   1.000   1.000   1.000   1.000   0.042   1.000   0.021   1.000   1.000   0.104   1.000   0.755   12
    high_basin               1.000   1.000   1.000   0.062   1.000   1.000   0.021   0.062   1.000   1.000   0.104   1.000   0.688   12
    low_basin                1.000   1.000   0.062   1.000   0.042   1.000   1.000   1.000   1.000   1.000   0.062   1.000   0.764   12
    rand_a                   1.000   1.000   0.104   1.000   0.042   1.000   1.000   1.000   0.062   0.104   1.000   0.104   0.618   12
    rand_b                   0.062   1.000   1.000   1.000   0.042   0.042   1.000   0.062   1.000   1.000   1.000   1.000   0.684   12

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.75, "effect": -0.0833, "min_effect": 0.25, "n_control": 12, "n_treatment": 12, "paired": 12, "paired_wins": 2, "treatment_mean": 0.6667}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: one task, one genotype-space slice (the opcode field), n=12 paired seeds, and a SMALL geometric difference (the informative table's encodings span a 32% relative range in basin share): whether a preregistered geometric difference moves realized search efficiency in the predicted direction; no claim that basin share is THE explanatory variable, and a null here does not separate 'geometry is inert' from 'this gap is too small'

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

Basin share does not act causally on this search. Holding the task, the operator masses (max deviation 0.008 across arms), the evaluation budget and generation 0 fixed, and changing only which opcode a mutation can reach, the encoding with the higher measured basin share confirmed W0 competence in 8 of 12 seeds against the lower encoding's 9 of 12: effect -0.083 against a declared minimum of +0.25, in the wrong direction. The preregistered kill condition fires on its own terms: two RANDOM orderings matched on basin share (perm_3 and perm_6, gap 0.0000) differ by 7/12 vs 8/12, the same 0.083 as the treatment contrast, so whatever separates the treatment arms is ordering noise and not geometry. Median time to confirmation orders the arms against the prediction as well (high 24, low 25, but both random orderings at 13-15 and the untouched grammar at 21). Taken with C3-SFE-06, the basin-share line now reads: the statistic is measurable, it correlates with search efficiency within one exhaustive toy table under one climber (rho -0.527), the pooled correlation that looked like an out-of-family replication was a two-strata artefact, and when the same statistic is used to PREDICT the effect of an intervention on a real evolutionary run it predicts nothing. The directive allowed this line to fail completely, and it has. Must NOT be claimed: that neighbourhood geometry in general cannot matter (one task, one genotype slice, one budget, and the largest matched basin gap the space offered was 0.0082 in absolute terms); that the toy-space correlation was fabricated (it is there, within one table and one climber); that the intervention failed to apply (567-573 rewrites per run, masses matched to 0.008). What this DOES establish, at n=12 paired with a matched-noise control: a geometry statistic that correlates with search in an exhaustive enumeration is not thereby a design variable for the evolutionary system built on the same cell.

## D. TEARDOWN (generated)

- worlds: {"geometry": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C3-SFE-07

Two attempts (a01 dry, a02 of record). 121 s for 60 runs (5 arms x 12 seeds) of 60 generations at N=200; 1 world, 1 published selection artifact, 60 records, 60 reachability rows, 0 errors. The intervention was applied and verified: 567-573 opcode-field rewrites per run in each of the four rewritten arms, 0 in the grammar arm, and the realized operator masses differ across arms by at most 0.008 (the grammar's own masses are untouched; only which opcode a mutation lands on changes). Instrument defect found in this run's own battery code, recorded and not hidden: the first attack ('the random pair's gap is smaller than the treatment pair's gap') was coded with a 0.1 floor, so it returns PASSED whenever both gaps are small. Its VALUE is what matters and it says the opposite of a pass: treatment gap -0.083, random gap +0.083. The record is read from the values, not from that flag.

## F. LANDSCAPE / GRADIENT NOTES

Rewriting the opcode-field neighbourhood to a measured ordering changes nothing detectable about a real evolutionary run on W0 at this budget. Confirmed held-out competence by arm: grammar 8/12, high basin 8/12, low basin 9/12, random A 7/12, random B 8/12. Median generation of confirmation: grammar 21, high 24, low 25, random A 15, random B 13 -- the two arms selected to differ in basin share are the two SLOWEST, and the two random orderings chosen to be identical in basin share are the two fastest. Every arm ends at held-out median 1.0 and every arm has the same median best-by-generation-20 (0.3125). The five arms are indistinguishable on every observable recorded. The geometric difference available to manipulate was small in absolute terms (basin share 0.0256 to 0.0338 on the one informative table, a 32% relative range against a 0.35% range in accessible variation), so this is a test of the biggest matched gap the measured space offered, not of an arbitrarily large one.

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). Assay capable: the grammar arm (unmodified neighbourhood) confirmed W0 competence in 8 of 12 seeds, above the declared 6, and the intervention fired in every treated run. The preregistered primary -- the higher-basin encoding confirms more often than the lower-basin one, minimum effect 0.25 -- comes out at 8/12 vs 9/12, an effect of -0.083 in the WRONG direction. The preregistered KILL CONDITION also fires: the two random orderings matched on basin share differ by 7/12 vs 8/12, exactly the same magnitude as the treatment contrast. The contrast is ordering noise.
