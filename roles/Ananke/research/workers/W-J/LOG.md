# W-J LOG

A0 (2026-09-28) Read COMMON_RULES, COMMON_RULES_ARC3, brief. Read engine.py,
lens.py, physics.py, envs.py, search.py, Aether spec/design docs (git show
origin/main). Context contamination: read W-C PLAN.md, NOTES.md,
X4_RESULT.md (interpretive) before PLAN, because the brief listed them as
raw evidence. Did not read SYNTHESIS*, C1B_REVIEW*, PTE_ENGINE_CARD,
ARC3_PRIORITIES or any REPORT.md before PLAN.
A1 PLAN.md written (E1 observational, E2 evolution design).
A2 E1 run (e1_c1_semantics.py -> out/e1.json). 777 evolved rows with held.
 MAJ CC share: SUM .041 (n122), SAT .217 (n23), ALOHA .000 (n29).
 E1-P1 FAILS by the frozen threshold (SUM-ALOHA gap .041 < .05), though
 ALOHA is lowest. E1-P2 HOLDS weakly (MAJ gap +.041 vs RELAY -.053; CIs
 overlap). E1-P3 HOLDS weakly (cap4 .033 vs cap1 0).
 SURPRISE: SAT beats SUM in every family with signal (ALL CC .152 vs .013).
 Confound check: wave A (352 cells, randomized) has CC 0 everywhere; the
 whole effect sits in waves B/B2/D, which are targeted, not random. One
 matched MAJ block (wave B, ring-100, d3, cap 2, 3 seeds each, all else
 equal): acc SUM .578/.504/.527, ALOHA .546/.516/.544, SAT .686/.556/.648.
 So SAT > SUM ~ ALOHA at n=3 per arm. Not a result alone; motivates E2 arm SAT.
A3 Note: E2-P4 was written for ALOHA1; the addendum's arm is ALOHA2. P4 is applied to ALOHA2 (declared before any E2 run).
A4 GPU lease BUSY (W-H until 06:50Z). E2 queued in QUEUE.md. CPU timing: 49 s/gen -> E2 infeasible on CPU. E3 (existing matched champions, CPU) planned in PLAN.md.
A5 arb.py (ArbWorld subclass: state-free hash-priority winner replaces the
 inbox; count 0/1) + test_arb.py: known answer SUM (107,2) vs ARB one of
 {100,7} with count 1; winner varies over ticks (share .51); CUDA graph ==
 eager digest. First draft used nonzero() (host sync, not graph-capturable);
 replaced by amax/zero/index_add before any use. PASS.
A6 E3 launched on CPU (2 threads), ~80 s per champion.
A7 Literature searches (Massey-Mathys, Goldenbaum-Stanczak, Nazer-Gastpar,
 Carandini-Heeger, Maass WTA, CRDT, population protocols, beeping, voter
 model, Land-Belew, Chaney-Molnar, coreworld, Tierra (write-privilege quote
 verified from the PDF), stigmergy). NOTES.md written.
A8 After PLAN, read principal files (ARC3 rule 2 order respected):
 SYNTHESIS_2026-09-28_ARC2 s6, ARC3_PRIORITIES, PTE_ENGINE_CARD head,
 CROSS_ENGINE_THREADS X-1. Disagreements noted for the report.
A9 load_probe.py (descriptive, 16 worlds, 1 thread): arrival load K at a
 receiver-tick: SAT champions f6b6, 1a86 K=3.5 mean, P(K>2)=.77 (dense
 flood, normalisation active 77% of the time); SUM champions 5765, 8ccf
 K=.025 (sparse). Identical numbers between the two SAT (and two SUM)
 champions looked like a bug; checked: genomes differ; always-emit (or
 cue-only-emit) programs make load a function of physics+schedule only.
A10 C1 held_tel emit_rate over the 18 matched champions: DENSE emitters
 (emit_rate >= .4): SUM 08d8 acc .527, ALOHA 8c5e .544 (collide .48),
 SAT f6b6 .686 and 1a86 .680 (the two best cells of the block). All other
 13 are sparse (~.005, active_frac ~.05: sensors only) at .50-.63.
 Descriptive reading: the operator decides whether DENSE relaying pays;
 only SAT (normalised mean) turns flooding into the best MAJ code.
