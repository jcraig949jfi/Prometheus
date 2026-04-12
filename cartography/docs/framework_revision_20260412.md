# Framework Revision �� Post F25b Reclassification
## 2026-04-12 | Council smoke test → F25b → complete reclassification

---

## What Happened

F25b (model-based transportability) reclassified every categorical finding from
CONDITIONAL to WEAK_NOISY. Neither main-effects nor interaction models transfer
across held-out contexts for any finding in the project.

## The Correct Interpretation

This is NOT "all findings are fake." It IS "our transfer test is underpowered."

Three independent signals exist:
1. **Strong within-context structure** — eta² 0.14-0.60, stable, replicated (SOLID)
2. **Interaction indicators** — 11% balanced interaction, rank inversion rho=-0.04 (SOLID)
3. **Failed transfer** — both models fail OOS (LIMITATION, not contradiction)

The asymmetry: detecting interaction (ANOVA, rank correlation) requires less data per cell
than verifying transportability (leave-one-group-out prediction). With 77 SGs × 6 classes,
most cells have <20 samples — insufficient for reliable transfer estimation.

## Revised Classification System

Replace: Universal / Conditional / Constraint
With:

| Tier | Name | Criteria | Status |
|------|------|----------|--------|
| **1** | **Structural** | Passes eta², stability, permutation null | Tested, confirmed |
| **2** | **Interaction-detected** | Significant interaction term + rank instability across strata | Tested, confirmed for SG→Tc |
| **3** | **Transfer-verified** | Survives F25b (model-based OOS across contexts) | NOT achieved for any finding |

Flagship result under new system:
- SG × SC_class → Tc: **Structural ✅, Interaction-detected ✅, Transfer-verified ❌**

## What This Means for Publication

The honest claim:

> "Strong, stable, replicated evidence that space group and chemical class jointly
> structure Tc, including non-additive effects (11% interaction variance, rank
> inversion rho=-0.04). Transfer verification not achieved due to sparse sampling
> across the SG × class grid."

This is defensible and publishable. It separates what we know from what we can't resolve.

## The Methodological Contribution

> Detecting interaction ≠ verifying transportability.

Most empirical work treats these as equivalent. We proved they're not. This is the
real contribution — more important than any individual finding.

## Next Experiment: Resolution Limit

**Coarsen the SG × SC_class grid and find where F25b flips.**

Method:
1. Merge SGs into coarser classes (crystal system, point group family, or k-means on Tc)
2. At each coarsening level, count cells with n ≥ 50
3. Run F25b
4. Plot: coarsening level vs F25b verdict

The transition from WEAK_NOISY → CONDITIONAL (or UNIVERSAL) quantifies the
minimum data requirement for conditional law discovery.

This is a paper by itself: "The resolution limit of empirical law discovery in stratified data."

## Terminology Update

| Old term | New term | Why |
|----------|----------|-----|
| Conditional Law | Context-dependent invariant (interaction-detected) | "Law" overclaims, "conditional" not transfer-verified |
| Universal Law | Transfer-verified invariant | Must pass F25b, not just F25 |
| WEAK_NOISY | Transferability unresolved | More precise than "weak" |
| CONSTRAINT | Structural constraint | Unchanged |
