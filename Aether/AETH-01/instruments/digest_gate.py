"""Phase 4 falsification oracle: reproduce the A40 receipt's digests.

Replicates aeth01_bench.py's procedure exactly (same RandomState seeding,
same 2 warmup + 5 measured ticks, same sha256[:16] over the 5 final uint8
fields) and compares against the digests frozen in
Aether/AETH-01/RUNPOD_SCALE_RECEIPT_2026-09-22.md, which were produced on
real A40 hardware with CuPy.

Any single differing digest is SEMANTIC_PARITY_FAILURE.
"""
import hashlib
import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT = Path(sys.argv[1])
MODULE = Path(sys.argv[2])
MAX_SIZE = int(sys.argv[3]) if len(sys.argv) > 3 else 2048

# Frozen on real A40 hardware, RUNPOD_SCALE_RECEIPT_2026-09-22.md.
RECEIPT = {
    16: "1000219c591e1595", 32: "9f65f15cb87b630f", 64: "3ce333436da923b0",
    128: "3ab66c98546a3a95", 256: "7383c7d828504a30", 512: "a04b1321280b0b97",
    1024: "87b8194c84a440d0", 2048: "f2ad4a9ec9dbac4f",
}

SEED = 0x1234ABCD
TICK0 = 0
WRITE_COST, MAINT = 10, 1
REPL_NUMER, REPL_AMT, MUT_NUMER = 1 << 31, 5, 1 << 31
TICKS_TOTAL = 7  # WARMUP 2 + MEASURE 5


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def build_host(n):
    rs = np.random.RandomState(SEED & 0x7FFFFFFF)
    opc = rs.randint(0, 256, size=(n, n)).astype(np.uint8)
    mask = rs.randint(0, 2, size=(n, n)).astype(bool)
    opc = np.where(mask, np.uint8(1), opc).astype(np.uint8)
    arg0 = rs.randint(0, 256, size=(n, n)).astype(np.uint8)
    arg1 = rs.randint(0, 256, size=(n, n)).astype(np.uint8)
    payload = rs.randint(0, 256, size=(n, n)).astype(np.uint8)
    energy = rs.randint(0, 256, size=(n, n)).astype(np.uint8)
    return opc, arg0, arg1, payload, energy


def digest_of(arrays):
    h = hashlib.sha256()
    for a in arrays:
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()[:16]


def run(mod, n):
    arrs = build_host(n)
    tick = TICK0
    for _ in range(TICKS_TOTAL):
        arrs = mod.gpu_step(n, n, SEED, tick, WRITE_COST, MAINT, REPL_NUMER,
                            REPL_AMT, MUT_NUMER, *arrs)[:5]
        tick += 1
    return digest_of(arrs)


if __name__ == "__main__":
    mod = load(MODULE, "_k_under_test")
    print(f"module: {MODULE.name}")
    print(f"{'size':>6} {'computed':>18} {'A40 receipt':>18}  verdict")
    bad = 0
    for n, expect in sorted(RECEIPT.items()):
        if n > MAX_SIZE:
            continue
        got = run(mod, n)
        ok = got == expect
        bad += (not ok)
        print(f"{n:>6} {got:>18} {expect:>18}  {'MATCH' if ok else 'DIFFER'}")
    print()
    print("SEMANTIC_PARITY_FAILURE" if bad else "DIGEST_PARITY_HELD")
    sys.exit(1 if bad else 0)
