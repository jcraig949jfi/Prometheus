# W-N LOG (T-SWAP-LOWACC)

A0 read COMMON_RULES.md + COMMON_RULES_ARC3.md, lens.py, lens_swap.py (docstring +
   census), W-L nback.py / carriers*.py and out/carriers_champs.json, W-F census.py
   and out/census_table.csv (specimen selection). Context note: saw W-L champion
   verdicts (S CHANCE at normal .58/.59) and W-F ELSEWHERE rows before PLAN. Did NOT
   read SYNTHESIS*, C1B_REVIEW*, PTE_ENGINE_CARD, ARC3_PRIORITIES or any REPORT.md.
A1 wrote swap_rel.py (rule + attainability). attain_table.py / attain_table2.py ->
   out/attain_table.json (pure simulation, no specimen data). First p_min run hit
   the 600 s tool timeout for the P=256 rows -> reran in background, completed.
A2 plants_rel.py; smoke_plants.py (M=64): P1S noiseless normal 1.0, S/S1 swap 0.0,
   S0 swap 1.0; P1S q=.3 normal .676, S .324. BUG: P1SK default th=-300 made the
   RAND flag ALWAYS fire (normal 0.0): flag iff RAND > th, so "never" needs th >= 256.
   Fixed to th=300. run_arms too slow (146 s per 34 arms x 64 worlds).
A3 added run_fork (deep-copy the normal world at the swap tick, step the copy to
   the readout only). selfcheck_fork.py: readouts bit-identical to run_arms and to
   lens.run (S swap, trial 4) on P1S q=.3, P1SK q=.3, P1SK noiseless: all True;
   5.5x faster. out/selfcheck_fork.json.
A4 PLAN.md frozen. Fabric lease skullport:cpu8 ACQUIRED lse-4124e1f2992d.
A5 test_swap_rel.py first run: 2 FAILS, both in my test expectations, not the rule:
   (i) absolute rule at P=256,K=11,normal .70 already FLIPs (hi99 ~.32 < .40): the
   absolute gap is SAMPLE-SIZE dependent (absent above normal ~.6+hw99); (ii) the
   lo99 test's draw had lo99 .592 > .59. Fixed the tests (gap shown at .60, ungated;
   new test documents the large-N FLIP). 23 passed.
   Pre-specimen observation (NO amendment to the frozen rule): the worst-case gate
   (lo99(normal) >= p_min) is STRICTER than the absolute rule's FLIP reach for exact
   mirror flips (e.g. P=64,K=11: absolute FLIP from normal ~.65, relative eligible from
   ~.72). All three relative verdicts are ~0.5 %-error certificates at any normal > .5;
   the gate trades valid-but-rare certificates for the "separable" guarantee the brief
   asked for. Both gated and ungated verdicts are reported.
A6 run_plants.py rep 0 launched, 8 threads, under lse-4124e1f2992d.
A7 run_plants rep0: P1S all 35 cells PASS (q .45/.40 -> NOT_ELIGIBLE as expected by
   gate; q<=.35 all verdicts == truth). Crashed at the first P1SK cell on a print
   (flip_rate f=None: swap arm all ties, no decisive cells) BEFORE writing json;
   P1S rows kept in out/run_plants_r0.log only. Fixed print; reran P1S+P1SK
   separately (argv plant filter). Absolute rule on the same data: FLIP truth read
   CHANCE at q=.40/.45; S1_half (CHANCE truth) read NO-EFFECT at q=.45; S1_3q
   (z=-1/2) read FLIP at q=0.
A8 run_plants rep0 P1S rerun: 35/35 PASS (identical to A7 rows). P1SK: 21/21 PASS (S, Kp tie-CHANCE ->
   CHANCE_REL for q<=.35; site_all FLIP_REL; q=.40 (lo99 .580) and .45 -> NOT_ELIGIBLE). Absolute rule
   read NO-EFFECT on the tie-CHANCE truth at q=.45.
A9 W-L specimens (M=512, W-N seeds 0x4E, 3 threads): every S / site_all arm FLIP_REL (z -0.95..-1.08);
   channel/inbox/Kp NO_EFFECT_REL (s == normal exactly, f = 0: arm effectively identical, trivial).
   The ABSOLUTE rule on the same data also says FLIP everywhere.
A10 wl_design.py: at W-L's own design (M=64 W-L seeds, trials 4,6,8) I reproduce W-L's numbers exactly
   (n1_s0 normal .583 swap .323); absolute CHANCE; relative NOT_ELIGIBLE (p_min .91 at P=32,K=3).
   => the W-L CHANCE was a SAMPLE-SIZE effect, not a rule effect.
A11 C1 5 ELSEWHERE cells (M=512, seeds 0xC1, SINGLE + EVERY + census). HOLD cells: site_all/joint FLIP_REL
   and absolute FLIP at M=512 (recorded M=64 EVERY: CHANCE). RELAY 42716814 mid: site CHANCE_REL
   (z -.37) but census fS .69 fN .22 = PARTIAL site transfer, not "neither"; late site FLIP_REL.
   d3c0d182: site/channel INDETERMINATE (z -.47/-.51); readout is one-sign: partners are never both
   correct (M=128 check: pair patterns (1,.5) 18 %, (.5,1) 28 %, (.5,.5) 30 %, (1,0)/(0,1) 24 %,
   (1,1) 0 %); census UNDEFINED (0 eligible). joint FLIP_REL.
A12 Lease lse-4124e1f2992d RELEASED 02:44 EDT (first release call refused: missing --as; re-ran
   with --as Ananke -> RELEASED; lease status []). Post-hoc run at 2 threads, no lease.
A13 run_posthoc.py: hook-vs-posthoc equivalence True/True. 85/90 PASS. The 5 FAILs are all the
   INDETERMINATE-truth arm S1_3q returning CHANCE_REL in 6-7 % (> frozen 5 %) at p .65-.70. Cause
   found after the fact: the fixed 75 % pair mask realised 69.1 % in this seed set (noiseless f =
   .691, s = .309 -> true z = -.38, INSIDE the CHANCE band), so my truth label "z = -1/2" was wrong
   for this seed set; CHANCE_REL is the midpoint-correct answer for z = -.38. Recorded as FAIL under
   the frozen criterion; no threshold changed.
A14 summarize.py -> out/negative_controls.json, out/verdict_changes.csv. pytest: see out/pytest.txt.
