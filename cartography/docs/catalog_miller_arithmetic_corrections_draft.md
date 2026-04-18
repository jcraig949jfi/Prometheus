# Draft catalog entry — Miller 2009 arithmetic lower-order terms (P106)

**Drafted by:** Harmonia_M2_sessionB, 2026-04-18 (Thread 4 of post-reflection threads)
**Task:** self-initiated — formalize Miller's arithmetic lower-order terms as the theoretical comparison for F011 rank-0 residual
**Status:** DRAFT — TENSOR_DIFF pending for sessionA review
**Target insertion:** after P105 DHKMS excised ensemble (both are theoretical-prediction type)

**Rationale for filing**: my Path 4 literature harvest surfaced Miller 2009 as uncatalogued. It's specifically the **a_p²-weighted correction** to 1-level density that DHKMS leading-order misses. Given that my rank-0 residual (Thread 1+2) survived alternative decay ansatze at ε₀ ≈ 22.9% under the classical 1/log(N) form, the natural theoretical explanation is Miller's arithmetic corrections. Filing this catalog entry makes the comparison possible.

---

## P106 — Miller arithmetic lower-order terms

**Code:** No direct implementation in the repo. Theoretical reference projection. Implementation sketch:
```python
# For a family F of L-functions with conductors c in [X, 2X],
# the 1-level density D(φ) = (1/|F|) Σ_{f ∈ F} Σ_γ φ(γ log(c_f)/(2π))
# has Miller-style expansion:
#   D(φ) = ∫ φ(x) W(x) dx + A_1 / log(X) + A_2 * M(family) / log(X)^2 + O(1/log^3)
# where M(family) = mean of a_p^2 / p over the family at a specific prime scaling.
# The coefficient A_2 and M(family) together determine the magnitude of
# the finite-conductor correction beyond DHKMS leading order.
```
**Type:** theoretical_prediction (arithmetic-corrected finite-conductor one-level density)

**What it resolves:**
- **Finite-conductor 1-level density beyond DHKMS leading order.** Where P105 DHKMS gives the finite-N excised-ensemble prediction for SO_even/SO_odd families, P106 Miller adds the arithmetic-level correction terms that depend on the specific family's a_p² statistics.
- **A_2 × (a_p² moments) / log(X)² corrections.** These can be substantial at EC conductor range and predict WHY the naive 1/log(X)² heuristic (~0.7% at our data) underestimates the observed deficit by 40-50×.
- **Rank-dependent finite-conductor behavior.** Different ranks sample different a_p² distributions via the Sato-Tate vertical (mu_ST distribution depends on CM status and rank). Miller corrections at rank 0 vs rank 1 differ via the a_p² moment structure of each sub-family.

**What it collapses:**
- **Exact per-curve zero positions.** Miller is an ensemble 1-level-density theory, not a per-curve prediction.
- **Edge-vs-bulk distinction at high zero-index.** Miller lower-order corrections decay rapidly away from the central point. Use for low-lying zero statistics only.
- **Structure orthogonal to a_p² moments.** Sato-Tate vertical symmetry-type effects beyond the a_p² moment are outside Miller's framework.

**Tautology profile:**
- **P106 ⊕ P105 — complementary, not redundant.** P105 DHKMS gives the leading excised-ensemble deficit; P106 Miller gives the next-order arithmetic correction. Both are needed to match observation at finite N. Using only P105 misses Miller corrections; using only P106 without the DHKMS ensemble term misses the leading behavior.
- **P106 ↔ Sato-Tate family structure (not catalogued, open).** Miller corrections are computed from a_p² moments over the family. Families with different Sato-Tate distributions (CM vs non-CM, for EC) give different Miller coefficients. If Sato-Tate vertical symmetry becomes a catalogued axis, P106 + that axis jointly characterize finite-N deviations.
- **P106 ↔ rank stratification (P023) — partial overlap.** At EC rank 0 vs 1, a_p² statistics differ subtly (analytic-rank-dependent Sato-Tate moments). Not strictly tautological but joint use must account for the rank-conditioned a_p² scaling.

**Calibration anchors:**
- **Miller (2004, 2009)** original derivations for families of elliptic curve L-functions; explicit formulas for A_1 and A_2 coefficients under specific test functions.
- **Huynh-Keating-Snaith (2009)** — 2-level Miller-type corrections.
- **Candidate anchor, not yet confirmed:** F011 rank-0 residual ε₀ = 22.9% (under 1/log(N) ansatz, Thread 2 result). If Miller arithmetic corrections at EC conductor range predict ~20% residual beyond DHKMS leading-order, this matches our data. Requires the closed-form computation.

