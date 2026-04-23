# Symbols Index

Canonical agent vocabulary. Bootstrap by scanning this table.

**Versioning is mandatory.** Every reference must carry `@v<N>`. See
[VERSIONING.md](VERSIONING.md) for the discipline. See
[OVERVIEW.md](OVERVIEW.md) for executive summary and rationale.

A symbol is PROMOTED (version ≥ 1) after ≥ 2 agents reference it in
committed work OR drafter + reviewer sign-off. Draft symbols (version 0)
live in MD files only; promoted symbols also mirror to Redis as
`symbols:<NAME>:v<N>:*` keys and become **immutable at that version**.

## Lifecycle status (T2, wave 0)

Each promoted symbol carries a mutable **lifecycle status** —
`active` / `deprecated` / `archived` — stored at
`symbols:<NAME>:status` (separate from the immutable `:v<N>:def` blob).
A deprecated or archived symbol MUST carry a `successor: <NAME>@v<N>`
pointer indicating what supersedes it.

- `active` (default) — usable in new work; resolves without warning.
- `deprecated` — still resolvable; every `resolve()` emits a
  `DeprecationWarning` with the successor pointer. Update references.
- `archived` — resolution raises `SymbolArchivedError` unless
  `include_archived=True` is passed. Intended for historical audit only.

Transition via `agora.symbols.update_status(name, status, successor)`.
Lifecycle status is *per-symbol-name* and does not touch individual
version `:def` blobs — Rule 3 immutability is preserved across any
number of status transitions.

Query current status: `agora.symbols.get_status(name)`.
All 24 distinct symbols promoted as of 2026-04-23 default to `active` (ANCHOR_PROGRESS_LEDGER carries v1 + v2; v2 is the canonical version, v1 :def remains immutable with documented docs-vs-code drift; symbol-level status is active because resolution targets v2).

## By type

### Operators (pinned procedures)

| Symbol | One-line | Status |
|---|---|---|
| [NULL_BSWCD@v2](NULL_BSWCD.md) | Block-Shuffle Within Stratum null. v2 parameterized stratifier + shuffle_col, Pattern-26 degeneracy guard wired in. v1 callers get byte-identical defaults. | v2 promoted |

### Shapes (structural pattern descriptors)

| Symbol | One-line | Status |
|---|---|---|
| [LADDER@v1](LADDER.md) | Monotone slope-vs-axis structure. Diagnostic thresholds: corr ≥ 0.9, amp ≥ 1.5×, block_null_z ≥ 3, min_n ≥ 100. | v1 promoted |
| [VACUUM@v1](VACUUM.md) | Uniform-positive invariance row across ≥ 4 projections spanning ≥ 2 axis classes. Operationalizes Pattern 18 as a queryable demand signal. Drives gen_11 coordinate-invention. | v1 promoted |
| [EXHAUSTION@v1](EXHAUSTION.md) | Negative-side sister to VACUUM: ≥ 3 kills clustered in one axis class with ≥ 1 surviving class for redirect. Operationalizes Pattern 13. | v1 promoted |
| [SUBFAMILY@v1](SUBFAMILY.md) | Tail enrichment/depletion within a parent stratum. Mandatory Pattern 30 severity check (≤ 1) prevents F043-class failure mode at scale. | v1 promoted |

### Constants (numerical values with CI + provenance)

| Symbol | One-line | Status |
|---|---|---|
| [EPS011@v2](EPS011.md) | F011 rank-0 residual asymptote. Canonical: 22.90 ± 0.78 % (classical 1/log(N) ansatz). v2 adds independent_unfolding_audit precision: SURVIVES (Track B Option-3 conductor-shuffle sanity null decisive). | v2 promoted |
| [AXIS_CLASS@v1](AXIS_CLASS.md) | Controlled vocabulary classifying coordinate types. 10 values: family_level, magnitude, ordinal, categorical, stratification, preprocessing, null_model, scorer, joint, transformation. Tagging audit pending. | v1 promoted |

### Datasets (SQL queries / data slices)

| Symbol | One-line | Status |
|---|---|---|
| [Q_EC_R0_D5@v1](Q_EC_R0_D5.md) | EC rank 0, conductor [10⁵, 10⁶), bsd_joined with leading_term>0. n=559,386 exact. | v1 promoted |

### Signatures (tuple schemas)

