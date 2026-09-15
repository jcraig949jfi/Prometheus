"""Anti-prior cell draw (round 2, cohort C). The cell is chosen by RNG, not by an LLM.

An LLM asked to "try something weird" still samples its own weights. Cohort C
therefore does not pick what to test: it draws a cell from the descriptor grid,
weighted toward cells nobody has visited, and must build and run THAT cell (an
infeasible combination is itself a row: status "aborted", reason "infeasible").

Every draw is logged, with its RNG seed, to primordial/ledger/qd/draws.jsonl
(committed on write) and posted on the bus, so a redraw is visible.

    python -m primordial.ops.draw_cell [--seed N]

Weights: 1 / (1 + visits), where visits counts QD ledger rows plus earlier
draws with the same (representation, world, pressure, substrate, channel).

Round 4 (SWARM_R4 s2 G-R4-4): graphworld worlds are drawn ONLY from the screen's
survivors (primordial/ledger/qd/worlds_r4.json, active variant; read, never
recomputed). No file means no graphworld world. The non-graphworld domains have
no floor suite and stay on the axis as landscape rows (no clause A claim).
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
DRAWS = ROOT / "primordial" / "ledger" / "qd" / "draws.jsonl"

AXES = {
    "representation": ["dense_table", "bitset", "linear", "lut_top", "additive", "pairwise", "cp", "tucker",
                       "tt_feat", "tt_digits", "small_program", "affine_plastic", "codebook"],
    "world": ["w1", "w2", "w3", "w4", "w5", "graphworld_b2", "signal_world_d1", "nk_stub"],
    "pressure": ["byte_charge", "decoder_rent", "bit_metering", "held_out_seeds", "corruption", "obs_delay",
                 "regime_switching", "cpu_ttl"],
    "substrate": ["numpy", "numba_fused", "redis_lua", "falkordb_cypher", "graphblas", "torch_gpu"],
    "channel": ["none", "metered_stream"],
}


NON_GRAPHWORLD = ["graphworld_b2", "signal_world_d1", "nk_stub"]
_FROM_FILE = object()


def axes(doc=_FROM_FILE) -> dict:
    """The draw grid: AXES with the world axis = screen survivors (w<gen_seed>) + NON_GRAPHWORLD."""
    from primordial.metric import worlds as WR
    doc = WR.load() if doc is _FROM_FILE else doc
    return {**AXES, "world": WR.survivor_worlds(doc) + NON_GRAPHWORLD}


def _key(cell: dict) -> tuple:
    return tuple(cell.get(k) for k in AXES)


def visits() -> dict:
    from primordial.ops import qd_ledger
    v: dict = {}
    for r in qd_ledger.load():
        k = _key(r["cell"])
        v[k] = v.get(k, 0) + 1
    if DRAWS.exists():
        for line in DRAWS.read_text(encoding="utf-8").splitlines():
            if line.strip():
                k = _key(json.loads(line)["cell"])
                v[k] = v.get(k, 0) + 1
    return v


def draw(seed: int | None = None, doc=_FROM_FILE) -> dict:
    seed = int.from_bytes(os.urandom(8), "little") if seed is None else int(seed)
    rng = np.random.default_rng(seed)
    ax = axes(doc)
    names = list(ax)
    sizes = [len(ax[n]) for n in names]
    n_cells = int(np.prod(sizes))
    v = visits()
    weights = np.ones(n_cells)
    for k, cnt in v.items():
        try:
            idx = np.ravel_multi_index([ax[n].index(x) for n, x in zip(names, k)], sizes)
        except ValueError:
            continue
        weights[idx] = 1.0 / (1.0 + cnt)
    flat = int(rng.choice(n_cells, p=weights / weights.sum()))
    coords = np.unravel_index(flat, sizes)
    cell = {n: ax[n][int(i)] for n, i in zip(names, coords)}
    return {"cell": cell, "seed": seed, "grid_cells": n_cells, "prior_visits": v.get(_key(cell), 0),
            "worlds_screen": "primordial/ledger/qd/worlds_r4.json", "status": "control", "ts": round(time.time(), 3)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int)
    ap.add_argument("--no-log", action="store_true", help="dry draw: not logged, not posted (tests only)")
    a = ap.parse_args(argv)
    d = draw(a.seed)
    if not a.no_log:
        from primordial.fabric.rows import RowWriter
        with RowWriter(DRAWS, "C-anti-prior-draws", commit_every_s=10**9) as w:
            w.write(d)
        try:
            from primordial.bus import bus
            os.environ.setdefault("PM_LANE", "C")
            bus.post("note", "DRAW " + " ".join(f"{k}={x}" for k, x in d["cell"].items()),
                     json.dumps(d), to="ALL")
        except Exception as e:                                  # bus down: the committed row still stands
            print(f"(bus post failed: {type(e).__name__})")
    print(json.dumps(d, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
