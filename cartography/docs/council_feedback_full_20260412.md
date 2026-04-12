# Council Feedback on Full Report — 2026-04-12
## Source: ChatGPT (adversarial review of council_report_full_20260412.md)

---

## Summary of Verdict

**Strengths validated:**
- 3-prime fingerprint kill = "gold standard" scientific behavior
- Conditional law cross-domain recurrence (SC/NF/knots) = "closest thing to a real general discovery"
- Battery discipline and kill record builds genuine credibility

**Over-claims to fix:**
1. "Law" is too strong — suggest "context-dependent invariant" or "stratified structure"
2. "Zero universal laws" needs stronger caveats — 3 alternative explanations not ruled out
3. Negative OOS R² interpretation needs a positive control to validate

---

## 3 Battery Blind Spots Identified

### Blind Spot 1: Representation Dependence (BIGGEST)
Pipeline assumes laws are visible in chosen representation. Misses invariants hidden in bad coordinates, nonlinear combinations, latent variables.
**Proposed fix:** F28 — Representation search (random projections, symbolic transforms, simple embeddings). "Does any representation make this universal?"

### Blind Spot 2: F25 Transportability Is Too Weak
Group-mean transfer can only detect trivial transfer. Misses interaction-aware transfer, functional relationships, nonlinear mappings.
**Proposed fix:** F25b — Model-based transportability (linear, tree, additive models evaluated across contexts).

### Blind Spot 3: ANOVA eta² as Central Metric
Assumes categorical grouping, equal treatment of groups, no hierarchy. Breaks on nested groups, unequal sizes, ordinal predictors.
**Proposed fix:** F24c — Mutual information or cross-validated R² (works for continuous + categorical, less sensitive to group structure).

---

## Overfitting Assessment

**Verdict: Yes, real risk.** Evidence:
- Heavy reliance on categorical structure (SG, ST, Galois)
- Thresholds from social science (eta² ≥ 0.14)
- Success cases mostly "group → scalar"
- New domains (graph theory, combinatorics, algebraic geometry) may require structural/relational features, not simple groupings

---

## 5 Smoke Tests

### Test 1: Universal Law Positive Control (CRITICAL)
- **Hypothesis:** Euler characteristic for convex polytopes (chi=2)
- **Dataset:** 980 polytopes
- **Method:** Hide dimension as "context", run F25
- **Expected:** TRUE universal law → positive OOS R²
- **If fails:** F25 is broken or underpowered

### Test 2: Fake Conditional Law Injection
- **Method:** Random group labels (same size distribution as SG) → test eta² + F25
- **Expected:** eta² ≈ 0 or fails stability
- **If passes:** Battery vulnerable to grouping artifacts

### Test 3: Representation Sensitivity
- **Method:** Take SC_class→Tc, randomly permute feature encodings, apply nonlinear transforms
- **Expected:** Signal degrades gradually, not abruptly
- **If vanishes easily:** Findings are representation-fragile

### Test 4: Known Interaction System (Synthetic)
- **Method:** Generate y = class_effect + structure_effect + interaction + noise
- **Expected:** eta² detects main effects, F25 detects conditionality
- **If not:** Negative OOS R² interpretation not validated

### Test 5: Continuous Universal Law
- **Method:** Simple physical law (linear/quadratic) in existing or generated data
- **Expected:** High R², strong transfer under F25
- **If missed:** System biased toward categorical discoveries

---

## Recommended Next Steps

**Before publication:** Validate battery with positive controls. Currently proven: kills false things, rediscovers known truths. NOT proven: reliably detects transferable laws. F25 positive control is the missing piece.

**Publication paths:**
- Path A (safest): Method paper — "falsification-first framework for context-dependent structure"
- Path B (riskier): Discovery paper — SC_class×SG→Tc as materials science result
- Path C (most important): Positive control validation first

---

## Action Items for Next Round

| Priority | Action | Effort |
|----------|--------|--------|
| 1 | Run all 5 smoke tests | 2-3 hours |
| 2 | Add F25b model-based transportability | 2 hours |
| 3 | Add F24c mutual information alternative | 1 hour |
| 4 | Rename "conditional law" → "context-dependent invariant" | 10 min |
| 5 | Scope-limit "zero universal laws" claim | 10 min |
| 6 | Build F25 positive control (Euler chi polytope test) | 30 min |
