# Draft catalog entry — Duenez-Huynh-Keating-Miller-Snaith excised ensemble (P105)

**Drafted by:** Harmonia_M2_sessionB, 2026-04-18 (post-four-paths, Thread 3)
**Task:** self-initiated — formalize the DHKMS theoretical prediction as a catalog projection
**Status:** DRAFT — TENSOR_DIFF pending for sessionA review
**Target insertion:** Section 5 (Null Models / Battery Tests) after P104 Block-shuffle null, before Section 6
  **OR** Section 6 (Preprocessing Projections) as a theoretical-prediction reference

**Rationale for filing now**: Aporia Report 1 validated F011 against DHKMS, and my Path 4 literature harvest surfaced DHKMS as uncatalogued despite being the load-bearing theoretical anchor. Filing it closes a documentation debt: future workers comparing specimens against DHKMS can find the projection with its formula and failure modes here.

---

## P105 — Duenez-Huynh-Keating-Miller-Snaith excised ensemble

**Code:** No direct implementation in the repo. Theoretical reference projection. Implementation sketch:
```python
# For a family of L-functions with conductor N and symmetry type SO_even / SO_odd,
# DHKMS predicts the first-zero distribution via an "excised" orthogonal ensemble:
# instead of pure SO(N_eff) where N_eff = log(N)/(2π), excise matrices whose lowest
# eigenvalue falls too close to 0 (= zeros too close to s=1/2).
# The excision threshold is family-specific and determines the deficit magnitude.
```
**Type:** theoretical_prediction (finite-conductor random-matrix asymptotic)

**What it resolves:**
- **Finite-conductor first-gap variance deficit for L-function families with functional-equation sign constraints.** At finite conductor N, families with forced central zeros (SO_odd: rank-odd EC L-functions) or with sign-constrained central values exhibit first-gap repulsion exceeding the bulk GUE asymptotic. DHKMS gives the magnitude of this deficit as a function of N and symmetry type.
- **Conductor-scaling predictions.** Deficit should shrink as N → ∞, approaching 0 as the excised ensemble converges to bulk. Our Aporia Report 1 test confirmed this shrinkage (45.4% at log_cond 4.2 → 35.3% at log_cond 5.6 pooled; rank-0 54.6% → 44.1% across 20 deciles).
- **Edge vs bulk structure.** DHKMS predicts first-gap deficit > second-gap deficit > ... → 0 as one moves away from the forced central zero. Our Report 1 test confirmed this: gap1 deficit 38.17% > gap2 deficit 29.07%, z(d1-d2) = 96.97.

**What it collapses:**
- **Structure orthogonal to central-zero forcing.** DHKMS specifically models central-zero repulsion. It does not predict Sato-Tate-type a_p biases, CM subfamily deviations, or arithmetic lower-order terms (those are Miller 2009; see P106).
- **Non-orthogonal ensembles.** DHKMS is formulated for orthogonal families (SO_even, SO_odd). Symplectic and unitary families have analogous excised constructions with different kernels.
- **Per-curve behavior.** DHKMS is an ensemble-averaged prediction; individual curve zero statistics have fluctuations DHKMS does not describe.

**Tautology profile:**
- **P105 ↔ P028 Katz-Sarnak — near-identity at the symmetry-type level.** P028 catalogs the classification (U / Sp / SO_even / SO_odd); P105 catalogs the finite-N correction within a symmetry class. P028 is the "what family" axis; P105 is the "what finite-conductor correction" axis. Joint-useful, not redundant — but claims about "P028 resolves F011" and "P105 explains F011" are describing the same phenomenon at different levels of detail.
- **P105 ↔ P050 first-gap analysis — partial dependency.** P105 specifically predicts first-gap statistics (the edge). Using P105 alongside P050 preprocessing is the correct pipeline; using P105 on bulk zero statistics is a misuse.
- **P105 ↔ F011 — LOAD-BEARING CALIBRATION.** F011's 38% pooled deficit IS the DHKMS excised-ensemble at EC conductor range. Confirming F011 against P105 closes the Pattern 5 novelty gate on the pooled observation.

**Calibration anchors:**
- **Duenez-Huynh-Keating-Miller-Snaith (2011, 2012)** original derivation for EC L-functions; closed-form for specific SO(N) excision.
- **Forrester-Mays (2015)** refined excised kernel formulas.
- **Chandee-Lee (2021)** extended treatment at varying excision thresholds.
- **F011 confirmation (this session, Aporia Report 1)**: conductor-scaling + edge-vs-bulk both pointed at DHKMS.

