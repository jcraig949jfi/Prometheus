"""PAN-10 controls for the local-fit estimate (pure arithmetic; no network).

POSITIVE  a 4B model fits 16 GB at Q4 and at fp16
NEGATIVE  a 671B model fits neither
NAME      '30B-A3B' parses as 30B total (all experts resident), '0.6B' as 0.6B
CHEAT     a quantized repo's packed safetensors count is marked unreliable, and a
          GGUF total, when present, outranks the safetensors count
"""
from pan.frontier import hf


def test_positive_small_model_fits():
    p, basis, f = hf.fit("Qwen/Qwen3-4B", ["transformers"], {"total": 4_022_468_096}, None)
    assert basis == "safetensors" and f["fits_16gb_q4"] and f["fits_16gb_fp16"] and f["reliable"]


def test_negative_huge_model_does_not_fit():
    p, basis, f = hf.fit("deepseek-ai/DeepSeek-V3", [], {"total": 671_000_000_000}, None)
    assert not f["fits_16gb_q4"] and not f["fits_16gb_fp16"]


def test_name_parsing():
    assert hf.params_from_name("Qwen/Qwen3-Coder-30B-A3B-Instruct") == 30_000_000_000
    assert hf.params_from_name("Qwen/Qwen3-Embedding-0.6B") == 600_000_000
    assert hf.params_from_name("someone/no-size-here") is None
    p, basis, f = hf.fit("Qwen/Qwen3-Coder-30B-A3B-Instruct", [], None, None)
    assert basis == "name" and not f["fits_16gb_q4"]   # 30e9 * 0.5625 + 1.5 = 18.4 GB


def test_cheat_quantized_packed_count_is_unreliable():
    p, basis, f = hf.fit("nvidia/Qwen3.8-27B-NVFP4", ["nvfp4", "modelopt"], {"total": 18_160_000_000}, None)
    assert basis == "safetensors" and f["reliable"] is False
    p, basis, f = hf.fit("x/y-GGUF", ["gguf"], {"total": 1_000}, {"total": 27_780_000_000})
    assert basis == "gguf" and p == 27_780_000_000
