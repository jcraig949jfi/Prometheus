"""Shared MAP-Elites archive in Redis (owner: lane E).

Keys for run R:
  pm:qd:R:c:<cell>   hash  f (int fitness), g (genome bytes), m (8-byte meta: u32 worker, u32 gen LE)
  pm:qd:R:niche      zset  member = cell, score = f

Total order on elites (arrival-order independent, so N concurrent instances
have ONE correct final archive): higher f wins; on equal f the genome that is
lexicographically smaller wins (compared as big-endian u32 chunks in Lua,
never with Lua string `<`, which goes through strcoll).

LuaArchive: one EVALSHA per offspring batch; the read-compare-write for every
cell is atomic on the server. RacyArchive: the same logic client-side (HMGET
pipeline, then HSET pipeline). It is the cheat control for E1: under
concurrency it must lose elites and the exactness instrument must see it.
"""
from __future__ import annotations

import numpy as np
import redis

INSERT_LUA = r"""
local zkey, pre, glen = KEYS[1], ARGV[1], tonumber(ARGV[2])
local cells, fits, gs, meta = ARGV[3], ARGV[4], ARGV[5], ARGV[6]
local function gless(a, b)
  for p = 1, glen, 4 do
    local x = struct.unpack('>I4', a, p)
    local y = struct.unpack('>I4', b, p)
    if x ~= y then return x < y end
  end
  return false
end
local wins = 0
for i = 0, #cells / 4 - 1 do
  local c = struct.unpack('<I4', cells, 4 * i + 1)
  local f = struct.unpack('<i4', fits, 4 * i + 1)
  local g = string.sub(gs, glen * i + 1, glen * (i + 1))
  local k = pre .. c
  local old = redis.call('HMGET', k, 'f', 'g')
  local better
  if not old[1] then better = true
  else
    local of = tonumber(old[1])
    better = (f > of) or (f == of and gless(g, old[2]))
  end
  if better then
    redis.call('HSET', k, 'f', f, 'g', g, 'm', string.sub(meta, 8 * i + 1, 8 * (i + 1)))
    redis.call('ZADD', zkey, f, c)
    wins = wins + 1
  end
end
return wins
"""

SAMPLE_LUA = r"""
local ms = redis.call('ZRANDMEMBER', KEYS[1], -tonumber(ARGV[2]))
local out = {}
for i, c in ipairs(ms) do out[i] = redis.call('HGET', ARGV[1] .. c, 'g') end
return table.concat(out)
"""


def order_key(fit: np.ndarray, genomes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(fit, genome rank) as sortable arrays: best elite = max fit, then min genome.
    The rank is unsigned lexicographic byte order (np.unique over rows), which equals the
    Lua comparison over big-endian u32 chunks for any genome length that is a multiple of 4."""
    rank = np.unique(genomes, axis=0, return_inverse=True)[1].reshape(-1)
    return fit.astype(np.int64), rank


def reduce_batch(cells, fits, genomes, meta):
    """Best offer per cell under the archive's total order (order-independent)."""
    fit64, gbe = order_key(fits, genomes)
    # sort: cell asc, fit desc, genome asc -> first row per cell is the best
    o = np.lexsort((gbe, -fit64, cells))
    c = cells[o]
    first = np.ones(len(c), dtype=bool)
    first[1:] = c[1:] != c[:-1]
    s = o[first]
    return cells[s], fits[s], genomes[s], meta[s]


class _Base:
    def __init__(self, r: redis.Redis, run: str, glen: int):
        self.r, self.run, self.glen = r, run, glen
        self.pre = f"pm:qd:{run}:c:"
        self.zkey = f"pm:qd:{run}:niche"
        self._sample = r.register_script(SAMPLE_LUA)

    def sample(self, n: int) -> np.ndarray:
        raw = self._sample(keys=[self.zkey], args=[self.pre, n])
        return np.frombuffer(raw, dtype=np.uint8).reshape(-1, self.glen) if raw else np.empty((0, self.glen), np.uint8)

    def dump(self) -> dict[int, tuple[int, bytes, bytes]]:
        cells = [int(c) for c in self.r.zrange(self.zkey, 0, -1)]
        p = self.r.pipeline(transaction=False)
        for c in cells:
            p.hmget(self.pre + str(c), "f", "g", "m")
        return {c: (int(f), g, m) for c, (f, g, m) in zip(cells, p.execute())}

    def clear(self) -> None:
        keys = list(self.r.scan_iter(f"pm:qd:{self.run}:*", count=5000))
        for i in range(0, len(keys), 1000):
            self.r.delete(*keys[i:i + 1000])


class LuaArchive(_Base):
    def __init__(self, r, run, glen):
        super().__init__(r, run, glen)
        self._insert = r.register_script(INSERT_LUA)

    def insert(self, cells, fits, genomes, meta) -> int:
        cells, fits, genomes, meta = reduce_batch(cells, fits, genomes, meta)
        return int(self._insert(keys=[self.zkey], args=[
            self.pre, self.glen, cells.astype("<u4").tobytes(), fits.astype("<i4").tobytes(),
            genomes.tobytes(), meta.astype("<u4").tobytes()]))


class RacyArchive(_Base):
    """CHEAT CONTROL: non-atomic read-modify-write from the client."""

    def insert(self, cells, fits, genomes, meta) -> int:
        cells, fits, genomes, meta = reduce_batch(cells, fits, genomes, meta)
        p = self.r.pipeline(transaction=False)
        for c in cells:
            p.hmget(self.pre + str(int(c)), "f", "g")
        olds = p.execute()
        w = self.r.pipeline(transaction=False)
        wins = 0
        for i, (of, og) in enumerate(olds):
            g = genomes[i].tobytes()
            if of is None or int(fits[i]) > int(of) or (int(fits[i]) == int(of) and g < og):
                w.hset(self.pre + str(int(cells[i])), mapping={"f": int(fits[i]), "g": g, "m": meta[i].astype("<u4").tobytes()})
                w.zadd(self.zkey, {str(int(cells[i])): int(fits[i])})
                wins += 1
        w.execute()
        return wins


def serial_reference(cells, fits, genomes) -> dict[int, tuple[int, bytes]]:
    """What the archive MUST contain given every offer ever made, any order."""
    meta = np.zeros((len(cells), 2), np.uint32)
    c, f, g, _ = reduce_batch(cells, fits, genomes, meta)
    return {int(ci): (int(fi), gi.tobytes()) for ci, fi, gi in zip(c, f, g)}
