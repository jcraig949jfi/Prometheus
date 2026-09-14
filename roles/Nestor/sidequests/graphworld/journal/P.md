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

Next: P4 cost under the O5 lease (wall and VRAM per precision on cuda,
including linear int8_intmm), then the per-elite mismatch column added to the
qd_cell rows.
