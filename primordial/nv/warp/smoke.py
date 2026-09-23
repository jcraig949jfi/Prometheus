"""W smoke: warp-lang 1.17 on the Blackwell RTX 5060 Ti. One integer kernel (the wforge
xorshift64* step, uint64 wraparound) on CPU and CUDA, compared against Python big-int arithmetic.

    python -m primordial.nv.warp.smoke          (nv-venv-w)
"""
from __future__ import annotations

import json
import sys

import numpy as np
import warp as wp

MASK64 = (1 << 64) - 1
C64 = 0x2545F4914F6CDD1D


@wp.kernel
def xs_kernel(s: wp.array(dtype=wp.uint64), out: wp.array(dtype=wp.uint64)):
    i = wp.tid()
    x = s[i]
    x = x ^ (x << wp.uint64(13))
    x = x ^ (x >> wp.uint64(7))
    x = x ^ (x << wp.uint64(17))
    s[i] = x
    out[i] = x * wp.uint64(0x2545F4914F6CDD1D)


def xs_ref(x: int) -> tuple[int, int]:
    x ^= (x << 13) & MASK64
    x ^= x >> 7
    x ^= (x << 17) & MASK64
    return x, (x * C64) & MASK64


def run(n: int = 4096, rounds: int = 8, seed: int = 1) -> dict:
    wp.init()
    s0 = np.random.default_rng(seed).integers(1, 2**63, size=n, dtype=np.uint64)
    s0[:3] = [1, 0xDEADBEEF, MASK64 - 2]
    want = []
    st = [int(v) for v in s0]
    for _ in range(rounds):
        outs = []
        for i in range(n):
            st[i], o = xs_ref(st[i])
            outs.append(o)
        want.append(np.array(outs, np.uint64))
    res = {"warp": wp.__version__, "devices": {}}
    for dev in [d.alias for d in wp.get_devices()]:
        a = wp.array(s0, dtype=wp.uint64, device=dev)
        o = wp.zeros(n, dtype=wp.uint64, device=dev)
        ok = True
        for r in range(rounds):
            wp.launch(xs_kernel, dim=n, inputs=[a, o], device=dev)
            ok &= bool(np.array_equal(o.numpy(), want[r]))
        d = wp.get_device(dev)
        res["devices"][dev] = {"name": d.name, "exact": ok,
                               "arch": getattr(d, "arch", None)}
    return res


def main() -> int:
    res = run()
    print(json.dumps(res))
    return 0 if all(v["exact"] for v in res["devices"].values()) and "cuda:0" in res["devices"] else 1


if __name__ == "__main__":
    sys.exit(main())
