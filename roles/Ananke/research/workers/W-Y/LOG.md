# W-Y LOG (E-ANANKE-W-Y, T-INS-20, thr-8c7342a7d513)

A0 Read T-INS-20_PLAN.md (frozen fc8bfa171, 2026-09-30T11:09:26Z), COMMON_RULES(+ARC3), W-V and W-P REPORT
   RESULTS/DISAGREEMENTS (context per brief). Decompiled 4781b0a1 (reduced fields): instr 7
   `ADDI S0 := IN0_1 + (-3 + Kp[7])`; instr 8 `WIMM Kp[S0 mod 16] := EMIT(=MAX(S1,SENSE))`; instr 15
   `WIMM Kp[RVAL mod 16] := PAY1` with RVAL never written (=0) -> writes Kp[0]. So Kp[7] is written only when
   the readout's own S0 == 7 mod 16 at a wake, with value MAX(S1, SENSE).
A1 PLAN_ADDENDUM.md A1-A5 written before any run (operationalizations, plants, MF-SHUF prediction).
A2 11:14Z Plant dev check (scratchpad script, ns 0x67f, M 16, normal run only). Attempt 1 FAILED: World() defaults
   to device cuda:0 and I had not passed device='cpu' -> a ~2 s CUDA context/tensor on the GPU (no lease). This
   breaks the "no GPU" rule briefly; logged. Fixed: every W-Y World now gets device='cpu' and CUDA_VISIBLE_DEVICES=
   is exported in every launch/test. Attempt 2: PA and PB readouts == majority of the 5 votes in 100% of trials
   (acc .917 = P(majority correct) in this dev sample). PB S0 is PA's +1 (the constant Kp[7]=1), as designed.
A3 11:17:06Z Launched plants (launch_plants.sh, 2 procs x 1 thread, unleased): Win32_Process PIDs 22976 (PA),
   27196 (PB), ns 0x670 M 128 o2..o14 even, trials 1..11.
A4 11:18Z pytest (test_wy.py, dev ns): 4 passed, RC 0, 21 s (logs/pytest.log).
A5 11:17-11:23Z Plant runs DONE RC 0: PA 381 s, PB 381 s (1 thread each). wyana.py pa pb; ka.py -> out/ka.json.
   KA-B PASS, MF-X PASS, MF-SHUF all-REDUNDANT as predicted (no IS; literal criterion FAILS), KA-A (prereg A3)
   FAILS: see PLAN_ADDENDUM A6 (written before the champion run) for the strata and the post hoc reading.
A6 11:25:06Z Champion launched (DEVIATION D-1, PLAN_ADDENDUM A6 written first): PID 26896, 1 thread, 4781b0a1 M 128
   ns 0x670 o10,12,14 trials 1..11, 6 arms. DONE RC 0, wall 39 s.
A7 11:26Z wyana.py champ: KP7 = KPALL = 0.00 [0,0] at every stratum; Kp[7] at the readout is mirror-different in
   0.00 of pairs (value 0 in all 4224 world-trial-offsets). Informative strata o12q0, o12q1, o14q0, o14q1 (o14q1 FLA
   .502, just over .50): all KP7 NOT A CARRIER. o10 q0/q1 NOT-INFORMATIVE (FLA .25/.27, SITE_R .00). OVERALL KP7 NOT A
   CARRIER (validated call: KA-B, MF-X). The only mirror-different Kp slot at the readout is Kp[0] (84-95%).
A8 11:27Z POST HOC posthoc_kp.py (labelled): over the whole episode (T 228, M 128) the readout's Kp[1..15] are
   never nonzero; Kp[0] nonzero 53% of ticks, mirror-different 85%. Other sites do write Kp[7] (68%).
A9 11:28Z Win32_Process: 0 W-Y python processes. No lease (<= 2 threads throughout). No __pycache__ created.
   Compute: plants 2 x 381 s + champion 39 s + pytest 21 s + dev/analysis/ka/posthoc ~60 s = ~880 core-s = 0.25 core-h.
   Outputs ~320 KB.
