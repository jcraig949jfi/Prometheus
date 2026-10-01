"""W2-H engine pool: per-(world, trial) scores of fixed C1 champions on many fresh mirror pairs.
CPU only, 2 threads. Usage: python engine_pool.py CELL_ID|null:CELL_ID NPAIRS
Writes out/pool_<tag>.npz with per_trial [M, trials] (NaN unscored), acc [M], pairs [M/2].
Namespace 0x57324800 + k (fresh; disjoint from every campaign namespace by construction of H_int)."""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
import gzip
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
import numpy as np
import torch

torch.set_num_threads(2)
assert not torch.cuda.is_available()
from prometheus.ananke import assays, envs, plants  # noqa: E402
from prometheus.ananke.engine import World  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
NS = 0x57324800


def load(cell):
    for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt"):
        r = json.loads(l)
        if r["cell_id"] == cell:
            return r
    raise KeyError(cell)


def per_trial(ph, genome, env, seeds):
    M = len(seeds)
    ws = [seeds[m - (m % 2)] for m in range(M)]          # assays.evaluate mirror semantics
    ep = envs.build(ph, env, seeds)
    w = World(ph, np.repeat(genome[None], M, 0), ws, device="cpu", schedule=ep.schedule)
    w.run(env.T(), graph=False)
    tr = w.trace.cpu().numpy()
    pt = envs.per_trial(ep, tr).astype(float)
    pt[~ep.scored] = np.nan
    return pt, envs.score(ep, tr)


if __name__ == "__main__":
    spec, npairs = sys.argv[1], int(sys.argv[2])
    null = spec.startswith("null:")
    cell = spec.split(":")[-1]
    r = load(cell)
    ph = Physics.from_dict(r["physics"])
    env = envs.EnvSpec(**r["env"])
    g = plants.plant("null", ph) if null else np.asarray(r["result"]["champion"])
    t0 = time.time()
    PT, AC = [], []
    chunk = 256                       # worlds per call
    for k in range(0, 2 * npairs, chunk):
        seeds = assays.world_seeds(NS + k // chunk, chunk)
        pt, ac = per_trial(ph, g, env, seeds)
        PT.append(pt)
        AC.append(ac)
    PT = np.concatenate(PT)
    AC = np.concatenate(AC)
    # sanity: same genome via assays.evaluate on the first chunk reproduces acc exactly
    chk = assays.evaluate(ph, g[None], env, assays.world_seeds(NS, chunk), device="cpu").acc[0]
    assert np.array_equal(chk, AC[:chunk]), "pool != assays.evaluate"
    tag = ("null_" if null else "") + cell
    np.savez_compressed(OUT / f"pool_{tag}.npz", per_trial=PT, acc=AC, pairs=AC.reshape(-1, 2).mean(1),
                        held=json.dumps(r["result"]["held"]), family=r["env"]["family"])
    print(tag, r["env"]["family"], "M", len(AC), "mean", AC.mean(), "held", r["result"]["held"],
          "wall", round(time.time() - t0, 1), flush=True)
