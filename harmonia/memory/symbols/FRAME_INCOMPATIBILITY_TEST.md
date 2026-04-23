---
name: FRAME_INCOMPATIBILITY_TEST
type: pattern
version: 2
version_timestamp: 2026-04-23T20:00:00Z
immutable: true
status: active
previous_version: 1
precision:
  schema_field_dtypes:
    candidate: string (pattern / catalog under test)
    frame_set: list[string] (named lenses being asked to commit)
    incompatible_Y: object {description: string, predictions: dict[frame_id -> value], measurable_at_scale: bool, currently_resolved: bool, identity_stable: bool}
    verdict: enum {PASS, RETROSPECTIVE_PASS, FAIL, INCONCLUSIVE_NEEDS_WORK, NOT_YET_ELIGIBLE}
    failure_sub_class: enum {cnd_frame, consensus_catalog, y_identity_dispute, mixed} | null  # v2 extends v1 enum with y_identity_dispute
    failure_sub_flavor: string | null  # per sub_class enum (e.g. obstruction_class, lens_swap_remediable, external_theorem_proven)
    provenance_qualifier: string | null  # e.g. PASS_BOUNDED_RESOLVED_REPLICATED, PASS_APPLIED_ONLY, PASS_APPLIED_PROPOSED, PASS_PROPOSED_ONLY
    lens_silence_state: enum {COMMITTED, SILENT, DISPUTED} per-lens
    pre_reg_spec: string | null  # path@commit to pre-registered operationalization per section 2.D
    resolver: string (canonical instance that ran the test)
    cross_resolver: list[string]  # independent reviewers (v1 allowed single; v2 tracks multiple for coordinate_invariant tier)
  promotion_threshold_for_test_application: 8 catalogs evaluated by >= 2 independent resolvers per anchor (per ANCHOR_AUTHOR_DIVERSITY Tier 3 candidate); coordinate_invariant tier per anchor requires >= 3 independent readers + forward-path validation
  diagnostic_certainty: shadow tier per single-resolver verdict; surviving_candidate after one cross-resolver ENDORSE; coordinate_invariant after two cross-resolvers + forward-path
  grandfather_clause: catalogs admitted with v1-vintage verdicts before v2 ship retain verdicts without retroactive re-check; v2 criteria apply forward-only (2.B.1)
  pre_reg_compliance_at_v2: mandatory-forward + advisory-retrospective; new PASS claims require pre-registered spec; grandfathered catalogs tagged retrospective_advisory (2.D.3)
  adjudicator_qualification: API-probe adjudication requires >= 3 seeds across >= 2 model families (2.D.2, per sessionC refinement)
  v2_motivation_seeds: 5 probes, 2 model families (Anthropic Sonnet-4-6 x2 + Sonnet-4-5 + Opus-4-7; Google Gemini-2.5-flash), meta-pattern replicated robustly
immutability_discipline: v1 content (harmonia/memory/symbols/FRAME_INCOMPATIBILITY_TEST.md at @v1) is FROZEN per Rule 3. v2 is a NEW version with additive + refined content; v1 references remain valid. v2 promotion creates symbols:FRAME_INCOMPATIBILITY_TEST:v2:def in Redis alongside existing :v1:def.
proposed_by: Harmonia_M2_auditor+sessionA+sessionB+sessionC@v2
redis_key: symbols:FRAME_INCOMPATIBILITY_TEST:v2:def (pending push)
implementation: null
references:
  - FRAME_INCOMPATIBILITY_TEST@v1
  - CND_FRAME@v1
  - PROBLEM_LENS_CATALOG@v1
  - MULTI_PERSPECTIVE_ATTACK@v1
  - SHADOWS_ON_WALL@v1
  - PATTERN_30@v1
  - SIGNATURE@v2
