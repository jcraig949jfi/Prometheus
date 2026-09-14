# Lane P journal (Nestor-P[m1-d940b176], PRECISION MVP, round 6 axis N1)

Budget from the conductor contract (bus 1789425755152-0, overrides the boot
prompt): OMP = NUMBA = torch threads = 1. No speed number counts without the
O5 lease.

## 2026-09-14 iteration 1 -- P1 Blackwell probe table (DONE)

Set up the venv nv-venv-p with uv (py3.12): torch 2.11.0+cu128,
nvidia-cutlass 4.2.0.0, numpy, numba, pytest, redis. The probe module is
primordial/nv/precision/probe.py and its tests are in
primordial/nv/precision/tests (3 pass). The table is in
PROBE_TABLE_2026-09-14.md, the raw output in probe_table_2026-09-14.json.

Findings (exact errors are in the table):
- fp32, fp16 and bf16 matmul run on cc 12.0.
- int8 `torch._int_mm` is bit-exact.
- fp8 has no working kernel. `_scaled_mm` requires dims divisible by 16 (the
  brain has A = 8). Padded, cuBLASLt returns CUBLAS_STATUS_NOT_SUPPORTED for
  e4m3 with fp32 out, bf16 out, and mixed e5m2. e5m2 x e5m2 is refused by
  design.
- CUTLASS python 4.2 (module cutlass_cppgen) fails in two ways:
  - with uv's default cuda-python 13, on `cuda.__version__`. Pinning
    cuda-python<13 fixes that.
  - then on `KeyError: 120` at utils/check.py:136, because its cc tables stop
    at 103. A cc=86 override does not bypass it.
- cutlass-dsl has no Windows wheel.

Decision for the MVP:
- fp8 enters as a simulated gene (fp8_sim: e4m3 storage, fp32 compute) and
  claims no speed.
- CUTLASS is dropped from the MVP.

## 2026-09-14 iteration 2 -- P2 precision gene + exactness metric (DONE)

primordial/nv/precision/forward.py adds a one-byte gene that indexes
PRECISIONS = fp32/fp16/bf16/fp8_sim/int8. It supports the linear and tt_feat
families on the torch forward (cpu and cuda). `exactness()` measures
argmax agreement against genomes ref_logits (fp64) on clear rows.
`nbytes()` is the weight storage at that precision, plus a 4-byte scale per
quantized tensor, plus the gene byte. Tests: 32 pass
(tests/test_forward.py).

New refusal: on cuda, `torch._int_mm` raises "self.size(1) needs to be
greater than 0 and a multiple of 8, but got 12". linear int8 now zero-pads D
up to 8k, which is exact. It equals the CPU integer emulation (test). The
substrate is int8_intmm for linear on cuda. tt_feat int8 is int8_sim: exact
integer products in float64, with v re-quantized per row after each core.

Dev table (NOT a record). Seed 1, D=12, 512 uniform uint16 rows, and every
row is clear (uniform obs have no near ties, so the next step needs the real
w4 obs). Figures are clear-row agreement, honest / skip-odd cheat, and bytes.
cpu and cuda gave identical figures.
  linear   fp32 1.000/0.518 417 | fp16 0.998 209 | bf16 0.990 209 | fp8_sim 0.975 113 | int8 0.994/0.518 113
  tt_feat  fp32 1.000/0.354 7021 | fp16 0.998 3511 | bf16 0.994 3511 | fp8_sim 0.957 1768 | int8 0.984/0.348 1768
The cheat is caught at every precision: its agreement is <= 0.52 against an
honest >= 0.957. The tt_feat max normalised logit error reaches 2.0 at
fp8_sim and 0.63 at int8. That is a sign flip of the normalised logits on
some row, so agreement, not the logit error, is the metric.

## 2026-09-14 iteration 3 -- P3 closed-loop held64 delta on w4, 8 seeds (GATE PASS, CONTROL FAIL as posted)

The predicate was posted first (bus 1789426796165-0). The harness is
primordial/nv/precision/p3_w4.py with tests/test_p3_w4.py (36 precision
tests pass; the shared suite gives 69 passed, 1 skipped). 106 rows are
committed at 8d4016cc1 in primordial/ledger/rows/P/P3-precision-w4-held64.jsonl:
80 run rows, 16 cheat rows and 10 qd_cell rows, all status dev or cheat.
Setup:
- E9 full top-16 elites, w4, run seeds 0-7.
- E7.rollout on HELD64, with the brain forward swapped for PrecisionFamily
  (per-genome quantization scales).
- E7.brain_oracle on HELD8 for on-policy clear-row agreement.
- cpu, 1 thread; the whole run took about 60 s.

GATE: fp32 held64 == E9 held64_per_seed EXACTLY in 16/16. The torch fp32
forward reproduces lane E's float32 numba numbers bit for bit on this world.

