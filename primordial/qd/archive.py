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

# Seeded sampling (lane D ask 2026-09-14, D4: ZRANDMEMBER is unseeded, so a fixed run seed gave a
# different archive every run). The client draws uniforms from its PCG64; the server maps each to a
# cell of the numerically sorted cell list, atomically, with replacement. Same archive state + same
# sampler_seed -> same parents.
SEEDED_SAMPLE_LUA = r"""
local ms = redis.call('ZRANGE', KEYS[1], 0, -1)
local n = #ms
if n == 0 then return '' end
local cs = {}
for i, c in ipairs(ms) do cs[i] = tonumber(c) end
table.sort(cs)
local u, out = ARGV[2], {}
for i = 0, #u / 8 - 1 do
  local j = math.floor(struct.unpack('<d', u, 8 * i + 1) * n) + 1
  if j > n then j = n end
  out[i + 1] = redis.call('HGET', ARGV[1] .. cs[j], 'g')
end
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


# C2 (round 3, builder G): sampler_seed is mandatory. A harness frozen before C2 that must keep the
# round 1 ZRANDMEMBER sampler passes UNSEEDED explicitly; its archive reports replayable=False and its
# saved elites say so. None, or leaving the seed out, raises.
UNSEEDED = "UNSEEDED-pre-C2"


class _Base:
    def __init__(self, r: redis.Redis, run: str, glen: int, sampler_seed):
        """sampler_seed: a PCG64 seed (int or int sequence), or UNSEEDED for a frozen pre-C2 harness."""
        if sampler_seed is None:
            raise ValueError("sampler_seed is mandatory (C2); pass a PCG64 seed, or UNSEEDED for a frozen pre-C2 harness")
        unseeded = isinstance(sampler_seed, str)
        if unseeded and sampler_seed != UNSEEDED:
            raise ValueError(f"sampler_seed string {sampler_seed!r} is not UNSEEDED")
        self.r, self.run, self.glen = r, run, glen
        self.sampler_seed = sampler_seed
        self.pre = f"pm:qd:{run}:c:"
        self.zkey = f"pm:qd:{run}:niche"
        self._sample = r.register_script(SAMPLE_LUA)
        self.srng = None if unseeded else np.random.Generator(np.random.PCG64(sampler_seed))
        if self.srng is not None:
            self._seeded = r.register_script(SEEDED_SAMPLE_LUA)

    @property
    def replayable(self) -> bool:
        return self.srng is not None

    def sample(self, n: int) -> np.ndarray:
        if self.srng is not None:
            u = self.srng.random(n).astype("<f8").tobytes()
            raw = self._seeded(keys=[self.zkey], args=[self.pre, u])
        else:
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
    def __init__(self, r, run, glen, sampler_seed):
        super().__init__(r, run, glen, sampler_seed)
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


ELITES_SCHEMA = "qd-elites-v1"


def _plain(x):
    if isinstance(x, (list, tuple, np.ndarray)):
        return [_plain(v) for v in x]
    return x if isinstance(x, str) else int(x)


def save_elites(arch: _Base, path, run_seed) -> dict:
    """C2: write the archive's elites for one run seed (cells ascending, genomes and meta hex) as one
    canonical JSON document. Same archive state + same seeds -> byte-identical file."""
    import json
    import pathlib
    doc = {"schema": ELITES_SCHEMA, "run": arch.run, "run_seed": _plain(run_seed),
           "sampler_seed": _plain(arch.sampler_seed), "replayable": arch.replayable, "glen": arch.glen,
           "elites": [[c, f, g.hex(), m.hex()] for c, (f, g, m) in sorted(arch.dump().items())]}
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return doc


def load_elites(path) -> dict:
    import json
    import pathlib
    doc = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if doc.get("schema") != ELITES_SCHEMA:
        raise ValueError(f"not a {ELITES_SCHEMA} document: {path}")
    return doc


def restore_elites(arch: _Base, doc: dict) -> int:
    """Insert saved elites into arch; returns the archive's win count. A fixed-length archive needs the
    same glen; a VarArchive takes any saved genome no longer than its max length."""
    es = doc["elites"]
    if isinstance(arch, VarArchive):
        if any(len(e[2]) // 2 > arch.glen for e in es):
            raise ValueError(f"a saved genome is longer than the archive max length {arch.glen}")
    elif doc["glen"] != arch.glen:
        raise ValueError(f"glen {doc['glen']} != archive glen {arch.glen}")
    if not es:
        return 0
    cells = np.array([e[0] for e in es], np.uint32)
    fits = np.array([e[1] for e in es], np.int32)
    meta = np.frombuffer(bytes.fromhex("".join(e[3] for e in es)), "<u4").reshape(-1, 2)
    if isinstance(arch, VarArchive):
        return arch.insert(cells, fits, [bytes.fromhex(e[2]) for e in es], meta)
    genomes = np.frombuffer(bytes.fromhex("".join(e[2] for e in es)), np.uint8).reshape(-1, arch.glen)
    return arch.insert(cells, fits, genomes, meta)


# C4 (round 3, builder G): variable-length genomes. The pad-to-4 rule came from the u32-chunk tie-break;
# here genomes are compared byte by byte (string.byte, never Lua `<`), a shorter genome winning on an
# equal prefix -- Python's bytes order. For equal-length genomes whose length is a multiple of 4 this is
# the same order as INSERT_LUA's, so an archive written by LuaArchive loads and keeps its elites.
INSERT_VAR_LUA = r"""
local zkey, pre = KEYS[1], ARGV[1]
local cells, fits, lens, gs, meta = ARGV[2], ARGV[3], ARGV[4], ARGV[5], ARGV[6]
local function bless(a, b)
  local n = math.min(#a, #b)
  for p = 1, n do
    local x, y = string.byte(a, p), string.byte(b, p)
    if x ~= y then return x < y end
  end
  return #a < #b
end
local wins, off = 0, 1
for i = 0, #cells / 4 - 1 do
  local c = struct.unpack('<I4', cells, 4 * i + 1)
  local f = struct.unpack('<i4', fits, 4 * i + 1)
  local L = struct.unpack('<I4', lens, 4 * i + 1)
  local g = string.sub(gs, off, off + L - 1)
  off = off + L
  local k = pre .. c
  local old = redis.call('HMGET', k, 'f', 'g')
  local better
  if not old[1] then better = true
  else
    local of = tonumber(old[1])
    better = (f > of) or (f == of and bless(g, old[2]))
  end
  if better then
    redis.call('HSET', k, 'f', f, 'g', g, 'm', string.sub(meta, 8 * i + 1, 8 * (i + 1)))
    redis.call('ZADD', zkey, f, c)
    wins = wins + 1
  end
end
return wins
"""

SAMPLE_VAR_LUA = r"""
local ms = redis.call('ZRANDMEMBER', KEYS[1], -tonumber(ARGV[2]))
local out = {}
for i, c in ipairs(ms) do out[i] = redis.call('HGET', ARGV[1] .. c, 'g') end
return out
"""

SEEDED_SAMPLE_VAR_LUA = r"""
local ms = redis.call('ZRANGE', KEYS[1], 0, -1)
local n = #ms
local out = {}
if n == 0 then return out end
local cs = {}
for i, c in ipairs(ms) do cs[i] = tonumber(c) end
table.sort(cs)
local u = ARGV[2]
for i = 0, #u / 8 - 1 do
  local j = math.floor(struct.unpack('<d', u, 8 * i + 1) * n) + 1
  if j > n then j = n end
  out[i + 1] = redis.call('HGET', ARGV[1] .. cs[j], 'g')
end
return out
"""


def reduce_var(cells, fits, genomes) -> list[int]:
    """Indices of the best offer per cell under (higher fit, then smaller bytes), ascending."""
    best = {}
    for i, (c, f, g) in enumerate(zip(cells, fits, genomes)):
        key = (-int(f), g)
        if int(c) not in best or key < best[int(c)][0]:
            best[int(c)] = (key, i)
    return sorted(i for _, i in best.values())


class VarArchive(_Base):
    """LuaArchive for genomes of 1..max_len bytes. insert takes a list of bytes; sample returns one."""

    def __init__(self, r, run, max_len, sampler_seed):
        super().__init__(r, run, max_len, sampler_seed)
        self._insert = r.register_script(INSERT_VAR_LUA)
        self._sample_var = r.register_script(SAMPLE_VAR_LUA)
        self._seeded_var = r.register_script(SEEDED_SAMPLE_VAR_LUA)

    def insert(self, cells, fits, genomes, meta) -> int:
        genomes = [bytes(g) for g in genomes]
        bad = [len(g) for g in genomes if not 1 <= len(g) <= self.glen]
        if bad:
            raise ValueError(f"genome lengths {sorted(set(bad))} outside 1..{self.glen}")
        s = reduce_var(cells, fits, genomes)
        cells, fits, meta = np.asarray(cells)[s], np.asarray(fits)[s], np.asarray(meta)[s]
        gs = [genomes[i] for i in s]
        return int(self._insert(keys=[self.zkey], args=[
            self.pre, cells.astype("<u4").tobytes(), fits.astype("<i4").tobytes(),
            np.array([len(g) for g in gs], "<u4").tobytes(), b"".join(gs), meta.astype("<u4").tobytes()]))

    def sample(self, n: int) -> list[bytes]:
        if self.srng is not None:
            u = self.srng.random(n).astype("<f8").tobytes()
            return list(self._seeded_var(keys=[self.zkey], args=[self.pre, u]))
        return list(self._sample_var(keys=[self.zkey], args=[self.pre, n]))


def serial_reference(cells, fits, genomes) -> dict[int, tuple[int, bytes]]:
    """What the archive MUST contain given every offer ever made, any order."""
    meta = np.zeros((len(cells), 2), np.uint32)
    c, f, g, _ = reduce_batch(cells, fits, genomes, meta)
    return {int(ci): (int(fi), gi.tobytes()) for ci, fi, gi in zip(c, f, g)}
