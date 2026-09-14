"""E4: MAP-Elites in lane B's batched Encounter, under the wforge trace-hash oracle.

  python -m primordial.qd.e4_run [--worlds 1,2,3,4,5] [--gens 100] [--batch 256] [--tag full]

Genome: open-loop action tensor [T, S, W], values in [0, 16), packed as bytes (padded
to a multiple of 4 for the Lua tie-break). Fitness: summed final charge (clipped at 0)
over 8 fixed episode seeds, evaluated as envs of B's NpEncounter. Descriptor (genome-
intrinsic): abstain-row fraction x mean action magnitude, 33x33 cells. Archive: E1's
Redis LuaArchive on the lane E substrate.

Oracle: 32 sampled elites x 8 seeds replayed in the wforge Encounter (read-only); each
episode must match the batched world's trace hash AND final charge.
Cheat control: the same QD run on B's skip_lin world; its elites must fail the oracle.
Positive control: QD best fitness vs random search at equal genome evaluations.
wforge is imported through lane B's common.py and never edited.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

import numpy as np
import redis

from primordial.qd.archive import UNSEEDED, LuaArchive
from primordial.soup.b1.common import Encounter, make_world
from primordial.soup.b1.np_world import NpEncounter

EXP = "E4-qd-on-encounter"
ROOT = pathlib.Path(__file__).resolve().parents[2]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "E" / f"{EXP}.jsonl"
SEEDS = np.arange(9100, 9108, dtype=np.int64)
GRID = 33
N_ORACLE = 32


class Spec:
    def __init__(self, gen_seed: int):
        self.gen_seed = gen_seed
        self.mech, self.wid = make_world(gen_seed)
        m = self.mech
        self.T, self.S, self.W = m.horizon, m.n_slots, m.act_width
        self.n = self.T * self.S * self.W
        self.glen = (self.n + 3) // 4 * 4

    def pack(self, G: np.ndarray) -> np.ndarray:
        out = np.zeros((len(G), self.glen), np.uint8)
        out[:, :self.n] = G.reshape(len(G), -1)
        return out

    def unpack(self, B: np.ndarray) -> np.ndarray:
        return B[:, :self.n].reshape(-1, self.T, self.S, self.W)


def init_genomes(rng, spec: Spec, P: int) -> np.ndarray:
    G = rng.integers(0, 16, size=(P, spec.T, spec.S, spec.W), dtype=np.uint8)
    abstain = rng.random((P, 1, 1, 1))
    return G * (rng.random((P, spec.T, spec.S, 1)) >= abstain)


def mutate(rng, spec: Spec, G: np.ndarray) -> np.ndarray:
    G = np.where(rng.random(G.shape) < 2.0 / spec.n, rng.integers(0, 16, G.shape, dtype=np.uint8), G)
    zero_rows = rng.random(G.shape[:3] + (1,)) < 1.0 / spec.T
    fill_rows = rng.random(G.shape[:3] + (1,)) < 1.0 / spec.T
    G = np.where(zero_rows, 0, G)
    return np.where(fill_rows, rng.integers(0, 16, G.shape, dtype=np.uint8), G).astype(np.uint8)


def descriptor(G: np.ndarray) -> np.ndarray:
    x = (G % 8).astype(np.int64)
    abst = (x.sum(-1) == 0).mean(axis=(1, 2))
    mag = x.mean(axis=(1, 2, 3)) / 7.0
    return (np.rint(abst * 32) * GRID + np.rint(mag * 32)).astype(np.uint32)


def evaluate(spec: Spec, G: np.ndarray, cheat: str = "", record: bool = False):
    """-> (fitness int32 [P], per-episode charge [P*8, S], world). env e = genome e//8, seed e%8."""
    P, k = len(G), len(SEEDS)
    n = P * k
    w = NpEncounter(spec.mech, spec.wid, record=np.arange(n) if record else None, cheat=cheat, with_obs=False)
    w.reset(np.tile(SEEDS, P))
    A = np.repeat(G, k, axis=0).astype(np.int32)
    for t in range(spec.T):
        _, _, done = w.step(A[:, t])
        if done.all():
            break
    ep = np.clip(w.charge, 0, None)
    return ep.sum(1).reshape(P, k).sum(1).astype(np.int32), ep, w


def wforge_replay(spec: Spec, g: np.ndarray, seed: int) -> tuple[str, np.ndarray]:
    e = Encounter(spec.mech, spec.wid, int(seed))
    done, t = False, 0
    while not done:
        done = e.step([[int(v) for v in g[t, s]] for s in range(spec.S)])
        t += 1
    out = e.outcome()
    return out["trace_hash"], np.array([max(0, p["final_charge"]) for p in out["per_slot"]])


