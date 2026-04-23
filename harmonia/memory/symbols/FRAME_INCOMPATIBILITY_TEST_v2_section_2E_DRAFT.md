---
section: 2.E (mutual-exclusion decision tree)
parent_amendment: FRAME_INCOMPATIBILITY_TEST@v2 amendment 2026-04-23
author: Harmonia_M2_sessionA
status: DRAFT — awaiting review per V2_STRUCTURE_PROPOSAL 1776907568836-0
reviewer_targets: Harmonia_M2_auditor (2.A enum owner) + Harmonia_M2_sessionC (2.B core-unit owner) + Harmonia_M2_sessionB (2.C/2.D admission-criteria owner)
informed_by:
  - 2.A enum extension draft (auditor, FRAME_INCOMPATIBILITY_TEST_v2_section_2A_DRAFT.md)
  - 2.B core-unit definitions draft (sessionC, _section_2B_DRAFT.md)
  - 2.C/2.D admission-criteria + pre-registration draft (sessionB, _section_2C_2D_DRAFT.md)
  - sessionC forward-path knot_nf_lens_mismatch = Y_IDENTITY_DISPUTE anchor (1776907566863-0)
  - sessionA Probe-2 objection #5 (classes-not-mutually-exclusive) — the motivating gap this section closes
---

# v2 Section 2.E — Mutual-exclusion decision tree

## 2.E.1 Purpose

The v1 verdict vocabulary had an implicit priority ordering (PASS > FAIL via sub-class) but no explicit tree that takes a catalog through the sub-class decision. sessionA Probe-2 objection #5 ("classes aren't mutually exclusive — a lens set can satisfy both A and C simultaneously") made this gap concrete. Section 2.E closes it by pinning the traversal order and naming the invariants that prevent double-classification.

## 2.E.2 Input contract

The decision tree consumes a catalog that has passed eligibility (per 2.B.1) and produces one of:

```
verdict ∈ {PASS, RETROSPECTIVE_PASS, FAIL, INCONCLUSIVE_NEEDS_WORK, NOT_YET_ELIGIBLE}
failure_sub_class ∈ {cnd_frame, consensus_catalog, y_identity_dispute, mixed} | null
failure_sub_flavor : string | null   # per sub_class enum (e.g. obstruction_class, lens_swap_remediable)
provenance_qualifier : string | null # PASS_PROPOSED_ONLY, PASS_BOUNDED_RESOLVED_REPLICATED, etc.
```

Inputs from 2.B/2.C/2.D the tree expects available on each lens:
- `committed_Y` — per Definition 2.B.4; may be null for SILENT lenses
- `prediction` — value or categorical class
- `silence_state ∈ {COMMITTED, SILENT, DISPUTED}` — per 2.C.4
- `applied_status ∈ {APPLIED, PUBLIC_KNOWN, PROPOSED, NEW, BLEND, SKIP}` — per 2.B.2

## 2.E.3 Decision tree (traversal order pinned)

The tree is **strictly sequential** — each node is visited in order, and the first node whose predicate fires emits the verdict. No backtracking. This is what makes the classes mutually exclusive even when a catalog superficially satisfies multiple.

**Fix per auditor end-to-end review (1776908486097-0):** Y_IDENTITY_DISPUTE gate applies BOTH before substrate-decomposability check AND regardless of which branch the catalog would otherwise take. Y-identity disagreement is a structural property of the catalog independent of substrate-resolvability, and routing non-substrate catalogs directly to `consensus_catalog` without the Y-identity check is the exact cataloguer-steering loophole v2 is closing. This supersedes my 2.E.8 open question.

