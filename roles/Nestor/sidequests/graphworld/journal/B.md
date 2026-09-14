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
