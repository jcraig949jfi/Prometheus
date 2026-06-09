# Battery Expansion v2: F15, F16, F17, F18
## Revised after frontier model review
## 2026-04-11

---

## Changes from v1

The frontier models identified three critical weaknesses in v1:
1. F15's binary threshold kills theoretically-expected log-normality (false kills)
2. F16's CI inclusion test has sample-size bias (false PASSes with small N)
3. F17 requires manual confound identification (no automated guardrail)

Additionally, F18 (subset stability) was recommended as a fourth test.

---

## F15 (revised): Log-Normal Calibration Test

**Purpose:** Determine whether a moment ratio is explained by log-normality or reflects independent structure.

**Key change from v1:** Instead of FAIL/PASS on a threshold, compare the observed raw M4/M2^2 against the EXPECTED value under a log-normal null with the same log-space variance. The finding SURVIVES if the observed ratio DEVIATES from log-normal expectation.

**Verdicts:**
- **CONSISTENT_WITH_LOGNORMAL** — The raw ratio matches the log-normal prediction. The moment ratio is determined by log-space variance. The observation is valid but the interpretation should be "this distribution is log-normal with specific sigma" rather than "this matches algebraic constant X."
- **DEVIATES_FROM_LOGNORMAL** — The raw ratio differs significantly from log-normal prediction. The distribution has structure BEYOND log-normality.
- **PASS_THEORETICAL** — The distribution IS log-normal AND this is the theoretically expected distribution for this domain (e.g., conductors as products of local factors). Log-normality is confirmation, not artifact.

**Domain awareness:** For multiplicative quantities (conductors, discriminants, determinants, particle masses), log-normality is often the correct theoretical prediction. The test should flag "consistent with log-normal" as INFORMATIVE rather than KILLING.

**Implementation sketch:**
```python
def F15_v2(values, domain_is_multiplicative=False):
    log_vals = np.log(values[values > 0])
    sigma_sq = np.var(log_vals)
    
    # Expected raw ratio under log-normal null
    expected = (np.exp(4*sigma_sq) + 2*np.exp(3*sigma_sq)) / (np.exp(2*sigma_sq) + 1)**2
    
    # Observed raw ratio
    vn = values / np.mean(values)
    observed = np.mean(vn**4) / np.mean(vn**2)**2
    
    # Bootstrap CI on observed to test significance of deviation
    # ...
    
    if expected inside observed_CI:
        if domain_is_multiplicative:
            return "PASS_THEORETICAL", "Log-normal expected, confirmed"
        else:
            return "CONSISTENT_WITH_LOGNORMAL", f"Ratio {observed:.3f} matches LN prediction {expected:.3f}"
    else:
        return "DEVIATES_FROM_LOGNORMAL", f"Ratio {observed:.3f} deviates from LN prediction {expected:.3f}"
```

---

## F16 (revised): Equivalence Test (TOST)

**Purpose:** Test whether an observed value is statistically equivalent to a predicted value, not just "consistent with" it.

**Key change from v1:** Replace CI inclusion (which gives false PASS at small N) with Two One-Sided Tests (TOST) framework. This requires BOTH that the CI falls inside equivalence bounds AND that the sample size provides sufficient power.

**Parameters:**
- `equivalence_margin`: default ±10% of predicted value
- `alpha`: 0.05 (each side)
- Minimum power requirement: 80%

**Verdicts:**
- **EQUIVALENT** — 90% CI falls entirely within ±margin of predicted value. Statistical precision is sufficient.
- **SIGNIFICANTLY_DIFFERENT** — Observed value is statistically distinguishable from predicted.
- **INCONCLUSIVE** — CI overlaps predicted value but exceeds equivalence bounds. Need more data.

**Sample size warning:** If N < recommended for 80% power at the specified margin, the test reports INCONCLUSIVE regardless of CI position.

**Implementation sketch:**
```python
def F16_v2(values, predicted, margin=0.10, n_bootstrap=2000):
    # Bootstrap the ratio
    ratios = [bootstrap_M4(sample) for sample in bootstrap_samples]
    lo_90, hi_90 = np.percentile(ratios, [5, 95])  # 90% CI for TOST
    
    lower_bound = predicted * (1 - margin)
    upper_bound = predicted * (1 + margin)
    
    # Power check
    se = np.std(ratios)
    required_n = 2 * ((1.645 + 0.842) * se / (margin * predicted))**2
    if len(values) < required_n:
        return "INCONCLUSIVE", f"N={len(values)} < recommended {required_n:.0f}"
    
    if lo_90 > lower_bound and hi_90 < upper_bound:
        return "EQUIVALENT", f"90% CI [{lo_90:.3f}, {hi_90:.3f}] inside [{lower_bound:.3f}, {upper_bound:.3f}]"
    elif hi_90 < lower_bound or lo_90 > upper_bound:
        return "SIGNIFICANTLY_DIFFERENT", f"90% CI [{lo_90:.3f}, {hi_90:.3f}] outside equivalence bounds"
    else:
        return "INCONCLUSIVE", f"CI overlaps bounds, insufficient precision"
```

