"""C-R2-04: drawn cell tt_feat / w3 / cpu_ttl / torch_gpu / none (draw seed 8325970016782937267).

Cohort C builds the drawn cell; it does not choose it. Posted on the bus before the run. GPU asked of lane B.

  substrate torch_gpu: the tt_feat brain forward (lane C's C4 _TT.logits, step for step: gather core, bmm,
            max-abs renormalise, output weights, argmax; skip-odd cheat identical) runs on CUDA float32; genome
            tensors are uploaded once per rollout. The world stays E7's numpy NpEncounter on the host (E7.rollout
            with g7.fam swapped), so E7's world and brain oracles test the GPU path unchanged.
  pressure  cpu_ttl, SAME definition as C-R2-01/03: training stops at 1.0 client process CPU-s (time.process_time).
            GPU kernel time and Redis server CPU are NOT charged; training wall and redis CPU are reported.
  setup     E9 otherwise: G7 tt_feat + codebook, LuaArchive, batch 128, E6's 8 train seeds, top-16 on 64 held-out
            seeds, RNG PCG64([990, run_seed, 3, family index]). Warm-up rollout off the clock.
  primary   held64_median over run seeds 0-7 >= 91.63 - 0.5 * 4.29 = 89.485 (round 1 baseline w3 tt_feat train8)
  oracles   run seed 0 on HELD8: world 0/16 failing, skip_lin >= 14/16; brain 0 mismatched clear rows,
            skip-odd cheat >= 14/16. Report-only: GPU argmax == numpy argmax share on the oracle rows.

  python -m primordial.cohorts.c.r2_04_cpu_ttl_gpu [--ttl-cpu-s 1.0] [--run-seeds 0-7]
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
from primordial.qd import e7_run as E7
from primordial.qd.archive import LuaArchive

EXP = "C-R2-04-tt-feat-w3-cpu-ttl-torch-gpu"
ROOT = pathlib.Path(__file__).resolve().parents[3]
ROWS = ROOT / "primordial" / "ledger" / "rows" / "C" / f"{EXP}.jsonl"
HOT = pathlib.Path("C:/Users/jcrai/lab/pm-data/C") / EXP          # hot data never on F:
GS, FAM, BATCH = 3, "tt_feat", 128
CELL = {"representation": "tt_feat", "world": "w3", "pressure": "cpu_ttl", "substrate": "torch_gpu", "channel": "none"}
BASE_MEDIAN, BASE_IQR = 91.63, 4.29
DEV = torch.device("cuda")


class TorchTTFeat(gm.TTFeat):
    """tt_feat with forward on CUDA; logits/ref_logits (numpy) inherited for comparison."""

    def __init__(self, D, A=8):
        super().__init__(D, A)
        self._src = None

    def _upload(self, g):
        if self._src is not g[1]:
            self._t = tuple(torch.from_numpy(np.ascontiguousarray(x)).to(DEV) for x in g)
            self._src = g[1]
        return self._t

    def forward(self, g, obs, gidx, cheat=False):
        al, G, Wo = self._upload(g)
        idx = torch.from_numpy(self.index(obs)).to(DEV)
        gi = torch.from_numpy(np.ascontiguousarray(gidx, np.int64)).to(DEV)
        v = al[gi]
        for c in range(idx.shape[1]):
            if cheat and c % 2:
                continue
            v = torch.bmm(v[:, None, :], G[gi, c, idx[:, c]])[:, 0]
            v = v / torch.clamp(v.abs().amax(1, keepdim=True), min=1e-30)
        return torch.bmm(v[:, None, :], Wo[gi])[:, 0].argmax(1).cpu().numpy()


def server_cpu(r) -> float:
    i = r.info("cpu")
    return float(i["used_cpu_sys"]) + float(i["used_cpu_user"])


def score(g7, raw, seeds) -> float:
    return float(E7.rollout(g7, g7.unpack(raw), seeds)[0].mean() / len(seeds))


def agreement(g7, top, seeds) -> float:
    _, _, _, L = E7.rollout(g7, top, seeds, log=True)
    k, n = len(seeds), 0
    same = 0
    for q in range(len(top[1])):
        t_i, e_i, s_i = np.nonzero(L["live"][:, q * k:(q + 1) * k])
        if len(t_i) == 0:
            continue
        e_i = e_i + q * k
        obs = L["obs"][t_i, e_i, s_i]
        npa = gm.TTFeat.logits(g7.fam, top[0], obs, np.full(len(obs), q)).argmax(1)
        same += int((npa == L["idx"][t_i, e_i, s_i]).sum()); n += len(obs)
    return round(same / max(n, 1), 6)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--ttl-cpu-s", type=float, default=1.0)
    p.add_argument("--run-seeds", default="0-7")
    p.add_argument("--port", type=int, default=6392)
    p.add_argument("--max-gens", type=int, default=200)
    a = p.parse_args()
    lo, hi = (int(x) for x in a.run_seeds.split("-"))
    HOT.mkdir(parents=True, exist_ok=True)
    r = redis.Redis(host="127.0.0.1", port=a.port)
    held, oracle = [], None
    with RowWriter(ROWS, EXP, commit_every_s=120) as w:
        for rs in range(lo, hi + 1):
            t0 = time.perf_counter()
            g7 = E7.G7(GS, FAM)
            g7.fam = TorchTTFeat(g7.fam.D, g7.fam.A)
            arch = LuaArchive(r, f"c-r2-04-{rs}", g7.glen)
            arch.clear()
            rng = np.random.Generator(np.random.PCG64([990, rs, GS, list(gm.FAMILIES).index(FAM)]))  # E9's stream
            E7.rollout(g7, g7.init(np.random.Generator(np.random.PCG64(12345)), BATCH), E7.TRAIN)  # warm-up, off clock
            torch.cuda.synchronize()
            s_cpu0, c0, w0, gens = server_cpu(r), time.process_time(), time.perf_counter(), 0
            while gens < a.max_gens and time.process_time() - c0 < a.ttl_cpu_s:
                par = arch.sample(BATCH)
                g = g7.init(rng, BATCH) if len(par) == 0 else g7.mutate(rng, g7.unpack(par))
                fit, cells, _, _ = E7.rollout(g7, g, E7.TRAIN)
                arch.insert(cells, fit, g7.pack(g), np.zeros((BATCH, 2), np.uint32))
                gens += 1
            client_cpu, train_wall = time.process_time() - c0, time.perf_counter() - w0
            srv = server_cpu(r) - s_cpu0
            el = arch.dump()
            raw = np.frombuffer(b"".join(v[1] for v in sorted(el.values(), key=lambda v: (-v[0], v[1]))[:E7.TOP]),
                                np.uint8).reshape(-1, g7.glen)
            arch.clear()
            np.save(HOT / f"w{GS}_{FAM}_r{rs}_top.npy", raw)
            row = {"kind": "run", "cell": CELL, "run_seed": rs, "ttl_cpu_s": a.ttl_cpu_s, "gens": gens,
                   "genomes": gens * BATCH, "cells": len(el), "client_cpu_s": round(client_cpu, 3),
                   "train_wall_s": round(train_wall, 3), "redis_server_cpu_s_uncharged": round(srv, 3),
                   "param_bytes": g7.pb, "genome_bytes": g7.glen,
                   "train_per_seed": score(g7, raw, E7.TRAIN), "held64_per_seed": score(g7, raw, E7.HELD64),
                   "status": "record"}
            if rs == lo:
                top = g7.unpack(raw)
                row["world_oracle_honest"] = E7.world_oracle(g7, top, E7.HELD8)
                row["world_oracle_skip_lin"] = E7.world_oracle(g7, top, E7.HELD8, "skip_lin")
                row["brain_oracle_honest"] = E7.brain_oracle(g7, top, E7.HELD8)
                row["brain_oracle_cheat"] = E7.brain_oracle(g7, top, E7.HELD8, cheat=True)
                row["gpu_vs_numpy_argmax_agreement"] = agreement(g7, top, E7.HELD8)
                oracle = row
            row["wall_s"] = round(time.perf_counter() - t0, 2)
            held.append(row["held64_per_seed"])
            print(json.dumps(row), flush=True)
            w.write(row)
        q1, med, q3 = (float(x) for x in np.percentile(held, [25, 50, 75]))
        wo, ws, bo, bc = (oracle["world_oracle_honest"], oracle["world_oracle_skip_lin"],
                          oracle["brain_oracle_honest"], oracle["brain_oracle_cheat"])
        oracle_clean = (wo["elites_failing"] == 0 and ws["elites_failing"] >= 14 and bo["mismatched_rows"] == 0
                        and bo["clear_rows"] > 0 and bc["elites_mismatching"] >= 14)
        threshold = BASE_MEDIAN - 0.5 * BASE_IQR
        summary = {"kind": "summary", "cell": CELL, "n_runs": len(held), "held64_median": round(med, 3),
                   "iqr": round(q3 - q1, 3), "threshold": round(threshold, 3), "oracle_clean": oracle_clean,
                   "primary": "PASS" if (oracle_clean and len(held) >= 8 and med >= threshold) else
                              ("INDETERMINATE" if not oracle_clean else "FAIL"),
                   "clause_a_check_cpu_ttl": qd_ledger.check(qd_ledger.load(), "w3", "cpu_ttl", med, q3 - q1,
                                                             g7.glen, len(held), oracle_clean),
                   "status": "record" if oracle_clean else "cheat"}
        print(json.dumps(summary), flush=True)
        w.write(summary)
    with RowWriter(qd_ledger.CELLS, EXP, commit_every_s=10**9) as q:
        q.write({"cell": CELL, "mechanism": f"closed_loop_tt_feat_codebook_torch_gpu_cpu_ttl_{a.ttl_cpu_s:g}s",
                 "fitness": {"held64_median": round(med, 3), "iqr": round(q3 - q1, 3), "n_runs": len(held)},
                 "footprint": {"genome_bytes": int(g7.glen)},
                 "oracle": "clean (E7 world/brain oracles on the GPU forward, skip_lin + skip-odd cheats)" if oracle_clean
                           else f"NOT clean: {json.dumps([wo, ws, bo, bc])}",
                 "baseline": False, "cohort": "C", "status": summary["status"],
                 "source": {"exp_id": EXP, "rows": ROWS.relative_to(ROOT).as_posix()}})


if __name__ == "__main__":
    main()
