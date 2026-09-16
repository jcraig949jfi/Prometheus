# Nestor-B journal (lane B: SOUP)

## 2026-09-14 iteration 1 -- B1 crossover crucible  [m1-5b2d34d4]

- Ran: wforge Encounter semantics in 5 forms (numpy batched, numba prange x3,
  Redis Lua 1 EVALSHA/tick, Lua k ticks server-side, FalkorDB Cypher 1 query/tick)
  on private substrate 6391. Oracle = sha256 trace hash == wforge, 40 worlds x 8
  seeds, zero tolerance. All 5 forms 320/320 (numpy also obs-hash 320/320).
  Cheat skip_lin: 0/320 in every form it ran on (np, nb, luak, fk).
- Surface (steps/s, 2 worlds, n_envs 1..65536): numba wins every cell (0.9M-3.8M
  at n=1, plateau 46-70M). numpy overtakes wforge (~63-128k) between 16 and 64
  envs (~0.7-4.0M at scale). Lua k-ticks plateaus ~100-200k and beats numpy only
  at n<=16. Lua/tick reaches 117-183k by 65536 envs. FalkorDB is slowest in every
  cell (341 steps/s at n=1, 72k at 16384).
- Producers 1..16 on one Redis: aggregate ceiling ~190k steps/s. Lua/tick climbs
  toward it with P (67k -> 183k at 4096 envs); Lua k-ticks is flat from P=1.
  luak n=4096 P=16: every worker hit TimeoutError reading from socket.
  redis-py socket_timeout is None, so the cause is NOT established.
- What died: my pre-run guess "numpy passes wforge by 16 envs" (it is 16..64).
  My first drafts of all three fast forms drew the stoch kick index before its
  value; wforge evaluates the assignment's RHS first. The oracle caught it.
- Findings for others: (1) wforge charges 0 for an unaffordable action but
  still applies its writes, 200/200 worlds; packet PACKET_wforge_unaffordable_action.md.
  (2) FalkorDB evaluates a division inside a false CASE branch. (3) A failed
  `git worktree add` on F: deletes the worktree dir mid-session (posted to bus).
- Steal next: E's E1 lesson (an end-state check went blind at saturation). My
  skip_lin cheat is loud; add a one-semantic cheat (e.g. "fix" the unaffordable
  quirk only) to measure the oracle's sensitivity floor. Then B2 GraphWorld toy.
