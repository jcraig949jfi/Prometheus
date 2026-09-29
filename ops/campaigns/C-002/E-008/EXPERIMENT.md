# E-008 -- Horizon falsifier for the Block D positives (d_horizon)

Campaign: C-002. Thread: TH-007 (thr-10216c7f001e), parked; this closes an open item, it does not reopen the search.
Question: are the locality conclusions for the two Block D positives, rcv_add and rcv_str, horizon-robust to 10,000 ticks?
Decision rule (declared before the Block C runs, committed 39b7f7e85): Aether/AETH-03/PHYSICS_DESIGN_03_2026-09-27.md s1, applied
unchanged to the two new OFF arms. Horizon-DEPENDENT if (i) share with max radius >= 5 at +10,000 is >= 2x the share at +500 AND
>= 0.10; or (ii) any region breaches (Chebyshev distance >= 28); or (iii) >= 10% of origins set a new maximum generation after
tick 2,000. Otherwise horizon-robust.
Units (frozen): Aether/runpod/aether_units/units.json set d_horizon, module v5 (9862cfa9e): T-087 rcv_add s0, T-088 rcv_add s1,
T-089 rcv_str s0, T-090 rcv_str s1; OFF; 256^2, 16 origins each, 10,000 ticks. Code pinned c49f2ebad4c888e49fde639e49ecb0d8be3eea83.
History: first executed 2026-09-27 on a RunPod pod; results lost (controller killed under host memory pressure + a resume defect,
fixed 3bd6f82b4). Re-run per operator ruling 2026-09-28 (MWO-0001): NO RunPod; a Fabric Task on existing CPU workers, same
unit IDs, same pinned code.
