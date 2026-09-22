"""E-R7-3 (SWARM_R7 s3, O5): B2 SEARCH OVERHEAD per generation with the compiled rollout, for G's B2 v2 admission cost.

E-R6-2 re-costed the B2 admission pilot from rollout time alone (episodes x compiled per-episode seconds); search overhead
(archive sample, mutation, packing, descriptor, archive insert) was outside. This job runs ONE B2 spec through a short
MAP-Elites loop of the same shape as G's baseline (LuaArchive with a seeded sampler, batch 128 genomes x 128 train seeds)
and times each generation's two parts separately:

  rollout   soup.b2.compiled.run_linear over batch x train seeds (float32 linear genome on the raw obs, A x W_OBS + A)
  overhead  everything else in the generation: sample + init/mutate + pack + descriptor + insert

Genome: W [A, W_OBS] float32 + b [A] float32, packed 72 bytes; init N(0, 0.05) W, N(0, 1) b; mutate adds N(0, 0.05) to
~10% of the values. Fitness = total charge over the train seeds (int32). Descriptor cell = min(32, mean charge // 4) * 33 +
min(32, mean moving actions per episode // 4). The loop is a cost probe: no B2 score is read or claimed.

Estimator: median over the timed generations (generation 0 warms the compile and is excluded) of each part; the row gives
effective seconds per evaluated episode INCLUDING overhead, the figure G's b2_screen cost function needs.
Oracle: 2 elites x 2 train seeds replayed by adapter.RefB2 == compiled hash + charges.

    python -m primordial.fabric.worker submit E primordial.cohorts.e.r7_b2_overhead:job --exp E-R7-3-b2-search-overhead \\
        --rows primordial/ledger/rows/E/E-R7-3-b2-search-overhead.jsonl --ttl-cpu-s 600 --kwargs '{}'
"""
from __future__ import annotations

import statistics
import time

import numpy as np

from primordial.soup.b2 import adapter as AD
from primordial.soup.b2 import compiled as CB

ARCHIVE_URL = "redis://127.0.0.1:6394/5"
GLEN = (AD.A * AD.W_OBS + AD.A) * 4
TRAIN0 = 9100


def pack(W: np.ndarray, b: np.ndarray) -> np.ndarray:
    G = len(W)
    return np.ascontiguousarray(np.concatenate([W.reshape(G, -1), b], 1).astype(np.float32)).view(np.uint8).reshape(G, GLEN)


def unpack(raw: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    f = np.ascontiguousarray(raw).view(np.float32).reshape(len(raw), -1)
    return f[:, :AD.A * AD.W_OBS].reshape(-1, AD.A, AD.W_OBS).copy(), f[:, AD.A * AD.W_OBS:].copy()


def init(rng, n: int):
    return (rng.standard_normal((n, AD.A, AD.W_OBS)) * 0.05).astype(np.float32), rng.standard_normal((n, AD.A)).astype(np.float32)


def mutate(rng, W, b, rate: float = 0.1, sigma: float = 0.05):
    W, b = W.copy(), b.copy()
    mW, mb = rng.random(W.shape) < rate, rng.random(b.shape) < rate
    W[mW] += (rng.standard_normal(int(mW.sum())) * sigma).astype(np.float32)
    b[mb] += (rng.standard_normal(int(mb.sum())) * sigma).astype(np.float32)
    return W, b


def descriptor(charge: np.ndarray, moving: np.ndarray, G: int, k: int) -> np.ndarray:
    mc = charge.reshape(G, k).mean(1)
    mm = moving.reshape(G, k).mean(1)
    return (np.minimum(32, mc // 4) * 33 + np.minimum(32, mm // 4)).astype(np.uint32)


def job(ctx, gens: int = 21, batch: int = 128, n_train: int = 128, spec_seed: int = 0, rng_family: int = 4200,
        run_seed: int = 0, archive_url: str = ARCHIVE_URL, campaign_stage: str = "SMOKE", dev: bool = False):
    import numba
    import redis
    from primordial.qd.archive import LuaArchive
    status = "dev" if dev else "record"
    s = AD.planted(spec_seed)
    seeds = list(range(TRAIN0, TRAIN0 + n_train))
    k = len(seeds)
    rng = np.random.Generator(np.random.PCG64([rng_family, run_seed, 2, n_train]))
    arch = LuaArchive(redis.Redis.from_url(archive_url), f"e-r7-b2-oh-f{rng_family}-r{run_seed}", GLEN,
                      [rng_family + 1, run_seed, 2, n_train])
    arch.clear()
    goe = np.repeat(np.arange(batch), k)
    ep_seeds = seeds * batch
    parts = []
    try:
        for gen in range(gens):
            t0 = time.perf_counter()
            par = arch.sample(batch)
            W, b = init(rng, batch) if len(par) == 0 else mutate(rng, *unpack(par))
            t1 = time.perf_counter()
            out = CB.run_linear(s, ep_seeds, W, b, goe)
            t2 = time.perf_counter()
            fit = out["charge"].reshape(batch, k).sum(1).astype(np.int32)
            cells = descriptor(out["charge"], out["moving_actions"], batch, k)
            arch.insert(cells, fit, pack(W, b), np.zeros((batch, 2), np.uint32))
            t3 = time.perf_counter()
            parts.append({"gen": gen, "rollout_s": t2 - t1, "overhead_s": (t1 - t0) + (t3 - t2), "total_s": t3 - t0})
        el = arch.dump()
        best = sorted(el.values(), key=lambda v: (-v[0], v[1]))[:2]
        raw = np.frombuffer(b"".join(v[1] for v in best), np.uint8).reshape(-1, GLEN)
        Wo, bo = unpack(raw)
        ok = 0
        for gi in range(len(raw)):
            for sd in seeds[:2]:
                ref = AD.episode("ref", AD.planted(sd), CB.linear_ref_policy(Wo, bo, gi))
                got = CB.run_linear(AD.planted(sd), [sd], Wo[gi:gi + 1], bo[gi:gi + 1], record=True)
                ok += int(got["hashes"][0] == ref["hash"] and int(got["charge"][0]) == ref["charge"])
        oracle = {"checked": len(raw) * 2, "equal": ok}
        cells_n = len(el)
    finally:
        arch.clear()
    timed = parts[1:] if len(parts) > 1 else parts
    med = {x: float(statistics.median(p[x] for p in timed)) for x in ("rollout_s", "overhead_s", "total_s")}
    eps = batch * k
    ctx.emit({"kind": "b2_search_overhead", "status": status if ok == oracle["checked"] else "control",
              "campaign_stage": campaign_stage, "spec": AD.PLANTED, "gens": gens, "timed_gens": len(timed), "batch": batch,
              "train_seeds": k, "episodes_per_gen": eps, "numba_threads": numba.get_num_threads(),
              "rollout_s_per_gen": med["rollout_s"], "overhead_s_per_gen": med["overhead_s"], "total_s_per_gen": med["total_s"],
              "overhead_fraction": med["overhead_s"] / med["total_s"], "rollout_s_per_episode": med["rollout_s"] / eps,
              "effective_s_per_episode_incl_overhead": med["total_s"] / eps, "overhead_s_per_genome": med["overhead_s"] / batch,
              "gen0_total_s": parts[0]["total_s"], "archive_cells": cells_n, "oracle_refb2": oracle,
              "estimator": "median over generations 1..gens-1 of per-part wall (perf_counter); gen 0 = compile warm, excluded",
              "not_claimed": "any B2 score; the loop is a cost probe"})
