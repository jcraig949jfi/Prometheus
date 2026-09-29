# W-P LOG (E-ANANKE-W-P, T-INS-8, MWO-0002)

A0 2026-09-29 boot. Read COMMON_RULES.md, COMMON_RULES_ARC3.md, lens_swap.py (docstring
  + code), engine.py, envs.py (build/per_trial), plants.py, W-M apply.py, W-N plants_rel.py
  header. Context contamination (brief-directed): read W-M/REPORT.md, the corrections
  register CORRECTIONS_2026-09-29_SWAP_AUDIT.md, W-O corrections_WI.csv (369f5a5b rows),
  W-I table_369f5a5b.csv / table_4781b0a1.csv and W-M census_*.json SINGLE blocks
  (per-offset fS/fC/fN) BEFORE writing PLAN.md. Did NOT read SYNTHESIS*, C1B_REVIEW*,
  PTE_ENGINE_CARD.md, ARC3_PRIORITIES.md.
A1 Decompiled both champion genomes (plants.regmap) before PLAN (specimen reading, no
  swap results). 4781b0a1 readout line 7: S0 := ADDI(IN0_1, imm -3 + Kp[7]); Kp written
  by WIMM (line 8 Kp[S0%16] := EMIT = MAX(S1,SENSE); line 15 Kp[0] := PAY1). sync,
  update_period 2, dest 'sample' with plastic w (w routes). 369f5a5b: 4 rules, async
  p=.8, dest 'all' (w never read by the physics -> inert component), rule 0 has
  S1 := MAX(IN1_0, SENSE+S1), S0 := 4*(Kp[7]-25) + S1, r := CNT0 mod 4 (SETRULE).
  Fabric lease status at boot: [] (no leases held).
A2 PLAN.md frozen (before any champion swap run). Wrote tt.py (snapshot truth-table
  runner), ana.py (relevant set / class / minimal decisive set / frozen rules),
  plants_joint.py (max_plant = KA-AND, mux_plant = KA-MUX), test_ana.py (6 synthetic
  classifier tests: AND, OR, MUX, XOR3 -> HIGHER, DICT, AND-not-MUX; 6 passed).
A3 timing.py on both champions (namespace 0x7777, outputs discarded, only wall time):
  369f5a5b 28 s, 4781b0a1 50 s per 32 subsets x 2 offsets x 256 worlds at 2 threads.
A4 run_ka.py (plants, seeds 0x611 x64, HOLD gap 8, offsets 3..8, trials 1..7): C1
  bit-identity vs lens_swap True x4 on all four plants. max: fN 1.00, JOINT-2(S,Msum),
  RECTIFIED(+), md {S,Msum} at every offset. mux: fN 1.00, GATED(Kp), R {S,Kp,Msum},
  md {S,Msum}. latch fS 1.00 / echo fC 1.00, base N 0 -> UNDEFINED (never JOINT/GATED).
  NOTE (bug-class finding): the max_plant with Msum DROPPED run through the half-cube
  pipeline read fS = 1.00, a spurious SITE: the half-cube trick b(z) = a(~z) assumes
  identity, which an incomplete partition breaks. Hence ka_mustfail.py: full cube, no
  identity assumption: complete list -> identity 1.0, decisive {S,Msum} 32/32; drop Msum
  -> identity 0.50, NO-DECISIVE 32/32. The C2 identity check is therefore load-bearing
  for the champions' half-cube runs.
A5 Fabric lease lse-feb3419a6fe6 (skullport:cpu8, --as Ananke) ACQUIRED 10:02Z, ttl 1 h.
  C1 on champions (trial 5, o6, 32 worlds): 369f5a5b and 4781b0a1 True x4.
  First launch attempt garbled by shell line continuation (no process started); relaunched
  via launch.sh: 4 procs x 2 threads (369 trials 1-11; 4781 1-4, 5-8, 9-11 + verify k6).
