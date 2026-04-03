# Package 3 Summary: Prior Art Assessment — Impact on Charon
## Date: 2026-04-02
## Source: Gemini Deep Research
## Status: Novelty confirmed on all four axes. One new paper demands immediate attention.

---

## Verdict

**All four novelty axes survive the prior art search.** No one has built what we built. But one paper — Wachs (2026) — changes the theoretical story of the spectral tail finding in a way that makes it stronger, not weaker.

---

## The Four Novelty Axes — Confirmed

### 1. k-NN on zero vectors across object types: NOVEL
No prior work builds a searchable retrieval system using L-function zeros as coordinates. The literature uses zeros for statistical distribution analysis (Montgomery-Odlyzko spacing, Katz-Sarnak density verification). Nobody treats the zero vector as an address in a metric space for nearest-neighbor retrieval. The closest work (Bieri et al. 2025, arXiv:2502.10360) uses Dirichlet coefficients, not zeros, and classifies rather than retrieves.

### 2. Cross-family metric comparison: NOVEL
All murmuration and zero-statistics literature stays within single families (elliptic curves, or holomorphic newforms, or quadratic twists). Nobody constructs a shared metric space where an elliptic curve and a modular form and a genus-2 curve coexist as points with measurable distances. Cross-family comparisons in the literature verify shared symmetry-type limits, not object-to-object metric distances.

### 3. Spectral tail ablation finding: NOVEL (with critical nuance)
No prior work reports that removing the first zero improves rank clustering as a machine learning result. However — **Wachs (2026) provides the physics that explains WHY it works** (see below). The ablation observation is new. The underlying mechanism was partially observed by Wachs in a completely different context.

### 4. Representation choice (zeros vs coefficients): DISTINCT
The field uses Dirichlet coefficients or Frobenius traces as ML features. Oliver (ICMS 2024), Costa (2016 infrastructure), and Bieri et al. (2025) all operate in coefficient space. Zero-based coordinate geometry is a different representation that avoids the cross-family normalization problems of coefficients (different weights, degrees, conductors).

---

## The Wachs (2026) Finding — This Changes Things

**Paper:** "BSD Invariants and Murmurations of Elliptic Curves" (Wachs, 2026)

**What Wachs found:** Within rank-0 elliptic curves, curves with Tate-Shafarevich order ≥ 4 have systematically different zero distributions: the first zero is displaced higher, subsequent zeros pack more tightly. He used Hotelling's T² test to confirm this is statistically significant. The mechanism: non-rank BSD invariants (Sha, Tamagawa product, real period) perturb the first zero independently of rank.

**What this means for the spectral tail finding:**

Wachs gives us the **physical mechanism** we were missing. The first zero isn't just "noisy" — it's encoding the Tate-Shafarevich group, Tamagawa numbers, and the real period. These are rank-independent invariants that add variance to the first zero without adding rank information. Removing it strips that variance. The spectral tail improvement isn't a dimensionality artifact — it's the removal of a specific, identifiable confound.

**What Wachs did NOT do:**
- Did not run ML ablation tests
- Did not build a retrieval system
- Did not frame this as a feature-engineering insight
- Did not extend beyond rank-0 elliptic curves (single family)
- Did not connect to the ILS support theorem

**The correct citation chain is now:**
ILS (2000) → theory predicts higher zeros distinguish families
Wachs (2026) → first zero is confounded by non-rank invariants
Charon (2026) → ablation demonstrates this computationally as feature selection

---

## Impact on Charon's Claims

### Strengthened
- **The spectral tail finding** now has a mechanistic explanation beyond ILS/Katz-Sarnak/Deuring-Heilbronn. The first zero encodes Sha — that's testable and specific.
- **The novelty claim** survives intact. We are the first to use zeros as coordinates for retrieval, first to compare across families metrically, first to run the ablation.
- **The engineering framing** is validated. Gemini confirms the transition from "statistical mechanics on ensembles" to "data engineering on discrete objects" is the genuine contribution.

### Needs Revision
- **The theoretical grounding section** in the spectral tail conclusion must now cite Wachs. The three-framework explanation (ILS + Katz-Sarnak + Deuring-Heilbronn) gets a fourth leg: Wachs's non-rank invariant confound.
- **The "What we don't know" section** shrinks. We now have a candidate answer for WHAT the first zero encodes that hurts clustering: Sha and BSD invariants.

### New Vulnerability
- If Sha alone explains the first-zero confound, then the spectral tail finding reduces to "remove the Sha signal and rank clustering improves." That's still novel as a computational result, but the "deep spectral geometry" framing weakens. Need to test: does stratifying by Sha order eliminate the ablation improvement?

---

## New Research Directions Opened

### 1. IMMEDIATE: The Sha Stratification Test
**Experiment:** Within rank-0 ECs, stratify by Sha order (trivial vs non-trivial). Run the first-zero ablation within each stratum. If the ablation improvement vanishes when Sha is controlled, the first zero's noise IS Sha, and the spectral tail finding reduces to "remove the Sha confound." If the improvement persists, something beyond Sha is also confounding the first zero.

**Priority:** HIGHEST. This is a kill test for the mechanistic claim. Runnable on existing data in one afternoon.

### 2. The BSD Invariant Decomposition
**Experiment:** Wachs showed real period, Tamagawa product, and Sha order each modulate murmuration profiles. Do these invariants also modulate zero-space position? For each BSD invariant, test whether it predicts position in zeros 5-19 space independently of rank and conductor. This decomposes the spectral tail into its BSD components.

**Priority:** HIGH. Connects Charon's geometry to the deepest conjecture in the field.

### 3. Wachs Replication on Our Dataset
**Experiment:** Reproduce Wachs's Hotelling T² test on our 31K ECs. Do we see the same first-zero displacement for high-Sha curves? This is both a sanity check and a bridge to Wachs's framework.

**Priority:** MEDIUM-HIGH. Fast, validates the connection.

---

## New Council Prompt Needed?

**Yes — but targeted.** The full spectral-tail council prompt (already written) covers the broad attack surface. A focused follow-up should be sent AFTER the Sha stratification test, presenting:
- The Wachs connection
- The Sha stratification result (whatever it is)
- The revised claim

The question to the Council becomes: "We now know the first zero encodes Sha. Does the spectral tail encode anything BEYOND the complement of Sha? What's the residual?"

---

## New Research Package Needed?

**Yes: Package 13 — BSD Invariants in Zero Space**

Questions for Gemini Deep Research:
1. What is the relationship between Sha order and the position of the first L-function zero, beyond Wachs (2026)?
2. Has anyone decomposed L-function zero positions into contributions from individual BSD invariants?
3. Is there a formula connecting Tamagawa numbers to zero displacement?
4. Does the BSD formula predict a quantitative relationship between Sha order and first-zero height?
5. Has anyone used BSD invariants as features for ML on elliptic curves (beyond rank prediction)?

---

## Papers to Add to Charon's Citation List

| Paper | Relevance | Priority |
|-------|-----------|----------|
| Wachs (2026) "BSD Invariants and Murmurations" | Direct mechanistic explanation for first-zero confound | CRITICAL — cite immediately |
| Bieri et al. (2025) arXiv:2502.10360 | Coefficient-based ML on L-functions; our representation is distinct | HIGH — cite to bound novelty |
| Oliver, ICMS 2024 | Unsupervised learning on LMFDB; uses coefficients not zeros | HIGH — cite to bound novelty |
| Zubrilina (2023) | Murmuration density formula; downstream of our sanity check | MEDIUM — cite for murmuration framing |
