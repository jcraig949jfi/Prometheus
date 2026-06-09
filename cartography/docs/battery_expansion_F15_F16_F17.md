# Battery Expansion: F15, F16, F17
## Proposed additions to the falsification battery
## 2026-04-11 — Born from the kill audit of 65 challenges

---

## Context

During a session of 65 rapid-fire challenges, we measured M4/M2^2 moment ratios across 33 distributions, enrichment across 22 grouping variables, and curvature across 9 graph types. Three findings in particular drove excitement:

1. Knot determinant M4/M2^2 = 2.16, close to SU(2) = 2.0
2. Genus-2 conductor M4/M2^2 = 3.01, matching USp(4) = 3.0
3. Enrichment values ranging from 52.6x (electron config) to 0.82x (ST → discriminant)

When we turned the battery on our own results, we discovered that **the moment hierarchy may be an artifact of tail-heaviness**, that **some enrichment values were inflated by confounds**, and that **some "near X" claims fail bootstrap testing**. These three vulnerabilities led to three new battery tests.

---

## F15: Log-Transform Invariance Test

### The Problem It Solves

M4/M2^2 (the kurtosis of the normalized distribution) is sensitive to the tail shape of the distribution. A distribution that looks "special" in raw space (M4/M2^2 = 2.16, near the Catalan number 2.0) may be completely generic after log-transformation.

### The Discovery

We measured M4/M2^2 across 33 distributions and built a "constraint spectrum" ranging from 1.0 (degenerate) to 69.6 (particle masses). The narrative was that this hierarchy measures "algebraic constraint depth" — more constrained systems have lower M4/M2^2.

Then we applied log-transform:

| Distribution | Raw M4/M2^2 | Log M4/M2^2 |
|-------------|-------------|-------------|
| Knot determinants | 2.156 | 1.112 |
| Genus-2 conductors | 3.008 | 1.047 |

Both collapse to ~1.0 after log-transform. The "structure" was entirely in the tail shape of the distribution, not in some deep algebraic property.

### Why This Happens

Any distribution of positive integers can be decomposed as:
- A **shape** component (log-space kurtosis)
- A **scale** component (mean and variance)

M4/M2^2 in raw space conflates these. A distribution that is approximately log-normal will have M4/M2^2 determined entirely by its log-space variance σ:

```
M4/M2^2 ≈ (e^{4σ²} + 2e^{3σ²}) / (e^{2σ²} + 1)²
```

For σ ≈ 0.7 (typical for conductors), this gives M4/M2^2 ≈ 3.0. For σ ≈ 0.5 (typical for knot determinants), M4/M2^2 ≈ 2.2. The "Catalan numbers" are just specific values of the log-normal kurtosis formula.

### The Test

```python
def F15_log_transform_invariance(values, claim="structural moment match"):
    """
    Test whether a moment ratio claim survives log-transformation.
    
    If log-transformed M4/M2^2 collapses to near 1.0, the raw ratio
    is measuring tail heaviness, not algebraic structure.
    
    Returns: (verdict, details)
    """
    values = np.array(values, dtype=float)
    values = values[values > 0]
    
    # Raw ratio
    vn = values / np.mean(values)
    m2 = np.mean(vn**2); m4 = np.mean(vn**4)
    raw_ratio = m4 / m2**2
    
    # Log-transformed ratio
    log_vals = np.log(values)
    ln = log_vals / np.mean(log_vals)
    lm2 = np.mean(ln**2); lm4 = np.mean(ln**4)
    log_ratio = lm4 / lm2**2
    
    # Verdict
    if log_ratio < 1.2:
        verdict = "FAIL"
        detail = (f"Log-transform collapses M4/M2^2 from {raw_ratio:.3f} to "
                  f"{log_ratio:.3f}. The raw ratio measures tail heaviness, "
                  f"not structural constraint.")
    elif log_ratio < 1.5:
        verdict = "WEAK"
        detail = (f"Log-transform reduces M4/M2^2 from {raw_ratio:.3f} to "
                  f"{log_ratio:.3f}. Partial tail artifact.")
    else:
        verdict = "PASS"
        detail = (f"Log-transform preserves structure: {raw_ratio:.3f} → "
                  f"{log_ratio:.3f}. Not a tail artifact.")
    
    return verdict, detail
```

### When to Apply

Apply F15 to ANY claim of the form "M4/M2^2 of distribution X matches/resembles known constant Y." This includes:
- "Knot determinants match SU(2)" → FAIL (log collapses)
- "G2 conductors match USp(4)" → FAIL (log collapses)
- "Prime gaps approach Poisson" → needs testing
- "Crystal formation energy matches Catalan C3" → needs testing

### What It Does NOT Kill

F15 kills the INTERPRETATION ("this matches because of shared algebraic structure") but not the OBSERVATION ("these two distributions have the same raw M4/M2^2"). The observation is still valid — it's just that the explanation is "similar tail shapes" rather than "shared algebraic constraint depth."

A finding can survive F15 failure if there is a THEORETICAL PREDICTION for why the log-space kurtosis takes that specific value. For example, if someone proves that conductors of genus-2 curves must have log-kurtosis σ such that M4/M2^2 = 3.0, then the F15 failure is expected and the finding is still meaningful.

---

## F16: Predicted Value Bootstrap Test

### The Problem It Solves

Researchers (including us) tend to report M4/M2^2 = 2.16 as "matching SU(2) = 2.0" because 2.16 is "close" to 2.0. But "close" is not a statistical statement. How close is close enough?

### The Discovery

Bootstrap analysis of our claims revealed:
- Knot determinant: 2.155 ± 0.033 (95% CI: [2.092, 2.217]). SU(2) = 2.0 is **OUTSIDE** the CI.
- G2 conductor: 3.009 ± 0.012 (95% CI: [2.984, 3.032]). USp(4) = 3.0 is **INSIDE** the CI.

The "match" between knot determinants and SU(2) is a false narrative. They're statistically distinguishable. The match between G2 conductors and USp(4) is genuine.

### The Test

```python
def F16_predicted_value_bootstrap(values, predicted_value, n_bootstrap=1000):
    """
    Test whether M4/M2^2 of a distribution matches a predicted value.
    
    Computes bootstrap 95% CI and checks if the predicted value falls inside.
    
    Returns: (verdict, details)
    """
    values = np.array(values, dtype=float)
    values = values[values > 0]
    rng = np.random.default_rng(42)
    
    ratios = []
    for _ in range(n_bootstrap):
        sample = rng.choice(values, len(values), replace=True)
        sn = sample / np.mean(sample)
        m2 = np.mean(sn**2); m4 = np.mean(sn**4)
        ratios.append(m4 / m2**2)
    
    ratios = np.array(ratios)
    mean_r = np.mean(ratios)
    lo, hi = np.percentile(ratios, [2.5, 97.5])
    
    if lo <= predicted_value <= hi:
        verdict = "PASS"
        detail = (f"Predicted {predicted_value} is INSIDE 95% CI "
                  f"[{lo:.4f}, {hi:.4f}]. Match is statistically exact.")
    else:
        distance = min(abs(predicted_value - lo), abs(predicted_value - hi))
        verdict = "FAIL"
        detail = (f"Predicted {predicted_value} is OUTSIDE 95% CI "
                  f"[{lo:.4f}, {hi:.4f}]. Closest edge is {distance:.4f} away. "
                  f"The 'match' is a false narrative.")
    
    return verdict, detail
```

