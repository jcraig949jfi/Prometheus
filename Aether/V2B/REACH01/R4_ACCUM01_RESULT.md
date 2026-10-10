# REACH01 R4 / ACCUM01 RESULT -- ASSISTED CONTROL (the reused component is a PLANTED mechanism)

Freeze 082f2f27b. Production 13:20Z-14:3xZ on 2026-10-10: 32/32 units rc=0. Reduction:
C:/Prometheus-data/aether_reach01/R4/REDUCTION.json (copied to R4/evidence/). Reducer r4_reduce.py: committed after 12
units' first-success counts were visible but before any necessity value was computed. Its necessity definition
refines the preregistered wording (all >= 80%-matching component copies inerted, then each copy alone, evaluated at a
tile position where the solution works).

## Frozen disposition: CUMULATIVE_ACQUISITION_ADVANTAGE (ASSISTED CONTROL)

| arm | seeds acquiring COMBINE3 (new 3-input capability) | median first-success evaluation (budget 20,480) |
|---|---|---|
| N no component | 0/8 | budget+1 |
| S shuffled component (insertable) | 0/8 | budget+1 |
| U correct component, not promoted (restore seed only) | 0/8 | budget+1 |
| **P correct component, promoted (insert / duplicate / relocate)** | **8/8** | **6,560** |

Component necessity in P solutions:
- 22 of the 36 checked solutions had a working position; inerting all component copies destroyed COMBINE3 in
  22/22 (necessity 1.0).
- Copy structure: 2 copies in 21 solutions, 3 in 5, 4 in 1, 1 in 2.
- Typical layout: one copy at or near (0, 0) carrying A and B, and one at about (+3, -1) whose relay row now lies
  on input C's row.
- Inerting either copy alone drops the rung to 0-1. Both instances are causally necessary: a composition of two
  copies of one building block in two different roles.

## Attacks
1. **Fragility:** P solutions keep COMBINE3 at a median of 1.6% of 64 tile positions (max ~6%).
   - They are contest-arbitration-specific (cf. R3: merging continuous streams is coordinate- and seed-keyed).
   - None is AUTONOMOUS in the R3 sense.
2. **Geometry:** the insert offset range [-3, 3] (chosen before the task geometry was examined) contains the exact
   shift that maps the component's row-6 relay onto input C's row 9.
   - In this tile every input row (3..16) is reachable from a relay row within +-3, so the result cannot separate
     "duplication + relocation helps" from "the offset range happened to be generous".
   - A cleaner control would remove relocations that align with any input row. Not run (no new physics, but a new
     operator; left as the next experiment).
3. **Transplant (task 1) FAILED, measured before the freeze:** relocated by any non-zero offset, the component never
   computes task 1 (0/256 positions at 5 offsets).
   - The component is geometry-bound for its ORIGINAL role. Yet duplicated copies serve a NEW role (relaying a
     different input), and that is what P exploited.
4. **Encoded answer?** The insert operator copies cells verbatim and knows nothing of the task. But the component
   (relay rows + combiner) was designed by the experimenter for a closely related task, and the task-2 geometry
   was chosen by the experimenter. The advantage is real relative to N, S and U, and it is NOT evidence that the
   substrate discovered or developed anything.

## Cognitive accounting
- Substrate: XOR combination at the merge; relay transport; contest arbitration (which also makes every solution
  fragile).
- Developmental machinery (decisive): the PROMOTION operator, which can duplicate and relocate a certified unit.
  The same component, merely available (U), gave 0/8.
- Search infrastructure: certificate-guided parent selection, held fixed across arms; equal budgets.
- Experimenter: designed the component and both task geometries.
- Certifier: strict 3-input dependence, copy detection, inertion necessity, position robustness.

## Answer to the R4 question
Under assisted control: a certified mechanism, once PROMOTED into a unit that later search can duplicate and
relocate, makes a NEW capability (3-input combination) acquirable in 8/8 runs where every control fails at equal
budget. The reused component is causally necessary, in two copies with distinct roles.
- What made the difference is promotion, not availability (U = 0/8).
- The result is fragile (~2% of positions), rests on a planted component, and may depend on a generous relocation
  range. It is a demonstration that the harness can produce building-block reuse; it is not evidence of evolved
  cumulative development.
