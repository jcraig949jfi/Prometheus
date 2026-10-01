# W2-13: chain length vs evolved epistasis (U1)

> Saved by Nestor from the worker's returned text, condensed with all numbers kept. The harness blocks report-file writes by subagents.
> - **How it was run:** static only. Single-genome VM screens, about 35 CPU-min, `python -B`.
> - **Scripts and JSON (this folder):** `search_hits.py`, `pairs_hits.py`, `lengths.py`, `analysis.py`, `robustness.py`, `rawgap.py`, plus their JSON and logs.

## Answer
**At matched executed pre-copy chain length, evolved copiers and never-evolved random-hit copiers show the same rate of strict synthetic lethality.**
- T3 (chain length) is sufficient to explain the gap.
- T4(c′) (generic evolved epistasis) is not supported.
- The power is limited, so this does not show that T4(c′) is absent.

## Method
1. **Random hits.** 180,000 uniform random 64-byte genomes, run through the exact S3 COMPETENT screen (cell 7ae3, dense VM).
   - A pre-filter sent genomes containing a copy op (E5, E7, ED B0 or ED B8) to the full screen: 39.6% of them.
   - Pre-filter check: 0 misses in 10,871 rejected genomes that were also fully screened.
   - Result: **33 hits, about 1.8e-4**. Together with 3 hits from C2, RAND = 36 genomes; 33 of them have dispensable pairs.
2. **Pair screen.** The identical S3/C2 path:
   - 3 single-knockout draws at all 64 positions;
   - up to 100 dispensable pairs per genome;
   - strict lethal = lost in ≥ 2 of 3 joint draws, confirmed by the S3R re-assay.
3. **Chain length.**
   - L_pre = distinct genome positions executed before the main copy op, on the instrumented dense VM. Median over 5 victim seeds.
   - Also recorded: L_exec (all executed positions) and D_pre (dynamic instruction count before the copy).
4. **Comparison groups.**
   - EVO_SD = the 48 state-dependent comparators from S3.
   - EVO_SF = the 48 panel genomes from S3.
   - PLANT = the 12 planted genomes from C2.
5. **Regression.** Strict rate = a + b·X + c·EVO, weighted by each genome's null-0 pairs.
   - Also fitted with an X×EVO term and as a binomial GLM.
   - 95% CIs: 4,000-resample genome bootstrap.
   - p-values: Freedman-Lane permutation, and label permutation within X quintiles.

## Results

**Pooled strict rates**

| group | genomes | null-0 pairs | strict lethal | rate | median L_pre |
|---|---|---|---|---|---|
| EVO_SD | 47 | 2,722 | 101 | 3.71% | 39.5 |
| EVO_SF | 47 | 3,495 | 131 | 3.75% | 48 |
| RAND | 33 | 2,371 | 55 | 2.32% | 21 |
| PLANT | 12 | 1,107 | 5 | 0.45% | 15.5 |

**Raw gap, EVO_SD − RAND:** +1.39 pp, 95% CI [+0.15, +2.69], p = 0.048.

**Adjusted for length (X = L_pre)**
- **c_EVO = +0.27 pp**, 95% CI [−0.90, +1.46]. Freedman-Lane p = 0.83; stratified p = 0.63.
- b = +0.09 pp per executed position, in both groups.
- d (X×EVO) = +0.046 pp per position, CI [−0.044, +0.125].
- GLM odds ratio for EVO: 1.16 [0.82, 1.65].
- Chain length accounts for about 80% of the raw gap (point estimate).

**Binned by L_pre**

| L_pre | EVO_SD rate (genomes) | RAND rate (genomes) |
|---|---|---|
| 0–15 | 0.5% (2) | 0.5% (8) |
| 15–30 | 2.8% (8) | 2.4% (15) |
| 30–45 | 3.3% (21) | 4.3% (5) |
| 45+ | 5.5% (16) | 3.2% (5) |

- **Length-matched** (3 nearest evolved per random hit): 2.08% vs 2.32%.

