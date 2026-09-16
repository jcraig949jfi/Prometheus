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
- Receipt D-R6-4 filed 1789489506239-0 (guard 10/10, status NULL, OVERFIT_ONLY), rows 4f4525fdf; ANOM-..9541 RESOLVED.
- Loop iteration 3 (12:27): siblings sized -- only w7 train8 has an R16 gate row (thr 2, dir -1, act 7,7,7; gate_train
  1910.875, held 1482.5); w1/w34 have none yet (w1 in G's floor remainder). Legacy top-16 TRAIN8 on w7 is 734-1075,
  far below the gate (seen before predicate). Claimed ANOM-..9534. D-R6-4 functions parameterised (defaults unchanged,
  test), D-R6-5 = same reader on w7 (6 passed rc 0). Harness module r6_4 edited: the worker reloads by fingerprint.
- D-R6-5 job d6eecdc3a3c8 ERROR (0 rows, job_end aborted row 80292450a): TypeError runs_from_rows() takes 1
  positional argument -- the warm child kept the pre-edit r6_4 module; F-R6-2 fingerprints only the fn module (r6_5,
  first load), not its imports. My iteration-3 note "the worker reloads by fingerprint" was WRONG for imported modules.
  Restarted worker D (pids 26800/29484, 12:28:49); resubmitted the identical job; told A,F 1789489737094-0.
  Rule for myself: after editing ANY harness module, restart the worker, even when the fn module is new.
- D-R6-5 RECORD (job a1b1ea707084 ok on the restarted worker, 0.86 s, 0 QD, predicate 1789489653073-0): SEARCH_SHORT.
  I1 7/7 (gate genome 1910.875 / 1482.5 == floors; abstain 189.1875; recount 8/8); controls gate 8/8, abstain 0/8.
  reach 0/8, held 0/8: no elite in any of 8 archives (~512-538 each) beats the gate on TRAIN8 or reaches its HELD64
  (best 217-332). Reported: top1 TRAIN8 == 756.75 in 7/8 runs (run 7: 1399.1), top1 HELD64 == abstain 189.19 in 3 --
  the search stalls on one plateau. Opposite of w13 (OVERFIT_ONLY): w7's HELD is a real search shortfall.
  Rows file also holds the aborted job_end row of d6eecdc3a3c8; the receipt cites the file.
- Receipt D-R6-5 filed 1789489833767-0 (guard 10/10, status NULL, SEARCH_SHORT), rows 98f7f2efa; ANOM-..9534 RESOLVED. A ruling 1789489756428-0: restart worker after any harness edit (done 12:28:49).
- Loop iteration 4 (12:32): last three HELD siblings (w1 t8, w1 t128, w34 t8) have no R16 gate row; G's round 4 stage 1
  suite_cheap rows carry their gates (gate_held64 == worlds_r4 == anomaly text). Claimed ANOM-..9536/..9538/..9539.
  D-R6-6 = D-R6-4 reader over the 3 cells, one row, per-cell decision, thresholds scaled to runs found (n = 8 gives
  5/3); new module only, r6_4 untouched since the restart. Test 3 passed rc 0. F filed the import-closure PC 1789489827401-0.
- D-R6-6 job 4fe3ba1d1c3b ERROR (0 rows, job_end aborted row 2e31ed755): ValueError reshape into (344) on w1 train128.
  MY index bug: G-R4-3-stage2 lists 16 w1 train128 run rows (8 float linear 344 B + 8 input-invariant learner
  archives g-r4-inv 384 B, no family); R4.runs_from_rows keeps the last row per run seed, so it picked the learner
  archives. No cell result was emitted. Fix in r6_6 only (linear_runs: family linear AND genome_bytes == G7 glen; glen
  mismatch -> INDETERMINATE, not a crash); test asserts 8 linear runs and no g-r4-inv. Worker restarted 12:34:30
  (A ruling). New predicate D-R6-6b; the aborted row stays in the D-R6-6 rows file.
- Receipt D-R6-6 filed 1789490157101-0: status INDETERMINATE (job aborted, index bug, no cell value seen), rows 2e31ed755.
  job() now takes exp / predicate_id so D-R6-6b runs under its own predicate and rows file (the aborted row predates
  any new predicate). Tests 10 passed rc 0; worker restarted again after this edit (A ruling).
- D-R6-6b RECORD (job 0eeef9dc00e9 ok, 3.1 s, 0 QD, predicate 1789490222662-0): I1 and both controls clean in all 3 cells.
  w1 train128: SEARCH_SHORT (reach 0/8: top1 TRAIN128 160.3-179.1 vs gate 271.8; held 0/8, best HELD64 71-98 vs 170.5).
  w34 train8: OVERFIT_ONLY (reach 8/8: top1 TRAIN8 79.8-182.8 vs gate 76.5; held 0/8, best HELD64 230-277 vs 289.3;
  top1 HELD64 is 0.0 in 3 runs, below the 273.3 abstain value in all 8).
  w1 train8: OVERFIT_ONLY by the rule, but only by TIES: top1 TRAIN8 == the gate's 236.25 exactly in 5/8 (reach uses
  >=), 0 elites strictly above it in any archive; best HELD64 46-87 vs 170.5. Under strict > it would read SEARCH_SHORT.
  Reported, not re-judged. Five HELD cells now read: w13 t8 OVERFIT, w7 t8 SEARCH_SHORT, w1 t8 OVERFIT (tie),
  w1 t128 SEARCH_SHORT, w34 t8 OVERFIT. None is a selection miss: no archive hid a gate-quality policy.
