# Symbol Candidates — Proposed but Not Yet Promoted

**Status:** Living catalog of symbol candidates surfaced from session work.
**Promotion criterion:** ≥ 2 agents reference in committed work OR drafter + reviewer sign-off, per `OVERVIEW.md`.
**Convention:** when a candidate promotes, move its entry to `INDEX.md` and write its `<NAME>.md`. Keep the entry here as a stub linking to the promoted version, so the proposal history is preserved.

---

## Why this file exists

The substrate produces more candidate symbols than it can responsibly promote in a single session. Each candidate represents a compression that a generator, a sweep, or a reviewer would benefit from — but premature promotion fills the registry with bloat. This file catalogs proposals so they are discoverable to other Harmonia sessions, can accumulate the second-reference required for promotion organically, and don't get re-derived from scratch each cold-start.

**North-star alignment** (from `user_prometheus_north_star.md`): every symbol promoted should be a *coordinate system of legibility*, not a law. A candidate that names a shape we keep recognizing is on-frame. A candidate that names a finding we want to celebrate is reward-signal capture and should be rejected at this layer.

---

## Tier 1 — load-bearing for in-flight infrastructure (gen_11 / Definition DAG)

### `VACUUM` (shape) — **PROMOTED 2026-04-20** → see [VACUUM.md](VACUUM.md)

Invariance row of uniform +1 (or +2) across all walked projections, signalling the resolving axis is outside the catalog. Operationalizes Pattern 18 as a queryable diagnostic. Drives gen_11's demand reader.

### `EXHAUSTION` (shape) — **PROMOTED 2026-04-21** → see [EXHAUSTION.md](EXHAUSTION.md)

Negative-side sister to VACUUM: ≥ 3 kills clustered in one axis class with ≥ 1 surviving class for redirect. Operationalizes Pattern 13. Two anchors at promotion (F011 family-level cluster, F010 aggregation cluster).

### `AXIS_CLASS` (constant — categorical taxonomy) — **PROMOTED 2026-04-21** → see [AXIS_CLASS.md](AXIS_CLASS.md)

Controlled vocabulary classifying coordinate types: 10 values (family_level, magnitude, ordinal, categorical, stratification, preprocessing, null_model, scorer, joint, transformation). Tagging audit of all 37 promoted P-IDs pending as a worker task — required for v1 status to be fully operational.

### `GATE_VERDICT` (signature) — **PROMOTED 2026-04-21** → see [GATE_VERDICT.md](GATE_VERDICT.md)

Standardized three-valued filter output: CLEAR / WARN / BLOCK with rationale, raised_by, optional override_token. Used by gen_06 sweeps, gen_11 filter, future Pattern 21 automation. Override protocol mandates recorded hash; silent bypass forbidden.

---

## Tier 2 — pre-existing INDEX.md gaps newly anchored by today's work

### `CLIFF` (shape) — pending second anchor

- **Definition:** sharp step-change at a single stratum boundary; non-ladder structural sibling to `LADDER@v1`. Where LADDER is monotone-and-smooth, CLIFF is monotone-and-discontinuous.
- **Fields:** `axis, boundary_stratum, pre_value, post_value, jump_ratio, n_pre, n_post, block_null_z`
- **Diagnostic threshold:** `jump_ratio ≥ 3.0` AND adjacent strata within 20% AND `block_null_z ≥ 3` AND `min(n_pre, n_post) ≥ 100`.
- **Anchor:** F014 num_ram boundary at k=3 (minimum jumps from 1.216 at num_ram=1,2 to 1.267 at num_ram=3, then 1.800 at num_ram=5). Today's coord-invention discussion sharpened this as the canonical CLIFF instance.
- **Composes with:** `LADDER@v1` (contrast — both monotone, different smoothness), `EXHAUSTION` (a CLIFF in axis-class space looks like exhaustion at the boundary)
- **Why not promoted yet:** needs a second anchor outside F014 to avoid single-specimen pattern.
- **Proposed by:** Harmonia (gaps list, 2026-04-19); re-anchored 2026-04-20

### `SUBFAMILY` (shape) — **PROMOTED 2026-04-21** → see [SUBFAMILY.md](SUBFAMILY.md)

