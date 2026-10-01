# W2-12: are implanted 7ae3 founders independent lottery tickets?

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **Scripts and outputs:** `build_table.py` → `run_table.json`, `table_summary.json`; `models.py` → `models.json`, `models.log`; `extra.py` → `extra.json`; `kin_hijack.py` → `kin_hijack.json`; `kin_hijack_atomic.py` → `kin_hijack_atomic.json`; `plugin_baseline_check.txt`.
> - **How it was run:** about 25 CPU-min (one Beta fit was aborted and rerun). No world run, no git writes.

## Answer
**The founders behave as independent tickets** (splice off, BASE).

The k = 4 excess at depth ≥ 5 is not superadditivity, not batch heterogeneity, and not specific to one endpoint. It is a plug-in artifact combined with one low k = 1 arm (C-CRITICAL-MASS).
- X-DOSE-CURVE's CLEAN_NULL stands.
- The D-12 retraction stands.

## 1. The table
Scope: 7ae3, splice off, BASE, tier M, 2000 epochs, nominal rates.

- **k = 1:** 798 runs in 11 disjoint seed blocks. This is Dossier A's 630 plus C-NORECOMB splice-off (24), X-ATOMIC BASE (64) and C-ATOMIC C1 BASE (80).
  - Depth ≥ 5: 89 (0.1115). Depth ≥ 20: 27 (0.0338).
- **Dose arms (depth ≥ 5):**

  | arm | k = 1 | k = 2 | k = 4 | k = 8 |
  |---|---|---|---|---|
  | X-DOSE-CURVE | 6/64 | 20/64 | 25/64 | 44/64 |
  | X-CRITICAL-MASS | 8/64 | | 32/64 | |
  | C-CRITICAL-MASS | 5/80 | | 41/80 | |

- **Code:** unchanged since 09-24 07:05 (cfe635933), before every experiment in the table.

## 2. Models
Complementary log-log: −log(1 − P) = exp(a_b)·k^β. Independence means β = 1.

**Depth ≥ 5**

| test | result |
|---|---|
| common p1 vs a saturated model | p = 0.31 (joint p1 = 0.1315) |
| block heterogeneity in p1 | p = 0.64 (random-effect SD → 0; Beta collapses) |
| β, pooled p1 | 1.13 [0.98, 1.29], p = 0.095 |
| β, block p1 | 1.18 [0.95, 1.44], p = 0.13 |
| pairwise interaction | p = 0.34 |

**Depth ≥ 20**

| test | result |
|---|---|
| common p1 | p = 0.56 |
| heterogeneity | p = 0.80 |
| β, pooled p1 | 1.10, p = 0.45 |
| β, block p1 | 1.26, p = 0.23 |

**Leave-one-experiment-out cross-validation (depth ≥ 5).** Independence scores best:

| model | new batch | k = 1 given |
|---|---|---|
| independence | −505.8 | −225.0 |
| superadditive | −508.9 | −229.0 |
| plug-in | | −245 |

## 3. Where the k = 4 excess comes from
1. **Plug-in artifact.**
   - 98/208 observed vs 76 expected (p = 0.0013) treats p1 as exact and looks only at k = 4. With all 798 runs the same calculation gives p = 0.0034.
   - W2-5's `plugin_baseline` check says PLUGIN_BASELINE_ARTIFACT.
   - What genuinely remains is pooled p1 0.1115 vs joint 0.1315, i.e. β = 1.13 (p = 0.095).
2. **Not batch heterogeneity.**
   - The k = 1 blocks are homogeneous: exact p = 0.53 at depth ≥ 5 and 0.47 at depth ≥ 20, with rates 0.078–0.21.
   - There is no seed-level effect: within-seed permutation p ≥ 0.16, and paired arms give Fisher p ≥ 0.24.
3. **Carried by one arm.**
   - C-CRITICAL-MASS alone rejects independence (p = 0.014).
   - Its k = 4 bands are on its own fit: 39/26/15 observed vs 44/22.5/13.5 expected.
   - Its k = 1 arm is what is low: 5/80 vs about 11 expected.
   - Drop C-CRITICAL-MASS: β = 1.06 (p = 0.64). Drop X-DOSE-CURVE: β = 1.45 (p = 0.027).
   - The three blocks' βs (1.74, 1.19, 1.02) do not differ (p = 0.14).
