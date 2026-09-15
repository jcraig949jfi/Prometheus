# Lane D journal (LINGUA: channels, codebooks, consequential symbols)

## 2026-09-14 iteration 1 -- D1 metered channel  [m1-5ab220e6]

- Booted 11:43 as the replacement for the lost D session (25c21d33). Worktree nestor-gw-d from the
  existing branch without -b, ff to 4cce561b5. Hello posted within 10 min. Substrate gw-sub-d on 6393.
- Ran: a 2-slot signal world. R in [0,256) is redrawn per tick; slot 1 is right iff a == R>>5, so 3 bits
  matter and 5 don't. The channel is one Lua EVALSHA per tick: it credits last tick's yield, charges
  alpha_int*bits atomically, and never delivers an unaffordable send. The receiver reads the Stream
  entry. A (1+32) hill climber evolves codes (k, enc, dec) under alpha*bits + beta*entries + delta*error
  over a 5 alpha x 2 beta x 3 seed grid at 2000 gens, and is compared with the exact analytic optimum
  (m* = 8,8,4,2,1). Hypothesis posted at 11:51 with P1-P6, before any run.
- Instrument held. The Lua and numpy settlements gave identical trace hashes on every honest audit
  episode, and conservation held. Cheat channels (free_unaffordable, undercharge) were detected 13/13
  where exercised, with 0 false alarms. The scramble probe's normalised drop was >= 0.935 on every
  eligible honest code; the LEAK cheat (slot 1 regenerates R from the shared seed) scored 0.0 and was
  flagged, and without the probe it would have sat on the front. At beta=0, alpha=0 the elites reach
  MI 2.74-2.82 bits and yield ~0.90.
- What died (KILL): P6 (max gap to optimum 0.69), P3-differ and P2b (MI with low bits 0.11 vs <=0.10).
  With decoder rent beta=0.01 the climber settles into silence (alpha 0.1/0.3) or 2-4 symbol codes
  (alpha 0). A 2000 -> 8000 gen check in the quick phase changed nothing. POST HOC, untested: one
  register moved to a new symbol gains <= 1/256 yield but pays beta = 0.01 of rent, so a single-mutation
  path out of silence is uphill whenever beta > 1/256. That is "evolution discovers silence" produced
  by rent plus local search, not by the cost function (the optimum is not silent there).
- Engineering: at 4096 envs Lua settles 1.92M msgs/s against 105M in numpy. At 1 env it runs 1.5k
  ticks/s, two round trips per tick (EVALSHA + XRANGE).
- Next (D1b): test the rent barrier. Predict escape when beta < 1/256 and a trap when beta > 1/256, and
  check a block-move mutation (one bucket at a time) as the positive control. Then D2 consequential
  symbols by ablation. Steal: E's archive (QD over codes instead of one climber) and B's
  one-semantic-cheat sensitivity floor for the conservation audit.

## 2026-09-14 iteration 2 -- D1b code-learner valleys  [m1-5ab220e6]

- Hypothesis on the bus before the run. It opened by correcting iteration 1: rent alone cannot explain
  the traps, because alpha=0.1, beta=0 was also trapped.
- Ran: an exhaustive single-move scan of the 24 D1 elites under exact cost, and an exact-cost (1+32)
  climber with acceptance threshold eps in {0,.01,.03,.1} from D1's start genomes (10 cells x 3 seeds x
  4000 gens). Rows c277e6e8b.
- Controls PASS: a planted encoder defect is found by the full scanner and MISSED by the skip_enc cheat
  scanner; a planted decoder defect is found by both; the clean m=8 code is not improvable; alpha=1.5
  held gap 0 at every eps.
- Died (KILL): H1 -- 8 of the 21 "valley" elites have an improving single move (all width cells, plus
  (0,0.01) seed 0). H2a -- the exact eps=0 climber escapes (0,0) 0/3, so D1's (0,0) gap was not
  sampling noise. H3 -- eps=0.01 escapes 0/3 in every rent cell. eps >= 0.03 behaves like "always take
  the best child" (identical results).
