# REACH01 R4 / ACCUM01 preregistration -- ASSISTED CONTROL (the component is a PLANTED mechanism)

The order requires that if only a planted mechanism exists, R4 runs as an explicitly labelled assisted-control
experiment. R3 attempt 2 has not discovered a COMBINE mechanism in the units completed so far; its search is still
running.
- R4 therefore reuses the R3 planted COMBINE (component_planted.json): 38 designed cells, of which 23 are certified
  necessary (Na U Nb).
- No claim of evolved cumulative development is possible from this experiment.
- If R3 later certifies a discovered, autonomous composition, a separate R4b (new preregistration) reuses that.

## New capability (task 2)
COMBINE3: strict dependence of the output on three inputs (A (6,1), B (13,1), C (9,1); values {0x33, 0xCC}). XOR
physics, execution-only regime, R3 tile. Known answers (CPU):
- the planted 2-input component, with no C path, depends strictly on a and b only;
- an empty patch depends on nothing.

## Arms (equal budget: 20 x 1024 evaluations per seed; certificate-guided parent selection for all)
- N: no component.
- S: shuffled component (states permuted among its cells), insertable.
- U: correct component as an unpromoted restore seed, cell mutation only.
- P: correct component PROMOTED to an insertable unit. With prob 0.3 a candidate is written at a random offset in
  [-3, 3]^2 (duplicate / relocate).
8 seeds each.

## Transplant test (task 1, already measured BEFORE this freeze, disclosed)
Component inserted into an inert patch, COMBINE fraction over 256 tile positions:
- offset (0,0): 0.26;
- offsets (1,0), (0,1), (-1,-1), (2,2), (-3,3): 0.00 each.
The component works only where it was built (geometry-bound interface).

## Decision (RULES.json)
- TRANSPLANT_SUPPORTED: COMBINE fraction >= 0.2 at >= 2 non-zero offsets. Already known: FAILS.
- COMPOSITION_REUSE_SUPPORTED: P or U finds COMBINE3 in >= 6/8 seeds, N and S in <= 2/8 each, and the component is
  causally necessary in >= 0.8 of the found solutions checked. Necessity is tested by inerting the cells that
  match the component at its best-matching offset.
- CUMULATIVE_ACQUISITION_ADVANTAGE: the above for P, AND P's median first-success evaluation <= 0.5 x U's
  (a failed seed counts as budget + 1).
- REUSE_NOT_SUPPORTED: otherwise.
All dispositions carry the label ASSISTED CONTROL.

## Runtime
~10 s per 1024-candidate batch with R3 sharing the GPU, so ~1 h for 32 units at --jobs 2.

Hashes:
  f611cc7ef4bbc99214aa57cf0cc841b7227fef40d8fc1e6dd8110399fdde7fd2 RULES.json
  d8f35315ec5194eb48a148111bd3146c2d2b93ec8eb79d874cf12488a97561fa plan_search.json
  b574007c57d1f9829f4f514759fae058aafdcac87d711be042fcbc13f14ac717 r4_accum.py
  ca50a82890675001f7577d69a516d8fa153139bcb13f6a80a04099e06d2a7627 component_planted.json
  72cd5c3f2e7e74af71546403aeb8da02d6c5783167a91ffcaf9bf5783154a3d6 ../R3/r3_frontier.py