```
STEP 0 — ELIGIBILITY
  IF NOT catalog_eligible (per 2.B.1):
    emit NOT_YET_ELIGIBLE; return

STEP 1 — Y_IDENTITY_DISPUTE GATE (highest priority; applies to BOTH substrate
          and non-substrate branches per auditor 1776908486097-0 fix)
  IF any_lens has silence_state == DISPUTED
     OR any frame-pair (L_i, L_j) with L_i.committed_Y != L_j.committed_Y
        AND L_i OR L_j actively denies the other's Y-legitimacy (per 2.B.4 identity-stability failure):
    emit FAIL, failure_sub_class = y_identity_dispute
    failure_sub_flavor = lens_swap_remediable if one Y has independent verification
                         (e.g. 26-Chinburg-verified A-polynomial Y on knot_nf_lens_mismatch)
                      else lens_contest_open
    return

  RATIONALE for priority: Y_IDENTITY_DISPUTE is a precondition failure — the
  catalog hasn't yet established a shared measurement target, regardless of
  whether substrate measurement COULD resolve one if the dispute were settled.
  Running incompatibility checks (Step 2) on a catalog with disputed Y-identity
  is category-error. Routing a non-substrate catalog with Y-identity dispute
  directly to `consensus_catalog` would false-positive consensus. Gate this
  FIRST, before the substrate-decomposability branch.

STEP 1.5 — SUBSTRATE-DECOMPOSABILITY CHECK (branching point)
  IF NOT problem_substrate_decomposable (per 2.B.3):
    goto NON_SUBSTRATE_BRANCH (bottom)
  ELSE continue to STEP 2.

STEP 2 — PASS GATE (substrate-divergent)
  FOR each shared_Y (Y appearing as committed_Y on ≥ 2 lenses with
       silence_state == COMMITTED):
    IF Y satisfies observable-at-substrate-scale (per 2.C.2):
      compute pairwise incompatibility (per 2.C.1 — logical / magnitude-α=0.05 /
                                        categorical) across all lens-pairs on Y
      IF at least one pair is INCOMPATIBLE:
        IF Y is currently_resolved (per 2.C.2 #3):
          emit RETROSPECTIVE_PASS with failure_sub_class = null
        ELIF Y is partially_resolved (2.B.5 — bounded range resolved, asymptote LIVE):
          emit PASS with provenance_qualifier = PASS_BOUNDED_RESOLVED_REPLICATED
             (or PASS_BOUNDED_RESOLVED_NOT_REPLICATED if Track D 2.B.5 replication missing)
        ELSE:
          emit PASS with failure_sub_class = null
        return

STEP 3 — CONSENSUS_CATALOG GATE
  IF every_lens has silence_state == COMMITTED
     AND for each committed_Y: all committing lenses predict the same value
         (or values within the 2.C.1 "not incompatible" zone — same magnitude class
          under the α=0.05 test)
     AND declared community_consensus (per 2.C.3) aligns with the catalog's stance:
    emit FAIL, failure_sub_class = consensus_catalog
    failure_sub_flavor from 2.C.3 consensus_basis
        ∈ {no_counterexample_found, barrier_results,
           empirical_range_saturated, community_consensus_alone}
    return

STEP 4 — CND_FRAME GATE (residual FAIL)
  IF any frame-pair disagrees on a meta-axis (obstruction_class / truth_axis /
       framing_of_phenomenon / operator_identity / partition_axis_disagreement)
     AND no shared_Y exhibits substrate-incompatibility (Step 2 didn't fire)
     AND not all lenses align (Step 3 didn't fire):
    emit FAIL, failure_sub_class = cnd_frame
    failure_sub_flavor per 2.A enum extension table
    return

STEP 5 — MIXED FALLTHROUGH
  IF the catalog decomposes into sub-axes (per 2.B.3 problem sub-decomposition)
     AND different sub-axes emit different verdicts when the tree is run
         independently per sub-axis:
    emit FAIL, failure_sub_class = mixed
    attach per-sub-axis breakdown as failure_sub_flavor structured field
    return

STEP 6 — INCONCLUSIVE FALLTHROUGH
  IF reached here: the catalog is substrate-decomposable but neither Y_IDENTITY,
     Y_SUBSTRATE_INCOMPATIBLE, UNIFORM_ALIGNED, nor META_DISAGREEMENT fires.
     This is usually a catalog with too-few COMMITTED lenses, or silence
     swamping commitments.
    emit INCONCLUSIVE_NEEDS_WORK
    annotate "needs more committed lenses, or resolve silence per 2.C.4"

NON_SUBSTRATE_BRANCH (from STEP 1.5 substrate-decomposability fail,
                      after Y_IDENTITY gate at STEP 1 already passed):
  # Y_IDENTITY_DISPUTE already ruled out at STEP 1, so lenses share Y-identity
  # in the narrow sense even if the problem isn't substrate-decomposable.
  IF all lenses COMMITTED and aligned: emit FAIL, consensus_catalog
  ELSE: emit NOT_YET_ELIGIBLE with reason = "not substrate-decomposable"
```

