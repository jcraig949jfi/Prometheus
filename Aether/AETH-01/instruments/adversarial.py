"""Adversarial differential aimed AT the narrowing, not around it.

Every case here is chosen because it is where an int64 -> int16 / uint8
change would first go wrong: the extremes of the validated parameter
domain (write_cost/maintenance_cost/replenish_amount in [0,255]),
saturating energy, always-on and never-on perturbation and
replenishment, all-WRITE grids, all-ENERGY target fields, degenerate
lattice shapes, and the top of the seed/tick domain.

The single most dangerous case: energy 0 with write_cost 255 and
target_field == ENERGY, which drives transfer_amt to -255. uint8 would
wrap it; int16 must not.
"""
import importlib.util
import itertools
import sys
from pathlib import Path

import numpy as np

ROOT = Path(sys.argv[1])
VARIANT = Path(sys.argv[2])
REF = ROOT / "Aether" / "test" / "reference" / "gpu_aeth01.py"
MASK64 = (1 << 64) - 1
U33_MAX = 1 << 32


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ref = load(REF, "_a_ref")
var = load(VARIANT, "_a_var")


def const(H, W, v):
    return np.full((H, W), v, dtype=np.uint8)


def run(mod, H, W, p, f):
    return mod.gpu_step(H, W, p["seed"], p["tick"], p["write_cost"],
                        p["maintenance_cost"], p["replenish_numer"],
                        p["replenish_amount"], p["mut_numer"],
                        *[a.copy() for a in f])


def compare(name, H, W, p, f):
    a, b = run(ref, H, W, p, f), run(var, H, W, p, f)
    for i in range(5):
        if not np.array_equal(a[i], b[i]):
            return f"FAIL {name}: field {i} differs (H={H} W={W} {p})"
    if a[5] != b[5]:
        return f"FAIL {name}: counters differ {a[5]} vs {b[5]} (H={H} W={W})"
    return None


def cases():
    shapes = [(1, 1), (1, 2), (2, 1), (1, 8), (8, 1), (2, 2), (3, 5), (5, 3), (16, 16)]
    extremes = [0, 1, 254, 255]
    # 1. the narrowing-killer: max write_cost, zero energy, all ENERGY targets
    for H, W in shapes:
        for wc in extremes:
            for energy in (0, 1, 127, 255):
                for tf_arg1 in (4, 9, 255):   # arg1 % 5 == 4 -> ENERGY
                    yield (f"transfer-extreme wc={wc} e={energy} arg1={tf_arg1}",
                           H, W,
                           dict(seed=0xFFFFFFFFFFFFFFFF, tick=MASK64,
                                write_cost=wc, maintenance_cost=255,
                                replenish_numer=U33_MAX, replenish_amount=255,
                                mut_numer=U33_MAX),
                           [const(H, W, 1), const(H, W, 0), const(H, W, tf_arg1),
                            const(H, W, 255), const(H, W, energy)])
    # 2. perturbation and replenishment fully on / fully off
    for mut, rep in itertools.product((0, U33_MAX), (0, U33_MAX)):
        for H, W in [(4, 4), (7, 3)]:
            rng = np.random.default_rng(99)
            f = [rng.integers(0, 256, size=(H, W), dtype=np.uint8) for _ in range(5)]
            f[0] = const(H, W, 1)
            yield (f"mut={mut} repl={rep}", H, W,
                   dict(seed=0, tick=0, write_cost=0, maintenance_cost=0,
                        replenish_numer=rep, replenish_amount=255, mut_numer=mut), f)
    # 3. every direction/target-field combination, all sites emitting
    for d, tf in itertools.product(range(4), range(5)):
        H = W = 6
        yield (f"dir={d} field={tf}", H, W,
               dict(seed=0xDEADBEEF, tick=7, write_cost=1, maintenance_cost=1,
                    replenish_numer=0, replenish_amount=0, mut_numer=U33_MAX),
               [const(H, W, 1), const(H, W, d), const(H, W, tf),
                const(H, W, 255), const(H, W, 255)])
    # 4. energy saturation: max payload, max replenish, zero maintenance
    for H, W in [(4, 4), (9, 2)]:
        yield ("saturation", H, W,
               dict(seed=1, tick=1, write_cost=0, maintenance_cost=0,
                    replenish_numer=U33_MAX, replenish_amount=255,
                    mut_numer=0),
               [const(H, W, 1), const(H, W, 0), const(H, W, 4),
                const(H, W, 255), const(H, W, 255)])
    # 5. nobody emits (opcode never WRITE) and everybody starves
    for H, W in [(3, 3), (5, 5)]:
        yield ("no-emitters", H, W,
               dict(seed=5, tick=5, write_cost=255, maintenance_cost=255,
                    replenish_numer=0, replenish_amount=0, mut_numer=U33_MAX),
               [const(H, W, 2), const(H, W, 3), const(H, W, 4),
                const(H, W, 200), const(H, W, 0)])


if __name__ == "__main__":
    total = 0
    failures = []
    for name, H, W, p, f in cases():
        total += 1
        bad = compare(name, H, W, p, f)
        if bad:
            failures.append(bad)
    print(f"adversarial: {total - len(failures)}/{total} bit-exact")
    for line in failures[:20]:
        print("  " + line)
    print("SEMANTIC_PARITY_FAILURE" if failures else "ADVERSARIAL_PARITY_HELD")
    sys.exit(1 if failures else 0)
