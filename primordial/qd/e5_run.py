"""E5: MAP-Elites over closed-loop tensor-train brains in lane B's Encounter.

  python -m primordial.qd.e5_run [--worlds 1,2,3,4,5] [--gens 60] [--batch 128] [--tag full]

Genome = lane C's TT policy (alpha [r], G [d,16,r,r], W [r,A]; d = 4 hex digits per obs
feature) + an A x W action codebook (row 0 = abstain), packed float32 LE + uint8.
Lane E runs a population-batched float32 forward (argmax is scale invariant, so v is
renormalised per core); lane C's ref64_logits is the brain oracle. World = lane B's
NpEncounter (with_obs), fitness = summed final charge over 8 seeds, descriptor =
(abstain fraction, magnitude) of actions TAKEN by live slots.

Oracles on 16 sampled elites (hot-path outputs recorded during a rollout):
  world  recorded actions replayed in wforge: trace hash AND final charge
         cheat: the same elites rolled out in B's skip_lin world must fail
  brain  emitted action == argmax ref64_logits(obs) on clear-margin rows
         cheat: a skip-odd-cores forward must mismatch
Comparator: E4b open-loop QD best per world (median over its 3 run seeds).
Reads lane B (soup/b1) and lane C (brain/tt_policy) read-only.
"""
from __future__ import annotations

import argparse
import json
import time
from statistics import median

import numpy as np
import redis

from primordial.brain.tt_policy import TTPolicy, digits, ref64_logits
from primordial.qd import e4_run as E4
from primordial.qd.archive import LuaArchive
from primordial.soup.b1.np_world import NpEncounter

EXP = "E5-qd-closed-loop-tt-brains"
ROWS = E4.ROWS.with_name(f"{EXP}.jsonl")
HOT = __import__("pathlib").Path("C:/Users/jcrai/lab/pm-data/E") / EXP  # hot data never on F:
R, A, N_ORACLE, ROWS_PER_ELITE = 3, 8, 16, 256
SEEDS = E4.SEEDS


class BrainSpec(E4.Spec):
    def __init__(self, gen_seed: int):
        super().__init__(gen_seed)
        self.D = len(self.mech.obs_perm)
        self.d = 4 * self.D
        self.sizes = [R, self.d * 16 * R * R, R * A]
        self.nf = sum(self.sizes)
        self.nbytes = self.nf * 4 + A * self.W
        self.glen = (self.nbytes + 3) // 4 * 4

    def pack(self, g) -> np.ndarray:
        al, G, W, C = g
        P = len(al)
        f = np.concatenate([al.reshape(P, -1), G.reshape(P, -1), W.reshape(P, -1)], 1).astype("<f4")
        out = np.zeros((P, self.glen), np.uint8)
        out[:, :self.nf * 4] = f.view(np.uint8)
        out[:, self.nf * 4:self.nbytes] = C.reshape(P, -1)
        return out

    def unpack(self, B: np.ndarray):
        P = len(B)
        f = np.ascontiguousarray(B[:, :self.nf * 4]).view("<f4").reshape(P, self.nf)
        a, b = self.sizes[0], self.sizes[0] + self.sizes[1]
        return (f[:, :a].copy(), f[:, a:b].reshape(P, self.d, 16, R, R).copy(), f[:, b:].reshape(P, R, A).copy(),
                B[:, self.nf * 4:self.nbytes].reshape(P, A, self.W).copy())


def init_brains(rng, bs: BrainSpec, P: int):
    al = rng.standard_normal((P, R)).astype(np.float32)
    G = (np.eye(R, dtype=np.float32) + 0.3 * rng.standard_normal((P, bs.d, 16, R, R))).astype(np.float32)
    W = rng.standard_normal((P, R, A)).astype(np.float32)
    C = rng.integers(0, 16, size=(P, A, bs.W), dtype=np.uint8)
    C[:, 0] = 0
    return al, G, W, C


def mutate_brains(rng, bs: BrainSpec, g):
    al, G, W, C = (x.copy() for x in g)
    for x in (al, G, W):
        m = rng.random(x.shape) < 0.05
        x += (m * 0.2 * rng.standard_normal(x.shape)).astype(np.float32)
    m = rng.random(C.shape) < 1.0 / (A * bs.W)
    C = np.where(m, rng.integers(0, 16, C.shape, dtype=np.uint8), C)
    C[:, 0] = 0
    return al, G, W, C


