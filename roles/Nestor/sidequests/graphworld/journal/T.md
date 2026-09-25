# Lane T journal (Nestor-T[m1-9ff9deec], CUTENSORNET MVP builder, round 6 axis N4)

Threads: 1 (conductor contract 1789425755152-0 overrides the boot prompt's 2).
Venv: WSL ~/lab/nv-venv-t (python 3.12.3): cuquantum-python-cu12 26.9.0, cutensornet-cu12 2.14.0,
cupy-cuda12x[ctk] 14.2.0, numpy 2.5.3, numba 0.67.0 (so primordial.brain.genomes imports read-only).

## 2026-09-14 iteration 1 -- WSL venv + GPU smoke + tt_digits as one cuTensorNet network (DONE, correctness only)

- venv: cupy alone failed on libcurand.so.1x; the [ctk] extra (pip CUDA wheels) fixed it. No system CUDA
  toolkit in WSL. The device shows as RTX 5060 Ti, cc 120. Smoke: contract("ij,jk->ik") vs a@b, error 2.2e-16.
- primordial/nv/tensornet/tt_cutn.py: one genome's tt_digits brain on a batch of B obs is ONE network:
  alpha[a0] x prod_c (onehot X_c[n,d_c] G_c[d_c,a_c,a_c+1]) x Wo[a_C,k] -> [n,k]. The batch index n is a
  hyperedge across all 4D one-hots, so there is no per-row gather. PlannedTT plans the path once per shape
  and re-executes with reset_operands. The stride-2 cheat drops the odd cores.
- Oracle: genomes.TTDigits.ref_logits (float64, per-step normalised). Values are compared row-normalised
  (divided by max|logit|), because the oracle's per-core rescale changes scale, not argmax.
- Tests (primordial/nv/tensornet/tests/test_tt_cutn.py, 5): numpy einsum on the same operands == oracle
  (runs in gw-venv too) + its cheat caught; cuTensorNet D=5, D=8, 400 rows: clear-row argmax mismatch 0,
  row-normalised max abs err < 1e-9, stride-2 cheat > 50 mismatches; one plan reused on 3 other genomes, exact.
  WSL 5 passed; gw-venv suite 39 passed, 3 skipped (the GPU tests skip without cuquantum).
- No timing claims (no lease). Open: max-abs-error receipt row on real E elites, plus plan-vs-exec cost vs
  C1c torch_gpu_bucket_e2e under the lease, and the topology-mutation note.

## 2026-09-14 iteration 2 -- N4 oracle receipt (PASS; MVP bullet 1 green on random genomes)

- Predicate posted before the run (bus 1789427310943-0). Code c830a6484 (n4_oracle.py).
  Rows: primordial/ledger/rows/T/N4-cutensornet-tt-digits-oracle.jsonl (header, 64 cells, summary).
- Sweep: D {3,5,8,16} (12..64 cores) x r {3,8} x 4 genome seeds, B=1024, float64, one-shot contract.
- Result: honest 32 cells, clear-row argmax mismatches 0 over 32,768 clear rows; row-normalised max abs err
  (all rows) 4.7e-13. Stride-2 cheat caught in 32/32 cells (min 577 clear-row mismatches per cell). PASS.
- Disclosure: the predicate text named "16 honest / 16 cheat cells". The sweep it describes is 32 + 32 (my
  arithmetic slip in the repost; the first draft said 32). The criteria ("all honest cells", "every cheat
  cell") are unchanged in substance and hold on all 32.
- Scope limit: genomes are Family.init random draws on uniform obs, not E's evolved elites or world obs.
  Unnormalised float64 contraction at 64 cores had no overflow here. Evolved G with a large spectral radius
  over long chains could overflow; a sliced or rescaled network would be needed before trusting it there.

## 2026-09-14 iteration 3 -- N4 timing vs C1c torch bucket kernel (PARTIAL, 28/36 shapes; QUIESCED for reboot)

- Predicate posted before the run (bus 1789427662060-0). Harness abd57b380, driver/filters 9e7883563.
  Both sides ran under the O5 lease (n4_leased holds it on Windows); lease rows: lost=false on both.
- Rows: primordial/ledger/rows/T/N4-timing-cutn.jsonl, N4-timing-torch.jsonl, N4-timing-combine.json.
- Exactness first: 28 honest cuTN cells valid, 36/36 torch cells valid, cuTN stride-2 cheat invalid 5/5.
- cuTN side hit its 540 s timeout (rc 124) after d64 r16 B65536: missing d64 r16 B>=262144 and all of d64 r64.
  A leased resume run (--configs 16:16 --min-b 262144) held the lease ~10+ min with only a header written
  (cause not established; the first pass showed a 9 GB cupy pool at d64 r16 B16384). I killed it at the
  operator's QUIESCE; the d64 r64 resume was stopped before it started. No resume rows are filed.
- Result on 28 shapes: cuTN faster on 22. bucket/cuTN exec ratio 2.3-11.7x at B<=16k (d16 r4..r64, d64 r4/r16),
  about 1.0-1.3x at d64 r4 B>=262k, and bucket wins at r>=16 with large B (d16 r16 B1M 0.48x, d16 r64 B1M 0.03x,
  d64 r16 B65536 0.28x). cuTN plan_s: 0.011-0.045 s at 16 cores, 0.19-0.37 s at 64 cores; the first plan in
  a process 1.23 s. Break-even executions where cuTN wins: 0.8-45, except 233 (first-plan cell) and 304 (d16 r64 B16k, ratio 1.00).
- Scored predictions: H1 (bucket wins >= 30/36) FAIL, bucket won 6/28. H2 (plan < 1 s at d64) PASS on the 12 d64
  shapes measured. H3 (finite break-even wherever cuTN wins) PASS.
- Confounds, not controlled: (1) small-B e2e time is CPU-dispatch dominated (bucket: ~22 kernel launches per core
  plus a host sync; C1c already saw it lose 5-10x below B~16k), and the two sides ran on different host load (torch
  on Windows, cuTN in WSL). The lease covers the GPU, not the CPU. (2) The torch header read 25% GPU utilisation
  30 ms after the cuTN lease was released (likely WSL teardown, not proven). (3) cuTN peak_mem is the cupy pool,
  which includes cuTensorNet's workspace, so it is not the minimal memory need. d16 r64 B1M (16.3 GB pool, 3.1 s)
  reads as a spill past the 16 GB card.
- MVP status: bullet 1 (oracle) green; bullet 2 (plan/exec cost vs bucket under lease) recorded on 28/36 shapes,
  missing d64 r16 B>=262k and d64 r64; bullet 3 (topology note) written:
  primordial/nv/tensornet/TOPOLOGY_MUTATIONS_N4.md.
- RESUME: after reboot, run `python -m primordial.nv.tensornet.n4_leased --side cutn --configs 16:64 ...` and
  `--configs 16:16 --min-b 262144` with a per-cell watchdog (the hang), then re-combine with --cutn a,b,c. Consider
  capping the cuTN workspace (NetworkOptions / memory limit) so d64 large-B slices instead of spilling.
