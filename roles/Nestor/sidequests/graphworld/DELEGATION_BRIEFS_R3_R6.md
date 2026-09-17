# Delegation briefs: round 3 builders (F, G, H) and round 6 MVP builders (P, Q, W, T, U)

Currency: 2026-09-14, Nestor-A[m1-449a9e76] (conductor). The backlog items
are in ROUND3_BACKLOG_2026-09-14.md; this file is what each delegated
session reads first. Every builder is a separate Claude Code session,
launched by the conductor through the scheduled-task launcher, with
--remote-control so the operator can watch.

## 0. Rules for every builder

1. Worktree F:/Prometheus-worktrees/nestor-bld-<l>, branch
   nestor/bld-<l>-2026-09-14. It is pre-built by the conductor (sparse,
   warmed). Integrate by rebasing onto the integration branch; never force.
2. Identity: `python -m comms boot Nestor`, `comms instance` -> tag;
   PM_LANE=<L> (the builder letter); `bus hello` within 10 min; `bus beat`
   every loop step.
3. Scope: only your package's ids. New code under
   primordial/<package dir>/ as listed below. Shared library files (bus,
   fabric, ops, qd, brain, soup, lingua, core) may be edited ONLY by F, G
   and H for the ids they own, with tests. Anyone else posts
   `ask --to <owner>`.
4. Every change ships with tests. The full suite
   (`python -m pytest -q primordial/tests`) passes before each push.
5. Rows go through RowWriter; receipts are guarded (push first, then
   file); predicates are posted before any experiment.
6. Venv: F, G and H use C:/Users/jcrai/lab/gw-venv and must NOT install
   packages. P, Q, W and U use their own uv venv
   C:/Users/jcrai/lab/nv-venv-<l> (a --system-site-packages clone is
   forbidden). T uses a WSL venv ~/lab/nv-venv-t. Never pip-install into
   gw-venv: rounds 4-5 run on it.
7. GPU: one RTX 5060 Ti shared with the swarm. Any timing claim needs the
   O5 lease (until F lands it: `bus burst` plus nvidia-smi showing idle).
   A contended measurement is INDETERMINATE for speed. Correctness work
   needs no lease.
8. Timebox: 30-min epochs. Post
   `EPOCH n: done=[ids] tests=K open=[ids]` each epoch. Stop when your
   package's acceptance list is green or at 4 epochs, whichever comes
   first. Then post a pause note and stop the loop.
9. The operator is on mobile: reports are plain text; anything to copy
   goes in ONE fenced block.

## F -- FABRIC builder (round 3; gate for round 4)

Package: F7, F8, F9, F14, O1, O3, O5, F15, plus the liveness STALE fix
(ROUND3_BACKLOG s1).
Code: primordial/fabric, primordial/ops, primordial/bus (owner for these
ids).
Order: O3 -> O5 -> O1 -> F7 -> F8 -> F14 -> F9 -> F15. O5 (GPU lease) lands
first after O3: builders P, Q, W and U wait on it.
First item: O3 (RowWriter PM_TAG guard + fast-forward-only push while a
writer is live).

## G -- METRIC HARDENING builder (round 3; gate for round 4)

Package: M1, M2, M3, C1, C2, C4, and the easy-metric discriminator
(ROUND3_BACKLOG s2).
Code: primordial/ops/qd_ledger.py, primordial/qd/archive.py,
primordial/cohorts/e/oracles.py (owner for these ids), and
primordial/metric/.
Order: C2 (seeded archives) -> M1 floors -> M2 re-seed baselines ->
M3 bootstrap CI -> C1 -> C4.
First item: C2. Then the M1 floor rows for w4, where B's easy-metric
anomaly points.
Compute: M2 re-seeding is ~21 cells x 8 runs. Use at most 5 cores, and
announce bursts.

## H -- MEASUREMENT builder (round 3; gate for round 5)

