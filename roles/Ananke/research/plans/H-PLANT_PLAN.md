# H-PLANT PLAN: plant viability for the undecided NULLs (frozen by commit before any run)

Authority: operator inference-harvest directive 2026-09-30 (bounded tests; no campaign; NO evolutionary
search in this item). Worker: H-PLANT. Cap: 2 CPU core-hours, CUDA_VISIBLE_DEVICES=-1, device="cpu", no GPU.
Source: harvest/INFERENCE_HARVEST_HANDOFF.md s5 items 1-2; H-SCI 1.2. The worker must NOT edit this file;
deviations go in harvest/H-PLANT/PLAN_ADDENDUM.md before the affected run.

## Question
C1's XOR, FLIP and multi-hop RELAY NULLs cannot currently be attributed to physics or to search: no plant
exists for them at any physics. relay_flood "cannot solve XOR or FLIP by design" (PREREG s11). Is there a
hand-written program, within the ENGINE's declared instruction set and the C1 dial ranges, that solves
each task with held accuracy lo99 > .60?

## Plants (hand-written with prometheus/ananke/plants.py helpers; one per task)
- P-XOR: a one-hop XOR (both sensors are direct neighbours of the actuator). The physics is chosen within
  C1's declared dial ranges so that both cue copies land in the SAME readout wake window: jitter 0, equal
  latency, sync period chosen for co-arrival. The readout computes a sign function of the two arrivals
  (e.g. via SUB / MAX / GT on the inbox).
- P-MULTIHOP: RELAY at d = 2 * radius (forced 2 hops) with one relay site forwarding payload 1. Physics:
  the d9cc point (ring 144, r3, fanout 8, sync period 2), and a lossless variant.
- P-FLIP: FLIP with its teacher/block structure; any program that tracks the teacher-set sign.
The plants may use only instructions and dials the engine declares (physics.validate must pass). No
physics dial outside C1's frozen A1 ranges (roles/Ananke/pte/FREEZE_PTE_C1.json config).

## Frozen readings (per task)
- PHYSICS ALLOWS: plant held accuracy lo99 > .60 on 256 fresh worlds (a new namespace), both at the chosen
  co-arrival physics AND at >= 1 physics point that C1 actually sampled for that family.
- PHYSICS ALLOWS ONLY OFF-CENSUS: lo99 > .60 only at physics C1 never sampled. (C1's NULL is then partly
  a sampling statement.)
- NOT SHOWN: no plant reaches lo99 > .60 within 1 core-hour of design effort per task. This is NOT
  evidence that physics forbids the task; it says the plant search was bounded.
- Must-fail per plant: the same plant with its key operand zeroed (e.g. XOR readout ignoring one sensor)
  must fall to lo99 <= .55.

## Known-answer gate
relay_flood and echo_hold at their published physics reproduce their recorded plant accuracies within
.02 before any new plant is scored. If not, stop.

## Report
harvest/H-PLANT/REPORT.md (delimited in the final message): the plants' programs (decompiled), physics
dials, accuracies with CIs, must-fail results, the per-task frozen reading, and what each reading implies
for H6.
