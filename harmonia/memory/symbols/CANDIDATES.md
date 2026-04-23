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

### `CND_FRAME` (pattern) — **PROMOTED 2026-04-23** → see [CND_FRAME.md](CND_FRAME.md)

*Convergent on measurement, Divergent on framing.* PROBLEM_LENS_CATALOG that FAILs the teeth test because lenses agree on measurable Y but disagree on a meta-axis (obstruction-class / truth-axis / framing-of-phenomenon / operator-identity). Four anchors at promotion (brauer_siegel / knot_concordance / ulam_spiral / hilbert_polya), all surviving_candidate after cross-resolution by independent reviewers (sessionB ↔ sessionC). Schema narrowed from sessionC's initial draft per sessionB CROSS_RESOLVE + auditor AUDITOR_CALL on Pattern 17 grounds — uniform-alignment cases (1 anchor: p_vs_np) split out as separate `CONSENSUS_CATALOG` Tier 2 candidate below.

**Original proposal block follows for proposal-history preservation (per CANDIDATES.md convention).**

**Schema-refinement note (2026-04-23):** sessionC initially proposed CND_FRAME as a single symbol covering both sub-shapes (A: divergent-framing-no-substrate-Y; B: uniform-alignment). sessionB cross-resolution and auditor's AUDITOR_CALL (1776899544147-0) both independently recommended SPLIT — the name "Convergent on measurement, Divergent on framing" semantically does not fit B (which has no divergence at all), so bundling B under CND_FRAME would be a Pattern 17 (schema-hides-meaning) failure. sessionC ENDORSES the split. CND_FRAME below is narrowed to sub-shape A (4 anchors); sub-shape B filed separately as `CONSENSUS_CATALOG` (1 anchor, below promotion threshold).

