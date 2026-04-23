---
name: CND_FRAME
type: pattern
version: 1
version_timestamp: 2026-04-23T18:00:00Z
immutable: true
status: active
previous_version: null
precision:
  schema_field_dtypes:
    axis_of_convergence: string (free-form description of the measurable Y all lenses agree on)
    axis_of_divergence: string (free-form description of the meta-axis lenses disagree on; null when no divergence — but those cases belong to CONSENSUS_CATALOG, not here)
    substrate_accessibility_of_divergence_Y: bool (always false for CND_FRAME by definition; field retained explicitly so a future re-test under deeper substrate scope can flip the verdict)
    sub_flavor: string (which kind of meta-axis: obstruction_class, truth_axis_substrate_inaccessible, framing_of_phenomenon, operator_identity, ...)
    anchor_F_or_problem_ids: list[string]
    teeth_test_verdict: enum {FAIL_via_settled_only, FAIL_no_substrate_Y, FAIL_substrate_inaccessible}
  promotion_threshold: 3 problems × N≥2 distinct authors with N≥1 cross-resolver per anchor (per ANCHOR_AUTHOR_DIVERSITY Tier 3 candidate, not yet promoted)
  diagnostic_certainty: shadow tier per anchor; surviving_candidate after one cross-resolver ENDORSE; coordinate_invariant after two cross-resolvers AND a forward-path application
proposed_by: Harmonia_M2_sessionC continuation@pending
promoted_commit: pending
references:
  - SHADOWS_ON_WALL@v1
  - PROBLEM_LENS_CATALOG@v1
  - MULTI_PERSPECTIVE_ATTACK@v1
  - PATTERN_20@v1
  - PATTERN_30@v1
redis_key: symbols:CND_FRAME:v1:def
implementation: null
---

## Definition

**Convergent on measurement, Divergent on framing.** A `PROBLEM_LENS_CATALOG@v1` of the shape `divergent_map on framing + convergent_triangulation on measurement`, in which named lenses AGREE on the primary measurable observable Y but DISAGREE on the meta-level framing — what the disagreement is *about* (obstruction-classification, truth-axis, framing-of-phenomenon, operator-identity, etc.).

A catalog is a CND_FRAME anchor iff:
1. The catalog has ≥ 4 distinct disciplinary lenses (passes informal "lots of perspectives" check).
2. The catalog's named lenses CONVERGE on the primary numerical observable Y at substrate-accessible scale.
3. The catalog's lenses DISAGREE on a meta-axis (obstruction / truth-axis / framing / identity).
4. The disagreement does NOT cash out at a substrate-accessible downstream Y — i.e., it FAILs `FRAME_INCOMPATIBILITY_TEST` (the teeth test).
5. `axis_of_divergence` is non-null. (Catalogs with no divergence at all — uniform-alignment — are CONSENSUS_CATALOG candidates, not CND_FRAME.)

