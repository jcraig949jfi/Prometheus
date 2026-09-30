# W-Z LOG (E-ANANKE-W-Z, T-SWAP-AUDIT3, thr-5df816e9b844; plan roles/Ananke/research/plans/T-SWAP-AUDIT3_PLAN.md @ 6f25dc642, committed 2026-09-30 07:49:43 -0400 = 11:49:43Z)

Host SKULLPORT, 16 logical CPUs. All engine processes: CUDA_VISIBLE_DEVICES= (empty), PYTHONDONTWRITEBYTECODE=1, torch 1 thread.
Context: read W-O runner/audit/inventory/ka_plants, W-U apply733/swap_rel3, W-W swap_rel4 header, COMMON_RULES(+ARC3) before
running; the plan was frozen by the principal (not by me), so reading those before execution does not bias it.

A0 11:51Z pytest prometheus/ananke/tests/test_swap_rel.py: 11 passed, RC=0 (KA gate 1). fabric lease status: skullport:cpu8 free.
A1 11:52Z wrote PLAN_ADDENDUM Z1-Z6 (readings, before any run), zcommon.py, ka_z.py.
A2 11:52:44-11:54:46Z ka_z.py (1 thread, unleased): ALL_PASS. KA-B latch channel_all NO_EFFECT_REL; must-fail latch
   site_all -> FLIP_REL (as required); KA-A champion S FLIP_REL COMPLETE (z -1.079), site_all FLIP_REL COMPLETE,
   channel_all NO_EFFECT_REL. cpu 114 s. out/ka_z.json, out/ka_z.log.
A3 ~11:55Z Fabric lease skullport:cpu8 ACQUIRED lse-d4c8d5dcc30b (expires 12:55Z; renew planned).
   Launched run_z.py workers 0..7 (1 torch thread each). Win32 PIDs w0 27532, w1 27520, w2 23144, w3 25856 (rest below).
   test_zbook.py written and run: 3 passed RC=0 (out/pytest.txt).
   PIDs w4 23056, w5 17708, w6 27240, w7 15492.
A4 12:35Z lease lse-d4c8d5dcc30b RENEWED. Progress: 91 groups done, 4.91 core-h measured (W-O-predicted 5.55), 0 errors.
A5 12:49Z all 8 workers exited (w5 wrote STOP: next group 61d65a4f would exceed 7.3 core-h: done 24014 s + pending 1497 s + pred 977 s). 124/249 groups, 0 errors. Lease lse-d4c8d5dcc30b RELEASED 12:50Z (status shows no skullport lease). analyze_z.py -> row_table.csv, group_table.csv, summary.json. Compute: specimen 25070 cpu-s = 6.96 core-h + KA 114 s + tests ~0.01 h = 7.0 core-h.
