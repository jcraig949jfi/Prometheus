# F011 in the Void-Detection Framework — Appendix Draft

**Audience:** Discussion section of the F011 paper.
**Author:** Aporia.
**Purpose:** Frame the F011 investigation (bulk rigidity + Sp uniqueness) as an instance of the project's void-detection methodology, making the paper's methodological story explicit.

---

## The Void-Detection Framework

Aporia's role in the Prometheus team is to detect "voids" in the mathematical landscape — places where structure should exist but doesn't, OR where observed structure differs from theoretical prediction. The framework identifies five strategies for finding voids:

1. **V1 Constraint Triangle Closure.** If domain A couples to B and B couples to C, expect A to couple to C. Deficits predict voids.
2. **V2 Feature Space Density Gaps.** In high-dimensional feature space, regions with predicted density but observed absence are candidate "missing objects" (Mendeleev-style).
3. **V3 Strategy Group Disagreement.** Multiple measurement strategies applied to the same objects can disagree; disagreement signals missing structure.
4. **V4 Spectral Gap Analysis.** Gaps in the coupling-matrix eigenvalue spectrum predict missing measurement modalities.
5. **V5 Sleeping Beauty Frequency Sweep.** High-internal-structure / low-external-connectivity objects (e.g. OEIS sequences) may be broadcasting at uncaptured frequencies.

The F011 investigation — EC rank-0 L-function zero statistics anomalies — emerged initially as an entry in Aporia's void catalog: "14% GUE deficit, no mechanism" (circa 2026-04-16).

---

## The F011 Arc as a V4 Spectral-Gap Instance

F011 belongs to V4 (Spectral Gap Analysis). The tensor's coupling framework uses "matched GUE" as a universality reference. Observing that rank-0 EC L-functions deviate from this reference predicts either (a) a missing measurement modality the tensor can't express, or (b) real structure beyond what universality predicts.

Over one session, the investigation moved through the following stages, each driven by a cross-check:

| Stage | Reframe | Trigger |
|-------|---------|---------|
| T0 | "14% GUE deficit, no mechanism" (initial void entry) | Opening |
| T7 | "resolved as finite-N correction" | Ergon matched-simulation |
| T13 | "not finite-N — structural compression at multiple gaps" | Matched-null cross-check |
| T18 | "Euler-product channels (CM, torsion) modulate compression" | CM/tor stratification |
| T32 | "V-GAMMA sub-void: Q(√-3) non-maximal orders invert gradient" | Charon shape taxonomy |
| T45 | "gap1 vs gap4 are DIFFERENT REGIMES (Euler-arithmetic vs asymptotic)" | Seed 2 24-gap scan |
| T50 | "Sp symmetry class emerges as unique negative per-curve ρ" | Ergon nbp cross-family |
| T53 | "Universal bulk deficit +46-51% across 3 Katz-Sarnak classes" | G2C USp(4) completion |
| T57 | "Axis 3b = per-curve resolution of Katz-Sarnak 2-point correction sign" | Charon KS 1999 Sec 3.3 |
| T73 | "Sp UNIQUELY negative across 5 families; U beyond KS at per-curve" | Dirichlet complex+real |

Each stage refined the void's scope — from "unknown mechanism" to "beyond classical RMT, per-curve arithmetic modulation, Sp uniquely reverses direction."

---

## How Void-Detection Produced the Paper

Three features of the void-detection methodology drove the result:

**1. Matched null preconditions (PATTERN_NULL_CONSTRAINT_MISMATCH).**

Early in the investigation, we used "GUE with global normalization" as the universality reference. Ergon's matched-local-normalization GUE simulation showed this was the wrong null; the real deviation emerged against a matched-GUE with local-4-gap constraint. This forced the reframing from "finite-N correction" to "structural compression."

**2. Scope-matrix discipline (PATTERN_SELECTION_BIAS).**

BSD-1646 (curated verification subset) showed nbp Spearman ≈ 0; Ergon's random 150K showed ≈ +1.0. The curated subset was unrepresentative. Without the scope-matrix discipline, we would have reported the curated-subset result as the universal finding.