Figures below are the median held64 delta vs fp32 (min..max over 8 seeds),
then the median and min on-policy clear-row agreement, then genome bytes.
  linear  fp32    0      agree 1.000        313
  linear  fp16   +0.002 (-0.02..+0.18)  1.000 / 0.9998  169
  linear  bf16   +0.097 (-0.06..+0.25)  0.9985 / 0.9954 169
  linear  int8   +0.087 (-0.13..+0.33)  0.9984 / 0.9946 105
  linear  fp8sim +0.191 (-0.59..+0.71)  0.9926 / 0.9734 105
  tt_feat fp32    0      agree 1.000        4741
  tt_feat fp16   +0.006 (-0.01..+0.06)  1.000 / 0.9983  2383
  tt_feat bf16   +0.079 (-0.18..+0.49)  0.9973 / 0.9924 2383
  tt_feat int8   +0.148 (-0.83..+0.59)  0.9895 / 0.9795 1216
  tt_feat fp8sim -0.249 (-1.02..+1.27)  0.9701 / 0.9580 1216
Held64 IQR per family is about 6-7, so every delta is inside one IQR.
PRIOR: all held. fp16 and bf16 have |median delta| <= 0.1 and agreement
>= 0.997. int8 agreement is >= 0.9895. fp8_sim has agreement >= 0.970 and
the largest |delta| in both families.

CONTROL: FAIL as posted, 15/16 (posted bar: cheat agreement < 0.9 in 16/16).
tt_feat cheats sit at 0.42-0.72 (8/8). Linear seed 4's cheat had pooled
agreement 0.954, although E7's per-elite oracle still flagged 14/16 elites
(189 of 4096 rows). Other linear seeds: 0.71-0.88. The pooled 0.9 bar was
set without an attainable-range check. More important: a skip-odd linear
cheat (half the features) can reach 0.954 pooled agreement, while honest
fp8_sim bottoms out at 0.973. So pooled agreement ALONE barely separates a
structurally broken brain from a quantized one, and the precision gene's
exactness metric must keep a per-elite mismatch count. Also: the cheat
RAISED held64 on 4/8 linear seeds, so the held64 delta alone is not an
exactness signal (below-floor policies).

Scope: every held64 here is below the w4 abstain floor 107.75 (conductor
1789426590314-0). These rows are exactness-vs-bytes engineering, not clause A.

EPOCH 1 posted at 19:03 (bus 1789426999457-0).

## 2026-09-14 iteration 4 -- P4 cost on cuda under the O5 lease (18/20 VALID)

The predicate was posted first (bus 1789427112467-0). The harness is
primordial/nv/precision/p4_cost.py with tests/test_p4_cost.py (38 precision
tests pass). 20 rows are committed at ae1b10a12 in
primordial/ledger/rows/P/P4-precision-cost-cuda.jsonl. Conditions:
- Held bus.gpu_lease the whole time and never lost it.
- nvidia-smi read 1% before timing; the lease was free at 19:05.
- The oracle ran before any timing.
- Path: the e2e host path the closed loop uses (host weights and obs in,
  logits out), D=8, 1 torch thread, 7 alternating reps, median.

Figures per cell: wall ms at n=1024 / n=65536, then peak VRAM MB at 65536,
then param bytes.
  linear  fp32    0.574 / 3.00   8.39   289
  linear  fp16    0.566 / 2.89   7.34   145
  linear  bf16    0.595 / 2.94   7.34   145
  linear  fp8sim  0.775 / 3.50   8.39    81
  linear  int8    0.993 / 3.25  15.47    81   (int8_intmm, the real kernel)
  tt_feat fp32    1.432 / 4.72  11.28  4717
  tt_feat fp16    1.476 / 4.82   9.83  2359
  tt_feat bf16    1.482 / 4.63   9.83  2359
  tt_feat fp8sim  1.750 / 5.10  11.28  1192   ORACLE FAIL -> INDETERMINATE (agreement 0.943 < 0.95)
  tt_feat int8    2.315 / 6.71  14.90  1192   (int8_sim)
PRIOR:
- Held: fp16 and bf16 are within 0.99-1.04x of fp32 wall at n=1024.
- Held: the VALID fp8_sim and int8 cells are slower than fp32 at both n
  (1.09-1.73x).
- Held: tt_feat int8 is the slowest cell at both n.
- FAILED: VRAM does not follow bytes. int8 peaks at 1.3-1.8x the VRAM of
  fp32. fp8_sim equals fp32, since it computes in fp32. Only fp16 and bf16
  save VRAM (-12.5% linear, -12.8% tt_feat).
New: with D=8, tt_feat fp8_sim fell below 0.95 on the 512-row sample. In P3
(D=8 on-policy) its minimum was 0.958. The fp8_sim gene on tt_feat sits
right at the exactness edge.

Engineering conclusion for the round 6 trait: on this stack, every
precision below 16 bits buys genome bytes only (3.6-4x smaller) and costs
wall time and VRAM. fp16 is the one free win: bytes /2, VRAM -12%, wall
unchanged, agreement >= 0.996. A search that scores bytes (clause A) will
push genomes toward int8/fp8. That is honest only if the cost axes (wall,
VRAM) stay in the row, which they do here.

Package sP acceptance: precisions selectable (P2), exactness + held64 delta
on w4 x 8 seeds (P3), cost bytes/wall-under-lease/VRAM (P4), QD rows per
precision (P3 qd_cell rows), Blackwell probe table (P1). GREEN.
Carry-forward (not in the acceptance list):
- P5: a per-elite mismatch count in the qd_cell rows. Pooled agreement did
  not separate the linear seed-4 cheat (P3 CONTROL 15/16).
- A real fp8 kernel needs torch cu129+ or Linux.
- The resident-GPU path (weights prepared once on device) is untimed.
