# ROBUST01 S2a RESULT: assisted reuse (R4, planted component) under aeth01.op_xor_fold

Freeze c989c09a1. Disposition from the frozen REACH01/R4/r4_reduce.py, under REACH01/R4/RULES.json, with S0's fold
transplant table:

**CUMULATIVE_ACQUISITION_ADVANTAGE (ASSISTED CONTROL), plus ROBUST_REUSE.**

- Runs, on spectrex5:gpu0:
  - plan_s2a_search.json, 32 units, 2026-10-17T22:35:40Z-23:47:44Z;
  - plan_s2a_reduce.json, 23:50:40Z-2026-10-18T00:26:59Z.
  - Every unit has rc 0 and is stamped aeth01.op_xor_fold with fold sha 50aeee33...
- evidence/S2A/ holds REDUCTION_S2A.json, both ledgers and S2A_DATA_SHA256.txt (32 unit JSONs, 9 npz). Data are in
  C:/Prometheus-data/aether_robust01/S2A/.
- ROBUST_REUSE is applied by its registered rule (RULES.json stage2) to r4_reduce's own summary fields: P
  success_seeds >= 6 AND P position_frac_median >= 0.9. Here 8 >= 6 and 1.0 >= 0.9.

## Arms, 8 seeds each (budget 20,480 evaluations; a median cost of 20481 means not reached)

| arm | fold: success seeds | fold: median cost | fold: necessity | fold: position frac (median) | contest (REACH01 R4): success / cost / necessity / position |
|---|---|---|---|---|---|
| N (no component) | 0/8 | 20481 | - | - | 0/8 / 20481 / - / - |
| S (component in world, not offered) | 1/8 | 20481 | 0.0 (5 solutions) | 1.0 | 0/8 / 20481 / - / - |
| U (component offered, unmarked) | 0/8 | 20481 | - | - | 0/8 / 20481 / - / - |
| P (component promoted) | **8/8** | **2090.5** | **1.0** (40/40) | **1.0** | 8/8 / 6559.5 / 1.0 / **0.016** |

- r4_reduce's frozen thresholds:
  - P >= 6/8, with N and S <= 2/8: P 8/8, N 0/8, S 1/8;
  - necessity >= 0.8: 1.0;
  - P cost <= 0.5 x U: 2090.5 against 20481, a ratio of 0.10.
- TRANSPLANT is not supported: the fold transplant table is 1.0 at (0, 0) and 0.0 at the 5 other offsets, as in S0.

## Predictions (P-S2a)

| registered prediction | outcome |
|---|---|
| CUMULATIVE_ACQUISITION_ADVANTAGE again (P >= 6/8, N and S <= 2/8, necessity >= 0.8) | held: 8/8, 0/8 and 1/8, 1.0 |
| ROBUST_REUSE: median P position fraction >= 0.9, against 0.016 under the contest law | held: 1.0 |

## Reading
- Under the contest law, reusing the planted component already made acquisition cheap and necessary. The solutions
  built that way, however, combined at only 1 of 64 tile positions (0.016).
- Under the fold law, every P solution in all 8 seeds combines at all 64 positions (40/40 checked), and every one
  needs its component copies.
- Acquisition is also about 3x cheaper: a median of 2,090 evaluations, against 6,560.
- That matches S0 and S1. For designed, discovered and search-built reuse structure alike, contest arbitration was the
  source of position fragility. The preregistered alternative ("contest semantics was the bottleneck for designed and
  discovered composition, but not for search-built reuse") does not arise.
- Two observations not anticipated in the preregistration:
  - Arm S found a solution in 1 seed (s4, first at evaluation 12,378) that uses no component copies (necessary =
    False). It counts within the frozen S <= 2/8 limit. Under the contest law, S found none.
  - P's 40 solutions use 2 to 5 copies of the component: 26 with 2, 8 with 3, 3 with 4 and 3 with 5. These are
    arrangements of copies, not single transplants. The transplant table shows the component alone does not work
    when shifted.

## Deviations
- None. The search ran under the GPU-sharing supervisor; it launched at 22:35:40Z, once the card was clean, and did
  not yield during the run.

## Next
S2b: genuine reuse with the component chosen by r01_stage2b.py from S1. The frozen rule selected G1_C_s13
88052bc1d0297f48: 6 cells, sufficient alone, known answer on R4c's task with in2 (0x55, 0xAA). Its own transplant
table is 1.0 at (0, 0) and 0 elsewhere.