4. **Not endpoint-specific.**
   - Over 17 thresholds from 1 to 300, β ranges 0.86–1.29 and no p < 0.10.
   - Pooled k = 4 bands match their own fits: 110/64/34 observed vs 113.5/63.9/30.6 expected. There is no mid-band excess.

**Verdict.** Independent tickets, with p1 ≈ 0.13 (depth ≥ 5) and ≈ 0.04 (depth ≥ 20). Mild superadditivity, β up to about 1.3, is not excluded. Dossier A's W2 nuance should be replaced.

## 4. Static kin-pairing probe (`p11.interact`, stock z8, 400 trials per cell)

**Half lost:**

| partner | side 0 | side 1 |
|---|---|---|
| random | 54% | 9–12% |
| exact copy | 0/400 | 0/400 |
| 1-operand mutant | 0% | ≤ 0.25% |
| 2-operand mutant | 2–4% | 2% |
| 4-operand mutant | 9–11% | 8–10% |

- **Bytes changed per call:**

  | partner | side 0 | side 1 |
  |---|---|---|
  | random | 33.6 | 5.3 (matches X-STALL-F0's 5.55) |
  | copy | 0.4 | 0.5 |

- **Conversion of a random partner:** side 1, 354/400; side 0, 2/400.
- **Under ATOMIC,** 190 of 222 side-0 hijack losses count as accepted replication events. Hijack protection therefore applies under both BASE and ATOMIC; erosion protection only under BASE.
- **Why this does not show up as superadditivity:**
  - Early lineage size is 1.1–2.7 (X-TICKET), so at k = 4 kin are only about 1–3% of partners.
  - That predicts β ≈ 1.02–1.05, far below the ~30% per-founder boost the plug-in result would require.
  - The k = 8 arm of X-DOSE-CURVE sits on its independence line: 44 vs 43.3.

## 5. Side finding: heterogeneity appears only with the splice on

| block | k = 1 rate |
|---|---|
| C9 | 4/16 |
| C-NORECOMB | 5/24 |
| C-RUNAWAY | 4/150 |
| X-H2-7AE3 | 0/16 |
| X-H2-NORECOMB | 0/16 |

- Exact p = 0.0005 with C9, 0.006 without.
- This is unexplained and does not affect the splice-off question.

## 6. Adversarial rounds
- **"The joint fit hides the effect."** Fitting a common p1 is the correct null.
- **"Pooling assumes homogeneity."** Homogeneity was tested and holds.
- **"Dropping C-CRITICAL-MASS is cherry-picking."** Granted. The conclusion is therefore "no strong effect", not "β = 1".
- **"Cross-validation favours the smaller model."** True, which is why the CI is stated alongside it.
- **Threshold scan:** clean.
- **Kin route:** real statically, but below what these data can resolve.

## Ledger entry (W2-12)
- **Result:**
  - A common p1 fits (p = 0.31 / 0.56), with no heterogeneity (p = 0.64).
  - β = 1.13 [0.98, 1.29] (p = 0.095), and cross-validation prefers independence.
  - The dossier's p = 0.0013 is a plug-in artifact. The residual tension is C-CRITICAL-MASS's k = 1 arm.
  - Kin pairing abolishes hijack (0/400 vs 54%) and about 90% of erosion statically, but predicts only β ≈ 1.02–1.05.
  - Splice-on heterogeneity: p = 0.006.
- **Confidence:**
  - high: no splice-off batch effect and no strong superadditivity;
  - moderate: β < 1.3;
  - low: the size of the kin effect.
- **Strongest objection:** β ≈ 1.2–1.3 is not excluded, and the only frozen two-dose block rejects independence (p = 0.014).
- **Next questions:**
  1. An ATOMIC k = 1 vs 8 test, to separate the hijack route from the erosion route.
  2. Instrument kin encounters in k = 4 replays.
  3. A powered k = 1 vs 8 test (about 300 seeds per arm).
  4. Audit the splice-on harness.
