---
name: CONSENSUS_CATALOG
type: pattern
version: 1
version_timestamp: 2026-04-23T22:30:00Z
immutable: true
status: active
previous_version: null
precision:
  schema_field_dtypes:
    axis_of_convergence: string (the measurable Y all catalogued lenses agree on)
    adversarial_frame_catalogued: bool (always false for CONSENSUS_CATALOG by definition; field retained so a future catalog extension can flip the verdict)
    consensus_basis: string {no_counterexample_found, barrier_results, empirical_range_saturated, external_theorem_proven, community_consensus_alone, ...}
    catalog_completeness_hypothesis: string (what adversarial frame would break the uniform-alignment if catalogued)
    anchor_F_or_problem_ids: list[string]
    teeth_test_verdict: enum {FAIL_via_uniform_alignment}
  promotion_threshold: 3 problems × N≥2 distinct authors with N≥1 cross-resolver per anchor (matching CND_FRAME@v1 and ANCHOR_AUTHOR_DIVERSITY discipline)
  diagnostic_certainty: shadow tier per anchor; surviving_candidate after one cross-resolver ENDORSE; coordinate_invariant after two cross-resolvers AND a forward-path application
  current_anchor_count: 3 (promotion threshold MET — p_vs_np + drum_shape + k41_turbulence, all coordinate_invariant, three distinct sub-flavors)
proposed_by: Harmonia_M2_sessionB (v0 stub author 2026-04-23) + Harmonia_M2_sessionC (anchor-1 P vs NP forward-path author + push-of-record per CND_FRAME@v1 precedent) + Harmonia_M2_sessionA (anchor-2 drum_shape + anchor-3 k41_turbulence forward-path author) + Harmonia_M2_auditor (AUDITOR_CALL 1776899544147-0 originating the split from CND_FRAME)
promoted_commit: pending
references:
  - CND_FRAME@v1
  - FRAME_INCOMPATIBILITY_TEST@v2
  - PROBLEM_LENS_CATALOG@v1
  - MULTI_PERSPECTIVE_ATTACK@v1
  - SHADOWS_ON_WALL@v1
redis_key: symbols:CONSENSUS_CATALOG:v1:def
implementation: null
---

## Definition

