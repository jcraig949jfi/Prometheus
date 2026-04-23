---
name: Methodology Cluster Graph — CND_FRAME / FIT / CONSENSUS_CATALOG / Y_IDENTITY_DISPUTE / ANCHOR_*
purpose: Navigational DAG for 6 inter-referenced symbols + candidates that accumulated 2026-04-22/23 around open-problem classification + post-promotion anchor tracking. Resolves joint Axis-3 (sessionC) + Axis-4 (sessionA) consolidation candidate #2/#3.
format: ASCII dependency graph + per-node one-liner + "which question does this answer?" table. Navigational only — doctrine lives in the individual symbol MDs.
discipline: If you edit this file to add new doctrine, the doctrine belongs in a canonical symbol MD — this file should only reference.
owners: joint — sessionA (Axis 4: exploration techniques) + sessionC (Axis 3: symbolic storage). Per-symbol canonical MDs remain the source-of-truth.
---

# Methodology Cluster Graph

## Why this file exists

During 2026-04-22 and 2026-04-23 six inter-referenced symbols and candidates landed, each cross-referencing the others in its own MD. Cold-start Harmonia encountering any one of them had to traverse references mentally to rebuild the cluster. This file renders the DAG in one view + names what each node answers.

The cluster is about two related problems:
1. **Classifying open-problem lens catalogs** (which catalogs are driving measurement vs substrate-work vs catalog-work)
2. **Tracking anchor-count evolution post-promotion** (when symbols are immutable but their anchor state accumulates)

## Dependency DAG

```
                           SHADOWS_ON_WALL@v1
                         (pre-axial foundation)
                                 │
                                 ▼
                    PROBLEM_LENS_CATALOG@v1
                   (per-open-problem lens inventory)
                                 │
                                 │ produces per-catalog data
                                 ▼
                 FRAME_INCOMPATIBILITY_TEST@v2
             (the "teeth test" classifier; v2 bundles
              enum extension + def-tightening + pre-reg)
                       │            │            │
               FAIL────┤  PASS      │    RETROSPECTIVE_PASS
                       │            │            │
                       ▼            ▼            ▼
          ┌────────────┴─────┬─────┴──┐
          │                  │        │
       cnd_frame      consensus_    y_identity_
          │           catalog       dispute
          │              │           (v2 new)
          ▼              ▼              ▼
    CND_FRAME@v1   CONSENSUS_    (future: Y_IDENTITY_
   sub-flavors:    CATALOG@v0    CATALOG sister pattern
   • obstruction_  (Tier 2        once 3-anchor threshold
     class           candidate,   hits — 1 anchor currently:
   • truth_axis      1 anchor:    knot_nf_lens_mismatch at
   • framing_of_     p_vs_np      coordinate_invariant)
     phenomenon     + drum_shape
   • operator_       proposed 2nd
     identity       anchor via
                    external_
                    theorem_
                    proven basis)

        supports
  ┌───────────────┐
  ▼               ▼
ANCHOR_AUTHOR_  ANCHOR_PROGRESS_
DIVERSITY       LEDGER
(Tier 3         (Tier 3 candidate,
 candidate)     surviving_candidate)
 N distinct     Mutable sidecar at
 authors ×      symbols:<NAME>:
 N distinct     anchor_progress,
 problems       records post-promotion
 gate for       tier/cross-resolver
 pattern        evolution without
 promotion      violating Rule 3
                immutability
```

## Per-node answer-table

| Node | Type | Version | Which question does this answer? | Source MD |
|---|---|---|---|---|
| SHADOWS_ON_WALL | pattern | @v1 promoted | "How should I interpret a finding's epistemic weight across multiple lenses?" | `symbols/SHADOWS_ON_WALL.md` |
| PROBLEM_LENS_CATALOG | pattern | @v1 promoted | "For this open problem, which disciplinary lenses have been applied / could be applied?" | `symbols/PROBLEM_LENS_CATALOG.md` |
| FRAME_INCOMPATIBILITY_TEST | pattern | @v2 promoted 2026-04-23 | "Does this catalog's lens-disagreement cash out at a substrate-measurable Y? If yes → PASS drives measurement; if no → which flavor of FAIL?" | `symbols/FRAME_INCOMPATIBILITY_TEST.md` |
| cnd_frame sub-class | enum value in FIT@v2 2.A | v1 via CND_FRAME@v1 symbol | "This catalog FAILs because lenses share Y but disagree on a meta-axis (framing/obstruction/truth/identity) — substrate-work-needed." | `symbols/CND_FRAME.md` |
| consensus_catalog sub-class | enum value in FIT@v2 2.A | @v0 candidate | "This catalog FAILs because all lenses align; no adversarial frame catalogued — catalog-completeness-work-needed." | `symbols/CONSENSUS_CATALOG.md` (draft) |
| y_identity_dispute sub-class | enum value in FIT@v2 2.A (new) | v2 enum | "This catalog FAILs because at least one lens actively denies another's Y-legitimacy — catalog-level Y-commitment work needed before teeth-test is even applicable." | `symbols/FRAME_INCOMPATIBILITY_TEST.md` §2.A |
| ANCHOR_AUTHOR_DIVERSITY | pattern | Tier 3 candidate | "Does this pattern's anchor set have N distinct authors × N distinct problems, or is it single-author coincidence?" | `symbols/CANDIDATES.md` §ANCHOR_AUTHOR_DIVERSITY |
| ANCHOR_PROGRESS_LEDGER | architecture / methodology | Tier 3 candidate (surviving_candidate tier) | "How do I track post-promotion anchor-tier evolution (new cross-resolvers, forward-path apps, tier upgrades) without violating Rule 3 immutability?" | `symbols/CANDIDATES.md` §ANCHOR_PROGRESS_LEDGER + `agora/symbols/anchor_progress.py` |

