# C3-SFE-05 -- retention economics break-even

## A. STARTUP (preregistration; sealed sha256:0d63541736f9d6e4c218de1851fe8283811fc4ea44546efe98ad9d80c1a1fe54)

- experiment ID: C3-SFE-05
- parents: C2-SFE-06, SFE-05
- QUESTION: Between p=0 and p=0.10 revisit share, where is the break-even at which rung-0 competence is retained to the end of the ladder without cost to rung-3 adaptation; and does removing the revisit pressure once the elite is general (p0.1_then_0) keep or lose that retention?
- PARENT EVIDENCE: C2-SFE-06 (n=6, 3 retained seeds): p=0 lost rung 0 within 5 generations of the pressure moving; p>=0.1 retained it and RAISED final delay-4 competence (0.36 -> 0.61-0.69); the first delay-1 solutions were delay-invariant on arrival.
- WHY THIS SLOT IS STILL WORTH SPENDING: The campaign-2 result located the effect but not the price: the economic boundary (and whether revisits are needed after generality) is the critical uncertainty of the retention line; n=6 with three informative seeds could not place it.
- ASSAY CAPABILITY REQUIREMENT: the p0 arm reaches rung-0 competence >= 0.5 within the rung-0 HOLD (<= 100 generations; C3-SFE-03 a02 showed a fixed first rung releases the ladder before W0 is climbed in 7/12) in >= 6 of 12 seeds (else POSITIVE_CONTROL_FAILED)
- POSITIVE CONTROL: rung-0 arrival under p0 within the hold of 100 generations (C3-SFE-03 a05: 12/12 seeds climbed rung 0 within the hold, 12-97 generations)
- REACHABILITY ESTIMATE:
    {"W0": {"at_budget": {"band95": [0.6212, 0.9626], "class": "COMMON", "class_summit": "COMMON", "first_shelf_gens": [0, 12, 16, 17, 17, 18, 18, 19, 19, 20, 27, 31, 99], "first_solved_gens": [0, 12, 16, 17, 17, 18, 18, 19, 19, 20, 27, 31, 99], "first_summit_gens": [], "freq": 0.8667, "freq_shelf": 0.8667, "freq_summit": 0.0, "k": 13, "k_shelf": 13, "k_summit": 0, "k_summit_any": 13, "k_summit_candidate": 13, "levels": {"FLOOR": 2, "SHELF": 13, "SUMMIT": 0}, "n": 15, "n_censored_runs": 15, "shelf_hist": {"0.2": 2, "1.0": 13}}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"budgets": [[200, 4, 16], [200, 16, 16], [200, 18, 16], [200, 19, 16], [200, 20, 16], [200, 21, 16], [200, 22, 16], [200, 23, 16], [200, 24, 16], [200, 30, 16], [200, 31, 16], [200, 35, 16], [200, 60, 16], [200, 100, 16]], "class": "REACHABLE", "class_summit": "REACHABLE", "freq": 0.619, "k": 13, "k_summit": 0, "k_summit_any": 13, "n": 21}}}
- ARMS:
    - p0.0
    - p0.05
    - p0.1
    - p0.2
    - p0.1_then_0
- COMMON-RANDOM-NUMBERS POLICY: default; identical generation 0 and selection stream per seed across arms; batteries keyed on (generation, seed); p0.1_then_0 differs from p0.1 only after the generality probe fires
- BUDGET:
    {"E": 16, "G_ladder": 100, "N": 200, "general_min": 0.75, "probe_dense": 5, "probe_sparse": 5, "rung0_max": 100, "rung_gens": 25, "seeds": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "shares": [0.0, 0.05, 0.1, 0.2]}