def oracle(spec: Spec, G: np.ndarray, cheat: str) -> dict:
    fit, ep, w = evaluate(spec, G, cheat=cheat, record=True)
    hashes = [h.decode() for h in w.trace_hashes()]
    k = len(SEEDS)
    bad_hash = bad_charge = 0
    bad_elite = np.zeros(len(G), bool)
    true_fit = np.zeros(len(G), np.int64)
    t0 = time.perf_counter()
    for e in range(len(G) * k):
        h, ch = wforge_replay(spec, G[e // k], SEEDS[e % k])
        true_fit[e // k] += ch.sum()
        hb, cb = h != hashes[e], not np.array_equal(ch, ep[e])
        bad_hash += hb
        bad_charge += cb
        bad_elite[e // k] |= hb or cb
    wf_s = time.perf_counter() - t0
    return {"elites": len(G), "episodes": len(G) * k, "elites_failing": int(bad_elite.sum()),
            "episodes_hash_mismatch": int(bad_hash), "episodes_charge_mismatch": int(bad_charge),
            "fitness_inflation_mean": round(float((fit - true_fit).mean()), 2),
            "wforge_episodes_per_s": round(len(G) * k / wf_s, 1)}


def qd(spec: Spec, r, run: str, cheat: str, gens: int, batch: int, seed: int) -> tuple[LuaArchive, dict]:
    arch = LuaArchive(r, run, spec.glen, UNSEEDED)
    arch.clear()
    rng = np.random.Generator(np.random.PCG64([seed, spec.gen_seed]))
    t_eval, best = 0.0, 0
    t0 = time.perf_counter()
    for _ in range(gens):
        parents = arch.sample(batch)
        kids = init_genomes(rng, spec, batch) if len(parents) == 0 else mutate(rng, spec, spec.unpack(parents))
        s = time.perf_counter()
        fit, _, _ = evaluate(spec, kids, cheat)
        t_eval += time.perf_counter() - s
        best = max(best, int(fit.max()))
        arch.insert(descriptor(kids), fit, spec.pack(kids), np.zeros((batch, 2), np.uint32))
    wall = time.perf_counter() - t0
    elites = arch.dump()
    return arch, {"best": best, "cells": len(elites), "qd_score": int(sum(v[0] for v in elites.values())),
                  "wall_s": round(wall, 2), "episodes_per_s_eval": round(gens * batch * len(SEEDS) / t_eval, 1),
                  "episode_steps_per_s_eval": round(gens * batch * len(SEEDS) * spec.T / t_eval, 1)}


def random_search(spec: Spec, n_genomes: int, batch: int, seed: int) -> int:
    rng = np.random.Generator(np.random.PCG64([seed + 1, spec.gen_seed]))
    best = 0
    for _ in range(n_genomes // batch):
        fit, _, _ = evaluate(spec, init_genomes(rng, spec, batch))
        best = max(best, int(fit.max()))
    return best


def sample_elites(arch: LuaArchive, spec: Spec, seed: int) -> np.ndarray:
    elites = arch.dump()
    cells = sorted(elites)
    rng = np.random.Generator(np.random.PCG64(seed))
    pick = rng.choice(len(cells), size=min(N_ORACLE, len(cells)), replace=False)
    raw = np.frombuffer(b"".join(elites[cells[i]][1] for i in sorted(pick)), np.uint8).reshape(-1, spec.glen)
    return spec.unpack(raw)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--worlds", default="1,2,3,4,5"); p.add_argument("--gens", type=int, default=100)
    p.add_argument("--batch", type=int, default=256); p.add_argument("--port", type=int, default=6394)
    p.add_argument("--tag", default="full")
    a = p.parse_args()
    ROWS.parent.mkdir(parents=True, exist_ok=True)
    r = redis.Redis(host="127.0.0.1", port=a.port)
    for gs in [int(x) for x in a.worlds.split(",")]:
        spec = Spec(gs)
        m = spec.mech
        base = {"exp_id": EXP, "tag": a.tag, "gen_seed": gs, "world_id": spec.wid, "T": spec.T, "S": spec.S,
                "W": spec.W, "n_regs": m.n_regs, "lin_ops": len(m.lin_ops), "gens": a.gens, "batch": a.batch,
                "seeds": len(SEEDS)}
        arch, hon = qd(spec, r, f"e4hon-{gs}", "", a.gens, a.batch, seed=41)
        o_hon = oracle(spec, sample_elites(arch, spec, 5), "")
        arch.clear()
        rnd_best = random_search(spec, a.gens * a.batch, a.batch, seed=41)
        carch, che = qd(spec, r, f"e4cheat-{gs}", "skip_lin", a.gens, a.batch, seed=41)
        o_che = oracle(spec, sample_elites(carch, spec, 5), "skip_lin")
        carch.clear()
        row = {**base, "honest": hon, "oracle_honest": o_hon, "random_best": rnd_best,
               "qd_beats_random": hon["best"] > rnd_best, "cheat_skip_lin": che, "oracle_cheat": o_che,
               "ts": time.time()}
        print(json.dumps(row), flush=True)
        with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