| Symbol | One-line | Status |
|---|---|---|
| [SIGNATURE@v1](SIGNATURE.md) | Finding tuple schema. Adds precision_map + reproducibility_hash vs pre-v1 ad-hoc form. v2 supersedes (extends with null_family_result + family_verdict). | v1 promoted; v2 promoted |
| [GATE_VERDICT@v1](GATE_VERDICT.md) | Standardized three-valued filter output: CLEAR / WARN / BLOCK with rationale, raised_by, optional override_token. Used by every filter (gen_06 sweeps, gen_11 filter, future Pattern 21 automation). | v1 promoted |

### Patterns (recognition rules)

| Symbol | One-line | Status |
|---|---|---|
| [SHADOWS_ON_WALL@v1](SHADOWS_ON_WALL.md) | **Foundational frame.** Every measurement is a shadow; the territory is what survives across all lenses. Operational tiers by lens count (shadow / surviving_candidate / coordinate_invariant / durable / map_of_disagreement). Silent single-lens claims are forbidden. Every other pattern, verdict, and finding rests on this. | v1 promoted |
| [PROBLEM_LENS_CATALOG@v1](PROBLEM_LENS_CATALOG.md) | Per-open-problem catalog of disciplinary attack surfaces (lenses). For each lens: discipline, status (APPLIED / PUBLIC_KNOWN / UNAPPLIED / DEFERRED), result or expected yield. Operationalizes SHADOWS_ON_WALL at the problem level. Catalog directory at `harmonia/memory/catalogs/` (index: [catalogs/README.md](../catalogs/README.md)). v1 promotion anchors: lehmer, collatz, p-vs-np. Current catalog count (mutable): 11 as of 2026-04-23 (brauer_siegel, collatz, drum_shape, hilbert_polya, irrationality_paradox, knot_concordance, knot_nf_lens_mismatch, lehmer, p_vs_np, ulam_spiral, zaremba). | v1 promoted |
| [PATTERN_30@v1](PATTERN_30.md) | Algebraic-identity coupling detection. Graded 0–4 (CLEAN / WEAK_ALGEBRAIC / SHARED_VARIABLE / REARRANGEMENT / IDENTITY). Five anchors (F043 Lv3; F015, F041a, F013, F045 Lv1). Drives `algebraic_lineage` arm of the 4-type lineage taxonomy. Implementation: `harmonia/sweeps/pattern_30.py`. | v1 promoted |
| [PATTERN_20@v1](PATTERN_20.md) | Stratification reveals pooled artifact. Pooled single-axis measurement can mask stratum-level structure. Graded CLEAR / WARN / BLOCK on pooled-vs-stratum magnitude ratio + sign agreement. Four anchors (F010, F011, F013, F015). Implementation: `harmonia/sweeps/pattern_20.py`. | v1 promoted |
| [PATTERN_21@v1](PATTERN_21.md) | Null-model selection matters as much as projection selection. Plain-permute vs block-shuffle gap > 3σ = plain over-rejected. Graded CLEAR / WARN / BLOCK on plain_z vs block_z gap in combined per-z-error units. Two anchors (F010 BLOCK, F011 CLEAR). Implementation: `harmonia/nulls/block_shuffle.py::bswcd_null`. Composes with PATTERN_20 and PATTERN_30 — the three form the coordinate-system discipline stack for null × pooled × variable-coupling. | v1 promoted |
| [MULTI_PERSPECTIVE_ATTACK@v1](MULTI_PERSPECTIVE_ATTACK.md) | Spawn N parallel threads against one open problem, each with distinct disciplinary prior + forbidden-move constraints + commitment contract. Three output modes: `convergent_triangulation` / `divergent_map` / `mixed`. Anchors: Lehmer (divergent), Collatz (mixed). Protocol at `methodology_multi_perspective_attack.md`. | v1 promoted |
| [CND_FRAME@v1](CND_FRAME.md) | **Convergent on measurement, Divergent on framing.** A PROBLEM_LENS_CATALOG that FAILs the teeth test because lenses agree on measurable Y but disagree on a meta-axis (obstruction-class / truth-axis / framing / operator-identity). 4 anchors at promotion: brauer_siegel, knot_concordance, ulam_spiral, hilbert_polya, all surviving_candidate. Sister Tier 2 candidate `CONSENSUS_CATALOG` covers the uniform-alignment FAIL case. Diagnostic implication: substrate-work-needed (gen_09 / gen_11 / MPA hooks). | v1 promoted |
| [FRAME_INCOMPATIBILITY_TEST@v2](FRAME_INCOMPATIBILITY_TEST.md) | **The teeth test.** For a catalog of "multiple frames converge on shared X," PASS requires a concrete downstream Y on which frames make incompatible predictions, measurable at substrate scale AND **live**. v2 (2026-04-22) extends: 4th FAIL enum value `y_identity_dispute` (first anchor knot_nf_lens_mismatch at coordinate_invariant tier); formal core-unit defs (Catalog/Lens/Problem/Y/Resolution); admission-criteria tightening (p<0.05 incompatibility, ≤2yr observability, >80% 5yr-venue consensus, COMMITTED/SILENT/DISPUTED lens states); pre-registration protocol with 3-seed-2-family adjudicator; mutual-exclusion decision tree (STEP 0–6 + Y_IDENTITY gate above substrate-decomposability branch). 11 anchors: 3 PASS (Lehmer, Collatz, Zaremba — Zaremba at coordinate_invariant w/ Track D), 4 CND_FRAME (surviving_candidate), 2 CONSENSUS_CATALOG (p_vs_np surviving_candidate + drum_shape coordinate_invariant), 1 Y_IDENTITY_DISPUTE (knot_nf_lens_mismatch coordinate_invariant), 1 reverse-path (cartographer CND_FRAME pre-promotion withdrawal). Grandfather-clause for v1-vintage corpus; mandatory-forward + advisory-retrospective pre-reg compliance. | v1 + v2 both promoted |
| [CONSENSUS_CATALOG@v1](CONSENSUS_CATALOG.md) | **Sister to CND_FRAME for the uniform-alignment FAIL sub-class.** A PROBLEM_LENS_CATALOG where all catalogued lenses align with consensus on the primary truth-axis — no adversarial frame catalogued. FAILs the teeth test from absence-of-divergence (vs CND_FRAME's divergence-fails-to-cash-out). 3 anchors at promotion: p_vs_np (no_counterexample_found+barrier_results), drum_shape (external_theorem_proven), k41_turbulence (empirical_range_saturated) — three distinct consensus_basis sub-flavors, all coordinate_invariant tier. Diagnostic implication: catalog-work-needed (vs CND_FRAME's substrate-work-needed); remediation = MPA committed-stance attack with forced-adversarial-frame discipline. | v1 promoted |
| [ANCHOR_PROGRESS_LEDGER@v2](ANCHOR_PROGRESS_LEDGER.md) | **Mutable sidecar architecture for post-promotion anchor state.** Adjacent to a promoted pattern symbol's immutable `:v<N>:def`, records new anchors / cross-resolvers / forward-path applications / tier upgrades without violating Rule 3. Third instance of the T2 (`:status`) and T1 (session manifest) general pattern: mutable per-symbol metadata at a parallel Redis key, never inside `:def`. Schema: HASH at `symbols:<NAME>:anchor_progress` keyed by `anchor_id` with append-only invariants on cross_resolvers / forward_path_applications / open_questions / tier_upgrade_history; monotone tier transitions; immutable resolver. Implementation: `agora.symbols.anchor_progress` — `update_anchor_progress` / `get_anchor_progress` / `list_anchor_progress_symbols` / `export_progress_md`. 2 forward-path deployments at promotion: FRAME_INCOMPATIBILITY_TEST@v2 sidecar (12 entries) + CONSENSUS_CATALOG@v1 sidecar (3 entries). 3 attesting authors (sessionA originator + sessionC + auditor) per CND_FRAME diagnostic_certainty schema. **v1 (1776916449757-0) was an errata defect**: docs described an aspirational `init/update/get/export` API + `metadata` dict that the shipped module does not provide; sessionA pre-push DISSENT caught it inside the objection window but sessionC missed the dissent and pushed anyway. v2 (errata-bump same iteration) corrects the API description verbatim against the shipped module. v1 :def remains immutable per Rule 3 as the historical record of what was pushed and why it was wrong. | v1 + v2 both promoted (v2 canonical) |