Package: F10, F12, F13, S1, S2, S3 (ROUND3_BACKLOG s3).
Code: primordial/score/ (new), plus the `check-b` command in
primordial/ops/qd_ledger.py after G's M-items merge (coordinate on the bus).
Order: F10 (resolve round 2 priors by code) -> F12 -> S1 -> F13 -> S2 -> S3.
First item: F10 on the 37 round 2 receipts in
bus_export/pm_results_2026-09-14.jsonl.
Rule: the scorer reads rows and receipts only. It never reads prose
fields to decide a score.

## P -- PRECISION MVP (round 6 axis N1; runs during rounds 4-5)

Goal: precision becomes a genome gene.
MVP done:
- fp32/fp16/bf16/fp8/int8 selectable for the linear and tt_feat brain
  forward;
- exactness measured as action agreement on clear rows vs fp64
  ref_logits, plus the held64 delta on one world (w4, 8 run seeds);
- cost = bytes, wall time under the lease, VRAM;
- QD rows per precision.
First: a probe table of what runs on Blackwell cc 12.0 (torch float8
matmul, cutlass python 4.2 install and a smoke kernel), with exact error
messages.
Code: primordial/nv/precision/. Venv: nv-venv-p.

## Q -- NSIGHT TELEMETRY MVP (N2)

Goal: hardware telemetry as descriptors, not fitness (for now).
MVP done:
- `ncu` or `nsys` captures one B6 fused rollout and one torch GPU brain
  forward on this Blackwell GPU, or a documented refusal naming the
  first tool version that supports cc 12.0;
- a parser extracts kernel time share, H2D/D2H bytes, peak memory and a
  memory-bound flag into engineering rows;
- cheat: a candidate with an injected host sleep or an extra device copy
  must move the right feature.
First: a capture smoke test with the installed Nsight Compute 2024.3 and
Systems 2024.4, and the version check.
Code: primordial/nv/telemetry/. Venv: nv-venv-q (no GPU lease is needed
for capture correctness).

## W -- WARP MVP (N3)

Goal: Warp as a numba successor for world kernels.
MVP done:
- the B world step as a Warp kernel on CPU and CUDA, trace-hash-exact vs
  wforge on sampled episodes (reuse the E4/E7 world oracle), with the
  skip_lin cheat caught;
- a crossover table n_envs 1..65536: Warp CPU, Warp CUDA and numba fused
  (B6), each cell timed under the GPU lease.
First: install warp-lang 1.17 in nv-venv-w and run a Blackwell smoke
kernel, then port one tick.
Code: primordial/nv/warp/.

## T -- CUTENSORNET MVP (N4, WSL)

Goal: TT/MPS brain contraction through cuTensorNet.
MVP done:
- in WSL, tt_digits logits via cuTensorNet contraction match
  genomes.ref_logits on clear rows (argmax exact, max abs error
  recorded), with the stride-2 cheat caught;
- contraction-path planning cost and execution time vs the torch bucket
  kernel (C1c) under the lease;
- a note on what topology mutations cuTensorNet makes cheap (bond
  dimension, core order).
First: build the WSL venv (python 3.12, cuquantum-python-cu12 or
cutensornet, cupy) and smoke-test on the GPU through WSL.
Code: primordial/nv/tensornet/. The worktree is shared via /mnt/f (never
put hot data on F:).

## U -- CUDA GRAPHS MVP (N5)

Goal: the closed-loop hot path on device.
MVP done:
- brain forward (linear, then tt_digits), action decode and world update
  captured as one torch CUDA graph per step, or a static multi-step graph;
- fitness and descriptor cells == E's numpy rollout 128/128 on one world;
- a VRAM budget table (envs x T that fit in 16 GB);
- throughput vs B6 fused numba, under the lease.
First: port the B world step to torch integer ops, checked exact vs
wforge on sampled episodes, before any capture.
Code: primordial/nv/cudagraph/. Venv: nv-venv-u (torch cu128 wheel;
verify the Blackwell kernels).
