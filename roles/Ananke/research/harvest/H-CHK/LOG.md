# H-CHK LOG

A0 2026-09-30. Read frozen plan H-CHK_PLAN.md (commit 7e156c12b, 18:22:10 -0400), COMMON_RULES(_ARC3), H-SCI
   items 12a/12d/claim 10 and chain sections 1.3-1.9, RESULTS of W-P, W-V, W-N, W-L reports, and the reused code.
   Context note: the plan itself directed me to read H-SCI and the worker reports before running.
A1 Timing smoke (no swap, no classifier): PMAJ plant, 128 worlds x 100 ticks, 1 thread CPU: ~3350 world-ticks/s.
A2 Wrote PLAN_ADDENDUM.md (X1-X6) before any gate/C1-C3 run.
A3 pytest first run: 1 failure = test bug (dict(**) with tuple keys), fixed.
A4 GATE (PIDs 11720 g1g3, 25916 g2). G1 PASS (latch fS 1.00 / echo fC 1.00, base_N 0, UNDEFINED at o3-8; C1 bit-identity True x4
   both; 64 s). G3 PASS (P1S mirror S1 and S: FLIP_REL, z -1.00 [-1.00,-1.00]). G2 PASS (KA-MAJ, KA-DICT, MF1-MF4; PMAJ/PDICT numbers
   identical to W-V summary_pmaj; 669 s). Gate passed -> C1-C3 allowed.
A5 C1 calib: theta j=3 (640; readout + iff >=3 payload-1 copies in window), acc .732 on 0xC4C1x512 (j=2 .699, j=4 .722); ideal 5-vote majority .838. C2 launched PID 18256.
A6 C2 done (567 s): lossy PMAJ normal acc .781; informative o2-o6 strata all DISTRIBUTED-NONMAJ, D_piv .44 [.34,.53] q0 / .38 [.28,.47] q1 -> frozen reading PARTIAL. C1 tt + C1 wv launched.
A7 C1 W-V run done (615 s): normal acc .745; verdict DISTRIBUTED-NONMAJ in 9/9 informative strata (o6-o14q0); D_piv .23-.31, median .3004 (frozen (ii) needs < .3 -> fails by .0004; CIs [.16-.26, .31-.37] straddle .3). o14 q1 E .50 (champion .49). C3 chain launched (P1S, P1S mustfail, n1_s0, n2_s2).
A8 C3 P1S: (a) mirror z -1.00 [-1,-1] FLIP_REL; (b) twin z -1.00 [-1,-1] FLIP_REL (twin outputs differ in 100% of pairs). Must-fail (twin at c_{k-2}) z +1.00, NO_EFFECT_REL: does not read <= -.95 -> must-fail FAILS as required. Bookkeeping bug: run.sh names logs by first arg only, so logs/c3_P1S.log was overwritten by the must-fail run; the JSONs (out/c3_P1S.json, out/c3_P1S_mustfail.json) are separate and intact.
A9 C3 n1_s0: (a) z -.953 [-1.154,-.786] (= W-N), (b) z -1.000 [-1.000,-1.000]; n2_s2: (a) -1.064 [-1.302,-.878], (b) -1.000 [-1,-1]. Twin outputs differ in .23-.54 of pairs (falling with trial index). Frozen reading NOT CONFIRMED (|za-zb| < .5 both). As predicted in X5.
A10 C1 truth tables (3566 s; bit-identity vs lens_swap True x4) + c1_ana: N at o3-o7 and o14-o15 only, every N stratum JOINT-2 (S,Msum at
    o3-o7; inbox,Msum at o14-o15) with AND/OR ~50/50, polarity PAIR-SPECIFIC; N confined to one clock phase at o3, o7, o14, o15;
    o14 parity0 fC 1.00 / parity1 fN .42; o15 parity0 fS 1.00 / parity1 fN .39 (champion pattern). (i) holds; (ii) fails by
    .0004 (median D_piv .3004) -> frozen C1 reading PARTIAL.
A11 Compute: sum of process walls 8069 s at 1 thread (+ ~5 min imports/pytest/smoke) ~ 2.3 core-h of 3. No lease. Max 2
    concurrent processes x 1 thread. Win32_Process: 0 H-CHK python processes remain. out 513 KB, logs 48 KB. No sensitivity run.