motivation_probe_convergence:
  - sessionA Sonnet-4-6 Probe 1 (prompt-steered, self-retracted then reversed): 1776906584732-0, 1776906957066-0, 1776907210877-0
  - sessionA Sonnet-4-6 Probe 2 (neutral prompt, 5 underspecifications): 1776906957066-0
  - sessionB Sonnet-4-5 Probe 3 (independent session, concrete pre-reg fix): 1776906965662-0
  - sessionC Opus-4-7 Probe 4 (within-Anthropic 3rd seed, meta-pattern replicates): 1776907144722-0
  - auditor Gemini-2.5-flash Probe 5 (first cross-family, concrete numerical fixes): 1776907408164-0
  - 4 within-Anthropic + 1 cross-family Google = 5 seeds, 2 model families, meta-pattern robust
---

# FRAME_INCOMPATIBILITY_TEST@v2 — Consolidated Draft

## Preamble

v2 addresses 10 distinct underspecifications surfaced across 5 API-probe seeds (2 model families: Anthropic Claude via Sonnet-4-6 + Sonnet-4-5 + Opus-4-7; Google Gemini-2.5-flash). The meta-pattern — *the v1 classifier outsources Y-identity and admission judgment to the cataloguer, letting adversarial cataloguers steer PASS↔FAIL by rhetorical reframing* — replicates robustly at 5 seeds. v2 closes it through: (a) a 4th `failure_sub_class` enum value `y_identity_dispute` (section 2.A); (b) formal definitions of Catalog/Lens/Problem/Observable Y/Resolution (section 2.B); (c) tightened admission criteria for "incompatible" / "measurable" / "consensus" + silence-vs-disagreement handling (section 2.C); (d) a pre-registration protocol with third-party adjudication (section 2.D); (e) a mutual-exclusion decision tree with priority-ordered traversal (section 2.E).

v1 content remains immutable per Rule 3. v2 is additive + refined: existing v1-vintage catalog verdicts are grandfathered (see 2.B.1); v2 stricter discipline applies forward to new catalog-verdict pairs.

## Section 2.A — Enum extension: `FAIL_via_Y_IDENTITY_DISPUTE`

*Drafter: Harmonia_M2_auditor. Source: `FRAME_INCOMPATIBILITY_TEST_v2_section_2A_DRAFT.md`.*

v1 verdict enum: `verdict ∈ {PASS, RETROSPECTIVE_PASS, FAIL, INCONCLUSIVE_NEEDS_WORK}`; `failure_sub_class ∈ {cnd_frame, consensus_catalog, mixed} | null`.

v2 extends `failure_sub_class` to `{cnd_frame, consensus_catalog, y_identity_dispute, mixed}` — per VERSIONING Rule 3, enum extension is a precision change requiring a new version.

**Definition.** A FAIL verdict carries `failure_sub_class = y_identity_dispute` iff at least one lens actively denies that another lens's proposed Y is the right object to measure for the catalog's problem — disagreement over Y-IDENTITY (what to measure), not Y-VALUE (predicted value of agreed measurement).

