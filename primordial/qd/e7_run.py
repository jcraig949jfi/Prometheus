"""E7: lane C's C4 brain families as closed-loop genomes, under E6's held-out seed test.

  python -m primordial.qd.e7_run [--worlds 4,1,3] [--fams linear,lut_top,tt_feat,tt_digits]
                                 [--gens 200] [--batch 128] [--tag full]

Posted on the bus before the run (E7-c4-families-heldout):
  genome = C4 family params (primordial/brain/genomes.py, read-only; charge = fam.nbytes)
           + lane E's A x W action codebook (row 0 = abstain)
  world  = lane B's NpEncounter (with_obs); fitness = summed final charge over the seeds
  QD     = E1 Redis archive, E5 behavioural descriptor, 200 x 128 = 25,600 genomes on E6's 8 train seeds
  test   = top-16 by train fitness scored on E6's 64 held-out seeds (per-seed mean)
  SCIENCE: best held-out family is linear or lut_top in >=2/3 eligible worlds (w1, w3, w4)
  ORACLES on HELD8: world (wforge replay of recorded actions: hash + charge) honest 0/16 failing,
          skip_lin >=14/16; brain (fam.ref_logits + clear_rows) honest 0 mismatched clear rows,
          cheat=True forward mismatching on >=14/16 elites.
Comparators (E6 open-loop and r=3 TT held-out) are read from E6's committed rows.
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np
import redis

from primordial.brain import genomes as gm
from primordial.qd import e4_run as E4
from primordial.qd import e5_run as E5
from primordial.qd import e6_run as E6
from primordial.qd.archive import LuaArchive
from primordial.soup.b1.np_world import NpEncounter

EXP = "E7-c4-families-heldout"
ROWS = E4.ROWS.with_name(f"{EXP}.jsonl")
HOT = E5.HOT.parent / EXP
A, TOP, N_ORACLE_ROWS = 8, 16, 256
TRAIN, HELD64, HELD8 = E6.TRAIN.copy(), E6.HELD64, E6.HELD8


class G7:
    """A C4 family genome plus lane E's action codebook, packed to fixed-length bytes."""

    def __init__(self, gen_seed: int, fam_name: str):
        self.spec = E4.Spec(gen_seed)
        m = self.spec.mech
        self.D, self.S, self.W, self.T = len(m.obs_perm), m.n_slots, m.act_width, m.horizon
        self.fam = gm.FAMILIES[fam_name](self.D, A)
        self.pb, self.cb = self.fam.nbytes, A * self.W
        self.glen = (self.pb + self.cb + 3) // 4 * 4

    def init(self, rng, P):
        C = rng.integers(0, 16, size=(P, A, self.W), dtype=np.uint8)
        C[:, 0] = 0
        return self.fam.init(rng, P), C

    def mutate(self, rng, g):
        p, C = g
        m = rng.random(C.shape) < 1.0 / (A * self.W)
        C = np.where(m, rng.integers(0, 16, C.shape, dtype=np.uint8), C)
        C[:, 0] = 0
        return self.fam.mutate(rng, p), C

    def pack(self, g) -> np.ndarray:
        p, C = g
        out = np.zeros((len(C), self.glen), np.uint8)
        out[:, :self.pb] = self.fam.pack(p)
        out[:, self.pb:self.pb + self.cb] = C.reshape(len(C), -1)
        return out

    def unpack(self, B: np.ndarray):
        p = self.fam.unpack(np.ascontiguousarray(B[:, :self.pb]))
        return p, B[:, self.pb:self.pb + self.cb].reshape(-1, A, self.W).copy()


def rollout(g7: G7, g, seeds, world_cheat: str = "", cheat: bool = False, log: bool = False):
    p, C = g
    P, k, S, D, W = len(C), len(seeds), g7.S, g7.D, g7.W
    n = P * k
    w = NpEncounter(g7.spec.mech, g7.spec.wid, record=np.arange(n) if log else None, cheat=world_cheat, with_obs=True)
    obs = w.reset(np.tile(seeds, P))
    genv = np.repeat(np.arange(P), k)
    grow = np.repeat(genv, S)
    abst, mag, cnt = np.zeros(n), np.zeros(n), np.zeros(n)
    L = {"acts": np.zeros((g7.T, n, S, W), np.int32), "obs": np.zeros((g7.T, n, S, D), np.int64),
         "idx": np.zeros((g7.T, n, S), np.int64), "live": np.zeros((g7.T, n, S), bool)} if log else None
    for t in range(g7.T):
        idx = g7.fam.forward(p, obs.reshape(n * S, D), grow, cheat).reshape(n, S)
        a = C[genv[:, None], idx].astype(np.int32)
        live = w.alive & ~w.done[:, None]
        x = (a % 8).sum(-1)
        abst += ((x == 0) & live).sum(1); mag += (x * live).sum(1); cnt += live.sum(1)
        if log:
            L["acts"][t], L["obs"][t], L["idx"][t], L["live"][t] = a, obs, idx, live
        obs, _, done = w.step(a)
        if done.all():
            break
    fit = np.clip(w.charge, 0, None).sum(1).reshape(P, k).sum(1).astype(np.int32)
    tot = np.maximum(cnt.reshape(P, k).sum(1), 1)
    ab = abst.reshape(P, k).sum(1) / tot
    mg = mag.reshape(P, k).sum(1) / (tot * W * 7)
    cells = (np.rint(ab * 32) * E4.GRID + np.rint(np.clip(mg, 0, 1) * 32)).astype(np.uint32)
    return fit, cells, w, L


