# Draft catalog entry — MF character parity stratification

**Drafted by:** Harmonia_M2_sessionB, 2026-04-17, tick 4
**Task:** catalog_character_parity
**Status:** Draft, NOT committed to main catalog. Posted as TENSOR_DIFF for sessionA review.
**Target insertion:** Section 4 (Stratifications) in `harmonia/memory/coordinate_system_catalog.md`, after P028 Katz-Sarnak (and after sessionD's MF-weight entry if it takes P029).

**Proposed ID:** P031 (per sessionA REVISION_REQUEST 1776423774297-0 — sessionC's P030 MF level was merged first, so this entry is renumbered P030 → P031). **Double-collision flag:** sessionD's Frobenius-Schur Indicator draft (CORRECTION 1776423778036-0) also proposes P031, with a timestamp-priority argument for sessionD at P031 / sessionB at P032. Resolution deferred to sessionA conductor — if they flip me to P032, re-edit is mechanical.

---

## P031 — MF character parity stratification

**Code:** `WHERE char_parity = 0` (even) vs `WHERE char_parity = 1` (odd) on `lmfdb.mf_newforms`. For Dirichlet L-functions directly: `WHERE char_parity = ...` on `lmfdb.char_dirichlet` (primitive characters only — parity is ill-defined for imprimitive induced characters).
**Type:** stratification (sign-of-functional-equation axis / Γ-factor choice)

**What it resolves:**
- **Archimedean local factor split.** Even characters give Γ_R(s) = π^(-s/2) Γ(s/2); odd give Γ_R(s+1) = π^(-(s+1)/2) Γ((s+1)/2). The functional equation pairs s ↔ 1-s through different shifts, producing distinct low-lying zero densities.
- **Katz-Sarnak low-lying zero predictions by parity.** Even Dirichlet families have SO_even-like lowest-zero distribution; odd have SO_odd-like forced central zero. Even/odd split at the low-lying level — bulk is universal.
- **Möbius/Liouville correlations at the L-function level.** μ (Möbius) and λ (Liouville) are "odd" with respect to parity of Ω (prime-factor count); character parity is the family-level analog. Any correlation between μ or λ and L-function data is expected to stratify by character parity.
- **Rubinstein–Sarnak chebyshev-type biases.** Prime-counting biases (π(x; q, a) for a a non-residue vs a residue) couple to character parity through the explicit formula. This is the foundational parity-sensitive family-level effect.

**What it collapses:**
- **Bulk zero statistics.** Above the unfolding scale, parity is invisible — all families converge to universal GUE.
- **Weight-invariant MF features.** Because for nonzero modular forms of weight k, character parity must equal k mod 2 (forced identity), char_parity stratification in MF without weight conditioning just re-splits weight parity.
- **Features of non-primitive characters.** Induced characters inherit parity from the underlying primitive — applying this stratification to imprimitive L-functions double-counts.

**Tautology profile:**
- **MF char_parity × MF weight parity.** Fully aliased within mf_newforms. Stratifying by char_parity across varying weight is identical to stratifying by weight mod 2. Only independent when conditioned on a single weight (or joint with the weight projection from sessionD's `catalog_mf_weight_draft.md`).
- **char_parity × Katz-Sarnak P028.** For MF and for Dirichlet L-function families, char_parity is one of the coordinates that P028 uses internally to pick SO_even vs SO_odd. Using both P031 and P028 jointly on the same family risks double-reporting. Use one or the other, or apply P028 within a fixed P031 class.
- **char_parity × CM flag (P025).** For weight-1 MF and for CM forms generally, character parity is correlated with the CM-character's parity. Non-independent; control via joint P025 × P031 when probing CM-specific signals.
- **Dirichlet χ(-1) identity.** By construction, char_parity encodes χ(-1). It is NOT an observable derived from zeros — it is a family-definition input. Do not treat "signal resolves under P031" as revealing new structure; it only means the signal respects the functional-equation sign.

**Calibration anchors:**
- **Functional equation Γ-factor structure** (Riemann, Hecke, Weil): the Γ_R / Γ_C factor-pair choice determined by parity is a proved identity, not a conjecture. If a fresh P031 implementation classifies any primitive character wrong, the instrument is broken (Pattern 7 — stop all work).
- **Rubinstein–Sarnak 1994** prime-bias predictions: verified empirically across residue classes modulo small N. An implementation of P031 on a Dirichlet L-function dataset should reproduce their prime-race asymmetries at the expected magnitudes.
- **Weight-char identity for MF newforms.** For every row in `mf_newforms`, `char_parity` must equal `weight % 2`. A deviation is a data-integrity violation, not a finding. Easy SQL check; worth running once.

**Known failure modes:**
- **Applied to MF without joint weight conditioning:** you are not measuring what you think. The signal is weight-parity, not character-parity. Always use `(weight, char_parity)` tuples when the data source is MF.
- **Applied to imprimitive induced characters:** inherited parity creates circular structure.
- **Small-n parity strata.** Some weight × level × character combinations have few instances. Apply Pattern 4 / F012-Liouville discipline: require n ≥ 100 per stratum before publication-grade per-stratum |z|.
- **Parity-aliased-with-rank for EC L-functions via modularity.** Modularity sends weight-2 MF ↔ EC. EC L-function parity (Atkin-Lehner sign) equals MF character parity under this correspondence. Using both as "independent" is a Pattern 1 tautology trap.

**When to use:**
- Any Dirichlet L-function family analysis where you expect parity-sensitive behavior (prime-counting biases, chebyshev biases, low-lying zero densities).
- As an axis of invariance analysis: does the feature resolve through χ(-1) = +1 but not −1, or both, or neither?
- Joint with P028 Katz-Sarnak when you want to separate "symmetry-type signal" from "parity-only signal" — use P031 within each P028 class.
- Cross-family modularity checks: the char_parity of a weight-2 MF must match the sign of the corresponding EC L-function. An identity calibration.

**When NOT to use:**
- MF analysis without joint weight stratification. You will measure weight-parity and think you measured character-parity.
- Bulk zero questions. Parity is a low-lying phenomenon.
- As evidence of novel structure — every parity effect has a classical explanation via the Γ-factor structure. Claims must pass Pattern 5 ("Known Bridges Are Known") explicitly — for character-parity phenomena, the relevant known theory is the explicit formula + Weil's explicit formula + Rubinstein–Sarnak. If your claim reduces to any of these, it is calibration, not discovery.
- On imprimitive characters without projecting to the primitive.

**Pattern 13 / Pattern 18-candidate connection:** Because char_parity is family-level (a property of χ itself, not of objects within the family), adding P031 to a "family-axis exhaustion" ledger is natural. If F011's GUE deficit is ALSO flat under P031 (even vs odd Dirichlet), that is another family-axis kill — further evidence the deficit sits in preprocessing (P051 unfolding) or finite-N structure (H09 conductor-window), not in any family axis.

**Collision note (RESOLVED for MF level, UNRESOLVED for Frobenius-Schur):** Original collision was on P030 vs sessionC's MF level entry — sessionA resolved by renumbering this entry to P031 (sessionC's merge lands first). A second collision exists with sessionD's Frobenius-Schur Indicator draft, which also claims P031 with a timestamp-ordering rationale. Pending sessionA arbitration. The entry content below is identity-correct regardless of which final ID (P031 or P032) is chosen; only the header and INVARIANCE manifest need remapping.

**Tensor manifest updates needed (on acceptance):**
```json
{
  "PROJECTIONS_append": {
    "id": "P031",
    "label": "MF / Dirichlet character parity stratification",
    "type": "stratification",
    "description": "Split by χ(-1) parity (char_parity 0/1). Resolves Γ-factor archimedean split, Katz-Sarnak SO_even/SO_odd class assignment within a parity, Rubinstein-Sarnak chebyshev biases. For MF: aliased with weight mod 2 — always use joint (weight, char_parity). Calibrated by the functional-equation Γ-factor structure (proved)."
  },
  "INVARIANCE_suggestions": {
    "F001": {"P031": 1, "note": "Modularity identity pairs weight-2 MF char_parity with EC Atkin-Lehner sign — calibration anchor."},
    "F011": {"P031": 0, "note": "Untested. Family-axis; under Pattern 13 expected to either resolve F011 low-lying zero structure or join the accumulated-kill ledger."},
    "F014": {"P031": 0, "note": "Not directly applicable; nf_fields doesn't carry an MF character. Skip."}
  }
}
```
