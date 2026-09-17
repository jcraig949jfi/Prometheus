# C3-SFE-10 -- import takeover / dose ecology

## A. STARTUP (preregistration; sealed sha256:b0e6bf1656baae95787929c6e0ce041780038743258711322235ec59b418c096)

- experiment ID: C3-SFE-10
- parents: C2-SFE-01, C3-SFE-01, C3-SFE-03
- QUESTION: When mature W0-general solvers or matched permuted controls are injected at generation 0 into a fresh W1_d4 population (N=200) at doses [0, 1, 4, 32], without the offspring cap and with caps [0.25, 0.05], when does the import take over (share >= 0.9), do resident lineages survive, and is the takeover explained by capability (mature only) or by injection mechanics (control too)? Reconnaissance made the CAP the control parameter: mature dose 1 takes over anyway.
- PARENT EVIDENCE: C2-SFE-01: transported material took the population over while the treatment hurt (-0.16). C3-SFE-01 shelf arm: dose 4 of shelf organisms reached import share 1.0 in 12/12 seeds by G300 with the cap off. C3-SFE-03: 11 W0-general elites with held-out 1.0 on every rung (the mature material). Mature direct competence on W1_d4 (held-out 48 episodes): [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]; permuted controls: [0.125, 0.0, 0.125, 0.125, 0.0, 0.1042, 0.0, 0.0, 0.0, 0.0, 0.0]. Reconnaissance: mature doses 1/4/32 of 200, no cap, 2 seeds, 20 generations: takeover (share >= 0.9) at generations 4-5 / 3 / 2, import share 1.0 and pure-resident 0.0 at the end in 6/6, held-out 1.0 in 6/6, distinct-genome share min 0.88-0.95; permuted controls' direct W1_d4 competence 0.0-0.125
- WHY THIS SLOT IS STILL WORTH SPENDING: every later experiment that injects organisms needs the dose at which 'transfer' becomes population replacement, and whether the replacement is driven by the material's competence or by the injection mechanics; neither number exists.
- ASSAY CAPABILITY REQUIREMENT: the mature material must be mature (source solved, held-out >= 0.9 on W0) and directly competent on the target (>= 0.5 held-out) else IMMATURE_ARTIFACT / INTERVENTION_NOT_APPLIED; controls must score < 0.25
- POSITIVE CONTROL: the takeover-prone dose (32, mature, no cap) reaches import share >= 0.9 within 60 generations in >= 8 of 12 seeds
- REACHABILITY ESTIMATE:
    {"W0": {"at_budget": {"band95": [0.4375, 0.8372], "class": "REACHABLE", "class_summit": "REACHABLE", "first_shelf_gens": [0, 12, 16, 17, 17, 18, 18, 19, 19, 20, 27, 31], "first_solved_gens": [0, 12, 16, 17, 17, 18, 18, 19, 19, 20, 27, 31], "first_summit_gens": [], "freq": 0.6667, "freq_shelf": 0.6667, "freq_summit": 0.0, "k": 12, "k_shelf": 12, "k_summit": 0, "k_summit_any": 12, "k_summit_candidate": 12, "levels": {"FLOOR": 6, "SHELF": 12, "SUMMIT": 0}, "n": 18, "n_censored_runs": 18, "shelf_hist": {"0.2": 6, "1.0": 12}}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"budgets": [[200, 4, 16], [200, 16, 16], [200, 18, 16], [200, 19, 16], [200, 20, 16], [200, 21, 16], [200, 22, 16], [200, 23, 16], [200, 24, 16], [200, 30, 16], [200, 31, 16], [200, 35, 16], [200, 60, 16], [200, 100, 16]], "class": "REACHABLE", "class_summit": "REACHABLE", "freq": 0.619, "k": 13, "k_summit": 0, "k_summit_any": 13, "n": 21}}, "W1_d4": {"at_budget": {"band95": [0.0127, 0.3147], "class": "RARE", "class_summit": "RARE", "first_shelf_gens": [52], "first_solved_gens": [52], "first_summit_gens": [53], "freq": 0.0714, "freq_shelf": 0.0714, "freq_summit": 0.0714, "k": 1, "k_shelf": 1, "k_summit": 1, "k_summit_any": 1, "k_summit_candidate": 1, "levels": {"FLOOR": 13, "SHELF": 0, "SUMMIT": 1}, "n": 14, "n_censored_runs": 0, "shelf_hist": {"0.2": 9, "0.3": 4, "1.0": 1}}, "foundry": "instr1-16:6528b9dc", "pooled_any_budget": {"budgets": [[200, 60, 16]], "class": "RARE", "class_summit": "RARE", "freq": 0.0714, "k": 1, "k_summit": 1, "k_summit_any": 1, "n": 14}}}
