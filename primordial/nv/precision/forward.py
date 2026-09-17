"""P2: precision as a genome gene for the linear and tt_feat brain forward (lane P, N1).

A genome in precision form is (family genome, precision gene). The gene is one byte: an index into
PRECISIONS. The forward is torch, one genome over a batch of obs rows. The probe table
(PROBE_TABLE_2026-09-14.md) decides how each precision is realised on this card:

  fp32      native fp32 matmul
  fp16      native fp16 matmul
  bf16      native bf16 matmul
  fp8_sim   weights stored as float8_e4m3fn (per-tensor scale), dequantized, computed in fp32.
            SIMULATED: torch cu128 cuBLASLt refuses fp8 on cc 12.0, so no fp8 speed can be claimed.
  int8      symmetric per-tensor int8 weights and per-row int8 activations. linear uses the real
            torch._int_mm kernel on cuda (bit-exact in the probe). tt_feat has no int8 batched
            kernel: its integer products are computed exactly in float64 (int8_sim substrate).

Oracle: genomes.Family.ref_logits (fp64, plain loops). Exactness = action agreement on clear rows
(genomes.clear_rows) plus the max logit error. Cost bytes = weight storage at the precision plus
one fp32 scale per quantized tensor plus the one-byte gene.

    from primordial.nv.precision.forward import precision_logits, exactness
    lg = precision_logits("tt_feat", g1, obs, "int8")
"""
from __future__ import annotations

import numpy as np
import torch

from primordial.brain import genomes as gm

PRECISIONS = ("fp32", "fp16", "bf16", "fp8_sim", "int8")
FAMILIES = ("linear", "tt_feat")
_TORCH = {"fp32": torch.float32, "fp16": torch.float16, "bf16": torch.bfloat16}
_BYTES = {"fp32": 4, "fp16": 2, "bf16": 2, "fp8_sim": 1, "int8": 1}
QMAX = 127


def gene_to_precision(gene: int) -> str:
    return PRECISIONS[int(gene) % len(PRECISIONS)]


def substrate(family: str, precision: str, device: str) -> str:
    if precision == "int8":
        return "int8_intmm" if (family == "linear" and device == "cuda") else "int8_sim"
    return precision


def nbytes(family: str, D: int, precision: str, A: int = 8) -> int:
    fam = gm.FAMILIES[family](D, A)
    quant = precision in ("fp8_sim", "int8")
    return fam.nf * _BYTES[precision] + (4 * len(fam.shapes()) if quant else 0) + 1


# ------------------------------------------------------------------ quantizers

def _q8(x: torch.Tensor, dim=None):
    """symmetric int8: -> (int8 tensor, fp32 scale). per tensor, or per slice along dim."""
    x = x.float()
    m = x.abs().amax() if dim is None else x.abs().amax(dim=dim, keepdim=True)
    s = torch.clamp(m, min=1e-30) / QMAX
    return torch.clamp(torch.round(x / s), -QMAX, QMAX).to(torch.int8), s


def _fp8(x: torch.Tensor) -> torch.Tensor:
    """store as float8_e4m3fn with a per-tensor scale; return the dequantized fp32 tensor."""
    fmax = torch.finfo(torch.float8_e4m3fn).max
    s = torch.clamp(x.float().abs().amax(), min=1e-30) / fmax
    return (x.float() / s).clamp(-fmax, fmax).to(torch.float8_e4m3fn).float() * s


# ------------------------------------------------------------------ forwards

def _feats(obs, device):
    return torch.as_tensor(np.asarray(obs, np.float64) / 65535.0 - 0.5, dtype=torch.float32, device=device)