### When to Apply

Apply F16 to ANY claim of the form "X matches/equals Y" where Y is a known mathematical constant. This includes:
- "M4/M2^2 matches a Catalan number"
- "Enrichment matches Charon's algebraic DNA (8x)"
- "Curvature matches the knot Jones value (-0.37)"
- "Phase coherence matches Charon's rho (0.197)"

Without F16, we cannot distinguish "intriguingly close" from "statistically identical."

### Relationship to F15

F15 and F16 are complementary:
- F15 tests whether the VALUE is meaningful (or a tail artifact)
- F16 tests whether the MATCH is real (or a precision illusion)

A finding needs to survive BOTH to be considered a genuine structural match:
- PASS F15 + PASS F16 = genuine structural match
- FAIL F15 + PASS F16 = the match is exact but the mechanism is tail shape
- PASS F15 + FAIL F16 = the structure is real but the specific match is false
- FAIL F15 + FAIL F16 = nothing meaningful

---

## F17: Confound Detrending Test

### The Problem It Solves

Enrichment measurements compare "within-group similarity" to "between-group similarity." But if the groups differ in a confounding variable (e.g., energy scale, sample size, compositional complexity), the enrichment may be measuring the confound rather than the grouping variable.

### The Discovery

Three of our enrichment claims were inflated by confounds:

| Claim | Original | After confound control | Drop |
|-------|----------|----------------------|------|
| Spectral config enrichment | 16.4x | 11.8x (detrend by element energy) | 28% |
| Tc complexity correlation | r=0.67 | r=0.37 (remove cuprates) | 44% |
| Namespace tactic enrichment | 3.71x | 2.64x (control for module size) | 29% |

All three survived (enrichment > 1.5x, p < 0.001 after control), but the corrected values are 25-45% lower. If we had not checked, we would be reporting inflated numbers.

### The Test

```python
def F17_confound_detrend(values_within, values_across, confound_name,
                          detrended_within, detrended_across):
    """
    Test whether enrichment survives after controlling for a confounding variable.
    
    Compares original enrichment to detrended enrichment.
    Reports the corrected value and flags if drop exceeds 50%.
    
    Returns: (verdict, details)
    """
    orig_enrichment = np.mean(values_across) / np.mean(values_within)
    detrended_enrichment = np.mean(detrended_across) / np.mean(detrended_within)
    
    drop = 1 - detrended_enrichment / orig_enrichment
    
    if detrended_enrichment < 1.1:
        verdict = "FAIL"
        detail = (f"Enrichment collapses from {orig_enrichment:.2f}x to "
                  f"{detrended_enrichment:.2f}x after controlling for {confound_name}. "
                  f"The original enrichment was a confound artifact.")
    elif drop > 0.5:
        verdict = "WEAK"
        detail = (f"Enrichment drops {drop*100:.0f}% from {orig_enrichment:.2f}x to "
                  f"{detrended_enrichment:.2f}x after controlling for {confound_name}. "
                  f"More than half the signal was confounded.")
    else:
        verdict = "PASS"
        detail = (f"Enrichment drops {drop*100:.0f}% from {orig_enrichment:.2f}x to "
                  f"{detrended_enrichment:.2f}x after controlling for {confound_name}. "
                  f"Signal survives confound control.")
    
    return verdict, detail
```

### What Confounds to Check

For each type of enrichment, there's a natural confound:

| Enrichment type | Natural confound |
|----------------|-----------------|
| Spectral (config → energy) | Element energy scale |
| Chemical (composition → Tc) | Dominant material class (cuprates) |
| Mathematical (namespace → complexity) | Module size |
| Arithmetic (Galois → class number) | Field degree |
| Physical (space group → property) | Crystal system |

**Rule:** Always identify the MOST OBVIOUS confound for a given enrichment claim and run F17 against it. If you can't think of a confound, the claim has not been properly scrutinized.

### When to Apply

Apply F17 to ANY enrichment claim before reporting it. The corrected value (after confound control) is the number to report. The original value is the upper bound.

---

## Summary: How These Three Tests Work Together

A robust finding must survive all applicable tests:

```
Claim: "M4/M2^2 of X matches known constant Y, and enrichment of 
grouping G on property P is Z times"

Step 1 — F15 (Log-Transform): Does the moment ratio survive log-transform?
  → If log_ratio < 1.2: the moment match is a tail artifact. 
    The specific value may still be interesting but the "structural 
    constraint" interpretation is dead.

Step 2 — F16 (Bootstrap Match): Is the claimed match statistically exact?
  → Compute 95% CI via 1000 bootstrap samples.
  → If predicted value outside CI: the match is a false narrative.
    Report the actual CI instead.

Step 3 — F17 (Confound Detrend): Is the enrichment inflated?
  → Identify the most obvious confound.
  → Recompute enrichment after stratifying by confound.
  → If drop > 50%: the enrichment was dominated by the confound.
    Report the detrended value.
```

### What This Session's Findings Look Like After Full Battery

| Finding | F15 | F16 | F17 | Revised Status |
|---------|-----|-----|-----|----------------|
| Knot det ≈ SU(2) | FAIL (log→1.1) | FAIL (2.0 outside CI) | N/A | **KILLED as match, survives as observation** |
| G2 cond ≈ USp(4) | FAIL (log→1.0) | PASS (3.0 inside CI) | N/A | **Match is exact but mechanism is tail shape** |
| Config enrichment 16.4x | N/A | N/A | PASS (→11.8x) | **Survives at corrected 11.8x** |
| Tc complexity r=0.67 | N/A | N/A | PASS (→0.37) | **Survives at corrected r=0.37** |
| Namespace enrichment 3.71x | N/A | N/A | PASS (→2.64x) | **Survives at corrected 2.64x** |
| Crystal form energy ≈ C3 | FAIL (log collapses) | Not tested | N/A | **Already killed (C60)** |
| Curvature sign boundary | N/A | Needs CI | N/A | **Needs bootstrap on curvature values** |

### The Meta-Lesson

The kill audit found that ~14% of our wins needed correction or asterisks. This is not a failure of the research — it's the battery working as designed. Charon's principle: "Each kill teaches more than a survivor." The battery's job is murder. F15/F16/F17 add three new weapons.

---

*Proposed: 2026-04-11*
*Born from: 65 challenges, 37 wins, 6 kills, the moment hierarchy collapse*
*Status: Awaiting review by frontier models*

[council responses]
[gemini]

This is a high-caliber audit. If Charon is to be a "genocidal maniac" for hypotheses, his weaponry must be impervious to the most common statistical illusions: **scale artifacts, precision bias, and hidden variables.**

The transition from "intriguingly close" to "statistically indistinguishable" is where the most dangerous "ghost structures" reside. F15–F17 are excellent, but they have specific failure modes in the "high-$N$" regime where Charon typically operates.

Here is a hostile review of your battery expansion.

---

## F15: Log-Transform Invariance Test

### Critique: The "Log-Normal Trap"
F15 correctly identifies that many "algebraic" constants are actually just shadows of the log-normal distribution's dispersion. However, F15 falls short by being **too binary.**

* **The Power-Law Blindspot:** Many physical and topological distributions (like knot invariants) follow power laws rather than log-normal distributions. A log-transform might "kill" a genuine power-law structure because it forces it into a scale-free space where all exponents look similar.
* **The Zero/Negative Problem:** Many Layer 2 results (like curvature or phase coherence) include zero or negative values. $\log(x)$ is undefined here.

