"""P1: probe table -- what runs on this Blackwell card (cc 12.0) for each brain-forward precision.

Every probe is one small, exactness-checked kernel call. A probe row records the exact exception
text when it fails; nothing is retried or filtered. No timing is taken here (correctness only, no
GPU lease needed): wall numbers belong to the lease-held cost step.

Probes
  torch_matmul_<dt>     x @ W on cuda in fp32/fp16/bf16; max abs error vs fp64 on the CPU
  torch_fp8_scaled_mm   torch._scaled_mm on float8_e4m3fn with per-tensor scales (cuBLASLt fp8)
  torch_fp8_e5m2        the same with float8_e5m2 operands
  torch_int8_int_mm     torch._int_mm int8 x int8 -> int32 (must be bit-exact vs int64 on the CPU)
  torch_int8_mm_cast    int8 matmul via the int32 cast path (fallback when _int_mm refuses)
  cutlass_import        nvidia-cutlass 4.2 python (module cutlass_cppgen) imports
  cutlass_env           nvcc version, device cc, CUDA install path seen by cutlass
  cutlass_gemm_fp32     cutlass_cppgen.Gemm smoke kernel (emits C++, compiles with nvcc + MSVC)

usage: python -m primordial.nv.precision.probe [--out PATH] [--skip-cutlass-compile]
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import traceback


def _err(e: BaseException) -> str:
    lines = traceback.format_exception_only(type(e), e)
    return "".join(lines).strip()[:2000]


def _where(e: BaseException) -> str:
    """Innermost frame of the exception, as file:line (function) -- where a library refused."""
    tb = traceback.extract_tb(e.__traceback__)
    if not tb:
        return ""
    f = tb[-1]
    return f"{f.filename.replace(chr(92), '/').split('site-packages/')[-1]}:{f.lineno} ({f.name})"


def _row(probe, ok, **kw):
    return dict(probe=probe, ok=bool(ok), **kw)


def probe_torch(n=64, m=48, k=8, seed=0):
    import numpy as np
    import torch

    rows = []
    dev = "cuda"
    rng = np.random.default_rng(seed)
    x64 = rng.standard_normal((n, m))
    w64 = rng.standard_normal((m, k))
    ref = x64 @ w64
    ref_arg = ref.argmax(1)

    for name, dt in (("fp32", torch.float32), ("fp16", torch.float16), ("bf16", torch.bfloat16)):
        try:
            y = (torch.tensor(x64, dtype=dt, device=dev) @ torch.tensor(w64, dtype=dt, device=dev))
            y = y.double().cpu().numpy()
            rows.append(_row(f"torch_matmul_{name}", True, max_abs_err=float(np.abs(y - ref).max()),
                             argmax_agree=float((y.argmax(1) == ref_arg).mean())))
        except Exception as e:
            rows.append(_row(f"torch_matmul_{name}", False, error=_err(e)))

    def scaled_mm(fdt, probe, xx, ww, out_dtype=torch.float32, fdt_b=None):
        fdt_b = fdt_b or fdt
        rr = xx @ ww
        shape = f"{xx.shape[0]}x{xx.shape[1]}x{ww.shape[1]}"
        try:
            a = torch.tensor(xx, dtype=torch.float32, device=dev)
            b = torch.tensor(ww, dtype=torch.float32, device=dev)
            fa, fb = torch.finfo(fdt).max, torch.finfo(fdt_b).max
            sa = (a.abs().max() / fa).reshape(())
            sb = (b.abs().max() / fb).reshape(())
            qa = (a / sa).clamp(-fa, fa).to(fdt)
            qb = (b / sb).clamp(-fb, fb).to(fdt_b)
            y = torch._scaled_mm(qa, qb, scale_a=sa, scale_b=sb, out_dtype=out_dtype)
            # the same quantized operands dequantized and multiplied in fp64: isolates the kernel error
            deq = (qa.double() * sa.double()) @ (qb.double() * sb.double())
            y = y.double()
            rows.append(_row(probe, True, shape=shape,
                             max_abs_err_vs_fp64=float((y.cpu() - torch.tensor(rr)).abs().max()),
                             max_abs_err_vs_dequant=float((y - deq).abs().max()),
                             argmax_agree=float((y.cpu().numpy().argmax(1) == rr.argmax(1)).mean())))
        except Exception as e:
            rows.append(_row(probe, False, shape=shape, error=_err(e)))

    # brain shapes (A = 8 actions) first, then the same kernel padded to multiples of 16
    x16 = rng.standard_normal((n, 16 * ((m + 15) // 16)))
    w16 = rng.standard_normal((x16.shape[1], 16 * ((k + 15) // 16)))
    scaled_mm(torch.float8_e4m3fn, "torch_fp8_scaled_mm", x64, w64)
    scaled_mm(torch.float8_e5m2, "torch_fp8_e5m2", x64, w64)
    scaled_mm(torch.float8_e4m3fn, "torch_fp8_scaled_mm_pad16", x16, w16)
    scaled_mm(torch.float8_e5m2, "torch_fp8_e5m2_pad16", x16, w16)
    scaled_mm(torch.float8_e4m3fn, "torch_fp8_scaled_mm_pad16_outbf16", x16, w16, out_dtype=torch.bfloat16)
    scaled_mm(torch.float8_e4m3fn, "torch_fp8_scaled_mm_outbf16", x64, w64, out_dtype=torch.bfloat16)
    scaled_mm(torch.float8_e4m3fn, "torch_fp8_e4m3_x_e5m2_pad16_outbf16", x16, w16, out_dtype=torch.bfloat16,
              fdt_b=torch.float8_e5m2)

    qi = rng.integers(-127, 128, (n, m))
    qw = rng.integers(-127, 128, (m, k))
    iref = qi @ qw
    try:
        y = torch._int_mm(torch.tensor(qi, dtype=torch.int8, device=dev),
                          torch.tensor(qw, dtype=torch.int8, device=dev))
        yy = y.cpu().numpy().astype(np.int64)
        rows.append(_row("torch_int8_int_mm", True, out_dtype=str(y.dtype), bit_exact=bool((yy == iref).all())))
    except Exception as e:
        rows.append(_row("torch_int8_int_mm", False, error=_err(e)))
    try:
        y = torch.tensor(qi, dtype=torch.int8, device=dev).to(torch.int32) @ \
            torch.tensor(qw, dtype=torch.int8, device=dev).to(torch.int32)
        yy = y.cpu().numpy().astype(np.int64)
        rows.append(_row("torch_int8_mm_cast", True, out_dtype=str(y.dtype), bit_exact=bool((yy == iref).all())))
    except Exception as e:
        rows.append(_row("torch_int8_mm_cast", False, error=_err(e)))
    return rows


def probe_cutlass(compile_kernel=True, n=64, m=48, k=8, seed=0):
    rows = []
    try:
        import cutlass_cppgen as cc
        from importlib.metadata import version
        rows.append(_row("cutlass_import", True, module="cutlass_cppgen", dist_version=version("nvidia-cutlass")))
    except Exception as e:
        rows.append(_row("cutlass_import", False, error=_err(e)))
        return rows
    env = {}
    for key, fn in (("nvcc_version", "nvcc_version"), ("device_cc", "device_cc"), ("cuda_install_path", "cuda_install_path")):
        try:
            v = getattr(cc, fn)
            env[key] = str(v() if callable(v) else v)
        except Exception as e:
            env[key] = "ERROR: " + _err(e)
    bad = [f"{k_}: {v[len('ERROR: '):]}" for k_, v in env.items() if v.startswith("ERROR")]
    rows.append(_row("cutlass_env", not bad, **env, **({"error": "; ".join(bad)} if bad else {})))
    if not compile_kernel:
        rows.append(_row("cutlass_gemm_fp32", False, error="skipped (--skip-cutlass-compile)"))
        return rows
    import numpy as np
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((n, m)).astype(np.float32)
    B = rng.standard_normal((m, k)).astype(np.float32)
    ref = A.astype(np.float64) @ B.astype(np.float64)
    # device cc first; then cc 86 (cutlass maps 86 -> sm80 generic kernels), in case only the table lacks 120
    for probe_name, cc_arg in (("cutlass_gemm_fp32", None), ("cutlass_gemm_fp32_cc86_override", 86)):
        try:
            kw = {} if cc_arg is None else {"cc": cc_arg}
            plan = cc.Gemm(element=np.float32, layout=cc.LayoutType.ColumnMajor, **kw)
            # cutlass is column-major: pass Fortran-ordered copies
            Af, Bf, Cf, Df = (np.asfortranarray(z) for z in (A, B, np.zeros((n, k), np.float32),
                                                                np.zeros((n, k), np.float32)))
            plan.run(Af, Bf, Cf, Df)
            rows.append(_row(probe_name, True, max_abs_err=float(np.abs(Df - ref).max())))
        except Exception as e:
            rows.append(_row(probe_name, False, error=_err(e), where=_where(e)))
    return rows


def host_facts():
    facts = {"python": sys.version.split()[0], "platform": platform.platform()}
    try:
        import torch
        facts.update(torch=torch.__version__, torch_cuda=torch.version.cuda,
                     cuda_available=torch.cuda.is_available())
        if torch.cuda.is_available():
            facts.update(device=torch.cuda.get_device_name(0),
                         capability=".".join(map(str, torch.cuda.get_device_capability(0))),
                         arch_list=torch.cuda.get_arch_list())
    except Exception as e:
        facts["torch_error"] = _err(e)
    return facts


def run(compile_cutlass=True) -> dict:
    return {"host": host_facts(), "rows": probe_torch() + probe_cutlass(compile_cutlass)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="")
    ap.add_argument("--skip-cutlass-compile", action="store_true")
    a = ap.parse_args(argv)
    res = run(not a.skip_cutlass_compile)
    txt = json.dumps(res, indent=1, sort_keys=True)
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(txt + "\n")
    print(txt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
