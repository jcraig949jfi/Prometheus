"""Operator 15 R15-1 (E): ONE readout for the M2 baseline and every clause A candidate.

Round 4 test launch 1 mixed readouts across the progress fraction: G's M2 baseline read the top-16 elites by
TRAIN (mean HELD64) and D-R4-4 showed the w13 train128 baseline is 182.72 under that readout but 189.53 under
top-1. A different readout on each side of `progress = (cand - floor) / (base - floor)` is the defect class.
This module is the only reader; both sides call it and stamp its NAME, and qd_ledger.check_r4 refuses a
candidate whose readout differs from the cell's baseline readout (INELIGIBLE READOUT_MISMATCH).

    top1_train  from an archive's elites [(train fitness, packed genome bytes)], select the ONE elite first by
                (-train fitness, genome bytes lexicographic) -- D-R4-4 `top1` and B-R4-7 `top1` -- and score it
                as its per-seed mean of summed clipped final charge on HELD64 (30000..30063).

The selection rule is genome-agnostic; the caller passes its family's scorer `score_fn(raw [n, glen], seeds)
-> per-seed mean` (linear_scorer for G7 linear; a quantized family passes its own decode + rollout).
A cell's value is the median over >= 8 run seeds with the M3 CI, unchanged.

LEGACY names the readout every row written before this module carried implicitly: top-16 by (-train fitness,
genome bytes), mean HELD64 (baseline.top_raw). An undeclared readout means LEGACY.
"""
from __future__ import annotations

import hashlib

import numpy as np

from primordial.metric import floors as F

NAME = "top1_train"
LEGACY = "m2_top16"
N = 1


def order(elites) -> list[tuple[int, bytes]]:
    """[(train fit, genome bytes)] best first: higher fit, then the lexicographically smaller genome."""
    return sorted(((int(f), bytes(g)) for f, g in elites), key=lambda v: (-v[0], v[1]))


def select(elites, n: int = N) -> list[tuple[int, bytes]]:
    got = order(elites)[:n]
    if not got:
        raise ValueError("empty archive: nothing to read")
    return got


def packed(sel, glen: int) -> np.ndarray:
    return np.frombuffer(b"".join(g for _, g in sel), np.uint8).reshape(-1, glen)


def elites_of(doc: dict) -> list[tuple[int, bytes]]:
    """A saved-elites document (qd.archive.save_elites) -> [(train fit, genome bytes)]."""
    return [(int(e[1]), bytes.fromhex(e[2])) for e in doc["elites"]]


def read(elites, glen: int, score_fn, seeds=None) -> dict:
    sel = select(elites)
    raw = packed(sel, glen)
    seeds = F.HELD64 if seeds is None else np.asarray(seeds)
    return {"readout": NAME, "held64_per_seed": float(score_fn(raw, seeds)), "train_fit": sel[0][0],
            "top_sha256": hashlib.sha256(raw.tobytes()).hexdigest(), "n_elites": len(elites)}


def read_doc(doc: dict, score_fn) -> dict:
    return read(elites_of(doc), int(doc["glen"]), score_fn)


def linear_scorer(gen_seed: int):
    """score_fn for E7.G7(gen_seed, 'linear') genomes: fused rollout, per-seed mean (== baseline.fused_per_seed)."""
    from primordial.qd import e7_run as E7
    from primordial.soup.b6.fused import FusedRollout
    g7 = E7.G7(int(gen_seed), "linear")

    def score(raw, seeds):
        seeds = np.asarray(seeds)
        return float(FusedRollout(g7.spec, len(raw), seeds, family="linear").run(g7.unpack(raw))[0].mean() / len(seeds))
    return score