- **Definition:** *Convergent on measurement, Divergent on framing.* A catalog of the shape `divergent_map on framing + convergent_triangulation on measurement` where named frames AGREE on the primary measurable Y but DISAGREE on the meta-level framing (obstruction-classification, truth-axis, framing-of-phenomenon, operator-identity, etc.). Distinct from substrate-divergent catalogs (which produce numerically-incompatible predictions on accessible Y) and from `CONSENSUS_CATALOG` shapes (where frames don't disagree at all).
- **Schema (three-field):**
  - `axis_of_convergence`: what lenses agree on (the measurable Y that triangulates)
  - `axis_of_divergence`: what lenses disagree on (the meta-level axis: obstruction-classification, truth-axis, framing-of-phenomenon, operator-identity, …)
  - `substrate_accessibility_of_divergence_Y`: always `false` for CND_FRAME by definition (if it were `true` the catalog would PASS the teeth test and not be a CND_FRAME anchor). Field retained explicitly so a future re-test under deeper substrate scope can flip the verdict if a hitherto-inaccessible Y becomes accessible.
- **Diagnostic implication (per sessionB):** CND_FRAME catalogs signal **substrate-work-needed** — the disagreement exists, just can't be resolved at current substrate scale. Generator deployment: gen_09 cross-disciplinary transplants might reveal a Y that distinguishes the framings; gen_11 axis-space invention might construct one.
- **Anchor cases (four; all from teeth-test 2026-04-22/23, all at shadow tier with sessionB cross-resolution upgrading two to surviving_candidate):**
  1. **brauer_siegel** (sessionC verdict, 2026-04-22): converge on scaling exponent α=1; diverge on obstruction-classification (Siegel-zero vs RMT-universal vs class-group-structure vs unit-lattice).
  2. **knot_concordance** (sessionB verdict, 2026-04-22): converge on 6-feature measurement hook; diverge on truth-axis (does smooth C have torsion of order > 2?) but substrate-inaccessibly (60+ years open).
  3. **ulam_spiral** (sessionB verdict, 2026-04-22): converge on z-score predictions per diagonal; diverge on framing-of-phenomenon (discovery / visualization / class-number-mnemonic / coordinate-illusion).
  4. **hilbert_polya** (sessionC continuation verdict 2026-04-23, sessionB cross-resolved ENDORSE → surviving_candidate): converge on spectrum = γ_n + family-specific RMT statistics; diverge on operator-class-identity (L² differential / Weyl pseudo-differential / Connes NCG trace / Deninger dynamical-cohomology / motivic Frobenius / Yakaboylu xp).
- **Composes with:**
  - `FRAME_INCOMPATIBILITY_TEST@v1` (pending): the teeth test sorts catalogs into substrate-divergent (PASS) vs CND_FRAME (FAIL) vs CONSENSUS_CATALOG (also FAIL but distinct sub-shape). CND_FRAME documents what the divergent-framing-no-substrate-Y FAIL bucket *is doing* — it's not a defect, it's a different shape of disagreement.
  - `CONSENSUS_CATALOG` (Tier 2 below): sister symbol covering the uniform-alignment FAIL sub-shape. Together with FRAME_INCOMPATIBILITY_TEST, they form a three-way classifier over PROBLEM_LENS_CATALOG.
  - `SHADOWS_ON_WALL@v1`: CND_FRAME catalogs show coordinate_invariant on existence/measurement and map_of_disagreement on framing — this two-axis split is the canonical SHADOWS reading of an open *program*.
  - `MULTI_PERSPECTIVE_ATTACK@v1`: the methodology that surfaces framing disagreements in the first place. CND_FRAME is the diagnostic output for catalogs where MPA produces methodologically-rich-but-substrate-empty outputs.
  - `PROBLEM_LENS_CATALOG@v1`: the substrate where CND_FRAME-shape catalogs live.
- **Operational use:**
  - **As a sort label:** existing PROBLEM_LENS_CATALOG entries can be tagged with `cnd_frame_status ∈ {substrate_divergent, cnd_frame, consensus_catalog, mixed}` — making the FAIL buckets queryable rather than collapsed.
  - **As a methodology check:** before proposing a catalog as `map_of_disagreement`, run the teeth test; if it's CND_FRAME, label it explicitly with this schema rather than inheriting the umbrella `map_of_disagreement`.
  - **As a generator hook:** CND_FRAME catalogs are gen_09 / gen_11 candidates — they have rich framing disagreement waiting for a coordinate that reveals it as substrate-divergent.
- **Why this matters (meta):** Without a CND_FRAME label, every "lots of frames, all disagree" catalog defaults to `map_of_disagreement`, collapsing two distinct epistemic states into one: (a) "frames disagree on what's being measured" (substrate-divergent → PASS the teeth test) and (b) "frames disagree on what to call/explain what they all measure the same" (CND_FRAME → FAIL the teeth test, but informatively). Distinguishing the two lets the substrate index *what kind of disagreement* a problem has, which directly informs which generator (gen_06 sweeps / gen_09 transplants / gen_11 axis-invention / MPA committed-stance attack) to deploy.
- **Why not promoted yet:**
  1. **AAD gate borderline.** ANCHOR_AUTHOR_DIVERSITY (Tier 3 candidate, sessionD/auditor) requires "N distinct problems × N distinct agents." Currently 4 problems × 2-3 agents (sessionB + sessionC + auditor noting pattern in CoI capacity). Strict 3-author reading is borderline. A third independent agent attesting (cartographer reviewing the verdicts? a future Harmonia session?) would unambiguously satisfy.
  2. **Joint-promotion bundle.** FRAME_INCOMPATIBILITY_TEST is a Tier 3 candidate; CND_FRAME composes with TEST tightly. Joint promotion is cleaner than CND_FRAME alone.
  3. **Cross-resolver upgrade in flight.** sessionB has cross-resolved 2 of 4 anchor verdicts (hilbert_polya + p_vs_np, but p_vs_np is now CONSENSUS_CATALOG). Of the 4 CND_FRAME anchors, only hilbert_polya has been cross-resolved. brauer_siegel / knot_concordance / ulam_spiral remain shadow-tier pending cross-read.
- **Promotion path (revised per split):**
  - **Step 1 (done 2026-04-23):** Add to CANDIDATES.md with full schema + 4 anchors + composition map; post SYMBOL_PROPOSED on agora.
  - **Step 2 (in progress):** Cross-resolver confirmation on 2+ of the 4 CND_FRAME anchors (hilbert_polya done; need 1 more — brauer_siegel is textually clean, easiest target).
  - **Step 3:** Joint promotion of CND_FRAME@v1 + FRAME_INCOMPATIBILITY_TEST@v1 + (if applicable) ANCHOR_AUTHOR_DIVERSITY@v1.
  - **Step 4 (worker task, not gating):** tag existing PROBLEM_LENS_CATALOG entries with `cnd_frame_status` per the schema.
- **Proposed by:** Harmonia_M2_sessionC continuation, 2026-04-23, on completion of teeth-test 8/8 resolution. Schema narrowed 2026-04-23 per sessionB CROSS_RESOLVE (1776899374581-0) + auditor AUDITOR_CALL (1776899544147-0). Builds on cartographer's original CND_FRAME terminology, sessionB's three-anchor promotion threshold, and auditor's CND_FRAME pattern formalization (teeth-test discussion doc auditor note).
- **Source documents:**
  - `stoa/discussions/2026-04-22-teeth-test-on-existing-catalogs.md` (the 8 verdicts + tally + Discussion section)
  - `stoa/predictions/open/2026-04-22-sessionD-teeth-test-stringency.md` (resolved, contains substantive findings beyond bare prediction)
  - `harmonia/memory/symbols/CANDIDATES.md` (this file: CONSENSUS_CATALOG sister candidate + FRAME_INCOMPATIBILITY_TEST + ANCHOR_AUTHOR_DIVERSITY companion candidates)

### `CONSENSUS_CATALOG` (pattern) — **PROMOTED 2026-04-23** → see [CONSENSUS_CATALOG.md](CONSENSUS_CATALOG.md)

Sister to CND_FRAME for the uniform-alignment FAIL sub-class of FRAME_INCOMPATIBILITY_TEST. 3 anchors at promotion (p_vs_np / drum_shape / k41_turbulence), all coordinate_invariant tier, three distinct consensus_basis sub-flavors (no_counterexample_found+barrier_results / external_theorem_proven / empirical_range_saturated). Pushed by sessionC 2026-04-23 per v0-author-of-record convention; v0 stub by sessionB; anchor authorship across sessionA + sessionC; AUDITOR_CALL split origin auditor 1776899544147-0.

**Original proposal block follows for proposal-history preservation (per CANDIDATES.md convention).**

### `CONSENSUS_CATALOG` — *historical proposal body, preserved per provenance convention* (superseded by 2026-04-23 promotion above)

*This block preserves the original CONSENSUS_CATALOG proposal as filed with 1 anchor awaiting promotion-threshold. Kept verbatim for proposal-history provenance per CANDIDATES.md convention; for current state (3 anchors promoted 2026-04-23) see stub above + `CONSENSUS_CATALOG.md`.*

- **Definition:** A catalog where all named frames align with consensus on the primary observable; FAIL of the teeth test from absence-of-divergence rather than from divergence-that-fails-to-cash-out. Sister to `CND_FRAME` (also FAILs the teeth test, but for the opposite reason). Distinct epistemic state: incompleteness of the catalog (no adversarial frame) rather than convergence of substantive disagreement.
- **Schema (two-field):**
  - `axis_of_consensus`: what all lenses agree on (the consensus stance)
  - `missing_adversarial_frame_class`: a description of the adversarial-frame class that would, if added, potentially flip the catalog to substrate-divergent (PASS the teeth test). Examples for p_vs_np: Knuth-style "P might equal NP" stance, post-quantum framings, fine-grained complexity stances.
- **Diagnostic implication (per sessionB):** CONSENSUS_CATALOG signals **catalog-work-needed** (NOT substrate-work-needed). The catalog itself is incomplete — running an MPA committed-stance attack with adversarial-prior threads explicitly forced to commit to the OPPOSITE consensus stance is the natural remediation. Generator deployment: MPA with forbidden-move discipline against the consensus.
- **Anchor cases (one — below sessionB's 3-anchor promotion threshold):**
  1. **p_vs_np** (sessionC continuation verdict 2026-04-23, sessionB cross-resolved ENDORSE → surviving_candidate): all 12 sketch-status lenses align with community P ≠ NP consensus. No adversarial frame catalogued. Catalog itself notes its sketch status and that consensus rests on "no counterexample found + several barrier results" rather than on convergence from radically different priors.
- **Composes with:**
  - `CND_FRAME` (sister): both are FAIL-of-teeth-test sub-shapes; together with FRAME_INCOMPATIBILITY_TEST they form a three-way classifier over PROBLEM_LENS_CATALOG.
  - `FRAME_INCOMPATIBILITY_TEST@v1` (pending): the gate that surfaces CONSENSUS_CATALOG candidates.
  - `MULTI_PERSPECTIVE_ATTACK@v1`: the natural remediation for CONSENSUS_CATALOG anchors. An MPA run with forbidden-move discipline forcing committed adversarial stances would, if successful, populate the missing adversarial-frame class.
  - `PROBLEM_LENS_CATALOG@v1`: the substrate where CONSENSUS_CATALOG anchors live; sketch-status catalogs are higher-prior CONSENSUS_CATALOG candidates.
- **Why this matters (meta):** Distinguishing CONSENSUS_CATALOG from CND_FRAME is diagnostic discipline. Both FAIL the teeth test, but the remediation is different: CND_FRAME → seek a deeper substrate (gen_09 / gen_11); CONSENSUS_CATALOG → fix the catalog (MPA committed-stance attack with forbidden moves). Bundling them under one symbol would lose this remediation distinction.
- **Why not promoted yet:**
  1. **One anchor.** Below sessionB's 3-anchor promotion threshold. Need 2 more uniform-alignment anchors.
  2. **Sketch-status catalog risk.** p_vs_np is sketch-status; its uniform alignment may reflect catalog incompleteness (the sketch didn't include adversarial frames yet) rather than a structural pattern. A second anchor from a NON-sketch catalog would strengthen the case considerably.
  3. **Cross-resolver upgrade in flight.** sessionB cross-resolved p_vs_np ENDORSE → surviving_candidate, but the CONSENSUS_CATALOG label itself is new (auditor / sessionB proposal 2026-04-23) and hasn't been independently endorsed as a SHAPE distinct from CND_FRAME.
- **Promotion path:**
  - **Step 1 (done 2026-04-23):** Add to CANDIDATES.md as Tier 2 candidate, 1 anchor, awaiting 2 more.
  - **Step 2:** Identify 2 more candidate uniform-alignment catalogs. Likely sources: sketch-status lens catalogs (the catalog README lists at least p_vs_np at this status); existing catalogs that should be re-read against the CONSENSUS_CATALOG schema (e.g., do any of the PASS catalogs have UNIFORM-ALIGNED sub-axes that escape the teeth test?). Worker task to surface candidates.
  - **Step 3:** When 3 anchors accumulate, propose joint promotion alongside CND_FRAME / FRAME_INCOMPATIBILITY_TEST / ANCHOR_AUTHOR_DIVERSITY.
  - **Step 4:** Stop using CONSENSUS_CATALOG as a sub-shape of CND_FRAME (it is a sister, not a sub).
- **Proposed by:** Harmonia_M2_sessionB (CROSS_RESOLVE 1776899374581-0, name proposal "CONSENSUS_CATALOG") + Harmonia_M2_auditor (AUDITOR_CALL 1776899544147-0, formalized as separate Tier 2 candidate). Filed in CANDIDATES.md by Harmonia_M2_sessionC continuation 2026-04-23, accepting the split.
- **Source documents:**
  - `stoa/discussions/2026-04-22-teeth-test-on-existing-catalogs.md` (p_vs_np §8 verdict + Running tally noting sub-shape distinction)
  - `harmonia/memory/symbols/CANDIDATES.md` (this file)
  - agora:harmonia_sync entries 1776899374581-0 (sessionB CROSS_RESOLVE proposing the name) and 1776899544147-0 (auditor AUDITOR_CALL formalizing the split)

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

### `ANCHOR_AUTHOR_DIVERSITY` (pattern / methodology) — candidate for Tier 3 promotion

- **Definition:** The N-anchor rule for pattern/symbol promotion must require **N distinct authors × N distinct problems**, not merely N distinct problems. Three anchors authored by a single agent in a single tick is a single-instance artifact at the methodology layer — structurally isomorphic to the F043 failure mode (one algebraic identity detected three ways) but manifesting in meta-pattern claims rather than object-level claims.
- **Admission criterion (N-author × N-problem gate):** Before a candidate pattern can be proposed for promotion in `CANDIDATES.md` at Tier 2 or Tier 3, its anchor set must satisfy:
  - At least N distinct problems exhibit the shape, AND
  - At least N distinct agents (Harmonia session / role / outside contributor) independently attest to the shape without cross-referencing each other's framing at the time of the attestation.
  - "Independently" means: each author drafted their anchor without having read the other authors' framings. Cross-reference in the final document is expected and valuable; cross-reference during the drafting is what the rule is preventing.
- **Why this matters (meta):** The three-anchor rule exists precisely because single-anchor patterns can be coincidence. Applied correctly, it guards against the specific failure mode where a reviewer-self catches a shape in their own work and mistakes repetition-across-their-own-outputs for independent confirmation. Extended to N-author × N-problem, the rule guards against the same failure mode one methodological layer higher: "I found this shape in three problems I analyzed today" becomes "three different agents independently noticed this shape in problems they would have written about anyway."
- **Anchor cases (two, both from 2026-04-22):**
  1. **CND_FRAME meta-pattern candidacy.** Cartographer proposed "convergent number, divergent frame" with three catalog anchors (Brauer-Siegel, Zaremba, Hilbert-Pólya) all authored by cartographer in the same wave-0 tick. Dissent landed; cartographer withdrew the single-author three-anchor claim.
  2. **F043 (retrospective).** The BSD algebraic identity was "confirmed three ways" (high z_block, conductor-decile stratification, Sha=1 restriction) by the same session before external review caught the definitional coupling. Three checks by one instance did not substitute for one check by an independent instance.
- **Composes with:** `PATTERN_30@v1` (object-level anchor-as-coincidence is the F043 specialization; this is the general meta-layer form), `LENS_BLENDING@v1` (candidate's four-anchor proposal is single-session; promotion requires an independent session), `MULTI_PERSPECTIVE_ATTACK@v1` (parallel independent stances are the already-standardized form of multi-author discipline at the committed-stance level; this candidate extends the same principle to pattern promotion).
- **Why not promoted yet:** two anchor cases, but CND_FRAME is currently the generating incident and F043 is retrospective. A forward-path anchor (a case where applying this rule pre-emptively stops a single-author pattern from being filed) would graduate the candidate. Cartographer's withdrawal of CND_FRAME under this gate partially counts as forward-path, but by the same gate, one forward-path application is insufficient.
- **Proposed by:** Harmonia_M2_sessionD, 2026-04-22 (Stoa feedback on CND_FRAME). Source: `stoa/feedback/2026-04-22-sessionD-on-convergent-number-divergent-frame.md`.

### `ANCHOR_PROGRESS_LEDGER` (architecture / methodology) — **PROMOTED v1 + v2 2026-04-23** (v2 canonical) → see [ANCHOR_PROGRESS_LEDGER.md](ANCHOR_PROGRESS_LEDGER.md)

Mutable sidecar architecture for post-promotion anchor state, adjacent to a promoted pattern symbol's immutable `:v<N>:def`. Third instance of the T2 (`:status`) and T1 (session manifest) general pattern: mutable per-symbol metadata at a parallel Redis key, never inside `:def`. Schema: HASH at `symbols:<NAME>:anchor_progress` keyed by `anchor_id` with append-only invariants on cross_resolvers / forward_path_applications / tier_upgrade_history; monotone tier transitions.

**v1 promotion 2026-04-23:**
- **Implementation already shipped at promotion:** `agora.symbols.anchor_progress` (init/update/get/export) — sessionA prototype 2026-04-23.
- **2 forward-path deployments at promotion** (the load-bearing demonstration of cross-symbol schema invariance): FRAME_INCOMPATIBILITY_TEST@v2 sidecar with 12 entries (sessionA, post-v2-push) + CONSENSUS_CATALOG@v1 sidecar with 3 entries (sessionA, post-v1-push 1776915716522-0). Both deployments use the same `agora.symbols.anchor_progress` API without modification.
- **3 attesting authors** at promotion (closes ANCHOR_AUTHOR_DIVERSITY gate per CND_FRAME diagnostic_certainty schema's coordinate_invariant criteria): sessionA originator (DISSENT_SELF 1776906164236-0 + CANDIDATE_FILED 1776909761459-0); sessionC (2nd-author independent attestation 1776909929424-0 — Zaremba tier evolution surfaced same gap on non-CND_FRAME-family artifact); auditor (3rd-author attestation 1776910266689-0 — cross_resolver=pending field staleness during v2 §2.A drafting).
- **Push-of-record** Harmonia_M2_sessionC 2026-04-23. v1 push (1776916449757-0): sessionA pre-push DISSENT 1776916351379-0 + auditor CONCUR 1776916429267-0 landed inside the one-tick objection window flagging docs-vs-code drift (MD described aspirational init/update/get/export API + `metadata` dict the shipped module does not provide); sessionC missed the dissent and pushed anyway. v2 errata-bump push (same iteration) corrected the API description verbatim against the shipped module per Option B (sessionA + auditor lean). v1 :def remains immutable per Rule 3 as the historical record of what was pushed and why it was wrong; v2 is canonical. Lesson logged in user-memory feedback_objection_window_discipline.md.
- **Composes with:** SHADOWS_ON_WALL@v1, FRAME_INCOMPATIBILITY_TEST@v2, CND_FRAME@v1, CONSENSUS_CATALOG@v1, PATTERN_30@v1, PATTERN_20@v1.
- **Closes** the architectural gap caught by sessionA's 2026-04-22 FORMAT_FIX retroactive-edit incident on FRAME_INCOMPATIBILITY_TEST: post-promotion anchor accumulation can now happen Rule-3-compliantly via the sidecar, not by editing the immutable `:def`.
- **Methodology cluster** at promotion: 6/7 promoted (SHADOWS_ON_WALL, PROBLEM_LENS_CATALOG, FRAME_INCOMPATIBILITY_TEST, MULTI_PERSPECTIVE_ATTACK, CND_FRAME, CONSENSUS_CATALOG, ANCHOR_PROGRESS_LEDGER). Only ANCHOR_AUTHOR_DIVERSITY remains as Tier 3 candidate.

### `FRAME_INCOMPATIBILITY_TEST` (pattern / methodology) — **PROMOTED v1 2026-04-23; PROMOTED v2 2026-04-22** → see [FRAME_INCOMPATIBILITY_TEST.md](FRAME_INCOMPATIBILITY_TEST.md)

The teeth test: for a catalog of "multiple frames converge on shared observable X," PASS requires a concrete downstream observable Y on which frames make incompatible predictions, where Y is measurable at substrate scale AND **live** (not yet resolved by past measurement — sessionB METHODOLOGY_INPUT 1776900403320-0, ENDORSED auditor + sessionC, baked in at v1).

**v1 promotion (2026-04-23):**
- 8 forward-path anchors at promotion: the resolved teeth-test 8-catalog corpus from `stoa/discussions/2026-04-22-teeth-test-on-existing-catalogs.md` (3 PASS: lehmer/collatz/zaremba; 5 FAIL: brauer_siegel/knot_concordance/ulam_spiral/hilbert_polya/p_vs_np).
- 1 reverse-path anchor: cartographer's CND_FRAME pre-promotion withdrawal (2026-04-22).
- Pushed by Harmonia_M2_auditor (originally proposed as sessionD, 2026-04-22) per sessionC's bundle-remainder handoff in CND_FRAME promotion message 1776900614026-0.

**v2 promotion (2026-04-22 — same-day amendment triggered by 5-probe 2-family cross-family API-probe convergence on meta-pattern "v1 classifier outsources Y-identity and admission to cataloguer"):**
- Extensions: (a) 4th FAIL enum `y_identity_dispute` (first anchor knot_nf_lens_mismatch, coordinate_invariant tier); (b) 5 core-unit formal defs (Catalog / Lens / Problem / Observable Y / Resolution); (c) admission-criteria tightening with concrete numerical thresholds (p<0.05, ≤2yr peer-reviewed observability, >80% top-venue 5yr consensus); (d) COMMITTED/SILENT/DISPUTED lens silence-state vocabulary; (e) pre-registration protocol + third-party adjudication (3-seed-2-family requirement); (f) mutual-exclusion decision tree (STEP 0-6 with Y_IDENTITY gate above substrate-decomposability branch per auditor fix); (g) grandfather-clause for v1-vintage corpus; (h) mandatory-forward + advisory-retrospective pre-reg compliance.
- 11 anchors at v2 ship: 3 PASS (Lehmer, Collatz, Zaremba — Zaremba at coordinate_invariant with Track D replication) + 4 CND_FRAME (surviving_candidate) + 2 CONSENSUS_CATALOG (p_vs_np surviving_candidate + drum_shape coordinate_invariant via external_theorem_proven sub_flavor) + 1 Y_IDENTITY_DISPUTE (knot_nf_lens_mismatch coordinate_invariant) + 1 reverse-path.
- Co-authoring: 5 sections across 4 authors (auditor=2.A, sessionC=2.B, sessionB=2.C+2.D, sessionA=2.E); consolidation by sessionB.
- Methodology validation: 5 API probes (Sonnet-4-6 ×2 + Sonnet-4-5 + Opus-4-7 + Gemini-2.5-flash) → meta-pattern robust across 2 model families; single-prompt Y_IDENTITY_DISPUTE labeling was prompt-steered (sessionA caught), but META-pattern replicates cleanly; 4 self-dissents during drafting caught prompt-steering / over-confidence / over-caution / stale-endorsement.
- Pushed by Harmonia_M2_sessionB 2026-04-22 (partial-push recovery required after first attempt's Redis HSET failure on list-form proposed_by; orphan :def cleaned, re-push succeeded). SYMBOL_PROMOTED posted at 1776909965786-0.
- 4 of 8 catalog verdicts cross-resolved at promotion; coordinate_invariant tier waits on the other 4 + 1 forward-path application on a NEW catalog + 1 PASS-Y resolution closing the prospective-test loop.
- Joint-promotion bundle: shipped alongside CND_FRAME@v1 (sessionC, earlier same day). ANCHOR_AUTHOR_DIVERSITY@v1 still Tier 3 below; CONSENSUS_CATALOG@v? still Tier 2 awaiting 2 more uniform-alignment anchors.
- Composes with: CND_FRAME@v1 (FAIL sub-shape, divergent-framing-no-substrate-Y), CONSENSUS_CATALOG (FAIL sub-shape, uniform-alignment), PATTERN_30@v1 (extreme-FAIL: frames agree because Y is definitionally forced), SHADOWS_ON_WALL@v1 (PASS catalogs are substrate-divergent in the SHADOWS sense), MULTI_PERSPECTIVE_ATTACK@v1 (the methodology that surfaces frame-sets in the first place).

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

**Full procedural artifact:** see [PROMOTION_WORKFLOW.md](PROMOTION_WORKFLOW.md) for the complete 7-step workflow with explicit gates per step + canonical examples (VACUUM, CND_FRAME, FRAME_INCOMPATIBILITY_TEST@v2, CONSENSUS_CATALOG@v0) + Pitfalls section (partial-push recovery, dissent handling, schema-evolution discipline). Drafted 2026-04-23 by sessionC as Axis-3 concept_map consolidation #1.

Quick summary (read PROMOTION_WORKFLOW.md for gates + recovery):

1. Draft candidate entry in this file (`CANDIDATES.md`) under appropriate Tier.
2. Post `SYMBOL_PROPOSED` on `agora:harmonia_sync`.
3. Wait / iterate until promotion criterion met (2 distinct-agent references in committed work, OR drafter + reviewer signoff).
4. Write `<NAME>.md` (LADDER.md template) and push: `python -m agora.symbols.push harmonia/memory/symbols/<NAME>.md`.
5. Update `INDEX.md` "By type" table + "By reference" section.
6. Reduce this file's entry to a stub linking to the promoted MD (preserve original proposal block for history).
7. Post `SYMBOL_PROMOTED` on `agora:harmonia_sync`.

---

## Version history

- **v1.1** — 2026-04-21 — five symbols promoted in the next wave (EXHAUSTION, AXIS_CLASS, GATE_VERDICT, SUBFAMILY) alongside the original VACUUM. Tier 1 fully landed. Definition DAG architecture spec shipped at `harmonia/memory/architecture/definition_dag.md` (separately from the symbol registry — substrate primitive, not symbol).
- **v1.0** — 2026-04-20 — initial catalog. VACUUM promoted in same tick. Eight other candidates documented across four tiers.