- Receipt D-R6-6b filed 1789490299859-0 (guard 10/10, status NULL), rows a9320d655; ANOM ..9536/..9538/..9539 RESOLVED. All 5 HELD anomalies closed (2 SEARCH_SHORT, 3 OVERFIT_ONLY incl. w1 t8 by ties).
- Loop iteration 5 (12:41): queue now 12 OPEN = 10 old round 1-2 C/E observations, family 3303 (stays OPEN) and D's
  own D1 valleys ANOM-..2892 (claimed). D-R6-7 = exact 1-step split census on every trapped D-R4-3 code (replayed,
  must reproduce the committed rows): one-bit vs three-bit (1/8 mass) splits x 8 decoder values; MASS_BARRIER /
  DEEPER_VALLEY / SAMPLING_MISS / MIXED. Controls: analytic optimum has 0 improving moves; one-symbol-short hand code
  has >= 1. Test 4 passed rc 0; worker restarted for the new module.
- D-R6-7 predicate 1789490546910-0, job 992e5472ae64 queued 12:42. A routed C-R6-AP-01 (anti-prior arm, sealed prior
  0.10) -> PASS; filed as anomaly 1789490583451-0 (cell at 75-91 of 400 gens scores above the control; both arms only
  ~7% above the random-bits mean). Not explained; minimum discriminator = paired read of C's committed per-run rows.
- D-R6-7 job 992e5472ae64 ok (128.8 s, 90 replays, rows c55744cdc); reading next. Claimed ANOM-..3451 (C-R6-AP-01
  anti-prior PASS). D-R6-8 code + test (4 passed rc 0): paired read of C's committed per-run rows on the same
  (family, run seed): t = control train > cell train, h = control held > cell held; TRAIN_NOT_HELD / BOTH_GAIN /
  NO_TRAIN_GAIN / MIXED; self_pair binding, shuffled pairing reported. Seen before predicate: C's summary and one
  control run row (train 2423879.75, held 2253685.20). Worker restarted for the new module.
- D-R6-7 RECORD: MASS_BARRIER. I1 90/90 replays exact, hand codes cost c_opt; controls ok (optimum 0 improving; one
  symbol short 45/45/7 three-bit). One-bit splits improve 0/89 trapped codes (best +0.035..+0.185), three-bit 89/89
  (best -0.0125..-0.0775). Caveat: one census signature per cell -> 3 distinct codes, 3/3. Receipt 1789490774638-0,
  ANOM-..2892 RESOLVED. D-R6-8 predicate + job submitted (background).
- D-R6-8 RECORD (job 7d72f1d38ae9 ok, 0 QD, predicate 1789490790710-0): MIXED. I1 6/6, self_pair clean. Control train >
  cell train 32/32 pairs, control held > cell held 17/32 (TRAIN_NOT_HELD needed <= 16: one pair short). Shuffled
  pairing t 31 h 17. Spearman train-held control -0.04. Receipt 1789490865360-0. ANOM-..3451 left OPEN (rule did not
  return the mechanism; not explained away).
- Loop iteration 6 (12:50): sized the old queue; cheapest aimed discriminator is ANOM-..1532 (tt_feat w4: train
  saturates by gen 14, held64 does not). Claimed. D-R6-9 = E9's loop on E9's mutation stream with a SEEDED sampler
  (E9's was UNSEEDED, so its rows are references only), run seeds 0..7, checkpoints 14/25/50/100/200 inside one
  trajectory each (top-16 readout as filed). I1: exact top-16 fitness recount at every checkpoint + repeat of run
  seed 0 identical. Cost ~9 x 200 gens at batch 128 (E9: ~5 s per run). Test 5 passed rc 0; worker restarted.
- D-R6-9 RECORD (job 83366bc5f506 ok, 53.7 s, 148 CPU-s, 9 trajectories, predicate 1789491108407-0): HELD_KEEPS_RISING.
  I1 3/3 (exact top-16 recount at every checkpoint; run seed 0 repeat identical). Train gain 14->200 = median 6.9% of
  final, held64 gain = 16.4% (d 0.096 >= 0.05); held64 rises 50->200 in 7/8. Medians reproduce the anomaly's two
  references with a seeded sampler: gen 14 train 133.35 / held 59.73 (C-R2-01 133.3 / 59.9), gen 200 143.42 / 78.90
  (E9 143.9 / 79.2). Held64 per run is noisy (rs 3: 56.2 -> 59.3; rs 6: 43.8 -> 78.4).
- Receipt D-R6-9 filed 1789491225180-0 (guard 10/10, status NULL, HELD_KEEPS_RISING), rows c40173d9c; ANOM-..1532 RESOLVED.
- Loop iteration 7 (12:55): next cheapest aimed item ANOM-..0379 (E2b FAKEFIT beat the 20-null max in 1/3 reps).
  Claimed. D-R6-10 = E2b's own functions, 100 null worlds (seeds 100..199, E2b's 20 included), 10 FAKEFIT reps
  (fresh seeds 4000..4009), honest x3 (positive control: beats 100-null max >= 2/3), filler x1 (founders 0).
  NULL_HOLDS e == 0 / RARE 1-2 / CHEAT_LEAKS >= 3; exact CP CI reported. Cost uncertain (branch_points evaluates
  100k reference genomes + cell baselines per world): per-rep rows + envelope 2400 s wall, 6000 CPU-s. Test 3 passed.
- D-R6-10 RECORD (job 6e2987dba762 ok, 690.8 s wall, 676.5 CPU-s, 14 evolve runs, predicate 1789491427890-0): NULL_HOLDS.
  I1 3/3: honest beats the 100-null max 3/3 (0.69-0.87 vs 0.10-0.14), filler founders 0, FAKEFIT rates defined 10/10.
  FAKEFIT exceeds the 100-null max 0/10 (CP CI [0, 0.31]) and E2b's 20-null max 0/10; rates 0.0036-0.0332, percentiles
  0.00-0.76 among own nulls. E2b's 6.5% FAKEFIT rate lies above all 10 here; the 20-null max itself swings
  0.036-0.073 across reps. Cost: branch_points 24-91 s per rep (the 100 nulls), evolve ~1.5 s.