def forward(g, obs: np.ndarray, gidx: np.ndarray, skip_odd: bool = False) -> np.ndarray:
    """obs int [n, D], gidx [n] genome per row -> action index int [n]."""
    al, G, W, _ = g
    dig = digits(obs.astype(np.uint16))
    v = al[gidx]
    for c in range(dig.shape[1]):
        if skip_odd and c % 2:
            continue
        v = np.einsum("nr,nrs->ns", v, G[gidx, c, dig[:, c]])
        v /= np.maximum(np.abs(v).max(1, keepdims=True), 1e-30)
    return np.einsum("nr,nra->na", v, W[gidx]).argmax(1)


def rollout(bs: BrainSpec, g, world_cheat: str = "", skip_odd: bool = False, log: bool = False):
    P, k, S, D = len(g[0]), len(SEEDS), bs.S, bs.D
    n = P * k
    w = NpEncounter(bs.mech, bs.wid, record=np.arange(n) if log else None, cheat=world_cheat, with_obs=True)
    obs = w.reset(np.tile(SEEDS, P))
    genv = np.repeat(np.arange(P), k)
    grow = np.repeat(genv, S)
    abst = np.zeros(n); mag = np.zeros(n); cnt = np.zeros(n)
    L = {"acts": np.zeros((bs.T, n, S, bs.W), np.int32), "obs": np.zeros((bs.T, n, S, D), np.int64),
         "idx": np.zeros((bs.T, n, S), np.int64), "live": np.zeros((bs.T, n, S), bool)} if log else None
    for t in range(bs.T):
        idx = forward(g, obs.reshape(n * S, D), grow, skip_odd).reshape(n, S)
        a = g[3][genv[:, None], idx].astype(np.int32)
        live = w.alive & ~w.done[:, None]
        x = (a % 8).sum(-1)
        abst += ((x == 0) & live).sum(1); mag += (x * live).sum(1); cnt += live.sum(1)
        if log:
            L["acts"][t], L["obs"][t], L["idx"][t], L["live"][t] = a, obs, idx, live
        obs, _, done = w.step(a)
        if done.all():
            break
    fit = np.clip(w.charge, 0, None).sum(1).reshape(P, k).sum(1).astype(np.int32)
    ab = abst.reshape(P, k).sum(1) / np.maximum(cnt.reshape(P, k).sum(1), 1)
    mg = mag.reshape(P, k).sum(1) / np.maximum(cnt.reshape(P, k).sum(1) * bs.W * 7, 1)
    cells = (np.rint(ab * 32) * E4.GRID + np.rint(np.clip(mg, 0, 1) * 32)).astype(np.uint32)
    return fit, cells, w, L


