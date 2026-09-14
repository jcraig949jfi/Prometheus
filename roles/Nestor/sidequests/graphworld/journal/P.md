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

Next: P3, the held64 delta on w4 with 8 run seeds, per precision (fp32 as the
reference genome set), and QD rows through RowWriter. The predicate is
posted before the run.
