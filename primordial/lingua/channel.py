"""Lane D, D1: driver for channel.lua on the private substrate (default 127.0.0.1:6393).

One EVALSHA per tick settles all envs' sends; the receiver then reads what was delivered
from the stream entry the script wrote (XRANGE by id), not from local variables.
"""
from __future__ import annotations

import os
import pathlib

import numpy as np
import redis

URL = os.environ.get("PM_D_SUBSTRATE", "redis://127.0.0.1:6393/0")
_SRC = pathlib.Path(__file__).with_name("channel.lua").read_text(encoding="ascii")
CHEATS = {"": 0, "free_unaffordable": 1, "undercharge": 2}


class LuaChannel:
    def __init__(self, r: redis.Redis | None, ns: str, n: int, alpha_int: int, start: int, cheat: str = ""):
        self.r = r or redis.Redis.from_url(URL)
        self.sha = self.r.script_load(_SRC)
        self.keys = [f"{ns}:charge", f"{ns}:msgs"]
        self.n, self.alpha, self.cheat = n, int(alpha_int), CHEATS[cheat]
        self.r.delete(*self.keys)
        self.r.set(self.keys[0], np.full(n, start, dtype="<u4").tobytes())

    def tick(self, t, bits, syms, credit):
        sid, _, _, cs = self.r.evalsha(self.sha, 2, *self.keys, self.n, self.alpha, int(t), self.cheat,
                                       np.asarray(bits, dtype=np.uint8).tobytes(),
                                       np.asarray(syms, dtype=np.uint8).tobytes(),
                                       np.asarray(credit, dtype=np.uint8).tobytes())
        entry = self.r.xrange(self.keys[1], sid, sid)[0][1]
        heard = np.frombuffer(entry[b"syms"], dtype=np.uint8).astype(np.int64)
        dbits = np.frombuffer(entry[b"bits"], dtype=np.uint8).astype(np.int64)
        return np.frombuffer(cs, dtype="<u4").astype(np.int64), heard, dbits

    def cleanup(self):
        self.r.delete(*self.keys)