Tail enrichment/depletion within a parent stratum. Three anchors at promotion (F042 CM disc=-27 enrichment, T4 low-L tail observation, F043 surviving empirical kernel). Mandatory Pattern 30 severity check (≤ 1) prevents F043-class failure mode at scale.

---

## Tier 3 — useful but can stay informal until consumer ships

### `PATTERN_STRATIFIER_INVARIANCE` (pattern) — first anchor 2026-04-21

- **Definition:** a null-test is structurally degenerate (null_std≈0; z uninformative) when the test statistic is a function only of *per-stratum aggregates of the stratifier variable* (means, variances, etc.). Within-stratum shuffle preserves those aggregates exactly → the statistic is invariant → the null cannot move.
- **Precondition for ANY `NULL_BSWCD@v2[stratifier=V]` call:** verify that the test statistic is non-invariant under within-V shuffle before interpreting z. Either shuffle once and check that statistic changes, or reason from the statistic's algebraic form.
- **Reformulation options when invariant:** (i) pair `value` with a non-V covariate (e.g., conductor) within each stratum; (ii) bootstrap per-stratum durability (F015/F011 pattern); (iii) switch stratifier to documented nuisance (the original design target).
- **Fields:** `statistic_form, stratifier, invariance_proof, proposed_reformulation, first_anchor_cell, first_anchor_commit`
- **Anchor cases:**
  - F011 cross-group-spread statistic under stratifier=V (V∈{num_bad_primes, rank, semistable, root_number}) — invariant by construction; confirmed in `cartography/docs/reaudit_10_stratifier_mismatch_results.md` §1.
  - F013 decile-variance slope-diff under stratifier=rank — invariant; same doc §3.
  - F013 addendum (`cartography/docs/reaudit_10_stratifier_mismatch_f013_addendum.json`) demonstrates the *dual*: an individual-curve (non-aggregated) F013 variant IS non-invariant under the same stratifier and produces a non-degenerate z=−11.53. Confirms that statistic *shape* (aggregated vs individual) is the axis.
- **Composes with:** `NULL_BSWCD@v2`, `null_protocol_v1.md` (extends §Class 2/3 with a statistic-shape precondition), `GATE_VERDICT@v1` (precondition-fail emits BLOCK with rationale `stratifier_invariance`).
- **Generalization target:** `null_protocol_v1.md` currently pins stratifier by claim class. This pattern adds the orthogonal axis: pin stratifier by *statistic shape*. The Class-2/3 classification is necessary but not sufficient.
- **Why not promoted yet:** one re-audit's worth of anchor evidence (multiple cells but one substrate-layer). Second anchor would be a separate generator or sweep that hits the same invariance independently (candidate: PATTERN_21 null-family sweep under gen_06 when it iterates a statistic through multiple stratifiers).
- **Proposed by:** Harmonia_M2_sessionD, 2026-04-21 re-audit of 10 stratifier-mismatch cells.

### `LENS_MISMATCH` (pattern) — candidate for Tier 3 promotion

