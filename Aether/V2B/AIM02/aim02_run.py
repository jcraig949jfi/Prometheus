"""AETH-V2B-AIM02 unit runner: matched-flicker richness test (measurement only; no new physics).

Conditions (order s9):
  L1 x {D25, D50, D75}    aeth01.reaim1, B_balanced energy (AIM01's L1, unchanged)
  L0 x {D25, D50, D75}    aeth01.v1, B_balanced (AIM01's L0; reference for report Q1)
  C1  ER01 R1 free compute  aeth01.v1, w0 m0 no rain, D50 (ER01's initial family)
  C2  ER01 R2 rich rain     aeth01.v1, w1 m1 rain 8 @ 1/4, D50
All P0 (perturbation OFF). Seeds = the ER01/AIM01 namespace (rng 0xE2010000+k, physics 0xE2011000+k).

Law step: identical logic to Aether/V2B/AIM01/aim01_run.law_step, with the energy economy as a parameter
(checked bit-identical to aim01_run (B_balanced) and to ER01's runner (R1, R2) by aim02_conformance.py).

PRIMARY CHANNEL: record_columns() samples ONLY opcode, arg1 and payload (fields 0, 2, 3) on the fixed grid
rows % step == 0, cols % step == 0. arg0 (the field re-aim writes) and energy never enter it. arg0 RAW is
recorded separately as a labelled DIAGNOSTIC channel.
"""

import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AETHER = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, AETHER)
sys.path.insert(0, os.path.join(AETHER, "test"))
sys.path.insert(0, os.path.join(AETHER, "runpod", "aeth01_canary"))

import aim02_meter as MTR  # noqa: E402
from observatory import aeth01_run as R  # noqa: E402

RUNNER_VERSION = "aim02_run.v1"
P32 = 1 << 32
ENERGIES = {
    "B": dict(write_cost=1, maintenance_cost=1, replenish_numer=int(round(0.125 * P32)), replenish_amount=8),
    "FREE": dict(write_cost=0, maintenance_cost=0, replenish_numer=0, replenish_amount=0),
    "RICH": dict(write_cost=1, maintenance_cost=1, replenish_numer=int(round(0.25 * P32)), replenish_amount=8),
}
CONDS = {
    "L1D25": ("L1", 0.25, "B"), "L1D50": ("L1", 0.50, "B"), "L1D75": ("L1", 0.75, "B"),
    "L0D25": ("L0", 0.25, "B"), "L0D50": ("L0", 0.50, "B"), "L0D75": ("L0", 0.75, "B"),
    "C1FREE": ("L0", 0.50, "FREE"), "C2RICH": ("L0", 0.50, "RICH"),
}
RNG_SEED_BASE = 0xE2010000
PHYS_SEED_BASE = 0xE2011000
PRIMARY_FIELDS = (0, 2, 3)          # opcode, arg1, payload