**3. Literature reframing (PATTERN_LITERATURE_REFRAME).**

Initially F011 was treated as a mystery ("14% GUE deficit"). Charon's literature check pinned rank-0 EC as O+(2N) family (Iwaniec-Luo-Sarnak 2000) and identified Katz-Sarnak 2-point correction signs from KS 1999 Sec 3.3. This transformed part of the "mystery" into classical confirmation and isolated the residual as the genuine novel finding.

---

## Voids Converted to Findings

The F011 investigation converted a single void-list entry into multiple distinct outcomes:

- **Axis 1 (CONFIRMED):** Classical Katz-Sarnak 1-level density signature verified to 0.2% (ratio 1.72 matches theory 1.71, z = +249).
- **Axis 2 (NEW):** Family-specific edge-spacing signatures differ across O+, U (CM), and USp(4) even under family-correct nulls.
- **Axis 3a (NEW):** Universal bulk rigidity (+46-51% at k=24) across all tested Katz-Sarnak classes — a cross-family invariant absent from standard compact-group RMT.
- **Axis 3b (NEW):** Per-curve arithmetic modulation of bulk rigidity, with nbp Spearman sign matching Katz-Sarnak 2-point correction sign (+ for Orthogonal, − unique for Symplectic, + for Unitary despite zero KS correction — the Unitary case is a beyond-theory per-curve signal).
- **V-GAMMA sub-void (NEW):** Q(√-3) non-maximal orders uniquely invert the gap-index gradient.
- **Per-disc gap profile (NEW):** CM family 1-level ruler shows clean hierarchy by D_K × order conductor.

These are CHARACTERIZED rather than merely killed — each outcome is a quantitative law, a fingerprint, or a classical confirmation.

---

## Seven Methodological Patterns Logged for Kairos

Each stage of the reframing exposed a methodological trap. Seven preconditions are proposed for the Kairos catalog (see separate document `aporia/docs/kairos_proposed_patterns_20260422.md`):

1. `PATTERN_NULL_CONSTRAINT_MISMATCH` — matched-constraint nulls are required.
2. `PATTERN_KILL_UNDER_CONSTRAINED` — 2/3 independent tests before any F-cell kill.
3. `PATTERN_PREDICTION_LEVEL_MISMATCH` — pre-register at measurement level, not estimator level.
4. `PATTERN_SELECTION_BIAS` — curated subsets must be cross-checked against random samples.
5. `PATTERN_NORMALIZATION_SIGN_FLIP` — statistics can flip sign under different normalizations.
6. `PATTERN_LITERATURE_REFRAME` — check family-correct universality before declaring a void.
7. `PATTERN_MEASUREMENT_CHANNEL` — different RMT statistics expose different features.

These patterns are the session's methodological deliverable. They generalize beyond the F011 investigation to any future void.

---

## How the Paper Is Structured Around This Framework

- **Abstract + Introduction:** State the 4-axis result + situate in Katz-Sarnak literature.
- **Methods:** Data sources, matched-null construction, family identification.
- **Results:** 3 Axes (1 classical confirmation, 2 novel findings).
- **Discussion:** Open questions (Why Sp uniquely negative? What explains the Unitary beyond-theory signal?), connection to BSD/CM/Sato-Tate theory.
- **Appendices:**
  - Scope matrix (curated vs random sampling)
  - Methodological patterns (the 7 above)
  - V-GAMMA sub-finding (Q(√-3) gradient inversion)
  - This appendix (void-detection framework)

---

## Takeaway for the Reader

The F011 paper is not simply a spacing-statistics finding. It is an EXAMPLE of what the void-detection methodology produces when operated at target: single void-list entries get converted into characterized laws + sub-findings + methodology patterns + open theoretical questions. The Prometheus team's void-detection plus cross-check + consensus loop was the engine that generated the result.

The BULK RIGIDITY finding itself is paper-worthy; the METHODOLOGY that produced it is reusable.

---

*Aporia, 2026-04-23. Draft appendix for F011 paper discussion.*
