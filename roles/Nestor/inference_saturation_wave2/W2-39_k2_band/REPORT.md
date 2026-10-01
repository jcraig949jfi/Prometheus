# W2-39: K2 prediction bands from M\* for morph founders

> Saved by Nestor from the worker's returned text, condensed with every number kept. The harness blocks report-file writes by subagents.
> - **Run:** 02:39Z–02:57Z, about 48 CPU-min.
> - **Files:** FROZEN_PREDICTIONS.md (written 02:56:37Z; commit-hash placeholder), `band.py`, `k2_decide.py`, `mstar.py`, `p1_run.py`, `runs_*.jsonl`, `v0_selftest.json`, `a1_results.json`, `a2_genotypes.json`, `a3_rule_props.json`.

## Answer
- **FROZEN_PREDICTIONS.md now exists.**
- **M\* predicts single-byte morph founders are strongly more productive (H-SUPER).**

  | quantity | 44→AC | 37→81 | founder F |
  |---|---|---|---|
  | R1 | 0.269 | 0.296 | 0.046 (about 6x lower) |
  | unconditional P(B_xk ≥ 163) | 0.21 | 0.26 | 0.009 |

  The C3+AC founder is predicted to run away in about 74% of runs.
- **K2 kills F\* sharply if the world is H-NEAR** (world R1 ≈ 0.08): exclusion probability ≥ 0.97 at n = 64 and ≥ 0.9999 at n = 128.
- **R3 is only weakly testable for two arms.** For F and 43→C3 the band admits anything, because FREE's 256-cap stop splits C− and C+.
- **K2 cannot see the K4 anomaly.** The world's founder 4/4 lies inside the C+ R3 band.

## Self-test
- `mstar.run` rebinds `ffield.G7` around a single `w22.run2` call. FREE / BANK / CARRY, mutation on, T = 300, stop on xk. No source edits.
- With the stock founder it reproduces W2-22 FREE exactly: 5/5 seeds, full per-epoch trajectories.
- Implant bytes are asserted (44 EC, 37 A5, 43 C1). The implant changes outcomes, and G7 is restored afterwards.

## Results
800 fresh seeds (39_390_000 + 0..799, shared across arms). Jeffreys 95% CIs.

| genotype | R1 C− | R1 C+ | R2 | R3 C− | R3 C+ |
|---|---|---|---|---|---|
| F | 0.046 [0.033, 0.063] | 0.079 | 0.040 | 7/37 = 0.19 | 29/37 = 0.78 |
| 44→AC | 0.269 [0.239, 0.300] | 0.280 | 0.253 | 0.80 | 0.93 |
| 37→81 | 0.296 [0.265, 0.329] | 0.308 | 0.279 | 0.86 | 0.92 |
| 43→C3 | 0.336 [0.304, 0.370] | 0.461 | 0.336 | 0.11 | 0.99 |
| C3+AC | 0.761 [0.731, 0.790] | 0.763 | 0.761 | 0.975 | 1.00 |

- The founder matches W2-22 FREE (37/800 vs 48/1200, p = 0.50).
- The world's historical 4/128 lies inside the founder band.
- B = B_xk in all 4,000 FREE runs.

## Bands
**Method.** Beta-binomial predictive bands, with censoring resolved against the kill: the band runs from the C− low to the C+ high. R3 is evaluated at the world's own m.

| genotype | n = 64: R1 / R3 | n = 128: R1 / R3 | n = 256: R1 / R3 |
|---|---|---|---|
| F | 0–10 / any | 2–17 / any | 5–31 / any |
| AC | 10–25 / 10–17 | 24–47 / 22–34 | 53–88 / 47–68 |
| 81 | 12–27 / 13–19 | 27–51 / 28–38 | 60–96 / 58–75 |
| C3 | 14–38 / any | 32–71 / 1–43 | 69–136 / 4–86 |
| C3+AC | 42–55 / 45–49 | 87–107 / 91–97 | 179–210 / 184–195 |

**False-kill rates at n = 128.**
- Per arm: 0.02–0.06.
- Two mandatory arms: about 0.10.
- Four arms: about 0.19.
- These are declared, not corrected.

**Frozen decision rule (`k2_decide.py`).**
1. **Positive control.** The founder arm's B ≥ 27 count must lie within the band derived from 4/128 (0–6 at n = 64, 0–11 at 128, 1–21 at 256). Otherwise the result is VOID.
2. **OUTSIDE.** A morph arm is OUTSIDE if its R1 count falls outside the hull, or its R3 count falls outside the R3 hull at its own m.
3. **Verdict.**
   - Any morph arm OUTSIDE → K2 KILLED.
   - If the founder arm is also OUTSIDE → the kill is marked "not morph-specific" and read as K4 residue.
   - Otherwise → PASSED-AT-BAND, scored separately from the equivalence tolerances.

## Adversarial round
1. **M\* can generate morph-driven persistence.**
   - Implanted morphs persist.
   - De novo morphs also arise: 2 of the 7 founder-arm B_xk ≥ 163 runs were swept by a de novo 44→AC, and one AC run acquired C3.
   - The other 5 founder runaways carry no morph.
2. **BANK erases the residue by construction**, so a K2 kill could be either residue or morph. The founder arm separates the two only partly.
3. **The 256 cap makes R3 untestable for F and C3.** Fixing this needs an uncapped M\*.
4. **Amplification.** A per-call gain of about 6% becomes a 6x R1 ratio near criticality. K2 is therefore a sharp test, and the bank's realism dominates the error budget.
5. **Multiplicity** is declared (see the false-kill rates above).
6. **Shared seeds** do not bias the marginals.
7. **The world's B_xk logger** must be validated before scoring.

## Ledger entry (W2-39)
- **Inference.** M\* predicts H-SUPER for single-byte morphs. A world result of H-NEAR (morph R1 ≤ about 0.08) would kill F\* at any n ≥ 64.
- **Confidence.** High for the estimates. Medium that the bands are fit for purpose: R3 is uninformative for F and C3, and the family-wise false-kill rate is 0.1–0.19.
- **Strongest objection.** BANK has no residue, so K2 cannot cleanly separate a morph effect from K4.
- **Next.**
  1. An uncapped M\* variant.
  2. Authorize Experiment 1 at n = 128 with arms F, AC and 81.
  3. Count de novo AC in the world's founder runaways.
  4. A seed-matched K4 run.
