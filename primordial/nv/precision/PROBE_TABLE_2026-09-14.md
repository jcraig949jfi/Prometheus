# P1: Blackwell precision probe table (lane P, Nestor-P[m1-d940b176])

Host: RTX 5060 Ti 16 GB, compute capability 12.0, driver 576.88, Windows 11.
Venv: C:/Users/jcrai/lab/nv-venv-p (uv, Python 3.12.10, not a gw-venv clone).
It has torch 2.11.0+cu128 (arch list up to sm_120), nvidia-cutlass 4.2.0.0,
and cuda-python 12.9.7 (pinned below 13, see row 11).
Toolchain: CUDA_PATH points at the v12.6 toolkit (nvcc 12.6). MSVC 14.50 comes
from VS 18 vcvars64.
Probe: `python -m primordial.nv.precision.probe`. The raw output is in
probe_table_2026-09-14.json. This is a correctness check only: no timing and
no GPU lease. Operands are seeded Gaussians: x [64,48], W [48,8] (the brain
has A = 8 actions), or W padded to [48,16].

| # | probe | result | exact error / measurement |
|---|---|---|---|
| 1 | torch fp32 matmul | OK | max abs err 2.9e-6 vs fp64; argmax agree 64/64 |
| 2 | torch fp16 matmul | OK | max abs err 1.2e-2; argmax agree 64/64 |
| 3 | torch bf16 matmul | OK | max abs err 6.7e-2; argmax agree 64/64 |
| 4 | fp8 e4m3 `_scaled_mm`, 48x8 | REFUSED | `RuntimeError: mat2 shape (48x8) must be divisible by 16` |
| 5 | fp8 e5m2, 48x8 | REFUSED | same shape rule |
| 6 | fp8 e4m3, padded 48x16, out fp32 | REFUSED | `RuntimeError: CUDA error: CUBLAS_STATUS_NOT_SUPPORTED when calling cublasLtMatmulAlgoGetHeuristic(...)` |
| 7 | fp8 e4m3, padded, out bf16 | REFUSED | same CUBLAS_STATUS_NOT_SUPPORTED |
| 8 | fp8 e4m3 x e5m2, padded, out bf16 | REFUSED | same CUBLAS_STATUS_NOT_SUPPORTED |
| 9 | fp8 e5m2 x e5m2, padded | REFUSED | `ValueError: Multiplication of two Float8_e5m2 matrices is not supported` |
| 10 | int8 `torch._int_mm` | OK | int32 out, BIT-EXACT vs int64 CPU |
| 10b | int8 via int32 cast `@` | REFUSED | `NotImplementedError: "addmm_cuda" not implemented for 'Int'` |
| 11 | cutlass python import | OK (after pin) | The module is `cutlass_cppgen`, not `cutlass`. With cuda-python 13.4.1 (uv's default resolve) every kernel fails: `AttributeError: module 'cuda' has no attribute '__version__'`. Pinning cuda-python<13 fixes the import. |
| 12 | cutlass env | PARTIAL | nvcc_version 12.6, device_cc 120; cuda_install_path raises `FileNotFoundError: [WinError 2]` |
| 13 | cutlass Gemm fp32 smoke | REFUSED | `KeyError: 120` at cutlass_cppgen/utils/check.py:136 (valid_stage_count). The `cc_map` / `SharedMemPerCC` tables stop at cc 103. |
| 13b | the same with `cc=86` override | REFUSED | the same `KeyError: 120` at the same line. The check reads the live device cc, not the override. |
| - | cutlass-dsl 4.2 (CuTe DSL) | NO WHEEL | `nvidia-cutlass-dsl` 4.2.0/4.2.1 has only manylinux_2_28 wheels, none for win_amd64 |

## What this means for N1 (precision as a gene)

- fp32, fp16 and bf16 run natively. Whether they are behaviourally exact is
  the real question. It is measured on clear rows against fp64 ref_logits in
  the next step, not assumed from these errors.
- int8 has one working exact kernel (`_int_mm`). An int8 brain is
  quantize (scale per tensor) -> `_int_mm` -> dequantize. Its error is pure
  quantization error: the kernel is bit-exact.
- fp8 has NO working hardware kernel on this stack. Shapes must be multiples
  of 16. Even padded, cuBLASLt in torch cu128 refuses every e4m3 combination
  on cc 12.0. The fp8 gene will therefore be SIMULATED: quantize to
  float8_e4m3fn storage, dequantize, multiply in fp32. It gets recorded as
  `substrate: fp8_sim`, so its cost row cannot claim fp8 speed. Two things
  could turn on a real kernel, and neither was tried here: a newer
  torch/cuBLAS (cu129+), or Linux/WSL.
- CUTLASS python 4.2 cannot target Blackwell at all, because of the cc table,
  before it ever reaches nvcc. The 12.6 toolkit's nvcc also predates sm_120
  (not exercised, since the failure comes first). CUTLASS is out of the MVP.
  Patching a third-party table is not a probe.