def world_oracle(bs, g, world_cheat=""):
    _, _, w, L = rollout(bs, g, world_cheat=world_cheat, log=True)
    hashes = [h.decode() for h in w.trace_hashes()]
    k, bad = len(SEEDS), np.zeros(len(g[0]), bool)
    ep = np.clip(w.charge, 0, None)
    mm_hash = mm_charge = 0
    for e in range(len(g[0]) * k):
        h, ch = E4.wforge_replay(bs, L["acts"][:, e], SEEDS[e % k])
        hb, cb = h != hashes[e], not np.array_equal(ch, ep[e])
        mm_hash += hb; mm_charge += cb
        bad[e // k] |= hb or cb
    return {"elites": len(g[0]), "elites_failing": int(bad.sum()), "episodes_hash_mismatch": int(mm_hash),
            "episodes_charge_mismatch": int(mm_charge)}


def brain_oracle(bs, g, skip_odd=False, seed=0):
    _, _, _, L = rollout(bs, g, skip_odd=skip_odd, log=True)
    rng = np.random.Generator(np.random.PCG64(seed))
    k, S = len(SEEDS), bs.S
    elites_bad, rows_clear, rows_mm = 0, 0, 0
    for p in range(len(g[0])):
        pol = TTPolicy(g[0][p].astype(np.float64), g[1][p].astype(np.float64), g[2][p].astype(np.float64))
        t_i, e_i, s_i = np.nonzero(L["live"][:, p * k:(p + 1) * k])
        if len(t_i) == 0:
            continue
        pick = rng.choice(len(t_i), size=min(ROWS_PER_ELITE, len(t_i)), replace=False)
        t_i, e_i, s_i = t_i[pick], e_i[pick] + p * k, s_i[pick]
        ref = ref64_logits(pol, L["obs"][t_i, e_i, s_i])
        top = np.sort(ref, 1)
        clear = (top[:, -1] - top[:, -2]) > 1e-4 * np.maximum(np.abs(top[:, -1]), 1e-30)
        mm = (ref.argmax(1) != L["idx"][t_i, e_i, s_i]) & clear
        rows_clear += int(clear.sum()); rows_mm += int(mm.sum())
        elites_bad += bool(mm.any())
    return {"elites": len(g[0]), "elites_mismatching": elites_bad, "clear_rows": rows_clear, "mismatched_rows": rows_mm}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--worlds", default="1,2,3,4,5"); p.add_argument("--gens", type=int, default=60)
    p.add_argument("--batch", type=int, default=128); p.add_argument("--port", type=int, default=6394)
    p.add_argument("--tag", default="full")
    a = p.parse_args()
    HOT.mkdir(parents=True, exist_ok=True)
    r = redis.Redis(port=a.port)
    e4b = [json.loads(l) for l in open(E4.ROWS.with_name("E4b-qd-encounter-archive-positive.jsonl"))]
    for gs in [int(x) for x in a.worlds.split(",")]:
        bs = BrainSpec(gs)
        open_best = median(x["qd"]["best"] for x in e4b if x["tag"] == "full" and x["gen_seed"] == gs)
        arch = LuaArchive(r, f"e5-{gs}", bs.glen)
        arch.clear()
        rng = np.random.Generator(np.random.PCG64([55, gs]))
        t0, t_roll = time.perf_counter(), 0.0
        for _ in range(a.gens):
            par = arch.sample(a.batch)
            g = init_brains(rng, bs, a.batch) if len(par) == 0 else mutate_brains(rng, bs, bs.unpack(par))
            s = time.perf_counter()
            fit, cells, _, _ = rollout(bs, g)
            t_roll += time.perf_counter() - s
            arch.insert(cells, fit, bs.pack(g), np.zeros((a.batch, 2), np.uint32))
        el = arch.dump()
        best = max(v[0] for v in el.values())
        cs = sorted(el)
        pick = np.random.Generator(np.random.PCG64(5)).choice(len(cs), size=min(N_ORACLE, len(cs)), replace=False)
        elites = bs.unpack(np.frombuffer(b"".join(el[cs[i]][1] for i in sorted(pick)), np.uint8).reshape(-1, bs.glen))
        np.save(HOT / f"{a.tag}_w{gs}_elites.npy", bs.pack(elites))
        row = {"exp_id": EXP, "tag": a.tag, "gen_seed": gs, "world_id": bs.wid, "T": bs.T, "S": bs.S, "W": bs.W,
               "obs_dim": bs.D, "d": bs.d, "r": R, "A": A, "genome_bytes": bs.glen, "gens": a.gens, "batch": a.batch,
               "genomes_evaluated": a.gens * a.batch, "qd_best": int(best), "qd_cells": len(el),
               "qd_score": int(sum(v[0] for v in el.values())), "open_loop_best_e4b_median": open_best,
               "closed_beats_open": best > open_best,
               "world_oracle_honest": world_oracle(bs, elites),
               "world_oracle_skip_lin": world_oracle(bs, elites, "skip_lin"),
               "brain_oracle_honest": brain_oracle(bs, elites),
               "brain_oracle_skip_odd": brain_oracle(bs, elites, skip_odd=True),
               "wall_s": round(time.perf_counter() - t0, 1),
               "episode_steps_per_s_rollout": round(a.gens * a.batch * len(SEEDS) * bs.T / t_roll, 1),
               "ts": time.time()}
        arch.clear()
        print(json.dumps(row), flush=True)
        with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
