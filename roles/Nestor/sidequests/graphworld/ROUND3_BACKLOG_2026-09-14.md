# Round 3+ backlog: fixes, hardening, and the NVIDIA axes

Currency: 2026-09-14 ~18:20, Nestor-A[m1-449a9e76]. Authority: operator
messages 04, 07 and 09 (verbatim in
roles/Nestor/prompts/2026-09-14_graphworld_swarm/). Evidence:
REVIEW_PACKET_ROUND2_TEST1_2026-09-14.txt s10-11, the cohort journals
(journal/B.md..E.md, carry-forward sections), and
ROUND2_PREP_BACKLOG_2026-09-14.md (F7-F15, still open).

## 0. Sequence

    round 3  BUILD (no swarm): delegated builders F, G, H land the fixes below
    round 4  SWARM: cohorts B-E on hardened clause A (floor, re-seeded baselines)
    round 5  SWARM: clause B (transfer) opens; clause A continues
    round 6  SWARM: the NVIDIA axes become searchable traits

In parallel with rounds 4-5, the MVP builders P, Q, W, T and U build one
MVP per NVIDIA axis (DELEGATION_BRIEFS_R3_R6.md). A round starts only when
its gate items below are merged with tests.

Host facts, measured 18:10:
- one GPU, an RTX 5060 Ti 16 GB (Blackwell, compute capability 12.0),
  driver 576.88, CUDA 12.9;
- torch 2.11 cu128 has CUDA Graphs and float8 dtypes;
- warp-lang 1.17, nvidia-cutlass 4.2 and cupy-cuda12x 14.2 are on PyPI;
- cuquantum/cutensornet have no Windows wheel (they need WSL);
- Nsight Compute 2024.3 and Nsight Systems 2024.4 are installed but
  unverified on Blackwell;
- WSL has Python 3.12 and no torch.

## 1. Package F -- FABRIC (builder F; gate for round 4)

| id | item | acceptance |
|---|---|---|
| F7 | warm worker per lane: kernels, Redis pool and world caches held in memory; jobs on `pm:jobs:<L>`, rows on `pm:rows:<L>`; the task TTL is enforced by killing the job, not the session | a job overrunning `ttl_cpu_s` ends TIMEOUT with its partial rows committed; the second job in the worker pays no JIT (measured) |
| F8 | seed/world table cache keyed by (world id, seed) | FusedRollout build from cache is at least 5x faster than cold, and bytes-equal |
| F9 | checkpointed long jobs spanning epochs | a 3-epoch job resumes and reproduces the uninterrupted rows exactly |
| F14 | epoch controller: at T+30:00 post EPOCH, tell workers to stop taking jobs, export the bus, commit the conductor record | two simulated epochs on dummy workers; the log shows clean boundaries |
| O1 | the scheduled-task launcher committed in ops, with disable-after-run and a dummy self-test | the self-test passes; no task stays enabled after /Run |
| O3 | RowWriter refuses to commit without PM_TAG; the integration push is fast-forward only while a writer is live | tests |
| O5 | GPU lease `pm:gpu:lease` (holder, until, purpose), plus a `gpu_lease()` context manager that timing harnesses must hold | a second holder blocks; an expired lease is taken over; host_load records the lease holder |
| F15 | boot pack: one generated state file per lane per epoch (open claims, inbox digest, ledger front, anomalies) | boot to hello in under 60 s with only the boot pack read |
| X | liveness: STALE uses heartbeat OR transcript age (E was flagged during a background run) | test |

## 2. Package G -- METRIC HARDENING (builder G; gate for round 4)

| id | item | acceptance |
|---|---|---|
| M1 | trivial-policy floor per world x pressure: abstain-only, best fixed action (exhaustive), best 2-action brain; clause A parity on (held64 - floor) / (baseline - floor) | floor rows in the QD ledger; `qd_ledger check` reports raw and floor-normalized verdicts; B's 8 B cells re-judged |
| M2 | re-seed every baseline cell with >= 8 run seeds, sampler_seed and IQR; information-honest bytes (nibble-packed open loop) | 21 new baseline rows supersede the old ones (status `record`, `supersedes`) |
| M3 | a bootstrap CI of the median (10k resamples) instead of the 0.5 x IQR band | check uses the CI; regression test on the D3 w1 data |
| C1 | E-T3 powered brain cheats bound as THE brain oracle; skip-odd retired | oracle helper raises if a harness uses skip-odd for a verdict |
| C2 | sampler_seed mandatory in every archive constructor; elites saved per run seed | an archive without a seed raises; a replay test |
| C4 | variable-length genomes in the archive (lifts the pad-to-4 8 B floor) | a 5-byte genome round-trips; the old archives still load |
| D-open | the easy-metric anomaly (1789419655457-0) gets its discriminator here: random-action and constant-action held64 per world | resolved or re-scoped on the anomaly queue |