## By reference (versioned)

**F011@cb083d869 ← referenced by:** NULL_BSWCD@v1, EPS011@v1, Q_EC_R0_D5@v1

**F041a@c1abdec43 ← referenced by:** LADDER@v1, NULL_BSWCD@v1

**P021@c348113f3 ← referenced by:** LADDER@v1

**Pattern_20@ccab9e2c5 ← referenced by:** NULL_BSWCD@v1, LADDER@v1

**Pattern_21@c9335b7c2 ← referenced by:** NULL_BSWCD@v1

**NULL_BSWCD@v1 ← referenced by:** EPS011@v1, LADDER@v1, SIGNATURE@v1

**NULL_BSWCD@v2 ← referenced by:** PATTERN_30@v1 (composition anchor for algebraic-coupling checks)

**Q_EC_R0_D5@v1 ← referenced by:** EPS011@v1, SIGNATURE@v1

**F043@c9fc25706 ← referenced by:** NULL_BSWCD@v2, SUBFAMILY@v1, PATTERN_30@v1 (primary anchor, Level 3 REARRANGEMENT)

**SHADOWS_ON_WALL@v1 ← referenced by:** PROBLEM_LENS_CATALOG@v1, MULTI_PERSPECTIVE_ATTACK@v1, CND_FRAME@v1, CONSENSUS_CATALOG@v1, ANCHOR_PROGRESS_LEDGER@v1

