# W2-45: out-of-sample test of BASE 7ae3 early-warning observables (directive item B)

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Written:** 2026-10-01T03:06:31Z. Under 1 CPU-min. W2-37 files were used only after both arms logged DONE.
> - **Files:** `PREREG.md` (03:03:43Z, before any scoring), `a1_score.py/.json` (the result the rule applies to), `a2_strata.py/.json` (post-hoc, descriptive).

## Answer
1. **EW-1 and EW-1b do not hold up out of sample as runaway warnings.**
   - On 600 FULL (world) seeds they catch 7–8 of the 8 B_xk runaways.
   - They also fire on **all 13 intermediate lineages** (B 27–162), which X-TICKET did not contain. That puts the false-alarm rate at 13/592 = 0.022 or more.
   - Pre-registered verdict: **UNRESOLVED (data-limited)**. Hit 0.875–1.0, false alarm 0.022–0.135, PPV ≤ 0.35. It would PASS only if 4 or fewer of the 66 unknown small runs fire.
   - **Within lineages that reach 27 births, EW-1 has no discrimination: 13/13 intermediates fire.**
   - W2-2's in-sample 0/124 false alarms rested on X-TICKET having 0 intermediates.
2. **EW-2 (B5 ≥ 4) fails.**
3. **EW-1 and EW-1b fail in all four BANK model arms.** Hit 0.8–1.0, false alarm 5.5–9%. They measure generic fast lineage growth, not a world signature.
4. **The pre-registered EW-N** (a side-0 converter or C3 present by epoch 20, among the 22 B ≥ 27 runs) **fails as predicted**: 6/8 runaways caught, but 7/14 false alarms.
5. **The "empty gap" does not replicate.**
   - FULL has 13/600 = 2.2% intermediates [1.3, 3.7]%, matching W2-2's single-law prediction of 2.4%. X-TICKET had 0/128 (P = 0.06 at the FULL rate).
   - The runaway "excess" persists: 1.5% vs the law's 0.03%.

## 1. What the data contain

| source | per-epoch births? | contents |
|---|---|---|
| W2-29 runs_FULL (600) | **no** | B, Bxk, kin, epochs, stop, maxA, depth_f, depth_world, n_genomes |
| W2-29 genomes_FULL (22 runs with B ≥ 27) | partial | first-epoch bounds per genome |
| W2-22 / W2-37 BANK | yes, when maxA ≥ 10 | (N, A, B, Bxk) trajectories |

**How alarms were assigned:**
- **Certain negatives:** B below the observable's threshold, or extinct by epoch 10.
- **Inferred negatives:** frozen runs whose last birth was at epoch ≤ 10. This rule had 0 violations in 326 BANK runs and held for 9/9 FULL runs.
- **Unknown:** everything else ("?"), scored both ways.

**Runaway definitions:**
- B_xk ≥ 163: 8 runs.
- B ≥ 163: 9 runs. The extra run is seed 1194 (B 209, Bxk 140).

EW-3, EW-5 and EW-6 are not computable from these data. EW-4 is a necessary condition for a runaway, and it holds 8/8 and 9/9.

## 2. FULL scores (n = 600; ranges run from "unknowns don't fire" to "unknowns fire")

| EW | target | hit | false alarm | PPV | unknowns (runaways among them) | verdict |
|---|---|---|---|---|---|---|
| EW-1 | xk | 7/8 → 8/8 | 0.022 [.013, .037] → 0.135 | 0.35 → 0.09 | 68 (1) | **UNRESOLVED** |
| EW-1b | xk | 7/8 → 8/8 | 0.022 → 0.142 | 0.35 → 0.09 | 72 (1) | **UNRESOLVED** |
| EW-2 | xk | 4/8 → 7/8 | 0.019 → 0.237 | 0.27 → 0.05 | 132 (3) | **FAIL** |
| EW-1 / 1b | B | 8/9 → 9/9 | 0.020 → 0.140 | | 68 / 72 | UNRESOLVED |
| EW-2 | B | 5/9 → 8/9 | 0.017 → 0.235 | | 132 | FAIL |