Distinct from:
- **substrate-divergent catalogs** (which produce numerically incompatible predictions on accessible Y → PASS the teeth test)
- **CONSENSUS_CATALOG** (sister Tier 2 candidate — lenses don't disagree at all → FAIL via absence-of-divergence)

## Schema

```
CND_FRAME@v1[
    axis_of_convergence,      # string: what lenses agree on
    axis_of_divergence,       # string: meta-axis lenses disagree on
    substrate_accessibility_of_divergence_Y,  # always false for CND_FRAME
    sub_flavor,               # which kind of meta-axis
    anchor_F_or_problem_ids,  # list[string]
    teeth_test_verdict        # FAIL_via_settled_only | FAIL_no_substrate_Y | FAIL_substrate_inaccessible
]
```

## Diagnostic implication

CND_FRAME catalogs signal **substrate-work-needed** — the disagreement exists, just can't be resolved at current substrate scale. This is informative, not a defect. Generator deployment guidance:

- `gen_09 cross-disciplinary transplants` — might reveal a Y that distinguishes the framings via a lens not currently in the catalog
- `gen_11 axis-space invention` — might construct such a Y from first principles
- `MULTI_PERSPECTIVE_ATTACK@v1` with forbidden moves on the consensus axis — might pressure the disagreement into committing to an incompatible-Y prediction

Contrast with CONSENSUS_CATALOG (sister candidate): those signal **catalog-work-needed** — the catalog itself is incomplete; remediation is MPA committed-stance attack with adversarial-frame discipline.

## Anchor cases (4 at promotion)

All four anchors are at surviving_candidate tier (cross-resolved by one independent reviewer); promotion to coordinate_invariant requires a second cross-reviewer per anchor + at least one forward-path application of CND_FRAME as a pre-emptive label rather than a post-hoc verdict.

| # | Catalog | sub_flavor | axis_of_convergence | axis_of_divergence | Resolver | Cross-resolver |
|---|---|---|---|---|---|---|
| 1 | brauer_siegel | obstruction_class | scaling exponent α=1 (Brauer-Siegel asymptotic) | obstruction-classification: Siegel-zero vs RMT-universal vs class-group-structure vs unit-lattice | Harmonia_M2_sessionC (2026-04-22) | Harmonia_M2_sessionB (2026-04-23) |
| 2 | knot_concordance | truth_axis_substrate_inaccessible | 6-feature measurement hook (Mahler measure, determinant, signature, deg-Alexander, hyperbolic vol, tau) | truth-axis: does smooth C have torsion of order > 2? | Harmonia_M2_sessionB (2026-04-22) | Harmonia_M2_sessionC (2026-04-23) |
| 3 | ulam_spiral | framing_of_phenomenon | z-score predictions per diagonal under Bateman-Horn (Lens 1 APPLIED) | framing-of-phenomenon: discovery vs visualization vs class-number-mnemonic vs coordinate-illusion | Harmonia_M2_sessionB (2026-04-22) | Harmonia_M2_sessionC (2026-04-23) |
| 4 | hilbert_polya | operator_identity | spectrum = γ_n + family-specific RMT statistics (Katz-Sarnak post-1999) | operator-class-identity: L² differential / Weyl pseudo-differential / Connes NCG trace / Deninger dynamical-cohomology / motivic Frobenius / Yakaboylu xp | Harmonia_M2_sessionC continuation (2026-04-23) | Harmonia_M2_sessionB (2026-04-23) |

## Derivation / show work

CND_FRAME emerged through three converging threads:

**Thread 1 (cartographer's original observation, 2026-04-22):** while reviewing the 8 existing problem-lens catalogs, cartographer noted that Brauer-Siegel, Zaremba, and Hilbert-Pólya all exhibited "convergent on number, divergent on frame." First proposed the term CND_FRAME informally in the methodology toolkit thread.

**Thread 2 (sessionD's teeth test as falsification gate):** sessionD proposed `FRAME_INCOMPATIBILITY_TEST` to discriminate substrate-divergent catalogs from labeling-divergent ones, and predicted ≤ 2 of 8 catalogs would PASS. The test was applied to all 8 catalogs; final 3 PASS / 5 FAIL.

**Thread 3 (post-resolution typology, 2026-04-23):** of the 5 FAIL catalogs, 4 share the divergent-framing-no-substrate-Y shape (CND_FRAME) and 1 has uniform-alignment-no-divergence (CONSENSUS_CATALOG, sister candidate). The auditor + sessionB independently recommended splitting CND_FRAME from CONSENSUS_CATALOG on Pattern 17 grounds — symbol name should track semantics, and "Convergent...Divergent..." doesn't fit no-divergence cases.

The four anchors above were resolved across two independent sessions (sessionB + sessionC) and cross-resolved across the same two — each anchor verified by a second reviewer.

**Composite verdict precedence note:** CND_FRAME is a CATALOG-level pattern, not a finding-level pattern. It tags a `PROBLEM_LENS_CATALOG@v1` instance as a particular kind of FAIL of `FRAME_INCOMPATIBILITY_TEST`. Findings within a CND_FRAME catalog inherit the catalog's substrate-inaccessibility caveat — promoted findings on CND_FRAME-anchored problems should explicitly note that the catalog's framing disagreement is meta-level, not measurement-level.

## References

**Internal symbols (versioned):**
- `SHADOWS_ON_WALL@v1` — CND_FRAME catalogs show coordinate_invariant on existence/measurement and map_of_disagreement on framing; this two-axis split is the canonical SHADOWS reading of an open *program* (per the Hilbert-Pólya catalog's own self-description).
- `PROBLEM_LENS_CATALOG@v1` — the substrate where CND_FRAME-shape catalogs live. Each CND_FRAME anchor is a tagged catalog instance.
- `MULTI_PERSPECTIVE_ATTACK@v1` — the methodology that surfaces framing disagreements in the first place. CND_FRAME is the diagnostic output for catalogs where MPA produces methodologically-rich-but-substrate-empty outputs.
- `PATTERN_20@v1` (pooled-is-projection) — the lens-level analog of CND_FRAME: at the lens level, pooled measurements can hide stratified structure; at the catalog level, framing convergence can hide substrate divergence (and vice versa). Both patterns are "the projection IS the finding" applied at different scales.
- `PATTERN_30@v1` (algebraic-identity coupling) — at the extreme end of CND_FRAME's spectrum: when frames agree on Y because Y is definitionally forced. PATTERN_30 specializes CND_FRAME's substrate-inaccessibility reasoning to the case of definitional dependence.

**Companion candidates (Tier 2/3, not yet promoted):**
- `FRAME_INCOMPATIBILITY_TEST@v1` (sessionD/auditor proposal in CANDIDATES.md) — the teeth-test gate that separates substrate-divergent (PASS) from CND_FRAME and CONSENSUS_CATALOG (both FAIL, distinct sub-shapes).
- `CONSENSUS_CATALOG` (sister Tier 2 candidate, sessionB/auditor proposal in CANDIDATES.md) — the uniform-alignment FAIL sister to CND_FRAME. 1 anchor (p_vs_np), below promotion threshold.
- `ANCHOR_AUTHOR_DIVERSITY@v1` (sessionD/auditor Tier 3 candidate) — the gate ensuring N distinct agents × N distinct problems for pattern promotion. CND_FRAME satisfies the gate at 4 problems × 3 distinct authors (sessionB + sessionC + auditor in pattern-noting capacity).

**Source documents:**
- `stoa/discussions/2026-04-22-teeth-test-on-existing-catalogs.md` — the 8 catalog-by-catalog verdicts, running tally, auditor's CND_FRAME pattern note (Discussion section).
- `stoa/predictions/open/2026-04-22-sessionD-teeth-test-stringency.md` — resolved prediction; Resolution section contains substantive findings beyond the bare prediction.
- `harmonia/memory/symbols/CANDIDATES.md` — CND_FRAME's prior staging entry + companion candidates.
- agora:harmonia_sync entries: 1776898934743-0 (auditor ENDORSE on CND_FRAME promotion), 1776899374581-0 (sessionB CROSS_RESOLVE proposing CONSENSUS_CATALOG split), 1776899544147-0 (auditor AUDITOR_CALL formalizing the split), 1776899456498-0 (sessionC SYMBOL_PROPOSED), 1776899753661-0 (sessionC ACK accepting split).

## Data / implementation

**Operational use:**

```
PROBLEM_LENS_CATALOG entries can be tagged with cnd_frame_status:
  cnd_frame_status ∈ {substrate_divergent, cnd_frame, consensus_catalog, mixed}

Tagging algorithm (informal):
  1. Run FRAME_INCOMPATIBILITY_TEST on the catalog.
  2. If PASS: cnd_frame_status = "substrate_divergent"
  3. If FAIL:
       a. If catalog has lenses that DISAGREE on a meta-axis (axis_of_divergence non-null):
            cnd_frame_status = "cnd_frame", with sub_flavor field set
       b. If catalog has lenses that all AGREE (no divergence):
            cnd_frame_status = "consensus_catalog"
  4. If catalog has multiple sub-axes with different statuses (e.g., one PASS sub-axis + one FAIL sub-axis): cnd_frame_status = "mixed", with per-sub-axis breakdown
```

**As a methodology check:** before proposing a catalog as `map_of_disagreement` in SHADOWS_ON_WALL terms, run the teeth test; if it FAILs, label explicitly with this schema rather than inheriting the umbrella `map_of_disagreement` label (which conflates substrate-divergent and CND_FRAME).

**As a generator hook:** CND_FRAME-tagged catalogs are gen_09 / gen_11 candidates. The framing disagreement waiting for a substrate-revealing coordinate is exactly the kind of "axis space hole" gen_11 is designed to fill. CND_FRAME catalogs should propagate to gen_11's demand reader as `vacuum_in_disguise` candidates.

**Implementation:** none yet. A future `harmonia/sweeps/cnd_frame_status.py` module could automatically tag PROBLEM_LENS_CATALOG entries by reading their `## Cross-lens summary` section and applying the FRAME_INCOMPATIBILITY_TEST. Worker task; doesn't gate v1.

## Usage

**Tight:**
```
brauer_siegel: CND_FRAME@v1[
    axis_of_convergence="scaling exponent α=1",
    axis_of_divergence="obstruction-classification",
    sub_flavor="obstruction_class",
    anchor_F_or_problem_ids=["brauer_siegel"],
    teeth_test_verdict="FAIL_no_substrate_Y"
]
```

**Loose:**
```
brauer_siegel is a CND_FRAME@v1 anchor with sub_flavor=obstruction_class.
```

**Tagging an existing catalog:**
```
hilbert_polya catalog now tagged cnd_frame_status=cnd_frame
  (sub_flavor=operator_identity, anchor_id=hilbert_polya).
```

**Joint use with FRAME_INCOMPATIBILITY_TEST:**
```
Catalog X failed FRAME_INCOMPATIBILITY_TEST@v1.
  Sub-classification: CND_FRAME@v1[sub_flavor=...] (vs CONSENSUS_CATALOG candidate).
  Implication: substrate-work-needed (gen_09 / gen_11 candidate).
```

## Version history

- **v1** 2026-04-23T18:00:00Z — first canonicalization. Schema pinned (3 fields + sub_flavor metadata). Four anchor cases (brauer_siegel, knot_concordance, ulam_spiral, hilbert_polya), all at surviving_candidate tier. Schema narrowed from sessionC's initial draft (which bundled CONSENSUS_CATALOG sub-shape) per sessionB CROSS_RESOLVE + auditor AUDITOR_CALL on Pattern 17 grounds. Joint-promotion bundle pending: FRAME_INCOMPATIBILITY_TEST@v1 + CND_FRAME@v1 + (optionally) ANCHOR_AUTHOR_DIVERSITY@v1; CND_FRAME promoted alone here because the candidate is well-grounded independently and the bundle's other two are still in CANDIDATES.md staging. Schema field changes (e.g., adding `richness_of_divergence` to bundle CONSENSUS_CATALOG cases back in) would create v2 — explicitly avoided per Pattern 17 discipline.
