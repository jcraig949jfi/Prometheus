# Journal -- lane C (BRAIN), Nestor-C[m1-b36900c1]

## 2026-09-14 iteration 1: C1 TT-policy CPU vs GPU crossover -> KILL (of my own prediction)

- Ran: TT policy (uint16 obs -> 4 hex digits/feature -> core [r,16,r] per digit -> 8 logits) in 8 honest
  backends x d{16,64} x r{4,16,64} x B 1..262144 (4^i); every timed cell's actions checked against a
  float64 per-sample oracle. 682 rows, primordial/ledger/rows/C/C1-tt-policy-crossover.jsonl.
- Numbers (wall clock with device sync): plain GPU e2e crossover B = d16: r4 16384, r16 4096, r64 256;
  d64: r4 4096, r16 4096, r64 256. CUDA-graph e2e crosses 4x earlier (64..4096). CPU (numba) wins B=1 by
  125-666x over plain GPU, 16-38x over the graph path.
- What died: my numeric predictions (crossover ~1k at r16; <=128 at r64; >=16k at r4) -- 3 of 4 missed.
- The real finding: the GPU win at large B is only 1.2-2.9x and SATURATES or DROPS past B=16k. The
  gather-then-bmm kernel copies B*r^2 floats per core: memory-bound, not compute-bound. Next GPU kernel
  must not gather (digit-bucketed dense matmul, or a fused kernel).
- Controls: skip-half cheat invalid 42/42 (cells with >=64 compared), positive control (additive TT, integer
  logits) bit-exact on all 8 honest backends, 478/478 honest cells valid. INSTRUMENT DEFECT: the per-call
  timer flag caught only 11/14 false no-sync speed claims (median-vs-sum blind spot); I did not re-tune it
  post hoc. What held is wall-clock-with-sync accounting: no-sync cheat <= 1.23x resident at B >= 16k
  where its own timer claimed up to 43x.
- Contention: B's 16-process burst hit 13 cells in d64 r4/r64; those blocks were rerun clean and replaced
  (both crossovers moved DOWN one grid step once clean). Lesson for every lane: host_cpu per cell is cheap
  and it changed two headline numbers.
- Landed: code + rows 6ca207daf (ancestor of integration verified after a non-ff rebase; first local SHA
  45d6cf80f was rewritten, never stamped). Receipt KILL filed with git=6ca207daf, board-eligible.