### Suggestion: The Box-Cox Generalization
Instead of a simple log-transform, apply a **Box-Cox Transformation** battery. Test if the moment match is stable across a range of $\lambda$ values.

$$y(\lambda) = \begin{cases} \frac{x^\lambda - 1}{\lambda} & \text{if } \lambda \neq 0 \\ \ln(x) & \text{if } \lambda = 0 \end{cases}$$

**Alternative F15 (Structural Stability Test):**
> If the moment ratio $M_4/M_2^2$ is purely structural, it should be an attractor. If perturbing the data via $\lambda \in [-1, 1]$ causes the ratio to wander aimlessly or collapse immediately to 1.0, the "match" is an artifact of the current scale.

---

## F16: Predicted Value Bootstrap Test

### Critique: The "Large N" Precision Trap
F16 is your most rigorous addition, but it faces a mathematical paradox: **The more data Charon collects, the more likely he is to "FAIL" a true match.**

* **The Over-Precision Problem:** With $N = 10^5$, the 95% Confidence Interval (CI) becomes vanishingly small. At that resolution, even tiny, non-structural "noise" in the database (rounding errors in LMFDB, measurement limits in NIST) will push the mean outside the CI. 
* **The "Match" vs. "Truth":** If the true value is $\pi$ but the data is recorded to 4 decimal places, a bootstrap of $10^6$ samples will *correctly* identify that the data does not match $\pi$ exactly, even if $\pi$ is the governing law.

### Suggestion: Equivalence Testing (TOST)
Instead of asking "Is the constant inside the CI?", use **Two One-Sided Tests (TOST)**. Define an "equivalence bound" $\epsilon$ based on the known noise floor of the dataset.

**Alternative F16 (Equivalence Match):**
> Instead of a binary PASS/FAIL on the CI, calculate the **Effect Size of the Deviation ($D$):**
> $$D = \frac{|\mu_{observed} - \text{constant}|}{\sigma_{bootstrap}}$$
> - $D < 2$: Statistical match (current F16).
> - $2 < D < 10$: Structural near-miss (worth investigating for confounds).
> - $D > 10$: Absolute kill.

---

## F17: Confound Detrending Test

### Critique: The "Unknown Unknowns" Problem
F17 is a defense against Simpson’s Paradox. However, its current iteration relies on the researcher to **manually** identify the confound. Charon is an automated instrument; he shouldn't wait for a human to guess that "Field Degree" is the problem.

### Suggestion: Automated Confound Sweep
Charon should automatically cross-reference the grouping variable against all other categorical and scalar variables in the metadata.

**Alternative F17 (Orthogonality Test):**
> For any enrichment claim of Group $G$ on Property $P$, Charon must calculate the **Mutual Information ($I$)** between $G$ and all other available metadata tags $M_i$.
> 1. If $I(G; M_i)$ is high, Charon must automatically run F17 using $M_i$ as the detrending variable.
> 2. **The Residual Enrichment Rule:** Only the enrichment that cannot be explained by the $M_i$ "background" is allowed to be reported as "Algebraic DNA."

---

## Revised Summary: The 3-Stage Massacre

If you implement these "hostile" versions, the Revised Status for your current findings would look even leaner:

| Finding | Revised F15 (Stability) | Revised F16 (Equivalence) | Revised F17 (Auto-Detrend) | Final Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Knot det ≈ SU(2)** | **FAIL** (Collapses) | **FAIL** ($D = 4.7$) | N/A | **Dead.** A tail-shape coincidence. |
| **G2 cond ≈ USp(4)** | **FAIL** (Collapses) | **PASS** ($D = 0.75$) | **FAIL** (Detrend by Conductor range) | **Dead.** The "match" is a log-normal artifact. |
| **Config enrichment** | N/A | N/A | **PASS** (Still 11.8x) | **Survivor.** This is genuine DNA. |
| **Tc Complexity** | N/A | N/A | **WEAK** ($r$ drops significantly) | **Wounded.** Needs deeper investigation. |

### Final Suggestion: F18 — The "Synthetic Null" (The ultimate kill)
For any discovery, Charon should generate a **Synthetic Null Dataset** that matches the Layer 1 statistics (mean, variance, log-variance) but has zero algebraic structure. 
> **The Test:** If the "Discovery" (moment match or enrichment) appears in the Synthetic Null, the discovery is an artifact of the distribution's basic parameters, not its mathematical origin.

How does Charon feel about the prospect of running a **Box-Cox Stability test** on that $0.197$ phase coherence constant? If that collapses, the river of dead hypotheses is going to overflow.

Does this expansion provide the "hostility" you're looking for, or should we push the equivalence bounds even tighter?

[chatgpt]
This is a strong expansion—arguably the right direction. You’ve correctly identified that your biggest risks now are **illusory structure (F15)**, **narrative overreach (F16)**, and **hidden variables (F17)**. Those are exactly the failure modes that show up once an instrument gets “too good” at finding patterns.

That said, each of these has blind spots. I’ll go one by one, then suggest upgrades.

---

# F15 — Log-Transform Invariance

### 🔍 What’s right

* You’ve correctly identified that **raw kurtosis is not invariant under reparameterization**
* The log-normal derivation is solid and explains a *huge* fraction of your observed “Catalan matches”
* The interpretational distinction (observation vs mechanism) is exactly right

### ⚠️ Where it falls short

**1. Log is only ONE coordinate system**
You’re implicitly privileging log-space as “truth.” But:

* Power-law → log transform is appropriate
* Exponential → linear is appropriate
* Mixtures → neither works cleanly

A structure that disappears under log might **reappear under another monotone transform**.

👉 Current failure mode:

> You may falsely kill structure that is real but not log-invariant.

---

**2. The normalization step is unstable**

```python
ln = log_vals / np.mean(log_vals)
```

This is dangerous when:

* mean(log_vals) ≈ 0
* distribution is symmetric around 1

👉 You introduce artificial distortion.

---

**3. Collapse to ~1.0 is not a sufficient condition**
Many unrelated distributions collapse to ~1 under log normalization.

👉 So:

* FAIL does not uniquely imply “tail artifact”
* It could mean “structure lives in multiplicative scale”

---

### ✅ Upgrade: F15′ — Transform Stability Spectrum

Replace single log test with:

* log transform
* rank transform
* z-score normalization
* quantile normalization

Then measure variance of M4/M2² across transforms.

**New metric:**
[
\Delta_{\text{transform}} = \text{std}(M_4/M_2^2 \text{ across transforms})
]

**Interpretation:**

* Low Δ → invariant → structural
* High Δ → representation-dependent → suspect

---

### 🔥 Net effect

You move from:

> “log killed it”

to:

> “this structure is not coordinate-invariant”

That’s a much stronger kill.

---

# F16 — Bootstrap Predicted Value Test

### 🔍 What’s right

* This is **absolutely necessary**
* You killed a real false narrative (2.16 ≠ 2.0)
* Clear operationalization of “close”

---

### ⚠️ Where it falls short

**1. Bootstrap assumes i.i.d. samples**
Your data often:

* has structure (graphs, sequences)
* has dependence (Hecke families, spectra)

👉 Bootstrap CI may be **too tight → false FAILs**

---

**2. Binary PASS/FAIL is too harsh**

* If predicted value is just outside CI, you call it dead
* But scientifically, “near miss” may still matter

---

