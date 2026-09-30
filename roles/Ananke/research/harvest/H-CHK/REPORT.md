<!-- DEPOSITED VERBATIM by Ananke for worker ../harvest/H-CHK; sha256(report)=ed28c303142877ef; delimited; see REPORT.provenance.json -->
H-CHK REPORT: three decisive checks from the inference harvest (worker H-CHK, Ananke seat)

WHAT I TESTED
- The plan was frozen at commit 7e156c12b (2026-09-30 18:22:10 -0400). I did not edit it.
  - The first run of any kind was a 100-tick engine timing smoke test at about 18:25. The first gate result came at about 18:30. Both came after the freeze.
  - I wrote PLAN_ADDENDUM.md (X1-X6, labelled post-freeze) before any gate or C1-C3 run.
- Every check reuses the workers' code by import, without edits: W-P tt.py and ana.py; W-V wv.py, ana.py and plants_wv.py; W-N plants_rel.py and swap_rel.py; W-L's champions and nback.
- Run conditions for every process: CUDA_VISIBLE_DEVICES=-1, device="cpu" passed explicitly, 1 thread, PYTHONDONTWRITEBYTECODE=1.
- C1. Does a noisy count threshold reproduce 4781b0a1's "joint carrier" signature?
  - Plant physics: W-V's plant physics, adjusted to the champion's delivery. That means dest 'sample', fanout 8 over the 6 ring ports, loss .1, jitter 1, sync period 2. I kept W-V's latencies (5/2) and cap 0.
  - Sensors latch the rectified cue (S1 := 256 or 0) and re-emit PAY1 = S1 on every wake.
  - Readout: S0 := IN0_1 - theta.
  - theta was fixed a priori on a disjoint namespace (0xC4C1 x 512) as the smallest grid value with accuracy >= .70. That gave theta = 640, meaning "+" iff at least 3 payload-1 copies arrive in the last wake window. Accuracy was .732 (ideal 5-vote majority: .838).
  - The plant then went through both workers' champion designs:
    - W-P: 0x610 x 256, trials {1,2,5,6,9,10}, o1-15, half cube, clock-parity split.
    - W-V: 0x650 x 128, trials 1-11, o2-14 even.
- C2. W-V's PMAJ plant, re-run at the champion's loss .1 and fanout-8 sampling. Everything else was as W-V (0x650 x 128, o2, o4, o6, o8, o12).
- C3. P1S (noiseless) and the W-L champions n1_s0 and n2_s2. M = 512 on W-N's specimen seeds, S swap after tick k*Pd-1, SINGLE trial, two modes:
  - (a) the mirror swap;
  - (b) single-cue twins (lens_swap.twin_profile semantics): the twins differ only in the held cue c_{k-n}, one episode per scored trial.
  - Statistic: z = (s-.5)/(a-.5), with a 99% pair-bootstrap CI on W-N's resample indices; W-N's verdict is reported alongside.

KNOWN-ANSWER GATE: PASS (all three parts, before any C-run)
- G1 (the frozen gate): hold_latch and echo_hold through W-P's pipeline at W-P's KA design.
  - Latch: fS 1.00, base_N 0, UNDEFINED at o3-8.
  - Echo: fC 1.00, base_N 0, UNDEFINED at o3-8.
  - Bit-identity against lens_swap: True x4 for both.
