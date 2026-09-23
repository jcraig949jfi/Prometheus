"""N4: tt_digits logits as a cuTensorNet contraction.

The tt_digits brain (primordial.brain.genomes.TTDigits) for one genome (alpha [r], G [C,16,r,r], Wo [r,A])
and a batch of B observations is one tensor network:

    alpha[a0]  x  prod_c ( X_c[n, d_c]  G_c[d_c, a_c, a_c+1] )  x  Wo[a_C, k]   ->  logits[n, k]

X_c is the one-hot [B,16] of hex digit c. The batch index n is a hyperedge shared by all C one-hot
tensors, so cuTensorNet contracts the whole batch with no per-row gather. The plan (contraction path)
depends only on shapes, so one Network is planned once and re-executed with reset_operands.

ref_logits (the oracle) normalises v after every core; argmax is scale invariant but logit values are
not, so values are compared after dividing each row by its max |logit| ("row-normalised").
Cheat control: stride 2 drops every odd core (the C6 / C1c skip-half cheat).

Only numpy is needed to build operands; cupy + cuquantum are imported lazily (WSL only).
"""
from __future__ import annotations

import time

import numpy as np

from primordial.brain.tt_policy import digits


def _cq():
    try:  # cuquantum-python >= 25.03
        from cuquantum.tensornet import Network, contract
    except ImportError:  # older layout
        from cuquantum import Network, contract
    return Network, contract


def digit_index(obs: np.ndarray) -> np.ndarray:
    """[B, 4D] int64 hex digits, most significant first (same as TTDigits.index)."""
    return digits(np.asarray(obs).astype(np.uint16)).astype(np.int64)


def build_operands(al, cores, onehots, Wo):
    """Interleave [al, X_0, G_0, X_1, G_1, ..., Wo, out] for the kept cores (any array module).
    Labels are ints (no 52-letter limit): 0 batch, 1 action, bonds from 2, digits after the bonds."""
    N, K, A0 = 0, 1, 2
    D0 = A0 + len(cores) + 1
    ops = [al, [A0]]
    for j, (G, X) in enumerate(zip(cores, onehots)):
        ops += [X, [N, D0 + j], G, [D0 + j, A0 + j, A0 + j + 1]]
    ops += [Wo, [A0 + len(cores), K], [N, K]]
    return ops


def network_operands(g1, obs, stride: int = 1, xp=np, dtype=np.float64):
    """Host-built operands for the batched network (one-hots made with numpy, then moved by xp)."""
    al, G, Wo = g1
    idx = digit_index(obs)
    eye = np.eye(16, dtype=dtype)
    kept = range(0, idx.shape[1], stride)
    return build_operands(xp.asarray(al, dtype=dtype), [xp.asarray(G[c], dtype=dtype) for c in kept],
                          [xp.asarray(eye[idx[:, c]]) for c in kept], xp.asarray(Wo, dtype=dtype))


def contract_logits(g1, obs, stride: int = 1):
    """One-shot cuquantum.contract on the GPU; returns numpy [B, A] (float64)."""
    import cupy as cp
    _, contract = _cq()
    out = contract(*network_operands(g1, obs, stride, xp=cp))
    return cp.asnumpy(out)


class PlannedTT:
    """Plan once per (genome shape, B, stride); execute many genomes/batches of that shape."""

    def __init__(self, g1, obs, stride: int = 1, optimize: dict | None = None):
        import cupy as cp
        Network, _ = _cq()
        self.cp = cp
        ops = network_operands(g1, obs, stride, xp=cp)
        self.labels = ops[1::2] + [ops[-1]]
        self.stride = stride
        t0 = time.perf_counter()
        self.net = Network(*ops)
        self.path, self.info = self.net.contract_path(optimize=optimize)
        cp.cuda.Device().synchronize()
        self.plan_s = time.perf_counter() - t0

    def run(self, g1, obs):
        ops = network_operands(g1, obs, self.stride, xp=self.cp)
        self.net.reset_operands(*ops[0:-1:2])
        out = self.net.contract()
        return self.cp.asnumpy(out)

    def close(self):
        self.net.free()


def row_normalised(logits: np.ndarray) -> np.ndarray:
    return logits / np.maximum(np.abs(logits).max(1, keepdims=True), 1e-300)


def compare_to_oracle(fam, g1, obs, got_logits):
    """argmax agreement on clear rows + max abs error of row-normalised logits (all rows and clear rows)."""
    from primordial.brain import genomes as gm
    ref = fam.ref_logits(g1, obs)
    ok = gm.clear_rows(ref)
    err = np.abs(row_normalised(got_logits) - row_normalised(ref)).max(1)
    return {"n": int(len(obs)), "n_clear": int(ok.sum()),
            "argmax_mismatch_clear": int((got_logits.argmax(1)[ok] != ref.argmax(1)[ok]).sum()),
            "max_abs_err_rownorm_clear": float(err[ok].max()) if ok.any() else None,
            "max_abs_err_rownorm_all": float(err.max())}