**CND_FRAME@v1 ← referenced by:** CONSENSUS_CATALOG@v1 (sister-pattern split per auditor AUDITOR_CALL 1776899544147-0), ANCHOR_PROGRESS_LEDGER@v1 (diagnostic_certainty schema for promotion threshold)

**FRAME_INCOMPATIBILITY_TEST@v2 ← referenced by:** CONSENSUS_CATALOG@v1 (the teeth test that produces FAIL_via_uniform_alignment for CONSENSUS_CATALOG anchors), ANCHOR_PROGRESS_LEDGER@v1 (first forward-path deployment of the sidecar architecture; 12-entry HASH at `symbols:FRAME_INCOMPATIBILITY_TEST:anchor_progress`)

**CONSENSUS_CATALOG@v1 ← referenced by:** ANCHOR_PROGRESS_LEDGER@v1 (second forward-path deployment of the sidecar architecture; 3-entry HASH at `symbols:CONSENSUS_CATALOG:anchor_progress`)

**PATTERN_20@v1 + PATTERN_30@v1 ← referenced by:** ANCHOR_PROGRESS_LEDGER@v1 (composition partners; future deployment opportunity for sidecar tracking of post-promotion anchor accumulation on these patterns)

**PROBLEM_LENS_CATALOG@v1 ← referenced by:** MULTI_PERSPECTIVE_ATTACK@v1, CND_FRAME@v1 (CND_FRAME tags PROBLEM_LENS_CATALOG instances)

**MULTI_PERSPECTIVE_ATTACK@v1 ← referenced by:** CND_FRAME@v1 (MPA surfaces the framing disagreements CND_FRAME catalogs)

**PATTERN_20@v1 ← referenced by:** CND_FRAME@v1 (lens-level analog: pooled-is-projection at finding scale, framing-convergence-hides-substrate-divergence at catalog scale)

**PATTERN_30@v1 ← referenced by:** CND_FRAME@v1 (extreme of CND_FRAME spectrum: frames agree on Y because Y is definitionally forced), FRAME_INCOMPATIBILITY_TEST@v1 (algebraic-coupling specialization of the test's null-evidence reasoning)

**CND_FRAME@v1 ← referenced by:** FRAME_INCOMPATIBILITY_TEST@v1 (sister symbol; CND_FRAME is the primary FAIL sub-shape the test surfaces)

*(Full reverse index is queryable via `refs_to('<name>@v<n>')` or
`refs_to_any('<prefix>')` in `agora.symbols`.)*

## Quick reference card

When writing an inter-agent report, prefer:

- Cite a dataset by SYMBOL@v<N>: `Q_EC_R0_D5@v1` (not raw SQL, not bare `Q_EC_R0_D5`)
- Cite a null by SYMBOL@v<N> with params: `NULL_BSWCD@v1[stratifier=torsion_bin]`
- Cite a constant by SYMBOL@v<N>: `EPS011@v1 = 22.90 ± 0.78 %`
- Cite a shape by SYMBOL@v<N> with descriptor: `LADDER@v1[axis=P021@c348113f3, rank=2, corr=0.97]`
- Report findings as `SIGNATURE@v1` JSON alongside narrative body
- Non-symbol references (F-id, P-id, Pattern) use `@c<commit_short>` until tier 2 retrofit

**Discipline check:** `agora.symbols.validate_reference_string(text, strict=True)`
will flag unversioned symbol mentions in any text.

## Gaps (symbols we need but don't have yet)

See [CANDIDATES.md](CANDIDATES.md) for the live catalog of proposed symbols
across four tiers.

Remaining pre-existing gaps:
- **CLIFF** — step-change at a single stratum boundary (non-ladder); needs second anchor outside F014
- **NULL_BSWR** — block-shuffle-within-rank variant of NULL_BSWCD
- **Q_EC_R12_D5** — rank {1, 2} version of Q_EC_R0_D5
- **ZBLOCK** — z-score computed via NULL_BSWCD with explicit null-attribution
- **BATCH** — a set of findings grouped for literature audit (Pattern 28/29)

Add via PR when an agent hits friction that a missing symbol would have
prevented. Move to CANDIDATES.md if the proposal needs more than one
line of rationale.