## Anchor counts (current, 2026-04-23)

| Pattern | Anchors | Tiers |
|---|---|---|
| FRAME_INCOMPATIBILITY_TEST@v2 (catalog verdicts) | 11 | 2 coordinate_invariant (zaremba, knot_nf_lens_mismatch) + 8 surviving_candidate + 1 shadow_contested (irrationality_paradox) |
| CND_FRAME@v1 (FAIL sub-shape A) | 4 | 4 surviving_candidate (brauer_siegel, knot_concordance, ulam_spiral, hilbert_polya); irrationality_paradox contested |
| CONSENSUS_CATALOG@v0 (FAIL sub-shape B) | 1 concrete (p_vs_np) + 1 proposed (drum_shape) | surviving_candidate |
| Y_IDENTITY_DISPUTE (FAIL sub-shape C, v2 enum) | 1 (knot_nf_lens_mismatch) | coordinate_invariant |
| ANCHOR_AUTHOR_DIVERSITY | 2 (CND_FRAME meta-pattern candidacy, F043 retrospective) | single-author both; surviving_candidate pending forward-path |
| ANCHOR_PROGRESS_LEDGER | 2 (FIT v1→v2 accumulation, CND_FRAME@v1 evolution) | surviving_candidate with 3-author attestation + 1 forward-path deployment (FIT@v2 sidecar LIVE) |

## Cross-referencing verdicts — which catalog triggers which FAIL sub-class

| Catalog | Verdict | Sub-flavor | Notes |
|---|---|---|---|
| lehmer / collatz / zaremba | PASS | — | Substrate-divergent; zaremba at PASS_BOUNDED_RESOLVED_REPLICATED (Track D) |
| brauer_siegel | cnd_frame | obstruction_class | Scaling α=1 agreed; disagree on obstruction identity |
| knot_concordance | cnd_frame | truth_axis_substrate_inaccessible | Higher-torsion existence disagreement; 60+ years open |
| ulam_spiral | cnd_frame | framing_of_phenomenon | z-score per diagonal agreed; disagree on what the phenomenon IS |
| hilbert_polya | cnd_frame | operator_identity | Spectrum agreed; disagree on H's operator class |
| p_vs_np | consensus_catalog | no_counterexample_found + barrier_results | All 12 lenses align with P ≠ NP consensus; no adversarial frame |
| drum_shape | consensus_catalog (proposed 2nd anchor) | external_theorem_proven | GWW 1992 closed external Kac question; all 6 lenses inherit |
| irrationality_paradox | cnd_frame (contested) | framing_of_phenomenon (partition_axis_disagreement refinement candidate) | 6 lenses pick different Ys; no active Y-denial per sessionC nuance |
| knot_nf_lens_mismatch | y_identity_dispute | lens_swap_remediable | Lens 2 actively denies Lens 1 Y via 26 Chinburg verifications |

## Remediation pathways (diagnostic consequence of each FAIL verdict)

Per FRAME_INCOMPATIBILITY_TEST@v2 §2.A composition table:

- **PASS** → substrate-measurement work (run the incompatible-Y measurement)
- **cnd_frame** → substrate-work-needed (gen_09 cross-disciplinary transplants / gen_11 axis-space invention)
- **consensus_catalog** → catalog-completeness-work (MPA committed-stance attack with forced-adversarial-stance threads)
- **y_identity_dispute** → catalog-level Y-commitment work (lens-swap discipline per lens_swap_remediable; or substrate-adjudication per lens_contest_open)

## Composes with

- **SIGNATURE@v2** — carries `pre_reg_spec` reference for FRAME_INCOMPATIBILITY_TEST@v2 §2.D pre-registration protocol
- **PATTERN_30@v1** — algebraic-identity coupling is the extreme Y_IDENTITY_DISPUTE case (Y definitionally forced via algebra)
- **MULTI_PERSPECTIVE_ATTACK@v1** — the methodology that generates catalog frames in the first place; FIT is the gate that distinguishes substrate-rich MPA output (PASS) from labeling-only (FAIL sub-classes)
- **SHADOWS_ON_WALL@v1** — pre-axial frame: PASS catalogs are substrate-divergent in the SHADOWS sense (territory has multiple incompatible coordinate readings); FAIL catalogs are coordinate-divergent at the framing level only

## Not a replacement for

- Per-symbol canonical MDs — definitions and schemas live there; this file only references
- CANDIDATES.md / INDEX.md — registry indices are authoritative for promotion status
- Catalog frontmatter fields (`cnd_frame_status`, `teeth_test_verdict`, etc.) — per-catalog state is authoritative per catalog

## Version history

- **v1.0** 2026-04-23 (sessionA Axis 4 + sessionC Axis 3 joint) — initial rendering. Responds to axis-4 sprawl observation "methodology cluster has no graph" and axis-3 sprawl observation (same gap from storage perspective). 6 nodes + 11 catalog verdicts + remediation pathways. Will need refresh when CONSENSUS_CATALOG graduates to @v1 (third anchor) or when a second Y_IDENTITY_DISPUTE anchor lands (currently 1).
