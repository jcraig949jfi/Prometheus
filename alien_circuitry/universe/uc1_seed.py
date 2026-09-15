"""U-C1 seed freeze (Gate C).  Committed BEFORE any n=7 measurement of this generator set.

Seed derivation is deterministic from a fixed string; nothing here was chosen after looking at outcomes.
The n=6 seeds 1 and 2 used in evidence/universe_c_probes/ are burnt (their consequence structure was inspected)
and are not eligible.  The frozen map may not be redrawn if its results are unattractive.
"""
import hashlib, random
import numpy as np

N = 7
TARGET_RANK = N - 2  # rank-5 map
SEED_STRING = "AC01|U-C1|rank5map|n=7|frozen-2026-09-12"
SEED = int(hashlib.sha256(SEED_STRING.encode()).hexdigest()[:16], 16)


def frozen_rank5_map(n: int = N, seed: int = SEED) -> np.ndarray:
    rr = random.Random(seed)
    while True:
        m = [rr.randrange(n) for _ in range(n)]
        if len(set(m)) == TARGET_RANK:
            return np.array(m, dtype=np.int64)


FROZEN_MAP = frozen_rank5_map()
FROZEN_MAP_SHA256 = hashlib.sha256(",".join(map(str, FROZEN_MAP.tolist())).encode()).hexdigest()


def uc1_generators(n: int = N) -> dict:
    return {"cycle": np.array([(i + 1) % n for i in range(n)]), "swap01": np.array([1, 0] + list(range(2, n))), "map_r5": FROZEN_MAP.copy()}


def pch_generators(n: int = N) -> dict:
    return {"cycle": np.array([(i + 1) % n for i in range(n)]), "swap01": np.array([1, 0] + list(range(2, n))), "collapse01": np.array([1] + list(range(1, n)))}


if __name__ == "__main__":
    print({"seed_string": SEED_STRING, "seed": SEED, "map": FROZEN_MAP.tolist(), "rank": len(set(FROZEN_MAP.tolist())), "sha256": FROZEN_MAP_SHA256})