---

## F17 (revised): Automated Confound Sensitivity Analysis

**Purpose:** Detect and measure the influence of confounding variables on enrichment claims.

**Key change from v1:** Add automated confound sweep across ALL available candidate variables, not just analyst-declared ones. Report sensitivity curve, not just a single detrended value.

**Mandatory confound declaration:** Every enrichment claim must list candidate confounds. The battery automatically tests each one.

**Verdicts:**
- **CONFOUND_ROBUST** — Enrichment varies < 30% across all confound strata. No confound dominates.
- **CONFOUND_SENSITIVE** — Enrichment varies > 30% with at least one confound. Report conditional enrichment.
- **CONFOUND_DOMINATED** — Enrichment drops > 50% after controlling for dominant confound. The original claim is suspect.

**Standard confounds by domain:**
| Domain | Standard confounds to sweep |
|--------|---------------------------|
| Spectral (energy levels) | Element, ionization state, energy scale |
| Chemical (materials) | Composition class (cuprates etc), n_elements, crystal system |
| Mathematical (proofs) | Module/file size, namespace depth |
| Arithmetic (number fields) | Degree, discriminant magnitude |
| Topological (knots) | Crossing number, determinant magnitude |
| Physical (crystals) | Crystal system, space group, density |

**Implementation sketch:**
```python
def F17_v2(within_pairs, across_pairs, candidate_confounds):
    """Sweep all confounds, report maximum sensitivity."""
    original_enrichment = np.mean(across_pairs) / np.mean(within_pairs)
    
    results = {}
    for conf_name, conf_values in candidate_confounds.items():
        # Stratify and compute conditional enrichment
        strata_enrichments = []
        for stratum in stratify(conf_values):
            stratum_enrichment = compute_enrichment_within_stratum(...)
            strata_enrichments.append(stratum_enrichment)
        
        conditional = np.mean(strata_enrichments)
        sensitivity = abs(original - conditional) / original
        results[conf_name] = {
            'conditional': conditional,
            'sensitivity': sensitivity,
            'by_stratum': strata_enrichments
        }
    
    max_conf = max(results, key=lambda k: results[k]['sensitivity'])
    max_sens = results[max_conf]['sensitivity']
    
    if max_sens < 0.3:
        verdict = "CONFOUND_ROBUST"
    elif max_sens < 0.5:
        verdict = "CONFOUND_SENSITIVE"
    else:
        verdict = "CONFOUND_DOMINATED"
    
    return verdict, results
```

---

## F18 (new): Subset Stability Test

**Purpose:** Detect findings driven by outliers or specific subpopulations.

**Method:** Compute the target statistic (M4/M2^2 or enrichment) across 100 random 80% subsets. Measure the coefficient of variation (CV).

**Verdicts:**
- **STABLE** — CV < 0.05. Finding is robust to subset selection.
- **MODERATE** — 0.05 ≤ CV < 0.15. Some sensitivity. Report CV alongside the statistic.
- **UNSTABLE** — CV ≥ 0.15. Finding may be driven by outliers or specific subpopulation. Investigate which subset drives the effect.

**Implementation sketch:**
```python
def F18_subset_stability(values, statistic_fn, n_splits=100, fraction=0.8):
    stats = []
    for _ in range(n_splits):
        idx = rng.choice(len(values), int(len(values) * fraction), replace=False)
        stats.append(statistic_fn(values[idx]))
    
    cv = np.std(stats) / np.mean(stats) if np.mean(stats) > 0 else float('inf')
    
    if cv < 0.05: return "STABLE", cv
    elif cv < 0.15: return "MODERATE", cv
    else: return "UNSTABLE", cv
```

---

## Complete Battery (F1-F18)

| Test | Purpose | Origin |
|------|---------|--------|
| F1 | Permutation null | Charon original |
| F2 | Subset stability (values) | Charon original |
| F3 | Effect size gate | Charon original |
| F4 | Confound sweep | Charon original |
| F5 | Normalization sensitivity | Charon original |
| F6 | Base rate / Bonferroni | Charon original |
| F7 | Dose-response | Charon original |
| F8 | Direction consistency | Charon original |
| F9 | Simpler explanation | Charon original |
| F10 | Outlier sensitivity | Charon original |
| F11 | Cross-validation | Charon original |
| F12 | Partial correlation | Charon original |
| F13 | Growth rate filter | Charon original |
| F14 | Phase shift test | Charon original (Gemini collab) |
| **F15** | **Log-normal calibration** | **This session (kill audit)** |
| **F16** | **Equivalence test (TOST)** | **This session (kill audit)** |
| **F17** | **Confound sensitivity sweep** | **This session (kill audit)** |
| **F18** | **Subset stability (statistics)** | **This session (frontier review)** |

---

*v2 revised: 2026-04-11*
*Incorporating frontier model critique*
*Status: Ready for implementation*