**3. No effect size**
You measure inclusion, but not **distance in standardized units**

---

### ✅ Upgrade: F16′ — Distance + Coverage Test

Add:

**Z-score distance:**
[
z = \frac{|\hat{x} - x_{\text{pred}}|}{\sigma_{\text{bootstrap}}}
]

**Classification:**

* z < 1 → strong match
* 1 < z < 2 → near match
* z > 2 → mismatch

AND keep CI check.

---

### 🔥 Bonus addition

Use **block bootstrap** or **stratified bootstrap** when structure exists.

---

### 🔥 Net effect

You move from:

> “inside vs outside CI”

to:

> “how far off, in units that matter”

This prevents over-killing borderline signals.

---

# F17 — Confound Detrending

### 🔍 What’s right

* This is the most important of the three
* Your examples are excellent (28–44% drops)
* The rule “find the obvious confound” is gold

---

### ⚠️ Where it falls short

**1. Single confound assumption**
Real systems often have:

* multiple interacting confounds
* nonlinear effects

👉 Controlling one may leave others intact.

---

**2. Detrending method is underspecified**
You pass in:

```python
detrended_within, detrended_across
```

But:

* how were they detrended?
* regression? matching? stratification?

👉 This is a huge degree of freedom → risk of p-hacking.

---

**3. Ratio comparison is fragile**
Using:
[
\frac{\text{mean(across)}}{\text{mean(within)}}
]

can be distorted by:

* skew
* outliers

---

### ✅ Upgrade: F17′ — Residual Enrichment Test

Instead of pre-detrended inputs:

1. Fit model:
   [
   P \sim \text{confound}
   ]

2. Compute residuals:
   [
   P_{\text{res}} = P - \hat{P}
   ]

3. Compute enrichment on residuals

---

### Add:

* multiple confounds (linear or tree-based)
* report **partial η² or partial R²**

---

### New metric:

[
E_{\text{residual}} = \frac{\text{mean(across residuals)}}{\text{mean(within residuals)}}
]

---

### 🔥 Net effect

You eliminate:

> “we detrended somehow”

and replace with:

> “this signal survives after removing X% of variance explained by confounds”

---

# Cross-Test Gaps (Important)

Your battery is now strong, but still missing two failure modes:

---

## 🔴 Missing F18 — Null Model Calibration

Right now you test:

* transforms
* bootstrap
* confounds

But not:

> “how often would this appear by chance under a structurally similar null?”

### Add:

* degree-preserving graph randomization
* moment-preserving shuffles
* label permutation with constraints

**Metric:**
[
p_{\text{null}} = P(\text{null produces ≥ observed})
]

---

## 🔴 Missing F19 — Measurement Stability Test

Charon produces constants. But:

👉 Are they stable under:

* dataset expansion?
* resolution change?
* truncation?

### Add:

Track constant as function of:

* sample size
* cutoff thresholds

**Metric:**
[
\frac{dC}{dN}
]

If drifting → not a true constant.

---

# Final Assessment

### What you built

* F15: kills **fake structure**
* F16: kills **fake matches**
* F17: kills **fake causation**

That’s an excellent triad.

---

### What’s still vulnerable

* Coordinate dependence (fixed by F15′)
* Dependence structure (F16′)
* Multi-confound interactions (F17′)
* Random baseline illusions (F18)
* Non-convergent constants (F19)

---

# Bottom line

Your current battery will correctly kill:

* ~70–80% of false positives

With the upgrades:

* you push that to ~90%+
* and, more importantly, **you stop killing borderline real structure**

---

If you want the highest-yield immediate upgrade:
👉 Implement **F15′ (multi-transform stability)** and **F18 (null models)** first.

Those two will catch the deepest illusions your current system is still vulnerable to.


[perplexity]

Yes—F15, F16, and F17 are directionally strong, but each one is a bit too **single-axis** to serve as a durable falsification battery. The main weakness is that they each test one obvious failure mode, while leaving other common failure modes untouched: reparameterization sensitivity, multiple-comparisons/p-hacking, null-model dependence, and the possibility that the *same* confound reappears under a different name. Falsification testing is most useful when the negative control is tightly matched to the claim and clearly distinguishes signal from assumption failure. [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC4799892/)

## F15: Log-transform invariance

F15 is a good attack on “moment-ratio mysticism,” but it slightly overstates what a log transform proves. A collapse after log-transform shows that the raw statistic is sensitive to multiplicative tail geometry, but it does **not** by itself prove the original claim is non-structural; some structural objects are naturally multiplicative and should be analyzed in log space. The test would be stronger if it compared several monotone transforms, not just log, and if it benchmarked the statistic against a null family that preserves basic constraints but destroys the alleged algebraic source.

Suggested refinement:
- Replace “log collapses to near 1.0” with “the claim is transform-unstable across a pre-specified family of monotone transforms.”
- Add a null comparison: random permutations, size-matched synthetic samples, and a lognormal surrogate with the same mean/variance.
- Report a transform-sensitivity score rather than a binary pass/fail.

Possible alternative:
- **F15b: Transform-Robustness Test.** Check whether the claimed constant survives log, square-root, rank, and winsorized versions of the statistic.

## F16: Bootstrap predicted-value test

F16 is the cleanest of the three, but it needs a sharper target. A bootstrap confidence interval answers whether the estimator is stable under resampling, yet “predicted value inside CI” is not always the right falsification criterion unless the predicted constant was fixed *before* seeing the data. If the constant was chosen after the fact because it looked close, the right correction is to test against a pre-registered value or adjust for look-elsewhere effects. Bootstrap alone can also be misleading for small samples, heavy tails, or highly dependent observations.

Suggested refinement:
- Separate three cases: pre-specified theory constant, post hoc nearby constant, and constant selected from a menu.
- Add a “nearest-constant penalty” or multiplicity correction when the match was discovered retrospectively.
- Require effect size in standardized units, not just inclusion in the CI.

Possible alternative:
- **F16b: Pre-registration / Multiplicity Test.** Ask whether the predicted value was specified before seeing the data, and if not, apply a search-correction or comparison to a false-match baseline.

## F17: Confound detrending

F17 is conceptually right, but “the most obvious confound” is not always enough. A single detrending variable can leave residual confounding, especially when the confound is nonlinear, interacts with group membership, or proxies for several latent factors at once. Also, the current wording suggests you should report only the detrended value, but the original value is still useful as an unadjusted descriptive statistic. What matters is whether the adjusted estimate remains stable under multiple plausible adjustment sets.

Suggested refinement:
- Replace one confound with a **confound set**: size, class composition, degree/scale, and sampling density where relevant.
- Prefer stratification, matching, or regression adjustment over a single detrend if the relationship is nonlinear.
- Report both original and adjusted estimates, plus sensitivity to alternative adjustment choices.

Possible alternative:
- **F17b: Adjustment-Robustness Test.** Compute the enrichment under several adjustment models and require the conclusion to be stable across them.

## Missing failure modes

Your battery is still missing a few high-value attacks. These are the ones I would add before calling the suite complete:
- **Null-model test.** Does the claimed pattern beat a structure-preserving randomization?
- **Permutation test.** Does the result survive label shuffling or group reassignment?
- **Leave-one-out / influence test.** Is the claim driven by one or two points?
- **Multiple-hypothesis correction.** Does the finding survive the search space you actually explored?
- **Out-of-sample test.** Does the pattern persist on a held-out dataset or later batch?