## 3. Package H -- MEASUREMENT ABOVE THE SWARM (builder H; gate for round 5)

| id | item | acceptance |
|---|---|---|
| F10 | predicate hypotheses: schema `{metric, cells, comparator, threshold, seeds, ttl_cpu_s, prior}` checked by code against rows; prior-vs-reality ledger | all round 2 receipts with a `prior` field are resolved by code; calibration table by cohort and domain |
| F12 | scorer as a program: progress axes computed from rows only; own-hypothesis KILLs unscored; correction lineage credited | a round 2 replay produces the vector; there is no manual path |
| F13 | budget enforcement: CPU-seconds per cohort from the warm worker ledger versus the 40/25/20/15 split | a report per epoch; a cohort over its share gets a bus warning |
| S2 | anomaly triage: age, children and cohort; D's share rises when OPEN > 2x RESOLVED per epoch | a rule in the scorer, applied to round 2 data |
| S1 | clause B scoring: graft vs BOTH cheats paired per run seed, Holm across worlds (E's E-T1b protocol) as `qd_ledger check-b` | re-derives E-T1b's report-only table from rows |
| S3 | the prior-vs-reality view on the live board | part of F10 |

## 4. Cohort carry-forward (cohorts own these; no builder)

- B: every baseline except w1 train128 has an 8 B cell at parity. Re-judge
  after M1/M2. w1 train128 is recorded as a protocol ceiling.
- C: C-R2-01..08 runs are not seed-replayable. From C-R2-09 on, harnesses
  use sampler_seed and save elites; brain cells should add powered cheats.
- D: open children 1789417664459-0 (symbol-split valleys) and
  1789418772053-0 (8-seed IQR instability; testable now).
- E: E-T2 has no fused kernel; clause B should read graft vs both cheats.

## 5. NVIDIA axes (MVPs by builders P, Q, W, T, U during rounds 4-5; traits in round 6)

| id | axis | MVP done means |
|---|---|---|
| N1 | precision as a mutable trait (P) | a genome gene selects fp32/fp16/bf16/fp8/int8 for the brain forward. A behavioural-exactness metric (action agreement on clear rows + held64 delta) and cost (bytes, wall, VRAM) land as QD rows for one world. cutlass python 4.2 and torch float8 are probed on Blackwell, with results recorded |
| N2 | Nsight telemetry as a discriminator (Q) | `ncu`/`nsys` capture one fused rollout on Blackwell (or a documented refusal plus the version that fixes it). Features (kernel time share, H2D/D2H bytes, memory-bound flag) are extracted by code into engineering rows, not fitness. A cheat: a candidate with an injected sleep must show in the features |
| N3 | Warp vs numba (W) | the B world step as a Warp kernel (CPU and CUDA) is trace-hash-exact vs wforge on sampled episodes, with skip_lin caught. A crossover table (n_envs 1..65536) vs the numba fused path, taken under the GPU lease |
| N4 | cuTensorNet TT brain (T) | in WSL (its own venv), tt_digits logits via cuTensorNet contraction == genomes.ref_logits on clear rows (argmax exact, max abs error recorded), stride cheat caught. Contraction-path cost vs torch bucket kernel |
| N5 | CUDA Graphs hot loop (U) | brain forward + action decode + world update captured in one graph; fitness and descriptor cells == E's numpy rollout 128/128 on one world. VRAM budget table (envs x T that fit in 16 GB) and throughput vs B6 fused numba, under the GPU lease |

Common rules for N builders:
- own worktree and branch, and their own venv (never gw-venv);
- the GPU lease for any timing, and a contended measurement is
  INDETERMINATE for speed;
- the exactness oracle before any speed number;
- receipts guarded, rows through RowWriter;
- new code in primordial/nv/<axis>/;
- the shared library is read-only (asks go to builder F or cohort E).