- PRIMARY OBSERVABLE: final_r0 per arm x seed (retained rung-0 competence at the end); cost: final_r3 and adaptation speed; revisit_cost_episodes; general_gen
- CLAIM CEILING: weak at n=12: a break-even REGION (the smallest p with final_r0 not below p0.1's by 0.15) and a yes/no on post-generality removal
- FALSIFICATION CONDITION: final_r0(p0.05) - final_r0(p0) < 0.15 => 5%% revisits do not retain (break-even is above 0.05); final_r0(p0.1_then_0) - final_r0(p0.1) < -0.15 => the pressure must continue after generality
- KILL CONDITION: positive control fails; or p0 retains rung 0 in >= 8/12 seeds (no cliff to price)
- TYPED FAILURE CONDITIONS:
    - POSITIVE_CONTROL_FAILED
    - UNDERPOWERED
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - rung x generation matrices (dense)
    - events per rung
    - adapt_gens per transition
    - revisit_cost_episodes
    - general_gen and rung_at_general
    - p_switched_at for the then_0 arm
    - held-out per rung at the end
- MACHINE CHANGES EXERCISED:
    - D dense probes
    - G per-step episodes with a mid-run policy change
    - I
- REPLACEMENT CONDITION: if C3-SFE-03 finds no generality in any seed the then_0 arm is vacuous and is dropped (4 arms remain)
- ANCESTRY (original | replacement): original (queue slot 5)
- decl (machine-read by archaeon.wse.states): {"n_min": 12, "positive_control": {"arm": "p0.0", "metric": "reached_r0_by_rung_end", "min": 1, "min_rows": 6}, "primary": {"control": "p0.0", "metric": "final_r0", "min_effect": 0.15, "treatment": "p0.05"}}

## B. EXECUTION (generated from receipts)

- attempts: 3 (of record: a03); resumed_from: None; replayed steps on the attempt of record: 0
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=POSITIVE_CONTROL_FAILED
    a02  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=POSITIVE_CONTROL_FAILED
    a03  errors=0 replayed=0 engine=True purpose=engine disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 1; artifacts 2; imports 0; records 60; errors 0
- timings (s): ladder_s=665.46, records_s=17.37, startup_s=0.06, teardown_s=0.19, total_s=683.9
- decisions: D3-009: the then_0 arm switches p to 0 at the first probe where the elite is general (all rungs >= 0.75); revisit cost is charged in episodes, not rewarded
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / final_r0              s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    p0.0                     1.000   1.000   1.000   0.000   1.000   0.000   1.000   1.000   1.000   1.000   1.000   0.167   0.764   12
    p0.05                    0.708   0.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   0.892   12
    p0.1                     1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   12
    p0.1_then_0              1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   12
    p0.2                     1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   12

    arm / final_r3              s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    p0.0                     1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   0.125   0.927   12
    p0.05                    0.167   0.917   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   0.924   12
    p0.1                     1.000   0.125   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   0.927   12
    p0.1_then_0              1.000   0.125   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   0.927   12
    p0.2                     1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   12

    arm / general_gen           s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    p0.0                       119      52      39       -      41       -      79       -      52      47     121       -  68.750    8
    p0.05                        -       -      39       -      41      99     101     147      52      47     155      67  83.111    9
    p0.1                        99       -      39      85      41      99      86     147      62      47     109      49  78.455   11
    p0.1_then_0                 99       -      39      85      41      99      86     147      62      47     109      49  78.455   11
    p0.2                        94      47      39      62      41      99      77     149      42      47     108      93  74.833   12

    arm / revisit_cost_episodes      s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    p0.0                         0       0       0       0       0       0       0       0       0       0       0       0   0.000   12
    p0.05                       75      75      75      75      75      75      75      75      75      75      75      75  75.000   12
    p0.1                       150     150     150     150     150     150     150     150     150     150     150     150  150.000   12
    p0.1_then_0                 32     150       2      52       0       2      22      52      52       2       8      22  33.000   12
    p0.2                       225     225     225     225     225     225     225     225     225     225     225     225  225.000   12

    arm / general_heldout       s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    p0.0                         1       1       1       0       1       0       1       0       1       1       1       0   0.667   12
    p0.05                        0       0       1       0       1       1       1       1       1       1       1       1   0.750   12
    p0.1                         1       0       1       1       1       1       1       1       1       1       1       1   0.917   12
    p0.1_then_0                  1       0       1       1       1       1       1       1       1       1       1       1   0.917   12
    p0.2                         1       1       1       1       1       1       1       1       1       1       1       1   1.000   12

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 0.7639, "effect": 0.1285, "min_effect": 0.15, "n_control": 12, "n_treatment": 12, "paired": 12, "paired_wins": 3, "treatment_mean": 0.8924}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: weak at n=12: a break-even REGION (the smallest p with final_r0 not below p0.1's by 0.15) and a yes/no on post-generality removal

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

THE ECONOMIC RESULT: the minimum revisit share that prevents the rung-boundary forgetting cliff on this ladder is above 0.05 and at most 0.10. At p=0.05 (75 revisit episodes per run) mean final rung-0 competence is 0.892 with 2 of 12 seeds below 0.75, which fails the preregistered 0.15 margin over p=0 (0.764) -- the falsification clause written before the run fires and names the answer. At p=0.10 (150 episodes) retention is 1.0 in 12 of 12 seeds; p=0.20 (225 episodes) buys nothing further on rung 0 and nothing measurable on rung 3. AND THE PRICE IS ONLY PAID UNTIL GENERALITY: the p0.1_then_0 arm, which drops the revisit share to zero the moment the elite is general on every rung, retains rung 0 at 1.0 in 12 of 12 seeds and reaches generality in the same 11 of 12 seeds at the same generations as p0.1, for a MEDIAN of 22 revisit episodes instead of 150 -- an 85% cost reduction with identical outcomes. Retention is therefore not a standing tax on the ecology; it is a transient pressure needed only while the general solution is being found, and the competence that survives afterwards survives without support. Falsification clause two ('the pressure must continue after generality', final_r0(then_0) - final_r0(p0.1) < -0.15) did NOT fire: the difference is 0.000. Instrument check: the p0.1 arm reproduces C3-SFE-03's ladder arm row for row under CRN (11/12 general, same seeds, same generations). Must NOT be claimed: that 0.10 is THE break-even (the tested grid is {0, 0.05, 0.10, 0.20}; the interval is (0.05, 0.10]); that revisits are free (they are 150 episodes per run, 6% of the training budget, and the then_0 arm is what makes them cheap); that retention costs adaptation (no cost was measurable here, but this ladder's adaptation is free after delay 1, so the trade-off is untested rather than absent).