- **Definition:** A negative tensor verdict (silence, z≈0, kill) resolves not because the underlying mathematics is trivial but because the **lens** applied was the wrong primitive for the phenomenon. Distinguishes *true kill* (the signal isn't there) from *lens kill* (the signal is structural, not distributional; or categorical, not numerical; or topological, not arithmetic). Adds a named alternative to the binary survives/killed verdict state.
- **Fields:** `f_id, projection_id, lens_applied, lens_type (distributional | structural | categorical | numerical | topological | …), proposed_alternate_lens, anchor_case, alternate_diagnostic_output`
- **Severity axis (graded; mirrors PATTERN_30 shape):**
  - Level 0: `lens_adequate` — primitive matches phenomenon; null result is a true kill
  - Level 1: `lens_coarse` — primitive is right family but too coarse (wrong marginal, wrong normalization); refine then re-test
  - Level 2: `lens_wrong_category` — primitive is in wrong mathematical category entirely (distributional where structural is required; numerical where categorical is required)
  - Level 3: `lens_requires_new_primitive` — no existing primitive in the lens catalog fits; Barrier-3/4 symbol candidate
- **Verdict vocabulary:** `[TRUE_KILL, LENS_COARSE, LENS_WRONG_CATEGORY, LENS_REQUIRES_NEW_PRIMITIVE]` — the latter three are all `lens_mismatch_suspect`, not `killed`.
- **Anchor case (two at proposal):**
  1. **F-ID knot-silence island** (Aporia `deep_research_batch1.md` §Report 3, 2026-04-18). We ran distributional coupling between Alexander polynomial Mahler measure and EC L-values. Result: z≈0, silence. Aporia's post-kill diagnostic: we tested the wrong polynomial. Boyd's conjecture is about A-polynomial (bivariate, SL(2,C) character variety), not Alexander (univariate). Example divergence: figure-eight knot Alexander Mahler = 2.618; A-polynomial prediction = 0.393. Severity: Level 2 (wrong category — distributional coupling applied to a structural bridge). Proposed alternate: database JOIN on algebraic identities (Chinburg 2026: 26 verified Mahler=L-value cases) + SnapPy A-polynomial computation.
  2. **F043 BSD retraction** (2026-04-19, retrospectively). We ran correlation on `log Sha` vs `log A` after Sha=1 restriction. Result: z_block = −348. Review diagnosed: `log A` algebraically contains `−log Sha` via the BSD identity; correlation was a rearrangement detection, not arithmetic evidence. Severity: Level 2 (wrong lens — correlation applied to definitionally coupled variables). PATTERN_30 is the specialized fix for this particular Level-2 failure mode; LENS_MISMATCH generalizes the pattern beyond algebraic coupling.
- **Composes with:** `PATTERN_30@v1` (PATTERN_30 is a LENS_MISMATCH specialization: the specific case where the lens is correlation and the correct primitive is algebraic-identity detection). `PATTERN_21@v1` (plain-null over-rejection is a Level-1 LENS_MISMATCH — lens family right, marginal wrong). `SHADOWS_ON_WALL@v1` (LENS_MISMATCH is the operational response to: "we pointed a lens, it returned nothing — is the shadow not there, or is the lens wrong?")
- **Why this matters (meta-level):** Without a named `LENS_MISMATCH` verdict class, every silent-island / z≈0 / killed cell defaults to `killed`, collapsing two distinct epistemic states ("signal absent" vs "lens inadequate") into one. The collapse hides substrate-debt: every `lens_mismatch_suspect` cell is a symbol-candidate for a missing primitive. Named, it becomes a ledger of *where we need new lenses*, which is directly what `gen_11` (axis-space coordinate invention) and `gen_09` (cross-disciplinary transplants) are designed to produce.
- **Why not promoted yet:** two anchors at proposal but both from retrospective analysis, not live usage as a pre-flight filter. Promote on (a) a gen_06-adjacent sweep module `harmonia/sweeps/lens_mismatch.py` that flags Level 2+ candidates at registration, OR (b) a third anchor from a *forward-path* use (a worker flags a lens-mismatch before promotion rather than after). Until then, remains a draft pattern in this file.
- **Proposed by:** Harmonia_M2_sessionE, 2026-04-21 (Aporia lens-sharpening scan). Source: `harmonia/memory/aporia_lens_scan_20260421.md` §Pick 3.

### `LENS_BLENDING` (pattern / methodology) — candidate for Tier 3 promotion

- **Definition:** A *blended lens* is a coordinate system formed by composing two or more existing lenses such that the blend's primitive is NOT the union of the parents' primitives but a third thing neither parent can express alone. Blending is admitted as a lens (not notation) only when the blend yields a **novel primitive** — a measurable quantity whose value could not be read off the components' measurements.
- **Admission criterion (novelty-of-primitive test):** the blend must propose at least one concrete measurable whose value is (i) not equal to any parent's measurable, (ii) not a trivial algebraic combination of parent measurables, and (iii) falsifiable — there exists a datum that would contradict the blend's committed prediction without contradicting any parent's. If any of (i)-(iii) fails, the blend is notation, not a lens.
- **Forbidden moves during blend construction:** citing parent-lens conclusions as the blend's conclusion; defining the blend's primitive as a function of parent primitives only; inheriting forbidden-move sets from parents additively (the blend needs its own forbidden-move discipline, typically stricter than either parent).
- **Blend composition grammar (proposed):**
  - `Lens_A × Lens_B` → primitive coupling two existing primitives (e.g., Lens 2 × Lens 16 → compressibility-of-ground-state)
  - `Lens_A × Lens_B × Lens_C` → three-way, requiring the triple to yield a measurement no pair captures
  - Blends CAN include PROPOSED (other blended) lenses; recursion is allowed up to depth 3 before combinatorial noise dominates
- **Anchor cases (four at proposal, all in `harmonia/memory/catalogs/collatz.md` 2026-04-21):**
  1. **Lens 19 (Spectral-Kolmogorov):** K(truncation) × transfer-matrix gap → compressibility-as-spectral-gap lower bound. Novel primitive: Δ ≥ 2^{−K(bound)}.
  2. **Lens 20 (p-adic spectral):** 2-adic dynamics × graph spectral → Haar-AC / singular-continuous / pure-point decomposition over Z_p. Novel primitive: the singular-continuous tail, which locates the integer-specific content of the conjecture.
  3. **Lens 21 (Proof-FRACTRAN):** proof-theoretic ordinal × computational universality → ordinal-length pair (α, ℓ) and its ratio α/ℓ. Novel primitive: quantitative provability-difficulty coordinate.
  4. **Lens 22 (Smooth-discrete Wasserstein):** smooth extension × Markov coupling → W_2(μ_integer, μ_smooth) time-series. Novel primitive: discretization-error decay rate as a standalone measurement.
- **Composes with:** `MULTI_PERSPECTIVE_ATTACK@v1` (blends extend the committed-stance parallel menu), `PROBLEM_LENS_CATALOG@v1` (blended lenses live in the same catalogs as parent lenses), `SHADOWS_ON_WALL@v1` (blends are coordinate-system transforms between existing lenses), `methodology_toolkit.md` (blended lenses are a new "tool-combination" category the toolkit should reflect).
- **Why this matters (meta):** Lens inventories grow linearly; lens blends grow combinatorially. Without an admission criterion, blend space is noise — every pair of lenses is nominally a "blend." The novelty-of-primitive test is the filter that makes the combinatorial expansion tractable. Given N lenses with K admissible blends each, the catalog grows by K×N rather than N² — bounded, curatable, and each blend earns its slot by producing a measurement the catalog previously couldn't make.
- **Why not promoted yet:** four anchor cases exist but all from a single session's first-pass draft; no cross-session verification that the admission criterion is *structurally* right rather than sessionD's framing artifact. Promotion path: (a) a second session blends independently and its blends meet the same admission test, OR (b) one of the four proposed blends graduates to APPLIED with a committed-stance run that produces a concrete measurable, validating the criterion empirically.
- **Proposed by:** Harmonia_M2_sessionD, 2026-04-21 (Collatz blended-lens extension).

### `DEMAND_SIGNAL` (signature) — defer until gen_11 implementation reveals stable schema

- **Definition:** tuple schema for what gen_11's demand reader emits per F-ID. Composition over `{VACUUM, EXHAUSTION, OUTLIER}`.
- **Why defer:** schema should follow the implementation, not lead it. Pin after first gen_11 run reveals which fields actually matter.

### `CANDIDATE_AXIS` (signature) — defer until gen_11 implementation

- **Definition:** tuple schema for gen_11 generator output: `{name, definition (sympy expression), source ∈ {combinatorial, algebraic, specimen, theory, kill_inversion}, expected_discriminates: list[F-ID], generator_module}`
- **Why defer:** same reasoning as DEMAND_SIGNAL.

### `NEAR_DUPLICATE` (shape) — filter-internal, low promotion value

- **Definition:** a candidate axis with high stratification overlap with an existing P-ID (ARI > 0.85).
- **Why defer:** lives inside gen_11's filter Gate 3. Symbolizing it is bookkeeping unless a second consumer appears.

---

## Tier 4 — pre-existing gaps still on the shelf (from INDEX.md)

For visibility; these have been on the gaps list since the registry was first promoted:

- **`NULL_BSWR`** — block-shuffle-within-rank variant of NULL_BSWCD. Needed for any rank-cohort claim where conductor-decile stratification doesn't apply. Promotion = first implementation + rank-cohort smoke test.
- **`Q_EC_R12_D5`** — rank ∈ {1, 2} version of `Q_EC_R0_D5@v1`. Needed for F041a-class work that crosses rank cohorts.
- **`ZBLOCK`** — z-score computed via NULL_BSWCD. A unit/operator that the SIGNATURE schema currently records as `z_score` without tying to its null. Promotion = SIGNATURE@v2 with explicit null-attribution per z-score.
- **`BATCH`** — set of findings grouped for literature audit (Pattern 28/29 anchor). Promotion = first batch literature-audit lands and the grouping criterion is pinned.

---

### `LENS_MISMATCH` (pattern) — first anchor 2026-04-21

- **Definition:** a tensor negative-verdict produced under a lens whose formal type matches the problem's discipline but whose specific implementation / projection / polynomial is not the one required by the bridge. Distinguished from `killed_no_correlation` (which claims no bridge exists) by the availability of an alternative lens in the SAME discipline that WOULD reveal the bridge.
- **Severity tiers:**
  - Level 0 CLEAN — lens is canonical; null result is real.
  - Level 1 MILD_MISMATCH — alternative lens exists but not yet identified as load-bearing.
  - Level 2 DOCUMENTED_MISMATCH — literature names the correct alternative; current lens is known-incorrect.
  - Level 3 PROVEN_MISMATCH — alternative lens applied, produces positive verdict on ≥ 1 anchor.
- **Anchor:** figure-eight knot Alexander Mahler 2.618 vs A-polynomial prediction 0.393 (Aporia Report 3, 2026-04-18). Level 2 at diagnosis; Level 3 after SnapPy A-polynomial recomputation.
- **Composes with:** `PATTERN_30@v1` (different failure-mode — algebraic-coupling is math-side, LENS_MISMATCH is instrument-side), `SHADOWS_ON_WALL@v1` (canonical single-lens failure pattern).
- **Why not promoted yet:** one anchor. Needs a second substrate-distinct case before promotion.
- **Proposed by:** Harmonia_M2_sessionE + sessionA (2026-04-21), anchored to Aporia's prior diagnosis.
- **Source catalog:** `harmonia/memory/catalogs/knot_nf_lens_mismatch.md`.

---

## Cross-disciplinary candidates from `methodology_toolkit.md`

The toolkit catalogs six tools (`KOLMOGOROV_HAT`, `CRITICAL_EXPONENT`, `CHANNEL_CAPACITY`, `MDL_SCORER`, `RG_FLOW`, `FREE_ENERGY`) that are not yet promoted symbols but are scoped into `gen_09_cross_disciplinary_transplants`. Their promotion path is *through* gen_09 implementation: when a tool ships, it promotes as a symbol and migrates from the toolkit to `INDEX.md`. The toolkit is the staging area for those; this file is the staging area for substrate-internal candidates.

---

## Promotion workflow

1. A candidate's second reference appears in committed work, OR a drafter + reviewer sign off.
2. Drafter writes `<NAME>.md` following the existing `LADDER.md` template (frontmatter + Definition / Derivation / References / Data / Usage / Version history).
3. Run `python -m agora.symbols.push harmonia/memory/symbols/<NAME>.md`.
4. Add to `INDEX.md` "By type" table.
5. Reduce this file's entry for that symbol to a stub linking to the promoted MD.

---

## Version history

- **v1.1** — 2026-04-21 — five symbols promoted in the next wave (EXHAUSTION, AXIS_CLASS, GATE_VERDICT, SUBFAMILY) alongside the original VACUUM. Tier 1 fully landed. Definition DAG architecture spec shipped at `harmonia/memory/architecture/definition_dag.md` (separately from the symbol registry — substrate primitive, not symbol).
- **v1.0** — 2026-04-20 — initial catalog. VACUUM promoted in same tick. Eight other candidates documented across four tiers.
