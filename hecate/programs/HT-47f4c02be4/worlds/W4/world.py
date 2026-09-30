"""HT-47f4c02be4 / W4 world: factor-inference arrow with a predictive prior.

See IMPLEMENTATION_NOTES.md for the spec -> code map. Writes rows.jsonl
(one row per arm x seed x s, flushed per row) and run_meta.json.
"""
import json
import os
import time

import numpy as np
from sympy import primerange

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "rows.jsonl")
META = os.path.join(HERE, "run_meta.json")

P = np.array(list(primerange(2, 10 ** 4)), dtype=np.int64)
NP = len(P)  # 1229
IDX = np.arange(NP, dtype=np.int64)
N_SAMPLES = 10000
SEEDS = [0, 1, 2, 3, 4]
STEPS = [1, 3, 10]
CHUNK = 1000


def walk(rng, s, T):
    i = np.empty(T, dtype=np.int64)
    i[0] = rng.integers(0, NP)
    steps = rng.choice([-s, s], size=T - 1) if s > 0 else np.zeros(T - 1, dtype=np.int64)
    for t in range(1, T):
        x = i[t - 1] + steps[t - 1]
        if x < 0:
            x = -x
        if x > NP - 1:
            x = 2 * (NP - 1) - x
        i[t] = x
    return i


def make_stream(seed, s):
    rng = np.random.default_rng(seed * 1000 + s)
    ip = walk(rng, s, N_SAMPLES)
    iq = walk(rng, s, N_SAMPLES)
    return ip, iq


def first_divisor_position(n, cand_idx):
    """n: (B,), cand_idx: (B, NP) candidate prime indices in trial order.
    Performs the trial divisions and returns 1-based position of first
    exact divisor."""
    rem = n[:, None] % P[cand_idx]
    hit = rem == 0
    assert hit.any(axis=1).all()
    return hit.argmax(axis=1) + 1


def ascending_cost(ip, iq):
    n = P[ip] * P[iq]
    out = np.empty(len(n), dtype=np.int64)
    for a in range(0, len(n), CHUNK):
        b = min(a + CHUNK, len(n))
        cand = np.broadcast_to(IDX, (b - a, NP))
        out[a:b] = first_divisor_position(n[a:b], cand)
    return out


def prior_ordered_cost(ip, iq):
    """Order candidates by min index distance to the previous sample's two
    factors; ties by ascending prime. t = 0 falls back to ascending."""
    n = P[ip] * P[iq]
    out = np.empty(len(n), dtype=np.int64)
    out[:1] = ascending_cost(ip[:1], iq[:1])
    for a in range(1, len(n), CHUNK):
        b = min(a + CHUNK, len(n))
        rp = ip[a - 1:b - 1][:, None]
        rq = iq[a - 1:b - 1][:, None]
        d = np.minimum(np.abs(IDX[None, :] - rp), np.abs(IDX[None, :] - rq))
        key = d * NP + IDX[None, :]
        order = np.argsort(key, axis=1, kind="stable")
        out[a:b] = first_divisor_position(n[a:b], order)
    return out


def memo_cost(ip, iq):
    """Diagnostic: try the two previous factors first (smaller first), then
    the remaining primes ascending. t = 0 ascending."""
    n = P[ip] * P[iq]
    out = np.empty(len(n), dtype=np.int64)
    out[:1] = ascending_cost(ip[:1], iq[:1])
    for a in range(1, len(n), CHUNK):
        b = min(a + CHUNK, len(n))
        rp = ip[a - 1:b - 1][:, None]
        rq = iq[a - 1:b - 1][:, None]
        lo = np.minimum(rp, rq)
        hi = np.maximum(rp, rq)
        key = np.where(IDX[None, :] == lo, -2, np.where(IDX[None, :] == hi, -1, IDX[None, :]))
        order = np.argsort(key, axis=1, kind="stable")
        out[a:b] = first_divisor_position(n[a:b], order)
    return out


def stats(c):
    return {"mean_cost": float(c.mean()), "sd_cost": float(c.std(ddof=1)),
            "n": int(len(c)), "first_try_frac": float((c == 1).mean()),
            "mean_ratio_infer_over_generate": float(c.mean() / 1.0)}


def main():
    if os.path.exists(ROWS):
        os.remove(ROWS)
    t0w, t0c = time.time(), time.process_time()
    common = {"n_primes": NP, "prime_bound": 10 ** 4, "n_samples": N_SAMPLES,
              "walk": "rademacher +-s, reflecting, uniform start",
              "prior_rule": "min index distance to previous (p,q); ties ascending; t=0 ascending",
              "generate_ops_per_sample": 1}
    with open(ROWS, "w", encoding="utf-8") as fh:
        def emit(row):
            row.update(common)
            fh.write(json.dumps(row) + "\n")
            fh.flush()

        for seed in SEEDS:
            # positive control s = 0
            ip, iq = make_stream(seed, 0)
            emit({"arm": "POSITIVE_CONTROL", "seed": seed, "s": 0,
                  "prior": stats(prior_ordered_cost(ip, iq)),
                  "ascending": stats(ascending_cost(ip, iq))})
            for s in STEPS:
                ip, iq = make_stream(seed, s)
                asc = ascending_cost(ip, iq)
                pri = prior_ordered_cost(ip, iq)
                emit({"arm": "CONTROL", "seed": seed, "s": s, "ascending": stats(asc)})
                emit({"arm": "TREATMENT", "seed": seed, "s": s, "prior": stats(pri),
                      "ascending_same_stream_mean": float(asc.mean()),
                      "range_idx_p": [int(ip.min()), int(ip.max())],
                      "range_idx_q": [int(iq.min()), int(iq.max())]})
                emit({"arm": "MEMO", "seed": seed, "s": s, "memo": stats(memo_cost(ip, iq)),
                      "ascending_same_stream_mean": float(asc.mean())})
                perm = np.random.default_rng(seed * 1000 + s + 500).permutation(N_SAMPLES)
                sp, sq = ip[perm], iq[perm]
                emit({"arm": "NULL_TWIN", "seed": seed, "s": s,
                      "prior": stats(prior_ordered_cost(sp, sq)),
                      "ascending": stats(ascending_cost(sp, sq))})
                if s == 1:
                    cheat = np.ones(N_SAMPLES, dtype=np.int64)  # injected, no mechanism
                    emit({"arm": "CHEAT", "seed": seed, "s": s, "prior": stats(cheat),
                          "ascending": stats(asc)})
    meta = {"wall_s": time.time() - t0w, "process_cpu_s": time.process_time() - t0c}
    meta["core_minutes"] = meta["process_cpu_s"] / 60.0
    with open(META, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