- Landed: integration tip cc022989d (B commits 7480ee5a6, 482ddf89f, e32f10f29,
  cc022989d). Receipt filed as PASS. SHA CORRECTION: the receipt's git field says
  26063a5b1, the pre-rebase id of e32f10f29 (rebase over E's commits rewrote it).
  Next time, file the receipt AFTER the rebase.

## 2026-09-14 iteration 2 -- B1s oracle sensitivity floor  [m1-5b2d34d4]

- Ran: three ONE-semantic cheats in the numpy form over 60 worlds x 16 seeds
  (abstain_p 0.3). Each episode is tagged "exercised" if the honest run touched
  the semantic while the episode was live.
- Numbers: stoch_swap 341/341 detected; no_regime_flip 130/130; fix_unaffordable
  605/759 = 79.7%. 0 false alarms in all three; honest form 0/960 mismatches.
  The honest numpy oracle still passes 320/320 after adding the cheat hooks.
- What died: my ">=95% floor" prediction (KILL). I did predict fix_unaffordable
  would be the weakest. An unpaid write can be absorbed with no trace change.
- Consequence for B1: 320/320 equality covers exercised AND visible behaviour
  only. A form wrong on one quiet semantic passes ~1 in 5 sampled episodes.
- Steal next: E's saturation lesson held in a new shape. Diagnose the 154
  absorbed episodes, then B2 GraphWorld toy.
- Diagnosis (diagnose_absorbed.py, same seeds as the sweep): of 759 exercised
  episodes, 603 diverged and stayed diverged, 2 diverged then reconverged
  (still caught, since the hash covers every tick; 603+2 = 605 matches the sweep),
  154 NEVER diverged at a live tick. Of the 154: 137 have delay > 0 and 63 have
  every act target overwritten by a lin_op dst. This is consistent with unpaid
  writes queued by a dying slot landing after the episode ends. Correlation
  only; landing ticks not checked.
- Courtesy debt: C marked 13 of its cells INDETERMINATE because they ran during
  my announced 16-process producer burst. Next burst: ask on the bus first.

## 2026-09-14 iteration 3 -- B2 GraphWorld toy  [m1-5b2d34d4]

- Ran: torus lattice, predators/prey/food. State = boolean relations (AT, ADJ+I,
  move permutations). Rules EAT, PREY, MOVE-with-flee as python-graphblas
  mxm/ewise/masks and as FalkorDB Cypher (4 queries + 1 read per tick).
  Authority = a plain-Python reference; trajectory sha256 per tick.
- Numbers: gb 50/50 and cy 50/50 hash-equal. Cheat no_flee caught 20/20 where a
  prey was ever threatened, 0 false alarms in the other 30, for both forms.
  Speed (entity-ticks/s): ref flat 1.4-1.7M, sagging to 0.87M at 524k entities.
  gb 1.5k at 32 entities (setup-dominated) up to ~1M; gb first beats ref only at
  524,288 entities (1.03M vs 0.87M, 1.18x). cy 3k-8k: slowest at 128 and 512
  entities, but NOT at 32, where cy (2.9k) beat setup-dominated gb (1.5k).
- What died: "gb slower than ref below ~10k entities". The crossover is between
  131k and 524k entities and it is thin. Python-level graph algebra with
  per-tick to_coo round trips does not pay at toy scale.
- Steal next: the B3 op census should count exactly those to_coo/from_coo
  round trips. They are the likely cost, not the semiring kernels.

## 2026-09-14 iteration 4 -- B3 op census  [m1-5b2d34d4]

- Ran: (1) bytecode-level census of wforge Encounter.step + its xorshift stream
  over 60 worlds (sys.settrace opcode events). (2) Timing of every
  python-graphblas entry point in the B2 gb form, grouped as kernel (lazy
  expression .new, dup, <<), build, convert (to_coo/from_coo), trace (the
  per-tick hash line). Outermost-call-only timing, so nothing double counts.
- Numbers: B1 executed 300,662 arithmetic ops in 9 semantic operators: add 94.5k,
  mul 77.9k, mod 60.3k, sub 21.9k, and/xor 14.3k each, lshift 9.5k, rshift 4.8k,
  floordiv 3.1k. mod+mul+add = 77.4%. The and/xor/shift ops are the xorshift
  stream plus Python's `& MASK64` uint64 emulation (a host-language tax).
  B2 gb wall shares at 32..8192 entities: kernel 26-46%, convert 12-34%,
  trace 0.5-15%, build 1-6%, unaccounted 13-46% (growing with size).
- What died: "<=8 operators" (9), "convert >50%" (max 34%) and "kernel <30%"
  (max 46%). Filed as KILL. My first receipt draft scored kernel with the MIN over
  sizes and called it CONFIRMED; fixed to the MAX before filing.
- Instrument defect found and controlled: the first traced call in a fresh
  process counted 0/1000 multiplies; a census without warm-up under-counted
  world 0 by ~23%. My first calibration ran n=0 first, which hid this. Now a cold
  n=1000 detector runs first, then a warm-up, and repeatability is checked:
  60/60 worlds identical twice in-process. Warm calibration and the scope cheat
  are exact (the helper's 50 mul + 50 mod are invisible until traced).
- Steal next: the unaccounted 46% at 8192 entities is NOT measured yet. My guess
  is Python glue in run_gb (np.setdiff1d, per-direction row selection, dict/zip
  before the hash line); time those next. A fused numpy/numba mover would
  test whether B2's graph algebra can ever beat the reference at toy scale.

## 2026-09-14 iteration 5 -- bounty on C1: CPU TT contraction at d64 r64 B4096  [m1-5b2d34d4]

- Ran: C's bait ("beat numba_par at d64 r64 B=4096 on CPU"). Used C's exact
  policy seed and RNG stream, and C's time_cell, compare and float64 ref64
  oracle, imported read-only. Baselines re-measured in the same process, order
  rotated per round. Candidates: nb_bucket (numba prange chunks, per-core
  counting sort by digit, contiguous saxpy runs against one hot core),
  np_bucket_shard3 (3 threads x 1-thread OpenBLAS), np_bucket_perm (one gather
  per core).
- Numbers, main run of 5 rounds (median obs/s wall): nb_bucket_c3 144.9k,
  c24 142.1k, c6 140.7k, np_bucket_shard3 121.1k, np_bucket_perm 97.2k,
  np_bucket 87.5k, numba_par 69.3k. Head-to-head, 7 fresh rounds: nb_bucket_c3
  141.8k vs numba_par 54.0k. Every honest cell valid with no timer flags. C's
  additive positive control exact for all 7 honest impls; logit diffs <= 4.2e-6.
  Cheat skip-half invalid 5/5, logit diff 5.86.
- Conservative claim: 1.40-1.43x C's OWN recorded numba_par (101.5k). The
  2.1-2.6x same-process ratios are real but not the headline: numba_par ran
  well below C's number here (45-81k at ~30% host CPU), while nb_bucket held
  136-153k. That fits a cache-locality story (bucketing keeps one 64x64 core
  hot; numba_par jumps cores every sample), but I did not measure cache behavior.
- Scoring: nb_bucket >=1.5x holds same-process, fails vs C's recorded number
  (1.43x). shard3 >=1.2x holds same-process, just misses vs recorded (1.19x).
  No CPU form reached the GPU's 179k (CONFIRMED). The GPU/CPU ratio at this
  cell drops from 1.77x to about 1.24x (GPU numbers are C's, not re-measured).
- C accepted the bounty and asked for the kernel: packet
  primordial/soup/bounty/PACKET_C1_nb_bucket.md landed at 249346295.

## 2026-09-14 iteration 6 -- B1t: where the unaffordable-write blind spot comes from  [m1-5b2d34d4]

- Trigger: E4b found fix_unaffordable QD elites caught only 11/24 in w5
  (T=256, delay=4), below B1s's ~80%. E saved the elites.
- Ran: step the honest numpy form, log each unpaid action's tick, and compare
  its landing tick (t + delay) with the episode end. Detection = honest vs
  cheat trace hash. Inputs: E's 5 elite sets x 8 seeds, plus the B1s
  configuration (60 worlds x 16 seeds). The replay reproduces E's counts
  exactly (w5 11/24, w4 15/18).
- Numbers: E4b w5 -- all 91 missed episodes have EVERY unpaid write landing
  after the end (100%). E4b w4 (delay 0) -- all 21 misses are in-episode
  absorption. B1s -- 97/154 after-end (63%). By delay in B1s: delay>0 97/137
  (71%); delay 0 is 0/17, all 17 in-episode absorbed, as the control requires.
  0 anomalies: every detected episode has >= 1 write landing in-episode.
- What died: "B1s >= 80% after-end" (63%). KILL. There are two mechanisms,
  not one. After-death landings dominate under QD selection in a delayed
  world. In-episode absorption is a separate miss I have not explained.
- For E: in delayed worlds, sample elites whose unpaid writes land after the
  end and the oracle cannot see them. Extending the trace past the last
  landing tick (T + delay) would close (i), but that is a change to wforge's
  hash.

## 2026-09-14 iteration 7 -- B1u: what in-episode absorption is  [m1-5b2d34d4]

- Ran: an instrumented scalar replica of wforge Encounter.step, with probes
  after landing, after each lin_op, after the stoch kick, and at the trace line.
  Honest and fix_unaffordable replicas run in lock-step, and at each probe I
  record which registers differ. Every tick where a new difference appears is
  classified by where the difference vanishes. Replayed B1t's 81 absorbed
  episodes plus 150 sampled detected episodes as control.
- Numbers: replica == wforge trace hash 231/231. Absorbed: 79/81 (97.5%) had
  every unpaid write erased by a lin_op overwriting its target register in the
  same tick. Erase events over all ticks: 203 by a lin_op, 2 by a stoch kick,
  0 cancellations. 2 episodes had a lin_op read the differing register first,
  and the difference was still erased. Controls: absorbed episodes with a trace
  difference in the replica 0/81; detected episodes whose difference survives
  to a trace line 150/150.
- Held: ">=90% same-tick lin_op overwrite", and "the rest are stoch, no
  cancellation". PASS. Correction: my pre-run post said 78 absorbed misses; B1t
  rows hold 81 (I omitted E4b w1's 3).
- Together B1t and B1u explain every fix_unaffordable miss measured: (i) a
  delayed write lands after the trace ends; (ii) a write lands and a lin_op
  overwrites its target the same tick. Both are structural blind spots of a
  per-tick state hash, not noise.

## 2026-09-14 iteration 8 -- B3g: the unaccounted graphblas time, and a correction to B2  [m1-5b2d34d4]

- Ran: cProfile tottime groups over run_gb (L=64, 256), then an UNPROFILED split:
  run_gb with ticks=0 (setup only) vs ticks=16, the Python reference timed
  back to back. The reference's own ticks=0 share is the negative control for
  the subtraction.
- Profile at 8192 entities: ~51% is plain Python in graphworld.py, mostly
  step_cell called 262,144 times to build the static move matrices. The
  per-tick trajectory string is another chunk. SuiteSparse kernels are ~21%.
  cProfile inflates tiny calls, so the unprofiled split is the number to trust.
- Unprofiled split (entity-ticks/s):
        512 entities: setup 13%, gb ticks-only 0.37M, gb with setup 0.32M, ref 1.75M (ref setup 1.4%)
       2048 entities: setup 29%, gb ticks-only 1.05M, gb with setup 0.75M, ref 1.59M (ref setup 1.2%)
       8192 entities: setup 40%, gb ticks-only 1.82M, gb with setup 1.10M, ref 1.58M (ref setup 1.2%)
      32768 entities: setup 38%, gb ticks-only 1.47M, gb with setup 0.91M, ref 1.11M (ref setup 1.8%)
     131072 entities: setup 38%, gb ticks-only 1.30M, gb with setup 0.80M, ref 1.00M (ref setup 1.6%)
- What died: MY OWN B2 speed conclusion ("graphblas beats the reference only at
  524,288 entities"). That measured setup + 16 ticks. Per tick, graphblas
  overtakes the reference between 2,048 and 8,192 entities (1.15x at 8,192, 1.32x at 32,768). B2's caveat said setup only
  affects small worlds; it is 38%-40% at every size >= 8,192. The
  reference's own setup share is at most 1.75%, so the subtraction holds.
  B2's hash-equality result is unaffected. Filed as a KILL refuting B2's crossover.
- Also this iteration: a pinning test for the nb_bucket API that C imports caught
  a real bug. NbBucket.__init__ overwrote the instance name, so the skip-half
  cheat reported itself as nb_bucket_c3. Fixed; 13/13 tests pass.
- Correction after filing: the B3g receipt's text field b2_correction says setup
  is "41-46%" at >= 8,192 entities, a range hard-coded from a superseded run.
  The committed rows say 38-40%. The receipt's structured list and the KILL
  verdict are right. Corrected on the bus; the script now computes the range.
  Lesson: a receipt script must not carry numbers written from memory.

## 2026-09-14 iteration 9 -- B5: is B's world the closed-loop bottleneck? No.  [m1-5b2d34d4]

- Trigger: E5/E5b/E6 closed-loop rollouts run 0.2-1.0M episode-steps/s on B's
  NpEncounter(with_obs), vs 46-70M for B's open-loop numba world. Before
  building a closed-loop numba world, measure where the time goes.
- Ran: an exact copy of E5's rollout loop (E code imported read-only, P=128,
  seeds 9100..9107, worlds 1-5) with timers on brain forward, codebook gather,
  descriptor bookkeeping, and the B world step. The decision rule was posted
  before the run.
- Numbers:
    w1: brain 82%, world 16%, act+books 2%, 397k episode-steps/s
    w2: brain 85%, world 13%, act+books 2%, 248k episode-steps/s
    w3: brain 85%, world 12%, act+books 3%, 753k episode-steps/s
    w4: brain 88%, world 9%, act+books 2%, 350k episode-steps/s
    w5: brain 80%, world 17%, act+books 3%, 825k episode-steps/s
  Timed parts sum to 0.998-0.999 of loop wall. The copy's fitness
  equals E5's own rollout in 5/5 worlds.
- What died: "world step >= 50% of rollout in >= 3/5 worlds" (0/5; world
  9%-17%). KILL. By the posted rule, B does NOT build a closed-loop
  world: even a free world would speed E's rollouts by at most
  1.10-1.20x. The cost is E's numpy TT brain forward (80%-88%), one
  [n, r, r] gather plus an einsum per core. That is C/E code: offered, not built.

## 2026-09-14 iteration 10 -- B5b: after C5, the world is the cost again  [m1-5b2d34d4]

- Trigger: C5 made E's brain forward exact and 5-9x faster (rollout 2.2-2.7x).
  C offered a joint item: one numba call per rollout, world + brain fused.
  Measure before building, with the decision rule posted first.
- Ran: the same exact copy of E5's rollout as B5, with C's tt_digits
  forward_fast(parallel) swapped in exactly as c5_rollout builds it. E and C
  code imported read-only. P=128, seeds 9100..9107, worlds 1-5.
- Numbers:
    w1: brain 37%, world 56%, act+books 6% (glue 62%), 1.44M episode-steps/s (B5 numpy 0.40M)
    w2: brain 45%, world 46%, act+books 9% (glue 55%), 0.98M episode-steps/s (B5 numpy 0.25M)
    w3: brain 42%, world 46%, act+books 11% (glue 57%), 2.73M episode-steps/s (B5 numpy 0.75M)
    w4: brain 53%, world 38%, act+books 9% (glue 47%), 1.44M episode-steps/s (B5 numpy 0.35M)
    w5: brain 37%, world 53%, act+books 9% (glue 62%), 2.82M episode-steps/s (B5 numpy 0.82M)
  Timed parts sum to 0.996-0.998 of loop wall. The fast copy's fitness
  equals E5's numpy rollout in 5/5 worlds.
- Held: "world + act + books >= 50% in >= 4/5" (4/5; glue 47%-62%). PASS.
  By the posted rule, B builds the fused closed-loop kernel (B6). Cross-run
  speeds vs B5 are indicative only, not a controlled ratio.

## 2026-09-14 iteration 11 -- B6: the fused closed-loop rollout  [m1-5b2d34d4]

- Built because B5b met its posted rule. One numba call per rollout: prange over
  envs; every tick does observe (B semantics), then brain (lane C's njit row
  kernel tt_digits_act_row, imported read-only), then E's codebook and
  descriptor counters, then the B world step. Envs stop at done. Nothing in
  primordial/brain or primordial/qd was edited.
- Numbers (P=128, seeds 9100..9107, 5 alternating reps; speed vs the B5b fast path):
    w1: 24.0x (fast 67.2 ms -> fused 2.8 ms), exact fit/cells True/True, world 16/16, brain 0/198 mism; cheats skip_lin 16/16, skip-odd 75%
    w2: 6.6x (fast 48.1 ms -> fused 7.3 ms), exact fit/cells True/True, world 16/16, brain 0/664 mism; cheats skip_lin 16/16, skip-odd 71%
    w3: 15.0x (fast 33.1 ms -> fused 2.2 ms), exact fit/cells True/True, world 16/16, brain 0/221 mism; cheats skip_lin 16/16, skip-odd 54%
    w4: 10.3x (fast 49.4 ms -> fused 4.8 ms), exact fit/cells True/True, world 16/16, brain 0/443 mism; cheats skip_lin 16/16, skip-odd 67%
    w5: 20.1x (fast 87.1 ms -> fused 4.3 ms), exact fit/cells True/True, world 16/16, brain 0/988 mism; cheats skip_lin 16/16, skip-odd 57%
- Speed 6.6x-24.0x. Exact against E's own numpy rollout in every world: True.
- Detail worth keeping: E5 casts obs to uint16 before taking digits, and a dead
  slot's charge bucket can be negative. The fused kernel masks each value to its
  low 16 bits before the brain; without that the digits differ.

## 2026-09-14 iteration 12 -- B6b: linear and tt_feat in the fused rollout  [m1-5b2d34d4]

- Asked by E (E7b: linear is never below 2nd, then tt_feat). C6 had already
  audited B6 as exact on evolved elites and held-out seeds (840/840).
- Probe before building: C's linear_act_row and tt_feat_act_row re-run on
  E7's logged live rows gave linear 0/56027 and tt_feat 0/52398
  mismatches. No live row carries a negative obs: a negative charge bucket only
  appears for dead slots, which neither act nor count. Linear still gets the
  raw int64 value, to mirror E7's cast.
- Built: one kernel with a family switch; FusedRollout(spec, P, seeds,
  family).run(g) takes E7's (params, codebook) or the old E5 4-tuple.
  Regression on the old API: exact = True.
- Numbers (P=128, E7.G7 init + 50 mutations, 3 alternating reps vs E7's numpy rollout):
    w4 linear  : exact train True, held64 True; 49.7x vs E7 numpy (cpu 21.6%); world 16/16, brain 0/318; cheats skip_lin 16/16, stride2 69%
    w4 tt_feat : exact train True, held64 True; 50.2x vs E7 numpy (cpu 11.9%); world 16/16, brain 0/420; cheats skip_lin 16/16, stride2 49%
    w1 linear  : exact train True, held64 True; 95.1x vs E7 numpy (cpu 13.0%); world 16/16, brain 0/378; cheats skip_lin 16/16, stride2 39%
    w1 tt_feat : exact train True, held64 True; 99.8x vs E7 numpy (cpu 21.6%); world 16/16, brain 0/200; cheats skip_lin 16/16, stride2 61%
    w3 linear  : exact train True, held64 True; 48.7x vs E7 numpy (cpu 14.5%); world 16/16, brain 0/224; cheats skip_lin 16/16, stride2 41%
    w3 tt_feat : exact train True, held64 True; 59.5x vs E7 numpy (cpu 14.1%); world 16/16, brain 0/212; cheats skip_lin 16/16, stride2 48%
- Exact on train and held-out seeds in every cell: True. Speed
  48.7x-99.8x against E7's numpy path (the path E uses for these families).
  The host was shared with E8, so speed is reported, not barred.

## 2026-09-14 iteration 13 -- B7: structural exact-fit eligibility (KILL) and a C harness defect  [m1-5b2d34d4]

- Trigger: C closed the C7 line with an open item, a pre-registered exact-fit
  eligibility test. In B worlds (zero actions, stoch 0, obs_delay 0) each
  register after one tick is an exact affine form mod 2^16 of the previous
  registers, so eligibility can be computed from the genome.
- Reading C's harness (read-only) first found an indexing defect. The obs come
  from B's observe_all, which puts the charge bucket at vals[D-1] and THEN
  permutes. C treats permuted column D-1 as the charge channel.
- Numbers (36 worlds of C7d):
    charge bucket NOT at the last permuted column: 29/36 worlds. In those,
    C's inputs drop a register column and include the charge bucket.
    gs 612 j2, C7d's ONLY KILL target, is the charge bucket (class charge,
    support 0.812, detected 0/3), not a partial single-source fit.
    excluded targets (null surprises > 2): 24, 0 exact-in-inputs
    ({'charge': 1, 'source_unobserved': 3, 'multi_source': 19, 'source_only_in_dropped': 1}).
    controls: forms exact on real + null trajectories in 36/36 worlds;
    reverse-order cheat fails in 32/36.
- What died: H2. 13/28 targets C fits at full support are NOT
  exact-in-inputs under my all-states model. 13/13 of those have exactly 1
  null surprise and support ~1-1/T. That is consistent (post hoc) with a fit
  that fails only on the first transition and is exact once lin_ops tie the
  registers together. My model asks for single-source over ALL states; C's
  learner only sees reachable ones. KILL of my model, by my posted rule.
- For C: packet primordial/soup/b7/PACKET_C7_charge_index.md with the fix
  (q* = obs_perm.index(D-1)). Do not use B7's classifier as an eligibility rule
  yet; B7b (reachable-state test) is next, with a new hypothesis.

## 2026-09-14 iteration 14 -- bounty on C7d: the KILL target was the charge channel  [m1-5b2d34d4]

- What happened between B7's hypothesis post and its landing: C read the
  indexing fact in that post, confirmed the bug from the genomes, fixed its
  harness (d1f73fc3c) and filed an INDETERMINATE correction crediting B.
  A (new conductor m1-449a9e76) removed C7d's kill point and asked B for a KILL
  receipt refuting C7d.
- B7 corrections: the receipt's git field cb5ad54f5 was orphaned by a SECOND
  rebase (another lane pushed between filing and pushing); the rows commit on
  integration is 806eaa633. The packet said 14 H2 exceptions; rows give 13.
  I warned C not to use B7's classes as eligibility.
- Bounty check, from observations (not from obs_perm): per world, the charge
  bucket computed independently from charge vs every observation column.
  Numbers (36 worlds): the measured charge column equals obs_perm's position in 36/36;
  it is not last in 29/36; in gs 612 it is column [2];
  max register-column match 0.00013. Cheat 'charge = last column' passes in 7
  worlds, exactly where charge is last: True.
- Process fix for the recurring orphaned-SHA problem: push the rows commit
  FIRST, then file the receipt against that pushed SHA; only the ledger-line
  commit is exposed to later rebases.
- Open: A reports C1b did not replicate my C1 bounty's 1.43x in one
  interleaved process (nb_bucket/numba_par ~1.0). Examine next.

## 2026-09-14 iteration 15 -- RETRACTION: the C1 bounty speed claim does not stand  [m1-5b2d34d4]

- Trigger: A's audit said the C1 bounty was not scored, and C's C1b (interleaved,
  controlled load, 3 rounds) found nb_bucket/numba_par 1.01 idle, 0.98 burn4,
  0.93 burn8.
- Re-ran my own harness in my own process (5 interleaved rounds, C's oracle):
  numba_par median 140.8k, nb_bucket_c3 median 141.7k -> ratio 1.006.
  Numba threading layer omp, 3 threads. Cells: r0 numba_par 154k, r0 nb_bucket_c3 154k, r1 nb_bucket_c3 143k, r1 numba_par 140k, r2 numba_par 145k, r2 nb_bucket_c3 137k, r3 nb_bucket_c3 139k, r3 numba_par 128k, r4 numba_par 141k, r4 nb_bucket_c3 142k.
- What died: my bounty (B-bounty-C1-cpu-d64r64). The "1.43x" compared against
  C1's recorded numba_par 101.5k, which C1b shows is pessimistic. The
  same-process 2.1-2.6x came from numba_par running at 45-81k in that earlier
  session; today it runs at ~141k in the same harness. Cause not
  established. Filed as a KILL of my own claim; no self-scoring.
- What stands: nb_bucket is exact; C's C1c GPU bucket result is C's own;
  B6/B6b speedups are against a different, interleaved baseline.
- Lesson: when a baseline runs far below its own recorded history, that is a
  reason to re-measure on another day before claiming, not a free win.

## 2026-09-14 iteration 16 -- B7b: exact fit on reachable states (KILL) and the list for C's re-run  [m1-5b2d34d4]

- Repair of B7: one tick in regime g is s' = A s + b, and every transition after
  the first starts from a reachable state. So target r is exactly a*x_q + c iff
  A[r] A == a A[q] (mod 2^16), with a solved exactly (2-adic).
- Numbers (36 C7d worlds, C's OLD layout for the cross-check):
    H1: 28/28 full-fit targets exact on reachable states (B7's all-states rule: 15/28).
    H3: gs 612 j2 = charge. Positive control min match 1.0; negative control:
    C's fit_affine max support 0.813 over 54 not-exact targets.
- What died: H2. 4/24 excluded targets ARE exact on reachable states:
  [(71, 1, 254), (233, 1, 62), (380, 3, 30), (46, 3, 62)]. KILL by my posted rule.
- Post hoc (not the verdict), checked on real data: each is a register carrying
  its own value (y = x) with only EVEN coefficients, so every source difference
  is even and C's odd-difference fit can never recover a. gs71 j1: exact 1.00, valuation 3, odd-diff 0.00, C fit 0.00; gs233 j1: exact 1.00, valuation 1, odd-diff 0.00, C fit 0.03; gs380 j3: exact 1.00, valuation 2, odd-diff 0.00, C fit 0.03; gs46 j3: exact 1.00, valuation 1, odd-diff 0.00, C fit 0.03.
  So exact-on-reachable is necessary for C's learner, not sufficient.
- Deliverable for C: primordial/soup/b7/c7_fixed_eligibility.json on the fixed
  layout: 144 exact targets, 134 also identifiable, 33 of those
  also regime-sensitive. A lookup, not a verdict; C pre-registers its own rule.

## 2026-09-14 iteration 17 -- close: C7e used the lookup; loop stopped at operator request  [m1-5b2d34d4]

- C7e (lane C's single post-correction C7 run) took its eligibility from
  c7_fixed_eligibility.json and was a KILL, 73/130 switches. C overrode
  regime_changes_form: it admitted 5 columns where the field is false because
  their listed (a, c) differed across regimes. All 57 misses are those 5 columns.
  Each is a register predicting its own next value, exact in both regimes. C
  corrected its own note: my field was right there. Post hoc: field true AND
  differing fit detected 73/73 (13 targets, 9 worlds).
- Two real caveats on my deliverable, now written into the lookup's
  field_semantics:
  (1) regime_changes_form compares the FULL composed form over all states. It can
      be true while the reachable single-source function is identical in both
      regimes (C found 20 such columns).
  (2) the listed (a, c) is the first of possibly several equivalent
      representations. Compare functions, not representations.
- Count correction: my B7b bus note said "134 exact+identifiable, 43 of those
  regime-sensitive". The right figure is 33 (exact+identifiable+regime_changes_form);
  43 is exact+regime_changes_form. Lookup totals: 172 register columns, 144 exact, 134 identifiable.
- Lane state at stop: all receipts landed (B1 PASS, B1s KILL, B1t KILL, B1u PASS,
  B2 PASS, B3 KILL, B3g KILL, B5 KILL, B5b PASS, B6 PASS, B6b PASS, B7 KILL,
  B7b KILL, bounty C7d KILL, C1 bounty PASS then retracted). Reusable pieces:
  primordial/soup/b1 (world forms + oracle), b6/fused.py (exact fused
  closed-loop rollout, C-audited), b7 (structural affine tools + C7 lookup).
  Substrate gw-sub-b on 6391 left running. Loop stopped at operator request.

## Round 2 -- HILL CLIMBERS, Nestor-B[m1-fd63b6d8], 2026-09-14

- B-R2-1 (clause A, w4 train128_held64): int4 linear brain + nibble codebook, 48 B,
  E10 closed condition otherwise unchanged. 8 run seeds: held64 median 98.20, IQR 2.80
  (94.89..99.90). Oracles clean on rs0 (world 0/16, skip_lin 16/16; brain 0 mm, skip-odd 16/16;
  fused==numpy). check vs baseline front: PASS parity at 48 < 192 B (open-loop 94.04).
- NOT parity with the float linear baseline (98.76 @ 312 B, 4 runs, IQR null): short by 0.56.
- Defect (shared lib, asked A+E): qd_ledger check builds the front from ALL rows, so my row
  evicts the open-loop baseline and the same numbers read FAIL after append.
- Hazard: open-loop genome stores 4-bit values one per byte; its 192 B is 2x its information.
- B-R2-2 (port, unchanged code): w3 32 B median 104.79 IQR 2.15 -> PASS parity vs open-loop
  102.71 @ 128 B (not parity with float linear 105.58 @ 208). w1 52 B median 57.64 IQR 19.37
  -> FAIL vs linear 61.40 @ 344. Joint 2-world claim fails; prior w3 0.55 / w1 0.5.
- w1 run seeds span 36.8..80.2: the search, not the genome, looks like the bottleneck there
  (float baseline had 4 runs, no IQR). Filed as an anomaly for D.
- E fixed qd_ledger check (edb064317, front over baseline rows); my w4 repro now PASS stably.
- B-R2-3 (train8_held64, E9 setup 200x128 on E6's 8 train seeds): int4 linear+nibble vs float
  linear. w4 48 B 87.54 IQR 9.23 (>= 86.885) PASS; w3 32 B 104.95 IQR 5.48 (>= 98.115) PASS;
  w1 52 B 43.63 IQR 7.26 (>= 27.565; also > 35.46 + 0.5 IQR) PASS. Oracles clean all rs0.
  w4 sits 2.4 below the float median: parity by the IQR tolerance, not a tie. Priors .6/.65/.5.
- B-R2-4 (bit-width descent, w4 train128): first int3 attempt ABORTED (LuaArchive needs glen%4==0;
  aborted row, commit 075bf0f42 is untagged: PM_TAG not exported in that call). Padded like E4/E7.
  Control: bits=4 re-pack reproduces B-R2-1 genomes byte-exact and held64 99.8193.
  int3 40 B: median 97.52 IQR 1.07, oracles clean -> PASS vs open-loop 94.04 @192 (prior .6).
  int2 32 B: median 97.92 IQR 0.73 but skip-odd cheat caught only 13/16 elites -> INELIGIBLE.
  The 3 blind elites (0, 0, 1 mismatched rows) do NOT have more zero odd weights (.31-.34 vs
  run .19-.44): the brain oracle's cheat is weak on low-precision brains. Anomaly + ask to E.
- EPOCH 1 closed (rows 66, receipts 8: PASS 6 / FAIL 1 / INDET 1). D3 answered the w1 anomaly:
  WORLD, not int4 (float linear w1 IQR 14.7); w1 8-seed IQR moves with the RNG family (19.4 vs 9.0),
  so any w1 margin built on 0.5 x IQR is fragile.
- B-R2-5 (int3 ports; exp ids carry the B-R2-4-int3 prefix from the code): all oracles clean.
  train8: w4 40 B 91.38 IQR 7.56 PASS (above float 89.94); w3 28 B 103.96 IQR 3.46 PASS;
  w1 44 B 40.11 IQR 15.65 PASS (fragile per D3). train128: w3 28 B 106.86 IQR 3.94 PASS, and
  above float linear 105.58 @ 208 (4 runs) outright; w1 44 B 58.44 FAIL vs 61.40. 4/5, priors
  .5/.6/.5/.6/.3.
- B-R2-6 (codebook shrink, int3, train128): int3 elites used a median 2 (w4) / 3 (w3) of 8 rows on
  HELD8. Control acts=8 re-pack byte-exact, held64 97.0566 reproduced. Oracles clean (skip-odd 15/16).
  w4 A4 20 B 98.20 IQR 1.64 PASS; w4 A2 12 B 97.18 IQR 1.16 PASS; w3 A4 16 B 106.83 IQR 1.32 PASS
  (also above float linear 105.58 @ 208). 3/3, priors .6/.35/.55.
- A 12-byte brain choosing only abstain vs one fixed action is within 1.6 of float linear on w4:
  the held-out metric may mostly reward abstain timing. Filed as an anomaly (possible easy metric).
- B-R2-7 (small-codebook ports, int3): A2 train8 w3 8 B 109.89 PASS (skip-odd exactly 14/16);
  A2 train8 w1 12 B 60.57 PASS (w1 fragile); A2 train8 w4 12 B 95.92 and A2 train128 w3 8 B 103.13
  INELIGIBLE (skip-odd 13/16); w1 train128 A2 12 B 58.19 and A4 24 B 57.84 FAIL (w1 train128 0/4 so far).
- E landed powered brain cheats (33038855e: ablate_top, shift_action floor, input_invariant).
  Posted B-R2-8 predicate BEFORE use: re-adjudicate the 3 INELIGIBLE cells on committed rs0 genomes.
- B-R2-8 result: all 3 meet the rule: ablate_top 16/16, shift_action 16/16, 0 input-invariant,
  honest 0 mismatched. Now PASS on recorded medians: int2 w4 train128 32 B; a2 w4 train8 12 B;
  a2 w3 train128 8 B. Corrected QD ledger rows appended (supersede the 'cheat' rows).
- a2 w3 train8 (PASS on skip-odd 14/16) re-scores 13/16 under E's row sampling but ablate 16/16:
  the 14/16 skip-odd bar was sampling-sensitive; powered cheats are the better control.
- EPOCH 2 closed (rows 117, receipts 13: PASS 10 / FAIL 3). No quiesce order from A.
- B-R2-9 (8 B floor: int2 codes + A2, pad-to-4 sets the floor; exp ids carry B-R2-6 prefix from
  code; binding rule --brain-cheat powered, fixed before the run): w4 train8 91.80 IQR 1.50 PASS
  (above float 89.94); w1 train8 55.21 IQR 3.31 PASS (> 35.46 + 0.5 IQR); w4 train128 97.19
  IQR 0.47 PASS but ablate_top exactly 14/16 with 2 input-invariant elites (open loop in effect).
- Input-invariant 8 B elites scoring ~97 on w4 add weight to the easy-metric anomaly.
- B-R2-10 (8 B int2 A2, powered rule): w1 train128 58.59 IQR 4.94 FAIL (5/5 B variants 57.6-58.6
  < 61.40) -> stop rule fired: w1 train128 recorded as a protocol ceiling (D3 float linear 8-seed
  median 59.2 is itself below the 4-run baseline). w3 train8 106.88 IQR 2.58 PASS (above float
  103.16); w3 train128 103.97 IQR 0.87 PASS (ablate 15/16, 1 input-invariant). Priors .2/.55/.5.
- Every baseline cell except w1 train128 now has an 8 B B cell at clause A parity.
- QUIESCE (A, 1789421177690-0): no task in hand; rows/receipts/journal pushed; EPOCH 3 (final)
  posted; no open claims; loop stopped. Carry-forward for round 3: (1) re-seed round 1 baselines
  with >=8 runs + IQR (w1 train128 bar is a 4-run draw); (2) easy-metric anomaly (2-action and
  input-invariant 8 B brains near float linear on w4) needs D's constant/random-action discriminator
  before more clause A compression on held64 counts; (3) bind E-T3 powered cheats, not skip-odd;
  (4) 8 B floor is pad-to-4, so bytes below it need a different archive, not a smaller genome.

## Round 4 (Nestor-B[m1-e27957ca], 2026-09-15)
- Boot at 35d8ef0b5: warmup rc 0, pytest rc 0 (209 passed, 1 skipped), worker B serving, hello posted. Launch gate GREEN (A 1789448010873-0).
- Screen: exactly one SURVIVED cell, w13 train128_held64 (gate_in|HOLD floor 166.47 = 2-action gate; float linear 182.72 ci [173.41,188.11] @ 200 B; w13 D=5 A=8 W=1). PASS needs median >= 181.906 at < 200 B; headroom is only 16.25.
- B-R4-1 (predicate 1789448206539-0, code 35290330b): QLin ladder int4a8 28B .. int2a2 4B at the M2 budget, seeded sampler, E-T3 powered oracles, judge qd_ledger check. Smoke (3 gens, dev, not committed) clean. Job 47dc1f8a0de8 submitted, ttl_cpu_s 3000.
- B-R4-1 result (rows e21660f52; job TIMEOUT at 3000 CPU-s inside the last rung, 6 of 7 rungs summarized; int2a2 4B has rs0 only, no verdict). Oracles clean on all 7 rs0 (world 0 failing, skip_lin 16/16, fused==numpy, brain honest 0, shift 16/16, ablate_top 16/16, 0 input-invariant).
  judge (qd_ledger check, gate_in|HOLD): int4a8 28B 175.32 FAIL progress 0.544 CI [-0.10,1.42]; int3a8 24B 167.67 FAIL 0.074 [-0.07,1.20];
  int2a8 16B 163.66 BELOW_FLOOR -0.173; int3a4 12B 165.40 BELOW_FLOOR -0.066; int2a4 8B 163.19 BELOW_FLOOR -0.202; int3a2 8B 160.32 BELOW_FLOOR -0.379 (CI all below floor).
  No PASS: first item open. Progress falls monotonically with weight precision; <= 16 B sits under the 2-action gate. int4a8 run seeds span 158.8..195.6 (the float baseline spans 156.8..189.2): 8-seed CIs are wider than the headroom (16.25).
  QD ledger rows appended for the 6 summaries. Cost: ~500 CPU-s per rung at 4 threads (TTL undersized by ~1 rung).
- Next (B-R4-2): climb toward float precision under 200 B -- int8a8 52B, int6a8 40B, int5a8 36B -- plus finish int2a2 4B; ttl 3000 per ~5 rungs is short, set 4000.
- Push of B-R4-1 hit the shared cells.jsonl conflict (push.py aborted, exit 4); manual rebase with union merge of cells.jsonl only, 103 lines, 0 dups, all parse; pushed a8da4f1d4 (on integration). Result posted 1789449146854-0.
- B-R4-2 (predicate 1789449162773-0): int8a8 52B, int6a8 40B, int5a8 36B, int2a2 4B, same code/budget/oracles/judge, ttl 4000. Smoke: pack/unpack exact at bits 8/6/5. Job 366394a41746 submitted.
- B-R4-2 so far (judge): int8a8 52B 174.15 FAIL progress .473 CI [.15,.89]; int6a8 40B 176.53 FAIL .619 [.38,1.35]; int5a8 36B 193.25 PASS 1.648 [.65,2.08], oracles clean, 0 input-invariant.
  NOT claimed: the ladder is non-monotone and bits enter the seed tuple. Per-seed read: int5 held [200.3,177.0,189.4,196.0,190.9,201.0,173.8,195.6], train median 194.8 (held tracks train), 0 shared top genomes, budget_ok.
  Predicate B-R4-3 posted: replicate int5a8 (int4a8 contrast) on run seeds 8-15, after B-R4-2 ends.
- B-R4-2 end (job ok, 2171 CPU-s): int2a2 4B 159.55 BELOW_FLOOR -0.426 (CI wholly below floor). QD ledger rows appended for the 4 summaries (ledger() now takes the exp id from the rows file; it had hardcoded B-R4-1's).
- B-R4-3 (job ok, 1114 CPU-s; run seeds 8-15; oracles clean, 0 input-invariant): int5a8 36B median 182.82 PASS progress 1.006 CI [.56,1.50]; int4a8 28B (contrast) 184.35 PASS 1.100 CI [-.58,1.84].
  Pooled 16 seeds (check_r4 with runs=16, report-only): int5a8 189.02 progress 1.388 CI [.72,1.60] PASS, 10/16 seeds >= 181.906; int4a8 179.59 progress .807 CI [-.10,1.42] FAIL, 8/16.
  CLAIM (first item): int5a8 36B is the smallest-bytes rung that PASSes on BOTH preregistered seed sets (0-7 and 8-15) and pooled; 36 B vs the 200 B float baseline (5.6x smaller).
  NOT claimed: int4a8 28B PASS on seeds 8-15 only -- choosing that set is seed shopping; its verdict flips FAIL/PASS by seed set and pools to FAIL.
  Finding for D: 8-seed clause A verdicts on w13 t128 flip with the run-seed set (baseline itself has only 5/8 seeds >= the pass line); filed as an anomaly.
- Receipt B-R4-3 PASS filed (1789450196529-0), mirror pushed c99ab44bc (on integration). Operator notified. A 1789449028866-0: w13 baseline is the top-16 readout (D-R4-1: it reads below top-1 in many cells); a w13 PASS carries that caveat, nothing promoted in the test launch; keep working.
- Loop iteration 1: B-R4-4 (shrink via codebook): int5a4 20B, int4a4 16B, int5a2 12B, seeds 0-7, ttl 2400. Rule fixed before the run: front membership needs PASS on seeds 0-7 AND 8-15.
- B-R4-4 (2 segments across the EPOCH 1 stop flag, 1392 CPU-s; oracles clean, 0 input-invariant): int5a4 20B 183.82 PASS progress 1.068 CI [.81,1.40]; int4a4 16B 189.91 PASS 1.442 [.86,1.76]; int5a2 12B 167.60 FAIL .070 [-.18,.14].
  Both PASSes are single-set: NOT claimed. B-R4-5 replicates int5a4 + int4a4 on run seeds 8-15. Front stays int5a8 36B until then.
- B-R4-5 (job ok, 1019 CPU-s; seeds 8-15; oracles clean on rs8, 0 input-invariant): int4a4 16B 191.14 PASS progress 1.518 CI [.22,1.91]; int5a4 20B 181.02 FAIL .895 [.50,1.15].
  Pooled 16 (report-only): int4a4 191.14, 1.518, CI [.78,1.76], 11/16 seeds >= 181.906; int5a4 182.42, .981, CI [.80,1.15], 9/16.
  FRONT UPDATE (rule fixed before B-R4-4): int4a4 16B PASSes on seeds 0-7 (1.442) AND 8-15 (1.518) -> new smallest claimed cell, 16 B vs 200 B (12.5x). int5a4 20B does not join (8-15 FAIL). Non-monotone again: 16B replicates, 20B does not -- another seed-set-dependent verdict on this cell (see anomaly 1789450127495-0).
- Receipt B-R4-5 PASS filed (1789451132642-0), mirror pushed 403b6dda7 (on integration); operator notified. FRONT: int4a4 16B (2 seed sets). Superseded as smallest: int5a8 36B.
- A 1789450588653-0 / 1789451109447-0 (push race, E incident): until quiesce, push only with the worker parked -- SET pm:jobs:B:stop, wait state stopped, ops.push, DEL; no push within 2 min of an epoch boundary. My earlier pushes ran with the worker idle and nothing queued; adopting the procedure from here. Push lock 898900b4e rolls out at quiesce.
- B-R4-6 (job ok, 1353 CPU-s; seeds 0-7; oracles clean on all rs0, ablate_top 16/16 incl. int4a3 which was 14/16 at 3 smoke gens): int4a3 12B 180.19 FAIL progress .845 CI [-.41,1.87] (seeds 156.9..199.2); int3a3 12B 163.25 BELOW_FLOOR -.198; int6a2 12B 168.31 FAIL .113 CI [.04,.18] (seeds 164..170, pinned at the 2-action gate).
  No 12B rung PASSes seeds 0-7: front stays int4a4 16B. a2 genomes sit at the gate regardless of weight precision (int2..int6). No rerun of int4a3 (a failed first set is not fished).
- B-R4-7 readout sensitivity (predicate 1789451717396-0, job 9e05da5173df ok, 72 rows, 1.5 CPU-s): re-read B's saved elites; top-16 re-read reproduces all 64 committed held64 exactly. Progress readout-for-readout vs D-R4-4 baseline medians (top16 182.72 / top1 189.53):
  int4a4 16B  0-7 1.442 | top1 1.121;  8-15 1.518 | top1 1.283  -> FRONT SURVIVES the readout caveat (A 1789449028866-0) on both seed sets.
  int5a8 36B  0-7 1.648 | 1.446;  8-15 1.006 | 1.087.   int5a4 20B  0-7 1.068 | 1.198;  8-15 .895 | 1.073 (top-1 flips its 8-15 verdict; still not claimed, judge is top-16).
  int4a8 28B  0-7 .544 | .555;  8-15 1.100 | 1.367 (seed-set flip under both readouts).
  Validation readouts not computed (no held-back split in B's TRAIN128 runs). Rows committed locally; push + post after the 02:01:49 quiesce with the worker parked.
- QUIESCE (A 1789452239356-0, test launch 1 over). No job in hand, 0 pending. Round 4 B totals: 254 rows (B-R4-1..7; 1 timeout row), 2 receipts (B-R4-3 int5a8 36B PASS, B-R4-5 int4a4 16B PASS), 20 QD ledger cells, 0 open claims. Stale checkpoint C:/Users/jcrai/lab/pm-data/ckpt/B/47dc1f8a0de8.pkl is B-R4-1's TTL-killed job (the worker does not unlink on kill), not a paused job; left in place.
  Resume notes for round 4 continuation: FRONT int4a4 16B (2 seed sets, holds under top-1 readout). Open leads: (1) int4a3 12B FAIL .845 on 0-7 with seeds 156.9..199.2 -- only worth a larger-n design, not a rerun; (2) the n=8 seed-set instability (anomaly 1789450127495-0, D-R4-2 covers it) should set whether the next front step needs n=16 per set; (3) a2 codebooks are pinned at the 2-action gate at every precision -- do not spend there. Code: primordial/cohorts/b/r4_1_qladder.py, r4_7_readout.py.

## Round 5 pilot -- Nestor-B[m1-3e1d1f00], worktree nestor-r5-b (prompts_r5/B.md)
- Boot 07:08 (T+11): ff to eca1a725b; comms tag m1-3e1d1f00; warmup ok; suite rc 0 (384 passed, 1 skipped, sparse tree); worker B serving; bus hello.
- Eligibility from code (w13_eligibility): SURVIVED gate_in|HOLD, floor 166.47, baseline 183.91 @ 200 B (top1_train; runs_total 32, rng_family_count 4, runs_per_family 8), denominator 17.4375. Round 4 w13 claims invalidated (op 15), not cited.
- Code c2e9b5ec3 (integration): primordial/cohorts/b/r5_1_candidate.py (job = CANDIDATE_N int4a4 16 B on R16 seed convention; reread_job = PILOT reread of saved r4 archives) + 4 tests rc 0.
- Predicates 1789470866771-0 (B-R5-1 CANDIDATE_N) and 1789470866786-0 (B-R5-2 PILOT reread) posted before any run.
- B-R5-1 submitted with envelope PILOT wall 620 / cpu 2150 (measured basis B-R4-5: 63.7 CPU-s, 16.6 s wall per run). Over the 1200 CPU-s ceiling: refusal expected -> PRODUCTION_CANDIDATE, not trimmed.
- B-R5-1 job 35c460947277 REFUSED by admission (07:21): STAGE_BUDGET_REFUSAL CPU_BUDGET_OVER_CEILING, 2150 > 1200. Stub 1789470879444-0. PRODUCTION_CANDIDATE FILED on pm:production_candidates with the measured basis (B-R4-5 done record, 63.7 CPU-s/run) + a row in B-R5-1 rows; result posted to A. Not trimmed, not split. No round 5 w13 verdict.
- Next iteration: B-R5-2 PILOT reread (predicate 1789470866786-0); judge INELIGIBLE(CANDIDATE_N) expected.
- B-R5-2 PILOT reread job 4b7883cbb0c7 ok (1.7 CPU-s, 8-thread token, rows 7335089f2): int4a4 16 B under top1_train, runs_total 16, rng_family_count 1, runs_per_family 16 (round 4 stream 4410). candidate_score 194.23 CI [187.78, 201.19]; floor 166.47; baseline 183.91 @ 200 B; progress_above_floor 1.59 CI [1.22, 1.99]; wall 0.42 s reread only (QD cost is in the PRODUCTION_CANDIDATE); VRAM none.
  Control: 16/16 selected elites use observations (W zeroed -> 159.0, 105.8 on rs 4/10; input_invariant 0); oracles clean on rs 0. One run seed (rs 0, 156.84) is below the floor.
  Judge INELIGIBLE(CANDIDATE_N), as predicted: PILOT, no verdict, no claim. The only eligible test is the filed PRODUCTION_CANDIDATE.
- B-R5-2 receipt 1789471092290-0 (INDETERMINATE, PILOT; guard 9/9 OK). EXPECTED_REFUSAL_OBSERVED emitted 1789471014088-0.
- Loop iteration (07:18): beat, inbox empty for B, no job. First item complete; worker idle. No further w13 work inside PILOT ceilings (CANDIDATE_N is the PRODUCTION_CANDIDATE).
- OPERATOR 20 (A 1789471490556-0, code d64580db2): PILOT cpu_budget_s ceiling 1200 -> 2400; wall ceilings unchanged. Verified in envelope.py after ff.
- 07:42 B-R5-1 RESUBMITTED as job 93fc506187dc, envelope identical (PILOT, wall 620, cpu 2150; runs_total 32, rng_family_count 4, runs_per_family 8). Old worker stopped (no surviving process), new worker on d64580db2. Predicate 1789470866771-0 reused (a fresh id would postdate the 07:15 PRODUCTION_CANDIDATE row in the same rows file); reuse noted to A 1789472533006-0. Not enlarged. Worker waiting_cpu at submit (both tokens held).
- 07:43:23 job 93fc506187dc got CPU token slot 1 (8 threads). 07:46:23 segment 0 PAUSED at the epoch 2 boundary (T+50, F9 checkpoint): 11/32 runs, 564.5 CPU-s, 196.1 s wall (~51 CPU-s, ~17.7 s qd wall per run; budget_ok all). Auto-requeued segment 1ea19737298e resumed 07:47 (token re-granted); budget remaining 1585 CPU-s / 424 s wall vs projected ~1080 / ~375 for 21 runs (wall margin thin). Rows not pushed while the job is live (paused jobs resume mid-push).
- 07:52:42 segment 1ea19737298e ok. B-R5-1 JUDGE PASS at CANDIDATE_N (runs_total 32, rng_family_count 4, runs_per_family 8): int4a4 16 B, candidate_score 194.22 CI [186.33, 198.33], floor 166.47, baseline 183.91 @ 200 B, progress_above_floor 1.591 CI [1.139, 1.827]; 1637.3 CPU-s, 563.8 s wall, 2 segments; VRAM none.
  Control 32/32 use observations (W zeroed 159.0), input_invariant 0; oracles clean. Verification: 32/32 saved elites re-read, 0 mismatches. Per-family progress 4200 1.783 / 2101 1.681 / 3303 1.184 / 5501 1.148; 3/32 below floor (3303 rs 2, 6, 7). Same-lane check, not a promotion.
  Push rebased (7ae496e45 rewritten); receipt cites the integration tip 4e69568e8. PRODUCTION_CANDIDATE 1789470947462-0 marked SUPERSEDED.
- 08:05 (T+69) loop iteration: H REPLAY B-R5-1 AGREE, 0 mismatches (predicate 1789473448642-0, rows a81a0e6e6, code 6a9f29d96): per-run values/shas, pooled median + CI, sample stamp, progress, judge PASS, obs-use control all equal B's. Cross-lane, same model family: still not a promotion (oracles not re-run by H). No job; worker idle; nothing further for B inside the pilot.
- 08:31 (T+95) loop iteration: full unpiped XRANGE audit of the bus since boot (every inbox read this session was piped through tail; see memory bus_bodies_truncated): 21 messages to B/ALL, none missed that needed B action. Relevant context: D-R5-1 REFUTED the family-4200 dependence -- w13 train128 SURVIVED holds with 4200 removed (leave-one-family-out 4/4, top1_train). No job; nothing further for B before NO_NEW_WORK (T+100).
- 08:53 (T+117) ROUND 5 CLOSE for B: controller stopped the worker at drain (stop flag set). Unpiped read since the last audit: NO_NEW_WORK, EPOCH 4 boundary, C final -- nothing for B.
  B FINAL: 1 Clause A attempt, B-R5-1 PASS at CANDIDATE_N (receipt 1789473262958-0, progress 1.591 CI [1.139, 1.827], 16 B vs 200 B); B-R5-2 PILOT reread INDETERMINATE (1789471092290-0); 1 admission refusal before operator 20; PRODUCTION_CANDIDATE superseded; H replay AGREE. 0 open claims. Not a promotion (same-model checks only; family 3303/5501 weaker, 3/32 below floor).

## Round 6 (Nestor-B[m1-5f942a2a], clock pm:round:r6 start 11:00, NO_NEW_WORK 14:20)

- 11:13 (T+13) boot: ff at bc5b661eb, warmup rc 0, suite 435 passed / 1 skipped rc 0, worker lane B started, hello (lane B tag was the stale R5 m1-3e1d1f00, no live heartbeat, replaced without takeover). Inbox read unpiped: nothing for B beyond the R6 contract.
  Item 1: accounting() re-run -> 102,400 evals per run both sides, ratio 1.000, comparator_fires False. Item 2 therefore skipped (rule not fired). pm:replication: 0 records.
  Added job wrapper primordial/cohorts/b/r6_1_budget.py (no harness module edited) so the accounting gets its own rows + guarded receipt (old rows predate any new predicate). Oracle cross-checks reader evals vs the R5 receipt qd_genomes_per_run and RECIPE search_evals. Tests 2 passed.
  Note for item 3: r5_1_candidate.job hardcodes GS=13 / PRESSURE train128; a replication on another cell must be judged against that when a record appears (no edit now).
- 11:18 DEADLOCK: worker B state 'stopped' -- stale R5 epoch-4 flags pm:jobs:{B,C,D,E}:stop='4' ttl -1. Reported to A (1789485092148-0), did not delete controller keys; A cleared the 4 keys ~11:19 (1789485113451-0, filed D12, clock not extended). Worker took the job without restart.
- 11:19 B-R6-1 predicate 1789485028907-0 (code a614746ff, refs/pm/pred pinned) -> job 5fe1b04500f5 ok (0.19 CPU-s, 1 row) -> rows 59f6047db pushed, ancestor of integration verified -> RECEIPT 1789485175950-0 (INDETERMINATE accounting record, guard 10/10 OK).
  Result as predicted: 102,400 evals/run both sides, ratio 1.000 (total and train episodes also 1.000); comparator_fires False; oracle crosscheck clean. ITEM 2 SKIPPED (rule not fired). No CPU comparison claimed. pm:replication still 0 records -> item 3 waits; loop polls it each iteration.
- 11:40 (T+40) loop iteration: beat; inbox read unpiped (predicates E-R6-1, D-R6-1 LOO on B-R5-1, C-R6-AP-01/02, C-R6-01, E-R6-2; EPOCH 1 boundary) -- nothing needs B action. pm:replication 0 records. No job; worker stopped by the boundary drain (normal). Monitor bg3c6v40k watches pm:replication (15 s poll). Journal committed at a later quiet point, not during the controller's boundary commit.
- 12:10 (T+70, epoch 2 running) loop iteration: beat; inbox unpiped. D-R6-1 ROBUST (receipt 1789488540808-0): B-R5-1 PASS holds leaving out any one family, progress CI low > 0.95 in 4/4, thin margin at leave-4200-out (0.9964); anomaly 1789485427773-0 (3303 below-floor runs) stays OPEN. B does not act on it (no retune, no re-run). E-R6-3 dispatch surface done (not B). pm:replication 0 records; monitor re-armed (b4isqjh5r). No job.
- 12:40 (T+100, epoch 3 running) loop iteration: beat; inbox unpiped (D-R6-2..6b anomaly discriminators, EPOCH 2 boundary, A ruling 1789489756428-0). A ruling: F-R6-2 fingerprint covers the job fn module only; every cohort restarts its worker after editing ANY harness module. B has edited no harness module this round (only added its own job module r6_1_budget.py, which ran on the live worker), so no restart. pm:replication 0 records; monitor bdvvnt8oo. No job.
- 13:10 (T+130, epoch 4 running) loop iteration: beat; inbox unpiped (D-R6-7..10, EPOCH 3 boundary) -- nothing for B. pm:replication 0 records; monitor bi0sz1wks. No job. NO_NEW_WORK at 14:20 (T+200).
  G screen read-only (G-R16-cells.jsonl on integration): 7 cells in R6, 0 SURVIVED (w1/w7/w26 t128 PENDING, w1/w7 t8 HELD, w21 t128 + w30 t8 CULLED); every cell_job ran replication_check, published [], refused None -> trigger live, no survivor.
- 13:40 (T+160, epoch 5 running) loop iteration: beat; inbox unpiped (D-R6-10/11, D ROUND 6 FINAL, EPOCH 4 boundary) -- nothing for B. pm:replication 0 records; monitor bvgjthf9z. No job. Plan: at NO_NEW_WORK with 0 records post item 3 NOT_REACHED + B ROUND 6 FINAL.
- 14:10 (T+190) loop iteration: beat; inbox unpiped: A 1789495487277-0 asks each lane for ONE '<L> ROUND 6 FINAL' note to A before 14:40, then stop the F7 worker. pm:replication 0 records. Holding NOT_REACHED until NO_NEW_WORK (14:20) as the prompt's rule says -- a G cell job could still publish before then. Monitor b1ge0tbyr covers 14:20.
- 14:12 close_sweep r6 (read-only): 19 rows files, 16 cited; unreceipted D-R6-11, E-R6-1, G-R16-cells -- no B file. B production candidates this round: none.
  Own slip: monitor b1ge0tbyr was armed ~13:45, not ~14:04 as I noted, so it expired at 14:15 before NO_NEW_WORK; a one-shot wait (blpyy4ob6) covered 14:20.
- 14:20:06 NO_NEW_WORK passed with pm:replication 0 records -> ITEM 3 NOT_REACHED posted (not evidence against B-R5-1). B ROUND 6 FINAL posted to A. Worker stopped by B (no queued jobs, 0 pending).
  B ROUND 6 FINAL: 1 receipt (B-R6-1 1789485175950-0, accounting, comparator_fires False); item 2 SKIPPED (rule not fired); item 3 NOT_REACHED; 0 unreceipted B rows; 0 PCs; 0 open claims. B-R5-1 stays a SURVIVING CANDIDATE, not promoted.

## Round 7 (Nestor-B[m1-86b1c645], clock pm:round:r7 start 17:37:49, NO_NEW_WORK 02:37:49, drain 03:07:49)

- 17:49 (T+11, epoch 1) boot: ff already at 7da5e86fd; warmup rc 0; suite 568 passed / 1 skipped rc 0; worker lane B started from this worktree (pid 28376; group worker-B has 1 consumer = m1-86b1c645, 0 pending, no stale prior-round worker); hello 1789508883575-0.
  Inbox read unpiped (to a file, all 66 lines): R7 CLOCK LIVE (A 1789508300210-0), E predicates E-R7-1/2/3/O8 -- nothing for B. Backend cpu_sequential / GPU_REJECT.
  Only item: REPLICATION of frozen B-R5-1 per pm:replication record. pm:replication 0 records, 0 published keys -> idle (bus beat only). Monitor bd22ejf9b polls the stream every 15 s.
  Carry-forward from R6: r5_1_candidate.job hardcodes GS=13 / train128; check that against a record's cell before submitting (no edit now). No harness module edited.
- 18:19 (T+41, epoch 1) loop iteration: beat; inbox unpiped to file (97 lines): predicates C-R7-AP-01, D-R7-1 (C-R6-AP-01 gens sweep), D-R7-2 (family 3303 below-floor runs of B-R5-1, same-stream baseline + obs use) -- D-R7-2 is D's anomaly work on B-R5-1; B does not act (no re-run, no re-read). pm:replication 0 records; monitor bm4n7w927 re-armed (bd22ejf9b expired, no record). No job; worker idle.
- 18:49 (T+71, epoch 2) loop iteration: beat; inbox unpiped to file (71 lines): EPOCH 1 boundary; predicates C-R7-AP-02, D-R7-2b (D-R7-2 rule unchanged after D's own I1 bug), C-R7-01.
  Relevant, no B action: A 1789512067159-0 -- O8 draw 24 graft_fused_eq_numpy False (FusedRollout != numpy on one real train128 genome; FusedRollout is the fast path under B-R5-1 too). Routed to D as priority 1; A: "B/G: no action; your paths are unchanged unless D's discriminator says otherwise". B watches for D's receipt; a replication run would still require its own oracles clean.
  pm:replication 0 records; monitor bv9feoro9 re-armed. No job; worker idle.
- 19:19 (T+101, epoch 2) loop iteration: beat; inbox unpiped to file (66 lines): E-R7-1 live Clause B pair w14->w13 32/4/8 (O8 gate INSTRUMENT_ADMISSIBLE, 40 draws, false_pass 0, 2 judged_indeterminate); C-R7-AP-02 amendment (6 -> 8 stored bytes, C's own defect); D-R7-3.
  Tracking, no B action: D-R7-3 (predicate 1789512977272-0, evidence_class OBSERVATION, 2 loci family 2101) localizes the fused != numpy divergence -- 2 of 1280 O8 graft runs, FusedRollout vs e7_run.rollout, the fast path under B-R5-1. B waits for D's receipt; no re-run or re-read of B-R5-1 either way.
  pm:replication 0 records; monitor b7u6sxh9j re-armed (bv9feoro9 expired, no record). No job; worker idle.
- 19:49 (T+131, epoch 3) loop iteration: beat; inbox unpiped to file (88 lines): EPOCH 2 boundary; D-R7-3b; D-R7-4 (C-R2-02 rent sweep). No B action.
  Tracking (still no receipt): D-R7-3 INDETERMINATE on D's own defect -- job emitted status 'observation', not in fabric.rows.STATUSES, so every row was refused (0 accepted); D-R7-3b re-runs the same rule with status 'record' and evidence_class OBSERVATION in the row. D disclosed, before the re-run, that it had read the refused wrappers: both cases label BRAIN_NEAR_TIE -- d24 genome 14 numpy 20871 vs fused 20868, one env diverging at tick 30 on idx, where the numpy float32 einsum logits tie EXACTLY (gap 0.0) and the sequential float32 kernel, linear_act_row and the float64 reference all pick 4 (ref top-2 gap 1.08e-07, clear_rows False). Read as disclosed-in-advance values on refused rows, not a verdict; B waits for D-R7-3b's receipt and does not re-run or re-read B-R5-1 either way.
  pm:replication 0 records; monitor bcgtn6eed re-armed (b7u6sxh9j expired, no record). No job; worker idle.
- 20:19 (T+161, epoch 3) loop iteration: beat; inbox unpiped to file (92 lines): D-R7-3b resolution + A ruling, D's PC, D-R7-5, D-R7-6. No B action; nothing B tracks is still open.
  CLOSED for B: ANOM-1789512027239-0 RESOLVED (D receipt 1789516880015-0, OBSERVATION) -- both O8 mismatches are BRAIN_NEAR_TIE, ONE env at ONE tick each, where the float32 linear logits tie exactly (f64 top-2 gaps 1.08e-07 / 1.78e-07, neither a clear row) because numpy's Linear.logits does einsum-then-bias and linear_act_row does bias-then-features; argmax breaks the tie to the lower action index. NEITHER path is consistently right (d24 numpy ties low, d31 the kernel ties low). Deterministic: 1 thread == 8 threads, 3 repeats agree; no thread race, no batch effect. Scope 2 of 1280 O8 graft runs on UNTRAINED random donors; trained genomes not covered.
  A ruling 1789516925555-0: (1) no mid-round change to fused_eq_numpy -- it stays exact-equality until round 8, since B, G and E all depend on it and three verdicts were emitted tonight under it; (3) stated for the packet: a tie-break artifact at a ~1e-7 margin is NOT a logic error and "does not impugn B-R5-1 (its own fused==numpy oracle was clean on 32/32 runs)". D filed the tie-aware gate as PRODUCTION_CANDIDATE 1789517018361-0 (prospective, no patch, no r7 verdict revisited). B's replication path is unchanged: a record's run would still be judged under the exact gate, oracles clean on every run.
  pm:replication 0 records; monitor b280afhdc re-armed (bcgtn6eed expired, no record). No job; worker idle.
- 20:49 (T+191, epoch 4) loop iteration: beat; inbox unpiped to file (104 lines): D-R7-7, C-R7-AP-03, D-R7-8, EPOCH 3 boundary. No B action; B has no open tracked items since the fused!=numpy resolution.
  Standing rule noted (A 1789518298673-0 to D,C,E,G,B): admission decides whether a job MAY run, not whether it SHOULD; a discretionary job that would hold one of only two shared CPU tokens at low utilisation gets sized and FILED, not run, because G's screen is the round's throughput path and the broker is not FIFO. B has no discretionary additions by charter (REPLICATION only, idle between records), so the rule changes nothing here; it does bar B from inventing filler work while waiting.
  pm:replication 0 records; monitor b3j1josg5 re-armed (b280afhdc expired, no record). No job; worker idle.
- 21:19 (T+221, epoch 4) loop iteration: beat; inbox unpiped to file (153 lines): D-R7-9 (C7 seed stability), D-R7-10 + D-R7-10b (byte-parity re-rank). No B action; no open B items.
  Noted, not B's: D-R7-10 asks the Clause A-adjacent question -- E9 ranked linear > tt_feat > tt_digits on held-out score while genome sizes run the other way, so does the fewest-byte family still win at MATCHED parameter count (tt_feat@rank1 548 B vs linear 288 B)? D's own item; B neither reads nor runs it. D-R7-10 died on D's envelope error (cpu_budget_s set equal to wall while the fused rollout uses 8 threads -> status timeout at 2400 CPU-s, 97/168 rows, no summary, INDETERMINATE); D-R7-10b re-runs the full set at cpu_budget_s 20000. Relevant to B only as a ceilings lesson: a checkpointable job's cpu_budget_s must be sized in CPU-seconds at the granted thread count, not copied from wall_budget_s -- if a replication record arrives, B's envelope inherits B-R5-1's measured 1637.3 CPU-s / 563.8 s wall shape, not a wall-equals-cpu guess.
  pm:replication 0 records; monitor b29n06c19 re-armed (b3j1josg5 expired, no record). No job; worker idle.
- 21:50 (T+252, epoch 5) loop iteration: beat; inbox unpiped to file (120 lines): D-R7-11 + D-R7-11b, EPOCH 4 boundary, C-R7-AP-04 feasibility scan, and A's mirror request 1789522135178-0 followed by A's CORRECTION 1789522231772-0 (A's own checkout was 205 commits behind; after ff 22 rows files / 20 cited; "B, C, D, E: mirrors current, NO action"). Real items are G's and D's, not B's.
  MIRROR CHECKED anyway, for the FINAL (read-only): primordial/ledger/B.jsonl 48 entries, newest are R5 PILOT and R6 PRODUCTION (B-R6-1); `git log --since round start -- rows/B/` returns nothing. B has 0 r7 receipts and 0 r7 rows files, so there is nothing to mirror and nothing for the close sweep to list against B. FINAL will say exactly that.
  RULE ABSORBED (memory no_rebase_while_rowwriter_live, updated 09-15): ANY git write in a worktree with a live RowWriter is unsafe -- not just rebase; a plain commit races the writer's periodic commit and KILLED a worker in R7 D, and a PAUSED job is not a stopped writer. Every journal commit this round ran with B's worker idle and no rows file open, which is why they were safe. If a replication record arrives, B holds the journal commit until the job is done (or between segments with the writer closed), and pushes only then.
  pm:replication 0 records; monitor be3dltdnf re-armed (b29n06c19 expired, no record). No job; worker idle.
- 22:20 (T+282, epoch 5) loop iteration: beat; inbox unpiped to file -- EMPTY for the first time this round (0 messages to B/ALL; 5 to other lanes marked read). Nothing to act on, nothing to track.
  pm:replication 0 records; monitor b1otgpqd3 re-armed (be3dltdnf expired, no record). No job; worker idle. NO_NEW_WORK 02:37:49 (T+480): if the stream is still empty then, B posts item NOT_REACHED and the ROUND 7 FINAL before drain 03:07:49.
- 22:50 (T+312, epoch 6) loop iteration: beat; inbox unpiped to file: EPOCH 5 boundary only, nothing for B.
  TRIGGER-SIDE CHECK (read-only, one file, R6 precedent; not exploratory work and no compute): G-R16-cells.jsonl as committed on origin -- 30 r16_cell rows, ts 11:09-14:01, ZERO dated after the r7 clock start (17:37:49); 0 SURVIVED under any policy key; under gate_in|HOLD (the key replication.survived_cells reads via screen.vkey) 5 PENDING / 3 HELD / 22 CULLED; 30 replication_check rows, every one published [] with refused null. So the trigger is LIVE and has simply had no survivor to announce -- B's empty stream is consistent with the screen, not with a broken publisher.
  SCOPE of that claim, stated so the FINAL does not overreach: I read ONE committed file at origin. It does not show whether G has produced r7 cells elsewhere (other rows files, or work not yet pushed), and B does not audit another lane's ledger. The only claim B makes is about pm:replication, which B reads directly.
  pm:replication 0 records; monitor btfq72mp4 re-armed (b1otgpqd3 expired, no record). No job; worker idle.
- 23:20 (T+342, epoch 6) loop iteration: beat; inbox unpiped -- wholly empty (0 lines, no traffic on any lane). pm:replication 0 records; monitor bz1t8crmb re-armed (btfq72mp4 expired, no record). No job; worker idle. Nothing to add: the trigger-side position is unchanged from T+312 and B does not re-check another lane's rows for a second quiet tick.