A6 10:15Z INCIDENT: the "garbled" first launch (A5) HAD started 3 processes (369 main,
  4781 main 5-8, 4781 main 9-11 chained to verify k6); Git-Bash ps does not list Windows
  python.exe, so I missed them. 7 run_champ processes ran for ~12 min (14 threads > the 8
  leased). Killed the three 06:02:44-local duplicates (PIDs 27184, 27588, 16084) and the
  verify they chained into (26380) via taskkill after listing Win32_Process command lines.
  No npz had been written by any process yet (no trial finished), so no output file was
  written twice. Remaining: 4 procs x 2 threads from launch.sh.
A7 10:21Z DEVIATION D1 (budget, decided on wall time only, no result inspected): trial 1
  took ~1000 s per process (partly under the A6 oversubscription); 11 trials x 2 cells would
  exceed the 3 h cap. Killed all 4 procs (after trial-1 files for 369 k1, 4781 k1/k5/k9 were
  written, complete). Trial sets reduced: 369f5a5b {1,2,3,4,5}, 4781b0a1 {1,2,5,6,9,10}.
  DEVIATION D2: verification slice (C2/C3) offsets reduced to {-1,1,5,10,14} (trial 6).
  Relaunched via launch2.sh (4 procs x 2 threads).
A8 10:22Z lease renewed (ttl 5400 s). 10:41Z main runs done: 369f5a5b trials 1-5, 4781b0a1
  trials 1,2,5,6,9,10 (~530-600 s per trial per proc). analyze.py -> out/summary_*.json,
  out/analyze_*.txt, out/recs_*.pkl. Added (reporting only, not decision rules) the
  per-(R, truth table) mode 'fn_top' and the swap-tick parity split; posthoc.py
  (monotonicity, |R| sizes, minimal decisive set inside site-only) -> out/posthoc_*.json.
A9 10:43Z stage 2 launched (launch3.sh; offsets chosen by PLAN s6 rule from stage-1
  census: 4781b0a1 max-fN o6, earliest o1, latest o15 (modal md {inbox,Msum}); 369f5a5b
  max-fN o9, earliest o1, latest fN>=.20 o13), restricted to stage-1 N pair-trials.
  Verify slices (C2/C3) still running (2 procs); stage 2 adds 2 procs -> 8 threads.
A10 10:46Z verify slices (trial 6, full cube): 4781b0a1 identity 1.000 at o1/5/10/14,
  .265 at o-1 (must-fail); 369f5a5b (incl. w) 1.000 at o1/5/10/14, .602 at o-1; w in R for
  0 pair-trials (C3); direct (no-identity) decisive set found for every eligible pair at
  o >= 1. out/verify_*.json.
A11 10:49Z stage 2 done (out/s2_*.json). All run_champ/stage2 processes exited (checked
  Win32_Process). Lease lse-feb3419a6fe6 RELEASED 10:49Z; `fabric lease status` -> [].
  git status: nothing modified outside W-P.
A12 Prediction outcomes (frozen PLAN s5): P1 held (identity 1.000 at o >= 1 both cells).
  P2 FAILED: Kp is in R for 0 N pair-trials of 4781b0a1; JOINT-2 held but with {S, Msum}
  (stage 2: S1 x Msum payload 1) at o1-9 and {inbox, Msum} (Acc_sum x Msum_p1) at
  o14-15; polarity RECTIFIED(-) at o1-5, (+) only at o12-15. P3 partly held: S and Msum
  in the modal R; r in R >= .30 at o1-3, o5, o6, o8; class HIGHER o1-8, MIXED o9-10,
  JOINT-2(S,Msum) o11-14; RECTIFIED(+) only at o10-12, o14 (PAIR-SPECIFIC o1-9). P4 held.
  GATED never met the rule (MUX share <= .16 anywhere).
  Post-hoc (not a frozen rule): 4781b0a1 N is concentrated in one sync phase (swap-tick
  parity, update_period 2): e.g. o14 even tick C 1.00 / odd tick N .70.
