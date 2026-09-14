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
- Would steal next: B's numba soup as the stub world for C2, and E's warning that end-state checks go blind
  at scale (C2's regime-leak probe must be scored per window, not at the end).