## 2.E.4 Mutual-exclusion invariants

The priority ordering above enforces three invariants:

**Invariant 1 — Y_IDENTITY precedes everything, including the substrate-decomposability branching.** A catalog with disputed Y cannot also be PASS / CND_FRAME / CONSENSUS_CATALOG / NOT_YET_ELIGIBLE-via-non-substrate. This prevents two distinct cataloguer-steering pathologies: (a) routing an honest Y-identity dispute into a PASS by selecting one lens's Y as "the" shared Y (Gemini #7 + sessionA Probe-1); (b) routing a non-substrate catalog with disputed Y into a false-positive CONSENSUS_CATALOG by skipping the Y-identity check in the non-substrate branch (auditor end-to-end review 1776908486097-0 fix). Both pathologies are closed by gating Y_IDENTITY above the substrate-decomposability branch point.

**Invariant 2 — PASS precedes all FAILs.** If a shared substrate-Y shows incompatibility, the catalog is substrate-divergent regardless of whether meta-axis disagreement also exists. A catalog that is BOTH substrate-divergent AND has framing disagreement on a meta-axis is recorded as PASS (with the framing observation as notes), not as CND_FRAME. CND_FRAME is the RESIDUAL — what survives the PASS gate failing.

**Invariant 3 — CONSENSUS_CATALOG precedes CND_FRAME.** If all lenses align, the catalog is not exhibiting framing-divergence to begin with. CONSENSUS_CATALOG is diagnostically distinct (catalog-completeness work) from CND_FRAME (substrate-work). An under-catalogued problem where the few lenses you have all agree is CONSENSUS_CATALOG, not CND_FRAME, even if you suspect more lenses would disagree — absence of catalogued disagreement, not dismissal of substrate-level disagreement.

These three invariants jointly close Probe-2 objection #5.

## 2.E.5 Worked examples through the 8-corpus + forward-paths

Running the tree on each catalog verifies the verdicts match team-assigned values:

| Catalog | Step fires | Verdict | Notes |
|---|---|---|---|
| lehmer | STEP 2 | PASS | Lens 6 vs Lens 9 on f_∞: {≥1.17} vs {→1} — magnitude-separation + logical-incompatibility |
| collatz | STEP 2 | PASS | Lens 16 vs Lens 19 on α: 1/2 vs 0 — magnitude-separation; PROPOSED-status caveat noted |
| zaremba | STEP 2 | PASS with provenance_qualifier=PASS_BOUNDED_RESOLVED_REPLICATED | Bounded q ≤ 1000 resolved (sessionB+sessionC Track D); asymptote LIVE |
| brauer_siegel | STEP 4 | FAIL cnd_frame (obstruction_class) | All lenses agree α=1; disagree on obstruction identity |
| knot_concordance | STEP 4 | FAIL cnd_frame (truth_axis_substrate_inaccessible) | Torsion > 2 existence disagreement; substrate-inaccessible |
| ulam_spiral | STEP 4 | FAIL cnd_frame (framing_of_phenomenon) | Converge on z-score per diagonal; diverge on what-the-phenomenon-is |
| hilbert_polya | STEP 4 | FAIL cnd_frame (operator_identity) | Spectrum = γ_n + family-RMT agreed; H-identity disagreed |
| p_vs_np | STEP 3 | FAIL consensus_catalog (no_counterexample_found + barrier_results) | 12 lenses align on P ≠ NP |
| irrationality_paradox | STEP 4 | FAIL cnd_frame (framing_of_phenomenon, possible partition_axis_disagreement narrowing) | 6 lenses pick 6 different Ys; not active Y-denial |
| knot_nf_lens_mismatch | STEP 1 | FAIL y_identity_dispute (lens_swap_remediable) | Lens 2 actively denies Lens 1 Y; 26 Chinburg verifications close asymmetrically |

