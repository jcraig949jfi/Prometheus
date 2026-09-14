"""C-R2-05: drawn cell tt_digits / w5 / corruption / torch_gpu / none (draw seed 6291447670595906400).

Cohort C builds the drawn cell; it does not choose it. Posted on the bus before the run. GPU asked of lane B.

  world     w5 (E4.Spec(5)): T=256, D=3, S=1, W=1; the world genome ALREADY corrupts observations
            (corrupt_rate 16: each value XOR uniform[0, M) with p = 1/16) and delays them by 2 ticks.
  pressure  corruption, brain-side, on top of the world's own: before the brain forward AND before logging,
            each observed value is XORed with uniform[0, M) with p = 1/RATE, RATE = 16 (the world's own rate:
            doubles corruption; derived from the world genome, not tuned). RNG PCG64([7707, seeds[0], len(seeds),
            P]) per rollout call, so repeated scoring is deterministic. The world itself is untouched.
  substrate torch_gpu: generic CUDA forward for C4 _TT families (C-R2-04 port, index() from the numpy family).
  arms      corrupt (RATE 16) vs clean (RATE 0), same code, same GA stream PCG64([990, run_seed, 5, fam idx]),
            interleaved by run seed. Budget 36 gens x 128 (TTL-derived: 16 runs x 0.6 CPU-s/gen within 600 s).
            Train on E6's 8 seeds, top-16 by train fitness, held-out on E6's 64 seeds, both evaluated in their
            own arm's observation channel.
  primary   median held64(corrupt) >= median held64(clean) - 0.5 * IQR(clean), 8 run seeds each
  oracles   run seed 0, each arm, on HELD8: world (wforge replay of recorded actions) honest 0/16, skip_lin >= 14/16;
            brain (ref_logits on the LOGGED observations, clear rows) honest 0 mismatched, skip-odd >= 14/16;
            corrupt arm only: log_clean cheat (brain fed corrupted obs, clean obs logged) mismatched rows > 0.
  report    cross-evaluation: corrupt-arm elites scored clean, clean-arm elites scored corrupted.

  python -m primordial.cohorts.c.r2_05_corruption_gpu [--gens 36] [--run-seeds 0-7]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

import numpy as np
import redis
import torch

from primordial.brain import genomes as gm
from primordial.fabric.rows import RowWriter
from primordial.ops import qd_ledger
from primordial.qd import e4_run as E4
from primordial.qd import e7_run as E7
from primordial.qd.archive import LuaArchive
from primordial.soup.b1.np_world import M, NpEncounter

EXP = "C-R2-05-tt-digits-w5-corruption-torch-gpu"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "C" / f"{EXP}.jsonl"
HOT = pathlib.Path("C:/Users/jcrai/lab/pm-data/C") / EXP          # hot data never on F:
GS, FAM, BATCH, RATE = 5, "tt_digits", 128, 16
CELL = {"representation": "tt_digits", "world": "w5", "pressure": "corruption", "substrate": "torch_gpu", "channel": "none"}
CELL_CLEAN = dict(CELL, pressure="corruption_rate0")
DEV = torch.device("cuda")


def torch_family(base):
    class TorchTT(base):
        def __init__(self, D, A=8):
            super().__init__(D, A)
            self._src = None

        def forward(self, g, obs, gidx, cheat=False):
            if self._src is not g[1]:
                self._t = tuple(torch.from_numpy(np.ascontiguousarray(x)).to(DEV) for x in g)
                self._src = g[1]
            al, G, Wo = self._t
            idx = torch.from_numpy(np.ascontiguousarray(self.index(obs))).to(DEV)
            gi = torch.from_numpy(np.ascontiguousarray(gidx, np.int64)).to(DEV)
            v = al[gi]
            for c in range(idx.shape[1]):
                if cheat and c % 2:
                    continue
                v = torch.bmm(v[:, None, :], G[gi, c, idx[:, c]])[:, 0]
                v = v / torch.clamp(v.abs().amax(1, keepdim=True), min=1e-30)
            return torch.bmm(v[:, None, :], Wo[gi])[:, 0].argmax(1).cpu().numpy()
    return TorchTT


def rollout(g7, g, seeds, rate, world_cheat="", cheat=False, log=False, log_clean=False):
    """E7.rollout (copy-on-write) with a brain-side corruption channel between world and brain."""
    p, C = g
    P, k, S, D, W = len(C), len(seeds), g7.S, g7.D, g7.W
    n = P * k
    w = NpEncounter(g7.spec.mech, g7.spec.wid, record=np.arange(n) if log else None, cheat=world_cheat, with_obs=True)
    obs = w.reset(np.tile(seeds, P))
    crng = np.random.Generator(np.random.PCG64([7707, int(seeds[0]), k, P]))
    genv = np.repeat(np.arange(P), k)
    grow = np.repeat(genv, S)
    abst, mag, cnt = np.zeros(n), np.zeros(n), np.zeros(n)
    L = {"acts": np.zeros((g7.T, n, S, W), np.int32), "obs": np.zeros((g7.T, n, S, D), np.int64),
         "idx": np.zeros((g7.T, n, S), np.int64), "live": np.zeros((g7.T, n, S), bool)} if log else None
    for t in range(g7.T):
        seen = obs
        if rate:
            hit = crng.integers(0, rate, obs.shape) == 0
            seen = obs ^ np.where(hit, crng.integers(0, M, obs.shape), 0)
        idx = g7.fam.forward(p, seen.reshape(n * S, D), grow, cheat).reshape(n, S)
        a = C[genv[:, None], idx].astype(np.int32)
        live = w.alive & ~w.done[:, None]
        x = (a % 8).sum(-1)
        abst += ((x == 0) & live).sum(1); mag += (x * live).sum(1); cnt += live.sum(1)
        if log:
            L["acts"][t], L["obs"][t], L["idx"][t], L["live"][t] = a, (obs if log_clean else seen), idx, live
        obs, _, done = w.step(a)
        if done.all():
            break
    fit = np.clip(w.charge, 0, None).sum(1).reshape(P, k).sum(1).astype(np.int32)
    tot = np.maximum(cnt.reshape(P, k).sum(1), 1)
    ab = abst.reshape(P, k).sum(1) / tot
    mg = mag.reshape(P, k).sum(1) / (tot * W * 7)
    cells = (np.rint(ab * 32) * E4.GRID + np.rint(np.clip(mg, 0, 1) * 32)).astype(np.uint32)
    return fit, cells, w, L


def world_oracle(g7, g, seeds, rate, world_cheat=""):
    _, _, w, L = rollout(g7, g, seeds, rate, world_cheat=world_cheat, log=True)
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


def brain_oracle(g7, g, seeds, rate, cheat=False, log_clean=False, seed=0):
    _, _, _, L = rollout(g7, g, seeds, rate, cheat=cheat, log=True, log_clean=log_clean)
    rng = np.random.Generator(np.random.PCG64(seed))
    k, P = len(seeds), len(g[1])
    elites_bad = rows_clear = rows_mm = 0
    for q in range(P):
        t_i, e_i, s_i = np.nonzero(L["live"][:, q * k:(q + 1) * k])
        if len(t_i) == 0:
            continue
        pick = rng.choice(len(t_i), size=min(E7.N_ORACLE_ROWS, len(t_i)), replace=False)
        t_i, e_i, s_i = t_i[pick], e_i[pick] + q * k, s_i[pick]
        ref = g7.fam.ref_logits(g7.fam.one(g[0], q), L["obs"][t_i, e_i, s_i])
        ok = gm.clear_rows(ref)
        mm = (ref.argmax(1) != L["idx"][t_i, e_i, s_i]) & ok
        rows_clear += int(ok.sum()); rows_mm += int(mm.sum())
        elites_bad += bool(mm.any())
    return {"elites": P, "elites_mismatching": elites_bad, "clear_rows": rows_clear, "mismatched_rows": rows_mm}


def per_seed(g7, raw, seeds, rate) -> float:
    return float(rollout(g7, g7.unpack(raw), seeds, rate)[0].mean() / len(seeds))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--gens", type=int, default=36)
    p.add_argument("--run-seeds", default="0-7")
    p.add_argument("--port", type=int, default=6392)
    a = p.parse_args()
    lo, hi = (int(x) for x in a.run_seeds.split("-"))
    HOT.mkdir(parents=True, exist_ok=True)
    r = redis.Redis(host="127.0.0.1", port=a.port)
    held = {RATE: [], 0: []}
    oracle_ok = {}
    with RowWriter(ROWS, EXP, commit_every_s=120) as w:
        for rs in range(lo, hi + 1):
            for rate in (RATE, 0):
                t0 = time.perf_counter()
                g7 = E7.G7(GS, FAM)
                g7.fam = torch_family(gm.FAMILIES[FAM])(g7.fam.D, g7.fam.A)
                arch = LuaArchive(r, f"c-r2-05-{rate}-{rs}", g7.glen)
                arch.clear()
                rng = np.random.Generator(np.random.PCG64([990, rs, GS, list(gm.FAMILIES).index(FAM)]))
                c0 = time.process_time()
                for _ in range(a.gens):
                    par = arch.sample(BATCH)
                    g = g7.init(rng, BATCH) if len(par) == 0 else g7.mutate(rng, g7.unpack(par))
                    fit, cells, _, _ = rollout(g7, g, E7.TRAIN, rate)
                    arch.insert(cells, fit, g7.pack(g), np.zeros((BATCH, 2), np.uint32))
                cpu = time.process_time() - c0
                el = arch.dump()
                raw = np.frombuffer(b"".join(v[1] for v in sorted(el.values(), key=lambda v: (-v[0], v[1]))[:E7.TOP]),
                                    np.uint8).reshape(-1, g7.glen)
                arch.clear()
                np.save(HOT / f"rate{rate}_r{rs}_top.npy", raw)
                other = 0 if rate else RATE
                row = {"kind": "run", "cell": CELL if rate else CELL_CLEAN, "arm": "corrupt" if rate else "clean",
                       "rate": rate, "run_seed": rs, "gens": a.gens, "genomes": a.gens * BATCH, "cells": len(el),
                       "train_cpu_s": round(cpu, 2), "genome_bytes": g7.glen,
                       "train_per_seed": per_seed(g7, raw, E7.TRAIN, rate),
                       "held64_per_seed": per_seed(g7, raw, E7.HELD64, rate),
                       f"held64_per_seed_evaluated_rate{other}": per_seed(g7, raw, E7.HELD64, other),
                       "status": "record" if rate else "control"}
                if rs == lo:
                    top = g7.unpack(raw)
                    row["world_oracle_honest"] = world_oracle(g7, top, E7.HELD8, rate)
                    row["world_oracle_skip_lin"] = world_oracle(g7, top, E7.HELD8, rate, "skip_lin")
                    row["brain_oracle_honest"] = brain_oracle(g7, top, E7.HELD8, rate)
                    row["brain_oracle_cheat"] = brain_oracle(g7, top, E7.HELD8, rate, cheat=True)
                    ok = (row["world_oracle_honest"]["elites_failing"] == 0
                          and row["world_oracle_skip_lin"]["elites_failing"] >= 14
                          and row["brain_oracle_honest"]["mismatched_rows"] == 0
                          and row["brain_oracle_honest"]["clear_rows"] > 0
                          and row["brain_oracle_cheat"]["elites_mismatching"] >= 14)
                    if rate:
                        row["brain_oracle_log_clean_cheat"] = brain_oracle(g7, top, E7.HELD8, rate, log_clean=True)
                        ok = ok and row["brain_oracle_log_clean_cheat"]["mismatched_rows"] > 0
                    oracle_ok[rate] = ok
                row["wall_s"] = round(time.perf_counter() - t0, 2)
                held[rate].append(row["held64_per_seed"])
                print(json.dumps(row), flush=True)
                w.write(row)
        stats = {}
        for rate in (RATE, 0):
            q1, med, q3 = (float(x) for x in np.percentile(held[rate], [25, 50, 75]))
            stats[rate] = (med, q3 - q1)
        oracle_clean = oracle_ok.get(RATE, False) and oracle_ok.get(0, False)
        threshold = stats[0][0] - 0.5 * stats[0][1]
        n = min(len(held[RATE]), len(held[0]))
        summary = {"kind": "summary", "cell": CELL, "n_runs": n,
                   "held64_median_corrupt": round(stats[RATE][0], 3), "iqr_corrupt": round(stats[RATE][1], 3),
                   "held64_median_clean": round(stats[0][0], 3), "iqr_clean": round(stats[0][1], 3),
                   "threshold": round(threshold, 3), "oracle_clean": oracle_clean,
                   "primary": ("INDETERMINATE" if not oracle_clean else
                               ("PASS" if n >= 8 and stats[RATE][0] >= threshold else "FAIL")),
                   "status": "record" if oracle_clean else "cheat"}
        print(json.dumps(summary), flush=True)
        w.write(summary)
    with RowWriter(qd_ledger.CELLS, EXP, commit_every_s=10**9) as q:
        for rate, cell, status in ((RATE, CELL, summary["status"]), (0, CELL_CLEAN, "control")):
            q.write({"cell": cell, "mechanism": f"closed_loop_tt_digits_codebook_gpu_brain_corruption_rate{rate}_{a.gens}gens",
                     "fitness": {"held64_median": round(stats[rate][0], 3), "iqr": round(stats[rate][1], 3),
                                 "n_runs": len(held[rate])},
                     "footprint": {"genome_bytes": int(g7.glen)},
                     "oracle": "clean (world replay, brain on logged obs, skip_lin + skip-odd + log_clean cheats)"
                               if oracle_clean else "NOT clean",
                     "baseline": False, "cohort": "C", "status": status,
                     "source": {"exp_id": EXP, "rows": ROWS.relative_to(ROOT).as_posix()}})


if __name__ == "__main__":
    main()
