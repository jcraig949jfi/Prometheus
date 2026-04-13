# Reviewer Questions and Answers
## 2026-04-13

---

## Question 1: How sensitive is the 14% rank-2 asymptote to conductor range?

**Answer: The asymptote is NOT stable. It drifts upward with conductor range.**

| Max conductor | Fitted saturation L | Midpoint |
|--------------|-------------------|----------|
| 50,000 | 10.2% | 7,938 |
| 100,000 | 11.9% | 11,285 |
| 200,000 | 12.6% | 13,257 |
| 300,000 | 13.0% | 14,650 |
| 400,000 | 13.4% | 15,967 |
| 500,000 | 13.7% | 16,879 |

The asymptote has risen from 10.2% to 13.7% as we extend the conductor range. It's still climbing. This means the logistic model fits the current data well (R^2 = 0.996) but the "saturation" level has not converged. We cannot confidently say the true asymptote is 13.7% -- it could settle at 15%, or 18%, or higher.

However, the growth IS decelerating. The slope drops from 0.0466 per decade in the early half to 0.0450 in the late half (ratio 0.97x). The second derivative is negative at both early and late conductor ranges. So the rank-2 fraction is genuinely slowing down -- we just don't know where it stops.

**Honest conclusion**: The logistic is the best-fitting model, but the asymptote is a moving target. We should NOT claim "saturates at 13.7%." We should say: "growth is decelerating (confirmed by negative second derivative) but the saturation level has not converged within our conductor range. Extended data above N = 10^6 is needed."

---

## Question 2: How quiet is the Sha channel? Is it carried by a thin tail?

**Answer: Yes. The Sha channel is carried almost entirely by the Sha = 1 vs Sha > 1 binary split.**

The Sha distribution in our rank-0 zero dataset:

| Sha | Count | % |
|-----|-------|---|
| 1 | 14,576 | 93.4% |
| 4 | 728 | 4.7% |
| 9 | 175 | 1.1% |
| 16 | 77 | 0.5% |
| 25+ | 43 | 0.3% |

Key results:

- **R^2 = 0.050 on all curves** (GB regressor on log(Sha))
- **R^2 = -0.061 on Sha > 1 only** -- the model has NO predictive power within the nontrivial tail
- **AUC = 0.658 for Sha=1 vs Sha>1 binary classification** -- modestly above chance (0.5)

The reviewer's suspicion is confirmed: the R^2 = 0.067 reported in the paper is driven by the binary split between Sha = 1 (93.4% of curves) and Sha > 1 (6.6%). Within the Sha > 1 subset, spectral features cannot distinguish Sha = 4 from Sha = 9 from Sha = 16.

The real signal is: **spectral features weakly predict WHETHER Sha is nontrivial (AUC = 0.658), but NOT how large nontrivial Sha is.** The strongest individual feature is max_gap (rho = -0.097): curves with larger maximum zero gap are slightly more likely to have Sha = 1.

**Correction to paper**: The Sha channel should be described as "a weak binary classifier (Sha = 1 vs Sha > 1) with AUC = 0.66, not a continuous predictor." The R^2 = 0.067 overstates what the model actually learns.

---

## Question 3: Are the three channels truly orthogonal?

**Answer: The TARGETS are orthogonal, but the PREDICTIONS are not.**

### Target-level orthogonality (mutual information)

| Pair | MI |
|------|-----|
| MI(rank, class_size) | 0.0216 |
| MI(rank, Sha) | 0.0000 |
| MI(class_size, Sha) | 0.0000 |

The arithmetic invariants themselves are nearly independent. Rank and Sha have literally zero mutual information. Rank and class_size have a tiny amount (0.022 nats).

### Prediction-level orthogonality (Spearman rho between model outputs)

| Pair | rho |
|------|------|
| rho(rank_pred, cs_pred) | **-0.448** |
| rho(rank_pred, sha_pred) | 0.221 |
| rho(cs_pred, sha_pred) | -0.269 |

The predictions are significantly correlated. The rank prediction and class size prediction correlate at rho = -0.45. This means the models are NOT using fully independent spectral features -- there is substantial overlap in what parts of the spectrum they rely on.

### The critical test: does rank prediction help class size prediction?

No. Adding the rank prediction to the class size model gives R^2 = 0.219, compared to R^2 = 0.222 without it (a change of -0.003). Even though the predictions are correlated, the rank channel adds zero new information about class size. The correlation between predictions reflects shared sensitivity to gamma_1 and zero variance, not genuine information leakage.

### Honest conclusion

The paper's claim of "three independent spectral channels" needs qualification:

- The **targets** (rank, class_size, Sha) are genuinely independent (MI ~ 0)
- The **spectral features** used by each model overlap substantially (prediction rho up to 0.45)
- But the **information content** is independent: adding one channel's output doesn't improve another channel's predictions

The correct statement is: "Three arithmetic invariants are encoded in partially overlapping but informationally independent spectral features." The channels share spectral real estate but carry non-redundant arithmetic information.

---

## Summary of Corrections

1. **Goldfeld asymptote**: Change "saturates at 13.7%" to "growth is decelerating but asymptote has not converged within conductor 500K."
2. **Sha channel**: Change "R^2 = 0.067 continuous predictor" to "AUC = 0.66 binary classifier (Sha=1 vs Sha>1); no predictive power within the nontrivial tail."
3. **Channel orthogonality**: Change "three independent channels" to "three informationally independent channels using partially overlapping spectral features."

All three corrections make the claims weaker but more honest. The core finding -- that zeros encode arithmetic -- is not affected.

---

*Tested: 2026-04-13*
*Results: harmonia/results/reviewer_questions.json*