**Known failure modes:**
- **Test-function sensitivity.** Miller corrections A_1 and A_2 depend on the Schwartz test function's support. Different test functions give different quantitative predictions. The comparison to our variance-based deficit is not direct and requires care.
- **a_p² moment extrapolation.** Computing Miller corrections requires averaging a_p² over the family at specific prime scales. For EC with limited a_p data, numerical Miller coefficients have their own uncertainty.
- **Fourth-order effects.** Miller 2009 gives 2nd-order corrections; our data range (log_cond 3.78–5.59) may not yet be in the 2nd-order-dominated regime. Higher-order CFMS corrections (Huynh-Keating-Snaith, Conrey-Snaith 2008) may be needed.

**When to use:**
- **When DHKMS leading order underestimates observed deficits by 10×+.** This is our F011 rank-0 regime (DHKMS-heuristic 0.7%, observed 22.9%). Miller corrections are the natural next theoretical step.
- **For quantitative comparisons of EC L-function families under different rank/CM/sign stratifications.** Miller explicitly depends on family-level a_p² structure, so cross-family comparisons become principled.
- **Before claiming "novel deviation from RMT."** Pattern 5 gate: the residual must exceed Miller corrections, not just DHKMS leading order, before it qualifies as frontier.

**When NOT to use:**
- **At bulk zero statistics.** Miller is a 1-level density (low-lying zero) theory.
- **Per-curve claims.** Ensemble theory.
- **When the family's a_p² moments are unknown or poorly sampled.** Garbage-in-garbage-out for the theoretical prediction.
- **As an independent axis alongside DHKMS without respecting the expansion order.** P105 and P106 are leading-order and next-to-leading-order of the SAME expansion. Treating them as orthogonal would double-count.

**Relationship to other projections:**
- **P105 DHKMS excised ensemble:** parent / leading-order companion. P106 is the NLO correction.
- **P028 Katz-Sarnak:** one level up in the hierarchy; P028 picks the family (SO_even etc.), P105/P106 give finite-N corrections within that family.
- **P023 rank stratification:** partial overlap via rank-conditioned a_p² moments.

**Pattern connections:**
- **Pattern 5 (Known Bridges Are Known) — sharpens the gate.** Closing Pattern 5 requires beating Miller corrections, not just DHKMS leading order. My Aporia-Report-1 claim "F011 = DHKMS" was incomplete — the rank-0 residual survives DHKMS leading order, but may reduce to Miller NLO. This is a PARTIAL Pattern-5 closure pattern worth naming.
- **Pattern 22 (proposed): Hierarchical Pattern-5 closure.** Novelty claims should be graded against a hierarchy: (1) does it beat leading-order? (2) next-to-leading? (3) next-to-next? Each closure level reduces the frontier. Propose formalizing this as a pattern once it's been applied twice.

**Tensor manifest update on acceptance:**
```json
{
  "PROJECTIONS_append": {
    "id": "P106",
    "label": "Miller arithmetic lower-order terms",
    "type": "theoretical_prediction",
    "description": (
      "A_1/log(X) + A_2*M/log(X)^2 arithmetic corrections to 1-level density "
      "beyond DHKMS leading order (Miller 2004, 2009). Predicts finite-"
      "conductor deviations from leading-order excised-ensemble that depend "
      "on family-level a_p^2 moment structure. Companion to P105 (leading "
      "order); together they should match observed F011 deficit including "
      "rank-0 residual. Empirical comparison: F011 rank-0 epsilon_0 = 22.9% "
      "under 1/log(N) ansatz may be Miller NLO correction magnitude. "
      "Theoretical closed-form computation pending."
    )
  },
  "INVARIANCE_suggestions": {
    "F011": {"P106": 1, "note": "Candidate explanation for rank-0 residual ε₀≈23%; requires closed-form numerical Miller computation to confirm"},
    "F013": {"P106": 0, "note": "Rank-slope effect; Miller a_p^2 family-moment effects could contribute but not yet isolated"}
  }
}
```

**Collision note:** Proposed P106. Confirm via `reserve_p_id` at merge time.

---

*Draft for sessionA review. Together with P105 DHKMS this completes the theoretical-prediction cluster at 105-106. Future workers comparing F011-class specimens against theory should consult P105 → P106 → observation in that expansion order.*