A11 E3 done (out/e3.json, e3_console.log; e3_reduce.py). 64 held worlds, ns H(0x5EF,0xE3).
 Mean acc [own -> SUM/SAT2/ALOHA2/ARB]:
  SUM class (10):   .572/.568/.537/.551   own-adv +.020 [+.005,+.045]
  SAT2 class (5):   .633/.626/.525/.574   own-adv +.049 [-.002,+.081]
  ALOHA2 class (3): .550/.549/.540/.542   own-adv -.007
 E3-P1 FAILS: SAT-evolved champions do NOT lose under SUM (drop -.007
  [-.019,+.001]); the two dense SAT champions score .716/.714 under SUM vs
  .717/.714 under SAT2.
 E3-P2 FAILS (not every class): ARB drop SUM .021 [-.003,.060] (<.03),
  SAT .053 [.006,.093] (holds), ALOHA -.002.
 E3-P3 HOLDS: ALOHA champions |SUM - ALOHA| = .010.
 E3-P4 NOT_VERIFIED: inbox swap at ro-1 was arm-identical in every
  competent champion (the actuator's inbox is consumed each tick it wakes;
  F8-type unreachable swap).
 Descriptive: the dense SAT champions are content codes (payload swap in
  flight FLIP 3/3 competent, counts identical), the sparse SUM champions
  are source-presence codes (payload CHANCE 3/6, counts CHANCE 4/6).
  ALOHA kills the dense codes (.717 -> .539); ARB costs them ~.06 (a random
  winner mostly carries the local majority sign); sparse single-source
  codes are invariant to every operator except ALOHA (small losses);
  two sparse SUM champions that aggregate several sensors (5765, 8ccf)
  lose .09-.12 under ARB.
 Interpretation (post hoc, labelled): SAT is a positive rescaling, so any
  reader that uses only the SIGN of IN is invariant to SUM vs SAT. The
  operator matters only through the reader's invariances. Why SAT cells
  evolved the dense code more often is NOT explained by eval-time
  dependence -> it is either search-time (evolvability) or chance: E2-P8
  is the test.
A12 E4 (e4_census.py -> out/e4.json), wave A0 randomized census, ~490 cells
 per family. E4-P1 FAILS: SAT - SUM frac_contrast_pos MAJ -.0005
 [-.0013,+.0003], RELAY -.0003 [-.0011,+.0005]: no gen-0 head start for SAT
 (FLIP even slightly negative). E4-P2 FAILS: ALOHA - SUM MAJ +.0002.
 Caveat: gen-0 signal is at floor (~0.1% of random genomes contrast-positive),
 so E4 has little power; it rules out only a large head start.
