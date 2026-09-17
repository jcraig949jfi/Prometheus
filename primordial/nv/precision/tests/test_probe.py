"""P1 probe: the table's contract (every row names a probe, ok is a bool, a failure carries its exact error)."""
import json

import pytest

from primordial.nv.precision import probe

torch = pytest.importorskip("torch")


def test_err_keeps_exception_text():
    try:
        raise RuntimeError("CUBLAS_STATUS_NOT_SUPPORTED when calling cublasLtMatmul")
    except RuntimeError as e:
        assert probe._err(e) == "RuntimeError: CUBLAS_STATUS_NOT_SUPPORTED when calling cublasLtMatmul"


@pytest.mark.skipif(not torch.cuda.is_available(), reason="needs cuda")
def test_torch_probe_rows_are_well_formed_and_fp32_is_exact_enough():
    rows = probe.probe_torch(n=16, m=12, k=4)
    names = [r["probe"] for r in rows]
    assert names == ["torch_matmul_fp32", "torch_matmul_fp16", "torch_matmul_bf16", "torch_fp8_scaled_mm",
                     "torch_fp8_e5m2", "torch_fp8_scaled_mm_pad16", "torch_fp8_e5m2_pad16",
                     "torch_fp8_scaled_mm_pad16_outbf16", "torch_fp8_scaled_mm_outbf16",
                     "torch_fp8_e4m3_x_e5m2_pad16_outbf16", "torch_int8_int_mm", "torch_int8_mm_cast"]
    for r in rows:
        assert isinstance(r["ok"], bool)
        assert r["ok"] or r["error"]
    fp32 = rows[0]
    assert fp32["ok"] and fp32["max_abs_err"] < 1e-3 and fp32["argmax_agree"] == 1.0
    int_mm = rows[names.index("torch_int8_int_mm")]
    assert not int_mm["ok"] or int_mm["bit_exact"]      # int8 is either refused or bit-exact, never approximate
    json.dumps(rows)


def test_cutlass_probe_without_compile_never_raises():
    rows = probe.probe_cutlass(compile_kernel=False)
    assert rows[0]["probe"] == "cutlass_import"
    for r in rows:
        assert isinstance(r["ok"], bool)
        assert r["ok"] or r["error"]