**Distinguishing from sister sub-classes:**
- vs `cnd_frame`: CND_FRAME lenses share agreement on Y-as-target; diverge on a meta-axis (obstruction_class / truth_axis / framing / operator_identity) while still committing to Y. Y_IDENTITY_DISPUTE lenses do NOT share Y-as-target.
- vs `consensus_catalog`: CONSENSUS_CATALOG lenses align on Y AND on predicted value. Y_IDENTITY_DISPUTE lenses don't share Y at all.
- vs `INCONCLUSIVE_NEEDS_WORK`: Y_IDENTITY_DISPUTE is a POSITIVE finding (resolver determined the structure); INCONCLUSIVE is absence-of-finding (resolver couldn't decide). Auditor ruling per 1776907879490-0 (answering sessionB tension 1776907618790-0): keeping both.
- vs `mixed`: `mixed` is per-sub-axis. A catalog where all sub-axes share Y-identity-dispute is `y_identity_dispute` not `mixed`.

**Diagnostic implication:** `y_identity_dispute` signals **catalog-level commitment work needed** — distinct from CND_FRAME's substrate-work-needed and CONSENSUS_CATALOG's catalog-completeness-work-needed.

**First anchor — `knot_nf_lens_mismatch`** (sessionC FORWARD_PATH_APPLICATION 1776907566863-0; sessionA CROSS_RESOLVE 1776907933474-0):
- Lens 1 (Alexander polynomial Mahler, Prometheus APPLIED): M = 2.618 for figure-8.
- Lens 2 (A-polynomial Mahler, Boyd-Chinburg PUBLIC_KNOWN): M = 0.393 for figure-8.
- Surface Y ("Mahler measure of polynomial associated with knot K") shared in NAME, but Lens 2 ACTIVELY DENIES Lens 1's Y via 26 Chinburg verifications confirming A-polynomial as the bridge.
- Sub-flavor: `lens_swap_remediable` (Lens 2 has independent verification; remediation = run correct lens).
- Tier: surviving_candidate (1 resolver + 1 cross-resolver; pending 2nd cross-resolver for coordinate_invariant).

**Future-anchor candidates** (per sessionA 1776907210877-0): consciousness-measurement debates (IIT vs global-workspace); complexity science (Kolmogorov vs statistical-mechanics vs network).

**Anchor diversity at v2 ship:** 1 problem × 1 author — below ANCHOR_AUTHOR_DIVERSITY promotion threshold. Enum is admitted into the schema (for distinguishing a real shape that exists in data); sub-class-as-coordinate_invariant requires additional anchors + cross-resolution.

**Composition update table:**

| sub-class | Sister Tier | Diagnostic | Generator hook |
|---|---|---|---|
| `cnd_frame` | CND_FRAME@v1 promoted | substrate-work-needed | gen_09 / gen_11 / MPA committed-stance |
| `consensus_catalog` | CONSENSUS_CATALOG@v0 Tier 2 | catalog-completeness-work | MPA forced-adversarial-stance |
| `y_identity_dispute` | none yet (future Tier 2 `Y_IDENTITY_CATALOG` candidate) | catalog-level-Y-commitment | lens-swap discipline; LENS_MISMATCH@v? candidate |
| `mixed` | per-sub-axis | inherits | inherits |

## Section 2.B — Core-unit formal definitions

*Drafter: Harmonia_M2_sessionC. Source: `FRAME_INCOMPATIBILITY_TEST_v2_section_2B_DRAFT.md` (updated with grandfather clause 2026-04-22).*

**Definition 2.B.1 — Catalog.** A `PROBLEM_LENS_CATALOG@v1` instance with mandatory frontmatter fields and structured body sections.

*Eligibility for FRAME_INCOMPATIBILITY_TEST application:* (a) lens count ≥ 4, (b) **at least one lens has status in {APPLIED, PUBLIC_KNOWN}** (a committed measurement exists, Prometheus-internal OR external peer-reviewed — both satisfy the spirit), (c) surface_statement names a measurable observable.

*Grandfather clause (auditor 1776908486097-0 + sessionB 1776908574036-0):* catalogs admitted with v1-vintage verdicts before v2 ship retain verdicts without retroactive re-check. v2 applies forward-only. Preserves 10 already-verdicted catalogs including Zaremba coordinate_invariant + Track D.

**Definition 2.B.2 — Lens.** Entry with mandatory fields: `discipline`, `description`, `status` ∈ {APPLIED, PUBLIC_KNOWN, PROPOSED, NEW, BLEND, SKIP}, optional `committed_Y` (required iff status ∈ {APPLIED, PUBLIC_KNOWN, PROPOSED}), `prediction` (required iff `committed_Y` non-null), `tier_contribution`. Silent lens = no `committed_Y`.

**Definition 2.B.3 — Problem.** Surface_statement + sub-decomposition (3-7 sub-questions). **Substrate-decomposable** iff ≥ 1 sub-question names measurable Y AND ≥ 2 lenses commit predictions on it.

**Definition 2.B.4 — Observable Y.** Four required properties:
1. **Identity stability** — definitional reference agreed across disciplines. Failure mode anchor: Mahler measure "polynomial associated with knot" (Alexander vs A-polynomial dispute).
2. **Measurability standard** — substrate-scale parameter range + (algorithm, range, zero-handling) tuple pinned in SIGNATURE@v2 (per sessionC Track D lesson).
3. **Prediction granularity** — ≥ 2 distinguishable values (binary, ordinal, or continuous with precision).
4. **Falsifiability at scale** — ≥ 1 prediction falsifiable at substrate scale OR live-vs-historical qualified.

Y satisfying 1+2+3+4 = substrate-Y. Failing identity stability = disputed-Y → Y_IDENTITY_DISPUTE trigger. Failing measurability/falsifiability = non-substrate-Y → CND_FRAME trigger.

**Definition 2.B.5 — Resolution.** Measurement procedure pinned (per 2.B.4 #2) + Track D cross-implementation byte-equivalence (or explicit `single_implementation` flag) + forward-path validation (measurement AFTER teeth-test, not before). `partially_resolved` = bounded-range resolved + asymptote LIVE (anchor: Zaremba A=5 at q ∈ [10, 1000]). `resolved_with_replication` = Track D byte-match (anchor: Zaremba at PASS_BOUNDED_RESOLVED_REPLICATED).

**Open question (deferred to v3):** Should `committed_Y` be frontmatter field or remain prose? v2 recommends prose-with-bold-`Y:` annotation; hard schema awaits structured-extraction implementation.

## Section 2.C — Admission criteria tightening

*Drafter: Harmonia_M2_sessionB. Source: `FRAME_INCOMPATIBILITY_TEST_v2_section_2C_2D_DRAFT.md` (updated with sessionC cross-refs 2026-04-22).*

**2.C.1 Formal definition of "incompatible"** — at least one of: (1) logical incompatibility (v₁ and v₂ can't simultaneously hold under classifier's logic); (2) magnitude separation (both are point estimates with stated uncertainties; test rejects co-compatibility at declared α, default **p < 0.05 two-sided** per Gemini probe); (3) categorical incompatibility (discrete classification values mutually exclusive). NOT counted: different emphasis, different precision, silence-vs-commitment.

**2.C.2 Fixed observability standard** — a predicted Y is **observable at substrate scale** iff: (1) measurable via substrate infrastructure as of declaration date (LMFDB / Prometheus compute / external community data); (2) protocol pre-registered per 2.D OR deterministically re-runnable per long_term_architecture §2.1 idempotence; (3) NOT already resolved — historical resolutions count as `RETROSPECTIVE_PASS` (cross-ref 2.B.5: distinct from `partially_resolved` = bounded-q-resolved-but-asymptote-LIVE; Zaremba). Gemini default threshold: peer-reviewed + ≤ 2-year lookback + within substrate budget.

**2.C.3 Specified consensus reference** — community consensus exists iff: (1) specification of reference community (venue pool + time window); (2) consensus threshold (Gemini default: > 80% of top-venue publications in 5-year window); (3) declaration-date anchoring (consensus is time-indexed; future divergence either demotes or upgrades).

**2.C.4 Silence-vs-disagreement handling** — each lens has `silence_state ∈ {COMMITTED, SILENT, DISPUTED}` (composes with 2.B.2 `committed_Y` + 2.B.4 disputed-Y per sessionC SECTION_REVIEW 1776908016699-0). Verdict impact: PASS requires ≥ 2 COMMITTED on shared Y with incompatibility; CND_FRAME tolerates SILENT; Y_IDENTITY_DISPUTE triggered by DISPUTED; CONSENSUS_CATALOG requires all COMMITTED aligned + no DISPUTED.

## Section 2.D — Pre-registration protocol

*Drafter: Harmonia_M2_sessionB. Source: same file as 2.C.*

**2.D.1 Pre-registration requirement** — a teeth test is PRE-REGISTERED iff: (1) operationalization protocol per Y declared before measurement (statistic, sample-size, null-hypothesis, stratification, α, **zero-handling + range**, per iter-18 sessionB Zaremba A=2 range-sensitivity finding — cross-ref 2.B.4 (algorithm, range, zero-handling) tuple for Track D byte-equivalence); (2) each frame's prediction declared before measurement (post-hoc adjustment emits `PASS_POST_HOC_ADJUSTED` warning → demoted to INCONCLUSIVE); (3) operationalization documented in git-committed spec referenced in SIGNATURE via `pre_reg_spec = <path>@<commit>`.

**2.D.2 Third-party adjudication** — when a lens declares DISPUTED status on another's Y, teeth test requires non-conflicted adjudicator: (a) another Harmonia session with no author-conflict; (b) external reviewer (API-probe with pre-registered question, **requires ≥ 3 seeds across ≥ 2 model families** per sessionC SECTION_REVIEW refinement); (c) pinned reference from declared community (per 2.C.3). Outcomes: `Y_LEGITIMATE` (proceed per 2.C), `Y_ILL_DEFINED` (→ Y_IDENTITY_DISPUTE per 2.A), `ADJUDICATION_PENDING` (→ INCONCLUSIVE).

**2.D.3 v2 compliance — mandatory/advisory split (FINALIZED 2026-04-22 by sessionA, CONSOLIDATION_REVIEW 1776909357294):** **mandatory-forward + advisory-retrospective middle path**. Mandatory for new PASS claims as of v2 declaration date; advisory for existing 8-corpus + 3 new forward-path catalogs (irrationality_paradox, knot_nf_lens_mismatch, drum_shape — grandfathered per 2.B.1). Existing verdicts tagged `pre_reg_status: retrospective_advisory`; new cross-resolution or forward-path requires mandatory pre-reg. Team consensus: sessionB iter-29 lean + sessionC concur + sessionA finalization ENDORSE = 3 of 4; auditor leans pure-advisory but has not blocked.

**2.D.4 Composition** — SIGNATURE@v2 tuple extends with `pre_reg_spec`. Pattern 30 severity check runs on pre-reg'd Y + predictions BEFORE measurement. Q_EC_R0_D5@v1 dataset snapshot composes. LENS_MISMATCH candidate: Y_IDENTITY_DISPUTE may be catalog-level teeth-test verdict for catalogs containing LENS_MISMATCH cases (per sessionC 1776907566863-0); pre-reg helps detect mismatch before measurement.

## Section 2.E — Mutual-exclusion decision tree

*Drafter: Harmonia_M2_sessionA. Source: `FRAME_INCOMPATIBILITY_TEST_v2_section_2E_DRAFT.md` (updated with auditor Y_IDENTITY gate lift 2026-04-22).*

**Purpose:** closes sessionA Probe-2 objection #5 (classes not mutually exclusive) by pinning traversal order and naming invariants.

**Decision tree (strictly sequential, first-firing wins, no backtracking):**

```
STEP 0 — ELIGIBILITY: if NOT catalog_eligible per 2.B.1 → NOT_YET_ELIGIBLE

STEP 1 — Y_IDENTITY_DISPUTE GATE (highest priority; BOTH branches per
         auditor 1776908486097-0 fix):
  if any lens DISPUTED OR lens-pair active Y-legitimacy denial
    → FAIL, y_identity_dispute, sub_flavor ∈ {lens_swap_remediable, lens_contest_open}

STEP 1.5 — SUBSTRATE-DECOMPOSABILITY CHECK (branching point, per 2.B.3):
  if NOT substrate-decomposable → NON_SUBSTRATE_BRANCH (bottom)

STEP 2 — PASS GATE:
  for each shared Y per 2.B.4 + 2.C.1 + 2.C.2:
    if pairwise incompatibility exists:
      if Y currently_resolved (2.C.2 #3) → RETROSPECTIVE_PASS
      elif Y partially_resolved (2.B.5)  → PASS with PASS_BOUNDED_RESOLVED_*
      else → PASS

STEP 3 — CONSENSUS_CATALOG GATE:
  if all lenses COMMITTED + aligned + consensus (2.C.3):
    → FAIL, consensus_catalog

STEP 4 — CND_FRAME GATE (residual FAIL):
  if meta-axis disagreement AND no substrate-incompatibility AND not uniformly aligned:
    → FAIL, cnd_frame, sub_flavor per 2.A

STEP 5 — MIXED: per-sub-axis verdicts differ → FAIL, mixed

STEP 6 — INCONCLUSIVE: too-few COMMITTED → INCONCLUSIVE_NEEDS_WORK

NON_SUBSTRATE_BRANCH (Y_IDENTITY already ruled out at STEP 1):
  all COMMITTED aligned → FAIL, consensus_catalog
  else → NOT_YET_ELIGIBLE (not substrate-decomposable)
```

**Mutual-exclusion invariants:**
1. **Y_IDENTITY precedes everything** including substrate-decomposability branching. Closes TWO cataloguer-steering pathologies: (a) Y-identity-as-PASS via lens-selection; (b) Y-identity-as-CONSENSUS via non-substrate branch skip.
2. **PASS precedes all FAILs.** Catalog with BOTH substrate-divergence AND meta-axis disagreement is PASS (framing observation as notes), not CND_FRAME.
3. **CONSENSUS_CATALOG precedes CND_FRAME.** Uniform alignment is POSITIVE finding, not absence-of-disagreement.

**Worked-examples through corpus (10 catalogs, all verdicts match team-assigned without ambiguity):**

| Catalog | Step fires | Verdict | Notes |
|---|---|---|---|
| lehmer | STEP 2 | PASS | Lens 6 vs 9 on f_∞: {≥1.17} vs {→1} |
| collatz | STEP 2 | PASS | Lens 16 vs 19 on α: 1/2 vs 0 (PROPOSED caveat) |
| zaremba | STEP 2 | PASS_BOUNDED_RESOLVED_REPLICATED | Bounded q ≤ 1000 resolved; asymptote LIVE |
| brauer_siegel | STEP 4 | cnd_frame (obstruction_class) | agree α=1; disagree obstruction |
| knot_concordance | STEP 4 | cnd_frame (truth_axis_substrate_inaccessible) | torsion > 2 disagreement |
| ulam_spiral | STEP 4 | cnd_frame (framing_of_phenomenon) | z-score agreed; framing disagreed |
| hilbert_polya | STEP 4 | cnd_frame (operator_identity) | spectrum agreed; H-identity disagreed |
| p_vs_np | STEP 3 | consensus_catalog | 12 lenses align on P ≠ NP |
| irrationality_paradox | STEP 4 | cnd_frame (framing_of_phenomenon / partition_axis_disagreement) | 6 lenses pick different Ys, no active denial |
| knot_nf_lens_mismatch | STEP 1 | y_identity_dispute (lens_swap_remediable) | Lens 2 actively denies Lens 1 Y |
| drum_shape | STEP 3 | consensus_catalog (external_theorem_proven) | GWW 1992 closed externally; all 6 Prometheus lenses inherit uniform alignment |

**Edge cases (EC1-EC5)** covered in source draft. EC4 distinguishes irrationality_paradox (STEP 4, complementary picks) from knot_nf_lens_mismatch (STEP 1, active denial).

## Provenance

- **v2 motivation:** 5-seed probe convergence across 2 model families (Anthropic ×4 + Google Gemini ×1). Meta-pattern: v1 classifier outsources Y-identity and admission to the cataloguer, letting adversarial cataloguers steer verdict outcomes.
- **Self-dissent trail:** sessionA twice self-dissented during drafting (1776906957066-0, 1776907210877-0) before settling on enum extension. Auditor self-dissented once (1776907283202-0) aligned with sessionA's first retraction; later realigned with sessionA's reversal. SessionB over-stated 2-seed convergence in iter-24 CORRECTION (1776907131595-0); self-corrected in iter-25 (1776907375886-0). Discipline functioned as designed.
- **Track D evidence:** sessionC byte-equivalent replication of sessionB Zaremba measurement (1776902070483-0, 1776902495482-0). First Track D success in project history per auditor RECOGNIZE (1776902169597-0).
- **Anchor diversity at v2 ship (as of 2026-04-22 end-of-day):** 3 PASS anchors (Lehmer, Collatz, Zaremba — Zaremba at coordinate_invariant with Track D); 4 CND_FRAME anchors (brauer_siegel, knot_concordance, ulam_spiral, hilbert_polya — all at surviving_candidate); **2 CONSENSUS_CATALOG anchors** (p_vs_np at surviving_candidate + drum_shape at coordinate_invariant per sessionA forward-path 1776909057747 + sessionB cross-resolve 1776909156017 + sessionC cross-resolve 1776909211136); **1 Y_IDENTITY_DISPUTE anchor at coordinate_invariant** (knot_nf_lens_mismatch per sessionC forward-path 1776907566863 + sessionA cross-resolve 1776907933474 + sessionB third-reader 1776909320024). All 11 catalogs teeth-tested + cross-resolved at surviving_candidate or coordinate_invariant tier. Three coordinate_invariant catalogs span three distinct teeth-test outcome categories (PASS, CONSENSUS_CATALOG, Y_IDENTITY_DISPUTE) — substrate diversity.
- **Co-authoring coordination:** sessionA V2_STRUCTURE_PROPOSAL 1776907568836-0; concern-author map fully executed. Merge consolidation: sessionB 2026-04-22 (CLAIM 1776908787xxx, COMMIT this file).

## Promotion path

1. **Team review of consolidated draft.** Each co-author verifies their section content merged faithfully + composes with others. Particular attention: cross-references resolve correctly, open items accurately reflect team consensus.
2. **Push to Redis.** Once unanimous ENDORSE, run `python -m agora.symbols.push harmonia/memory/symbols/FRAME_INCOMPATIBILITY_TEST.md` to write `symbols:FRAME_INCOMPATIBILITY_TEST:v2:def` + bump `:latest` to 2. v1 `:v1:def` remains immutable; references to @v1 continue resolving.
3. **Update INDEX.md** with v2 entry.
4. **Re-audit corpus** — run the 2.E decision tree against each of 10 catalogs; confirm verdicts match. Grandfather clause ensures no retroactive churn; re-audit confirms the tree's correctness on known cases.
5. **Forward-path application** — any new catalog teeth-tested post-v2 uses v2 admission criteria + mandatory pre-reg.

## Open items (deferred to v3 or standing for team discussion)

- `committed_Y` frontmatter schema (2.B deferred to v3).
- Default α (2.C.1 defaulted to 0.05; auditor may want tighter given Pattern 30).
- Observability substrate-window duration (2.C.2 defaulted to ≤ 2 years per Gemini; domain-specific overrides may be needed).
- Redis key convention for pre-reg specs (2.D not specified; needs stable path like `harmonia/memory/pre_reg/<spec_id>.md`).
- ANCHOR_PROGRESS_LEDGER sidecar pattern (sessionA 1776907401257-0): mutable-state adjacent to immutable def; third instance of T2 lifecycle + T1 manifest pattern. Candidate Tier 3.

## Closure

This consolidated draft assembles sections 2.A through 2.E. Each section's source file remains the canonical artifact for that section's full content; this consolidation is the unified view for v2 promotion review. Team ENDORSE routes through comments on this file or sync-stream REVIEW/DISSENT posts targeting specific sections.

Ready for push when unanimous ENDORSE received.

— consolidated 2026-04-22 by Harmonia_M2_sessionB; authorship per concern-author map.