- Held: H2b (the beta>0 silent elites are true single-move optima) and H4 (the width cells stay
  trapped at eps=0).
- POST HOC, unscored (scratchpad script): with 1 enc + 1 dec change per child instead of 4 + 2, the
  exact climber reaches gap 0.000 3/3 in (0,0) against 0.055 bundled. The width cells (0.1,0) and
  (0.3,0) stop at k=1, m=2 under both operators, and the rent cells stay silent under both. So there
  are three traps: operator bundling (0,0), width valley (alpha>0, beta=0), and a rent valley that a
  small eps does not cross.
- Next: D1c. A symbol-split move (split one symbol's register set into a new symbol with a copied
  decoder entry: neutral on yield, costs beta + bits) should cross the rent and width valleys if the
  valley picture is right. Pre-register which cells it should fix. Or go on to D2 by ablation using
  the hand codes, which are already on the front.

## 2026-09-14 round 2 iteration 1 -- D1c operator unbundling (ANOM-1789415790377-0)  [m1-4f51cc32]

- Claimed ANOM-1789415790377-0 and posted the predicate on the bus before running. This is the
  prospective version of D1b's post hoc: exact cost, eps=0, 4000 gens, 10 FRESH run seeds, 10 cells,
  with three operators: BUNDLED 4enc+2dec, SINGLE 1enc+1dec, and a FROZEN cheat (0 moves).
- All 6 checks PASS (rows primordial/ledger/rows/D/D1c-operator-unbundling.jsonl, 301 rows, 116 s on 2 cores).
  - H1: SINGLE escapes (0,0) 10/10.
  - H2: BUNDLED escapes (0,0) 0/10, stuck at gap 0.055.
  - H3: SINGLE escapes the width cells (.1,0) and (.3,0) 0/10.
  - H4: SINGLE escapes the rent cells 0/10.
  - FROZEN escapes 0/100. alpha=1.5 escapes 10/10 under both real operators.
- Survives a fresh generation: the (0,0) trap is caused by the operator. The rent and width traps do not
  depend on the operator; neither real operator crosses them. The anomaly is RESOLVED, and a child
  anomaly is filed for the valleys.
- Next: the child anomaly's discriminator (a symbol-split move, pre-registered per cell), or the next OPEN anomaly.

## 2026-09-14 round 2 iteration 2 -- D2 fitness-gate blindness (ANOM-1789415790381-0)  [m1-4f51cc32]

- Claim: a one-semantic cheat leaves fitness exactly invariant when the state it corrupts cannot reach
  yield_reg. Tested on 40 worlds (E4 used 5), 65 genomes x E4's 8 seeds, 4 cheats vs honest, predicate
  posted first. Rows primordial/ledger/rows/D/D2-fitness-gate-blindness.jsonl, 4.3 s.
- Held: the H1 theorem direction (yield_reg not a lin dst -> gate passes, 27/27 worlds); H2 (E4 worlds
  1,2,4 not dst, 3,5 dst); H3 (w1 skip_lin fitness identical on every genome, so E4's cheat best
  1818 > 1287 there was search noise, not an easier world); H5 (untriggered envs never change charge);
  controls (honest repeat 0, trace hash never blind, label-shuffle null max 31 < 37).
- Died: H1 as registered (37/40). Worlds 14 and 27 pass with yield_reg a lin dst because the yield window
  (2048/65536) never fires; world 24 passes because the 0-clip absorbs 36 differing envs. H4 (29/40):
  POST HOC the registers that are not lin dsts stay fixed in 29/29 charge-invariant worlds and 0/11 others,
  because liveness couples charge back into action writes.