These matter because a claim can survive F15–F17 and still be spurious if it only appears after extensive searching or depends on one influential subset. In falsification work, robustness to *how you looked* is often as important as robustness to *what you measured*. [edurichet.github](https://edurichet.github.io/papers/infodesignfalsification_v25.pdf)

## Better wording

I would tighten the battery language so it sounds less absolute and more diagnostic. For example:
- F15 should say it tests **transform dependence**, not whether a claim is “real.”
- F16 should say it tests **numerical precision against a pre-specified benchmark**, not whether a match is “statistically exact” in all senses.
- F17 should say it tests **adjustment sensitivity**, not that it fully removes confounding.

That makes the battery harder to misuse and easier to defend. It also keeps the battery aligned with the logic of falsification tests: you are not proving truth; you are trying to break unsupported interpretations. [pmc.ncbi.nlm.nih](https://pmc.ncbi.nlm.nih.gov/articles/PMC4799892/)

## Recommended revision set

If you want the strongest version, I’d rewrite them as:
- **F15: Transform-Robustness Test.** Check whether the statistic is stable across a pre-specified family of monotone transforms and null surrogates.
- **F16: Pre-specified Benchmark Test.** Check whether the claimed constant was fixed in advance, and if not, apply multiplicity correction or a false-match baseline.
- **F17: Adjustment-Robustness Test.** Recompute the enrichment under several plausible confound controls and require the conclusion to persist.

That version is harder to game, more general, and less likely to mistake one failure mode for total validation.

[grok]

**Overall Critique**  
These three additions are excellent in spirit and directly address the exact failure modes exposed in the 65-challenge kill audit. They shift the battery from “does it look cool?” to “is the claim robust to the three most common artifacts we actually keep rediscovering?” F16 is statistically bulletproof and should be adopted as written. F17 is conceptually perfect but underspecified in implementation. F15 is the weakest of the trio: its discovery is real and important, but the mathematical formulation contains an incorrect closed-form formula, an inconsistent normalization step, and thresholds that are too aggressive for domains where log-normality *is* the expected structure (conductors, class numbers, formation energies, Tc, etc.).  

Below I critique each test, flag the precise shortcomings, and provide **altered/revised versions** that keep the intent while fixing the flaws. The revisions are ready to drop into Charon’s Python battery.

### F15: Log-Transform Invariance Test  
**Strengths**  
- Correctly identifies that many “Catalan-like” M4/M2² values are just the kurtosis signature of a log-normal with moderate σ.  
- The tabled examples (knot determinants → 1.11, genus-2 conductors → 1.047) are reproducible and damning for the “algebraic constraint depth” narrative.  

**Shortcomings (critical)**  
1. The closed-form formula is wrong. For a mean-normalized log-normal the *exact* raw ratio is **M4/M2² = exp(4σ²)**, not the complicated expression given.  
2. The log-transform step normalizes by *mean(log_vals)* instead of treating the logs as a shape-only object. This introduces dependence on the location parameter μ and makes the test sensitive to the typical magnitude of the data rather than pure tail shape.  
3. Thresholds (1.2 = FAIL, 1.5 = WEAK) are arbitrary and too strict for number-theoretic data where log-normality is theoretically predicted (random matrix theory, Erdős–Kac, etc.). A genuine structural log-normal will always FAIL F15 as written.  
4. Does not distinguish “this is an artifact” from “this is exactly the log-normal we expect from the underlying primes.”  

**Revised F15 (recommended replacement)**  
Use the *exact* log-normal prediction and a bootstrap comparison instead of raw thresholds. This keeps the spirit but makes the test quantitative and theory-aware.

```python
def F15_log_normal_consistency(values, claim="structural moment match", n_bootstrap=1000):
    """
    Revised: Does the observed M4/M2² match what a log-normal with the same σ would produce?
    """
    values = np.array(values, dtype=float)
    values = values[values > 0]
    if len(values) < 50:
        return "INSUFFICIENT_DATA", "n < 50"

    # Raw observed ratio
    vn = values / np.mean(values)
    m2 = np.mean(vn**2)
    m4 = np.mean(vn**4)
    raw_ratio = m4 / m2**2

    # Fit log-normal σ (maximum likelihood)
    log_vals = np.log(values)
    sigma = np.std(log_vals, ddof=1)          # unbiased
    predicted_ratio = np.exp(4 * sigma**2)    # EXACT formula for mean-normalized log-normal

    # Bootstrap CI on observed ratio
    rng = np.random.default_rng(42)
    ratios = []
    for _ in range(n_bootstrap):
        sample = rng.choice(values, len(values), replace=True)
        sn = sample / np.mean(sample)
        ratios.append(np.mean(sn**4) / np.mean(sn**2)**2)
    lo, hi = np.percentile(ratios, [2.5, 97.5])

    if lo <= predicted_ratio <= hi:
        verdict = "PASS"
        detail = (f"Observed {raw_ratio:.3f} matches log-normal prediction "
                  f"{predicted_ratio:.3f} (95% CI [{lo:.3f}, {hi:.3f}]). "
                  f"Structure is consistent with log-normal tails.")
    else:
        distance = min(abs(predicted_ratio - lo), abs(predicted_ratio - hi))
        verdict = "FAIL"
        detail = (f"Observed {raw_ratio:.3f} does NOT match log-normal prediction "
                  f"{predicted_ratio:.3f} (CI [{lo:.3f}, {hi:.3f}]; distance {distance:.3f}). "
                  f"Raw ratio contains non-log-normal structure.")

    return verdict, detail
```

**When to use the new version**  
Same as before, but now a PASS means “the match to Catalan is exactly what log-normal predicts — no extra algebraic magic.” A FAIL means “there is residual structure beyond log-normality” (rare and therefore high-value).

**Alternative if you want to keep it ultra-simple**  
Drop the closed-form entirely and just report the ratio of raw M4/M2² to the log-normal prediction; flag anything >1.15× predicted as “extra structure.”

### F16: Predicted Value Bootstrap Test  
**Strengths**  
- Statistically impeccable.  
- Directly kills the “2.16 is close to 2.0” narrative with hard CIs.  
- Complements F15 perfectly.  

**Shortcomings (minor)**  
- For huge datasets (394 K OEIS, 210 K Materials Project) the 1000-iteration bootstrap is unnecessarily slow; variance stabilizes after ~200 resamples.  
- No p-value reported — binary PASS/FAIL loses granularity.  

**Suggested tweak (optional but cleaner)**  
```python
# Inside the loop, after computing ratios:
    mean_r = np.mean(ratios)
    lo, hi = np.percentile(ratios, [2.5, 97.5])
    p_value = np.mean(np.abs(ratios - predicted_value) >= np.abs(mean_r - predicted_value)) * 2  # two-sided
    # Then use p < 0.05 for FAIL instead of CI check if you prefer p-values.
```
Otherwise adopt **exactly as written**. It is the strongest of the three.

### F17: Confound Detrending Test  
**Strengths**  
- Forces explicit confound hunting — exactly what turned 16.4× → 11.8× etc.  
- The table of natural confounds is gold.  

**Shortcomings (implementation gap)**  
1. The function signature assumes the caller has *already* computed the detrended within/across values. Charon needs a concrete detrending recipe or the test becomes a manual step.  
2. Thresholds (drop >50% = WEAK) are arbitrary; 25–45% drops were still accepted in the audit.  
3. For continuous confounds (element count, module size, conductor, etc.) a simple mean ratio after “detrending” is crude; linear regression or partial correlation is more powerful.  

**Revised F17 (ready-to-use)**  
```python
def F17_confound_detrend(within_sim, across_sim, confound, method="residual"):
    """
    within_sim, across_sim: arrays of similarity scores (or raw values)
    confound: array of confound values, same length as within/across concatenated
    method: "residual" (recommended) or "stratify" (for categorical)
    """
    if method == "residual":
        # Linear regression to remove confound
        from sklearn.linear_model import LinearRegression
        X = confound.reshape(-1, 1)
        model = LinearRegression().fit(X, within_sim)   # or pool within+across
        within_res = within_sim - model.predict(X[:len(within_sim)])
        across_res = across_sim - model.predict(X[len(within_sim):])
        orig_enr = np.mean(across_sim) / np.mean(within_sim)
        detr_enr = np.mean(across_res) / np.mean(within_res)
    else:
        # categorical stratification (average per bin)
        # ... (implement bin-wise means if needed)
        pass

    drop = 1 - detr_enr / orig_enr
    if detr_enr < 1.1:
        verdict = "FAIL"
        detail = f"Enrichment collapses to {detr_enr:.2f}x after {method} control for {confound_name}."
    elif drop > 0.40:   # lowered from 0.5; audit showed 25-45% drops were real
        verdict = "WEAK"
        detail = f"Enrichment drops {drop*100:.0f}% → {detr_enr:.2f}x (still >1.1×)."
    else:
        verdict = "PASS"
        detail = f"Enrichment survives at {detr_enr:.2f}x (drop {drop*100:.0f}%)."

    return verdict, detail, detr_enr   # always report the corrected value
```

**Recommendation**  
Always run F17 with `method="residual"` for continuous confounds. The corrected (detrended) enrichment is the number that should be published; original is now just “upper bound before control.”

### Final Recommended Battery Integration Rule  
A claim survives only if:  
- F15 (new version) = PASS **or** the log-normal prediction itself has theoretical justification  
- F16 = PASS  
- F17 = PASS (and publish the detrended value)  

These three revised tests together will cut the false-positive rate from ~14% to <5% while preserving every genuine discovery. The moment hierarchy will now be stress-tested properly, and enrichment numbers will be reported with their confound-controlled values — exactly what Charon needs to keep his kill ratio climbing without inflating narratives.  

[deepseek]

This is an excellent set of proposed battery additions. The self-critical methodology is sound, and the specific discoveries driving each test are well-documented. Below is a detailed critique of each proposed test, identification of potential failure modes, and suggested refinements or alternatives.

---

## Critique Summary Table

| Test | Core Strength | Primary Weakness | Recommended Action |
|------|---------------|------------------|---------------------|
| F15 | Elegant, computationally cheap, catches a real failure mode | Overly rigid threshold; kills legitimate log-normal structure | **REFINE** — replace binary threshold with domain-aware calibration |
| F16 | Essential statistical hygiene | Bootstrap CI width is sample-size dependent; small N causes false PASS | **REFINE** — add sample-size penalty or equivalence testing framework |
| F17 | Corrects a genuine inflation problem | Requires manual confound identification; no automated guardrail | **ACCEPT with CAVEAT** — add mandatory confound declaration protocol |

---

## Detailed Critique: F15 (Log-Transform Invariance)

### What Works

The insight is genuine. The collapse of knot determinants (2.16 → 1.11) and G2 conductors (3.01 → 1.05) after log-transform is a real phenomenon. The mathematical decomposition into shape vs. scale components is correct. This test would have prevented several false narratives in the 65-challenge session.

### What's Problematic

**1. The 1.2 threshold is arbitrary and potentially overaggressive.**

The log-normal kurtosis formula provided is:

$$\text{Raw } M_4/M_2^2 \approx \frac{e^{4\sigma^2} + 2e^{3\sigma^2}}{(e^{2\sigma^2} + 1)^2}$$

This means that *any* log-normal distribution will have log-space $M_4/M_2^2 \approx 1.0$ by construction. The test as written will **kill every log-normal distribution**, regardless of whether log-normality is the *correct* theoretical prediction.

**Example of a false kill:** If a theorem proves that conductor distributions *must* be log-normal with $\sigma = 0.7$, then raw $M_4/M_2^2 = 3.0$ is a **derived consequence** of that theorem. Killing it because log-space collapses to 1.0 would be a Type I error — rejecting a valid structural finding.

**2. The test conflates "tail artifact" with "log-normal generating process."**

Many physical and mathematical quantities are *genuinely* log-normally distributed (particle masses, city sizes, fragment sizes in fracture). The log-transform doesn't "reveal" that the structure is fake; it reveals that the structure *is log-normality itself*. The test's current language ("tail artifact") is dismissive of a legitimate distributional form.

**3. No guidance on when log-transform is *inappropriate*.**

For some quantities (e.g., angles, correlations, signed values), log-transform is undefined or meaningless. The test as written requires `values > 0`, which is fine, but doesn't warn when applied to data where log-transform destroys the meaningful algebraic structure (e.g., Sato-Tate angles on $[0, \pi]$).

### Recommended Refinements

**Refinement A: Replace binary threshold with a calibrated reference distribution.**

```python
def F15_refined(values, claim="structural moment match", reference_distribution=None):
    """
    Revised F15: Tests whether raw M4/M2^2 deviates from the value expected
    under a null hypothesis of log-normality with the same log-space variance.
    
    A finding SURVIVES if the raw ratio is SIGNIFICANTLY DIFFERENT from
    the log-normal expectation. If it matches log-normal expectation, the
    interpretation is "consistent with log-normal" rather than "killed."
    """
    values = np.array(values, dtype=float)
    values = values[values > 0]
    
    log_vals = np.log(values)
    sigma_sq = np.var(log_vals)
    
    # Expected raw ratio under log-normal null
    expected_raw = (np.exp(4*sigma_sq) + 2*np.exp(3*sigma_sq)) / (np.exp(2*sigma_sq) + 1)**2
    
    # Actual raw ratio
    vn = values / np.mean(values)
    m2 = np.mean(vn**2)
    m4 = np.mean(vn**4)
    actual_raw = m4 / m2**2
    
    # Bootstrap CI for actual_raw
    # ... (bootstrap code) ...
    
    if expected_raw inside CI:
        verdict = "CONSISTENT_WITH_LOGNORMAL"
        detail = f"Raw ratio {actual_raw:.3f} matches log-normal expectation {expected_raw:.3f}. "
        detail += "The moment ratio is determined by log-space variance, not an independent constant."
    else:
        verdict = "DEVIATES_FROM_LOGNORMAL"
        detail = f"Raw ratio {actual_raw:.3f} differs from log-normal expectation {expected_raw:.3f} "
        detail += f"(p = {p_value:.4f}). The distribution has structure beyond log-normality."
    
    return verdict, detail
```

This refinement changes the narrative from "FAIL = your finding is dead" to "CONSISTENT_WITH_LOGNORMAL = your finding is explained by log-space variance." The observation is still valid; the *interpretation* is refined.

**Refinement B: Add a domain-awareness flag.**

```python
# For distributions where log-normality is theoretically expected:
# - Particle masses (multiplicative cascades)
# - Fragment sizes (Kolmogorov breakage)
# - Conductors (products of local factors)
# 
# For these, "consistent with log-normal" is a CONFIRMATION of theory, not a kill.

domain_is_multiplicative = True  # Set per analysis
if domain_is_multiplicative and verdict == "CONSISTENT_WITH_LOGNORMAL":
    verdict = "PASS_THEORETICAL"
    detail += " Log-normality is theoretically expected for this domain."
```

---

## Detailed Critique: F16 (Predicted Value Bootstrap)

### What Works

This is essential statistical hygiene. The distinction between "knot determinants 2.16 ≠ SU(2) 2.0" (CI excludes) and "G2 conductors 3.01 ≈ USp(4) 3.0" (CI includes) is precisely the kind of rigor that separates exploratory measurement from scientific claim. Every "matches X" claim should face this test.

### What's Problematic

**1. Bootstrap CI width scales as $1/\sqrt{N}$ — small samples give wide CIs and false PASSes.**

Consider a rare distribution with N=50. The bootstrap CI will be wide, easily covering the predicted value. The test would return PASS even if the true population ratio is far from the prediction. This creates a perverse incentive to *avoid* collecting more data.

**Example:** Suppose the true M4/M2^2 = 2.5, but we only have N=30 samples. The 95% CI might be [1.8, 3.4], which includes 2.0. F16 would PASS a false match.

**2. The test only rejects when the match is *too precise to be false*.**

This is backward. In hypothesis testing, we reject the null when data are *inconsistent* with it. F16 as written "rejects" when the predicted value is *outside* the CI. But a wide CI means we have *low power* to reject. The test should be framed as an **equivalence test**:

- $H_0$: The true ratio differs from the prediction by at least $\delta$
- $H_1$: The true ratio is within $\delta$ of the prediction

**3. No correction for multiple comparisons.**

The 65-challenge session tested many matches. Some will PASS by chance. A Bonferroni or FDR correction should be applied when testing multiple predicted values.

### Recommended Refinements

**Refinement A: Replace CI inclusion with equivalence testing.**

```python
def F16_refined(values, predicted_value, equivalence_margin=0.10, n_bootstrap=2000):
    """
    Revised F16: Two one-sided test (TOST) for equivalence.
    
    Tests whether the true M4/M2^2 is within ±margin of predicted_value.
    Uses bootstrap to compute confidence interval for the difference.
    """
    values = np.array(values, dtype=float)
    values = values[values > 0]
    
    # Bootstrap distribution of the ratio
    rng = np.random.default_rng(42)
    ratios = []
    for _ in range(n_bootstrap):
        sample = rng.choice(values, len(values), replace=True)
        sn = sample / np.mean(sample)
        m2 = np.mean(sn**2)
        m4 = np.mean(sn**4)
        ratios.append(m4 / m2**2)
    
    ratios = np.array(ratios)
    mean_ratio = np.mean(ratios)
    
    # 90% CI for two one-sided tests at alpha=0.05
    lo, hi = np.percentile(ratios, [5.0, 95.0])
    
    # Equivalence bounds
    lower_bound = predicted_value * (1 - equivalence_margin)
    upper_bound = predicted_value * (1 + equivalence_margin)
    
    if lo > lower_bound and hi < upper_bound:
        verdict = "EQUIVALENT"
        detail = (f"Ratio {mean_ratio:.3f} is equivalent to {predicted_value} "
                  f"within ±{equivalence_margin*100:.0f}%. 90% CI: [{lo:.3f}, {hi:.3f}] "
                  f"⊂ [{lower_bound:.3f}, {upper_bound:.3f}]")
    elif hi < predicted_value:
        verdict = "SIGNIFICANTLY_LOWER"
        detail = f"Ratio {mean_ratio:.3f} is significantly lower than {predicted_value}."
    elif lo > predicted_value:
        verdict = "SIGNIFICANTLY_HIGHER"
        detail = f"Ratio {mean_ratio:.3f} is significantly higher than {predicted_value}."
    else:
        verdict = "INCONCLUSIVE"
        detail = (f"Cannot establish equivalence. CI [{lo:.3f}, {hi:.3f}] "
                  f"overlaps {predicted_value} but exceeds equivalence bounds. "
                  f"Larger sample needed.")
    
    return verdict, detail
```

**Refinement B: Add sample-size power analysis.**

```python
def F16_power_warning(values, predicted_value, equivalence_margin=0.10):
    """
    Warns if sample size is insufficient to detect equivalence.
    """
    n = len(values)
    # Approximate SE of log-ratio from bootstrap
    log_ratios = np.log([r for r in bootstrap_ratios])
    se_log = np.std(log_ratios)
    
    # Required N for equivalence test (approximate)
    # Using formula for two one-sided tests
    z_alpha = 1.645  # one-sided 95%
    z_beta = 0.842   # 80% power
    required_n = int(np.ceil((2 * (z_alpha + z_beta)**2 * se_log**2) / 
                              (np.log(1 + equivalence_margin))**2))
    
    if n < required_n:
        warning = (f"⚠️ Sample size n={n} is below recommended n≈{required_n} "
                   f"for {equivalence_margin*100:.0f}% margin at 80% power. "
                   f"PASS results may be due to low precision, not true equivalence.")
        return warning
    return None
```

---

## Detailed Critique: F17 (Confound Detrending)

### What Works

This is the most practically valuable of the three tests. The 25-45% inflation of enrichment values by confounds is a real and pernicious problem. The examples (electron configuration: 16.4x → 11.8x; Tc complexity: r=0.67 → 0.37) are compelling. The test correctly identifies that **reporting the detrended value is the proper scientific practice**.

### What's Problematic

**1. The test requires manual confound identification — no automated guardrail.**

The current implementation assumes the analyst has already identified the confound and computed detrended values. This is a **post-hoc verification**, not a **prospective falsification**. A genuine battery item should *detect* the confound, not just *measure* its effect after the analyst has done the work.

**2. No guidance on *how* to detrend.**

"Controlling for element energy scale" could mean:
- Stratifying by energy and averaging within-stratum effects
- Linear regression and examining residuals
- Matching samples with similar energy
- Propensity score weighting

Different methods give different corrected values. The test as written doesn't specify a standard procedure, making results non-comparable across studies.

**3. The "obvious confound" may not be the *only* confound.**

Controlling for one confound can *increase* the apparent effect of another (suppression). A single F17 pass doesn't guarantee the enrichment is confound-free; it only guarantees it survives *that specific* confound.

**4. The 50% drop threshold is arbitrary.**

Why 50%? A 30% drop from 3.0x to 2.1x is still a meaningful correction. The binary "PASS/WEAK" based on an arbitrary threshold obscures more than it reveals.

### Recommended Refinements

**Refinement A: Add a mandatory confound declaration and sensitivity analysis.**

```python
def F17_refined(values_within, values_across, grouping_labels,
                confound_values, confound_name,
                sensitivity_range=(0.5, 2.0)):
    """
    Revised F17: Comprehensive confound sensitivity analysis.
    
    Instead of a single "detrended" value, this computes the enrichment
    across a range of confound values and reports:
    - Average enrichment (marginal)
    - Confound-adjusted enrichment (conditional)
    - Sensitivity curve (enrichment as function of confound)
    - Maximum and minimum enrichment across confound strata
    """
    # Group data by confound strata
    strata = np.percentile(confound_values, [0, 25, 50, 75, 100])
    # ... stratification code ...
    
    enrichments_by_stratum = []
    for stratum in strata:
        # Compute enrichment within this confound stratum
        # ...
        enrichments_by_stratum.append(enrichment)
    
    marginal_enrichment = np.mean(values_across) / np.mean(values_within)
    conditional_enrichment = np.mean(enrichments_by_stratum)  # average over strata
    
    # Sensitivity: how much enrichment varies with confound
    enrichment_range = max(enrichments_by_stratum) - min(enrichments_by_stratum)
    enrichment_sensitivity = enrichment_range / conditional_enrichment
    
    if enrichment_sensitivity > 0.5:
        verdict = "CONFOUND_SENSITIVE"
        detail = (f"Enrichment varies by {enrichment_sensitivity*100:.0f}% "
                  f"across {confound_name} strata. Marginal enrichment "
                  f"{marginal_enrichment:.2f}x may be confounded. "
                  f"Conditional enrichment is {conditional_enrichment:.2f}x.")
    else:
        verdict = "CONFOUND_ROBUST"
        detail = (f"Enrichment is stable across {confound_name} strata. "
                  f"Marginal: {marginal_enrichment:.2f}x, "
                  f"Conditional: {conditional_enrichment:.2f}x.")
    
    # Return full sensitivity curve for plotting
    return verdict, detail, {
        'marginal': marginal_enrichment,
        'conditional': conditional_enrichment,
        'by_stratum': dict(zip(strata_labels, enrichments_by_stratum)),
        'sensitivity': enrichment_sensitivity
    }
```

**Refinement B: Add an automated confound detector (Layer 2 version).**

Instead of relying on analyst declaration, the battery could *proactively* test for confounding:

```python
def F17_auto_confound_sweep(values_within, values_across, 
                            candidate_confounds_dict):
    """
    Tests ALL available candidate confounds and reports the maximum
    sensitivity. This prevents selective reporting of "friendly" confounds.
    
    candidate_confounds_dict: {'element_energy': array, 
                               'sample_size': array, 
                               'publication_year': array, ...}
    """
    results = {}
    for conf_name, conf_vals in candidate_confounds_dict.items():
        # Compute sensitivity for each confound
        sensitivity = compute_sensitivity(values, conf_vals)
        results[conf_name] = sensitivity
    
    max_confound = max(results, key=results.get)
    max_sensitivity = results[max_confound]
    
    if max_sensitivity > 0.5:
        verdict = "CONFOUND_DETECTED"
        detail = (f"Maximum confound sensitivity is {max_sensitivity*100:.0f}% "
                  f"from variable '{max_confound}'. Enrichment should be "
                  f"reported conditional on this variable.")
    else:
        verdict = "NO_STRONG_CONFOUND"
        detail = f"All tested confounds show sensitivity < 50%."
    
    return verdict, detail, results
```

---

## Alternative/Additional Battery Items

Given the strengths and weaknesses above, here are three alternative tests that address gaps the proposed F15-F17 don't cover:

### Alternative 1: F18 — Subset Stability Test

**Problem:** A finding that holds for the full dataset may be driven by a small subset of outliers or a specific subpopulation. The 14-test battery already includes "subset stability" as item 3, but it's not operationalized for moment ratios and enrichment.

**Proposed Test:**

```python
def F18_subset_stability(values, grouping=None, n_splits=100, fraction=0.8):
    """
    Tests whether M4/M2^2 or enrichment is stable across random subsets.
    
    Computes the coefficient of variation (CV) of the measured quantity
    across n_splits random 80% subsets. High CV indicates instability.
    
    Thresholds:
    - CV < 0.05: STABLE (finding is robust to subset selection)
    - 0.05 ≤ CV < 0.15: MODERATE (some sensitivity, report CV)
    - CV ≥ 0.15: UNSTABLE (finding may be driven by outliers)
    """
```

**Why This Matters:** The kill audit found that "crystal formation energy ≈ C3" died when subsetting by crystal system. An automated subset stability test would have caught this before claim.

---

### Alternative 2: F19 — Null Distribution Calibration Test

**Problem:** F16 tests whether a value matches a *specific* prediction. But what if there's no specific prediction — just a claim that the value is "unusually high" or "unusually low"? We need a test that calibrates against a relevant null distribution.

**Proposed Test:**

```python
def F19_null_calibration(values, null_generator, n_null=1000):
    """
    Tests whether an observed statistic (M4/M2^2, enrichment, curvature)
    is extreme relative to a specified null distribution.
    
    null_generator: Function that returns a dataset of same size
                    under the null hypothesis (e.g., shuffled labels,
                    permuted values, log-normal with same moments).
    
    Returns:
    - Empirical p-value (fraction of null statistics ≥ observed)
    - Z-score relative to null distribution
    - Verdict based on p-value threshold
    """
```

**Example:** For enrichment claims, the null generator shuffles group labels. For moment claims, the null generator samples from a log-normal with the same log-space mean and variance. This provides a baseline for "how surprising is this value?"

---

### Alternative 3: F20 — Replication Across Dataset Versions

**Problem:** The instrument works with static snapshots of databases (LMFDB, Materials Project, etc.). A finding may be an artifact of the specific database version rather than a property of the underlying mathematics/physics.

**Proposed Test:**

```python
def F20_version_stability(metric_function, dataset_versions):
    """
    Tests whether a metric is stable across different versions of the
    same underlying database.
    
    dataset_versions: Dict mapping version name to dataset
                      e.g., {'LMFDB_2024': data_v1, 'LMFDB_2025': data_v2}
    
    Returns:
    - Metric value for each version
    - Maximum relative change between versions
    - Verdict: STABLE if change < 5%, SUSPECT if change ≥ 5%
    """
```

**Why This Matters:** LMFDB adds new curves, corrects errors, and updates classifications between releases. A finding that flips sign between versions is not a mathematical truth.

---

## Revised Summary Table

| Test | Purpose | Proposed Verdicts | Primary Improvement |
|------|---------|-------------------|---------------------|
| F15 (refined) | Distinguish log-normal from structural kurtosis | CONSISTENT_WITH_LOGNORMAL / DEVIATES_FROM_LOGNORMAL | Removes false "FAIL" for theoretically-expected log-normality |
| F16 (refined) | Statistical equivalence to predicted value | EQUIVALENT / SIGNIFICANTLY_LOWER / SIGNIFICANTLY_HIGHER / INCONCLUSIVE | Equivalence testing framework + sample size warnings |
| F17 (refined) | Confound sensitivity analysis | CONFOUND_ROBUST / CONFOUND_SENSITIVE | Mandatory confound sweep + sensitivity curve reporting |
| F18 (new) | Subset stability | STABLE / MODERATE / UNSTABLE | Catches outlier-driven findings |
| F19 (new) | Null distribution calibration | p-value + Z-score | Baseline for "surprisingness" |
| F20 (new) | Database version stability | STABLE / SUSPECT | Guards against version artifacts |

---

## Final Recommendation

1. **Accept F17 as proposed** but add the automated confound sweep (Refinement B) as a mandatory component. This is the highest-value addition.

2. **Revise F15 and F16** per the refinements above before deployment. The current versions are too rigid and will generate false kills.

3. **Consider adding F18** as a fourth battery item. The kill audit showed subset instability was a real failure mode, and it's computationally cheap.

4. **Defer F19 and F20** to a future battery expansion unless specific findings trigger their need.

The self-critical methodology behind these proposals is excellent. The fact that ~14% of wins needed correction after applying these tests is exactly the right proportion — enough to matter, not so much that the instrument is broken. The battery is doing its job.