# REACH01 LADDER01 RESULT: where does spontaneous combination become discoverable?

Freeze f372e412c (PREREGISTRATION_LADDER01.md). Production 15:10Z-17:4xZ on 2026-10-10: search 48/48 and certify
48/48 rc=0. Evidence: R3/evidence_ladder/; certificates in CAUSAL_CERTIFICATES/.
Physics, search and certifier: as R3 attempt 2 (aeth01.op_xor, execution-only regime, descriptor v2). Inputs 2 rows
apart (A (8,1), B (10,1)); output moved: G1 (9,6), G2 (9,10), G3 (9,18). Arms C (certificate-guided) and A
(ordinary), 8 seeds, 20,480 evaluations each.

## Frozen outcomes

| geometry | arm | seeds with COMBINE | seeds with certified COMPOSE | AUTONOMOUS | outcome |
|---|---|---|---|---|---|
| G1 (output 5 columns away) | C | **3/8** (s2, s6, s7) | 1/8 (s2) | 1 mechanism (s7, a COMBINE) | **COMBINE_ONLY** (COMPOSE in 1 seed; 2 needed) |
| G1 | A | 0/8 | 0 | -- | NONE |
| G2 (9 columns) | C / A | 0/8 / 0/8 | 0 | -- | NONE |
| G3 (17 columns) | C / A | 0/8 / 0/8 | 0 | -- | NONE |

Joint a-and-b-dependent cells now appear in every arm-C run. Best joint reach: 3-5 columns for A, 4-5+ for C.
Arm-C progress is 21-35 vs arm A's 15-21, at every geometry.

## The discoveries (first spontaneous input combinations in the REACH01 campaign)
- **s2 -- archive-assisted COMPOSITION, not autonomous.**
  - 10 certified variants (one lineage, found at evaluations 19,461-19,808).
  - Certificate: 1 cell necessary only for a, 2 only for b, 8 shared.
  - COMBINE at 33% of tile positions, under neither alternative physics seed (contest-arbitration fragile).
- **s6 -- COMBINE, not COMPOSE.** No b-exclusive necessary cell; 4% of positions.
- **s7 -- AUTONOMOUS COMBINE (not COMPOSE).**
  - COMBINE at 256/256 positions and under both alternative physics seeds.
  - Its 7 certified-necessary cells (patch rows 6-8, columns 0-3, sitting between the two input deposits) alone
    reproduce the full 123-writer patch's function at 100% of positions: a minimal, sufficient, extractable
    mechanism.
  - Its function is a low-information combination: f(a, b) = [46 unless a = 0x55] XOR [1 iff b = 0xAA].
  - Not COMPOSE: every a-necessary cell is also b-necessary (one shared pathway, not two substructures).

## Reading
- With inputs 2 rows apart, the first combination event becomes reachable. Certificate-guided search finds input
  combinations at short output distance (5 columns) in 3/8 seeds, where ordinary search finds none.
- At 9 or 17 columns, no search finds any, even though joint-dependent cells exist inside the patch.
- So the R3 desert has two parts:
  1. bringing two input streams together, which is solved here by geometry;
  2. carrying a joint dependence to a distant output, which is unsolved beyond 5 columns at this budget.
- Certificate guidance matters at the reachable boundary: C 3/8 vs A 0/8 at G1, always higher progress.
- Of 3 discoveries, the one that is robust (s7) is the simplest: no separate substructures, a single shared pathway.
  The one that composes (s2) is contest-fragile. This mirrors the planted combiner: in this physics, composition by
  merging two streams is arbitration-sensitive, and robustness came with non-composition.

## Mapped onto the order's R3 decision terms (descriptive)
- ARCHIVE-ASSISTED COMPOSITION: one seed (s2). Below the 3/8 bar.
- AUTONOMOUS COMPETENCE: one discovered mechanism (s7) is autonomous, but it is a COMBINE, not a composition.
- AUTONOMOUS_COMPOSITION: not achieved.

## Cognitive accounting
- Substrate: XOR combination and transport; the 7-cell s7 motif executes autonomously.
- Search infrastructure: the certificate-guided archive found all 3 discoveries; ordinary search found none.
- Experimenter: geometry (bringing inputs within 2 rows), search space.
- Certifier: ablation, autonomy, minimality.