def table_hash():
    blob = json.dumps({"conds": CONDS, "energies": ENERGIES, "rng": RNG_SEED_BASE, "phys": PHYS_SEED_BASE,
                       "fields": PRIMARY_FIELDS, "bins": MTR.BIN_EDGES}, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def load_backend(name):
    if name == "gpu":
        import aeth01_gpu_kernel as K
        if K.BACKEND != "cupy":
            raise SystemExit("gpu backend requested but CuPy is not importable")
        import cupy as xp
        return xp, K
    from reference import gpu_aeth01 as K
    return np, K


def digest(fields):
    h = hashlib.sha256()
    for f in fields:
        h.update(np.ascontiguousarray(np.asarray(getattr(f, "get", lambda: f)())).tobytes())
    return h.hexdigest()[:32]


def law_step(xp, K, law, energy, n, seed, tick, state):
    obs = []
    out = K.gpu_step(n, n, seed, tick, energy["write_cost"], energy["maintenance_cost"],
                     energy["replenish_numer"], energy["replenish_amount"], 0, *state, observer=obs)
    nxt = list(out[:5])
    if law == "L0":
        return nxt
    won = xp.zeros((n, n), dtype=bool)
    for f in range(5):
        best_slot = obs[f][0]
        for s, (dr, dc, _req) in enumerate(K._NEIGHBOR_SLOTS):
            won |= xp.roll(best_slot == s, (dr, dc), axis=(0, 1))
    reaim = won & ~(obs[1][0] != 255)
    nxt[1] = xp.where(reaim, (nxt[1].astype(xp.uint16) + 1).astype(xp.uint8), nxt[1])
    return nxt


def record_columns(xp, state, step=2):
    """PRIMARY channel frame: opcode, arg1, payload on the sample grid, flattened. Never arg0, never energy."""
    return xp.concatenate([state[f][::step, ::step].ravel() for f in PRIMARY_FIELDS])


def run_unit(backend, cond, k, n, ticks, window, step=2, digest_every=0):
    xp, K = load_backend(backend)
    law, dens, en = CONDS[cond]
    energy = ENERGIES[en]
    fields, recipe = R.build_initial(R.SPARSE_SOUP, n, n, RNG_SEED_BASE + k, write_density=dens,
                                     energy_mode=R.ENERGY_UNIFORM)
    s = [xp.asarray(f) for f in fields]
    phys = PHYS_SEED_BASE + k
    start = ticks - window          # frame 0 = state after `start` ticks
    frames, a0frames, digests = [], [], []
    late_nonaim = xp.zeros((), dtype=xp.int64)
    t0 = time.time()
    if start == 0:
        frames.append(record_columns(xp, s, step))
        a0frames.append(s[1][::step, ::step].ravel())
    for t in range(ticks):
        nxt = law_step(xp, K, law, energy, n, phys, t + 1, s)
        if t + 1 > start:
            late_nonaim += ((nxt[0] != s[0]) | (nxt[2] != s[2]) | (nxt[3] != s[3])).sum(dtype=xp.int64)
        s = nxt
        if t + 1 >= start:
            frames.append(record_columns(xp, s, step))
            a0frames.append(s[1][::step, ::step].ravel())
        if digest_every and (t + 1) % digest_every == 0:
            digests.append([t + 1, digest(s)])
    seq = xp.stack(frames)
    prim = MTR.analyze(xp, seq)
    diag = MTR.analyze(xp, xp.stack(a0frames))
    res = {"schema": "aether.aim02.unit.v1", "runner": RUNNER_VERSION, "table_hash": table_hash(),
           "backend": backend, "cond": cond, "law": law, "write_density": dens, "energy": en,
           "seed_index": k, "n": n, "ticks": ticks, "window": window, "step": step,
           "initial_digest": recipe["initial_state_digest"], "final_digest": digest(s), "digests": digests,
           "late_nonaim_turnover_site": int(late_nonaim) / (window * n * n),
           "primary": prim, "diagnostic_arg0_raw": diag, "wall_seconds": time.time() - t0}
    if backend == "gpu":
        import cupy
        res["gpu"] = {"mempool_total_bytes": int(cupy.get_default_memory_pool().total_bytes())}
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["gpu", "cpu"], default="gpu")
    ap.add_argument("--cond", choices=sorted(CONDS), required=True)
    ap.add_argument("--seed-index", type=int, required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--ticks", type=int, required=True)
    ap.add_argument("--window", type=int, required=True)
    ap.add_argument("--step", type=int, default=2)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if os.path.exists(a.out):
        return 0
    res = run_unit(a.backend, a.cond, a.seed_index, a.n, a.ticks, a.window, a.step)
    try:
        import psutil
        res["host_rss_bytes"] = int(psutil.Process().memory_info().rss)
    except ImportError:
        res["host_rss_bytes"] = None
    tmp = a.out + ".partial"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(res, fh, separators=(",", ":"))
    os.replace(tmp, a.out)
    print("done %s s%d %s %.1fs" % (a.cond, a.seed_index, res["final_digest"], res["wall_seconds"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