- G2 (added; hold_latch and echo_hold cannot go through W-V's 5-sensor classifier): my re-run of PMAJ and PDICT reproduced W-V's numbers exactly.
  - KA-MAJ, KA-DICT and MF1-MF4 all pass.
  - PMAJ D_piv is 1.00 [1.00,1.00].
- G3 (added): P1S mirror S1/S swap gives FLIP_REL, z -1.00 [-1.00,-1.00].

C1 RESULT. Frozen reading: PARTIAL, decided by a margin of .0004.
- (i) AND/OR-dominated N in one clock phase: HOLDS.
  - Every N stratum is JOINT-2 with AND/OR near 50/50. The JOINT-2 share is 1.00 [1.00,1.00] everywhere.
  - o3-o7: JOINT-2(S, Msum). For example, o4 fN .37, AND .50 / OR .50.
  - o14-o15: JOINT-2(inbox, Msum), the same pair W-P found in the champion at o14-15.
  - N sits in one clock phase at o3 (parity0 fN .37, parity1 0), o7, o14 and o15.
  - The plant reproduces the champion's late phase pattern:
    - o14: parity0 fC 1.00, parity1 fN .42 (champion: C 1.00 / N .70);
    - o15: parity0 fS 1.00, parity1 fN .39 (champion: S 1.00 / N .64).
  - The W-V run replicates the phase effect: o14 q1 E .50 [.44,.56] (champion .49).
- (ii) DISTRIBUTED-NONMAJ with D_piv < .3: FAILS at the boundary.
  - The W-V verdict is DISTRIBUTED-NONMAJ in 9 of 9 informative strata. Singles are .20-.25, complements .58-.80.
  - D_piv ranges from .23 [.16,.31] to .31 [.26,.37]. The median is .3004, against the pre-declared rule "median < .3".
  - For comparison: champion D_piv .10-.12; lossy PMAJ .38-.44; lossless PMAJ 1.00.
- Where the plant differs from the champion:
  - The plant has no N at o8-o13, and its readout-bound traffic acts from o4. The champion's acts from o10. This fits the longer W-V latencies.
  - The plant's polarity is PAIR-SPECIFIC, not RECTIFIED(-).
  - The plant's D_piv sits above the champion's.

C2 RESULT. Frozen reading: PARTIAL.
- The lossy PMAJ (normal accuracy .781) reads DISTRIBUTED-NONMAJ{0-4} in every informative stratum at o2-o6.
  - D_piv .44 [.34,.53] in q0 and .38 [.28,.47] in q1. The lossless plant gave 1.00.
  - At o8: D_piv .36 / .30. o12 is NOT-INFORMATIVE.
- Loss and sampling alone make W-V's frozen classifier call a true majority "not a majority". They do not push D_piv all the way down to the champion's .10-.12.

C3 RESULT. Frozen reading: NOT CONFIRMED. This is what I predicted in writing (addendum X5) before the run.

| Specimen | (a) mirror z [99% CI] | (b) twin z [99% CI] | Verdict (both modes) |
|---|---|---|---|
| P1S | -1.00 [-1,-1] | -1.00 [-1,-1] | FLIP_REL |
| n1_s0 | -.953 [-1.154, -.786] (reproduces W-N) | -1.000 [-1.000, -1.000] | FLIP_REL |
| n2_s2 | -1.064 [-1.302, -.878] | -1.000 [-1.000, -1.000] | FLIP_REL |

- Must-fail: P1S with the twin differing at cue k-2 reads z +1.00 (NO_EFFECT_REL). It does not read <= -.95, so the must-fail fails as required.
- Why z is -1 for the integrators: the twins receive identical input after the swap tick. So an S swap puts world A exactly on world B's trajectory, and s = 1 - a holds pair by pair, whatever the mechanism.
- The lag weight shows up elsewhere: in how often the twins' outputs differ at all (.23-.54 of pairs, falling with trial index, as integration predicts). It does not show up in z.

DEVIATIONS (all in PLAN_ADDENDUM.md, written before the affected runs)
- X1: two gates added (G2, G3). The plan's gate plants do not fit W-V's classifier.
- X2: concrete plant program, theta grid, and the latencies kept at W-V's values. I also made the frozen readings operational: (i) is W-P's frozen JOINT-2 class in some parity stratum; (ii) is W-V's verdict plus median D_piv.
- X3: C2 read at W-V's KA offsets 2, 4 and 6.
- X4: "cue k" means the held cue c_{k-n}. The literal reading makes z undefined and the must-fail meaningless. "Similarly" means |z_a - z_b| < .5.
- No sensitivity variant (champion latencies) was run.
- Bookkeeping bug: run.sh names logs by the first argument only, so logs/c3_P1S.log was overwritten by the must-fail run. The JSONs are separate and intact (LOG A8).

DISAGREEMENTS
- With H-SCI claim 10 and C3's premise: a single-cue-twin S swap cannot tell an integrator from a lag-k store. It gives z = -1 for both. So "the mirror certificate is overstated" is not shown by this test. Telling them apart needs a statistic that is not normalised by the twin effect, such as the twin-difference rate, or a lag profile.
- With W-V (12d) and W-P (12a):
  - W-V's classifier calls a lossy true majority DISTRIBUTED-NONMAJ. So that label is not evidence against "noisy majority by count".
  - A count threshold with no joint logic reproduces JOINT-2 AND/OR, including W-P's (inbox, Msum) pair and the clock-phase split at o14-15.
  - "Joint carrier" as a distinct architecture is therefore not supported by these tables. The frozen readings are still PARTIAL: D_piv sits at .30, and the champion's D_piv (.10-.12) is lower than both plants'. Something beyond loss plus a count threshold (rectification strength, latency) remains unexplained.
- With H-SCI 12d's expectation "D_piv falls to about .1": it fell to .38-.44, not .1.

PYTEST
- Command: `CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python -m pytest test_hchk.py -q -p no:cacheprovider` (run from H-CHK/).
- Result: 4 passed, RC=0 (logs/pytest.log).
- The first run had 1 failure, which was a test bug (tuple keys passed to dict(**)). It is logged as A3 and fixed.

LEASES
- None. At most 2 processes x 1 thread, no GPU.
- PIDs logged in LOG (11720, 25916, 18256, and the others). Win32_Process shows 0 H-CHK python processes remaining. No background processes are left.

COMPUTE
- About 2.3 CPU core-hours (cap 3): 8069 s of summed process wall at 1 thread, plus about 5 min of imports, pytest and smoke.
- Wall time about 1 h 25 min.
- Outputs 513 KB (out) + 48 KB (logs).
- No git writes. No edits outside H-CHK/. No pycache.

FILES (F:/Prometheus-worktrees/ananke-base-role/roles/Ananke/research/harvest/H-CHK/)
- PLAN_ADDENDUM.md, LOG.md (A0-A11)
- Code: hchk.py, gate_g1g3.py, gate_g2.py, c1.py, c1_ana.py, c2.py, c3.py, run.sh, test_hchk.py
- out/:
  - gate_g1.json, gate_g2.json, gate_g3.json, raw_g2_{pmaj,pdict}.npz
  - c1_calib.json, c1_tt_raw.npz, c1_tt_meta.json, c1_wp_table.txt, c1_wv_raw.npz, c1_wv_meta.json, c1_wv_summary.json, c1.json
  - c2_raw.npz, c2.json
  - c3_P1S.json, c3_P1S_mustfail.json, c3_n1_s0.json, c3_n2_s2.json, c3.json
- logs/