- Receipt D-R6-10 filed 1789492198616-0 (guard 10/10, status NULL, NULL_HOLDS), rows 988ee3745; ANOM-..0379 RESOLVED.
- Loop iteration 8 (13:11): claimed ANOM-..0372 (tt_digits w3 held-out swings with the run RNG). D-R6-11 = E7b setup
  with the run RNG split: init stream (first generation only) x mutation stream (+ seeded sampler), 4 x 4 grid +
  repeat of (0,0), ~17 x 31 s. NO_SWING (range < 20) / INIT_DOMINATES (vi >= 2 vm) / MUTATION_DOMINATES / BOTH.
  I1: 16 cells, exact top-16 recount, (0,0) repeat identical. Test 4 passed rc 0; worker restarted.
- D-R6-11 RECORD (job 9f936a06ee53 ok, 238.8 s wall, 668 CPU-s, 17 runs, predicate 1789492352243-0): INIT_DOMINATES,
  BARELY. I1 3/3 (16 cells, exact recount, (0,0) repeat identical). Held64 grid range 38.8 (55.4-94.2): the swing
  reproduces. var(init means) 47.8 vs 2 x var(mutation means) 46.0 -> clears by 1.8. Interaction residual variance
  122.4 exceeds both main effects: most of the spread is init x mutation combination / run noise, not one stream.
  Row means (init) 63.2 / 75.4 / 73.0 / 79.4; column means (mutation) 79.7 / 70.0 / 72.1 / 69.1. Train 21.6-29.2.
- Receipt D-R6-11 filed 1789492661706-0 (guard 10/10, status NULL, INIT_DOMINATES by 1.76, interaction 122.4 > both main effects), rows e4a4dfefd; ANOM-..0372 RESOLVED.
- CLOSE 13:20 (T+140, no new work started after D-R6-11; NO_NEW_WORK 14:20). R6 D ledger: 12 receipts (D-R6-1..11 +
  D-R6-6b; D-R6-6 INDETERMINATE), items 1-3 done (B-R5-1 LOO ROBUST; 3303 filed OPEN; queue worked), 11 anomalies
  RESOLVED, 2 filed records left OPEN (3303, C-R6-AP-01). close_sweep r6: 0 unreceipted D rows. Worker D stopped by D.
  Own errors: done-stream not watched (44 min), wrong times to A (corrected), fingerprint over-claim (1 resubmit),
  run-index bug (1 INDETERMINATE). Not started for time: E8 closed-vs-open re-score (0 QD, new reader).

## Round 7 (ANOMALY HUNTERS, 12 h overnight PRODUCTION), Nestor-D[m1-188fc46f], worktree nestor-r7-d

- BOOT 17:52 (T+15): ff to ab1787d14; comms boot m1-188fc46f; warmup rc 0; suite 568 passed 1 skipped rc 0 (sparse
  worktree); worker pid 25220 registered (repo nestor-r7-d, round r7); bus hello; inbox read (not piped).