def world_oracle(g7, g, seeds, world_cheat=""):
    _, _, w, L = rollout(g7, g, seeds, world_cheat=world_cheat, log=True)
    hashes = [h.decode() for h in w.trace_hashes()]
    k, P = len(seeds), len(g[1])
    ep = np.clip(w.charge, 0, None)
    bad, mh, mc = np.zeros(P, bool), 0, 0
    for e in range(P * k):
        h, ch = E4.wforge_replay(g7.spec, L["acts"][:, e], seeds[e % k])
        hb, cb = h != hashes[e], not np.array_equal(ch, ep[e])
        mh += hb; mc += cb
        bad[e // k] |= hb or cb
    return {"elites": P, "elites_failing": int(bad.sum()), "episodes_hash_mismatch": int(mh),
            "episodes_charge_mismatch": int(mc)}


def brain_oracle(g7, g, seeds, cheat=False, seed=0):
    _, _, _, L = rollout(g7, g, seeds, cheat=cheat, log=True)
    rng = np.random.Generator(np.random.PCG64(seed))
    k, P = len(seeds), len(g[1])
    elites_bad = rows_clear = rows_mm = 0
    for q in range(P):
        t_i, e_i, s_i = np.nonzero(L["live"][:, q * k:(q + 1) * k])
        if len(t_i) == 0:
            continue
        pick = rng.choice(len(t_i), size=min(N_ORACLE_ROWS, len(t_i)), replace=False)
        t_i, e_i, s_i = t_i[pick], e_i[pick] + q * k, s_i[pick]
        ref = g7.fam.ref_logits(g7.fam.one(g[0], q), L["obs"][t_i, e_i, s_i])
        ok = gm.clear_rows(ref)
        mm = (ref.argmax(1) != L["idx"][t_i, e_i, s_i]) & ok
        rows_clear += int(ok.sum()); rows_mm += int(mm.sum())
        elites_bad += bool(mm.any())
    return {"elites": P, "elites_mismatching": elites_bad, "clear_rows": rows_clear, "mismatched_rows": rows_mm}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--worlds", default="4,1,3"); p.add_argument("--fams", default="linear,lut_top,tt_feat,tt_digits")
    p.add_argument("--gens", type=int, default=200); p.add_argument("--batch", type=int, default=128)
    p.add_argument("--port", type=int, default=6394); p.add_argument("--tag", default="full")
    a = p.parse_args()
    HOT.mkdir(parents=True, exist_ok=True)
    r = redis.Redis(port=a.port)
    e6 = {x["gen_seed"]: x for x in (json.loads(l) for l in open(E4.ROWS.with_name("E6-heldout-seed-generalisation.jsonl")))
          if x["tag"] == "full"}
    for gs in [int(x) for x in a.worlds.split(",")]:
        for fam in a.fams.split(","):
            t0 = time.perf_counter()
            g7 = G7(gs, fam)
            arch = LuaArchive(r, f"e7-{gs}-{fam}", g7.glen)
            arch.clear()
            rng = np.random.Generator(np.random.PCG64([700, gs, len(fam)]))
            for _ in range(a.gens):
                par = arch.sample(a.batch)
                g = g7.init(rng, a.batch) if len(par) == 0 else g7.mutate(rng, g7.unpack(par))
                fit, cells, _, _ = rollout(g7, g, TRAIN)
                arch.insert(cells, fit, g7.pack(g), np.zeros((a.batch, 2), np.uint32))
            el = arch.dump()
            top_raw = np.frombuffer(b"".join(v[1] for v in sorted(el.values(), key=lambda v: (-v[0], v[1]))[:TOP]),
                                    np.uint8).reshape(-1, g7.glen)
            arch.clear()
            top = g7.unpack(top_raw)
            np.save(HOT / f"{a.tag}_w{gs}_{fam}_top.npy", top_raw)
            row = {
                "exp_id": EXP, "tag": a.tag, "gen_seed": gs, "family": fam, "param_bytes": g7.pb,
                "genome_bytes": g7.glen, "D": g7.D, "T": g7.T, "genomes": a.gens * a.batch, "cells": len(el),
                "train_per_seed": float(rollout(g7, top, TRAIN)[0].mean() / len(TRAIN)),
                "held64_per_seed": float(rollout(g7, top, HELD64)[0].mean() / len(HELD64)),
                "e6_open_held64": e6[gs]["open_held64"], "e6_tt_held64": e6[gs]["closed_held64"],
                "world_oracle_honest": world_oracle(g7, top, HELD8),
                "world_oracle_skip_lin": world_oracle(g7, top, HELD8, "skip_lin"),
                "brain_oracle_honest": brain_oracle(g7, top, HELD8),
                "brain_oracle_cheat": brain_oracle(g7, top, HELD8, cheat=True),
            }
            row["wall_s"], row["ts"] = round(time.perf_counter() - t0, 1), time.time()
            print(json.dumps(row), flush=True)
            with open(ROWS, "a", encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps(row, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
