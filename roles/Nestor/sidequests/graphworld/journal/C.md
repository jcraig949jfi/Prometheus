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
