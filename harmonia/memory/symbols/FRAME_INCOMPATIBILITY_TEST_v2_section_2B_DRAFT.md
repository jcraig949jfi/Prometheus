---
section: 2.B (core-unit formal definitions)
parent_amendment: FRAME_INCOMPATIBILITY_TEST@v2 amendment 2026-04-23
author: Harmonia_M2_sessionC
status: DRAFT (awaiting team review + merge into FRAME_INCOMPATIBILITY_TEST_v2_DRAFT.md per sessionA V2_STRUCTURE_PROPOSAL 1776907568836-0)
---

## 2.B Core-unit formal definitions

The v1 spec referred to "lenses," "catalogs," "observables," and "resolution" as if they were primitives, but each of these terms hides definitional choices that the cataloguer makes implicitly. Multiple v1.1 probe seeds (sessionA Probe-2 #2, Opus #4, Gemini #1) flagged this as an under-specification that lets adversarial cataloguers steer verdict outcomes. v2 promotes these four terms (plus a fifth, "resolution") to formally-defined units with required schema fields.

### Definition 2.B.1 — Catalog

A **catalog** is a `PROBLEM_LENS_CATALOG@v1` instance — a markdown file at `harmonia/memory/catalogs/<problem_id>.md` with frontmatter declaring `problem_id`, `surface_statement`, `version`, and (post-this-amendment) `cnd_frame_status` + `teeth_test_*` fields. The catalog body contains: `## What the problem is really asking` (sub-question decomposition), `## Data provenance`, `## Lens catalog (N entries)`, and `## Cross-lens summary`.

A catalog is **eligible for FRAME_INCOMPATIBILITY_TEST application** iff: (a) lens count ≥ 4 (informal "lots of perspectives" check), (b) at least one lens has status in {APPLIED, PUBLIC_KNOWN} (a committed measurement exists, either via Prometheus-internal MPA run OR via external peer-reviewed literature — both satisfy the spirit of "catalog has at least one committed-measurement lens"), AND (c) the surface_statement names a measurable observable (i.e., is not purely philosophical). Catalogs failing eligibility are not assigned a teeth-test verdict; they remain `not_yet_eligible`.

**Grandfather clause for v1-vintage corpus (per auditor end-to-end review 1776908486097-0):** catalogs that received teeth-test verdicts BEFORE v2 ship date under v1-vintage criteria retain those verdicts and are NOT subject to retroactive eligibility re-check. v2 criteria apply forward-only to NEW catalog-verdict pairs. The 10 catalogs already verdicted (8-corpus + irrationality_paradox + knot_nf_lens_mismatch as of v2 ship) are grandfathered. This preserves substrate progress (especially Zaremba's coordinate_invariant tier with Track D replication) while keeping v2 discipline strict for future work. SessionB concurs (1776908574036-0).

*Eligibility-criterion-b fix log (2026-04-23):* initial draft required APPLIED-only, which would have retroactively disqualified 4 of 8 corpus catalogs (Brauer-Siegel, Zaremba, knot_concordance, p_vs_np all have APPLIED=0). SessionB caught the over-strict reading (1776908351842-0); auditor recommended grandfather clause (1776908486097-0) as cleaner solution than blanket relaxation. Adopted both: relaxation as the going-forward rule + grandfather clause as the v1-vintage preservation. Stricter alternative (any lens commits a measurable prediction on substrate-scale Y) flagged for v3 once `committed_Y` becomes a frontmatter field.

### Definition 2.B.2 — Lens

A **lens** is a single entry in the `## Lens catalog` section of a catalog. Each lens has a frontmatter-equivalent block in markdown declaring:
- `discipline`: the disciplinary tradition the lens inherits from (e.g., "Diophantine approximation," "spectral graph theory," "gauge theory"). Required.
- `description`: prose explaining what the lens measures. Required.
- `status`: one of `{APPLIED, PUBLIC_KNOWN, PROPOSED, NEW, BLEND, SKIP}`. Required.
- `committed_Y`: the observable Y the lens predicts on (see Definition 2.B.4 below). Required iff `status ∈ {APPLIED, PUBLIC_KNOWN, PROPOSED}`. May be null for BLEND or SKIP.
- `prediction`: the lens's stated value or class for `committed_Y`. Required iff `committed_Y` is non-null. May be a numerical value, a numerical range, an asymptotic class (e.g., "polynomial decay"), or a binary/categorical commitment ("YES / NO").
- `tier_contribution`: bool — does this lens contribute to the catalog's SHADOWS_ON_WALL tier classification? Default true.

A lens **without a `committed_Y`** is silent — it offers a measurement protocol or a framing but does not commit to a prediction. Silent lenses do not participate in teeth-test classification (see 2.C admission criteria silence-vs-disagreement clause).

### Definition 2.B.3 — Problem

A **problem** is the open question or research target that the catalog is built around. It is operationalized as the catalog's `surface_statement` field plus the `## What the problem is really asking` sub-decomposition (typically 3–7 sub-questions). The surface_statement may be in lay phrasing; the sub-decomposition refines toward measurable form.

A problem is **substrate-decomposable** iff at least one sub-question names a measurable observable Y and at least two lenses commit predictions on that Y. Problems that are not substrate-decomposable are eligible only for the CONSENSUS_CATALOG / non-substrate FAIL classification path; the PASS / CND_FRAME / Y_IDENTITY_DISPUTE branches require substrate-decomposability.

### Definition 2.B.4 — Observable Y

An **observable Y** is a quantity that a lens commits a prediction to. v2 requires Y to satisfy four properties:

1. **Identity stability**: Y is named with a definitional reference that two readers from different disciplines would agree refers to the same quantity (modulo notation). Example: "asymptotic exponent α such that count(q, A=5) ~ q^α" satisfies identity stability via the functional definition. "Mahler measure of the polynomial associated with knot K" does NOT satisfy identity stability — different disciplines disagree on which polynomial is "associated with" the knot (Alexander vs A-polynomial — see knot_nf_lens_mismatch as Y_IDENTITY_DISPUTE anchor).

2. **Measurability standard** (per 2.C): Y is measurable at substrate scale within a stated parameter range, with a stated zero-handling / regression-method / numerical-precision protocol. Per sessionC Track D lesson (1776902495482-0): identical (algorithm, range, zero-handling) tuple is required for cross-implementation byte-equivalence. v2 mandates the tuple be pinned in SIGNATURE@v2.

3. **Prediction granularity**: Y admits at least two distinguishable values that lenses can predict — binary (YES/NO), ordinal (low/medium/high or similar), or continuous (numerical with stated precision). Predictions that are "consistent with X" without ruling anything out are silence, not commitment.

4. **Falsifiability at scale**: at least one of the predictions on Y can be falsified by a measurement at currently-accessible substrate scale, OR the prediction can be downgraded / qualified per the live-vs-historical clause if the resolution requires beyond-substrate-scale data.

Y candidates that satisfy 1+2+3+4 are **substrate-Y**. Y candidates failing identity stability are **disputed-Y** and trigger Y_IDENTITY_DISPUTE classification (see 2.A enum). Y candidates failing measurability or falsifiability are **non-substrate-Y** and trigger CND_FRAME classification.

### Definition 2.B.5 — Resolution

A Y is **resolved** when a measurement at substrate scale produces a value (or value range) that distinguishes at least two of the lens predictions on Y. Resolution requires:
- A measurement procedure pinned to the (algorithm, range, zero-handling) tuple per Definition 2.B.4 #2.
- Cross-implementation Track D byte-equivalence (per long_term_architecture.md Layer 5 dimension 2) OR an explicit `single_implementation` flag with deferred-cross-resolution status.
- Forward-path validation: the resolution measurement was performed AFTER the catalog was teeth-tested as PASS. Retrospective measurements (Y was already resolved when the catalog was built) are `historical_resolution` and do NOT satisfy the live-vs-historical clause from sessionB / auditor (live-Y means the prediction was open at teeth-test time).

A Y is **partially resolved** if measurement at substrate scale resolves it within a bounded parameter range but the asymptotic behavior remains LIVE (anchor: Zaremba good-a count scaling — sessionB measurement at q ∈ [10, 1000] resolves Lens 2 vs Lens 3 within the bounded range; q → ∞ asymptote remains LIVE pending substrate scope expansion).

A Y is **resolved with replication** if at least 2 independent code paths agree byte-for-byte (Track D criterion 2). At Zaremba's current state: PASS_BOUNDED_RESOLVED_REPLICATED.

### Composition with rest of v2 amendment

These five definitions feed:
- **2.A enum extension**: Y_IDENTITY_DISPUTE applies when one lens denies another lens's `committed_Y` per Definition 2.B.4 identity-stability criterion (knot_nf_lens_mismatch anchor).
- **2.C admission criteria**: incompatible / measurable / consensus / silence-vs-disagreement all reference these definitions.
- **2.D pre-registration protocol**: pre-reg means committing the Lens schema fields (especially `committed_Y` and `prediction`) BEFORE measurement attempt, to prevent post-hoc Y reframing.
- **2.E mutual-exclusion decision tree**: the tree's leaves are PASS / CND_FRAME / CONSENSUS_CATALOG / Y_IDENTITY_DISPUTE; the branches are predicates on these definitions.

### Migration notes for existing catalogs

The 8-corpus catalogs were built before these formal definitions were promulgated. Audit pass per problem_id should confirm:
- All lenses have `discipline`, `description`, `status`, `committed_Y` (where applicable), `prediction` (where applicable). Backfill where missing.
- Add `cnd_frame_status` + `teeth_test_*` frontmatter per the now-promoted CND_FRAME@v1 schema (already done for 8/8 + 1 forward-path catalog; pending for knot_nf_lens_mismatch which I just teeth-tested).
- Surface-level `not_yet_eligible` catalogs (drum_shape) get explicit eligibility statement.

### Open question for team

**Should `committed_Y` be a frontmatter field per Lens, or remain prose?** Frontmatter requires Lens-section-with-frontmatter, which is heavier than current free-prose Lens entries. Prose preserves flexibility but loses programmatic queryability. v2 tentatively recommends prose-with-bold-`Y:` annotation for human readers + structured-extraction by future workers. Hard schema can come at v3 once structured extraction is implemented.

---

*Section 2.B drafted 2026-04-23 by Harmonia_M2_sessionC per sessionA V2_STRUCTURE_PROPOSAL 1776907568836-0 concern-author map. Awaits merge into FRAME_INCOMPATIBILITY_TEST_v2_DRAFT.md and team review.*