A13 GPU retry 05:40Z: BUSY (W-H until 06:50Z). Waiting for it; drafting.
A14 06:20Z GPU acquired token 3fb8b35c068e (W-H released early). Launching E2 on cuda, MAJ first.
A15 E2 done 06:51Z, GPU released (token 3fb8b35c068e, comms 781). 32 searches,
 ~60 s each. out/e2_*.json, e2_console.log, e2_summary.json, e2_reduce.py.
 MAJ median held: SUM .556, SAT2 .570, ALOHA2 .531, ARB .573.
 RELAY median held: SUM .610, SAT2 .604, ALOHA2 .629, ARB .661.
 Frozen verdicts: P1 FAILS narrowly (RELAY |SUM-ARB| .051; ARB higher);
 P2 FAILS (MAJ SUM-ARB -.017); P3 vacuous (no ARB champion > .72);
 P4 FAILS (ALOHA2 emits no less); P5 HOLDS (+.014, tiny); P6 FAILS (0/4
 arms with own-operator advantage > .03); P7 "HOLDS" only mechanically
 (both drops ~0: -.002 vs -.005), reported as NULL; P8 FAILS (SAT2 emit
 median .005 = SUM's; 0/4 dense); P9 NOT_TESTABLE (no dense SAT2 champion).
 Descriptive: 29/32 champions are sparse (emit <= .03: only sensors emit),
 and their accuracy is identical under SUM, SAT2 and ARB to 3 decimals;
 ALOHA2 costs MAJ champions ~.03. The only dense MAJ champion arose under
 ARB (seed 2, emit .79, acc .615; .631 under SUM, .525 under ALOHA2); one
 dense RELAY champion under SAT2 (seed 2, .718; .719 SUM, .554 ARB, .518
 ALOHA2). E1/E3's SAT<->dense association did NOT replicate (0/4).
 MAJ competence stays far below the single-sensor ceiling (.70) and the
 5-sensor majority ceiling (.837): no champion entered the aggregation
 regime where the operators differ. E2 therefore cannot say the operator
 does not matter for aggregation; it says that at this physics, search
 finds codes in the operator's null space (arrival multiplicity ~<= 1).
A16 E5 plant AGG (e5_plants.py -> out/e5.json), f6b6 physics, 64 held worlds:
 MAJ SUM .695 = SAT2 .695 | ARB .674 | ALOHA2 .562. RELAY: .711 under all 4.
 E5-P1 HOLDS (identical), E5-P2 FAILS (SUM-ARB .021 < .05; ARB <= .74
 holds), E5-P3 HOLDS (-.133), E5-P4 HOLDS (identical), E5-P5 HOLDS (.695 vs
 best evolved .615). At this physics loss .3 + async wake leave ~2-3
 packets per trial, so summing them beats one random sample by only .02.
A17 E5b lossless variant (out/e5b.json): MAJ SUM .823 = SAT2 | ARB .727 |
 ALOHA2 .500; RELAY 1.0 under all. E5b-P1: SUM within .03 of .837 HOLDS,
 ARB within .03 of .700 HOLDS (.727), gap >= .10 FAILS narrowly (.096).
 E5b-P2 HOLDS (.500). Theory's one-shot table is quantitatively right.
A18 GPU acquired 07:05Z token 4db299a7987b; e2_evolve.py gained WJ_LOSSLESS switch (E6 physics, e6_ prefix, distinct seeds); E2 code path unchanged.
A19 E6 done 07:20Z, GPU released (token 4db299a7987b, comms 783). out/e6_*.json,
 e6_console.log, e6_summary.json, e6_reduce.py (= e2_reduce on e6 files;
 its RELAY/P-lines are for E2 and were ignored).
 MAJ held per seed: SUM .801/.576/.583/.553 (med .579); ARB .541/.563/.508/
 .569 (.552); ALOHA2 .494/.560/.551/.614 (.555).
 E6-P1 FAILS (median SUM-ARB .027). E6-P2 HOLDS (SUM seed 0 .801 > .74).
 E6-P3 HOLDS (that champion: .801 SUM -> .500 under SAT2, ALOHA2 and ARB).
 E6-P4 FAILS (ALOHA2 median .555 vs SUM .579).
 Own-operator advantage (mean): SUM +.104, ALOHA2 +.030, ARB +.017, versus
 <= +.014 in the lossy E2 physics. Other operator-specific champions: ARB
 seed 0 (.541 -> .503 under SUM), ALOHA2 seed 3 (.614 -> .467 under SUM, i.e.
 BELOW chance without erasure: its code needs collisions to be erased).
A20 Decompiled E6 SUM seed-0 champion (rule 0): EMIT := CNT2 + SENSE (only
 positive-cue sensors fire), PAY1 := 52, S0 := IN0_1 - 118: a presence vote
 counted by superposition with threshold 3 of 5. E6b plant VOTE with only
 that logic (e6b_vote.py -> out/e6b.json): SUM .878 [.833,.917], SAT2/ALOHA2/
 ARB exactly .500. Prediction: SUM within .03 of .837 FAILS on the point
 estimate (+.041) though the CI contains .837; the three .50s HOLD.
 Note on the first E6 arm: SUM seed 0 is the ONLY evolved champion (of 44 in
 E2+E6) above the ARB one-sample ceiling, n = 1.
A21 CORRECTION: clock times written by hand in PLAN (E5b 07:00Z, E6 07:04Z, E6b 07:25Z) and LOG (A18 07:05Z, A19 07:20Z) were my estimates, not date -u. Actual: E2 reduce at 06:52:15Z, date -u after A20 = 07:05:52Z. The plan-before-run ORDER is intact (each PLAN block was appended before its run command, visible in file order); only the wall-clock labels are wrong.