- ARMS:
    - none_d0_nocap
    - mature_d1_nocap
    - mature_d1_cap0.25
    - mature_d1_cap0.05
    - control_d1_nocap
    - control_d1_cap0.25
    - control_d1_cap0.05
    - mature_d4_nocap
    - mature_d4_cap0.25
    - mature_d4_cap0.05
    - control_d4_nocap
    - control_d4_cap0.25
    - control_d4_cap0.05
    - mature_d32_nocap
    - mature_d32_cap0.25
    - mature_d32_cap0.05
    - control_d32_nocap
    - control_d32_cap0.25
    - control_d32_cap0.05
- COMMON-RANDOM-NUMBERS POLICY: default; every arm of a seed shares generation 0 (common fill; the import REPLACES the worst-scored members after the first evaluation) and the per-generation episode batteries; the cap redraws the primary parent among residents beyond 0.25 of the children
- BUDGET:
    {"E": 16, "G": 60, "N": 200, "caps": [0.0, 0.25, 0.05], "doses": [0, 1, 4, 32], "mature_sources": 11, "qualities": ["mature", "control"], "runs": 228, "seeds": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "target": {"D": 1, "K": 1, "Kd": 0, "ask_kind": "ASK", "ask_mode": "all", "ask_timing": "end", "delay": 4, "delays": [], "expensive": 0, "fanout": 1, "interfere": false, "interleave": "sequential", "n_defs": 0, "name": "W1_d4", "noise_rate": 0.0, "op_mode": "fixed", "recycle": false, "retire_rate": 0.0, "topology": "streams", "value_bits": 4, "vocab": "train"}}
- PRIMARY OBSERVABLE: takeover (import share >= 0.9 by G) and takeover_gen per run, as a function of dose x quality x cap; the declared machine contrast is mature vs control at dose 4 without the cap
- CLAIM CEILING: an ecological reading of THIS loop (tournament 4, elitism 4, N=200): the dose above which foreign lineage replaces the population, and whether the replacement needs competence; no claim about transfer value
- FALSIFICATION CONDITION: if the permuted control takes over at the same doses as the mature material, capability does not drive takeover: injection mechanics do (the C2 'transport hurts yet takes over' reading is mechanics); if neither takes over below dose 32, injection is ecologically safe at small doses and campaign-2 takeovers were dose effects
- KILL CONDITION: the mature material is not directly competent on W1_d4 (held-out < 0.5): the source is not 'mature relevant' and the slot must use another source
- TYPED FAILURE CONDITIONS:
    - IMMATURE_ARTIFACT
    - INTERVENTION_NOT_APPLIED
    - POSITIVE_CONTROL_FAILED
    - UNDERPOWERED
    - ENGINE_FAILURE / INSTRUMENT_FAILURE
- EXPECTED MACHINE TELEMETRY:
    - import / pure-resident / hybrid share per generation
    - distinct-genome share per generation
    - takeover and half-takeover generations
    - resident best reward at the end
    - elite origin
    - target held-out competence and levels
    - reachability rows (treated)
- MACHINE CHANGES EXERCISED:
    - F inject + offspring_cap
    - origin shares per generation
    - levels + held-out
    - reachability rows
- REPLACEMENT CONDITION: none: the slot is a replacement itself (failed-fragment transfer retired); it is moot only if no mature source exists
- ANCESTRY (original | replacement): replacement (queue slot 10; the retired failed-material-transfer programme)
- decl (machine-read by archaeon.wse.states): {"battery": [{"name": "control_takeover_at_mid_dose_below_half", "passed": null}, {"name": "mature_takeover_monotone_in_dose", "passed": null}, {"name": "cap_slows_takeover", "passed": null}], "n_min": 12, "positive_control": {"arm": "mature_d32_nocap", "metric": "takeover", "min": 1, "min_rows": 8}, "primary": {"control": "control_d4_nocap", "metric": "takeover", "min_effect": 0.5, "treatment": "mature_d4_nocap"}}

