# W-U LOG (E-ANANKE-W-U, T-SWAP-REL3, MWO-0004)

A0 2026-09-29 15:00Z context. Read COMMON_RULES.md + COMMON_RULES_ARC3.md. Read (as the brief directs,
BEFORE the PLAN) W-Q REPORT.md (rule, results, disagreements) and W-Q code swap_rel2.py, build_tables.py,
apply_wo.py, validate_plants.py, run_plants2.py, head of out/fc_precision.json; W-N plants_rel.py
readout_noise + run_plants.py; W-O out/rerun_table.csv header + one rerun_s0.jsonl line.
Context contamination (declared): W-Q's FC numbers (P256 .6-.9%, P64 ~1.04%, P32 K3 up to 1.8%, P4 13-16%)
are known to me before the PLAN, as the brief itself states them. No SYNTHESIS/C1B_REVIEW/ENGINE_CARD read.
Finding before PLAN: W-O saved NO pair-level arrays for the 733 verdicts (only per-arm mean + percentile
CI of normal and swap, M=512, P=256). A pair-level re-application is therefore impossible without an
engine rerun; PLAN s6 freezes a bounding protocol from the saved marginals instead.
Fabric `lease status` at 15:01Z: [] (no leases).
A1 15:05Z wrote intervals.py (vectorised PCT/BCA/BOOTT/TINT/XPCT + T90 control). Timing only, on
uniform random data (no model, no FC computed): ~0.25-0.34 s per 1000 datasets for all candidates
at P=8..256, 1 thread -> n=20000 per point ~7 s.
A2 15:05Z lease lse-b3feff8054ae ACQUIRED (token 2114fe8c...); launched fc_sim.py workers 0-7 (1 thread each), PIDs in out/pids.txt, logs/fc_w*.log
A3 15:06Z wrote swap_rel3.py skeleton; METHOD='TINT' and P_FLOOR=16 are PLACEHOLDERS (= predictions Pr2/Pr3) until the s4 selection is run
A3b 15:08Z TIMESTAMP CORRECTION: my earlier LOG/PLAN clock labels were guesses. Actual (file mtimes, UTC):
intervals.py 15:03:23, PLAN.md frozen 15:04:28 (sha256 58255ac1ee466821...; its header says "~15:15Z", which
is wrong - left unedited to keep the hash), fc_sim.py 15:04:46, launch 15:05:06, swap_rel3.py 15:06:10.
The PLAN predates the first simulated candidate (launch) by ~40 s. Lease acquired ~15:04:50.
Win32 PIDs of fc_sim workers 0-7: 18188 20000 10984 26508 24656 25716 20916 23156 (out/pids.txt).
A4 15:27Z lease renewed (RENEWED); FC jobs 24/54 done, P64 jobs ~10-20 min each due to stage-2 top-ups
A5 16:16Z all 54 FC jobs + 19 reach jobs DONE; build_table.py -> WINNER BOOTT, P_FLOOR 32 (only candidate with floor < 64; PCT 128, BCA 128, TINT 128, XPCT 64). Lease lse-b3feff8054ae RELEASED 16:17Z (0 fc/reach procs; status shows no cpu8). Set swap_rel3 METHOD=BOOTT P_FLOOR=32 per s4 (placeholders were TINT/16). FINDING: BOOTT power collapses at p=.99 (P64 K11 realistic FLIP .72, P32 K11 realistic .23) -> frozen p_min rule gives p_min=1.0 for F/N at P32-P64 (K3 also P128/P256 NO_EFFECT). Reported, rule not changed. apply733 uses the t normal-approx (TQ) for BOOTT at P=256 (PLAN s7 had no BOOTT approx): noted approximation.
A6 16:17Z validate3 run 1: z_class float bug (exact z=-1 zero-width CI classed OVERSHOOT); fixed with eps=1e-9 tolerance; rerun.
A7 16:18Z validate3 rerun: KA1 0 FC, 59/59; KA2 P32/64/128 0 FC (recovery .73/.98/1.0); KA3 0 FC 19/19; M3 40 FC (must-fail OK).
apply733: 669 DETERMINED (all identical to REL2), 64 AMBIGUOUS (cert may drop to INDETERMINATE), 0 INCONSISTENT.
pytest: 10 passed RC=0 (out/pytest.txt); added test documenting the BOOTT near-degenerate weakness.
POST HOC (labelled): out/pmin_posthoc.txt = p_min with the power curve capped at p<=.95 (BOOTT then matches TINT/PCT within .01).
Compute: fc_sim 28864 core-s (8.0 core-h) + reach_sim 2227 core-s (0.6) + validation/tests ~0.05 -> ~8.7 core-h. Max 8 threads.
Final Win32_Process check: 0 W-U python processes. Lease lse-b3feff8054ae RELEASED (status: no cpu8 lease).
