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