**Other covariates and contrasts**

| covariate | c_EVO | 95% CI | Freedman-Lane p |
|---|---|---|---|
| L_exec | +0.48 pp | [−0.62, +1.55] | 0.69 |
| D_pre | +0.95 pp | [−0.36, +2.17] | 0.45 |
| frac_both_pre | +0.89 pp | [−0.32, +2.10] | 0.47 (stratified 0.14) |

- The GLM's Wald CIs just exclude an odds ratio of 1 for D_pre (1.48) and frac_both_pre (1.43). They ignore between-genome overdispersion; the genome-level permutation tests are not significant.

| contrast | c | Freedman-Lane p |
|---|---|---|
| all evolved vs RAND | −0.24 pp | 0.82 |
| EVO_SD vs RAND + PLANT | +0.51 pp | 0.63 |
| all vs all | −0.02 pp | 0.98 |

**By pair class**

| pair class | EVO_SD | RAND | PLANT |
|---|---|---|---|
| both positions executed pre-copy | 8.7% | 6.0% | 0 of 26 pairs |
| one position | 2.8% | 4.2% | |
| neither | 0.7% | 0.3% | |

- Mantel-Haenszel OR across classes: 1.08 [0.67, 1.64], p = 0.71. All evolved vs RAND: 0.96.
- In both groups, synthetic lethality sits almost entirely in executed code.

## Adversarial rounds

1. **Are random hits a fair comparator?**
   - They pass the same COMPETENT screen, which is the right control for "evolution beyond the competence filter".
   - But they have shorter chains: only 10 of 33 have L_pre ≥ 30.
   - Common support only (L_pre 15.6–53.8: 38 evolved, 22 random): c = +0.23 pp [−1.10, +1.71], p = 0.87.
   - Leave-one-out moves c only between +0.05 and +0.44 pp.
2. **Is L_pre the right covariate?**
   - Four covariates and the pair-class stratification all agree.
   - L_pre is seed-stable (median spread 0); a single-seed refit gives c = +0.30 pp, p = 0.80.
   - **Objection:** every point estimate is positive (+0.3 to +0.95 pp), and the slope difference is positive in every fit.
3. **Power.**
   - The CI upper bound (+1.47 pp) is about the size of the whole raw gap, so an evolved excess that large cannot be excluded.
   - What the data do support: the raw gap is marginal, and matching on length shrinks it to about 0.2 of itself. That is evidence that **T3 is sufficient**, not proof that T4(c′) is absent.
4. **PLANT.** Its low rate is mostly short chains. The earlier 3.7% vs 0.45% contrast was largely a length confound.

**Prior figure revised:** the random-hit rate of 5.1% (7/136, from 2 genomes) becomes 2.3% with 33 genomes.

## Ledger entry (W2-13)
- **Question.** U1: is strict synthetic lethality in evolved copiers T4(c′) evolved organisation, or T3 chain length?
- **Result.**
  - Raw gap +1.39 pp (p = 0.048).
  - Length-adjusted c_EVO = +0.27 pp [−0.90, +1.46], p_FL = 0.83.
  - Matched rates 2.08% vs 2.32%; Mantel-Haenszel OR 1.08.
  - All 4 covariates and all 4 contrasts are null.
  - T3 is sufficient; T4(c′) is not supported.
- **Confidence.** Moderate. The CI upper bound is about the raw gap, and the point estimates are consistently positive.
- **Strongest objection.**
  - Random hits are competence-selected and short, so the overlap above L_pre 30 is thin.
  - A small real evolved component (both-pre pairs 8.7% vs 6.0%) could be hidden.
- **Unresolved.**
  - d > 0 in every fit.
  - The one-pre class is higher in RAND.
  - PLANT's low matched rate.
- **Next.**
  1. A length-stratified search for random hits with L_pre ≥ 35 (about 25 CPU-min).
  2. Pair-level logistic regression with genome random effects.
  3. State-free random hits vs EVO_SF.
  4. Pre-copy sets as the union over seeds.
