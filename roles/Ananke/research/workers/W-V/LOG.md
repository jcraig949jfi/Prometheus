# W-V LOG (E-ANANKE-W-V, T-INS-18, MWO-0004)

A0 06:56Z Read COMMON_RULES.md, COMMON_RULES_ARC3.md. Context read before PLAN (per brief, so stated as
   context contamination per ARC3 s2): W-T REPORT RESULTS/DISAGREEMENTS, W-P REPORT RESULTS/DISAGREEMENTS,
   W-T LOG tail, W-R PLAN head; code W-R fork.py/specs.py/followdiff.py, W-S probe.py/analyze.py, W-T wt.py,
   posthoc_maj.py; prometheus/ananke engine.py, envs.py, lens_swap.py, lens.py (head), topology.py, plants.py.
A1 06:58Z Decompiled 4781b0a1 (one rule, 16 lines, Kp offsets on imm): EMIT = MAX(S1, SENSE); S1 := 256*(S1 +
   SENSE > CNT0); PAY0 := S1; PAY1 := MAX(IN0_1, SENSE) (rectified; sensors can relay IN0_1); readout
   S0 := IN0_1 - 3 + Kp[7]; WIMM writes Kp. Physics: ring 144 r3, dest sample fanout 8, loss .1, cap 2
   saturate, lat 1+dist+jit{0,1}, sync period 2, LM 7. Sensors sit at ring distance 3,3,2,2,1 (indices 0..4)
   in every world checked.
A2 07:00Z Plants built (plants_wv.py) and dev-checked at M 16, ns 0x651 (not the analysis namespace):
   PMAJ readout == majority of the 5 votes in 100% of trials (acc .864 = P(majority correct)); PDICT ==
   sensor 4 (distance 1) in 100% (acc .648). Champion agrees with majority .795, with sensor 4 .773 (dev).
A3 ~06:59Z PLAN.md frozen (timestamps A3-A5 corrected from the wall clock; first draft had guessed times).
A4 07:00Z pytest attempt 1: 6 passed, 1 FAILED - test bug, not an instrument bug: my T2 "sensors send to the
   readout" assert looked only at the LAST tick (3*Pd), when nothing of the plant is in flight. Fixed to
   accumulate over ticks. Attempt 2: 7 passed RC 0. Added T5 (my per-offset fork FLA arm == W-S probe.fork
   flight_a, which forks at o_min with hooks): 8 passed RC 0 (logs/pytest.log).
A5 07:01Z Timing (1 thread, ns 0x65f dev): champion M 128, one (trial, offset) with base run = 42 s.
   Estimate: 77 forks champion + 55 per plant, ~1-1.5 core-hours total.
   Compute so far (tests + dev): ~0.05 core-hours.
A6 07:02Z Fabric lease lse-cfddaaf967a6 on skullport:cpu8 (--as Ananke) ACQUIRED (expires 08:02Z).
   Launch 07:02:37Z (launch.sh, 4 procs x 1 thread, ns 0x650 M 128). Win32_Process: 23392 champA
   (4781b0a1 o2,4,6,8), 24692 champB (o10,12,14), 23572 PMAJ (o2,4,6,8,12), 19856 PDICT (o2,4,6,8,12).
A7 07:06-07:11Z Runs finished RC 0: champB 203 s, champA 499 s, PDICT 560 s, PMAJ 564 s (1 thread each).
A8 07:11Z ana.py champA champB: o2-o8 E = 0.00 exactly (all 12 arms, raw S0 identical to normal in every world).
   Checked it was not a no-op swap (dev M 32, trial 5): 80-95% of pairs have mirror-different in-flight traffic
   to the readout from every sensor at every offset 0-16, and 0% from non-sensors. So the swap acts, and the
   readout ignores it. o10 E .24 (s0, s1 only), o12 q0/q1 and o14 q0 DISTRIBUTED-NONMAJ{0..4}, o14 q1 E .49
   (NOT-INFORMATIVE, just under .50). Verdict per PLAN s3: DISTRIBUTED-NONMAJ (3/3 informative strata).
A9 07:11Z POST HOC posthoc_state.py (labelled): the readout's S1 NEVER differs between mirror partners (0.000 at
   o0-16, M 128, trials 1-11); the readout's S differs only via S0, and its Kp differs 78-98%. Every sensor's S1
   differs in 100% of pairs.
A10 07:12Z ka.py: KA-MAJ, KA-DICT, MF1-MF4 all PASS (out/ka.json).
A11 07:12Z POST HOC posthoc_sign.py (labelled): single-sensor follows come almost entirely from the "-" world
   receiving the partner's + traffic (follow .43-.61 at o12/o14q0, even with 0 + votes), while the "+" world
   losing one + sensor rarely flips (.01-.23, more often with fewer + votes). This is anti-majority.
A12 07:13Z Win32_Process: 0 W-V python processes. Lease lse-cfddaaf967a6 RELEASED (--lease --token);
   `python -m fabric lease status` -> []. Monitor task stopped. Compute: runs 1826 s x 1 thread = 0.51
   core-h; tests + dev + post hoc about 250 s = 0.07; total about 0.6 core-hours. Outputs 506 KB. No pycache.