**Where EW-1 false alarms fire:**

| population | EW-1 fires |
|---|---|
| FULL intermediates | 13/13 |
| FULL, B < 27 | 0 known, 66 unknown |
| X-TICKET in-sample (B < 27, B ≥ 3, alive past epoch 10) | 0/27 |
| comparable BANK small runs | 77/216 = 0.36 |

The single unknown runaway is seed 1303.

## 3. Model processes (all FAIL; FREE scored C−, C+ also fails)

| arm | runaways (xk) | EW-1 hit / FA | EW-1b hit / FA | EW-2 hit / FA | intermediates firing EW-1 |
|---|---|---|---|---|---|
| W2-22 FIELD BANK | 5 | 5/5 / 0.069–0.091 | 4/5 / 0.067–0.089 | 2/5 / 0.08–0.17 | 23/24 |
| W2-37 FIELD BANK | 6 | 6/6 / 0.071–0.088 | 6/6 / 0.064–0.081 | 5/6 / 0.09–0.17 | 15/15 |
| W2-22 FREE BANK | 10 | 9/10 / 0.061–0.074 | 10/10 / 0.055–0.071 | 7/10 / 0.08–0.18 | 36/38 |
| W2-37 FREE BANK | 10 | 10/10 / 0.050–0.073 | 10/10 / 0.046–0.071 | 7/10 / 0.07–0.14 | 36/40 |

## 4. EW-N (pre-registered; FULL runs with B ≥ 27, n = 22)

| variant | hit (xk) | FA | PPV | verdict |
|---|---|---|---|---|
| **EW-N** (side-0 or C3 by epoch 20) | 6/8 | 7/14 | 0.46 | **FAIL** |
| side-0 only | 5/8 | 6/14 | 0.45 | FAIL |
| C3 only | 1/8 | 1/14 | 0.50 | FAIL |
| ring definition | 6/8 | 6/14 | 0.50 | FAIL |
| by epoch 15 / by epoch 30 | 5/8 / 7/8 | 6/14 / 7/14 | | FAIL |
| EW-N ∧ EW-1b | 5/8 | 6/14 | | FAIL |
| EW-1b (same stratum) | 7/7 | 13/13 | 0.35 | FAIL |

Converters appear early in both outcomes: runaways at epochs 4–16, intermediates at 4–18 (plus C3 at epoch 2 in seed 1427).

## Adversarial points
1. **Intermediates are not frozen-stop artefacts.** X-TICKET never revives after a 100-epoch gap, and 4 intermediates reached the horizon uncensored.
2. **FULL is bit-exact world.** But X-TICKET's 0/128 vs FULL's 13/600 gives p = 0.08: either X-TICKET was a lucky draw or the cells differ subtly.
3. **UNRESOLVED could still become PASS.** Even then, PPV ≤ 0.35 and there is no discrimination among lineages that reach 27.
4. **Imputation is tight** (≤ 3 births of slack) in 20 of 22 runs.
5. **EW-N was not fully blind:** the composition was known, which was disclosed. A FAIL was predicted.
6. **8 runaways** gives a hit-rate interval of about 0.53–1.0. The 13/13 is the robust part.

## Ledger entry (W2-45)
- **Inference:**
  - EW-1 and EW-1b measure early growth. This is necessary but not specific: it separates "large" from "small", not "runaway" from "intermediate".
  - The signal is generic to branching processes.
  - Genotype presence by epoch 20 does not discriminate.
  - The empty gap does not replicate in FULL.
- **Confidence:**
  - high: no discrimination among lineages ≥ 27, and FAIL in the models;
  - medium: the gap non-replication;
  - low: the final FULL verdict.
- **Next:**
  1. Replay the 66–70 unknown seeds with trajectory logging (about 5 CPU-min).
  2. A pre-registered intermediate-vs-runaway discriminator on a trajectory-logging FULL run of about 2,000 seeds.
  3. Revisit W2-2's second regime using the FULL size distribution.
