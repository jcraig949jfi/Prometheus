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

Next: P2, a precision gene in the linear and tt_feat forward (torch, per
precision), plus the exactness metric on clear rows vs fp64 ref_logits.