def _linear(g1, obs, precision, device, stride):
    W, b = (torch.as_tensor(np.asarray(x), dtype=torch.float32, device=device) for x in g1)
    xs = _feats(obs, device)
    if stride == 2:
        xs[:, 1::2] = 0.0
    if precision in _TORCH:
        dt = _TORCH[precision]
        return (xs.to(dt) @ W.to(dt) + b.to(dt)).double()
    if precision == "fp8_sim":
        return (xs @ _fp8(W) + _fp8(b)).double()
    # int8: per-row activation scale, per-tensor weight scale
    qx, sx = _q8(xs, dim=1)
    qw, sw = _q8(W)
    qb, sb = _q8(b)
    if device == "cuda":
        # _int_mm refuses mat1.size(1) not a multiple of 8 ("needs to be greater than 0 and a multiple
        # of 8"); zero feature columns contribute exactly nothing, so pad D up to 8k
        pad = (-qx.shape[1]) % 8
        if pad:
            qx = torch.nn.functional.pad(qx, (0, pad))
            qw = torch.nn.functional.pad(qw, (0, 0, 0, pad))
        prod = torch._int_mm(qx.contiguous(), qw.contiguous()).double()
    else:
        prod = (qx.long() @ qw.long()).double()
    return prod * sx.double() * sw.double() + qb.double() * sb.double()


def _tt_feat(g1, obs, precision, device, stride):
    al, G, Wo = (torch.as_tensor(np.asarray(x), dtype=torch.float32, device=device) for x in g1)
    idx = torch.as_tensor((np.asarray(obs).astype(np.int64) >> 12) & 15, device=device)
    n, D = idx.shape
    if precision in _TORCH or precision == "fp8_sim":
        if precision == "fp8_sim":
            al, G, Wo = _fp8(al), _fp8(G), _fp8(Wo)
            dt = torch.float32
        else:
            dt = _TORCH[precision]
            al, G, Wo = al.to(dt), G.to(dt), Wo.to(dt)
        v = al.expand(n, -1)
        for f in range(0, D, stride):
            v = torch.bmm(v.unsqueeze(1), G[f, idx[:, f]]).squeeze(1)
            v = v / torch.clamp(v.abs().amax(1, keepdim=True), min=torch.finfo(dt).tiny)
        return (v @ Wo).double()
    # int8_sim: int8 cores (per-tensor), v re-quantized to int8 per row after each core
    qG, sG = _q8(G)
    qWo, sWo = _q8(Wo)
    qv, sv = _q8(al.expand(n, -1), dim=1)
    Gd = qG.double()
    for f in range(0, D, stride):
        u = torch.bmm(qv.double().unsqueeze(1), Gd[f, idx[:, f]]).squeeze(1)   # exact integer products
        qv, _ = _q8(u, dim=1)                                                 # argmax is scale invariant
    return qv.double() @ qWo.double() * sWo.double()


def precision_logits(family: str, g1, obs, precision: str, device: str | None = None, cheat: bool = False):
    """logits [n, A] (float64 numpy) for one genome g1 over obs [n, D] uint16 at `precision`."""
    if precision not in PRECISIONS:
        raise ValueError(f"precision must be one of {PRECISIONS}, got {precision!r}")
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    fn = {"linear": _linear, "tt_feat": _tt_feat}[family]
    with torch.no_grad():
        return fn(g1, obs, precision, device, 2 if cheat else 1).cpu().numpy()


def exactness(family: str, g1, obs, precision: str, device: str | None = None, cheat: bool = False,
              ref: np.ndarray | None = None) -> dict:
    """agreement with the fp64 oracle on clear rows (and on all rows), plus the max logit error."""
    fam = gm.FAMILIES[family](obs.shape[1])
    if ref is None:
        ref = fam.ref_logits(g1, obs)
    lg = precision_logits(family, g1, obs, precision, device, cheat)
    clear = gm.clear_rows(ref)
    agree = lg.argmax(1) == ref.argmax(1)
    # tt logits are only defined up to a positive per-row scale: compare shapes after max-abs normalising
    nr = lambda z: z / np.maximum(np.abs(z).max(1, keepdims=True), 1e-300)
    err = np.abs(nr(lg) - nr(ref)).max() if family == "tt_feat" else np.abs(lg - ref).max()
    return {"family": family, "precision": precision, "cheat": bool(cheat),
            "substrate": substrate(family, precision, device or ("cuda" if torch.cuda.is_available() else "cpu")),
            "n_rows": int(len(obs)), "n_clear": int(clear.sum()),
            "agree_clear": float(agree[clear].mean()) if clear.any() else float("nan"),
            "agree_all": float(agree.mean()), "max_logit_err": float(err),
            "bytes": nbytes(family, obs.shape[1], precision, fam.A)}
