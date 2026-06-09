# Battery Stress Test Prompt
## Purpose: Generate 5 problems with KNOWN answers that test whether our F1-F20 battery is correctly calibrated
## Copy/paste this into ChatGPT, Gemini, DeepSeek, or Claude

---

## THE PROMPT:

We have built a 20-test falsification battery for an automated mathematical instrument. We need you to design 5 specific stress tests — problems where YOU know the correct answer — that will expose calibration weaknesses in our battery.

**Our battery (F1-F20):**

| Test | What it does | Threshold |
|------|-------------|-----------|
| F1 | Permutation null (10K shuffles) | p < 0.05 |
| F2 | Subset stability (5× random 50% splits) | All splits consistent |
| F3 | Effect size gate | Cohen's d > 0.2 or r > 0.1 |
| F4 | Confound sweep | Survives controlling for identified confound |
| F5 | Alternative normalization | Sign doesn't flip under log/rank/z-score |
| F6 | Base rate / Bonferroni correction | p survives multiple comparison |
| F7 | Monotonic dose-response | More X = more Y monotonically |
| F8 | Direction consistency | Same sign in all subgroups |
| F9 | Simpler explanation check | Not explained by a simpler model |
| F10 | Outlier sensitivity | Survives removing top/bottom 5% |
| F11 | Cross-validation | Train on half, predict on half |
| F12 | Partial correlation | Survives removing obvious confounds |
| F13 | Growth rate filter | Not just polynomial growth correlation |
| F14 | Phase shift test | Correlation decays when index shifted |
| F15 | Log-normal calibration | Observed M4/M2² deviates from log-normal prediction |
| F16 | Equivalence test (TOST) | Predicted value inside 90% CI within ±margin |
| F17 | Confound sensitivity sweep | Enrichment drops < 50% after stratifying by confound |
| F18 | Subset stability (statistic) | CV < 0.05 across 100 random 80% subsets |
| F19 | Generative replay | Real statistic within 2σ of synthetic ensemble |
| F20 | Representation invariance | CV < 0.1 across raw/log/sqrt/rank/z-score transforms |

**What we've learned about the battery so far:**

1. F20 kills M4/M2² for ALL distributions (even known ones like exponential). This is correct behavior — M4/M2² IS representation-dependent. But it means F20's threshold may be too aggressive for statistics that are inherently representation-sensitive.

2. F19 returns MODEL_PARTIAL for correctly-specified models (exponential with exponential generator) because the KS component on a single synthetic sample is noisy. The z-score component works fine.

3. F15 was redesigned from v1 (binary log-collapse threshold) to v2 (compare observed vs log-normal prediction). The v2 version correctly identifies distributions that deviate from log-normality.

4. F16 uses TOST equivalence testing. At small sample sizes, the CI is wide and gives false INCONCLUSIVE. At large sample sizes, it correctly distinguishes true matches from near-misses.

5. We have not yet stress-tested F1-F14 (Charon's original battery) against adversarial inputs.

**What we need from you:**

Design exactly 5 problems. For each problem:

1. **Specify the data** — provide the actual numbers, or a precise generation procedure we can run in Python. No ambiguity. We need to be able to reproduce your test case exactly.

2. **Specify the claim** — what hypothesis the battery should be testing (e.g., "these two groups have different means" or "this distribution matches Poisson" or "this enrichment is real").

3. **Specify the ground truth** — YOU know whether the claim is TRUE or FALSE. Tell us which.

4. **Specify which battery tests should catch it** — which of F1-F20 should correctly identify the truth, and which might fail.

5. **Specify the calibration lesson** — what does this test teach us about our battery's thresholds or design?

**The 5 tests should cover these failure modes:**

- **Test 1: A TRUE finding that a poorly-calibrated battery might KILL.** (Tests whether our battery is too aggressive — false negatives)
- **Test 2: A FALSE finding that passes most tests but should be caught by ONE specific test.** (Tests whether each test is pulling its weight)
- **Test 3: A finding that is TRUE in one representation and FALSE in another.** (Tests F20 calibration — when should representation dependence be a kill vs. informative?)
- **Test 4: A confounded finding where the confound is subtle and non-obvious.** (Tests F4/F12/F17 — can the battery find hidden confounds?)
- **Test 5: A finding where the generative model is slightly wrong but the conclusion is still valid.** (Tests F19 — when should model mismatch be a kill vs. a refinement?)

**Format each test as:**

```
### Test N: [Name]
**Data generation:** [exact Python code or explicit numbers]
**Claim:** [precise hypothesis]
**Ground truth:** TRUE / FALSE / CONDITIONAL
**Expected battery behavior:** [which tests pass, which fail, why]
**Calibration lesson:** [what this teaches about thresholds]
```

We will run all 5 through our F1-F20 battery and report back the results. Your job is to design tests that will expose weaknesses we haven't found yet.