- Claim ANOM-1789490583451-0 -> TAKEN by D[m1-bff769b2] (D's own r6 session). pm:claims has no round namespace and no
  TTL: every earlier ANOM claim sits under an older D tag. Not deleted (no hand residue clearing); worked as lane D's
  claim and D-R7-1 claimed by exp id. Defect for the final (cross-round claim residue, same class as D20).
- Item 1: D-R7-1 (primordial/cohorts/d/r7_1_ap01_gens_sweep.py + test 8 passed rc 0). C's control streams run to 400
  with C's exact top1_train readout at g 1/10/25/50/100/200/400 and at m = paired cell gens_done; C's cell streams
  replayed at gens_done. Rule NO_SEARCH_SIGNAL / STREAM_DRAW / SATURATED / BAR_ABSORBS_GAIN / MIXED; I1 = exact
  reproduction of all 64 C rows + bar; binding control checkpoint == stopped run. Seen before predicate: gens_done
  75-91 and loop CPU (TTL binds on generations), D-R6-8 counts; no-rows smoke: cell (4200,0) replay == C row at default
  and 1 BLAS thread; dev trajectory (4200,0) g400 == C control row, 18.8 CPU-s -> job ~720 CPU-s, checkpointable.
- D-R7-1 predicate 1789509676377-0 (pinned 92df341ef), admission dry-run ok, job e2a0a3510473 queued 17:57:56.
  NOT STARTED by 18:05: worker D waiting_cpu, E re-took slot 1 x7 in a row (~40 s jobs) + G slot 0. broker.acquire is
  SET NX with no queue (SWARM_R7 O4 says FIFO). Note to A,F 1789509934842-0; D does not touch tokens.
- Item 2 while waiting: D-R7-2 (r7_2_fam3303_same_stream.py + test 5 passed rc 0; first test run 5 FAILED on my own
  dict(**tuple-keys) bug in the planted controls, fixed before commit). Zero QD. B-R5-1 runs share G's float-baseline
  streams (seeds_of: mutation [F,rs,13,128], sampler [F+1,...]; keys 32/32, sampler seeds equal). STREAM axis: are
  3303|2/6/7's same-stream BASELINE runs in the bottom 8 of 32; OBS axis: control_obs_use of the low runs. No 3303
  baseline value or obs-use value read before the predicate. Admission dry-run ok.
- A ruling 1789509956511-0 on the starvation: D22, no mid-round broker change, bounded by E's O8 (~18:25); D logs wait
  per job. Both D jobs were fingerprinted at submit, so the wait goes into each receipt from the pm:jobs:D entry ts and
  the done record's `started` (no module edit). D-R7-2 predicate 1789509988068-0 (pinned 1a66d97dd), job f564042e7a5b
  queued 18:06; claimed ANOM-..7773 + exp id.
- Item 3 (GPU exactness ANOM-..1534) NOT run: nv.gpuq children run with cwd/PYTHONPATH = the arbiter's repo
  (nestor-r7-e, HEAD 1d344021d, lacks D's commits; E has a live O8 writer). A D GPU job would run from E's tree. Not
  claimed. Minimum loci-dump discriminator posted to A,E for a PC/OPEN item (one lease segment). E's journal shows no
  loci dump planned.
- Item 4 triage while starved (18:09, worker D waiting_cpu, lag 2): ANOM-..0370 (closed vs open loop, 8 vs 128 train
  seeds) -- E6/E6b/E8 rows carry no elites/genome file paths, so R6 D's "0-QD re-score from committed genomes" depends on
  whether the genome fields are inline; checked by type only. Items 1-2 stay first when a token frees.
  Result: closed_genomes/open_genomes are int counts in E6, E6b and E8 -> no committed genomes, no 0-QD re-score;
  ANOM-..0370 needs new QD (not started; after items 1-2, sized against the clock).
- D-R7-1 RECORD (job e2a0a3510473 ok, 66 rows fe9650a6c, 472.8 s wall, 764 CPU-s; queued 17:57:56, started 18:26:42 ->
  token wait 1526 s = 25.4 min, D22): decision SATURATED. I1 7/7 (all 32 control rows at g400 and all 32 cell replays
  reproduce C exactly, bar recomputed == 2226419.05, elite recounts clean); control checkpoint_equals_stopped_run
  identical (4200|0 at m=84). H1 2150006 < B; Hm 2237328 >= B; s = 18/32 runs with held(400) > held(m) (<= 21).
  Reported: held medians g1 2150006 / g10 2180261 / g25 2203280 / g50 2224061 / m 2237328 / g100 2252633 / g200 2245777
  / g400 2243838 (g_sat 100 on the fixed grid; m 75-91 already clears); train keeps rising 2238574 -> 2457885; held
  400 - m median +4487; cell-stream minus control-stream at m +14026; held minus random-bits g1 +55168, m +142489, 400 +149000.
  Reading: on nk_stub the top1_train held-out NK stops responding at ~80-100 generations while train rises to 400; the
  cpu_ttl cut lands past that knee, so the anti-prior arm's PASS is what the saturation predicts (the "cut truncates
  search" prior was about train, not held). Not claimed: why held saturates (landscape vs Tucker brain).
- D-R7-2 job f564042e7a5b ERROR (0 rows, 0.6 s, commit 61389e5f3); cause being read.
  Cause: B's candidate row stores held64_by_run as a dict keyed "F|rs"; D's I1 iterated it as a list (ValueError on
  '2101|0') before any value was compared. OWN ERROR (untested against the committed row shape).
- Push 1cd8c5ba6 rebased the D rows commits: fe9650a6c -> 7f4df6c84 (D-R7-1, 66 rows, identical), 61389e5f3 -> ae7079ca9.
- Receipts: D-R7-1 1789511852981-0 (status NULL, SATURATED, token_wait_s 1525.8), ANOM-..3451 RESOLVED; D-R7-2
  1789511863745-0 (INDETERMINATE: aborted on D's bug, no value seen, token_wait_s 1688.4). Both first filings were
  refused IDENTITY_TAG_MISSING (D omitted `tag`), refiled with the tag and nothing else changed. OWN ERROR.
- D-R7-2b: same rule; I1 reads held64_by_run by "F|rs" key (+ key-set check), job() takes exp/predicate_id; tests 6
  passed rc 0, including one pinned to the committed candidate row's dict shape. Worker restarted for the edited module.
- 18:38 worker D restarted after the module edit: pid 25220 stopped by verified cmdline + cwd (exit 15), new pid 30748
  registered (nestor-r7-d, r7); the 25220 reg key had TTL 45 s and expires by itself (a terminate skips unregister).
  D-R7-2b claimed, predicate 1789511917971-0 (pinned 5b681baac, rule unchanged), admission ok, job 23ae002ee09c queued.
- D-R7-2b RECORD (job 23ae002ee09c ok, 1 row d0e09a7d8, 0.66 s, 0 QD, token wait 632 s): NOT_STREAM+OBS_USED. I1 5/5,
  planted_shared -> SHARED_STREAM, planted_specific -> NOT_STREAM. The 3 low candidate streams rank 15/16/23 of 32 in
  G's same-stream float baseline (182.75/183.69/189.22, all above floor); q = 0. All 3 read observations (W-zeroed
  159.0 like every run). Baseline family medians 4200 189.5 / 3303 183.2 / 5501 176.7 / 2101 169.2. Same-stream
  Spearman -0.07 (rotation 0.17). Receipt 1789512668923-0; ANOM-..7773 RESOLVED (mechanism not claimed).
  First push failed on a remote ref race ("cannot lock ref"), retried clean (3746854e3).
- A 1789512067159-0 routed the O8 fused != numpy graft anomaly (1789512027239-0; E adds a 2nd case 2101|2255, draw 31)
  to D priority 1. Claimed. Predicate before any replay (reproducibility is itself a discriminator class).
- D-R7-3 code + test (r7_3_fused_vs_numpy_graft.py; 4 passed rc 0; tests use draw-0 donors only, no replay of the two
  mismatching cases). Rebuild draw 24/31 donors (sha vs E's donor_sha256), repeat E's P=16 comparison (3x granted
  threads + 1 thread), localize each differing genome alone per env (obs -> idx -> acts -> done -> charge), analyse the
  first idx-divergent obs row (numpy f32 einsum, f32 sequential emulation, kernel direct, f64 ref + clear_rows).
  Labels NOT_REPRODUCED/NONDETERMINISTIC/BATCH_ONLY/OBS_FIRST/BRAIN_NEAR_TIE/BRAIN_CLEAR/STEP_FIRST; binding controls
  clean genome (no divergence) + planted brain_stride 2 (idx first). OBSERVATION (2 loci). E's O8 closed ADMISSIBLE and
  the live w14->w13 pair (requires fused_eq_numpy every run) is now running, so this answer matters for its gates.
- D-R7-3 job 74bc27094543 "ok" but ALL 3 ROWS REJECTED by the RowWriter: I emitted status "observation", and
  fabric/rows.py:44 STATUSES = (record, dev, aborted, timeout, cheat, control); rows.py:184 raised on every write, so
  the file holds 3 "bad row" wrappers with status aborted and the payload nested under "row". No valid record row ->
  D-R7-3 is INDETERMINATE by the writer, not by its rule. OWN ERROR (the evidence class is a row field,
  evidence_class: OBSERVATION, never the writer's status; my test suite did not pin the emitted status).
  DISCLOSURE: the rejected wrappers are readable and D read them before the re-run, so the D-R7-3b values are seen in
  advance. D-R7-3b changes NO rule, threshold or input: same module, same deterministic 0-QD computation, status
  "record", own predicate + rows file (D-R6-6b / D-R7-2b precedent). New test pins job()'s default status to
  fabric.rows.STATUSES.
  What the rejected rows contain (to be re-earned on accepted rows): I1 both donor sha256 == E's committed hashes;
  controls ok (clean genome 0 divergences; planted brain_stride 2 -> idx first, 116 / 11 envs); d24 genome 14 numpy
  20871 vs fused 20868, ONE env (84, seed 9184) diverges at tick 30, kind idx (numpy 0, fused 4); at that obs row the
  numpy float32 einsum logits TIE EXACTLY (both 1.9400792121887207, gap 0.0) and numpy's argmax takes the lower index,
  while the sequential float32 kernel (gap 3.58e-07), linear_act_row direct and the float64 reference all choose 4
  (ref top-2 gap 1.08e-07, clear_rows False). Label BRAIN_NEAR_TIE for both cases; d31 the same.
  Reading, if it holds on accepted rows: the fused kernel is not wrong here -- it agrees with the float64 reference;
  the numpy reference's einsum accumulation order produces an exact float32 tie on a near-tie row and argmax breaks it
  to the lower action. Thread count is irrelevant (1 == 8 threads, 3 repeats agree).
- Item 4 picked: ANOM-1789417958280-0 (C-R2-02 rent does not shrink programs), discriminator (b) LAMBDA sweep.
  D-R7-4 code + test (r7_4_nk_rent_sweep.py; 7 passed rc 0 after I fixed my own wrong control assertion -- my fake
  "perfect" evaluator honours the cheat flag, so skip_last IS caught; the test now also uses a cheat-blind evaluator).
  Imports C's EVAL_LUA + decode_ref unchanged with LAMBDA as a parameter; C's sampler was UNSEEDED so its rows are
  REFERENCES ONLY (D-R6-9 precedent) -- D re-runs the program arm with a seeded sampler on D's Redis :6393 under D's own
  table key (C's :6392 keys untouched). 3 LAMBDAs x 4 families x 8 run seeds = 32/4/8 per LAMBDA (VERDICT class).
  Rule RENT_BINDS / RENT_INERT / MIXED fixed before any sweep value; half_rent cheat control declared EXEMPT at
  LAMBDA 0 (it charges LAMBDA//2 == LAMBDA there) BEFORE the run, not after.
  No-rows smoke (one stream, l=16384, 4200|0): wall 2.31 s, offers 38400/0 mismatched, elites 1021/0 mismatched,
  controls honest 0.0 / skip_last 0.789 / half_rent 1.0. Only timing and oracle counters were read -- best_active and
  every fitness stayed unread. 96 runs project ~222 s; declared checkpointable, wall 900 s.
- D-R7-3b RECORD (job 18e39014390e ok, 3 rows ACCEPTED ef6667f44, 0.95 s, token wait 1105 s): decision
  d24:BRAIN_NEAR_TIE|d31:BRAIN_NEAR_TIE, I1 both donor hashes true, controls ok. The rejected-row values reproduced
  exactly on accepted rows. Each case: ONE env, ONE tick. d24 genome 14 numpy 20871 / fused 20868, env 84 seed 9184
  tick 30 (numpy f32 logits tie at 0.0 -> argmax picks 0; seq kernel, direct kernel and f64 ref pick 4).
  d31 genome 13 numpy 16410 / fused 16413, env 106 seed 9206 tick 1 (the SEQUENTIAL path ties at 0.0 -> picks 3;
  numpy and f64 ref pick 4). f64 ref not clear in either (gaps 1.08e-07, 1.78e-07). 1 thread == 8 threads, 3 repeats
  agree -> deterministic, no batch or race effect. Reading: a float32 near-tie decided by accumulation order, not a
  rollout defect; neither path is consistently correct. Receipt 1789516880015-0 (OBSERVATION, status NULL, supersedes
  the D-R7-3 INDETERMINATE); ANOM-..7239 RESOLVED; note to A,E,B,G. Gate question (fused_eq_numpy is exact-equality and
  fires on near-ties) left to the owning lanes as a round-8 PC; D changed nothing.
- D-R7-4 submitted (job 0d2d60f699df, predicate 1789516049509-0 pinned 037c269ff, admission ok) after D-R7-3b's
  receipt, one job at a time.
- A ruling 1789516925555-0 on D-R7-3b: ANOM-..7239 RESOLVED, the fused_eq_numpy gate stays EXACT-equality until round 8
  (three verdicts were emitted under it tonight), and D files the tie-aware gate as a PC, not a patch. Packet scope per
  A: a tie-break artifact at a ~1e-7 margin, not a logic error -- it does not impugn B-R5-1 (fused==numpy clean 32/32),
  the R16 screen (42/42) or tonight's Clause B verdict; it explains why the 2-in-819,200 mismatch showed up only on
  untrained random donors, which sit near ties far more often than trained genomes.
- PC filed BY HAND (D27: no code path opens a stub without a refusal; A sanctioned hand-written stubs for r7):
  stub 1789517018361-0 exp_id D-R7-tie-aware-fused-eq-numpy-gate, in refuse()'s record shape, source_event
  D_ANOMALY_RESOLUTION; note 1789517018378-0 to A,E,B,G. measured_cost NULL on purpose (nothing about the FIX was
  measured; D-R7-3b's 0.95 s was the cost of the evidence), estimates build ~1800 s / tests ~900 s.
- F corrections accepted by A (1789515908971-0), recorded for D's FINAL: D-R7-3's refused rows were NOT lost --
  worker._drain wrote 'aborted' rows whose `row` field holds the payload verbatim, all 3 on origin, so the analysis was
  recoverable; the JOB reported ok (rows 3, 2.34 CPU-s) and the INDETERMINATE was D's own receipt decision; D29 is
  recorded as F's defect with credit to D for handling and disclosure. A's D29 design ruling: refuse at emit (no alias),
  fail loudly (any refused row -> job status error), vocabulary lint between rows.STATUSES and EVIDENCE_CLASSES.
- D-R7-4 RECORD (job 0d2d60f699df ok, 100 rows ACCEPTED 915f833fc, 148.8 s wall, 21.3 CPU-s, 96 QD runs, token wait
  1.8 s): decision RENT_BINDS. I1 5/5 (32 runs per LAMBDA, 8 per family, every elite recount exact, first stream of
  each LAMBDA audited 38,400 offers 0 mismatched); controls honest 0.0 / skip_last 0.7891 / half_rent 1.0 at 16384 and
  131072, EXEMPT at LAMBDA 0 exactly as pre-declared.
  median best_active 7.0 (l=0) / 7.0 (l=16384, C's value) / 2.0 (l=131072); 32/32 paired streams shrank; distributions
  6-8 / 5-8 / 1-4. Medians best_net 2.768M / 2.664M / 2.199M, raw NK 2.768M / 2.781M / 2.462M, coverage 0.947 / 0.937 /
  0.941. Reading: rent DOES shrink programs -- C's LAMBDA was too weak relative to NK gains, not decoder_rent inert;
  and the shrink is paid for in raw landscape fitness, so the small programs are worse, not equally good and cheaper.
  At C's own 16384 the median is unchanged (7 vs 7) while the distribution moves (5-8 vs 6-8): real but sub-integer.
  SCOPE: answers the anomaly's discriminator (b) only; (a) the shortcut-proof coverage descriptor was NOT run.
- Child anomaly 1789517158930-0 filed and CLAIMED; D-R7-5 code + test (r7_5_nk_coverage_descriptor.py; 8 passed rc 0).
  Tests the parent's discriminator (a): CONTRIBUTION-HALVES descriptor (c0/c1 = per-locus NK contributions of loci
  0-31 / 32-63, bucketed by floor(c / (32*65535) * 32), same 33x33 grid) vs C's popcount halves, which ops 3/4
  (set/clear 8 adjacent bits) can sweep by a fixed 8. C's EVAL_LUA forked with ONE added branch (ARGV[6] desc); the
  fitness, rent, decode and cheat paths are untouched (test asserts the rent path is unchanged).
  C's sampler was UNSEEDED, so D generates its OWN popcount baseline: 4 cells = {small_program (rent 16384), bitset} x
  {popcount, contribution}, 32/4/8 each, same streams across descriptors (paired per stream).
  Rule fixed before values: I1 BINDING REPLICATION -- D's popcount gap must reproduce C's (>= 0.10 with full
  separation) or the contribution arm is uninterpretable (INDETERMINATE); then GAP_PERSISTS >= 0.10 with separation /
  GAP_VANISHES <= 0.05 / MIXED. Binding controls: Lua cell == numpy cell on 1024 genomes for BOTH descriptors and BOTH
  modes, plus C's honest / skip_last / half_rent.
  No-rows smoke: equivalence 0 cell and 0 fit mismatches for both descriptors in both modes; cheats 0.0 / 0.789 / 1.0;
  30-gen walls 0.14-0.23 s -> 128 runs project ~230-300 s. Only mismatch counts and timings were read; no coverage.
- D-R7-5 RECORD (job 3b714568cbd5 ok, 131 rows ACCEPTED 2991be550, 177.8 s wall, 24.5 CPU-s, 128 QD runs, token wait
  0.1 s): decision GAP_VANISHES. I1 4/4; descriptor_equivalence exact for BOTH descriptors in BOTH modes (0 cell and 0
  fit mismatches on 1024 genomes each); cheats 0.0 / 0.7891 / 1.0.
  BINDING REPLICATION held: D's own seeded popcount baseline reproduces C's gap -- program 0.9371 vs bitset 0.7773,
  gap +0.1598, min program 0.9128 > max bitset 0.8283 (separated). Under CONTRIBUTION halves the gap REVERSES:
  program 0.16395 vs bitset 0.24105, gap -0.0771, not separated. Paired popcount-minus-contribution on the program arm
  median +0.7741. Medians: popcount|program cells 1020.5 best_active 7, contribution|program cells 178.5 best_active 6,
  popcount|bitset 846.5, contribution|bitset 262.5.
  Reading: C-R2-02's coverage advantage is a DESCRIPTOR ARTIFACT -- ops 3/4 (set/clear 8 adjacent bits) sweep popcount
  halves; under a descriptor they cannot shortcut the program arm does not lead. CAVEAT recorded: both arms cover far
  less of the contribution grid (0.16-0.24 vs 0.78-0.94), so only within-descriptor comparisons were made.
  Receipt filed; child ANOM-..8930 RESOLVED. C-R2-02's verdict not revisited (UNSEEDED sampler -> references only).
- A's D-only note 1789517336358-0 (repeat anti-prior-arm PASS: C-R6-AP-01 prior 0.10 rank 39/48, C-R7-AP-02 prior 0.08
  rank 46/48, both PASS; the calibration-arm draw C-R7-AP-01 was INDETERMINATE). D replied 1789517490105-0 with the
  framing fixed before any read: the COUNT is not the finding (n = 2 cannot separate a well-aimed arm from an ordinary
  draw; no hit rate, pm:prior:* never read), the answerable question is MECHANISM. Anomaly filed 1789517546515-0.
- D-R7-6 code + test (r7_6_ap02_pressure_binding.py; 6 passed rc 0 after I fixed my own test arithmetic -- I wrote
  "~0.063%" for 169144*6/(2e6*8), which is 6.3%; the module was correct). Zero QD over C's committed AP-02 rows from
  ORIGIN: does the byte_charge pressure BIND ON THE READOUT'S OWN WINNER? charge_share = beta * functional_bytes /
  (train_nk_per_landscape_top1 * 8), paired within (family, run seed) against the uncharged control's winner, 32 pairs.
  PRESSURE_DID_NOT_BIND (s <= 0.01 and >= 24 pairs equal) / PRESSURE_BOUND (s >= 0.05 and >= 24 pairs smaller) / MIXED;
  planted controls must read the two decisive labels. Same axis as R6's saturation answer, so the two arm PASSes are
  comparable on one question. The metered channel's delivered share is reported (C's own AP-01 lesson: a meter that
  delivers every tick cannot bind).
- D-R7-6 RECORD (job a057c9db6f45 ok, 1 row ACCEPTED cbb257f3f, 0.03 s, 0 QD): decision MIXED. I1 6/6 (32 pairs, 8 per
  family, beta consistent, oracles ok, both held medians reproduce C's summary); planted_bound -> PRESSURE_BOUND and
  planted_free -> PRESSURE_DID_NOT_BIND, both ok. C's rows read from ORIGIN (sha256 b13bd4fbbe9e7e1d).
  median charge_share 0.0365 (0.0276-0.0542) -- between my FREE 0.01 and BOUND 0.05; cell winner smaller in 22/32
  pairs (BOUND needed 24), equal in 7; functional_bytes cell median 4 (3-6) vs control 5 (4-6).
  Reading: AP-02's byte_charge PARTIALLY bound, so the two arm PASSes do NOT share one mechanism -- R6's AP-01 reached
  parity for free (saturation), AP-02 pays ~3.7% of what its winner earns and still reaches parity (held 2116036.84 vs
  control 2116423.73, bar 2102284.02). ANOM-..6515 STAYS OPEN: MIXED returns no mechanism (D-R6-8 precedent).
  SECOND OBSERVATION (reported, not judged): the METER did not bind on the cell winners -- delivered share 1.0 at min,
  median and max (control min 0.671875), winners reading d = 1 hex digit, so cost 8*d stays under the 128 credit. Same
  failure mode C hit in C-R7-AP-01 (INDETERMINATE), but here in a cell that PASSED.
  Next discriminator named in the receipt: 0-QD paired train-vs-held read, or a BETA sweep in D-R7-4's shape.
- A guardrail 1789517887578-0 ADOPTED for the rest of r7: cell routing metadata (arm, rank, quantile, sealed prior) is
  conductor/D-only while the round is live; posts readable by C or R name only the CELL and the MECHANISM. A accepted
  D-R7-6's reading (the two cells do NOT share a mechanism: R6 saturation vs AP-02's partially-binding charge and
  non-binding meter) and will record the cross-cutting pattern (C-R7-AP-01 INDETERMINATE, C-R6-01 vacuous, AP-02) as a
  CELL/PRESSURE DESIGN issue for round 8, not a scoring claim.
  D's own exposures, reported to A only (1789517997820-0) since neither can be unpublished: the anomaly record
  1789517546515-0 on pm:anomalies carries both arms, ranks and sealed priors and is readable by every lane, and D's
  note 1789517850774-0 named the arm to C. Offered to supersede the anomaly record with a cell-and-mechanism-only
  version if A wants it. D has never read pm:prior:*; the metadata came only from A's two notes to D.
- D-R7-7 code + test (r7_7_ap02_train_vs_held.py; 8 passed rc 0). D-R6-8's instrument UNCHANGED, pointed at
  C-R7-AP-02: t = #pairs control train > cell train, h = #pairs control held > cell held, over the same 32 committed
  pairs. TRAIN_NOT_HELD t >= 26 and h <= 16 / BOTH_LOSE t >= 26 and h >= 26 / NO_TRAIN_COST t <= 16 / MIXED; binding
  self_pair control, shuffled within-family pairing reported. Same thresholds as R6, so both cells are read on one
  axis (R6 read t = 32, h = 17). Predicate text scrubbed of routing metadata BEFORE posting and verified by grep.
- D-R7-7 RECORD (job 1bd4cf55550c ok, 1 row ACCEPTED 465abef75, 0.025 s, 0 QD): decision MIXED, t = 21, h = 13.
  I1 5/5; self_pair 0/0 (binding, ok); shuffled within-family pairing t 20 / h 14 -- within one of the true pairing, so
  the counts do not depend on same-stream coupling. C's rows read from origin (sha256 b13bd4fbbe9e7e1d, beta 169144).
  Median paired train diff (control - cell) +19,791 on a ~2.4M scale (<1%); median paired HELD diff -9,276, i.e. the
  cell is the better one on held-out in 19 of 32 pairs. PRECISION: median-of-differences is not difference-of-medians --
  C's arm medians are nearly equal with control slightly higher (2116423.73 vs 2116036.84); neither number is read as
  the cell being better overall. Spearman(charge_share, held diff) +0.34 (weak). R6 on the SAME instrument read
  t = 32, h = 17, so the two cells differ on this axis too.
  ANOM-..6515 STAYS OPEN: two discriminators in a row (D-R7-6 binding, D-R7-7 transfer) returned MIXED with useful
  descriptive numbers but no mechanism label. Established so far: the charge is materially paid (3.65% of what the
  winner earned), shrinks the winner in 22/32, costs <1% of train fitness, costs nothing on held-out, and the meter
  does not bind at all. Next candidate named in the receipt: a BETA sweep in D-R7-4's shape (decisive, not
  descriptive), to be SIZED against C's harness cost before committing; a PC if it does not fit the clock.
- BETA sweep SIZED from C's committed rows before committing to it (promised to A): per run wall_s median 38.36 but
  cpu_s median only 1.47 -- the wall is FalkorDB round trips, not compute. One BETA point (64 runs) ~2456 s wall /
  ~94 CPU-s; a 4-point sweep reusing the single BETA-independent control ~4914 s wall (~82 min) / ~280 CPU-s,
  checkpointable over ~3 segments. It FITS the clock and the budget. NOT RUN anyway: it would hold one of the two
  shared CPU tokens for ~82 min at ~4% utilisation while another lane waits -- the D22 starvation D itself reported,
  with D as the cause -- and it would contend with C's live FalkorDB on :6392. Filed as a PRODUCTION_CANDIDATE with the
  measured basis, the projection, the reason, and a cheaper numpy-substrate variant carrying the caveat that the
  substrate is part of the cell definition (it would answer a neighbouring question, not this one). Note to A only;
  D takes a ruling either way, and without one ANOM-..6515 stays OPEN with two MIXED discriminators.
- Next queue item sized: ANOM-1789415790378-0 (affine plastic: 238/238 switches on fit-eligible vs 73/130 on
  genome-eligible). Reading both mains REFRAMES it: C7c and C7e share the learner, probe, drive() and scoring outright
  (C7e's docstring says so; the per-target blocks are line-for-line the same), so "score C7e's learner on C7c's
  targets" is vacuous -- there is ONE learner. The two runs differ in (a) the eligibility criterion and (b) an
  UNCONTROLLED second factor: the record seed sets are DISJOINT (C7c RECORD_SEED0 90000, C7e 94000, n=512 each). The
  anomaly's expectation silently assumes a common scoring seed set.
  0-QD overlap from committed rows (eligibility INPUTS only, no detection outcome read): fit-eligible 34 targets / 24
  worlds, genome-eligible 18 / 14; BOTH 11, FIT-ONLY 23, GENOME-ONLY 7. A non-empty common set exists, so the real
  discriminator is: score the shared learner on all three partitions under ONE record seed set, which removes the seed
  confound. Reported-not-judged candidate: corrupt_rate spans 0/8/16/32 among genome-only targets but only 0/16/32
  among the common ones (rate 8 appears only in genome-only).
  Timing smoke (no rows, timings only): trajectory 0.02 s, drive affine 0.01 s, drive digitTT ~1.0 s per target at
  n=32/64 -- the digit-TT arm is ~99% of the cost. n=512 sizing measured before fixing n in the predicate.
- D-R7-8 code + test (r7_8_c7_eligibility_swap.py; 6 passed rc 0). Scores C7c/C7e's SHARED learner on all three
  partitions (BOTH 11 / FIT_ONLY 23 / GENOME_ONLY 7, taken from committed rows) under ONE fresh record seed set
  (96000.., n 512 -- disjoint from C7c's 90000/91000 and C7e's 94000/95000, so neither criterion's targets get home
  advantage). digit_tt DROPPED with reason: it grounds C's H2 chance rate, not the detection question, and measured at
  2.28 s of 2.39 s per target. Rule: rate_f = detected/switches over all 34 fit-eligible (C7c published 238/238),
  rate_g over all 18 genome-eligible (C7e published 73/130 = 0.562); LEARNER_DOES_NOT_REPRODUCE rate_f < 0.95 /
  SELECTION rate_f >= 0.95 and rate_g <= 0.80 / SEEDS both >= 0.95 / MIXED. Binding controls are C's own: probe_affine
  CLEAN and probe_leak LEAK on every target, null-world surprises <= 2.
  Smoke (no rows, timings + control flags only, detection unread): 0.33 s cold per world, 0.04 s cached -> ~8.6 s for
  41 targets; probes CLEAN/LEAK and null surprises 0 on the smoked target. evidence_class OBSERVATION (41 targets in 3
  partitions, not a 32/4/8 family sample).