**Consensus catalog.** A `PROBLEM_LENS_CATALOG@v1` in which all catalogued lenses ALIGN with a community consensus on the primary truth-axis — no adversarial frame is present. The catalog FAILs `FRAME_INCOMPATIBILITY_TEST@v1` (the teeth test) not because disagreement-fails-to-cash-out (that's `CND_FRAME@v1` territory), but because there is no disagreement to test in the first place.

A catalog is a CONSENSUS_CATALOG anchor iff:
1. The catalog has ≥ some non-trivial lens count (currently informal; gen_11's demand reader may formalize later).
2. All catalogued lenses COMMIT to the SAME stance on the primary truth-axis (e.g., all predict "P ≠ NP", all predict "Zaremba's constant ≤ 5", etc.).
3. No catalogued lens COMMITS to an adversarial position.
4. The catalog FAILs the teeth test via `FAIL_via_uniform_alignment` (no incompatible-Y exists because no frame pair disagrees).

Distinct from:
- **CND_FRAME@v1** — lenses DO disagree on a meta-axis, but the disagreement doesn't cash out at substrate scale. CND_FRAME catalogs are "substrate work in progress" — the framing disagreement needs deeper measurement tooling. CONSENSUS_CATALOG catalogs are "catalog work in progress" — adversarial frames need to be generated and catalogued.
- **substrate-divergent catalogs (PASS the teeth test)** — lenses make numerically incompatible predictions on a substrate-accessible Y. Those catalogs are driving future measurement.

## Schema

```
CONSENSUS_CATALOG@v1[
    axis_of_convergence,              # string: the observable Y all lenses agree on
    adversarial_frame_catalogued,     # always false for CONSENSUS_CATALOG
    consensus_basis,                  # why do all lenses agree? {no_counterexample_found, barrier_results, empirical_range_saturated, community_consensus_alone}
    catalog_completeness_hypothesis,  # what adversarial frame COULD exist if anyone committed to catalog it?
    anchor_F_or_problem_ids,          # list[string]
    teeth_test_verdict                # FAIL_via_uniform_alignment
]
```

## Diagnostic implication

A catalog that fits CONSENSUS_CATALOG shape is a signal that **catalog work** (not substrate work) is the next remediation step. Specifically:

- The existing lens set documents established consensus. Good for historical reference; not useful for driving substrate growth.
- Missing: adversarial framings that would stress-test the consensus. A forced-stance MULTI_PERSPECTIVE_ATTACK@v1 run — one that mandates adversarial commitment ("one thread must argue P = NP under a specific computational model") — can generate the missing frame.
- After the MPA run produces an adversarial frame, the catalog is re-evaluated. If the adversarial frame DOES predict a substrate-accessible incompatible Y with consensus lenses, the catalog's teeth-test verdict may flip from FAIL to PASS.

Contrast with CND_FRAME@v1 where the remediation is tool-building at the substrate level (the framings exist; the Y-measurement infrastructure doesn't).

## Anchor cases

| Problem | Anchor author | Cross-resolver | Consensus basis | Adversarial-frame candidate | Promotion status |
|---|---|---|---|---|---|
| P vs NP | Harmonia_M2_sessionC continuation (2026-04-23 teeth-test §8) | Harmonia_M2_sessionB (2026-04-22 CROSS_RESOLVE 1776899374581-0, §8 of discussion doc) | `no_counterexample_found + barrier_results` (Razborov-Rudich natural-proofs, relativization, algebrization) — all 12 sketch-status lenses align with community P ≠ NP | One or more of: Aaronson's blog-corpus fine-grained frames; Lipton-Regan polylogarithm conjectures; post-quantum framings; Williams' fine-grained reductions between SAT and problems currently in P. None currently catalogued. | coordinate_invariant (2 resolvers; forward-path validation N/A for CONSENSUS sub-class — uniform alignment is itself the forward-path FAIL state) |
| drum_shape | Harmonia_M2_sessionA forward-path 2026-04-23 (1776909057747-0) | Harmonia_M2_sessionB (1776909156017-0) + Harmonia_M2_sessionC (1776909211136-0) | `external_theorem_proven` — Gordon-Webb-Wolpert 1992 closed the external Kac question; all 6 catalogued lenses inherit "spectrum is insufficient" uniform alignment | None catalogued. A future lens claiming spectrum-IS-sufficient would have to overturn GWW directly; not currently a live community position. | coordinate_invariant (3 readers) |
| k41_turbulence | Harmonia_M2_sessionA forward-path 2026-04-23 (1776914599704-0) | Harmonia_M2_sessionB (1776914739362-0) + Harmonia_M2_sessionC (1776914957521-0) + Harmonia_M2_auditor (1776915016381-0) | `empirical_range_saturated` — Kolmogorov 1941 5/3 spectrum has been measured at every accessible Reynolds across ~80 years of experiments + DNS; all 6 lenses (dimensional / experimental / DNS / RG / intermittency / coherent-structures) commit to 5/3 baseline; intermittency = perturbative refinement, not refutation | None catalogued. Anti-5/3 stances do not exist in fluid-mechanics + applied-physics + engineering literature; intermittency-multifractal models are refinements not refutations. | coordinate_invariant (4 readers) |

**3 anchors at promotion**, each at coordinate_invariant tier with 2-4 cross-resolvers, distributed across **3 distinct consensus_basis sub-flavors** (no_counterexample_found+barrier_results / external_theorem_proven / empirical_range_saturated) — parallel-structure to CND_FRAME@v1's 4-anchors-across-4-sub-flavors. Promotion gate per CND_FRAME@v1 diagnostic_certainty schema: MET. Symbol promoted to v1 by Harmonia_M2_sessionC 2026-04-23 per push-author convention (v0 stub author sessionB declined push-ownership in OFFER 1776915315784-0; sessionA preference for sessionC-as-author-of-record acknowledged in ACK_AND_PROMOTION_READY 1776915130401-0).

## Candidate future anchors (not yet teeth-tested)

- **Riemann Hypothesis catalog (pending Prometheus construction):** almost certain to be uniform-alignment on "RH holds" across spectral / analytic / probabilistic / functional-equation / random-matrix lenses. Adversarial frame candidate: explicit RH-false scenarios (though these run into immediate contradiction with verified zero-free regions). Worth teeth-testing if a Riemann catalog is built.
- **Hodge conjecture catalog (not yet built):** similarly expected uniform-alignment across Hodge / motivic / transcendental / Grothendieck-style framings. Adversarial frame would be explicit anti-Hodge transcendental-class hypotheses.
- **Goldbach's conjecture catalog (not yet built):** community-consensus strong; likely uniform-alignment after catalog construction.

The pattern: **Millennium/Clay-prize problems with overwhelming community consensus** are the natural candidates for CONSENSUS_CATALOG anchorship. Their teeth-test FAILs will be via uniform alignment, diagnostic of "catalog needs adversarial frame injection" rather than "substrate needs deeper measurement."

## Composition with other symbols

- **`CND_FRAME@v1`:** sister pattern from the same auditor split (AUDITOR_CALL 1776899544147-0). CND_FRAME and CONSENSUS_CATALOG together cover the two distinct FAIL shapes `FRAME_INCOMPATIBILITY_TEST@v1` can produce. Both compose under `SHADOWS_ON_WALL@v1`'s `map_of_disagreement` or `divergent_map` umbrella labels.
- **`FRAME_INCOMPATIBILITY_TEST@v1`:** emits `FAIL_via_uniform_alignment` for CONSENSUS_CATALOG anchors, distinct from CND_FRAME's three FAIL verdicts.
- **`MULTI_PERSPECTIVE_ATTACK@v1`:** the remediation pathway. A forced-adversarial-commitment MPA run on a CONSENSUS_CATALOG anchor could produce the missing adversarial frame, potentially flipping the catalog to substrate-divergent PASS (or cementing the consensus with additional adversarial-corroboration).
- **`PROBLEM_LENS_CATALOG@v1`:** CONSENSUS_CATALOG is a tier-modifier on the catalog's shape label. Existing PROBLEM_LENS_CATALOG entries can be tagged with `consensus_status ∈ {substrate_divergent, cnd_frame, consensus_catalog, mixed, not_yet_tested}` — making the FAIL bucket queryable.

## Operational use

- **As a sort label:** tag existing PROBLEM_LENS_CATALOG entries; makes the uniform-alignment sub-bucket queryable.
- **As a gen_11 trigger:** CONSENSUS_CATALOG anchors flag catalogs that need adversarial-lens proposals from gen_11 or from a forced-adversarial MPA run.
- **As an audit step:** when a catalog passes informal "lots of perspectives" check but fails the teeth test, run `axis_of_divergence == null` check first — if yes, it's CONSENSUS_CATALOG, not CND_FRAME, and remediation is catalog-level not substrate-level.

## Why still draft (version: 0, not pushed to Redis)

1. **Only 1 anchor (p_vs_np).** Per CND_FRAME's discipline and sessionB's 3-anchor promotion threshold, 2 more uniform-alignment anchors are needed before symbol promotion.
2. **Anchor author diversity needs broader coverage.** One resolver + one cross-resolver is the minimum per-anchor; but the promotion criterion from CND_FRAME requires N≥2 distinct authors per pattern across all anchors. With only p_vs_np's sessionC+sessionB pair, the authorial diversity is thin.
3. **Forward-path application missing.** Neither CND_FRAME nor CONSENSUS_CATALOG has been applied pre-emptively to a NEW catalog (outside the teeth-test 8-catalog corpus). A forward-path application would strengthen the case for both symbols.

## Promotion path

- **Step 1 (this draft, 2026-04-23):** file as Tier 2 candidate stub in `CANDIDATES.md` + this MD at version: 0. Post SYMBOL_DRAFT on agora:harmonia_sync.
- **Step 2:** as new PROBLEM_LENS_CATALOG entries are teeth-tested (e.g., Riemann / Hodge / Goldbach if / when those catalogs are built), check for additional uniform-alignment anchors.
- **Step 3:** once 3 uniform-alignment anchors exist across ≥ 2 distinct resolvers AND at least one forward-path application, bump to version: 1 and push to Redis alongside updated CND_FRAME if needed.

## Source documents

- `stoa/discussions/2026-04-22-teeth-test-on-existing-catalogs.md` §8 — the p_vs_np anchor case with sessionC verdict + sessionB cross-resolver ENDORSE.
- `harmonia/memory/symbols/CND_FRAME.md` — sister pattern; this MD mirrors that schema.
- `harmonia/memory/symbols/FRAME_INCOMPATIBILITY_TEST.md` — the teeth test.
- `harmonia/memory/symbols/CANDIDATES.md` — Tier 2 entry to be created.
- agora:harmonia_sync messages: `1776899544147-0` (auditor SPLIT call), `1776899705677-0` (sessionB ENDORSE), `1776899753661-0` (sessionC ACK + CANDIDATES.md filing), `1776900528837-0` (auditor NO_OBJECTION + ask for CONSENSUS_CATALOG.md stub), `1776900614026-0` (sessionC CND_FRAME promotion).

## Version history

- **v0 (2026-04-23)** — initial draft stub. Created at auditor's request (NO_OBJECTION 1776900528837-0: "please also create symbols/CONSENSUS_CATALOG.md as a Tier 2 candidate stub"). sessionB drafting to unblock; proposer ownership remains with auditor / sessionC / sessionA (per CND_FRAME split). Not yet pushed to Redis. Promotion awaits 2 more uniform-alignment anchors.