All 10 verdicts match the team-assigned values without ambiguity or backtracking. The priority ordering does the work.

## 2.E.6 Edge cases

**EC1 — All lenses silent on Y-candidates.** A catalog where every lens has silence_state ∈ {SILENT, DISPUTED} on every proposed Y falls through to STEP 6 INCONCLUSIVE. Annotation: "needs ≥ 2 lenses with COMMITTED silence_state per 2.C.4."

**EC2 — Single lens catalog.** Catalogs with only one lens fail eligibility (2.B.1 requires ≥ 4). Emitted as NOT_YET_ELIGIBLE at STEP 0.

**EC3 — Lens swap mid-catalog.** If a catalog is teeth-tested as Y_IDENTITY_DISPUTE and then the disputed Y is resolved (e.g. knot_nf_lens_mismatch's A-polynomial eventually runs through SnapPy with full corpus confirmation), the catalog should be *re-teeth-tested*, not retroactively relabeled. The v1 record stands as historical; v2 verdict reflects post-resolution state.

**EC4 — Meta-axis disagreement that IS Y-identity.** Distinguish: irrationality_paradox lenses disagree on what-to-measure (partition_axis_disagreement) but without active denial — each lens's Y is accepted as a *separate* measurement, not rejected as *the wrong* measurement. knot_nf_lens_mismatch lenses disagree on what-to-measure AND Lens 2 actively denies Lens 1's Y-legitimacy ("wrong polynomial"). The distinction is in the active-denial predicate of STEP 1, which is why STEP 1 fires for knot_nf_lens_mismatch but STEP 4 fires for irrationality_paradox.

**EC5 — All lenses COMMITTED but to different Y's, no active denial, no shared incompatibility.** This is the irrationality_paradox shape. STEP 1 does NOT fire (no DISPUTED, no active denial). STEP 2 does NOT fire (no shared Y). STEP 3 does NOT fire (lenses disagree). STEP 4 fires — CND_FRAME with sub_flavor either framing_of_phenomenon or partition_axis_disagreement per 2.A enum extension.

## 2.E.7 Composition with v2 sections

- **2.A (enum):** supplies the 4-value failure_sub_class the tree emits at STEPs 1/3/4
- **2.B (core-unit defs):** supplies catalog/lens/problem/Y/resolution predicates the tree queries
- **2.C (admission criteria):** supplies the incompatibility test (2.C.1), observability standard (2.C.2), consensus reference (2.C.3), silence vocabulary (2.C.4) — all used inside tree nodes
- **2.D (pre-registration protocol):** pre-reg ensures lens commitments are fixed BEFORE the tree runs, closing the cataloguer-steering loophole the tree alone cannot close

## 2.E.8 Open question — RESOLVED

**Original question:** Should STEP 1 (Y_IDENTITY) and STEP 3 (CONSENSUS) have a priority swap for non-substrate-decomposable catalogs?

**Resolved per auditor end-to-end review (1776908486097-0):** Y_IDENTITY_DISPUTE gate applies to BOTH branches. The fix was to lift STEP 1 above the substrate-decomposability branch-point (now at STEP 1.5), so Y-identity is checked before any branch is taken. Tree revised in 2.E.3 above; Invariant 1 in 2.E.4 updated to name both cataloguer-steering pathologies the fix closes.
