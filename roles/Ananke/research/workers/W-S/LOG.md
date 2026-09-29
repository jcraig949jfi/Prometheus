# W-S LOG (E-ANANKE-W-S, T-INS-11, MWO-0004)

A0 2026-09-29T13:24Z  Read COMMON_RULES.md, COMMON_RULES_ARC3.md; W-R REPORT.md RESULTS + DISAGREEMENTS
  (as the brief directs: context contamination = W-R's interpretation of the mixed phase, declared);
  read W-R fork.py, specs.py, PLAN s4 (KA-P), prometheus/ananke/{engine,lens_swap,envs,topology,rng} and
  plants.echo_hold. Did NOT read SYNTHESIS*, PTE_ENGINE_CARD, other workers' reports.
  Champions: ring r3, N 144, fanout 8 sampled routes (plastic w), lat = 1 + dist + jitter{0,1}, loss .1,
  cap 2 saturate, LM 8, sync period 2; RELAY d 3, delta 8, cue_len 2, Pd 11 (odd).
  Hand derivation (before any run): q1 of o5 = t0 even -> source wakes at t0, emits; direct copy to the
  readout (ring dist 3) has delay 4/5 -> arrives t0+4/t0+5 <= tau=t0+5 -> held in site/inbox -> SITE.
  q0 of o5 = t0 odd -> source's first wake at t0+1, direct delay 4/5 -> arrives t0+5 (<= tau) or t0+6
  (> tau): latency jitter would split S/C ~50/50. This is H1's mechanism; the probe tests it per pair-trial.
A1 13:40Z  Wrote probe.py (LogWorld: log of mirror-different packet copies with engine-identical draws;
  fork with arms site/chan/site_a/flight_a), analyze.py (predictors, accuracy, KA-L in-flight check), run.py.
A2 13:50Z  Smoke PLANT2J1 (echo_hold, period 2, jitter 1) M16: KA-L in-flight reconstruction 440/440 equal
  (must-fail te+1: 234/440, mostly empty sets agreeing). Finding: in the plant, a copy pair straddling
  tau (one delivered, one in flight) is NOT read as N: the echoes cancel, the sensor keeps its stale
  (previous-trial, mirror-different, site-held) S0, and S vs C then follows y_prev == y_now. So H1 needs a
  3-way predictor (all-held S / all-in-flight C / straddle M).
A3 13:55Z  KA-F (arm identity vs W-R fork_single, M16 ns 0x630 trials 1-3): PLANT2J1 11/11, 2dccdaa5 5/5,
  e06701a5 5/5; must-fail late=1: 10/11, 3/5, 3/5 (not identical). NOTE: this touched champion
  2dccdaa5 at M16 for arm identity only; no pattern or predictor output was computed or looked at.
A4 13:57Z  DEV run (predictor development, declared): e06701a5 (same geometry, NOT a champion),
  M64, ns 0x631, o4,o5. Plant exploration also counts as development.
A5 14:00Z  e06701a5 dev gave 0 eligible pair-trials (normal S0 mostly 0 = ties; it is a follow-census cell). Switched DEV to 4781b0a1 (MAJ, sync p2, same geometry; not a champion) M64 ns 0x631 o5,o9.
A6 (clock 13:31Z) CLOCK CORRECTION: the times in A1-A5 were estimates; `date -u` read 13:24Z at A0 and
  13:31Z here. Changes since A5: switched predictors to CUE-BEARING packets (cue-flip twin, same world
  seed) because the mirror-difference log is non-specific (every emission of a sign-flipped world differs).
  Dev plant (jitter 1, M64 0x631): decisive P3 100% correct at the straddle phases (o5/o6/o11/o12 q1);
  P3 = M cases follow y_prev == y_now exactly (S iff same). Dev 4781b0a1: every cone M, direct in-flight
  share ~equal across S/C/N (no timing signal in MAJ). KA-L now scored as real-subset-of-logged (4781b0a1:
  704/704 subset, 624/704 equal: logged copies can cancel in a slot sum).
A7 13:32Z  PLAN.md FROZEN, sha256 5ef889411088081abcae7f8fa2eb17f0cd39c3408c6d8e2c577dd523b58e7719.
  Added P6_share to analyze.features (defined in PLAN s3; code written after freeze, no data seen).
A8 13:32:40Z  Lease lse-6d73ca4a7e5b skullport:cpu8 ACQUIRED (--as Ananke), expires 14:32Z. Win32_Process: no W-S python running. pytest 7 passed RC 0.
A9 13:33:20Z  Launch bug: $W unset in 2 of 3 background subshells -> champion runs did not start (bash error only); KA-P plant J1/J0 runs started (PIDs 26844 J1, then 26764 J0). Relaunching champions via launch_champs.sh.
A10 13:33:48Z  Champion PIDs 7808 (c16d5231), 10984 (2dccdaa5 then 8c37f32e), 2 threads each. KA-P runs done (J1 21 s, J0 27 s).
A11 13:34:42Z  KA-P PASS (out/summary_KA.txt): jitter1 straddle phase q1 at o5/o6/o11/o12: P3 decisive 1.00 [1.00,1.00], coverage .48/.51/.49/.53; P7b on M 1.00 (n335/375/324/361); shuffled P3 decisive .50/.54/.45/.51 (<=.65). jitter0: every offset-phase a single class, P3 strict 1.00. Direct-only predictors P1/P2/P4 fail the first-leg offsets (carrier upstream), as expected.
A12 13:36:22Z  Champion runs done (2dccdaa5 66 s, c16d5231 65 s, 8c37f32e 50 s); summary out/summary_champions.{txt,json}. KA_L real-subset 2816/2816 in all three.
A13 13:38:48Z  POST HOC (labelled): posthoc.py re-runs champions (same seeds) for source-first-emission features (P8_srcfirst). Found: log field 'dist' is side-A's hop distance, wrong for twin-side copies when the cue changes the route (it does: plastic routing); jit is a shared draw and correct. first_dist descriptor therefore unreliable; not used.
A14 13:40:38Z  POST HOC results out/posthoc_summary.txt: P8 decisive 1.00 in U1-U4 (coverage .75/.62/.61/.28); P8any strict U1 .87 [.83,.91], U2 1.00 [1.00,1.00], U3 1.00 [1.00,1.00], U4 .64 [.59,.70]. Straddle cases: 2dccdaa5 C60/S68 (chimera readouts are small near-cancellation residuals, e.g. site [-18,16] vs normal [187,-189]); c16d5231 all C; 8c37f32e C161/S160/N178. No simple split predictor (y_prev, label sign, partner magnitude). PLAN s7 addendum written for a confirmatory 0x632 replication; PLAN sha256 now below.
c75a1dad6de27bd3c6809c2ff2cfb1b7363e29a82a9600eb7856f98f65a241d1 *PLAN.md
A15 13:41Z  CONFIRMATORY replication ns 0x632 (PLAN s7), out/posthoc_summary_ns632.txt: R1 P8 decisive
  1.00 [1.00,1.00] in U1-U4 (coverage .75/.61/.60/.28): PASS. R2 P8any U2 1.00 [1.00,1.00], U3 1.00
  [1.00,1.00], U1 .88 [.84,.91] (in [.80,.95]), U4 .65 [.58,.71] (not > .80): PASS as predicted. R3 straddles:
  c16d5231 141/141 and 165/165 C; 2dccdaa5 S share .49; 8c37f32e .49 (+201 N): PASS. R4 clean phases P8any
  1.00 (8c37f32e o5q1 .997): PASS. Must-fail shuffled P8any U2/U3 .52/.52: PASS.
A16 13:41Z  No W-S python processes (Win32_Process count 0). Lease lse-6d73ca4a7e5b RELEASED (--lease
  --token), `python -m fabric lease status` -> []. Compute: ~800 process-seconds x 2 threads ~ 0.45
  core-hours (<= 0.5). Wall 13:24Z-13:42Z (clock) plus analysis.
