"""F8 (round 3): seed/world table cache keyed by (world id, seed).

FusedRollout.__init__ spent 0.37-0.39 s at 128 genomes x 128 seeds (measured
19:00; round 1 profile: 0.37 s), 87% of it in init_regs: 229k wforge
stream() hashes for 16,384 envs when only the 128 seeds differ. Every table
it builds is a pure function of (world, seed):

  regs   init registers            (n_regs,)   int64
  stoch  stoch stream state        ()          uint64
  corr   corrupt stream per slot   (n_slots,)  uint64

So they are computed once per (world id, mechanics digest, seed), held in
process memory (the F7 warm child keeps them across jobs) and in one .npz per
(world id, digest) under PM_WORLDCACHE_DIR, shared across processes and lanes.
The digest (sha256 of the Mechanics dataclass) guards against a world id
reused with different mechanics. PM_WORLDCACHE=0 disables the disk layer.
The disk write is atomic (temp file + os.replace); a corrupt or mismatched
file is ignored and rebuilt.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import pathlib
import tempfile

import numpy as np

DIR = pathlib.Path(os.environ.get("PM_WORLDCACHE_DIR", "C:/Users/jcrai/lab/pm-data/worldcache"))
_MEM: dict = {}                     # (wid, digest) -> {seed: (regs row, stoch, corr row)}


def mech_digest(mech) -> str:
    d = dataclasses.asdict(mech) if dataclasses.is_dataclass(mech) else dict(vars(mech))
    return hashlib.sha256(json.dumps(d, sort_keys=True, default=list).encode()).hexdigest()[:16]


def cold_tables(mech, wid: str, seeds) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """The uncached computation, exactly as FusedRollout.__init__ did it before F8."""
    from primordial.soup.b1.common import init_regs, stream_state
    seeds = np.asarray(seeds, np.int64)
    n = len(seeds)
    regs = np.ascontiguousarray(init_regs(mech, wid, seeds), np.int64)
    stoch = np.array([stream_state("stoch", wid, int(s)) for s in seeds], dtype=np.uint64)
    corr = np.array([[stream_state("corrupt", wid, int(s), i) for i in range(mech.n_slots)] for s in seeds],
                    dtype=np.uint64).reshape(n, mech.n_slots)
    return regs, stoch, corr


def _path(wid: str, digest: str) -> pathlib.Path:
    return DIR / f"{wid}-{digest}.npz"


def _disk_on() -> bool:
    return os.environ.get("PM_WORLDCACHE", "1") != "0"


def _load(wid: str, digest: str, mech) -> dict:
    p = _path(wid, digest)
    if not (_disk_on() and p.exists()):
        return {}
    try:
        with np.load(p) as z:
            s, r, st, c = z["seeds"], z["regs"], z["stoch"], z["corr"]
        if r.shape[1:] != (mech.n_regs,) or c.shape[1:] != (mech.n_slots,) or not (len(s) == len(r) == len(st) == len(c)):
            return {}
        return {int(k): (r[i], st[i], c[i]) for i, k in enumerate(s)}
    except Exception:
        return {}


def _save(wid: str, digest: str, mech, table: dict) -> None:
    if not _disk_on():
        return
    DIR.mkdir(parents=True, exist_ok=True)
    keys = sorted(table)
    fd, tmp = tempfile.mkstemp(prefix=".wc-", suffix=".npz", dir=DIR)
    os.close(fd)
    try:
        np.savez(tmp, seeds=np.array(keys, np.int64),
                 regs=np.array([table[k][0] for k in keys], np.int64).reshape(len(keys), mech.n_regs),
                 stoch=np.array([table[k][1] for k in keys], np.uint64),
                 corr=np.array([table[k][2] for k in keys], np.uint64).reshape(len(keys), mech.n_slots))
        os.replace(tmp, _path(wid, digest))
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def tables(mech, wid: str, seeds) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(regs (k, n_regs) int64, stoch (k,) uint64, corr (k, n_slots) uint64) for `seeds`, in order."""
    seeds = np.asarray(seeds, np.int64)
    digest = mech_digest(mech)
    key = (wid, digest)
    table = _MEM.get(key)
    if table is None:
        table = _MEM[key] = _load(wid, digest, mech)
    missing = sorted({int(s) for s in seeds} - table.keys())
    if missing:
        if _disk_on():                                           # another process may have added them
            table.update({k: v for k, v in _load(wid, digest, mech).items() if k not in table})
            missing = sorted({int(s) for s in seeds} - table.keys())
    if missing:
        r, st, c = cold_tables(mech, wid, np.array(missing, np.int64))
        for i, k in enumerate(missing):
            table[k] = (r[i], st[i], c[i])
        _save(wid, digest, mech, table)
    n = len(seeds)
    regs = np.empty((n, mech.n_regs), np.int64)
    stoch = np.empty(n, np.uint64)
    corr = np.empty((n, mech.n_slots), np.uint64)
    for i, s in enumerate(seeds):
        regs[i], stoch[i], corr[i] = table[int(s)]
    return regs, stoch, corr


def clear_memory() -> None:
    _MEM.clear()