- Gate pass rates over 40 worlds: skip_lin 30, no_regime_flip 39, stoch_swap 25, fix_unaffordable 32.
  The fitness gate is not an oracle. RESOLVED; child anomaly: E4's QD is nondeterministic at a fixed seed.

## 2026-09-14 round 2 iteration 3 -- D3 w1 linear spread (ANOM-1789417951134-0, lane B's)  [m1-4f51cc32]

- Question: is B-R2-1's w1 held64 IQR 19.4 caused by int4 or by the world/search? Paired rerun of E10's closed
  condition on w1, run seeds 0-7, float (E7.G7) vs int4 (B's QLin), same RNG, Redis 6393. Predicate
  posted first. Rows primordial/ledger/rows/D/D3-w1-linear-spread.jsonl, 16 runs, about 9 min in two 600 s tasks.
- Verdict WORLD. Float IQR is 14.74 (>= 10) and int4 IQR is 8.98. The CI of the IQR ratio int4/float is
  [0.12, 4.04], so the spread is not quantization. Medians: float 59.2, int4 58.0.
- H3 held: the within-run SD of held64 across the top-16 elites (about 13) is at least the across-run SD
  (9-10), so choosing the top 16 by train fitness is the noise. H2 died: int4 train IQR is 8.1 (> 5).
  Oracles clean in both arms.
- Two ways the record was fooled. (1) E10's 4-seed float IQR of 5.6 understated w1's spread. (2) The same
  int4 code has IQR 19.4 under B's RNG family and 9.0 under mine, so an 8-seed w1 IQR is not a stable
  clause A threshold. Filed as a child anomaly.

## 2026-09-14 round 2 iteration 4 -- D4 QD sampler nondeterminism (ANOM-1789417965533-0, my D2 child)  [m1-4f51cc32]

- Reading the code: LuaArchive.sample draws parents with server-side ZRANDMEMBER, which no client seed
  controls. Predicate posted, then E4's QD loop rerun on worlds 1-5 (100x256, seed 41, Redis 6393):
  LUA twice; DET (seeded client sampler, copy-on-write subclass in cohorts/d) twice at s=0, once at s=1,
  and skip_lin at s=0. Rows primordial/ledger/rows/D/D4-qd-sampler-nondeterminism.jsonl, 202 s.
- All 4 checks PASS. H1: the LUA repeat archive differs in 5/5 worlds; w1 best is 1806 vs 1128 at the same
  seed in the honest world, which covers E4's 1818 vs 1287. H2: the DET repeat is bit-identical 5/5.
  H3: DET skip_lin reproduces the honest archive exactly in w1, w2, w4 and differs in w3, w5. Instrument:
  s=1 changes the archive 5/5.
- Being fooled: every LuaArchive-based result (E4, E8-E10, B-R2-1, D3) has run seeds that do not reproduce;
  "run seed" labels a server draw, not a stream. The spread across seeds is still a valid sample, but
  paired or re-run claims are not. Told E, the archive owner, and A.

## 2026-09-14 17:33 -- QUIESCE (test launch 1 over)  [m1-4f51cc32]

- Epochs 1-2: 4 anomalies RESOLVED (D1c, D2, D3, D4), 3 child anomalies filed (..4459 symbol-split valleys,
  ..5533 now resolved by D4, ..2053 unstable 8-seed IQR), 636 rows, 0 receipts, every predicate posted before
  its run. E landed LuaArchive(sampler_seed=) at 33038855e in answer to D4; C confirmed D4 on its own.
- Open for the next D session: child ..4459 (symbol-split move) and ..2053 (IQR sampling CI and clause A flip
  rate, which is now possible with seeded samplers). No task in hand at quiesce; no open claims.

## 2026-09-15 01:0x -- round 4 boot + D-R4-1 dev  [m1-646ed853]

- Booted on r4-d at b5f548c05 (ff from integration); warmup ok, pytest rc 0 (209 passed, 1 skipped); worker D live.
  Claimed ANOM-1789426590583-0 (QD archives never reach abstain). Predicate D-R4-1 posted (bus 1789448648486-0).
- Read-only census of G's saved M2 archives: cell 1056 (abstain row 32, mag 0) is occupied in 30/32 looked at, and top-1
  TRAIN often ties abstain exactly. "Never reaches" is false on these archives.
- Dev job (w1, w4 train8; rows D-R4-1-abstain-cell-reach-dev): instrument OK (top-16 mean reproduces 16/16, floor match,
  planted cheat fails 14/14, oracles clean). But the cell-1056 occupant is a TRAIN MIMIC: w1 r0 ties abstain on train
  (236.25) yet scores 46.2 vs 88.3 on HELD64; exact abstain on HELD in 1/14. Next: real insertion test of the all-zero
  genome into each restored archive (the anomaly's own discriminator), as a pre-run amendment.
- D-R4-1 RECORD (rows D-R4-1-abstain-cell-reach, dec8c18ef; 592 archives, 82 CPU-s via worker D). I1 top-16 reproduces
  592/592, I2 floor match 74/74, planted cheat fails 585/585, zero genome == abstain 592/592, oracles 74/74 clean.
  P1 PASS reach 585/592. P2 FAIL occupant exact-abstain on HELD 309/585 (143 train mimics). P3 FAIL 32/66. P4 FAIL
  zero survives 453/592, and all 139 losses are to an occupant strictly better on TRAIN (never a tie/worse).
- Reading: REFUTED as stated. Archives reach abstain (top-1 TRAIN >= abstain 583/592); the HELD64 deficit is train-seed
  overfitting of the selected elites + the top-16 mean readout (top-16 below abstain 66/74 cells; top-1 >= 30/74).
  w7 train8 HELD: top-1 = occupant = abstain 189.19 exactly, baseline top-16 mean 174.14. Child anomaly for G/A.
- ANOM-..0583 RESOLVED REFUTED (--exp D-R4-1-abstain-cell-reach, pushed fe1694c74). Child anomaly filed: M2 readout
  (top-16 mean by TRAIN) below its own archive's abstain-grade elite; told A and G (bus 1789448985956-0).
- Claimed ANOM-..2053 (8-seed IQR). D-R4-2 predicate posted (bus 1789449122570-0): float_w1, int4_w1, float_w13 x RNG
  families 4200/2101/3303/5501 x 8 seeded run seeds at M2 budget; family 4200 float must reproduce G's M2 16/16.
  Dev (gens 20) caught two analyse bugs (8-of-4 draw; screen read the four-policy floor, not gate_in 166.47): fixed
  before the record run. Worker restarted twice (the child caches imported modules; no reload).
- D-R4-2 record job 4dd87eded458 running (96 runs, ~33 s each): family 4200 float_w1 reproduces G's M2 held64 7/7 so
  far, oracles clean on float_w1. Seeded archives are reproducible across processes; that half of ..2053 holds.
- Claimed ANOM-..4459 (symbol-split valleys). D-R4-3 predicate posted (bus 1789449431422-0) BEFORE any scored run:
  P1 neutral split crosses none of the 6 D1c trapped cells (eps=0: +beta, no yield; width cells saturated);
  P2 split+re-point macro crosses all 6. Local smoke only (no scored rows): split yield-neutral 83/512, D1c single
  reproduced exactly. Record job 24f2f1a3dcf3 queued behind D-R4-2.
- EPOCH 1 stop paused D-R4-2 (34 rows); D-R4-3 and D-R4-4 ran meanwhile. Pushed 5b5d7595b with worker parked per A's
  workaround (SET stop -> stopped -> ops.push -> DEL stop).
- ANOM-..4459 RESOLVED (D-R4-3): neutral split 0/10 in all 6 trapped cells (P1 PASS); macro crosses (.1,.01) 5/10,
  (.3,0) 1/10 (P2 FAIL), gaps cut 3-10x in 3 cells; instrument 8/8; frozen 1/10 at alpha=1.5 = init already optimal
  (disclosed). Child filed: high-alpha cells gap identical under every op (bit split = half mass vs 1/8 needed).
- ANOM-..9514 RESOLVED REFUTED (D-R4-4): 0 verdict flips under top1/val16/val1 in all 4 variants; only the HELD64 leak
  flips. Medians move, CI lows do not. w13 denominator readout-dependent (16.25/23.06/14.68/22.05); told B via ALL.
- Open: D-R4-2 (claimed ..2053) paused, ~60 runs left; resume after quiesce. Covers B's 1789450127495-0.
- D-R4-2 finished across 4 segments (epoch pauses; F9 resumed cleanly), rows pushed 7697a12a5 with worker parked.
  I: family 4200 reproduces G's M2 16/16; oracles clean; shifted-family cheat detected (p <= .0012).
  P1 PASS (float_w1 8-of-32 IQR [4.1,17.4]), P2 PASS (int4 family IQR 2.9x), P3 FAIL as registered (int4 Kruskal
  .046; floats .49/.26; not Holm-significant), P4 PASS (r2 rule 81% of draws), P5 FAIL: w13 train128 SURVIVED in
  13.6% of draws, 1/4 families (4200 = G's). ANOM-..2053 RESOLVED; B's ..7495 claimed+RESOLVED; child filed (w13
  survival rests on one family). Operator ruling 15: B's w13 claims invalidated; E fixes readout. My note: readout
  fix will not stabilise w13; run-seed n will.
- QUIESCE state: no open claims; worker D idle; children open for next D: high-alpha valleys, w13 survival.

## Round 5 pilot (Nestor-D[m1-181e5997], worktree nestor-r5-d)

- Boot at ~T+19 (clock pm:round:r5 live): ff to eca1a725b, hello took lane D from dead tag m1-646ed853, warmup ok,
  suite 384 passed rc 0, worker D serving. Queue: priority 1 parent ..7495 RESOLVED; child ..6045 OPEN -> claimed.
  No OPEN sham-control, B2 or GPU-crossover anomalies on the queue.
- ..6045's first discriminator (pooled 32) was already answered by G R16: top1_train CI [170.95, 188.56] > 166.47.
  Legacy top-16 pooled CI low is 164.70 (seen before predicate; retired readout). The claim itself (rests on 4200)
  is untested: predicate D-R5-1 posted (bus 1789471125531-0), leave-one-family-out on G-R16 rows, zero QD.
  Code aa38557db; job 1cb7bd63372a PILOT wall 120 / cpu 120. The 5th fresh family (32 QD runs, ~732 s QD wall
  from D-R4-2) is not run: PRODUCTION_CANDIDATE.
- D-R5-1 RECORD (job 1cb7bd63372a, 11.8 s wall, rows 930609f36): I1 PASS (pooled CI [170.9531, 188.5625] == G).
  P1 TRUE: leave-4200-out (runs_total 24, rng_family_count 3, runs_per_family 8) median 176.73 CI [169.02, 186.23]
  > 166.47. P2 4/4 LOO pools survive (CI lows 172.27/168.22/169.02/170.17). P3 2/4 retired 8-run blocks
  (4200, 3303). P4 96.5% of stratified resamples. Decision REFUTED: w13 SURVIVED does not rest on family 4200 under
  top1_train. Readout note: legacy top-16 pooled CI low 164.60 (fails), LOO 2/4, strat 41.3% -- the one-family
  dependence was a property of the retired readout, and the w13 margin is 2.55 above floor at leave-4200-out.
- Receipt D-R5-1 filed (bus 1789471347601-0, guard accepted), ANOM-..6045 REFUTED on the bus, result 1789471321153-0,
  PRODUCTION_CANDIDATE 1789471299163-0 (5th family, 32 QD runs, ~732 s QD wall). Pushed a4641ceaf. ~T+27.
- Queue after ..6045: no OPEN sham-control or B2 anomalies. E handed D a GPU-1 crossover reversal as a NOTE only
  (1789471230754-0: warp loses at 65536, h2d 34 ms of 37 ms); filed it on the queue citing E, to claim as priority 4.
- Claimed ANOM-..1162 (GPU-1 reversal at 65536). Code read: bench_cell times h2d_s ONCE (first load_actions on a fresh
  encounter = alloc + pageable copy) while the kernel is a median of reps. Predicate D-R5-2 posted (1789471566566-0)
  before any h2d measurement: cold vs 11 warm reps of alloc / assign / pinned at n 16384..131072, readback oracle,
  REFUTED iff E kernel 3.295 ms + warm alloc median < numba_t8 10.355 ms at 65536. Arbiter runs from nestor-r5-e
  (two gpuq serve processes seen, one on H:\Python312): E must ff before D's job can import.
- Operator 20 (PILOT cpu_budget_s 1200 -> 2400; walls unchanged): HEAD == integration incl. d64580db2; worker D
  restarted at an idle boundary. Asked E (1789471620448-0) to ff nestor-r5-e so the arbiter can import D-R5-2;
  flagged a stale second gpu-arbiter consumer (m1-2adb547f, H:/Python312). GPU submit waits on E's checkout.
- CORRECTION (A 1789471692590-0): ONE gpuq arbiter, not two -- pid 25632 (gw-venv launcher) and its H:/Python312 child
  25488 are the same process chain; the idle consumer m1-2adb547f was a stale registration (0 pending), removed by A.
  E ff'd nestor-r5-e to 3a6beef19 (1789471703047-0). D-R5-2 submitted to the GPU queue as preregistered: job 8b801e1a99fe.
- D-R5-2 RECORD (gpu job 8b801e1a99fe, 7.3 s, lease held, 16/16 VALID, readback PASS 4/4; rows 0deee846c on E's
  branch). 65536: cold 5.59 / alloc 5.13 / assign 2.87 / pinned 1.80 ms; ms per MiB flat 12..96 MiB, no knee.
  Preregistered rule met: E kernel 3.295 + warm alloc 5.13 = 8.43 < numba_t8 10.355 -> REFUTED.
  My mechanism was WRONG: cold/warm 1.1, cold 5.59 not 33.97 ms; E's 34 ms is unreproduced, cause unidentified.
  Receipt + resolve wait on 0deee846c reaching integration (asked E, result 1789471... posted).
- ~T+55: E pushed D-R5-2 rows as 269a55d84 (rebased from 0deee846c) and withdrew the 65536 reversal (1789472674732-0),
  naming the defect: warp wall = kernel median + ONE h2d draw, so ratios are not like-for-like at any n.
  ANOM-..1162 resolved REFUTED (mechanism not confirmed). Receipt filed with the envelope passed explicitly (GPU jobs
  live on pm:gpu:jobs, so the guard cannot look it up on pm:jobs:D). Queue: no OPEN anomalies left for D.
- CLOSE ~T+95 (no new work before NO_NEW_WORK): queue has 0 OPEN D-priority anomalies; worker D idle, no open claims.
  R5 D ledger: 2 claims, 2 receipts (D-R5-1 1789471347601-0, D-R5-2 1789473124768-0), 2 anomalies REFUTED
  (..6045 w13 not a one-family artifact under top1_train; ..1162 GPU-1 reversal gone, mechanism unconfirmed),
  1 PRODUCTION_CANDIDATE (5th RNG family, 32 QD runs, 1789471299163-0), 0 QD runs, ~19 s total compute.
  Own error metabolised: D's cold-copy mechanism for ..1162 was wrong (cold 5.59 ms, not 33.97 ms).

## Round 6 PRODUCTION (Nestor-D[m1-bff769b2], worktree nestor-r6-d)

- Boot ~T+19 (clock pm:round:r6 live 11:00): ff to integration, warmup ok, suite 437 passed / 1 skipped rc 0, worker D
  serving (fresh process, so no stale-module reload needed). A cleared the stale r5 stop flags (1789485113451-0).
- Item 2 first (pure filing, 0 compute): anomaly 1789485427773-0 -- B-R5-1's 3/32 below-floor runs are all family 3303
  (3303|2 165.88, |6 162.00, |7 161.61 vs floor 166.47); the other 5 runs of 3303 sit 16-44 above. Not explained.
- Item 1: D-R6-1 code 6a498d6db (+ test, 5 passed rc 0), predicate D-R6-1-b-r5-1-family-loo bus 1789485461951-0,
  ref refs/pm/pred pinned. Rule: ROBUST iff progress CI low > 0.95 in 4/4 held-out pools. check_r4 refuses 24-run
  pools CANDIDATE_N by design, so the LOO CI goes through check_r4's formula + median_ci; refusal recorded per pool.
- Job 38c04bba9aeb was granted a CPU token at 11:34 but consumed by the STALE round 5 D worker (nestor-r5-d, pids
  25004/26160, consumer m1-181e5997, alive since 07:28): status error in 0.11 s, 0 rows (r5 checkout lacks the module).
  My wait loop watched only pm:events + the rows file and missed pm:jobs:D:done: ~44 min lost (submit 11:17:52,
  error 11:34:17, found 12:00, resubmit 01f9789d6e6f 12:01:34 = T+62). Own error: watch the
  done stream for every terminal status. Killed exactly those 2 pids (cwd checked); told A 1789488081865-0.
  Resubmitted the identical job (execution error, not a refusal); predicate unchanged.
- D-R6-1 RECORD (job 01f9789d6e6f ok, 0.27 s wall, 0 QD, worker rows commit e82ada8e8): decision ROBUST.
  I1 exact (32-run pool via check_r4 PASS 1.5914 CI [1.1389, 1.8271]); controls ok (one-family-carries 0/4,
  all-progress-2 4/4); source-rows oracle clean (B rows byte-equal 4e69568e8). LOO CI low: -4200 0.9964, -2101 1.1022,
  -3303 1.1568, -5501 1.2366 -> 4/4 > 0.95. Thin: leave-4200-out clears by 0.046. check_r4 refused all 4 pools
  CANDIDATE_N as predicted. Reported only: matched-baseline LOO 4/4 > 1.08 (leave-4200-out 2.35: without 4200 the
  baseline median drops to 176.73); 8-run blocks CI low 3303 -0.256, 5501 0.688. Item 3 discriminator NOT triggered.
  Anomaly ..7773 (3303 bimodal) stays OPEN: the PASS does not depend on 3303, the observation is unexplained.
- Receipt D-R6-1 filed 1789488540808-0 (guard 10/10 OK, status NULL: robustness read, decision ROBUST), rows 4660b347c.
- Item 3 -> OPEN queue (D-R6-1 ROBUST, no discriminator owed). Claimed ANOM-..7943 (skip-odd brain cheat blind on 3
  of 16 int2 w4 elites). D-R6-2 code + test (4 passed rc 0): zero QD, B-R2-4 rs0 committed top_hex; census of EVERY
  live row of the cheat trajectory vs E7's 256-row sample. SAMPLE_MISS vs GENUINE_IGNORE per blind elite; I1 = B's
  recorded oracle (13/709/4096, honest 0) reproduced; controls planted_zero_odd + honest_census.
- D-R6-2 RECORD (job 4f11a90219d2 ok, 0.71 s, 0 QD, predicate 1789488790812-0): decision MIXED. I1 exact (cheat
  13/709/4096, honest 0, fused==numpy 16/16, sample replay equal); controls ok. Blind elites 0,1: 0 flips in 512 live
  HELD8 rows (GENUINE_IGNORE on HELD8); elite 2: 2 flips in 512 (SAMPLE_MISS). The anomaly's per-elite list
  0,0,1,94,... == separate per-elite oracle calls exactly; its 13/16 == the joint call: elite 2's 2 rows are hit by one
  sample stream and missed by the other. Reported: held64 changes under brain_stride 2 for 16/16 elites (0 and 1
  107.64/106.59 -> 107.75), so "ignore" is HELD8-local, not a brain property; odd |W| mass blind .56/.52/.56 vs caught
  .49-.65 (not zero weights, as filed).
- Receipt D-R6-2 filed 1789488889783-0 (guard 10/10 OK, status NULL, decision MIXED), rows 9927ff9b4; ANOM-..7943 RESOLVED; child anomaly filed (HELD8 coverage).
- Loop iteration 1 (12:15, T+76): claimed child ANOM-..9775 (1789488929775-0, HELD8 coverage). D-R6-3 code + test (4 passed rc 0), 0 QD:
  numpy honest vs cheat charge per HELD64 seed x any-flip census on the cheat trajectory; COVERAGE / PATH_DISAGREE /
  NOT_COVERAGE; I1 = numpy == fused (stride 1 and 2) and D-R6-2 held64 reproduced; control planted_zero_odd.
  Memory saved: stale prior-round worker steals jobs; watch pm:jobs:<L>:done.
- D-R6-3 RECORD (job 86136d5a92eb ok, 0.13 s, 0 QD, predicate 1789489073092-0): decision COVERAGE. I1 4/4 (numpy ==
  fused stride 1 and 2; D-R6-2 held64 reproduced); control zero-odd 0/0; PATH_DISAGREE none. Elite 0: charge differs on
  2/64 seeds (7 flips), elite 1: 6/64 (71 flips), 0 of them in HELD8; the cheat RAISES their charge (-7, -74). Elite 2:
  18 seeds, 2 in HELD8. Caught elites 28-54 seeds. Every charge-diff seed has >= 1 flip. The skip-odd oracle's HELD8
  blindness on elites 0,1 is seed coverage: the cheat has power, HELD8 never reaches it.
- Receipt D-R6-3 filed 1789489146880-0 (guard 10/10, status NULL, COVERAGE), rows 55c35e49d; ANOM-..9775 RESOLVED; ..7943 chain closed.
- Loop iteration 2 (12:23): claimed ANOM-..9541 (HELD w13 train8: gate 166.47 held vs baseline 149.08). Committed M2
  legacy rows already show top-16 TRAIN8 193-220 > gate 183.625 in 8/8 runs (seen before predicate). D-R6-4 code +
  test (3 passed rc 0), 0 QD: re-read G's 8 saved M2 archives, every elite on TRAIN8 + HELD64; gate as a float linear
  genome must reproduce the floor rows; SEARCH_SHORT / SELECTION / OVERFIT_ONLY / MIXED. w13 train8 is position 20
  in G's R6 screen order; this reads round 4 archives only, no overlap with G's runs.
- D-R6-4 RECORD (job e304812b3a6e ok, 0.40 s, 0 QD, predicate 1789489433361-0): decision OVERFIT_ONLY. I1 7/7 (gate as
  float linear genome == floor rows 183.625 / 166.46875, floors.gate_scores agrees, abstain 159.0, archive fitness
  recount 8/8); controls planted gate 8/8, planted abstain 0/8. top1 TRAIN8 197.5-233.75 > 183.625 in 8/8 (not
  search). Archives with >= 1 elite at HELD64 >= 166.47: 2/8 (runs 2, 5: 7 and 2 elites; top1 is rank 1 / near,
  held 182.84 / 172.03). Other 6 runs: best elite of ~488 reaches 157.9-163.2, none at the gate. The search overfits
  TRAIN8; it is not a selection miss. Caveat: 8 runs, one RNG stream (round 4 v1 = family 4200).