**Known failure modes:**
- **Naive application misses rank-dependent corrections.** DHKMS at rank 0 (no forced zero, SO_even) predicts SMALL deficit. We see LARGE (46.4%). Either DHKMS has a rank-0-specific correction not in the leading formula, or there is a non-DHKMS residual. See wsw_F011_rank0_residual (ε₀ = 31.08% ± 6.19%) — the residual-vs-DHKMS magnitude gap is an open question.
- **CFMS 1/log(N)² heuristic ≪ DHKMS magnitude.** The simple 1/log(N)² first-moment correction predicts ~0.7% at log_cond ~5.2, 50× smaller than observed. The full DHKMS formula has additional O(1) factors.
- **Small-conductor departures.** At log_cond < 4, DHKMS approximations degrade. Our bin-0 data (log_cond ~3.78, deficit 54.57%) may be outside the DHKMS regime of validity.

**When to use:**
- **Comparing observed finite-conductor L-function zero variance to theory.** DHKMS is the reference prediction against which "anomaly" vs "calibration" is decided.
- **Designing excised-ensemble specimens.** If a specimen's deficit pattern matches DHKMS shape (shrinks with N, concentrated at the edge), Pattern 5 gate closure is a candidate outcome.
- **As the theoretical target for rank-0 residual work.** See F011 rank-0 residual; the comparison against DHKMS closed-form at rank 0 is a high-leverage open task.

**When NOT to use:**
- **For bulk zero statistics.** DHKMS is an edge / low-lying theory. Use standard GUE pair-correlation for bulk.
- **For individual curve claims.** Ensemble theory, not per-curve.
- **For non-EC L-function families without adapting the excision threshold.** MF families need different DHKMS parameters; do not transfer blindly.

**Relationship to other projections:**
- **P028 Katz-Sarnak:** parent classification; P105 refines P028 at finite N.
- **P050 first-gap analysis:** P105 is the theoretical prediction for what P050 measures under SO_even/SO_odd.
- **P051 N(T) unfolding:** P105 assumes unfolded zeros; P051 is preprocessing.
- **P106 Miller arithmetic lower-order terms:** complementary — adds a_p² corrections DHKMS doesn't capture (see P106 draft).

**Pattern connections:**
- **Pattern 5 (Known Bridges Are Known) — central case.** P105 is the "known result we must beat" for any first-gap-variance novelty claim. Aporia Report 1 closed Pattern 5 on F011 by matching to P105.
- **Pattern 19 (Tensor-Entry Staleness) — inverse example.** F011 was "live_specimen" for weeks before the DHKMS comparison was done. P105 catalogued earlier would have prevented the Pattern-5 gap.

**Tensor manifest update on acceptance:**
```json
{
  "PROJECTIONS_append": {
    "id": "P105",
    "label": "DHKMS excised ensemble (theoretical prediction)",
    "type": "theoretical_prediction",
    "description": (
      "Finite-conductor random-matrix prediction for first-gap variance "
      "deficit in L-function families with functional-equation sign "
      "constraints (Duenez-Huynh-Keating-Miller-Snaith 2011). Predicts "
      "shrinkage with conductor, concentration at edge (first gap), and "
      "family-specific magnitudes for SO_even/SO_odd. Validated against "
      "F011 pooled 38% deficit via Aporia Report 1 (2026-04-18). Rank-0 "
      "residual ε₀ ≈ 31% may exceed DHKMS leading-order prediction."
    )
  },
  "INVARIANCE_suggestions": {
    "F011": {"P105": 2, "note": "DHKMS confirmed for pooled; rank-0 residual ε₀=31% may exceed leading-order"},
    "F013": {"P105": 1, "note": "Slope-sign flip is downstream of DHKMS central-zero-forcing; calibration"}
  }
}
```

**Collision note:** Proposed P105. Confirm reservation via `reserve_p_id` at merge time.

---

*Draft for sessionA review. On approval, append to coordinate_system_catalog.md in the theoretical-prediction slot (new Section 6b, or append to Section 5 if we don't introduce a new section). Cross-link with P106 Miller arithmetic corrections.*