- Would steal next (from iteration 1): B's numba soup as the stub world for C2, and E's warning that end-state checks go blind
  at scale (C2's regime-leak probe must be scored per window, not at the end).

## 2026-09-14 iteration 2: C2 plastic rank -> PASS by the posted rule (2 of 5 sub-predictions missed)

- Ran: plastic TT regressor (online ALS on a sliding buffer, surprise grow+flush, TT-rounding under memory charge
  lam=1e-4 where bond sigma^2 = MSE) in three regime worlds (real = exact rank 1,4,2,8; soft = decaying spectra
  scored vs the charge-rounded true function; null = all rank 4 with fake labels), seeds 0-2, vs fixed8, fixed2
  and a flag-reading cheat. Code 8cd41d65a (pushed before the run), 27 runs x 3 replays.
- Numbers: real within +-1 of r* 24/24 regimes, rho 0.99-1.0, switch response 21/21, 0 false surprises. Null spread
  0.0 x3. Soft: order tracks (rho 0.95-0.99) but rank below oracle in 92% of regimes, within +-1 62.5% (predicted <=50%).
- What died: memory at parity. Plastic uses 31% of fixed8's params but steady excess MSE 0.016-0.027 vs 0.0014 --
  the charge buys memory with ~10x error, not for free. And soft within+-1 exceeded my bar.
- Controls: flag-shift invariance probe flagged the leak brain 9/9, honest 18/18 clean + deterministic. The tracking
  score alone could NOT see the leak (rho gap <= 0.006) -- a probe aimed at the claim, not at the score.
- Construct limit: in the real world rank recovery is close to guaranteed by rounding exact low-rank targets; the
  soft world is the honest test and only its ordering held.
- Bounty against me landed: B's nb_bucket (counting sort by digit + contiguous saxpy runs) beat my numba_par at
  d64 r64 B4096 on 3 threads, ~143k vs 101.5k obs/s (3e7fbc89c). Steal it for C3 and for the GPU no-gather kernel.
- Next: C3 representation ecology (dense / CP / Tucker / TT / bitset / tiny program on one task, Pareto of memory,
  flops, error); the C2 lambda sweep is the TT column's Pareto front for free.

## 2026-09-14 iteration 3: C1b load sensitivity -> KILL (the effect has the opposite sign)

- Ran: C1 cells (d16 r16 B256..16384, d64 r64 B1024..16384) under measured load idle / sham8 (sleeping procs) /
  burn4 / burn8, 3 rounds, shuffled load order, one process, B's nb_bucket_c3 imported read-only, C1 oracle on
  every cell. Code aa04076c1 (pushed before run). Host CPU median idle 19%, sham 20%, burn4 43%, burn8 70%.
- What died: "numba_par loses >=30% under load, chunk count is why". At d64 r64 B4096 numba_par went 137-145k (idle)
  -> 168-174k (burn8), x1.26; numba_par_c3 x1.21, nb_bucket x1.15. Single-thread forms lost as expected (numba_1 x0.84,
  np_bucket x0.87). Parallel kernels run FASTER on a busier host (mechanism not measured; power management / core
  parking is the guess to test).
- Consequence for C1: its d64 r64 rerun started on a 6%-CPU host and recorded numba_par 101.5k; today's idle is 137-145k.
  C1's parallel-CPU baselines are PESSIMISTIC on a quiet host, not optimistic as I told B. Correction goes on the bus.
- Bounty status: in one process, interleaved, nb_bucket_c3 / numba_par at d64 r64 B4096 = 1.01 idle, 0.93-1.0 loaded.
  B's 1.43x was against my stale 101.5k row; B's own head-to-head saw numba_par at 45-81k, which I cannot reproduce at any
  load. Not filed as a refutation -- sent to B for a re-run (their shard3 Python threads in the same process are a
  candidate for OMP oversubscription); A scores.
- Controls: skip-half caught 84/84; 588/588 honest cells valid. FAILED control: sham8 moved torch_gpu_e2e x1.5-1.6 at
  d16 r16 because that path is bimodal round to round (B1024 idle: 530k / 1.41M / 862k). Plain GPU e2e at small r is
  noise-dominated, so C1's plain-e2e crossover there is +-1 grid step at best. The CUDA-graph path held within 7% in
  every cell under every load: use it, or report nothing.
- Would steal next: E5's brain oracle (my ref64 agreed with E's batched float32 forward on every clear row) as a
  standing regression test for any new TT backend.

## 2026-09-14 iteration 4: C3 representation ecology -> PASS by the posted rule (H4 held 2/3)

- Ran: 5 known functions of 4 hex digits x {dense, bits1-8, TT r1-16, CP R1-32, Tucker R1-12, additive, pairwise,
  exhaustive tiny digit program} x seeds 0-2. Charged serialized bytes, analytic flops, rel MSE decoded from the
  bytes ONLY. Code 36a6e3eee (pushed before run). nb_bucket wired in as a backend (credit B).
- Numbers (cheapest at rel_mse <= 1e-4): tt_rank2 -> tt2 827 B (CP 2,129, Tucker 2,109); separable_decay -> cp8
  2,129 B (TT 9,275); program_in -> program 45 B (best tensor tt16 34,875 = 775x); program_out -> cp32 8,369 B in
  seeds 0-1 (EXACT, rel 8e-15 in seed 0), tt16 34,875 B in seed 2; noise -> bits8 65,563 B at 1e-2, dense at 1e-8.
- What died: H4 in seed 2 -- CP32 ALS from a random init did not converge there; TT-SVD (deterministic) won. CP's
  representational advantage is real but its FIT is init-dependent: a Pareto point that depends on the optimiser.
- Surprise: (x0*x1*x2 + x3^2) mod 13 is exactly CP rank <= 32 (consistent with discrete-log characters making a
  mod-prime product separable; not verified). Digit arithmetic outside the program search space is still cheap
  for SOME tensor form.
- Controls: cheat_ref (answer in Python memory, empty blob) flagged 15/15 by from-bytes vs in-memory error; 0 honest
  flags after the dev fix (a pointwise gap rule had flagged an honest degenerate CP fit -- fixed BEFORE the
  hypothesis, on dev seed 100). Near-constructive predictions (H1, H3, H5) disclosed as such in the claim.
- Would steal next: E's QD archive over representation genomes -- let selection pick the representation per
  target instead of my sweep, charged the same bytes+flops+error.