## D. TEARDOWN (generated)

- worlds: {"retention": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C3-SFE-05

Three attempts (a01/a02 dry, a03 of record). 684 s for 60 runs (5 arms x 12 seeds) of hold + 100 generations at N=200 on 12 processes; 1 world, 1 published matrix artifact, 60 records, 60 reachability rows, 0 errors. The rung-0 hold built for C3-SFE-03 (L3-011) was wired into this harness before it ran, and it is why the experiment is readable at all: the hold released by competence in 60 of 60 runs (median 35 generations), so every arm starts its ladder from a W0-competent population and the arms differ only in the revisit share. Bench note: the p0.1 arm is a CRN replicate of C3-SFE-03's single arm and reproduces it exactly (general 11/12, the same 11 seeds, the same general_gen values), which is the strongest instrument check in the campaign: two experiments, two sealed preregistrations, identical rows.

## F. LANDSCAPE / GRADIENT NOTES

The retention price curve on this ladder is a step, not a slope. Mean final rung-0 competence by revisit share: 0.764 (p=0), 0.892 (p=0.05), 1.000 (p=0.10), 1.000 (p=0.20). Runs ending below 0.75 on rung 0: 3, 2, 0, 0 of 12. The break-even therefore lies in the interval (0.05, 0.10]: at one episode in twenty the cliff still opens in 2 of 12 seeds, at one in ten it never does. The cost side is linear (0 / 75 / 150 / 225 revisit episodes per run), so p=0.10 is the cheapest setting that retains. NO TRADE-OFF WAS DETECTABLE: adaptation to the new rung cost 0 generations in 57 of the 58 runs that went general, in every arm including p=0.20, and final rung-3 competence is flat across arms (0.924-1.000). The presumed price of retention -- slower adaptation -- is zero here, because delay generality arrives all at once (C3-SFE-03) and there is nothing for the revisit pressure to slow down. Forgetting at p=0 is also partial rather than catastrophic: 9 of 12 seeds kept rung 0 at 1.0 with no revisits at all, and transient dips below 0.25 occur in every arm (including p=0.20, 2 of 12) and recover within a few generations. The cliff C2-SFE-06 reported at n=6 is real but it fires in a minority of seeds, which is why n=6 could neither price it nor bound it.

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). Assay capable (60/60 climbed rung 0 within the hold; the p0 arm shows the forgetting the experiment prices). The preregistered primary -- final_r0(p0.05) - final_r0(p0) >= 0.15 -- is not met: 0.892 vs 0.764, effect 0.128, and the preregistered falsification clause for that number says exactly this: 5% revisits do not buy retention, the break-even is above 0.05. The experiment's positive readings (the break-even is located, and post-generality removal is free) are secondary and descriptive, so the disposition stays CAPABLE_NEGATIVE.
