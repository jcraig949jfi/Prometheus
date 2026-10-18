# ROBUST01 S2b RESULT: genuine reuse of the S1-discovered composition, under aeth01.op_xor_fold

Freeze c989c09a1. Disposition from the frozen REACH01/R4/r4_reduce.py, under REACH01/R4/RULES.json, on R4c's task,
with the component's own fold transplant table:

**REUSE_NOT_SUPPORTED.** (r4_reduce prints the fixed label "ASSISTED CONTROL (planted component)" for every run; it
is not a description of this component.)

- Component: chosen by the frozen r01_stage2b.py rule from REDUCTION_S1.json; evidence/S2B/component_s2b.json.
  - Source: G1_C_s13, hash 88052bc1d0297f48, the only arm-C COMPOSE candidate with zero energy-field contests.
  - Certificate: COMPOSE and AUTONOMOUS, position fraction 1.0, a_only / b_only / shared = 1 / 1 / 4, 2 distinct
    outputs, held-out rung 2.
  - Cells: Na U Nb = 6 cells.
  - Checks: SUFFICIENT alone; KNOWN ANSWER on R4c's task (input C at (12, 1)) with in2 = (0x55, 0xAA), the first
    alphabet tried.
  - Transplant: 1.0 at (0, 0) and 0.0 at all 5 other offsets, the same geometric interface as the planted
    component.
- Runs, on spectrex5:gpu0, 2026-10-18:
  - plan_s2b_search.json, 32 units (N S U P x seeds 0-7, 20 x 1024), 00:29:58Z-01:50:10Z;
  - plan_s2b_reduce.json, 01:53:05Z-01:58:47Z.
  - All units have rc 0 and are stamped aeth01.op_xor_fold. The gpu0 lease was released at 01:59:41Z.
- evidence/S2B/ holds REDUCTION_S2B.json, the component, its transplant table, both plans, both ledgers and
  S2B_DATA_SHA256.txt (32 unit JSONs, 2 npz).

## Arms, 8 seeds each (budget 20,480; a median cost of 20481 means not reached)

| arm | fold (this run): success / necessity / position frac | contest, R4c (REACH01, discovered s7 component): success / cost / necessity / position |
|---|---|---|
| N (no component) | 0/8 / - / - | 0/8 / 20481 / - / - |
| S (in world, not offered) | 1/8 (s0) / 0.0, 5 solutions with 0 copies / 1.0 | 0/8 |
| U (offered, unmarked) | 0/8 | 0/8 |
| P (promoted) | **1/8** (s3, first at evaluation 6,134) / 1.0 (5/5) / 1.0 | **7/8** / 11691 / **0.66** / 0.109 |

- reuse(P) needs P >= 6/8 with necessity >= 0.8, and P got 1/8. reuse(U) needs U >= 6/8, and U got 0/8. The
  transplant clause needs 2 non-zero offsets >= 0.2, and none qualified. That leaves REUSE_NOT_SUPPORTED.
- Median max rung: P 2.0, U 2.0, S 2.0, N 0.5.
  - Offered or not, the search mostly reaches the component's own a-b combination (rung 2), but rarely adds input C
    (rung 3).

## Prediction (P-S2b)

| registered prediction | outcome |
|---|---|
| if testable, COMPOSITION_REUSE_SUPPORTED or better (necessity >= 0.8, against R4c's 0.66) | **failed**: REUSE_NOT_SUPPORTED |

- The necessity clause on its own would have passed: 5/5 of P's solutions need the copies.
- The failure is acquisition: 1/8 seeds against the frozen 6/8.

## Reading
- The fold law repairs the quality of reuse, not its rate.
  - Where P does build a 3-input solution, it really uses the component (necessity 1.0) and the solution is
    position-robust (1.0). Under the contest law, R4c's solutions were neither (0.66 and 0.109).
  - But promoting this discovered composition made 3-input solutions rare (1/8).
- The comparison with R4c is not like-for-like, so the contrast says nothing about the law alone.
  - R4c offered a different component: the contest-era s7 value detector, which has a single pathway.
  - Here the component is s13's composition, 0x64 * g(a ^ b), which has 2 output values.
- Against S2a, which used the same task family, fold law and arm structure, the difference is the component.
  - Planted a ^ b (7 distinct outputs): P 8/8 at a median cost of 2,090.
  - Discovered s13 (2 distinct outputs): P 1/8.
  - One hypothesis, not tested here: a component that emits only 2 values is a poor substrate for adding a third
    input. Its output has too little information for c to modulate.
- Arm S again found a copy-free 3-input solution in 1 seed, as in S2a. Copy-free solutions to the 3-input task now
  turn up at about 1/8 under fold, against 0/8 under the contest law (S2a and S2b each 1/8; R4 and R4c each 0/8).

## Deviations
- None. The search and reduction ran under the GPU-sharing supervisor, which did not yield.
