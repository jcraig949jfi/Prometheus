# Out-of-sample test of the repaired map predictor (P_run500_causal) on X-DD-ESTABLISH W1 D0 donors

Date: 2026-09-30. Static analysis (single-interaction VM calls only; no world runs, no evolution runs, no git writes).

## PRE-REGISTRATION (written verbatim before any computation)

**PRE-REGISTRATION (frozen here, before you compute anything).**
- **Predictor.** Exactly the P_run500_causal predictor as implemented in map_correlate.py / map_children.py. Read the code and reuse it unchanged. It is computed per donor under the register context matching the target experiment's world (see below). Do not tune anything. If the code has free choices, use the same values it used for panel A.
- **Out-of-sample panel.** The W1 first donors (D0) of X-DD-ESTABLISH:
  - F:/Prometheus-worktrees/nestor-d2v13/roles/Nestor/campaigns/npe-w1-donor-discovery-2026-09-26/x_dd_establish/ (results/*.json; field lineage_births = causal births from the D0 lineage; outcome label ESTABLISHED/NO_COPY/...).
  - Get the D0 genome hex from those results, or from x_dd_selfstate/results or x_dd_nocopy_context/results, matching on (cell, seed). If a D0 has several genomes, use the first listed, and say so.
- **World of that experiment.** Dense VM, cells 7ae3 and ffa6 (run_dd.CELLS), ATOMIC runner (run_ds.runner_cls), CARRIED registers, random background population. Use the CARRY context of the existing harness. Check how the harness builds the runner for a given cell, and build it the way X-DD-ESTABLISH does (read its run_*.py).
- **Outcomes, both pre-declared:**
  - O1 = D0 made ≥ 1 causal birth (lineage_births ≥ 1);
  - O2 = D0 made ≥ 29 causal births (the "real establishment" split seen in dossier D U3).
- **Pass criterion (frozen).** For O1: ROC AUC ≥ 0.75 with a one-sided permutation p < 0.01. For O2: Spearman(predictor, lineage_births) ≥ 0.4 with permutation p < 0.01.
  - Both met: PASS.
  - One met: PARTIAL.
  - Neither met: FAIL.
  - Report also the specified (non-repaired) P_est as a comparator. It is not decisive.
- **Exclusions.** Exclude runs with no identifiable D0 genome (NO_D0) and report the count. Include no other exclusions.

---

## Verdict: PASS (with three qualifications that limit what it credits)

The pre-registered predictor, P_run500_causal, meets both frozen criteria on the 43 out-of-sample D0 donors.

| outcome | statistic | value | 95% bootstrap CI | one-sided permutation p | threshold | met |
|---|---|---|---|---|---|---|
| O1 (births >= 1; 15 pos / 28 neg) | ROC AUC | **0.891** | [0.765, 0.978] | 5e-5 (the floor with 20,000 permutations) | >= 0.75, p < 0.01 | yes |
| O2 (births >= 29; 8 pos / 35 neg) | Spearman(pred, lineage_births) | **0.706** | [0.468, 0.884] | 5e-5 (floor) | >= 0.4, p < 0.01 | yes |

Read these qualifications before crediting the repair:
1. **The pre-registered predictor is not the child-law repair.**
   - In `map_correlate.py`, `P_run500_causal = gw_run(CAUSAL p0, p1, p2)`. That is the donor's *own* causal single-type law, run through a 500-generation finite horizon with K = 230. It uses no child law.
   - The two-type "children's conversion law" repair is `P_run2` (map_children + `gw2_run`). The brief's wording ("children's own conversion law plus a 500-epoch horizon (P_run500 and P_run500_causal)") mixes the two up.
   - I followed the pre-registration's operative sentence and scored P_run500_causal as decisive.
   - I also computed P_run2 as a secondary, non-decisive predictor. It passes too: AUC 0.912, rho 0.688.
   - In panel A-ZERO, P_run500_causal had rho 0.02. Only P_run2 fixed that arm.
   - The brief's "0.81-0.86" figures are P_run500_causal pooled over A+B-CF (0.81) and P_run2 pooled (0.86).
2. **The test does not separate the repair from the specified map.**
   - The specified P_est also clears both frozen thresholds here, barely: AUC 0.779 (p 0.001) and rho 0.413 (p 0.0045).
   - Every other comparator passes as well. Plain mean offspring m (AUC 0.993, rho 0.804) and children's conversion rate (AUC 0.991, rho 0.861) beat the pre-registered predictor.
   - The repair is clearly better than P_est: AUC 0.89 vs 0.78, rho 0.71 vs 0.41. But the finite-horizon GW machinery adds nothing over one question: does this donor convert partners from its carried state at all (m, p2)?
   - This panel is easier than A-ZERO. 23 of the 28 O1-negatives have causal p2 <= 0.002, meaning they do not copy from carried state. What gets predicted here is the split between copiers and non-copiers.
3. **W1 already measured this.** W1's earlier carried-state measurements of the same genomes predict as well or better (descriptive only, from `oos_sensitivity.py`):
   - x_dd_nocopy_context OWN_REAL rate: AUC 0.920, rho 0.845;
   - x_dd_selfstate rate_k1: AUC 0.900, rho 0.886 (n = 41).

   The out-of-sample success fits the view that carried-state self-poisoning decides whether D0 copies, which W1 had already established. It shows that the single-interaction map recovers that finding, not that the map adds new information.

## 1. What was run

**Panel.**
- All 49 X-DD-ESTABLISH runs.
- The D0 genome is the `donor_hex` field of `x_dd_nocopy_context/results/<cell>_<seed>.json`, matched on (cell, seed). That script stores exactly one genome per run, `comp[0]`, the first COMPETENT organism at the D0 check. So "use the first listed genome" is applied automatically.
- D0 had more than one member in 17 of the 43 runs used (see the d0_size column). Only the first member was scored.
- Neither x_dd_selfstate nor x_dd_establish records a genome hex.
- All 43 matched records have `replay_ok = True`. Two have `control_ok = False` (7ae3 16000008 and 16000020). They are included, because the pre-registration allows no other exclusions.

**Exclusions: 6 runs (NO_D0).**
- 1 run has status NO_D0: 7ae3 16000014.
- 5 runs have a D0 whose genome no source records, because x_dd_nocopy_context only replayed NO_COPY and ESTABLISHED runs:

  | run | status | births |
  |---|---|---|
  | 7ae3 16000000 | LOST_COMPETENT | 13 |
  | 7ae3 16000010 | INCOMPETENT_COPIES | 1 |
  | 7ae3 16000029 | LOST_COMPETENT | 4 |
  | ffa6 16000021 | LOST_COMPETENT | 4 |
  | ffa6 16000024 | INCOMPETENT_COPIES | 2 |

- These five fall under the pre-registered definition "no identifiable D0 genome". Recovering them would need a world replay, which is out of scope.
- All five are O1-positive and O2-negative, so dropping them could flatter the O1 result.
- **Worst-case bound** (each of the five given the floor predictor value 0.0): O1 AUC 0.775 (p 5e-5) and O2 rho 0.592 (p 5e-5), n = 48. The verdict survives the worst case.
- Best case (each given 1.0): AUC 0.918, rho 0.707.

**World.**
- X-DD-ESTABLISH builds its runner as `run_ds.runner_cls(world)(dict(run_ds.cells()[run_dd.CELLS[cell]]["cell"], atlas_axis="NONE"), seed, tier=...)`, with `world.z8 = run_dc.dense_z8()` and no implant, so the population is random.
- I verified in code, with a check that returned True for both cells, that the 7ae3 cell dict and tier equal the map harness's cell "C7", and that ffa6's equal the harness's cell "CF". Both have L 64, tape 128, slice 300, ops mask 42, cmr 0.002 and tier M.
- `run_rs.runner(..., "CARRY")` returns the bare ATOMIC class, so the harness's CARRY context is exactly this world's register physics.
- **The harness and the decisive predictor's code needed no adaptation.** `oos_predict.py` imports `map_common`, `map_offspring` and `map_correlate` and calls them unchanged.

**How the predictors were computed (panel-A values).**
- `T = map_offspring.transmitted(g)`, using the default cell as `map_offspring.main` does.
- `law = map_offspring.condition(g, harness_cell, "CARRY", T, partner_pool(harness_cell), 30_000 + 97*i + CTX.index("CARRY"))`, with N = 500 interactions. Here i is the donor's index in this panel, following the panel-A seed formula.
- `P_run500_causal = map_correlate.gw_run(CAUSAL law)`, with K = 230, H = 500 and 2,000 reps. The module RNG is `default_rng(20260930)`, as for panels A and B.
- Comparators from the same law: P_est (the T law, the specified map), P_est_causal, P_run500 and m.
- P_run2 (secondary) uses `map_children.run_law`, the child loop and `map_correlate.gw2_run`, with NF 400, NC 40, NI 25 and the panel-A seed offset. **Adaptation:** `map_children.main` hard-codes cell CF; here the donor's own harness cell is passed (C7 for 7ae3 donors). P_run2 is non-decisive.

**Statistics (`oos_stats.py`).**
- AUC is the Mann-Whitney statistic, with ties counted as 1/2.
- Spearman uses average ranks.
- The one-sided permutation p uses 20,000 label shuffles, so its floor is 5e-5.
- Bootstrap CIs resample donors 2,000 times.

## 2. Per-donor table

Rows are sorted by lineage_births, then by P_run500_causal. "W1 nc label" is x_dd_nocopy_context's label; STATE means the donor's own carried state blocks copying.

| # | cell | seed | status | d0_size | births | O1 | O2 | P_run500_causal | P_est | P_est_causal | causal p0 / p2 | m | P_run2 | child_conv | W1 nc label |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ffa6 | 16000030 | ESTABLISHED | 2 | 25950 | 1 | 1 | **0.761** | 0.768 | 0.761 | 0.044 / 0.184 | 1.146 | 0.690 | 0.150 | STATE |
| 2 | ffa6 | 16000007 | ESTABLISHED | 1 | 5603 | 1 | 1 | **0.689** | 0.694 | 0.680 | 0.128 / 0.400 | 1.290 | 0.644 | 0.347 | NONE |
| 3 | ffa6 | 16000022 | ESTABLISHED | 1 | 3037 | 1 | 1 | **0.868** | 0.885 | 0.883 | 0.018 / 0.154 | 1.138 | 0.814 | 0.090 | NONE |
| 4 | 7ae3 | 16000046 | ESTABLISHED | 5 | 1163 | 1 | 1 | **0.570** | 0.621 | 0.574 | 0.144 / 0.338 | 1.236 | 0.602 | 0.248 | NONE |
| 5 | ffa6 | 16000033 | ESTABLISHED | 7 | 1001 | 1 | 1 | **0.747** | 0.739 | 0.739 | 0.046 / 0.176 | 1.130 | 0.804 | 0.131 | NONE |
| 6 | 7ae3 | 16000026 | ESTABLISHED | 48 | 986 | 1 | 1 | **0.688** | 0.752 | 0.694 | 0.160 / 0.522 | 1.484 | 0.750 | 0.589 | NONE |
| 7 | 7ae3 | 16000006 | ESTABLISHED | 7 | 527 | 1 | 1 | **0.851** | 0.865 | 0.854 | 0.014 / 0.096 | 1.090 | 0.736 | 0.084 | STATE |
| 8 | 7ae3 | 16000042 | ESTABLISHED | 13 | 29 | 1 | 1 | **0.972** | 0.990 | 0.976 | 0.002 / 0.082 | 1.200 | 1.000 | 0.181 | STATE |
| 9 | ffa6 | 16000005 | ESTABLISHED | 3 | 7 | 1 | 0 | **0.000** | 0.690 | 0.000 | 0.062 / 0.042 | 1.138 | 0.622 | 0.169 | PARTNER |
| 10 | 7ae3 | 16000028 | ESTABLISHED | 2 | 6 | 1 | 0 | **0.562** | 0.816 | 0.579 | 0.032 / 0.076 | 1.142 | 0.762 | 0.168 | STATE |
| 11 | ffa6 | 16000012 | ESTABLISHED | 2 | 5 | 1 | 0 | **1.000** | 1.000 | 1.000 | 0.000 / 0.096 | 1.114 | 0.964 | 0.063 | NONE |
| 12 | ffa6 | 16000026 | ESTABLISHED | 3 | 4 | 1 | 0 | **0.464** | 0.784 | 0.458 | 0.064 / 0.118 | 1.232 | 0.782 | 0.246 | NONE |
| 13 | ffa6 | 16000003 | ESTABLISHED | 2 | 3 | 1 | 0 | **1.000** | 1.000 | 1.000 | 0.000 / 0.052 | 1.112 | 1.000 | 0.105 | NONE |
| 14 | 7ae3 | 16000015 | ESTABLISHED | 2 | 3 | 1 | 0 | **0.668** | 0.923 | 0.647 | 0.012 / 0.034 | 1.144 | 0.894 | 0.135 | STATE |
| 15 | 7ae3 | 16000021 | ESTABLISHED | 2 | 1 | 1 | 0 | **0.649** | 0.922 | 0.636 | 0.016 / 0.044 | 1.190 | 0.930 | 0.118 | STATE |
| 16 | ffa6 | 16000032 | ESTABLISHED | 1 | 0 | 0 | 0 | **0.962** | 0.970 | 0.958 | 0.002 / 0.048 | 1.064 | 1.000 | 0.046 | STATE |
| 17 | ffa6 | 16000045 | ESTABLISHED | 1 | 0 | 0 | 0 | **0.868** | 0.925 | 0.875 | 0.006 / 0.048 | 1.074 | 0.944 | 0.061 | PARTNER |
| 18 | ffa6 | 16000020 | ESTABLISHED | 2 | 0 | 0 | 0 | **0.760** | 0.968 | 0.800 | 0.004 / 0.020 | 1.122 | 0.902 | 0.112 | PARTNER |
| 19 | 7ae3 | 16000020 | NO_COPY | 1 | 0 | 0 | 0 | **0.011** | 1.000 | 1.000 | 0.000 / 0.008 | 1.012 | 0.000 | 0.000 | NONE (ctrl fail) |
| 20 | 7ae3 | 16000003 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.000 | 0.000 | 0.000 / 0.000 | 1.000 | 0.000 | 0.000 | STATE |
| 21 | 7ae3 | 16000008 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.800 | 0.000 | 0.002 / 0.002 | 1.008 | 0.000 | 0.011 | STATE (ctrl fail) |
| 22 | 7ae3 | 16000019 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.667 | 0.500 | 0.002 / 0.004 | 1.004 | 0.000 | 0.000 | PARTNER |
| 23 | 7ae3 | 16000033 | ESTABLISHED | 1 | 0 | 0 | 0 | **0.000** | 0.000 | 0.000 | 0.000 / 0.000 | 1.000 | 0.004 | 0.013 | PARTNER |
| 24 | 7ae3 | 16000036 | ESTABLISHED | 2 | 0 | 0 | 0 | **0.000** | 0.000 | 0.000 | 0.004 / 0.000 | 0.996 | 0.000 | 0.000 | STATE |
| 25 | 7ae3 | 16000043 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.000 | 0.000 | 0.000 / 0.000 | 1.000 | 0.000 | 0.000 | STATE |
| 26 | 7ae3 | 16000045 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.000 | 0.000 | 0.018 / 0.000 | 0.982 | 0.000 | 0.000 | STATE |
| 27 | ffa6 | 16000000 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.500 | 0.000 | 0.006 / 0.002 | 1.006 | 0.000 | 0.000 | STATE |
| 28 | ffa6 | 16000001 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.000 | 0.000 | 0.024 / 0.002 | 0.978 | 0.000 | 0.000 | PARTNER |
| 29 | ffa6 | 16000002 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.000 | 0.000 | 0.012 / 0.000 | 0.990 | 0.000 | 0.000 | PARTNER |
| 30 | ffa6 | 16000006 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.000 | 0.000 | 0.000 / 0.000 | 1.000 | 0.000 | 0.000 | PARTNER |
| 31 | ffa6 | 16000008 | ESTABLISHED | 1 | 0 | 0 | 0 | **0.000** | 0.000 | 0.000 | 0.020 / 0.000 | 0.980 | 0.000 | 0.000 | PARTNER |
| 32 | ffa6 | 16000010 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.000 | 0.000 | 0.024 / 0.004 | 0.980 | 0.000 | 0.000 | PARTNER |
| 33 | ffa6 | 16000011 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.000 | 0.000 | 0.030 / 0.002 | 0.972 | 0.000 | 0.000 | PARTNER |
| 34 | ffa6 | 16000014 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.500 | 0.000 | 0.002 / 0.000 | 1.002 | 0.000 | 0.000 | PARTNER |
| 35 | ffa6 | 16000016 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.000 | 0.000 | 0.016 / 0.000 | 0.990 | 0.000 | 0.000 | PARTNER |
| 36 | ffa6 | 16000025 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.000 | 0.000 | 0.010 / 0.000 | 0.998 | 0.000 | 0.000 | STATE |
| 37 | ffa6 | 16000027 | ESTABLISHED | 1 | 0 | 0 | 0 | **0.000** | 0.778 | 0.000 | 0.004 / 0.000 | 1.014 | 0.000 | 0.010 | PARTNER |
| 38 | ffa6 | 16000035 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.667 | 0.000 | 0.002 / 0.000 | 1.004 | 0.000 | 0.000 | STATE |
| 39 | ffa6 | 16000038 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 1.000 | 0.000 | 0.000 / 0.000 | 1.002 | 0.000 | 0.000 | STATE |
| 40 | ffa6 | 16000039 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.000 | 0.000 | 0.000 / 0.000 | 1.000 | 0.000 | 0.000 | PARTNER |
| 41 | ffa6 | 16000041 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.000 | 0.000 | 0.004 / 0.002 | 0.998 | 0.000 | 0.000 | PARTNER |
| 42 | ffa6 | 16000043 | NO_COPY | 1 | 0 | 0 | 0 | **0.000** | 0.000 | 0.000 | 0.014 / 0.000 | 0.986 | 0.000 | 0.000 | PARTNER |
| 43 | ffa6 | 16000044 | ESTABLISHED | 1 | 0 | 0 | 0 | **0.000** | 1.000 | 1.000 | 0.000 / 0.002 | 1.002 | 0.000 | 0.000 | STATE |

Reading the table:
- All 8 O2-positive donors have P_run500_causal between 0.57 and 0.97.
- Every O1-negative with causal p2 <= 0.002 scores 0.00-0.01.
- **One O1 miss.** ffa6 16000005 made 7 births, but its causal p2 (0.042) is below its p0 (0.062), so the horizon rule gives it 0.0. P_est (0.69) and P_run2 (0.62) rank it higher.
- **Two O1-negatives rank high:** ffa6 16000020 (0.76) and ffa6 16000045 (0.87). Both are ESTABLISHED runs in which the lineage that established was not D0's own; D0's lineage made 0 births.
- 8 of the 23 ESTABLISHED runs have 0 D0-lineage births, and the predictor gives 6 of them 0.0. It tracks the D0 lineage, not world establishment, which is what O1 and O2 are meant to measure.

## 3. All predictors (n = 43)

| predictor | O1 AUC [95% CI] | perm p | O2 Spearman rho [95% CI] | perm p | AUC for O2 binary | mean pred, O1+ / O1- | would pass frozen rule |
|---|---|---|---|---|---|---|---|
| **P_run500_causal (decisive)** | **0.891** [0.765, 0.978] | 5e-5 | **0.706** [0.468, 0.884] | 5e-5 | 0.871 | 0.699 / 0.093 | PASS |
| P_est (specified comparator) | 0.779 [0.627, 0.909] | 0.0011 | 0.413 [0.164, 0.640] | 0.0045 | 0.650 | 0.830 / 0.349 | PASS (marginal) |
| P_est_causal | 0.824 [0.683, 0.941] | 1e-4 | 0.568 [0.324, 0.798] | 1.5e-4 | 0.811 | 0.699 / 0.183 | PASS |
| P_run500 (T law) | 0.917 [0.809, 1.000] | 5e-5 | 0.669 [0.468, 0.821] | 5e-5 | 0.771 | 0.831 / 0.147 | PASS |
| m (mean offspring, T law) | 0.993 [0.971, 1.000] | 5e-5 | 0.804 [0.692, 0.858] | 5e-5 | 0.927 | 1.186 / 1.006 | PASS |
| P_run2 (two-type child law, secondary) | 0.912 [0.803, 1.000] | 5e-5 | 0.688 [0.465, 0.881] | 5e-5 | 0.782 | 0.800 / 0.102 | PASS |
| child_conv | 0.991 [0.963, 1.000] | 5e-5 | 0.861 [0.761, 0.925] | 5e-5 | 0.921 | 0.188 / 0.009 | PASS |

By cell (descriptive only; all p < 0.001):
- 7ae3 (n = 15): AUC 1.000, rho 0.874;
- ffa6 (n = 28): AUC 0.847, rho 0.612.

P_est stays miscalibrated out of sample.
- Its mean on O1-negatives is 0.35.
- Several non-copiers score 0.5-1.0 through the p0 ≈ 0 degeneracy. For example, 7ae3 16000020 and ffa6 16000038 both score 1.0 with p2 <= 0.008.
- The horizon rule removes that degeneracy: the same two donors score 0.011 and 0.0.

## 4. CPU and files

CPU (single process, `python -B`):

| step | time |
|---|---|
| oos_predict.py | 56.7 s (primary predictors about 20 s, P_run2 children about 37 s) |
| oos_stats.py | about 68 s wall |
| oos_sensitivity.py | about 19 s wall |
| checks | about 10 s |
| **total** | **about 2.6 min** |

Files (all in this folder):
- `oos_predict.py` → `oos_predict.json`, `oos_predict.log`: per-donor laws and predictors, and the exclusions;
- `oos_stats.py` → `oos_stats.json`, `oos_stats.log`: the pre-registered statistics and the verdict;
- `oos_sensitivity.py` → `oos_sensitivity.json`: written after the verdict, descriptive only (exclusion bounds and W1 baselines).

No git writes were made. Nothing under holdout_D2, c3_holdout or nestor_secrets was read or written.

## Summary (10 lines)
1. Panel: 49 X-DD-ESTABLISH W1 runs; 43 D0 genomes recovered from x_dd_nocopy_context (first D0 organism); 6 excluded as NO_D0 (1 with status NO_D0, 5 with no recorded genome).
2. The world was reproduced exactly: 7ae3 = harness C7 and ffa6 = harness CF (verified), ATOMIC runner, CARRY context. The predictor code was reused unchanged.
3. Decisive predictor P_run500_causal: O1 AUC 0.891 [0.765, 0.978], p 5e-5; O2 Spearman 0.706 [0.468, 0.884], p 5e-5.
4. **Verdict: PASS** (both frozen criteria met). Giving the 5 genome-less exclusions the worst-case value still passes (AUC 0.775, rho 0.592).
5. Caveat: P_run500_causal as coded has no child law. The child-law repair is P_run2, which also passes (0.912 / 0.688) but needed an adaptation (own cell) and is non-decisive.
6. Caveat: the specified P_est also passes, marginally (0.779 / 0.413). The test confirms the map family but does not isolate the repair, although the repair is clearly better.
7. Simpler statistics beat the pre-registered one: m (0.993 / 0.804) and child_conv (0.991 / 0.861). The finite-horizon GW adds nothing over "copies from carried state or not".
8. W1's own carried-state measurements of the same genomes predict as well (nc OWN_REAL 0.920 / 0.845). The map recovers the known self-poisoning split rather than adding new information.
9. P_est's p0 ≈ 0 degeneracy persists out of sample (non-copiers scoring 0.5-1.0), and the horizon rule removes it. 8 of 23 ESTABLISHED runs had 0 D0-lineage births.
10. CPU: about 2.6 min. Report: F:/Prometheus-worktrees/nestor-d2v13/roles/Nestor/inference_harvest_2026-09-30/forensics/FORENSIC_MAP_OUT_OF_SAMPLE.md