## B. EXECUTION (generated from receipts)

- attempts: 2 (of record: a04); resumed_from: 3; replayed steps on the attempt of record: 6
    a01  errors=0 replayed=0 engine=False purpose=dry run disposition_candidate=POSITIVE_CONTROL_FAILED
    a04  errors=0 replayed=6 engine=True purpose=engine disposition_candidate=CAPABLE_NEGATIVE
- engine: live; worlds 1; artifacts 3; imports 1; records 228; errors 0
- import hash checks: 1/1 ok
- timings (s): ecology_s=1386.39, records_s=123.81, startup_s=0.0, teardown_s=0.21, total_s=1511.7
- decisions: D3-014: the matched control is the SAME instruction blocks permuted (length, opcode multiset, operands and VM knobs preserved; competence removed, verified < 0.25 held-out), D3-015: injection at generation 0 after the first evaluation (inject replaces the worst-scored residents); the cap arm uses offspring_cap=0.25 on the 'import' origin
- warnings from the loop: []

## C. SCIENCE (numbers generated from rows; interpretation in the addendum)

- primary table:
    arm / takeover              s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    control_d1_cap0.05           0       1       1       1       1       1       1       1       1       1       1       1   0.917   12
    control_d1_cap0.25           0       1       1       1       1       1       1       1       1       1       1       1   0.917   12
    control_d1_nocap             0       1       1       1       1       1       1       1       1       1       1       1   0.917   12
    control_d32_cap0.05          1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    control_d32_cap0.25          1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    control_d32_nocap            1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    control_d4_cap0.05           1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    control_d4_cap0.25           1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    control_d4_nocap             1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d1_cap0.05            1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d1_cap0.25            1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d1_nocap              1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d32_cap0.05           1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d32_cap0.25           1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d32_nocap             1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d4_cap0.05            1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d4_cap0.25            1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d4_nocap              1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    none_d0_nocap                0       0       0       0       0       0       0       0       0       0       0       0   0.000   12

    arm / takeover_gen          s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    control_d1_cap0.05           -      41      45      33      34      41      34      57      44      41      37      36  40.273   11
    control_d1_cap0.25           -      12      14      17      13      13      13       8      12      10      11      10  12.091   11
    control_d1_nocap             -       8       9      11       8       7       9       6       8       6       8       7   7.909   11
    control_d32_cap0.05         45      36      26      30      36      32      27      32      27      35      36      34  33.000   12
    control_d32_cap0.25          9       7       5       7       9       6       4       8       7       7       6       8   6.917   12
    control_d32_nocap            4       3       3       4       4       4       3       4       3       3       4       3   3.500   12
    control_d4_cap0.05          43      33      34      41      46      51      37      32      35      35      48      46  40.083   12
    control_d4_cap0.25          11       9      13       9       9      10      12       8      10      10       9       9   9.917   12
    control_d4_nocap             7       4       7       6       6       6       6       5       7       6       6       6   6.000   12
    mature_d1_cap0.05           21      22      20      16      22      18      22      17      16      18      16      15  18.583   12
    mature_d1_cap0.25            6       6       6       7       7       6       5       6       7       6       6       6   6.167   12
    mature_d1_nocap              4       4       5       4       5       4       5       5       5       4       4       5   4.500   12
    mature_d32_cap0.05          15       6      20      19      10      11      16      16       6       9       9      14  12.583   12
    mature_d32_cap0.25           3       3       3       3       3       3       2       4       3       3       4       3   3.083   12
    mature_d32_nocap             2       2       2       2       2       2       2       2       2       2       2       2   2.000   12
    mature_d4_cap0.05           21      13      14      17      14      24      12      15      16      12      16      15  15.750   12
    mature_d4_cap0.25            4       5       6       6       5       4       5       5       5       7       6       5   5.250   12
    mature_d4_nocap              3       3       3       3       3       3       4       3       4       4       3       3   3.250   12
    none_d0_nocap                -       -       -       -       -       -       -       -       -       -       -       -       -    0

    arm / pure_resident_final      s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    control_d1_cap0.05       1.000   0.000   0.000   0.000   0.000   0.120   0.000   0.135   0.000   0.020   0.035   0.000   0.109   12
    control_d1_cap0.25       1.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.083   12
    control_d1_nocap         1.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.083   12
    control_d32_cap0.05      0.075   0.060   0.000   0.020   0.000   0.000   0.000   0.000   0.000   0.035   0.000   0.010   0.017   12
    control_d32_cap0.25      0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12
    control_d32_nocap        0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12
    control_d4_cap0.05       0.035   0.000   0.000   0.080   0.140   0.020   0.005   0.000   0.000   0.030   0.000   0.000   0.026   12
    control_d4_cap0.25       0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12
    control_d4_nocap         0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12
    mature_d1_cap0.05        0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12
    mature_d1_cap0.25        0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12
    mature_d1_nocap          0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12
    mature_d32_cap0.05       0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12
    mature_d32_cap0.25       0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12
    mature_d32_nocap         0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12
    mature_d4_cap0.05        0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12
    mature_d4_cap0.25        0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12
    mature_d4_nocap          0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   0.000   12
    none_d0_nocap            1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   12

    arm / competence_heldout      s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    control_d1_cap0.05       0.042   0.042   0.062   0.104   0.167   0.062   0.062   0.125   0.083   0.062   0.021   0.104   0.078   12
    control_d1_cap0.25       0.042   0.062   0.062   0.979   0.021   0.062   0.083   0.125   0.083   0.062   0.125   0.104   0.151   12
    control_d1_nocap         0.042   0.062   0.062   0.104   0.021   0.062   1.000   1.000   1.000   1.000   0.125   0.104   0.382   12
    control_d32_cap0.05      0.042   0.062   0.062   0.104   0.021   0.062   0.062   0.125   0.083   0.062   0.042   0.083   0.068   12
    control_d32_cap0.25      0.042   0.062   0.062   0.104   0.021   0.125   0.083   0.125   0.104   0.062   0.125   0.083   0.083   12
    control_d32_nocap        1.000   1.000   0.083   1.000   0.021   0.062   1.000   0.125   1.000   1.000   0.125   0.979   0.616   12
    control_d4_cap0.05       0.042   0.062   0.062   0.021   0.021   0.062   0.062   0.125   0.083   0.062   0.042   0.062   0.059   12
    control_d4_cap0.25       0.021   0.062   0.062   1.000   1.000   0.042   0.083   0.125   0.083   0.062   0.125   0.062   0.227   12
    control_d4_nocap         0.042   0.083   0.062   0.021   1.000   0.062   0.083   0.125   0.083   1.000   0.125   0.104   0.233   12
    mature_d1_cap0.05        1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   12
    mature_d1_cap0.25        1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   12
    mature_d1_nocap          1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   12
    mature_d32_cap0.05       1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   12
    mature_d32_cap0.25       1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   12
    mature_d32_nocap         1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   12
    mature_d4_cap0.05        1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   12
    mature_d4_cap0.25        1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   12
    mature_d4_nocap          1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   1.000   12
    none_d0_nocap            0.042   0.062   0.062   0.104   0.021   0.062   0.062   0.125   0.104   0.062   0.167   0.083   0.080   12

    arm / distinct_min          s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    control_d1_cap0.05       0.930   0.875   0.640   0.825   0.855   0.865   0.845   0.895   0.850   0.785   0.835   0.765   0.830   12
    control_d1_cap0.25       0.930   0.890   0.690   0.880   0.810   0.875   0.875   0.860   0.775   0.910   0.870   0.840   0.850   12
    control_d1_nocap         0.930   0.965   0.870   0.945   0.915   0.945   0.930   0.880   0.930   0.925   0.935   0.820   0.916   12
    control_d32_cap0.05      0.870   0.860   0.610   0.755   0.840   0.860   0.820   0.850   0.690   0.575   0.790   0.845   0.780   12
    control_d32_cap0.25      0.695   0.895   0.780   0.895   0.705   0.825   0.895   0.855   0.715   0.845   0.820   0.815   0.812   12
    control_d32_nocap        0.895   0.895   0.895   0.895   0.895   0.895   0.895   0.895   0.895   0.895   0.895   0.895   0.895   12
    control_d4_cap0.05       0.620   0.790   0.635   0.630   0.885   0.905   0.815   0.880   0.630   0.650   0.785   0.730   0.746   12
    control_d4_cap0.25       0.780   0.690   0.600   0.900   0.885   0.770   0.800   0.910   0.830   0.830   0.920   0.685   0.800   12
    control_d4_nocap         0.925   0.950   0.860   0.940   0.935   0.940   0.945   0.940   0.930   0.880   0.955   0.905   0.925   12
    mature_d1_cap0.05        0.765   0.850   0.575   0.820   0.835   0.710   0.845   0.565   0.700   0.790   0.710   0.785   0.746   12
    mature_d1_cap0.25        0.635   0.775   0.635   0.860   0.765   0.865   0.805   0.850   0.595   0.870   0.745   0.865   0.772   12
    mature_d1_nocap          0.880   0.885   0.855   0.880   0.885   0.905   0.885   0.870   0.900   0.875   0.875   0.875   0.881   12
    mature_d32_cap0.05       0.730   0.810   0.795   0.825   0.810   0.770   0.830   0.780   0.780   0.800   0.840   0.845   0.801   12
    mature_d32_cap0.25       0.735   0.895   0.805   0.865   0.760   0.815   0.835   0.845   0.860   0.765   0.720   0.880   0.815   12
    mature_d32_nocap         0.895   0.895   0.895   0.895   0.895   0.895   0.895   0.895   0.895   0.895   0.895   0.895   0.895   12
    mature_d4_cap0.05        0.840   0.860   0.490   0.785   0.865   0.705   0.865   0.660   0.800   0.810   0.680   0.810   0.764   12
    mature_d4_cap0.25        0.650   0.825   0.745   0.900   0.840   0.905   0.725   0.585   0.735   0.885   0.835   0.700   0.777   12
    mature_d4_nocap          0.930   0.940   0.935   0.930   0.920   0.905   0.925   0.910   0.925   0.925   0.930   0.920   0.925   12
    none_d0_nocap            0.930   0.915   0.775   0.950   0.925   0.940   0.945   0.915   0.920   0.945   0.960   0.925   0.920   12

    arm / elite_import_final      s1     s10     s11     s12      s2      s3      s4      s5      s6      s7      s8      s9    mean    n
    control_d1_cap0.05           0       1       1       1       1       1       1       1       1       1       1       1   0.917   12
    control_d1_cap0.25           0       1       1       1       1       1       1       1       1       1       1       1   0.917   12
    control_d1_nocap             0       1       1       1       1       1       1       1       1       1       1       1   0.917   12
    control_d32_cap0.05          1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    control_d32_cap0.25          1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    control_d32_nocap            1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    control_d4_cap0.05           1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    control_d4_cap0.25           1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    control_d4_nocap             1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d1_cap0.05            1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d1_cap0.25            1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d1_nocap              1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d32_cap0.05           1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d32_cap0.25           1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d32_nocap             1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d4_cap0.05            1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d4_cap0.25            1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    mature_d4_nocap              1       1       1       1       1       1       1       1       1       1       1       1   1.000   12
    none_d0_nocap                0       0       0       0       0       0       0       0       0       0       0       0   0.000   12

- typed states fired: none
- disposition candidate (machine): CAPABLE_NEGATIVE -- assay capable and effect < min_effect
    evidence: {"control_mean": 1.0, "effect": 0.0, "min_effect": 0.5, "n_control": 12, "n_treatment": 12, "paired": 12, "paired_wins": 0, "treatment_mean": 1.0}
- claim ceiling (machine): negative at this budget/envelope; preregistered ceiling: an ecological reading of THIS loop (tournament 4, elitism 4, N=200): the dose above which foreign lineage replaces the population, and whether the replacement needs competence; no claim about transfer value

### C-addendum (agent interpretation; quotes the candidate, may argue with it)

(none)

## D. TEARDOWN (generated)

- worlds: {"dose": "TERMINATED"}
- all TERMINATED: True

## E. BENCH IMPROVEMENT

- ledger candidates (generated): see LEDGER.jsonl entries tagged C3-SFE-10

(none)

## F. LANDSCAPE / GRADIENT NOTES

(none)

DISPOSITION: CAPABLE_NEGATIVE (machine candidate CAPABLE_NEGATIVE). 
